#!/usr/bin/env python3
"""
pipeline/test_flux.py
---------------------
Single-call Cloudflare Workers AI FLUX test using `@cf/black-forest-labs/flux-1-schnell`.

Beginner-friendly breakdown:
1. Loads configuration from `.env` (CLOUDFLARE_ACCOUNT_ID & CLOUDFLARE_API_TOKEN).
2. Never prints or leaks secret tokens or account IDs (strictly masked/redacted).
3. Reads ONE prompt from `outputs/prompts.json` (Shot 1) or falls back to a default shot prompt.
4. Sends an HTTP POST request to Cloudflare Workers AI.
5. Receives the generated image and cleanly saves it under `outputs/`.
6. Appends a structured audit entry (timestamp, status, duration) to `runs.jsonl`.
"""

import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


def load_env_file(env_path: Path) -> dict:
    """
    Reads .env line by line and sets environment variables if not already set.
    """
    loaded = {}
    if not env_path.exists():
        return loaded

    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                loaded[key] = val
                if key not in os.environ:
                    os.environ[key] = val
    return loaded


def sanitize_text(text: str, secrets: list) -> str:
    """
    Removes any sensitive tokens or IDs from error messages or log output.
    """
    sanitized = str(text)
    for secret in secrets:
        if secret and len(secret) > 4:
            sanitized = sanitized.replace(secret, "[REDACTED]")
    return sanitized


def get_test_prompt(root_dir: Path) -> tuple:
    """
    Attempts to read Shot 1 from outputs/prompts.json.
    Falls back to a default shot prompt if not available.
    """
    prompts_file = root_dir / "outputs" / "prompts.json"
    if prompts_file.exists():
        try:
            with open(prompts_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            prompts = data.get("prompts", [])
            if prompts and "visual_prompt" in prompts[0]:
                shot_id = prompts[0].get("shot_id", 1)
                scene = prompts[0].get("scene_name", "Scene 1")
                return (
                    prompts[0]["visual_prompt"],
                    f"outputs/prompts.json (Shot {shot_id}: {scene})",
                )
        except Exception:
            pass

    fallback = (
        "Golden hour sunrise over mist-covered Ethiopian highland courtyard, "
        "traditional jebena buna pot, cinematic 35mm film still, photorealistic"
    )
    return fallback, "fallback_default_prompt"


def append_run_log(runs_path: Path, entry: dict):
    """
    Appends a structured JSON line to runs.jsonl.
    """
    runs_path.parent.mkdir(parents=True, exist_ok=True)
    with open(runs_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser(description="Cloudflare Workers AI FLUX generation")
    parser.add_argument("--prompt", default=None, help="Custom prompt text")
    parser.add_argument("--output", default=None, help="Custom output image file path")
    args = parser.parse_args()

    root_dir = Path(__file__).resolve().parent.parent
    env_file = root_dir / ".env"

    print("=" * 65)
    print(" Cloudflare Workers AI - FLUX Schnell Generation")
    print("=" * 65)

    # 1. Load .env
    load_env_file(env_file)

    account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID", "").strip()
    api_token = os.getenv("CLOUDFLARE_API_TOKEN", "").strip()
    output_dir = Path(os.getenv("OUTPUT_DIR", "./outputs"))
    if not output_dir.is_absolute():
        output_dir = root_dir / output_dir

    runs_log_path = Path(os.getenv("RUNS_LOG_PATH", "./runs.jsonl"))
    if not runs_log_path.is_absolute():
        runs_log_path = root_dir / runs_log_path

    # Security check: never print raw tokens or account IDs
    secrets = [account_id, api_token]
    print(f"[*] Config file        : {env_file} ({'Found' if env_file.exists() else 'Missing'})")
    print(f"[*] Account ID Status  : {'[CONFIGURED]' if account_id else '[EMPTY / UNSET]'}")
    print(f"[*] API Token Status   : {'[CONFIGURED]' if api_token else '[EMPTY / UNSET]'}")
    print(f"[*] Target Model       : @cf/black-forest-labs/flux-1-schnell")
    print("-" * 65)

    now_utc = datetime.now(timezone.utc)
    run_id = f"flux-{now_utc.strftime('%Y%m%d-%H%M%S')}"
    timestamp_str = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")

    # If credentials are not present, log gracefully and exit
    if not account_id or not api_token:
        print("[!] Missing CLOUDFLARE_ACCOUNT_ID or CLOUDFLARE_API_TOKEN in .env.")
        print("[!] Test skipped without making network calls.")
        log_entry = {
            "run_id": run_id,
            "timestamp": timestamp_str,
            "test_type": "cloudflare_workers_ai_flux",
            "model": "@cf/black-forest-labs/flux-1-schnell",
            "status": "SKIPPED",
            "duration_s": 0.0,
            "output_image": None,
            "notes": "CLOUDFLARE_ACCOUNT_ID or CLOUDFLARE_API_TOKEN is empty/missing in .env",
        }
        append_run_log(runs_log_path, log_entry)
        print(f"[✓] Logged status to {runs_log_path}")
        return

    # 2. Select prompt
    if args.prompt:
        prompt_text = args.prompt.strip()
        prompt_source = "CLI --prompt (Character Portrait)"
    else:
        prompt_text, prompt_source = get_test_prompt(root_dir)

    prompt_preview = (prompt_text[:90] + "...") if len(prompt_text) > 90 else prompt_text
    print(f"[*] Prompt Source      : {prompt_source}")
    print(f"[*] Prompt Preview     : \"{prompt_preview}\"")
    print(f"[*] Submitting generation request to Cloudflare Workers AI...")

    # 3. Prepare Cloudflare Workers AI API Request
    # Endpoint uses account ID, but we mask it when printing to screen
    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/@cf/black-forest-labs/flux-1-schnell"

    # Cloudflare Workers AI FLUX accepts {"prompt": "..."} (and optionally "steps")
    request_payload = {
        "prompt": prompt_text,
        "steps": 4,
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(request_payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
            "User-Agent": "heritage-short-flux-test/1.0",
        },
        method="POST",
    )

    start_time = time.time()
    status = "FAILED"
    output_image_rel = None
    detail_notes = ""

    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            duration_s = round(time.time() - start_time, 2)
            content_type = response.headers.get("Content-Type", "").lower()
            raw_body = response.read()

            image_bytes = None
            ext = ".png"

            # Check if response is raw binary image
            if "image/" in content_type or raw_body.startswith(b"\x89PNG") or raw_body.startswith(b"\xff\xd8\xff"):
                image_bytes = raw_body
                if raw_body.startswith(b"\xff\xd8\xff"):
                    ext = ".jpg"
            else:
                # Parse JSON response
                try:
                    res_json = json.loads(raw_body.decode("utf-8"))
                    # Cloudflare Workers AI can return {"result": {"image": "<base64>"}}
                    result_field = res_json.get("result", {})
                    if isinstance(result_field, dict) and "image" in result_field:
                        image_bytes = base64.b64decode(result_field["image"])
                    elif isinstance(result_field, str):
                        image_bytes = base64.b64decode(result_field)
                    elif res_json.get("success") is False:
                        errors = res_json.get("errors", [])
                        detail_notes = f"Cloudflare API error: {errors}"
                except Exception as json_err:
                    detail_notes = f"Failed to parse response: {json_err}"

            if image_bytes:
                # Detect image format from magic bytes
                if image_bytes.startswith(b"\xff\xd8\xff"):
                    ext = ".jpg"
                elif image_bytes.startswith(b"\x89PNG"):
                    ext = ".png"

                output_dir.mkdir(parents=True, exist_ok=True)
                if args.output:
                    custom_out = Path(args.output)
                    if not custom_out.is_absolute():
                        custom_out = root_dir / custom_out
                    custom_out.parent.mkdir(parents=True, exist_ok=True)
                    out_path = custom_out
                    out_filename = custom_out.name
                else:
                    out_filename = f"flux_test_sample{ext}"
                    out_path = output_dir / out_filename

                with open(out_path, "wb") as f_img:
                    f_img.write(image_bytes)

                output_image_rel = str(out_path.relative_to(root_dir)).replace("\\", "/")
                status = "PASSED"
                detail_notes = f"Image generated successfully ({len(image_bytes):,} bytes)"
                print(f"[✓] Status             : PASSED in {duration_s}s")
                print(f"[✓] Saved Test Image   : {out_path} ({len(image_bytes):,} bytes)")
            else:
                status = "FAILED"
                if not detail_notes:
                    detail_notes = "No valid image data extracted from response"
                print(f"[✗] Status             : FAILED in {duration_s}s ({detail_notes})")

    except urllib.error.HTTPError as e:
        duration_s = round(time.time() - start_time, 2)
        status = "FAILED"
        err_msg = f"HTTP {e.code}: {e.reason}"
        try:
            err_data = json.loads(e.read().decode("utf-8"))
            if "errors" in err_data:
                err_msg = f"HTTP {e.code}: {err_data['errors']}"
        except Exception:
            pass
        detail_notes = sanitize_text(err_msg, secrets)
        print(f"[✗] HTTP Error ({duration_s}s) : {detail_notes}")

    except urllib.error.URLError as e:
        duration_s = round(time.time() - start_time, 2)
        status = "FAILED"
        detail_notes = sanitize_text(f"Network error: {e.reason}", secrets)
        print(f"[✗] Network Error      : {detail_notes}")

    except Exception as e:
        duration_s = round(time.time() - start_time, 2)
        status = "FAILED"
        detail_notes = sanitize_text(f"Unexpected error: {str(e)}", secrets)
        print(f"[✗] Error              : {detail_notes}")

    # 4. Append audit record to runs.jsonl
    log_entry = {
        "run_id": run_id,
        "timestamp": timestamp_str,
        "test_type": "cloudflare_workers_ai_flux",
        "model": "@cf/black-forest-labs/flux-1-schnell",
        "status": status,
        "duration_s": duration_s,
        "prompt_source": prompt_source,
        "prompt_preview": prompt_preview,
        "output_image": output_image_rel,
        "notes": detail_notes,
    }

    append_run_log(runs_log_path, log_entry)
    print(f"[✓] Run Log Appended   : {runs_log_path} (Run ID: {run_id})")
    print("=" * 65)

    if status == "FAILED":
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
