# !/usr/bin/env python3
# -*- coding:utf-8 -*-


def parse_strict_bool(value, field_name: str, default: bool = False) -> bool:
    """Parse a boolean-like tool input value without unsafe truthy fallback."""
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes", "y", "on"}:
            return True
        if normalized in {"false", "0", "no", "n", "off"}:
            return False
        raise ValueError(
            f"{field_name} must be a boolean value: true/false, 1/0, yes/no, or on/off"
        )
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if value == 1:
            return True
        if value == 0:
            return False
        raise ValueError(f"{field_name} numeric value must be 0 or 1")
    raise ValueError(
        f"{field_name} must be a boolean value: true/false, 1/0, yes/no, or on/off"
    )
