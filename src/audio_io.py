"""
audio_io.py
Simple offline record/playback helpers using sounddevice + soundfile.
Same interface as Module 1's audio_io.py so both modules stay interchangeable.

Install: pip install sounddevice soundfile
"""

import sounddevice as sd
import soundfile as sf

SAMPLE_RATE = 16000  # 16kHz mono — matches what whisper-tamil-small expects


def record_audio(filepath: str, duration: float = 4.0, sample_rate: int = SAMPLE_RATE):
    """Record `duration` seconds of mono audio from the default mic and save to filepath (wav)."""
    print(f"Recording for {duration}s... speak now.")
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype="float32")
    sd.wait()
    sf.write(filepath, audio, sample_rate)
    print(f"Saved recording to {filepath}")
    return filepath


def play_audio(filepath: str):
    """Play back a wav file."""
    data, sample_rate = sf.read(filepath, dtype="float32")
    sd.play(data, sample_rate)
    sd.wait()
