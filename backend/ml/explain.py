# backend/ml/explain.py
from typing import List, Dict

POS_WORDS = {
    "great", "amazing", "love", "fantastic", "excellent",
    "sharp", "perfect", "helped", "relief", "working"
}
NEG_WORDS = {
    "garbage", "slow", "overheats", "buzzes", "nauseous",
    "terrible", "bad", "hot", "hurt", "pain", "ache",
    "headache", "dizzy"
}

def run_explanation(text: str) -> List[Dict[str, float]]:
    """
    Very lightweight "attribution":
    +0.9 if obviously positive
    -0.9 if obviously negative
    else small neutral 0.1 just so we render something.

    Output format matches what routes_explain.py expects.
    """

    out = []
    for tok in text.split():
        low = tok.strip(",.!?;:").lower()

        if low in POS_WORDS:
            score = 0.9
        elif low in NEG_WORDS:
            score = -0.9
        else:
            score = 0.1

        out.append({"token": tok, "attribution": score})

    return out
