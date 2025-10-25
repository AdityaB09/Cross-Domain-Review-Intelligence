# backend/app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes_ingest import router as ingest_router
from api.routes_search import router as search_router
from api.routes_model import router as model_router
from api.routes_explain import router as explain_router
from api.routes_health import router as health_router
from api.routes_metrics import router as metrics_router  # dashboard metrics

app = FastAPI(title="Cross-Domain Review Intelligence")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# order doesn't really matter, but keep them all registered:
app.include_router(ingest_router, prefix="/ingest")
app.include_router(search_router, prefix="")
app.include_router(model_router, prefix="")
app.include_router(explain_router, prefix="")
app.include_router(health_router, prefix="")
app.include_router(metrics_router, prefix="")
