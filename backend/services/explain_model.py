# services/explain_model.py

from typing import List, Dict, Any, Tuple
from ml.sentiment_model import predict_sentiment, aspect_breakdown

# rolling aspect stats for EDA
# _eda_tracker = {
#   "battery life": {"count": 4.0, "avg_sentiment": -0.63},
#   ...
# }
_eda_tracker: Dict[str, Dict[str, float]] = {}


def _continuous_sentiment(label: str, score: float) -> float:
    """
    Convert model output into a smooth numeric range [-1, 1].
    Example:
      ("POSITIVE", 0.93) -> +0.93
      ("NEGATIVE", 0.80) -> -0.80
      ("NEUTRAL",  0.50) -> 0.0
    """
    if not label:
        return 0.0
    l = label.lower()
    clamped = max(0.0, min(1.0, float(score)))
    if "pos" in l:
        return clamped
    if "neg" in l:
        return -clamped
    return 0.0


def _validate_confidence(x: float) -> float:
    if x is None:
        return 0.0
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return float(x)


def _consistency_check(global_sent_cont: float, per_aspect_scores: List[float]) -> bool:
    """
    Quick sanity check:
    If global sentiment is strongly positive (>0.6) but EVERY aspect is <-0.2,
    or strongly negative (<-0.6) but EVERY aspect is >0.2,
    we flag as suspicious.
    """
    if not per_aspect_scores:
        return False

    all_neg = all(s < -0.2 for s in per_aspect_scores)
    all_pos = all(s > 0.2 for s in per_aspect_scores)

    if global_sent_cont > 0.6 and all_neg:
        return True
    if global_sent_cont < -0.6 and all_pos:
        return True
    return False


def _update_eda_tracker(aspects_list: List[Dict[str, Any]]):
    """
    Maintain rolling average sentiment per aspect using CONTINUOUS values
    (not just -1/0/1). This is what powers /eda/aspects.
    """
    for a in aspects_list:
        asp = a["aspect"]
        sent_val = float(a["sentiment"])  # now continuous [-1,1]
        stats = _eda_tracker.get(asp)
        if stats is None:
            _eda_tracker[asp] = {
                "count": 1.0,
                "avg_sentiment": sent_val,
            }
        else:
            new_count = stats["count"] + 1.0
            new_avg = (stats["avg_sentiment"] * stats["count"] + sent_val) / new_count
            stats["count"] = new_count
            stats["avg_sentiment"] = new_avg
            _eda_tracker[asp] = stats


def get_eda_snapshot() -> List[Dict[str, Any]]:
    """
    Return EDA rollup, sorted by 'most pain' first.
    Each row looks like:
      {
        "aspect": "battery life",
        "mentions": 5.0,
        "avg_sentiment": -0.62
      }
    avg_sentiment is continuous [-1..1].
    """
    rows = []
    for asp, stats in _eda_tracker.items():
        rows.append({
            "aspect": asp,
            "mentions": stats["count"],
            "avg_sentiment": stats["avg_sentiment"],
        })
    # sort: most negative first, break ties by highest mentions
    rows.sort(key=lambda r: (r["avg_sentiment"], -r["mentions"]))
    return rows


def analyze_aspects(text: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Pipeline for /explain-request.
    1. aspect_breakdown(text) pulls noun chunks + local window sentiment
    2. convert each aspect sentiment -> continuous [-1,1] using label + confidence
    3. fallback "overall" if no aspects found
    4. update rolling EDA
    5. compute debug info (not sent to FE)
    """

    raw_aspects = aspect_breakdown(text)
    aspects_list: List[Dict[str, Any]] = []

    for a in raw_aspects:
        # From aspect_breakdown():
        # {
        #   "aspect": "the battery life",
        #   "sentiment": "negative" | "positive" | "neutral",
        #   "score": 0.98,
        #   "context": "the battery life is embarrassing ..."
        # }
        polarity_label = a.get("sentiment", "neutral")
        raw_conf = float(a.get("score", 0.8))
        raw_conf_clamped = _validate_confidence(raw_conf)

        cont_sent = _continuous_sentiment(polarity_label, raw_conf_clamped)

        aspects_list.append({
            "aspect": a.get("aspect", "unknown"),
            "sentiment": cont_sent,           # continuous [-1..1]
            "confidence": raw_conf_clamped,   # raw model confidence [0..1]
            "polarity": polarity_label.lower()
        })

    # fallback if no aspects extracted
    if not aspects_list:
        global_pred = predict_sentiment(text)
        g_label = global_pred["label"]          # "POSITIVE"/"NEGATIVE"/"NEUTRAL"
        g_score = _validate_confidence(float(global_pred["score"]))
        cont_sent = _continuous_sentiment(g_label, g_score)

        aspects_list.append({
            "aspect": "overall",
            "sentiment": cont_sent,
            "confidence": g_score,
            "polarity": g_label.lower(),
        })

    # update rolling tracker for /eda/aspects
    _update_eda_tracker(aspects_list)

    # compute global sentiment in continuous form for debug
    global_sent_pred = predict_sentiment(text)
    global_label = global_sent_pred["label"]
    global_score = _validate_confidence(float(global_sent_pred["score"]))
    global_cont = _continuous_sentiment(global_label, global_score)

    per_scores = [item["sentiment"] for item in aspects_list]
    looks_suspicious = _consistency_check(global_cont, per_scores)

    debug_info = {
        "global_sentiment_label": global_label,
        "global_sentiment_cont": global_cont,
        "all_aspect_cont_scores": per_scores,
        "suspicious": looks_suspicious,
        "eda_snapshot": get_eda_snapshot(),
    }

    return aspects_list, debug_info


def token_attributions(text: str) -> List[Dict[str, Any]]:
    """
    Per-token sentiment explanation.
    BEFORE: we snapped each token into {-0.4, 0.05, 0.4}
    NOW:    we return continuous sentiment per token ([-1..1]) based on
            predict_sentiment(token). This gives Scatter-ish distribution
            instead of flat 0.4 / -0.4 everywhere.
    """
    toks = text.split()
    out: List[Dict[str, Any]] = []

    for tok in toks:
        sent = predict_sentiment(tok)
        lbl = sent.get("label", "NEUTRAL")
        conf = _validate_confidence(float(sent.get("score", 0.5)))

        cont = _continuous_sentiment(lbl, conf)
        # clamp just in case
        if cont < -1.0:
            cont = -1.0
        if cont > 1.0:
            cont = 1.0

        out.append({
            "token": tok,
            "score": cont  # continuous now, e.g. -0.78, 0.12, etc.
        })

    return out
