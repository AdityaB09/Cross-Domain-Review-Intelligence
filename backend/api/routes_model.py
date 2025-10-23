from fastapi import APIRouter
from pydantic import BaseModel
from ml.train_multilabel import train
from ml.inference import Predictor
from ml.absa_ner import ABSA

router = APIRouter()
predictor: Predictor | None = None
absa = ABSA()

class TextIn(BaseModel):
    text: str

@router.post("/train")
def train_model():
    r = train()
    global predictor
    predictor = Predictor()
    return r

@router.post("/predict")
def predict(inp: TextIn):
    global predictor
    if predictor is None:
      predictor = Predictor()
    y = predictor.predict(inp.text)
    y["aspects"] = absa.extract(inp.text)
    return y
