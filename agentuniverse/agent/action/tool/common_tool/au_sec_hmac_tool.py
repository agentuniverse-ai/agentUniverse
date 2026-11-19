#!/usr/bin/env python3
"""Bounded, deterministic, constant-time HMAC-SHA256 sign/verify/compare for agents (au-sec series #1)."""

# Public execute() converts validation exceptions into structured tool errors.
# ruff: noqa: TRY003

import hmac
from typing import Any, ClassVar

from agentuniverse.agent.action.tool.tool import Tool


class AuSecHmacTool(Tool):
    """Sign, verify, compare, and introspect messages with bounded, constant-time HMAC-SHA256."""

    max_key_bytes: int = 4096
    max_message_bytes: int = 1_048_576
    max_signature_bytes: int = 4096

    _ACTIONS: ClassVar[tuple[str, ...]] = ("sign", "verify", "compare", "info")

    def _bound(self, what: str, raw: bytes, cap: int) -> bytes:
        if len(raw) > cap:
            raise ValueError(f"{what} is {len(raw)} bytes, exceeds {cap}: {raw[:32]!r}")
        return raw

    def _need(self, what: str, value: Any) -> Any:
        if value is None:
            raise ValueError(f"{what} is required, got: {value!r}")
        return value

    def execute(
        self,
        action: str = "sign",
        key: str | None = None,
        message: str | None = None,
        signature: str | None = None,
        other: str | None = None,
    ) -> dict[str, Any]:
        try:
            if action not in self._ACTIONS:
                raise ValueError(f"unknown action: {action!r} (expected one of {self._ACTIONS})")
            if action == "info":
                return {
                    "action": "info",
                    "actions": list(self._ACTIONS),
                    "algorithm": "hmac-sha256",
                    "compare": "constant-time",
                    "bounds": {
                        "max_key_bytes": self.max_key_bytes,
                        "max_message_bytes": self.max_message_bytes,
                        "max_signature_bytes": self.max_signature_bytes,
                    },
                }
            if action == "compare":
                sig = self._bound("signature", self._need("signature", signature).encode("utf-8"), self.max_signature_bytes)
                oth = self._bound("other", self._need("other", other).encode("utf-8"), self.max_signature_bytes)
                return {"action": "compare", "equal": hmac.compare_digest(sig, oth)}
            key_raw = self._bound("key", self._need("key", key).encode("utf-8"), self.max_key_bytes)
            if action == "sign":
                msg = self._bound("message", self._need("message", message).encode("utf-8"), self.max_message_bytes)
                return {"action": "sign", "digest": hmac.new(key_raw, msg, "sha256").hexdigest(), "truncated": False}
            if action == "verify":
                msg = self._bound("message", self._need("message", message).encode("utf-8"), self.max_message_bytes)
                sig = self._bound("signature", self._need("signature", signature).encode("utf-8"), self.max_signature_bytes)
                want = hmac.new(key_raw, msg, "sha256").hexdigest().encode("utf-8")
                return {"action": "verify", "valid": hmac.compare_digest(want, sig)}
            raise ValueError(f"unreachable action: {action!r}")
        except (TypeError, AttributeError) as error:
            raise ValueError(f"malformed hmac input: {error!r}") from error
