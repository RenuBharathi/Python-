"""
import_mobile_recordings.py
Import reference recordings made on your phone (any format: m4a, aac, 3gp, etc.)
into the project, converting to wav and building the accepted_variants.json
file — same end result as record_reference_audio.py, but starting from files
you already recorded elsewhere instead of recording live through this laptop.

HOW TO USE:
1. On your phone, record each word/phrase 3 times (3 separate files).
2. Name each file exactly:  <item_id>_take<N>.<any_extension>
   Example, for w09 (naai/dog), recorded 3 times:
     w09_take1.m4a
     w09_take2.m4a
     w09_take3.m4a
3. Put ALL these files (for every item) into one folder, e.g.:
     D:\module2_vocab_sentence\phone_recordings\
4. Transfer that folder from phone to laptop (USB / Drive / WhatsApp / etc.)
5. Run this script, pointing it at that folder:
     python import_mobile_recordings.py "D:\module2_vocab_sentence\phone_recordings"

Requires ffmpeg installed and on PATH (for format conversion).

Run: python import_mobile_recordings.py <path_to_folder_of_recordings>
"""

import json
import os
import re
import shutil
import subprocess
import sys

import stt

REFERENCE_AUDIO_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "reference_audio")
VARIANTS_PATH = os.path.join(os.path.dirname(__file__), "..", "content", "accepted_variants.json")
CONTENT_PATH = os.path.join(os.path.dirname(__file__), "..", "content", "vocab_phrase_list.json")

FILENAME_PATTERN = re.compile(r"^(?P<item_id>\w+)_take(?P<take_num>\d+)\.\w+$", re.IGNORECASE)


def load_content_lookup():
    with open(CONTENT_PATH, "r", encoding="utf-8") as f:
        items = json.load(f)["items"]
    return {item["id"]: item for item in items}


def load_variants():
    if os.path.exists(VARIANTS_PATH):
        with open(VARIANTS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_variants(variants):
    os.makedirs(os.path.dirname(VARIANTS_PATH), exist_ok=True)
    with open(VARIANTS_PATH, "w", encoding="utf-8") as f:
        json.dump(variants, f, ensure_ascii=False, indent=2)


def add_variant(variants, item_id, variant_text):
    variants.setdefault(item_id, [])
    if variant_text and variant_text not in variants[item_id]:
        variants[item_id].append(variant_text)


def convert_to_wav(src_path: str, dst_path: str):
    """Convert any audio format to 16kHz mono wav using ffmpeg."""
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    result = subprocess.run(
        ["ffmpeg", "-y", "-i", src_path, "-ar", "16000", "-ac", "1", dst_path],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed on {src_path}:\n{result.stderr}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python import_mobile_recordings.py <path_to_folder_of_recordings>")
        sys.exit(1)

    source_folder = sys.argv[1]
    if not os.path.isdir(source_folder):
        print(f"Folder not found: {source_folder}")
        sys.exit(1)

    content_lookup = load_content_lookup()
    variants = load_variants()

    files = sorted(os.listdir(source_folder))
    matched = 0
    skipped = []

    for filename in files:
        match = FILENAME_PATTERN.match(filename)
        if not match:
            skipped.append(filename)
            continue

        item_id = match.group("item_id")
        take_num = match.group("take_num")

        if item_id not in content_lookup:
            print(f"  [!] {filename}: item_id '{item_id}' not found in content list — skipping")
            continue

        item = content_lookup[item_id]
        item_folder = os.path.join(
            REFERENCE_AUDIO_DIR, f"{item_id}_{item['english_gloss'].replace(' ', '_')}"
        )
        dst_wav = os.path.join(item_folder, f"reference_take{take_num}.wav")

        src_path = os.path.join(source_folder, filename)
        print(f"Converting {filename} -> {dst_wav}")
        convert_to_wav(src_path, dst_wav)

        if take_num == "1":
            main_ref_path = os.path.join(REFERENCE_AUDIO_DIR, f"{item_id}.wav")
            shutil.copyfile(dst_wav, main_ref_path)

        variant_text = stt.transcribe(dst_wav)
        add_variant(variants, item_id, variant_text)
        print(f"  Recognized as: '{variant_text}' — added as accepted variant")

        matched += 1

    save_variants(variants)

    print(f"\nImported {matched} recordings.")
    if skipped:
        print(f"Skipped {len(skipped)} file(s) that didn't match the naming pattern:")
        for f in skipped:
            print(f"  - {f}")
        print("Expected pattern: <item_id>_take<N>.<extension>  e.g. w09_take1.m4a")

    print(f"\nAccepted variants saved to: {VARIANTS_PATH}")


if __name__ == "__main__":
    main()