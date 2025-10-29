# backend/api/routes_explain.py
from fastapi import APIRouter
from pydantic import BaseModel

from core.db import init_db_if_possible
from services.lightweight_explain import update_everything_with_text
from services.lightweight_search import add_review_text_for_search

router = APIRouter()

class ExplainRequest(BaseModel):
    text: str

@router.post("/explain-request")
def explain_endpoint(body: ExplainRequest):
    # try DB init (safe no-op if already good)
    init_db_if_possible()

    # run pipeline: aspects, sentiment, store stats (memory + Neon), etc.
    resp = update_everything_with_text(body.text)

    # add to search memory
    add_review_text_for_search(body.text)

    return resp
