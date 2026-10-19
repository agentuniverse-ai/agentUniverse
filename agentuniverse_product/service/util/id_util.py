"""Validate product IDs before using them as configuration filenames."""

import re


_SAFE_ID = re.compile(r"[A-Za-z0-9_-]{1,64}\Z")
_WINDOWS_RESERVED_NAMES = {"CON", "PRN", "AUX", "NUL"} | {
    f"{prefix}{number}" for prefix in ("COM", "LPT") for number in range(1, 10)
}


def validate_component_id(component_id: str, kind: str) -> None:
    """Reject IDs that cannot safely form one portable filename component."""
    if not isinstance(component_id, str) or not _SAFE_ID.fullmatch(component_id):
        raise ValueError(
            f"{kind} id must contain 1-64 ASCII letters, digits, underscores or hyphens."
        )
    if component_id.upper() in _WINDOWS_RESERVED_NAMES:
        raise ValueError(f"{kind} id cannot be a reserved Windows filename.")
