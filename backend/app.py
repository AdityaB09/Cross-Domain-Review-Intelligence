# backend/app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.db import init_db

from api.routes_health import router as health_router
from api.routes_explain import router as explain_router
# from api.routes_search import router as search_router
# from api.routes_ingest import router as ingest_router
# from api.routes_metrics import router as metrics_router
# # DO NOT import routes that pull torch / transformers here.
# e.g. routes_model, routes_eval, etc. Leave them out for Render.

app = FastAPI(
    title="Cross-Domain Review Intelligence",
    version="0.1.0"
)

raw_origins = settings.allowed_origins.strip()
if raw_origins == "*":
    allow_origins = ["*"]
else:
    allow_origins = [
        o.strip()
        for o in raw_origins.split(",")
        if o.strip()
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    # create tables if they don't exist and Neon is reachable
    try:
        init_db()
    except Exception:
        # swallow so startup doesn't crash if DB is cold or schema incomplete
        pass

# mount ONLY safe routers
app.include_router(health_router)
app.include_router(explain_router)
# app.include_router(search_router)
# app.include_router(ingest_router)
# app.include_router(metrics_router)
