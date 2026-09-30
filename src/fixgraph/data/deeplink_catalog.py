"""Immutable Deeplink Catalog abstraction for verified screen resolution."""

from dataclasses import dataclass
from typing import Dict, Iterator, List, Optional

from fixgraph.data.fingerprints import compute_sha256_json


@dataclass(frozen=True)
class DeeplinkRecord:
    record_id: str
    uri: str
    name: str
    description: str
    message: str = ""
    qna_description: str = ""
    classes: str = ""
    control_type: str = ""
    original_type: str = ""
    category: str = "auto"  # "auto", "critical", "manual"
    validation: Optional[Dict[str, str]] = None

    def get_searchable_text(self) -> str:
        """Build descriptive metadata document for retrieval.

        CRITICAL REQUIREMENT (P0-08): Explicitly excludes masked bixby URI string
        from semantic index search text to prevent artificial URI string token matching.
        """
        parts = [
            self.name,
            self.description,
            self.message,
            self.qna_description,
            self.classes,
            self.control_type,
            self.original_type,
        ]
        return " ".join([p for p in parts if p]).strip()


class DeeplinkCatalog:
    def __init__(
        self,
        records: List[DeeplinkRecord],
        source_path: str = "",
        source_sha256: str = "",
        is_test_fixture: bool = False,
    ):
        self._records_by_id: Dict[str, DeeplinkRecord] = {r.record_id: r for r in records}
        self._records_list: List[DeeplinkRecord] = list(records)
        self._fingerprint = compute_sha256_json(
            [{"id": r.record_id, "uri": r.uri, "name": r.name} for r in self._records_list]
        )
        self._source_path = source_path
        self._source_sha256 = source_sha256
        self._is_test_fixture = is_test_fixture

    @property
    def fingerprint(self) -> str:
        return self._fingerprint

    @property
    def source_path(self) -> str:
        return self._source_path

    @property
    def source_sha256(self) -> str:
        return self._source_sha256

    @property
    def is_test_fixture(self) -> bool:
        return self._is_test_fixture

    @property
    def record_count(self) -> int:
        return len(self._records_list)

    def __len__(self) -> int:
        return len(self._records_list)

    def get_by_id(self, record_id: str) -> Optional[DeeplinkRecord]:
        return self._records_by_id.get(record_id)

    def iter_records(self) -> Iterator[DeeplinkRecord]:
        return iter(self._records_list)

    def resolve_exact_uri(self, record_id: str) -> Optional[str]:
        """Return the exact, unmodified catalog URI for a record ID."""
        record = self.get_by_id(record_id)
        if record:
            return record.uri
        return None

    def exists_uri(self, uri: str) -> bool:
        """Check if exact URI exists in catalog."""
        return any(r.uri == uri for r in self._records_list)
