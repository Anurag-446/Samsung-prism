"""Application bootstrap and dependency injection factory."""

import os
from typing import Optional

from fixgraph.config import Settings
from fixgraph.data.deeplink_catalog import DeeplinkCatalog
from fixgraph.data.fingerprints import compute_sha256_file
from fixgraph.data.loaders import ChallengeAssets, load_deeplink_catalog
from fixgraph.service.troubleshoot import TroubleshootService


class ConfigurationError(Exception):
    """Raised when runtime configuration is invalid or missing required assets."""

    pass


def get_mode() -> str:
    """Get the current execution mode (production, development, test)."""
    return os.environ.get("FIXGRAPH_MODE", "development").lower()


def build_challenge_assets(settings: Settings, mode: str) -> ChallengeAssets:
    """Resolve and validate challenge assets based on environment mode."""
    deeplinks_path = settings.get_resolved_path(settings.deeplinks_path)
    queries_path = settings.get_resolved_path(settings.queries_path)
    siis_path = settings.get_resolved_path(settings.siis_path)
    schema_path = settings.get_resolved_path(settings.challenge_assets_dir) / "schema.py"

    if mode == "production":
        if not deeplinks_path.is_file():
            raise ConfigurationError(f"Production mode requires {deeplinks_path} to exist.")

    # Compute fingerprints
    dl_hash = compute_sha256_file(deeplinks_path) if deeplinks_path.is_file() else ""
    q_hash = compute_sha256_file(queries_path) if queries_path.is_file() else None
    s_hash = compute_sha256_file(siis_path) if siis_path.is_file() else None
    schema_hash = compute_sha256_file(schema_path) if schema_path.is_file() else None

    return ChallengeAssets(
        deeplinks_path=deeplinks_path,
        queries_path=queries_path if queries_path.is_file() else None,
        siis_path=siis_path if siis_path.is_file() else None,
        schema_path=schema_path if schema_path.is_file() else None,
        samples_dir=None,
        deeplinks_sha256=dl_hash,
        queries_sha256=q_hash,
        siis_sha256=s_hash,
        schema_sha256=schema_hash,
    )


def build_catalog(
    settings: Settings, assets: ChallengeAssets, mode: str
) -> Optional[DeeplinkCatalog]:
    if not assets.deeplinks_path.is_file():
        return None

    is_test_fixture = ("fixtures" in str(assets.deeplinks_path).replace("\\", "/")) or (
        mode == "test"
    )

    if mode == "production" and is_test_fixture:
        raise ConfigurationError("Production mode cannot use synthetic test fixtures!")

    return load_deeplink_catalog(assets.deeplinks_path, is_test_fixture=is_test_fixture)


def build_service(
    settings: Settings, catalog: Optional[DeeplinkCatalog] = None
) -> TroubleshootService:
    """Build the troubleshoot service instance."""
    return TroubleshootService(
        catalog=catalog, cache_db_path=str(settings.get_resolved_path(settings.cache_db_path))
    )
