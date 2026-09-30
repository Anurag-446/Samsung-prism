FROM python:3.11-slim

WORKDIR /app

# Install system deps for health check
RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -m -s /bin/bash fixgraph_user

# Install Python deps first (layer caching)
COPY pyproject.toml .
# Install CPU-only torch to keep image size manageable
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir ".[ml]"

# Copy source
COPY . .

RUN mkdir -p /app/data && \
    chown -R fixgraph_user:fixgraph_user /app

USER fixgraph_user

ENV FIXGRAPH_MODE=production
ENV FIXGRAPH_ENV=production
ENV FIXGRAPH_PORT=8000
ENV FIXGRAPH_LLM_PROVIDER=gemma_local
ENV FIXGRAPH_LLM_MODEL_NAME=Qwen/Qwen2.5-0.5B

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "fixgraph.app:app", "--host", "0.0.0.0", "--port", "8000"]
