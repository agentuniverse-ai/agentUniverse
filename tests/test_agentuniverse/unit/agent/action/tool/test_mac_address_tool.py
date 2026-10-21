#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: test_mac_address_tool.py

"""Offline unit tests for MacAddressTool.

The tool is built purely on the Python standard library and never
touches the network, so this suite runs fully offline. Every
assertion is deterministic and backed by an *independent* oracle:

* notation battery — 400 seeded addresses are rendered by the test
  into all six notations and checked against a regex-based reference
  parser written independently of the tool's split-based logic, plus
  hostile mutations (11/13 bare hex digits, 'gg' groups, mixed
  separators, wrong Cisco group lengths, fullwidth digits, mixed
  case) whose verdicts and finding positions are computed test-side;
* bit semantics — a hand-written truth table of the first octet's
  low two bits (I/G and U/L) plus the broadcast / zero specials;
* IPv6 derivation — 200 seeded EUI-48 addresses go through
  ipv6_link_local and back through mac_from_ipv6 (round trip), with
  the link-local address recomputed independently from the seed, and
  ten famous hand-verified vectors pinned as literals;
* OUI integrity — the embedded curated table is asserted equal to a
  static fixture copied from the public IEEE MA-L registry at
  test-authoring time (no network); misses report unknown_oui
  instead of crashing.

The seeded stream is hashlib-based (no random module), so the suite
is byte-for-byte reproducible across runs and platforms.
"""

import hashlib
import ipaddress
import json
import re
import unittest

from agentuniverse.agent.action.tool.common_tool import MacAddressTool
from agentuniverse.agent.action.tool.common_tool.mac_address_tool import (
    MacAddressTool as DirectMacAddressTool,
)

# --------------------------------------------------------------------- #
# Deterministic seed stream (hashlib, no random module)
# --------------------------------------------------------------------- #


def seeded_eui48(index: int) -> str:
    """Deterministic 48-bit address hex for an integer index."""
    material = b"mac-address-tool-oracle/" + str(index).encode("ascii")
    digest = b""
    counter = 0
    while len(digest) < 6:
        digest += hashlib.blake2b(
            material + b"/" + str(counter).encode("ascii"), digest_size=6
        ).digest()
        counter += 1
    return digest[:6].hex()


# --------------------------------------------------------------------- #
# Independent reference parser (regex-based, not the tool's logic)
# --------------------------------------------------------------------- #

REF_PATTERNS = {
    "colon": re.compile(
        r"\A([0-9a-fA-F]{2}):([0-9a-fA-F]{2}):([0-9a-fA-F]{2})"
        r":([0-9a-fA-F]{2}):([0-9a-fA-F]{2}):([0-9a-fA-F]{2})\Z"
    ),
    "hyphen": re.compile(
        r"\A([0-9a-fA-F]{2})-([0-9a-fA-F]{2})-([0-9a-fA-F]{2})"
        r"-([0-9a-fA-F]{2})-([0-9a-fA-F]{2})-([0-9a-fA-F]{2})\Z"
    ),
    "cisco_dotted": re.compile(
        r"\A([0-9a-fA-F]{4})\.([0-9a-fA-F]{4})\.([0-9a-fA-F]{4})\Z"
    ),
    "bare": re.compile(r"\A([0-9a-fA-F]{12})\Z"),
    "prefixed": re.compile(r"\A0x([0-9a-fA-F]{12})\Z"),
    "dotted_pairs": re.compile(
        r"\A([0-9a-fA-F]{2})\.([0-9a-fA-F]{2})\.([0-9a-fA-F]{2})"
        r"\.([0-9a-fA-F]{2})\.([0-9a-fA-F]{2})\.([0-9a-fA-F]{2})\Z"
    ),
}


def ref_render(bytes_hex: str, notation: str) -> str:
    """Render canonical lowercase bytes into one of the six notations."""
    octets = [bytes_hex[i : i + 2] for i in range(0, 12, 2)]
    if notation == "colon":
        return ":".join(octets)
    if notation == "hyphen":
        return "-".join(octets)
    if notation == "cisco_dotted":
        return (
            f"{octets[0]}{octets[1]}.{octets[2]}{octets[3]}."
            f"{octets[4]}{octets[5]}"
        )
    if notation == "bare":
        return bytes_hex
    if notation == "prefixed":
        return "0x" + bytes_hex
    if notation == "dotted_pairs":
        return ".".join(octets)
    raise AssertionError(notation)


def ref_parse(text: str):
    """Independent reference verdict: (bytes_hex, notation) or None."""
    for notation, pattern in REF_PATTERNS.items():
        match = pattern.match(text)
        if match:
            return "".join(group.lower() for group in match.groups()), notation
    return None


def ref_ipv6_link_local(bytes_hex: str) -> str:
    """Independent RFC 4291 Modified EUI-64 computation."""
    first = int(bytes_hex[0:2], 16) ^ 0x02
    iid = format(first, "02x") + bytes_hex[2:6] + "fffe" + bytes_hex[6:]
    return str(ipaddress.IPv6Address((0xFE80 << 112) | int(iid, 16)))


# --------------------------------------------------------------------- #
# Static OUI fixture — copied verbatim from the public IEEE MA-L
# registry (https://standards-oui.ieee.org/oui/oui.csv) at
# test-authoring time (2026-10-21). The tool's embedded table must
# match this snapshot exactly; no network is used at test time.
# --------------------------------------------------------------------- #

OUI_REGISTRY_FIXTURE = {
    "000001": "XEROX CORPORATION",
    "0000aa": "XEROX CORPORATION",
    "00000c": "Cisco Systems, Inc",
    "001b0d": "Cisco Systems, Inc",
    "0022bd": "Cisco Systems, Inc",
    "58971e": "Cisco Systems, Inc",
    "00270d": "Cisco Systems, Inc",
    "000121": "WatchGuard Technologies, Inc.",
    "000c41": "Cisco-Linksys, LLC",
    "0014bf": "Cisco-Linksys, LLC",
    "002369": "Cisco-Linksys, LLC",
    "001d7e": "Cisco-Linksys, LLC",
    "08002b": "DIGITAL EQUIPMENT CORPORATION",
    "0000f8": "DIGITAL EQUIPMENT CORPORATION",
    "080020": "Oracle Corporation",
    "0021f6": "Oracle Corporation",
    "00001b": "Novell, Inc.",
    "0020af": "3COM",
    "00608c": "3COM",
    "02608c": "3COM",
    "0004ac": "IBM Corp",
    "002035": "IBM Corp",
    "5cf3fc": "IBM Corp",
    "0002b3": "Intel Corporation",
    "002710": "Intel Corporate",
    "3ca9f4": "Intel Corporate",
    "a0369f": "Intel Corporate",
    "000393": "Apple, Inc.",
    "0021e9": "Apple, Inc.",
    "002500": "Apple, Inc.",
    "002608": "Apple, Inc.",
    "f01898": "Apple, Inc.",
    "3c0754": "Apple, Inc.",
    "10ddb1": "Apple, Inc.",
    "a45e60": "Apple, Inc.",
    "2c200b": "Apple, Inc.",
    "acde48": "Private",
    "001422": "Dell Inc.",
    "f8db88": "Dell Inc.",
    "8cec4b": "Dell Inc.",
    "001a4b": "Hewlett Packard",
    "001f29": "Hewlett Packard",
    "3cd92b": "Hewlett Packard",
    "000b86": "Hewlett Packard Enterprise",
    "24dec6": "Hewlett Packard Enterprise",
    "001882": "HUAWEI TECHNOLOGIES CO.,LTD",
    "286ed4": "HUAWEI TECHNOLOGIES CO.,LTD",
    "58605f": "HUAWEI TECHNOLOGIES CO.,LTD",
    "781dba": "HUAWEI TECHNOLOGIES CO.,LTD",
    "d4612e": "HUAWEI TECHNOLOGIES CO.,LTD",
    "002389": "Hangzhou H3C Technologies Co., Limited",
    "001632": "Samsung Electronics Co.,Ltd",
    "002454": "Samsung Electronics Co.,Ltd",
    "0024e9": "Samsung Electronics Co.,Ltd",
    "8c7712": "Samsung Electronics Co.,Ltd",
    "0022a9": "LG Electronics (Mobile Communications)",
    "10683f": "LG Electronics (Mobile Communications)",
    "64bc0c": "LG Electronics (Mobile Communications)",
    "00014a": "Sony Corporation",
    "0024be": "Sony Corporation",
    "001dbc": "Nintendo Co., Ltd.",
    "0025a0": "Nintendo Co., Ltd.",
    "002659": "Nintendo Co., Ltd.",
    "00e04c": "REALTEK SEMICONDUCTOR CORP.",
    "001018": "Broadcom",
    "005043": "MARVELL SEMICONDUCTOR, INC.",
    "00044b": "NVIDIA",
    "00037f": "Atheros Communications, Inc.",
    "0026e8": "Murata Manufacturing Co., Ltd.",
    "006057": "Murata Manufacturing Co., Ltd.",
    "000569": "VMware, Inc.",
    "000c29": "VMware, Inc.",
    "005056": "VMware, Inc.",
    "0003ff": "Microsoft Corporation",
    "00155d": "Microsoft Corporation",
    "0050f2": "MICROSOFT CORP.",
    "00163e": "Xensource, Inc.",
    "001c42": "Parallels, Inc.",
    "00a098": "NetApp",
    "0090a9": "WESTERN DIGITAL",
    "001075": "Segate Technology LLC",
    "002590": "Super Micro Computer, Inc.",
    "0cc47a": "Super Micro Computer, Inc.",
    "000d61": "Giga-Byte Technology Co., Ltd.",
    "000c6e": "ASUSTek COMPUTER INC.",
    "ac9e17": "ASUSTek COMPUTER INC.",
    "04d9f5": "ASUSTek COMPUTER INC.",
    "00016c": "FOXCONN",
    "54ee75": "Wistron InfoComm(Kunshan)Co.,Ltd.",
    "005907": "LenovoEMC Products USA, LLC",
    "106f3f": "BUFFALO.INC",
    "00095b": "NETGEAR",
    "a040a0": "NETGEAR",
    "00055d": "D-LINK SYSTEMS, INC.",
    "001e58": "D-Link Corporation",
    "0023cd": "TP-LINK TECHNOLOGIES CO.,LTD.",
    "002719": "TP-LINK TECHNOLOGIES CO.,LTD.",
    "50c7bf": "TP-LINK TECHNOLOGIES CO.,LTD.",
    "00a0c5": "Zyxel Communications Corporation",
    "4c9eff": "Zyxel Communications Corporation",
    "001150": "Belkin Corporation",
    "c05627": "Belkin International Inc.",
    "000585": "Juniper Networks",
    "001f12": "Juniper Networks",
    "0418d6": "Ubiquiti Inc",
    "f09fc2": "Ubiquiti Inc",
    "c84f86": "Sophos Ltd",
    "00869c": "Palo Alto Networks",
    "00a08e": "Check Point Software Technologies",
    "7478a6": "Fortinet, Inc.",
    "0006b1": "Sonicwall",
    "085531": "Routerboard.com",
    "44650d": "Amazon Technologies Inc.",
    "74c246": "Amazon Technologies Inc.",
    "f04f7c": "Amazon Technologies Inc.",
    "f4f5d8": "Google, Inc.",
    "4857dd": "Facebook Inc",
    "480560": "Meta Platforms, Inc.",
    "8cbebe": "Xiaomi Communications Co Ltd",
    "3c8cf8": "TRENDnet, Inc.",
    "b827eb": "Raspberry Pi Foundation",
    "dca632": "Raspberry Pi Trading Ltd",
    "e45f01": "Raspberry Pi Trading Ltd",
    "240ac4": "Espressif Inc.",
    "30aea4": "Espressif Inc.",
    "a4cf12": "Espressif Inc.",
    "0024fe": "AVM GmbH",
    "001788": "Philips Lighting BV",
    "c42996": "Signify B.V.",
    "90ece3": "Nokia",
    "e04735": "Ericsson AB",
    "001b1b": "Siemens AG,",
    "008045": "MATSUSHITA ELECTRIC IND. CO",
    "84ba3b": "CANON INC.",
    "008077": "Brother industries, LTD.",
    "a4d73c": "Seiko Epson Corporation",
    "583879": "RICOH COMPANY, LTD.",
    "9075de": "Zebra Technologies Inc.",
    "004084": "Honeywell",
    "000496": "Extreme Networks, Inc.",
    "0c75d2": "Hangzhou Hikvision Digital Technology Co.,Ltd.",
    "244845": "Hangzhou Hikvision Digital Technology Co.,Ltd.",
    "74c929": "Zhejiang Dahua Technology Co., Ltd.",
    "0050c2": "IEEE Registration Authority",
    "00005e": "ICANN, IANA Department",
}


class MacAddressToolMetadataTest(unittest.TestCase):
    """Contract-level checks shared by every mode."""

    def setUp(self) -> None:
        self.tool = MacAddressTool()

    def test_import_paths(self) -> None:
        self.assertIs(MacAddressTool, DirectMacAddressTool)

    def test_metadata(self) -> None:
        self.assertEqual(self.tool.name, "mac_address_tool")
        self.assertIn("MacAddressTool", type(self.tool).__name__)
        self.assertIn("mode='parse'", self.tool.description)
        self.assertIn("mode='lookup'", self.tool.description)
        self.assertIn("mode='derive'", self.tool.description)
        self.assertIn("mode='compare'", self.tool.description)

    def test_unknown_mode_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="sniff")
        with self.assertRaises(ValueError):
            self.tool.execute(mode=None, address="aa:bb:cc:dd:ee:ff")

    def test_bad_parameter_types_raise(self) -> None:
        for bad in (None, 123, True, ["aa:bb:cc:dd:ee:ff"], b"aabbccddeeff"):
            for kwargs in (
                {"mode": "parse", "address": bad},
                {"mode": "lookup", "address": bad},
                {"mode": "compare", "address_a": "00:11:22:33:44:55",
                 "address_b": bad},
            ):
                with self.assertRaises(ValueError):
                    self.tool.execute(**kwargs)

    def test_empty_and_oversized_addresses_raise(self) -> None:
        for bad in ("", "   ", "\t\n"):
            with self.assertRaises(ValueError):
                self.tool.execute(mode="parse", address=bad)
        with self.assertRaises(ValueError):
            self.tool.execute(mode="parse", address="0" * 65)
        with self.assertRaises(ValueError):
            self.tool.execute(
                mode="compare",
                address_a="0" * 65,
                address_b="aa:bb:cc:dd:ee:ff",
            )

    def test_bad_derivation_and_marker_raise(self) -> None:
        for bad in (None, "eui64", "ipv6", 7):
            with self.assertRaises(ValueError):
                self.tool.execute(
                    mode="derive",
                    address="00:11:22:33:44:55",
                    derivation=bad,
                )
        for bad in ("gggg", "", 123, True):
            with self.assertRaises(ValueError):
                self.tool.execute(
                    mode="parse",
                    address="00:11:22:33:44:55",
                    eui64_marker=bad,
                )

    def test_determinism(self) -> None:
        first = self.tool.execute(
            mode="parse", address="AC:DE:48:00:11:22", eui64_marker="fffe"
        )
        second = self.tool.execute(
            mode="parse", address="ac:de:48:00:11:22", eui64_marker="fffe"
        )
        # Same input in different case: identical payload except raw echo.
        first.pop("input")
        second.pop("input")
        self.assertEqual(json.dumps(first, sort_keys=True),
                         json.dumps(second, sort_keys=True))
        repeat = self.tool.execute(
            mode="derive",
            address="02:11:22:33:44:55",
            derivation="ipv6_link_local",
        )
        again = self.tool.execute(
            mode="derive",
            address="02:11:22:33:44:55",
            derivation="ipv6_link_local",
        )
        self.assertEqual(json.dumps(repeat, sort_keys=True),
                         json.dumps(again, sort_keys=True))


class MacAddressToolParseTest(unittest.TestCase):
    """Notation battery: 400 seeds x 6 notations + hostile mutations."""

    SEEDS = 400

    def setUp(self) -> None:
        self.tool = MacAddressTool()

    def test_notation_battery_vs_reference(self) -> None:
        failures = []
        for index in range(self.SEEDS):
            bytes_hex = seeded_eui48(index)
            for notation in REF_PATTERNS:
                rendered = ref_render(bytes_hex, notation)
                verdict = self.tool.execute(
                    mode="parse", address=rendered
                )
                reference = ref_parse(rendered)
                if reference is None:
                    failures.append(
                        f"seed {index} {notation}: reference rejected its "
                        f"own rendering {rendered!r}"
                    )
                    continue
                ref_bytes, ref_notation = reference
                if not verdict.get("valid"):
                    failures.append(
                        f"seed {index} {notation}: tool rejected valid "
                        f"{rendered!r}: {verdict.get('findings')}"
                    )
                elif verdict["bytes_hex"] != ref_bytes:
                    failures.append(
                        f"seed {index} {notation}: bytes "
                        f"{verdict['bytes_hex']} != reference {ref_bytes}"
                    )
                elif verdict["notation_detected"] != ref_notation:
                    failures.append(
                        f"seed {index} {notation}: notation "
                        f"{verdict['notation_detected']} != {ref_notation}"
                    )
                elif verdict["bytes_hex"] != bytes_hex:
                    failures.append(f"seed {index} {notation}: seed mismatch")
                elif verdict["canonical_forms"]["cisco_dotted"] != (
                    f"{bytes_hex[0:4]}.{bytes_hex[4:8]}.{bytes_hex[8:12]}"
                ):
                    failures.append(
                        f"seed {index} {notation}: canonical forms broken"
                    )
        self.assertEqual(
            failures[:5], [], f"{len(failures)} battery failures: "
            f"{failures[:5]}"
        )

    def test_uppercase_and_mixed_case_accepted(self) -> None:
        for index in range(50):
            bytes_hex = seeded_eui48(index)
            for variant in (
                bytes_hex.upper(),
                "".join(
                    c.upper() if position % 2 else c
                    for position, c in enumerate(bytes_hex)
                ),
                ref_render(bytes_hex, "colon").upper(),
                ref_render(bytes_hex, "cisco_dotted").upper(),
                "0X" + bytes_hex.upper(),
            ):
                verdict = self.tool.execute(mode="parse", address=variant)
                self.assertTrue(
                    verdict["valid"], f"case variant {variant!r} rejected"
                )
                self.assertEqual(verdict["bytes_hex"], bytes_hex)

    def test_mutation_wrong_total_length(self) -> None:
        for index in range(100):
            bytes_hex = seeded_eui48(index)
            for mutated, label in (
                (bytes_hex[:-1], "11 digits"),
                (bytes_hex + "0", "13 digits"),
                ("0x" + bytes_hex[:-1], "prefixed 11 digits"),
                ("0x" + bytes_hex + "f", "prefixed 13 digits"),
            ):
                verdict = self.tool.execute(mode="parse", address=mutated)
                self.assertFalse(
                    verdict["valid"], f"{label} {mutated!r} accepted"
                )
                codes = [f["code"] for f in verdict["findings"]]
                self.assertIn(
                    "wrong_total_length", codes,
                    f"{label} {mutated!r}: findings {verdict['findings']}",
                )

    def test_mutation_bad_hex_digit_position(self) -> None:
        for index in range(100):
            bytes_hex = seeded_eui48(index)
            groups = [bytes_hex[i : i + 2] for i in range(0, 12, 2)]
            for slot in (0, 2, 5):
                mutated = groups[:]
                mutated[slot] = "gg"
                rendered = ":".join(mutated)
                verdict = self.tool.execute(mode="parse", address=rendered)
                self.assertFalse(verdict["valid"])
                finding = verdict["findings"][0]
                self.assertEqual(finding["code"], "bad_hex_digit")
                expected_position = rendered.index("g") + 1
                self.assertEqual(
                    finding["position"], expected_position,
                    f"position for {rendered!r}",
                )
            # Same defect in the bare notation.
            bare_bad = "aa" + "g" + bytes_hex[3:]
            verdict = self.tool.execute(mode="parse", address=bare_bad)
            self.assertFalse(verdict["valid"])
            self.assertEqual(
                verdict["findings"][0]["code"], "bad_hex_digit"
            )
            self.assertEqual(
                verdict["findings"][0]["position"],
                bare_bad.index("g") + 1,
            )

    def test_prefixed_position_base_is_the_input_string(self) -> None:
        # Positions must be 1-based within the input string for every
        # notation, including the lenient '0x' + separated hybrid —
        # the prefixed bare form already offsets by the two prefix
        # characters, so the grouped forms must agree with it.
        rendered = "0xAA:BB:CC:DD:EE:FG"
        verdict = self.tool.execute(mode="parse", address=rendered)
        self.assertFalse(verdict["valid"])
        finding = verdict["findings"][0]
        self.assertEqual(finding["code"], "bad_hex_digit")
        self.assertEqual(finding["position"], rendered.index("G") + 1)
        rendered = "0xAA:BB-CC:DD:EE:FF"
        verdict = self.tool.execute(mode="parse", address=rendered)
        finding = verdict["findings"][0]
        self.assertEqual(finding["code"], "mixed_separators")
        self.assertEqual(finding["position"], rendered.index("-") + 1)
        # The prefixed bare form keeps its raw-relative position.
        rendered = "0x" + "aabbccddeefg"
        verdict = self.tool.execute(mode="parse", address=rendered)
        self.assertEqual(
            verdict["findings"][0]["position"], rendered.index("g") + 1
        )

    def test_mutation_mixed_separators(self) -> None:
        for index in range(100):
            bytes_hex = seeded_eui48(index)
            groups = [bytes_hex[i : i + 2] for i in range(0, 12, 2)]
            for sep_mix in (
                groups[:2] + ["-".join(groups[2:4])] + groups[4:],
                [".".join(groups[:2])] + groups[1:],
            ):
                rendered = ":".join(sep_mix)
                verdict = self.tool.execute(mode="parse", address=rendered)
                self.assertFalse(
                    verdict["valid"], f"mixed separators {rendered!r} taken"
                )
                finding = verdict["findings"][0]
                self.assertEqual(finding["code"], "mixed_separators")
                first_separator = next(
                    char for char in rendered if char in ":.-"
                )
                deviating = next(
                    char for char in rendered
                    if char in ":.-" and char != first_separator
                )
                self.assertEqual(
                    finding["position"], rendered.index(deviating) + 1
                )

    def test_mutation_dotted_structure(self) -> None:
        cases = {
            "aab.ccdd.eeff": "wrong_group_length",
            "aabb.ccdd.ee.ff": "wrong_group_count",
            "aabbcc.ddeeff": "wrong_group_count",
            "aa.bb.cc.dd.ee": "wrong_group_count",
            "aa.bbb.cc.dd.ee.ff": "wrong_group_length",
            "aabb.ccdd.eef": "wrong_group_length",
            "aa.bb.ccc.dd.ee.ff": "wrong_group_length",
        }
        for mutated, expected_code in cases.items():
            verdict = self.tool.execute(mode="parse", address=mutated)
            self.assertFalse(
                verdict["valid"], f"{mutated!r} accepted"
            )
            codes = [f["code"] for f in verdict["findings"]]
            self.assertIn(
                expected_code, codes,
                f"{mutated!r}: expected {expected_code}, got {codes}",
            )

    def test_mutation_group_count_colon_hyphen(self) -> None:
        for mutated, expected_code in {
            "aa:bb:cc:dd:ee": "wrong_group_count",
            "aa:bb:cc:dd:ee:ff:00": "wrong_group_count",
            "aa:bb:cc:dd:ee:fff": "wrong_group_length",
            "aa-bb-cc-dd-e-f": "wrong_group_length",
            "aa:bb:cc:dd:ee:": "wrong_group_length",
            "aa-bb-cc-dd-ee-ff-f0": "wrong_group_count",
        }.items():
            verdict = self.tool.execute(mode="parse", address=mutated)
            self.assertFalse(verdict["valid"], f"{mutated!r} accepted")
            codes = [f["code"] for f in verdict["findings"]]
            self.assertIn(expected_code, codes, mutated)

    def test_fullwidth_and_unicode_rejected(self) -> None:
        for mutated in (
            "\uff41\uff41:bb:cc:dd:ee:ff",  # fullwidth 'a'
            "aa:bb:cc:dd:ee:\uff46\uff46",  # fullwidth 'f'
            "\uff11\uff12aabbccddeeff",  # fullwidth digits
            "aa:bb:cc:dd:ee:f\uff46",
            "aa:bb:cc:dd:ee:f\u20ac",  # euro sign
        ):
            verdict = self.tool.execute(mode="parse", address=mutated)
            self.assertFalse(
                verdict["valid"], f"unicode {mutated!r} accepted"
            )
            finding = verdict["findings"][0]
            self.assertEqual(finding["code"], "non_ascii_character")
            self.assertEqual(
                finding["position"],
                next(
                    position + 1
                    for position, char in enumerate(mutated)
                    if ord(char) > 0x7F
                ),
            )

    def test_whitespace_only_edges(self) -> None:
        verdict = self.tool.execute(mode="parse", address="  aa:bb:cc:dd:ee:ff ")
        self.assertTrue(verdict["valid"])
        self.assertEqual(verdict["bytes_hex"], "aabbccddeeff")
        # Interior whitespace is a (reportable) defect, not a strip target.
        verdict = self.tool.execute(mode="parse", address="aa: bb:cc:dd:ee:ff")
        self.assertFalse(verdict["valid"])

    def test_parse_eui64_marker_flag(self) -> None:
        base = "00:11:22:33:44:55"
        default = self.tool.execute(mode="parse", address=base)
        self.assertEqual(default["eui64_marker"], "ffff")
        self.assertEqual(default["eui64_hex"], "001122ffff334455")
        fffe = self.tool.execute(
            mode="parse", address=base, eui64_marker="fffe"
        )
        self.assertEqual(fffe["eui64_marker"], "fffe")
        self.assertEqual(fffe["eui64_hex"], "001122fffe334455")


class MacAddressToolBitSemanticsTest(unittest.TestCase):
    """Hand-written truth table of the first octet's low two bits."""

    def setUp(self) -> None:
        self.tool = MacAddressTool()

    # (first octet, binary, local_admin (bit 1), multicast (bit 0))
    HAND_TABLE = (
        (0x00, "00000000", False, False),
        (0x01, "00000001", False, True),
        (0x02, "00000010", True, False),
        (0x03, "00000011", True, True),
        (0x10, "00010000", False, False),
        (0x11, "00010001", False, True),
        (0x12, "00010010", True, False),
        (0x13, "00010011", True, True),
        (0x55, "01010101", False, True),
        (0x7F, "01111111", True, True),
        (0x80, "10000000", False, False),
        (0xAA, "10101010", True, False),
        (0xFC, "11111100", False, False),
        (0xFD, "11111101", False, True),
        (0xFE, "11111110", True, False),
        (0xFF, "11111111", True, True),
    )

    def test_hand_table(self) -> None:
        for octet, binary, local_admin, multicast in self.HAND_TABLE:
            address = f"{octet:02x}:11:22:33:44:55"
            verdict = self.tool.execute(mode="parse", address=address)
            self.assertTrue(verdict["valid"], address)
            bits = verdict["bit_semantics"]
            self.assertEqual(
                bits["local_admin"], local_admin,
                f"U/L bit for first octet {binary}",
            )
            self.assertEqual(
                bits["multicast"], multicast,
                f"I/G bit for first octet {binary}",
            )
            self.assertEqual(bits["first_octet_binary"], binary)
            self.assertEqual(bits["oui"], f"{octet:02x}:11:22")
            self.assertEqual(bits["nic"], "33:44:55")
            self.assertFalse(bits["is_broadcast"])
            self.assertFalse(bits["is_zero"])

    def test_specials(self) -> None:
        broadcast = self.tool.execute(
            mode="parse", address="ff:ff:ff:ff:ff:ff"
        )
        self.assertTrue(broadcast["bit_semantics"]["is_broadcast"])
        self.assertTrue(broadcast["bit_semantics"]["multicast"])
        self.assertTrue(broadcast["bit_semantics"]["local_admin"])
        self.assertIn("broadcast", " ".join(broadcast.get("notes", [])))
        zero = self.tool.execute(
            mode="parse", address="0000.0000.0000"
        )
        self.assertTrue(zero["bit_semantics"]["is_zero"])
        self.assertIn("unspecified", " ".join(zero.get("notes", [])))

    def test_locally_administered_classics(self) -> None:
        for address, local, multi in (
            ("02:00:00:00:00:00", True, False),  # the canonical local MAC
            ("02:11:22:33:44:55", True, False),
            ("01:00:5e:00:00:01", False, True),  # IPv4 multicast mapping
            ("33:33:00:00:00:01", True, True),  # IPv6 multicast mapping
            ("00:00:0c:12:34:56", False, False),  # Cisco unicast
            # 0xAC = 10101100b: both flag bits clear (globally unique).
            ("ac:de:48:00:11:22", False, False),
        ):
            verdict = self.tool.execute(mode="parse", address=address)
            bits = verdict["bit_semantics"]
            self.assertEqual(bits["local_admin"], local, address)
            self.assertEqual(bits["multicast"], multi, address)
            note = verdict["bits_note"]
            if local:
                self.assertIn("locally administered", note)
            else:
                self.assertIn("globally unique", note)
            if multi:
                self.assertIn("multicast", note)


class MacAddressToolDeriveTest(unittest.TestCase):
    """EUI-64 / IPv6 derivations against hand vectors and round trips."""

    def setUp(self) -> None:
        self.tool = MacAddressTool()

    # Hand-verified RFC 4291 Modified EUI-64 vectors. Each link-local
    # literal below was derived by hand: insert FF-FE between octet 3
    # and 4, invert bit 1 of the first octet (0x02 XOR), prepend
    # fe80::/10, then compress. Example walkthrough for the textbook
    # 00:11:22:33:44:55 -> 00^02=02, IID 0211:22ff:fe33:4455 ->
    # fe80::211:22ff:fe33:4455.
    HAND_VECTORS = {
        "00:11:22:33:44:55": "fe80::211:22ff:fe33:4455",
        "02:00:00:00:00:00": "fe80::ff:fe00:0",
        "00:00:00:00:00:00": "fe80::200:ff:fe00:0",
        "ff:ff:ff:ff:ff:ff": "fe80::fdff:ffff:feff:ffff",
        # QEMU/KVM de-facto prefix (52 has the U/L bit set; 52^02=50).
        "52:54:00:12:34:56": "fe80::5054:ff:fe12:3456",
        # AC-DE-48: registry 'Private', widely attributed to Apple.
        "ac:de:48:00:11:22": "fe80::aede:48ff:fe00:1122",
        # 08-00-20: the classic Sun Microsystems block (now Oracle).
        "08:00:20:11:22:33": "fe80::a00:20ff:fe11:2233",
        "00:00:0c:12:34:56": "fe80::200:cff:fe12:3456",
        # OpenStack Neutron's FA:16:3E locally administered prefix.
        "fa:16:3e:aa:bb:cc": "fe80::f816:3eff:feaa:bbcc",
        "3c:07:54:aa:bb:cc": "fe80::3e07:54ff:feaa:bbcc",
    }

    def test_hand_vectors_ipv6_link_local(self) -> None:
        for base, expected in self.HAND_VECTORS.items():
            result = self.tool.execute(
                mode="derive", address=base, derivation="ipv6_link_local"
            )
            self.assertEqual(
                result["link_local"], expected, f"vector {base}"
            )
            self.assertTrue(result["inverse_check"]["performed"])
            self.assertTrue(
                result["inverse_check"]["matches"], f"vector {base}"
            )
            self.assertTrue(result["steps"])
            # Independent recomputation from the seed.
            self.assertEqual(
                ref_ipv6_link_local(base.replace(":", "")),
                expected,
            )

    def test_round_trip_200_seeds(self) -> None:
        failures = []
        for index in range(200):
            bytes_hex = seeded_eui48(index)
            derived = self.tool.execute(
                mode="derive",
                address=bytes_hex,
                derivation="ipv6_link_local",
            )
            if not derived["inverse_check"]["matches"]:
                failures.append(
                    f"seed {index}: self inverse check failed"
                )
            if derived["link_local"] != ref_ipv6_link_local(bytes_hex):
                failures.append(f"seed {index}: reference mismatch")
            recovered = self.tool.execute(
                mode="derive",
                address=derived["link_local"],
                derivation="mac_from_ipv6",
            )
            if "eui48_hex" not in recovered:
                failures.append(
                    f"seed {index}: recovery failed: {recovered}"
                )
            elif recovered["eui48_hex"] != bytes_hex:
                failures.append(f"seed {index}: round trip mismatch")
            elif not recovered["inverse_check"]["matches"]:
                failures.append(f"seed {index}: recovery inverse failed")
        self.assertEqual(
            failures[:5], [], f"{len(failures)} round-trip failures"
        )

    def test_mac_from_ipv6_requires_fffe_marker(self) -> None:
        # IID 0211:22ab:cd33:4455 has no FF-FE marker -> structured error.
        result = self.tool.execute(
            mode="derive",
            address="fe80::211:22ab:cd33:4455",
            derivation="mac_from_ipv6",
        )
        self.assertEqual(result["error"]["type"], "no_fffe_marker")
        self.assertIn("FF-FE", result["error"]["message"])
        # FF-FF marker is NOT the Modified EUI-64 marker.
        result = self.tool.execute(
            mode="derive",
            address="fe80::211:22ff:ff33:4455",
            derivation="mac_from_ipv6",
        )
        self.assertEqual(result["error"]["type"], "no_fffe_marker")
        # A zero IID (fe80::) has no marker either.
        result = self.tool.execute(
            mode="derive", address="fe80::", derivation="mac_from_ipv6"
        )
        self.assertEqual(result["error"]["type"], "no_fffe_marker")

    def test_mac_from_ipv6_requires_link_local(self) -> None:
        for address in (
            "2001:db8::1",
            "::1",
            "2001:db8:0:0:0:211:22ff:fe33:4455",
            "fec0::211:22ff:fe33:4455",  # old site-local, not fe80::/10
        ):
            result = self.tool.execute(
                mode="derive", address=address, derivation="mac_from_ipv6"
            )
            self.assertIn(
                result["error"]["type"],
                ("not_link_local", "invalid_ipv6"),
                address,
            )
        result = self.tool.execute(
            mode="derive",
            address="not-an-address",
            derivation="mac_from_ipv6",
        )
        self.assertEqual(result["error"]["type"], "invalid_ipv6")

    def test_mac_from_ipv6_zone_index_round_trip(self) -> None:
        # The standard Linux link-local notation carries a zone index;
        # it must not break the inverse check (the zone names the
        # interface, not address bits).
        result = self.tool.execute(
            mode="derive",
            address="fe80::211:22ff:fe33:4455%eth0",
            derivation="mac_from_ipv6",
        )
        self.assertNotIn("error", result)
        self.assertEqual(result["eui48_canonical"], "00:11:22:33:44:55")
        self.assertTrue(result["inverse_check"]["matches"])
        self.assertEqual(
            result["inverse_check"]["recomputed_address"],
            "fe80::211:22ff:fe33:4455",
        )

    def test_eui64_markers(self) -> None:
        base = "00:11:22:33:44:55"
        for derivation, marker in (
            ("eui64_fffe", "fffe"),
            ("eui64_ffff", "ffff"),
        ):
            result = self.tool.execute(
                mode="derive", address=base, derivation=derivation
            )
            expected = "001122" + marker + "334455"
            self.assertEqual(result["eui64_hex"], expected)
            self.assertEqual(
                result["eui64_canonical"],
                ":".join(
                    expected[i : i + 2] for i in range(0, 16, 2)
                ),
            )
            self.assertTrue(result["inverse_check"]["matches"])
            self.assertEqual(
                result["inverse_check"]["recovered_eui48_hex"],
                "001122334455",
            )
            self.assertIn("marker", " ".join(result["steps"]))
        # 200 seeds for both markers against the reference formula.
        for index in range(200):
            bytes_hex = seeded_eui48(index)
            for marker in ("fffe", "ffff"):
                result = self.tool.execute(
                    mode="derive",
                    address=bytes_hex,
                    derivation=f"eui64_{marker}",
                )
                self.assertEqual(
                    result["eui64_hex"],
                    bytes_hex[:6] + marker + bytes_hex[6:],
                )

    def test_degenerate_bases_flagged_not_blocked(self) -> None:
        for base in ("00:00:00:00:00:00", "ff:ff:ff:ff:ff:ff"):
            result = self.tool.execute(
                mode="derive", address=base, derivation="ipv6_link_local"
            )
            codes = [f["code"] for f in result["findings"]]
            self.assertIn("degenerate_base", codes)
            self.assertIn("link_local", result)

    def test_derive_invalid_base_is_structured_error(self) -> None:
        for bad in ("aa:bb:cc:dd:ee", "gg:bb:cc:dd:ee:ff", "0x123"):
            result = self.tool.execute(
                mode="derive", address=bad, derivation="ipv6_link_local"
            )
            self.assertEqual(result["error"]["type"], "invalid_address")


class MacAddressToolLookupTest(unittest.TestCase):
    """OUI identification: fixture integrity, specials, misses."""

    def setUp(self) -> None:
        self.tool = MacAddressTool()

    def test_table_matches_registry_fixture(self) -> None:
        # The embedded table must equal the static IEEE snapshot,
        # entry for entry (no network involved).
        self.assertEqual(
            self.tool.OUI_TABLE, OUI_REGISTRY_FIXTURE,
            "embedded OUI table drifted from the registry fixture",
        )
        self.assertEqual(len(self.tool.OUI_TABLE), 145)

    def test_famous_lookups(self) -> None:
        cases = {
            "00:00:0c:12:34:56": "Cisco Systems, Inc",
            "00:03:93:12:34:56": "Apple, Inc.",
            "00:02:b3:12:34:56": "Intel Corporation",
            "00:e0:4c:12:34:56": "REALTEK SEMICONDUCTOR CORP.",
            "08:00:2b:12:34:56": "DIGITAL EQUIPMENT CORPORATION",
            "00:20:af:12:34:56": "3COM",
            "00:04:ac:12:34:56": "IBM Corp",
            "b8:27:eb:12:34:56": "Raspberry Pi Foundation",
            "00:05:85:12:34:56": "Juniper Networks",
            "00:50:56:12:34:56": "VMware, Inc.",
        }
        for address, organization in cases.items():
            result = self.tool.execute(mode="lookup", address=address)
            self.assertTrue(result["known"], address)
            self.assertEqual(
                result["organization"], organization, address
            )
            self.assertEqual(result["source"], "ieee_ma-l_curated")
            self.assertEqual(
                result["oui_prefix"],
                "-".join(address.split(":")[:3]),
                address,
            )

    def test_private_blocks(self) -> None:
        # AC-DE-48: registry lists the assignment as 'Private' (it is
        # widely attributed to Apple, but the IEEE record says Private).
        result = self.tool.execute(
            mode="lookup", address="ac:de:48:00:11:22"
        )
        self.assertTrue(result["known"])
        self.assertEqual(result["organization"], "Private")
        self.assertTrue(result["is_private"])
        codes = [f["code"] for f in result["findings"]]
        self.assertIn("registry_private_block", codes)
        # 0xAC has the U/L bit clear, so no randomization warning fires.
        self.assertNotIn("local_admin_prefix_unreliable", codes)
        # 00-50-C2: the ex-IAB base, held by the IEEE Registration
        # Authority; 24-bit lookup cannot resolve the 28-bit assignee.
        result = self.tool.execute(
            mode="lookup", address="00:50:c2:00:0a:01"
        )
        self.assertTrue(result["known"])
        self.assertTrue(result["is_private"])
        self.assertIn(
            "registry_private_block",
            [f["code"] for f in result["findings"]],
        )

    def test_unknown_oui_is_a_finding_not_a_crash(self) -> None:
        for address in (
            "de:ad:be:ef:00:01",  # the classic bogus prefix
            "ca:fe:ba:be:00:01",
            "90:99:99:99:99:99",  # plausible but uncurated
        ):
            result = self.tool.execute(mode="lookup", address=address)
            self.assertFalse(result["known"], address)
            self.assertIsNone(result["organization"], address)
            self.assertIsNone(result["source"], address)
            codes = [f["code"] for f in result["findings"]]
            self.assertIn("unknown_oui", codes, address)
            self.assertIn("unknown", result["findings"][0]["message"])
        # Misses must never be a negative vendor claim.
        message = self.tool.execute(
            mode="lookup", address="de:ad:be:ef:00:01"
        )["findings"][0]["message"]
        self.assertIn("NOT", message)

    def test_iana_multicast_blocks(self) -> None:
        result = self.tool.execute(
            mode="lookup", address="01:00:5e:00:00:01"
        )
        self.assertTrue(result["known"])
        self.assertEqual(result["source"], "iana_special")
        self.assertIn("RFC 1112", result["organization"])
        result = self.tool.execute(
            mode="lookup", address="33:33:00:00:00:01"
        )
        self.assertTrue(result["known"])
        self.assertEqual(result["source"], "iana_special")
        self.assertIn("RFC 2464", result["organization"])

    def test_coverage_note_and_size(self) -> None:
        result = self.tool.execute(
            mode="lookup", address="00:00:0c:12:34:56"
        )
        self.assertEqual(result["table_size"], 145)
        self.assertIn("MA-L", result["coverage_note"])
        self.assertIn("unknown_oui", result["coverage_note"])

    def test_lookup_invalid_address_is_structured_error(self) -> None:
        result = self.tool.execute(mode="lookup", address="aa:bb:cc")
        self.assertEqual(result["error"]["type"], "invalid_address")
        self.assertTrue(result["findings"])


class MacAddressToolCompareTest(unittest.TestCase):
    """Same-device relations between two addresses."""

    def setUp(self) -> None:
        self.tool = MacAddressTool()

    def test_identical(self) -> None:
        result = self.tool.execute(
            mode="compare",
            address_a="aa:bb:cc:dd:ee:ff",
            address_b="aabb.ccdd.eeff",
        )
        self.assertEqual(result["relation"], "identical")
        self.assertTrue(result["identical"])
        self.assertIn("different notations", result["relation_detail"])
        result = self.tool.execute(
            mode="compare",
            address_a="aa:bb:cc:dd:ee:ff",
            address_b="aa:bb:cc:dd:ee:ff",
        )
        self.assertEqual(result["relation"], "identical")

    def test_differs_by_local_admin_bit(self) -> None:
        result = self.tool.execute(
            mode="compare",
            address_a="00:11:22:33:44:55",
            address_b="02:11:22:33:44:55",
        )
        self.assertEqual(
            result["relation"], "differs_by_local_admin_bit"
        )
        self.assertIn("universal/local", result["relation_detail"])
        # Any other bit difference must NOT classify as U/L-only.
        result = self.tool.execute(
            mode="compare",
            address_a="00:11:22:33:44:55",
            address_b="04:11:22:33:44:55",
        )
        self.assertNotEqual(
            result["relation"], "differs_by_local_admin_bit"
        )

    def test_differs_in_nic_only(self) -> None:
        result = self.tool.execute(
            mode="compare",
            address_a="00:00:0c:12:34:56",
            address_b="00:00:0c:aa:bb:cc",
        )
        self.assertEqual(result["relation"], "differs_in_nic_only")
        self.assertIn("Cisco Systems, Inc", result["relation_detail"])
        # Un-curated same OUI still relates, with an honest note.
        result = self.tool.execute(
            mode="compare",
            address_a="de:ad:be:12:34:56",
            address_b="de:ad:be:65:43:21",
        )
        self.assertEqual(result["relation"], "differs_in_nic_only")
        self.assertIn("not in the embedded", result["relation_detail"])

    def test_same_vendor_family(self) -> None:
        result = self.tool.execute(
            mode="compare",
            address_a="00:00:0c:12:34:56",
            address_b="00:1b:0d:aa:bb:cc",
        )
        self.assertEqual(result["relation"], "same_vendor_family")
        self.assertIn("Cisco Systems, Inc", result["relation_detail"])

    def test_special_block_relations_wording(self) -> None:
        # Two addresses inside the 33-33/16 IPv6 multicast mapping
        # block with different 24-bit prefixes are a same-block
        # family — the detail must not claim a vendor line.
        result = self.tool.execute(
            mode="compare",
            address_a="33:33:aa:00:00:01",
            address_b="33:33:bb:00:00:02",
        )
        self.assertEqual(result["relation"], "same_vendor_family")
        self.assertIn(
            "IANA special multicast mapping block",
            result["relation_detail"],
        )
        self.assertNotIn("vendors own", result["relation_detail"])
        # NIC-only difference inside a special block is also not a
        # vendor line.
        result = self.tool.execute(
            mode="compare",
            address_a="33:33:00:00:00:01",
            address_b="33:33:00:00:00:02",
        )
        self.assertEqual(result["relation"], "differs_in_nic_only")
        self.assertIn("IANA special block", result["relation_detail"])
        self.assertNotIn(
            "from the embedded OUI table", result["relation_detail"]
        )

    def test_unrelated(self) -> None:
        result = self.tool.execute(
            mode="compare",
            address_a="00:00:0c:12:34:56",
            address_b="de:ad:be:aa:bb:cc",
        )
        self.assertEqual(result["relation"], "unrelated")

    def test_invalid_side_is_structured_error(self) -> None:
        result = self.tool.execute(
            mode="compare",
            address_a="aa:bb:cc:dd:ee",
            address_b="aa:bb:cc:dd:ee:ff",
        )
        self.assertEqual(result["error"]["type"], "invalid_address")
        self.assertIn("address_a", result["error"]["message"])
        result = self.tool.execute(
            mode="compare",
            address_a="aa:bb:cc:dd:ee:ff",
            address_b="zz:bb:cc:dd:ee:ff",
        )
        self.assertEqual(result["error"]["type"], "invalid_address")
        self.assertIn("address_b", result["error"]["message"])


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
