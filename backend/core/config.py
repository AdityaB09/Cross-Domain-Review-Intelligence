from pydantic import BaseModel
import os

class Settings(BaseModel):
    database_url: str = os.getenv("DATABASE_URL", "postgresql+psycopg2://cdri:cdri@postgres:5432/cdri")
    redis_url: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    mlflow_uri: str = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")
    api_host: str = os.getenv("API_HOST","0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8080"))
    data_dir: str = os.getenv("DATA_DIR","/data")  # for faiss, artifacts

settings = Settings()
