"""Catalog-only lexical table selection with bounded foreign-key context."""

import asyncio
import hashlib
import json
import re
from collections import deque
from typing import List, Tuple

from pydantic import Field

from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.store import Store


def _tokens(value):
    return set(re.findall(r"[^\W_]+", value.casefold()))


class RelationalSchemaStore(Store):
    """Read-only schema context for NL2SQL, never database row contents.

    The caller supplies an initialized SQLAlchemy Engine as ``client``. Each
    query reflects only explicitly allowed (schema, table) pairs. Foreign keys
    may connect two lexical seeds through otherwise unmatched bridge tables.
    No model or generated SQL is run, and the Engine remains caller-owned.
    """

    tables: List[Tuple[str, str]] = Field(min_length=1, max_length=100)
    seed_limit: int = Field(default=3, strict=True, ge=1, le=10)
    max_context_tables: int = Field(default=12, strict=True, ge=1, le=100)
    max_hops: int = Field(default=3, strict=True, ge=0, le=6)
    max_columns: int = Field(default=2000, strict=True, ge=1)
    max_foreign_keys: int = Field(default=2000, strict=True, ge=1)
    max_context_chars: int = Field(default=50000, strict=True, ge=1)

    def query(self, query, **kwargs):
        """Return one self-contained context Document or no lexical match."""
        return self.query_with_report(query)[0]

    async def async_query(self, query, **kwargs):
        return await asyncio.to_thread(self.query, query, **kwargs)

    def query_with_report(self, query):
        """Select seeds and shortest FK bridges, reporting all budget omissions."""
        from sqlalchemy import inspect, text

        if self.client is None:
            raise ValueError("Supply a caller-owned SQLAlchemy Engine as client")
        allowed = sorted(set(self.tables))
        if len(allowed) != len(self.tables) or any(not s or not t for s, t in allowed):
            raise ValueError("tables must contain unique explicit schema/table pairs")
        if self.max_context_tables < self.seed_limit:
            raise ValueError("max_context_tables must be at least seed_limit")
        if query.similarity_top_k is not None and query.similarity_top_k != 1:
            raise ValueError("Schema context is one document; similarity_top_k must be 1")
        terms = _tokens(query.query_str or "")
        report = {"seeds": [], "paths": [], "omitted_paths": [], "external_foreign_keys": []}
        if not terms:
            return [], report
        catalog = {}
        edges = []
        total_columns = 0
        with self.client.connect() as connection:
            inspector = inspect(connection)
            if connection.dialect.name not in ("sqlite", "postgresql"):
                raise ValueError("Only SQLite and PostgreSQL reflection are supported")
            for schema, table in allowed:
                columns = inspector.get_columns(table, schema=schema)
                total_columns += len(columns)
                if total_columns > self.max_columns:
                    raise ValueError("Catalog exceeds max_columns")
                pk = inspector.get_pk_constraint(table, schema=schema)
                unique = inspector.get_unique_constraints(table, schema=schema)
                foreign_keys = inspector.get_foreign_keys(table, schema=schema)
                # PostgreSQL may omit a referenced schema visible on search_path.
                # Resolve the actual target namespace from catalog object IDs,
                # including references to the default schema from another schema.
                target_schemas = {}
                if connection.dialect.name == "postgresql":
                    rows = connection.execute(
                        text("""
                        SELECT c.conname, target_ns.nspname
                        FROM pg_catalog.pg_constraint c
                        JOIN pg_catalog.pg_class source ON source.oid = c.conrelid
                        JOIN pg_catalog.pg_namespace source_ns ON source_ns.oid = source.relnamespace
                        JOIN pg_catalog.pg_class target ON target.oid = c.confrelid
                        JOIN pg_catalog.pg_namespace target_ns ON target_ns.oid = target.relnamespace
                        WHERE c.contype = 'f' AND source_ns.nspname = :schema
                        AND source.relname = :table
                    """),
                        {"schema": schema, "table": table},
                    )
                    target_schemas = dict(rows.tuples().all())
                if len(edges) + len(report["external_foreign_keys"]) + len(foreign_keys) > self.max_foreign_keys:
                    raise ValueError("Catalog exceeds max_foreign_keys")
                catalog[(schema, table)] = {
                    "schema": schema,
                    "table": table,
                    "columns": [
                        {"name": col["name"], "type": str(col["type"]), "nullable": col["nullable"]} for col in columns
                    ],
                    "primary_key": pk.get("constrained_columns", []),
                    "unique_constraints": [item["column_names"] for item in unique],
                }
                for fk in foreign_keys:
                    target_schema = fk.get("referred_schema") or schema
                    if connection.dialect.name == "postgresql":
                        if fk.get("name") not in target_schemas:
                            raise ValueError("Foreign key catalog changed during reflection")
                        target_schema = target_schemas[fk["name"]]
                    target = (target_schema, fk["referred_table"])
                    edge = {
                        "from": [schema, table],
                        "to": list(target),
                        "columns": fk["constrained_columns"],
                        "referred_columns": fk["referred_columns"],
                        "name": fk.get("name"),
                    }
                    if target in allowed:
                        edges.append(edge)
                    else:
                        report["external_foreign_keys"].append(edge)
        ranked = []
        for key, table in catalog.items():
            table_matches = sorted(terms & _tokens(table["table"]))
            column_matches = {
                c["name"]: sorted(terms & _tokens(c["name"])) for c in table["columns"] if terms & _tokens(c["name"])
            }
            score = 3 * len(table_matches) + sum(map(len, column_matches.values()))
            if score:
                ranked.append((-score, key, table_matches, column_matches))
        ranked.sort()
        selected = set()
        for negative, key, table_matches, column_matches in ranked[: self.seed_limit]:
            selected.add(key)
            report["seeds"].append(
                {"table": list(key), "score": -negative, "table_terms": table_matches, "column_terms": column_matches}
            )
        if not selected:
            return [], report
        adjacency = {key: set() for key in allowed}
        for edge in edges:
            a, b = tuple(edge["from"]), tuple(edge["to"])
            adjacency[a].add(b)
            adjacency[b].add(a)
        seeds = sorted(selected)
        for i, start in enumerate(seeds):
            for end in seeds[i + 1 :]:
                path = self._shortest_path(adjacency, start, end)
                if path is None:
                    report["omitted_paths"].append(
                        {"from": list(start), "to": list(end), "reason": "no_path_within_hops"}
                    )
                elif len(selected | set(path)) > self.max_context_tables:
                    report["omitted_paths"].append({"from": list(start), "to": list(end), "reason": "table_budget"})
                else:
                    selected.update(path)
                    report["paths"].append([list(key) for key in path])
        relations = [edge for edge in edges if tuple(edge["from"]) in selected and tuple(edge["to"]) in selected]
        relations.sort(key=lambda edge: json.dumps(edge, sort_keys=True))
        context = {"tables": [catalog[key] for key in sorted(selected)], "foreign_keys": relations, "selection": report}
        text = json.dumps(context, ensure_ascii=False, sort_keys=True)
        if len(text) > self.max_context_chars:
            raise ValueError("Schema context exceeds max_context_chars; narrow the allowlist")
        digest = hashlib.sha256(text.encode()).hexdigest()
        return [
            Document(
                id=f"schema:{digest}", text=text, metadata={"relational_schema": context, "content_sha256": digest}
            )
        ], report

    def _shortest_path(self, adjacency, start, end):
        queue = deque([[start]])
        seen = {start}
        while queue:
            path = queue.popleft()
            if path[-1] == end:
                return path
            if len(path) - 1 >= self.max_hops:
                continue
            for neighbor in sorted(adjacency[path[-1]]):
                if neighbor not in seen:
                    seen.add(neighbor)
                    queue.append(path + [neighbor])
        return None
