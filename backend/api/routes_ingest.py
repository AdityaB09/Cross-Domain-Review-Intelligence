from fastapi import APIRouter, UploadFile, File, Form
from pydantic import BaseModel
import pandas as pd
from sqlalchemy import text
from core.db import engine

router = APIRouter()

class ReviewIn(BaseModel):
    domain: str     # "health" | "product"
    product: str
    text: str
    rating: float | None = None

@router.post("/jsonl")
async def ingest_jsonl(file: UploadFile = File(...), domain: str = Form(...)):
    df = pd.read_json(file.file, lines=True)
    df["domain"] = domain
    with engine.begin() as conn:
        for _, r in df.iterrows():
            conn.execute(
                text("""INSERT INTO reviews(domain,product,text,rating)
                        VALUES(:d,:p,:t,:r)"""),
                {"d": r.get("domain","product"),
                 "p": r.get("product","unknown"),
                 "t": r["text"],
                 "r": r.get("rating")}
            )
    return {"rows": len(df)}

@router.post("/")
async def ingest_one(review: ReviewIn):
    with engine.begin() as conn:
        conn.execute(
            text("""INSERT INTO reviews(domain,product,text,rating)
                    VALUES(:d,:p,:t,:r)"""),
            review.model_dump()
        )
    return {"status":"ok"}
