# FixGraph — Samsung PRISM Theme 2

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)
![Status](https://img.shields.io/badge/Status-Submission_Ready-success.svg)

**FixGraph** transforms a Samsung Galaxy troubleshooting complaint into a deterministic, evidence-bounded, risk-ordered sequence of verified Settings actions. It acts as a safety compiler for GenAI, preventing unsupported or fabricated deeplinks from ever reaching the user.

## Why FixGraph?
Traditional LLM chatbots hallucinate. They invent fake Bixby URIs, propose destructive resets immediately, or offer software fixes for broken hardware. FixGraph removes the generative risk. 

**Our Guarantees:**
1. **Zero Hallucinated Deeplinks**: The LLM *never* writes URLs. It only plans concepts. FixGraph maps these concepts to the exact Samsung catalog using Hybrid Dense/BM25 retrieval.
2. **Evidence-Grounded**: Actions lacking support in official SIIS documents are stripped.
3. **Zero False Cache Hits**: We don't just use cosine similarity. We enforce structural compatibility gates to prevent dangerous false-positive matches for similar-sounding issues.
4. **Deterministic Risk Sorting**: Factory resets and destructive actions are automatically reordered to the end of any troubleshooting plan by a deterministic firewall.

## Quick Start (Judge / Demo Mode)
Ensure you have Python 3.11+ installed.
```bash
python -m venv .venv
# Activate venv: .venv\Scripts\Activate.ps1 (Windows) or source .venv/bin/activate (Linux/Mac)
pip install -e ".[dev]"
python scripts/run_dev.py
```
Open [http://localhost:8000/](http://localhost:8000/) to access the FixGraph Product Dashboard.

## Architecture Highlights
* **One-Action, One-Screen**: Resolves ambiguous parent menus (e.g., "Display") by actively searching for specific child deep-links (e.g., "Motion Smoothness").
* **Validation Firewall**: A strict schema filter that audits all generated plans.
* **Semantic Cache Lattices**: Sub-5ms response times for repeated problems without contacting the LLM.

## Reproducible Evaluation
We evaluated FixGraph on a 130-case synthetic matrix, testing prompt injection, destructive ordering, and multi-symptom complaints.
```bash
python scripts/run_full_evaluation.py --suite all --provider mock
```
Read the full report at `reports/FINAL_EVALUATION_REPORT.md`.

## Repository Map
- `src/fixgraph/web/`: Modern Product Dashboard UI.
- `src/fixgraph/api/`: FastAPI backend and core compiler limits.
- `src/fixgraph/validation/`: The deterministic safety firewall rules.
- `demo/`: Auto-runner and presentation scripts.
- `eval/`: Raw testing datasets and configurations.
