FROM python:3.11-slim
WORKDIR /app

# OS deps for psycopg, tokenizers, etc.
RUN apt-get update && apt-get install -y build-essential git wget curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && python -m spacy download en_core_web_sm

COPY . .
CMD ["uvicorn","app:app","--host","0.0.0.0","--port","8080","--reload"]
