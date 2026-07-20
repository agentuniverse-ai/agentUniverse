"""agentUniverse Tool adapter for the financial research workspace."""
# ruff: noqa: TRY003
from __future__ import annotations

import json

from pydantic import Field, PrivateAttr

from agentuniverse.agent.action.tool.tool import Tool
from examples.sample_apps.financial_research_app.application import FinancialResearchApplication
from examples.sample_apps.financial_research_app.workspace import FinancialResearchWorkspace


class FinancialEvidenceTool(Tool):
    """Ingest local evidence or prepare a cited research package."""

    name: str = "financial_evidence_tool"
    description: str = (
        "Tenant-isolated financial evidence ingestion and cited retrieval tool."
    )
    database_path: str = "financial-research.db"
    max_citations: int = 5
    input_keys: list[str] = Field(
        default_factory=lambda: ["mode", "tenant_id"]
    )
    _workspace: FinancialResearchWorkspace | None = PrivateAttr(default=None)

    def _get_workspace(self) -> FinancialResearchWorkspace:
        if self._workspace is None:
            self._workspace = FinancialResearchWorkspace(self.database_path)
        return self._workspace

    def execute(self, mode: str, tenant_id: str, question: str = "", title: str = "",
                content: str = "", job_id: str = "") -> str:
        workspace = self._get_workspace()
        if mode == "ingest":
            source_id = workspace.ingest(tenant_id, title, content)
            return json.dumps({"source_id": source_id}, sort_keys=True)
        if mode != "research":
            raise ValueError("mode must be 'ingest' or 'research'")
        application = FinancialResearchApplication.with_native_defaults(workspace)
        report = application.research(
            tenant_id, question, job_id=job_id or None,
            top_k=self.max_citations,
        )
        return json.dumps(report, ensure_ascii=False, sort_keys=True)
