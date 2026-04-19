# backend/app/services/fill_blanks_service.py

import random
from typing import List, Dict


def _clean(text: str) -> str:
    return (text or "").strip()


def _select_words(glossary: List[Dict], num_blanks: int = 4) -> List[Dict]:
    """
    Select important words for blanks
    """
    cleaned = [
        {
            "word": _clean(item.get("word")),
            "meaning": _clean(item.get("meaning"))
        }
        for item in glossary
        if item.get("word") and item.get("meaning")
    ]

    if len(cleaned) <= num_blanks:
        return cleaned

    return random.sample(cleaned, num_blanks)


def _replace_word_once(text: str, word: str, blank: str) -> str:
    """
    Replace only first occurrence of word in text.
    Handles partial matching.
    """
    idx = text.find(word)
    if idx == -1:
        return text

    return text[:idx] + blank + text[idx + len(word):]


def generate_fill_in_blanks(sanskrit_text: str, glossary: List[Dict], num_blanks: int = 4):

    import re

    text = sanskrit_text

    # Step 1: pick words
    selected = _select_words(glossary, num_blanks)

    # Step 2: find positions
    word_positions = []

    for item in selected:
        word = item["word"]
        idx = text.find(word)

        if idx != -1:
            word_positions.append((idx, item))

    # ❗ IMPORTANT: sort by position in text
    word_positions.sort(key=lambda x: x[0])

    blanks = []
    options = []

    for i, (pos, item) in enumerate(word_positions):

        word = item["word"]
        meaning = item["meaning"]

        blank_token = f"____({meaning})"

        text = text.replace(word, blank_token, 1)

        blanks.append({
            "id": i,
            "answer": word,
            "hint": meaning
        })

        options.append(word)

    # add extra options
    all_words = [g["word"] for g in glossary if g.get("word")]
    extra = list(set(all_words) - set(options))

    if len(extra) >= len(options):
        options += random.sample(extra, len(options))

    random.shuffle(options)

    return {
        "question_text": text,
        "blanks": blanks,
        "options": options
    }