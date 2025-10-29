# backend/api/routes_explain.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from services.lightweight_explain import run_lightweight_explain
from core.db import SessionLocal

router = APIRouter()

class ExplainRequest(BaseModel):
    text: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def _persist_result(db: Session, text: str, aspects_payload):
    """
    Optional: aggregate for EDA.
    If you don't have these tables in Neon yet, wrap this call in try/except.
    """
    try:
        db.execute(
            "INSERT INTO raw_reviews(text) VALUES (:t)",
            {"t": text},
        )
    except Exception:
        pass

    for a in aspects_payload:
        aspect = a["aspect"]
        sent = float(a["sentiment"])

        try:
            db.execute(
                """
                INSERT INTO eda_aspects(aspect, count, avg_sentiment)
                VALUES (:aspect, 1, :sent)
                ON CONFLICT (aspect) DO UPDATE SET
                  count = eda_aspects.count + 1,
                  avg_sentiment = (
                    (eda_aspects.avg_sentiment * eda_aspects.count) + EXCLUDED.avg_sentiment
                  ) / (eda_aspects.count + 1)
                """,
                {"aspect": aspect, "sent": sent},
            )
        except Exception:
            pass

    try:
        db.commit()
    except Exception:
        pass

@router.post("/explain-request")
def explain_endpoint(body: ExplainRequest, db: Session = Depends(get_db)):
    """
    SUPER LIGHT inference so Render Free doesn't OOM.
    """
    resp = run_lightweight_explain(body.text)
    _persist_result(db, body.text, resp["aspects"])
    return resp
