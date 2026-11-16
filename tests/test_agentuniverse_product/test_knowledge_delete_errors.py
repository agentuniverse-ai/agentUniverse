"""Knowledge deletion must not report success when a config cannot be removed."""

import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from agentuniverse_product.base.util import yaml_util


ROOT = Path(__file__).resolve().parents[2]


def test_yaml_delete_propagates_io_failures(tmp_path, monkeypatch):
    config = tmp_path / "knowledge.yaml"
    config.write_text("name: example\n", encoding="utf-8")

    def deny(_path):
        raise PermissionError("file is locked")

    monkeypatch.setattr(yaml_util.os, "remove", deny)
    with pytest.raises(PermissionError, match="locked"):
        yaml_util.delete_yaml_file(str(config))
    assert config.exists()


def test_yaml_delete_allows_already_missing_file(tmp_path):
    yaml_util.delete_yaml_file(str(tmp_path / "missing.yaml"))


def test_knowledge_service_does_not_claim_success_after_delete_failure(tmp_path, monkeypatch):
    knowledge_path = tmp_path / "knowledge.yaml"
    product_path = tmp_path / "product.yaml"
    knowledge_path.write_text("name: example\n", encoding="utf-8")
    product_path.write_text("id: example\n", encoding="utf-8")
    knowledge = SimpleNamespace(component_config_path=str(knowledge_path))
    product = SimpleNamespace(component_config_path=str(product_path))
    source = ROOT / "agentuniverse_product/service/knowledge_service/knowledge_service.py"
    tree = ast.parse(source.read_text(encoding="utf-8"))
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef))
    method = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == "delete_knowledge")
    namespace = {"Knowledge": object, "Product": object,
                 "KnowledgeManager": lambda: SimpleNamespace(get_instance_obj=lambda **_kw: knowledge),
                 "ProductManager": lambda: SimpleNamespace(get_instance_obj=lambda **_kw: product),
                 "unregister_knowledge": Mock(), "unregister_product": Mock(),
                 "delete_yaml_file": yaml_util.delete_yaml_file}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[])), str(source), "exec"), namespace)

    def deny(_path):
        raise PermissionError("file is locked")

    monkeypatch.setattr(yaml_util.os, "remove", deny)
    with pytest.raises(PermissionError, match="locked"):
        namespace["delete_knowledge"]("example")
    assert knowledge_path.exists() and product_path.exists()
