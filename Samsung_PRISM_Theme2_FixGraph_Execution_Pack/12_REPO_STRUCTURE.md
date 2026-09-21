# Proposed Repository Structure

```text
fixgraph-prism-theme2/
├── README.md
├── pyproject.toml
├── Dockerfile
├── .env.example
├── .gitignore
├── Makefile
│
├── challenge_assets/                  # only if redistribution is permitted
│   ├── schema.py
│   ├── queries.json
│   ├── siis_responses.json
│   ├── deeplinks.json
│   └── samples/
│
├── src/
│   └── fixgraph/
│       ├── __init__.py
│       ├── app.py
│       ├── config.py
│       │
│       ├── api/
│       │   ├── routes.py
│       │   └── errors.py
│       │
│       ├── contracts/
│       │   ├── public.py
│       │   └── internal.py
│       │
│       ├── data/
│       │   ├── loaders.py
│       │   ├── fingerprints.py
│       │   └── deeplink_catalog.py
│       │
│       ├── query/
│       │   ├── normalizer.py
│       │   ├── symptom_parser.py
│       │   ├── case_signature.py
│       │   └── paraphrase.py
│       │
│       ├── evidence/
│       │   ├── resolver.py
│       │   └── provenance.py
│       │
│       ├── retrieval/
│       │   ├── bm25_index.py
│       │   ├── dense_index.py
│       │   ├── fusion.py
│       │   └── screen_resolver.py
│       │
│       ├── planning/
│       │   ├── action_extractor.py
│       │   ├── action_graph.py
│       │   ├── grouping.py
│       │   ├── risk.py
│       │   ├── sequencing.py
│       │   └── compiler.py
│       │
│       ├── validation/
│       │   ├── base.py
│       │   ├── schema.py
│       │   ├── text_rules.py
│       │   ├── url_hygiene.py
│       │   ├── deeplink_integrity.py
│       │   ├── grounding.py
│       │   ├── sequencing.py
│       │   └── pipeline.py
│       │
│       ├── cache/
│       │   ├── store.py
│       │   ├── matcher.py
│       │   └── invalidation.py
│       │
│       ├── providers/
│       │   ├── llm.py
│       │   ├── embedder.py
│       │   └── fakes.py
│       │
│       ├── observability/
│       │   ├── logging.py
│       │   └── metrics.py
│       │
│       └── service/
│           └── troubleshoot.py
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── e2e/
│   ├── adversarial/
│   ├── fixtures/
│   └── regression/
│
├── scripts/
│   ├── build_indexes.py
│   ├── warm_cache.py
│   ├── demo.py
│   ├── benchmark_cache.py
│   ├── benchmark_retrieval.py
│   ├── benchmark_latency.py
│   ├── run_ablation.py
│   └── clean_room_smoke.sh
│
├── reports/
│   ├── metrics.json
│   ├── metrics.md
│   ├── ablation.md
│   ├── RED_TEAM.md
│   └── FINAL_CONTRACT_AUDIT.md
│
└── docs/
    ├── ARCHITECTURE.md
    ├── AI_USAGE_LEDGER.md
    ├── CONTRACT_NOTES.md
    ├── REPO_AUDIT.md
    └── PPT_EVIDENCE.md
```

## Ownership boundaries

### `query/`
Understands wording. It does not decide final steps or deeplinks.

### `evidence/`
Controls what source text is permitted to support a plan.

### `retrieval/`
Resolves action intent to candidate Settings screens using catalog metadata.

### `planning/`
Builds action structure and order.

### `validation/`
Authoritative policy enforcement.

### `cache/`
Stores/reuses only already validated artifacts.

### `service/`
Orchestrates pipeline without embedding low-level logic.

## What not to add unless genuinely needed

- Kubernetes;
- Kafka;
- Neo4j;
- a separate microservice for every module;
- paid vector DB;
- Redis as a required dependency;
- frontend framework solely for decoration.

A single well-structured service is more reproducible for this hackathon.
