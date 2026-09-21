# Source Requirements Notes

This pack was prepared from the supplied Samsung PRISM GenAI Hackathon 3.0 package, specifically the general hackathon brief, Theme 2 guide, official submission PPT template and AI usage disclosure form.

## Theme 2 guide items incorporated

- Smart Guided Troubleshooting Engine target.
- Vague complaint -> machine-actionable troubleshooting plan.
- Phase pipeline: query enrichment, structure extraction, deeplink mapping/sequencing, semantic fast-path cache, REST API.
- Starter asset names described in the guide: `queries.json`, `siis_responses.json`, `deeplinks.json`, `bixby://dummy_positive`, `samples/`, `schema.py`.
- Goal/title/score/action/description/step/category/deeplink/query-variation constraints.
- Non-negotiables: no web URLs, exact catalog URI, no unsupported/hallucinated steps, pure JSON.
- Endpoints: `POST /v1/troubleshoot`, `GET /health`.
- Evaluation: schema, zero leakage, determinism, exact-screen precision, paraphrase cache, plan hierarchy, latency and cost.
- Targets: paraphrase cache >=80%, cache-hit P95 <=300 ms, cold path P95 <=8 s.
- Milestones: validation -> semantic indexing -> cache -> API/verification.

## General hackathon brief items incorporated

- Working prototype submitted in first build round.
- Evaluation weights: 30/25/20/15/10.
- Final submission due 25 Sep 2026, 11:59 PM.
- Public/shared GitHub repo, README/reproducible setup, demo <=5 minutes, PPT/PDF.
- Release tag `PRISM_GENAI_HACKATHON_Y2026` on final judged commit.
- Everything referenced in submission should exist in tagged commit.

## Important caution

The detailed Theme 2 guide refers to starter assets that were not present in the ZIP analyzed here itself. They may be distributed separately in the registered challenge repository/package. The implementation must inspect the actual starter repository and **must not fabricate these files** if they are absent.
