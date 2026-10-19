#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: test_random_data_generator_tool.py

"""Offline unit tests for RandomDataGeneratorTool.

The tool is built purely on the standard library (random, uuid) and
never touches the network, so this suite runs fully offline. Every
assertion is deterministic: the tool's ``random_gen`` attribute is
substituted with ``random.Random(seed)`` and the outputs are checked
against literal known vectors captured with the same seeds, so a
regression in generation order, formatting or metadata cannot pass
silently. The default system random source is only asserted by
format, pool membership, and uniqueness.
"""

import random
import re
import unittest
import uuid

from agentuniverse.agent.action.tool.common_tool import RandomDataGeneratorTool
from agentuniverse.agent.action.tool.common_tool.random_data_generator_tool import (
    RandomDataGeneratorTool as DirectRandomDataGeneratorTool,
)

# --------------------------------------------------------------------- #
# Known vectors — outputs of random.Random(<seed>) through the tool,
# captured as literals so the assertions stand on their own.
# --------------------------------------------------------------------- #
NAME_42_FULL = ["Marco Haddad", "Liam Larsen", "Aisha Novak"]
NAME_7_FIRST = ["Yusuf", "Aiden", "Ananya"]
NAME_9_LAST = ["Ueda", "Bauer"]
EMAIL_42 = [
    "marco.haddad03@example.net",
    "aisha.novak28@example.com",
    "tara.garcia86@example.net",
]
EMAIL_7_CUSTOM = ["yusuf.jensen50@corp.example", "nadia.diallo09@corp.example"]
HEX_42_16B = [
    "9d79b1a37f31801cd11a6706fb40d6bd",
    "57526846903bb13ede562439e9c1b823",
]
HEX_7_4B_PREFIXED = ["tok_38b4e652", "tok_e44da7f2"]
UUID_42 = [
    "9d79b1a3-7f31-401c-911a-6706fb40d6bd",
    "57526846-903b-413e-9e56-2439e9c1b823",
]
UUID_7 = ["38b4e652-e44d-47f2-b70d-9e260e271365"]
HEX_1_8B = ["f5b165224a58b791", "df6af1d8303e61cd"]

EMAIL_PATTERN = re.compile(
    r"\A[a-z]+\.[a-z]+[0-9]{2}@[a-z0-9]([a-z0-9.-]*[a-z0-9])?\Z"
)
UUID_V4_PATTERN = re.compile(
    r"\A[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-"
    r"[0-9a-f]{12}\Z"
)
HEX_PATTERN = re.compile(r"\A[0-9a-f]+\Z")


def make_seeded_tool(seed: int) -> RandomDataGeneratorTool:
    """Build a tool whose random source is a freshly seeded Random."""
    tool = RandomDataGeneratorTool()
    tool.random_gen = random.Random(seed)
    return tool


class RandomDataGeneratorToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib random data tool."""

    def setUp(self) -> None:
        self.tool = RandomDataGeneratorTool()

    def assert_invalid(self, **kwargs) -> None:
        """Assert that malformed input raises the standard ValueError."""
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(**kwargs)
        self.assertIn("random_data_generator_tool:", str(ctx.exception))

    # ------------------------------------------------------------------ #
    # Deterministic known vectors (injected seeded RNG)
    # ------------------------------------------------------------------ #

    def test_name_known_vectors(self) -> None:
        result = make_seeded_tool(42).execute(mode="name", count=3)
        self.assertEqual(
            result,
            {
                "mode": "name",
                "style": "full",
                "count": 3,
                "entropy_bits": 11.2,
                "result": NAME_42_FULL,
            },
        )
        result = make_seeded_tool(7).execute(mode="name", count=3, style="first")
        self.assertEqual(
            result,
            {
                "mode": "name",
                "style": "first",
                "count": 3,
                "entropy_bits": 5.6,
                "result": NAME_7_FIRST,
            },
        )

    def test_name_style_is_case_insensitive(self) -> None:
        result = make_seeded_tool(9).execute(mode="name", count=2, style="LAST")
        self.assertEqual(
            result,
            {
                "mode": "name",
                "style": "last",
                "count": 2,
                "entropy_bits": 5.6,
                "result": NAME_9_LAST,
            },
        )

    def test_email_known_vector_builtin_pool(self) -> None:
        result = make_seeded_tool(42).execute(mode="email", count=3)
        self.assertEqual(
            result,
            {
                "mode": "email",
                "count": 3,
                "entropy_bits": 19.4,
                "result": EMAIL_42,
                "domain_pool": ["example.com", "example.org", "example.net"],
            },
        )

    def test_email_known_vector_custom_domain_normalized(self) -> None:
        # Surrounding whitespace is stripped and the domain lower-cased.
        result = make_seeded_tool(7).execute(
            mode="email", count=2, domain=" Corp.Example "
        )
        self.assertEqual(
            result,
            {
                "mode": "email",
                "count": 2,
                "entropy_bits": 17.8,
                "result": EMAIL_7_CUSTOM,
                "domain": "corp.example",
            },
        )

    def test_hex_known_vectors(self) -> None:
        result = make_seeded_tool(42).execute(mode="hex", count=2)
        self.assertEqual(
            result,
            {
                "mode": "hex",
                "bytes": 16,
                "prefix": "",
                "count": 2,
                "entropy_bits": 128,
                "result": HEX_42_16B,
            },
        )
        result = make_seeded_tool(7).execute(
            mode="hex", count=2, bytes=4, prefix="tok_"
        )
        self.assertEqual(
            result,
            {
                "mode": "hex",
                "bytes": 4,
                "prefix": "tok_",
                "count": 2,
                "entropy_bits": 32,
                "result": HEX_7_4B_PREFIXED,
            },
        )

    def test_digit_string_count_and_bytes_accepted(self) -> None:
        result = make_seeded_tool(1).execute(
            mode="hex", count="2", bytes="8"
        )
        self.assertEqual(result["count"], 2)
        self.assertEqual(result["bytes"], 8)
        self.assertEqual(result["result"], HEX_1_8B)

    def test_uuid_known_vectors(self) -> None:
        result = make_seeded_tool(42).execute(mode="uuid", count=2)
        self.assertEqual(
            result,
            {
                "mode": "uuid",
                "version": 4,
                "count": 2,
                "entropy_bits": 122,
                "result": UUID_42,
            },
        )
        result = make_seeded_tool(7).execute(mode="uuid")
        self.assertEqual(result["result"], UUID_7)

    def test_hex_and_uuid_share_the_random_stream(self) -> None:
        # Both modes consume 16 random bytes the same way, so with the
        # same seed the UUID's leading bytes (before the version and
        # variant bits are forced) equal the hex token's leading bytes.
        hex_token = make_seeded_tool(42).execute(mode="hex")["result"][0]
        uid = make_seeded_tool(42).execute(mode="uuid")["result"][0]
        self.assertEqual(uid.replace("-", "")[:12], hex_token[:12])

    # ------------------------------------------------------------------ #
    # Determinism and seeding semantics
    # ------------------------------------------------------------------ #

    def test_same_seed_same_output_different_seed_differs(self) -> None:
        first = make_seeded_tool(42).execute(mode="name", count=5)
        second = make_seeded_tool(42).execute(mode="name", count=5)
        self.assertEqual(first, second)
        other = make_seeded_tool(43).execute(mode="name", count=5)
        self.assertNotEqual(first["result"], other["result"])

    def test_default_random_source_is_system_random(self) -> None:
        self.assertIsInstance(self.tool.random_gen, random.SystemRandom)

    def test_injection_changes_the_stream(self) -> None:
        # The default source must not repeat the seeded stream.
        seeded = make_seeded_tool(42).execute(mode="name", count=3)
        system = self.tool.execute(mode="name", count=3)
        self.assertNotEqual(seeded["result"], system["result"])

    # ------------------------------------------------------------------ #
    # Format, pool membership and uniqueness (default source)
    # ------------------------------------------------------------------ #

    def test_name_values_come_from_the_pools(self) -> None:
        result = self.tool.execute(mode="name", count=50)
        for full_name in result["result"]:
            first, last = full_name.split(" ")
            self.assertIn(first, RandomDataGeneratorTool.FIRST_NAMES)
            self.assertIn(last, RandomDataGeneratorTool.LAST_NAMES)

    def test_email_format_and_reserved_domains(self) -> None:
        result = self.tool.execute(mode="email", count=50)
        for address in result["result"]:
            self.assertRegex(address, EMAIL_PATTERN)
            self.assertIn(
                address.rsplit("@", 1)[1], RandomDataGeneratorTool.DOMAINS
            )

    def test_hex_format_length_and_charset(self) -> None:
        for nbytes in (1, 16, 256):
            result = self.tool.execute(
                mode="hex", count=5, bytes=nbytes, prefix="tk-"
            )
            for token in result["result"]:
                self.assertTrue(token.startswith("tk-"))
                body = token[len("tk-"):]
                self.assertEqual(len(body), 2 * nbytes)
                self.assertRegex(body, HEX_PATTERN)

    def test_uuid_format_version_and_variant(self) -> None:
        result = self.tool.execute(mode="uuid", count=50)
        for uid in result["result"]:
            self.assertRegex(uid, UUID_V4_PATTERN)
            parsed = uuid.UUID(uid)
            self.assertEqual(parsed.version, 4)
            self.assertEqual(parsed.variant, uuid.RFC_4122)

    def test_batch_uniqueness(self) -> None:
        tokens = self.tool.execute(mode="hex", count=50, bytes=32)["result"]
        self.assertEqual(len(set(tokens)), 50)
        uids = self.tool.execute(mode="uuid", count=50)["result"]
        self.assertEqual(len(set(uids)), 50)

    # ------------------------------------------------------------------ #
    # Entropy metadata
    # ------------------------------------------------------------------ #

    def test_entropy_math(self) -> None:
        import math

        first = self.tool.execute(mode="name", style="first")
        self.assertEqual(
            first["entropy_bits"],
            round(math.log2(len(RandomDataGeneratorTool.FIRST_NAMES)), 1),
        )
        full = self.tool.execute(mode="name")
        self.assertEqual(
            full["entropy_bits"],
            round(
                math.log2(
                    len(RandomDataGeneratorTool.FIRST_NAMES)
                    * len(RandomDataGeneratorTool.LAST_NAMES)
                ),
                1,
            ),
        )
        token = self.tool.execute(mode="hex", bytes=16)
        self.assertEqual(token["entropy_bits"], 128)
        uid = self.tool.execute(mode="uuid")
        self.assertEqual(uid["entropy_bits"], 122)

    # ------------------------------------------------------------------ #
    # Bounds — the edges of every limit are accepted
    # ------------------------------------------------------------------ #

    def test_boundary_values_accepted(self) -> None:
        for count in (1, 50):
            result = self.tool.execute(mode="name", count=count)
            self.assertEqual(len(result["result"]), count)
        for nbytes in (1, 256):
            result = self.tool.execute(mode="hex", bytes=nbytes)
            self.assertEqual(len(result["result"][0]), 2 * nbytes)

    # ------------------------------------------------------------------ #
    # Error matrix — strict validation raises ValueError
    # ------------------------------------------------------------------ #

    def test_invalid_mode(self) -> None:
        self.assert_invalid(mode="password")
        self.assert_invalid(mode="")
        self.assert_invalid(mode=None)
        self.assert_invalid(mode=123)

    def test_invalid_count(self) -> None:
        self.assert_invalid(mode="name", count=0)
        self.assert_invalid(mode="name", count=51)
        self.assert_invalid(mode="name", count=-1)
        self.assert_invalid(mode="name", count=True)
        self.assert_invalid(mode="name", count=1.5)
        self.assert_invalid(mode="name", count="abc")
        self.assert_invalid(mode="name", count="")
        self.assert_invalid(mode="hex", count="12x")

    def test_invalid_style(self) -> None:
        self.assert_invalid(mode="name", style="nickname")
        self.assert_invalid(mode="name", style="")
        self.assert_invalid(mode="name", style=7)
        self.assert_invalid(mode="name", style=True)

    def test_invalid_bytes(self) -> None:
        self.assert_invalid(mode="hex", bytes=0)
        self.assert_invalid(mode="hex", bytes=257)
        self.assert_invalid(mode="hex", bytes=-4)
        self.assert_invalid(mode="hex", bytes=True)
        self.assert_invalid(mode="hex", bytes="16.0")

    def test_invalid_prefix(self) -> None:
        self.assert_invalid(mode="hex", prefix="a b")
        self.assert_invalid(mode="hex", prefix="tok\t")
        self.assert_invalid(mode="hex", prefix="toké")
        self.assert_invalid(mode="hex", prefix="t" * 17)
        self.assert_invalid(mode="hex", prefix=123)
        self.assert_invalid(mode="hex", prefix=True)

    def test_invalid_domain(self) -> None:
        self.assert_invalid(mode="email", domain="example")
        self.assert_invalid(mode="email", domain="-example.com")
        self.assert_invalid(mode="email", domain="example.com-")
        self.assert_invalid(mode="email", domain="ex ample.com")
        self.assert_invalid(mode="email", domain="example..com")
        self.assert_invalid(mode="email", domain=".example.com")
        self.assert_invalid(mode="email", domain="example.com/path")
        self.assert_invalid(mode="email", domain=123)
        self.assert_invalid(mode="email", domain=True)
        self.assert_invalid(mode="email", domain="")

    # ------------------------------------------------------------------ #
    # Packaging / registration
    # ------------------------------------------------------------------ #

    def test_class_defaults_and_export(self) -> None:
        self.assertIs(DirectRandomDataGeneratorTool, RandomDataGeneratorTool)
        self.assertEqual(self.tool.name, "random_data_generator_tool")
        self.assertIn("name", self.tool.description)
        from agentuniverse.agent.action.tool.common_tool import __all__

        self.assertIn("RandomDataGeneratorTool", __all__)


if __name__ == "__main__":
    unittest.main()
