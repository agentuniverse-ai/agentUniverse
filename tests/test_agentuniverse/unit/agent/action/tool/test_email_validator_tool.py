#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: test_email_validator_tool.py

"""Offline unit tests for EmailValidatorTool.

The tool is built purely on the standard library (re / str /
ipaddress) and performs no DNS, MX or SMTP lookups, so this suite runs
fully offline. Every assertion is deterministic: ground-truth valid and
invalid addresses from the RFC 5322-lite profile are checked against
exact reason codes, parse decomposition and normalization are compared
literally, and normalization is proven idempotent by double execution.
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import EmailValidatorTool
from agentuniverse.agent.action.tool.common_tool.email_validator_tool import (
    EmailValidatorTool as DirectEmailValidatorTool,
)

LOCAL_64 = "a" * 64
LOCAL_65 = "a" * 65
LABEL_63 = "l" * 63
LABEL_64 = "l" * 64
ADDR_TOTAL_257 = "a" * 245 + "@example.com"  # 245 + 12 = 257 > 254
ADDR_OVER_CAP = "a" * 321


class EmailValidatorToolValidateTest(unittest.TestCase):
    """RFC 5322-lite ground truths for the validate mode."""

    def setUp(self) -> None:
        self.tool = EmailValidatorTool()

    # ------------------------- valid ground truths ------------------- #

    def test_valid_simple(self) -> None:
        result = self.tool.execute(mode="validate", address="user@example.com")
        self.assertTrue(result["valid"])
        self.assertEqual(result["reason"], "ok")
        self.assertEqual(result["warnings"], [])
        self.assertEqual(
            result["parts"],
            {
                "display_name": None,
                "addr_spec": "user@example.com",
                "local": "user",
                "local_kind": "dot_atom",
                "tag": None,
                "local_base": None,
                "domain": "example.com",
                "domain_kind": "dotted",
            },
        )

    def test_valid_plus_tag(self) -> None:
        result = self.tool.execute(
            mode="validate", address="jane.doe+newsletter@gmail.com"
        )
        self.assertTrue(result["valid"])
        self.assertEqual(result["parts"]["tag"], "newsletter")
        self.assertEqual(result["parts"]["local_base"], "jane.doe")

    def test_valid_quoted_local_with_spaces(self) -> None:
        result = self.tool.execute(
            mode="validate", address='"john smith"@example.com'
        )
        self.assertTrue(result["valid"])
        self.assertEqual(result["parts"]["local_kind"], "quoted")
        self.assertEqual(result["parts"]["local"], '"john smith"')
        self.assertEqual(result["parts"]["tag"], None)

    def test_valid_quoted_local_with_at(self) -> None:
        # The @ inside the quotes must not be treated as the separator.
        result = self.tool.execute(mode="validate", address='"a@b"@example.com')
        self.assertTrue(result["valid"])
        self.assertEqual(result["parts"]["local"], '"a@b"')
        self.assertEqual(result["parts"]["domain"], "example.com")

    def test_valid_quoted_local_with_escapes(self) -> None:
        result = self.tool.execute(mode="validate", address='"a\\"b"@example.com')
        self.assertTrue(result["valid"])
        self.assertEqual(result["parts"]["local_kind"], "quoted")

    def test_valid_atext_specials(self) -> None:
        result = self.tool.execute(
            mode="validate", address="!#$%&'*+-/=?^_`{|}~@example.com"
        )
        self.assertTrue(result["valid"])

    def test_valid_local_exactly_64(self) -> None:
        result = self.tool.execute(
            mode="validate", address=f"{LOCAL_64}@example.com"
        )
        self.assertTrue(result["valid"])

    def test_valid_single_label_flagged(self) -> None:
        result = self.tool.execute(mode="validate", address="root@localhost")
        self.assertTrue(result["valid"])
        self.assertEqual(result["warnings"], ["single_label_domain"])
        self.assertEqual(result["parts"]["domain_kind"], "single_label")

    def test_valid_ip_literal_v4_flagged(self) -> None:
        result = self.tool.execute(mode="validate", address="admin@[127.0.0.1]")
        self.assertTrue(result["valid"])
        self.assertEqual(result["warnings"], ["ip_literal_domain"])
        self.assertEqual(result["parts"]["domain_kind"], "ip_literal")

    def test_valid_ip_literal_v6_flagged(self) -> None:
        result = self.tool.execute(
            mode="validate", address="user@[IPv6:2001:db8::1]"
        )
        self.assertTrue(result["valid"])
        self.assertEqual(result["warnings"], ["ip_literal_domain"])
        self.assertEqual(result["parts"]["domain_kind"], "ip_literal")

    def test_valid_label_exactly_63(self) -> None:
        result = self.tool.execute(
            mode="validate", address=f"user@{LABEL_63}.example.com"
        )
        self.assertTrue(result["valid"])

    def test_valid_display_name_form(self) -> None:
        result = self.tool.execute(
            mode="validate", address="Jane Doe <jane@example.com>"
        )
        self.assertTrue(result["valid"])
        self.assertEqual(result["parts"]["display_name"], "Jane Doe")
        self.assertEqual(result["parts"]["addr_spec"], "jane@example.com")

    def test_valid_surrounding_whitespace_stripped(self) -> None:
        result = self.tool.execute(mode="validate", address="  user@example.com\n")
        self.assertTrue(result["valid"])
        self.assertEqual(result["address"], "  user@example.com\n")

    # ------------------------- invalid ground truths ------------------ #

    def test_invalid_no_at(self) -> None:
        result = self.tool.execute(mode="validate", address="plainaddress")
        self.assertFalse(result["valid"])
        self.assertEqual(result["reason"], "missing_at")
        self.assertIsNone(result["parts"])

    def test_invalid_double_at(self) -> None:
        result = self.tool.execute(mode="validate", address="a@b@c.com")
        self.assertFalse(result["valid"])
        self.assertEqual(result["reason"], "multiple_at")

    def test_invalid_stray_quote_after_quoted_local(self) -> None:
        # '"a@b"@x' is valid; with a stray quote after the local there
        # are two '@'s outside quotes and the address is rejected.
        result = self.tool.execute(mode="validate", address='"a"@b"@x.com')
        self.assertFalse(result["valid"])
        self.assertEqual(result["reason"], "multiple_at")

    def test_invalid_empty_local(self) -> None:
        result = self.tool.execute(mode="validate", address="@example.com")
        self.assertFalse(result["valid"])
        self.assertEqual(result["reason"], "empty_local")

    def test_invalid_empty_domain(self) -> None:
        result = self.tool.execute(mode="validate", address="user@")
        self.assertFalse(result["valid"])
        self.assertEqual(result["reason"], "empty_domain")

    def test_invalid_consecutive_dots_local(self) -> None:
        result = self.tool.execute(mode="validate", address="user..name@example.com")
        self.assertFalse(result["valid"])
        self.assertEqual(result["reason"], "consecutive_dots_in_local")

    def test_invalid_leading_dot_local(self) -> None:
        result = self.tool.execute(mode="validate", address=".user@example.com")
        self.assertFalse(result["valid"])
        self.assertEqual(result["reason"], "leading_dot_in_local")

    def test_invalid_trailing_dot_local(self) -> None:
        result = self.tool.execute(mode="validate", address="user.@example.com")
        self.assertFalse(result["valid"])
        self.assertEqual(result["reason"], "trailing_dot_in_local")

    def test_invalid_domain_leading_dot(self) -> None:
        result = self.tool.execute(mode="validate", address="a@.example.com")
        self.assertFalse(result["valid"])
        self.assertEqual(result["reason"], "empty_domain_label")

    def test_invalid_domain_trailing_dot(self) -> None:
        result = self.tool.execute(mode="validate", address="a@example.com.")
        self.assertFalse(result["valid"])
        self.assertEqual(result["reason"], "empty_domain_label")

    def test_invalid_domain_consecutive_dots(self) -> None:
        result = self.tool.execute(mode="validate", address="a@example..com")
        self.assertFalse(result["valid"])
        self.assertEqual(result["reason"], "empty_domain_label")

    def test_invalid_space_in_local(self) -> None:
        result = self.tool.execute(mode="validate", address="user name@example.com")
        self.assertFalse(result["valid"])
        self.assertEqual(result["reason"], "invalid_local_chars")

    def test_invalid_local_too_long(self) -> None:
        result = self.tool.execute(mode="validate", address=f"{LOCAL_65}@example.com")
        self.assertFalse(result["valid"])
        self.assertEqual(result["reason"], "local_too_long")
        self.assertEqual(result["parts"]["local"], LOCAL_65)

    def test_invalid_address_too_long(self) -> None:
        result = self.tool.execute(mode="validate", address=ADDR_TOTAL_257)
        self.assertFalse(result["valid"])
        self.assertEqual(result["reason"], "address_too_long")

    def test_invalid_label_too_long(self) -> None:
        result = self.tool.execute(
            mode="validate", address=f"a@{LABEL_64}.example.com"
        )
        self.assertFalse(result["valid"])
        self.assertEqual(result["reason"], "label_too_long")

    def test_invalid_label_leading_hyphen(self) -> None:
        result = self.tool.execute(mode="validate", address="a@-example.com")
        self.assertFalse(result["valid"])
        self.assertEqual(result["reason"], "invalid_label_hyphens")

    def test_invalid_label_trailing_hyphen(self) -> None:
        result = self.tool.execute(mode="validate", address="a@example-.com")
        self.assertFalse(result["valid"])
        self.assertEqual(result["reason"], "invalid_label_hyphens")

    def test_invalid_label_underscore(self) -> None:
        result = self.tool.execute(mode="validate", address="a@ex_ample.com")
        self.assertFalse(result["valid"])
        self.assertEqual(result["reason"], "invalid_label_chars")

    def test_invalid_label_space(self) -> None:
        result = self.tool.execute(mode="validate", address="a@ex ample.com")
        self.assertFalse(result["valid"])
        self.assertEqual(result["reason"], "invalid_label_chars")

    def test_invalid_non_ascii_idn_label(self) -> None:
        # IDNs must be passed in xn-- A-label form.
        result = self.tool.execute(mode="validate", address="user@münchen.com")
        self.assertFalse(result["valid"])
        self.assertEqual(result["reason"], "invalid_label_chars")

    def test_invalid_ip_literal_out_of_range(self) -> None:
        result = self.tool.execute(mode="validate", address="a@[999.0.0.1]")
        self.assertFalse(result["valid"])
        self.assertEqual(result["reason"], "invalid_ip_literal")

    def test_invalid_ip_literal_short_v4(self) -> None:
        result = self.tool.execute(mode="validate", address="a@[1.2.3]")
        self.assertFalse(result["valid"])
        self.assertEqual(result["reason"], "invalid_ip_literal")

    def test_invalid_ip_literal_bad_v6(self) -> None:
        result = self.tool.execute(mode="validate", address="a@[IPv6:zzzz::1]")
        self.assertFalse(result["valid"])
        self.assertEqual(result["reason"], "invalid_ip_literal")

    def test_invalid_ip_literal_empty(self) -> None:
        result = self.tool.execute(mode="validate", address="a@[]")
        self.assertFalse(result["valid"])
        self.assertEqual(result["reason"], "invalid_ip_literal")

    def test_invalid_quoted_unterminated(self) -> None:
        result = self.tool.execute(mode="validate", address='"abc@example.com')
        self.assertFalse(result["valid"])
        self.assertEqual(result["reason"], "invalid_quoted_local")

    def test_invalid_quoted_junk_after_close(self) -> None:
        result = self.tool.execute(mode="validate", address='"ab"cd@example.com')
        self.assertFalse(result["valid"])
        self.assertEqual(result["reason"], "invalid_quoted_local")

    def test_invalid_quoted_bad_escape(self) -> None:
        # A backslash must escape a printable character, not the separator.
        result = self.tool.execute(mode="validate", address='"a\\"@example.com')
        self.assertFalse(result["valid"])
        self.assertEqual(result["reason"], "invalid_quoted_local")

    def test_invalid_whitespace_only(self) -> None:
        result = self.tool.execute(mode="validate", address="   ")
        self.assertFalse(result["valid"])
        self.assertEqual(result["reason"], "empty_address")

    def test_verdict_carries_human_message(self) -> None:
        result = self.tool.execute(mode="validate", address="a@b@c")
        self.assertIn("more than one '@'", result["message"])
        self.assertTrue(result["message"].startswith("the address contains"))


class EmailValidatorToolParseTest(unittest.TestCase):
    """Decomposition ground truths for the parse mode."""

    def setUp(self) -> None:
        self.tool = EmailValidatorTool()

    def test_parse_basic_decomposition(self) -> None:
        result = self.tool.execute(mode="parse", address="user@sub.example.com")
        parts = result["parts"]
        self.assertEqual(parts["local"], "user")
        self.assertEqual(parts["domain"], "sub.example.com")
        self.assertEqual(parts["local_kind"], "dot_atom")
        self.assertEqual(parts["domain_kind"], "dotted")
        self.assertIsNone(parts["display_name"])
        self.assertIsNone(parts["tag"])

    def test_parse_display_name_extraction(self) -> None:
        result = self.tool.execute(
            mode="parse", address="Jane Q. Doe <jane.doe@example.com>"
        )
        self.assertTrue(result["valid"])
        self.assertEqual(result["parts"]["display_name"], "Jane Q. Doe")
        self.assertEqual(result["parts"]["addr_spec"], "jane.doe@example.com")

    def test_parse_display_name_quoted(self) -> None:
        result = self.tool.execute(
            mode="parse", address='"Jane Doe" <jane@example.com>'
        )
        self.assertTrue(result["valid"])
        self.assertEqual(result["parts"]["display_name"], '"Jane Doe"')

    def test_parse_bare_angle_form(self) -> None:
        result = self.tool.execute(mode="parse", address="<user@example.com>")
        self.assertTrue(result["valid"])
        self.assertIsNone(result["parts"]["display_name"])
        self.assertEqual(result["parts"]["local"], "user")

    def test_parse_quoted_vs_dot_atom_classification(self) -> None:
        quoted = self.tool.execute(mode="parse", address='"john smith"@x.com')
        dot_atom = self.tool.execute(mode="parse", address="john.smith@x.com")
        self.assertEqual(quoted["parts"]["local_kind"], "quoted")
        self.assertEqual(dot_atom["parts"]["local_kind"], "dot_atom")

    def test_parse_plus_tag_detection(self) -> None:
        result = self.tool.execute(
            mode="parse", address="dev+git.issue@corp.example.com"
        )
        self.assertEqual(result["parts"]["tag"], "git.issue")
        self.assertEqual(result["parts"]["local_base"], "dev")

    def test_parse_plus_tag_absent(self) -> None:
        result = self.tool.execute(mode="parse", address="dev@corp.example.com")
        self.assertIsNone(result["parts"]["tag"])
        self.assertIsNone(result["parts"]["local_base"])

    def test_parse_plus_inside_quotes_is_literal(self) -> None:
        result = self.tool.execute(mode="parse", address='"a+b"@example.com')
        self.assertTrue(result["valid"])
        self.assertIsNone(result["parts"]["tag"])

    def test_parse_domain_kind_classification(self) -> None:
        dotted = self.tool.execute(mode="parse", address="a@b.example.org")
        single = self.tool.execute(mode="parse", address="a@localhost")
        literal = self.tool.execute(mode="parse", address="a@[10.0.0.1]")
        self.assertEqual(dotted["parts"]["domain_kind"], "dotted")
        self.assertEqual(single["parts"]["domain_kind"], "single_label")
        self.assertEqual(literal["parts"]["domain_kind"], "ip_literal")

    def test_parse_invalid_returns_verdict_not_exception(self) -> None:
        result = self.tool.execute(mode="parse", address="not-an-address")
        self.assertFalse(result["valid"])
        self.assertEqual(result["reason"], "missing_at")
        self.assertIsNone(result["parts"])


class EmailValidatorToolNormalizeTest(unittest.TestCase):
    """Canonicalization and idempotence ground truths."""

    def setUp(self) -> None:
        self.tool = EmailValidatorTool()

    def test_normalize_lowercase_domain_only(self) -> None:
        result = self.tool.execute(mode="normalize", address="User@EXAMPLE.COM")
        self.assertEqual(result["normalized"], "User@example.com")
        self.assertTrue(result["valid"])

    def test_normalize_strips_redundant_quotes(self) -> None:
        result = self.tool.execute(mode="normalize", address='"john.doe"@Example.COM')
        self.assertEqual(result["normalized"], "john.doe@example.com")

    def test_normalize_keeps_meaningful_quotes(self) -> None:
        result = self.tool.execute(
            mode="normalize", address='"john smith"@Example.COM'
        )
        self.assertEqual(result["normalized"], '"john smith"@example.com')

    def test_normalize_keeps_quotes_with_special_chars(self) -> None:
        result = self.tool.execute(mode="normalize", address='"a@b"@Example.COM')
        self.assertEqual(result["normalized"], '"a@b"@example.com')

    def test_normalize_folds_display_name_keeps_local_case(self) -> None:
        result = self.tool.execute(
            mode="normalize", address="  Jane   Doe  <JANE@Example.COM> "
        )
        self.assertEqual(result["normalized"], "Jane Doe <JANE@example.com>")

    def test_normalize_unquotes_display_name(self) -> None:
        result = self.tool.execute(
            mode="normalize", address='"Jane   Doe" <JANE@Example.COM>'
        )
        self.assertEqual(result["normalized"], "Jane Doe <JANE@example.com>")

    def test_normalize_preserves_plus_tag(self) -> None:
        result = self.tool.execute(
            mode="normalize", address="Jane+Tag@Example.COM"
        )
        self.assertEqual(result["normalized"], "Jane+Tag@example.com")

    def test_normalize_invalid_input(self) -> None:
        result = self.tool.execute(mode="normalize", address="a@b@c")
        self.assertFalse(result["valid"])
        self.assertEqual(result["reason"], "multiple_at")
        self.assertIsNone(result["normalized"])

    def test_normalize_idempotent(self) -> None:
        inputs = [
            "User@EXAMPLE.COM",
            '"john.doe"@Example.COM',
            '"john smith"@Example.COM',
            "  Jane   Doe  <JANE@Example.COM> ",
            '"Jane   Doe" <JANE@Example.COM>',
            "root@LOCALHOST",
            "dev+git@Corp.Example.COM",
            "user@[IPv6:2001:DB8::1]",
            '<Only.Addr@Example.COM>',
        ]
        for value in inputs:
            with self.subTest(address=value):
                first = self.tool.execute(mode="normalize", address=value)
                self.assertTrue(first["valid"], value)
                second = self.tool.execute(
                    mode="normalize", address=first["normalized"]
                )
                self.assertTrue(second["valid"], value)
                self.assertEqual(second["normalized"], first["normalized"], value)


class EmailValidatorToolBatchTest(unittest.TestCase):
    """Batch mode: per-item results, summary counts, ordering."""

    def setUp(self) -> None:
        self.tool = EmailValidatorTool()

    def test_batch_mixed_verdicts(self) -> None:
        result = self.tool.execute(
            mode="validate",
            addresses=[
                "user@example.com",
                "root@localhost",
                "a@b@c",
                '"john smith"@example.com',
                "no-at-sign",
            ],
        )
        self.assertEqual(result["mode"], "validate")
        self.assertEqual(result["count"], 5)
        self.assertEqual(
            result["summary"], {"total": 5, "valid": 3, "invalid": 2}
        )
        self.assertEqual(
            [item["address"] for item in result["results"]],
            [
                "user@example.com",
                "root@localhost",
                "a@b@c",
                '"john smith"@example.com',
                "no-at-sign",
            ],
        )
        self.assertEqual(
            [item["reason"] for item in result["results"]],
            ["ok", "ok", "multiple_at", "ok", "missing_at"],
        )
        self.assertEqual(result["results"][1]["warnings"], ["single_label_domain"])

    def test_batch_parse_mode(self) -> None:
        result = self.tool.execute(
            mode="parse", addresses=["Name <n@x.com>", "plain"]
        )
        self.assertEqual(result["mode"], "parse")
        self.assertEqual(result["summary"]["valid"], 1)
        self.assertEqual(result["results"][0]["parts"]["display_name"], "Name")

    def test_batch_normalize_mode(self) -> None:
        result = self.tool.execute(
            mode="normalize", addresses=["A@B.COM", "bad@@"]
        )
        self.assertEqual(result["results"][0]["normalized"], "A@b.com")
        self.assertIsNone(result["results"][1]["normalized"])
        self.assertEqual(result["summary"], {"total": 2, "valid": 1, "invalid": 1})

    def test_batch_all_invalid(self) -> None:
        result = self.tool.execute(mode="validate", addresses=["@x", "x@", "x"])
        self.assertEqual(result["summary"], {"total": 3, "valid": 0, "invalid": 3})

    def test_batch_over_limit_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="validate", addresses=["a@b.com"] * 101)


class EmailValidatorToolParamTest(unittest.TestCase):
    """Strict parameter validation (raises before any computation)."""

    def setUp(self) -> None:
        self.tool = EmailValidatorTool()

    def _assert_invalid_param(self, *args, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(*args, **kwargs)

    def test_unknown_mode(self) -> None:
        self._assert_invalid_param(mode="check", address="a@b.com")
        self._assert_invalid_param(mode=None, address="a@b.com")

    def test_both_carriers_rejected(self) -> None:
        self._assert_invalid_param(
            mode="validate", address="a@b.com", addresses=["c@d.com"]
        )

    def test_neither_carrier_rejected(self) -> None:
        self._assert_invalid_param(mode="validate")
        self._assert_invalid_param(mode="validate", address=None, addresses=None)

    def test_address_must_be_non_empty_string(self) -> None:
        self._assert_invalid_param(mode="validate", address="")
        self._assert_invalid_param(mode="validate", address=123)
        self._assert_invalid_param(mode="validate", address=["a@b.com"])

    def test_address_over_char_cap(self) -> None:
        self._assert_invalid_param(mode="validate", address="a" * 321)

    def test_addresses_must_be_list_of_strings(self) -> None:
        self._assert_invalid_param(mode="validate", addresses="a@b.com")
        self._assert_invalid_param(mode="validate", addresses=[])
        self._assert_invalid_param(mode="validate", addresses=[123])
        self._assert_invalid_param(mode="validate", addresses=[""])
        self._assert_invalid_param(mode="validate", addresses=["a@b.com", None])
        self._assert_invalid_param(mode="validate", addresses=["a" * 321])

    def test_error_message_prefixed_with_tool_name(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="validate")
        self.assertTrue(str(ctx.exception).startswith("email_validator_tool:"))


class EmailValidatorToolMetaTest(unittest.TestCase):
    """Module surface, defaults and determinism."""

    def test_export_from_common_tool_package(self) -> None:
        self.assertIs(DirectEmailValidatorTool, EmailValidatorTool)

    def test_default_name(self) -> None:
        self.assertEqual(EmailValidatorTool().name, "email_validator_tool")

    def test_mode_constant(self) -> None:
        self.assertEqual(
            EmailValidatorTool.MODES, ("validate", "parse", "normalize")
        )

    def test_results_are_deterministic(self) -> None:
        tool = EmailValidatorTool()
        for _ in range(3):
            self.assertEqual(
                tool.execute(mode="validate", address='"a@b"@Example.COM'),
                tool.execute(mode="validate", address='"a@b"@Example.COM'),
            )
            self.assertEqual(
                tool.execute(mode="normalize", address="  X  Y <A@B.COM>"),
                tool.execute(mode="normalize", address="  X  Y <A@B.COM>"),
            )


if __name__ == "__main__":
    unittest.main()
