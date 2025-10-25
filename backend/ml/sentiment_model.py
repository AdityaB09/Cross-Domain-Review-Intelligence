# backend/ml/sentiment_model.py
from typing import Dict
import os

# Try to load a HF sentiment pipeline, but don't die if offline
# or model can't load. We'll gracefully degrade.
_hf_pipeline = None
_hf_loaded = False

def _maybe_load_hf():
    global _hf_pipeline, _hf_loaded
    if _hf_loaded:
        return
    _hf_loaded = True
    try:
        from transformers import pipeline
        model_name = os.getenv(
            "SENTIMENT_MODEL",
            "distilbert-base-uncased-finetuned-sst-2-english",
        )
        _hf_pipeline = pipeline("sentiment-analysis", model=model_name)
    except Exception:
        _hf_pipeline = None  # fallback only


POS_WORDS = {
    "great", "amazing", "love", "fantastic", "excellent",
    "sharp", "perfect", "helped", "relief", "working"
}
NEG_WORDS = {
    "garbage", "slow", "overheats", "buzzes", "nauseous",
    "terrible", "bad", "hot", "hurt", "pain", "ache",
    "headache", "dizzy"
}

def _fallback_sentiment(text: str) -> Dict[str, float]:
    """
    Heuristic sentiment if HF pipeline not available.
    We'll just count word hits.
    """
    score = 0.0
    toks = text.lower().split()
    for t in toks:
        tclean = t.strip(",.!?;:")
        if tclean in POS_WORDS:
            score += 1.0
        if tclean in NEG_WORDS:
            score -= 1.0

    # clamp
    if score > 3.0:
        score = 3.0
    if score < -3.0:
        score = -3.0

    # map to [0,1] confidence-ish
    conf = min(abs(score) / 3.0, 1.0)

    label = "POSITIVE" if score > 0 else "NEGATIVE" if score < 0 else "NEUTRAL"
    return {"label": label, "score": conf}


def predict_sentiment(text: str) -> Dict[str, float]:
    """
    Unified interface that /metrics and /model/predict can call.

    Returns dict like:
      { "label": "POSITIVE", "score": 0.93 }
    """
    _maybe_load_hf()

    # happy path HF pipeline
    if _hf_pipeline is not None:
        try:
            result = _hf_pipeline(text)[0]
            # HF result looks like { 'label': 'POSITIVE', 'score': 0.999 }
            return {
                "label": result["label"],
                "score": float(result["score"]),
            }
        except Exception:
            pass

    # fallback
    return _fallback_sentiment(text)


def aspect_breakdown(text: str):
    """
    This powers ABSA in the UI (Explain page "Aspect Heatmap").
    We'll do a trivial "extract aspects" + attach sentiment to each.

    Output example:
    [
      {"aspect": "the camera", "sentiment": "positive", "score": 0.95},
      {"aspect": "the speaker", "sentiment": "negative", "score": 0.87},
    ]
    """
    aspects = []
    lower = text.lower()

    candidates = [
        ("battery", "battery"),
        ("charging", "charging"),
        ("charge port", "charge port"),
        ("overheats", "the phone overheats"),
        ("speaker", "the speaker"),
        ("camera", "the camera"),
        ("nauseous", "the medicine / nausea"),
        ("back pain", "my back pain"),
    ]

    for keyword, label in candidates:
        if keyword in lower:
            # sentiment = use predict_sentiment on that span
            seg = label
            sent = predict_sentiment(seg)
            raw_label = sent["label"].lower()
            if "pos" in raw_label:
                sentiment_txt = "positive"
            elif "neg" in raw_label:
                sentiment_txt = "negative"
            else:
                sentiment_txt = "neutral"

            aspects.append(
                {
                    "aspect": label,
                    "sentiment": sentiment_txt,
                    "score": float(sent["score"]),
                }
            )

    # dedupe by aspect
    dedup = {}
    for a in aspects:
        dedup[a["aspect"]] = a
    return list(dedup.values())
