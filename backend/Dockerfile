# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app
ENV PYTHONPATH=/app

# basic build deps
RUN apt-get update && apt-get install -y \
    build-essential git wget curl \
    && rm -rf /var/lib/apt/lists/*

# install lightweight requirements
COPY requirements-lite.txt ./requirements.txt
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# install spaCy model (en_core_web_sm)
RUN pip install --no-cache-dir \
    https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl

# copy source
COPY . .

EXPOSE 8080

# run uvicorn on the port Render injects
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port $PORT"]
