# ml/sentiment_model.py
from typing import Dict, Any, List
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import spacy

_MODEL_NAME = "distilbert-base-uncased-finetuned-sst-2-english"

class SentimentAspectModel:
    def __init__(self):
        # load tiny CPU-friendly HF model
        self.tokenizer = AutoTokenizer.from_pretrained(_MODEL_NAME)
        self.model = AutoModelForSequenceClassification.from_pretrained(_MODEL_NAME)
        self.model.eval()

        # load spaCy noun chunker
        # make sure container runs:
        #   python -m spacy download en_core_web_sm
        self.nlp = spacy.load("en_core_web_sm")

        # distilbert sst2: 0 = NEGATIVE, 1 = POSITIVE
        self.id2label = {0: "negative", 1: "positive"}

    def _classify_text(self, text: str) -> Dict[str, Any]:
        """
        Return {'sentiment': 'positive'|'negative', 'score': confidence 0..1}
        """
        enc = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=256,
            padding=False,
        )

        with torch.no_grad():
            out = self.model(**enc)
            logits = out.logits  # [1,2]
            probs = F.softmax(logits, dim=-1)[0]  # [2]

        best_id = int(torch.argmax(probs).item())
        best_label = self.id2label[best_id]
        best_score = float(probs[best_id].item())

        return {
            "sentiment": best_label,
            "score": best_score,
        }

    def _extract_aspects(self, text: str) -> List[str]:
        """
        Heuristic aspect candidates by noun chunks.
        e.g. "battery life", "the charging", "the speaker"
        We'll lowercase + dedupe.
        """
        doc = self.nlp(text)
        out: List[str] = []
        for chunk in doc.noun_chunks:
            cand = chunk.text.strip(" ,.!?;:\"'()[]").lower()
            if len(cand) < 3:
                continue
            if cand in ("i","you","it","he","she","we","they"):
                continue
            if cand not in out:
                out.append(cand)
        return out

    def _score_aspect_in_context(self, aspect: str, full_text: str) -> Dict[str, Any]:
        """
        Zero/low-shot ABSA trick:
        we feed model "Aspect: {aspect}. Opinion: {full_text}"
        and classify sentiment.
        """
        conditioned = f"Aspect: {aspect}. Opinion: {full_text}"
        res = self._classify_text(conditioned)
        return {
            "aspect": aspect,
            "sentiment": res["sentiment"],
            "score": res["score"],
        }

    def predict(self, text: str) -> Dict[str, Any]:
        """
        This is what /model/predict returns via routes_model.py.
        Shape MUST match what frontend is already using:
        {
          "sentiment": "...",
          "score": float,
          "aspects": [
            {"aspect":"...","sentiment":"...","score":float},
            ...
          ]
        }
        """
        overall = self._classify_text(text)
        aspects_raw = self._extract_aspects(text)

        aspect_details: List[Dict[str, Any]] = []
        for asp in aspects_raw:
            aspect_details.append(self._score_aspect_in_context(asp, text))

        # if the same aspect phrase repeats, keep highest-confidence
        best_by_aspect: Dict[str, Dict[str, Any]] = {}
        for a in aspect_details:
            k = a["aspect"]
            if (k not in best_by_aspect) or (a["score"] > best_by_aspect[k]["score"]):
                best_by_aspect[k] = a

        return {
            "sentiment": overall["sentiment"],
            "score": overall["score"],
            "aspects": list(best_by_aspect.values()),
        }

# singleton instance imported by routes_model.py
sentiment_model = SentimentAspectModel()
