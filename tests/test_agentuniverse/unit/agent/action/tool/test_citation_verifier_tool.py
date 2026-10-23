"""Literal quotation provenance, not semantic/factual evaluation."""
import asyncio
import hashlib
import json
from pathlib import Path

import pytest

from agentuniverse.agent.action.tool.common_tool.citation_verifier_tool import CitationVerifierTool


def citation(**updates):
    return {"source_id": "s", "start": 0, "end": 5, "quote": "alpha", **updates}


def test_valid_hash_and_no_source_text_echo():
    source = "alpha SECRET remainder"
    sha = hashlib.sha256(source.encode()).hexdigest()
    result = CitationVerifierTool().execute({"s": source}, [citation(source_sha256=sha.upper())])
    assert result["all_verified"]
    assert "SECRET" not in json.dumps(result)
    assert "alpha" not in json.dumps(result)


@pytest.mark.parametrize("updates,status", [
    ({"source_id": "missing"}, "source_missing"), ({"start": -1}, "span_out_of_bounds"),
    ({"end": 100}, "span_out_of_bounds"), ({"end": 0}, "span_out_of_bounds"),
    ({"quote": "ALPHA"}, "quote_mismatch"), ({"source_sha256": "0" * 64}, "source_changed"),
    ({"start": True}, "invalid_citation"), ({"quote": ""}, "invalid_citation"),
    ({"start": "0"}, "invalid_citation"), ({"source_sha256": None}, "invalid_citation"),
    ({"source_sha256": "bad"}, "invalid_citation"), ({"extra": 1}, "invalid_citation"),
])
def test_diagnostic_codes(updates, status):
    result = CitationVerifierTool().execute({"s": "alpha"}, [citation(**updates)])
    assert result["results"][0]["status"] == status
    assert not result["all_verified"]


def test_unicode_offsets_repeated_quotes_and_crlf_are_exact():
    text = "😀甲\r\nalpha alpha"
    source = {"s": text}
    first = text.index("alpha")
    result = CitationVerifierTool().execute(source, [citation(start=first, end=first + 5),
        citation(start=first + 6, end=first + 11)])
    assert result["verified_count"] == 2
    assert source["s"] == text
    assert not CitationVerifierTool().execute(source, [citation(start=first + 1, end=first + 6)])["all_verified"]


def test_empty_is_not_success_and_malformed_rows_retained():
    tool = CitationVerifierTool()
    assert not tool.execute({}, [])["all_verified"]
    result = tool.execute({"s": "alpha"}, [citation(), None, {}])
    assert result["citation_count"] == 3
    assert result["verified_count"] == 1


@pytest.mark.parametrize("options", [{"max_sources": 1}, {"max_source_chars": 1}, {"max_citations": 1}])
def test_bounds(options):
    with pytest.raises(ValueError):
        CitationVerifierTool(**options).execute({"s": "alpha", "t": "beta"}, [citation(), citation()])


def test_real_tool_manager_yaml_sync_async_and_langchain():
    from agentuniverse.agent.action.tool.tool_manager import ToolManager
    from agentuniverse.base.config.application_configer.app_configer import AppConfiger
    from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
    from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
    from agentuniverse.base.config.configer import Configer
    apps = ApplicationConfigManager()
    manager = ToolManager()
    previous_pool = dict(manager._instance_obj_map)
    try:
        previous_app = apps.app_configer
    except ValueError:
        previous_app = None
    try:
        settings = Configer()
        settings.value = {"BASE_INFO": {"appname": "citation-contract"}}
        app = AppConfiger().load_by_configer(settings)
        root = Path(__file__).resolve().parents[6]
        path = root / "agentuniverse/agent/action/tool/common_tool/citation_verifier_tool.yaml"
        config = ToolConfiger().load_by_configer(Configer(str(path)).load())
        app.tool_configer_map = {config.name: config}
        apps.app_configer = app
        tool = manager.get_instance_obj(config.name)
        assert isinstance(tool, CitationVerifierTool)
        assert tool.args_model_schema["required"] == ["sources", "citations"]
        data = {"sources": {"s": "alpha"}, "citations": [citation()]}
        assert tool.run(**data)["all_verified"]
        assert asyncio.run(tool.async_run(**data))["all_verified"]
        assert tool.langchain_run(json.dumps(data))["all_verified"]
    finally:
        manager._instance_obj_map.clear()
        manager._instance_obj_map.update(previous_pool)
        apps.app_configer = previous_app


@pytest.mark.parametrize("limit", [0, True, "10"])
def test_real_initialization_rejects_invalid_limits_before_mutating_tool(limit):
    import yaml
    from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
    from agentuniverse.base.config.configer import Configer

    root = Path(__file__).resolve().parents[6]
    path = root / "agentuniverse/agent/action/tool/common_tool/citation_verifier_tool.yaml"
    configer = Configer()
    configer.value = yaml.safe_load(path.read_text(encoding="utf-8"))
    configer.value["max_sources"] = limit
    config = ToolConfiger().load_by_configer(configer)
    tool = CitationVerifierTool(name="original", max_sources=7)
    with pytest.raises(ValueError):
        tool.initialize_by_component_configer(config)
    assert tool.name == "original" and tool.max_sources == 7
