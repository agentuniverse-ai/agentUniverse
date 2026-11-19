"""Resumable, tenant-isolated storage for the financial research sample."""
# ruff: noqa: TRY003
from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import uuid
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class Citation:
    citation_id: str
    source_id: str
    title: str
    excerpt: str
    score: float
    ordinal: int
    content_hash: str
    metadata: dict

    def to_dict(self) -> dict:
        return asdict(self)


class FinancialResearchWorkspace:
    """Small operational store around agentUniverse research components."""

    def __init__(self, database: str | Path = ":memory:") -> None:
        self.connection = sqlite3.connect(str(database))
        self.connection.row_factory = sqlite3.Row
        self.connection.executescript("""
        CREATE TABLE IF NOT EXISTS research_job (
          tenant_id TEXT NOT NULL, job_id TEXT NOT NULL, question TEXT NOT NULL,
          state TEXT NOT NULL, checkpoint TEXT NOT NULL, evidence TEXT, report TEXT,
          created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
          PRIMARY KEY (tenant_id, job_id));
        CREATE TABLE IF NOT EXISTS research_source (
          tenant_id TEXT NOT NULL, source_id TEXT NOT NULL, title TEXT NOT NULL,
          content TEXT NOT NULL, content_hash TEXT NOT NULL, metadata TEXT NOT NULL,
          PRIMARY KEY (tenant_id, source_id));
        CREATE TABLE IF NOT EXISTS research_chunk (
          tenant_id TEXT NOT NULL, source_id TEXT NOT NULL, chunk_id TEXT NOT NULL,
          ordinal INTEGER NOT NULL, content TEXT NOT NULL,
          PRIMARY KEY (tenant_id, chunk_id));
        CREATE INDEX IF NOT EXISTS ix_research_chunk_tenant_source
          ON research_chunk (tenant_id, source_id);
        """)
        self._upgrade_job_schema()

    def _upgrade_job_schema(self) -> None:
        columns = {
            row["name"] for row in self.connection.execute(
                "PRAGMA table_info(research_job)"
            ).fetchall()
        }
        if "evidence" not in columns:
            with self.connection:
                self.connection.execute(
                    "ALTER TABLE research_job ADD COLUMN evidence TEXT"
                )

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def ingest(self, tenant_id: str, title: str, content: str, *,
               metadata: dict | None = None, chunk_chars: int = 800) -> str:
        if not tenant_id or not title or not content.strip():
            raise ValueError("tenant_id, title and non-empty content are required")
        if not 100 <= chunk_chars <= 10_000:
            raise ValueError("chunk_chars must be between 100 and 10000")
        digest = hashlib.sha256(content.encode()).hexdigest()
        source_id = digest[:24]
        with self.connection:
            self.connection.execute(
                "INSERT OR IGNORE INTO research_source "
                "(tenant_id,source_id,title,content,content_hash,metadata) "
                "VALUES (?,?,?,?,?,?)",
                (tenant_id, source_id, title, content, digest,
                 json.dumps(metadata or {}, sort_keys=True)),
            )
            for ordinal, start in enumerate(range(0, len(content), chunk_chars)):
                chunk = content[start:start + chunk_chars]
                chunk_id = hashlib.sha256(
                    f"{source_id}:{ordinal}:{chunk}".encode()
                ).hexdigest()[:24]
                self.connection.execute(
                    "INSERT OR IGNORE INTO research_chunk "
                    "(tenant_id,source_id,chunk_id,ordinal,content) "
                    "VALUES (?,?,?,?,?)",
                    (tenant_id, source_id, chunk_id, ordinal, chunk),
                )
        return source_id

    def create_job(self, tenant_id: str, question: str, *,
                   job_id: str | None = None) -> str:
        if not tenant_id or not question.strip():
            raise ValueError("tenant_id and a non-empty question are required")
        job_id = job_id or uuid.uuid4().hex
        now = self._now()
        with self.connection:
            self.connection.execute(
                "INSERT INTO research_job "
                "(tenant_id,job_id,question,state,checkpoint,evidence,report,"
                "created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?)",
                (tenant_id, job_id, question, "pending", "created", None,
                 None, now, now),
            )
        return job_id

    @staticmethod
    def _tokens(text: str) -> set[str]:
        return set(re.findall(r"[a-z0-9_]+", text.lower()))

    def retrieve(self, tenant_id: str, query: str, *,
                 top_k: int = 5) -> list[Citation]:
        if top_k < 1 or top_k > 20:
            raise ValueError("top_k must be between 1 and 20")
        query_tokens = self._tokens(query)
        rows = self.connection.execute("""
          SELECT c.source_id,c.chunk_id,c.ordinal,c.content,
                 s.title,s.content_hash,s.metadata
          FROM research_chunk c
          JOIN research_source s
            ON s.tenant_id=c.tenant_id AND s.source_id=c.source_id
          WHERE c.tenant_id=?""", (tenant_id,)).fetchall()
        scored = []
        for row in rows:
            tokens = self._tokens(row["content"])
            score = len(query_tokens & tokens) / max(len(query_tokens), 1)
            if score:
                scored.append(Citation(
                    citation_id=row["chunk_id"], source_id=row["source_id"],
                    title=row["title"], excerpt=row["content"][:500],
                    score=score, ordinal=row["ordinal"],
                    content_hash=row["content_hash"],
                    metadata=json.loads(row["metadata"]),
                ))
        return sorted(
            scored, key=lambda item: (-item.score, item.citation_id)
        )[:top_k]

    def run(self, tenant_id: str, job_id: str, *, top_k: int = 5) -> dict:
        """Prepare an evidence package, resuming after the retrieval checkpoint."""
        row = self.connection.execute(
            "SELECT * FROM research_job WHERE tenant_id=? AND job_id=?",
            (tenant_id, job_id),
        ).fetchone()
        if row is None:
            raise KeyError(job_id)
        if row["state"] == "completed":
            return json.loads(row["report"])

        if row["checkpoint"] == "retrieved" and row["evidence"]:
            citations = json.loads(row["evidence"])
        else:
            citations = [
                item.to_dict()
                for item in self.retrieve(tenant_id, row["question"], top_k=top_k)
            ]
            with self.connection:
                self.connection.execute(
                    "UPDATE research_job SET state='running',checkpoint='retrieved',"
                    "evidence=?,updated_at=? WHERE tenant_id=? AND job_id=?",
                    (json.dumps(citations, sort_keys=True), self._now(),
                     tenant_id, job_id),
                )

        report = {
            "job_id": job_id,
            "tenant_id": tenant_id,
            "question": row["question"],
            "summary": "Evidence package ready for agentUniverse analysis.",
            "citations": citations,
            "provenance": {
                "retriever": "deterministic_token_overlap",
                "citation_count": len(citations),
                "source_hashes": sorted({
                    item["content_hash"] for item in citations
                }),
            },
        }
        with self.connection:
            self.connection.execute(
                "UPDATE research_job SET state='completed',checkpoint='reported',"
                "report=?,updated_at=? WHERE tenant_id=? AND job_id=?",
                (json.dumps(report, sort_keys=True), self._now(),
                 tenant_id, job_id),
            )
        return report

    @staticmethod
    def evaluate(report: dict, expected_source_ids: Iterable[str]) -> dict:
        """Calculate deterministic citation precision/recall for demo datasets."""
        expected = set(expected_source_ids)
        cited = {item["source_id"] for item in report.get("citations", [])}
        matched = cited & expected
        return {
            "citation_precision": len(matched) / len(cited) if cited else 0.0,
            "citation_recall": len(matched) / len(expected) if expected else 1.0,
            "matched_sources": sorted(matched),
        }

    def job(self, tenant_id: str, job_id: str) -> dict:
        row = self.connection.execute(
            "SELECT * FROM research_job WHERE tenant_id=? AND job_id=?",
            (tenant_id, job_id),
        ).fetchone()
        if row is None:
            raise KeyError(job_id)
        return dict(row)

    def close(self) -> None:
        self.connection.close()

    def __enter__(self) -> FinancialResearchWorkspace:
        return self

    def __exit__(self, *_args) -> None:
        self.close()
