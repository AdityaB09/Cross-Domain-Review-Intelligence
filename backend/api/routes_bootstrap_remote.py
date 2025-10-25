# backend/api/routes_bootstrap_remote.py
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any

from core.config import settings
from core.logging import get_logger
from services.index_bootstrap import build_index

router = APIRouter(prefix="/bootstrap", tags=["bootstrap"])
log = get_logger("bootstrap_remote")

class BootstrapOut(BaseModel):
    total_seen: int
    kept_indexed: int
    index_path: str
    meta_path: str
    sources: List[Dict[str, Any]]

@router.post("/from-remote", response_model=BootstrapOut)
def bootstrap_from_remote():
    """
    Build a FAISS index (index.faiss + meta.json) directly from remote/public
    review sources defined in settings.bootstrap_sources, without touching
    Postgres. This is your "demo / cold start" endpoint.
    """
    total_seen, kept = build_index()

    log.info(
        "bootstrap_from_remote complete total_seen={} kept={}",
        total_seen,
        kept,
    )

    return BootstrapOut(
        total_seen=total_seen,
        kept_indexed=kept,
        index_path=str(settings.faiss_index_path),
        meta_path=str(settings.faiss_meta_path),
        sources=[
            {
                "name": src.name,
                "url": src.url,
                "fmt": src.fmt,
                "domain": src.domain,
            }
            for src in settings.bootstrap_sources
        ],
    )
