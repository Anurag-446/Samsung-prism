"""Live LLM Provider using OpenAI API for structured reasoning."""
import json
from typing import List

import httpx
from pydantic import ValidationError

from fixgraph.contracts.internal import (
    CandidateActionExtractionResult,
    EvidenceSpan,
    SymptomAtom,
    SymptomExtractionResult,
)
from fixgraph.providers.base import LLMProvider
from fixgraph.providers.exceptions import ProviderError, ProviderResponseError, ProviderTimeoutError
from fixgraph.providers.prompts import (
    get_action_extraction_prompt,
    get_symptom_extraction_prompt,
)


class LiveLLMProvider(LLMProvider):
    def __init__(self, api_key: str, model_name: str, temperature: float, timeout: float, max_retries: int):
        if not api_key:
            raise ProviderError("API key is required for LiveLLMProvider")
        self.api_key = api_key
        self.model_name = model_name
        self.temperature = temperature
        self.timeout = timeout
        self.max_retries = max_retries

    @property
    def provider_id(self) -> str:
        return "openai"

    @property
    def model_id(self) -> str:
        return self.model_name

    def _call_openai(self, messages: list, schema: dict) -> dict:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": self.temperature,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "structured_output",
                    "schema": schema,
                    "strict": True
                }
            }
        }

        retries = 0
        while retries <= self.max_retries:
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    response = client.post(
                        "https://api.openai.com/v1/chat/completions",
                        headers=headers,
                        json=payload
                    )
                if response.status_code == 401:
                    raise ProviderError("Authentication failed with provider")
                response.raise_for_status()
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                return json.loads(content)
            except httpx.TimeoutException:
                retries += 1
                if retries > self.max_retries:
                    raise ProviderTimeoutError(f"Provider timed out after {self.max_retries} retries")
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                retries += 1
                if retries > self.max_retries:
                    raise ProviderResponseError(f"Provider HTTP error: {str(e)}")
            except json.JSONDecodeError:
                raise ProviderResponseError("Provider returned malformed JSON")

        raise ProviderError("Failed to call provider")

    def extract_symptoms(
        self, query: str, evidence: List[EvidenceSpan]
    ) -> SymptomExtractionResult:
        sys_prompt = get_symptom_extraction_prompt()
        evidence_text = "\n".join([f"[{e.evidence_id}] {e.text_content}" for e in evidence])

        user_prompt = f"USER COMPLAINT:\n{query}\n\nREFERENCE EVIDENCE:\n{evidence_text}"

        messages = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_prompt}
        ]

        schema = SymptomExtractionResult.model_json_schema()
        # Ensure additionalProperties is False for OpenAI structured outputs
        def _set_additional_properties_false(schema_obj):
            if isinstance(schema_obj, dict):
                if schema_obj.get("type") == "object":
                    schema_obj["additionalProperties"] = False
                for k, v in schema_obj.items():
                    _set_additional_properties_false(v)
            elif isinstance(schema_obj, list):
                for item in schema_obj:
                    _set_additional_properties_false(item)

        _set_additional_properties_false(schema)

        try:
            result_dict = self._call_openai(messages, schema)
            return SymptomExtractionResult.model_validate(result_dict)
        except ValidationError as e:
            raise ProviderResponseError(f"Schema validation error: {str(e)}")

    def extract_candidate_actions(
        self, query: str, symptoms: SymptomAtom, evidence: List[EvidenceSpan]
    ) -> CandidateActionExtractionResult:
        sys_prompt = get_action_extraction_prompt()
        evidence_text = "\n".join([f"[{e.evidence_id}] {e.text_content}" for e in evidence])

        user_prompt = f"USER COMPLAINT:\n{query}\n\nSYMPTOMS DETECTED:\n{symptoms.model_dump_json()}\n\nREFERENCE EVIDENCE:\n{evidence_text}"

        messages = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_prompt}
        ]

        schema = CandidateActionExtractionResult.model_json_schema()

        def _set_additional_properties_false(schema_obj):
            if isinstance(schema_obj, dict):
                if schema_obj.get("type") == "object":
                    schema_obj["additionalProperties"] = False
                for k, v in schema_obj.items():
                    _set_additional_properties_false(v)
            elif isinstance(schema_obj, list):
                for item in schema_obj:
                    _set_additional_properties_false(item)

        _set_additional_properties_false(schema)

        try:
            result_dict = self._call_openai(messages, schema)
            return CandidateActionExtractionResult.model_validate(result_dict)
        except ValidationError as e:
            raise ProviderResponseError(f"Schema validation error: {str(e)}")
