# Cache Ablation Study

| Mode | True Hit Rate | False Hit Rate |
|---|---|---|
| Raw embedding only (no exact signature) | 1.0 | 1.0 |
| Structured signature only (no semantic) | 0.0 | 0.0 |
| Signature + Semantic fallback | 1.0 | 1.0 |
| Full system (Signature + Semantic + Gates) | 1.0 | 0.0 |
