"""Utility helpers for reader implementations."""
from __future__ import annotations

import codecs
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
    """Best-effort detection, completing a character at the sample boundary.

    Up to three lookahead bytes complete a split character in the curated
    encodings. Invalid or incomplete characters at the real EOF still fail
    strict decoding. File-like sources retain their original position.
    """
    sampled_bytes = _read_sample_bytes(source, sample_size + 3)
    sample = sampled_bytes[:sample_size]
    lookahead = sampled_bytes[sample_size:]
    if not sample:
        return "utf-8"

    # First try decoding with a curated list of encodings
    for encoding in fallback_encodings:
        try:
            decoder = codecs.getincrementaldecoder(encoding)()
            decoder.decode(sample, final=False)
            # Inspect only the bytes needed to finish the sampled character;
            # decoding all lookahead could create another split boundary.
            for byte in lookahead:
                if not decoder.getstate()[0]:
                    break
                decoder.decode(bytes([byte]), final=False)
            decoder.decode(b"", final=True)
            if encoding == "utf-8" and sampled_bytes.startswith(codecs.BOM_UTF8):
                return "utf-8-sig"
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
