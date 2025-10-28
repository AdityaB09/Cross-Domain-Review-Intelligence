# backend/Dockerfile
FROM python:3.11-slim

# 1. Set workdir and PYTHONPATH so imports like "from core.db import ..." work.
WORKDIR /app
ENV PYTHONPATH=/app

# 2. System deps for building wheels, etc.
RUN apt-get update && apt-get install -y \
    build-essential git wget curl \
    && rm -rf /var/lib/apt/lists/*

# 3. Copy requirements first (better layer caching)
COPY requirements.txt .

# 4. Install Python deps
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 5. Install spaCy English model (pinned to 3.7.1 to match your code)
RUN pip install --no-cache-dir \
    https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl

# 6. Copy the rest of the backend code into the image
# IMPORTANT: we are building from inside backend/ when Render builds
COPY . .

# 7. Expose a port just for documentation (Render will still inject $PORT)
EXPOSE 8080

# 8. Start command.
# Render will set $PORT at runtime. We have to respect that.
# We do NOT use --reload in production.
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port $PORT"]
