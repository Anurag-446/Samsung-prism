# Judging Alignment

This file maps project evidence to the official weighting in the supplied hackathon brief. It is not a guarantee of selection; it is a way to ensure the submission demonstrates its work clearly.

## 1. Working prototype & functionality — 30%

Evidence to prepare:

- live `/v1/troubleshoot` API;
- three demo scenarios;
- exact catalog deeplinks;
- semantic cache hit;
- safe fallback;
- Docker clean-room run;
- regression suite.

Best proof:

A single end-to-end demo where the result is not mocked and can be repeated from the tagged repository.

## 2. Technical depth & feasibility — 25%

Evidence:

- hybrid screen retrieval;
- source provenance;
- one-screen action graph;
- deterministic validation compiler;
- cache fingerprints/invalidation;
- risk-aware sequence policy;
- latency benchmark;
- clean provider abstractions.

Avoid adding architecture solely to sound complex. Every box should have a working implementation or be removed from the diagram.

## 3. Innovation & originality — 20%

Primary differentiators:

### Verified Action Graph

Explicit provenance from complaint to evidence to action to exact screen/deeplink.

### Semantic Case Lattice

Structured canonical signature + semantic fallback instead of raw sentence-vector caching alone.

### Deterministic compilation

The model produces an intermediate representation; deterministic passes produce trusted final output.

Strongest proof:

Ablation data showing why these mechanisms matter.

## 4. Relevance to theme — 15%

Keep the demo centered on the supplied requirements:

- vague complaints;
- SIIS/reference evidence;
- exact Settings deeplinks;
- logical ordering;
- cache speed.

Do not let a flashy unrelated dashboard dominate the presentation.

## 5. Presentation & documentation — 10%

Prepare:

- concise README;
- one architecture figure;
- measured results table;
- limitations;
- reproducible setup;
- <=5-minute demo;
- official PPT template completed;
- all artifacts in final tagged commit.

## 6. Questions the jury may ask

### Why not just prompt an LLM?

Answer with the measured/architectural difference: final deeplinks and compliance cannot be trusted to unconstrained generation; FixGraph resolves exact catalog records and runs deterministic validators.

### Why hybrid retrieval?

Show ablation: BM25 catches exact Settings vocabulary; dense retrieval catches paraphrases; consistency reranking reduces generic parent-menu matches.

### How do you stop hallucinations?

Evidence IDs + source-bounded extraction + catalog-only URI + deterministic final validation.

### What happens when you are unsure?

Low-confidence match is rejected and returns a safe fallback rather than guessing.

### How does cache avoid wrong reuse?

Structured signature compatibility gates plus semantic threshold, with hard-negative evaluation and false-hit rate reporting.

### Is the cache truly faster?

Show p95 and prove no LLM call occurs on hit.

### Can the system scale?

Discuss index sizes and architecture conservatively; do not claim production scale without load measurements.

### What are limitations?

State data/catalog coverage and model cold-path latency honestly.
