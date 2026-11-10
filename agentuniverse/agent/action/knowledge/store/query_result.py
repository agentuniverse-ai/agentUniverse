"""Structured result models for observable knowledge queries."""

from pydantic import BaseModel, Field

from agentuniverse.agent.action.knowledge.store.document import Document


class StoreQueryDiagnostic(BaseModel):
    """Outcome and timing for one routed store query."""

    store_code: str
    succeeded: bool
    duration_ms: float = Field(ge=0)
    document_count: int = Field(default=0, ge=0)
    error: str | None = None


class KnowledgeQueryResult(BaseModel):
    """Post-processed documents and their per-store diagnostics."""

    documents: list[Document] = Field(default_factory=list)
    diagnostics: list[StoreQueryDiagnostic] = Field(default_factory=list)
