# backend/app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.db import init_db

# import your routers
from api.routes_health import router as health_router
from api.routes_explain import router as explain_router
from api.routes_search import router as search_router
from api.routes_metrics import router as metrics_router
from api.routes_ingest import router as ingest_router
# if you have EDA aggregation endpoint, include it:
from api.routes_eda import router as eda_router
# if you have routes_model, include it too, etc.

app = FastAPI(
    title="Cross-Domain Review Intelligence",
    version="0.1.0"
)

# CORS setup:
# ALLOWED_ORIGINS env will look like:
#   https://your-frontend.vercel.app,https://localhost:3000
allowed_origins_list = [
    origin.strip()
    for origin in settings.allowed_origins.split(",")
    if origin.strip()
]

# if ALLOWED_ORIGINS="*" we just allow all
if settings.allowed_origins.strip() == "*":
    allow_origins = ["*"]
else:
    allow_origins = allowed_origins_list

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    # create tables in Neon if missing
    init_db()

# register subrouters
app.include_router(health_router)
app.include_router(explain_router)
app.include_router(search_router)
app.include_router(metrics_router)
app.include_router(ingest_router)
app.include_router(eda_router)  # uncomment if you have it
