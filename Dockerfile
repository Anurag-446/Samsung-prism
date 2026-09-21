FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml /app/
COPY README.md /app/

RUN pip install --no-cache-dir -e .

COPY challenge_assets /app/challenge_assets/
COPY src /app/src/

EXPOSE 8000

HEALTHCHECK --interval=5s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "fixgraph.app:app", "--host", "0.0.0.0", "--port", "8000"]
