# Known Limitations

FixGraph has been rigorously evaluated, but there are explicit limitations in the current implementation:

1. **Catalog Dependency**: The system's coverage is strictly bounded by the `deeplinks.json` catalog provided in the Samsung Challenge Assets. The system will successfully reject valid device actions if they are not present in this file. This is an intentional safety feature, but limits breadth.
2. **Language Coverage**: The pipeline currently relies heavily on English-language dense embedding models (like `all-MiniLM-L6-v2`) and BM25 tokenizers. Multilingual queries might fall below the strict confidence thresholds and trigger safe fallbacks instead of generating automated plans.
3. **Live Provider Variability**: The system is designed to use mock deterministic providers for evaluation. If attached to a live generative LLM API, latency will scale directly with the provider's token-generation speed (often 500ms - 2s), which far exceeds the 300ms P95 target. Semantic Caching was introduced to bypass this API bottleneck for high-frequency queries.
