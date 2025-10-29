# backend/services/lightweight_search.py
from typing import List, Dict, Any
from .state_store import GLOBAL_REVIEWS, REVIEWS_LOCK

def _tokenize_simple(s: str) -> List[str]:
    return [t.lower().strip(".,!?") for t in s.split() if t.strip()]

def _score(query_tokens: List[str], doc_tokens: List[str]) -> float:
    # simple Jaccard-like overlap score
    if not doc_tokens:
        return 0.0
    q = set(query_tokens)
    d = set(doc_tokens)
    if not q or not d:
        return 0.0
    inter = len(q & d)
    union = len(q | d)
    if union == 0:
        return 0.0
    return inter / union  # 0..1

def add_review_text_for_search(text: str):
    # Add raw text to GLOBAL_REVIEWS if not already present
    with REVIEWS_LOCK:
        GLOBAL_REVIEWS.append({"text": text})

def search_similar(query: str, k: int = 5) -> List[Dict[str, Any]]:
    q_tokens = _tokenize_simple(query)
    scored = []
    with REVIEWS_LOCK:
        for row in GLOBAL_REVIEWS:
            doc_text = row["text"]
            doc_tokens = _tokenize_simple(doc_text)
            s = _score(q_tokens, doc_tokens)
            if s > 0.0:
                scored.append({"text": doc_text, "score": s})
    # sort high to low
    scored.sort(key=lambda r: r["score"], reverse=True)
    return scored[:k]
