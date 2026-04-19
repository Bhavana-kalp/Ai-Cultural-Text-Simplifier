# backend/app/services/mcq_service.py

import random
from typing import List, Dict


def _clean_text(text: str) -> str:
    """
    Normalize text for consistent comparison/display.
    """
    return (text or "").strip()


def _generate_options(correct: str, pool: List[str], num_options: int = 4) -> List[str]:
    """
    Generate MCQ options:
    - 1 correct answer
    - remaining from pool (unique)
    """

    pool = list(set([_clean_text(p) for p in pool if p and p != correct]))

    # If pool is too small, reuse items safely
    if len(pool) < num_options - 1:
        pool = pool * 2

    wrong_options = random.sample(pool, num_options - 1)

    options = wrong_options + [correct]
    random.shuffle(options)

    return options
def extract_short_meaning(meaning: str) -> str:
    # Extract word inside quotes if present
    import re

    match = re.search(r"'(.*?)'", meaning)
    if match:
        return match.group(1)

    # fallback → take first 2–3 words
    return " ".join(meaning.split()[:3])

def generate_mcqs(glossary: List[Dict], num_questions: int = 5) -> List[Dict]:
    """
    Generate MCQs from glossary.

    Supports:
    1. Sanskrit → Hindi
    2. Hindi → Sanskrit

    Returns:
    [
      {
        "question": "...",
        "options": ["A", "B", "C", "D"],
        "answer": "correct option",
        "type": "sanskrit_to_hindi"
      }
    ]
    """

    if not glossary or len(glossary) < 2:
        return []

    # Clean glossary
    cleaned = [
        {
            "word": _clean_text(item.get("word")),
            "meaning": _clean_text(item.get("meaning"))
        }
        for item in glossary
        if item.get("word") and item.get("meaning")
    ]

    words = [item["word"] for item in cleaned]
    meanings = [item["meaning"] for item in cleaned]

    mcqs = []

    # Ensure randomness but reproducible structure
    selected_items = random.sample(cleaned, min(num_questions, len(cleaned)))

    for item in selected_items:

        word = item["word"]
        meaning = item["meaning"]
        #short_meaning = extract_short_meaning(meaning)
        # Randomly choose question type
        q_type = random.choice(["sanskrit_to_hindi", "hindi_to_sanskrit"])

        if q_type == "sanskrit_to_hindi":

            options = _generate_options(meaning, meanings)

            question = f"‘{word}’ का अर्थ क्या है?"

            mcqs.append({
                "question": question,
                "options": options,
                "answer": meaning,
                "type": q_type
            })

        else:

            options = _generate_options(word, words)

            question = f"‘{meaning}’ के लिए सही संस्कृत शब्द चुनिए।"

            mcqs.append({
                "question": question,
                "options": options,
                "answer": word,
                "type": q_type
            })

    return mcqs