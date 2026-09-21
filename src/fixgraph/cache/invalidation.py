"""Cache invalidation and compatibility checking module (M5-05)."""

from fixgraph.contracts.internal import CacheEntry


class CacheInvalidator:
    def __init__(self, current_catalog_fingerprint: str, schema_version: str = "v1"):
        self.current_catalog_fingerprint = current_catalog_fingerprint
        self.schema_version = schema_version

    def is_compatible(self, entry: CacheEntry) -> bool:
        if entry.catalog_fingerprint != self.current_catalog_fingerprint:
            return False
        if entry.schema_version != self.schema_version:
            return False
        return True
