# Final Acceptance Checklist — GO / NO-GO

Do this on the exact commit you intend to tag.

## 1. Repository

- [ ] `git status` clean.
- [ ] no untracked required artifact.
- [ ] no secret/API key committed.
- [ ] official challenge assets preserved as required.
- [ ] README setup commands verified from clean environment.
- [ ] Docker build/run verified.

## 2. Contract

- [ ] `POST /v1/troubleshoot` correct.
- [ ] `GET /health` correct.
- [ ] 100% schema validity on regression/adversarial tests.
- [ ] pure JSON responses.
- [ ] exact goal syntax.
- [ ] title constraints enforced.
- [ ] description constraints enforced.
- [ ] score range enforced.
- [ ] one action = one screen.
- [ ] critical/destructive actions ordered last.
- [ ] manual actions have no actionable deeplink.

## 3. Safety/hygiene

- [ ] 0 web URL leaks.
- [ ] 0 fabricated deeplinks.
- [ ] no semantic matching on masked URI strings.
- [ ] every final action grounded in evidence.
- [ ] insufficient context produces safe fallback.
- [ ] low-confidence target screen produces safe fallback.

## 4. Cache

- [ ] only validated plans cached.
- [ ] catalog/schema/model/reference invalidation works.
- [ ] held-out paraphrase hit rate measured.
- [ ] hit rate >=80% target OR any shortfall clearly known before release.
- [ ] false-hit rate measured.
- [ ] hard-negative pairs pass.

## 5. Performance

- [ ] fast-path p50/p90/p95/p99 measured.
- [ ] fast-path P95 <=300 ms target.
- [ ] cold-path p50/p90/p95/p99 measured.
- [ ] cold-path P95 <=8 s target.
- [ ] hardware/runtime documented.

## 6. Testing

- [ ] unit tests pass.
- [ ] integration tests pass.
- [ ] e2e tests pass.
- [ ] supplied sample regressions pass.
- [ ] adversarial suite passes.
- [ ] determinism 50-run test passes.
- [ ] load test completes without corruption/crash.

## 7. Evidence

- [ ] metrics.md generated from current commit.
- [ ] ablation.md current.
- [ ] red-team report current.
- [ ] final contract audit has no unresolved P0 FAIL.
- [ ] architecture diagram matches actual code.

## 8. Demo

- [ ] cold multi-symptom demo works.
- [ ] unseen paraphrase cache-hit demo works.
- [ ] URL/fake-action safety demo works.
- [ ] demo can be reset/replayed.
- [ ] no secret shown on screen.
- [ ] video <=5 minutes.
- [ ] hosted video link opens in incognito/private window.

## 9. PPT

- [ ] official template used.
- [ ] correct college/team naming convention.
- [ ] team details correct.
- [ ] GitHub link correct.
- [ ] architecture correct.
- [ ] results are measured, not estimated.
- [ ] limitations included.
- [ ] checklist slide truthful.

## 10. AI disclosure

- [ ] form completed.
- [ ] AI usage ledger matches actual use.
- [ ] feature origins classified honestly.
- [ ] prompts/tools summarized without secrets.

## 11. Final tagged commit

Before tag:

```bash
git rev-parse HEAD
```

Record hash: `________________________`

Then:

```bash
git tag -a PRISM_GENAI_HACKATHON_Y2026 -m "Samsung PRISM GenAI Hackathon 2026 final submission"
git push origin PRISM_GENAI_HACKATHON_Y2026
```

After tag:

- [ ] remote tag exists.
- [ ] remote tag hash equals intended commit.
- [ ] all PPT/demo/README artifacts referenced by submission are present in that tagged commit.

## Final decision

```text
P0 CONTRACT       PASS / FAIL
P0 SAFETY         PASS / FAIL
P0 CACHE          PASS / FAIL
P0 PERFORMANCE    PASS / FAIL
TESTS             PASS / FAIL
REPRODUCIBILITY   PASS / FAIL
SUBMISSION FILES  PASS / FAIL
AI DISCLOSURE     PASS / FAIL

FINAL: GO / NO-GO
```
