#!/usr/bin/env python3
"""Hash and crypto utility tool.

Provides hash (md5/sha1/sha256/sha512), HMAC, base64 encode/decode, and
hex encode/decode operations. All using Python's standard library — zero
third-party dependency.

Addresses #252 (more tools).
"""

# ruff: noqa: TRY003, TRY004

import base64
import hashlib
import hmac
import logging
from typing import Any

from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger

logger = logging.getLogger(__name__)

_HASH_ALGOS = {"md5", "sha1", "sha256", "sha512"}
_ENCODE_FORMATS = {"base64", "hex"}


class HashCryptoTool(Tool):
    """Hash, HMAC, and encoding/decoding utility tool.

    All operations use Python's standard ``hashlib``, ``hmac``, and
    ``base64`` modules — zero third-party dependency.
    """

    def execute(self, mode: str, text: str = "", algorithm: str = "sha256",
                key: str = "", encoding: str = "base64",
                **kwargs) -> dict:
        try:
            op = self._normalize_mode(mode)
            if op == "hash":
                return self._hash(text, algorithm)
            if op == "hmac":
                return self._hmac(text, key, algorithm)
            if op == "encode":
                return self._encode(text, encoding)
            if op == "decode":
                return self._decode(text, encoding)
            return self._error("validation_error", f"Unknown mode: {mode}")
        except (TypeError, ValueError) as exc:
            return self._error("validation_error", str(exc))
        except Exception as exc:
            return self._error("operation_error", str(exc))

    @staticmethod
    def _normalize_mode(mode: str) -> str:
        if not isinstance(mode, str):
            raise TypeError("mode must be a string")
        normalized = mode.strip().lower()
        allowed = {"hash", "hmac", "encode", "decode"}
        if normalized not in allowed:
            raise ValueError(f"mode must be one of: {', '.join(sorted(allowed))}")
        return normalized

    @staticmethod
    def _error(error_type: str, message: str) -> dict:
        return {"status": "error", "error_type": error_type, "error": message}

    @staticmethod
    def _ok(**kwargs) -> dict:
        return {"status": "success", **kwargs}

    def _hash(self, text: str, algorithm: str) -> dict:
        if not isinstance(text, str):
            raise ValueError("text must be a string")
        algorithm = (algorithm or "sha256").lower()
        if algorithm not in _HASH_ALGOS:
            raise ValueError(
                f"algorithm must be one of: {', '.join(sorted(_HASH_ALGOS))}")
        data = text.encode("utf-8")
        digest = hashlib.new(algorithm, data).hexdigest()
        return self._ok(mode="hash", algorithm=algorithm,
                        input_length=len(text), digest=digest)

    def _hmac(self, text: str, key: str, algorithm: str) -> dict:
        if not isinstance(text, str) or not isinstance(key, str):
            raise ValueError("text and key must be strings")
        if not key:
            raise ValueError("key is required for HMAC")
        algorithm = (algorithm or "sha256").lower()
        if algorithm not in _HASH_ALGOS:
            raise ValueError(
                f"algorithm must be one of: {', '.join(sorted(_HASH_ALGOS))}")
        digest = hmac.new(
            key.encode("utf-8"), text.encode("utf-8"), algorithm
        ).hexdigest()
        return self._ok(mode="hmac", algorithm=algorithm, digest=digest)

    def _encode(self, text: str, encoding: str) -> dict:
        if not isinstance(text, str):
            raise ValueError("text must be a string")
        encoding = (encoding or "base64").lower()
        if encoding not in _ENCODE_FORMATS:
            raise ValueError(
                f"encoding must be one of: {', '.join(sorted(_ENCODE_FORMATS))}")
        data = text.encode("utf-8")
        if encoding == "base64":
            encoded = base64.b64encode(data).decode("ascii")
        else:
            encoded = data.hex()
        return self._ok(mode="encode", encoding=encoding, encoded=encoded)

    def _decode(self, text: str, encoding: str) -> dict:
        if not isinstance(text, str) or not text:
            raise ValueError("text must be a non-empty string")
        encoding = (encoding or "base64").lower()
        if encoding not in _ENCODE_FORMATS:
            raise ValueError(
                f"encoding must be one of: {', '.join(sorted(_ENCODE_FORMATS))}")
        try:
            if encoding == "base64":
                decoded = base64.b64decode(text).decode("utf-8")
            else:
                decoded = bytes.fromhex(text).decode("utf-8")
        except (ValueError, UnicodeDecodeError) as exc:
            raise ValueError(
                f"Failed to decode {encoding!r} input: {exc}") from exc
        return self._ok(mode="decode", encoding=encoding, decoded=decoded)

    def _initialize_by_component_configer(self, configer: ComponentConfiger) \
            -> "HashCryptoTool":
        super()._initialize_by_component_configer(configer)
        return self
