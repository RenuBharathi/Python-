"""
record_reference_audio.py
One-time content-prep script: record clean reference audio for every
word/phrase in vocab_phrase_list.json. Run this yourself or with a native
Tamil speaker (per the Module 1 decision — NOT TTS).

Each recording is transcribed and its text is saved as an "accepted
variant" for that item. Recording a word 3 times (even with slight natural
variation in how you say it) builds a small pool of acceptable pronunciations,
so a child's attempt is compared against ALL of them — not just one rigid
"correct" string — and scored against whichever one matches best.

Run: python record_reference_audio.py
"""

import json
import os
import shutil

import audio_io
import stt

CONTENT_PATH = os.path.join(os.path.dirname(__file__), "..", "content", "vocab_phrase_list.json")
REFERENCE_AUDIO_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "reference_audio")
VARIANTS_PATH = os.path.join(os.path.dirname(__file__), "..", "content", "accepted_variants.json")


def load_variants():
    if os.path.exists(VARIANTS_PATH):
        with open(VARIANTS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_variants(variants):
    os.makedirs(os.path.dirname(VARIANTS_PATH), exist_ok=True)
    with open(VARIANTS_PATH, "w", encoding="utf-8") as f:
        json.dump(variants, f, ensure_ascii=False, indent=2)


def add_variant(item_id: str, variant_text: str):
    variants = load_variants()
    variants.setdefault(item_id, [])
    if variant_text and variant_text not in variants[item_id]:
        variants[item_id].append(variant_text)
    save_variants(variants)


def record_one_reference(item, take_num: int, item_folder: str):
    """Record a single reference take for an item, transcribe it, and store
    the transcription as an accepted variant."""
    out_path = os.path.join(item_folder, f"reference_take{take_num}.wav")
    input(f"  Take {take_num}: press Enter to record (3s)...")
    audio_io.record_audio(out_path, duration=3.0)
    audio_io.play_audio(out_path)

    keep = input("  Keep this take? (y/n): ").strip().lower()
    if keep != "y":
        input("  Press Enter to re-record...")
        audio_io.record_audio(out_path, duration=3.0)

    print("  Transcribing to add as an accepted variant...")
    variant_text = stt.transcribe(out_path)
    add_variant(item["id"], variant_text)
    print(f"  Recognized as: '{variant_text}' — added to accepted variants.\n")

    return out_path


def main(num_takes: int = 3):
    with open(CONTENT_PATH, "r", encoding="utf-8") as f:
        items = json.load(f)["items"]

    print(f"Recording reference audio for {len(items)} items.")
    print(f"Each item will be recorded {num_takes} times to capture natural")
    print("pronunciation variation. Speak clearly, one word/phrase at a time.\n")

    for item in items:
        item_folder = os.path.join(
            REFERENCE_AUDIO_DIR, f"{item['id']}_{item['english_gloss'].replace(' ', '_')}"
        )
        os.makedirs(item_folder, exist_ok=True)

        print(f"\n[{item['type']}] {item['tamil_text']}  ({item['english_gloss']})")

        existing_takes = [f for f in os.listdir(item_folder) if f.startswith("reference_take")]
        if existing_takes:
            skip = input(f"  {len(existing_takes)} take(s) already recorded. Re-record all? (y/n): ")
            if skip.strip().lower() != "y":
                continue

        # First take also becomes the single "reference" file Module 2 plays back to the child
        main_ref_path = os.path.join(REFERENCE_AUDIO_DIR, f"{item['id']}.wav")

        for take_num in range(1, num_takes + 1):
            take_path = record_one_reference(item, take_num, item_folder)
            if take_num == 1:
                shutil.copyfile(take_path, main_ref_path)

    print("\nAll reference audio recorded. Accepted variants saved to:")
    print(f"  {VARIANTS_PATH}")


if __name__ == "__main__":
    main()