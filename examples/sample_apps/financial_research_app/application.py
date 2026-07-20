"""Framework-native research pipeline built from agentUniverse components."""
from __future__ import annotations

import hashlib
import re
from collections.abc import Iterable

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.doc_processor.doc_processor_manager import DocProcessorManager
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.work_pattern.work_pattern import WorkPattern
from agentuniverse.agent.work_pattern.work_pattern_manager import WorkPatternManager
from examples.sample_apps.financial_research_app.workspace import FinancialResearchWorkspace


def _embedding(text: str, dimensions: int = 64) -> list[float]:
    """Create a deterministic offline vector used only by the sample's MMR."""
    vector = [0.0] * dimensions
    for token in re.findall(r"[a-z0-9_]+", text.lower()):
        digest = hashlib.sha256(token.encode()).digest()
        index = int.from_bytes(digest[:2], "big") % dimensions
        vector[index] += -1.0 if digest[2] & 1 else 1.0
    return vector


class FinancialResearchApplication:
    """Compose workspace evidence, native doc processors, and a work pattern."""

    def __init__(self, workspace: FinancialResearchWorkspace, *,
                 processors: Iterable[DocProcessor] | None = None,
                 work_pattern: WorkPattern | None = None) -> None:
        self.workspace = workspace
        self.processors = list(processors or [])
        self.work_pattern = work_pattern

    @classmethod
    def with_native_defaults(cls, workspace: FinancialResearchWorkspace, *,
                             work_pattern: WorkPattern | None = None):
        """Build an offline pipeline from built-in agentUniverse processors."""
        from agentuniverse.agent.action.knowledge.doc_processor.financial_indicator_extractor import (
            FinancialIndicatorExtractor,
        )
        from agentuniverse.agent.action.knowledge.doc_processor.mmr_processor import MMRProcessor

        return cls(
            workspace,
            processors=[
                FinancialIndicatorExtractor(use_llm=False),
                MMRProcessor(lambda_coef=0.7, top_n=5),
            ],
            work_pattern=work_pattern,
        )

    @classmethod
    def from_registry(cls, workspace: FinancialResearchWorkspace, *,
                      processor_names: Iterable[str] = (
                          "financial_indicator_extractor", "mmr_processor",
                      ), work_pattern_name: str | None = None):
        """Resolve components registered by ``AgentUniverse.start``."""
        processors = [
            DocProcessorManager().get_instance_obj(name, strict=True)
            for name in processor_names
        ]
        work_pattern = None
        if work_pattern_name:
            work_pattern = WorkPatternManager().get_instance_obj(
                work_pattern_name, strict=True
            )
        return cls(workspace, processors=processors, work_pattern=work_pattern)

    def ingest(self, tenant_id: str, title: str, content: str, *,
               metadata: dict | None = None) -> str:
        return self.workspace.ingest(
            tenant_id, title, content, metadata=metadata
        )

    def research(self, tenant_id: str, question: str, *,
                 job_id: str | None = None, top_k: int = 5,
                 retry_count: int = 1, eval_threshold: float = 0.8) -> dict:
        job_id = job_id or self.workspace.create_job(tenant_id, question)
        report = self.workspace.run(tenant_id, job_id, top_k=top_k)
        documents = [
            Document(
                id=item["citation_id"], text=item["excerpt"],
                metadata={**item, "citation_id": item["citation_id"]},
                embedding=_embedding(item["excerpt"]),
            )
            for item in report["citations"]
        ]
        query = Query(query_str=question, embeddings=[_embedding(question)])
        for processor in self.processors:
            documents = processor.process_docs(documents, query)

        report["agentuniverse"] = {
            "doc_processors": [
                processor.name or processor.__class__.__name__
                for processor in self.processors
            ],
            "analysis_documents": [
                {"id": document.id, "text": document.text,
                 "metadata": document.metadata or {}}
                for document in documents
            ],
        }
        if self.work_pattern is not None:
            pattern_input = {
                "input": question,
                "retry_count": retry_count,
                "jump_step": "planning",
                "eval_threshold": eval_threshold,
            }
            input_object = InputObject({
                "input": question,
                "question": question,
                "tenant_id": tenant_id,
                "job_id": job_id,
                "evidence": report["agentuniverse"]["analysis_documents"],
                "citations": report["citations"],
            })
            report["agentuniverse"]["work_pattern"] = (
                self.work_pattern.name or self.work_pattern.__class__.__name__
            )
            report["agentuniverse"]["work_pattern_result"] = (
                self.work_pattern.invoke(input_object, pattern_input)
            )
        return report
