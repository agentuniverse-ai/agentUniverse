#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: checksum_tool.py

"""Lightweight transmission checksum tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency checksum utility
agents can call when exchanging text: detecting typos or truncated
transfers before heavier validation runs. It deliberately complements
the existing common tools — cryptographic digests (MD5 / SHA families)
live in ``TextCodecTool``'s ``hash`` mode and Luhn / ISBN / EAN / UPC
checksums live in ``BarcodeValidatorTool`` — by covering the cheap
non-cryptographic checksums used in file formats, serial protocols and
documentation: CRC-32, Adler-32, Fletcher-16 and simple byte sums.

Three modes are supported:

* ``compute`` — checksum the input with one ``algorithm`` and return
  both the zero-padded lowercase hex string (8 digits for crc32 /
  adler32, 4 for fletcher16 / sum16, 2 for sum8) and the unsigned
  integer value.
* ``verify`` — checksum the input and compare against ``expected``,
  a case-insensitive hex string of exactly the algorithm's digit
  width; returns a ``match`` boolean plus the computed hex for
  transparency.
* ``all`` — compute every supported algorithm over the same input at
  once, keyed by algorithm name.

The input is text in one of two ``input_encoding`` forms:
``utf8-text`` (default — the text's UTF-8 bytes are checksummed) or
``base64`` (the decoded bytes are checksummed, so arbitrary binary
payloads can be verified through a text channel). Base64 decoding is
strict (``validate=True`` semantics); invalid Base64 is returned as a
structured ``error`` payload instead of raising.

Algorithm notes: ``crc32`` and ``adler32`` come from ``zlib`` (masked
to unsigned 32-bit); ``fletcher16`` is the classic byte-wise form
(two running sums modulo 255, result ``sum2 * 256 + sum1``),
hand-implemented here in the streaming form used across serial
protocols; ``sum8`` / ``sum16`` are plain byte sums modulo 256 /
65536. All of them are error-detection codes, not security
mechanisms — anyone can forge a matching checksum, and short
checksums collide by design (for example fletcher16 maps both the
empty input and ``b"\\xff\\xff"`` to ``0x0000``).

Input validation is strict and happens before any computation:
malformed parameters (wrong types, unknown mode / algorithm /
input_encoding, missing ``algorithm`` in the compute / verify modes,
missing or non-hex ``expected`` with the position of the first
invalid character reported, wrong or odd ``expected`` digit count,
input over 1 MB) raise a ``ValueError``, mirroring the other common
tools. Errors that depend on the *content being processed* — input
that is not valid standard Base64 — are returned as a structured
``error`` payload so an agent can react without catching exceptions.
"""

import base64
import binascii
import zlib
from typing import Any, ClassVar, Dict

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

_HEX_DIGITS = "0123456789abcdefABCDEF"


class ChecksumTool(Tool):
    """Lightweight transmission checksum tool built purely on the stdlib.

    Attributes:
        max_input_bytes (int): Upper bound on the number of input bytes
            (UTF-8 encoded text or Base64-decoded bytes) the tool will
            checksum; larger inputs are rejected before any work.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "checksum_tool"
    description: str = (
        "Checksum tool — pure Python stdlib, no network required. "
        "Lightweight transmission checksums over text or Base64-decoded "
        "bytes; crc32 and adler32 via zlib (8 hex digits), classic "
        "byte-wise fletcher16 (4 hex digits), sum8 (mod 256, 2 hex "
        "digits) and sum16 (mod 65536, 4 hex digits). Compute mode "
        "returns the hex and unsigned int for one algorithm, verify "
        "mode compares a case-insensitive expected hex string and "
        "returns a match bool, and all mode computes every algorithm "
        "at once. Not cryptographic — use TextCodecTool hash mode for "
        "digests."
    )

    MODES: ClassVar[tuple] = ("compute", "verify", "all")
    ENCODINGS: ClassVar[tuple] = ("utf8-text", "base64")
    ALGORITHMS: ClassVar[tuple] = (
        "crc32",
        "adler32",
        "fletcher16",
        "sum8",
        "sum16",
    )
    # Zero-padded lowercase hex digit count per algorithm.
    HEX_WIDTHS: ClassVar[Dict[str, int]] = {
        "crc32": 8,
        "adler32": 8,
        "fletcher16": 4,
        "sum8": 2,
        "sum16": 4,
    }

    max_input_bytes: int = 1_048_576

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any = None,
        input: Any = None,
        algorithm: Any = None,
        input_encoding: Any = None,
        expected: Any = None,
    ) -> Dict[str, Any]:
        """Run one checksum operation.

        Args:
            mode (str): One of ``compute`` / ``verify`` / ``all``.
            input (str): The text to checksum. For the default
                ``utf8-text`` encoding its UTF-8 bytes are checksummed
                (the empty string is allowed — its checksums are
                well-defined); for ``base64`` the decoded bytes are
                checksummed, so binary payloads can pass through a
                text channel.
            algorithm (str): ``crc32`` / ``adler32`` / ``fletcher16`` /
                ``sum8`` / ``sum16`` — required for the ``compute`` and
                ``verify`` modes, not used by ``all``.
            input_encoding (str): ``utf8-text`` (default) or ``base64``.
            expected (str): Verify mode only — the expected checksum as
                a case-insensitive hex string of exactly the
                algorithm's digit width (8 / 8 / 4 / 2 / 4 digits for
                crc32 / adler32 / fletcher16 / sum8 / sum16), with no
                ``0x`` prefix, sign or whitespace.

        Returns:
            Dict[str, Any]: The checksum result (``algorithm``, ``hex``
                and ``unsigned_int`` for compute; ``match`` plus the
                computed hex for verify; a per-algorithm ``results``
                mapping for all) or a structured ``error`` payload for
                content-level failures (input that is not valid
                standard Base64).

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        clean_encoding = self._validate_encoding(input_encoding)
        data = self._load_input(input, clean_encoding)
        if data is None:
            return self._error_result(
                {"input_encoding": "base64"},
                error_type="invalid_base64",
                message=(
                    "input is not valid standard Base64: expected only "
                    "characters from the Base64 alphabet with correct "
                    "'=' padding and a length that is a multiple of four "
                    f"(got {input[:64]!r})"
                ),
            )
        if mode == "all":
            return self._run_all(data, clean_encoding)
        clean_algorithm = self._validate_algorithm(algorithm)
        if mode == "compute":
            return self._run_compute(data, clean_encoding, clean_algorithm)
        return self._run_verify(
            data, clean_encoding, clean_algorithm, expected
        )

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"checksum_tool: {message}")

    @classmethod
    def _validate_encoding(cls, input_encoding: Any) -> str:
        """Validate the ``input_encoding`` selector (None = default)."""
        if input_encoding is None:
            return "utf8-text"
        if isinstance(input_encoding, bool) or input_encoding not in cls.ENCODINGS:
            cls._invalid(
                "input_encoding must be one of: "
                f"{', '.join(cls.ENCODINGS)} (got {input_encoding!r})"
            )
        return input_encoding

    @classmethod
    def _validate_algorithm(cls, algorithm: Any) -> str:
        """Validate the ``algorithm`` whitelist selector."""
        if algorithm not in cls.ALGORITHMS:
            cls._invalid(
                "algorithm must be one of: "
                f"{', '.join(cls.ALGORITHMS)} (got {algorithm!r})"
            )
        return algorithm

    def _load_input(self, input: Any, input_encoding: str) -> bytes:
        """Validate ``input`` and return the bytes to be checksummed.

        The checksum of the empty input is well-defined for every
        algorithm, so an empty string is accepted. Invalid Base64
        content is reported as a structured error payload by the
        caller-facing wrapper instead of raising.
        """
        limit = self.max_input_bytes
        if input is None or isinstance(input, bool) or not isinstance(input, str):
            self._invalid(f"input must be a string (got {input!r})")
        if input_encoding == "base64":
            # Bound the decode work before touching binascii: a 1 MB
            # payload needs at most ~1.4 M Base64 characters.
            if len(input) > limit * 2:
                self._invalid(
                    f"input exceeds the {limit * 2:,}-character limit for "
                    f"Base64 text (got {len(input):,} characters)"
                )
            try:
                data = base64.b64decode(input, validate=True)
            except (binascii.Error, ValueError):
                return None  # replaced by the structured error below
            if len(data) > limit:
                self._invalid(
                    f"decoded input exceeds the {limit:,}-byte "
                    f"(1 MB) limit (got {len(data):,} bytes)"
                )
            return data
        if len(input) > limit:
            self._invalid(
                f"input exceeds the {limit:,}-character limit "
                f"(got {len(input):,} characters)"
            )
        data = input.encode("utf-8")
        if len(data) > limit:
            self._invalid(
                f"input exceeds the {limit:,}-byte (1 MB) limit once "
                f"UTF-8 encoded (got {len(data):,} bytes)"
            )
        return data

    @classmethod
    def _validate_expected(cls, expected: Any, algorithm: str) -> str:
        """Validate the verify-mode ``expected`` hex string.

        Returns the normalized lowercase hex. Position numbers are
        zero-based, mirroring the byte indexes reported elsewhere in
        the codebase.
        """
        width = cls.HEX_WIDTHS[algorithm]
        if expected is None or isinstance(expected, bool) or not isinstance(expected, str):
            cls._invalid(
                f"expected must be a hexadecimal string of {width} digits "
                f"for {algorithm} (got {expected!r})"
            )
        for position, char in enumerate(expected):
            if char not in _HEX_DIGITS:
                cls._invalid(
                    f"expected contains invalid hexadecimal character "
                    f"{char!r} at position {position}"
                )
        if len(expected) != width:
            cls._invalid(
                f"expected must be exactly {width} hexadecimal digits for "
                f"{algorithm} (got {len(expected)} digits: {expected[:32]!r})"
            )
        return expected.lower()

    # ------------------------------------------------------------------ #
    # Checksum primitives
    # ------------------------------------------------------------------ #

    @staticmethod
    def _fletcher16(data: bytes) -> int:
        """Classic byte-wise Fletcher-16 (sums modulo 255).

        Two running sums are updated per byte — ``sum1`` accumulates
        the bytes, ``sum2`` accumulates ``sum1`` — and the checksum is
        ``sum2 * 256 + sum1``, the form used across serial protocols.
        """
        sum1 = 0
        sum2 = 0
        for byte in data:
            sum1 = (sum1 + byte) % 255
            sum2 = (sum2 + sum1) % 255
        return (sum2 << 8) | sum1

    @classmethod
    def _checksum(cls, algorithm: str, data: bytes) -> int:
        """Compute the unsigned integer checksum for one algorithm."""
        if algorithm == "crc32":
            return zlib.crc32(data) & 0xFFFFFFFF
        if algorithm == "adler32":
            return zlib.adler32(data) & 0xFFFFFFFF
        if algorithm == "fletcher16":
            return cls._fletcher16(data)
        if algorithm == "sum8":
            return sum(data) % 256
        return sum(data) % 65536

    def _entry(self, algorithm: str, data: bytes) -> Dict[str, Any]:
        """Build the per-algorithm result entry."""
        value = self._checksum(algorithm, data)
        return {
            "algorithm": algorithm,
            "hex": f"{value:0{self.HEX_WIDTHS[algorithm]}x}",
            "unsigned_int": value,
        }

    # ------------------------------------------------------------------ #
    # Modes
    # ------------------------------------------------------------------ #

    def _run_compute(
        self, data: bytes, input_encoding: str, algorithm: str
    ) -> Dict[str, Any]:
        """Checksum the input with one algorithm."""
        return {
            "mode": "compute",
            "input_encoding": input_encoding,
            "byte_length": len(data),
            **self._entry(algorithm, data),
        }

    def _run_verify(
        self, data: bytes, input_encoding: str, algorithm: str, expected: Any
    ) -> Dict[str, Any]:
        """Checksum the input and compare with the expected hex."""
        clean_expected = self._validate_expected(expected, algorithm)
        entry = self._entry(algorithm, data)
        return {
            "mode": "verify",
            "input_encoding": input_encoding,
            "byte_length": len(data),
            "algorithm": algorithm,
            "expected": clean_expected,
            "computed_hex": entry["hex"],
            "match": entry["hex"] == clean_expected,
        }

    def _run_all(self, data: bytes, input_encoding: str) -> Dict[str, Any]:
        """Compute every supported algorithm over the same input."""
        return {
            "mode": "all",
            "input_encoding": input_encoding,
            "byte_length": len(data),
            "results": {
                algorithm: self._entry(algorithm, data)
                for algorithm in self.ALGORITHMS
            },
        }

    # ------------------------------------------------------------------ #
    # Error payloads (structured, returned instead of raising)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _error_result(
        context: Dict[str, Any], error_type: str, message: str
    ) -> Dict[str, Any]:
        """Build a structured error payload."""
        return {
            **context,
            "error": {"type": error_type, "message": str(message)[:500]},
        }
