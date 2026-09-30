# FixGraph Safety & Threat Model

FixGraph is designed with a **zero-trust** approach toward the generative LLM. 

## Defense in Depth
1. **LLM cannot create deeplinks**: The LLM outputs conceptual actions. The pipeline maps these to deterministic, mathematically verified Samsung catalog items. If the LLM invents a fake setting, the pipeline rejects it and falls back safely.
2. **Unsupported Actions are Removed**: We require evidence grounding. If a user asks to fix a "shattered camera lens," no software setting can fix it. The pipeline safely generates a manual fallback plan rather than guessing.
3. **Cache Compatibility Gates**: Two complaints may look semantically similar (cosine similarity > 0.9) but require different fixes ("battery draining" vs "battery physically swollen"). FixGraph extracts domain signatures and enforces strict multi-dimensional compatibility before a cache hit is allowed.
4. **Risk Sequencer**: The LLM might suggest doing a factory reset first. Our Deterministic compiler intercepts this, checks our internal Risk enum taxonomy, and forces DESTRUCTIVE actions to the very bottom of the chain.
