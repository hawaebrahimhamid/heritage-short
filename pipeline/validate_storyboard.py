#!/usr/bin/env python3
"""
Validates storyboard.json against schema/storyboard.schema.json and checks timing invariants.
"""

import sys
import json
from pathlib import Path


def validate_storyboard(storyboard_path: str, schema_path: str) -> bool:
    sb_file = Path(storyboard_path)
    sc_file = Path(schema_path)

    if not sb_file.exists():
        print(f"Error: Storyboard file '{storyboard_path}' not found.", file=sys.stderr)
        return False

    with open(sb_file, "r", encoding="utf-8") as f:
        try:
            storyboard = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in '{storyboard_path}': {e}", file=sys.stderr)
            return False

    # Optional jsonschema library validation if installed
    try:
        import jsonschema

        if sc_file.exists():
            with open(sc_file, "r", encoding="utf-8") as f:
                schema = json.load(f)
            jsonschema.validate(instance=storyboard, schema=schema)
            print("✓ JSON schema validation passed.")
    except ImportError:
        print("Notice: 'jsonschema' package not installed; running fallback invariant checks.")
    except Exception as e:
        print(f"Schema Validation Failed: {e}", file=sys.stderr)
        return False

    # Perform structural and timing invariant assertions
    shots = storyboard.get("shots", [])
    if len(shots) != 8:
        print(f"Error: Expected exactly 8 shots, found {len(shots)}.", file=sys.stderr)
        return False

    total_duration = sum(shot.get("duration_s", 0) for shot in shots)
    target_duration = storyboard.get("target_total_duration_s", 72)
    print(f"✓ Total calculated duration: {total_duration:.1f}s (Target: {target_duration}s)")

    if abs(total_duration - target_duration) > 2.0:
        print(f"Warning: Total duration ({total_duration}s) deviates from target ({target_duration}s).")

    # Verify AI end card presence on final shot
    last_shot = shots[-1]
    if not last_shot.get("is_end_card", False):
        print("Warning: Last shot (Shot 8) is not marked as is_end_card=true.")

    print(f"✓ Storyboard '{storyboard.get('film_title')}' successfully verified.")
    return True


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Validate storyboard integrity.")
    parser.add_argument("--storyboard", default="storyboard.json", help="Path to storyboard.json")
    parser.add_argument("--schema", default="schema/storyboard.schema.json", help="Path to schema JSON")
    args = parser.parse_args()

    success = validate_storyboard(args.storyboard, args.schema)
    sys.exit(0 if success else 1)
