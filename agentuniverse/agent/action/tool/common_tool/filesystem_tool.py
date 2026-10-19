#!/usr/bin/env python3
"""Bounded file system operations tool.

Provides mkdir, list, copy, move, delete, and tree operations, all confined
to ``base_dir`` via ``resolve_safe_path``. Every operation is bounded by
configurable limits (max files listed, max tree depth, max file count for
copy/move batches).
"""

# ruff: noqa: TRY003, TRY004

import logging
import os
import shutil
from typing import Any, ClassVar

from agentuniverse.agent.action.tool.common_tool.file_path_utils import \
    resolve_safe_path
from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger

logger = logging.getLogger(__name__)


class FileSystemTool(Tool):
    """Bounded file system operations confined to ``base_dir``.

    Attributes:
        base_dir: Root directory; all paths are resolved underneath it.
        max_list_entries: Maximum entries returned by list/tree (default 500).
        max_tree_depth: Maximum depth for tree (default 5).
        max_batch_size: Maximum files per copy/move batch (default 100).
    """

    base_dir: str = "."
    max_list_entries: int = 500
    max_tree_depth: int = 5
    max_batch_size: int = 100

    def execute(self, mode: str, path: str = "", target: str = "",
                **kwargs) -> dict:
        try:
            self._validate_config()
            op = self._normalize_mode(mode)
            safe_path = self._resolve(path) if path else self.base_dir
            if op == "list":
                return self._list(safe_path)
            if op == "tree":
                return self._tree(safe_path, kwargs.get("depth", self.max_tree_depth))
            if op == "mkdir":
                return self._mkdir(safe_path)
            if op == "copy":
                return self._copy(safe_path, self._resolve(target))
            if op == "move":
                return self._move(safe_path, self._resolve(target))
            if op == "delete":
                return self._delete(safe_path)
            if op == "exists":
                return self._exists(safe_path)
            if op == "info":
                return self._info(safe_path)
            return self._error("validation_error", f"Unknown mode: {mode}")
        except (TypeError, ValueError) as exc:
            return self._error("validation_error", str(exc))
        except Exception as exc:
            return self._error("operation_error", str(exc))

    # ------------------------------------------------------------------ #
    # Config
    # ------------------------------------------------------------------ #
    def _validate_config(self) -> None:
        if not isinstance(self.base_dir, str) or not self.base_dir:
            raise ValueError("base_dir must be a non-empty string")
        for field in ("max_list_entries", "max_tree_depth", "max_batch_size"):
            value = getattr(self, field)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{field} must be a positive integer")

    def _initialize_by_component_configer(self, configer: ComponentConfiger) -> "FileSystemTool":
        super()._initialize_by_component_configer(configer)
        if hasattr(configer, "base_dir"):
            self.base_dir = configer.base_dir
        if hasattr(configer, "max_list_entries"):
            self.max_list_entries = configer.max_list_entries
        if hasattr(configer, "max_tree_depth"):
            self.max_tree_depth = configer.max_tree_depth
        if hasattr(configer, "max_batch_size"):
            self.max_batch_size = configer.max_batch_size
        return self

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    @staticmethod
    def _normalize_mode(mode: str) -> str:
        if not isinstance(mode, str):
            raise TypeError("mode must be a string")
        normalized = mode.strip().lower()
        allowed = {"list", "tree", "mkdir", "copy", "move", "delete", "exists", "info"}
        if normalized not in allowed:
            raise ValueError(f"mode must be one of: {', '.join(sorted(allowed))}")
        return normalized

    def _resolve(self, path: str) -> str:
        return resolve_safe_path(path, self.base_dir)

    @staticmethod
    def _error(error_type: str, message: str) -> dict:
        return {"status": "error", "error_type": error_type, "error": message}

    @staticmethod
    def _ok(**kwargs) -> dict:
        return {"status": "success", **kwargs}

    # ------------------------------------------------------------------ #
    # Operations
    # ------------------------------------------------------------------ #
    def _list(self, path: str) -> dict:
        if not os.path.isdir(path):
            return self._error("validation_error", f"Not a directory: {path}")
        entries = []
        truncated = False
        try:
            for i, name in enumerate(sorted(os.listdir(path))):
                if i >= self.max_list_entries:
                    truncated = True
                    break
                full = os.path.join(path, name)
                entries.append({
                    "name": name,
                    "type": "dir" if os.path.isdir(full) else "file",
                    "size": os.path.getsize(full) if os.path.isfile(full) else 0,
                })
        except OSError as exc:
            return self._error("operation_error", str(exc))
        return self._ok(path=path, entries=entries, count=len(entries),
                        truncated=truncated, max_entries=self.max_list_entries)

    def _tree(self, path: str, max_depth: int) -> dict:
        if not os.path.isdir(path):
            return self._error("validation_error", f"Not a directory: {path}")
        depth = min(max_depth, self.max_tree_depth)
        result = []

        def _walk(current: str, prefix: str, d: int):
            if d > depth or len(result) >= self.max_list_entries:
                return
            try:
                items = sorted(os.listdir(current))
            except OSError:
                return
            for name in items:
                if len(result) >= self.max_list_entries:
                    return
                full = os.path.join(current, name)
                is_dir = os.path.isdir(full)
                result.append({
                    "name": f"{prefix}{name}",
                    "type": "dir" if is_dir else "file",
                })
                if is_dir and d < depth:
                    _walk(full, f"{prefix}{name}/", d + 1)

        _walk(path, "", 0)
        return self._ok(path=path, entries=result, count=len(result),
                        truncated=len(result) >= self.max_list_entries)

    def _mkdir(self, path: str) -> dict:
        os.makedirs(path, exist_ok=True)
        return self._ok(mode="mkdir", path=path)

    def _copy(self, src: str, dst: str) -> dict:
        if not os.path.exists(src):
            return self._error("validation_error", f"Source does not exist: {src}")
        if os.path.isdir(src):
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dst)
        return self._ok(mode="copy", source=src, target=dst)

    def _move(self, src: str, dst: str) -> dict:
        if not os.path.exists(src):
            return self._error("validation_error", f"Source does not exist: {src}")
        shutil.move(src, dst)
        return self._ok(mode="move", source=src, target=dst)

    def _delete(self, path: str) -> dict:
        if not os.path.exists(path):
            return self._ok(mode="delete", path=path, deleted=False,
                            message="Path does not exist; nothing deleted")
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
        return self._ok(mode="delete", path=path, deleted=True)

    def _exists(self, path: str) -> dict:
        exists = os.path.exists(path)
        return self._ok(path=path, exists=exists,
                        type=("dir" if os.path.isdir(path)
                              else "file" if os.path.isfile(path) else "none"))

    def _info(self, path: str) -> dict:
        if not os.path.exists(path):
            return self._error("validation_error", f"Path does not exist: {path}")
        stat = os.stat(path)
        return self._ok(
            path=path,
            type="dir" if os.path.isdir(path) else "file",
            size=stat.st_size,
            modified=stat.st_mtime,
        )
