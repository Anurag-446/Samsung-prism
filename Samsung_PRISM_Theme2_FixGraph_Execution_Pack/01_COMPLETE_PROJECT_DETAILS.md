# FixGraph — Complete Project Details

## 1. Project title

**FixGraph: A Verified, Semantic-Cached Troubleshooting Compiler for Galaxy Devices**

Short pitch:

> FixGraph turns vague Galaxy-device complaints into evidence-grounded, schema-valid, deeplink-executable troubleshooting plans. A generative model interprets the complaint, while a deterministic verification layer guarantees source grounding, exact catalog deeplinks, safe action ordering, output hygiene, and low-latency reuse of previously validated cases.

## 2. Problem statement in practical terms

Users rarely describe device faults using clean technical vocabulary. They say things such as:

- “My phone got slow after the update.”
- “Screen flickers and battery dies fast.”
- “Swipes started going the wrong way after I installed an app.”

A support agent must normally map those descriptions to technical symptoms, find the relevant support guidance, decompose that guidance into physical interactions, determine which Settings screen each action belongs to, order operations safely, and communicate the result clearly.

FixGraph automates that pipeline while preserving the strict contracts in the hackathon specification.

## 3. Core functional requirements

### R1 — Complaint understanding

The system SHALL accept a natural-language complaint and optional supplied SIIS/reference text.

The system SHALL produce a normalized internal representation containing:

- domain(s),
- symptom atoms,
- trigger/context,
- candidate target features,
- risk indicators,
- semantic case signature,
- query variations for cache/evaluation.

### R2 — Evidence-bounded planning

Every troubleshooting action SHALL be traceable to provided/reference evidence.

If sufficient evidence is not available, FixGraph SHALL return an empty contexts list plus explicit fallback metadata internally; it SHALL NOT invent troubleshooting steps.

### R3 — Screen-specific actions

Each final `Action` SHALL correspond to one physical screen or one feature.

Multiple taps performed on the same screen MAY be grouped into the same action.

Steps spanning multiple screens SHALL NOT be collapsed into one action.

### R4 — Exact deeplink resolution

Actionable deeplinks SHALL be selected only from the supplied deeplink catalog.

The URI SHALL be copied verbatim after catalog lookup.

Masked URI strings SHALL NOT be used as semantic retrieval text. Candidate matching SHALL use metadata such as description, message and `qna_description`.

### R5 — Action sequencing

The system SHALL order lower-disruption operations before higher-disruption operations.

A simple internal ordering can be:

`inspect/configure -> optimize/restrict -> restart app/service -> reboot device -> safe mode/update/reset -> manual/repair`

The final rule set must preserve any category constraints in the supplied data contract.

### R6 — Output contract

Final responses SHALL be valid JSON objects and conform to the supplied Pydantic contract.

No markdown code fence, prose prefix, or prose suffix is permitted.

### R7 — Zero URL leakage

Any `http://`, `https://`, `www.`, or markdown-link syntax in generated/user/reference text SHALL be blocked or scrubbed before final serialization.

Catalog-approved masked `bixby://...` deeplinks are allowed only in the deeplink fields intended by the schema.

### R8 — Semantic caching

FixGraph SHALL match semantically equivalent/paraphrased complaints to previously validated plans.

The target supplied in the guide is >=80% unseen-paraphrase cache hit rate.

Cached path target: P95 <=300 ms.

### R9 — Determinism

Repeated identical inputs SHALL produce equivalent final plans after normalization, barring intentional version changes to data/indexes.

## 4. Proposed innovations

### 4.1 Verified Action Graph

Instead of allowing a model to generate an end-to-end answer, FixGraph represents reasoning as a graph:

```text
Complaint
   -> Symptom atoms
   -> Evidence spans
   -> Candidate actions
   -> Target screen/feature
   -> Catalog deeplink
   -> Verification gates
   -> Final plan
```

Every final action therefore has an auditable provenance chain.

### 4.2 Semantic Case Lattice

Naive semantic caching stores an embedding of the whole sentence. FixGraph additionally creates a structured fingerprint such as:

```text
DEVICE=phone
DOMAIN=battery
SYMPTOM=fast_drain
TRIGGER=post_update
CONSTRAINT=none
```

This normalized signature reduces cache fragmentation across slang, typos and paraphrases.

Use a two-stage cache lookup:

1. exact canonical-signature match;
2. semantic nearest-neighbor match with intent/domain compatibility gates.

### 4.3 Hybrid screen resolver

Use three signals for target-screen matching:

- lexical BM25 score,
- dense embedding similarity,
- rule/graph consistency score.

A possible fusion score:

`final_score = 0.35 * bm25_norm + 0.45 * dense + 0.20 * consistency`

Do not hard-code these weights as truth; tune them on supplied examples and a held-out synthetic paraphrase set.

### 4.4 Risk-aware action ordering

Assign each action a disruption tier rather than relying on prompt language. Suggested tiers:

- Tier 0: inspect/read setting
- Tier 1: reversible toggle/configuration
- Tier 2: app-level restriction or temporary cleanup
- Tier 3: app/service restart
- Tier 4: device reboot
- Tier 5: safe mode, firmware/update recovery
- Tier 6: reset/destructive/manual repair

Topological constraints can be added when one action must precede another.

### 4.5 Deterministic validation compiler

Treat generation as an untrusted intermediate representation.

Final response compilation runs deterministic passes:

1. schema pass,
2. word-count pass,
3. exact-goal-syntax pass,
4. action-screen granularity pass,
5. source-evidence pass,
6. URL hygiene pass,
7. deeplink-catalog integrity pass,
8. action ordering pass,
9. duplicate action pass,
10. JSON-only serialization pass.

## 5. Intended user flow

```text
POST /v1/troubleshoot
  query + optional siis_response
        |
        v
normalize / canonicalize
        |
        +--> cache lookup --> validated cached response --> return
        |
        v
retrieve/parse reference evidence
        |
        v
extract candidate actions
        |
        v
resolve each action to exact screen
        |
        v
map screen to catalog deeplink
        |
        v
order + group
        |
        v
validate / repair / reject
        |
        v
cache validated artifact
        |
        v
return pure JSON + operational metadata
```

## 6. Scope boundaries

### In scope

- Four primary device domains supplied by the starter dataset, including Battery, Display, Camera and Performance.
- Multi-symptom complaints.
- Typos, informal language and frustrated wording.
- Optional SIIS context supplied at request time.
- Catalog-backed Settings deeplinks.
- Semantic cache.
- API, local reproducible setup, Docker, tests, metrics.

### Out of scope for the hackathon prototype

- Arbitrary web search.
- Live device control.
- Unsupported device domains without reference evidence.
- Fabricated service-center advice.
- Any deeplink not present in the supplied catalog.
- Production authentication/authorization beyond minimal API hardening.

## 7. Success criteria

A submission-ready build should satisfy all of the following:

1. 100% supplied-schema conformance on the internal evaluation suite.
2. 0 web URL leaks over the adversarial suite.
3. 0 fabricated deeplinks.
4. 0 actionable deeplinks attached to manual-only actions.
5. 0 critical/destructive actions placed ahead of clearly safer alternatives, except where reference evidence requires otherwise.
6. >=80% semantic paraphrase cache hit rate on a held-out paraphrase set.
7. P95 cache-hit latency <=300 ms in local benchmark.
8. P95 cold path <=8 s under the selected model/runtime environment.
9. Deterministic exact-plan equivalence for repeated identical requests.
10. Reproducible Docker/README setup from a clean machine.

## 8. Differentiation statement

The differentiator is not “we use RAG.” The differentiator is the **verified compilation pipeline**:

- generation is treated as untrusted;
- evidence, action, screen and deeplink remain separately represented;
- only catalog-approved deeplinks are emitted;
- deterministic guards enforce output constraints;
- the final validated plan becomes a reusable semantic case artifact.

This makes the system easier to audit, benchmark and explain than a single-prompt chatbot.

## 9. What to show in the demo

Use three cases:

### Demo A — multi-symptom cold path

A complaint containing two symptoms, e.g. Display + Battery. Show:

- symptom decomposition,
- separate evidence retrieval,
- merged action plan,
- exact deeplink resolution,
- final safe order.

### Demo B — paraphrase fast path

Issue a very different paraphrase of Demo A. Show:

- semantic cache hit,
- same validated plan family,
- latency <300 ms target,
- no LLM call/cost on cache hit.

### Demo C — safety failure

Feed reference text containing a web URL or ask for an unsupported action. Show:

- URL removed/rejected,
- no hallucinated action,
- no fabricated deeplink,
- graceful fallback.

## 10. Naming

Recommended repo name:

`fixgraph-prism-theme2`

Recommended package name:

`fixgraph`

Recommended API service name:

`fixgraph-api`
