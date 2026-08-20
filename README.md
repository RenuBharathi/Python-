# Module 2: Vocabulary & Sentence Practice

Extends Module 1 (Repeat & Speak) to cover the "Vocabulary" section of the
3-4yo notes: new words, short phrases/sentences, and re-reading (repeat
exposure) of under-practiced items.

## Folder structure
```
module2_vocab_sentence/
├── content/
│   └── vocab_phrase_list.json   # words + 2-3 word phrases (VERIFY WITH NATIVE SPEAKER)
├── src/
│   ├── audio_io.py              # record/playback
│   ├── stt.py                   # whisper-tamil-small wrapper
│   ├── scoring.py                # text-similarity scoring (words + phrases)
│   ├── storage.py               # local JSON history + exposure count tracking
│   ├── module2_vocab_sentence.py  # main loop
│   └── record_reference_audio.py  # one-time content-prep script
├── data/                        # created at runtime (reference audio, attempts, history)
└── requirements.txt
```

## Before running
1. `pip install -r requirements.txt`
2. **Verify every entry in `content/vocab_phrase_list.json` with a native Tamil
   speaker** — the current entries are placeholders/examples, same caution as
   Module 1's reference audio.
3. Run `python src/record_reference_audio.py` once to record clean human
   reference audio for each word/phrase (not TTS — same decision as Module 1).

## Run
```
cd src
python module2_vocab_sentence.py
```

## How it differs from Module 1
- **Phrases, not just single words** — `scoring.py`'s `score_similarity()`
  works unchanged for both, since it compares full strings.
- **Re-reading logic** — `storage.get_exposure_count()` tracks how many times
  each item has been attempted; `pick_next_item()` weights selection toward
  less-practiced items so nothing gets skipped, without needing a full
  spaced-repetition system yet (phase 1, keep it simple).
- Everything else (recording, transcription, star feedback, local-only
  JSON logging with no name/ID) matches Module 1's pattern exactly, so this
  can sit alongside `module1_repeat_speak.py` in the same project and share
  the same `stt.py`/`scoring.py` if you prefer one shared copy instead of two.

## Next steps
- Merge into your existing `speech_app_mvp` project folder (these files use
  the same interfaces as your Module 1 files, so they should drop in cleanly
  — just check function names match if you've since modified Module 1).
- Test with real recordings before trusting the scoring on children's voices,
  same caveat as Module 1 (clean-speech WER ≠ real-world accuracy).
- Category/word-type module (adjectives, adverbs, prepositions, WH questions)
  and the Rhyming/Phonological Awareness module are the next two areas from
  the notes — each needs a different scoring approach (keyword-match and
  phonetic-ending match respectively) rather than straight text similarity.
