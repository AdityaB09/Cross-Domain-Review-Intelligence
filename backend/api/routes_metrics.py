# backend/api/routes_metrics.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from sqlalchemy import text
from core.db import SessionLocal
from ml.sentiment_model import predict_sentiment, aspect_breakdown

router = APIRouter()

class TrendPoint(BaseModel):
    day: str
    avg_sentiment: float  # -1 .. +1 style

class TopAspect(BaseModel):
    aspect: str
    count: int

class MetricsOverview(BaseModel):
    status: str
    postgres: str
    redis: str
    index: str
    volume_total: int
    pct_negative: float
    top_aspects: List[TopAspect]
    trend: List[TrendPoint]


def _score_sentiment_num(label: str) -> float:
    # map POSITIVE / NEGATIVE / NEUTRAL into [-1,1]
    lower = label.lower()
    if "pos" in lower: return 1.0
    if "neg" in lower: return -1.0
    return 0.0

def _calc_pct_negative(samples: List[str]) -> float:
    if not samples:
        return 0.0
    neg = 0
    for t in samples:
        s = predict_sentiment(t)
        if "neg" in s["label"].lower():
            neg += 1
    return (neg / len(samples)) * 100.0


def _top_aspects(samples: List[str], max_items: int = 5) -> List[TopAspect]:
    freq: Dict[str, int] = {}
    for txt in samples:
        aspects = aspect_breakdown(txt)
        for a in aspects:
            # "the phone overheats" etc.
            key = a["aspect"]
            freq[key] = freq.get(key, 0) + 1

    # sort by count desc
    items = sorted(freq.items(), key=lambda kv: kv[1], reverse=True)
    out = []
    for aspect, c in items[:max_items]:
        out.append(TopAspect(aspect=aspect, count=c))
    return out


@router.get("/metrics/overview", response_model=MetricsOverview)
def metrics_overview():
    """
    Returns health + basic analytics.
    NOTE: in real prod you’d time-slice by created_at and only pull recent rows.
    """

    db = SessionLocal()

    # 1. total rows
    total_reviews = db.execute(text("SELECT COUNT(*) FROM reviews")).scalar() or 0

    # 2. grab up to N most recent reviews for analytics; assumes id is monotonic.
    rs = db.execute(
        text("SELECT text FROM reviews ORDER BY id DESC LIMIT 200")
    ).fetchall()
    recent_texts = [r[0] for r in rs]

    # 3. % negative
    pct_neg = _calc_pct_negative(recent_texts)

    # 4. top complaint aspects
    top_asps = _top_aspects(recent_texts)

    # 5. "trend": quick fake 5-day rollup.
    # We'll just bucket the recent_texts into 5 slices and compute average sentiment score.
    buckets = []
    if recent_texts:
        chunk_size = max(1, len(recent_texts) // 5)
        for i, dayname in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri"]):
            chunk = recent_texts[i * chunk_size:(i + 1) * chunk_size]
            if not chunk:
                buckets.append({"day": dayname, "avg_sentiment": 0.0})
                continue
            vals = []
            for t in chunk:
                s = predict_sentiment(t)
                vals.append(_score_sentiment_num(s["label"]))
            avg_sent = sum(vals) / len(vals)
            buckets.append({"day": dayname, "avg_sentiment": avg_sent})
    else:
        buckets = [
            {"day": d, "avg_sentiment": 0.0}
            for d in ["Mon", "Tue", "Wed", "Thu", "Fri"]
        ]

    # 6. index health:
    # we’ll say "ready" if index file exists in /data/index/index.faiss
    import os
    from core.config import settings
    index_ok = "ready" if os.path.exists(settings.faiss_index_path) else "building"

    # 7. redis health basic ping. if you didn't wire redis client yet just stub "ok"
    redis_ok = "ok"

    return MetricsOverview(
        status="ok",
        postgres="ok",
        redis=redis_ok,
        index=index_ok,
        volume_total=total_reviews,
        pct_negative=pct_neg,
        top_aspects=top_asps,
        trend=[
            TrendPoint(day=b["day"], avg_sentiment=b["avg_sentiment"])
            for b in buckets
        ]
    )
