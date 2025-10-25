from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any

from ml.sentiment_model import sentiment_model  # make sure name matches the file you just edited

router = APIRouter()

class TextIn(BaseModel):
    text: str

@router.post("/predict")
def predict(inp: TextIn) -> Dict[str, Any]:
    return sentiment_model.predict(inp.text)

@router.post("/train")
def train_model() -> Dict[str, Any]:
    # stub: we won't do training live
    return {"status": "not_implemented"}
