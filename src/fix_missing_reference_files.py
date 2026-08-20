"""
fix_missing_reference_files.py
One-time fix: copies each item's first take (reference_take1.wav) from its
subfolder up into data/reference_audio/<item_id>.wav -- the flat file the
app actually plays back.

Run: python fix_missing_reference_files.py
"""

import json
import os
import shutil

CONTENT_PATH = os.path.join(os.path.dirname(__file__), "..", "content", "vocab_phrase_list.json")
REFERENCE_AUDIO_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "reference_audio")


def main():
    with open(CONTENT_PATH, "r", encoding="utf-8") as f:
        items = json.load(f)["items"]

    fixed = 0
    missing = []

    for item in items:
        item_folder = os.path.join(
            REFERENCE_AUDIO_DIR, f"{item['id']}_{item['english_gloss'].replace(' ', '_')}"
        )
        main_ref_path = os.path.join(REFERENCE_AUDIO_DIR, f"{item['id']}.wav")

        if os.path.exists(main_ref_path):
            continue

        take1_path = os.path.join(item_folder, "reference_take1.wav")
        source = None
        if os.path.exists(take1_path):
            source = take1_path
        elif os.path.isdir(item_folder):
            candidates = [f for f in os.listdir(item_folder) if f.startswith("reference_take")]
            if candidates:
                source = os.path.join(item_folder, sorted(candidates)[0])

        if source:
            shutil.copyfile(source, main_ref_path)
            print(f"Fixed {item['id']}: copied {os.path.basename(source)} -> {item['id']}.wav")
            fixed += 1
        else:
            missing.append(item['id'])

    print(f"\nFixed {fixed} item(s).")
    if missing:
        print(f"No recordings found at all for: {', '.join(missing)}")
        print("These still need to be recorded.")


if __name__ == "__main__":
    main()