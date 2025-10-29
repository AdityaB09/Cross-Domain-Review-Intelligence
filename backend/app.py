# backend/app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings

from api.routes_health import router as health_router
from api.routes_explain import router as explain_router
from api.routes_search import router as search_router
from api.routes_ingest import router as ingest_router
from api.routes_metrics import router as metrics_router
from api.routes_eda import router as eda_router

app = FastAPI(
    title="Cross-Domain Review Intelligence (Lite)",
    version="0.1.0"
)

raw_origins = getattr(settings, "allowed_origins", "*").strip()
if raw_origins == "*":
    allow_origins = ["*"]
else:
    allow_origins = [
        o.strip() for o in raw_origins.split(",") if o.strip()
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all lightweight routers
app.include_router(health_router)
app.include_router(explain_router)
app.include_router(search_router)
app.include_router(ingest_router)
app.include_router(metrics_router)
app.include_router(eda_router)

@app.get("/")
def root():
    return {"msg": "CDRI Lite up and running"}
