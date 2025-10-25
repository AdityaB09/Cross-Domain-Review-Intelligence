# backend/api/routes_model.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from ml.sentiment_model import predict_sentiment, aspect_breakdown

router = APIRouter()

class AspectOut(BaseModel):
    aspect: str
    sentiment: str
    score: float

class PredictResponse(BaseModel):
    sentiment: str
    score: float
    aspects: List[AspectOut]

class PredictRequest(BaseModel):
    text: str

@router.post("/model/predict", response_model=PredictResponse)
def model_predict(req: PredictRequest):
    """
    Sentiment + ABSA summary.
    """
    try:
        overall = predict_sentiment(req.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"sentiment failed: {e}")

    overall_label = overall["label"].lower()
    if "pos" in overall_label:
        overall_sent = "positive"
    elif "neg" in overall_label:
        overall_sent = "negative"
    else:
        overall_sent = "neutral"

    # aspect-level
    aspects_raw = aspect_breakdown(req.text)
    aspects_typed = [
        AspectOut(
            aspect=a["aspect"],
            sentiment=a["sentiment"],
            score=float(a["score"]),
        )
        for a in aspects_raw
    ]

    return PredictResponse(
        sentiment=overall_sent,
        score=float(overall["score"]),
        aspects=aspects_typed,
    )
