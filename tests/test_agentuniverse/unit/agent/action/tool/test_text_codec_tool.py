#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: test_text_codec_tool.py

"""Offline unit tests for TextCodecTool.

The tool is built purely on the standard library (base64, urllib.parse,
hashlib, uuid) and never touches the network, so this suite runs fully
offline. Every assertion is deterministic: encode/decode modes are
checked against known vectors and exact round trips, hash digests
against published well-known values, and UUID v5 values against the
fixed RFC 4122 reference results. The only random output — UUID v4 —
is asserted by format, version, variant, and uniqueness instead of by
value.
"""

import hashlib
import unittest
import uuid

from agentuniverse.agent.action.tool.common_tool import TextCodecTool
from agentuniverse.agent.action.tool.common_tool.text_codec_tool import (
    TextCodecTool as DirectTextCodecTool,
)

# --------------------------------------------------------------------- #
# Known vectors (independent of hashlib output — literal expected values)
# --------------------------------------------------------------------- #
BASE64_HELLO = "aGVsbG8="
MD5_HELLO = "5d41402abc4b2a76b9719d911017c592"
SHA1_HELLO = "aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d"
SHA256_HELLO = "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
SHA512_HELLO = (
    "9b71d224bd62f3785d96d46ad3ea3d73319bfbc2890caadae2dff72519673ca7"
    "2323c3d99ba5c11d7c7acc6e14b8c5da0c4663475c2e5c3adef46f73bcdec043"
)
MD5_EMPTY = "d41d8cd98f00b204e9800998ecf8427e"
SHA1_EMPTY = "da39a3ee5e6b4b0d3255bfef95601890afd80709"
SHA256_EMPTY = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
SHA512_EMPTY = (
    "cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce"
    "47d0d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af927da3e"
)
# Reference value from the Python uuid documentation.
UUID5_DNS_PYTHON_ORG = "886313e1-3b8a-5372-9b90-0c9aee199e5d"
UUID5_URL_PYTHON_ORG = "54456a86-ff7a-507c-ab55-c4d535450fb7"
# Canonical (dashed) text form of uuid.NAMESPACE_DNS.
NAMESPACE_DNS_HEX = "6ba7b810-9dad-11d1-80b4-00c04fd430c8"
NAMESPACE_DNS_HEX_NODASH = "6ba7b8109dad11d180b400c04fd430c8"

UNICODE_TEXT = "héllo 世界 🌍 query?a=b&c=d"


class TextCodecToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib TextCodecTool."""

    def setUp(self) -> None:
        self.tool = TextCodecTool()

    # ------------------------------------------------------------------ #
    # base64 mode
    # ------------------------------------------------------------------ #

    def test_base64_encode_known_vector(self) -> None:
        result = self.tool.execute(
            mode="base64", operation="encode", text="hello"
        )
        self.assertEqual(
            result,
            {"mode": "base64", "operation": "encode", "result": BASE64_HELLO},
        )

    def test_base64_decode_known_vector(self) -> None:
        result = self.tool.execute(
            mode="base64", operation="decode", text=BASE64_HELLO
        )
        self.assertEqual(
            result,
            {"mode": "base64", "operation": "decode", "result": "hello"},
        )

    def test_base64_round_trip(self) -> None:
        for text in ("hello", UNICODE_TEXT, "line1\nline2\ttab", "a" * 5000):
            encoded = self.tool.execute(
                mode="base64", operation="encode", text=text
            )["result"]
            decoded = self.tool.execute(
                mode="base64", operation="decode", text=encoded
            )["result"]
            self.assertEqual(decoded, text)

    def test_base64_decode_invalid_alphabet(self) -> None:
        result = self.tool.execute(
            mode="base64", operation="decode", text="hello world!"
        )
        self.assertEqual(result["mode"], "base64")
        self.assertEqual(result["operation"], "decode")
        self.assertEqual(result["error"]["type"], "invalid_base64")
        self.assertIn("Base64", result["error"]["message"])

    def test_base64_decode_invalid_padding(self) -> None:
        result = self.tool.execute(
            mode="base64", operation="decode", text="aGVsbG8"
        )
        self.assertEqual(result["error"]["type"], "invalid_base64")

    def test_base64_decode_non_utf8_bytes(self) -> None:
        # "//8=" decodes to b"\xff\xff", which is not valid UTF-8.
        result = self.tool.execute(mode="base64", operation="decode", text="//8=")
        self.assertEqual(result["error"]["type"], "invalid_utf8")

    # ------------------------------------------------------------------ #
    # url mode
    # ------------------------------------------------------------------ #

    def test_url_encode_known_vector(self) -> None:
        result = self.tool.execute(
            mode="url", operation="encode", text="hello world/é"
        )
        self.assertEqual(result["result"], "hello%20world%2F%C3%A9")
        self.assertEqual(result["safe"], "")

    def test_url_encode_keeps_unreserved_characters(self) -> None:
        result = self.tool.execute(
            mode="url", operation="encode", text="AZaz09-_.~"
        )
        self.assertEqual(result["result"], "AZaz09-_.~")

    def test_url_encode_safe_option(self) -> None:
        result = self.tool.execute(
            mode="url", operation="encode", text="a/b&c=d", safe="/&="
        )
        self.assertEqual(result["result"], "a/b&c=d")
        self.assertEqual(result["safe"], "/&=")

    def test_url_encode_escapes_reserved_without_safe(self) -> None:
        result = self.tool.execute(
            mode="url", operation="encode", text="a/b&c=d"
        )
        self.assertEqual(result["result"], "a%2Fb%26c%3Dd")

    def test_url_round_trip(self) -> None:
        for safe in (None, "", "/&", "~"):
            encoded = self.tool.execute(
                mode="url", operation="encode", text=UNICODE_TEXT, safe=safe
            )["result"]
            decoded = self.tool.execute(
                mode="url", operation="decode", text=encoded
            )["result"]
            self.assertEqual(decoded, UNICODE_TEXT)

    def test_url_decode_known_vector(self) -> None:
        result = self.tool.execute(
            mode="url", operation="decode", text="hello%20world%2F%C3%A9"
        )
        self.assertEqual(result["result"], "hello world/é")

    def test_url_decode_rejects_dangling_percent(self) -> None:
        result = self.tool.execute(mode="url", operation="decode", text="100%")
        self.assertEqual(result["mode"], "url")
        self.assertEqual(result["error"]["type"], "invalid_percent_encoding")
        self.assertIn("%", result["error"]["message"])

    def test_url_decode_rejects_non_hex_escape(self) -> None:
        result = self.tool.execute(mode="url", operation="decode", text="a%zzb")
        self.assertEqual(result["error"]["type"], "invalid_percent_encoding")

    # ------------------------------------------------------------------ #
    # hex mode
    # ------------------------------------------------------------------ #

    def test_hex_encode_known_vector(self) -> None:
        result = self.tool.execute(mode="hex", operation="encode", text="hello")
        self.assertEqual(result["result"], "68656c6c6f")

    def test_hex_decode_case_insensitive(self) -> None:
        result = self.tool.execute(
            mode="hex", operation="decode", text="68656C6C6F"
        )
        self.assertEqual(result["result"], "hello")

    def test_hex_round_trip(self) -> None:
        for text in ("hello", UNICODE_TEXT, "0" * 1000):
            encoded = self.tool.execute(
                mode="hex", operation="encode", text=text
            )["result"]
            self.assertEqual(encoded, encoded.lower())
            decoded = self.tool.execute(
                mode="hex", operation="decode", text=encoded
            )["result"]
            self.assertEqual(decoded, text)

    def test_hex_decode_odd_length(self) -> None:
        result = self.tool.execute(mode="hex", operation="decode", text="abc")
        self.assertEqual(result["error"]["type"], "invalid_hex")

    def test_hex_decode_non_hex_digits(self) -> None:
        result = self.tool.execute(mode="hex", operation="decode", text="zz")
        self.assertEqual(result["error"]["type"], "invalid_hex")
        self.assertIn("hexadecimal", result["error"]["message"])

    def test_hex_decode_rejects_prefix_and_whitespace(self) -> None:
        for bad in ("0x68", "68 65", "68-65"):
            result = self.tool.execute(mode="hex", operation="decode", text=bad)
            self.assertEqual(result["error"]["type"], "invalid_hex")

    def test_hex_decode_non_utf8_bytes(self) -> None:
        result = self.tool.execute(mode="hex", operation="decode", text="ff")
        self.assertEqual(result["error"]["type"], "invalid_utf8")

    # ------------------------------------------------------------------ #
    # hash mode
    # ------------------------------------------------------------------ #

    def test_hash_known_vectors(self) -> None:
        cases = [
            ("md5", MD5_HELLO),
            ("sha1", SHA1_HELLO),
            ("sha256", SHA256_HELLO),
            ("sha512", SHA512_HELLO),
        ]
        for algorithm, expected in cases:
            with self.subTest(algorithm=algorithm):
                result = self.tool.execute(
                    mode="hash", text="hello", algorithm=algorithm
                )
                self.assertEqual(
                    result,
                    {
                        "mode": "hash",
                        "algorithm": algorithm,
                        "salted": False,
                        "result": expected,
                    },
                )

    def test_hash_empty_string_known_vectors(self) -> None:
        cases = [
            ("md5", MD5_EMPTY),
            ("sha1", SHA1_EMPTY),
            ("sha256", SHA256_EMPTY),
            ("sha512", SHA512_EMPTY),
        ]
        for algorithm, expected in cases:
            with self.subTest(algorithm=algorithm):
                result = self.tool.execute(
                    mode="hash", text="", algorithm=algorithm
                )
                self.assertEqual(result["result"], expected)
                self.assertEqual(result["salted"], False)

    def test_hash_unicode_text(self) -> None:
        # The digest must be taken over the UTF-8 encoding of the text.
        result = self.tool.execute(
            mode="hash", text=UNICODE_TEXT, algorithm="sha256"
        )
        self.assertEqual(
            result["result"],
            hashlib.sha256(UNICODE_TEXT.encode("utf-8")).hexdigest(),
        )

    def test_hash_salt_is_prefixed(self) -> None:
        result = self.tool.execute(
            mode="hash", text="hello", algorithm="sha256", salt="pepper"
        )
        self.assertEqual(result["salted"], True)
        self.assertEqual(
            result["result"],
            hashlib.sha256(b"pepperhello").hexdigest(),
        )

    def test_hash_salt_changes_digest(self) -> None:
        plain = self.tool.execute(
            mode="hash", text="hello", algorithm="sha256"
        )["result"]
        salted = self.tool.execute(
            mode="hash", text="hello", algorithm="sha256", salt="pepper"
        )["result"]
        self.assertNotEqual(plain, salted)

    # ------------------------------------------------------------------ #
    # uuid mode
    # ------------------------------------------------------------------ #

    def test_uuid5_dns_known_vector(self) -> None:
        result = self.tool.execute(
            mode="uuid", version=5, namespace="dns", name="python.org"
        )
        self.assertEqual(result["mode"], "uuid")
        self.assertEqual(result["version"], 5)
        self.assertEqual(result["namespace"], "dns")
        self.assertEqual(result["name"], "python.org")
        self.assertEqual(result["result"], UUID5_DNS_PYTHON_ORG)

    def test_uuid5_url_known_vector(self) -> None:
        result = self.tool.execute(
            mode="uuid", version=5, namespace="url", name="https://python.org"
        )
        self.assertEqual(result["result"], UUID5_URL_PYTHON_ORG)

    def test_uuid5_namespace_label_case_insensitive(self) -> None:
        upper = self.tool.execute(
            mode="uuid", version=5, namespace="DNS", name="python.org"
        )
        self.assertEqual(upper["namespace"], "dns")
        self.assertEqual(upper["result"], UUID5_DNS_PYTHON_ORG)

    def test_uuid5_custom_hex_namespace_matches_label(self) -> None:
        dashed = self.tool.execute(
            mode="uuid", version=5, namespace=NAMESPACE_DNS_HEX, name="python.org"
        )
        undashed = self.tool.execute(
            mode="uuid",
            version=5,
            namespace=NAMESPACE_DNS_HEX_NODASH,
            name="python.org",
        )
        self.assertEqual(dashed["result"], UUID5_DNS_PYTHON_ORG)
        self.assertEqual(undashed["result"], UUID5_DNS_PYTHON_ORG)

    def test_uuid5_deterministic(self) -> None:
        first = self.tool.execute(
            mode="uuid", version=5, namespace="dns", name="example.com"
        )["result"]
        second = self.tool.execute(
            mode="uuid", version=5, namespace="dns", name="example.com"
        )["result"]
        self.assertEqual(first, second)
        parsed = uuid.UUID(first)
        self.assertEqual(parsed.version, 5)

    def test_uuid5_different_namespaces_differ(self) -> None:
        dns = self.tool.execute(
            mode="uuid", version=5, namespace="dns", name="python.org"
        )["result"]
        url = self.tool.execute(
            mode="uuid", version=5, namespace="url", name="python.org"
        )["result"]
        self.assertNotEqual(dns, url)

    def test_uuid5_string_version_accepted(self) -> None:
        result = self.tool.execute(
            mode="uuid", version="5", namespace="dns", name="python.org"
        )
        self.assertEqual(result["result"], UUID5_DNS_PYTHON_ORG)

    def test_uuid5_invalid_namespace_payload(self) -> None:
        for bad in ("bogus", "zz", "not-a-uuid"):
            with self.subTest(namespace=bad):
                result = self.tool.execute(
                    mode="uuid", version=5, namespace=bad, name="python.org"
                )
                self.assertEqual(result["mode"], "uuid")
                self.assertEqual(result["error"]["type"], "invalid_namespace")
                for label in ("dns", "url", "oid", "x500"):
                    self.assertIn(label, result["error"]["message"])

    def test_uuid4_format_version_variant(self) -> None:
        result = self.tool.execute(mode="uuid", version=4)
        self.assertEqual(result["mode"], "uuid")
        self.assertEqual(result["version"], 4)
        parsed = uuid.UUID(result["result"])
        self.assertEqual(parsed.version, 4)
        self.assertIn(parsed.variant, (uuid.RFC_4122,))
        self.assertEqual(str(parsed), result["result"])

    def test_uuid4_unique_across_calls(self) -> None:
        values = {
            self.tool.execute(mode="uuid", version=4)["result"]
            for _ in range(64)
        }
        self.assertEqual(len(values), 64)

    # ------------------------------------------------------------------ #
    # Invalid inputs raise ValueError (strict validation)
    # ------------------------------------------------------------------ #

    def assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def test_invalid_mode(self) -> None:
        self.assert_invalid(mode="b64", text="hello")
        self.assert_invalid(mode=None, text="hello")
        self.assert_invalid(mode=123, text="hello")

    def test_invalid_operation(self) -> None:
        self.assert_invalid(mode="base64", operation="encrypt", text="hello")
        self.assert_invalid(mode="base64", operation=None, text="hello")
        self.assert_invalid(mode="url", operation="ENCODE", text="hello")

    def test_invalid_text_type(self) -> None:
        for bad in (None, 123, True, b"hello", ["hello"]):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="base64", operation="encode", text=bad)
                self.assert_invalid(mode="hash", text=bad, algorithm="sha256")

    def test_empty_text_rejected_for_encode_decode_modes(self) -> None:
        self.assert_invalid(mode="base64", operation="encode", text="")
        self.assert_invalid(mode="url", operation="encode", text="")
        self.assert_invalid(mode="hex", operation="decode", text="")

    def test_text_length_limit(self) -> None:
        oversized = "a" * 100_001
        self.assert_invalid(
            mode="base64", operation="encode", text=oversized
        )
        self.assert_invalid(mode="hash", text=oversized, algorithm="md5")
        ok = self.tool.execute(
            mode="hash", text="a" * 100_000, algorithm="md5"
        )
        self.assertEqual(len(ok["result"]), 32)

    def test_invalid_algorithm(self) -> None:
        self.assert_invalid(mode="hash", text="hello", algorithm="sha999")
        self.assert_invalid(mode="hash", text="hello", algorithm=None)
        self.assert_invalid(mode="hash", text="hello", algorithm="SHA256")

    def test_invalid_salt(self) -> None:
        self.assert_invalid(mode="hash", text="hello", algorithm="sha256", salt=123)
        self.assert_invalid(mode="hash", text="hello", algorithm="sha256", salt="")
        self.assert_invalid(
            mode="hash", text="hello", algorithm="sha256", salt=True
        )

    def test_invalid_safe(self) -> None:
        self.assert_invalid(
            mode="url", operation="encode", text="a b", safe="a b"
        )
        self.assert_invalid(mode="url", operation="encode", text="a", safe="%")
        self.assert_invalid(mode="url", operation="encode", text="a", safe="é")
        self.assert_invalid(mode="url", operation="encode", text="a", safe=123)

    def test_invalid_uuid_version(self) -> None:
        self.assert_invalid(mode="uuid", version=6)
        self.assert_invalid(mode="uuid", version=None)
        self.assert_invalid(mode="uuid", version=True)
        self.assert_invalid(mode="uuid", version="v4")

    def test_uuid5_missing_name_or_namespace(self) -> None:
        self.assert_invalid(mode="uuid", version=5, namespace="dns")
        self.assert_invalid(mode="uuid", version=5, namespace="dns", name="")
        self.assert_invalid(mode="uuid", version=5, name="python.org")
        self.assert_invalid(
            mode="uuid", version=5, namespace=123, name="python.org"
        )

    # ------------------------------------------------------------------ #
    # Packaging / registration
    # ------------------------------------------------------------------ #

    def test_class_defaults_and_export(self) -> None:
        self.assertIs(DirectTextCodecTool, TextCodecTool)
        self.assertEqual(self.tool.name, "text_codec_tool")
        self.assertIn("base64", self.tool.description)
        from agentuniverse.agent.action.tool.common_tool import __all__

        self.assertIn("TextCodecTool", __all__)


if __name__ == "__main__":
    unittest.main()
