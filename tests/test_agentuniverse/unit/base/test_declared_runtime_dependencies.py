"""The runtime dependency metadata must cover what the package imports.

`agentuniverse/base/config/configer.py` imports `yaml` at module scope -- it is
the core config loader, so the very first thing `AgentUniverse().start()` does
is read YAML. PyYAML was never declared, and only arrived because unrelated
transitive dependencies (langchain-core, chromadb, kubernetes, ...) happen to
require it. Installing exactly what `pyproject.toml` declares is therefore not
enough to import the framework:

    ModuleNotFoundError: No module named 'yaml'

These tests read the declaration, and check it against what the shipped
package actually imports, so a dropped or renamed transitive dependency cannot
take the framework down silently.
"""

import ast
import sys
import tomllib
from importlib.metadata import packages_distributions, version
from pathlib import Path
from typing import Dict, Set

import pytest

REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
PYPROJECT = REPOSITORY_ROOT / "pyproject.toml"
SHIPPED_PACKAGES = ("agentuniverse", "agentuniverse_product", "agentuniverse_extension")

# Modules that need a concrete platform and are imported behind a guard.
PLATFORM_MODULES = {"pywintypes", "win32api", "win32con", "win32process"}

# Backends that are deliberately not declared: only one optional store needs
# them, and no shipped module imports them on a default path. Anything not in
# this set must be declared, so a new unguarded import fails this test.
OPTIONAL_BACKENDS = {
    "qdrant_client",   # qdrant_store / qdrant_memory_storage
}


def _normalize(name: str) -> str:
    """PEP 503 style: `ruamel.yaml`, `ruamel_yaml` and `Ruamel-Yaml` are one."""
    return name.lower().replace("_", "-").replace(".", "-")


def _declared_runtime_dependencies() -> Dict[str, str]:
    data = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    return {
        _normalize(name): spec
        for name, spec in data["tool"]["poetry"]["dependencies"].items()
    }


def _module_level_imports(package: str) -> Set[str]:
    """Top-level third-party modules imported at module scope inside `package`."""
    modules = set()
    for path in (REPOSITORY_ROOT / package).rglob("*.py"):
        # utf-8-sig: at least one shipped module starts with a BOM.
        tree = ast.parse(path.read_text(encoding="utf-8-sig"))
        for node in tree.body:  # module scope only: lazy imports are optional
            if isinstance(node, ast.Import):
                modules.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                modules.add(node.module.split(".")[0])
    return modules


def _own_or_stdlib(module: str) -> bool:
    return (
        module in sys.stdlib_module_names
        or module.startswith("agentuniverse")
        or module in SHIPPED_PACKAGES
        or module in PLATFORM_MODULES
        or module in OPTIONAL_BACKENDS
    )


@pytest.mark.parametrize(
    "module,spec,installed_name",
    [
        ("yaml", "^6.0", "PyYAML"),
        ("aiohttp", "^3.8.3", "aiohttp"),
        ("anyio", "^4.0.0", "anyio"),
        ("typing_extensions", "^4.0.0", "typing_extensions"),
        ("ruamel.yaml", ">=0.17.21", "ruamel.yaml"),
    ],
)
def test_module_scope_imports_are_declared(module, spec, installed_name):
    """A module-scope import is mandatory, so it has to be declared."""
    declared = _declared_runtime_dependencies()

    key = _normalize(installed_name)
    assert spec == declared.get(key), (
        f"{module} is imported at module scope but {installed_name} is not "
        f"declared with that spec: {declared.get(key)}"
    )
    assert version(installed_name)


@pytest.mark.parametrize("package", SHIPPED_PACKAGES)
def test_module_level_imports_are_declared(package):
    """Every third-party module imported at module scope needs a declaration."""
    declared = _declared_runtime_dependencies()
    module_to_distributions = packages_distributions()

    missing = []
    for module in sorted(_module_level_imports(package)):
        if _own_or_stdlib(module):
            continue
        distributions = module_to_distributions.get(module)
        if not distributions:
            # Not installed here, so the providing distribution is unknown.
            continue
        if not any(_normalize(d) in declared for d in distributions):
            missing.append(f"{module} (provided by {', '.join(distributions)})")

    assert missing == [], f"{package} imports undeclared modules: {missing}"


def test_configer_can_load_yaml(tmp_path):
    """The functional consequence: the core config loader reads a YAML file."""
    from agentuniverse.base.config.configer import Configer

    path = tmp_path / "config.yaml"
    path.write_text("name: demo\nnested:\n  flag: true\n", encoding="utf-8")

    assert Configer(str(path)).load().value == {"name": "demo", "nested": {"flag": True}}
