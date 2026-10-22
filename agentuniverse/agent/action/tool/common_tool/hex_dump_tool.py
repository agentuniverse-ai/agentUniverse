#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: hex_dump_tool.py

"""Classic hexdump views over raw bytes, built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency byte inspection
utility. Where ``TextCodecTool`` *converts* between representations
(Base64 / hex encoding round trips), this tool *renders* human
readable, offset-aligned dump views of byte data for debugging, plus
byte-level search and patching. It supports three modes:

* ``dump`` — render the input as classic hexdump lines (xxd style).
  The input is UTF-8 text (``input_encoding='utf8-text'``, the
  default) or Base64-encoded bytes (``input_encoding='base64'``).
  Every line is ``{offset:8 hex digits}``, two spaces, ``width``
  space-separated lowercase two-digit hex byte pairs (``width`` is 8,
  16 or 32, default 16; slots past the end of the data stay blank so
  the columns remain aligned on short lines), two spaces, and an
  ASCII column between pipes where every byte outside ``0x20``-``0x7E``
  is shown as ``.``. For example, ``"Hello, World!\\n"`` at width 16
  renders as::

      00000000  48 65 6c 6c 6f 2c 20 57 6f 72 6c 64 21 0a        |Hello, World!.|

* ``find`` — locate a hex ``pattern`` inside the input and report
  every matching byte offset — *including overlapping occurrences*
  (a forward scan that reports each and every start position, e.g.
  pattern ``"6161"`` in ``"aaaa"`` matches at offsets 0, 1 and 2).
  Each reported match carries the dump line(s) of context that cover
  its bytes. The pattern is two hex digits per byte (case
  insensitive), where the token ``??`` matches any single byte.
* ``patch`` — apply a list of ``{"offset": int, "hex": str}``
  patches to the decoded input bytes and return the patched bytes as
  Base64. Patches are bounds-checked (``offset + length`` must stay
  within the data) and applied in list order, so a later patch
  overwrites an earlier one in overlapping regions.

Input validation is strict and happens before any computation:
malformed parameters (wrong types, empty input, unknown mode /
width / input encoding, an odd-length pattern or one with invalid
characters such as a lone ``?``, a pattern over 4096 bytes, more
than 1000 patches, a patch offset that is not a non-negative
integer, a decoded payload over 1 MiB) raise a ``ValueError``,
mirroring the other common tools. Errors that depend on the
*content being processed* — input declared as Base64 that is not
valid standard Base64, and a patch that would write past the end of
the data — are returned as a structured ``error`` payload so an
agent can react without catching exceptions.
"""

import base64
import binascii
import re
from typing import Any, ClassVar

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Whole pattern: two-char tokens, each either two hex digits or '??'.
# Also rejects odd lengths and half-wildcards such as '?4'.
_HEX_PAIR_TOKENS = re.compile(r"\A(?:[0-9a-fA-F]{2}|\?\?)+\Z")
_PLAIN_HEX = re.compile(r"\A[0-9a-fA-F]+\Z")
_DECIMAL = re.compile(r"\A[0-9]+\Z")


class HexDumpTool(Tool):
    """Hexdump view / search / patch tool built purely on the stdlib.

    Attributes:
        max_bytes (int): Upper bound on the decoded input size; larger
            payloads are rejected before any work.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "hex_dump_tool"
    description: str = (
        "Hex dump tool — pure Python stdlib, no network required. "
        "Classic offset-aligned byte views for debugging (xxd style): "
        "render 8/16/32-byte-per-line hexdump lines of text or "
        "Base64-encoded bytes with an ASCII column (mode='dump'), find "
        "hex patterns with ?? wildcard bytes and get match offsets plus "
        "context dump lines (mode='find'), and apply bounds-checked "
        "{offset, hex} patches to Base64 bytes returning patched Base64 "
        "(mode='patch')."
    )

    MODES: ClassVar[tuple] = ("dump", "find", "patch")
    WIDTHS: ClassVar[tuple] = (8, 16, 32)
    INPUT_ENCODINGS: ClassVar[tuple] = ("utf8-text", "base64")

    #: Decoded input size cap (1 MiB).
    max_bytes: int = 1_048_576
    #: Pattern length cap in bytes.
    MAX_PATTERN_BYTES: ClassVar[int] = 4096
    #: Patch count cap per call.
    MAX_PATCHES: ClassVar[int] = 1000
    #: Cap on matches reported with context (total is still counted).
    MAX_MATCHES: ClassVar[int] = 1000
    #: Cap on offsets listed in the human-readable find summary.
    MAX_SUMMARY_OFFSETS: ClassVar[int] = 100

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        data: Any = None,
        input_encoding: Any = None,
        width: Any = None,
        pattern: Any = None,
        patches: Any = None,
    ) -> dict[str, Any]:
        """Run one hexdump operation.

        Args:
            mode (str): One of ``dump`` / ``find`` / ``patch``.
            data (str): The input to process — UTF-8 text (default) or
                a standard Base64 string, selected by ``input_encoding``.
            input_encoding (str): ``utf8-text`` (default) or ``base64``.
            width (int | str): Bytes per dump line — 8, 16 or 32
                (default 16). Used by the ``dump`` mode and the
                ``find`` context lines.
            pattern (str): Find mode only — hex pattern, two hex
                digits per byte (case-insensitive), where the token
                ``??`` matches any single byte; no spaces, no prefix.
            patches (list): Patch mode only — a non-empty list of
                ``{"offset": non-negative int, "hex": even-length hex
                string}`` objects applied in list order to the decoded
                bytes; the patched bytes are returned as Base64.

        Returns:
            Dict[str, Any]: The operation result (always a ``result``
                string plus the call context) or a structured ``error``
                payload for content-level failures (invalid Base64
                input, a patch writing past the end of the data).

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        clean_data = self._validate_data(data)
        encoding = self._validate_input_encoding(input_encoding)
        clean_width = self._validate_width(width)

        if encoding == "base64":
            try:
                raw = base64.b64decode(clean_data, validate=True)
            except (binascii.Error, ValueError):
                return self._error_result(
                    {"mode": mode, "input_encoding": "base64"},
                    error_type="invalid_base64",
                    message=(
                        "input is not valid standard Base64: expected only "
                        "characters from the Base64 alphabet with correct "
                        "'=' padding and a length that is a multiple of four "
                        f"(got {clean_data[:64]!r})"
                    ),
                )
        else:
            raw = clean_data.encode("utf-8")
        if len(raw) > self.max_bytes:
            self._invalid(
                f"decoded input exceeds the {self.max_bytes:,}-byte limit "
                f"(got {len(raw):,} bytes)"
            )

        context: dict[str, Any] = {
            "mode": mode,
            "input_encoding": encoding,
            "size": len(raw),
        }
        if mode == "patch":
            return self._run_patch(raw, patches, context)
        context["width"] = clean_width
        if mode == "find":
            return self._run_find(raw, pattern, clean_width, context)
        lines = [
            self._format_line(raw, clean_width, line_start)
            for line_start in range(0, len(raw), clean_width)
        ]
        return {**context, "result": "\n".join(lines)}

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"hex_dump_tool: {message}")

    @classmethod
    def _validate_data(cls, data: Any) -> str:
        """Validate the ``data`` input."""
        if data is None or isinstance(data, bool) or not isinstance(data, str):
            cls._invalid(f"data must be a non-empty string (got {data!r})")
        if not data:
            cls._invalid("data must be a non-empty string (got '')")
        return data

    @classmethod
    def _validate_input_encoding(cls, input_encoding: Any) -> str:
        """Validate the ``input_encoding`` selector."""
        if input_encoding is None:
            return "utf8-text"
        if isinstance(input_encoding, bool) or input_encoding not in (
            cls.INPUT_ENCODINGS
        ):
            cls._invalid(
                "input_encoding must be one of: "
                f"{', '.join(cls.INPUT_ENCODINGS)} (got {input_encoding!r})"
            )
        return input_encoding

    @classmethod
    def _validate_width(cls, width: Any) -> int:
        """Validate the ``width`` selector (accepts int or digit string)."""
        if width is None:
            return 16
        if isinstance(width, bool):
            cls._invalid(
                f"width must be one of: {', '.join(map(str, cls.WIDTHS))} "
                f"(got {width!r})"
            )
        if isinstance(width, int):
            if width in cls.WIDTHS:
                return width
        elif isinstance(width, str) and width in map(str, cls.WIDTHS):
            return int(width)
        cls._invalid(
            f"width must be one of: {', '.join(map(str, cls.WIDTHS))} "
            f"(got {width!r})"
        )

    @classmethod
    def _validate_pattern(cls, pattern: Any) -> str:
        """Validate the find-mode ``pattern`` (hex bytes + ``??`` wildcards)."""
        if pattern is None or isinstance(pattern, bool) or not isinstance(
            pattern, str
        ):
            cls._invalid(f"pattern must be a non-empty hex string (got {pattern!r})")
        if not pattern:
            cls._invalid("pattern must be a non-empty hex string (got '')")
        if not _HEX_PAIR_TOKENS.match(pattern):
            cls._invalid(
                "pattern must be an even number of two-digit hex bytes "
                "(0-9, a-f, A-F) with optional '??' wildcard bytes, without "
                f"whitespace or prefix (got {pattern[:64]!r})"
            )
        if len(pattern) > 2 * cls.MAX_PATTERN_BYTES:
            cls._invalid(
                f"pattern exceeds the {cls.MAX_PATTERN_BYTES:,}-byte limit "
                f"(got {len(pattern) // 2:,} bytes)"
            )
        return pattern

    @classmethod
    def _validate_patches(cls, patches: Any) -> list[tuple[int, bytes]]:
        """Validate the patch-mode ``patches`` list (offset, payload) pairs."""
        shape = "patches must be a non-empty list of {'offset': int, 'hex': str} objects"
        if patches is None or isinstance(patches, bool) or not isinstance(
            patches, list
        ):
            cls._invalid(f"{shape} (got {patches!r})")
        if not patches:
            cls._invalid(f"{shape} (got [])")
        if len(patches) > cls.MAX_PATCHES:
            cls._invalid(
                f"too many patches: at most {cls.MAX_PATCHES:,} are allowed "
                f"per call (got {len(patches):,})"
            )
        clean: list[tuple[int, bytes]] = []
        for index, entry in enumerate(patches):
            if isinstance(entry, bool) or not isinstance(entry, dict):
                cls._invalid(
                    f"patch #{index} must be an object with 'offset' and "
                    f"'hex' keys (got {entry!r})"
                )
            keys = set(entry)
            if keys != {"offset", "hex"}:
                missing = ", ".join(sorted({"offset", "hex"} - keys)) or "none"
                unknown = ", ".join(sorted(keys - {"offset", "hex"})) or "none"
                cls._invalid(
                    f"patch #{index} must have exactly the keys 'offset' and "
                    f"'hex' (missing: {missing}; unexpected: {unknown})"
                )
            offset = cls._validate_patch_offset(entry["offset"], index)
            hex_str = entry["hex"]
            if (
                isinstance(hex_str, bool)
                or not isinstance(hex_str, str)
                or not hex_str
                or len(hex_str) % 2 != 0
                or not _PLAIN_HEX.match(hex_str)
            ):
                cls._invalid(
                    f"patch #{index} 'hex' must be a non-empty even-length "
                    f"hex string without wildcards (got {hex_str!r})"
                )
            clean.append((offset, bytes.fromhex(hex_str)))
        return clean

    @classmethod
    def _validate_patch_offset(cls, offset: Any, index: int) -> int:
        """Validate one patch ``offset`` (non-negative int or digit string)."""
        if isinstance(offset, bool):
            cls._invalid(
                f"patch #{index} 'offset' must be a non-negative integer "
                f"(got {offset!r})"
            )
        if isinstance(offset, int):
            value = offset
        elif isinstance(offset, str) and _DECIMAL.match(offset):
            value = int(offset)
        else:
            cls._invalid(
                f"patch #{index} 'offset' must be a non-negative integer "
                f"(got {offset!r})"
            )
        if value < 0:
            cls._invalid(
                f"patch #{index} 'offset' must be a non-negative integer "
                f"(got {value})"
            )
        return value

    # ------------------------------------------------------------------ #
    # Rendering (shared by dump lines and find context lines)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _format_line(data: bytes, width: int, line_start: int) -> str:
        """Render one hexdump line starting at ``line_start``.

        Layout: 8 lowercase hex offset digits, two spaces, ``width``
        two-character tokens (a lowercase hex byte pair, or two blanks
        past the end of the data) joined by single spaces, two spaces,
        then the ASCII column between pipes — printable bytes
        (0x20-0x7E) as themselves, everything else as ``.``.
        """
        chunk = data[line_start : line_start + width]
        tokens = [f"{byte:02x}" for byte in chunk]
        tokens.extend(["  "] * (width - len(chunk)))
        ascii_part = "".join(
            chr(byte) if 0x20 <= byte <= 0x7E else "." for byte in chunk
        )
        return f"{line_start:08x}  {' '.join(tokens)}  |{ascii_part}|"

    # ------------------------------------------------------------------ #
    # find mode
    # ------------------------------------------------------------------ #

    def _run_find(
        self, raw: bytes, pattern: Any, width: int, context: dict[str, Any]
    ) -> dict[str, Any]:
        """Locate every (possibly overlapping) occurrence of the pattern."""
        clean_pattern = self._validate_pattern(pattern)
        pattern_len = len(clean_pattern) // 2
        regex = self._pattern_regex(clean_pattern)
        # Overlapping policy: a lookahead-based finditer reports every
        # start position whose following bytes match the pattern, not
        # just non-overlapping ones.
        offsets = [match.start() for match in regex.finditer(raw)]
        total = len(offsets)
        reported = offsets[: self.MAX_MATCHES]
        matches: list[dict[str, Any]] = []
        for offset in reported:
            first_line = (offset // width) * width
            last_line = ((offset + pattern_len - 1) // width) * width
            matches.append(
                {
                    "offset": offset,
                    "context": [
                        self._format_line(raw, width, line_start)
                        for line_start in range(first_line, last_line + 1, width)
                    ],
                }
            )
        if total == 0:
            summary = "0 match(es) found — the pattern does not occur in the input"
        else:
            summary = (
                f"{total:,} match(es) at byte offset(s): "
                + ", ".join(str(offset) for offset in reported[: self.MAX_SUMMARY_OFFSETS])
            )
            if len(reported) > self.MAX_SUMMARY_OFFSETS:
                summary += ", ..."
            if total > len(reported):
                summary += (
                    f" (first {len(reported):,} of {total:,} matches reported)"
                )
        return {
            **context,
            "pattern": clean_pattern.lower(),
            "matches": matches,
            "total_matches": total,
            "truncated": total > len(reported),
            "result": summary,
        }

    @staticmethod
    def _pattern_regex(pattern: str) -> "re.Pattern[bytes]":
        """Compile a validated hex/``??`` pattern to an overlap-aware regex."""
        parts: list[bytes] = []
        for index in range(0, len(pattern), 2):
            pair = pattern[index : index + 2]
            if pair == "??":
                parts.append(b".")
            else:
                # Escape the byte as an explicit \xNN regex escape; the
                # hex digits must be ASCII text, not the raw byte.
                parts.append(b"\\x%02x" % int(pair, 16))
        return re.compile(b"(?=(" + b"".join(parts) + b"))", re.DOTALL)

    # ------------------------------------------------------------------ #
    # patch mode
    # ------------------------------------------------------------------ #

    def _run_patch(
        self, raw: bytes, patches: Any, context: dict[str, Any]
    ) -> dict[str, Any]:
        """Apply bounds-checked patches in list order, return Base64."""
        clean_patches = self._validate_patches(patches)
        size = len(raw)
        for index, (offset, payload) in enumerate(clean_patches):
            if offset + len(payload) > size:
                return self._error_result(
                    context,
                    error_type="offset_out_of_range",
                    message=(
                        f"patch #{index} (offset {offset}, {len(payload)} "
                        f"byte(s)) would write past the end of the "
                        f"{size:,}-byte input; every patch must satisfy "
                        f"offset + hex length <= {size:,}"
                    ),
                )
        buffer = bytearray(raw)
        for offset, payload in clean_patches:
            buffer[offset : offset + len(payload)] = payload
        return {
            **context,
            "patches_applied": len(clean_patches),
            "result": base64.b64encode(bytes(buffer)).decode("ascii"),
        }

    # ------------------------------------------------------------------ #
    # Error payloads (structured, returned instead of raising)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _error_result(
        context: dict[str, Any], error_type: str, message: str
    ) -> dict[str, Any]:
        """Build a structured error payload."""
        return {
            **context,
            "error": {"type": error_type, "message": str(message)[:500]},
        }
