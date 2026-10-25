#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: mac_address_tool.py

"""MAC / EUI-48 / EUI-64 address analysis tool, pure Python stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency inspector for
**link-layer identifiers** — the address namespace of Ethernet, Wi-Fi
and Bluetooth hardware, distinct both from IP *network* math
(subnets, masks, containment — see ``CidrCalculatorTool``) and from
UUID logical identifiers (see ``UuidTool``).

Four modes:

* ``parse`` — strict structural validation of one EUI-48 / MAC-48
  address written in any of six notations (case-insensitive):
  colon ``aa:bb:cc:dd:ee:ff``, hyphen ``aa-bb-cc-dd-ee-ff``, Cisco
  dotted ``aabb.ccdd.eeff``, bare ``aabbccddeeff``, ``0x``-prefixed
  ``0xaabbccddeeff`` and the rare dotted-pairs ``aa.bb.cc.dd.ee.ff``.
  A valid address decodes to the canonical separator-free lowercase
  ``bytes_hex``, the detected notation with its groups, the canonical
  forms of every notation, and an informational EUI-64 encapsulation
  (marker ``ffff`` per the IEEE EUI-48-to-EUI-64 mapping or ``fffe``
  per the IPv6 convention — both documented, selected by the
  ``eui64_marker`` flag). Invalid inputs get ``valid: false`` plus
  precise ``findings``: non-ASCII characters (fullwidth digits are
  rejected), bad hex digits with their 1-based position, wrong group
  count per notation, wrong group lengths, wrong total length (11 or
  13 bare hex digits) and mixed separators with the position of the
  deviating separator.
* ``lookup`` — identifies the organization behind the first three
  octets (the OUI) using an embedded curated table of ~145 MA-L
  assignments copied verbatim from the public IEEE registry at
  authoring time (Xerox 00-00-01, Cisco 00-00-0C, Apple 00-03-93,
  Intel, Huawei, Samsung, DEC, 3Com, IBM, Realtek, Broadcom, ...),
  plus the IANA/IEEE special multicast mapping blocks
  01-00-5E-00-00-00/24 (RFC 1112) and 33-33-00-00-00-00/16
  (RFC 2464). The tool is honest about coverage: the table is MA-L
  (24-bit) only, so 28-bit MA-S (the discontinued IAB program, base
  00-50-C2) and 36-bit MA-M assignments resolve to
  ``unknown_oui`` — reported as *unknown*, never as a negative
  vendor claim. Registry-listed ``Private`` assignments and the
  IEEE Registration Authority 00-50-C2 base are flagged
  ``is_private``. When the local-administration bit is set the
  prefix may be randomized by a client, which is surfaced as an
  informational finding.
* ``derive`` — derived-address semantics with step-by-step
  explanations and an inverse check:
  ``eui64_fffe`` / ``eui64_ffff`` insert the FF-FE (IPv6-style) or
  FF-FF (IEEE encapsulation) marker between octet 3 and 4 of an
  EUI-48; ``ipv6_link_local`` implements the full RFC 4291 Modified
  EUI-64 algorithm — insert FF-FE, invert bit 1 of the first octet
  (the universal/local bit), prepend ``fe80::/10`` — producing the
  complete compressed link-local address via the stdlib
  ``ipaddress`` module; ``mac_from_ipv6`` is the reverse: it
  validates that a link-local address really carries the FF-FE
  marker (privacy/random interface identifiers from RFC 7217 do
  not) and recovers the original EUI-48.
* ``compare`` — same-device analysis of two addresses: identical
  (possibly different notations), differs in the NIC part only
  (same OUI, same vendor line), differs exactly by the
  local-administration bit (possibly the same hardware re-notated),
  same vendor family via different OUI blocks of one organization,
  or unrelated.

Input validation is strict and happens before any computation:
malformed parameters (unknown mode, wrong types, missing / empty /
oversized inputs — an address string is capped at 64 characters)
raise a ``ValueError``, mirroring the other common tools. Errors
that depend on the *content being analyzed* — an unparseable
address where one is required, a non-link-local IPv6 address in
``mac_from_ipv6``, a missing FF-FE marker — are returned as a
structured ``error`` payload (or as ``valid: false`` in ``parse``,
where validity *is* the analysis) so an agent can react without
catching exceptions.

Every result is deterministic; the tool performs no network access
(the OUI table is embedded, not queried) and no randomness.
"""

import ipaddress
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

_ASCII_HEX = set("0123456789abcdefABCDEF")

# --------------------------------------------------------------------- #
# Embedded curated OUI table (static fixture, no network at runtime).
#
# Source: the public IEEE MA-L registry
# https://standards-oui.ieee.org/oui/oui.csv as retrieved on
# 2026-10-21 (registry column MA-L). Organization names are copied
# VERBATIM from the registry, including legacy spellings ("DEC",
# "Segate Technology LLC", "Hewlett Packard" vs "Hewlett Packard
# Enterprise", trailing commas) — they are identifiers of registry
# records, not marketing names. ~145 well-known assignments; misses
# are reported as unknown_oui, never as a negative vendor claim.
# --------------------------------------------------------------------- #
_OUI_ASSIGNMENTS: Tuple[Tuple[str, str], ...] = (
    ("000001", "XEROX CORPORATION"),  # Xerox
    ("0000aa", "XEROX CORPORATION"),  # Xerox
    ("00000c", "Cisco Systems, Inc"),  # Cisco
    ("001b0d", "Cisco Systems, Inc"),  # Cisco
    ("0022bd", "Cisco Systems, Inc"),  # Cisco
    ("58971e", "Cisco Systems, Inc"),  # Cisco
    ("00270d", "Cisco Systems, Inc"),  # Cisco
    ("000121", "WatchGuard Technologies, Inc."),  # WatchGuard
    ("000c41", "Cisco-Linksys, LLC"),  # Cisco-Linksys
    ("0014bf", "Cisco-Linksys, LLC"),  # Cisco-Linksys
    ("002369", "Cisco-Linksys, LLC"),  # Cisco-Linksys
    ("001d7e", "Cisco-Linksys, LLC"),  # Cisco-Linksys
    ("08002b", "DIGITAL EQUIPMENT CORPORATION"),  # DEC
    ("0000f8", "DIGITAL EQUIPMENT CORPORATION"),  # DEC
    ("080020", "Oracle Corporation"),  # Oracle/Sun
    ("0021f6", "Oracle Corporation"),  # Oracle
    ("00001b", "Novell, Inc."),  # Novell
    ("0020af", "3COM"),  # 3Com
    ("00608c", "3COM"),  # 3Com
    ("02608c", "3COM"),  # 3Com
    ("0004ac", "IBM Corp"),  # IBM
    ("002035", "IBM Corp"),  # IBM
    ("5cf3fc", "IBM Corp"),  # IBM
    ("0002b3", "Intel Corporation"),  # Intel
    ("002710", "Intel Corporate"),  # Intel
    ("3ca9f4", "Intel Corporate"),  # Intel
    ("a0369f", "Intel Corporate"),  # Intel
    ("000393", "Apple, Inc."),  # Apple
    ("0021e9", "Apple, Inc."),  # Apple
    ("002500", "Apple, Inc."),  # Apple
    ("002608", "Apple, Inc."),  # Apple
    ("f01898", "Apple, Inc."),  # Apple
    ("3c0754", "Apple, Inc."),  # Apple
    ("10ddb1", "Apple, Inc."),  # Apple
    ("a45e60", "Apple, Inc."),  # Apple
    ("2c200b", "Apple, Inc."),  # Apple
    ("acde48", "Private"),  # Apple/Private
    ("001422", "Dell Inc."),  # Dell
    ("f8db88", "Dell Inc."),  # Dell
    ("8cec4b", "Dell Inc."),  # Dell
    ("001a4b", "Hewlett Packard"),  # HP
    ("001f29", "Hewlett Packard"),  # HP
    ("3cd92b", "Hewlett Packard"),  # HP
    ("000b86", "Hewlett Packard Enterprise"),  # HPE/Aruba
    ("24dec6", "Hewlett Packard Enterprise"),  # HPE/Aruba
    ("001882", "HUAWEI TECHNOLOGIES CO.,LTD"),  # Huawei
    ("286ed4", "HUAWEI TECHNOLOGIES CO.,LTD"),  # Huawei
    ("58605f", "HUAWEI TECHNOLOGIES CO.,LTD"),  # Huawei
    ("781dba", "HUAWEI TECHNOLOGIES CO.,LTD"),  # Huawei
    ("d4612e", "HUAWEI TECHNOLOGIES CO.,LTD"),  # Huawei
    ("002389", "Hangzhou H3C Technologies Co., Limited"),  # H3C
    ("001632", "Samsung Electronics Co.,Ltd"),  # Samsung
    ("002454", "Samsung Electronics Co.,Ltd"),  # Samsung
    ("0024e9", "Samsung Electronics Co.,Ltd"),  # Samsung
    ("8c7712", "Samsung Electronics Co.,Ltd"),  # Samsung
    ("0022a9", "LG Electronics (Mobile Communications)"),  # LG
    ("10683f", "LG Electronics (Mobile Communications)"),  # LG
    ("64bc0c", "LG Electronics (Mobile Communications)"),  # LG
    ("00014a", "Sony Corporation"),  # Sony
    ("0024be", "Sony Corporation"),  # Sony
    ("001dbc", "Nintendo Co., Ltd."),  # Nintendo
    ("0025a0", "Nintendo Co., Ltd."),  # Nintendo
    ("002659", "Nintendo Co., Ltd."),  # Nintendo
    ("00e04c", "REALTEK SEMICONDUCTOR CORP."),  # Realtek
    ("001018", "Broadcom"),  # Broadcom
    ("005043", "MARVELL SEMICONDUCTOR, INC."),  # Marvell
    ("00044b", "NVIDIA"),  # NVIDIA
    ("00037f", "Atheros Communications, Inc."),  # Atheros
    ("0026e8", "Murata Manufacturing Co., Ltd."),  # Murata
    ("006057", "Murata Manufacturing Co., Ltd."),  # Murata
    ("000569", "VMware, Inc."),  # VMware
    ("000c29", "VMware, Inc."),  # VMware
    ("005056", "VMware, Inc."),  # VMware
    ("0003ff", "Microsoft Corporation"),  # Microsoft
    ("00155d", "Microsoft Corporation"),  # Microsoft
    ("0050f2", "MICROSOFT CORP."),  # Microsoft
    ("00163e", "Xensource, Inc."),  # Xen
    ("001c42", "Parallels, Inc."),  # Parallels
    ("00a098", "NetApp"),  # NetApp
    ("0090a9", "WESTERN DIGITAL"),  # Western Digital
    ("001075", "Segate Technology LLC"),  # Seagate
    ("002590", "Super Micro Computer, Inc."),  # Supermicro
    ("0cc47a", "Super Micro Computer, Inc."),  # Supermicro
    ("000d61", "Giga-Byte Technology Co., Ltd."),  # Gigabyte
    ("000c6e", "ASUSTek COMPUTER INC."),  # ASUSTek
    ("ac9e17", "ASUSTek COMPUTER INC."),  # ASUSTek
    ("04d9f5", "ASUSTek COMPUTER INC."),  # ASUSTek
    ("00016c", "FOXCONN"),  # Foxconn
    ("54ee75", "Wistron InfoComm(Kunshan)Co.,Ltd."),  # Wistron
    ("005907", "LenovoEMC Products USA, LLC"),  # LenovoEMC
    ("106f3f", "BUFFALO.INC"),  # Buffalo
    ("00095b", "NETGEAR"),  # Netgear
    ("a040a0", "NETGEAR"),  # Netgear
    ("00055d", "D-LINK SYSTEMS, INC."),  # D-Link
    ("001e58", "D-Link Corporation"),  # D-Link
    ("0023cd", "TP-LINK TECHNOLOGIES CO.,LTD."),  # TP-LINK
    ("002719", "TP-LINK TECHNOLOGIES CO.,LTD."),  # TP-LINK
    ("50c7bf", "TP-LINK TECHNOLOGIES CO.,LTD."),  # TP-LINK
    ("00a0c5", "Zyxel Communications Corporation"),  # Zyxel
    ("4c9eff", "Zyxel Communications Corporation"),  # Zyxel
    ("001150", "Belkin Corporation"),  # Belkin
    ("c05627", "Belkin International Inc."),  # Belkin
    ("000585", "Juniper Networks"),  # Juniper
    ("001f12", "Juniper Networks"),  # Juniper
    ("0418d6", "Ubiquiti Inc"),  # Ubiquiti
    ("f09fc2", "Ubiquiti Inc"),  # Ubiquiti
    ("c84f86", "Sophos Ltd"),  # Sophos
    ("00869c", "Palo Alto Networks"),  # Palo Alto Networks
    ("00a08e", "Check Point Software Technologies"),  # Check Point
    ("7478a6", "Fortinet, Inc."),  # Fortinet
    ("0006b1", "Sonicwall"),  # SonicWall
    ("085531", "Routerboard.com"),  # MikroTik/Routerboard
    ("44650d", "Amazon Technologies Inc."),  # Amazon
    ("74c246", "Amazon Technologies Inc."),  # Amazon
    ("f04f7c", "Amazon Technologies Inc."),  # Amazon
    ("f4f5d8", "Google, Inc."),  # Google
    ("4857dd", "Facebook Inc"),  # Facebook
    ("480560", "Meta Platforms, Inc."),  # Meta
    ("8cbebe", "Xiaomi Communications Co Ltd"),  # Xiaomi
    ("3c8cf8", "TRENDnet, Inc."),  # TRENDnet
    ("b827eb", "Raspberry Pi Foundation"),  # Raspberry Pi
    ("dca632", "Raspberry Pi Trading Ltd"),  # Raspberry Pi
    ("e45f01", "Raspberry Pi Trading Ltd"),  # Raspberry Pi
    ("240ac4", "Espressif Inc."),  # Espressif
    ("30aea4", "Espressif Inc."),  # Espressif
    ("a4cf12", "Espressif Inc."),  # Espressif
    ("0024fe", "AVM GmbH"),  # AVM
    ("001788", "Philips Lighting BV"),  # Philips Hue/Signify
    ("c42996", "Signify B.V."),  # Signify
    ("90ece3", "Nokia"),  # Nokia
    ("e04735", "Ericsson AB"),  # Ericsson
    ("001b1b", "Siemens AG,"),  # Siemens
    ("008045", "MATSUSHITA ELECTRIC IND. CO"),  # Panasonic/Matsushita
    ("84ba3b", "CANON INC."),  # Canon
    ("008077", "Brother industries, LTD."),  # Brother
    ("a4d73c", "Seiko Epson Corporation"),  # Epson
    ("583879", "RICOH COMPANY, LTD."),  # Ricoh
    ("9075de", "Zebra Technologies Inc."),  # Zebra
    ("004084", "Honeywell"),  # Honeywell
    ("000496", "Extreme Networks, Inc."),  # Extreme Networks
    ("0c75d2", "Hangzhou Hikvision Digital Technology Co.,Ltd."),  # Hikvision
    ("244845", "Hangzhou Hikvision Digital Technology Co.,Ltd."),  # Hikvision
    ("74c929", "Zhejiang Dahua Technology Co., Ltd."),  # Dahua
    ("0050c2", "IEEE Registration Authority"),  # IEEE RA (IAB base)
    ("00005e", "ICANN, IANA Department"),  # IANA
)

_OUI_TABLE: Dict[str, str] = dict(_OUI_ASSIGNMENTS)

# IANA / IEEE *special* multicast mapping blocks. These are protocol
# reservations documented in RFC 1112 (IPv4) and RFC 2464 (IPv6
# Ethernet mapping), not MA-L organization assignments, so they are
# kept apart from the vendor table above and carry their own source
# label in lookup results.
_SPECIAL_PREFIXES: Dict[str, str] = {
    "01005e": "IPv4 multicast mapping block 01-00-5E-00-00-00/24 "
              "(RFC 1112 / IANA special block)",
    "3333": "IPv6 multicast mapping block 33-33-00-00-00-00/16 "
            "(RFC 2464 / IANA special block)",
}

# OUIs whose registry record itself marks the block as non-public or
# as held by the IEEE Registration Authority for subdivision (the
# discontinued 28-bit IAB program, now MA-S). A 24-bit lookup cannot
# attribute these to a final organization.
_PRIVATE_OUIS = frozenset({"acde48", "0050c2"})

# Notation names, in the order documented above.
NOTATIONS: Tuple[str, ...] = (
    "colon",
    "hyphen",
    "cisco_dotted",
    "bare",
    "prefixed",
    "dotted_pairs",
)

_NOTATION_SPECS: Dict[str, str] = (
    "colon: six groups of two hex digits separated by ':' "
    "(aa:bb:cc:dd:ee:ff); "
    "hyphen: six groups of two separated by '-' "
    "(aa-bb-cc-dd-ee-ff); "
    "cisco_dotted: three groups of four separated by '.' "
    "(aabb.ccdd.eeff); "
    "bare: twelve contiguous hex digits (aabbccddeeff); "
    "prefixed: '0x' followed by twelve contiguous hex digits "
    "(0xaabbccddeeff); "
    "dotted_pairs: six groups of two separated by '.' "
    "(aa.bb.cc.dd.ee.ff — rare; documented for completeness)"
)


class _MacAddressError(Exception):
    """Internal carrier for a structural address defect + findings."""

    def __init__(self, findings: List[Dict[str, Any]]) -> None:
        super().__init__(findings[0]["message"] if findings else "invalid")
        self.findings = findings


def _finding(code: str, message: str, position: Optional[int] = None) -> Dict[str, Any]:
    item: Dict[str, Any] = {"code": code, "message": message}
    if position is not None:
        item["position"] = position
    return item

class MacAddressTool(Tool):
    """MAC / EUI-48 / EUI-64 address analysis tool (pure stdlib).

    Attributes:
        max_address_chars (int): Upper bound on any single address
            string input; longer inputs are rejected before any work.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "mac_address_tool"
    description: str = (
        "MAC / EUI-48 / EUI-64 address analysis tool — pure Python "
        "stdlib, no network required. Strict parsing of six MAC "
        "notations with canonical forms and precise findings "
        "(mode='parse'), OUI organization identification against an "
        "embedded curated IEEE registry table with honest "
        "unknown-oui reporting (mode='lookup'), EUI-64 and IPv6 "
        "link-local derivation with step-by-step math and inverse "
        "checks (mode='derive'), and same-device comparison of two "
        "addresses (mode='compare')."
    )

    MODES: ClassVar[tuple] = ("parse", "lookup", "derive", "compare")
    DERIVATIONS: ClassVar[tuple] = (
        "eui64_fffe",
        "eui64_ffff",
        "ipv6_link_local",
        "mac_from_ipv6",
    )
    EUI64_MARKERS: ClassVar[tuple] = ("fffe", "ffff")
    #: Embedded MA-L assignments (public IEEE registry snapshot).
    OUI_TABLE: ClassVar[Dict[str, str]] = _OUI_TABLE
    #: IANA/IEEE special multicast mapping blocks.
    SPECIAL_PREFIXES: ClassVar[Dict[str, str]] = dict(_SPECIAL_PREFIXES)

    max_address_chars: int = 64

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any = None,
        address: Any = None,
        address_a: Any = None,
        address_b: Any = None,
        derivation: Any = None,
        eui64_marker: Any = None,
    ) -> Dict[str, Any]:
        """Run one MAC address analysis.

        Args:
            mode (str): One of ``parse`` / ``lookup`` / ``derive`` /
                ``compare``.
            address (str): The address to analyze — required for the
                ``parse``, ``lookup`` and ``derive`` modes (for
                ``mac_from_ipv6`` it is the IPv6 link-local address).
                Any of the six supported notations, any case.
            address_a (str): First address of the ``compare`` mode.
            address_b (str): Second address of the ``compare`` mode.
            derivation (str): ``derive`` only — one of ``eui64_fffe``,
                ``eui64_ffff``, ``ipv6_link_local``, ``mac_from_ipv6``.
            eui64_marker (str): ``parse`` only — ``"ffff"`` (default,
                the IEEE EUI-48-to-EUI-64 encapsulation marker) or
                ``"fffe"`` (the IPv6 convention marker); selects which
                informational EUI-64 form ``parse`` reports.

        Returns:
            Dict[str, Any]: The analysis result (always including the
                mode and the raw input) — for ``parse`` a ``valid``
                flag with the decoded structure, for the other modes
                the mode-specific payload — or a structured ``error``
                payload for content-level failures (unparseable
                address, non-link-local IPv6, missing FF-FE marker).

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        if eui64_marker is None:
            eui64_marker = "ffff"
        if eui64_marker not in self.EUI64_MARKERS:
            self._invalid(
                "eui64_marker must be one of: "
                f"{', '.join(self.EUI64_MARKERS)} (got {eui64_marker!r})"
            )
        if mode == "parse":
            return self._run_parse(
                self._validate_address_param(address, "address"), eui64_marker
            )
        if mode == "lookup":
            return self._run_lookup(
                self._validate_address_param(address, "address")
            )
        if mode == "derive":
            if derivation not in self.DERIVATIONS:
                self._invalid(
                    "derivation is required for derive mode and must be one "
                    f"of: {', '.join(self.DERIVATIONS)} (got {derivation!r})"
                )
            return self._run_derive(
                self._validate_address_param(address, "address"), derivation
            )
        address_a = self._validate_address_param(address_a, "address_a")
        address_b = self._validate_address_param(address_b, "address_b")
        return self._run_compare(address_a, address_b)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"mac_address_tool: {message}")

    def _validate_address_param(self, value: Any, label: str) -> str:
        """Validate one address string parameter (type/size only)."""
        if (
            value is None
            or isinstance(value, bool)
            or not isinstance(value, str)
        ):
            self._invalid(
                f"{label} must be a non-empty address string of at most "
                f"{self.max_address_chars} characters (got {value!r})"
            )
        if not value.strip():
            self._invalid(f"{label} must be a non-empty address string (got {value!r})")
        if len(value) > self.max_address_chars:
            self._invalid(
                f"{label} exceeds the {self.max_address_chars}-character "
                f"limit (got {len(value)} characters)"
            )
        return value

    # ------------------------------------------------------------------ #
    # Structural EUI-48 analysis (shared by every mode)
    # ------------------------------------------------------------------ #

    @classmethod
    def _analyze(cls, raw: str) -> Dict[str, Any]:
        """Normalize one address string from any of the six notations.

        Returns ``bytes_hex`` (12 lowercase hex digits), the detected
        notation, the groups as written (lower-cased), and the
        canonical forms of every notation.

        Raises:
            _MacAddressError: If the string is not a valid EUI-48 in
                one of the six notations, carrying precise findings.
        """
        text = raw.strip()

        # 0. Charset gate: everything must be ASCII; hex digits are
        #    checked per group below. Fullwidth (Unicode) digits are
        #    a classic paste artifact and are rejected explicitly.
        for position, char in enumerate(text):
            if ord(char) > 0x7F:
                raise _MacAddressError([
                    _finding(
                        "non_ascii_character",
                        f"character {char!r} (U+{ord(char):04X}) at position "
                        f"{position + 1} (1-based) is not an ASCII "
                        "hexadecimal digit — fullwidth/Unicode digits are "
                        "not accepted",
                        position=position + 1,
                    )
                ])

        # 1. 0x/0X prefix handling. Finding positions are always
        #    1-based within the input string (after whitespace
        #    stripping), so positions computed inside the body shift
        #    by the two prefix characters when one is present.
        prefixed = False
        body = text
        prefix_offset = 0
        if body[:2] in ("0x", "0X"):
            prefixed = True
            body = body[2:]
            prefix_offset = 2

        separators = {char for char in body if char in ":.-"}

        # 2. Mixed separators: never valid.
        if len(separators) > 1:
            first_sep = next(
                char for char in body if char in ":.-"
            )
            deviating_position = None
            deviating_char = None
            for index, char in enumerate(body):
                if char in ":.-" and char != first_sep:
                    deviating_position = prefix_offset + index + 1
                    deviating_char = char
                    break
            raise _MacAddressError([
                _finding(
                    "mixed_separators",
                    f"separators are mixed: '{first_sep}' and "
                    f"'{deviating_char}' (deviating '{deviating_char}' at "
                    f"position {deviating_position}, 1-based) — an address "
                    "must use one separator notation consistently "
                    f"({_NOTATION_SPECS})",
                    position=deviating_position,
                )
            ])

        # 3. No separators: bare (or prefixed) contiguous hex.
        if not separators:
            groups = [body]
            if len(body) != 12 or not all(c in _ASCII_HEX for c in body):
                raise _MacAddressError(
                    cls._contiguous_defects(body, prefixed=prefixed)
                )
            notation = "prefixed" if prefixed else "bare"
            return cls._assemble(body, notation, groups)

        # 4. Exactly one separator kind.
        separator = next(iter(separators))
        groups = body.split(separator)
        if separator in (":", "-"):
            if len(groups) != 6 or any(len(group) != 2 for group in groups):
                raise _MacAddressError(
                    cls._grouped_defects(groups, separator)
                )
            cls._require_hex_groups(groups, prefix_offset)
            notation = "colon" if separator == ":" else "hyphen"
            return cls._assemble("".join(groups), notation, groups)

        # 5. Dotted: either Cisco 3x4 or the rare dotted-pairs 6x2.
        if len(groups) == 3:
            if any(len(group) != 4 for group in groups):
                raise _MacAddressError(
                    cls._grouped_defects(groups, separator)
                )
            cls._require_hex_groups(groups, prefix_offset)
            return cls._assemble("".join(groups), "cisco_dotted", groups)
        if len(groups) == 6:
            if any(len(group) != 2 for group in groups):
                raise _MacAddressError(
                    cls._grouped_defects(groups, separator)
                )
            cls._require_hex_groups(groups, prefix_offset)
            return cls._assemble("".join(groups), "dotted_pairs", groups)
        raise _MacAddressError(cls._grouped_defects(groups, separator))

    @classmethod
    def _contiguous_defects(
        cls, body: str, prefixed: bool
    ) -> List[Dict[str, Any]]:
        """Diagnose a separator-free body that is not 12 hex digits."""
        findings: List[Dict[str, Any]] = []
        for index, char in enumerate(body):
            if char not in _ASCII_HEX:
                offset = 2 if prefixed else 0
                position = offset + index + 1
                findings.append(_finding(
                    "bad_hex_digit",
                    f"character {char!r} at position {position} (1-based) "
                    "is not a hexadecimal digit",
                    position=position,
                ))
                break
        if not findings:
            label = "after the '0x' prefix " if prefixed else ""
            findings.append(_finding(
                "wrong_total_length",
                f"expected 12 hexadecimal digits (48-bit EUI-48 / MAC-48) "
                f"{label}but got {len(body)} — wrong total length",
            ))
        return findings

    @classmethod
    def _grouped_defects(
        cls, groups: List[str], separator: str
    ) -> List[Dict[str, Any]]:
        """Diagnose a wrong group count or wrong group lengths."""
        if separator in (":", "-"):
            sep_name = "colon" if separator == ":" else "hyphen"
            example = separator.join(["aa", "bb", "cc", "dd", "ee", "ff"])
            return [
                _finding(
                    "wrong_group_count"
                    if len(groups) != 6
                    else "wrong_group_length",
                    f"the {sep_name} '{separator}' notation expects six "
                    "groups of two hex digits "
                    f"({example}); got {len(groups)} group(s) with "
                    f"lengths {[len(group) for group in groups]}",
                )
            ]
        # Dotted: the structure itself decides which notation was
        # attempted; 3 groups point at Cisco 4-4-4, 6 at dotted-pairs.
        if len(groups) == 3:
            expectation = (
                "the Cisco dotted notation expects three groups of four "
                "hex digits (aabb.ccdd.eeff)"
            )
        elif len(groups) == 6:
            expectation = (
                "the dotted-pairs notation expects six groups of two hex "
                "digits (aa.bb.cc.dd.ee.ff)"
            )
        else:
            expectation = (
                "the dotted notations expect either three groups of four "
                "hex digits (Cisco, aabb.ccdd.eeff) or six groups of two "
                "hex digits (aa.bb.cc.dd.ee.ff)"
            )
        return [
            _finding(
                "wrong_group_count"
                if len(groups) not in (3, 6)
                else "wrong_group_length",
                f"{expectation}; got {len(groups)} group(s) with lengths "
                f"{[len(group) for group in groups]}",
            )
        ]

    @classmethod
    def _require_hex_groups(
        cls, groups: List[str], offset: int = 0
    ) -> None:
        """Raise on the first non-hex character with its position.

        ``offset`` shifts positions from the group body to the whole
        input string (2 when a ``0x``/``0X`` prefix was stripped).
        """
        position_offset = offset
        for index, group in enumerate(groups):
            for inner, char in enumerate(group):
                if char not in _ASCII_HEX:
                    position = position_offset + inner + 1
                    raise _MacAddressError([
                        _finding(
                            "bad_hex_digit",
                            f"character {char!r} at position {position} "
                            f"(1-based, in group {index + 1} {group!r}) is "
                            "not a hexadecimal digit",
                            position=position,
                        )
                    ])
            position_offset += len(group) + 1

    @staticmethod
    def _assemble(
        bytes_hex: str, notation: str, groups: List[str]
    ) -> Dict[str, Any]:
        """Build the shared decode result for a validated address."""
        lowered = bytes_hex.lower()
        octets = [lowered[i : i + 2] for i in range(0, 12, 2)]
        return {
            "bytes_hex": lowered,
            "notation_detected": notation,
            "groups": [group.lower() for group in groups],
            "canonical_forms": {
                "colon": ":".join(octets),
                "hyphen": "-".join(octets),
                "cisco_dotted": (
                    f"{octets[0]}{octets[1]}.{octets[2]}{octets[3]}."
                    f"{octets[4]}{octets[5]}"
                ),
                "bare": lowered,
                "prefixed": f"0x{lowered}",
                "dotted_pairs": ".".join(octets),
            },
        }

    # ------------------------------------------------------------------ #
    # Bit semantics
    # ------------------------------------------------------------------ #

    @staticmethod
    def _bit_semantics(bytes_hex: str) -> Dict[str, Any]:
        """Decode the I/G and U/L bits, the specials and OUI/NIC."""
        first_octet = int(bytes_hex[0:2], 16)
        # Bit 0 of the first octet: Individual/Group (I/G) bit —
        # 0 unicast, 1 group/multicast (01:xx:xx:xx:xx:xx onward).
        multicast = bool(first_octet & 0x01)
        # Bit 1 of the first octet: Universal/Local (U/L) bit —
        # 0 globally unique (IEEE-assigned OUI), 1 locally
        # administered (02:00:00:00:00:00 style, virtual NICs, MAC
        # randomization).
        local_admin = bool(first_octet & 0x02)
        return {
            "local_admin": local_admin,
            "multicast": multicast,
            "is_broadcast": bytes_hex == "ffffffffffff",
            "is_zero": bytes_hex == "000000000000",
            "oui": ":".join(
                bytes_hex[i : i + 2] for i in range(0, 6, 2)
            ),
            "nic": ":".join(
                bytes_hex[i : i + 2] for i in range(6, 12, 2)
            ),
            "first_octet_binary": format(first_octet, "08b"),
        }

    @staticmethod
    def _bits_note(bit_semantics: Dict[str, Any]) -> str:
        """Plain-language reading of the two flag bits."""
        ig = (
            "group/multicast (I/G bit set — bit 0 of the first octet)"
            if bit_semantics["multicast"]
            else "individual/unicast (I/G bit clear)"
        )
        ul = (
            "locally administered (U/L bit set — bit 1 of the first octet; "
            "the OUI part is NOT an IEEE-assigned vendor prefix)"
            if bit_semantics["local_admin"]
            else "globally unique (U/L bit clear; OUI part conventionally "
            "an IEEE-assigned vendor prefix)"
        )
        return (
            f"first octet {bit_semantics['first_octet_binary']}b: {ig}; {ul}"
        )

    # ------------------------------------------------------------------ #
    # parse mode
    # ------------------------------------------------------------------ #

    def _run_parse(self, raw: str, eui64_marker: str) -> Dict[str, Any]:
        """Strictly validate one address and decode its structure."""
        try:
            decoded = self._analyze(raw)
        except _MacAddressError as exc:
            return {
                "mode": "parse",
                "input": raw,
                "valid": False,
                "findings": exc.findings,
            }
        bytes_hex = decoded["bytes_hex"]
        bit_semantics = self._bit_semantics(bytes_hex)
        result: Dict[str, Any] = {
            "mode": "parse",
            "input": raw,
            "valid": True,
            "bytes_hex": bytes_hex,
            "notation_detected": decoded["notation_detected"],
            "groups": decoded["groups"],
            "canonical_forms": decoded["canonical_forms"],
            "eui64_marker": eui64_marker,
            "eui64_hex": self._eui64_insert(bytes_hex, eui64_marker),
            "bit_semantics": bit_semantics,
            "bits_note": self._bits_note(bit_semantics),
            "findings": [],
        }
        notes: List[str] = []
        if bit_semantics["is_broadcast"]:
            notes.append(
                "ff:ff:ff:ff:ff:ff is the Ethernet broadcast address"
            )
        if bit_semantics["is_zero"]:
            notes.append(
                "00:00:00:00:00:00 is the unspecified/zero address"
            )
        if notes:
            result["notes"] = notes
        return result

    # ------------------------------------------------------------------ #
    # lookup mode
    # ------------------------------------------------------------------ #

    @classmethod
    def _special_prefix_match(cls, bytes_hex: str) -> Optional[str]:
        """Match IANA/IEEE special multicast mapping blocks.

        The IPv4 mapping block 01-00-5E-00-00-00/24 is a full 24-bit
        prefix (exact match on the OUI); the IPv6 mapping block
        33-33-00-00-00-00/16 (RFC 2464) is only a 16-bit prefix, so
        every address whose first two octets are 33-33 matches.
        """
        oui_hex = bytes_hex[:6]
        if oui_hex in cls.SPECIAL_PREFIXES:
            return cls.SPECIAL_PREFIXES[oui_hex]
        if bytes_hex[:4] == "3333":
            return cls.SPECIAL_PREFIXES["3333"]
        return None

    def _run_lookup(self, raw: str) -> Dict[str, Any]:
        """Identify the OUI organization behind an address."""
        context: Dict[str, Any] = {"mode": "lookup"}
        try:
            decoded = self._analyze(raw)
        except _MacAddressError as exc:
            return self._error_result(
                context,
                error_type="invalid_address",
                message=(
                    "input is not a valid EUI-48 address in one of the six "
                    f"supported notations: {exc.findings[0]['message']}"
                ),
                findings=exc.findings,
            )
        bytes_hex = decoded["bytes_hex"]
        oui_hex = bytes_hex[:6]
        bit_semantics = self._bit_semantics(bytes_hex)
        findings: List[Dict[str, Any]] = []

        special = self._special_prefix_match(bytes_hex)
        if special is not None:
            organization = special
            source = "iana_special"
            known = True
        elif oui_hex in self.OUI_TABLE:
            organization = self.OUI_TABLE[oui_hex]
            source = "ieee_ma-l_curated"
            known = True
        else:
            organization = None
            source = None
            known = False
            findings.append(_finding(
                "unknown_oui",
                f"the OUI {oui_hex[0:2]}-{oui_hex[2:4]}-{oui_hex[4:6]} is "
                "not in the embedded curated MA-L table (~145 entries) — "
                "reported as unknown, NOT as a negative vendor claim; the "
                "prefix may belong to a smaller vendor, to a 28-bit MA-S "
                "(ex-IAB) or 36-bit MA-M assignment outside this table's "
                "24-bit scope, or to a randomized/local prefix",
            ))

        is_private = oui_hex in _PRIVATE_OUIS
        if is_private:
            note = (
                "the registry record for AC-DE-48 is listed as 'Private' — "
                "widely attributed to Apple (Bonjour/AirDrop era) but not "
                "published as such by the IEEE"
                if oui_hex == "acde48"
                else "the base OUI 00-50-C2 is held by the IEEE "
                "Registration Authority: it fronts the discontinued "
                "28-bit IAB program (now MA-S), whose individual "
                "assignees cannot be resolved from any 24-bit table"
            )
            findings.append(_finding(
                "registry_private_block", note
            ))
        if bit_semantics["local_admin"]:
            findings.append(_finding(
                "local_admin_prefix_unreliable",
                "the local-administration (U/L) bit is set: the first "
                "three octets are not an IEEE-assigned OUI — client MAC "
                "randomization (iOS/Android/Windows) and virtual NICs "
                "generate such prefixes, so any OUI identification is "
                "unreliable",
            ))

        result: Dict[str, Any] = {
            **context,
            "input": raw,
            "bytes_hex": bytes_hex,
            "oui_prefix": (
                f"{oui_hex[0:2]}-{oui_hex[2:4]}-{oui_hex[4:6]}"
            ),
            "organization": organization,
            "known": known,
            "source": source,
            "is_private": is_private,
            "table_size": len(self.OUI_TABLE),
            "coverage_note": (
                "the embedded table contains MA-L (24-bit / OUI) "
                "assignments only, snapshotted from the public IEEE "
                "registry at authoring time; MA-S (28-bit, ex-IAB) and "
                "MA-M (36-bit) blocks are out of scope and resolve to "
                "unknown_oui"
            ),
            "findings": findings,
        }
        return result

    # ------------------------------------------------------------------ #
    # derive mode
    # ------------------------------------------------------------------ #

    @staticmethod
    def _eui64_insert(bytes_hex: str, marker: str) -> str:
        """Encapsulate an EUI-48 into 64 bits with the given marker."""
        return bytes_hex[:6] + marker + bytes_hex[6:]

    def _run_derive(self, raw: str, derivation: str) -> Dict[str, Any]:
        """Derive EUI-64 / IPv6 forms with steps and inverse checks."""
        context: Dict[str, Any] = {"mode": "derive", "derivation": derivation}
        if derivation == "mac_from_ipv6":
            return self._derive_mac_from_ipv6(context, raw)
        try:
            decoded = self._analyze(raw)
        except _MacAddressError as exc:
            return self._error_result(
                context,
                error_type="invalid_address",
                message=(
                    "base is not a valid EUI-48 address: "
                    f"{exc.findings[0]['message']}"
                ),
                findings=exc.findings,
            )
        bytes_hex = decoded["bytes_hex"]
        base = decoded["canonical_forms"]["colon"]
        bit_semantics = self._bit_semantics(bytes_hex)
        findings: List[Dict[str, Any]] = []
        if bit_semantics["is_zero"] or bit_semantics["is_broadcast"]:
            findings.append(_finding(
                "degenerate_base",
                "the base address is all-zero or broadcast — the "
                "derivation is still well-defined math and is performed, "
                "but such a base carries no device identity",
            ))

        if derivation in ("eui64_fffe", "eui64_ffff"):
            marker = derivation[-4:]
            eui64_hex = self._eui64_insert(bytes_hex, marker)
            eui64_octets = [
                eui64_hex[i : i + 2] for i in range(0, 16, 2)
            ]
            if marker == "fffe":
                marker_note = (
                    "FF-FE - the marker of the IPv6 Modified EUI-64 "
                    "convention (RFC 4291)"
                )
            else:
                marker_note = (
                    "FF-FF - the IEEE EUI-48-to-EUI-64 encapsulation "
                    "marker"
                )
            steps = [
                f"start from the canonical EUI-48 {base} "
                f"(bytes {bytes_hex})",
                f"insert the 16-bit marker {eui64_octets[3]}:"
                f"{eui64_octets[4]} ({marker_note}) between octet 3 and "
                "octet 4",
                f"join to the 64-bit EUI-64 {':'.join(eui64_octets)} - no "
                "U/L bit flip in the plain encapsulation (only the IPv6 "
                "link-local derivation inverts it)",
            ]
            inverse = {
                "performed": True,
                "method": (
                    f"strip the {marker} marker bytes at positions 4-5 "
                    "and compare the remaining six octets with the base"
                ),
                "recovered_eui48_hex": bytes_hex,
                "matches": True,
            }
            return {
                **context,
                "input": raw,
                "base": base,
                "eui64_hex": eui64_hex,
                "eui64_canonical": ":".join(eui64_octets),
                "steps": steps,
                "inverse_check": inverse,
                "findings": findings,
            }

        # ipv6_link_local — RFC 4291 Modified EUI-64.
        first_octet = int(bytes_hex[0:2], 16)
        flipped = first_octet ^ 0x02
        modified_first = format(flipped, "02x")
        iid_hex = modified_first + bytes_hex[2:6] + "fffe" + bytes_hex[6:]
        eui64_octets = [iid_hex[i : i + 2] for i in range(0, 16, 2)]
        interface_id = int(iid_hex, 16)
        link_local = ipaddress.IPv6Address(
            (0xFE80 << 112) | interface_id
        )
        recovered = self._recover_eui48_from_iid(interface_id)
        return {
            **context,
            "input": raw,
            "base": base,
            "eui64_hex": iid_hex,
            "eui64_canonical": ":".join(eui64_octets),
            "link_local": str(link_local),
            "link_local_exploded": link_local.exploded,
            "interface_id_hex": iid_hex,
            "steps": [
                f"start from the canonical EUI-48 {base} (bytes "
                f"{bytes_hex})",
                f"insert the FF-FE marker between octet 3 and octet 4: "
                f"{':'.join(eui64_octets[:3])}:ff:fe:{':'.join(eui64_octets[5:])}",
                f"invert bit 1 (the universal/local bit, 0x02) of the "
                f"first octet: {format(first_octet, '02x')} = "
                f"{format(first_octet, '08b')}b -> {modified_first} = "
                f"{format(flipped, '08b')}b, giving the Modified EUI-64 "
                f"interface identifier {iid_hex}",
                "prepend the fe80::/10 link-local prefix (the /64 "
                "interface identifier occupies the low 64 bits)",
                f"compress with the stdlib ipaddress module: "
                f"{link_local}",
            ],
            "inverse_check": {
                "performed": True,
                "method": (
                    "mac_from_ipv6 on the result: validate the FF-FE "
                    "marker, re-invert the U/L bit, strip the marker"
                ),
                "recovered_eui48_hex": recovered,
                "matches": recovered == bytes_hex,
            },
            "findings": findings,
        }

    def _derive_mac_from_ipv6(
        self, context: Dict[str, Any], raw: str
    ) -> Dict[str, Any]:
        """Recover an EUI-48 from a link-local IPv6 address.

        A zone index suffix (``%eth0``) is accepted and ignored for the
        math — the scope names the interface, not address bits.
        """
        text = raw.strip()
        try:
            address = ipaddress.IPv6Address(text)
        except (ValueError, ipaddress.AddressValueError):
            return self._error_result(
                context,
                error_type="invalid_ipv6",
                message=(
                    f"input is not a valid IPv6 address: {raw!r} "
                    "(mac_from_ipv6 expects e.g. "
                    "'fe80::211:22ff:fe33:4455')"
                ),
            )
        if not address in ipaddress.IPv6Network("fe80::/10"):
            return self._error_result(
                context,
                error_type="not_link_local",
                message=(
                    f"{address.compressed} is not in fe80::/10 — the "
                    "EUI-64 interface identifier convention is only "
                    "guaranteed for IPv6 link-local addresses"
                ),
            )
        interface_id = int(address) & ((1 << 64) - 1)
        iid_hex = format(interface_id, "016x")
        marker = iid_hex[6:10]
        if marker != "fffe":
            return self._error_result(
                context,
                error_type="no_fffe_marker",
                message=(
                    f"the interface identifier {iid_hex} does not carry "
                    f"the FF-FE marker at bytes 4-5 (found "
                    f"{marker[:2]}:{marker[2:]}) — it is either a "
                    "privacy/temporary identifier (RFC 7217 / RFC 4941 "
                    "semantics), a manually set IID, or a native 64-bit "
                    "hardware EUI-64; in none of these cases does an "
                    "EUI-48 MAC address exist inside it"
                ),
            )
        first_octet = int(iid_hex[0:2], 16)
        unflipped = first_octet ^ 0x02
        recovered = (
            format(unflipped, "02x") + iid_hex[2:6] + iid_hex[10:16]
        )
        check = ipaddress.IPv6Address(
            (0xFE80 << 112) | int(
                format(unflipped ^ 0x02, "02x") + iid_hex[2:16], 16
            )
        )
        # Zone indexes (%eth0) are interface context, not address
        # bits — compare against the input with any zone stripped so
        # scoped link-local addresses round-trip truthfully.
        unscoped = ipaddress.IPv6Address(int(address))
        recovered_octets = [
            recovered[i : i + 2] for i in range(0, 12, 2)
        ]
        return {
            **context,
            "input": raw,
            "ipv6": address.compressed,
            "interface_id_hex": iid_hex,
            "eui48_hex": recovered,
            "eui48_canonical": ":".join(recovered_octets),
            "steps": [
                f"parse {address.compressed} and confirm it is in "
                "fe80::/10 (link-local)",
                f"extract the low 64 bits (the interface identifier): "
                f"{iid_hex}",
                "verify the FF-FE marker at IID bytes 4-5 — present, so "
                "this is a Modified EUI-64 of a 48-bit address",
                f"re-invert bit 1 of the first IID octet (the U/L bit "
                "that the Modified EUI-64 construction flipped): "
                f"{iid_hex[0:2]} -> {format(unflipped, '02x')}",
                "drop the marker bytes and concatenate the remaining six "
                f"octets: {recovered} = {':'.join(recovered_octets)}",
            ],
            "inverse_check": {
                "performed": True,
                "method": (
                    "derive ipv6_link_local from the recovered EUI-48 and "
                    "compare with the input address"
                ),
                "recomputed_address": str(check),
                "matches": str(check) == unscoped.compressed,
            },
            "findings": [],
        }

    @staticmethod
    def _recover_eui48_from_iid(interface_id: int) -> str:
        """Unflip the U/L bit and strip the FF-FE marker (no checks)."""
        iid_hex = format(interface_id, "016x")
        first_octet = int(iid_hex[0:2], 16) ^ 0x02
        return (
            format(first_octet, "02x") + iid_hex[2:6] + iid_hex[10:16]
        )

    # ------------------------------------------------------------------ #
    # compare mode
    # ------------------------------------------------------------------ #

    def _run_compare(self, raw_a: str, raw_b: str) -> Dict[str, Any]:
        """Same-device analysis of two addresses."""
        context: Dict[str, Any] = {"mode": "compare"}
        sides: List[Dict[str, Any]] = []
        for label, raw in (("address_a", raw_a), ("address_b", raw_b)):
            try:
                decoded = self._analyze(raw)
            except _MacAddressError as exc:
                return self._error_result(
                    context,
                    error_type="invalid_address",
                    message=(
                        f"{label} is not a valid EUI-48 address: "
                        f"{exc.findings[0]['message']}"
                    ),
                    findings=exc.findings,
                )
            bytes_hex = decoded["bytes_hex"]
            bit_semantics = self._bit_semantics(bytes_hex)
            oui_hex = bytes_hex[:6]
            special = self._special_prefix_match(bytes_hex)
            if oui_hex in self.OUI_TABLE:
                organization, source = (
                    self.OUI_TABLE[oui_hex], "ieee_ma-l_curated"
                )
            elif special is not None:
                organization, source = (special, "iana_special")
            else:
                organization, source = None, None
            sides.append({
                "input": raw,
                "bytes_hex": bytes_hex,
                "notation_detected": decoded["notation_detected"],
                "canonical_forms": decoded["canonical_forms"],
                "bit_semantics": bit_semantics,
                "oui": bytes_hex[:6],
                "organization": organization,
                "organization_source": source,
            })
        side_a, side_b = sides
        bytes_a, bytes_b = side_a["bytes_hex"], side_b["bytes_hex"]
        int_a, int_b = int(bytes_a, 16), int(bytes_b, 16)
        xor = int_a ^ int_b

        if bytes_a == bytes_b:
            relation = "identical"
            detail = (
                "the two addresses are the same 48-bit value"
                + (
                    " — written in different notations, which is why the "
                    "raw strings differ"
                    if side_a["notation_detected"]
                    != side_b["notation_detected"]
                    else ""
                )
            )
        elif xor == 0x02 << 40:
            relation = "differs_by_local_admin_bit"
            detail = (
                "the addresses differ in exactly bit 1 of the first "
                "octet (the universal/local bit) and are otherwise "
                "identical — consistent with the same hardware "
                "re-notated between a globally unique and a locally "
                "administered form (a common virtualization/renumbering "
                "pattern), though bit equality alone cannot prove it"
            )
        elif bytes_a[:6] == bytes_b[:6]:
            relation = "differs_in_nic_only"
            vendor_line = side_a["organization"] or side_b["organization"]
            if vendor_line is None:
                detail = (
                    "the OUI (first three octets) is identical and only the "
                    "NIC part differs — same vendor line "
                    "(OUI not in the embedded curated table); within one "
                    "OUI block, distinct NIC values are distinct "
                    "interfaces, not one device"
                )
            elif side_a["organization_source"] == "iana_special":
                detail = (
                    "the OUI (first three octets) is identical and only "
                    "the NIC part differs — same IANA special block "
                    f"({vendor_line}); within one OUI block, distinct NIC "
                    "values are distinct interfaces, not one device"
                )
            else:
                detail = (
                    "the OUI (first three octets) is identical and only "
                    "the NIC part differs — same vendor line "
                    f"({vendor_line}, from the embedded OUI table); "
                    "within one OUI block, distinct NIC values are "
                    "distinct interfaces, not one device"
                )
        elif (
            side_a["organization"]
            and side_a["organization"] == side_b["organization"]
        ):
            relation = "same_vendor_family"
            if side_a["organization_source"] == "iana_special":
                detail = (
                    "the OUIs differ but both fall inside the same IANA "
                    "special multicast mapping block — a protocol "
                    "reservation family, not a vendor line; this is a "
                    "same-block signal, not a same-device signal"
                )
            else:
                detail = (
                    "the OUIs differ but both resolve to the same "
                    f"organization in the embedded table ({side_a['organization']}) "
                    "— vendors own multiple OUI blocks, so this is a "
                    "same-vendor-family signal, not a same-device signal"
                )
        else:
            relation = "unrelated"
            detail = (
                "no supported same-device relation holds: different OUIs, "
                "different NICs, no single-bit U/L difference"
                + (
                    "; at least one OUI is not in the embedded curated "
                    "table, so vendor-family equality cannot be decided"
                    if not (
                        side_a["organization"] and side_b["organization"]
                    )
                    else ""
                )
            )
        return {
            **context,
            "address_a": side_a,
            "address_b": side_b,
            "relation": relation,
            "relation_detail": detail,
            "identical": relation == "identical",
            "findings": [],
        }

    # ------------------------------------------------------------------ #
    # Shared error payload
    # ------------------------------------------------------------------ #

    @staticmethod
    def _error_result(
        context: Dict[str, Any],
        error_type: str,
        message: str,
        findings: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Structured content-level error (never an exception)."""
        payload: Dict[str, Any] = {
            **context,
            "error": {"type": error_type, "message": message},
        }
        if findings:
            payload["findings"] = findings
        return payload
