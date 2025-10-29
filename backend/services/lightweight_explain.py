# backend/services/lightweight_explain.py
"""
Pure-Python fallback "model" for production on Render free tier.

- Extracts aspects by keyword
- Estimates sentiment per aspect using tiny lexicons
- Generates token attribution scores for UI

No torch, no transformers, no huggingface_hub.
"""

import re
from typing import List, Dict, Any

POS_WORDS = {
    "good", "great", "amazing", "awesome", "love", "fast",
    "cool", "nice", "sharp", "clear", "beautiful", "gorgeous",
    "lifesaver", "excellent", "solid", "decent"
}
NEG_WORDS = {
    "bad", "terrible", "garbage", "trash", "hate", "slow",
    "overheats", "overheat", "hot", "distorts", "buzzes",
    "crackles", "disgusting", "awful", "annoying", "headache",
    "pain", "dizzy", "nauseous"
}

ASPECT_KEYWORDS = {
    "speaker quality": ["speaker", "audio", "sound"],
    "camera sharpness": ["camera", "photo", "picture", "image"],
    "overheating": ["overheat", "overheats", "overheating", "hot", "heat", "heats"],
    "battery life": ["battery", "charge", "charging", "drain", "battery life"],
    "performance": ["slow", "lag", "laggy", "fast", "performance"],
    "overall": ["overall", "experience", "product", "phone", "it", "this"]
}

def _tokenize(text: str) -> List[str]:
    # split words and keep punctuation tokens
    return re.findall(r"[A-Za-z0-9']+|[^\sA-Za-z0-9']", text)

def _sentiment_score(tokens: List[str]) -> float:
    """
    Returns a float in [-1,1].
    """
    pos_hits = 0
    neg_hits = 0
    for t in tokens:
        low = t.lower().strip(".,!?")
        if low in POS_WORDS:
            pos_hits += 1
        if low in NEG_WORDS:
            neg_hits += 1

    total = pos_hits + neg_hits
    if total == 0:
        return 0.0
    raw = (pos_hits - neg_hits) / total
    if raw > 1.0:
        raw = 1.0
    if raw < -1.0:
        raw = -1.0
    return raw

def _detect_aspects(text: str) -> List[Dict[str, Any]]:
    toks = _tokenize(text)
    low_toks = [t.lower() for t in toks]
    aspects_out: List[Dict[str, Any]] = []

    for aspect_label, kws in ASPECT_KEYWORDS.items():
        hit_positions = []
        for i, tok in enumerate(low_toks):
            for kw in kws:
                if kw in tok:  # substring match is fine for "overheats"
                    hit_positions.append(i)
                    break
        if not hit_positions:
            continue

        # gather local sentiment windows
        window_scores = []
        for pos in hit_positions:
            start = max(0, pos - 5)
            end = min(len(toks), pos + 6)
            local_tokens = toks[start:end]
            s = _sentiment_score(local_tokens)
            window_scores.append(s)

        avg_sent = sum(window_scores) / len(window_scores) if window_scores else 0.0
        conf = min(1.0, abs(avg_sent) + 0.1)

        aspects_out.append({
            "aspect": aspect_label,
            "sentiment": float(round(avg_sent, 2)),
            "confidence": float(round(conf, 2)),
            "polarity": (
                "positive" if avg_sent > 0.1
                else "negative" if avg_sent < -0.1
                else "mixed"
            ),
        })

    if not aspects_out:
        overall = _sentiment_score(toks)
        conf = min(1.0, abs(overall) + 0.1)
        aspects_out.append({
            "aspect": "overall",
            "sentiment": float(round(overall, 2)),
            "confidence": float(round(conf, 2)),
            "polarity": (
                "positive" if overall > 0.1
                else "negative" if overall < -0.1
                else "mixed"
            ),
        })

    return aspects_out

def _token_attributions(text: str) -> List[Dict[str, Any]]:
    toks = _tokenize(text)
    out = []
    for t in toks:
        low = t.lower().strip(".,!?")
        if low in POS_WORDS:
            score = 0.4
        elif low in NEG_WORDS:
            score = -0.4
        else:
            score = 0.05
        out.append({"token": t, "score": float(score)})
    return out

def run_lightweight_explain(text: str) -> Dict[str, Any]:
    aspects = _detect_aspects(text)
    tokens = _token_attributions(text)
    return {
        "aspects": aspects,
        "tokens": tokens,
    }
