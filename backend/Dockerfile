# backend/Dockerfile
FROM python:3.11-slim
WORKDIR /app
ENV PYTHONPATH=/app


RUN apt-get update && apt-get install -y build-essential git wget curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# 1) install deps
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
# 2) install spaCy English model wheel explicitly (compatible with spaCy 3.7.x)
RUN pip install --no-cache-dir \
    https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl

COPY . .
CMD ["uvicorn","app:app","--host","0.0.0.0","--port","8080","--reload"]
