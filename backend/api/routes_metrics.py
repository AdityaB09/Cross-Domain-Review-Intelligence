# backend/api/routes_metrics.py
from fastapi import APIRouter
router = APIRouter()

@router.get("/metrics-overview")
def metrics_overview():
    """
    Returns fake health/status + rolling sentiment stub,
    so Dashboard page works without DB / Prometheus.
    """
    return {
        "status": "ok",
        "postgres": "ok",
        "redis": "ok",
        "index": "ready",
        "sentiment_over_time": {
            "days": ["Mon","Tue","Wed","Thu","Fri"],
            "daily": [-0.1, 0.05, 0.2, -0.05, 0.6],
            "rolling": [0.0, 0.02, 0.08, 0.1, 0.22]
        },
        "trend_label": "sentiment improving"
    }
