# backend/api/routes_explain.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

# We will import from services.explain if present,
# otherwise fall back to ml.explain (your earlier stub file).
try:
    from services.explain import run_explanation
except ImportError:
    # fallback if you didn't move it yet
    from ml.explain import run_explanation  # we'll define this below

router = APIRouter()

class TokenAttrib(BaseModel):
    token: str
    attribution: float

class ExplainResponse(BaseModel):
    text: str
    tokens: List[TokenAttrib]


class ExplainRequest(BaseModel):
    text: str


@router.post("/explain", response_model=ExplainResponse)
def explain(req: ExplainRequest):
    """
    Returns token-level contribution scores for the given text.
    This feeds the "Token attributions" section in the UI.
    """
    try:
        tokens = run_explanation(req.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"explain failed: {e}")

    # tokens should be list[dict{token, attribution}]
    return ExplainResponse(
        text=req.text,
        tokens=[
            TokenAttrib(token=t["token"], attribution=float(t["attribution"]))
            for t in tokens
        ],
    )
