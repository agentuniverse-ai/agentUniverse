#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: text_codec_tool.py

"""Text encoding / hashing / ID utility tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency text codec agents can
call for identifier plumbing: preparing payloads, checking digests, or
generating deterministic IDs.

The tool is a thin, strictly-validated façade over four standard
library modules — ``base64``, ``urllib.parse``, ``hashlib`` and
``uuid`` — and supports five modes:

* ``base64`` — encode UTF-8 text to standard Base64 (with padding) and
  decode it back. Decoding uses ``validate=True`` semantics: any
  character outside the standard alphabet, missing or misplaced ``=``
  padding, or decoded bytes that are not valid UTF-8 are reported as a
  structured ``error`` payload instead of raising.
* ``url`` — RFC 3986 percent encoding and decoding. Encoding escapes
  every reserved and non-ASCII character (the unreserved
  ``A-Za-z0-9_.-~`` set is always kept); an optional ``safe`` string
  lists extra ASCII characters to leave unescaped. Decoding rejects
  dangling or non-hex ``%`` escapes with a structured error payload
  instead of silently passing them through.
* ``hex`` — encode UTF-8 text to lowercase hexadecimal and decode it
  back (case-insensitive input, strictly even-length hex digits, no
  ``0x`` prefix, no embedded whitespace).
* ``hash`` — MD5 / SHA-1 / SHA-256 / SHA-512 digest of the UTF-8
  encoding of the text, returned as a lowercase hex string. An optional
  ``salt`` string is prefixed to the text before hashing
  (``digest(salt + text)``).
* ``uuid`` — UUID generation: version 4 (random, ``os.urandom``) or
  version 5 (SHA-1, deterministic) with one of the well-known
  namespaces ``dns`` / ``url`` / ``oid`` / ``x500`` (case-insensitive)
  or a custom namespace given as a UUID hex string.

Input validation is strict and happens before any computation:
malformed parameters (wrong types, empty text in the encode/decode
modes, unknown mode / operation / algorithm / version, missing
version-5 ``name`` or ``namespace``, non-ASCII or whitespace ``safe``
characters, oversized text) raise a ``ValueError``, mirroring the
other common tools. Errors
that depend on the *content being processed* — invalid Base64, invalid
percent escapes, invalid hex, decoded bytes that are not UTF-8, and a
namespace string that is neither a well-known label nor a valid UUID —
are returned as a structured ``error`` payload so an agent can react
without catching exceptions.
"""

import base64
import binascii
import hashlib
import re
import urllib.parse
import uuid as uuid_module
from typing import Any, ClassVar, Dict

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

_HEXDIGITS = re.compile(r"\A[0-9a-fA-F]+\Z")
# Every '%' must be followed by exactly two hex digits (RFC 3986 pct-encoded).
_BAD_PERCENT = re.compile(r"%(?![0-9A-Fa-f]{2})")


class TextCodecTool(Tool):
    """Encoding / hashing / ID utility tool built purely on the stdlib.

    Attributes:
        max_text_chars (int): Upper bound on the ``text`` / ``name``
            input length; longer inputs are rejected before any work.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "text_codec_tool"
    description: str = (
        "Text codec tool — pure Python stdlib, no network required. "
        "Base64 encode/decode of UTF-8 text (mode='base64'), RFC 3986 "
        "percent encode/decode with an optional safe-character string "
        "(mode='url'), lowercase hex encode/decode (mode='hex'), "
        "MD5/SHA-1/SHA-256/SHA-512 hashes with optional salt prefix "
        "(mode='hash'), and UUID v4 random / v5 namespace+name "
        "deterministic generation (mode='uuid')."
    )

    MODES: ClassVar[tuple] = ("base64", "url", "hex", "hash", "uuid")
    OPERATIONS: ClassVar[tuple] = ("encode", "decode")
    ALGORITHMS: ClassVar[tuple] = ("md5", "sha1", "sha256", "sha512")
    UUID_VERSIONS: ClassVar[tuple] = (4, 5)
    # Well-known RFC 4122 namespaces, accepted case-insensitively.
    NAMESPACES: ClassVar[Dict[str, Any]] = {
        "dns": uuid_module.NAMESPACE_DNS,
        "url": uuid_module.NAMESPACE_URL,
        "oid": uuid_module.NAMESPACE_OID,
        "x500": uuid_module.NAMESPACE_X500,
    }

    max_text_chars: int = 100_000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        text: Any = None,
        operation: Any = None,
        algorithm: Any = None,
        salt: Any = None,
        version: Any = None,
        namespace: Any = None,
        name: Any = None,
        safe: Any = None,
    ) -> Dict[str, Any]:
        """Run one codec operation.

        Args:
            mode (str): One of ``base64`` / ``url`` / ``hex`` / ``hash`` /
                ``uuid``.
            text (str): The text to encode / decode / hash. Required for
                the ``base64``, ``url``, ``hex`` and ``hash`` modes (a
                non-empty string for the encode/decode modes; the
                ``hash`` mode also accepts the empty string, whose
                digest is a well-defined value); not used by ``uuid``.
            operation (str): ``encode`` or ``decode`` — required for the
                ``base64``, ``url`` and ``hex`` modes; not used by
                ``hash`` or ``uuid``.
            algorithm (str): ``md5`` / ``sha1`` / ``sha256`` / ``sha512`` —
                required for the ``hash`` mode.
            salt (str): Optional salt string prefixed to the text before
                hashing (``digest(salt + text)``). Hash mode only.
            version (int | str): ``4`` or ``5`` (or ``"4"`` / ``"5"``) —
                required for the ``uuid`` mode.
            namespace (str): Version 5 only — one of the well-known
                labels ``dns`` / ``url`` / ``oid`` / ``x500``
                (case-insensitive) or a custom namespace as a UUID hex
                string.
            name (str): Version 5 only — the name to hash into the UUID.
            safe (str): URL mode only — extra ASCII characters (no
                whitespace, no ``%``) left unescaped when encoding;
                defaults to escaping everything but unreserved
                characters.

        Returns:
            Dict[str, Any]: The operation result (always a ``result``
                string plus the call context) or a structured ``error``
                payload for content-level failures (invalid Base64,
                invalid percent escapes, invalid hex, non-UTF-8 decoded
                bytes, invalid namespace).

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        if mode == "uuid":
            return self._run_uuid(version, namespace, name)
        if mode == "hash":
            # The digest of the empty string is a well-defined value, so
            # the hash mode accepts it; the encode/decode modes do not.
            clean_text = self._validate_text(text, allow_empty=True)
            return self._run_hash(clean_text, algorithm, salt)

        clean_text = self._validate_text(text)
        clean_operation = self._validate_operation(operation)
        if mode == "base64":
            return self._run_base64(clean_operation, clean_text)
        if mode == "url":
            return self._run_url(clean_operation, clean_text, safe)
        return self._run_hex(clean_operation, clean_text)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"text_codec_tool: {message}")

    @classmethod
    def _validate_text(cls, text: Any, allow_empty: bool = False) -> str:
        """Validate the ``text`` input (also used for ``name``)."""
        if text is None or isinstance(text, bool) or not isinstance(text, str):
            cls._invalid(f"text must be a non-empty string (got {text!r})")
        if not text and not allow_empty:
            cls._invalid("text must be a non-empty string (got '')")
        if len(text) > 100_000:
            cls._invalid(
                f"text exceeds the {100_000:,}-character limit "
                f"(got {len(text):,} characters)"
            )
        return text

    @classmethod
    def _validate_operation(cls, operation: Any) -> str:
        """Validate the encode/decode ``operation`` selector."""
        if operation not in cls.OPERATIONS:
            cls._invalid(
                "operation must be one of: "
                f"{', '.join(cls.OPERATIONS)} (got {operation!r})"
            )
        return operation

    @classmethod
    def _validate_safe(cls, safe: Any) -> str:
        """Validate the URL-mode ``safe`` extra-unescaped character set.

        Accepts ``None`` (escape everything but unreserved characters)
        and ASCII printable characters other than ``%``; rejects
        whitespace, non-ASCII characters and ``%`` itself.
        """
        if safe is None:
            return ""
        if isinstance(safe, bool) or not isinstance(safe, str):
            cls._invalid(f"safe must be a string of ASCII characters (got {safe!r})")
        for char in safe:
            code = ord(char)
            if code < 0x21 or code > 0x7E:
                cls._invalid(
                    "safe must only contain printable ASCII characters "
                    f"without whitespace (got {safe!r})"
                )
            if char == "%":
                cls._invalid(
                    "safe must not contain '%' — percent escapes must "
                    "stay unambiguous"
                )
        return safe

    # ------------------------------------------------------------------ #
    # base64 / url / hex modes
    # ------------------------------------------------------------------ #

    def _run_base64(self, operation: str, text: str) -> Dict[str, Any]:
        """Encode / decode standard Base64 with strict validation."""
        context = {"mode": "base64", "operation": operation}
        if operation == "encode":
            encoded = base64.b64encode(text.encode("utf-8")).decode("ascii")
            return {**context, "result": encoded}
        try:
            raw = base64.b64decode(text, validate=True)
        except (binascii.Error, ValueError):
            return self._error_result(
                context,
                error_type="invalid_base64",
                message=(
                    "input is not valid standard Base64: expected only "
                    "characters from the Base64 alphabet with correct "
                    "'=' padding and a length that is a multiple of four "
                    f"(got {text[:64]!r})"
                ),
            )
        try:
            decoded = raw.decode("utf-8")
        except UnicodeDecodeError:
            return self._error_result(
                context,
                error_type="invalid_utf8",
                message=(
                    "Base64 input decodes to bytes that are not valid "
                    "UTF-8 text"
                ),
            )
        return {**context, "result": decoded}

    def _run_url(self, operation: str, text: str, safe: Any) -> Dict[str, Any]:
        """Percent encode / decode according to RFC 3986."""
        clean_safe = self._validate_safe(safe)
        context = {"mode": "url", "operation": operation, "safe": clean_safe}
        if operation == "encode":
            encoded = urllib.parse.quote(text, safe=clean_safe)
            return {**context, "result": encoded}
        if _BAD_PERCENT.search(text):
            return self._error_result(
                context,
                error_type="invalid_percent_encoding",
                message=(
                    "input contains a '%' that is not followed by two "
                    "hexadecimal digits; strict RFC 3986 percent-decoding "
                    f"is required (got {text[:64]!r})"
                ),
            )
        return {**context, "result": urllib.parse.unquote(text)}

    def _run_hex(self, operation: str, text: str) -> Dict[str, Any]:
        """Encode / decode lowercase hexadecimal text."""
        context = {"mode": "hex", "operation": operation}
        if operation == "encode":
            return {**context, "result": text.encode("utf-8").hex()}
        if len(text) % 2 != 0 or not _HEXDIGITS.match(text):
            return self._error_result(
                context,
                error_type="invalid_hex",
                message=(
                    "input is not valid hexadecimal text: expected an "
                    "even number of hex digits (0-9, a-f, A-F) without "
                    "prefix or whitespace "
                    f"(got {text[:64]!r})"
                ),
            )
        raw = bytes.fromhex(text)
        try:
            decoded = raw.decode("utf-8")
        except UnicodeDecodeError:
            return self._error_result(
                context,
                error_type="invalid_utf8",
                message="hex input decodes to bytes that are not valid UTF-8 text",
            )
        return {**context, "result": decoded}

    # ------------------------------------------------------------------ #
    # hash mode
    # ------------------------------------------------------------------ #

    def _run_hash(self, text: str, algorithm: Any, salt: Any) -> Dict[str, Any]:
        """Hash the (optionally salt-prefixed) text to a hex digest."""
        if algorithm not in self.ALGORITHMS:
            self._invalid(
                "algorithm must be one of: "
                f"{', '.join(self.ALGORITHMS)} (got {algorithm!r})"
            )
        if salt is not None and (isinstance(salt, bool) or not isinstance(salt, str)):
            self._invalid(f"salt must be a non-empty string or None (got {salt!r})")
        if salt == "":
            self._invalid("salt must be a non-empty string or None (got '')")
        hasher = hashlib.new(algorithm)
        if salt:
            hasher.update(salt.encode("utf-8"))
        hasher.update(text.encode("utf-8"))
        return {
            "mode": "hash",
            "algorithm": algorithm,
            "salted": bool(salt),
            "result": hasher.hexdigest(),
        }

    # ------------------------------------------------------------------ #
    # uuid mode
    # ------------------------------------------------------------------ #

    def _run_uuid(
        self, version: Any, namespace: Any, name: Any
    ) -> Dict[str, Any]:
        """Generate a UUID v4 (random) or v5 (namespace + name)."""
        if isinstance(version, bool) or version not in (4, 5, "4", "5"):
            self._invalid(
                f"version must be 4 or 5 (got {version!r})"
            )
        version = int(version)
        if version == 4:
            return {
                "mode": "uuid",
                "version": 4,
                "result": str(uuid_module.uuid4()),
            }

        clean_name = self._validate_uuid_name(name)
        context: Dict[str, Any] = {
            "mode": "uuid",
            "version": 5,
        }
        if namespace is None or isinstance(namespace, bool) or not isinstance(namespace, str):
            self._invalid(
                "namespace is required for UUID v5 and must be one of: "
                f"{', '.join(sorted(self.NAMESPACES))} (case-insensitive) "
                "or a UUID hex string "
                f"(got {namespace!r})"
            )
        label = namespace.strip().lower()
        if label in self.NAMESPACES:
            return {
                **context,
                "namespace": label,
                "name": clean_name,
                "result": str(uuid_module.uuid5(self.NAMESPACES[label], clean_name)),
            }
        try:
            custom = uuid_module.UUID(namespace.strip())
        except ValueError:
            return self._error_result(
                context,
                error_type="invalid_namespace",
                message=(
                    "namespace must be one of: "
                    f"{', '.join(sorted(self.NAMESPACES))} "
                    "(case-insensitive) or a custom namespace given as a "
                    f"UUID hex string, e.g. "
                    "'6ba7b810-9dad-11d1-80b4-00c04fd430c8' "
                    f"(got {namespace[:64]!r})"
                ),
            )
        return {
            **context,
            "namespace": str(custom),
            "name": clean_name,
            "result": str(uuid_module.uuid5(custom, clean_name)),
        }

    @classmethod
    def _validate_uuid_name(cls, name: Any) -> str:
        """Validate the UUID v5 ``name`` (the string hashed into the UUID)."""
        if name is None or isinstance(name, bool) or not isinstance(name, str):
            cls._invalid(f"name must be a non-empty string for UUID v5 (got {name!r})")
        if not name:
            cls._invalid("name must be a non-empty string for UUID v5 (got '')")
        if len(name) > 100_000:
            cls._invalid(
                f"name exceeds the {100_000:,}-character limit "
                f"(got {len(name):,} characters)"
            )
        return name

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
