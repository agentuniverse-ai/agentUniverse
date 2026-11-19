#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_uuid_tool.py

"""Offline unit tests for UuidTool.

The tool is built purely on the standard library ``uuid`` module and
never touches the network, so this suite runs fully offline. Every
assertion is deterministic: parsing and field decoding are checked
against hand-verified literal ground truths (the RFC 4122 example
UUID, the nil and max UUIDs, the Python documentation ``uuid5`` vector),
against independently computed integer arithmetic (the 1582-10-15
Gregorian epoch math for version 1 timestamps), and against the
stdlib itself for in-test generated uuid1/uuid3/uuid4/uuid5 values,
which the tool must decode exactly.
"""

import datetime
import unittest
import uuid

from agentuniverse.agent.action.tool.common_tool import UuidTool
from agentuniverse.agent.action.tool.common_tool.uuid_tool import (
    UuidTool as DirectUuidTool,
)

# --------------------------------------------------------------------- #
# Hand-verified ground truths (independent literals, not stdlib calls)
# --------------------------------------------------------------------- #

# The classic RFC 4122 section 4.1.2 example UUID (version 1).
RFC_EXAMPLE = "f81d4fae-7dec-11d0-a765-00a0c91e6bf6"
RFC_EXAMPLE_FIELDS = {
    "time_low": {"hex": "f81d4fae", "int": 4162670510},
    "time_mid": {"hex": "7dec", "int": 32236},
    "time_hi_and_version": {"hex": "11d0", "int": 4560},
    "clock_seq_hi_and_reserved": {"hex": "a7", "int": 167},
    "clock_seq_low": {"hex": "65", "int": 101},
    "node": {"hex": "00a0c91e6bf6", "int": 690568981494},
}
# 0x1d0 << 48 | 0x7dec << 32 | 0xf81d4fae (version nibble dropped) —
# the 60-bit timestamp in 100-ns ticks since 1582-10-15T00:00:00 UTC.
RFC_EXAMPLE_TIMESTAMP = 130742845922168750
# 1582-10-15 + 130742845922168750 // 10 microseconds.
RFC_EXAMPLE_DATETIME = "1997-02-03T17:43:12.216875+00:00"
# (0x27 << 8) | 0x65 — the 14-bit clock sequence.
RFC_EXAMPLE_CLOCK_SEQ = 10085

NIL_UUID = "00000000-0000-0000-0000-000000000000"
MAX_UUID = "ffffffff-ffff-ffff-ffff-ffffffffffff"

# Reference values from the Python uuid documentation.
UUID5_DNS_PYTHON_ORG = "886313e1-3b8a-5372-9b90-0c9aee199e5d"
# uuid3(NAMESPACE_DNS, "python.org") — MD5-based, pinned literal.
UUID3_DNS_PYTHON_ORG = "6fa459ea-ee8a-3ca4-894e-db77e160355e"
UUID3_DNS_PYTHON_COM = "e27638fb-546d-33f6-818d-81e75096dbc6"

NAMESPACE_DNS_CANONICAL = "6ba7b810-9dad-11d1-80b4-00c04fd430c8"
NAMESPACE_DNS_NODASH = "6ba7b8109dad11d180b400c04fd430c8"

GREGORIAN_EPOCH = datetime.datetime(1582, 10, 15, tzinfo=datetime.timezone.utc)

# Pinned pair where raw string order and RFC 4122 field order diverge:
# 'F' (ASCII 70) sorts before 'a' (ASCII 97), but 0xF = 15 > 0xa = 10.
DIVERGE_A = "0000000F-0000-4000-8000-000000000000"
DIVERGE_B = "0000000a-0000-4000-8000-000000000000"

# Stdlib variant strings mapped to the tool's compact labels.
VARIANT_LABELS = {
    "reserved for NCS compatibility": "NCS",
    "specified in RFC 4122": "RFC 4122",
    "reserved for Microsoft compatibility": "Microsoft",
    "reserved for future definition": "reserved",
}


def v1_datetime(timestamp: int) -> str:
    """The standard RFC 4122 offset math, computed independently."""
    return (
        GREGORIAN_EPOCH
        + datetime.timedelta(microseconds=timestamp // 10)
    ).isoformat()


class UuidToolParseTest(unittest.TestCase):
    """Strict parsing and RFC 4122 field decoding."""

    def setUp(self) -> None:
        self.tool = UuidTool()

    def test_metadata(self) -> None:
        self.assertEqual(self.tool.name, "uuid_tool")
        self.assertIn("parse", self.tool.description)
        self.assertTrue(DirectUuidTool is UuidTool)

    def test_parse_rfc_example_ground_truth(self) -> None:
        result = self.tool.execute(mode="parse", uuid=RFC_EXAMPLE)
        self.assertEqual(result["mode"], "parse")
        self.assertTrue(result["valid"])
        self.assertEqual(result["canonical"], RFC_EXAMPLE)
        self.assertEqual(result["form"], "hyphenated")
        self.assertEqual(result["version"], 1)
        self.assertTrue(result["version_known"])
        self.assertEqual(result["variant"], "RFC 4122")
        self.assertEqual(result["fields"], RFC_EXAMPLE_FIELDS)

    def test_parse_nil_uuid(self) -> None:
        result = self.tool.execute(mode="parse", uuid=NIL_UUID)
        self.assertTrue(result["valid"])
        self.assertEqual(result["canonical"], NIL_UUID)
        self.assertEqual(result["version"], 0)
        self.assertFalse(result["version_known"])
        self.assertIn("version_note", result)
        self.assertEqual(result["variant"], "NCS")
        self.assertEqual(result["fields"]["node"]["int"], 0)

    def test_parse_max_uuid(self) -> None:
        result = self.tool.execute(mode="parse", uuid=MAX_UUID)
        self.assertTrue(result["valid"])
        self.assertEqual(result["version"], 15)
        self.assertFalse(result["version_known"])
        self.assertEqual(result["variant"], "reserved")
        self.assertEqual(result["int"], 2**128 - 1)

    def test_parse_accepts_urn_brace_and_case_forms(self) -> None:
        for raw, form in [
            (RFC_EXAMPLE.upper(), "hyphenated"),
            ("urn:uuid:" + RFC_EXAMPLE, "urn"),
            ("URN:UUID:" + RFC_EXAMPLE.upper(), "urn"),
            ("{" + RFC_EXAMPLE + "}", "braced"),
            ("urn:uuid:{" + RFC_EXAMPLE.upper() + "}", "urn+braced"),
            ("  {" + RFC_EXAMPLE + "}  ", "braced"),
            (RFC_EXAMPLE + "\n", "hyphenated"),
            ("\t" + RFC_EXAMPLE + "\t", "hyphenated"),
        ]:
            with self.subTest(raw=raw):
                result = self.tool.execute(mode="parse", uuid=raw)
                self.assertTrue(result["valid"])
                self.assertEqual(result["canonical"], RFC_EXAMPLE)
                self.assertEqual(result["form"], form)
                self.assertEqual(result["input"], raw)

    def test_parse_version_nibble_matrix(self) -> None:
        for nibble in range(16):
            raw = f"00000000-0000-{nibble:x}000-8000-000000000000"
            result = self.tool.execute(mode="parse", uuid=raw)
            self.assertTrue(result["valid"])
            self.assertEqual(result["version"], nibble)
            self.assertEqual(
                result["version_known"], 1 <= nibble <= 8
            )
            self.assertEqual(result["variant"], "RFC 4122")

    def test_parse_variant_matrix_matches_stdlib(self) -> None:
        for nibble in range(16):
            raw = f"00000000-0000-4000-{nibble:x}000-000000000000"
            result = self.tool.execute(mode="parse", uuid=raw)
            expected = VARIANT_LABELS[uuid.UUID(raw).variant]
            self.assertEqual(result["variant"], expected)

    def test_parse_stdlib_round_trip(self) -> None:
        for value in (
            uuid.uuid1(),
            uuid.uuid3(uuid.NAMESPACE_DNS, "round-trip"),
            uuid.uuid4(),
            uuid.uuid5(uuid.NAMESPACE_URL, "round-trip"),
        ):
            with self.subTest(value=value):
                result = self.tool.execute(mode="parse", uuid=str(value))
                self.assertTrue(result["valid"])
                self.assertEqual(result["canonical"], str(value))
                self.assertEqual(result["version"], value.version)
                self.assertEqual(result["int"], value.int)
                self.assertEqual(result["variant"], VARIANT_LABELS[value.variant])
                self.assertEqual(
                    result["fields"]["time_low"]["int"], value.time_low
                )
                self.assertEqual(
                    result["fields"]["time_mid"]["int"], value.time_mid
                )
                self.assertEqual(
                    result["fields"]["time_hi_and_version"]["int"],
                    value.time_hi_version,
                )
                self.assertEqual(
                    result["fields"]["clock_seq_hi_and_reserved"]["int"],
                    value.clock_seq_hi_variant,
                )
                self.assertEqual(
                    result["fields"]["clock_seq_low"]["int"], value.clock_seq_low
                )
                self.assertEqual(result["fields"]["node"]["int"], value.node)

    def test_parse_invalid_wrong_group_length(self) -> None:
        result = self.tool.execute(
            mode="parse", uuid="550e8400-e29b-41d4-a716-44665544000"
        )
        self.assertFalse(result["valid"])
        self.assertIn("group 5 (node) has 11 character(s)", result["reason"])
        self.assertIn("expected exactly 12", result["reason"])
        self.assertNotIn("canonical", result)

    def test_parse_invalid_missing_hyphens_bare_hex(self) -> None:
        result = self.tool.execute(
            mode="parse", uuid="550e8400e29b41d4a716446655440000"
        )
        self.assertFalse(result["valid"])
        self.assertIn("hyphens are missing", result["reason"])

    def test_parse_invalid_group_count(self) -> None:
        result = self.tool.execute(
            mode="parse", uuid="550e8400-e29b41d4-a716-446655440000"
        )
        self.assertFalse(result["valid"])
        self.assertIn("got 4 group(s)", result["reason"])
        self.assertIn("[8, 8, 4, 12]", result["reason"])

    def test_parse_invalid_non_hex_reports_position(self) -> None:
        for raw, position in [
            ("g5000000-0000-4000-8000-000000000000", 1),
            ("0000000G-0000-4000-8000-000000000000", 8),
            ("550e8400-E29B-x1d4-a716-446655440000", 15),
            ("550e8400-e29b-41d4-a716-44665544000z", 36),
        ]:
            with self.subTest(raw=raw):
                result = self.tool.execute(mode="parse", uuid=raw)
                self.assertFalse(result["valid"])
                self.assertIn(f"position {position} (1-based", result["reason"])

    def test_parse_invalid_prefix_braces_and_empty(self) -> None:
        for raw, fragment in [
            ("urn:oid:550e8400-e29b-41d4-a716-446655440000", "'urn:uuid:'"),
            ("{550e8400-e29b-41d4-a716-446655440000", "braces are unbalanced"),
            ("{}", "UUID body is empty"),
            ("urn:uuid:", "UUID body is empty"),
        ]:
            with self.subTest(raw=raw):
                result = self.tool.execute(mode="parse", uuid=raw)
                self.assertFalse(result["valid"])
                self.assertIn(fragment, result["reason"])


class UuidToolV1DecodeTest(unittest.TestCase):
    """Version 1 timestamp, clock sequence and node recovery."""

    def setUp(self) -> None:
        self.tool = UuidTool()

    def test_v1_decode_ground_truth(self) -> None:
        # Independent arithmetic check of the pinned literals first.
        reconstructed = (0x1D0 << 48) | (0x7DEC << 32) | 0xF81D4FAE
        self.assertEqual(reconstructed, RFC_EXAMPLE_TIMESTAMP)
        self.assertEqual(
            v1_datetime(RFC_EXAMPLE_TIMESTAMP), RFC_EXAMPLE_DATETIME
        )
        result = self.tool.execute(mode="v1_decode", uuid=RFC_EXAMPLE)
        self.assertEqual(result["uuid"], RFC_EXAMPLE)
        self.assertEqual(result["version"], 1)
        self.assertEqual(result["timestamp"], RFC_EXAMPLE_TIMESTAMP)
        self.assertEqual(result["datetime"], RFC_EXAMPLE_DATETIME)
        self.assertEqual(result["clock_sequence"], RFC_EXAMPLE_CLOCK_SEQ)
        self.assertEqual(
            result["node"], {"int": 690568981494, "hex": "00a0c91e6bf6"}
        )
        self.assertFalse(result["multicast_bit"])
        self.assertFalse(result["local_administration_bit"])
        self.assertIn("IEEE 802", result["node_note"])

    def test_v1_decode_stdlib_uuid1_round_trip(self) -> None:
        value = uuid.uuid1()
        result = self.tool.execute(mode="v1_decode", uuid=str(value))
        self.assertEqual(result["timestamp"], value.time)
        self.assertEqual(result["clock_sequence"], value.clock_seq)
        self.assertEqual(result["node"]["int"], value.node)
        # Cross-check against the uuid.UUID(...).time offset math.
        expected = (
            GREGORIAN_EPOCH
            + datetime.timedelta(microseconds=uuid.UUID(str(value)).time // 10)
        ).isoformat()
        self.assertEqual(result["datetime"], expected)
        self.assertEqual(
            result["multicast_bit"], bool(value.node & 0x010000000000)
        )

    def test_v1_decode_urn_form_and_sub_microsecond_truncation(self) -> None:
        odd = uuid.UUID(
            fields=(
                0xF81D4FAE + 1,
                0x7DEC,
                0x11D0,
                0xA7,
                0x65,
                0x00A0C91E6BF6,
            )
        )
        self.assertEqual(odd.version, 1)
        self.assertEqual(odd.time % 10, 1)
        result = self.tool.execute(
            mode="v1_decode", uuid="urn:uuid:" + str(odd)
        )
        self.assertEqual(result["timestamp"], odd.time)
        self.assertEqual(result["datetime"], v1_datetime(odd.time))
        self.assertEqual(result["sub_microsecond_remainder_100ns"], 1)

    def test_v1_decode_node_bit_note(self) -> None:
        multicast = uuid.UUID(
            fields=(0xF81D4FAE, 0x7DEC, 0x11D0, 0x83, 0x65, 0x010000000000)
        )
        result = self.tool.execute(mode="v1_decode", uuid=str(multicast))
        self.assertTrue(result["multicast_bit"])
        self.assertIn("random/pseudo-random", result["node_note"])

        local = uuid.UUID(
            fields=(0xF81D4FAE, 0x7DEC, 0x11D0, 0x83, 0x65, 0x020000000000)
        )
        result = self.tool.execute(mode="v1_decode", uuid=str(local))
        self.assertFalse(result["multicast_bit"])
        self.assertTrue(result["local_administration_bit"])
        self.assertIn("locally administered", result["node_note"])

    def test_v1_decode_non_v1_is_structured_error(self) -> None:
        result = self.tool.execute(mode="v1_decode", uuid=str(uuid.uuid4()))
        self.assertEqual(result["error"]["type"], "not_version_1")
        self.assertIn("version 4", result["error"]["message"])

    def test_v1_decode_invalid_uuid_is_structured_error(self) -> None:
        result = self.tool.execute(mode="v1_decode", uuid="zzz-not-a-uuid")
        self.assertEqual(result["error"]["type"], "invalid_uuid")
        self.assertIn("not a valid UUID", result["error"]["message"])


class UuidToolCompareTest(unittest.TestCase):
    """RFC 4122 field-lexicographic ordering with string-order notes."""

    def setUp(self) -> None:
        self.tool = UuidTool()

    def test_compare_time_low_is_most_significant(self) -> None:
        result = self.tool.execute(
            mode="compare",
            uuid_a="ffffffff-0000-4000-8000-000000000000",
            uuid_b="00000001-ffff-4fff-bfff-ffffffffffff",
        )
        self.assertEqual(result["order"], ">")
        self.assertEqual(result["canonical_string_order"], ">")
        self.assertIn("time_low is the most significant field", result["order_basis"])

    def test_compare_string_order_divergence_pinned_example(self) -> None:
        # Pinned: raw input order says A < B ('F' < 'a' in ASCII), but the
        # field order says A > B (0xF = 15 > 0xa = 10).
        self.assertTrue(DIVERGE_A < DIVERGE_B)  # raw string order
        result = self.tool.execute(
            mode="compare", uuid_a=DIVERGE_A, uuid_b=DIVERGE_B
        )
        self.assertEqual(result["order"], ">")
        self.assertEqual(result["canonical_string_order"], ">")
        self.assertEqual(result["input_string_order"], "<")
        self.assertTrue(result["string_order_divergence"])
        self.assertIn("not in canonical lowercase form", result["string_order_note"])

    def test_compare_equal_uuids_via_different_forms(self) -> None:
        result = self.tool.execute(
            mode="compare",
            uuid_a="urn:uuid:00000000-0000-4000-8000-000000000000",
            uuid_b="{00000000-0000-4000-8000-000000000000}",
        )
        self.assertEqual(result["order"], "=")
        self.assertEqual(result["canonical_string_order"], "=")
        # 'u' (117) sorts before '{' (123): same UUID, different raw strings.
        self.assertEqual(result["input_string_order"], "<")
        self.assertTrue(result["string_order_divergence"])

    def test_compare_identical_canonical_inputs_agree(self) -> None:
        result = self.tool.execute(
            mode="compare", uuid_a=RFC_EXAMPLE, uuid_b=RFC_EXAMPLE
        )
        self.assertEqual(result["order"], "=")
        self.assertEqual(result["input_string_order"], "=")
        self.assertFalse(result["string_order_divergence"])
        self.assertNotIn("string_order_note", result)

    def test_compare_whitespace_divergence_is_flagged(self) -> None:
        canonical = "00000001-0000-4000-8000-000000000000"
        self.assertTrue(canonical + " " > canonical)
        result = self.tool.execute(
            mode="compare", uuid_a=canonical + " ", uuid_b=canonical
        )
        self.assertEqual(result["order"], "=")
        self.assertEqual(result["canonical_string_order"], "=")
        self.assertEqual(result["input_string_order"], ">")
        self.assertTrue(result["string_order_divergence"])
        self.assertIn("surrounding whitespace", result["string_order_note"])

    def test_compare_later_fields_decide_when_time_low_equal(self) -> None:
        result = self.tool.execute(
            mode="compare",
            uuid_a="00000000-0001-4000-8000-000000000000",
            uuid_b="00000000-0002-4000-8000-000000000000",
        )
        self.assertEqual(result["order"], "<")
        self.assertIn(
            "(time_low, time_mid, time_hi_and_version, "
            "clock_seq_hi_and_reserved, clock_seq_low, node)",
            result["order_basis"],
        )

    def test_compare_invalid_uuid_is_structured_error(self) -> None:
        result = self.tool.execute(
            mode="compare", uuid_a=RFC_EXAMPLE, uuid_b="nope"
        )
        self.assertEqual(result["error"]["type"], "invalid_uuid")
        self.assertIn("uuid_b", result["error"]["message"])


class UuidToolNamespaceCheckTest(unittest.TestCase):
    """Brute-force (namespace, name) verification via the stdlib."""

    def setUp(self) -> None:
        self.tool = UuidTool()

    def test_namespace_check_uuid5_known_vector(self) -> None:
        result = self.tool.execute(
            mode="namespace_check",
            uuid=UUID5_DNS_PYTHON_ORG,
            namespace="dns",
            name="python.org",
        )
        self.assertTrue(result["match"])
        self.assertEqual(result["version"], 5)
        self.assertEqual(result["namespace"], "dns")
        self.assertEqual(result["name"], "python.org")
        self.assertEqual(result["expected"], UUID5_DNS_PYTHON_ORG)

    def test_namespace_check_uuid3_known_vector(self) -> None:
        result = self.tool.execute(
            mode="namespace_check",
            uuid=UUID3_DNS_PYTHON_ORG,
            namespace="DNS",
            name="python.org",
        )
        self.assertTrue(result["match"])
        self.assertEqual(result["version"], 3)
        self.assertEqual(result["namespace"], "dns")

    def test_namespace_check_negative_cases(self) -> None:
        wrong_name = self.tool.execute(
            mode="namespace_check",
            uuid=UUID3_DNS_PYTHON_ORG,
            namespace="dns",
            name="python.com",
        )
        self.assertFalse(wrong_name["match"])
        self.assertEqual(wrong_name["expected"], UUID3_DNS_PYTHON_COM)

        wrong_ns = self.tool.execute(
            mode="namespace_check",
            uuid=UUID5_DNS_PYTHON_ORG,
            namespace="url",
            name="python.org",
        )
        self.assertFalse(wrong_ns["match"])
        self.assertNotEqual(wrong_ns["expected"], UUID5_DNS_PYTHON_ORG)

    def test_namespace_check_custom_namespace_forms(self) -> None:
        for namespace in (NAMESPACE_DNS_CANONICAL, NAMESPACE_DNS_NODASH):
            with self.subTest(namespace=namespace):
                result = self.tool.execute(
                    mode="namespace_check",
                    uuid=UUID5_DNS_PYTHON_ORG,
                    namespace=namespace,
                    name="python.org",
                )
                self.assertTrue(result["match"])
                self.assertEqual(
                    result["namespace"], NAMESPACE_DNS_CANONICAL
                )

    def test_namespace_check_stdlib_round_trip(self) -> None:
        for namespace_label, namespace_uuid in (
            ("dns", uuid.NAMESPACE_DNS),
            ("url", uuid.NAMESPACE_URL),
            ("oid", uuid.NAMESPACE_OID),
            ("x500", uuid.NAMESPACE_X500),
        ):
            with self.subTest(namespace=namespace_label):
                value = uuid.uuid5(namespace_uuid, "agentuniverse")
                result = self.tool.execute(
                    mode="namespace_check",
                    uuid=str(value),
                    namespace=namespace_label.upper(),
                    name="agentuniverse",
                )
                self.assertTrue(result["match"])
                self.assertEqual(result["expected"], str(value))
                self.assertEqual(result["namespace"], namespace_label)

    def test_namespace_check_non_v3_v5_is_structured_error(self) -> None:
        result = self.tool.execute(
            mode="namespace_check",
            uuid=str(uuid.uuid4()),
            namespace="dns",
            name="python.org",
        )
        self.assertEqual(result["error"]["type"], "not_version_3_or_5")

    def test_namespace_check_invalid_namespace_is_structured_error(self) -> None:
        result = self.tool.execute(
            mode="namespace_check",
            uuid=UUID5_DNS_PYTHON_ORG,
            namespace="not-a-namespace",
            name="python.org",
        )
        self.assertEqual(result["error"]["type"], "invalid_namespace")

    def test_namespace_check_unencodable_name_is_structured_error(self) -> None:
        bad_name = "lone-surrogate-\ud800-name"
        for value, version in (
            (UUID3_DNS_PYTHON_ORG, 3),
            (UUID5_DNS_PYTHON_ORG, 5),
        ):
            with self.subTest(version=version):
                result = self.tool.execute(
                    mode="namespace_check",
                    uuid=value,
                    namespace="dns",
                    name=bad_name,
                )
                self.assertEqual(result["error"]["type"], "unencodable_name")
                self.assertIn("lone surrogate", result["error"]["message"])
                self.assertNotIn("match", result)

    def test_namespace_check_invalid_uuid_is_structured_error(self) -> None:
        result = self.tool.execute(
            mode="namespace_check",
            uuid="6fa459ea-ee8a-3ca4-894e",
            namespace="dns",
            name="python.org",
        )
        self.assertEqual(result["error"]["type"], "invalid_uuid")


class UuidToolBatchStatsTest(unittest.TestCase):
    """Batch profiling: histograms and nil detection."""

    def setUp(self) -> None:
        self.tool = UuidTool()

    def test_batch_stats_mixed_ground_truth(self) -> None:
        batch = [
            NIL_UUID,
            RFC_EXAMPLE,
            "urn:uuid:" + UUID5_DNS_PYTHON_ORG,
            "{" + MAX_UUID + "}",
            "not-a-uuid",
            "",
            "550e8400e29b41d4a716446655440000",
        ]
        result = self.tool.execute(mode="batch_stats", batch=batch)
        self.assertEqual(result["total"], 7)
        self.assertEqual(result["valid_count"], 4)
        self.assertEqual(result["invalid_count"], 3)
        self.assertEqual(
            result["version_histogram"], {"0": 1, "1": 1, "5": 1, "15": 1}
        )
        self.assertEqual(result["unknown_version_count"], 2)
        self.assertEqual(
            result["variant_histogram"],
            {"NCS": 1, "RFC 4122": 2, "reserved": 1},
        )
        self.assertEqual(result["nil_count"], 1)
        self.assertFalse(result["all_nil"])
        self.assertEqual(len(result["invalid_entries"]), 3)
        self.assertEqual(result["invalid_entries"][0]["index"], 4)
        self.assertIn("got 3 group(s)", result["invalid_entries"][0]["reason"])
        self.assertIn("UUID body is empty", result["invalid_entries"][1]["reason"])
        self.assertIn("hyphens are missing", result["invalid_entries"][2]["reason"])
        self.assertFalse(result["invalid_entries_truncated"])

    def test_batch_stats_all_nil(self) -> None:
        result = self.tool.execute(
            mode="batch_stats", batch=[NIL_UUID, "{" + NIL_UUID + "}"]
        )
        self.assertEqual(result["valid_count"], 2)
        self.assertEqual(result["version_histogram"], {"0": 2})
        self.assertEqual(result["nil_count"], 2)
        self.assertTrue(result["all_nil"])

    def test_batch_stats_stdlib_round_trip(self) -> None:
        batch = [str(uuid.uuid4()) for _ in range(10)]
        result = self.tool.execute(mode="batch_stats", batch=batch)
        self.assertEqual(result["valid_count"], 10)
        self.assertEqual(result["invalid_count"], 0)
        self.assertEqual(result["version_histogram"], {"4": 10})
        self.assertEqual(result["variant_histogram"], {"RFC 4122": 10})
        self.assertEqual(result["nil_count"], 0)
        self.assertFalse(result["all_nil"])

    def test_batch_stats_invalid_entries_are_bounded(self) -> None:
        result = self.tool.execute(
            mode="batch_stats", batch=["nope"] * 25
        )
        self.assertEqual(result["invalid_count"], 25)
        self.assertEqual(len(result["invalid_entries"]), 20)
        self.assertTrue(result["invalid_entries_truncated"])


class UuidToolValidationTest(unittest.TestCase):
    """Strict parameter validation (ValueError before any computation)."""

    def setUp(self) -> None:
        self.tool = UuidTool()

    def test_bad_mode_raises(self) -> None:
        for mode in (None, "generate", 4, True):
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                self.tool.execute(mode=mode, uuid=RFC_EXAMPLE)

    def test_missing_or_malformed_uuid_raises(self) -> None:
        for kwargs in (
            {},
            {"uuid": None},
            {"uuid": 123},
            {"uuid": True},
            {"uuid": "   "},
            {"uuid": "x" * 101},
        ):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                self.tool.execute(mode="parse", **kwargs)

    def test_compare_requires_both_uuids(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="compare", uuid_a=RFC_EXAMPLE)
        with self.assertRaises(ValueError):
            self.tool.execute(
                mode="compare", uuid_a=RFC_EXAMPLE, uuid_b=42
            )

    def test_namespace_check_requires_name_and_namespace(self) -> None:
        base = {"uuid": UUID5_DNS_PYTHON_ORG, "namespace": "dns", "name": "x"}
        for drop in ("name", "namespace"):
            kwargs = {k: v for k, v in base.items() if k != drop}
            with self.subTest(drop=drop), self.assertRaises(ValueError):
                self.tool.execute(mode="namespace_check", **kwargs)
        with self.assertRaises(ValueError):
            self.tool.execute(
                mode="namespace_check",
                uuid=UUID5_DNS_PYTHON_ORG,
                namespace="dns",
                name="",
            )

    def test_batch_parameter_validation(self) -> None:
        for batch in (None, "not-a-list", 42, [], [NIL_UUID, 7], ["x" * 101]):
            with self.subTest(batch=batch), self.assertRaises(ValueError):
                self.tool.execute(mode="batch_stats", batch=batch)

    def test_batch_size_cap(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(
                mode="batch_stats", batch=[NIL_UUID] * 10_001
            )

    def test_error_messages_are_prefixed(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="explode", uuid=RFC_EXAMPLE)
        self.assertTrue(str(ctx.exception).startswith("uuid_tool:"))


if __name__ == "__main__":
    unittest.main()
