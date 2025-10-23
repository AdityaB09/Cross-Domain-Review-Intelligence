import torch, mlflow
import torch.nn as nn
from torch.utils.data import DataLoader, random_split
from transformers import AutoModel, AutoTokenizer
from sqlalchemy import text
from core.db import engine
from .dataset import ReviewDataset
from .labels import SIDE_FX

class Head(nn.Module):
    def __init__(self, d):
        super().__init__()
        self.sent = nn.Linear(d, 3)
        self.eff  = nn.Linear(d, 3)
        self.fx   = nn.Linear(d, len(SIDE_FX))
    def forward(self, h):
        return self.sent(h), self.eff(h), self.fx(h)

class MultiLabelModel(nn.Module):
    def __init__(self, base="distilbert-base-uncased"):
        super().__init__()
        self.tok = AutoTokenizer.from_pretrained(base)
        self.enc = AutoModel.from_pretrained(base)
        d = self.enc.config.hidden_size
        self.head = Head(d)
    def forward(self, input_ids, attention_mask):
        h = self.enc(input_ids=input_ids, attention_mask=attention_mask).last_hidden_state[:,0]
        return self.head(h)

@torch.no_grad()
def _metrics(ls, le, lf, b):
    sent = ls.argmax(-1).eq(b["y_sent"]).float().mean().item()
    eff  = le.argmax(-1).eq(b["y_eff"]).float().mean().item()
    fx   = ((lf.sigmoid()>0.5) == (b["y_fx"]>0.5)).float().mean().item()
    return {"acc_sent":sent, "acc_eff":eff, "acc_fx":fx}

def train(run_name="cdri-multilabel", base="distilbert-base-uncased", epochs=2, bs=16, lr=3e-5):
    mlflow.set_experiment("cdri")
    with mlflow.start_run(run_name=run_name):
        model = MultiLabelModel(base)
        tok = model.tok
        with engine.begin() as conn:
            rows = [dict(x) for x in conn.execute(text("SELECT text FROM reviews ORDER BY id DESC LIMIT 2000"))]
            for r in rows:
                r.update({"sentiment":"neu","effectiveness":"med","side_effects":[]})
        ds = ReviewDataset(rows, tok, side_fx_vocab=SIDE_FX)
        n_val = max(50, int(0.1*len(ds))) if len(ds) > 50 else 10
        tr, va = random_split(ds, [max(1,len(ds)-n_val), min(n_val, len(ds)-1)])
        dl_tr = DataLoader(tr, batch_size=bs, shuffle=True)
        dl_va = DataLoader(va, batch_size=bs)

        opt = torch.optim.AdamW(model.parameters(), lr=lr)
        ce, bce = nn.CrossEntropyLoss(), nn.BCEWithLogitsLoss()

        for ep in range(epochs):
            model.train()
            for b in dl_tr:
                ls,le,lf = model(b["input_ids"], b["attention_mask"])
                loss = ce(ls, b["y_sent"]) + ce(le, b["y_eff"]) + bce(lf, b["y_fx"])
                opt.zero_grad(); loss.backward(); opt.step()
            model.eval()
            with torch.no_grad():
                b = next(iter(dl_va))
                ls,le,lf = model(b["input_ids"], b["attention_mask"])
                m = _metrics(ls,le,lf,b)
                mlflow.log_metrics({"val_"+k:v for k,v in m.items()}, step=ep)
        torch.save(model.state_dict(), "/app/model_multilabel.pt")
        mlflow.log_artifact("/app/model_multilabel.pt")
        return {"ok": True}
