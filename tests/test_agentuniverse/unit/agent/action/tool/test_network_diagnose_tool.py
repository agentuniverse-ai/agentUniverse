#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @FileName: test_network_diagnose_tool.py

"""Offline unit tests for NetworkDiagnoseTool.

Every test replaces the socket/SSL objects the tool touches, so the suite
runs without network access and without an API key.
"""

import pathlib
import socket
import unittest
from unittest.mock import patch

import yaml

import agentuniverse
from agentuniverse.agent.action.tool.common_tool import network_diagnose_tool
from agentuniverse.agent.action.tool.common_tool.network_diagnose_tool import NetworkDiagnoseTool

TOOL_PATH = network_diagnose_tool.__name__

REPO_ROOT = pathlib.Path(agentuniverse.__file__).resolve().parent.parent
COMPONENT_YAML = (REPO_ROOT / "agentuniverse" / "agent" / "action" / "tool" / "common_tool"
                  / "network_diagnose_tool.yaml")
EXAMPLE_YAML = (REPO_ROOT / "examples" / "sample_standard_app" / "intelligence"
                / "agentic" / "tool" / "buildin" / "network_diagnose_tool.yaml")


class FakeTlsSocket:
    """A minimal stand-in for the ssl.SSLSocket returned by the tool."""

    def __init__(self, cert, protocol="TLSv1.3", cipher=("TLS_AES_256_GCM_SHA384", "TLSv1.3", 256)):
        self._cert = cert
        self._protocol = protocol
        self._cipher = cipher
        self.closed = False

    def getpeercert(self):
        return self._cert

    def version(self):
        return self._protocol

    def cipher(self):
        return self._cipher

    def close(self):
        self.closed = True


def make_cert(not_after, not_before="Jan  1 00:00:00 2029 GMT"):
    """Build a certificate dictionary shaped like getpeercert() output."""
    return {
        "subject": ((("commonName", "example.com"),),),
        "issuer": ((("commonName", "Example CA"),),
                   (("organizationName", "Example Org"),)),
        "notBefore": not_before,
        "notAfter": not_after,
        "subjectAltName": (("DNS", "example.com"), ("DNS", "www.example.com")),
    }


class NetworkDiagnoseToolTest(unittest.TestCase):
    """Test cases for the NetworkDiagnoseTool class."""

    def setUp(self) -> None:
        """Create a fresh tool instance for every test."""
        self.tool = NetworkDiagnoseTool()

    def test_dns_mode_returns_deduplicated_addresses(self) -> None:
        """A host name resolves into distinct IPv4/IPv6 addresses plus aliases."""
        addrinfo = [
            (socket.AF_INET, None, None, None, ("93.184.216.34", 0)),
            (socket.AF_INET, None, None, None, ("93.184.216.34", 0)),
            (socket.AF_INET6, None, None, None, ("2606:2800:220:1::248", 0, 0, 0)),
        ]
        with patch(f"{TOOL_PATH}.socket.getaddrinfo", return_value=addrinfo), \
                patch(f"{TOOL_PATH}.socket.gethostbyname_ex",
                      return_value=("example.com", ["example.com", "alias.example.com"], ["93.184.216.34"])):
            result = self.tool.execute(mode="dns", target="example.com")

        self.assertEqual(result["mode"], "dns")
        self.assertEqual(result["ipv4"], ["93.184.216.34"])
        self.assertEqual(result["ipv6"], ["2606:2800:220:1::248"])
        self.assertEqual(result["address_count"], 2)
        self.assertEqual(result["aliases"], ["alias.example.com"])
        self.assertNotIn("error", result)

    def test_dns_failure_returns_readable_error(self) -> None:
        """A resolver failure is reported as an error key instead of an exception."""
        with patch(f"{TOOL_PATH}.socket.getaddrinfo",
                   side_effect=socket.gaierror(-2, "Name or service not known")):
            result = self.tool.execute(mode="dns", target="no-such-host.invalid")

        self.assertIn("error", result)
        self.assertIn("no-such-host.invalid", result["error"])
        self.assertNotIn("ipv4", result)

    def test_dns_without_aliases_still_succeeds(self) -> None:
        """getaddrinfo success is enough when the alias lookup fails."""
        addrinfo = [(socket.AF_INET, None, None, None, ("93.184.216.34", 0))]
        with patch(f"{TOOL_PATH}.socket.getaddrinfo", return_value=addrinfo), \
                patch(f"{TOOL_PATH}.socket.gethostbyname_ex",
                      side_effect=socket.gaierror(-2, "Name or service not known")):
            result = self.tool.execute(mode="dns", target="example.com")

        self.assertEqual(result["ipv4"], ["93.184.216.34"])
        self.assertEqual(result["aliases"], [])
        self.assertNotIn("error", result)

    def test_reverse_mode_returns_ptr(self) -> None:
        """An IP address reverses into its PTR record."""
        with patch(f"{TOOL_PATH}.socket.gethostbyaddr",
                   return_value=("example.com", ["alias.example.com"], ["93.184.216.34"])):
            result = self.tool.execute(mode="reverse", target="93.184.216.34")

        self.assertEqual(result["mode"], "reverse")
        self.assertEqual(result["ptr"], "example.com")
        self.assertEqual(result["aliases"], ["alias.example.com"])

    def test_reverse_requires_an_ip_address(self) -> None:
        """A host name is rejected before any lookup happens."""
        with self.assertRaises(ValueError):
            self.tool.execute(mode="reverse", target="example.com")

    def test_reverse_failure_returns_readable_error(self) -> None:
        """A missing PTR record is reported as an error key."""
        with patch(f"{TOOL_PATH}.socket.gethostbyaddr",
                   side_effect=socket.herror(1, "Unknown host")):
            result = self.tool.execute(mode="reverse", target="10.0.0.1")

        self.assertIn("error", result)
        self.assertIn("10.0.0.1", result["error"])

    def test_tls_mode_reports_certificate_validity(self) -> None:
        """A valid certificate reports subject, issuer and remaining days."""
        fake_socket = FakeTlsSocket(make_cert("Jan  1 00:00:00 2030 GMT"))
        with patch(f"{TOOL_PATH}._open_tls_socket", return_value=fake_socket) as open_socket:
            result = self.tool.execute(mode="tls", target="example.com", port=443, timeout=5.0)

        open_socket.assert_called_once_with("example.com", 443, 5.0)
        self.assertEqual(result["subject"], "example.com")
        self.assertEqual(result["issuer"], "Example CA")
        self.assertEqual(result["protocol"], "TLSv1.3")
        self.assertEqual(result["cipher"], "TLS_AES_256_GCM_SHA384")
        self.assertFalse(result["expired"])
        self.assertGreater(result["days_remaining"], 0)
        self.assertIn("www.example.com", result["subject_alt_names"])
        self.assertTrue(fake_socket.closed)

    def test_tls_mode_marks_expired_certificate(self) -> None:
        """An expired certificate reports a negative remaining time."""
        fake_socket = FakeTlsSocket(make_cert("Jan  1 00:00:00 2020 GMT"))
        with patch(f"{TOOL_PATH}._open_tls_socket", return_value=fake_socket):
            result = self.tool.execute(mode="tls", target="example.com")

        self.assertTrue(result["expired"])
        self.assertLess(result["days_remaining"], 0)

    def test_tls_connection_failure_returns_readable_error(self) -> None:
        """A refused connection is reported as an error key and closes the socket."""
        with patch(f"{TOOL_PATH}._open_tls_socket",
                   side_effect=ConnectionRefusedError(10061, "Connection refused")):
            result = self.tool.execute(mode="tls", target="example.com", port=8443)

        self.assertIn("error", result)
        self.assertIn("example.com:8443", result["error"])

    def test_invalid_mode_raises(self) -> None:
        """An unknown mode is a programming error, not a network error."""
        with self.assertRaises(ValueError):
            self.tool.execute(mode="traceroute", target="example.com")

    def test_empty_target_raises(self) -> None:
        """An empty target cannot be diagnosed."""
        with self.assertRaises(ValueError):
            self.tool.execute(mode="dns", target="   ")

    def test_tls_accepts_numeric_strings(self) -> None:
        """Numeric strings coming from a JSON tool call are converted."""
        fake_socket = FakeTlsSocket(make_cert("Jan  1 00:00:00 2030 GMT"))
        with patch(f"{TOOL_PATH}._open_tls_socket", return_value=fake_socket) as open_socket:
            result = self.tool.execute(mode="tls", target="example.com", port="8443", timeout="2.5")

        open_socket.assert_called_once_with("example.com", 8443, 2.5)
        self.assertEqual(result["port"], 8443)
        self.assertNotIn("error", result)

    def test_non_numeric_port_raises(self) -> None:
        """A value that cannot be coerced to an integer is rejected."""
        with self.assertRaises(ValueError):
            self.tool.execute(mode="tls", target="example.com", port="abc")

    def test_invalid_port_raises(self) -> None:
        """A port outside 1-65535 is rejected before connecting."""
        with self.assertRaises(ValueError):
            self.tool.execute(mode="tls", target="example.com", port=70000)

    def test_invalid_timeout_raises(self) -> None:
        """A timeout outside (0, 30] is rejected before connecting."""
        with self.assertRaises(ValueError):
            self.tool.execute(mode="tls", target="example.com", timeout=60)

    def test_mode_is_trimmed_and_case_insensitive(self) -> None:
        """A mode coming from a JSON tool call may carry padding or casing."""
        with patch(f"{TOOL_PATH}._resolve_addresses", return_value=(["1.2.3.4"], [], [])):
            result = self.tool.execute(mode="  DNS  ", target="example.com")

        self.assertEqual(result["mode"], "dns")
        self.assertEqual(result["ipv4"], ["1.2.3.4"])
        self.assertNotIn("error", result)

    def test_boolean_port_raises(self) -> None:
        """A boolean is not a port, even though bool subclasses int."""
        with self.assertRaises(ValueError):
            self.tool.execute(mode="tls", target="example.com", port=True)

    def test_component_yaml_matches_the_tool_class(self) -> None:
        """The shipped component yaml must point at the real module and class."""
        config = yaml.safe_load(COMPONENT_YAML.read_text(encoding="utf-8"))

        self.assertEqual(config["tool_type"], "func")
        self.assertEqual(config["input_keys"], ["mode", "target"])
        self.assertEqual(config["metadata"]["module"], NetworkDiagnoseTool.__module__)
        self.assertEqual(config["metadata"]["class"], NetworkDiagnoseTool.__name__)
        self.assertEqual(set(config["args_model"]), {"mode", "target", "port", "timeout"})
        self.assertEqual(config["args_model_schema"]["required"], ["mode", "target"])

    def test_example_config_documents_every_argument(self) -> None:
        """The example agent config stays in step with the tool's arguments."""
        example = yaml.safe_load(EXAMPLE_YAML.read_text(encoding="utf-8"))

        self.assertEqual(example["name"], "network_diagnose_tool")
        self.assertEqual(example["tool_type"], "func")
        self.assertEqual(example["input_keys"], ["mode", "target"])
        self.assertEqual(example["metadata"]["module"], NetworkDiagnoseTool.__module__)
        self.assertEqual(example["metadata"]["class"], NetworkDiagnoseTool.__name__)
        for keyword in ("dns", "reverse", "tls", "target", "port", "timeout"):
            self.assertIn(keyword, example["description"])


if __name__ == '__main__':
    unittest.main()
