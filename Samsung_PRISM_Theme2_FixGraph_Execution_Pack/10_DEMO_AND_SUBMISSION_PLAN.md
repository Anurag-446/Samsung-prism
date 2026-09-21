# Demo and Submission Plan

## 1. Submission requirements from supplied brief

Final submission deadline: **25 September 2026, 11:59 PM**.

Required submission items include:

- working prototype code in a public/shared GitHub repository;
- README with reproducible setup;
- Docker files and required setup artifacts;
- demo video, maximum 5 minutes, via YouTube or Drive link;
- presentation file using the supplied template/nomenclature;
- one team submission through the supplied form.

The brief states that the final judged commit should be tagged:

`PRISM_GENAI_HACKATHON_Y2026`

Everything referenced in PPT/demo/documentation must exist in that tagged commit.

## 2. Five-minute demo script

### 0:00-0:25 — Problem

Explain:

- users describe faults vaguely;
- ordinary LLMs can hallucinate steps/links;
- Settings navigation needs exact screen resolution;
- validated repeat cases should be instant.

### 0:25-0:55 — Architecture

Show one diagram:

```text
Complaint -> normalize -> cache?
                     miss -> evidence -> candidate actions
                          -> exact screen resolver
                          -> catalog deeplink
                          -> safety compiler
                          -> validated cache
```

State clearly: the LLM never gets final authority over deeplinks or compliance.

### 0:55-2:10 — Demo A: cold multi-symptom case

Example:

`Screen flickers and battery dies fast after the update.`

Show:

- two symptom atoms;
- evidence provenance;
- action grouping;
- exact screen candidates;
- safe sequence;
- final JSON;
- cold latency.

### 2:10-2:55 — Demo B: unseen paraphrase cache hit

Use a wording that was not the original warm query.

Show:

- normalized signature;
- semantic cache match;
- no LLM call;
- same validated plan family;
- fast-path latency.

### 2:55-3:40 — Demo C: adversarial safety

Reference text contains a web URL or asks the system to invent a support URL/deeplink.

Show:

- URL hygiene gate;
- exact catalog verification;
- safe rejection/fallback.

### 3:40-4:20 — Metrics

Only show measured values:

- schema validity;
- URL leaks;
- fabricated deeplinks;
- screen top-1/top-3;
- parent-menu error;
- paraphrase hit rate + false-hit rate;
- fast/cold P95.

### 4:20-4:50 — Innovation

Three points:

1. Verified Action Graph.
2. Semantic Case Lattice.
3. Deterministic safety compiler with hybrid exact-screen resolution.

### 4:50-5:00 — Closing

One sentence:

> FixGraph makes generative troubleshooting useful by making the final plan verifiable, executable and reusable.

## 3. Official PPT mapping

The supplied deck contains these slides.

### Slide 1 — Team details

Fill Theme ID 02, team, college, member names/emails, GitHub link.

### Slide 2 — Theme

Summarize the provided Smart Guided Troubleshooting Engine problem in your own words.

### Slide 3 — Existing Solutions & Gaps

Use a 3-column comparison:

| Approach | Strength | Gap |
|---|---|---|
| Keyword support search | simple | weak on vague language |
| Generic LLM | flexible | hallucination/URL/deeplink risk |
| Plain RAG | grounded text | not necessarily exact-screen/action-safe |
| FixGraph | grounded + verified + executable | prototype scope limited to supplied data |

### Slide 4 — Our Solution & Architecture

Use the architecture diagram from `02_ARCHITECTURE.md`.

### Slide 5 — Demo & Product Walkthrough

Three screenshots: cold case, cache hit, safety rejection.

### Slide 6 — Tools and Tech Stack

Only list what is actually used.

### Slide 7 — Impact & Use Case

Focus on:

- reducing manual interpretation;
- exact one-tap navigation;
- deterministic support consistency;
- reuse of validated cases.

Avoid claiming enterprise cost savings unless measured.

### Slide 8 — Innovation, Results, Limitations

Use measured metrics plus candid limitations.

### Slide 9 — What's Next

Possible extensions:

- broader device domains;
- richer device/OS-version compatibility;
- online feedback from resolved cases;
- multilingual complaint normalization;
- production support analytics.

### Slide 10 — Brownie points / differentiation

Show ablations and provenance graph.

### Slide 11 — Checklist

Mark Y only after artifact exists and has been verified.

### Slide 12 — Thank you

Add repo/demo QR only if allowed and tested; otherwise keep clean.

## 4. README sections

1. Project summary
2. Why this is different
3. Architecture
4. Starter asset expectations
5. Setup
6. Environment configuration
7. Run API
8. Example request/response
9. Tests
10. Benchmarks
11. Results
12. Failure/safety behavior
13. Demo
14. AI usage disclosure
15. Limitations
16. License/attribution as applicable

## 5. Final Git procedure

Before tagging:

```bash
git status
git diff --check
ruff check .
pytest -q
```

Run final benchmarks and verify generated results.

Then manually tag approved final commit:

```bash
git tag -a PRISM_GENAI_HACKATHON_Y2026 -m "Samsung PRISM GenAI Hackathon 2026 final submission"
git push origin PRISM_GENAI_HACKATHON_Y2026
```

Verify remote tag points to intended commit.
