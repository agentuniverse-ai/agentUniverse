"""Preflight tests use real YAML and actual configers without bootstrapping services."""

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from agentuniverse.base.config.preflight import inspect_components


def write(tmp_path, filename="component.yaml", **data):
    path = tmp_path / filename
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    return path


def codes(report):
    return {item["code"] for item in report["diagnostics"]}


def test_graph_and_actual_configer_identity(tmp_path):
    from agentuniverse.base.config.component_configer.configers.knowledge_configer import KnowledgeConfiger
    from agentuniverse.base.config.configer import Configer

    path = write(tmp_path, name="library", metadata={"type": "KNOWLEDGE"}, stores=["sqlite"], readers={"txt": "text"})
    report = inspect_components([path], external=["STORE:sqlite", "READER:text"])
    config = KnowledgeConfiger().load_by_configer(Configer(str(path)).load())
    assert report["nodes"][0]["id"] == f"{config.metadata_type}:{config.name}"
    assert {edge["target"] for edge in report["edges"]} == {"STORE:sqlite", "READER:text"}
    assert report["status"] == "checked"


def test_actual_prompt_registration(tmp_path):
    from agentuniverse.base.config.component_configer.configers.prompt_configer import PromptConfiger
    from agentuniverse.base.config.configer import Configer
    from agentuniverse.prompt.prompt import Prompt
    from agentuniverse.prompt.prompt_manager import PromptManager

    path = write(tmp_path, "prompt_version.yaml", instruction="Hello {name}")
    prompt = Prompt().initialize_by_component_configer(PromptConfiger().load_by_configer(Configer(str(path)).load()))
    manager = PromptManager()
    previous = manager._instance_obj_map.copy()
    try:
        manager.register(prompt.get_instance_code(), prompt)
        report = inspect_components([path])
        assert report["nodes"][0]["name"] == prompt.get_instance_code()
        assert manager.get_instance_obj(report["nodes"][0]["name"]) is prompt
    finally:
        manager._instance_obj_map = previous


def test_agent_paths(tmp_path):
    path = write(
        tmp_path,
        metadata={"type": "AGENT"},
        info={"name": "a"},
        profile={"llm_model": {"name": "llm"}, "prompt_version": "v"},
        plan={"planner": {"name": "p"}},
        memory={"name": "m", "conversation_memory": "c"},
        action={"tool": ["t"], "toolkit": ["tk"], "knowledge": ["k"]},
    )
    external = ["LLM:llm", "PROMPT:v", "PLANNER:p", "MEMORY:m", "MEMORY:c", "TOOL:t", "TOOLKIT:tk", "KNOWLEDGE:k"]
    report = inspect_components([path], external=external)
    assert report["status"] == "checked"
    assert {edge["target"] for edge in report["edges"]} == set(external)


def test_missing_and_wrong_type(tmp_path):
    path = write(tmp_path, name="k", metadata={"type": "KNOWLEDGE"}, stores=["absent", "text"])
    report = inspect_components([path], external=["READER:text"])
    assert codes(report) == {"missing_reference", "wrong_type"}
    assert [d["field"] for d in report["diagnostics"]] == ["stores.0", "stores.1"]


def test_duplicate_names_across_same_type_only(tmp_path):
    a = write(tmp_path, "a.yaml", name="x", metadata={"type": "KNOWLEDGE"})
    b = write(tmp_path, "b.yaml", name="x", metadata={"type": "KNOWLEDGE"})
    c = write(tmp_path, "c.yaml", name="x", metadata={"type": "STORE"})
    report = inspect_components([c, b, a])
    assert sum(d["code"] == "duplicate_name" for d in report["diagnostics"]) == 1
    assert inspect_components([a], external=["KNOWLEDGE:x"])["status"] == "error"


def test_dynamic_never_imports_or_resolves_environment(tmp_path, monkeypatch):
    monkeypatch.setenv("SECRET", "do-not-include")
    path = write(tmp_path, meta_class="explosive.Module", name="x", stores=["@FUNC(boom())"], key="${SECRET}")
    report = inspect_components([path])
    assert codes(report) == {"dynamic_type", "dynamic_value"}
    assert "do-not-include" not in json.dumps(report)
    assert report["status"] == "unresolved"
    report = inspect_components([path], class_types={"explosive.Module": "KNOWLEDGE"})
    assert len(report["nodes"]) == 1
    assert report["edges"] == []


def test_subprocess_no_component_import_or_network(tmp_path):
    module = tmp_path / "explosive.py"
    module.write_text("raise AssertionError('configured module imported')", encoding="utf-8")
    path = write(tmp_path, name="x", meta_class="explosive.Component")
    code = """
import socket, sys
socket.socket = lambda *a, **k: (_ for _ in ()).throw(AssertionError('network'))
sys.path.insert(0, sys.argv[2])
from agentuniverse.base.config.preflight import inspect_components
assert inspect_components([sys.argv[1]])['status'] == 'unresolved'
assert 'explosive' not in sys.modules
assert 'agentuniverse.base.component.component_configer_util' not in sys.modules
"""
    subprocess.run([sys.executable, "-c", code, str(path), str(tmp_path)], check=True)


@pytest.mark.parametrize(
    "text", ["", "[]", "a: 1\na: 2", "[broken", "!!python/object:os.system {}", "a: &a [*a]", "1: value"]
)
def test_invalid_yaml(tmp_path, text):
    path = tmp_path / "invalid.yaml"
    path.write_text(text, encoding="utf-8")
    assert codes(inspect_components([path])) == {"invalid_yaml"}


@pytest.mark.parametrize(
    "data,code",
    [
        ({"metadata": []}, "unknown_type"),
        ({"metadata": [1]}, "invalid_metadata"),
        ({"metadata": {"type": [1]}}, "unknown_type"),
        ({"metadata": {"type": "NOPE"}}, "unknown_type"),
        ({"metadata": {"type": "AGENT"}, "name": "not-info"}, "missing_name"),
        ({"metadata": {"type": "STORE"}, "name": 12}, "missing_name"),
        ({"metadata": {"type": "PROMPT"}}, "missing_name"),
    ],
)
def test_bad_identity(tmp_path, data, code):
    assert code in codes(inspect_components([write(tmp_path, **data)]))


@pytest.mark.parametrize("value", [None, 42, {}, [{"name": "s"}], [False], "s"])
def test_malformed_reference_collections(tmp_path, value):
    path = write(tmp_path, name="k", metadata={"type": "KNOWLEDGE"}, stores=value)
    report = inspect_components([path])
    if value == {} or value is None:
        assert report["edges"] == []
    else:
        assert "invalid_reference" in codes(report) or "missing_reference" in codes(report)


def test_cycles_and_declared_capabilities(tmp_path):
    paths = [
        write(tmp_path, f"{name}.yaml", name=name, metadata={"type": "TOOL"}, delegate=other)
        for name, other in [("a", "b"), ("b", "c"), ("c", "a")]
    ]
    report = inspect_components(
        paths,
        reference_fields={"TOOL": {"delegate": "TOOL"}},
        capabilities={"TOOL:a": ["paged"]},
        requirements={"TOOL:a": ["paged"], "TOOL:b": ["paged"]},
    )
    assert sum(d["code"] == "cycle" for d in report["diagnostics"]) == 3
    assert sum(d["code"] == "capability_unresolved" for d in report["diagnostics"]) == 1


def test_deterministic_and_non_mutating(tmp_path):
    paths = [write(tmp_path, f"{name}.yaml", name=name, metadata={"type": "KNOWLEDGE"}) for name in ["a", "b"]]
    before = [p.read_bytes() for p in paths]
    assert inspect_components(paths) == inspect_components(reversed(paths))
    assert before == [p.read_bytes() for p in paths]


def test_limits_and_missing_file(tmp_path):
    path = write(tmp_path, name="x")
    assert "invalid_yaml" in codes(inspect_components([path], max_file_bytes=1))
    assert "invalid_yaml" in codes(inspect_components([tmp_path / "absent"]))
    with pytest.raises(ValueError):
        inspect_components([path, path], max_files=1)
    with pytest.raises(ValueError):
        inspect_components([], max_files=True)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"class_types": {"X": "BAD"}},
        {"external": ["wrong"]},
        {"reference_fields": {"BAD": {"x": "TOOL"}}},
        {"reference_fields": {"TOOL": {"x": "BAD"}}},
        {"capabilities": {"TOOL:x": "streaming"}},
    ],
)
def test_invalid_declarations(kwargs):
    with pytest.raises(ValueError):
        inspect_components([], **kwargs)


def test_real_example_reports_runtime_shape_mismatch():
    root = Path(__file__).resolve().parents[5]
    path = root / "examples/context_engineering/multi_tier_agent.yaml"
    report = inspect_components([path])
    # This shipped example has top-level name, whereas Agent reads info.name.
    assert "missing_name" in codes(report)


def test_cli_json_and_exit(tmp_path):
    path = write(tmp_path, metadata={"type": "KNOWLEDGE"}, name="k", stores=["missing"])
    result = subprocess.run(
        [sys.executable, "-m", "agentuniverse.base.config.preflight", str(path)], capture_output=True, text=True
    )
    assert result.returncode == 1
    assert json.loads(result.stdout)["status"] == "error"


def test_standard_app_literal_references():
    root = Path(__file__).resolve().parents[5]
    path = root / "examples/sample_standard_app/intelligence/agentic/agent/agent_instance/demo_agent.yaml"
    report = inspect_components(
        [path],
        class_types={"sample_standard_app.intelligence.agentic.agent.agent_instance.demo_agent.DemoAgent": "AGENT"},
        external=[
            "PROMPT:demo_agent.cn_v2",
            "LLM:qwen3-32b",
            "TOOL:mock_search_tool",
            "TOOLKIT:search_toolkit",
            "MEMORY:demo_memory",
        ],
    )
    assert report["status"] == "checked"
    assert len(report["edges"]) == 5


def test_expanded_alias_budget(tmp_path):
    path = tmp_path / "aliases.yaml"
    text = "a: &a [x,x,x,x,x,x,x,x,x,x]\n"
    for level, previous in [("b", "a"), ("c", "b"), ("d", "c"), ("e", "d"), ("f", "e")]:
        text += f"{level}: &{level} [" + ",".join([f"*{previous}"] * 10) + "]\n"
    path.write_text(text, encoding="utf-8")
    assert codes(inspect_components([path])) == {"invalid_yaml"}
