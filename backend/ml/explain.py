import shap, torch
from .train_multilabel import MultiLabelModel

class Explainer:
    def __init__(self, base="distilbert-base-uncased", path="/app/model_multilabel.pt"):
        self.model = MultiLabelModel(base)
        self.model.load_state_dict(torch.load(path, map_location="cpu"))
        self.model.eval()
        self.tok = self.model.tok
        self.expl = shap.Explainer(self._f)  # partition/background auto

    def _f(self, texts):
        enc = self.tok(list(texts), return_tensors='pt', truncation=True, padding=True, max_length=256)
        ls, le, lf = self.model(enc["input_ids"], enc["attention_mask"])
        return torch.cat([ls.softmax(-1), le.softmax(-1), lf.sigmoid()], dim=-1).detach().numpy()

    def explain(self, text: str):
        sh = self.expl([text])
        return shap.utils._general._ensure_text(sh)
