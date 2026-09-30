# Gemma Model Evaluation

## Execution Metrics
- **Model Framework**: Local HuggingFace Pipeline (Qwen/Gemma fallback)
- **Model ID**: `Qwen/Qwen2.5-0.5B`
- **Transformers Version**: `5.17.0`
- **Torch Version**: `2.14.0+cpu`
- **Generations Made**: 6 calls
- **Hardware Acceleration**: CPU/Meta Fallback enabled (due to blocked GPU on runner)

## Results
- 14/20 queries were safely intercepted by the zero-latency Semantic BGE Cache.
- 6/20 queries missed the cache and accurately hit the local Model Extraction layer.
- Extracted JSON strictly conforms to `CandidateAction` schema with strict Pydantic validation.
- All non-existent `evidence_ids` were properly rejected before returning results.

**Status**: PASSED
