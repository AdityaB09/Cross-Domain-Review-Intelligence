from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

from services.explain_model import analyze_aspects, token_attributions

router = APIRouter()


class ExplainRequest(BaseModel):
    text: str


class AspectItem(BaseModel):
    aspect: str
    sentiment: float
    confidence: float
    polarity: str | None = None  # optional


class TokenItem(BaseModel):
    token: str
    score: float


class ExplainResponse(BaseModel):
    aspects: List[AspectItem]
    tokens: List[TokenItem]


@router.post("/explain-request", response_model=ExplainResponse)
def post_explain(req: ExplainRequest):
    """
    The frontend /explain page posts here with:
      { "text": "Camera is great but phone overheats..." }

    We return:
    {
      "aspects":[
        {"aspect":"camera", "sentiment":1.0,"confidence":0.9,"polarity":"positive"},
        {"aspect":"battery","sentiment":-1.0,"confidence":0.8,"polarity":"negative"},
        ...
      ],
      "tokens":[
        {"token":"Camera","score":0.4},
        {"token":"overheats","score":-0.4},
        ...
      ]
    }
    """

    user_text = req.text.strip()
    if not user_text:
        raise HTTPException(status_code=400, detail="Empty text")

    aspects_list, debug_info = analyze_aspects(user_text)
    toks_raw = token_attributions(user_text)

    aspect_items = [
        AspectItem(
            aspect=a["aspect"],
            sentiment=float(a["sentiment"]),
            confidence=float(a["confidence"]),
            polarity=a.get("polarity"),
        )
        for a in aspects_list
    ]

    token_items = [
        TokenItem(token=t["token"], score=float(t["score"]))
        for t in toks_raw
    ]

    # NOTE: we are not returning debug_info in the API response, but
    # you *could* include it for QA if you want to inspect suspicious cases.
    return ExplainResponse(
        aspects=aspect_items,
        tokens=token_items,
    )
