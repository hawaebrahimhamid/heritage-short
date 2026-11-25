#!/usr/bin/env python3
"""
pipeline/generate_narration.py
------------------------------
Generates Amharic voiceover narration audio (.wav) for all 8 shots in storyboard.json
using the Gemini TTS model (gemini-2.5-flash-preview-tts) configured in .env.

What this script does step-by-step:
1. Loads API credentials safely from `.env` without printing or leaking secrets.
2. Reads the 8 shots and their `voiceover_amharic` text from `storyboard.json` (read-only).
3. Calls the Gemini TTS API for each shot and converts the raw 24kHz PCM audio into standard .wav files:
   outputs/narration_01.wav through outputs/narration_08.wav.
4. Assembles a combined master track: `outputs/radio_cut_audio.wav` timed to the storyboard.
5. Appends a complete run record to `runs.jsonl`.
"""

import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request
import wave
from datetime import datetime, timezone
from pathlib import Path


def load_env_file(env_path: Path) -> dict:
    """
    Parses key-value pairs from .env and populates os.environ
    without requiring third-party packages.
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


def load_storyboard_shots(storyboard_path: Path) -> list:
    """
    Reads shot definitions from storyboard.json strictly in read-only mode.
    """
    if not storyboard_path.exists():
        raise FileNotFoundError(f"Storyboard not found at: {storyboard_path}")

    with open(storyboard_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    shots = data.get("shots", [])
    if not shots:
        raise ValueError(f"No shots found in storyboard: {storyboard_path}")

    return shots, data.get("film_title", "Heritage Short"), data.get("target_total_duration_s", 72.0)


def generate_shot_speech(api_key: str, model: str, voice_name: str, amharic_text: str) -> bytes:
    """
    Calls the Gemini TTS API to synthesize speech for the given Amharic text.
    Returns raw 16-bit PCM 24kHz mono audio bytes.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    # Precise prompt instructing the TTS model to speak only the text transcript
    prompt = (
        f"Read the following text transcript aloud naturally, warmly, and clearly in Amharic "
        f"without any introductory or concluding commentary: {amharic_text}"
    )

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {
                "voiceConfig": {
                    "prebuiltVoiceConfig": {
                        "voiceName": voice_name
                    }
                }
            },
        },
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "User-Agent": "heritage-short-narration/1.0",
        },
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=30) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        candidates = res.get("candidates", [])
        if not candidates:
            raise RuntimeError("Gemini API returned no candidates.")

        parts = candidates[0].get("content", {}).get("parts", [])
        for part in parts:
            if "inlineData" in part:
                data_b64 = part["inlineData"].get("data", "")
                return base64.b64decode(data_b64)

    raise RuntimeError("No audio data found in Gemini response.")


def write_pcm_to_wav(pcm_bytes: bytes, output_path: Path, sample_rate: int = 24000):
    """
    Wraps raw 16-bit mono PCM bytes into a standard RIFF/WAV file.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(output_path), "wb") as wav_out:
        wav_out.setnchannels(1)       # Mono
        wav_out.setsampwidth(2)       # 16-bit = 2 bytes per sample
        wav_out.setframerate(sample_rate)
        wav_out.writeframes(pcm_bytes)


def combine_radio_cut(shot_wavs: list, shot_durations: list, output_path: Path, sample_rate: int = 24000):
    """
    Combines individual shot narration audio files into a single master 'radio cut' WAV.
    Each shot is padded with gentle silence to match the storyboard's target duration,
    ensuring the dialogue lines up with the visual storyboard pace (~72 seconds total).
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    bytes_per_second = sample_rate * 2  # 16-bit mono = 2 bytes per sample

    with wave.open(str(output_path), "wb") as master_wav:
        master_wav.setnchannels(1)
        master_wav.setsampwidth(2)
        master_wav.setframerate(sample_rate)

        for wav_path, target_duration in zip(shot_wavs, shot_durations):
            with wave.open(str(wav_path), "rb") as w_in:
                frames = w_in.readframes(w_in.getnframes())
                master_wav.writeframes(frames)

                # Calculate padding needed to reach the storyboard shot duration
                actual_duration = len(frames) / bytes_per_second
                silence_needed_s = max(0.5, target_duration - actual_duration)
                silence_frames = b"\x00\x00" * int(silence_needed_s * sample_rate)
                master_wav.writeframes(silence_frames)


def append_run_log(runs_path: Path, entry: dict):
    """
    Appends an audit record to runs.jsonl.
    """
    runs_path.parent.mkdir(parents=True, exist_ok=True)
    with open(runs_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def main():
    root_dir = Path(__file__).resolve().parent.parent
    env_file = root_dir / ".env"
    storyboard_file = root_dir / "storyboard.json"

    print("=" * 68)
    print(" Heritage Short Pipeline - Amharic Narration Generator (Gemini TTS)")
    print("=" * 68)

    # 1. Load configuration safely
    load_env_file(env_file)
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()

    # Model selection: prefer dedicated TTS preview model
    tts_model = os.getenv("GEMINI_TTS_MODEL", "gemini-2.5-flash-preview-tts").strip()
    voice_name = os.getenv("GEMINI_TTS_VOICE", "Kore").strip()  # "Kore" = warm, calm, serene female voice

    output_dir = Path(os.getenv("OUTPUT_DIR", "./outputs"))
    if not output_dir.is_absolute():
        output_dir = root_dir / output_dir

    runs_log_path = Path(os.getenv("RUNS_LOG_PATH", "./runs.jsonl"))
    if not runs_log_path.is_absolute():
        runs_log_path = root_dir / runs_log_path

    print(f"[*] Configuration File   : {env_file} ({'Found' if env_file.exists() else 'Missing'})")
    print(f"[*] GEMINI_API_KEY       : {'[CONFIGURED]' if gemini_key else '[MISSING / EMPTY]'}")
    print(f"[*] TTS Model            : {tts_model}")
    print(f"[*] Voice Setting        : {voice_name} (warm, serene matriarch tone)")
    print(f"[*] Output Directory     : {output_dir}")
    print("-" * 68)

    now_utc = datetime.now(timezone.utc)
    run_id = f"narration-{now_utc.strftime('%Y%m%d-%H%M%S')}"
    timestamp_str = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")

    if not gemini_key:
        print("[!] Error: GEMINI_API_KEY is not set in .env.")
        log_entry = {
            "run_id": run_id,
            "timestamp": timestamp_str,
            "test_type": "gemini_tts_narration",
            "status": "SKIPPED",
            "notes": "GEMINI_API_KEY is missing or empty in .env",
        }
        append_run_log(runs_log_path, log_entry)
        sys.exit(1)

    # 2. Read storyboard.json (strict read-only)
    shots, film_title, target_duration = load_storyboard_shots(storyboard_file)
    print(f"[*] Loaded Storyboard    : \"{film_title}\" ({len(shots)} shots, target {target_duration}s)")
    print("-" * 68)

    generated_wavs = []
    shot_durations = []
    shot_results = []
    overall_start_time = time.time()

    # 3. Generate narration audio for each shot
    for idx, shot in enumerate(shots, start=1):
        shot_id = shot.get("shot_id", idx)
        duration_s = float(shot.get("duration_s", 9.0))
        audio_spec = shot.get("audio", {})
        amharic_text = audio_spec.get("voiceover_amharic", "").strip()

        wav_filename = f"narration_{shot_id:02d}.wav"
        wav_path = output_dir / wav_filename

        print(f"[*] Shot {shot_id}/{len(shots)}: \"{shot.get('scene_name', '')}\"")
        preview = (amharic_text[:65] + "...") if len(amharic_text) > 65 else amharic_text
        print(f"    Script : {preview}")

        if not amharic_text:
            print("    [!] Warning: Empty voiceover_amharic text; skipping synthesis.")
            continue

        shot_start = time.time()
        try:
            pcm_data = generate_shot_speech(gemini_key, tts_model, voice_name, amharic_text)
            write_pcm_to_wav(pcm_data, wav_path, sample_rate=24000)

            elapsed = round(time.time() - shot_start, 2)
            audio_duration = round(len(pcm_data) / (24000 * 2), 2)

            generated_wavs.append(wav_path)
            shot_durations.append(duration_s)

            shot_results.append({
                "shot_id": shot_id,
                "file": f"outputs/{wav_filename}",
                "audio_duration_s": audio_duration,
                "target_duration_s": duration_s,
                "api_latency_s": elapsed,
            })
            print(f"    [✓] Generated {wav_filename} ({audio_duration}s audio in {elapsed}s)")

        except urllib.error.HTTPError as e:
            err_msg = f"HTTP {e.code}: {e.reason}"
            try:
                err_body = json.loads(e.read().decode("utf-8"))
                if "error" in err_body and "message" in err_body["error"]:
                    err_msg = f"HTTP {e.code}: {err_body['error']['message']}"
            except Exception:
                pass
            print(f"    [✗] Synthesis failed for shot {shot_id}: {err_msg}")
            sys.exit(1)
        except Exception as e:
            print(f"    [✗] Error generating shot {shot_id}: {e}")
            sys.exit(1)

        time.sleep(0.5)  # Courteous pacing between calls

    # 4. Combine into master radio cut
    radio_cut_path = output_dir / "radio_cut_audio.wav"
    print("-" * 68)
    print(f"[*] Combining {len(generated_wavs)} narration clips into master radio cut...")
    combine_radio_cut(generated_wavs, shot_durations, radio_cut_path, sample_rate=24000)

    # Calculate radio cut total duration
    with wave.open(str(radio_cut_path), "rb") as w_final:
        final_total_seconds = round(w_final.getnframes() / float(w_final.getframerate()), 2)

    total_pipeline_time = round(time.time() - overall_start_time, 2)
    print(f"[✓] Created Master Audio : {radio_cut_path}")
    print(f"[✓] Radio Cut Duration   : {final_total_seconds}s (Storyboard Target: {target_duration}s)")
    print(f"[✓] Total Pipeline Time  : {total_pipeline_time}s")
    print("-" * 68)

    # 5. Append run telemetry to runs.jsonl
    log_entry = {
        "run_id": run_id,
        "timestamp": timestamp_str,
        "film_title": film_title,
        "test_type": "gemini_tts_narration",
        "status": "COMPLETED",
        "model": tts_model,
        "voice": voice_name,
        "total_shots_synthesized": len(shot_results),
        "radio_cut_duration_s": final_total_seconds,
        "pipeline_latency_s": total_pipeline_time,
        "outputs": {
            "individual_clips": [r["file"] for r in shot_results],
            "master_radio_cut": "outputs/radio_cut_audio.wav",
        },
        "shots_detail": shot_results,
        "notes": f"Successfully generated all {len(shot_results)} Amharic narration shots and master radio cut",
    }
    append_run_log(runs_log_path, log_entry)
    print(f"[✓] Logged execution audit to {runs_log_path}")
    print("=" * 68)


if __name__ == "__main__":
    main()
