# backend/services/lightweight_explain.py
import re
from typing import List, Dict, Any
from .state_store import GLOBAL_ASPECT_COUNTS, ASPECT_LOCK
from core.db import db_upsert_aspect, db_insert_review

POS_WORDS = {
    "good","great","amazing","awesome","love","fast",
    "cool","nice","sharp","clear","beautiful","gorgeous",
    "lifesaver","excellent","solid","decent","impressive","reliable"
}
NEG_WORDS = {
    "bad","terrible","garbage","trash","hate","slow",
    "overheats","overheat","hot","distorts","buzzes",
    "crackles","disgusting","awful","annoying","headache",
    "pain","dizzy","nauseous","laggy","lag","drains","drain"
}

ASPECT_KEYWORDS = {
    "speaker quality": ["speaker","audio","sound"],
    "camera sharpness": ["camera","photo","picture","image"],
    "overheating": ["overheat","overheats","overheating","hot","heat","heats"],
    "battery life": ["battery","charge","charging","drain","drains","battery life"],
    "performance": ["slow","lag","laggy","fast","performance"],
    "overall": ["overall","experience","product","phone","it","this"]
}

def _tokenize(text: str) -> List[str]:
    return re.findall(r"[A-Za-z0-9']+|[^\sA-Za-z0-9']", text)

def _sentiment_score(tokens: List[str]) -> float:
    pos_hits = 0
    neg_hits = 0
    for t in tokens:
        lw = t.lower().strip(".,!?")
        if lw in POS_WORDS:
            pos_hits += 1
        if lw in NEG_WORDS:
            neg_hits += 1
    total = pos_hits + neg_hits
    if total == 0:
        return 0.0
    raw = (pos_hits - neg_hits) / total
    if raw > 1.0: raw = 1.0
    if raw < -1.0: raw = -1.0
    return raw

def _detect_aspects(text: str) -> List[Dict[str, Any]]:
    toks = _tokenize(text)
    low_toks = [t.lower() for t in toks]
    out: List[Dict[str, Any]] = []

    for aspect_label, kws in ASPECT_KEYWORDS.items():
        hit_idx = []
        for i, tok in enumerate(low_toks):
            for kw in kws:
                if kw in tok:
                    hit_idx.append(i)
                    break
        if not hit_idx:
            continue

        scores = []
        for p in hit_idx:
            start = max(0, p - 5)
            end = min(len(toks), p + 6)
            window = toks[start:end]
            s = _sentiment_score(window)
            scores.append(s)

        avg_sent = sum(scores)/len(scores) if scores else 0.0
        conf = min(1.0, abs(avg_sent) + 0.1)
        out.append({
            "aspect": aspect_label,
            "sentiment": float(round(avg_sent, 2)),
            "confidence": float(round(conf, 2)),
            "polarity": (
                "positive" if avg_sent > 0.1
                else "negative" if avg_sent < -0.1
                else "mixed"
            ),
        })

    if not out:
        overall = _sentiment_score(toks)
        conf = min(1.0, abs(overall) + 0.1)
        out.append({
            "aspect": "overall",
            "sentiment": float(round(overall, 2)),
            "confidence": float(round(conf, 2)),
            "polarity": (
                "positive" if overall > 0.1
                else "negative" if overall < -0.1
                else "mixed"
            ),
        })

    return out

def _token_attributions(text: str) -> List[Dict[str, Any]]:
    toks = _tokenize(text)
    pills = []
    for t in toks:
        lw = t.lower().strip(".,!?")
        if lw in POS_WORDS:
            score = 0.4
        elif lw in NEG_WORDS:
            score = -0.4
        else:
            score = 0.05
        pills.append({"token": t, "score": float(score)})
    return pills

def _update_memory_aspect_agg(aspects: List[Dict[str, Any]]):
    with ASPECT_LOCK:
        for a in aspects:
            asp = a["aspect"]
            sent = float(a["sentiment"])
            row = GLOBAL_ASPECT_COUNTS.get(asp)
            if row is None:
                GLOBAL_ASPECT_COUNTS[asp] = {
                    "count": 1,
                    "total_sent": sent
                }
            else:
                row["count"] += 1
                row["total_sent"] += sent
            # also try Neon upsert
            db_upsert_aspect(asp, sent)

def update_everything_with_text(review_text: str) -> Dict[str, Any]:
    """
    Process 1 review:
    - run aspect extraction/sentiment
    - generate token attributions
    - update in-memory agg
    - push stats + raw review to Neon if available
    """
    aspects = _detect_aspects(review_text)
    tokens = _token_attributions(review_text)

    # persist raw text if DB available
    db_insert_review(review_text)

    # update memory + Neon counts
    _update_memory_aspect_agg(aspects)

    return {
        "aspects": aspects,
        "tokens": tokens,
    }
