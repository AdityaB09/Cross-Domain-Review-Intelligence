# backend/api/routes_ingest.py
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

from core.db import init_db_if_possible
from services.lightweight_explain import update_everything_with_text
from services.lightweight_search import add_review_text_for_search

router = APIRouter()

class IngestRequest(BaseModel):
    lines: List[str]

@router.post("/ingest/jsonl")
def ingest_jsonl(body: IngestRequest):
    init_db_if_possible()
    processed = 0
    for text in body.lines:
        text_clean = text.strip()
        if not text_clean:
            continue

        # run ABSA + sentiment + persist aspect stats in Neon & memory
        update_everything_with_text(text_clean)

        # make searchable
        add_review_text_for_search(text_clean)

        processed += 1

    return {"status": "ok", "ingested": processed}
