import json
import sqlite3
from pathlib import Path

# ruff: noqa: S101
import pytest

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.work_pattern.work_pattern import WorkPattern
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer
from examples.sample_apps.financial_research_app.application import FinancialResearchApplication
from examples.sample_apps.financial_research_app.components import FinancialEvidenceTool
from examples.sample_apps.financial_research_app.workspace import FinancialResearchWorkspace


def test_offline_ingest_retrieve_report_and_resume(tmp_path):
    workspace = FinancialResearchWorkspace(tmp_path / "research.db")
    first = workspace.ingest("tenant-a", "report", "Revenue grew 20 percent. Margin reached 15 percent.")
    assert workspace.ingest("tenant-a", "report", "Revenue grew 20 percent. Margin reached 15 percent.") == first
    job = workspace.create_job("tenant-a", "revenue margin")
    report = workspace.run("tenant-a", job)
    assert report["citations"] and report["citations"][0]["title"] == "report"
    assert workspace.run("tenant-a", job) == report
    assert workspace.job("tenant-a", job)["checkpoint"] == "reported"


def test_tenant_isolation(tmp_path):
    workspace = FinancialResearchWorkspace(tmp_path / "research.db")
    workspace.ingest("a", "private-a", "revenue secret alpha")
    workspace.ingest("b", "private-b", "revenue public beta")
    assert [item.title for item in workspace.retrieve("a", "revenue")] == ["private-a"]
    assert [item.title for item in workspace.retrieve("b", "revenue")] == ["private-b"]


def test_bounds_and_cross_tenant_job_access(tmp_path):
    workspace = FinancialResearchWorkspace(tmp_path / "research.db")
    job = workspace.create_job("a", "q")
    with pytest.raises(KeyError):
        workspace.run("b", job)
    with pytest.raises(ValueError, match="between 1 and 20"):
        workspace.retrieve("a", "q", top_k=100)
    with pytest.raises(ValueError, match="chunk_chars"):
        workspace.ingest("a", "bad", "content", chunk_chars=5)


def test_retrieval_checkpoint_resume_and_evaluation(tmp_path):
    workspace = FinancialResearchWorkspace(tmp_path / "research.db")
    source = workspace.ingest("tenant", "annual", "Revenue reached 120 million in FY2025.")
    job = workspace.create_job("tenant", "FY2025 revenue")
    citation = workspace.retrieve("tenant", "FY2025 revenue")[0].to_dict()
    with workspace.connection:
        workspace.connection.execute(
            "UPDATE research_job SET state='running',checkpoint='retrieved',evidence=? "
            "WHERE tenant_id=? AND job_id=?",
            (json.dumps([citation]), "tenant", job),
        )
    report = workspace.run("tenant", job)
    assert report["citations"] == [citation]
    assert workspace.evaluate(report, [source]) == {
        "citation_precision": 1.0,
        "citation_recall": 1.0,
        "matched_sources": [source],
    }


def test_existing_pre_checkpoint_database_is_upgraded(tmp_path):
    database = tmp_path / "legacy.db"
    connection = sqlite3.connect(database)
    connection.execute("""
        CREATE TABLE research_job (
          tenant_id TEXT NOT NULL, job_id TEXT NOT NULL, question TEXT NOT NULL,
          state TEXT NOT NULL, checkpoint TEXT NOT NULL, report TEXT,
          created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
          PRIMARY KEY (tenant_id, job_id))
    """)
    connection.close()
    workspace = FinancialResearchWorkspace(database)
    job = workspace.create_job("tenant", "question")
    stored = workspace.job("tenant", job)
    assert stored["evidence"] is None
    assert stored["report"] is None


class RecordingWorkPattern(WorkPattern):
    name: str = "recording_pattern"

    def invoke(self, input_object: InputObject, work_pattern_input: dict, **kwargs) -> dict:
        return {
            "question": input_object.get_data("question"),
            "citation_count": len(input_object.get_data("citations")),
            "retry_count": work_pattern_input["retry_count"],
        }

    async def async_invoke(self, input_object: InputObject,
                           work_pattern_input: dict, **kwargs) -> dict:
        return self.invoke(input_object, work_pattern_input, **kwargs)


def test_native_processors_and_work_pattern_receive_cited_evidence(tmp_path):
    workspace = FinancialResearchWorkspace(tmp_path / "research.db")
    app = FinancialResearchApplication.with_native_defaults(
        workspace, work_pattern=RecordingWorkPattern(),
    )
    app.ingest("tenant", "annual report", "FY2025 revenue reached 120 million and margin was 18 percent.")
    report = app.research("tenant", "FY2025 revenue margin", retry_count=2)
    pipeline = report["agentuniverse"]
    assert pipeline["doc_processors"] == [
        "FinancialIndicatorExtractor", "MMRProcessor",
    ]
    assert pipeline["analysis_documents"][0]["metadata"]["financial_metrics"]
    assert pipeline["work_pattern_result"] == {
        "question": "FY2025 revenue margin", "citation_count": 1, "retry_count": 2,
    }


def test_tool_adapter_and_yaml_component_configuration(tmp_path):
    tool = FinancialEvidenceTool(database_path=str(tmp_path / "tool.db"))
    ingested = json.loads(tool.execute(
        "ingest", "tenant", title="report",
        content="Revenue reached 50 million in FY2025.",
    ))
    assert ingested["source_id"]
    report = json.loads(tool.execute(
        "research", "tenant", question="FY2025 revenue",
    ))
    assert report["citations"][0]["source_id"] == ingested["source_id"]

    # Locate the checked-out sample without depending on pytest's working directory.
    path = Path(__file__).parents[1] / "agentic/tool/financial_evidence_tool.yaml"
    configer = ToolConfiger().load_by_configer(Configer(path=str(path)).load())
    configured = FinancialEvidenceTool().initialize_by_component_configer(configer)
    assert configured.name == "financial_evidence_tool"
    assert configured.max_citations == 5

    app_root = Path(__file__).parents[2]
    app_config = Configer(path=str(app_root / "config/config.toml")).load().value
    log_path = app_root / "config" / app_config["SUB_CONFIG_PATH"]["log_config_path"]
    assert log_path.resolve().is_file()
