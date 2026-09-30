$env:ALLOW_EMBEDDER_FALLBACK="true"
$env:EMBEDDER_PROVIDER="hashngram"
$env:ASSETS_DIR="manager_assets/Theme 2"
uv run python scripts/prewarm_manager_cases.py
uv run python scripts/benchmark_manager_cache.py
uv run python scripts/evaluate_gemma_manager_cases.py
