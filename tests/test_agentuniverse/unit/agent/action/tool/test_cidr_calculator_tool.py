#!/usr/bin/env python3

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: test_cidr_calculator_tool.py

"""Offline unit tests for CidrCalculatorTool.

The tool is built purely on the standard library ``ipaddress``
module and never touches the network, so this suite runs fully
offline. Every assertion is deterministic: network reports, subnet
splits and supernet calculations are checked against literal ground
truths computed by hand (netmasks, wildcard masks, broadcast
addresses, usable host ranges, counts), address classification
against the IANA special-purpose ranges, and summarization against
known collapse results.
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import CidrCalculatorTool
from agentuniverse.agent.action.tool.common_tool.cidr_calculator_tool import (
    CidrCalculatorTool as DirectCidrCalculatorTool,
)

# --------------------------------------------------------------------- #
# Ground truths (literal expected values, independent of the tool)
# --------------------------------------------------------------------- #
INFO_192_168_1_0_24 = {
    "mode": "info",
    "network": "192.168.1.0/24",
    "version": 4,
    "prefix": 24,
    "netmask": "255.255.255.0",
    "network_address": "192.168.1.0",
    "first_address": "192.168.1.0",
    "last_address": "192.168.1.255",
    "size": 256,
    "broadcast_address": "192.168.1.255",
    "wildcard_mask": "0.0.0.255",
    "first_usable_host": "192.168.1.1",
    "last_usable_host": "192.168.1.254",
    "usable_host_count": 254,
}
# 2 ** 96, the size of a /32 IPv6 block.
SIZE_V6_32 = 79228162514264337593543950336
# 2 ** 128 for /0 and 2 ** 64 for a /64.
SIZE_V6_0 = 340282366920938463463374607431768211456
SIZE_V6_64 = 18446744073709551616
INT_2001_DB8_1 = 42540766411282592856903984951653826561
INT_8_8_8_8 = 134744072
INT_192_168_1_1 = 3232235777


class CidrCalculatorToolInfoTest(unittest.TestCase):
    """info mode: CIDR and address+prefix network reports."""

    def setUp(self) -> None:
        self.tool = CidrCalculatorTool()

    def test_info_ipv4_cidr_full_report(self) -> None:
        result = self.tool.execute(mode="info", network="192.168.1.0/24")
        self.assertEqual(result, INFO_192_168_1_0_24)

    def test_info_address_plus_prefix_matches_cidr_form(self) -> None:
        result = self.tool.execute(mode="info", network="192.168.1.0", prefix=24)
        self.assertEqual(result, INFO_192_168_1_0_24)

    def test_info_prefix_as_decimal_string(self) -> None:
        result = self.tool.execute(mode="info", network="192.168.1.0", prefix="24")
        self.assertEqual(result["network"], "192.168.1.0/24")
        self.assertEqual(result["usable_host_count"], 254)

    def test_info_bare_address_is_host_network(self) -> None:
        result = self.tool.execute(mode="info", network="192.168.1.1")
        self.assertEqual(result["network"], "192.168.1.1/32")
        self.assertEqual(result["prefix"], 32)
        self.assertEqual(result["size"], 1)
        self.assertEqual(result["first_usable_host"], "192.168.1.1")
        self.assertEqual(result["last_usable_host"], "192.168.1.1")
        self.assertEqual(result["usable_host_count"], 1)

    def test_info_ipv4_slash_31_all_addresses_usable(self) -> None:
        result = self.tool.execute(mode="info", network="192.168.1.0/31")
        self.assertEqual(result["usable_host_count"], 2)
        self.assertEqual(result["first_usable_host"], "192.168.1.0")
        self.assertEqual(result["last_usable_host"], "192.168.1.1")
        self.assertEqual(result["broadcast_address"], "192.168.1.1")

    def test_info_ipv4_slash_30(self) -> None:
        result = self.tool.execute(mode="info", network="10.0.0.0/30")
        self.assertEqual(result["netmask"], "255.255.255.252")
        self.assertEqual(result["wildcard_mask"], "0.0.0.3")
        self.assertEqual(result["broadcast_address"], "10.0.0.3")
        self.assertEqual(result["first_usable_host"], "10.0.0.1")
        self.assertEqual(result["last_usable_host"], "10.0.0.2")
        self.assertEqual(result["usable_host_count"], 2)

    def test_info_ipv4_default_route(self) -> None:
        result = self.tool.execute(mode="info", network="0.0.0.0/0")
        self.assertEqual(result["netmask"], "0.0.0.0")  # noqa: S104
        self.assertEqual(result["wildcard_mask"], "255.255.255.255")
        self.assertEqual(result["broadcast_address"], "255.255.255.255")
        self.assertEqual(result["size"], 4294967296)
        self.assertEqual(result["first_usable_host"], "0.0.0.1")
        self.assertEqual(result["last_usable_host"], "255.255.255.254")
        self.assertEqual(result["usable_host_count"], 4294967294)

    def test_info_ipv6_network(self) -> None:
        result = self.tool.execute(mode="info", network="2001:db8::/32")
        self.assertEqual(
            result,
            {
                "mode": "info",
                "network": "2001:db8::/32",
                "version": 6,
                "prefix": 32,
                "netmask": "ffff:ffff::",
                "network_address": "2001:db8::",
                "first_address": "2001:db8::",
                "last_address": "2001:db8:ffff:ffff:ffff:ffff:ffff:ffff",
                "size": SIZE_V6_32,
            },
        )

    def test_info_ipv6_omits_v4_only_fields(self) -> None:
        result = self.tool.execute(mode="info", network="fe80::/64")
        for key in (
            "broadcast_address",
            "wildcard_mask",
            "first_usable_host",
            "last_usable_host",
            "usable_host_count",
        ):
            self.assertNotIn(key, result)
        self.assertEqual(result["netmask"], "ffff:ffff:ffff:ffff::")
        self.assertEqual(result["size"], SIZE_V6_64)
        self.assertEqual(result["first_address"], "fe80::")
        self.assertEqual(result["last_address"], "fe80::ffff:ffff:ffff:ffff")

    def test_info_ipv6_default_route_size(self) -> None:
        result = self.tool.execute(mode="info", network="::/0")
        self.assertEqual(result["size"], SIZE_V6_0)
        self.assertEqual(result["netmask"], "::")

    def test_info_ipv6_address_plus_prefix_normalizes(self) -> None:
        result = self.tool.execute(mode="info", network="fe80:0:0:0:0:0:0:0", prefix="64")
        self.assertEqual(result["network"], "fe80::/64")

    def test_info_host_bits_set_reports_both_interpretations(self) -> None:
        result = self.tool.execute(mode="info", network="192.168.1.5/24")
        self.assertEqual(result["mode"], "info")
        self.assertEqual(result["error"]["type"], "host_bits_set")
        self.assertEqual(result["error"]["input"], "192.168.1.5/24")
        self.assertEqual(result["error"]["normalized"], "192.168.1.0/24")
        self.assertIn("192.168.1.5/24", result["error"]["message"])
        self.assertIn("192.168.1.0/24", result["error"]["message"])

    def test_info_host_bits_via_address_plus_prefix(self) -> None:
        result = self.tool.execute(mode="info", network="10.0.0.5", prefix=8)
        self.assertEqual(result["error"]["type"], "host_bits_set")
        self.assertEqual(result["error"]["input"], "10.0.0.5/8")
        self.assertEqual(result["error"]["normalized"], "10.0.0.0/8")

    def test_info_conflicting_prefix_spellings(self) -> None:
        result = self.tool.execute(mode="info", network="10.0.0.0/24", prefix=8)
        self.assertEqual(result["error"]["type"], "invalid_network")
        self.assertIn("10.0.0.0/24", result["error"]["message"])

    def test_info_invalid_address_token(self) -> None:
        result = self.tool.execute(mode="info", network="300.1.1.0/24")
        self.assertEqual(result["error"]["type"], "invalid_address")
        self.assertIn("300.1.1.0", result["error"]["message"])

    def test_info_invalid_address_extra_octet(self) -> None:
        result = self.tool.execute(mode="info", network="10.0.0.0.5/24")
        self.assertEqual(result["error"]["type"], "invalid_address")

    def test_info_prefix_out_of_range_v4(self) -> None:
        for bad in ("10.0.0.0/33", "10.0.0.0/-1", "10.0.0.0/"):
            result = self.tool.execute(mode="info", network=bad)
            self.assertEqual(
                result["error"]["type"],
                "invalid_prefix",
                msg=f"network={bad!r}",
            )

    def test_info_prefix_argument_out_of_range_v4(self) -> None:
        result = self.tool.execute(mode="info", network="10.0.0.0", prefix=33)
        self.assertEqual(result["error"]["type"], "invalid_prefix")

    def test_info_prefix_out_of_range_v6(self) -> None:
        result = self.tool.execute(mode="info", network="fe80::/129")
        self.assertEqual(result["error"]["type"], "invalid_prefix")


class CidrCalculatorToolContainsTest(unittest.TestCase):
    """contains mode: per-address membership verdicts."""

    def setUp(self) -> None:
        self.tool = CidrCalculatorTool()

    def test_contains_ipv4_matrix(self) -> None:
        result = self.tool.execute(
            mode="contains",
            network="10.0.0.0/8",
            addresses=[
                "10.1.2.3",
                "10.255.255.255",
                "11.0.0.0",
                "192.168.1.1",
                "not-an-ip",
                "::1",
            ],
        )
        self.assertEqual(result["mode"], "contains")
        self.assertEqual(result["network"], "10.0.0.0/8")
        self.assertEqual(result["contained_count"], 2)
        self.assertEqual(result["not_contained_count"], 3)
        self.assertEqual(result["invalid_count"], 1)
        self.assertEqual(
            result["results"][0],
            {
                "address": "10.1.2.3",
                "normalized": "10.1.2.3",
                "version": 4,
                "contained": True,
                "invalid": False,
            },
        )
        self.assertTrue(result["results"][1]["contained"])
        self.assertFalse(result["results"][2]["contained"])
        self.assertFalse(result["results"][3]["contained"])
        self.assertEqual(
            result["results"][4],
            {"address": "not-an-ip", "contained": False, "invalid": True},
        )
        # An IPv6 address is simply outside an IPv4 network.
        self.assertFalse(result["results"][5]["contained"])
        self.assertEqual(result["results"][5]["version"], 6)

    def test_contains_ipv6_matrix(self) -> None:
        result = self.tool.execute(
            mode="contains",
            network="2001:db8::/32",
            addresses=[
                "2001:db8::1",
                "2001:DB8:dead:beef::1",
                "2001:db9::1",
                "fe80::1",
            ],
        )
        self.assertEqual(result["contained_count"], 2)
        self.assertEqual(result["not_contained_count"], 2)
        self.assertEqual(result["invalid_count"], 0)
        self.assertTrue(result["results"][0]["contained"])
        self.assertTrue(result["results"][1]["contained"])
        self.assertEqual(result["results"][1]["normalized"], "2001:db8:dead:beef::1")
        self.assertFalse(result["results"][2]["contained"])
        self.assertFalse(result["results"][3]["contained"])

    def test_contains_boundary_addresses(self) -> None:
        result = self.tool.execute(
            mode="contains",
            network="192.168.1.0/24",
            addresses=["192.168.0.255", "192.168.1.0", "192.168.1.255", "192.168.2.0"],
        )
        verdicts = [entry["contained"] for entry in result["results"]]
        self.assertEqual(verdicts, [False, True, True, False])

    def test_contains_accepts_tuple(self) -> None:
        result = self.tool.execute(mode="contains", network="10.0.0.0/8", addresses=("10.0.0.1",))
        self.assertEqual(result["contained_count"], 1)

    def test_contains_invalid_network_returns_error(self) -> None:
        result = self.tool.execute(mode="contains", network="10.0.0.999/24", addresses=["10.0.0.1"])
        self.assertEqual(result["error"]["type"], "invalid_address")


class CidrCalculatorToolSubnetTest(unittest.TestCase):
    """subnet mode: splitting with exact counts and capped output."""

    def setUp(self) -> None:
        self.tool = CidrCalculatorTool()

    def test_subnet_10_slash_8_into_slash_16_exact_list(self) -> None:
        result = self.tool.execute(mode="subnet", network="10.0.0.0/8", new_prefix=16)
        self.assertEqual(
            result,
            {
                "mode": "subnet",
                "network": "10.0.0.0/8",
                "new_prefix": 16,
                "count": 256,
                "subnets": [f"10.{i}.0.0/16" for i in range(256)],
                "returned": 256,
                "truncated": False,
            },
        )

    def test_subnet_output_capped_with_count(self) -> None:
        result = self.tool.execute(mode="subnet", network="10.0.0.0/8", new_prefix=24)
        self.assertEqual(result["count"], 65536)
        self.assertEqual(result["returned"], 256)
        self.assertTrue(result["truncated"])
        self.assertEqual(len(result["subnets"]), 256)
        self.assertEqual(result["subnets"][0], "10.0.0.0/24")
        self.assertEqual(result["subnets"][1], "10.0.1.0/24")
        self.assertEqual(result["subnets"][255], "10.0.255.0/24")

    def test_subnet_first_entry_matches_input_network(self) -> None:
        result = self.tool.execute(mode="subnet", network="192.168.1.0/24", new_prefix=25)
        self.assertEqual(result["subnets"], ["192.168.1.0/25", "192.168.1.128/25"])
        self.assertEqual(result["count"], 2)
        self.assertFalse(result["truncated"])

    def test_subnet_ipv6(self) -> None:
        result = self.tool.execute(mode="subnet", network="2001:db8::/32", new_prefix=34)
        self.assertEqual(
            result["subnets"],
            [
                "2001:db8::/34",
                "2001:db8:4000::/34",
                "2001:db8:8000::/34",
                "2001:db8:c000::/34",
            ],
        )
        self.assertEqual(result["count"], 4)
        self.assertFalse(result["truncated"])

    def test_subnet_new_prefix_not_longer(self) -> None:
        for bad in (8, 7):
            result = self.tool.execute(mode="subnet", network="10.0.0.0/8", new_prefix=bad)
            self.assertEqual(result["error"]["type"], "invalid_prefix")
            self.assertIn("greater than", result["error"]["message"])

    def test_subnet_new_prefix_out_of_range(self) -> None:
        result = self.tool.execute(mode="subnet", network="10.0.0.0/8", new_prefix=33)
        self.assertEqual(result["error"]["type"], "invalid_prefix")
        v6 = self.tool.execute(mode="subnet", network="fe80::/64", new_prefix=129)
        self.assertEqual(v6["error"]["type"], "invalid_prefix")

    def test_subnet_host_bits_set(self) -> None:
        result = self.tool.execute(mode="subnet", network="192.168.1.5/24", new_prefix=26)
        self.assertEqual(result["error"]["type"], "host_bits_set")
        self.assertEqual(result["error"]["normalized"], "192.168.1.0/24")


class CidrCalculatorToolSupernetTest(unittest.TestCase):
    """supernet mode: enclosing networks of shorter prefixes."""

    def setUp(self) -> None:
        self.tool = CidrCalculatorTool()

    def test_supernet_ipv4(self) -> None:
        result = self.tool.execute(mode="supernet", network="192.168.128.0/17", new_prefix=16)
        self.assertEqual(
            result,
            {
                "mode": "supernet",
                "network": "192.168.128.0/17",
                "new_prefix": 16,
                "supernet": "192.168.0.0/16",
                "supernet_network_address": "192.168.0.0",
                "supernet_netmask": "255.255.0.0",
                "supernet_size": 65536,
            },
        )

    def test_supernet_to_default_route(self) -> None:
        result = self.tool.execute(mode="supernet", network="10.0.0.0/8", new_prefix=0)
        self.assertEqual(result["supernet"], "0.0.0.0/0")
        self.assertEqual(result["supernet_size"], 4294967296)

    def test_supernet_ipv6(self) -> None:
        result = self.tool.execute(mode="supernet", network="2001:db8:8000::/33", new_prefix=32)
        self.assertEqual(result["supernet"], "2001:db8::/32")
        self.assertEqual(result["supernet_size"], SIZE_V6_32)

    def test_supernet_new_prefix_not_shorter(self) -> None:
        for bad in (17, 18):
            result = self.tool.execute(mode="supernet", network="192.168.0.0/16", new_prefix=bad)
            self.assertEqual(result["error"]["type"], "invalid_prefix")
            self.assertIn("smaller than", result["error"]["message"])

    def test_supernet_new_prefix_out_of_range(self) -> None:
        result = self.tool.execute(mode="supernet", network="192.168.0.0/16", new_prefix=33)
        self.assertEqual(result["error"]["type"], "invalid_prefix")
        self.assertIn("between 0 and 32", result["error"]["message"])


class CidrCalculatorToolIpInfoTest(unittest.TestCase):
    """ip_info mode: classification and textual forms."""

    def setUp(self) -> None:
        self.tool = CidrCalculatorTool()

    def _info(self, address: str) -> dict:
        return self.tool.execute(mode="ip_info", address=address)

    def test_ip_info_global_ipv4(self) -> None:
        result = self._info("8.8.8.8")
        self.assertEqual(result["version"], 4)
        self.assertEqual(result["type"], "global")
        self.assertTrue(result["is_global"])
        self.assertFalse(result["is_private"])
        self.assertFalse(result["is_loopback"])
        self.assertFalse(result["is_multicast"])
        self.assertEqual(result["compressed"], "8.8.8.8")
        self.assertEqual(result["exploded"], "8.8.8.8")
        self.assertEqual(result["int"], INT_8_8_8_8)

    def test_ip_info_private_ipv4(self) -> None:
        result = self._info("192.168.1.1")
        self.assertEqual(result["type"], "private")
        self.assertTrue(result["is_private"])
        self.assertFalse(result["is_global"])
        self.assertEqual(result["int"], INT_192_168_1_1)

    def test_ip_info_loopback_beats_private(self) -> None:
        result = self._info("127.0.0.1")
        self.assertEqual(result["type"], "loopback")
        self.assertTrue(result["is_loopback"])
        self.assertTrue(result["is_private"])

    def test_ip_info_link_local_beats_private(self) -> None:
        result = self._info("169.254.1.1")
        self.assertEqual(result["type"], "link_local")
        self.assertTrue(result["is_link_local"])

    def test_ip_info_multicast(self) -> None:
        result = self._info("224.0.0.1")
        self.assertEqual(result["type"], "multicast")
        self.assertTrue(result["is_multicast"])

    def test_ip_info_reserved_beats_private(self) -> None:
        result = self._info("240.0.0.1")
        self.assertEqual(result["type"], "reserved")
        self.assertTrue(result["is_reserved"])

    def test_ip_info_shared_address_space_is_other(self) -> None:
        # 100.64.0.0/10 (CGNAT shared space): neither private nor global.
        result = self._info("100.64.0.1")
        self.assertEqual(result["type"], "other")
        self.assertFalse(result["is_private"])
        self.assertFalse(result["is_global"])

    def test_ip_info_ipv6_forms(self) -> None:
        result = self._info("2001:db8::1")
        self.assertEqual(result["version"], 6)
        self.assertEqual(result["compressed"], "2001:db8::1")
        self.assertEqual(result["exploded"], "2001:0db8:0000:0000:0000:0000:0000:0001")
        self.assertEqual(result["int"], INT_2001_DB8_1)
        self.assertEqual(result["type"], "private")
        self.assertTrue(result["is_private"])

    def test_ip_info_ipv6_classifications(self) -> None:
        self.assertEqual(self._info("::1")["type"], "loopback")
        self.assertEqual(self._info("fe80::1")["type"], "link_local")
        self.assertTrue(self._info("fe80::1")["is_link_local"])
        self.assertEqual(self._info("ff02::1")["type"], "multicast")
        self.assertTrue(self._info("ff02::1")["is_multicast"])
        self.assertEqual(self._info("fc00::1")["type"], "private")
        self.assertEqual(self._info("2001:4860:4860::8888")["type"], "global")
        self.assertTrue(self._info("2001:4860:4860::8888")["is_global"])

    def test_ip_info_normalizes_uppercase_ipv6(self) -> None:
        result = self._info("FE80::1")
        self.assertEqual(result["address"], "fe80::1")

    def test_ip_info_invalid_address(self) -> None:
        for bad in ("999.999.999.999", "1.2.3", "10.0.0.0/24", "::gg::"):
            result = self.tool.execute(mode="ip_info", address=bad)
            self.assertEqual(
                result["error"]["type"],
                "invalid_address",
                msg=f"address={bad!r}",
            )
            self.assertIn(bad[:10], result["error"]["message"])

    def test_ip_info_empty_address_is_parameter_error(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="ip_info", address="")


class CidrCalculatorToolSummarizeTest(unittest.TestCase):
    """summarize mode: merging addresses / CIDRs into ranges."""

    def setUp(self) -> None:
        self.tool = CidrCalculatorTool()

    def test_summarize_adjacent_networks_merge(self) -> None:
        result = self.tool.execute(mode="summarize", networks=["192.168.0.0/24", "192.168.1.0/24"])
        self.assertEqual(
            result,
            {
                "mode": "summarize",
                "input_count": 2,
                "networks": ["192.168.0.0/24", "192.168.1.0/24"],
                "summary": ["192.168.0.0/23"],
                "count": 1,
            },
        )

    def test_summarize_overlapping_inputs_collapse(self) -> None:
        result = self.tool.execute(
            mode="summarize",
            networks=["192.168.1.0/25", "192.168.1.128/25", "192.168.1.0/24"],
        )
        self.assertEqual(result["summary"], ["192.168.1.0/24"])

    def test_summarize_contiguous_addresses_form_prefix(self) -> None:
        result = self.tool.execute(
            mode="summarize",
            networks=["192.168.0.0", "192.168.0.1", "192.168.0.2", "192.168.0.3"],
        )
        self.assertEqual(result["summary"], ["192.168.0.0/30"])
        self.assertEqual(
            result["networks"],
            [
                "192.168.0.0/32",
                "192.168.0.1/32",
                "192.168.0.2/32",
                "192.168.0.3/32",
            ],
        )

    def test_summarize_disjoint_networks_stay_sorted(self) -> None:
        result = self.tool.execute(mode="summarize", networks=["192.168.0.0/24", "10.0.0.0/8"])
        self.assertEqual(result["summary"], ["10.0.0.0/8", "192.168.0.0/24"])
        self.assertEqual(result["count"], 2)

    def test_summarize_mixed_families_grouped(self) -> None:
        result = self.tool.execute(
            mode="summarize",
            networks=[
                "192.168.0.0/24",
                "192.168.1.0/24",
                "2001:db8::/33",
                "2001:db8:8000::/33",
            ],
        )
        self.assertEqual(result["summary"], ["192.168.0.0/23", "2001:db8::/32"])

    def test_summarize_ipv6_normalization(self) -> None:
        result = self.tool.execute(mode="summarize", networks=["2001:0db8:0000:0000:0000:0000:0000:0001"])
        self.assertEqual(result["networks"], ["2001:db8::1/128"])
        self.assertEqual(result["summary"], ["2001:db8::1/128"])

    def test_summarize_host_bits_item_fails_whole_call(self) -> None:
        result = self.tool.execute(mode="summarize", networks=["192.168.0.0/24", "192.168.1.5/24"])
        self.assertEqual(result["error"]["type"], "host_bits_set")
        self.assertEqual(result["error"]["normalized"], "192.168.1.0/24")

    def test_summarize_invalid_item_fails_whole_call(self) -> None:
        result = self.tool.execute(mode="summarize", networks=["192.168.0.0/24", "banana/24"])
        self.assertEqual(result["error"]["type"], "invalid_address")
        self.assertIn("banana", result["error"]["message"])


class CidrCalculatorToolValidationTest(unittest.TestCase):
    """Parameter-level errors raise ValueError before any computation."""

    def setUp(self) -> None:
        self.tool = CidrCalculatorTool()

    def test_unknown_mode_rejected(self) -> None:
        for bad in ("calc", "", None, 123):
            with self.assertRaises(ValueError, msg=f"mode={bad!r}"):
                self.tool.execute(mode=bad)

    def test_network_must_be_non_empty_string(self) -> None:
        for bad in (None, 123, True, "   "):
            with self.assertRaises(ValueError):
                self.tool.execute(mode="info", network=bad)

    def test_prefix_must_be_integer(self) -> None:
        for bad in ("abc", True, 24.5, [24]):
            with self.assertRaises(ValueError):
                self.tool.execute(mode="info", network="10.0.0.0", prefix=bad)

    def test_new_prefix_required_and_integer(self) -> None:
        for bad in (None, "abc", True, 16.0):
            with self.assertRaises(ValueError):
                self.tool.execute(mode="subnet", network="10.0.0.0/8", new_prefix=bad)
            with self.assertRaises(ValueError):
                self.tool.execute(mode="supernet", network="10.0.0.0/8", new_prefix=bad)

    def test_new_prefix_decimal_string_accepted(self) -> None:
        result = self.tool.execute(mode="subnet", network="10.0.0.0/8", new_prefix="9")
        self.assertEqual(result["new_prefix"], 9)
        self.assertEqual(result["count"], 2)

    def test_addresses_must_be_non_empty_string_list(self) -> None:
        for bad in ("10.0.0.1", None, [], ["10.0.0.1", 42], ["10.0.0.1", "  "]):
            with self.assertRaises(ValueError):
                self.tool.execute(mode="contains", network="10.0.0.0/8", addresses=bad)

    def test_networks_must_be_non_empty_string_list(self) -> None:
        for bad in ("10.0.0.0/8", None, [], [16], [""]):
            with self.assertRaises(ValueError):
                self.tool.execute(mode="summarize", networks=bad)

    def test_input_lists_capped(self) -> None:
        too_many = [f"10.0.{i // 256}.{i % 256}" for i in range(257)]
        with self.assertRaises(ValueError):
            self.tool.execute(mode="contains", network="10.0.0.0/8", addresses=too_many)
        with self.assertRaises(ValueError):
            self.tool.execute(mode="summarize", networks=too_many)

    def test_address_required_for_ip_info(self) -> None:
        for bad in (None, 8, ["8.8.8.8"]):
            with self.assertRaises(ValueError):
                self.tool.execute(mode="ip_info", address=bad)


class CidrCalculatorToolImportTest(unittest.TestCase):
    """Package-level export mirrors the module-level class."""

    def test_package_export(self) -> None:
        self.assertIs(CidrCalculatorTool, DirectCidrCalculatorTool)


if __name__ == "__main__":
    unittest.main()
