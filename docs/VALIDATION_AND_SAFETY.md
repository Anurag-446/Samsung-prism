# FixGraph Validation and Safety Firewall (Phase 5)

## Overview
The Phase 5 execution pipeline enforces strict deterministic policies through a centralized `FinalValidationGate`. The core invariant is that **no plan leaves FixGraph unless it completely passes the final validation pipeline**. 

## Validation Architecture
All paths (Cold pipeline, Semantic Cache Hit, Fallback generation, and Repair outcomes) route through a single `FinalValidationGate` object instance.

```mermaid
graph TD
    A[Cold/Cache Result] --> B[Compiler]
    B --> C{Validation Firewall}
    C -- PASS --> D[Cache / Serve]
    C -- FAIL --> E[Deterministic Repair]
    E --> F{Validation Firewall}
    F -- PASS --> D
    F -- FAIL --> G[Safe Reason-Specific Fallback]
    G --> H{Validation Firewall}
    H -- PASS --> I[Serve]
    H -- FAIL --> J[Controlled API Failure (500)]
```

## Validators Implemented
The validation framework runs several `GoalValidator` components:
- **TitleValidator**: Ensures titles are 2-5 words.
- **DescriptionValidator**: Ensures descriptions begin with "It will" and are 5-7 words.
- **StepValidator**: Blocks empty, duplicated, or leaked internal reasoning (e.g. "According to evidence...").
- **QueryVariationValidator**: Ensures 8-10 distinct variations.
- **DeeplinkIntegrityValidator**: Asserts that every non-manual action contains a valid URI mapped exactly to a catalog record without duplication.
- **RiskOrderValidator**: Prevents destructive/CRITICAL actions from appearing before reversible/AUTO actions.
- **UserConstraintValidator**: Respects SIIS context restrictions.
- **URLLeakValidator**: Rejects user-visible strings containing `http://`, `file://`, or system artifacts.
- **DuplicateActionValidator**: Prevents identical semantic actions.

## Risk Policy Implementation
Risk classification maps to `CategoryEnum` (AUTO, CRITICAL, MANUAL). `FinalValidationGate` strictly blocks risk inversions, preventing dangerous operations without attempting reversible fixes first.

## Deterministic Repair
Failed validation triggers `DeterministicRepairPass`, attempting whitespace and basic normalization. It strictly prohibits fabricating new steps, evidence, or URIs.

## Fallback Design
If a plan fails validation entirely, `TroubleshootService` falls back to reason-aware, MANUAL-only action categories ("no_evidence", "provider_error", etc.). It **never** fabricates a URI. 

## API Errors & Observability
- 5xx errors returned explicitly for pipeline or safety firewall failures.
- `X-Request-ID` is extracted and tracked end-to-end.
- Outputs structured JSON logs encompassing request, token counts, latency, and status.

## Determinism
A new test harness `scripts/check_determinism.py` verifies the pure execution flow (without caching or network noise) always outputs identically deterministic hashes.
