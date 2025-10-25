# backend/api/routes_search.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from services.semantic_index import SemanticIndex

router = APIRouter()


class SearchRequest(BaseModel):
    q: str
    k: int = 5


class SearchHit(BaseModel):
    id: str
    text: str
    score: Optional[float] = None
    domain: Optional[str] = None
    product: Optional[str] = None
    date: Optional[str] = None


class SearchResponse(BaseModel):
    results: List[SearchHit]


# create shared index instance
index = SemanticIndex()


def _do_search(req: SearchRequest) -> SearchResponse:
    q = req.q.strip()
    if not q:
        raise HTTPException(status_code=400, detail="Empty query")

    try:
        hits = index.search(q, req.k)
    except RuntimeError as e:
        # index not built or empty
        raise HTTPException(status_code=500, detail=str(e))

    cleaned: List[SearchHit] = []
    for h in hits:
        cleaned.append(
            SearchHit(
                id=str(h.get("id", "")),
                text=h.get("text", ""),
                score=h.get("score"),
                domain=h.get("domain"),
                product=h.get("product"),
                date=h.get("date"),
            )
        )

    return SearchResponse(results=cleaned)


@router.post("/", response_model=SearchResponse)
def search_root(req: SearchRequest):
    # backwards compat for POST /
    return _do_search(req)


@router.post("/search", response_model=SearchResponse)
def search_route(req: SearchRequest):
    # main endpoint (what Next.js calls via /api/search)
    return _do_search(req)
