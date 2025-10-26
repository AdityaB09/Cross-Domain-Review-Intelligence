# ml/sentiment_model.py

from typing import List, Dict, Any, Tuple, Optional
import re

########################################
# 1. Sentiment model (overall sentiment + fallback heuristic)
########################################

# We try to load a transformer sentiment pipeline at import time.
# If that fails (no internet / no weights), we fall back to a tiny heuristic.
from transformers import pipeline

_hf_pipeline = None
try:
    _hf_pipeline = pipeline(
        "sentiment-analysis",
        model="distilbert-base-uncased-finetuned-sst-2-english",
    )
except Exception:
    _hf_pipeline = None


_POS_WORDS = {
    "good", "great", "amazing", "love", "cool", "fast", "beautiful", "clear",
    "gorgeous", "perfect", "awesome", "excellent", "works", "fine", "acceptable",
    "insane", "super", "loved", "easy", "recommend", "best"
}
_NEG_WORDS = {
    "bad", "garbage", "trash", "hate", "awful", "horrible", "terrible", "broke",
    "crap", "bleed", "nauseous", "dizzy", "pain", "disgusting", "overheats",
    "hot", "unusable", "slow", "worst"
}


def _heuristic_sentiment(text: str) -> Dict[str, Any]:
    """
    Simple fallback if HF sentiment model can't load.
    Score = (#pos - #neg) / (total matches+1) -> map to label.
    """
    toks = re.findall(r"\w+", text.lower())
    pos_hits = sum(1 for t in toks if t in _POS_WORDS)
    neg_hits = sum(1 for t in toks if t in _NEG_WORDS)

    raw = pos_hits - neg_hits
    denom = (pos_hits + neg_hits) if (pos_hits + neg_hits) > 0 else 1
    confidence = abs(raw) / denom

    if raw > 0:
        label = "POSITIVE"
    elif raw < 0:
        label = "NEGATIVE"
    else:
        label = "NEUTRAL"

    return {"label": label, "score": float(min(1.0, max(0.0, confidence)))}


def predict_sentiment(text: str) -> Dict[str, Any]:
    """
    Public: returns {"label": "POSITIVE"/"NEGATIVE"/"NEUTRAL", "score": float}
    Used by:
    - /model/predict
    - /metrics/overview
    - explain_model.token_attributions()
    - explain_model.analyze_aspects() fallback
    """
    cleaned = text.strip()
    if not cleaned:
        return {"label": "NEUTRAL", "score": 0.0}

    if _hf_pipeline is not None:
        try:
            res = _hf_pipeline(cleaned)
            # Usually looks like [{'label': 'POSITIVE', 'score': 0.998...}]
            if isinstance(res, list) and len(res) > 0:
                item = res[0]
                label = item.get("label", "NEUTRAL")
                score = float(item.get("score", 0.0))
                # Normalize to POSITIVE / NEGATIVE / NEUTRAL
                # HF SST-2 is binary, so if it's neither pos nor neg explicitly,
                # treat as neutral
                up = label.upper()
                if "POS" in up:
                    final_label = "POSITIVE"
                elif "NEG" in up:
                    final_label = "NEGATIVE"
                else:
                    final_label = "NEUTRAL"
                return {"label": final_label, "score": score}
        except Exception:
            # fall through to heuristic
            pass

    # fallback heuristic
    return _heuristic_sentiment(cleaned)


########################################
# 2. ABSA via spaCy noun chunks + local sentiment window
########################################

import spacy
from spacy.tokens import Span, Doc

# Load spaCy English model once.
# You must have this in requirements.txt:
#   spacy
#   en-core-web-sm @ https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1.tar.gz
#
# and ensure Docker installs it.
_nlp = spacy.load("en_core_web_sm")


def _normalize_aspect_text(span: Span) -> str:
    """
    Turn noun chunk into a nice label for display:
    - lowercase
    - strip punctuation
    - collapse spaces
    """
    txt = span.text.strip().lower()
    txt = re.sub(r"[^\w\s\-]+", "", txt)
    txt = re.sub(r"\s+", " ", txt).strip()
    return txt


def _window_for_span(doc: Doc, span: Span, window_size: int = 6) -> str:
    """
    Build a sentiment context window around a noun chunk:
    tokens [span.start-window_size : span.end+window_size]
    """
    start_i = max(span.start - window_size, 0)
    end_i = min(span.end + window_size, len(doc))
    window_tokens = [t.text for t in doc[start_i:end_i]]
    return " ".join(window_tokens)


def aspect_breakdown(text: str) -> List[Dict[str, Any]]:
    """
    Return a list of aspect dicts:
    [
      {
        "aspect": "the speaker",
        "sentiment": "negative" | "positive" | "neutral",
        "score": 0.98,
        "context": "the speaker is garbage and the phone overheats..."
      },
      ...
    ]

    Steps:
    1. Extract noun chunks with spaCy.
    2. For each chunk, grab a local +/- 6-token context window.
    3. Run predict_sentiment(context_window).
    4. Deduplicate aspects, preferring the strongest polarity:
       - negative > positive > neutral
       - tie-breaker = higher confidence score.
    """
    if not text or not text.strip():
        return []

    doc = _nlp(text)

    candidates: List[Tuple[str, Dict[str, Any]]] = []

    for chunk in doc.noun_chunks:
        aspect_label = _normalize_aspect_text(chunk)
        if not aspect_label:
            continue

        context_window = _window_for_span(doc, chunk, window_size=6)

        sent_res = predict_sentiment(context_window)
        polarity = sent_res["label"].lower()  # "positive"/"negative"/"neutral"
        conf = float(sent_res["score"])

        candidates.append((
            aspect_label,
            {
                "aspect": aspect_label,
                "sentiment": polarity,
                "score": conf,
                "context": context_window,
            }
        ))

    # Deduplicate by aspect_label with priority: negative > positive > neutral.
    best_for_aspect: Dict[str, Dict[str, Any]] = {}
    priority = {"negative": 3, "positive": 2, "neutral": 1}

    for aspect_label, info in candidates:
        prev = best_for_aspect.get(aspect_label)
        if prev is None:
            best_for_aspect[aspect_label] = info
        else:
            prev_sent = prev["sentiment"]
            new_sent = info["sentiment"]
            if priority.get(new_sent, 0) > priority.get(prev_sent, 0):
                best_for_aspect[aspect_label] = info
            elif new_sent == prev_sent:
                # tie: keep higher confidence
                if info["score"] > prev["score"]:
                    best_for_aspect[aspect_label] = info

    return list(best_for_aspect.values())
