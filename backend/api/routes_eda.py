# backend/api/routes_eda.py
from fastapi import APIRouter
from services.state_store import GLOBAL_ASPECT_COUNTS, ASPECT_LOCK

router = APIRouter()

@router.get("/eda/aspects")
def eda_aspects():
    """
    Return aspect analytics for dashboard charts.
    Each aspect has mentions (count) and avg_sentiment.
    """
    rows = []
    with ASPECT_LOCK:
        for aspect, row in GLOBAL_ASPECT_COUNTS.items():
            count = row["count"]
            total_sent = row["total_sent"]
            avg_sent = total_sent / count if count > 0 else 0.0
            rows.append({
                "aspect": aspect,
                "mentions": count,
                "avg_sentiment": round(avg_sent, 2),
            })
    # sort by mentions descending just so charts look nice
    rows.sort(key=lambda r: r["mentions"], reverse=True)
    return {"aspects": rows}
