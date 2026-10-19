#!/usr/bin/env python3

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: test_domain_validator_tool.py

"""Offline unit tests for DomainValidatorTool.

The tool is built purely on the standard library (re, ipaddress,
encodings.idna) and never touches the network or any WHOIS/DNS service,
so this suite runs fully offline. Every assertion is deterministic:
validation verdicts are checked against hand-computed ground truths for
each rejection rule individually, the 253/254 overall-length and 63/64
label-length boundaries are tested on both sides, the punycode paths
are pinned to the exact stdlib IDNA round trip (案例.cn <->
xn--fsqx61d.cn), and the TLD table categories are asserted against the
built-in indicative list.
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import DomainValidatorTool
from agentuniverse.agent.action.tool.common_tool.domain_validator_tool import (
    COUNTRY_CODE_TLDS,
    GENERIC_TLDS,
    NEW_GTLDS,
    DomainValidatorTool as DirectDomainValidatorTool,
)

# --------------------------------------------------------------------- #
# Ground truths independent of the implementation under test
# --------------------------------------------------------------------- #
# '案例'.encode('idna') == b'xn--fsqx61d'  (verified against the stdlib)
ACE_CASE_CN = "xn--fsqx61d.cn"
UNICODE_CASE_CN = "案例.cn"
ACE_MUNCHEN_DE = "xn--mnchen-3ya.de"
UNICODE_MUNCHEN_DE = "münchen.de"

# 253 characters exactly: 63+63+63+30+30 labels + 4 dots.
HOST_253 = ".".join(["a" * 63, "b" * 63, "c" * 63, "d" * 30, "e" * 30])
assert len(HOST_253) == 253
# 254 characters exactly: 63+63+62+32+30 labels + 4 dots.
HOST_254 = ".".join(["a" * 63, "b" * 63, "c" * 62, "f" * 32, "e" * 30])
assert len(HOST_254) == 254


class DomainValidatorToolValidateTest(unittest.TestCase):
    """Offline deterministic test cases for the validate mode."""

    def setUp(self) -> None:
        self.tool = DomainValidatorTool()

    # ------------------------------------------------------------------ #
    # Valid ground truths
    # ------------------------------------------------------------------ #

    def test_valid_multi_label(self) -> None:
        result = self.tool.execute(mode="validate", hostname="example.com")
        self.assertEqual(
            result,
            {
                "mode": "validate",
                "hostname": "example.com",
                "trailing_dot_stripped": False,
                "verdict": "valid",
                "is_ip_literal": False,
                "reasons": [],
                "warnings": [],
            },
        )

    def test_valid_deep_subdomain(self) -> None:
        result = self.tool.execute(
            mode="validate", hostname="www.blog.example.co.uk"
        )
        self.assertEqual(result["verdict"], "valid")
        self.assertEqual(result["reasons"], [])

    def test_valid_hyphens_and_digits(self) -> None:
        for host in (
            "a-b.example.com",
            "s3.amazonaws.com",
            "xn--fsqx61d.cn",
            "9fans.example.org",
        ):
            result = self.tool.execute(mode="validate", hostname=host)
            self.assertEqual(result["verdict"], "valid", host)

    def test_uppercase_input_is_normalized(self) -> None:
        result = self.tool.execute(
            mode="validate", hostname="WWW.Example.COM"
        )
        self.assertEqual(result["hostname"], "www.example.com")
        self.assertEqual(result["verdict"], "valid")

    def test_trailing_dot_stripped_and_reported(self) -> None:
        result = self.tool.execute(
            mode="validate", hostname="example.com."
        )
        self.assertTrue(result["trailing_dot_stripped"])
        self.assertEqual(result["hostname"], "example.com")
        self.assertEqual(result["verdict"], "valid")

    def test_valid_at_253_char_boundary(self) -> None:
        result = self.tool.execute(mode="validate", hostname=HOST_253)
        self.assertEqual(result["verdict"], "valid")
        self.assertEqual(result["reasons"], [])

    def test_valid_label_at_63_char_boundary(self) -> None:
        result = self.tool.execute(
            mode="validate", hostname="a" * 63 + ".example.com"
        )
        self.assertEqual(result["verdict"], "valid")

    # ------------------------------------------------------------------ #
    # Each rejection reason, individually triggered
    # ------------------------------------------------------------------ #

    def test_reject_254_char_overall_length(self) -> None:
        result = self.tool.execute(mode="validate", hostname=HOST_254)
        self.assertEqual(result["verdict"], "invalid")
        self.assertEqual(len(result["reasons"]), 1)
        self.assertIn("253", result["reasons"][0])
        self.assertIn("254 characters", result["reasons"][0])

    def test_reject_label_64_chars(self) -> None:
        result = self.tool.execute(
            mode="validate", hostname="a" * 64 + ".example.com"
        )
        self.assertEqual(result["verdict"], "invalid")
        self.assertEqual(len(result["reasons"]), 1)
        self.assertIn("63", result["reasons"][0])

    def test_reject_underscore_by_default(self) -> None:
        result = self.tool.execute(
            mode="validate", hostname="foo_bar.example.com"
        )
        self.assertEqual(result["verdict"], "invalid")
        self.assertTrue(
            any("underscore" in r for r in result["reasons"]),
            result["reasons"],
        )

    def test_underscore_lenient_option_downgrades_to_warning(self) -> None:
        result = self.tool.execute(
            mode="validate",
            hostname="foo_bar.example.com",
            allow_underscores=True,
        )
        self.assertEqual(result["verdict"], "valid")
        self.assertTrue(
            any("underscore" in w for w in result["warnings"]),
            result["warnings"],
        )

    def test_reject_other_bad_charset(self) -> None:
        result = self.tool.execute(
            mode="validate", hostname="example!.com"
        )
        self.assertEqual(result["verdict"], "invalid")
        self.assertTrue(
            any("disallowed characters" in r for r in result["reasons"]),
            result["reasons"],
        )

    def test_reject_non_ascii_charset(self) -> None:
        result = self.tool.execute(
            mode="validate", hostname="exämple.com"
        )
        self.assertEqual(result["verdict"], "invalid")
        self.assertTrue(
            any("non-ASCII" in r for r in result["reasons"]),
            result["reasons"],
        )

    def test_reject_leading_hyphen(self) -> None:
        result = self.tool.execute(
            mode="validate", hostname="-bad.example.com"
        )
        self.assertEqual(result["verdict"], "invalid")
        self.assertTrue(
            any("hyphen" in r for r in result["reasons"]),
            result["reasons"],
        )

    def test_reject_trailing_hyphen(self) -> None:
        result = self.tool.execute(
            mode="validate", hostname="bad-.example.com"
        )
        self.assertEqual(result["verdict"], "invalid")
        self.assertTrue(
            any("hyphen" in r for r in result["reasons"]),
            result["reasons"],
        )

    def test_reject_empty_label(self) -> None:
        result = self.tool.execute(
            mode="validate", hostname="example..com"
        )
        self.assertEqual(result["verdict"], "invalid")
        self.assertTrue(
            any("empty" in r for r in result["reasons"]),
            result["reasons"],
        )

    def test_reject_leading_dot_empty_label(self) -> None:
        result = self.tool.execute(mode="validate", hostname=".example.com")
        self.assertEqual(result["verdict"], "invalid")
        self.assertTrue(
            any("empty" in r for r in result["reasons"]),
            result["reasons"],
        )

    def test_reject_single_label_by_default(self) -> None:
        result = self.tool.execute(mode="validate", hostname="localhost")
        self.assertEqual(result["verdict"], "invalid")
        self.assertTrue(
            any("single-label" in r for r in result["reasons"]),
            result["reasons"],
        )

    def test_single_label_option_downgrades_to_warning(self) -> None:
        result = self.tool.execute(
            mode="validate", hostname="localhost", allow_single_label=True
        )
        self.assertEqual(result["verdict"], "valid")
        self.assertTrue(
            any("single-label" in w for w in result["warnings"]),
            result["warnings"],
        )

    def test_reject_numeric_tld(self) -> None:
        result = self.tool.execute(mode="validate", hostname="example.123")
        self.assertEqual(result["verdict"], "invalid")
        self.assertTrue(
            any("not purely alphabetic" in r for r in result["reasons"]),
            result["reasons"],
        )

    def test_reject_single_char_tld(self) -> None:
        result = self.tool.execute(mode="validate", hostname="example.c")
        self.assertEqual(result["verdict"], "invalid")
        self.assertTrue(
            any("at least two" in r for r in result["reasons"]),
            result["reasons"],
        )

    def test_reject_mixed_alphanumeric_tld(self) -> None:
        result = self.tool.execute(
            mode="validate", hostname="example.c0m"
        )
        self.assertEqual(result["verdict"], "invalid")
        self.assertTrue(
            any("not purely alphabetic" in r for r in result["reasons"]),
            result["reasons"],
        )

    def test_multiple_reasons_collected_together(self) -> None:
        # 64-char label AND a bad TLD in one hostname.
        result = self.tool.execute(
            mode="validate", hostname="a" * 64 + ".example.123"
        )
        self.assertEqual(result["verdict"], "invalid")
        self.assertEqual(len(result["reasons"]), 2)

    # ------------------------------------------------------------------ #
    # IP-literal routing
    # ------------------------------------------------------------------ #

    def test_ipv4_literal_gets_dedicated_verdict(self) -> None:
        result = self.tool.execute(
            mode="validate", hostname="192.168.1.1"
        )
        self.assertEqual(result["verdict"], "ip_literal")
        self.assertTrue(result["is_ip_literal"])
        self.assertIn("IPv4", result["reasons"][0])
        self.assertIn("not a domain name", result["reasons"][0])

    def test_ipv6_literal_gets_dedicated_verdict(self) -> None:
        result = self.tool.execute(mode="validate", hostname="::1")
        self.assertEqual(result["verdict"], "ip_literal")
        self.assertIn("IPv6", result["reasons"][0])

    def test_five_octets_is_not_an_ip_literal(self) -> None:
        # 1.2.3.4.5 is not a valid IPv4 address and must fall through to
        # the domain rules (numeric TLD), not the ip_literal verdict.
        result = self.tool.execute(mode="validate", hostname="1.2.3.4.5")
        self.assertEqual(result["verdict"], "invalid")
        self.assertFalse(result["is_ip_literal"])
        self.assertTrue(
            any("not purely alphabetic" in r for r in result["reasons"]),
            result["reasons"],
        )


class DomainValidatorToolInfoTest(unittest.TestCase):
    """Offline deterministic test cases for the info mode."""

    def setUp(self) -> None:
        self.tool = DomainValidatorTool()

    def test_structure_of_deep_subdomain(self) -> None:
        # The registered-domain guess is the last two labels, so the
        # 'co' label counts as a subdomain here (the tool deliberately
        # does not ship a full Public Suffix List).
        result = self.tool.execute(
            mode="info", hostname="www.blog.example.co.uk"
        )
        self.assertEqual(
            result,
            {
                "mode": "info",
                "hostname": "www.blog.example.co.uk",
                "trailing_dot_stripped": False,
                "is_ip_literal": False,
                "labels": 5,
                "registered_domain": "co.uk",
                "tld": "uk",
                "subdomain_count": 3,
                "punycode": {
                    "applicable": False,
                    "has_ace_label": False,
                    "ace_form": "www.blog.example.co.uk",
                    "unicode_form": None,
                    "error": None,
                },
            },
        )

    def test_structure_of_bare_domain(self) -> None:
        result = self.tool.execute(mode="info", hostname="example.com")
        self.assertEqual(result["registered_domain"], "example.com")
        self.assertEqual(result["tld"], "com")
        self.assertEqual(result["subdomain_count"], 0)
        self.assertEqual(result["labels"], 2)

    def test_single_label_has_no_tld(self) -> None:
        result = self.tool.execute(mode="info", hostname="localhost")
        self.assertEqual(result["registered_domain"], "localhost")
        self.assertIsNone(result["tld"])
        self.assertEqual(result["subdomain_count"], 0)

    def test_punycode_decode_round_trip(self) -> None:
        # xn--fsqx61d.cn decodes to 案例.cn via the stdlib IDNA codec.
        result = self.tool.execute(mode="info", hostname=ACE_CASE_CN)
        punycode = result["punycode"]
        self.assertTrue(punycode["applicable"])
        self.assertTrue(punycode["has_ace_label"])
        self.assertEqual(punycode["ace_form"], ACE_CASE_CN)
        self.assertEqual(punycode["unicode_form"], UNICODE_CASE_CN)
        self.assertIsNone(punycode["error"])
        self.assertEqual(result["registered_domain"], ACE_CASE_CN)
        self.assertEqual(result["tld"], "cn")
        # Round trip: the decoded Unicode form re-encodes to the input.
        self.assertEqual(
            punycode["unicode_form"].encode("idna").decode("ascii"),
            ACE_CASE_CN,
        )

    def test_uppercase_ace_label_decodes(self) -> None:
        result = self.tool.execute(
            mode="info", hostname="XN--FSQX61D.CN"
        )
        self.assertEqual(result["punycode"]["unicode_form"], UNICODE_CASE_CN)
        self.assertIsNone(result["punycode"]["error"])

    def test_non_ascii_hostname_encoded_to_ace(self) -> None:
        result = self.tool.execute(mode="info", hostname=UNICODE_CASE_CN)
        punycode = result["punycode"]
        self.assertTrue(punycode["applicable"])
        self.assertEqual(punycode["unicode_form"], UNICODE_CASE_CN)
        self.assertEqual(punycode["ace_form"], ACE_CASE_CN)
        self.assertTrue(punycode["has_ace_label"])
        self.assertIsNone(punycode["error"])
        # Structure is computed on the ASCII (ACE) form.
        self.assertEqual(result["registered_domain"], ACE_CASE_CN)
        self.assertEqual(result["tld"], "cn")
        self.assertEqual(result["labels"], 2)

    def test_non_ascii_umlaut_domain(self) -> None:
        result = self.tool.execute(
            mode="info", hostname=UNICODE_MUNCHEN_DE
        )
        self.assertEqual(
            result["punycode"]["ace_form"], ACE_MUNCHEN_DE
        )
        self.assertEqual(
            result["punycode"]["unicode_form"], UNICODE_MUNCHEN_DE
        )

    def test_invalid_punycode_reports_error_without_raising(self) -> None:
        result = self.tool.execute(mode="info", hostname="xn--!.com")
        punycode = result["punycode"]
        self.assertTrue(punycode["has_ace_label"])
        self.assertIsNone(punycode["unicode_form"])
        self.assertIsNotNone(punycode["error"])
        self.assertIn("decoded", punycode["error"])

    def test_non_ascii_label_too_long_reports_error(self) -> None:
        # 'münchen' repeated 12 times is 84 characters long, which the
        # stdlib IDNA codec refuses to encode (label too long).
        host = "münchen" * 12 + ".de"
        result = self.tool.execute(mode="info", hostname=host)
        punycode = result["punycode"]
        self.assertIsNone(punycode["ace_form"])
        self.assertIsNotNone(punycode["error"])
        self.assertIn("ACE", punycode["error"])

    def test_info_on_ip_literal(self) -> None:
        result = self.tool.execute(mode="info", hostname="10.0.0.1")
        self.assertTrue(result["is_ip_literal"])
        self.assertEqual(result["ip_version"], 4)
        self.assertIsNone(result["registered_domain"])
        self.assertIsNone(result["tld"])
        self.assertFalse(result["punycode"]["applicable"])


class DomainValidatorToolTldLookupTest(unittest.TestCase):
    """Offline deterministic test cases for the tld_lookup mode."""

    def setUp(self) -> None:
        self.tool = DomainValidatorTool()

    def test_table_shape_is_indicative_120_entries(self) -> None:
        self.assertEqual(len(DomainValidatorTool.KNOWN_TLDS), 120)
        self.assertEqual(
            len(DomainValidatorTool.KNOWN_TLDS),
            len(GENERIC_TLDS) + len(COUNTRY_CODE_TLDS) + len(NEW_GTLDS),
        )
        # No accidental overlaps between the three groups.
        self.assertEqual(
            len(set(GENERIC_TLDS) | set(COUNTRY_CODE_TLDS) | set(NEW_GTLDS)),
            len(GENERIC_TLDS) + len(COUNTRY_CODE_TLDS) + len(NEW_GTLDS),
        )

    def test_generic_tlds(self) -> None:
        for tld in ("com", "org", "net", "edu", "gov", "io", "ai",
                    "dev", "app", "co", "me", "info", "biz"):
            result = self.tool.execute(mode="tld_lookup", hostname=tld)
            self.assertEqual(result["verdict"], "known", tld)
            self.assertEqual(result["category"], "generic", tld)

    def test_country_code_tlds(self) -> None:
        for tld in ("cn", "us", "uk", "jp", "de", "fr", "ru", "kr",
                    "in", "br", "au", "ca", "nl", "it", "es", "se",
                    "no", "dk", "fi", "pl", "ch", "at", "be"):
            result = self.tool.execute(mode="tld_lookup", hostname=tld)
            self.assertEqual(result["verdict"], "known", tld)
            self.assertEqual(result["category"], "country", tld)

    def test_new_gtlds(self) -> None:
        for tld in ("xyz", "online", "site", "shop", "top", "tech",
                    "cloud"):
            result = self.tool.execute(mode="tld_lookup", hostname=tld)
            self.assertEqual(result["verdict"], "known", tld)
            self.assertEqual(result["category"], "new_gtld", tld)

    def test_lookup_from_full_hostname(self) -> None:
        result = self.tool.execute(
            mode="tld_lookup", hostname="www.example.xyz"
        )
        self.assertEqual(result["tld"], "xyz")
        self.assertEqual(result["verdict"], "known")
        self.assertEqual(result["category"], "new_gtld")

    def test_lookup_is_case_insensitive(self) -> None:
        result = self.tool.execute(mode="tld_lookup", hostname="COM")
        self.assertEqual(result["tld"], "com")
        self.assertEqual(result["verdict"], "known")

    def test_unknown_tld(self) -> None:
        result = self.tool.execute(
            mode="tld_lookup", hostname="example.frobnicate"
        )
        self.assertEqual(result["tld"], "frobnicate")
        self.assertEqual(result["verdict"], "unknown")
        self.assertEqual(result["category"], "unknown")
        self.assertIn("NOT exhaustive", result["note"])

    def test_lookup_accepts_trailing_dot(self) -> None:
        result = self.tool.execute(mode="tld_lookup", hostname="com.")
        self.assertEqual(result["tld"], "com")
        self.assertEqual(result["verdict"], "known")


class DomainValidatorToolErrorMatrixTest(unittest.TestCase):
    """Parameter-level errors (ValueError) for malformed input."""

    def setUp(self) -> None:
        self.tool = DomainValidatorTool()

    def assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def test_unknown_mode(self) -> None:
        self.assert_invalid(mode="resolve", hostname="example.com")

    def test_missing_or_malformed_hostname(self) -> None:
        self.assert_invalid(mode="validate")
        self.assert_invalid(mode="validate", hostname="")
        self.assert_invalid(mode="validate", hostname=None)
        self.assert_invalid(mode="validate", hostname=123)
        self.assert_invalid(mode="validate", hostname=True)
        self.assert_invalid(mode="validate", hostname=["a.com"])

    def test_scheme_rejected_with_hint(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(
                mode="validate", hostname="https://example.com/path"
            )
        message = str(ctx.exception)
        self.assertIn("scheme", message)
        self.assertIn("example.com", message)

    def test_url_parts_rejected(self) -> None:
        for host in (
            "example.com/path",
            "example.com?a=b",
            "example.com#fragment",
            "user@example.com",
            "example.com:8080",
        ):
            self.assert_invalid(mode="validate", hostname=host)
            self.assert_invalid(mode="info", hostname=host)

    def test_whitespace_rejected(self) -> None:
        self.assert_invalid(mode="validate", hostname="exa mple.com")
        self.assert_invalid(mode="validate", hostname=" example.com")
        self.assert_invalid(mode="validate", hostname="example.com\n")

    def test_bad_flag_types_rejected(self) -> None:
        self.assert_invalid(
            mode="validate", hostname="example.com",
            allow_single_label="yes",
        )
        self.assert_invalid(
            mode="validate", hostname="example.com",
            allow_underscores=1,
        )

    def test_oversized_input_rejected(self) -> None:
        self.assert_invalid(mode="validate", hostname="a" * 4096)

    def test_tld_lookup_degenerate_input(self) -> None:
        self.assert_invalid(mode="tld_lookup", hostname="..")

    def test_direct_module_import_matches_package_export(self) -> None:
        self.assertIs(DomainValidatorTool, DirectDomainValidatorTool)


if __name__ == "__main__":
    unittest.main()
