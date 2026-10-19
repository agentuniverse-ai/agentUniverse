#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Tests for HashCryptoTool."""

import hashlib
import hmac
import base64
import unittest

from agentuniverse.agent.action.tool.common_tool.hash_crypto_tool \
    import HashCryptoTool


class TestHash(unittest.TestCase):

    def test_sha256(self):
        tool = HashCryptoTool()
        result = tool.execute(mode="hash", text="hello", algorithm="sha256")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["digest"],
                         hashlib.sha256(b"hello").hexdigest())

    def test_md5(self):
        tool = HashCryptoTool()
        result = tool.execute(mode="hash", text="hello", algorithm="md5")
        self.assertEqual(result["digest"],
                         hashlib.md5(b"hello").hexdigest())

    def test_invalid_algorithm(self):
        tool = HashCryptoTool()
        result = tool.execute(mode="hash", text="x", algorithm="crc32")
        self.assertEqual(result["status"], "error")

    def test_default_algorithm_is_sha256(self):
        tool = HashCryptoTool()
        result = tool.execute(mode="hash", text="test")
        self.assertEqual(result["algorithm"], "sha256")


class TestHMAC(unittest.TestCase):

    def test_hmac_sha256(self):
        tool = HashCryptoTool()
        result = tool.execute(mode="hmac", text="data", key="secret",
                              algorithm="sha256")
        expected = hmac.new(b"secret", b"data", "sha256").hexdigest()
        self.assertEqual(result["digest"], expected)

    def test_hmac_missing_key(self):
        tool = HashCryptoTool()
        result = tool.execute(mode="hmac", text="data", key="")
        self.assertEqual(result["status"], "error")


class TestEncodeDecode(unittest.TestCase):

    def test_base64_encode(self):
        tool = HashCryptoTool()
        result = tool.execute(mode="encode", text="hello", encoding="base64")
        self.assertEqual(result["encoded"], base64.b64encode(b"hello").decode())

    def test_base64_decode(self):
        tool = HashCryptoTool()
        encoded = base64.b64encode(b"hello").decode()
        result = tool.execute(mode="decode", text=encoded, encoding="base64")
        self.assertEqual(result["decoded"], "hello")

    def test_hex_encode(self):
        tool = HashCryptoTool()
        result = tool.execute(mode="encode", text="AB", encoding="hex")
        self.assertEqual(result["encoded"], "4142")

    def test_hex_decode(self):
        tool = HashCryptoTool()
        result = tool.execute(mode="decode", text="4142", encoding="hex")
        self.assertEqual(result["decoded"], "AB")

    def test_decode_invalid_input(self):
        tool = HashCryptoTool()
        result = tool.execute(mode="decode", text="!!!notb64!!!", encoding="base64")
        self.assertEqual(result["status"], "error")

    def test_round_trip_base64(self):
        tool = HashCryptoTool()
        text = "Hello, World! 你好"
        encoded = tool.execute(mode="encode", text=text, encoding="base64")["encoded"]
        decoded = tool.execute(mode="decode", text=encoded, encoding="base64")["decoded"]
        self.assertEqual(decoded, text)


class TestValidation(unittest.TestCase):

    def test_unknown_mode(self):
        tool = HashCryptoTool()
        result = tool.execute(mode="encrypt")
        self.assertEqual(result["status"], "error")


if __name__ == "__main__":
    unittest.main(verbosity=2)
