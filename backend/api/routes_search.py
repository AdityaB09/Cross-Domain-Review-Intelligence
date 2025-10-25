from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any

from ml.embed_index import index  # <-- uses the singleton we create in embed_index.py

router = APIRouter()

class Query(BaseModel):
    q: str
    k: int = 10


@router.post("/build")
def build_index() -> Dict[str, Any]:
    """
    Rebuild FAISS index from Postgres reviews table.
    """
    index.build()
    return {"status": "ok"}


@router.post("/")
def search(q: Query) -> List[Dict[str, Any]]:
    """
    Semantic search against the FAISS index.
    """
    return index.search(q.q, q.k)
