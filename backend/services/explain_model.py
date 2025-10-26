from typing import List, Dict, Any, Tuple
from ml.sentiment_model import predict_sentiment, aspect_breakdown


def _numeric_sentiment(polarity_text: str) -> float:
    """
    Map string label -> numeric score for the heatmap.
    positive -> +1.0
    negative -> -1.0
    neutral / anything else -> 0.0
    """
    p = (polarity_text or "").lower()
    if "pos" in p:
        return 1.0
    if "neg" in p:
        return -1.0
    return 0.0


def _validate_confidence(x: float) -> float:
    """
    Clamp confidence to [0,1] just to be safe,
    so the frontend bar doesn't explode.
    """
    if x is None:
        return 0.0
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return float(x)


def _consistency_check(global_label: str, per_aspect_scores: List[float]) -> bool:
    """
    Simple sanity signal:
    Return True if the breakdown looks suspicious.
    'Suspicious' = global is POSITIVE but every aspect is NEGATIVE, or vice versa.
    Used for debugging/QA, can be logged or attached in response.
    """
    if not per_aspect_scores:
        return False

    gl = global_label.lower()
    all_neg = all(s < 0 for s in per_aspect_scores)
    all_pos = all(s > 0 for s in per_aspect_scores)

    if "pos" in gl and all_neg:
        return True
    if "neg" in gl and all_pos:
        return True
    return False


def analyze_aspects(text: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Generate aspect-based sentiment for the Explainability / ABSA panel.

    Returns a tuple:
    - aspects_list: list of {aspect, sentiment, confidence, polarity}
    - debug_info:   dict with validation info for internal debugging / QA

    The frontend will ONLY use aspects_list, but we keep debug_info around in
    case you want to surface warnings later.
    """

    # 1. Run your aspect extractor (keyword-ish) + sentiment scorer (transformer or fallback).
    raw_aspects = aspect_breakdown(text)
    # raw_aspects looks like:
    # [
    #   {"aspect": "the camera", "sentiment": "positive", "score": 0.95},
    #   {"aspect": "battery", "sentiment": "negative", "score": 0.83},
    #   ...
    # ]

    aspects_list: List[Dict[str, Any]] = []
    for a in raw_aspects:
        polarity_label = a.get("sentiment", "neutral")
        numeric_sent = _numeric_sentiment(polarity_label)
        conf = _validate_confidence(float(a.get("score", 0.8)))

        aspects_list.append({
            "aspect": a.get("aspect", "unknown"),
            "sentiment": numeric_sent,       # -1.0 | 0.0 | 1.0 (used for color in heatmap)
            "confidence": conf,              # 0..1      (used for tiny bar)
            "polarity": polarity_label.lower()
        })

    # 2. Fallback: if we found 0 aspects, still return something
    # so the UI doesn't look empty. We'll call this "overall".
    if not aspects_list:
        overall = predict_sentiment(text)
        overall_label = overall["label"]  # "POSITIVE"/"NEGATIVE"/"NEUTRAL"
        overall_conf = float(overall["score"])
        aspects_list.append({
            "aspect": "overall",
            "sentiment": _numeric_sentiment(overall_label),
            "confidence": _validate_confidence(overall_conf),
            "polarity": overall_label.lower(),
        })

    # 3. Validation / sanity info for debugging
    global_sent_dict = predict_sentiment(text)
    global_label = global_sent_dict["label"]  # global sentiment text
    all_scores = [item["sentiment"] for item in aspects_list]
    looks_suspicious = _consistency_check(global_label, all_scores)

    debug_info = {
        "global_sentiment": global_label,
        "all_aspect_scores": all_scores,
        "suspicious": looks_suspicious,
    }

    return aspects_list, debug_info


def token_attributions(text: str) -> List[Dict[str, Any]]:
    """
    Token-level attribution. This is intentionally light-weight.
    We reuse predict_sentiment() token-by-token instead of doing
    gradient-based attribution, because it's easy to run on CPU.

    Output format matches frontend TokenAttributionsPills:
    [
      {"token":"camera","score":0.4},
      {"token":"is","score":0.05},
      {"token":"garbage","score":-0.4},
      ...
    ]
    """
    toks = text.split()
    out: List[Dict[str, Any]] = []

    for tok in toks:
        sent = predict_sentiment(tok)  # may use HF model or fallback wordlist
        lbl = sent["label"].lower()

        if "pos" in lbl:
            score = 0.4
        elif "neg" in lbl:
            score = -0.4
        else:
            score = 0.05

        out.append({
            "token": tok,
            "score": score
        })

    return out
