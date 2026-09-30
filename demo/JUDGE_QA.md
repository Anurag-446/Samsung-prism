# Judge Q&A Preparation

**Q: How do you prevent hallucinated deeplinks?**
A: The LLM does not generate deeplinks. The LLM only generates conceptual actions (e.g., "Enable Wi-Fi"). The pipeline's Screen Resolver then performs a hybrid BM25+Dense retrieval against the *exact* official Samsung Bixby catalog. If the score doesn't pass our confidence threshold, the action is rejected entirely.

**Q: Why use hybrid retrieval?**
A: BM25 is great for exact keyword matches (e.g., "Bluetooth"), while Dense embeddings (SentenceTransformers) are great for semantic matches (e.g., "Earbuds" -> "Bluetooth"). Hybrid ensures we catch both without losing accuracy.

**Q: Why not let the LLM choose the setting directly?**
A: LLMs are probabilistic. They will occasionally invent a URI like `bixby://com.samsung.settings/FakeWifi` which causes the device to crash or error. By decoupling planning (LLM) from resolution (Retrieval against Catalog), we guarantee 100% valid URIs.

**Q: How is cache similarity made safe?**
A: A naive semantic cache just checks if the embedding similarity is >0.90. But "Battery draining" and "Battery not charging" are very close in embedding space but require totally different fixes. We use a `ValidationContext` and dimensional signature checks to ensure that domains and symptoms overlap before allowing a cache hit.

**Q: What happens with unsupported hardware damage?**
A: The Evidence Grounding module requires every action to be supported by SIIS troubleshooting evidence. There is no evidence for "shattered screen" settings. Therefore, the pipeline generates a graceful manual fallback.

**Q: How do you handle destructive actions?**
A: We have a Risk Sequencer that cross-references actions against a risk taxonomy. "Reset Network Settings" is classified as HIGH risk, and "Factory Data Reset" is DESTRUCTIVE. They are forcefully moved to the end of the action list, regardless of the LLM's original order.

**Q: Can this work without the internet?**
A: Yes. In demo mode, we use a `MockLLMProvider` and a local SQLite cache. All embeddings and BM25 indexes run entirely on-device via CPU. Only the real LLM generation (if enabled) requires external API access.
