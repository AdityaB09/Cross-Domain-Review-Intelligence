from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from .config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def init_db():
    with engine.connect() as conn:
        with open("core/schemas.sql","r",encoding="utf-8") as f:
            conn.execute(text(f.read()))
            conn.commit()
