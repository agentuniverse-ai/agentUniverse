#!/usr/bin/env python3

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: cidr_calculator_tool.py
# ruff: noqa: TRY003

"""IPv4 / IPv6 network calculator tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency network math tool
agents can call for CIDR plumbing: subnet planning, address range
checks, or IP classification.

The tool is a thin, strictly-validated façade over the standard
library ``ipaddress`` module and supports six deterministic modes:

* ``info`` — full network report for a CIDR (``"192.168.1.0/24"``) or
  an address plus a separate ``prefix`` argument: normalized network,
  version, prefix length, netmask, wildcard mask and broadcast address
  (IPv4 only — IPv6 has no broadcast or wildcard concepts), first /
  last address, network size, and the first / last usable host plus
  the usable host count (IPv4 only; ``/31`` and ``/32`` count every
  address as usable per RFC 3021, matching ``ipaddress``'s own
  ``hosts()`` semantics).
* ``contains`` — a network plus a list of addresses; every address
  gets its own verdict (contained, not contained, or invalid token),
  with normalized spellings and summary counts.
* ``subnet`` — split a network into equal subnets of a longer
  ``new_prefix``; returns the total count and the first subnets, with
  the output list capped (``max_subnets``) and a ``truncated`` flag
  when the count exceeds the cap.
* ``supernet`` — the enclosing network of a shorter ``new_prefix``.
* ``ip_info`` — a single address: version, canonical (compressed) and
  exploded textual forms, integer value, the private / global /
  loopback / link-local / multicast / reserved classifications, and a
  single deterministic ``type`` label.
* ``summarize`` — collapse a list of addresses and/or CIDRs into the
  minimal set of merged summary ranges; adjacent and overlapping
  inputs are merged, IPv4 and IPv6 inputs are summarized in separate
  groups (IPv4 ranges first).

Input validation is strict and happens before any computation:
malformed parameters (unknown mode, wrong types, missing required
arguments, non-integer prefixes, empty or non-list inputs, oversized
input lists) raise a ``ValueError``, mirroring the other common tools.
Errors that depend on the *content being processed* — a bad address,
a bad network, a prefix outside the address family's range, a
``new_prefix`` that is not a strict refinement of the input network,
and a network whose host bits are set — are returned as a structured
``error`` payload (including the offending token) so an agent can
react without catching exceptions. For a network with host bits set
(e.g. ``192.168.1.5/24``) the payload reports both interpretations:
the strict network as written and the normalized (host bits masked)
network.
"""

import ipaddress
from itertools import islice
from typing import Any, ClassVar

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool


class CidrCalculatorTool(Tool):
    """IPv4 / IPv6 network calculator built purely on the stdlib.

    Attributes:
        max_input_items (int): Upper bound on the number of items
            accepted by the ``contains`` / ``summarize`` list inputs.
        max_subnets (int): Cap on how many subnets the ``subnet`` mode
            returns in one response (the total count is always
            reported; a ``truncated`` flag marks capped output).
    """

    model_config = ConfigDict(arbitrary_types_allowed=True, protected_namespaces=())

    name: str = "cidr_calculator_tool"
    description: str = (
        "CIDR / subnet calculator tool — pure Python stdlib ipaddress "
        "module, no network required. Network report for a CIDR or "
        "address+prefix (mode='info': netmask, wildcard, broadcast, "
        "host range, size), membership check of addresses in a network "
        "(mode='contains'), split into subnets with capped output "
        "(mode='subnet'), enclosing supernet (mode='supernet'), single "
        "address classification and forms (mode='ip_info'), and "
        "merging of addresses/CIDRs into summary ranges "
        "(mode='summarize'). IPv4 and IPv6 are both supported."
    )

    MODES: ClassVar[tuple] = (
        "info",
        "contains",
        "subnet",
        "supernet",
        "ip_info",
        "summarize",
    )

    max_input_items: int = 256
    max_subnets: int = 256

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        network: Any = None,
        address: Any = None,
        prefix: Any = None,
        new_prefix: Any = None,
        addresses: Any = None,
        networks: Any = None,
    ) -> dict[str, Any]:
        """Run one network calculation.

        Args:
            mode (str): One of ``info`` / ``contains`` / ``subnet`` /
                ``supernet`` / ``ip_info`` / ``summarize``.
            network (str): The network for the ``info``, ``contains``,
                ``subnet`` and ``supernet`` modes — either a CIDR
                string (``"192.168.1.0/24"``) or a bare address to
                combine with the ``prefix`` argument.
            address (str): The single address for the ``ip_info``
                mode.
            prefix (int | str): The prefix length when ``network`` is
                a bare address; ``0``-``32`` for IPv4, ``0``-``128``
                for IPv6. Without it a bare address is treated as a
                host network (``/32`` or ``/128``).
            new_prefix (int | str): The target prefix length —
                strictly longer than the input prefix for ``subnet``,
                strictly shorter for ``supernet``.
            addresses (List[str]): Addresses to test, for the
                ``contains`` mode.
            networks (List[str]): Addresses / CIDRs to merge, for the
                ``summarize`` mode.

        Returns:
            Dict[str, Any]: The calculation result (always carrying
                the call context) or a structured ``error`` payload
                for content-level failures (invalid address, invalid
                network, invalid prefix, host bits set).

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})")
        if mode == "ip_info":
            return self._run_ip_info(address)
        if mode == "summarize":
            return self._run_summarize(networks)

        token = self._validate_str_param(network, "network")
        clean_prefix = self._validate_int_param(prefix, "prefix")
        context: dict[str, Any] = {"mode": mode}
        if mode == "info":
            return self._run_info(context, token, clean_prefix)
        if mode == "contains":
            return self._run_contains(context, token, clean_prefix, addresses)

        clean_new_prefix = self._validate_int_param(new_prefix, "new_prefix")
        if clean_new_prefix is None:
            self._invalid(f"new_prefix is required for the {mode} mode (got None)")
        if mode == "subnet":
            return self._run_subnet(context, token, clean_prefix, clean_new_prefix)
        return self._run_supernet(context, token, clean_prefix, clean_new_prefix)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"cidr_calculator_tool: {message}")

    @classmethod
    def _validate_str_param(cls, value: Any, label: str) -> str:
        """Validate a required string parameter, returned stripped."""
        if value is None or isinstance(value, bool) or not isinstance(value, str):
            cls._invalid(f"{label} must be a non-empty string (got {value!r})")
        token = value.strip()
        if not token:
            cls._invalid(f"{label} must be a non-empty string (got {value!r})")
        return token

    @classmethod
    def _validate_int_param(cls, value: Any, label: str) -> int | None:
        """Validate an optional integer parameter (``int`` or decimal
        string; ``bool`` is rejected explicitly)."""
        if value is None:
            return None
        if isinstance(value, bool):
            cls._invalid(f"{label} must be an integer (got {value!r})")
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.strip().lstrip("-").isdigit():
            return int(value.strip())
        cls._invalid(f"{label} must be an integer or a decimal string such as '24' " f"(got {value!r})")

    def _validate_str_list(self, value: Any, label: str) -> list[str]:
        """Validate a required non-empty list of non-empty strings."""
        if not isinstance(value, (list, tuple)):
            self._invalid(f"{label} must be a non-empty list of strings (got {value!r})")
        if not value:
            self._invalid(f"{label} must be a non-empty list of strings (got [])")
        if len(value) > self.max_input_items:
            self._invalid(f"{label} exceeds the {self.max_input_items}-item limit " f"(got {len(value)} items)")
        items: list[str] = []
        for item in value:
            if item is None or isinstance(item, bool) or not isinstance(item, str):
                self._invalid(f"every {label} item must be a non-empty string " f"(got {item!r})")
            clean = item.strip()
            if not clean:
                self._invalid(f"every {label} item must be a non-empty string " f"(got {item!r})")
            items.append(clean)
        return items

    # ------------------------------------------------------------------ #
    # Network parsing (content-level — structured errors, not raises)
    # ------------------------------------------------------------------ #

    def _parse_network(
        self,
        context: dict[str, Any],
        token: str,
        prefix: int | None,
    ) -> tuple[ipaddress.IPv4Network | ipaddress.IPv6Network | None, dict[str, Any] | None]:
        """Parse a network token into an ``ipaddress`` network object.

        Returns ``(network, None)`` on success or ``(None, error)``
        with a structured payload for an invalid address part, an
        invalid prefix, conflicting prefix spellings, or host bits set
        (the payload then carries both the strict and the normalized
        interpretation).
        """
        if "/" in token and prefix is not None:
            return None, self._error_result(
                context,
                error_type="invalid_network",
                message=(
                    f"network {token[:64]!r} already contains a prefix "
                    f"length; pass either the CIDR form or the address "
                    f"and a separate prefix={prefix}, not both"
                ),
            )
        if "/" in token:
            base, _, embedded = token.partition("/")
            if not embedded.isdigit():
                return None, self._error_result(
                    context,
                    error_type="invalid_prefix",
                    message=(
                        "the prefix part of "
                        f"{token[:64]!r} must be a decimal integer "
                        "between 0 and 128 without a sign or spaces "
                        f"(got {embedded[:16]!r})"
                    ),
                )
            clean_prefix: int | None = int(embedded)
        else:
            base = token
            clean_prefix = prefix

        try:
            addr = ipaddress.ip_address(base)
        except ValueError:
            return None, self._error_result(
                context,
                error_type="invalid_address",
                message=(
                    f"{base[:64]!r} is not a valid IPv4 or IPv6 "
                    "address (check octet ranges, hexadecimal groups "
                    "and stray characters)"
                ),
            )
        max_prefix = 32 if addr.version == 4 else 128
        if clean_prefix is None:
            # A bare address denotes its own host network.
            clean_prefix = max_prefix
        if not 0 <= clean_prefix <= max_prefix:
            return None, self._error_result(
                context,
                error_type="invalid_prefix",
                message=(
                    f"the prefix must be an integer between 0 and "
                    f"{max_prefix} for IPv{addr.version} "
                    f"(got {clean_prefix!r})"
                ),
            )
        combined = f"{addr}/{clean_prefix}"
        try:
            net = ipaddress.ip_network(combined, strict=True)
        except ValueError:
            normalized = ipaddress.ip_network(combined, strict=False)
            return None, self._error_result(
                context,
                error_type="host_bits_set",
                message=(
                    f"network {combined!r} has host bits set: as written "
                    f"the strict network is {combined} (not the intended "
                    f"block); masking the host bits gives the normalized "
                    f"network {normalized} — retry with that"
                ),
                extra={"input": combined, "normalized": str(normalized)},
            )
        return net, None

    # ------------------------------------------------------------------ #
    # info / contains modes
    # ------------------------------------------------------------------ #

    def _run_info(
        self,
        context: dict[str, Any],
        token: str,
        prefix: int | None,
    ) -> dict[str, Any]:
        """Produce the full network report."""
        net, error = self._parse_network(context, token, prefix)
        if error:
            return error
        result: dict[str, Any] = {
            **context,
            "network": str(net),
            "version": net.version,
            "prefix": net.prefixlen,
            "netmask": str(net.netmask),
            "network_address": str(net.network_address),
            "first_address": str(net.network_address),
            "last_address": str(net.broadcast_address),
            "size": net.num_addresses,
        }
        if net.version == 4:
            # Broadcast and wildcard masks are IPv4 concepts; every
            # address of a /31 or /32 is usable (RFC 3021), larger
            # IPv4 blocks reserve the network and broadcast addresses.
            result["broadcast_address"] = str(net.broadcast_address)
            result["wildcard_mask"] = str(net.hostmask)
            if net.prefixlen >= 31:
                first_usable = net.network_address
                last_usable = net.broadcast_address
                usable_count = net.num_addresses
            else:
                first_usable = net.network_address + 1
                last_usable = net.broadcast_address - 1
                usable_count = net.num_addresses - 2
            result["first_usable_host"] = str(first_usable)
            result["last_usable_host"] = str(last_usable)
            result["usable_host_count"] = usable_count
        return result

    def _run_contains(
        self,
        context: dict[str, Any],
        token: str,
        prefix: int | None,
        addresses: Any,
    ) -> dict[str, Any]:
        """Check a list of addresses against one network."""
        net, error = self._parse_network(context, token, prefix)
        if error:
            return error
        items = self._validate_str_list(addresses, "addresses")
        results: list[dict[str, Any]] = []
        contained = not_contained = invalid = 0
        for item in items:
            try:
                addr = ipaddress.ip_address(item)
            except ValueError:
                invalid += 1
                results.append({"address": item, "contained": False, "invalid": True})
                continue
            inside = addr in net
            if inside:
                contained += 1
            else:
                not_contained += 1
            results.append(
                {
                    "address": item,
                    "normalized": str(addr),
                    "version": addr.version,
                    "contained": inside,
                    "invalid": False,
                }
            )
        return {
            **context,
            "network": str(net),
            "results": results,
            "contained_count": contained,
            "not_contained_count": not_contained,
            "invalid_count": invalid,
        }

    # ------------------------------------------------------------------ #
    # subnet / supernet modes
    # ------------------------------------------------------------------ #

    def _run_subnet(
        self,
        context: dict[str, Any],
        token: str,
        prefix: int | None,
        new_prefix: int | None,
    ) -> dict[str, Any]:
        """Split a network into subnets of a longer prefix."""
        net, error = self._parse_network(context, token, prefix)
        if error:
            return error
        max_prefix = 32 if net.version == 4 else 128
        if not 0 <= new_prefix <= max_prefix:
            return self._error_result(
                context,
                error_type="invalid_prefix",
                message=(
                    f"new_prefix must be an integer between 0 and "
                    f"{max_prefix} for IPv{net.version} "
                    f"(got {new_prefix!r})"
                ),
            )
        if new_prefix <= net.prefixlen:
            return self._error_result(
                context,
                error_type="invalid_prefix",
                message=(
                    "new_prefix must be greater than the current prefix "
                    f"length {net.prefixlen} of {net!s} to split it "
                    f"into subnets (got {new_prefix})"
                ),
            )
        count = 1 << (new_prefix - net.prefixlen)
        cap = self.max_subnets
        subnets = [str(sub) for sub in islice(net.subnets(new_prefix=new_prefix), cap)]
        return {
            **context,
            "network": str(net),
            "new_prefix": new_prefix,
            "count": count,
            "subnets": subnets,
            "returned": len(subnets),
            "truncated": count > len(subnets),
        }

    def _run_supernet(
        self,
        context: dict[str, Any],
        token: str,
        prefix: int | None,
        new_prefix: int | None,
    ) -> dict[str, Any]:
        """Compute the enclosing network of a shorter prefix."""
        net, error = self._parse_network(context, token, prefix)
        if error:
            return error
        max_prefix = 32 if net.version == 4 else 128
        if not 0 <= new_prefix <= max_prefix:
            return self._error_result(
                context,
                error_type="invalid_prefix",
                message=(
                    f"new_prefix must be an integer between 0 and "
                    f"{max_prefix} for IPv{net.version} "
                    f"(got {new_prefix!r})"
                ),
            )
        if new_prefix >= net.prefixlen:
            return self._error_result(
                context,
                error_type="invalid_prefix",
                message=(
                    "new_prefix must be smaller than the current prefix "
                    f"length {net.prefixlen} of {net!s} to form a "
                    f"supernet (got {new_prefix})"
                ),
            )
        supernet = net.supernet(new_prefix=new_prefix)
        return {
            **context,
            "network": str(net),
            "new_prefix": new_prefix,
            "supernet": str(supernet),
            "supernet_network_address": str(supernet.network_address),
            "supernet_netmask": str(supernet.netmask),
            "supernet_size": supernet.num_addresses,
        }

    # ------------------------------------------------------------------ #
    # ip_info mode
    # ------------------------------------------------------------------ #

    def _run_ip_info(self, address: Any) -> dict[str, Any]:
        """Classify a single address and report its textual forms."""
        token = self._validate_str_param(address, "address")
        context: dict[str, Any] = {"mode": "ip_info"}
        try:
            addr = ipaddress.ip_address(token)
        except ValueError:
            return self._error_result(
                context,
                error_type="invalid_address",
                message=(
                    f"{token[:64]!r} is not a valid IPv4 or IPv6 address "
                    "(check octet ranges, hexadecimal groups and stray "
                    "characters)"
                ),
            )
        return {
            **context,
            "address": str(addr),
            "version": addr.version,
            "compressed": str(addr),
            "exploded": addr.exploded,
            "int": int(addr),
            "is_private": addr.is_private,
            "is_global": addr.is_global,
            "is_loopback": addr.is_loopback,
            "is_link_local": addr.is_link_local,
            "is_multicast": addr.is_multicast,
            "is_reserved": addr.is_reserved,
            "type": self._address_type(addr),
        }

    @staticmethod
    def _address_type(addr: Any) -> str:
        """One deterministic label from the classification flags."""
        if addr.is_loopback:
            return "loopback"
        if addr.is_multicast:
            return "multicast"
        if addr.is_link_local:
            return "link_local"
        if addr.is_reserved:
            return "reserved"
        if addr.is_private:
            return "private"
        if addr.is_global:
            return "global"
        return "other"

    # ------------------------------------------------------------------ #
    # summarize mode
    # ------------------------------------------------------------------ #

    def _run_summarize(self, networks: Any) -> dict[str, Any]:
        """Merge addresses / CIDRs into minimal summary ranges."""
        items = self._validate_str_list(networks, "networks")
        context: dict[str, Any] = {"mode": "summarize"}
        parsed = []
        for item in items:
            net, error = self._parse_network(context, item, None)
            if error:
                return error
            parsed.append(net)
        # collapse_addresses requires a single address family, so IPv4
        # and IPv6 inputs are summarized separately (IPv4 first).
        summary = []
        for version in (4, 6):
            group = [net for net in parsed if net.version == version]
            if group:
                summary.extend(ipaddress.collapse_addresses(group))
        return {
            **context,
            "input_count": len(items),
            "networks": [str(net) for net in parsed],
            "summary": [str(net) for net in summary],
            "count": len(summary),
        }

    # ------------------------------------------------------------------ #
    # Error payloads (structured, returned instead of raising)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _error_result(
        context: dict[str, Any],
        error_type: str,
        message: str,
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a structured error payload."""
        error: dict[str, Any] = {"type": error_type, "message": str(message)[:500]}
        if extra:
            error.update(extra)
        return {**context, "error": error}
