"""
scoring.py
Phase-1 text-similarity scoring (rapidfuzz stand-in for true phonetic scoring,
per JD's "start simple" guidance). Works for single words AND short phrases —
no change needed to the underlying function, since rapidfuzz compares full strings.

Install: pip install rapidfuzz
"""

from rapidfuzz import fuzz


def score_similarity(target_text: str, transcribed_text: str) -> int:
    """
    Compare target Tamil text against transcribed attempt.
    Returns a 0-100 similarity score.
    Works the same for single words and multi-word phrases.
    """
    if not transcribed_text:
        return 0
    return round(fuzz.ratio(target_text.strip(), transcribed_text.strip()))


def score_against_variants(target_variants: list, transcribed_text: str) -> int:
    """
    Score a transcribed attempt against MULTIPLE accepted pronunciations
    (built from several reference recordings), and return the best match.
    This is what lets natural pronunciation variation count as correct,
    instead of only accepting one rigid "correct" string.
    """
    if not transcribed_text or not target_variants:
        return 0
    return max(score_similarity(v, transcribed_text) for v in target_variants)


def score_to_stars(score: int) -> int:
    """Map a 0-100 score to a 1-3 star rating for child-friendly feedback."""
    if score >= 80:
        return 3
    elif score >= 50:
        return 2
    else:
        return 1