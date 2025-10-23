import spacy
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch

class ABSA:
    def __init__(self, base="distilbert-base-uncased"):
        self.nlp = spacy.load("en_core_web_sm")
        self.tok = AutoTokenizer.from_pretrained(base)
        self.cls = AutoModelForSequenceClassification.from_pretrained(base, num_labels=3)
        self.labels = ["neg","neu","pos"]

    def extract(self, text: str):
        doc = self.nlp(text)
        aspects = [ent.text for ent in doc.ents]  # simple; replace with custom aspect NER as needed
        out = []
        for a in aspects:
            pair = f"[ASPECT] {a} [TEXT] {text}"
            enc = self.tok(pair, return_tensors='pt', truncation=True, max_length=256)
            with torch.no_grad():
                logits = self.cls(**enc).logits.softmax(-1).squeeze().tolist()
            pol = self.labels[int(max(range(3), key=lambda i: logits[i]))]
            out.append({"aspect": a, "polarity": pol, "scores": logits})
        return out
