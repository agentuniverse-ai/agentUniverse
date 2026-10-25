"""Helpers for running the CSV tool tests with minimal optional dependencies.

The CSV tool itself only needs the standard library, pydantic, and PyYAML.
The registration tests import the tool manager, which in turn imports optional
model-provider integrations. A minimal test environment may not have those
packages installed, so install inert placeholders only when they are missing;
real installations are left untouched.
"""

import importlib.abc
import importlib.machinery
import importlib.util
import sys
import types

_OPTIONAL_PACKAGES = ("langchain", "langchain_", "openai", "anthropic")


class _StubModule(types.ModuleType):
    """Provide attribute placeholders for an absent optional package."""

    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(name)
        value = type(name, (), {})
        setattr(self, name, value)
        return value


class _StubFinder(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    """Load placeholders for optional packages that are not installed."""

    def find_spec(self, fullname, path=None, target=None):
        if fullname in {"langchain", "openai", "anthropic"} or fullname.startswith(_OPTIONAL_PACKAGES):
            return importlib.machinery.ModuleSpec(fullname, self, is_package=True)
        return None

    def create_module(self, spec):
        module = _StubModule(spec.name)
        module.__path__ = []
        return module

    def exec_module(self, module):
        return None


def install_optional_dependency_stubs() -> None:
    """Make optional integrations importable when the environment lacks them.

    Present packages keep winning because the finder is appended to
    ``sys.meta_path``; it only answers imports the normal finders cannot
    resolve. This lets the focused CSV suite run on a machine that has only
    the test dependencies, without changing behavior in a full install.
    """
    if all(importlib.util.find_spec(name) is not None for name in ("langchain", "openai", "anthropic")):
        return
    if not any(isinstance(finder, _StubFinder) for finder in sys.meta_path):
        sys.meta_path.append(_StubFinder())
