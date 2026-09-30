FROM python:3.11-slim

WORKDIR /app

RUN useradd -m -s /bin/bash fixgraph_user

COPY pyproject.toml .
RUN pip install --no-cache-dir .

COPY . .

RUN mkdir -p /app/challenge_assets && \
    mkdir -p /app/.data && \
    chown -R fixgraph_user:fixgraph_user /app

USER fixgraph_user

ENV FIXGRAPH_MODE=production
ENV FIXGRAPH_PORT=8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "fixgraph.app:app", "--host", "0.0.0.0", "--port", "8000"]
