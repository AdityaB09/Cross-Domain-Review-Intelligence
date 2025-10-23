from fastapi import APIRouter
from pydantic import BaseModel
from ml.embed_index import EmbIndex

router = APIRouter()
index = EmbIndex()
is_built = False

class Query(BaseModel):
    q: str
    k: int = 10

@router.post("/build")
def build_index():
    global is_built
    index.build()
    is_built = True
    return {"status":"built"}

@router.post("/")
def search(q: Query):
    if not is_built:
        index.build()
    return {"results": index.query(q.q, q.k)}
