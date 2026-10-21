#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: uuid_tool.py

"""UUID analysis tool built purely on the stdlib ``uuid`` module.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency inspector for UUID
identifiers: instead of *generating* UUIDs (the stdlib and the existing
generator / codec tools already cover that), this tool **validates and
decodes** an existing UUID — the analysis inverse of generation.

Five modes:

* ``parse`` — strict structural validation and RFC 4122 field decoding
  of one UUID given in hyphenated, ``urn:uuid:`` or braced ``{...}``
  form (any case). Returns the canonical lowercase form, the unsigned
  128-bit integer, the raw version nibble (0-15) with an
  assigned-range flag (versions 1-8 are defined by RFC 4122 / RFC
  9562; any other nibble is reported as-is and flagged), the variant
  (NCS / RFC 4122 / Microsoft / reserved) decoded from the top bits of
  ``clock_seq_hi_and_reserved``, and all six RFC 4122 fields
  (``time_low``, ``time_mid``, ``time_hi_and_version``,
  ``clock_seq_hi_and_reserved``, ``clock_seq_low``, ``node``) as both
  hexadecimal and unsigned integer values. Invalid inputs get
  ``valid: false`` plus a precise reason — missing or misplaced
  hyphens, wrong group lengths, non-hexadecimal characters reported
  with their 1-based position.
* ``v1_decode`` — recovers the creation data of a version 1
  (time-based) UUID: the 60-bit timestamp in 100-nanosecond intervals
  since the Gregorian epoch 1582-10-15T00:00:00 UTC, the equivalent
  UTC datetime (ISO 8601; sub-microsecond ticks are truncated), the
  14-bit clock sequence and the 48-bit node, with the multicast /
  local-administration bit analysis that tells a real MAC address from
  a random node. A structurally valid UUID of another version returns
  a structured ``not_version_1`` error payload.
* ``compare`` — orders two UUIDs by the RFC 4122 field-lexicographic
  rule: the unsigned fields are compared as
  ``(time_low, time_mid, time_hi_and_version,
  clock_seq_hi_and_reserved, clock_seq_low, node)`` in exactly that
  order — ``time_low`` is the *most significant* field because it is
  first in the spec's big-endian bit layout, which makes the rule
  equivalent to unsigned 128-bit integer comparison and **not** to
  sorting arbitrary strings. For canonical lowercase forms string
  order always agrees with field order; the raw input strings, when
  non-canonical (mixed case, ``urn:uuid:``, braces), may sort
  differently, so the result also reports both string orders and
  flags any divergence.
* ``namespace_check`` — brute-force verification of a version 3 or
  version 5 UUID against its supposed ``(namespace, name)`` origin:
  recomputes ``uuid3`` / ``uuid5`` with the stdlib for one of the
  well-known namespaces ``dns`` / ``url`` / ``oid`` / ``x500``
  (case-insensitive) or a custom namespace UUID and reports whether it
  reproduces the input exactly.
* ``batch_stats`` — version and variant histograms plus nil-UUID
  detection for a list of UUID strings, with per-entry reasons for the
  invalid ones (bounded to the first 20).

Input validation is strict and happens before any computation:
malformed parameters (unknown mode, wrong types, missing / empty /
oversized inputs — a UUID string is capped at 100 characters, a name
at 100,000 and a batch at 10,000 entries) raise a ``ValueError``,
mirroring the other common tools. Errors that depend on the *content
being analyzed* — a string that is not a parseable UUID where one is
required, a non-v1 UUID in ``v1_decode``, a non-v3/v5 UUID in
``namespace_check``, an unresolvable namespace — are returned as a
structured ``error`` payload (or as ``valid: false`` in ``parse`` /
``batch_stats``, where validity *is* the analysis) so an agent can
react without catching exceptions.
"""

import re
import uuid as uuid_module
from datetime import datetime, timedelta, timezone
from typing import Any, ClassVar, Dict, List, Tuple

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

_HEX_DIGITS = set("0123456789abcdefABCDEF")
# The strict canonical body layout: 8-4-4-4-12 hyphen-separated hex digits.
_CANONICAL_BODY = re.compile(
    r"\A[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}"
    r"-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\Z"
)
_HEX_BLOCK = re.compile(r"\A[0-9a-fA-F]+\Z")
# The Gregorian epoch of RFC 4122 timestamps (100-ns ticks origin).
_GREGORIAN_EPOCH = datetime(1582, 10, 15, tzinfo=timezone.utc)
_NIL_CANONICAL = "00000000-0000-0000-0000-000000000000"


class _MalformedUuid(Exception):
    """Internal carrier for a structural UUID defect and its reason."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


class UuidTool(Tool):
    """UUID validation and decoding tool built purely on the stdlib.

    Attributes:
        max_uuid_input_chars (int): Upper bound on any single UUID
            string input; longer inputs are rejected before any work.
        max_name_chars (int): Upper bound on the ``name`` string of the
            ``namespace_check`` mode.
        max_batch_size (int): Upper bound on the number of entries of
            the ``batch_stats`` mode.
        max_invalid_entries_reported (int): Number of invalid batch
            entries reported individually (the rest are only counted).
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "uuid_tool"
    description: str = (
        "UUID analysis tool — validate and decode existing UUIDs with the "
        "pure Python stdlib, no network required. Strict parsing with "
        "RFC 4122 field extraction (mode='parse'), version 1 timestamp / "
        "clock sequence / node MAC recovery (mode='v1_decode'), RFC 4122 "
        "field-lexicographic comparison of two UUIDs with a string-order "
        "note (mode='compare'), brute-force namespace+name verification "
        "of v3/v5 UUIDs (mode='namespace_check'), and version/variant "
        "histograms with nil detection for a batch (mode='batch_stats')."
    )

    MODES: ClassVar[tuple] = (
        "parse",
        "v1_decode",
        "compare",
        "namespace_check",
        "batch_stats",
    )
    # Version nibbles with a defined meaning in RFC 4122 / RFC 9562.
    KNOWN_VERSIONS: ClassVar[tuple] = (1, 2, 3, 4, 5, 6, 7, 8)
    # Well-known RFC 4122 namespaces, accepted case-insensitively.
    NAMESPACES: ClassVar[Dict[str, Any]] = {
        "dns": uuid_module.NAMESPACE_DNS,
        "url": uuid_module.NAMESPACE_URL,
        "oid": uuid_module.NAMESPACE_OID,
        "x500": uuid_module.NAMESPACE_X500,
    }
    # RFC 4122 field names, in bit-layout order, with their hex widths.
    FIELD_NAMES: ClassVar[tuple] = (
        "time_low",
        "time_mid",
        "time_hi_and_version",
        "clock_seq_hi_and_reserved",
        "clock_seq_low",
        "node",
    )
    FIELD_WIDTHS: ClassVar[tuple] = (8, 4, 4, 2, 2, 12)

    max_uuid_input_chars: int = 100
    max_name_chars: int = 100_000
    max_batch_size: int = 10_000
    max_invalid_entries_reported: int = 20

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any = None,
        uuid: Any = None,
        uuid_a: Any = None,
        uuid_b: Any = None,
        namespace: Any = None,
        name: Any = None,
        batch: Any = None,
    ) -> Dict[str, Any]:
        """Run one UUID analysis.

        Args:
            mode (str): One of ``parse`` / ``v1_decode`` / ``compare`` /
                ``namespace_check`` / ``batch_stats``.
            uuid (str): The UUID to analyze — required for the ``parse``,
                ``v1_decode`` and ``namespace_check`` modes. Accepts the
                hyphenated form, the ``urn:uuid:`` form and the braced
                ``{...}`` form, in any case.
            uuid_a (str): First UUID of the ``compare`` mode.
            uuid_b (str): Second UUID of the ``compare`` mode.
            namespace (str): ``namespace_check`` only — one of the
                well-known labels ``dns`` / ``url`` / ``oid`` / ``x500``
                (case-insensitive) or a custom namespace as a UUID hex
                string.
            name (str): ``namespace_check`` only — the original name the
                UUID is supposed to encode.
            batch (list[str]): ``batch_stats`` only — the list of UUID
                strings to profile.

        Returns:
            Dict[str, Any]: The analysis result (always including the
                call context) — for ``parse`` a ``valid`` flag with the
                decoded fields, for the other modes the mode-specific
                payload — or a structured ``error`` payload for
                content-level failures (unparseable UUID where one is
                required, non-v1 UUID in ``v1_decode``, non-v3/v5 UUID
                or unresolvable namespace in ``namespace_check``).

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        if mode == "parse":
            return self._run_parse(self._validate_uuid_string(uuid, "uuid"))
        if mode == "v1_decode":
            return self._run_v1_decode(
                self._validate_uuid_string(uuid, "uuid")
            )
        if mode == "compare":
            uuid_a = self._validate_uuid_string(uuid_a, "uuid_a")
            uuid_b = self._validate_uuid_string(uuid_b, "uuid_b")
            return self._run_compare(uuid_a, uuid_b)
        if mode == "namespace_check":
            clean_uuid = self._validate_uuid_string(uuid, "uuid")
            clean_name = self._validate_name(name)
            clean_namespace = self._validate_namespace_param(namespace)
            return self._run_namespace_check(
                clean_uuid, clean_namespace, clean_name
            )
        return self._run_batch_stats(self._validate_batch(batch))

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"uuid_tool: {message}")

    def _validate_uuid_string(self, value: Any, label: str) -> str:
        """Validate a single UUID string parameter."""
        if value is None or isinstance(value, bool) or not isinstance(value, str):
            self._invalid(
                f"{label} must be a non-empty UUID string "
                f"of at most {self.max_uuid_input_chars} characters "
                f"(got {value!r})"
            )
        if not value.strip():
            self._invalid(f"{label} must be a non-empty UUID string (got {value!r})")
        if len(value) > self.max_uuid_input_chars:
            self._invalid(
                f"{label} exceeds the {self.max_uuid_input_chars}-character "
                f"limit (got {len(value)} characters)"
            )
        return value

    def _validate_name(self, name: Any) -> str:
        """Validate the ``namespace_check`` name parameter."""
        if name is None or isinstance(name, bool) or not isinstance(name, str):
            self._invalid(
                f"name must be a non-empty string for namespace_check "
                f"(got {name!r})"
            )
        if not name:
            self._invalid("name must be a non-empty string for namespace_check (got '')")
        if len(name) > self.max_name_chars:
            self._invalid(
                f"name exceeds the {self.max_name_chars:,}-character limit "
                f"(got {len(name):,} characters)"
            )
        return name

    def _validate_namespace_param(self, namespace: Any) -> str:
        """Validate the namespace parameter type and length only."""
        if (
            namespace is None
            or isinstance(namespace, bool)
            or not isinstance(namespace, str)
        ):
            self._invalid(
                "namespace is required for namespace_check and must be one "
                f"of: {', '.join(sorted(self.NAMESPACES))} (case-insensitive) "
                "or a UUID hex string "
                f"(got {namespace!r})"
            )
        if not namespace.strip():
            self._invalid(
                "namespace must be a non-empty label or UUID hex string "
                f"(got {namespace!r})"
            )
        if len(namespace) > self.max_uuid_input_chars:
            self._invalid(
                f"namespace exceeds the {self.max_uuid_input_chars}-character "
                f"limit (got {len(namespace)} characters)"
            )
        return namespace

    def _validate_batch(self, batch: Any) -> List[str]:
        """Validate the ``batch_stats`` list parameter."""
        if isinstance(batch, bool) or not isinstance(batch, (list, tuple)):
            self._invalid(
                f"batch must be a list of UUID strings (got {batch!r})"
            )
        if len(batch) == 0:
            self._invalid("batch must contain at least one UUID string")
        if len(batch) > self.max_batch_size:
            self._invalid(
                f"batch exceeds the {self.max_batch_size:,}-entry limit "
                f"(got {len(batch):,} entries)"
            )
        for index, entry in enumerate(batch):
            if entry is None or isinstance(entry, bool) or not isinstance(entry, str):
                self._invalid(
                    f"batch entry at index {index} must be a string "
                    f"(got {entry!r})"
                )
            if len(entry) > self.max_uuid_input_chars:
                self._invalid(
                    f"batch entry at index {index} exceeds the "
                    f"{self.max_uuid_input_chars}-character limit "
                    f"(got {len(entry)} characters)"
                )
        return list(batch)

    # ------------------------------------------------------------------ #
    # Structural UUID analysis (shared by every mode)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _body_defect_reason(body: str) -> str:
        """Diagnose why a UUID body does not match the 8-4-4-4-12 layout."""
        if not body:
            return "the UUID body is empty (nothing between the braces/prefix)"
        groups = body.split("-")
        if len(groups) == 1 and len(body) == 32 and _HEX_BLOCK.match(body):
            return (
                "hyphens are missing: a bare 32-digit hex block is not "
                "accepted — expected 5 hyphen-separated groups of "
                "8-4-4-4-12 hexadecimal digits"
            )
        if len(groups) != 5:
            lengths = [len(group) for group in groups]
            return (
                "expected 5 hyphen-separated groups of 8-4-4-4-12 "
                f"hexadecimal digits, got {len(groups)} group(s) with "
                f"lengths {lengths}"
            )
        widths = (8, 4, 4, 4, 12)
        # The five hyphen-separated groups of the text form (the fourth
        # group is the combined clock_seq_hi_and_reserved + clock_seq_low).
        names = ("time_low", "time_mid", "time_hi_and_version", "clock_seq", "node")
        for index, (group, width) in enumerate(zip(groups, widths)):
            if len(group) != width:
                return (
                    f"group {index + 1} ({names[index]}) has {len(group)} "
                    f"character(s); expected exactly {width} hexadecimal "
                    "digits"
                )
        # Group lengths are correct, so the hyphens sit at their structural
        # positions and any remaining defect is a non-hexadecimal character.
        for position, char in enumerate(body):
            if char != "-" and char not in _HEX_DIGITS:
                return (
                    f"character {char!r} at position {position + 1} (1-based, "
                    "within the UUID body after any 'urn:uuid:' prefix and "
                    "braces) is not a hexadecimal digit"
                )
        return "not a valid 8-4-4-4-12 hyphenated UUID"

    @staticmethod
    def _variant_label(clock_seq_hi_reserved: int) -> str:
        """Decode the variant from the top bits of clock_seq_hi_reserved."""
        bits = clock_seq_hi_reserved
        if bits & 0b1000_0000 == 0b0000_0000:
            return "NCS"
        if bits & 0b1100_0000 == 0b1000_0000:
            return "RFC 4122"
        if bits & 0b1110_0000 == 0b1100_0000:
            return "Microsoft"
        return "reserved"

    @classmethod
    def _analyze(cls, raw: str) -> Dict[str, Any]:
        """Normalize and decode one UUID string.

        Returns the canonical form, the detected input form, the raw
        version nibble, the variant label and the six RFC 4122 fields.

        Raises:
            _MalformedUuid: If the string is not a structurally valid
                UUID, carrying a precise reason.
        """
        text = raw.strip()
        form = "hyphenated"
        lowered = text.lower()
        if lowered.startswith("urn:"):
            if not lowered.startswith("urn:uuid:"):
                raise _MalformedUuid(
                    "input starts with 'urn:' but is not a 'urn:uuid:' "
                    "prefixed UUID (only the urn:uuid: form is accepted)"
                )
            text = text[len("urn:uuid:"):]
            form = "urn"
        if text.startswith("{") or text.endswith("}"):
            if not (text.startswith("{") and text.endswith("}") and len(text) >= 2):
                raise _MalformedUuid(
                    "braces are unbalanced: a braced UUID must be exactly "
                    "'{<uuid>}'"
                )
            text = text[1:-1]
            form = "braced" if form == "hyphenated" else "urn+braced"
        if not _CANONICAL_BODY.match(text):
            raise _MalformedUuid(cls._body_defect_reason(text))

        parsed = uuid_module.UUID(text)
        values = (
            parsed.time_low,
            parsed.time_mid,
            parsed.time_hi_version,
            parsed.clock_seq_hi_variant,
            parsed.clock_seq_low,
            parsed.node,
        )
        fields: Dict[str, Dict[str, Any]] = {
            field_name: {
                "hex": format(value, f"0{width}x"),
                "int": value,
            }
            for field_name, width, value in zip(
                cls.FIELD_NAMES, cls.FIELD_WIDTHS, values
            )
        }
        version = parsed.time_hi_version >> 12
        return {
            "canonical": str(parsed),
            "form": form,
            "int": parsed.int,
            "version": version,
            "version_known": version in cls.KNOWN_VERSIONS,
            "variant": cls._variant_label(parsed.clock_seq_hi_variant),
            "fields": fields,
        }

    # ------------------------------------------------------------------ #
    # parse mode
    # ------------------------------------------------------------------ #

    def _run_parse(self, raw: str) -> Dict[str, Any]:
        """Strictly validate one UUID and decode its RFC 4122 fields."""
        try:
            decoded = self._analyze(raw)
        except _MalformedUuid as exc:
            return {
                "mode": "parse",
                "input": raw,
                "valid": False,
                "reason": exc.reason,
            }
        result: Dict[str, Any] = {"mode": "parse", "input": raw, "valid": True}
        result.update(decoded)
        if not decoded["version_known"]:
            result["version_note"] = (
                f"the version nibble is {decoded['version']:x}, outside the "
                "assigned range 1-8 (RFC 4122 / RFC 9562); it is reported "
                "as-is with known=false"
            )
        return result

    # ------------------------------------------------------------------ #
    # v1_decode mode
    # ------------------------------------------------------------------ #

    def _run_v1_decode(self, raw: str) -> Dict[str, Any]:
        """Recover the timestamp, clock sequence and node of a v1 UUID."""
        context: Dict[str, Any] = {"mode": "v1_decode"}
        try:
            decoded = self._analyze(raw)
        except _MalformedUuid as exc:
            return self._error_result(
                context,
                error_type="invalid_uuid",
                message=f"input is not a valid UUID: {exc.reason}",
            )
        if decoded["version"] != 1:
            return self._error_result(
                context,
                error_type="not_version_1",
                message=(
                    "v1_decode requires a version 1 (time-based) UUID; this "
                    f"UUID declares version {decoded['version']}"
                ),
            )
        parsed = uuid_module.UUID(decoded["canonical"])
        timestamp = parsed.time
        moment = _GREGORIAN_EPOCH + timedelta(microseconds=timestamp // 10)
        node = parsed.node
        multicast_bit = bool(node & 0x010000000000)
        local_admin_bit = bool(node & 0x020000000000)
        if multicast_bit:
            node_note = (
                "multicast bit set — per RFC 4122 section 4.5 the node is a "
                "random/pseudo-random identifier, not a hardware MAC address"
            )
        elif local_admin_bit:
            node_note = (
                "multicast bit clear but local-administration bit set — "
                "consistent with a locally administered (virtual) MAC, not a "
                "globally unique hardware address"
            )
        else:
            node_note = (
                "multicast and local-administration bits clear — consistent "
                "with a globally unique IEEE 802 hardware MAC address"
            )
        return {
            **context,
            "uuid": decoded["canonical"],
            "version": 1,
            "timestamp": timestamp,
            "datetime": moment.isoformat(),
            "sub_microsecond_remainder_100ns": timestamp % 10,
            "clock_sequence": parsed.clock_seq,
            "node": {"int": node, "hex": format(node, "012x")},
            "multicast_bit": multicast_bit,
            "local_administration_bit": local_admin_bit,
            "node_note": node_note,
        }

    # ------------------------------------------------------------------ #
    # compare mode
    # ------------------------------------------------------------------ #

    @staticmethod
    def _order_symbol(left: Any, right: Any) -> str:
        """Map a comparison to the '<' / '=' / '>' symbol."""
        if left < right:
            return "<"
        if left > right:
            return ">"
        return "="

    def _run_compare(self, uuid_a: str, uuid_b: str) -> Dict[str, Any]:
        """Order two UUIDs by the RFC 4122 field-lexicographic rule."""
        context: Dict[str, Any] = {"mode": "compare"}
        try:
            decoded_a = self._analyze(uuid_a)
        except _MalformedUuid as exc:
            return self._error_result(
                context,
                error_type="invalid_uuid",
                message=f"uuid_a is not a valid UUID: {exc.reason}",
            )
        try:
            decoded_b = self._analyze(uuid_b)
        except _MalformedUuid as exc:
            return self._error_result(
                context,
                error_type="invalid_uuid",
                message=f"uuid_b is not a valid UUID: {exc.reason}",
            )

        def field_tuple(decoded: Dict[str, Any]) -> Tuple[int, ...]:
            return tuple(
                decoded["fields"][name]["int"] for name in self.FIELD_NAMES
            )

        order = self._order_symbol(field_tuple(decoded_a), field_tuple(decoded_b))
        canonical_order = self._order_symbol(
            decoded_a["canonical"], decoded_b["canonical"]
        )
        input_order = self._order_symbol(uuid_a, uuid_b)
        result = {
            **context,
            "uuid_a": decoded_a["canonical"],
            "uuid_b": decoded_b["canonical"],
            "order": order,
            "order_basis": (
                "RFC 4122 field-lexicographic order — unsigned comparison "
                "of (time_low, time_mid, time_hi_and_version, "
                "clock_seq_hi_and_reserved, clock_seq_low, node) in that "
                "order; time_low is the most significant field per the "
                "spec's big-endian bit layout (equivalent to unsigned "
                "128-bit integer comparison), not general string sorting"
            ),
            "canonical_string_order": canonical_order,
            "input_string_order": input_order,
        }
        if input_order != order:
            result["string_order_divergence"] = True
            result["string_order_note"] = (
                "the raw input strings sort differently from the UUID "
                "field order because they are not in canonical lowercase "
                "form (mixed case, 'urn:uuid:' prefix and/or braces change "
                "lexicographic order); canonical-form string order always "
                "equals field order"
            )
        else:
            result["string_order_divergence"] = False
        return result

    # ------------------------------------------------------------------ #
    # namespace_check mode
    # ------------------------------------------------------------------ #

    def _run_namespace_check(
        self, raw: str, namespace: str, name: str
    ) -> Dict[str, Any]:
        """Brute-force verify a v3/v5 UUID against (namespace, name)."""
        context: Dict[str, Any] = {"mode": "namespace_check"}
        try:
            decoded = self._analyze(raw)
        except _MalformedUuid as exc:
            return self._error_result(
                context,
                error_type="invalid_uuid",
                message=f"input is not a valid UUID: {exc.reason}",
            )
        if decoded["version"] not in (3, 5):
            return self._error_result(
                context,
                error_type="not_version_3_or_5",
                message=(
                    "namespace_check requires a version 3 (MD5) or version 5 "
                    "(SHA-1) name-based UUID; this UUID declares version "
                    f"{decoded['version']}"
                ),
            )
        label = namespace.strip().lower()
        if label in self.NAMESPACES:
            namespace_value = self.NAMESPACES[label]
            namespace_echo: str = label
        else:
            try:
                namespace_value = uuid_module.UUID(namespace.strip())
            except (ValueError, AttributeError, TypeError):
                return self._error_result(
                    context,
                    error_type="invalid_namespace",
                    message=(
                        "namespace must be one of: "
                        f"{', '.join(sorted(self.NAMESPACES))} "
                        "(case-insensitive) or a custom namespace given as a "
                        "UUID hex string, e.g. "
                        "'6ba7b810-9dad-11d1-80b4-00c04fd430c8' "
                        f"(got {namespace[:64]!r})"
                    ),
                )
            namespace_echo = str(namespace_value)
        if decoded["version"] == 3:
            expected = uuid_module.uuid3(namespace_value, name)
        else:
            expected = uuid_module.uuid5(namespace_value, name)
        return {
            **context,
            "uuid": decoded["canonical"],
            "version": decoded["version"],
            "namespace": namespace_echo,
            "name": name,
            "expected": str(expected),
            "match": str(expected) == decoded["canonical"],
        }

    # ------------------------------------------------------------------ #
    # batch_stats mode
    # ------------------------------------------------------------------ #

    def _run_batch_stats(self, batch: List[str]) -> Dict[str, Any]:
        """Profile a batch of UUID strings."""
        version_histogram: Dict[str, int] = {}
        variant_histogram: Dict[str, int] = {}
        invalid_entries: List[Dict[str, Any]] = []
        invalid_count = 0
        valid_count = 0
        nil_count = 0
        for index, entry in enumerate(batch):
            try:
                decoded = self._analyze(entry)
            except _MalformedUuid as exc:
                invalid_count += 1
                if len(invalid_entries) < self.max_invalid_entries_reported:
                    invalid_entries.append(
                        {
                            "index": index,
                            "input": entry,
                            "reason": exc.reason,
                        }
                    )
                continue
            valid_count += 1
            version_key = str(decoded["version"])
            version_histogram[version_key] = (
                version_histogram.get(version_key, 0) + 1
            )
            variant_histogram[decoded["variant"]] = (
                variant_histogram.get(decoded["variant"], 0) + 1
            )
            if decoded["canonical"] == _NIL_CANONICAL:
                nil_count += 1
        unknown_version_count = sum(
            count
            for key, count in version_histogram.items()
            if int(key) not in self.KNOWN_VERSIONS
        )
        return {
            "mode": "batch_stats",
            "total": len(batch),
            "valid_count": valid_count,
            "invalid_count": invalid_count,
            "invalid_entries": invalid_entries,
            "invalid_entries_truncated": (
                invalid_count > len(invalid_entries)
            ),
            "version_histogram": version_histogram,
            "unknown_version_count": unknown_version_count,
            "variant_histogram": variant_histogram,
            "nil_count": nil_count,
            "all_nil": valid_count > 0 and nil_count == valid_count,
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
