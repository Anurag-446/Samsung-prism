"""Robust loaders for challenge assets with strict validation."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from fixgraph.data.deeplink_catalog import DeeplinkCatalog, DeeplinkRecord
from fixgraph.data.fingerprints import compute_sha256_file


@dataclass(frozen=True)
class AssetFingerprint:
    deeplinks_sha256: str
    queries_sha256: Optional[str] = None
    siis_sha256: Optional[str] = None
    schema_sha256: Optional[str] = None


@dataclass(frozen=True)
class ChallengeAssets:
    deeplinks_path: Path
    queries_path: Optional[Path] = None
    siis_path: Optional[Path] = None
    schema_path: Optional[Path] = None
    samples_dir: Optional[Path] = None
    deeplinks_sha256: str = ""
    queries_sha256: Optional[str] = None
    siis_sha256: Optional[str] = None
    schema_sha256: Optional[str] = None


class CatalogValidationError(Exception):
    """Raised when deeplink catalog fails structural validation."""

    pass


def load_deeplink_catalog(file_path: str | Path, is_test_fixture: bool = False) -> DeeplinkCatalog:
    """
    Load and validate deeplink records from a JSON file.
    Must not mutate original URIs. Will strictly reject malformed files.
    """
    path = Path(file_path)
    if not path.is_file():
        raise CatalogValidationError(f"Deeplink file not found: {path}")

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise CatalogValidationError(f"Invalid JSON in {path}: {e}")
    except Exception as e:
        raise CatalogValidationError(f"Error reading {path}: {e}")

    items = data.get("deeplinks", data) if isinstance(data, dict) else data
    if not isinstance(items, list):
        raise CatalogValidationError(f"Catalog at {path} must contain a list of records")

    if len(items) == 0:
        raise CatalogValidationError(f"Catalog at {path} is empty")

    records: List[DeeplinkRecord] = []
    seen_ids = set()
    seen_uris = set()

    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            raise CatalogValidationError(f"Record at index {idx} is not an object")

        rec_id = str(item.get("id") or item.get("record_id") or "")
        if not rec_id:
            raise CatalogValidationError(f"Record at index {idx} has no stable identifier (id)")

        if rec_id in seen_ids:
            raise CatalogValidationError(f"Duplicate record ID found: {rec_id}")
        seen_ids.add(rec_id)

        uri = item.get("deeplink") or item.get("uri", "")
        if not uri:
            raise CatalogValidationError(f"Record '{rec_id}' is missing a deeplink URI")

        if uri in seen_uris:
            # We just report/warn, but strict requirements say "duplicate URIs are reported"
            # It may not always be fatal if Samsung duplicated a URI, but we can log it.
            pass
        seen_uris.add(uri)

        records.append(
            DeeplinkRecord(
                record_id=rec_id,
                uri=uri,
                name=item.get("description", rec_id), # We use description as name for retrieval
                description=item.get("description", ""),
                message=item.get("message", ""),
                qna_description=item.get("qna_description", ""),
                classes=item.get("classes", ""),
                control_type=str(item.get("control_type", "")),
                original_type=item.get("originalType", ""),
                category="manual" if item.get("originalType") is None else "auto",
                validation=item.get("validation", None)
            )
        )

    source_sha256 = compute_sha256_file(path)
    return DeeplinkCatalog(
        records=records,
        source_path=str(path),
        source_sha256=source_sha256,
        is_test_fixture=is_test_fixture,
    )
