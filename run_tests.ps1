$env:ALLOW_EMBEDDER_FALLBACK="true"
$env:EMBEDDER_PROVIDER="hashngram"
uv run pytest -q
