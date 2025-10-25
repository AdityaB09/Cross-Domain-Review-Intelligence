from fastapi import APIRouter
import os, json
from typing import Dict, Any

router = APIRouter()

def _ok(x: Any) -> bool:
    return (isinstance(x, str) and x == "ok") or (x is True)

@router.get("/health")
async def health() -> Dict[str, Any]:
    checks: Dict[str, Any] = {}

    # Redis
    try:
        import redis  # type: ignore
        redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
        r = redis.Redis.from_url(redis_url)
        r.ping()
        checks["redis"] = "ok"
    except Exception as e:
        checks["redis"] = f"error: {e.__class__.__name__}: {e}"

    # Postgres
    try:
        import psycopg2  # type: ignore
        raw_dsn = os.getenv(
            "DATABASE_URL",
            "postgresql://postgres:postgres@postgres:5432/postgres"
        )
        # normalize SQLAlchemy DSN (postgresql+psycopg2://...) for psycopg2
        dsn = raw_dsn.replace("postgresql+psycopg2://", "postgresql://")
        conn = psycopg2.connect(dsn)
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            cur.fetchone()
        conn.close()
        checks["postgres"] = "ok"
    except Exception as e:
        checks["postgres"] = f"error: {e.__class__.__name__}: {e}"

    # Index files presence
    index_dir = os.getenv("INDEX_DIR", "/data/index")
    faiss_path = os.path.join(index_dir, "index.faiss")
    meta_path = os.path.join(index_dir, "meta.json")
    idx_ok = os.path.exists(faiss_path) and os.path.exists(meta_path)
    checks["index_files"] = idx_ok

    status = "ok" if all(_ok(v) for v in checks.values()) else "degraded"
    return {"status": status, "checks": checks}
