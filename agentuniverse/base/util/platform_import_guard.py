# !/usr/bin/env python3
# -*- coding:utf-8 -*-

import importlib
import os
import sys
from types import ModuleType
from typing import Optional


def ensure_stdlib_platform(module_name: str, module_file: str) -> Optional[ModuleType]:
    """Resolve accidental top-level imports of example ``platform`` packages.

    Some example applications have a package named ``platform`` for product UI
    metadata. When users run Python from an example app root, ``import platform``
    may resolve that local package instead of Python's stdlib module. This guard
    only acts in that accidental top-level import case; qualified imports such as
    ``react_agent_app.platform`` keep their normal behavior.
    """
    if module_name != "platform":
        return None

    module_dir = os.path.dirname(os.path.abspath(module_file))
    shadowing_path = os.path.dirname(module_dir)
    original_path = list(sys.path)
    cwd = os.path.abspath(os.getcwd())

    def normalize_path(path: str) -> str:
        return os.path.abspath(path or cwd)

    try:
        sys.modules.pop("platform", None)
        sys.path = [
            path for path in sys.path
            if normalize_path(path) not in {module_dir, shadowing_path}
        ]
        stdlib_platform = importlib.import_module("platform")
        sys.modules["platform"] = stdlib_platform
        return stdlib_platform
    finally:
        sys.path = original_path
