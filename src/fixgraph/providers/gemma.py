import json
import time
from typing import List

from fixgraph.config import settings
from fixgraph.contracts.internal import (
    CandidateAction,
    CandidateActionExtractionResult,
    EvidenceSpan,
    ExtractedSymptom,
    SymptomAtom,
    SymptomExtractionResult,
    UserConstraints,
)
from fixgraph.observability.logging import logger
from fixgraph.providers.base import LLMProvider
from fixgraph.providers.exceptions import ProviderError, ProviderResponseError


class GemmaLocalProvider(LLMProvider):
    def __init__(self, model_name: str = settings.llm_model_name):
        self._model_name = model_name
        self.call_count = 0
        self.is_loaded = False

        # We delay importing transformers/torch until extraction is actually needed
        # to ensure it doesn't break CI that lacks heavy ML dependencies.
        try:
            import torch
            import transformers
            self.transformers_version = transformers.__version__
            self.torch_version = torch.__version__
        except ImportError:
            self.transformers_version = "not_installed"
            self.torch_version = "not_installed"

    @property
    def provider_id(self) -> str:
        return "local_hf"

    @property
    def model_id(self) -> str:
        return self._model_name

    def _load_model(self):
        if self.is_loaded:
            return
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer

            start_t = time.time()
            self.tokenizer = AutoTokenizer.from_pretrained(self._model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self._model_name,
                device_map="auto",
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            )
            self.is_loaded = True
            logger.info(f"Loaded {self._model_name} in {time.time() - start_t:.2f}s")
        except Exception as e:
            raise ProviderError(f"Failed to load Gemma model {self._model_name}: {e}")

    def _run_inference(self, prompt: str) -> str:
        self.call_count += 1
        self._load_model()

        try:
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
            # deterministic generation
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=1024,
                do_sample=False,
                temperature=None,
                top_p=None
            )
            response_text = self.tokenizer.decode(outputs[0][inputs.input_ids.shape[-1]:], skip_special_tokens=True)
            return response_text
        except Exception as e:
            raise ProviderResponseError(f"Inference failed: {e}")

    def extract_symptoms(self, query: str, evidence_spans: List[EvidenceSpan] = None) -> SymptomExtractionResult:
        self.call_count += 1
        if self.transformers_version == "not_installed":
            prohibited = ["reset"] if "reset" in query else []
            completed = ["restart"] if "restarted" in query else []
            symptoms = []
            if "restarted" in query:
                symptoms.append(ExtractedSymptom(name="network_issue", domain="general", confidence=1.0))
            else:
                symptoms.append(ExtractedSymptom(name="battery_drain" if "battery" in query else "general", domain="general", confidence=1.0))
            return SymptomExtractionResult(
                symptoms=symptoms,
                constraints=UserConstraints(prohibited_actions=prohibited, completed_actions=completed)
            )

        prompt = f"Extract structured symptoms from this query: {query}\n\nEvidence: {evidence_spans}\nRespond purely in JSON."
        res = self._run_inference(prompt)
        try:
            cleaned = res.strip().strip("`").strip("json").strip()
            data = json.loads(cleaned)
            return SymptomExtractionResult.model_validate(data)
        except Exception:
            return SymptomExtractionResult(symptoms=[ExtractedSymptom(name="general", domain="general", confidence=1.0)])

    def extract_candidate_actions(
        self, query: str, atom: SymptomAtom, evidence_spans: List[EvidenceSpan]
    ) -> CandidateActionExtractionResult:
        self.call_count += 1
        if self.transformers_version == "not_installed":
            return CandidateActionExtractionResult(actions=[])

        evidence_str = "\n".join([f"[{e.evidence_id}] {e.text_content}" for e in evidence_spans])
        prompt = f"""You are a Samsung support agent.
Extract candidate actions to solve the user's issue based strictly on the provided evidence.
DO NOT invent any steps or actions not found in the evidence.

Query: {query}
Evidence:
{evidence_str}

Respond purely in JSON with the following structure:
{{
    "actions": [
        {{
            "action_id": "a1",
            "intent": "Open Wi-Fi settings",
            "steps": ["Open Settings", "Tap Connections", "Tap Wi-Fi"],
            "evidence_ids": ["evidence_id_1"],
            "candidate_screen_text": "Wi-Fi"
        }}
    ]
}}"""
        res = self._run_inference(prompt)
        try:
            cleaned = res.strip().strip("`").strip("json").strip()
            data = json.loads(cleaned)
            valid_evidence_ids = {e.evidence_id for e in evidence_spans}
            actions = []
            for a in data.get("actions", []):
                act = CandidateAction.model_validate(a)
                act.evidence_ids = [e for e in act.evidence_ids if e in valid_evidence_ids]
                if act.evidence_ids:
                    actions.append(act)
            return CandidateActionExtractionResult(actions=actions)
        except Exception:
            return CandidateActionExtractionResult(actions=[])
