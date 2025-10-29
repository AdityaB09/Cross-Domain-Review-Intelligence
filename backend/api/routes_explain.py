# backend/api/routes_explain.py
from fastapi import APIRouter
from pydantic import BaseModel

from services.lightweight_explain import run_lightweight_explain
from services.lightweight_search import add_review_text_for_search

router = APIRouter()

class ExplainRequest(BaseModel):
    text: str

@router.post("/explain-request")
def explain_endpoint(body: ExplainRequest):
    """
    1. Run lightweight explain (no torch).
    2. Store this text as a review for future /search.
    3. Return aspects & token attributions.
    """
    resp = run_lightweight_explain(body.text)
    add_review_text_for_search(body.text)
    return resp
