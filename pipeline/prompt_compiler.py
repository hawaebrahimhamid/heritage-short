#!/usr/bin/env python3
"""
Compiles storyboard.json shots into production prompt manifests and subtitle files.
"""

import json
import sys
from pathlib import Path


def compile_storyboard(input_path: str, output_path: str):
    in_file = Path(input_path)
    if not in_file.exists():
        print(f"Error: {input_path} not found", file=sys.stderr)
        sys.exit(1)

    with open(in_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    prompts = []
    subtitles = []

    for shot in data.get("shots", []):
        shot_id = shot["shot_id"]
        start_t = shot.get("start_time_s", 0)
        dur = shot.get("duration_s", 0)
        end_t = start_t + dur

        # Format visual prompt with camera and stylistic anchors
        visual_prompt = (
            f"{shot['visual_prompt']}, Shot Type: {shot['camera']['shot_type']}, "
            f"Movement: {shot['camera']['movement']}, Lens: {shot['camera']['lens']}"
        )

        prompts.append({
            "shot_id": shot_id,
            "scene_name": shot["scene_name"],
            "duration_s": dur,
            "visual_prompt": visual_prompt,
            "negative_prompt": shot.get("negative_prompt", ""),
            "audio": shot.get("audio", {})
        })

        # Basic subtitle line
        if shot["audio"].get("voiceover_english"):
            subtitles.append({
                "index": shot_id,
                "start_s": start_t,
                "end_s": end_t,
                "amharic": shot["audio"]["voiceover_amharic"],
                "english": shot["audio"]["voiceover_english"]
            })

    output_manifest = {
        "film_title": data.get("film_title"),
        "total_shots": len(prompts),
        "prompts": prompts,
        "subtitles": subtitles
    }

    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(output_manifest, f, indent=2, ensure_ascii=False)

    print(f"✓ Compiled {len(prompts)} shot manifests to {output_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Compile prompts and subtitle manifests.")
    parser.add_argument("--input", default="storyboard.json", help="Path to input storyboard.json")
    parser.add_argument("--output", default="outputs/prompts.json", help="Path to output prompts file")
    args = parser.parse_args()

    compile_storyboard(args.input, args.output)
