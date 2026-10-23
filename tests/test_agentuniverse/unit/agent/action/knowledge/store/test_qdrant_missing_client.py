"""A missing qdrant client must say how to install it.

Every other optional store backend in this repository guards its import and
re-raises with an actionable message -- see `milvus_store.py` and
`neo4j_store.py`, and `aws_bedrock_llm` for the same shape:

    try:
        from pymilvus import connections, Collection, ...
    except ImportError as e:
        raise ImportError(
            "pymilvus is not installed. Please install it with 'pip install pymilvus'"
        ) from e

`qdrant_store` and `qdrant_memory_storage` did not, so configuring a Qdrant
backend surfaced a bare `ModuleNotFoundError: No module named 'qdrant_client'`
with no hint about the package name or the install command.
"""

import importlib
import sys

import pytest

QDRANT_MODULES = [
    "qdrant_client",
    "qdrant_client.models",
    "agentuniverse.agent.action.knowledge.store.qdrant_store",
    "agentuniverse.agent.memory.memory_storage.qdrant_memory_storage",
]


@pytest.fixture()
def qdrant_unavailable(monkeypatch):
    """Make `import qdrant_client` fail, as it does on a default install."""
    for name in list(sys.modules):
        if name.startswith("qdrant_client") or name.split(".")[-1].startswith("qdrant"):
            monkeypatch.delitem(sys.modules, name, raising=False)

    real_import = __builtins__["__import__"] if isinstance(__builtins__, dict) else __builtins__.__import__

    def guarded_import(name, *args, **kwargs):
        if name == "qdrant_client" or name.startswith("qdrant_client."):
            raise ModuleNotFoundError("No module named 'qdrant_client'")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", guarded_import)
    yield
    for name in QDRANT_MODULES:
        sys.modules.pop(name, None)


@pytest.mark.parametrize(
    "module,owner",
    [
        ("agentuniverse.agent.action.knowledge.store.qdrant_store", "QdrantStore"),
        (
            "agentuniverse.agent.memory.memory_storage.qdrant_memory_storage",
            "QdrantMemoryStorage",
        ),
    ],
)
def test_missing_qdrant_client_names_the_package(module, owner, qdrant_unavailable):
    with pytest.raises(ImportError) as excinfo:
        importlib.import_module(module)

    message = str(excinfo.value)
    assert "qdrant-client is required" in message
    assert owner in message
    assert "pip install qdrant-client" in message
    # The original error must stay attached, so the traceback still points at
    # the missing module rather than only at this re-raise.
    assert isinstance(excinfo.value.__cause__, ImportError)


def test_the_message_is_not_the_bare_module_name(qdrant_unavailable):
    """The old behaviour was a bare ModuleNotFoundError naming the import."""
    with pytest.raises(ImportError) as excinfo:
        importlib.import_module("agentuniverse.agent.action.knowledge.store.qdrant_store")

    assert type(excinfo.value) is ImportError
    assert "pip install" in str(excinfo.value)


def test_qdrant_store_imports_when_the_client_is_installed():
    """The guard must not swallow a working installation."""
    pytest.importorskip("qdrant_client")

    module = importlib.import_module(
        "agentuniverse.agent.action.knowledge.store.qdrant_store"
    )

    assert hasattr(module, "QdrantStore")


def test_every_imported_qdrant_symbol_still_exists():
    """The guard must only fire for a *missing package*, not a missing symbol.

    `qdrant_memory_storage` imported `NamedVector`, which qdrant-client dropped
    in 1.20 while qdrant_store did not need it. With a current client installed
    the module therefore raised "qdrant-client is required ... install it" even
    though the package was present, and `QdrantMemoryStorage` was unusable. Every
    name the two modules import must exist in the installed client.
    """
    qdrant = pytest.importorskip("qdrant_client")
    pytest.importorskip("qdrant_client.models")

    import ast
    import pathlib

    for module_path in (
        "agentuniverse/agent/action/knowledge/store/qdrant_store.py",
        "agentuniverse/agent/memory/memory_storage/qdrant_memory_storage.py",
    ):
        source = pathlib.Path(module_path).read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom):
                continue
            if not (node.module or "").startswith("qdrant_client"):
                continue
            target = importlib.import_module(node.module)
            for alias in node.names:
                assert hasattr(target, alias.name), (
                    f"{module_path} imports {alias.name} from {node.module}, "
                    f"which qdrant-client {getattr(qdrant, '__version__', '?')} does not provide"
                )
