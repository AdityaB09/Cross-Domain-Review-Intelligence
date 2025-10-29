# backend/core/db.py
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from .config import settings

# We'll lazily init so if DATABASE_URL is missing/bad,
# we degrade gracefully to memory mode.
_engine = None
_SessionLocal = None
_db_ok = False

def init_db_if_possible():
    global _engine, _SessionLocal, _db_ok
    if _db_ok:
        return
    try:
        db_url = settings.database_url
    except AttributeError:
        db_url = None

    if not db_url:
        _db_ok = False
        return

    try:
        _engine = create_engine(db_url, pool_pre_ping=True)
        _SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False)

        # ensure tables exist (idempotent)
        with _engine.connect() as conn:
            conn.execute(text("""
            CREATE TABLE IF NOT EXISTS raw_reviews (
                id SERIAL PRIMARY KEY,
                text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            );
            """))
            conn.execute(text("""
            CREATE TABLE IF NOT EXISTS eda_aspects (
                aspect TEXT PRIMARY KEY,
                count INTEGER NOT NULL DEFAULT 0,
                total_sentiment DOUBLE PRECISION NOT NULL DEFAULT 0
            );
            """))
            conn.commit()

        _db_ok = True
    except Exception:
        # Neon offline or not reachable
        _db_ok = False
        _engine = None
        _SessionLocal = None

def db_available() -> bool:
    return _db_ok

def get_db_session():
    """
    Returns a SQLAlchemy session if DB is available,
    otherwise returns None to signal fallback mode.
    """
    if not _db_ok:
        return None
    try:
        return _SessionLocal()
    except Exception:
        return None


# Helpers for writes/reads ---------------------------------------

def db_insert_review(text_value: str):
    """
    Insert into raw_reviews if DB available.
    Silent no-op if DB down.
    """
    if not _db_ok:
        return
    session = get_db_session()
    if session is None:
        return
    try:
        session.execute(
            text("INSERT INTO raw_reviews(text) VALUES (:t)"),
            {"t": text_value}
        )
        session.commit()
    except SQLAlchemyError:
        session.rollback()
    finally:
        session.close()

def db_upsert_aspect(aspect_name: str, sentiment_value: float):
    """
    Update eda_aspects row in Neon:
    - increment count
    - add to total_sentiment

    Silent no-op if DB down.
    """
    if not _db_ok:
        return
    session = get_db_session()
    if session is None:
        return
    try:
        session.execute(text("""
            INSERT INTO eda_aspects(aspect, count, total_sentiment)
            VALUES (:asp, 1, :sent)
            ON CONFLICT (aspect) DO UPDATE SET
                count = eda_aspects.count + 1,
                total_sentiment = eda_aspects.total_sentiment + EXCLUDED.total_sentiment
        """), {"asp": aspect_name, "sent": sentiment_value})
        session.commit()
    except SQLAlchemyError:
        session.rollback()
    finally:
        session.close()

def db_get_aspect_stats():
    """
    Returns list of {aspect, mentions, avg_sentiment} from Neon
    or None if DB down.
    """
    if not _db_ok:
        return None
    session = get_db_session()
    if session is None:
        return None
    try:
        rows = session.execute(text("""
            SELECT
                aspect,
                count AS mentions,
                CASE WHEN count > 0
                     THEN total_sentiment / count
                     ELSE 0
                END AS avg_sentiment
            FROM eda_aspects
            ORDER BY count DESC;
        """)).mappings().all()
        out = []
        for r in rows:
            out.append({
                "aspect": r["aspect"],
                "mentions": int(r["mentions"]),
                "avg_sentiment": float(round(r["avg_sentiment"], 2)),
            })
        return out
    except SQLAlchemyError:
        return None
    finally:
        session.close()
