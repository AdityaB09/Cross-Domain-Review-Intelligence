# api/routes_eda.py

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from services.explain_model import get_eda_snapshot

router = APIRouter()


class EDARow(BaseModel):
    aspect: str
    mentions: float
    avg_sentiment: float  # -1 (hate) to 1 (love)


class EDAResponse(BaseModel):
    aspects: List[EDARow]


@router.get("/eda/aspects", response_model=EDAResponse)
def get_aspect_eda():
    """
    Returns rolling aggregate of aspects we've seen across calls,
    sorted by most problematic first (most negative avg_sentiment).
    """
    snapshot = get_eda_snapshot()
    rows = [
        EDARow(
            aspect=row["aspect"],
            mentions=row["mentions"],
            avg_sentiment=row["avg_sentiment"],
        )
        for row in snapshot
    ]
    return EDAResponse(aspects=rows)
