"""Regressions for user-provided IDs used in product YAML paths."""

import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from agentuniverse_product.service.util.common_util import validate_component_id


ROOT = Path(__file__).resolve().parents[2]


def load_function(relative_path, name, namespace):
    source = ROOT / relative_path
    tree = ast.parse(source.read_text(encoding="utf-8"))
    functions = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == name]
    function = functions[0]
    module = ast.Module(body=[function], type_ignores=[])
    scope = dict(namespace)
    exec(compile(ast.fix_missing_locations(module), str(source), "exec"), scope)
    return scope[name]


@pytest.mark.parametrize("identifier", [None, "", ".", "..", "../outside", r"..\outside", "/tmp/outside", r"C:\outside", "a:b", "a\x00b"])
def test_component_id_rejects_unsafe_path_names(identifier):
    with pytest.raises(ValueError):
        validate_component_id(identifier)


@pytest.mark.parametrize("identifier", ["plain", "with-dashes_123", "a.b", "知识库"])
def test_component_id_preserves_safe_existing_names(identifier):
    assert validate_component_id(identifier) is None


@pytest.mark.parametrize("service,util,validator,dto_attrs", [
    ("agent_service", "agent_util", "validate_create_agent_parameters", {"planner": None}),
    ("tool_service", "tool_util", "validate_create_api_tool_parameters", {"openapi_schema": None}),
    ("plugin_service", "plugin_util", "validate_create_plugin_parameters", {"openapi_desc": None}),
])
def test_creators_reject_traversal_before_writes(service, util, validator, dto_attrs, tmp_path):
    util_namespace = {
        "AgentDTO": object, "ToolDTO": object, "PluginDTO": object,
        "validate_component_id": validate_component_id,
        "AgentManager": Mock(), "ToolManager": Mock(), "ProductManager": Mock(),
    }
    validate = load_function(
        Path("agentuniverse_product/service/util") / f"{util}.py", validator, util_namespace
    )
    write = Mock()
    service_namespace = {
        "AgentDTO": object, "ToolDTO": object, "PluginDTO": object,
        "validate_create_agent_parameters": validate,
        "validate_create_api_tool_parameters": validate,
        "validate_create_plugin_parameters": validate,
        "write_yaml_file": write,
        "get_core_path": lambda: tmp_path,
        "assemble_product_config_data": Mock(),
        "assemble_tool_product_config_data": Mock(),
        "parse_openapi_yaml_to_tool_bundle": Mock(),
        "os": __import__("os"),
    }
    source = ROOT / "agentuniverse_product" / "service" / service / f"{service}.py"
    tree = ast.parse(source.read_text(encoding="utf-8"))
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef))
    create = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name.startswith("create_"))
    scope = dict(service_namespace)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[create], type_ignores=[])), str(source), "exec"), scope)

    with pytest.raises(ValueError):
        scope[create.name](SimpleNamespace(id="../outside", **dto_attrs))
    write.assert_not_called()


def test_knowledge_creator_rejects_traversal_before_writes(tmp_path):
    write = Mock()
    create = load_function(
        Path("agentuniverse_product/service/knowledge_service/knowledge_service.py"),
        "create_knowledge",
        {"KnowledgeDTO": object, "validate_component_id": validate_component_id,
         "write_yaml_file": write, "get_core_path": lambda: tmp_path,
         "os": __import__("os")},
    )
    with pytest.raises(ValueError):
        create(SimpleNamespace(id="../outside"))
    write.assert_not_called()
