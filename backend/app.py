from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.db import init_db
from api.routes_ingest import router as ingest_router
from api.routes_model import router as model_router
from api.routes_search import router as search_router
from api.routes_explain import router as explain_router
from api.routes_eval import router as eval_router

app = FastAPI(title="CDRI API (Postgres, no S3)", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

@app.on_event("startup")
def _startup():
    init_db()

@app.get("/health")
def health():
    return {"status":"ok"}

app.include_router(ingest_router, prefix="/ingest", tags=["ingest"])
app.include_router(model_router,  prefix="/model",  tags=["model"])
app.include_router(search_router, prefix="/search", tags=["search"])
app.include_router(explain_router,prefix="/explain",tags=["explain"])
app.include_router(eval_router,   prefix="/eval",   tags=["eval"])
