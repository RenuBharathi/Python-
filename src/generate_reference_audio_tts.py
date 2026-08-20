"""
generate_reference_audio_tts.py
Generate reference audio using Meta's MMS-TTS Tamil model (facebook/mms-tts-tam)
-- fully offline, on-device, no cloud API calls, so this stays compliant with
the JD's "on-device only, no cloud" requirement.

IMPORTANT CAVEATS (read before trusting this for your final app):
- This produces ONE adult-sounding voice, not a child's voice -- genuine
  child-voice TTS doesn't really exist for Tamil, on-device or otherwise.
- Quality is noticeably more robotic than cloud services like ElevenLabs.
- ALWAYS listen to and verify every generated clip with a native speaker
  before using it -- TTS mispronunciations are a real risk.

Requires: pip install transformers torch scipy

Run: python generate_reference_audio_tts.py
"""

import json
import os

import numpy as np
import torch
from scipy.io.wavfile import write as wav_write
from transformers import VitsModel, AutoTokenizer

import stt

CONTENT_PATH = os.path.join(os.path.dirname(__file__), "..", "content", "vocab_phrase_list.json")
REFERENCE_AUDIO_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "reference_audio")
VARIANTS_PATH = os.path.join(os.path.dirname(__file__), "..", "content", "accepted_variants.json")

MODEL_NAME = "facebook/mms-tts-tam"

_model = None
_tokenizer = None


def load_tts():
    global _model, _tokenizer
    if _model is None:
        print(f"Loading Tamil TTS model ({MODEL_NAME})... first run downloads it, then it's offline.")
        _model = VitsModel.from_pretrained(MODEL_NAME)
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    return _model, _tokenizer


def synthesize(text: str, out_path: str):
    model, tokenizer = load_tts()
    inputs = tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        output = model(**inputs).waveform
    audio = output.squeeze().cpu().numpy()
    audio = audio / max(np.abs(audio).max(), 1e-6) * 0.9
    wav_write(out_path, model.config.sampling_rate, (audio * 32767).astype(np.int16))


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


def main():
    with open(CONTENT_PATH, "r", encoding="utf-8") as f:
        items = json.load(f)["items"]

    variants = load_variants()

    print(f"Generating TTS reference audio for {len(items)} items.\n")
    for item in items:
        item_folder = os.path.join(
            REFERENCE_AUDIO_DIR, f"{item['id']}_{item['english_gloss'].replace(' ', '_')}"
        )
        os.makedirs(item_folder, exist_ok=True)

        main_ref_path = os.path.join(REFERENCE_AUDIO_DIR, f"{item['id']}.wav")
        take_path = os.path.join(item_folder, "reference_tts.wav")

        print(f"[{item['type']}] {item['tamil_text']}  ({item['english_gloss']}) ...", end=" ")
        synthesize(item["tamil_text"], take_path)

        import shutil
        shutil.copyfile(take_path, main_ref_path)

        recognized = stt.transcribe(take_path)
        add_variant(variants, item["id"], item["tamil_text"])
        add_variant(variants, item["id"], recognized)
        print(f"done (ASR heard: '{recognized}')")

    save_variants(variants)
    print(f"\nAll reference audio generated. Accepted variants saved to:\n  {VARIANTS_PATH}")
    print("\n>>> IMPORTANT: listen to a sample of these files yourself before trusting them.")
    print(">>> Check a few in:", REFERENCE_AUDIO_DIR)


if __name__ == "__main__":
    main()