# app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes_ingest import router as ingest_router
from api.routes_search import router as search_router
from api.routes_model import router as model_router
from api.routes_explain import router as explain_router
from api.routes_bootstrap_remote import router as bootstrap_remote_router
from api.routes_health import router as health_router

app = FastAPI(title="Cross-Domain Review Intelligence")

# Allow the Next.js frontend (and anything else) to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # in prod you can lock this down
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ingestion endpoints:
# - POST /ingest/jsonl   (upload local reviews.jsonl into Postgres)
app.include_router(ingest_router, prefix="/ingest")

# Semantic search + index mgmt:
# - POST /build          (rebuild FAISS from DB)
# - POST /               (semantic search {q,k})
app.include_router(search_router, prefix="")

# Sentiment & ABSA:
# - POST /model/predict  (overall sentiment, aspects sentiment)
app.include_router(model_router, prefix="/model")

# Token-level attribution / heatmap:
# - POST /explain/       (gradient-based token attributions)
app.include_router(explain_router, prefix="/explain")

# Cold-start remote bootstrap:
# - POST /bootstrap/from-remote  (pull remote public sources, build FAISS demo index)
app.include_router(bootstrap_remote_router, prefix="")

# Health:
# - GET /health          (checks Postgres, Redis, index files)
app.include_router(health_router)
