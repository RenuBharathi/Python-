"""
interactive_app.py
Simple Tkinter GUI wrapping the Module 2 loop: play reference -> record ->
transcribe -> score -> show stars -> next word. Same underlying logic as
module2_vocab_sentence.py, just with buttons instead of terminal prompts.

Run: python interactive_app.py
"""

import os
import threading
import tkinter as tk
from tkinter import font as tkfont

import audio_io
import stt
import scoring
import storage
from module2_vocab_sentence import load_content, load_variants, pick_next_item, \
    REFERENCE_AUDIO_DIR, ATTEMPT_AUDIO_DIR

NUM_TRIALS = 3


class SpeechApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tamil Speech Practice")
        self.root.geometry("500x400")
        self.root.configure(bg="#fdf6e3")

        self.big_font = tkfont.Font(family="Noto Sans Tamil", size=32, weight="bold")
        self.med_font = tkfont.Font(family="Helvetica", size=14)
        self.status_font = tkfont.Font(family="Helvetica", size=12)

        self.items = load_content()
        self.variants = load_variants()
        self.current_item = None
        self.trial_num = 0
        self.trial_results = []
        self.recording = False

        # --- UI layout ---
        self.target_label = tk.Label(root, text="", font=self.big_font, bg="#fdf6e3", fg="#333")
        self.target_label.pack(pady=(30, 5))

        self.gloss_label = tk.Label(root, text="", font=self.med_font, bg="#fdf6e3", fg="#666")
        self.gloss_label.pack()

        self.status_label = tk.Label(root, text="", font=self.status_font, bg="#fdf6e3", fg="#444")
        self.status_label.pack(pady=15)

        self.stars_label = tk.Label(root, text="", font=self.big_font, bg="#fdf6e3", fg="#e6a817")
        self.stars_label.pack(pady=5)

        button_frame = tk.Frame(root, bg="#fdf6e3")
        button_frame.pack(pady=20)

        self.play_btn = tk.Button(button_frame, text="🔊 Play", font=self.med_font,
                                   width=10, command=self.play_reference)
        self.play_btn.grid(row=0, column=0, padx=10)

        self.record_btn = tk.Button(button_frame, text="🎤 Record", font=self.med_font,
                                     width=10, bg="#8fbf7f", command=self.start_recording)
        self.record_btn.grid(row=0, column=1, padx=10)

        self.next_btn = tk.Button(button_frame, text="Next ➜", font=self.med_font,
                                   width=10, command=self.next_word, state=tk.DISABLED)
        self.next_btn.grid(row=0, column=2, padx=10)

        self.load_next_item()

    def load_next_item(self):
        if not self.items:
            self.target_label.config(text="No recorded words yet.")
            self.gloss_label.config(text="Run record_reference_audio.py or import_mobile_recordings.py first.")
            self.record_btn.config(state=tk.DISABLED)
            return

        self.current_item = pick_next_item(self.items)
        self.trial_num = 0
        self.trial_results = []

        self.target_label.config(text=self.current_item["tamil_text"])
        self.gloss_label.config(text=f"({self.current_item['english_gloss']})")
        self.status_label.config(text=f"Trial 0/{NUM_TRIALS} — press Record when ready")
        self.stars_label.config(text="")
        self.record_btn.config(state=tk.NORMAL)
        self.next_btn.config(state=tk.DISABLED)

    def play_reference(self):
        ref_path = os.path.join(REFERENCE_AUDIO_DIR, f"{self.current_item['id']}.wav")
        if not os.path.exists(ref_path):
            self.status_label.config(text="No reference audio for this word yet.")
            return
        threading.Thread(target=audio_io.play_audio, args=(ref_path,), daemon=True).start()

    def start_recording(self):
        if self.recording or self.trial_num >= NUM_TRIALS:
            return
        self.recording = True
        self.record_btn.config(state=tk.DISABLED)
        self.trial_num += 1
        self.status_label.config(text=f"Trial {self.trial_num}/{NUM_TRIALS} — recording, speak now...")
        threading.Thread(target=self._record_and_score, daemon=True).start()

    def _record_and_score(self):
        item_folder = os.path.join(
            ATTEMPT_AUDIO_DIR,
            f"{self.current_item['id']}_{self.current_item['english_gloss'].replace(' ', '_')}"
        )
        os.makedirs(item_folder, exist_ok=True)
        attempt_path = os.path.join(item_folder, f"attempt{self.trial_num}.wav")

        audio_io.record_audio(attempt_path, duration=4.0)
        transcribed = stt.transcribe(attempt_path)

        target_variants = self.variants.get(self.current_item["id"], [self.current_item["tamil_text"]])
        score = scoring.score_against_variants(target_variants, transcribed)

        storage.log_attempt(
            item_id=self.current_item["id"],
            item_type=self.current_item["type"],
            target_text=self.current_item["tamil_text"],
            transcribed_text=transcribed,
            score=score,
        )

        self.trial_results.append({"trial": self.trial_num, "transcribed_text": transcribed, "score": score})

        # UI updates must happen on the main thread
        self.root.after(0, self._on_trial_done, transcribed, score)

    def _on_trial_done(self, transcribed, score):
        self.status_label.config(
            text=f"Trial {self.trial_num}/{NUM_TRIALS}: you said '{transcribed}' — {score}/100"
        )
        self.recording = False

        if self.trial_num >= NUM_TRIALS:
            best = max(self.trial_results, key=lambda t: t["score"])
            stars = scoring.score_to_stars(best["score"])
            self.stars_label.config(text="⭐" * stars + "☆" * (3 - stars))
            self.status_label.config(text=f"Best: {best['score']}/100 (trial {best['trial']})")
            self.next_btn.config(state=tk.NORMAL)
        else:
            self.record_btn.config(state=tk.NORMAL)

    def next_word(self):
        self.load_next_item()


if __name__ == "__main__":
    root = tk.Tk()
    app = SpeechApp(root)
    root.mainloop()