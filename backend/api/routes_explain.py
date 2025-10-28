# backend/api/routes_explain.py
from fastapi import APIRouter
from pydantic import BaseModel
from services.lightweight_explain import run_lightweight_explain

router = APIRouter()

class ExplainRequest(BaseModel):
    text: str

@router.post("/explain-request")
def explain_endpoint(body: ExplainRequest):
    """
    Lightweight inference. No torch. Safe for 512MB Render free.
    """
    return run_lightweight_explain(body.text)
