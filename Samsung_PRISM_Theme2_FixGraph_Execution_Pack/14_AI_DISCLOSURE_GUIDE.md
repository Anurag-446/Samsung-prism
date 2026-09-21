# AI Usage Disclosure Guide

The supplied hackathon package includes an AI Usage Disclosure Form asking for team details, whether AI was used, purpose of use, feature-by-feature origin classification, tools/platforms, prompts, output summaries and modifications.

## 1. Maintain evidence while building

Create `docs/AI_USAGE_LEDGER.md` in the repo and update it as work happens.

Recommended columns:

| Feature | Origin | AI tool | Prompt ID | AI output summary | Human changes | Files |
|---|---|---|---|---|---|---|
| Architecture brainstorming | Both | ChatGPT | P-ARCH-01 | proposed verified pipeline | team selected/modified modules | docs/ARCHITECTURE.md |
| BM25 implementation | Both | coding agent | P-CODE-11 | initial index code | tests/bug fixes by team | src/... |
| URL validator | Both | coding agent | P-CODE-06 | validator + tests | expanded obfuscation cases | src/... |

## 2. Preserve prompts

Assign IDs to significant AI prompts, for example:

```text
P-IDEA-001
P-ARCH-001
P-CODE-001
P-TEST-001
P-DOC-001
```

Store either the full prompts or a concise traceable copy in the ledger/repo if permitted by your team policy.

## 3. Origin classification

Use the form's intended categories honestly:

- `Self-Generated`: team created without generative AI contribution;
- `AI-Generated`: generated substantially by AI with minimal modification;
- `Both`: AI assisted, team reviewed/changed/integrated.

For most coding-agent-assisted features, `Both` is usually the accurate classification when the team validates and modifies the result.

## 4. Do not disclose secrets

When recording prompts/output summaries:

- remove API keys;
- remove private tokens;
- remove proprietary credentials;
- do not paste hidden `.env` contents.

## 5. Compliance confirmation checklist

Before signing:

- [ ] all AI tools actually used are listed;
- [ ] major AI-assisted features are represented;
- [ ] prompts are traceable;
- [ ] human modifications are described;
- [ ] no proprietary/copyrighted data was knowingly misused;
- [ ] repository and form tell the same story.

## 6. Suggested statement for project documentation

> Generative AI tools were used for selected brainstorming, coding assistance, test generation and documentation tasks. All generated material was reviewed, modified where needed, integrated by the team, and validated through the project's automated contract, safety and performance test suites. The runtime system itself uses generative AI only within constrained intermediate stages; final deeplinks and contract compliance are determined programmatically from supplied assets.

Adjust this statement to match what your team actually did.
