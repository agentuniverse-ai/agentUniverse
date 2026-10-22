"""Offline unit tests for PortListTool.

The oracles are deliberately independent of the tool's implementation:

* specs are re-parsed by a trivial split-on-comma reference parser,
* compression is re-derived by a brute-force run walker over sorted port sets,
* algebra results are re-derived with Python set operations,
* the embedded service table is pinned against a static fixture captured at
  authoring time and cross-checked against socket.getservbyname only where
  the platform's /etc/services agrees with the fixture.

No network access, no filesystem access outside the repo, stdlib only.
"""

# Fullwidth digits are intentional inputs for the rejection tests, and the
# seeded pseudo-random generator only produces deterministic test data.
# ruff: noqa: RUF001, S311

import json
import os
import random
import socket
import time
import unittest
from itertools import pairwise
from typing import ClassVar

from agentuniverse.agent.action.tool.common_tool import port_list_tool as port_module
from agentuniverse.agent.action.tool.common_tool.port_list_tool import PortListTool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer

YAML_PATH = os.path.join(os.path.dirname(port_module.__file__), "port_list_tool.yaml")


# --------------------------------------------------------------------------
# Independent oracles
# --------------------------------------------------------------------------

def oracle_spec_to_set(spec):
    """Reference parser: trivial split/int conversion, no validation."""
    ports = set()
    for segment in spec.split(","):
        segment = segment.strip()
        if not segment:
            continue
        if "-" in segment:
            low, high = segment.split("-", 1)
            ports.update(range(int(low), int(high) + 1))
        else:
            ports.add(int(segment))
    return ports


def oracle_compress(ports):
    """Brute-force minimal compressor: sort, then walk consecutive runs."""
    values = sorted(set(ports))
    parts = []
    index = 0
    while index < len(values):
        end = index
        while end + 1 < len(values) and values[end + 1] == values[end] + 1:
            end += 1
        if index == end:
            parts.append(f"{values[index]}")
        else:
            parts.append(f"{values[index]}-{values[end]}")
        index = end + 1
    return ",".join(parts)


def random_valid_spec(rng, top=2000, max_segments=12):
    """Seeded generator of valid specs inside a small port universe."""
    segments = []
    for _ in range(rng.randint(1, max_segments)):
        start = rng.randint(0, top)
        if rng.random() < 0.5:
            segments.append(str(start))
            continue
        end = rng.randint(start, min(start + rng.randint(0, 400), 65535))
        piece = str(start) if end == start else f"{start}-{end}"
        if rng.random() < 0.2:
            piece = f"  {piece} "
        if rng.random() < 0.15:
            piece = f"{start} - {end}" if end != start else piece
        segments.append(piece)
    if segments and rng.random() < 0.3:
        segments.append(segments[rng.randrange(len(segments))])
    return ",".join(segments)


class PortListParseTest(unittest.TestCase):
    """Documented parse conventions: errors, infos, and tolerances."""

    def setUp(self):
        self.tool = PortListTool()

    def test_basic_parse(self):
        result = self.tool.execute(mode="parse", spec="22,80-90,443")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["ranges"], [
            {"start": 22, "end": 22, "size": 1},
            {"start": 80, "end": 90, "size": 11},
            {"start": 443, "end": 443, "size": 1},
        ])
        self.assertEqual(result["ports_total"], 13)
        self.assertEqual(result["errors"], [])

    def test_whitespace_tolerance(self):
        result = self.tool.execute(mode="parse", spec=" 80 , 443 ")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["ports_total"], 2)
        spaced = self.tool.execute(mode="parse", spec="\t80 -\t90\t, 443")
        self.assertEqual(spaced["status"], "success")
        self.assertEqual(spaced["ports_total"], 12)

    def test_reversed_range_is_error(self):
        """Convention: reversed ranges error instead of auto-normalizing."""
        result = self.tool.execute(mode="parse", spec="90-80")
        self.assertEqual(result["status"], "error")
        self.assertEqual([e["code"] for e in result["errors"]], ["reversed_range"])
        self.assertEqual(result["errors"][0]["position"], 3)

    def test_singleton_collapse(self):
        result = self.tool.execute(mode="parse", spec="80-80")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["ranges"], [{"start": 80, "end": 80, "size": 1}])
        self.assertEqual(result["infos"][0]["code"], "singleton_collapse")

    def test_port_zero_parses_but_is_flagged(self):
        result = self.tool.execute(mode="parse", spec="0,80")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["ports_total"], 2)
        self.assertIn("reserved_port_zero", [i["code"] for i in result["infos"]])

    def test_out_of_range(self):
        for spec, position in (("65536", 0), ("80-65536", 3), ("80,70000", 3)):
            result = self.tool.execute(mode="parse", spec=spec)
            self.assertEqual(result["status"], "error", spec)
            self.assertEqual(result["errors"][0]["code"], "out_of_range")
            self.assertEqual(result["errors"][0]["position"], position, spec)

    def test_boundary_ports_accepted(self):
        result = self.tool.execute(mode="parse", spec="0-65535")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["ports_total"], 65536)

    def test_empty_segment_error_position(self):
        result = self.tool.execute(mode="parse", spec="80,,443")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["errors"][0]["code"], "empty_segment")
        self.assertEqual(result["errors"][0]["position"], 3)
        self.assertEqual(self.tool.execute(mode="parse", spec="")["errors"][0]["code"], "empty_segment")

    def test_leading_zero_rejected(self):
        """Port specs do not zero-pad; '080' is rejected with an explanation."""
        result = self.tool.execute(mode="parse", spec="080,443")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["errors"][0]["code"], "leading_zero")
        self.assertIn("zero-pad", result["errors"][0]["message"])
        self.assertEqual(self.tool.execute(mode="parse", spec="0")["status"], "success")

    def test_unicode_digits_rejected(self):
        for spec in ("８０", "80４", "٤٤٣", "½", "80-9５"):
            result = self.tool.execute(mode="parse", spec=spec)
            self.assertEqual(result["status"], "error", repr(spec))
            self.assertEqual(result["errors"][0]["code"], "non_numeric", repr(spec))

    def test_duplicate_ranges_reported_with_overlap_arithmetic(self):
        result = self.tool.execute(mode="parse", spec="80-90,80-90")
        codes = [i["code"] for i in result["infos"]]
        self.assertIn("duplicate_range", codes)
        self.assertIn("overlap by 11 port(s)", json.dumps(result["infos"]))
        self.assertEqual(result["ports_total"], 11)
        singleton = self.tool.execute(mode="parse", spec="80,80")
        self.assertIn("overlap by 1 port(s)", json.dumps(singleton["infos"]))

    def test_partial_overlap_arithmetic(self):
        result = self.tool.execute(mode="parse", spec="80-90,85-95")
        self.assertEqual(result["ports_total"], 16)
        self.assertIn("overlap by 6 port(s)", json.dumps(result["infos"]))

    def test_all_keyword_requires_opt_in(self):
        self.assertEqual(self.tool.execute(mode="parse", spec="all")["status"], "error")
        result = self.tool.execute(mode="parse", spec="all", allow_all=True)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["ranges"], [{"start": 0, "end": 65535, "size": 65536}])
        self.assertEqual(result["ports_total"], 65536)

    def test_deterministic_repetition(self):
        for spec in ("22,80-90,443,80-80", " 1-10 , 20-15 ", "0-65535,2"):
            first = self.tool.execute(mode="parse", spec=spec)
            second = self.tool.execute(mode="parse", spec=spec)
            self.assertEqual(json.dumps(first, sort_keys=True), json.dumps(second, sort_keys=True))

    def test_argument_validation(self):
        cases = [
            {"mode": "wat"},
            {"mode": 7},
            {"mode": "parse", "spec": 80},
            {"mode": "algebra", "spec_a": "80", "spec_b": "90", "op": "xor"},
            {"mode": "compress", "spec": "80", "ports": [80]},
            {"mode": "compress", "ports": [True]},
            {"mode": "compress", "ports": [70000]},
            {"mode": "compress", "ports": 80},
            {"mode": "check", "spec": "80", "max_ports": -1},
            {"mode": "check", "spec": "80", "max_ports": True},
        ]
        for kwargs in cases:
            result = self.tool.execute(**kwargs)
            self.assertEqual(result["status"], "error", kwargs)
            self.assertEqual(result["error_type"], "validation_error", kwargs)

    def test_spec_length_cap(self):
        result = self.tool.execute(mode="parse", spec="80," * 20_000 + "443")
        self.assertEqual(result["status"], "error")
        self.assertIn("max_spec_segments", result["error"])


class PortListAdjacencyTest(unittest.TestCase):
    """Hand table for the adjacency-merge rule: 80,81,82 -> 80-82 but 79,81 stays."""

    CASES: ClassVar[list] = [
        (([80, 81, 82]), "80-82", "chained adjacent singletons"),
        (([79, 81]), "79,81", "non-adjacent singletons NOT merged (80 missing)"),
        (([80, 82]), "80,82", "gap of one port blocks merging"),
        (([80, 81, 82, 83, 84]), "80-84", "five-way chain"),
        (([1, 2, 3, 5, 6, 7]), "1-3,5-7", "two separate runs"),
        (([80, 82]), "80,82", "singletons two apart"),
        (([100, 101, 103, 104]), "100-101,103-104", "alternating adjacency"),
        (([65534, 65535]), "65534-65535", "adjacent at the top boundary"),
        (([0, 1]), "0-1", "adjacent at the bottom boundary"),
        (([80, 79]), "79-80", "input order must not matter"),
        (([443, 80, 22]), "22,80,443", "unsorted input is sorted"),
        (([80, 81, 80, 81]), "80-81", "duplicates collapse before merging"),
        (([30000, 30002, 30001]), "30000-30002", "chained through the middle"),
    ]

    SPEC_CASES: ClassVar[list] = [
        ("80-82,83-85", "80-85", "adjacent ranges merge"),
        ("80-82,84-86", "80-82,84-86", "non-adjacent ranges stay split"),
        ("80-90,85-95", "80-95", "partial overlap merges"),
        ("80-90,90-95", "80-95", "touching at a shared endpoint merges"),
        ("80-90,80-90", "80-90", "exact duplicate collapses"),
        ("1-3,2", "1-3", "contained range is absorbed"),
        ("1-3,3-5", "1-5", "endpoint-shared partial overlap"),
        ("5-10,1-2,20,19", "1-2,5-10,19-20", "mixed order with pairs"),
        ("100-200,150-160,0-50,55-99", "0-50,55-200", "99-100 adjacency chains three ranges"),
        ("30000-30002,30003-30005,30007", "30000-30005,30007", "high ports with one stray"),
    ]

    def setUp(self):
        self.tool = PortListTool()

    def test_port_list_adjacency_table(self):
        for ports, expected, label in self.CASES:
            with self.subTest(label=label):
                result = self.tool.execute(mode="compress", ports=ports)
                self.assertEqual(result["status"], "success")
                self.assertEqual(result["spec"], expected)
                self.assertEqual(oracle_compress(ports), expected)

    def test_spec_adjacency_table(self):
        for spec, expected, label in self.SPEC_CASES:
            with self.subTest(label=label):
                result = self.tool.execute(mode="compress", spec=spec)
                self.assertEqual(result["status"], "success")
                self.assertEqual(result["spec"], expected)
                self.assertEqual(oracle_compress(oracle_spec_to_set(spec)), expected)

    def test_non_adjacent_79_81_not_merged(self):
        """The canonical negative case: a missing middle port blocks merging."""
        result = self.tool.execute(mode="compress", spec="79,81")
        self.assertEqual(result["ranges"], [
            {"start": 79, "end": 79, "size": 1},
            {"start": 81, "end": 81, "size": 1},
        ])


class PortListRoundTripPropertyTest(unittest.TestCase):
    """500 seeded specs: set-equality and minimal form vs a brute-force oracle."""

    def setUp(self):
        self.tool = PortListTool()

    def test_round_trip_and_minimal_form(self):
        rng = random.Random(2025)
        specs = [random_valid_spec(rng, top=2000) for _ in range(460)]
        rng2 = random.Random(2026)
        specs += [random_valid_spec(rng2, top=65535, max_segments=6) for _ in range(40)]
        self.assertEqual(len(specs), 500)
        for spec in specs:
            with self.subTest(spec=spec):
                compressed = self.tool.execute(mode="compress", spec=spec)
                self.assertEqual(compressed["status"], "success", spec)
                canonical = compressed["spec"]
                self.assertEqual(oracle_spec_to_set(canonical), oracle_spec_to_set(spec), "set equality")
                if max(oracle_spec_to_set(spec)) <= 2000:
                    self.assertEqual(canonical, oracle_compress(oracle_spec_to_set(spec)), "minimal form vs brute force")
                ranges = compressed["ranges"]
                for previous, following in pairwise(ranges):
                    self.assertGreater(following["start"], previous["end"] + 1, "canonical form must not be re-mergeable")
                expanded = self.tool.execute(mode="expand", spec=canonical, include_full=True)
                self.assertEqual(set(expanded["ports"]), oracle_spec_to_set(spec), "expand(compress(x)) set equality")
                parsed = self.tool.execute(mode="parse", spec=spec)
                self.assertEqual(parsed["ports_total"], len(oracle_spec_to_set(spec)))

    def test_compress_empty_port_list(self):
        result = self.tool.execute(mode="compress", ports=[])
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["spec"], "")
        self.assertEqual(result["count"], 0)


class PortListServiceTableTest(unittest.TestCase):
    """The embedded curated table is pinned to an authoring-time fixture."""

    # Static fixture captured at authoring time; no network involved.
    FIXTURE: ClassVar[dict] = {
        7: [("echo", "both")],
        9: [("discard", "both")],
        13: [("daytime", "both")],
        17: [("qotd", "both")],
        19: [("chargen", "both")],
        20: [("ftp-data", "tcp")],
        21: [("ftp", "tcp")],
        22: [("ssh", "both")],
        23: [("telnet", "tcp")],
        25: [("smtp", "tcp")],
        26: [("rsftp", "tcp")],
        37: [("time", "both")],
        42: [("nameserver", "both")],
        43: [("whois", "tcp")],
        49: [("tacacs", "both")],
        53: [("dns", "both")],
        67: [("dhcp-server", "udp")],
        68: [("dhcp-client", "udp")],
        69: [("tftp", "udp")],
        70: [("gopher", "tcp")],
        79: [("finger", "tcp")],
        80: [("http", "both")],
        88: [("kerberos", "both")],
        102: [("iso-tsap", "tcp")],
        107: [("rtelnet", "tcp")],
        109: [("pop2", "tcp")],
        110: [("pop3", "tcp")],
        111: [("rpcbind", "both")],
        113: [("ident", "tcp")],
        119: [("nntp", "tcp")],
        123: [("ntp", "udp")],
        135: [("msrpc", "tcp")],
        137: [("netbios-ns", "udp")],
        138: [("netbios-dgm", "udp")],
        139: [("netbios-ssn", "tcp")],
        143: [("imap", "tcp")],
        161: [("snmp", "udp")],
        162: [("snmptrap", "udp")],
        177: [("xdmcp", "udp")],
        179: [("bgp", "tcp")],
        194: [("irc", "tcp")],
        201: [("apple-talk", "udp")],
        389: [("ldap", "tcp")],
        427: [("svrloc", "udp")],
        443: [("https", "tcp")],
        444: [("snpp", "tcp")],
        445: [("smb", "tcp")],
        464: [("kpasswd", "both")],
        465: [("smtps", "tcp")],
        500: [("isakmp", "udp")],
        502: [("modbus", "tcp")],
        506: [("ohmserver", "tcp")],
        514: [("shell", "tcp"), ("syslog", "udp")],
        515: [("printer", "tcp")],
        520: [("rip", "udp")],
        521: [("ripng", "udp")],
        526: [("tempo", "tcp")],
        530: [("rpc", "tcp")],
        540: [("uucp", "tcp")],
        543: [("klogin", "tcp")],
        544: [("kshell", "tcp")],
        546: [("dhcpv6-client", "udp")],
        547: [("dhcpv6-server", "udp")],
        548: [("afp", "tcp")],
        554: [("rtsp", "both")],
        555: [("dsf", "tcp")],
        563: [("nntp-over-tls", "tcp")],
        587: [("submission", "tcp")],
        591: [("http-mgmt", "tcp")],
        631: [("ipp", "both")],
        636: [("ldaps", "tcp")],
        646: [("ldp", "tcp")],
        647: [("dhcp-failover", "tcp")],
        873: [("rsync", "tcp")],
        990: [("ftps", "tcp")],
        992: [("telnets", "tcp")],
        993: [("imaps", "tcp")],
        994: [("ircs", "tcp")],
        995: [("pop3s", "tcp")],
        1080: [("socks", "tcp")],
        1099: [("jms", "tcp")],
        1433: [("mssql", "tcp")],
        1434: [("mssql-monitor", "udp")],
        1521: [("oracle-db", "tcp")],
        1701: [("l2tp", "udp")],
        1723: [("pptp", "tcp")],
        1725: [("ibm-db2", "tcp")],
        1812: [("radius", "udp")],
        1813: [("radius-accounting", "udp")],
        1883: [("mqtt", "tcp")],
        1900: [("ssdp", "udp")],
        1935: [("rtmp", "tcp")],
        2049: [("nfs", "both")],
        2082: [("infowave", "tcp")],
        2181: [("zookeeper", "tcp")],
        2375: [("docker-api", "tcp")],
        2376: [("docker-api-tls", "tcp")],
        2379: [("etcd-client", "tcp")],
        2380: [("etcd-peer", "tcp")],
        2404: [("iec-104", "tcp")],
        3128: [("web-proxy", "tcp")],
        3260: [("iscsi", "tcp")],
        3306: [("mysql", "tcp")],
        3389: [("rdp", "tcp")],
        3478: [("stun", "udp")],
        3690: [("svn", "tcp")],
        4190: [("sieve", "tcp")],
        4500: [("ipsec-nat-t", "udp")],
        4840: [("opc-ua", "tcp")],
        5060: [("sip", "both")],
        5061: [("sip-tls", "tcp")],
        5222: [("xmpp-client", "tcp")],
        5269: [("xmpp-server", "tcp")],
        5353: [("mdns", "udp")],
        5355: [("llmnr", "udp")],
        5432: [("postgresql", "tcp")],
        5672: [("amqp", "tcp")],
        5683: [("coap", "udp")],
        5684: [("coaps", "udp")],
        5800: [("vnc-http", "tcp")],
        5900: [("vnc", "tcp")],
        5985: [("winrm", "tcp")],
        5986: [("winrm-tls", "tcp")],
        6000: [("x11", "tcp")],
        6379: [("redis", "tcp")],
        6443: [("kubernetes-api", "tcp")],
        6667: [("irc-alt", "tcp")],
        7000: [("cassandra", "tcp")],
        7001: [("weblogic-admin", "tcp")],
        8000: [("http-alt", "tcp")],
        8080: [("http-proxy", "tcp")],
        8443: [("https-alt", "tcp")],
        8500: [("consul", "tcp")],
        8883: [("mqtt-tls", "tcp")],
        9001: [("etcd-alt", "tcp")],
        9090: [("prometheus", "tcp")],
        9100: [("node-exporter", "tcp")],
        9200: [("elasticsearch", "tcp")],
        9300: [("elasticsearch-transport", "tcp")],
        10000: [("ndmp", "both")],
        10250: [("kubelet", "tcp")],
        11211: [("memcached", "both")],
        15672: [("rabbitmq-mgmt", "tcp")],
        27017: [("mongodb", "tcp")],
        27018: [("mongodb-shard", "tcp")],
        27019: [("mongodb-config", "tcp")],
        50000: [("db2", "tcp")],
        61613: [("stomp", "tcp")],
        61616: [("activemq", "tcp")],
    }

    # getservbyname cross-check candidates: (port, /etc/services name, protocol).
    # Only agreements are pinned; /etc/services is platform-dependent, so
    # lookups that fail or disagree are documented divergences and skipped.
    CROSS_CHECK: ClassVar[list] = [
        (7, "echo", "tcp"), (9, "discard", "tcp"), (13, "daytime", "tcp"),
        (19, "chargen", "tcp"), (20, "ftp-data", "tcp"), (21, "ftp", "tcp"),
        (22, "ssh", "tcp"), (23, "telnet", "tcp"), (25, "smtp", "tcp"),
        (37, "time", "tcp"), (43, "whois", "tcp"), (53, "domain", "tcp"),
        (67, "bootps", "udp"), (68, "bootpc", "udp"), (69, "tftp", "udp"),
        (70, "gopher", "tcp"), (79, "finger", "tcp"), (80, "http", "tcp"),
        (88, "kerberos", "tcp"), (110, "pop3", "tcp"), (119, "nntp", "tcp"),
        (123, "ntp", "udp"), (137, "netbios-ns", "udp"),
        (138, "netbios-dgm", "udp"), (139, "netbios-ssn", "tcp"),
        (143, "imap", "tcp"), (161, "snmp", "udp"), (179, "bgp", "tcp"),
        (389, "ldap", "tcp"), (443, "https", "tcp"), (445, "microsoft-ds", "tcp"),
        (514, "shell", "tcp"), (514, "syslog", "udp"), (515, "printer", "tcp"),
        (543, "klogin", "tcp"), (546, "dhcpv6-client", "udp"),
        (548, "afp", "tcp"), (554, "rtsp", "tcp"), (587, "submission", "tcp"),
        (636, "ldaps", "tcp"), (873, "rsync", "tcp"), (993, "imaps", "tcp"),
        (995, "pop3s", "tcp"), (1080, "socks", "tcp"), (1433, "ms-sql-s", "tcp"),
        (3306, "mysql", "tcp"), (3389, "ms-wbt-server", "tcp"),
        (5432, "postgresql", "tcp"), (6379, "redis", "tcp"),
    ]

    # Tool service name for a given /etc/services name where they differ.
    ALIASES: ClassVar[dict] = {
        "domain": "dns",
        "bootps": "dhcp-server",
        "bootpc": "dhcp-client",
        "microsoft-ds": "smb",
        "ms-sql-s": "mssql",
        "ms-wbt-server": "rdp",
    }

    def setUp(self):
        self.tool = PortListTool()

    def test_table_matches_authoring_fixture(self):
        table = port_module._SERVICE_TABLE
        self.assertEqual(sorted(table), sorted(self.FIXTURE))
        for port, expected_rows in self.FIXTURE.items():
            with self.subTest(port=port):
                actual = [(row["service"], row["protocol"]) for row in table[port]]
                self.assertEqual(actual, expected_rows)
                for row in table[port]:
                    self.assertTrue(row["note"].strip(), "every row carries a note")

    def test_required_task_ports_present(self):
        table = port_module._SERVICE_TABLE
        expected = {
            20: "ftp-data", 21: "ftp", 22: "ssh", 23: "telnet", 25: "smtp",
            53: "dns", 67: "dhcp-server", 68: "dhcp-client", 69: "tftp",
            80: "http", 110: "pop3", 123: "ntp", 137: "netbios-ns",
            138: "netbios-dgm", 139: "netbios-ssn", 143: "imap", 161: "snmp",
            162: "snmptrap", 389: "ldap", 445: "smb", 465: "smtps",
            514: "syslog", 587: "submission", 636: "ldaps", 993: "imaps",
            995: "pop3s", 1080: "socks", 1433: "mssql", 1434: "mssql-monitor",
            1521: "oracle-db", 2049: "nfs", 2181: "zookeeper", 3306: "mysql",
            3389: "rdp", 5432: "postgresql", 5672: "amqp", 5900: "vnc",
            6379: "redis", 8080: "http-proxy", 8443: "https-alt",
            9200: "elasticsearch", 11211: "memcached", 27017: "mongodb",
            1900: "ssdp", 5353: "mdns", 443: "https",
        }
        for port, service in expected.items():
            self.assertIn(service, {r["service"] for r in table[port]}, port)

    def test_protocol_split_at_514(self):
        rows = {r["service"]: r["protocol"] for r in port_module._SERVICE_TABLE[514]}
        self.assertEqual(rows["shell"], "tcp")
        self.assertEqual(rows["syslog"], "udp")

    def test_udp_contexts_marked(self):
        for port, service in ((1900, "ssdp"), (5353, "mdns"), (5355, "llmnr"), (137, "netbios-ns")):
            row = next(r for r in port_module._SERVICE_TABLE[port] if r["service"] == service)
            self.assertEqual(row["protocol"], "udp", port)

    def test_services_mode_output(self):
        result = self.tool.execute(mode="services", spec="22,80-81,7900,514")
        self.assertEqual(result["status"], "success")
        by_range = {entry["range"]: entry for entry in result["results"]}
        self.assertEqual(by_range["22"]["names"][0]["service"], "ssh")
        self.assertEqual(by_range["80-81"]["names"][0]["service"], "http")
        self.assertTrue(by_range["7900"]["unknown"])
        self.assertEqual(by_range["7900"]["names"], [])
        self.assertEqual(
            {n["service"] for n in by_range["514"]["names"]},
            {"shell", "syslog"},
        )
        self.assertIn("unknown means 'not in this table'", result["coverage_note"])

    def test_unknown_is_honest_not_wrong(self):
        result = self.tool.execute(mode="services", spec="7900-7905")
        self.assertTrue(all(entry["unknown"] for entry in result["results"]))

    def test_getservbyname_cross_check_where_platform_agrees(self):
        """Pin fixture rows only where /etc/services confirms them.

        getservbyname depends on the platform's /etc/services; lookups that
        fail or return a different port are divergences and are skipped.
        """
        checked = 0
        for port, name, protocol in self.CROSS_CHECK:
            with self.subTest(name=name, protocol=protocol):
                try:
                    found = socket.getservbyname(name, protocol)
                except OSError:
                    continue
                if found != port:
                    continue  # documented platform divergence, not pinned
                rows = port_module._SERVICE_TABLE.get(port, ())
                services = {row["service"] for row in rows}
                self.assertIn(self.ALIASES.get(name, name), services)
                checked += 1
        self.assertGreaterEqual(checked, 25, "cross-check must actually pin a meaningful subset")


class PortListAlgebraTest(unittest.TestCase):
    """300 seeded spec pairs against brute-force Python set operations."""

    def setUp(self):
        self.tool = PortListTool()
        self.rng = random.Random(2024)

    def _pair(self):
        return random_valid_spec(self.rng, top=3000), random_valid_spec(self.rng, top=3000)

    def test_algebra_matches_brute_force(self):
        for index in range(300):
            spec_a, spec_b = self._pair()
            set_a, set_b = oracle_spec_to_set(spec_a), oracle_spec_to_set(spec_b)
            with self.subTest(index=index, a=spec_a, b=spec_b):
                result = self.tool.execute(mode="algebra", spec_a=spec_a, spec_b=spec_b, op="union")
                self.assertEqual(oracle_spec_to_set(result["result_spec"]), set_a | set_b)
                self.assertEqual(result["count"], len(set_a | set_b))
                self.assertEqual(result["result_spec"], oracle_compress(set_a | set_b))

                result = self.tool.execute(mode="algebra", spec_a=spec_a, spec_b=spec_b, op="intersection")
                self.assertEqual(oracle_spec_to_set(result["result_spec"]), set_a & set_b)
                self.assertEqual(result["count"], len(set_a & set_b))
                self.assertEqual(result["result_spec"], oracle_compress(set_a & set_b))

                result = self.tool.execute(mode="algebra", spec_a=spec_a, spec_b=spec_b, op="difference")
                self.assertEqual(oracle_spec_to_set(result["result_spec"]), set_a - set_b)
                self.assertEqual(result["count"], len(set_a - set_b))
                self.assertEqual(result["result_spec"], oracle_compress(set_a - set_b))

    def test_hand_cases(self):
        self.assertEqual(
            self.tool.execute(mode="algebra", spec_a="20-30,40", spec_b="25-45", op="intersection")["result_spec"],
            "25-30,40",
        )
        self.assertEqual(
            self.tool.execute(mode="algebra", spec_a="20-30", spec_b="25-45", op="difference")["result_spec"],
            "20-24",
        )
        self.assertEqual(
            self.tool.execute(mode="algebra", spec_a="80,443", spec_b="443,8080", op="union")["result_spec"],
            "80,443,8080",
        )
        self.assertEqual(
            self.tool.execute(mode="algebra", spec_a="1-10", spec_b="1-10", op="difference")["result_spec"],
            "",
        )

    def test_invalid_operands(self):
        result = self.tool.execute(mode="algebra", spec_a="90-80", spec_b="80", op="union")
        self.assertEqual(result["status"], "error")
        self.assertIn("reversed_range", json.dumps(result["errors"]))


class PortListMutationBatteryTest(unittest.TestCase):
    """200 mutation cases: every documented rejection and tolerance."""

    BASES: ClassVar[list] = [
        "", "22", "80-90", "1-65535", "443", "22,80,443", "1000-2000,3000",
        "0-100", "53,53", "8080-8081",
    ]

    # (label, mutation, expected status, expected error code or None)
    MUTATIONS: ClassVar[list] = [
        ("reversed_range", lambda b: "90-80" if not b.strip() else b.replace("80-90", "90-80") if "80-90" in b else b + ",90-80", "error", "reversed_range"),
        ("overflow_end", lambda b: b + ",65536", "error", "out_of_range"),
        ("negative", lambda b: "-1" if not b.strip() else b + ",-1", "error", "missing_start"),
        ("alpha", lambda b: "a" if not b.strip() else b + ",a", "error", "non_numeric"),
        ("trailing_hyphen", lambda b: "80-" if not b.strip() else b + ",80-", "error", "missing_end"),
        ("leading_hyphen", lambda b: "-90" if not b.strip() else b + ",-90", "error", "missing_start"),
        ("empty_string", lambda b: "", "error", "empty_segment"),
        ("whitespace_tolerated", lambda b: " 80 , 443 " if not b.strip() else f" {b} ", "success", None),
        ("leading_zero", lambda b: "080,443" if not b.strip() else b + ",080", "error", "leading_zero"),
        ("unicode_fullwidth", lambda b: "８０" if not b.strip() else b + ",８０", "error", "non_numeric"),
        ("vulgar_fraction", lambda b: "½", "error", "non_numeric"),
        ("double_comma", lambda b: (b + ",,") if "," not in b else b.replace(",", ",,", 1), "error", "empty_segment"),
        ("trailing_comma", lambda b: b + "," if b.strip() else ",", "error", "empty_segment"),
        ("multi_hyphen", lambda b: "80-90-100" if not b.strip() else b + ",80-90-100", "error", "non_numeric"),
        ("space_joined_numbers", lambda b: "80 443", "error", "non_numeric"),
        ("port_zero_ok", lambda b: "0" if not b.strip() else b + ",0", "success", None),
        ("singleton_range", lambda b: "80-80" if not b.strip() else b + ",80-80", "success", None),
        ("all_disabled", lambda b: "all", "error", "all_keyword_disabled"),
        ("huge_number", lambda b: "99999" if not b.strip() else b + ",99999", "error", "out_of_range"),
        ("tab_whitespace", lambda b: "\t22,\t443\t", "success", None),
    ]

    def setUp(self):
        self.tool = PortListTool()

    def test_mutation_battery(self):
        cases = [(base, *mutation) for base in self.BASES for mutation in self.MUTATIONS]
        self.assertEqual(len(cases), 200)
        for base, label, mutate, expected_status, expected_code in cases:
            spec = mutate(base)
            with self.subTest(label=label, base=base, spec=spec):
                result = self.tool.execute(mode="parse", spec=spec)
                self.assertEqual(result["status"], expected_status, spec)
                if expected_code is not None:
                    codes = [e["code"] for e in result["errors"]]
                    self.assertIn(expected_code, codes, spec)
                    for error in result["errors"]:
                        self.assertIsInstance(error["position"], int)
                        self.assertGreaterEqual(error["position"], 0)
                        # A trailing empty segment points one past the last character.
                        self.assertLessEqual(error["position"], max(len(spec), 1))
                else:
                    self.assertEqual(result["errors"], [], spec)
                    self.assertEqual(
                        result["ports_total"],
                        len(oracle_spec_to_set(spec)) if spec.strip() else 0,
                    )
                # Whatever happens, the result must stay JSON-serializable and bounded.
                json.dumps(result)


class PortListExpandCheckTest(unittest.TestCase):
    """expand caps with the include_full guard, and the check policy audit."""

    def setUp(self):
        self.tool = PortListTool()

    def test_expand_small(self):
        result = self.tool.execute(mode="expand", spec="80-82")
        self.assertEqual(result["ports"], [80, 81, 82])
        self.assertEqual(result["total"], 3)
        self.assertFalse(result["truncated"])

    def test_expand_cap_error_then_full(self):
        result = self.tool.execute(mode="expand", spec="1-5000")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["errors"][0]["code"], "expand_cap_exceeded")
        self.assertEqual(result["ports_total"], 5000)
        full = self.tool.execute(mode="expand", spec="1-5000", include_full=True)
        self.assertEqual(full["status"], "success")
        self.assertEqual(full["ports"][0], 1)
        self.assertEqual(full["ports"][-1], 5000)
        self.assertEqual(len(set(full["ports"])), 5000)

    def test_check_blocked_and_allowed(self):
        result = self.tool.execute(
            mode="check",
            spec="22,80-90,1433-1434",
            blocked_ports="1433",
            allowed_ranges="1-1024,1433",
            max_ports=500,
        )
        self.assertEqual(result["status"], "success")
        self.assertFalse(result["compliant"])
        rules = {v["rule"] for v in result["violations"]}
        self.assertEqual(rules, {"blocked", "not_in_allowed_ranges"})
        blocked = next(v for v in result["violations"] if v["rule"] == "blocked")
        self.assertEqual(blocked["range"], "1433-1434")
        self.assertIn("1433", blocked["detail"])

    def test_check_compliant(self):
        result = self.tool.execute(mode="check", spec="22,80,443", allowed_ranges="1-1024", max_ports=10)
        self.assertTrue(result["compliant"])
        self.assertEqual(result["violations"], [])
        self.assertEqual(result["ports_total"], 3)

    def test_check_max_ports_exceeded(self):
        result = self.tool.execute(mode="check", spec="1-100", max_ports=50)
        self.assertFalse(result["compliant"])
        violation = next(v for v in result["violations"] if v["rule"] == "max_ports_exceeded")
        self.assertIn("100 ports exceed max_ports=50", violation["detail"])

    def test_check_invalid_policy(self):
        result = self.tool.execute(mode="check", spec="22", blocked_ports="99-1")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["policy_field"], "blocked_ports")


class PortListPathologicalTest(unittest.TestCase):
    """Full-universe expansion and very large specs stay fast and bounded."""

    def setUp(self):
        self.tool = PortListTool()

    def test_full_range_expand_exactly_65536_under_one_second(self):
        started = time.monotonic()
        result = self.tool.execute(mode="expand", spec="all", allow_all=True, include_full=True)
        elapsed = time.monotonic() - started
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["total"], 65536)
        self.assertEqual(result["ports"], list(range(65536)))
        self.assertLess(elapsed, 1.0, f"full expansion took {elapsed:.3f}s")

    def test_ten_thousand_entry_spec_bounded(self):
        rng = random.Random(7)
        segments = []
        expected = set()
        for _ in range(10_000):
            port = rng.randint(1024, 65535)
            segments.append(str(port))
            expected.add(port)
        spec = ",".join(segments)
        self.assertEqual(len(spec.split(",")), 10_000)
        started = time.monotonic()
        parsed = self.tool.execute(mode="parse", spec=spec)
        elapsed = time.monotonic() - started
        self.assertEqual(parsed["status"], "success")
        self.assertEqual(parsed["ports_total"], len(expected))
        self.assertLess(elapsed, 5.0, f"10k-entry parse took {elapsed:.3f}s")

        started = time.monotonic()
        compressed = self.tool.execute(mode="compress", spec=spec)
        elapsed = time.monotonic() - started
        self.assertEqual(compressed["status"], "success")
        self.assertEqual(oracle_spec_to_set(compressed["spec"]), expected)
        self.assertLess(elapsed, 5.0, f"10k-entry compress took {elapsed:.3f}s")

    def test_spec_length_cap_rejects_early(self):
        result = self.tool.execute(mode="parse", spec="80," * 400_000 + "443")
        self.assertEqual(result["status"], "error")
        self.assertIn("max_spec_length", result["error"])

    def test_error_list_is_bounded(self):
        spec = ",".join("65536" for _ in range(1_000))
        result = self.tool.execute(mode="parse", spec=spec)
        self.assertEqual(result["status"], "error")
        self.assertLessEqual(len(result["errors"]), 100)


class PortListRegistrationTest(unittest.TestCase):
    """Unit tests for registering the shipped port_list_tool.yaml as a tool component."""

    def setUp(self):
        self.config = Configer(path=os.path.abspath(YAML_PATH)).load()
        try:
            self.previous = ApplicationConfigManager().app_configer
        except ValueError:
            self.previous = None

    def tearDown(self):
        ApplicationConfigManager().app_configer = self.previous

    def test_schema(self):
        component = ComponentConfiger().load_by_configer(self.config)
        self.assertEqual(component.get_component_config_type(), ComponentEnum.TOOL.value)
        self.assertEqual(component.metadata_class, "PortListTool")

    def test_manager(self):
        configer = ToolConfiger().load_by_configer(self.config)
        app = AppConfiger()
        app.tool_configer_map = {configer.name: configer}
        ApplicationConfigManager().app_configer = app
        tool = ToolManager().get_instance_obj(configer.name)
        self.assertIsInstance(tool, PortListTool)
        self.assertEqual(tool.input_keys, ["mode", "spec"])

    def test_exported_from_package(self):
        from agentuniverse.agent.action.tool.common_tool import PortListTool as Exported
        from agentuniverse.agent.action.tool.common_tool import __all__ as tool_exports
        self.assertIs(Exported, PortListTool)
        self.assertIn("PortListTool", tool_exports)


if __name__ == "__main__":
    unittest.main()
