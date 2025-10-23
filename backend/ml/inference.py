import torch
from transformers import AutoTokenizer
from .train_multilabel import MultiLabelModel
from .labels import SIDE_FX

class Predictor:
    def __init__(self, path="/app/model_multilabel.pt", base="distilbert-base-uncased"):
        self.model = MultiLabelModel(base)
        self.model.load_state_dict(torch.load(path, map_location="cpu"))
        self.model.eval()
        self.tok = self.model.tok

    @torch.no_grad()
    def predict(self, text: str):
        enc = self.tok(text, return_tensors='pt', truncation=True, max_length=256)
        ls, le, lf = self.model(enc["input_ids"], enc["attention_mask"])
        return {
          "sentiment": ["neg","neu","pos"][ls.argmax(-1).item()],
          "effectiveness": ["low","med","high"][le.argmax(-1).item()],
          "side_effects": [f for i,f in enumerate(SIDE_FX) if lf.sigmoid().squeeze()[i].item()>0.5],
        }
