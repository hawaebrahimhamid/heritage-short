#!/usr/bin/env python3
"""
pipeline/smoke_test.py
----------------------
A lightweight smoke test for the heritage-short project stack.

What it does:
1. Loads environment variables from `.env` (without requiring extra pip packages).
2. Verifies expected configuration keys (GEMINI_API_KEY, CLOUDFLARE_*, models, etc.).
3. Performs a lightweight connectivity check against Google Gemini API.
4. Appends a structured audit entry to `runs.jsonl`.
"""

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


def load_env_file(env_path: Path) -> dict:
    """
    Parse a simple .env file into a dictionary and populate os.environ
    if keys are not already set in the system environment.
    """
    loaded = {}
    if not env_path.exists():
        return loaded

    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Ignore comments and empty lines
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                loaded[key] = val
                # Populate os.environ if not already present
                if key not in os.environ:
                    os.environ[key] = val
    return loaded


def check_gemini_connectivity(api_key: str, model: str) -> dict:
    """
    Performs a lightweight GET request against the Gemini API to verify connectivity
    and key validity without generating tokens or incurring cost.
    """
    if not api_key:
        return {
            "status": "SKIPPED",
            "message": "GEMINI_API_KEY is empty or not configured in .env",
            "http_code": None,
        }

    # Querying the model info endpoint is lightweight and verifies authorization
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}?key={api_key}"

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "heritage-short-smoke-test/1.0"},
        method="GET",
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            status_code = response.getcode()
            body = response.read().decode("utf-8")
            data = json.loads(body)
            display_name = data.get("displayName", model)
            return {
                "status": "PASSED",
                "message": f"Successfully connected to Gemini API (Model: {display_name})",
                "http_code": status_code,
            }
    except urllib.error.HTTPError as e:
        error_msg = f"HTTP Error {e.code}: {e.reason}"
        try:
            err_body = json.loads(e.read().decode("utf-8"))
            if "error" in err_body and "message" in err_body["error"]:
                error_msg = f"HTTP {e.code}: {err_body['error']['message']}"
        except Exception:
            pass
        return {
            "status": "FAILED",
            "message": error_msg,
            "http_code": e.code,
        }
    except urllib.error.URLError as e:
        return {
            "status": "FAILED",
            "message": f"Network connection error: {e.reason}",
            "http_code": None,
        }
    except Exception as e:
        return {
            "status": "FAILED",
            "message": f"Unexpected error: {str(e)}",
            "http_code": None,
        }


def append_run_log(runs_path: Path, entry: dict):
    """
    Appends a single JSON line to the runs.jsonl log file.
    """
    runs_path.parent.mkdir(parents=True, exist_ok=True)
    with open(runs_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def main():
    root_dir = Path(__file__).resolve().parent.parent
    env_file = root_dir / ".env"

    print("=" * 60)
    print(" Heritage Short Pipeline - Environment & Gemini Smoke Test")
    print("=" * 60)

    # 1. Load .env
    env_vars = load_env_file(env_file)
    print(f"[*] Configuration file : {env_file} ({'Found' if env_file.exists() else 'Missing'})")

    # 2. Extract configuration variables
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    cloudflare_account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID", "").strip()
    cloudflare_api_token = os.getenv("CLOUDFLARE_API_TOKEN", "").strip()

    # Optional settings
    gemini_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash").strip()
    video_model = os.getenv("VIDEO_MODEL", "cinematic-v2-anchor").strip()
    audio_model = os.getenv("AUDIO_MODEL", "amharic-elder-tts-v3").strip()
    amharic_tts_provider = os.getenv("AMHARIC_TTS_PROVIDER", "local").strip()
    runs_log_path = Path(os.getenv("RUNS_LOG_PATH", "runs.jsonl"))
    if not runs_log_path.is_absolute():
        runs_log_path = root_dir / runs_log_path

    # Print summary of environment status
    print(f"[*] GEMINI_API_KEY      : {'[CONFIGURED]' if gemini_key else '[EMPTY / UNSET]'}")
    print(f"[*] CLOUDFLARE_ACCOUNT  : {'[CONFIGURED]' if cloudflare_account_id else '[EMPTY / UNSET]'}")
    print(f"[*] CLOUDFLARE_TOKEN    : {'[CONFIGURED]' if cloudflare_api_token else '[EMPTY / UNSET]'}")
    print(f"[*] GEMINI_MODEL        : {gemini_model}")
    print(f"[*] VIDEO_MODEL         : {video_model}")
    print(f"[*] AUDIO_MODEL         : {audio_model}")
    print(f"[*] AMHARIC_TTS_PROVIDER: {amharic_tts_provider}")
    print(f"[*] RUNS_LOG_PATH       : {runs_log_path}")
    print("-" * 60)

    # 3. Perform Gemini connectivity check
    print(f"[*] Running connectivity check for Gemini model: '{gemini_model}'...")
    check_result = check_gemini_connectivity(gemini_key, gemini_model)
    print(f"[*] Status : {check_result['status']}")
    print(f"[*] Detail : {check_result['message']}")
    print("-" * 60)

    # 4. Prepare structured telemetry audit record
    now_utc = datetime.now(timezone.utc)
    timestamp_str = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
    run_id = f"smoke-{now_utc.strftime('%Y%m%d-%H%M%S')}"

    log_entry = {
        "run_id": run_id,
        "timestamp": timestamp_str,
        "film_title": "Morning Barakah & The Proverb",
        "test_type": "smoke_test",
        "status": check_result["status"],
        "connectivity": {
            "gemini": {
                "model": gemini_model,
                "status": check_result["status"],
                "http_code": check_result["http_code"],
                "message": check_result["message"],
            },
            "cloudflare_configured": bool(cloudflare_account_id and cloudflare_api_token),
        },
        "models": {
            "video": video_model,
            "audio": audio_model,
            "compiler": gemini_model,
        },
        "notes": f"Automated smoke test run: {check_result['message']}",
    }

    # 5. Append entry to runs.jsonl
    append_run_log(runs_log_path, log_entry)
    print(f"[✓] Appended test result to {runs_log_path}")
    print(f"[✓] Run ID logged: {run_id}")
    print("=" * 60)

    # Return exit code: 0 if passed or gracefully skipped due to missing keys, 1 if network/API failure
    if check_result["status"] == "FAILED":
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
