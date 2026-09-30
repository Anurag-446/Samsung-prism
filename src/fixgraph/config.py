"""Typed application settings for FixGraph configuration."""

from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    env: str = "development"
    log_level: str = "INFO"
    host: str = "0.0.0.0"
    port: int = 8000

    # LLM settings
    llm_provider: str = "mock"  # "mock", "openai", "azure"
    llm_api_key: Optional[str] = None
    llm_model_name: str = "gpt-4o-mini"
    llm_temperature: float = 0.0
    llm_timeout_seconds: float = 10.0
    llm_max_retries: int = 1
    min_action_evidence_score: float = 0.35

    # Embedding settings
    embedding_model_name: str = "all-MiniLM-L6-v2"
    similarity_threshold: float = 0.82
    cache_min_margin: float = 0.05
    cache_store_raw_query: bool = False

    # Storage paths
    cache_db_path: str = "data/cache.db"
    challenge_assets_dir: str = "tests/fixtures/challenge_assets"
    deeplinks_path: str = "tests/fixtures/challenge_assets/deeplinks.json"
    queries_path: str = "tests/fixtures/challenge_assets/queries.json"
    siis_path: str = "tests/fixtures/challenge_assets/siis_responses.json"

    # Latency targets (ms)
    cache_hit_p95_limit_ms: float = 300.0
    cold_path_p95_limit_ms: float = 8000.0

    # Safety limits
    max_query_chars: int = 1000
    request_timeout_seconds: float = 15.0
    cache_enabled: bool = True

    def get_resolved_path(self, rel_or_abs_path: str) -> Path:
        path = Path(rel_or_abs_path)
        if path.is_absolute():
            return path
        return Path.cwd() / path


settings = Settings()
