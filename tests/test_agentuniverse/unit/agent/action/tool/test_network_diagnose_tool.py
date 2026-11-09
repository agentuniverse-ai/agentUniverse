#!/usr/bin/env python3

import hashlib
import socket
import ssl
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import yaml

from agentuniverse.agent.action.tool.common_tool import network_diagnose_tool as module
from agentuniverse.agent.action.tool.common_tool.network_diagnose_tool import (
    NetworkDiagnoseTool,
)
from agentuniverse.base.config.component_configer.configers.tool_configer import (
    ToolConfiger,
)
from agentuniverse.base.config.configer import Configer

MODULE = "agentuniverse.agent.action.tool.common_tool.network_diagnose_tool"
TOOL_DIR = Path(module.__file__).resolve().parent
REPOSITORY_ROOT = TOOL_DIR.parents[4]
YAML_PATH = TOOL_DIR / "network_diagnose_tool.yaml"
EXAMPLE_PATH = (
    REPOSITORY_ROOT
    / "examples"
    / "sample_standard_app"
    / "intelligence"
    / "agentic"
    / "tool"
    / "buildin"
    / "network_diagnose_tool.yaml"
)

CERTIFICATE = {
    "subject": ((("commonName", "www.example.com"),), (("organizationName", "Example"),)),
    "issuer": ((("commonName", "Example Intermediate CA"),),),
    "version": 3,
    "serialNumber": "0A1B2C3D",
    "notBefore": "Jan  1 00:00:00 2026 GMT",
    "notAfter": "Jan  1 00:00:00 2027 GMT",
    "subjectAltName": (("DNS", "www.example.com"), ("DNS", "example.com")),
}


class FakeSocket:
    def __init__(self) -> None:
        self.closed = False

    def __enter__(self) -> "FakeSocket":
        return self

    def __exit__(self, *_exc) -> bool:
        self.close()
        return False

    def close(self) -> None:
        self.closed = True


def tls_connection(certificate):
    connection = MagicMock()
    connection.__enter__.return_value = connection
    connection.__exit__.return_value = False
    connection.getpeercert.return_value = certificate
    connection.version.return_value = "TLSv1.3"
    connection.cipher.return_value = ("TLS_AES_256_GCM_SHA384", "TLSv1.3", 256)
    return connection


def address_info(family, address, canonical="example.com"):
    sockaddr = (address, 0, 0, 0) if family == socket.AF_INET6 else (address, 0)
    return (family, socket.SOCK_STREAM, 6, canonical, sockaddr)


class NetworkDiagnoseToolDnsTest(unittest.TestCase):
    def test_dns_deduplicates_and_lists_ipv4_before_ipv6(self) -> None:
        infos = [
            address_info(socket.AF_INET6, "2606:2800:220:1:248:1893:25c8:1946"),
            address_info(socket.AF_INET, "93.184.216.34"),
            address_info(socket.AF_INET, "93.184.216.34"),
        ]

        with (
            patch(f"{MODULE}.socket.getaddrinfo", return_value=infos),
            patch(
                f"{MODULE}.socket.gethostbyname_ex",
                return_value=("example.com", ["alias.example.com"], ["93.184.216.34"]),
            ),
        ):
            result = NetworkDiagnoseTool().execute(mode="dns", target="example.com")

        self.assertEqual(
            [item["address"] for item in result["addresses"]],
            ["93.184.216.34", "2606:2800:220:1:248:1893:25c8:1946"],
        )
        self.assertEqual([item["family"] for item in result["addresses"]], ["IPv4", "IPv6"])
        self.assertEqual(result["host"], "example.com")
        self.assertEqual(result["canonical_name"], "example.com")
        self.assertEqual(result["aliases"], ["alias.example.com"])
        self.assertIsNone(result["error"])

    def test_dns_encodes_internationalized_host_names(self) -> None:
        infos = [address_info(socket.AF_INET, "192.0.2.1", canonical="xn--bcher-kva.example")]

        with (
            patch(f"{MODULE}.socket.getaddrinfo", return_value=infos) as getaddrinfo,
            patch(f"{MODULE}.socket.gethostbyname_ex", return_value=("xn--bcher-kva.example", [], [])),
        ):
            result = NetworkDiagnoseTool().execute(mode="dns", target="bücher.example")

        self.assertEqual(getaddrinfo.call_args.args[0], "xn--bcher-kva.example")
        self.assertEqual(result["host"], "xn--bcher-kva.example")

    def test_dns_returns_a_resolver_error_instead_of_raising(self) -> None:
        with patch(
            f"{MODULE}.socket.getaddrinfo",
            side_effect=socket.gaierror(11001, "getaddrinfo failed"),
        ):
            result = NetworkDiagnoseTool().execute(mode="dns", target="missing.example")

        self.assertEqual(result["error"]["type"], "resolver_error")
        self.assertIn("getaddrinfo failed", result["error"]["message"])

    def test_dns_without_addresses_is_a_resolver_error(self) -> None:
        with patch(f"{MODULE}.socket.getaddrinfo", return_value=[]):
            result = NetworkDiagnoseTool().execute(mode="dns", target="empty.example")

        self.assertEqual(result["error"]["type"], "resolver_error")

    def test_dns_survives_an_alias_lookup_failure(self) -> None:
        infos = [address_info(socket.AF_INET, "93.184.216.34")]

        with (
            patch(f"{MODULE}.socket.getaddrinfo", return_value=infos),
            patch(
                f"{MODULE}.socket.gethostbyname_ex",
                side_effect=socket.gaierror(11001, "no IPv4 address"),
            ),
        ):
            result = NetworkDiagnoseTool().execute(mode="dns", target="example.com")

        self.assertEqual(result["aliases"], [])
        self.assertIsNone(result["error"])


class NetworkDiagnoseToolReverseTest(unittest.TestCase):
    def test_reverse_returns_the_ptr_name_and_family(self) -> None:
        with patch(
            f"{MODULE}.socket.gethostbyaddr",
            return_value=("dns.google", ["alias.example"], ["8.8.8.8"]),
        ):
            result = NetworkDiagnoseTool().execute(mode="reverse", target="8.8.8.8")

        self.assertEqual(result["hostname"], "dns.google")
        self.assertEqual(result["aliases"], ["alias.example"])
        self.assertEqual(result["family"], "IPv4")
        self.assertIsNone(result["error"])

    def test_reverse_accepts_ipv6(self) -> None:
        with patch(f"{MODULE}.socket.gethostbyaddr", return_value=("dns.google", [], [])) as gethostbyaddr:
            result = NetworkDiagnoseTool().execute(mode="reverse", target="2001:4860:4860::8888")

        self.assertEqual(result["family"], "IPv6")
        gethostbyaddr.assert_called_once_with("2001:4860:4860::8888")

    def test_reverse_rejects_a_host_name(self) -> None:
        with self.assertRaises(ValueError):
            NetworkDiagnoseTool().execute(mode="reverse", target="example.com")

    def test_reverse_reports_a_missing_ptr_record(self) -> None:
        with patch(
            f"{MODULE}.socket.gethostbyaddr",
            side_effect=socket.herror(1, "Unknown host"),
        ):
            result = NetworkDiagnoseTool().execute(mode="reverse", target="192.0.2.1")

        self.assertEqual(result["error"]["type"], "ptr_not_found")
        self.assertIn("Unknown host", result["error"]["message"])


class NetworkDiagnoseToolTlsTest(unittest.TestCase):
    def test_tls_reports_certificate_connection_and_validation(self) -> None:
        raw = FakeSocket()
        connection = tls_connection(CERTIFICATE)
        context = MagicMock()
        context.wrap_socket.return_value = connection

        with (
            patch(f"{MODULE}.socket.create_connection", return_value=raw),
            patch(f"{MODULE}.ssl.create_default_context", return_value=context),
        ):
            result = NetworkDiagnoseTool().execute(mode="tls", target="www.example.com", port="443", timeout="2.5")

        self.assertTrue(result["verified"])
        self.assertEqual(result["port"], 443)
        self.assertEqual(result["tls_version"], "TLSv1.3")
        self.assertEqual(
            result["cipher"],
            {"name": "TLS_AES_256_GCM_SHA384", "protocol": "TLSv1.3", "bits": 256},
        )
        certificate = result["certificate"]
        self.assertEqual(certificate["subject"]["commonName"], "www.example.com")
        self.assertEqual(certificate["issuer"]["commonName"], "Example Intermediate CA")
        self.assertEqual(certificate["not_after"], "2027-01-01T00:00:00Z")
        self.assertFalse(certificate["expired"])
        self.assertIsInstance(certificate["days_remaining"], int)
        self.assertEqual(
            certificate["subject_alt_names"],
            [
                {"type": "DNS", "value": "www.example.com"},
                {"type": "DNS", "value": "example.com"},
            ],
        )
        context.wrap_socket.assert_called_once_with(raw, server_hostname="www.example.com")
        self.assertTrue(raw.closed)

    def test_tls_reports_expired_certificates_with_negative_days(self) -> None:
        expired = dict(CERTIFICATE, notAfter="Jan  1 00:00:00 2020 GMT")
        connection = tls_connection(expired)
        context = MagicMock()
        context.wrap_socket.return_value = connection

        with (
            patch(f"{MODULE}.socket.create_connection", return_value=FakeSocket()),
            patch(f"{MODULE}.ssl.create_default_context", return_value=context),
        ):
            result = NetworkDiagnoseTool().execute(mode="tls", target="expired.example")

        self.assertTrue(result["certificate"]["expired"])
        self.assertLess(result["certificate"]["days_remaining"], 0)

    def test_tls_handshake_failure_is_structured_and_closes_the_socket(self) -> None:
        raw = FakeSocket()
        context = MagicMock()
        context.wrap_socket.side_effect = ssl.SSLError(1, "handshake failure")

        with (
            patch(f"{MODULE}.socket.create_connection", return_value=raw),
            patch(f"{MODULE}.ssl.create_default_context", return_value=context),
        ):
            result = NetworkDiagnoseTool().execute(mode="tls", target="example.com")

        self.assertEqual(result["error"]["type"], "tls_error")
        self.assertIn("handshake failure", result["error"]["message"])
        self.assertTrue(raw.closed)

    def test_tls_connection_refused_is_structured(self) -> None:
        with patch(
            f"{MODULE}.socket.create_connection",
            side_effect=ConnectionRefusedError(10061, "connection refused"),
        ):
            result = NetworkDiagnoseTool().execute(mode="tls", target="example.com")

        self.assertEqual(result["error"]["type"], "connection_refused")
        self.assertEqual(result["port"], 443)

    def test_tls_timeout_is_structured(self) -> None:
        with patch(
            f"{MODULE}.socket.create_connection",
            side_effect=TimeoutError("timed out"),
        ):
            result = NetworkDiagnoseTool().execute(mode="tls", target="example.com", timeout=1)

        self.assertEqual(result["error"]["type"], "timeout")

    def test_tls_verification_failure_reports_the_served_certificate(self) -> None:
        raw = FakeSocket()
        der = b"not-a-real-der-certificate"
        connection = tls_connection(None)
        connection.getpeercert.return_value = der
        context = MagicMock()
        context.wrap_socket.side_effect = [
            ssl.SSLCertVerificationError(1, "certificate verify failed: self-signed"),
            connection,
        ]

        with (
            patch(f"{MODULE}.socket.create_connection", return_value=raw),
            patch(f"{MODULE}.ssl.create_default_context", return_value=context),
        ):
            result = NetworkDiagnoseTool().execute(mode="tls", target="selfsigned.example")

        self.assertFalse(result["verified"])
        self.assertEqual(result["error"]["type"], "certificate_verification_failed")
        self.assertEqual(result["certificate"]["sha256"], hashlib.sha256(der).hexdigest())
        self.assertIn("BEGIN CERTIFICATE", result["certificate"]["pem"])

    def test_tls_accepts_a_bracketed_ipv6_literal(self) -> None:
        connection = tls_connection(CERTIFICATE)
        context = MagicMock()
        context.wrap_socket.return_value = connection

        with (
            patch(f"{MODULE}.socket.create_connection", return_value=FakeSocket()) as create_connection,
            patch(f"{MODULE}.ssl.create_default_context", return_value=context),
        ):
            result = NetworkDiagnoseTool().execute(mode="tls", target="[2001:db8::1]", port=8443)

        self.assertEqual(result["host"], "2001:db8::1")
        create_connection.assert_called_once_with(("2001:db8::1", 8443), timeout=5.0)


class NetworkDiagnoseToolArgumentTest(unittest.TestCase):
    def test_unknown_mode_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            NetworkDiagnoseTool().execute(mode="scan", target="example.com")

    def test_empty_target_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            NetworkDiagnoseTool().execute(mode="dns", target="   ")

    def test_target_with_control_characters_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            NetworkDiagnoseTool().execute(mode="dns", target="example.com\nother")

    def test_target_with_whitespace_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            NetworkDiagnoseTool().execute(mode="dns", target="exa mple.com")

    def test_non_string_target_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            NetworkDiagnoseTool().execute(mode="dns", target=1234)

    def test_port_outside_the_range_is_rejected(self) -> None:
        for port in (0, 65536, "0", "65536", -1):
            with self.subTest(port=port), self.assertRaises(ValueError):
                NetworkDiagnoseTool().execute(mode="tls", target="example.com", port=port)

    def test_boolean_port_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            NetworkDiagnoseTool().execute(mode="tls", target="example.com", port=True)

    def test_non_numeric_port_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            NetworkDiagnoseTool().execute(mode="tls", target="example.com", port="https")

    def test_timeout_outside_the_range_is_rejected(self) -> None:
        for timeout in (0, 30.1, "0", "-1", "nan", True):
            with self.subTest(timeout=timeout), self.assertRaises(ValueError):
                NetworkDiagnoseTool().execute(mode="tls", target="example.com", timeout=timeout)

    def test_mode_is_case_insensitive_and_trimmed(self) -> None:
        with patch(f"{MODULE}.socket.gethostbyaddr", return_value=("dns.google", [], [])):
            result = NetworkDiagnoseTool().execute(mode="  REVERSE  ", target=" 8.8.8.8 ")

        self.assertEqual(result["mode"], "reverse")
        self.assertEqual(result["target"], "8.8.8.8")


class NetworkDiagnoseToolConfigTest(unittest.TestCase):
    def test_component_yaml_registers_the_tool(self) -> None:
        config = Configer(str(YAML_PATH)).load()
        configer = ToolConfiger().load_by_configer(config)

        tool = NetworkDiagnoseTool().initialize_by_component_configer(configer)

        self.assertEqual(configer.name, "network_diagnose_tool")
        self.assertEqual(tool.name, "network_diagnose_tool")
        self.assertEqual(tool.input_keys, ["mode", "target"])

    def test_declared_input_keys_are_accepted_by_execute(self) -> None:
        import inspect

        configer = ToolConfiger().load_by_configer(Configer(str(YAML_PATH)).load())
        accepted = set(inspect.signature(NetworkDiagnoseTool.execute).parameters) - {"self"}

        self.assertTrue(set(configer.input_keys or []) <= accepted)

    def test_example_yaml_documents_every_argument(self) -> None:
        with EXAMPLE_PATH.open(encoding="utf-8") as example:
            config = yaml.safe_load(example)

        self.assertEqual(config["name"], "network_diagnose_tool")
        self.assertEqual(config["metadata"]["module"], MODULE)
        self.assertEqual(config["metadata"]["class"], "NetworkDiagnoseTool")
        self.assertEqual(config["input_keys"], ["mode", "target"])
        for token in ("mode", "target", "port", "timeout", "dns", "reverse", "tls"):
            self.assertIn(token, config["description"])

    def test_component_yaml_declares_every_execute_argument(self) -> None:
        import inspect

        with YAML_PATH.open(encoding="utf-8") as component:
            config = yaml.safe_load(component)

        accepted = set(inspect.signature(NetworkDiagnoseTool.execute).parameters) - {"self"}

        self.assertEqual(config["tool_type"], "func")
        self.assertEqual(config["metadata"]["module"], MODULE)
        self.assertEqual(config["metadata"]["class"], "NetworkDiagnoseTool")
        self.assertEqual(set(config["args_model"]), accepted)
        self.assertEqual(config["args_model_schema"]["required"], ["mode", "target"])
        self.assertEqual(
            config["args_model_schema"]["properties"]["mode"]["enum"],
            ["dns", "reverse", "tls"],
        )


if __name__ == "__main__":
    unittest.main()
