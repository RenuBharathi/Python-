"""
fix_model_config.py
ONE-TIME FIX: directly patches the cached generation_config.json file for
the Tamil Whisper model on disk.

Run ONCE: python fix_model_config.py
"""

import glob
import json
import os

cache_pattern = os.path.expanduser(
    "~/.cache/huggingface/hub/models--vasista22--whisper-tamil-small/snapshots/*/generation_config.json"
)

matches = glob.glob(cache_pattern)

if not matches:
    print("Could not find the cached generation_config.json automatically.")
    print(f"Looked in: {cache_pattern}")
    print("The model may be cached in a different location. Check:")
    print(r"  %USERPROFILE%\.cache\huggingface\hub")
else:
    for path in matches:
        print(f"Found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            config = json.load(f)

        before = config.get("suppress_tokens")
        config["suppress_tokens"] = None

        with open(path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

        print(f"  Changed suppress_tokens: {before} -> None")
    print("\nDone. This should fix the crash permanently.")