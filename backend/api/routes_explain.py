from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from services.explain_model import analyze_aspects, token_attributions

router = APIRouter()

class ExplainRequest(BaseModel):
    text: str

class AspectItem(BaseModel):
    aspect: str
    sentiment: float          # -1.0 / 0.0 / 1.0
    confidence: float         # 0..1
    polarity: str | None = None

class TokenItem(BaseModel):
    token: str
    score: float              # -0.4 / 0.05 / 0.4 etc.

class ExplainResponse(BaseModel):
    aspects: List[AspectItem]
    tokens: List[TokenItem]

@router.post("/explain-request", response_model=ExplainResponse)
def post_explain(req: ExplainRequest):
    """
    Input:
      { "text": "camera is great but the battery overheats" }

    Output:
      {
        "aspects": [
          {"aspect":"the camera","sentiment":1.0,"confidence":0.91,"polarity":"positive"},
          {"aspect":"battery","sentiment":-1.0,"confidence":0.83,"polarity":"negative"},
          {"aspect":"the phone overheats","sentiment":-1.0,"confidence":0.88,"polarity":"negative"}
        ],
        "tokens": [
          {"token":"camera","score":0.4},
          {"token":"overheats","score":-0.4},
          ...
        ]
      }
    """

    user_text = req.text.strip()
    if not user_text:
        raise HTTPException(status_code=400, detail="Empty text")

    aspects_list, _debug_info = analyze_aspects(user_text)
    toks_raw = token_attributions(user_text)

    # shape -> pydantic models
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

    return ExplainResponse(
        aspects=aspect_items,
        tokens=token_items,
    )
