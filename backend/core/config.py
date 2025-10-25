# backend/core/config.py
import os
from pathlib import Path
from typing import List
from dataclasses import dataclass
from pydantic import BaseModel

@dataclass
class RemoteSource:
    name: str
    url: str
    fmt: str           # "jsonl", "jsonl_gz", "csv", "tsv"
    text_key: str = "text"
    domain: str = ""

class Settings(BaseModel):
    #
    # --- Infra / runtime ---
    #
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://cdri:cdri@postgres:5432/cdri",
    )
    redis_url: str = os.getenv(
        "REDIS_URL",
        "redis://redis:6379/0",
    )
    mlflow_uri: str = os.getenv(
        "MLFLOW_TRACKING_URI",
        "http://mlflow:5000",
    )

    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8080"))

    #
    # --- Data storage / artifacts ---
    #
    # /data should be a volume in docker-compose so index survives restarts.
    data_dir: Path = Path(os.getenv("DATA_DIR", "/data"))

    @property
    def index_dir(self) -> Path:
        return self.data_dir / "index"

    @property
    def faiss_index_path(self) -> Path:
        return self.index_dir / "index.faiss"

    @property
    def faiss_meta_path(self) -> Path:
        return self.index_dir / "meta.json"

    #
    # --- ML model names ---
    #
    # Used for semantic search embeddings:
    emb_model: str = os.getenv(
        "EMB_MODEL",
        "sentence-transformers/all-MiniLM-L6-v2",
    )

    # Used for sentiment + ABSA scoring in ml/sentiment_model.py
    sentiment_model_name: str = os.getenv(
        "SENTIMENT_MODEL",
        "distilbert-base-uncased-finetuned-sst-2-english",
    )

    #
    # --- Optional public bootstrap sources for /bootstrap/from-remote
    #
    bootstrap_sources: List[RemoteSource] = [
        RemoteSource(
            name="amazon_sample",
            url="https://raw.githubusercontent.com/openai/openai-cookbook/main/examples/data/amazon_10.jsonl",
            fmt="jsonl",
            text_key="reviewText",
            domain="amazon",
        ),
        RemoteSource(
            name="drugs_sample",
            url="https://raw.githubusercontent.com/allenai/scifact/master/data/reviews_small.jsonl",
            fmt="jsonl",
            text_key="text",
            domain="drugs",
        ),
    ]

settings = Settings()
# make sure /data/index exists in the container
settings.index_dir.mkdir(parents=True, exist_ok=True)
