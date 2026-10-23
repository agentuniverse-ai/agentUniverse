"""A missing tree-sitter must name itself, not raise UnboundLocalError.

`CodeAstProcessor._process_with_tree_sitter()` looks the language up through a
nested `_ensure_language()`. The old version bound `module_name` *inside* the
`try` and used it in the `except ImportError` handler:

    try:
        from tree_sitter import Language
        from importlib import import_module
        module_name = f'tree_sitter_{language}'
        lang_module = import_module(module_name)
        self._languages[language] = Language(lang_module.language())
    except ImportError:
        raise ImportError(f"Could not import {module_name}. ...")

`tree-sitter` is not a declared dependency, so the failing import is usually the
first line, before `module_name` is bound. The handler then raised

    UnboundLocalError: cannot access local variable 'module_name' where it is
    not associated

which hid both the real cause and the install hint.
"""

import sys
import types

import pytest

from agentuniverse.agent.action.knowledge.doc_processor.code_ast_processor import (
    CodeAstProcessor,
)
from agentuniverse.agent.action.knowledge.store.document import Document


def _processor():
    """A processor with a parser, bypassing the configer it normally needs."""
    instance = CodeAstProcessor()
    instance._parser = types.SimpleNamespace(language=None, parse=lambda *_a, **_k: None)
    return instance


@pytest.fixture()
def tree_sitter_missing(monkeypatch):
    """Make `import tree_sitter` fail, as it does on a default install."""
    for name in list(sys.modules):
        if name == "tree_sitter" or name.startswith("tree_sitter"):
            monkeypatch.delitem(sys.modules, name, raising=False)

    real_import = __builtins__["__import__"] if isinstance(__builtins__, dict) else __builtins__.__import__

    def guarded_import(name, *args, **kwargs):
        if name == "tree_sitter" or name.startswith("tree_sitter."):
            raise ModuleNotFoundError("No module named 'tree_sitter'")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", guarded_import)


@pytest.mark.parametrize("language", ["python", "javascript", "unknown"])
def test_missing_tree_sitter_names_the_package(language, tree_sitter_missing):
    processor = _processor()

    with pytest.raises(ImportError) as excinfo:
        processor.process_docs(
            [Document(text="x = 1", metadata={"language": language})]
        )

    message = str(excinfo.value)
    assert "tree-sitter is required" in message
    assert "pip install tree-sitter" in message
    # The original failure must stay attached for the traceback.
    assert isinstance(excinfo.value.__cause__, ImportError)


def test_missing_tree_sitter_does_not_raise_unbound_local(tree_sitter_missing):
    """The regression: the old code raised UnboundLocalError here."""
    processor = _processor()

    try:
        processor.process_docs([Document(text="x = 1", metadata={"language": "python"})])
    except ImportError:
        return
    except UnboundLocalError:
        pytest.fail("UnboundLocalError: the message handler lost its variable")
    pytest.fail("expected an ImportError naming tree-sitter")


def test_missing_language_package_names_that_package(monkeypatch):
    """With tree-sitter present, the missing parser package is named instead."""
    fake_tree_sitter = types.ModuleType("tree_sitter")
    fake_tree_sitter.Language = lambda *_a, **_k: object()
    monkeypatch.setitem(sys.modules, "tree_sitter", fake_tree_sitter)
    monkeypatch.delitem(sys.modules, "tree_sitter_cobol", raising=False)

    processor = _processor()

    with pytest.raises(ImportError) as excinfo:
        processor.process_docs([Document(text="x", metadata={"language": "cobol"})])

    message = str(excinfo.value)
    assert "tree_sitter_cobol" in message
    assert "pip install tree_sitter_cobol" in message


def test_a_cached_language_is_reused_without_re_importing(monkeypatch):
    """The fast path must still work, and must not touch the imports."""
    processor = _processor()
    processor._languages["python"] = "cached-language"

    calls = []

    def guarded_import(name, *args, **kwargs):
        calls.append(name)
        raise ModuleNotFoundError(f"should not import {name}")

    monkeypatch.setattr("builtins.__import__", guarded_import)

    # Reaches `self._parser.language = ...` without importing anything.
    try:
        processor.process_docs([Document(text="x = 1", metadata={"language": "python"})])
    except Exception:
        pass

    assert not [c for c in calls if c.startswith("tree_sitter")]
