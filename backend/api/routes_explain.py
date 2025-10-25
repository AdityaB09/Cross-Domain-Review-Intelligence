from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any
from ml.explain import explainer  # <-- import singleton

router = APIRouter()

class TextIn(BaseModel):
    text: str

@router.post("/")
def explain(inp: TextIn) -> Dict[str, Any]:
    return explainer.explain(inp.text)
