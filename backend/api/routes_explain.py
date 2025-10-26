# api/routes_explain.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

from services.explain_model import analyze_aspects, token_attributions

router = APIRouter()


class ExplainRequest(BaseModel):
    text: str


class AspectItem(BaseModel):
    aspect: str
    sentiment: float
    confidence: float


class TokenItem(BaseModel):
    token: str
    score: float


class ExplainResponse(BaseModel):
    aspects: List[AspectItem]
    tokens: List[TokenItem]


@router.post("/explain-request", response_model=ExplainResponse)
def post_explain(req: ExplainRequest):
    """
    The frontend /explain page posts here with { text: "..." }.
    We return:
    {
      "aspects":[{"aspect":"...","sentiment":0.8,"confidence":0.9},...],
      "tokens":[{"token":"...","score":-0.7},...]
    }
    """

    user_text = req.text.strip()
    if not user_text:
        raise HTTPException(status_code=400, detail="Empty text")

    aspects_raw = analyze_aspects(user_text)
    toks_raw = token_attributions(user_text)

    # convert to pydantic models
    aspect_items = [
        AspectItem(
            aspect=a["aspect"],
            sentiment=float(a["sentiment"]),
            confidence=float(a["confidence"]),
        )
        for a in aspects_raw
    ]

    token_items = [
        TokenItem(token=t["token"], score=float(t["score"])) for t in toks_raw
    ]

    return ExplainResponse(aspects=aspect_items, tokens=token_items)
