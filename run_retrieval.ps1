$env:ALLOW_EMBEDDER_FALLBACK="true"
$env:EMBEDDER_PROVIDER="hashngram"
$env:ASSETS_DIR="manager_assets/Theme 2"
uv run python scripts/benchmark_retrieval.py
