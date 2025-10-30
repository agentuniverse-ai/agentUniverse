"""Utility helpers for reader implementations."""
from __future__ import annotations

from pathlib import Path
from typing import BinaryIO, Iterable, Sequence, Union

# Candidate encodings to try when automatic detection libraries are not available.
_FALLBACK_ENCODINGS: Sequence[str] = (
    "utf-8",
    "utf-8-sig",
    "gb18030",
    "gbk",
    "big5",
    "shift_jis",
    "latin-1",
)


def _read_sample_bytes(source: Union[str, Path, BinaryIO, bytes, bytearray],
                       sample_size: int) -> bytes:
    """Read a byte sample from the given file path or binary handle."""
    if isinstance(source, (bytes, bytearray)):
        return bytes(source[:sample_size])
    if isinstance(source, (str, Path)):
        path = Path(source)
        with path.open("rb") as handle:
            return handle.read(sample_size)

    # File-like object – preserve the original pointer
    handle = source
    current_pos = handle.tell()
    try:
        data = handle.read(sample_size)
    finally:
        handle.seek(current_pos)
    return data if data is not None else b""


def detect_file_encoding(source: Union[str, Path, BinaryIO, bytes, bytearray],
                         sample_size: int = 32 * 1024,
                         fallback_encodings: Iterable[str] = _FALLBACK_ENCODINGS) -> str:
    """Best-effort detection of the text encoding for the given file."""
    sample = _read_sample_bytes(source, sample_size)
    if not sample:
        return "utf-8"

    # First try decoding with a curated list of encodings
    for encoding in fallback_encodings:
        try:
            sample.decode(encoding)
            return encoding
        except UnicodeDecodeError:
            continue

    # If the curated list fails, fall back to charset_normalizer if available
    try:  # pragma: no cover - optional dependency
        from charset_normalizer import from_bytes
    except ImportError:  # pragma: no cover - handled above
        best_guess = None
    else:
        result = from_bytes(sample).best()
        best_guess = result.encoding if result is not None else None
        if best_guess:
            return best_guess

    return "utf-8"


__all__ = ["detect_file_encoding"]
