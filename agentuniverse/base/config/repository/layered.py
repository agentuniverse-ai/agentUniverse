"""Deterministic defaults -> YAML -> database -> runtime configuration precedence."""
from __future__ import annotations

import copy


def deep_merge(base: dict, overlay: dict) -> dict:
    result = copy.deepcopy(base)
    for key, value in overlay.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


class LayeredConfigResolver:
    def resolve(self, *, defaults=None, yaml=None, database=None, runtime=None) -> dict:
        result = {}
        for layer in (defaults or {}, yaml or {}, database or {}, runtime or {}):
            result = deep_merge(result, layer)
        return result
