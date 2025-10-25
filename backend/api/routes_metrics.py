# backend/api/routes_metrics.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta

from sqlalchemy import text
from core.db import SessionLocal
from ml.sentiment_model import predict_sentiment  # we'll define this stable helper

router = APIRouter()

# ---------- response models ----------

class TrendPoint(BaseModel):
    day: str  # "2025-10-25"
    avg_sentiment: float

class MetricsOverview(BaseModel):
    total_reviews: int
    avg_sentiment: float
    pct_negative: float
    top_aspects: List[str]
    trend: List[TrendPoint]


# ---------- helpers ----------

def _extract_aspects_stub(review_text: str) -> List[str]:
    """
    Placeholder aspect extraction.
    You already do similar logic for Explain / ABSA.
    We reuse that style for Dashboard's "top complaint topics".
    """
    aspects = []
    lower = review_text.lower()

    if "battery" in lower:
        aspects.append("battery")
    if "charge" in lower or "charging" in lower:
        aspects.append("charging")
    if "overheat" in lower or "hot" in lower:
        aspects.append("overheating")
    if "speaker" in lower or "audio" in lower:
        aspects.append("speaker")
    if "nauseous" in lower or "nausea" in lower:
        aspects.append("nausea")
    if "headache" in lower or "dizzy" in lower or "light headed" in lower:
        aspects.append("side effects")

    # dedupe
    return list(dict.fromkeys(aspects))


def _calc_sentiment_stub(text_val: str) -> float:
    """
    Fallback if ml.sentiment_model didn't get wired with HF pipeline.
    Convention:
      +1.0 = very positive
      0.0 = neutral
      -1.0 = very negative
    We'll look for keywords just like in explain.py.
    """
    pos_words = {"great","amazing","love","fantastic","excellent","sharp","perfect"}
    neg_words = {"garbage","slow","overheats","buzzes","nauseous","terrible","bad","hot"}

    score = 0.0
    tokens = text_val.lower().split()
    for t in tokens:
        if t.strip(",.!?;:") in pos_words:
            score += 1.0
        if t.strip(",.!?;:") in neg_words:
            score -= 1.0

    # normalize: cap between -1 and +1
    if score > 1.0: score = 1.0
    if score < -1.0: score = -1.0
    return score


def _score_sentiment(text_val: str) -> float:
    """
    Try your real sentiment model first. If that raises or returns None,
    fall back to keyword heuristic.
    """
    try:
        out = predict_sentiment(text_val)
        # expect something like {"label": "POSITIVE", "score": 0.93}
        label = out.get("label","").lower()
        if "pos" in label:
            return min(1.0, float(out.get("score", 0.5)) * 2.0)  # ~0.0-1.0
        elif "neg" in label:
            return -min(1.0, float(out.get("score", 0.5)) * 2.0)
        else:
            return 0.0
    except Exception:
        return _calc_sentiment_stub(text_val)


@router.get("/metrics/overview", response_model=MetricsOverview)
def metrics_overview():
    """
    Returns aggregate metrics for dashboard.
    We'll:
    - pull recent reviews from Postgres
    - compute sentiment per review
    - produce summary stats
    """

    # how far back we look
    days_back = 5
    since = datetime.utcnow() - timedelta(days=days_back)

    # NOTE: if you don't have created_at in your schema, we just grab N latest rows instead.
    # We'll handle both paths.
    db = SessionLocal()

    # 1. try to select recent rows w/ created_at
    rows = []
    try:
        q = text("""
            SELECT id, text, rating,
                   COALESCE(created_at, NOW()) AS ts
            FROM reviews
            ORDER BY ts DESC
            LIMIT 200
        """)
        res = db.execute(q)
        for r in res:
            rows.append({
                "id": r.id,
                "text": r.text,
                "rating": float(r.rating) if r.rating is not None else None,
                "ts": r.ts,
            })
    except Exception as e:
        db.close()
        raise HTTPException(status_code=500, detail=f"DB error: {e}")

    db.close()

    if not rows:
        return MetricsOverview(
            total_reviews=0,
            avg_sentiment=0.0,
            pct_negative=0.0,
            top_aspects=[],
            trend=[],
        )

    # compute per-row sentiment + aspects
    sentiments: list[float] = []
    aspects_counter: dict[str,int] = {}
    bucket_by_day: dict[str, list[float]] = {}  # "YYYY-MM-DD" -> list of scores

    for r in rows:
        txt = r["text"] or ""
        sent_score = _score_sentiment(txt)
        sentiments.append(sent_score)

        # track aspects
        for asp in _extract_aspects_stub(txt):
            aspects_counter[asp] = aspects_counter.get(asp, 0) + 1

        # bucket by day
        day_key = r["ts"].strftime("%Y-%m-%d")
        bucket_by_day.setdefault(day_key, []).append(sent_score)

    # aggregate sentiment summary
    avg_sent = sum(sentiments) / len(sentiments)

    neg_count = sum(1 for s in sentiments if s < -0.2)
    pct_negative = (neg_count / len(sentiments)) * 100.0

    # top 3 complaint topics (sorted desc by count)
    top_aspects = sorted(
        aspects_counter.items(), key=lambda kv: kv[1], reverse=True
    )
    top_aspects = [a for (a, c) in top_aspects[:3]]

    # trend: avg sentiment per day, sorted by day asc
    trend_points = []
    for day_key in sorted(bucket_by_day.keys()):
        vals = bucket_by_day[day_key]
        d_avg = sum(vals)/len(vals)
        trend_points.append(
            TrendPoint(day=day_key, avg_sentiment=d_avg)
        )

    return MetricsOverview(
        total_reviews=len(rows),
        avg_sentiment=round(avg_sent, 3),
        pct_negative=round(pct_negative, 1),
        top_aspects=top_aspects,
        trend=trend_points,
    )
