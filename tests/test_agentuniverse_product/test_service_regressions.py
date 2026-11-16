"""Dependency-light regression tests for product service methods."""

import ast
import io
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest


ROOT = Path(__file__).resolve().parents[2]


def load_method(service, method, namespace):
    """Load one method without importing optional application integrations."""
    source = ROOT / "agentuniverse_product" / "service" / service / f"{service}.py"
    tree = ast.parse(source.read_text(encoding="utf-8"))
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef))
    function = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == method)
    module = ast.Module(body=[ast.ClassDef(name="Service", bases=[], keywords=[], body=[function], decorator_list=[])], type_ignores=[])
    scope = dict(namespace)
    exec(compile(ast.fix_missing_locations(module), str(source), "exec"), scope)
    return getattr(scope["Service"], method)


@pytest.mark.parametrize("knowledge_id,filename", [
    ("missing", "document.txt"),
    ("safe", "../escape.txt"),
    ("safe", r"..\escape.txt"),
    ("../escape", "document.txt"),
])
def test_upload_rejects_invalid_input_before_writing(tmp_path, knowledge_id, filename):
    resources = tmp_path / "resources"
    manager = Mock()
    manager.get_instance_obj.return_value = None if knowledge_id == "missing" else SimpleNamespace(
        component_config_path=str(tmp_path / "knowledge.yaml"), stores=[], insert_knowledge=Mock()
    )
    upload = load_method("knowledge_service", "upload_knowledge_file", {
        "os": __import__("os"), "shutil": __import__("shutil"),
        "get_core_path": lambda: tmp_path,
        "get_resources_path": lambda: resources,
        "KnowledgeManager": lambda: manager,
    })

    with pytest.raises(ValueError):
        upload(knowledge_id, SimpleNamespace(filename=filename, file=io.BytesIO(b"secret")))

    assert not resources.exists()
    assert not (tmp_path / "escape.txt").exists()


def test_upload_valid_file_reaches_existing_store(tmp_path):
    resources = tmp_path / "resources"
    store = tmp_path / "store" / "safe_store.yaml"
    store.parent.mkdir()
    store.write_text("name: existing", encoding="utf-8")
    knowledge = SimpleNamespace(stores=[], insert_knowledge=Mock())
    manager = Mock()
    manager.get_instance_obj.return_value = knowledge
    upload = load_method("knowledge_service", "upload_knowledge_file", {
        "os": __import__("os"), "shutil": __import__("shutil"),
        "get_core_path": lambda: tmp_path,
        "get_resources_path": lambda: resources,
        "KnowledgeManager": lambda: manager,
    })

    assert upload("safe", SimpleNamespace(filename="document.txt", file=io.BytesIO(b"data")))
    assert (resources / "document.txt").read_bytes() == b"data"
    knowledge.insert_knowledge.assert_called_once_with(
        source_path=str(resources / "document.txt"), stores=["safe_chroma_store"]
    )
