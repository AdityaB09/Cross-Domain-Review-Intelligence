# backend/api/routes_ingest.py
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

from services.lightweight_explain import run_lightweight_explain
from services.lightweight_search import add_review_text_for_search

router = APIRouter()

class IngestRequest(BaseModel):
    lines: List[str]

@router.post("/ingest/jsonl")
def ingest_jsonl(body: IngestRequest):
    """
    Lightweight ingest: you send a list of review texts.
    We update global EDA + global search cache.
    """
    processed = 0
    for text in body.lines:
        text_clean = text.strip()
        if not text_clean:
            continue
        # update aspect aggregates
        run_lightweight_explain(text_clean)
        # store for search
        add_review_text_for_search(text_clean)
        processed += 1

    return {"status": "ok", "ingested": processed}
