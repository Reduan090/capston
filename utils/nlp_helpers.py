# utils/nlp_helpers.py
import spacy
from typing import List
from config import logger

nlp = spacy.load("en_core_web_sm")

def extract_topics(text: str, top_n: int = 10) -> List[str]:
    """Extract key topics using spaCy."""
    try:
        doc = nlp(text)
        keywords = [ent.text for ent in doc.ents] + [token.lemma_ for token in doc if token.pos_ in ["NOUN", "PROPN"] and not token.is_stop]
        from collections import Counter
        return [word for word, count in Counter(keywords).most_common(top_n)]
    except Exception as e:
        logger.error(f"NLP error: {e}")
        return []