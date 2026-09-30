"""SQLite-backed persistent semantic CaseCache store (M5-02)."""

import json
import sqlite3
import time
from pathlib import Path
from typing import List, Optional

from fixgraph.contracts.internal import CacheEntry, PipelineFingerprint


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
            # We migrate to v2 by simply recreating. In production, use migrations.
            conn.execute("DROP TABLE IF EXISTS case_cache")
            conn.execute(
                """
                CREATE TABLE case_cache (
                    cache_id TEXT PRIMARY KEY,
                    signature_hash TEXT NOT NULL,
                    canonical_signature_json TEXT NOT NULL,
                    canonical_query TEXT NOT NULL,
                    original_query_hash TEXT NOT NULL,
                    validated_plan_json TEXT NOT NULL,
                    query_embedding TEXT NOT NULL,
                    embedding_model_id TEXT NOT NULL,
                    embedding_model_revision TEXT,
                    embedding_dimension INTEGER NOT NULL,
                    pipeline_fingerprint TEXT NOT NULL,
                    catalog_fingerprint TEXT NOT NULL,
                    reference_fingerprint TEXT,
                    schema_fingerprint TEXT,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    hit_count INTEGER DEFAULT 0,
                    validation_hash TEXT NOT NULL,
                    plan_hash TEXT NOT NULL,
                    cache_entry_version TEXT NOT NULL,
                    quality_score REAL,
                    source_case_id TEXT
                )
                """
            )
            # Index for fast exact signature lookups
            conn.execute("CREATE INDEX IF NOT EXISTS idx_signature_hash ON case_cache (signature_hash)")
            conn.commit()

    def _row_to_entry(self, row: sqlite3.Row) -> CacheEntry:
        return CacheEntry(
            cache_id=row["cache_id"],
            signature_hash=row["signature_hash"],
            canonical_signature_json=row["canonical_signature_json"],
            canonical_query=row["canonical_query"],
            original_query_hash=row["original_query_hash"],
            validated_plan_json=row["validated_plan_json"],
            query_embedding=json.loads(row["query_embedding"]),
            embedding_model_id=row["embedding_model_id"],
            embedding_model_revision=row["embedding_model_revision"],
            embedding_dimension=row["embedding_dimension"],
            pipeline_fingerprint=PipelineFingerprint.model_validate_json(row["pipeline_fingerprint"]),
            catalog_fingerprint=row["catalog_fingerprint"],
            reference_fingerprint=row["reference_fingerprint"],
            schema_fingerprint=row["schema_fingerprint"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            hit_count=row["hit_count"],
            validation_hash=row["validation_hash"],
            plan_hash=row["plan_hash"],
            cache_entry_version=row["cache_entry_version"],
            quality_score=row["quality_score"],
            source_case_id=row["source_case_id"]
        )

    def get_by_signature(self, signature_hash: str) -> Optional[CacheEntry]:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM case_cache WHERE signature_hash = ? ORDER BY created_at DESC LIMIT 1",
                (signature_hash,)
            )
            row = cursor.fetchone()
            if row:
                conn.execute(
                    "UPDATE case_cache SET hit_count = hit_count + 1, updated_at = ? WHERE cache_id = ?",
                    (time.time(), row["cache_id"]),
                )
                conn.commit()
                # Return the updated object
                entry = self._row_to_entry(row)
                entry.hit_count += 1
                return entry
        return None

    def get_all_entries(self) -> List[CacheEntry]:
        entries: List[CacheEntry] = []
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM case_cache")
            for row in cursor.fetchall():
                entries.append(self._row_to_entry(row))
        return entries

    def put_validated_plan(self, entry: CacheEntry) -> None:
        """Store ONLY 100% fully validated response JSON (P0-17)."""
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO case_cache (
                    cache_id, signature_hash, canonical_signature_json, canonical_query,
                    original_query_hash, validated_plan_json, query_embedding,
                    embedding_model_id, embedding_model_revision, embedding_dimension,
                    pipeline_fingerprint, catalog_fingerprint, reference_fingerprint, schema_fingerprint,
                    created_at, updated_at, hit_count, validation_hash, plan_hash,
                    cache_entry_version, quality_score, source_case_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    entry.cache_id,
                    entry.signature_hash,
                    entry.canonical_signature_json,
                    entry.canonical_query,
                    entry.original_query_hash,
                    entry.validated_plan_json,
                    json.dumps(entry.query_embedding),
                    entry.embedding_model_id,
                    entry.embedding_model_revision,
                    entry.embedding_dimension,
                    entry.pipeline_fingerprint.model_dump_json(),
                    entry.catalog_fingerprint,
                    entry.reference_fingerprint,
                    entry.schema_fingerprint,
                    entry.created_at,
                    entry.updated_at,
                    entry.hit_count,
                    entry.validation_hash,
                    entry.plan_hash,
                    entry.cache_entry_version,
                    entry.quality_score,
                    entry.source_case_id,
                ),
            )
            conn.commit()

    def clear(self) -> None:
        with self._get_connection() as conn:
            conn.execute("DELETE FROM case_cache")
            conn.commit()

    def close(self) -> None:
        pass

