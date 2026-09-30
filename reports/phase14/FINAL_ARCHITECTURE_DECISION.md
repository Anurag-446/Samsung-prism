# Final Architecture Decision

## Model Stack
- **Routing & Retrieval**: BAAI/bge-small-en-v1.5 + Reciprocal Rank Fusion + BM25
- **Semantic Generation**: Qwen2.5-0.5B (local inference) / Gemma Local Fallback
- **Reason**: Meets the strict offline, zero-latency caching, deterministic, no-internet requirements of the PRISM Hackathon.

## Manager Contract Alignment
- SIIS text is strictly forwarded to the models as evidence context.
- Fallback paths guarantee a `CandidateAction` response for deterministic repair gates.
- Exact URI and ID matching via DeepLinkCatalog ensuring we hit valid manager catalog items.

## Rules Met
- Semantic cache hit -> 0 model inference calls.
- `originalType` triggers implemented as intent bonuses matching strict rules.
- Gemma strictly constrained to `CandidateAction` structure.
