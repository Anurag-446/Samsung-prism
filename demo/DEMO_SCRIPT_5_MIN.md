# 5-Minute FixGraph Demo Script

## 0:00–0:30 | The Problem & The Insight
* **Visual:** Main UI Screen (Default view)
* **Voiceover:** "Hello! Traditional generative AI is great for text, but risky for device troubleshooting. Chatbots can hallucinate instructions or fabricate settings deeplinks that don't exist. FixGraph solves this by treating troubleshooting not as text generation, but as a verifiable planning problem. Every action is grounded in evidence and mapped to a mathematically verified Samsung Settings screen before it reaches the user."

## 0:30–1:10 | Architecture Overview
* **Visual:** `docs/ARCHITECTURE.md` (or presentation slide)
* **Voiceover:** "Here’s how it works: the user's complaint is analyzed to retrieve Samsung-approved SIIS evidence. An LLM acts only as a candidate planner. The core of FixGraph—the Validation Firewall—then takes over. It intercepts the plan, forces a semantic retrieval against the exact Bixby catalog, rejects uncertain matches, and orders the actions safely. Let’s see it live."

## 1:10–2:00 | Normal Troubleshooting Case
* **Visual:** Run "Battery & Location (Multi)" on UI
* **Voiceover:** "I’m submitting a multi-symptom issue: battery drain and location accuracy. FixGraph independently grounds each issue. Notice it returns *two* distinct actions. If we toggle Developer View, you can see it mapped 'location accuracy' to the precise Location Settings URI, and 'battery' to Device Care. The exact URI is validated—no hallucinations possible."

## 2:00–2:40 | Semantic Cache Paraphrase
* **Visual:** Run "Wi-Fi Drop", wait for finish, then re-run it slightly modified ("my wireless net drops").
* **Voiceover:** "Latency matters. For frequent issues, FixGraph uses a verifiable Semantic Cache. I just ran a Wi-Fi complaint, which took a cold-path. Now I'll ask the same thing but rephrased: 'my wireless net drops'. Notice the 'CACHE HIT' badge. It reused the validated plan safely in under 5 milliseconds. But importantly, our cache uses structural compatibility gates, preventing dangerous false positives on similar-sounding but different issues."

## 2:40–3:20 | Parent-Menu / Exact-Screen Resolution
* **Visual:** Run "Display (Parent Ambiguity)"
* **Voiceover:** "When an LLM suggests 'Display Settings', it's too broad. Here, the user wants to reduce refresh rate. The screen resolver detects that 'Motion Smoothness' is a more specific child screen than the parent 'Display' menu, applies a penalty to the parent, and correctly routes the user directly to the deep child screen."

## 3:20–4:00 | Safety Case: Fallbacks & Destructive Actions
* **Visual:** Run "Unsupported Hardware (Fallback)" then "Reset (Destructive)"
* **Voiceover:** "What happens when things go wrong? I'll type 'my camera lens is physically shattered.' FixGraph recognizes there's no software setting for physical damage and gracefully falls back to a manual support plan, rather than guessing. And if I ask to 'factory reset', the Risk Sequencer automatically flags it as DESTRUCTIVE, pushing it to the end of any troubleshooting chain."

## 4:00–4:35 | Red-Team & Evaluation Metrics
* **Visual:** Open `reports/FINAL_EVALUATION_REPORT.md`
* **Voiceover:** "We didn't just build this, we subjected it to a 130-case evaluation framework. FixGraph maintained a 0% false cache hit rate and successfully blocked 100% of adversarial prompt injections (like trying to force external URLs). The final safety gates are impenetrable."

## 4:35–5:00 | Conclusion
* **Visual:** Main UI Screen (Developer view open)
* **Voiceover:** "FixGraph demonstrates that generative AI can be securely harnessed for Samsung device troubleshooting by wrapping it in deterministic safety guarantees. Thank you!"
