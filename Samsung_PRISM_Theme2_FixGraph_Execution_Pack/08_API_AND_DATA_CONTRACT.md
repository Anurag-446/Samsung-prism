# API and Data Contract Guide

## 1. Public API

### `POST /v1/troubleshoot`

Input shape described in the Theme 2 guide:

```json
{
  "query": "phone swipe gestures wrong direction after app install",
  "siis_response": "optional raw text context"
}
```

Rules:

- `query` is required and non-empty after normalization.
- `siis_response` is optional.
- if reference context is omitted, the engine may use its pre-warmed semantic cache and any challenge-provided indexed reference source; it must not fabricate troubleshooting knowledge.

### `GET /health`

Healthy response:

```json
{"status":"ok"}
```

Return 200 only when required local components are initialized.

## 2. Supplied core model concepts

The Theme 2 appendix defines model concepts including:

- `BaseDeeplink`
- `Deeplink`
- `Condition`
- `ResultTypes`
- `actionCategory`
- `ValidationDeeplink`
- `StepGroup`
- `Action`
- `Goal`
- `ContextDeeplinkResponse`

Do not re-interpret field semantics without checking the actual supplied `schema.py` in the starter repository.

## 3. Public output constraints

### Goal

Required syntax pattern:

```text
Follow these steps to perform this <Topic> Troubleshooting
```

or the corresponding `<Topic> Configuration` form when appropriate according to supplied guidance.

### Title

- 2-3 words;
- sentence case;
- identify core issue.

### Score

- float;
- inclusive range 0.0 to 1.0.

### Action name

- Title Case;
- exactly one physical screen or feature.

### Description

- exactly 5-7 words;
- starts with `It will`;
- explains concrete benefit.

### Steps

- imperative;
- UI-specific;
- one physical interaction per step where practical;
- no web URL/external link.

### Category

- `auto`: standard configuration screens reachable via deeplink;
- `critical`: disruptive or irreversible actions; order last;
- `manual`: physical/service interventions; no actionable deeplink.

### Deeplink

- exact value from the provided catalog;
- no URI generation, mutation or completion.

### Query variations

- 8-10 distinct paraphrases;
- include diverse registers such as formal, casual, keyword-only, frustrated and typo-inclusive;
- preserve meaning.

## 4. Internal schemas

Recommended internal models:

```python
NormalizedQuery
SymptomAtom
CaseSignature
EvidenceSpan
CandidateAction
ScreenCandidate
ResolvedAction
RiskTier
ValidationIssue
ValidationReport
RunMetrics
CacheEntry
```

These are not public challenge fields; keep them internal.

## 5. Provenance contract

Every `CandidateAction` should contain:

```text
action_id
intent
steps
evidence_ids
candidate_screen_text
risk_hint
```

Every `ResolvedAction` should additionally contain:

```text
catalog_record_id
screen_match_score
screen_match_components
exact_catalog_uri
risk_tier
```

This is how FixGraph proves that the final plan did not come directly from free-form model output.

## 6. Fallback semantics

Recommended internal reasons:

```text
no_siis_context
no_match
low_confidence_screen
invalid_plan
provider_timeout
provider_error
```

Public fallback still must conform to the actual supplied public response schema. Do not add fields to the official model unless the starter contract explicitly permits them.

## 7. Version/fingerprint contract

Persist:

```text
schema_version
catalog_sha256
reference_sha256
embedding_model_id
embedding_model_sha256_or_revision
signature_version
validator_version
```

A cache item is reusable only when compatibility checks pass.

## 8. Serialization

Use Pydantic serialization or equivalent and return application/json.

Do not use:

```text
```json
{...}
```
```

Do not prepend:

```text
Here is your troubleshooting plan:
```

The response body itself must be JSON.
