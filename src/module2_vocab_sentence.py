"""
module2_vocab_sentence.py
Module 2: Vocabulary & Sentence practice.

Same loop pattern as Module 1 (Repeat & Speak):
  play reference -> record attempt -> transcribe -> score -> feedback -> log

Includes:
  - handles both single words and short phrases from the same content list
  - "re-reading": tracks how many times each item has been attempted, and
    surfaces items with low exposure count more often
  - scores against MULTIPLE accepted pronunciation variants (built from
    several reference recordings via record_reference_audio.py), so a
    child saying a word with natural variation isn't marked wrong just
    because it doesn't match one single rigid reference string
  - gives the child 3 attempts per round and shows the best score, so one
    bad take doesn't define the result; ALL trials are still logged

Run: python module2_vocab_sentence.py
"""

import json
import os
import random

import audio_io
import stt
import scoring
import storage

CONTENT_PATH = os.path.join(os.path.dirname(__file__), "..", "content", "vocab_phrase_list.json")
VARIANTS_PATH = os.path.join(os.path.dirname(__file__), "..", "content", "accepted_variants.json")
REFERENCE_AUDIO_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "reference_audio")
ATTEMPT_AUDIO_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "attempts")


def load_content():
    with open(CONTENT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    all_items = data["items"]

    variants = load_variants()
    available_items = [item for item in all_items if item["id"] in variants]

    if not available_items:
        print("No recorded reference audio found yet. Run record_reference_audio.py "
              "or import_mobile_recordings.py first.")
    else:
        print(f"Testing with {len(available_items)} recorded item(s) "
              f"out of {len(all_items)} total in the word list.")

    return available_items


def load_variants():
    """Accepted pronunciation variants per item_id, built during reference
    recording. Falls back to the plain target text if no variants exist yet."""
    if os.path.exists(VARIANTS_PATH):
        with open(VARIANTS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def pick_next_item(items):
    """
    Simple re-reading logic: weight selection toward items with fewer past
    exposures, so new/under-practiced words and phrases come up more often.
    """
    weights = []
    for item in items:
        exposure = storage.get_exposure_count(item["id"])
        weights.append(1.0 / (exposure + 1))
    return random.choices(items, weights=weights, k=1)[0]


def run_round(item, num_trials: int = 3):
    ref_audio_path = os.path.join(REFERENCE_AUDIO_DIR, f"{item['id']}.wav")
    item_folder = os.path.join(
        ATTEMPT_AUDIO_DIR, f"{item['id']}_{item['english_gloss'].replace(' ', '_')}"
    )
    os.makedirs(item_folder, exist_ok=True)

    variants_by_id = load_variants()
    target_variants = variants_by_id.get(item["id"], [item["tamil_text"]])

    print(f"\n--- {item['type'].upper()} ({item['category']}) ---")
    print(f"Target: {item['tamil_text']}  ({item['english_gloss']})")

    if os.path.exists(ref_audio_path):
        audio_io.play_audio(ref_audio_path)
    else:
        print(f"[No reference audio found at {ref_audio_path} — record it first with "
              f"record_reference_audio.py]")

    trial_results = []
    for trial_num in range(1, num_trials + 1):
        attempt_audio_path = os.path.join(item_folder, f"attempt{trial_num}.wav")
        input(f"\nTrial {trial_num}/{num_trials} — press Enter, then repeat what you heard...")
        audio_io.record_audio(attempt_audio_path, duration=4.0)

        transcribed = stt.transcribe(attempt_audio_path)
        score = scoring.score_against_variants(target_variants, transcribed)
        print(f"  You said: {transcribed}  →  Score: {score}/100")

        trial_results.append({
            "trial": trial_num,
            "transcribed_text": transcribed,
            "score": score,
        })

    best = max(trial_results, key=lambda t: t["score"])
    stars = scoring.score_to_stars(best["score"])

    print(f"\nBest attempt (trial {best['trial']}): {best['transcribed_text']}")
    print(f"Score: {best['score']}/100  {'⭐' * stars}")

    for t in trial_results:
        storage.log_attempt(
            item_id=item["id"],
            item_type=item["type"],
            target_text=item["tamil_text"],
            transcribed_text=t["transcribed_text"],
            score=t["score"],
        )


def main():
    items = load_content()
    print("Module 2: Vocabulary & Sentence Practice")
    print("Press Ctrl+C at any time to stop.\n")

    while True:
        item = pick_next_item(items)
        run_round(item)
        again = input("\nPlay another? (y/n): ").strip().lower()
        if again != "y":
            break

    print("Session ended. Progress saved.")


if __name__ == "__main__":
    main()