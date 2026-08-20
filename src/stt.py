"""
stt.py
On-device Tamil speech-to-text using vasista22/whisper-tamil-small.
Same interface as Module 1's stt.py — one shared model, reused across modules.

Install: pip install transformers torch soundfile
First run downloads the model (~1GB) then works fully offline.
"""

from transformers import pipeline

_asr_pipeline = None


def _get_pipeline():
    global _asr_pipeline
    if _asr_pipeline is None:
        print("Loading Tamil ASR model (first run may take a while)...")
        _asr_pipeline = pipeline(
            "automatic-speech-recognition",
            model="vasista22/whisper-tamil-small",
        )
    return _asr_pipeline


def transcribe(filepath: str) -> str:
    """Transcribe a wav file and return the recognized Tamil text."""
    asr = _get_pipeline()
    result = asr(filepath)
    return result["text"].strip()
