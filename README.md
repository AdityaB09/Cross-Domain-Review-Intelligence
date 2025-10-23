# Cross-Domain Review Intelligence (Postgres, no S3)

**What it does**
- Ingest drug & product reviews (JSONL or one-by-one)
- Multi-label classification: sentiment, effectiveness, side-effects
- ABSA: aspect extraction (NER) + polarity
- Similar experience search: sentence-transformers + FAISS (local files)
- Explainability: SHAP (token attributions)
- Dashboard: validation metrics

**Run**
```bash
cp .env.example .env
docker compose up --build
# API: http://localhost:8080
# UI : http://localhost:3000
# MLflow: http://localhost:5000
