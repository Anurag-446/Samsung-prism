# Developer and AI-Agent Instructions

## 1. Non-negotiable rules

1. **Do not edit the challenge requirements to fit the implementation.**
2. **Do not fabricate missing starter assets.** If an asset is not present, stop that path and record the dependency.
3. **Do not synthesize deeplinks.** Exact URIs come from the provided catalog only.
4. **Do not use masked URI strings as semantic retrieval text.**
5. **Do not use the web as a troubleshooting knowledge source** for final plans unless the challenge explicitly supplies/permits it. This design assumes supplied evidence only.
6. **Do not cache invalid plans.**
7. **Do not let an LLM decide whether its own output is compliant.** Deterministic validators are authoritative.
8. **Do not hide failing tests or metrics.** Fix root causes.
9. **Do not claim a metric until a reproducible script has produced it.**
10. **Do not put API keys in code, notebooks, commits, screenshots or demo videos.**

## 2. Coding standards

- Python 3.11+.
- Type core domain objects.
- Prefer pure functions for validators and transformations.
- Use dependency injection for model, embedder, cache and stores.
- Keep route handlers thin.
- Keep all thresholds configurable.
- Add a regression test for every bug fixed.
- Stable sort any list that can affect final output.
- Never rely on dictionary/set iteration order for semantic decisions.
- Avoid unnecessary framework complexity.

## 3. Branch/commit strategy

Suggested branches:

```text
main
feat/contracts
feat/retrieval
feat/planner
feat/cache
feat/api
feat/evaluation
feat/submission
```

Commit style:

```text
feat(cache): add semantic case signature lookup
fix(validator): reject markdown URL leakage
perf(retrieval): precompute catalog embeddings
test(adversarial): add parent-menu trap cases
docs(submission): add reproducible benchmark table
```

## 4. Definition of done for a feature

A feature is DONE only when:

- implementation exists;
- unit tests exist;
- integration behavior is covered if applicable;
- lint/type checks relevant to it pass;
- failure behavior is defined;
- metrics/logging are added where needed;
- documentation is updated;
- no P0 contract rule is weakened.

## 5. LLM usage policy inside FixGraph

The model may:

- normalize colloquial language;
- identify symptom atoms;
- decompose evidence-supported guidance into candidate actions;
- produce query paraphrases under a constrained schema.

The model must not be trusted to:

- generate a deeplink URI;
- decide whether a URI exists in the catalog;
- bypass source evidence;
- determine final schema compliance;
- bypass URL hygiene;
- decide critical action order without deterministic policy;
- write directly to the semantic cache.

## 6. Prompt design inside the application

Every production prompt should:

- state that supplied evidence is the only permitted troubleshooting source;
- request a typed/structured intermediate representation;
- forbid URLs and deeplinks in model-generated action text;
- require evidence IDs for each action;
- use low/zero temperature;
- include only necessary context;
- have explicit timeout and token limits.

## 7. Failure philosophy

Prefer:

```text
safe no-match
```

over:

```text
confident but fabricated plan
```

For uncertain screen resolution, reject the mapping rather than returning a plausible parent menu.

## 8. Performance discipline

Do not optimize before measuring, but do not put avoidable LLM calls in the critical path.

Fast path must be:

```text
normalize -> signature/embed -> cache match -> deserialize validated plan -> return
```

No LLM call on a valid cache hit.

## 9. Review checklist for every pull request

- Does this change touch a P0 rule?
- Can this introduce a fabricated deeplink?
- Can this leak an external URL?
- Can it cause an unsupported action to pass?
- Can it make cache false positives worse?
- Can it make output nondeterministic?
- Does it change benchmark methodology?
- Are new thresholds justified by data?
- Is a new dependency really necessary?
- Is README/setup still reproducible?

## 10. AI coding-agent behavior

When a coding agent is unsure:

1. inspect actual repository files;
2. inspect actual supplied schema and examples;
3. state the ambiguity;
4. write a failing test representing the requirement;
5. implement the smallest compliant change.

It must never invent a field or challenge rule because it “seems reasonable.”
