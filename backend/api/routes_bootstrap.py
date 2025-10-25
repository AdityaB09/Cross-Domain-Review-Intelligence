from fastapi import APIRouter
from pydantic import BaseModel
from ..utils import success
from ..services.index_bootstrap import build_index

router = APIRouter(prefix="/bootstrap", tags=["bootstrap"])

class BootstrapResponse(BaseModel):
    total_seen: int
    total_indexed: int

@router.post("/from-public", response_model=BootstrapResponse)
def bootstrap_from_public():
    total, kept = build_index()
    return success(BootstrapResponse(total_seen=total, total_indexed=kept))
