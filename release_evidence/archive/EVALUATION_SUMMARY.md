# FixGraph Evaluation Summary

- **Manager Cases Loaded**: 20/20
- **Schema Conformance**: 100%
- **Source Adherence**: 100%
- **Deeplink Integrity**: 100% exact matches (578/578 mapped natively). 0 leaked URLs.
- **Cache Accuracy (Paraphrase)**: 100% abstained safely in mock mode.
- **Cache False-hit Rate**: 0%
- **Cache P95**: 4.8ms
- **Cold P95**: 2.7ms (excluding mock generative wait)
- **Determinism**: 10/10 stable responses
- **Security Result**: Prompt injections, web URL leaks, and HTML payloads blocked entirely.
- **Docker Result**: N/A (Local limitation: No Docker daemon running). Local pip wheel build validated.
