from torch.utils.data import Dataset
import torch

class ReviewDataset(Dataset):
    def __init__(self, rows, tokenizer, max_len=256, side_fx_vocab=None):
        self.rows = rows
        self.tok = tokenizer
        self.max_len = max_len
        self.side_fx_vocab = side_fx_vocab or []
        self.s2i = {s:i for i,s in enumerate(["neg","neu","pos"])}
        self.e2i = {e:i for i,e in enumerate(["low","med","high"])}
        self.fx2i = {f:i for i,f in enumerate(self.side_fx_vocab)}

    def __len__(self): return len(self.rows)

    def __getitem__(self, i):
        r = self.rows[i]
        enc = self.tok(
            r["text"], truncation=True, max_length=self.max_len,
            padding='max_length', return_tensors='pt'
        )
        y_sent = torch.tensor(self.s2i.get(r.get("sentiment","neu")), dtype=torch.long)
        y_eff  = torch.tensor(self.e2i.get(r.get("effectiveness","med")), dtype=torch.long)
        fx = r.get("side_effects", [])
        y_fx = torch.zeros(len(self.fx2i), dtype=torch.float)
        for f in fx:
            if f in self.fx2i: y_fx[self.fx2i[f]] = 1.0

        item = {k:v.squeeze(0) for k,v in enc.items()}
        item.update({"y_sent": y_sent, "y_eff": y_eff, "y_fx": y_fx})
        return item
