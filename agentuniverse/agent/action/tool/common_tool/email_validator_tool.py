#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: email_validator_tool.py

"""Email address validation / parsing / normalization tool, pure stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network utility agents can call before handing
an address to a sender, a CRM or a dedup step. Everything is computed
locally with ``re`` / ``str`` / ``ipaddress`` — **the tool never opens
a socket**: there are no DNS, MX, SMTP or disposable-domain lookups,
and a ``valid`` verdict therefore means *syntactically valid*, not
*deliverable* (deliverability checks are explicitly out of scope).

Three modes are supported:

* ``validate`` — a verdict plus a machine-readable reason for one
  address or a list of addresses. The syntax check is an RFC 5322-lite
  profile: a local part that is either a dot-atom (``atext`` characters
  separated by single dots) or a quoted string (spaces, ``@`` and
  escaped characters allowed inside the quotes), followed by ``@`` and
  a domain made of LDH labels — letters, digits and hyphens, 1-63
  characters per label, no leading or trailing hyphen — or an IP
  literal ``[127.0.0.1]`` / ``[IPv6:2001:db8::1]``. Length limits are
  enforced (64 characters for the local part, 254 for the whole
  addr-spec). Leading / trailing / consecutive dots are rejected in
  both parts. Single-label domains (``root@localhost``) and IP-literal
  domains are accepted but *flagged* in ``warnings`` because many
  public mail systems reject them.
* ``parse`` — decompose the address: local / domain split (quote
  aware, so ``"a@b"@example.com`` splits correctly), display-name
  extraction from ``Name <addr>`` forms, ``+tag`` detection for
  plus-addressed dot-atom locals, and classification of the local part
  as ``quoted`` or ``dot_atom`` and of the domain as ``dotted`` /
  ``single_label`` / ``ip_literal``.
* ``normalize`` — a canonical form: domain lowercased, redundant
  quoting stripped from quoted locals whose content is itself a valid
  dot-atom (``"john.doe"@x`` becomes ``john.doe@x``; quotes are kept
  when they carry meaning, e.g. spaces or ``@``), and the display name
  whitespace-folded and unquoted. Normalization is idempotent —
  normalizing twice returns the same string.

Parameter validation is strict and happens before any computation:
wrong types, an unknown mode, both (or neither) of ``address`` /
``addresses``, empty strings, a batch larger than 100 entries, or a
single input longer than 320 characters raise a ``ValueError`',
mirroring the other common tools. Verdicts that depend on the *content
being processed* (every syntax rule above) are returned as structured
per-item payloads — ``{"address", "valid", "reason", "message",
"warnings", "parts"}`` — so an agent can react without catching
exceptions. Batch calls additionally return ``summary`` counts.
"""

import ipaddress
import re
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# RFC 5322 atext — the dot-atom alphabet of an unquoted local part.
_ATEXT = re.compile(r"\A[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+\Z")
# Display-name form: "Anything <addr-spec>" (the input already stripped).
_ANGLE_ADDR = re.compile(r"\A(?P<name>[^<>]*)<(?P<inner>[^<>]*)>\Z")
_FOLD_WS = re.compile(r"\s+")


class EmailValidatorTool(Tool):
    """Email address validation / parsing / normalization (pure stdlib).

    Attributes:
        max_address_chars (int): Upper bound on a single input string;
            longer inputs are rejected before any work. The bound (320)
            deliberately sits above the RFC limit (254) so over-length
            addresses are still *reported* as invalid verdicts up to
            that size.
        max_batch_addresses (int): Upper bound on the number of
            addresses accepted in one batch call.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "email_validator_tool"
    description: str = (
        "Email validator tool — pure Python stdlib, no network access. "
        "mode='validate' checks one address or a list of addresses "
        "against an RFC 5322-lite syntax profile and returns a "
        "per-address verdict with reason, length limits (64 local / "
        "254 total), quoted-local support, dot and domain-label rules, "
        "and single-label / IP-literal flags; mode='parse' decomposes "
        "an address into local/domain, display name, +tag and local "
        "kind; mode='normalize' returns a canonical, idempotent form "
        "(lowercased domain, stripped redundant quotes, folded display "
        "name). Deliverability (DNS/MX/SMTP) is out of scope."
    )

    MODES: ClassVar[tuple] = ("validate", "parse", "normalize")

    # RFC limits enforced as *content* verdicts.
    MAX_LOCAL_CHARS: ClassVar[int] = 64
    MAX_ADDR_SPEC_CHARS: ClassVar[int] = 254
    MAX_LABEL_CHARS: ClassVar[int] = 63
    # Parameter-level caps (raise ValueError before any computation).
    max_address_chars: int = 320
    max_batch_addresses: int = 100

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any = None,
        address: Any = None,
        addresses: Any = None,
    ) -> Dict[str, Any]:
        """Run one email validation / parsing / normalization request.

        Args:
            mode (str): One of ``validate`` / ``parse`` / ``normalize``.
            address (str): A single address. Accepts bare addr-specs
                (``user@example.com``), quoted locals
                (``"john smith"@example.com``) and display-name forms
                (``Jane Doe <jane@example.com>``). Exactly one of
                ``address`` / ``addresses`` must be given.
            addresses (List[str]): A list of addresses (same grammar
                per item); the result carries per-item verdicts plus
                ``summary`` counts. At most 100 items.

        Returns:
            Dict[str, Any]: For a single address, one structured
            payload ``{"mode", "address", "valid", "reason",
            "message", "warnings", "parts", ...}``; for a batch,
            ``{"mode", "count", "results": [...], "summary":
            {"total", "valid", "invalid"}}``. The ``normalize`` mode
            adds ``"normalized"`` (``None`` when the input is invalid).

        Raises:
            ValueError: If any parameter is malformed (unknown mode,
                wrong types, both or neither of ``address`` /
                ``addresses``, empty items, oversized inputs or
                batches) — always before any computation.
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        single, batch = self._validate_carriers(address, addresses)
        if batch is not None:
            results = [self._process_one(mode, item) for item in batch]
            valid_count = sum(1 for item in results if item["valid"])
            return {
                "mode": mode,
                "count": len(results),
                "results": results,
                "summary": {
                    "total": len(results),
                    "valid": valid_count,
                    "invalid": len(results) - valid_count,
                },
            }
        return self._process_one(mode, single)

    # ------------------------------------------------------------------ #
    # Parameter validation (strict — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"email_validator_tool: {message}")

    @classmethod
    def _validate_carriers(
        cls, address: Any, addresses: Any
    ) -> Tuple[str, Optional[List[str]]]:
        """Validate the address/addresses carriers; return (single, batch)."""
        if address is not None and addresses is not None:
            cls._invalid(
                "pass either 'address' (single string) or 'addresses' "
                "(list of strings), not both"
            )
        if address is None and addresses is None:
            cls._invalid(
                "one of 'address' (single string) or 'addresses' "
                "(list of strings) is required"
            )
        if address is not None:
            return cls._validate_one_address(address, "address"), None
        if isinstance(addresses, (str, bytes)) or not isinstance(addresses, list):
            cls._invalid(
                f"addresses must be a list of strings (got {addresses!r})"
            )
        if not addresses:
            cls._invalid("addresses must be a non-empty list of strings")
        if len(addresses) > 100:
            cls._invalid(
                f"addresses exceeds the 100-item batch limit "
                f"(got {len(addresses)} items)"
            )
        return "", [
            cls._validate_one_address(item, f"addresses[{index}]")
            for index, item in enumerate(addresses)
        ]

    @classmethod
    def _validate_one_address(cls, item: Any, label: str) -> str:
        """Validate a single address carrier (type, emptiness, size)."""
        if not isinstance(item, str):
            cls._invalid(f"{label} must be a non-empty string (got {item!r})")
        if not item:
            cls._invalid(f"{label} must be a non-empty string (got '')")
        if len(item) > 320:
            cls._invalid(
                f"{label} exceeds the 320-character input limit "
                f"(got {len(item)} characters)"
            )
        return item

    # ------------------------------------------------------------------ #
    # Per-address pipeline (never raises; content errors become verdicts)
    # ------------------------------------------------------------------ #

    def _process_one(self, mode: str, raw: str) -> Dict[str, Any]:
        """Run the shared pipeline for one address and shape its payload."""
        verdict = self._analyze(raw)
        payload: Dict[str, Any] = {
            "mode": mode,
            "address": raw,
            "valid": verdict["valid"],
            "reason": verdict["reason"],
            "message": verdict["message"],
            "warnings": verdict["warnings"],
            "parts": verdict["parts"],
        }
        if mode == "normalize":
            payload["normalized"] = (
                self._normalized_form(verdict) if verdict["valid"] else None
            )
        return payload

    def _analyze(self, raw: str) -> Dict[str, Any]:
        """Produce the verdict dict for one raw address string."""
        trimmed = raw.strip()
        if not trimmed:
            return self._verdict(False, "empty_address",
                                 "the address is empty or only whitespace")
        display_name: Optional[str] = None
        addr_spec = trimmed
        if trimmed.endswith(">"):
            match = _ANGLE_ADDR.match(trimmed)
            if match:
                display_name = match.group("name").strip() or None
                addr_spec = match.group("inner").strip()
                if not addr_spec:
                    return self._verdict(False, "empty_address",
                                         "the angle-bracket address is empty")
        if len(addr_spec) > self.MAX_ADDR_SPEC_CHARS:
            return self._verdict(
                False, "address_too_long",
                f"the address exceeds the {self.MAX_ADDR_SPEC_CHARS}-character "
                f"limit (got {len(addr_spec)} characters)",
            )

        split = self._split_addr_spec(addr_spec)
        if isinstance(split, str):  # a reason code
            return self._verdict(False, split,
                                 self._reason_message(split, addr_spec))
        local, domain = split
        parts: Dict[str, Any] = {
            "display_name": display_name,
            "addr_spec": f"{local}@{domain}",
            "local": local,
            "local_kind": "quoted" if local.startswith('"') else "dot_atom",
            "tag": None,
            "local_base": None,
            "domain": domain,
            "domain_kind": None,
        }

        local_error = self._check_local(local)
        if local_error:
            return self._verdict(False, local_error,
                                 self._reason_message(local_error, local),
                                 parts=parts)

        domain_error, domain_kind, warnings = self._check_domain(domain)
        parts["domain_kind"] = domain_kind
        if domain_error:
            return self._verdict(False, domain_error,
                                 self._reason_message(domain_error, domain),
                                 parts=parts, warnings=warnings)
        if not local.startswith('"'):
            # Plus-addressing tag: only meaningful for dot-atom locals —
            # a '+' inside a quoted local part is a literal character.
            if "+" in local:
                base, tag = local.split("+", 1)
                parts["tag"], parts["local_base"] = tag, base
        return self._verdict(True, "ok", "the address is syntactically valid",
                             parts=parts, warnings=warnings)

    # ------------------------------------------------------------------ #
    # addr-spec splitting (quote aware)
    # ------------------------------------------------------------------ #

    @classmethod
    def _split_addr_spec(
        cls, addr_spec: str
    ) -> Tuple[str, str] | str:
        """Split ``local@domain`` respecting a quoted local part.

        Returns ``(local, domain)`` or a reason code (str) on failure.
        """
        if addr_spec.startswith('"'):
            # Find the closing quote of the quoted-string local part.
            index, length = 1, len(addr_spec)
            while index < length:
                char = addr_spec[index]
                if char == "\\":
                    index += 2  # skip the escaped character
                    continue
                if char == '"':
                    break
                index += 1
            else:
                # Unterminated quote (or a trailing escape ate the closer).
                return "invalid_quoted_local"
            if index + 1 >= length or addr_spec[index + 1] != "@":
                # Junk between the closing quote and any later '@' is a
                # quoted-local violation; with no '@' at all it is a
                # missing separator instead.
                if "@" in addr_spec[index + 1 :]:
                    return "invalid_quoted_local"
                return "missing_at"
            local, domain = addr_spec[: index + 1], addr_spec[index + 2 :]
        else:
            at = addr_spec.find("@")
            if at < 0:
                return "missing_at"
            local, domain = addr_spec[:at], addr_spec[at + 1 :]
        if "@" in domain:
            return "multiple_at"
        if not local:
            return "empty_local"
        if not domain:
            return "empty_domain"
        return local, domain

    # ------------------------------------------------------------------ #
    # Local part checks
    # ------------------------------------------------------------------ #

    @classmethod
    def _check_local(cls, local: str) -> Optional[str]:
        """Check the local part; return a reason code or None."""
        if len(local) > cls.MAX_LOCAL_CHARS:
            return "local_too_long"
        if local.startswith('"'):
            return cls._check_quoted_local(local)
        if local.startswith("."):
            return "leading_dot_in_local"
        if local.endswith("."):
            return "trailing_dot_in_local"
        if ".." in local:
            return "consecutive_dots_in_local"
        for segment in local.split("."):
            if not _ATEXT.match(segment):
                return "invalid_local_chars"
        return None

    @classmethod
    def _check_quoted_local(cls, local: str) -> Optional[str]:
        """Check a quoted-string local part (RFC 5322-lite).

        The whole local part must be one quoted string: printable ASCII
        (plus space) with ``"`` and ``\\`` only as escaped pairs, no
        control characters, and nothing after the closing quote.
        """
        index, length = 1, len(local)
        while index < length:
            char = local[index]
            if char == "\\":
                if index + 1 >= length or not (0x20 <= ord(local[index + 1]) <= 0x7E):
                    return "invalid_quoted_local"
                index += 2
                continue
            if char == '"':
                # Closing quote: nothing but the end may follow.
                if index != length - 1:
                    return "invalid_quoted_local"
                return None
            if not (0x20 <= ord(char) <= 0x7E):
                return "invalid_quoted_local"
            index += 1
        return "invalid_quoted_local"  # unterminated quote

    @classmethod
    def _unescape_quoted(cls, local: str) -> Optional[str]:
        """Return the unescaped content of a *valid* quoted local part."""
        if not (local.startswith('"') and local.endswith('"') and len(local) >= 2):
            return None
        content, index = [], 1
        while index < len(local) - 1:
            char = local[index]
            if char == "\\":
                index += 1
                if index >= len(local) - 1:
                    return None
                content.append(local[index])
            else:
                content.append(char)
            index += 1
        return "".join(content)

    # ------------------------------------------------------------------ #
    # Domain checks
    # ------------------------------------------------------------------ #

    @classmethod
    def _check_domain(
        cls, domain: str
    ) -> Tuple[Optional[str], Optional[str], List[str]]:
        """Check the domain; return (reason, domain_kind, warnings)."""
        if domain.startswith("["):
            if not domain.endswith("]"):
                return "invalid_ip_literal", None, []
            literal = domain[1:-1]
            ipv6 = literal.lower().startswith("ipv6:")
            body = literal[5:] if ipv6 else literal
            try:
                if ipv6:
                    ipaddress.IPv6Address(body)
                else:
                    ipaddress.IPv4Address(body)
            except ValueError:
                return "invalid_ip_literal", None, []
            return None, "ip_literal", ["ip_literal_domain"]

        labels = domain.split(".")
        for label in labels:
            if not label:
                return "empty_domain_label", None, []
            if len(label) > cls.MAX_LABEL_CHARS:
                return "label_too_long", None, []
            if not re.match(r"\A[A-Za-z0-9-]+\Z", label):
                return "invalid_label_chars", None, []
            if label.startswith("-") or label.endswith("-"):
                return "invalid_label_hyphens", None, []
        kind = "single_label" if len(labels) == 1 else "dotted"
        warnings = ["single_label_domain"] if kind == "single_label" else []
        return None, kind, warnings

    # ------------------------------------------------------------------ #
    # Normalization
    # ------------------------------------------------------------------ #

    @classmethod
    def _fold_display_name(cls, name: str) -> str:
        """Fold a display name: strip, unquote, collapse whitespace."""
        folded = name.strip()
        if len(folded) >= 2 and folded.startswith('"') and folded.endswith('"'):
            inner = folded[1:-1].strip()
            folded = inner.replace('\\"', '"').replace("\\\\", "\\")
        return _FOLD_WS.sub(" ", folded).strip()

    def _normalized_form(self, verdict: Dict[str, Any]) -> str:
        """Build the canonical form for a *valid* verdict."""
        parts = verdict["parts"]
        local = parts["local"]
        if parts["local_kind"] == "quoted":
            content = self._unescape_quoted(local)
            # Strip the quoting only when the content survives unquoted.
            if content is not None and self._check_local(content) is None:
                local = content
        domain = parts["domain"].lower()
        addr = f"{local}@{domain}"
        name = parts.get("display_name")
        return f"{self._fold_display_name(name)} <{addr}>" if name else addr

    # ------------------------------------------------------------------ #
    # Verdict / message helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _verdict(
        valid: bool,
        reason: str,
        message: str,
        parts: Optional[Dict[str, Any]] = None,
        warnings: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Build the internal verdict dict."""
        return {
            "valid": valid,
            "reason": reason,
            "message": str(message)[:300],
            "warnings": list(warnings or []),
            "parts": parts,
        }

    @classmethod
    def _reason_message(cls, reason: str, subject: str) -> str:
        """Map a reason code to a human-readable explanation."""
        shown = subject[:64]
        messages = {
            "missing_at": "the address contains no '@' separator",
            "multiple_at": "the address contains more than one '@' "
                "outside quotes",
            "empty_local": "the local part (before '@') is empty",
            "empty_domain": "the domain part (after '@') is empty",
            "local_too_long": f"the local part exceeds the "
                f"{cls.MAX_LOCAL_CHARS}-character limit",
            "leading_dot_in_local": "the local part must not start with a dot",
            "trailing_dot_in_local": "the local part must not end with a dot",
            "consecutive_dots_in_local": "the local part must not contain "
                "consecutive dots",
            "invalid_local_chars": "the local part contains characters "
                "outside the RFC 5322 atext set (letters, digits and "
                "!#$%&'*+/=?^_`{|}~-)",
            "invalid_quoted_local": "the quoted local part is malformed "
                "(unterminated quote, invalid escape, control character, "
                "or text after the closing quote)",
            "empty_domain_label": "the domain contains an empty label "
                "(leading, trailing or consecutive dots)",
            "label_too_long": "a domain label exceeds the "
                f"{cls.MAX_LABEL_CHARS}-character limit",
            "invalid_label_chars": "a domain label contains characters "
                "outside letters, digits and hyphens (an underscore or "
                "space, or a non-ASCII / IDN label — pass IDNs in "
                "xn-- A-label form)",
            "invalid_label_hyphens": "a domain label starts or ends with "
                "a hyphen",
            "invalid_ip_literal": "the bracketed domain is not a valid "
                "[IPv4] or [IPv6:...] address literal",
        }
        text = messages.get(reason, "the address is invalid")
        return f"{text} (got {shown!r})"
