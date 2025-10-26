# services/explain_model.py

"""
This module wraps your existing sentiment / ABSA / attribution logic into
two clean functions the API can call.

You already have ml/sentiment_model.py etc.
We'll assume we can reuse that code here.
Fill in the TODOs with your real model calls.
"""

from typing import List, Dict, Any

# If you already have these models loaded globally somewhere, import them.
# For example:
# from ml.sentiment_model import (
#     extract_aspects_and_sentiment,
#     explain_token_attributions,
# )

# We'll define stubs that you must connect to real code.
# Replace the bodies of these two functions so they call your actual pipeline.


def analyze_aspects(text: str) -> List[Dict[str, Any]]:
    """
    Run your ABSA / aspect extraction model:
    return a list of:
      {
        "aspect": "battery life",
        "sentiment": 0.8,      # -1 .. 1
        "confidence": 0.9      # 0 .. 1
      }
    """

    # TODO: REPLACE THIS BODY with your real aspect-based sentiment
    # e.g.:
    # results = extract_aspects_and_sentiment(text)
    # return [
    #   {
    #     "aspect": r.aspect,
    #     "sentiment": r.score,
    #     "confidence": r.confidence,
    #   }
    #   for r in results
    # ]

    # placeholder uses overall sentiment words to fake per-aspect groups.
    return [
        {
            "aspect": "speaker quality",
            "sentiment": -0.7,
            "confidence": 0.85,
        },
        {
            "aspect": "camera sharpness",
            "sentiment": 0.9,
            "confidence": 0.9,
        },
        {
            "aspect": "overheating",
            "sentiment": -0.8,
            "confidence": 0.88,
        },
    ]


def token_attributions(text: str) -> List[Dict[str, Any]]:
    """
    Run your attribution explainer (e.g. Integrated Gradients / LIME on your classifier).
    return list of:
      {
        "token": "dizzy",
        "score": -0.9
      }
    """

    # TODO: REPLACE THIS BODY with your real attribution logic
    # e.g.:
    # attrs = explain_token_attributions(text)
    # return [{"token": t.word, "score": t.contribution} for t in attrs]

    toks = text.strip().split()
    demo = []
    for tok in toks:
        # trivial heuristic: "good" words -> +0.4, "bad" words -> -0.8
        lower = tok.lower().strip(",.!?")
        if lower in ["love", "great", "amazing", "sharp", "fast", "helped"]:
            score = 0.4
        elif lower in ["overheats", "buzzes", "dizzy", "nauseous", "terrible"]:
            score = -0.8
        else:
            score = 0.05
        demo.append({"token": lower, "score": score})

    return demo
