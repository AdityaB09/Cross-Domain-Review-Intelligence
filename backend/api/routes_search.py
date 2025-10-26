# api/routes_search.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

from services.semantic_index import SemanticIndex

router = APIRouter()

# keep a global-ish index instance so we don't reload model every request
semantic_index = None


class SearchRequest(BaseModel):
    query: str


class SearchHit(BaseModel):
    text: str
    score: float


class SearchResponse(BaseModel):
    hits: List[SearchHit]


@router.post("/search", response_model=SearchResponse)
def post_search(req: SearchRequest):
    """
    POST /search
    body: { "query": "..." }

    returns:
    {
      "hits":[
        {"text":"...", "score":0.93},
        ...
      ]
    }
    """

    global semantic_index
    if semantic_index is None:
        try:
            semantic_index = SemanticIndex()
        except RuntimeError as e:
            # index not built yet etc.
            raise HTTPException(status_code=422, detail=str(e))

    hits_raw = semantic_index.search(req.query, top_k=5)

    # Convert raw dicts -> Pydantic
    hits = [SearchHit(text=h["text"], score=h["score"]) for h in hits_raw]

    return SearchResponse(hits=hits)
