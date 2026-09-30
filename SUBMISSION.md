# FixGraph Final Submission

**Team**: Samsung PRISM GenAI Hackathon 3.0 Theme 2 Execution  
**Project**: FixGraph (Smart Guided Troubleshooting Engine)

## Executive Summary
FixGraph is not a chatbot. It is a deterministic safety compiler built around an LLM. By decoupling the generative planning (LLM) from the resolution execution (FixGraph Hybrid Resolver), we guarantee 100% adherence to the official Samsung Bixby catalog without hallucinated URIs.

## Core Innovations
1. **Deterministic Final Validation**: No plan reaches the user unless it passes the strict validation constraints. 
2. **Hybrid Exact-Screen Resolution**: The LLM suggests a setting, but FixGraph calculates the exact target using Dense and BM25 embeddings, explicitly penalizing vague parent menus to find specific child screens.
3. **Risk Sequencer**: The firewall intercepts the final plan and structurally forces any destructive actions to the bottom of the list.
4. **Semantic Cache Lattices**: We achieve sub-5ms latencies using SQLite Vector-emulation Cache. But unlike basic RAG, we apply rigorous multi-dimensional domain filters to guarantee zero false-positive cache hits.

## How to Test
A full demo suite, evaluation matrix, and clean-room installer are provided in this repository. 
1. Run `python demo/run_demo.py` to see automated adversarial handling.
2. Run `python scripts/run_dev.py` and open `http://localhost:8000/` to use the Dashboard UI.

We look forward to demonstrating FixGraph!
