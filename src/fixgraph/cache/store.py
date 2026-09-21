"""SQLite-backed persistent semantic CaseCache store (M5-02)."""

import json
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from fixgraph.contracts.internal import CacheEntry


class CaseCacheStore:
    def __init__(self, db_path: str = "data/cache.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS case_cache (
                    signature_hash TEXT PRIMARY KEY,
                    canonical_query TEXT NOT NULL,
                    query_embedding TEXT NOT NULL,
                    validated_plan_json TEXT NOT NULL,
                    catalog_fingerprint TEXT NOT NULL,
                    schema_version TEXT NOT NULL,
                    validator_version TEXT NOT NULL,
                    created_at_ts REAL NOT NULL,
                    hit_count INTEGER DEFAULT 0
                )
                """
            )
            conn.commit()

    def get_by_signature(self, signature_hash: str) -> Optional[CacheEntry]:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM case_cache WHERE signature_hash = ?", (signature_hash,)
            )
            row = cursor.fetchone()
            if row:
                # Update hit count
                conn.execute(
                    "UPDATE case_cache SET hit_count = hit_count + 1 WHERE signature_hash = ?",
                    (signature_hash,),
                )
                conn.commit()
                return CacheEntry(
                    signature_hash=row["signature_hash"],
                    canonical_query=row["canonical_query"],
                    query_embedding=json.loads(row["query_embedding"]),
                    validated_plan_json=row["validated_plan_json"],
                    catalog_fingerprint=row["catalog_fingerprint"],
                    schema_version=row["schema_version"],
                    validator_version=row["validator_version"],
                    created_at_ts=row["created_at_ts"],
                    hit_count=row["hit_count"] + 1,
                )
        return None

    def get_all_entries(self) -> List[CacheEntry]:
        entries: List[CacheEntry] = []
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM case_cache")
            for row in cursor.fetchall():
                entries.append(
                    CacheEntry(
                        signature_hash=row["signature_hash"],
                        canonical_query=row["canonical_query"],
                        query_embedding=json.loads(row["query_embedding"]),
                        validated_plan_json=row["validated_plan_json"],
                        catalog_fingerprint=row["catalog_fingerprint"],
                        schema_version=row["schema_version"],
                        validator_version=row["validator_version"],
                        created_at_ts=row["created_at_ts"],
                        hit_count=row["hit_count"],
                    )
                )
        return entries

    def put_validated_plan(
        self,
        signature_hash: str,
        canonical_query: str,
        query_embedding: List[float],
        validated_plan_json: str,
        catalog_fingerprint: str,
        schema_version: str = "v1",
        validator_version: str = "v1",
    ) -> None:
        """Store ONLY 100% fully validated response JSON (P0-17)."""
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO case_cache (
                    signature_hash, canonical_query, query_embedding,
                    validated_plan_json, catalog_fingerprint,
                    schema_version, validator_version, created_at_ts, hit_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
                """,
                (
                    signature_hash,
                    canonical_query,
                    json.dumps(query_embedding),
                    validated_plan_json,
                    catalog_fingerprint,
                    schema_version,
                    validator_version,
                    time.time(),
                ),
            )
            conn.commit()

    def clear(self) -> None:
        with self._get_connection() as conn:
            conn.execute("DELETE FROM case_cache")
            conn.commit()

    def close(self) -> None:
        pass
