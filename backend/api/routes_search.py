# backend/api/routes_search.py
from fastapi import APIRouter
from pydantic import BaseModel
from services.lightweight_search import search_similar

router = APIRouter()

class SearchRequest(BaseModel):
    query: str

@router.post("/search")
def search_endpoint(body: SearchRequest):
    """
    Lightweight semantic-ish search using token overlap.
    """
    hits = search_similar(body.query, k=5)
    # shape: { "hits": [ { "text": "...", "score": 0.57 }, ... ] }
    return {"hits": hits}
