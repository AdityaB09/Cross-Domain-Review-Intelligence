# backend/services/lightweight_explain.py
"""
Lightweight, no-torch fallback "model" so Render Free (512MB RAM) won't OOM.

We:
- extract aspects by scanning for common nouns / problem words
- score sentiment using simple positive/negative lexicons
- build token-level attributions so the UI pills show up

Return shape matches what the frontend expects from /explain-request.
"""

import re
from typing import List, Dict, Any, Tuple

# super tiny sentiment lexicons
POS_WORDS = {
    "good", "great", "amazing", "awesome", "love", "fast",
    "cool", "nice", "sharp", "clear", "beautiful", "gorgeous",
    "lifesaver", "excellent", "solid", "decent"
}
NEG_WORDS = {
    "bad", "terrible", "garbage", "trash", "hate", "slow",
    "overheats", "hot", "distorts", "buzzes", "crackles",
    "disgusting", "awful", "annoying", "headache", "pain",
    "dizzy", "nauseous"
}

# aspects we care about (the UI cards like "speaker quality", "camera sharpness", "overheating"...)
# map aspect label -> keywords to detect it in text
ASPECT_KEYWORDS = {
    "speaker quality": ["speaker", "audio", "sound"],
    "camera sharpness": ["camera", "photo", "picture", "image"],
    "overheating": ["overheat", "hot", "heat", "heats up", "overheats"],
    "battery life": ["battery", "charge", "charging", "drain"],
    "performance": ["slow", "lag", "laggy", "fast", "performance"],
    "overall": ["overall", "experience", "product", "phone", "it", "this"],
}

def tokenize(text: str) -> List[str]:
    # crude whitespace/punctuation split
    return re.findall(r"[A-Za-z0-9']+|[^\sA-Za-z0-9']", text)

def score_sentiment_window(tokens: List[str]) -> float:
    """
    Return sentiment score in range [-1, 1] based on word hits.
    +1 = strongly positive, -1 = strongly negative, 0 = meh.
    We'll count pos and neg hits and normalize.
    """
    pos_hits = 0
    neg_hits = 0

    # compare lowercase tokens to lexicons
    for t in tokens:
        low = t.lower().strip(".,!?")
        if low in POS_WORDS:
            pos_hits += 1
        if low in NEG_WORDS:
            neg_hits += 1

    # convert to score
    total = pos_hits + neg_hits
    if total == 0:
        return 0.0
    raw = (pos_hits - neg_hits) / total  # -1..1
    # clamp for safety
    if raw > 1.0:
        raw = 1.0
    if raw < -1.0:
        raw = -1.0
    return raw

def detect_aspects_and_scores(text: str) -> List[Dict[str, Any]]:
    """
    For each known aspect, if any of its keywords appear in the text,
    compute a local sentiment window around those mentions.
    We'll also attach a "confidence" ~ magnitude of sentiment.
    """
    toks = tokenize(text)
    lower_toks = [t.lower() for t in toks]

    aspects_out: List[Dict[str, Any]] = []

    for aspect_label, kws in ASPECT_KEYWORDS.items():
        # find all positions where any keyword matches
        hit_positions = []
        for i, t in enumerate(lower_toks):
            for kw in kws:
                # allow partial match for overheating / heats / overheats etc.
                if kw in t:
                    hit_positions.append(i)
                    break

        if not hit_positions:
            continue

        # for each hit, take a local window around that keyword and score it
        window_scores = []
        for pos in hit_positions:
            start = max(0, pos - 5)
            end = min(len(toks), pos + 6)
            window_tokens = toks[start:end]
            s = score_sentiment_window(window_tokens)
            window_scores.append(s)

        # average sentiment across mentions for that aspect
        if window_scores:
            avg_sent = sum(window_scores) / len(window_scores)
        else:
            avg_sent = 0.0

        # fake "confidence": absolute value of sentiment, clipped 0..1
        conf = min(1.0, abs(avg_sent) + 0.1)

        aspects_out.append({
            "aspect": aspect_label,
            "sentiment": float(round(avg_sent, 2)),
            "confidence": float(round(conf, 2)),
            "polarity": "positive" if avg_sent > 0.1 else "negative" if avg_sent < -0.1 else "mixed",
        })

    # If we found nothing, fall back to a generic "overall"
    if not aspects_out:
        overall_sent = score_sentiment_window(toks)
        conf = min(1.0, abs(overall_sent) + 0.1)
        aspects_out.append({
            "aspect": "overall",
            "sentiment": float(round(overall_sent, 2)),
            "confidence": float(round(conf, 2)),
            "polarity": "positive" if overall_sent > 0.1 else "negative" if overall_sent < -0.1 else "mixed",
        })

    return aspects_out

def build_token_attributions(text: str) -> List[Dict[str, Any]]:
    """
    Token-level heatmap for UI.
    We'll assign +0.4 to obviously positive tokens,
    -0.4 to obviously negative tokens,
    0.05 to everything else.
    """
    toks = tokenize(text)
    out = []
    for t in toks:
        low = t.lower().strip(".,!?")
        if low in POS_WORDS:
            score = 0.4
        elif low in NEG_WORDS:
            score = -0.4
        else:
            score = 0.05
        out.append({
            "token": t,
            "score": float(score),
        })
    return out

def run_lightweight_explain(text: str) -> Dict[str, Any]:
    """
    Main entry point. Returns the same schema that the frontend expects.

    {
      "aspects":[{aspect, sentiment, confidence, polarity}],
      "tokens":[{token, score}]
    }
    """
    aspects = detect_aspects_and_scores(text)
    tokens = build_token_attributions(text)
    return {
        "aspects": aspects,
        "tokens": tokens,
    }
