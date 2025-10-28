# backend/core/db.py
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from .config import settings

# Create engine against Neon (or local dev Postgres)
# pool_pre_ping=True helps recover if Neon suspends and resumes
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

def init_db():
    """
    Ensure tables exist.
    schemas.sql should use CREATE TABLE IF NOT EXISTS so we can safely run
    this every time the container (re)starts on Render.
    """
    with engine.connect() as conn:
        with open("core/schemas.sql", "r", encoding="utf-8") as f:
            sql_text = f.read()
            conn.execute(text(sql_text))
            conn.commit()
