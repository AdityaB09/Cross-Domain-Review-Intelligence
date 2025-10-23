from fastapi import APIRouter
from pydantic import BaseModel
from ml.explain import Explainer

router = APIRouter()
explainer = Explainer()

class TextIn(BaseModel):
    text: str

@router.post("/")
def explain(inp: TextIn):
    sh = explainer.explain(inp.text)
    # tokens + aggregate value per token
    d = [{"token": t, "value": float(v)} for t, v in zip(sh.data[0], sh.values[0].sum(axis=1))]
    return {"tokens": d}
