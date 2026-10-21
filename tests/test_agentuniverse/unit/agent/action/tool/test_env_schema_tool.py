#!/usr/bin/env python3

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: test_env_schema_tool.py

"""Offline unit tests for EnvSchemaTool.

The tool is built purely on the standard library and never touches
the network or the filesystem, so this suite runs fully offline.
Every assertion is deterministic: check results are compared against
literal ground-truth payloads (type pass/fail per declared type,
required/optional/default handling, enum/min/max violations, extras),
suggest_schema against a literal inference matrix (including the enum
detection cutoff) and diff against exact masked/unmasked structures.

Security invariant asserted in EVERY test whose fixture carries a
secret-ish variable name (containing KEY/SECRET/PASSWORD/TOKEN): the
raw secret value must not appear anywhere in the serialized result.
"""

import json
import unittest

from agentuniverse.agent.action.tool.common_tool import EnvSchemaTool
from agentuniverse.agent.action.tool.common_tool.env_schema_tool import (
    EnvSchemaTool as DirectEnvSchemaTool,
)

BASIC_TEXT = "\n".join(
    [
        "# service configuration",
        "API_HOST=localhost",
        "API_PORT=8080",
        "RATE_LIMIT=1.5",
        "DEBUG=true",
        "LOG_LEVEL=debug",
        "SITE_URL=https://example.com",
        "ADMIN_EMAIL=admin@example.com",
        "DATA_DIR=/var/lib/app",
        "API_KEY=sk-live-abcdef123456",
        "DB_PASSWORD=hunter2-secret",
        "",
    ]
)

SECRET_RAW_VALUES = ("sk-live-abcdef123456", "hunter2-secret")


class EnvSchemaToolTestCase(unittest.TestCase):
    """Shared helpers."""

    def setUp(self) -> None:
        self.tool = EnvSchemaTool()

    def assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def assert_no_secret_leak(self, result) -> None:
        """No raw secret value may appear anywhere in the payload."""
        dumped = json.dumps(result, sort_keys=True, default=str)
        for raw in SECRET_RAW_VALUES:
            self.assertNotIn(raw, dumped)


class EnvSchemaCheckPassTest(EnvSchemaToolTestCase):
    """check mode: every declared type accepts its documented values."""

    def test_pass_all_types(self) -> None:
        result = self.tool.execute(
            mode="check",
            text=BASIC_TEXT,
            schema={
                "API_HOST": {"type": "string"},
                "API_PORT": {"type": "int"},
                "RATE_LIMIT": {"type": "float"},
                "DEBUG": {"type": "bool"},
                "SITE_URL": {"type": "url"},
                "ADMIN_EMAIL": {"type": "email"},
                "DATA_DIR": {"type": "path"},
            },
        )
        self.assertTrue(result["passed"])
        self.assertEqual(result["result"], "passed")
        self.assertEqual(result["missing"], [])
        self.assertEqual(result["type_mismatches"], [])
        self.assertEqual(result["violations"], [])
        self.assertEqual(result["applied_defaults"], [])
        self.assert_no_secret_leak(result)

    def test_int_accepted_forms(self) -> None:
        for value in ("0", "42", "-7", "+7"):
            with self.subTest(value=value):
                result = self.tool.execute(
                    mode="check",
                    text=f"N={value}\n",
                    schema={"N": {"type": "int"}},
                )
                self.assertTrue(result["passed"])

    def test_int_rejected_forms(self) -> None:
        for value in ("abc", "1.5", "0x10", "1_000", "1e3", "", "٣"):
            with self.subTest(value=value):
                result = self.tool.execute(
                    mode="check",
                    text=f"N={value}\n",
                    schema={"N": {"type": "int"}},
                )
                self.assertFalse(result["passed"])
                self.assertEqual(len(result["type_mismatches"]), 1)
                self.assertEqual(result["type_mismatches"][0]["expected"], "int")
                self.assertEqual(
                    result["type_mismatches"][0]["raw_value_preview"],
                    value if value else "",
                )

    def test_float_accepted_forms(self) -> None:
        for value in ("0", "1", "1.5", ".5", "1.", "-2.25", "+2.25", "1e3",
                      "1.5E-2", "-1e+9"):
            with self.subTest(value=value):
                result = self.tool.execute(
                    mode="check",
                    text=f"N={value}\n",
                    schema={"N": {"type": "float"}},
                )
                self.assertTrue(result["passed"])

    def test_float_rejected_forms(self) -> None:
        for value in ("inf", "-inf", "nan", "NaN", "0x1.8p3", "1e", "1.2.3",
                      "abc", "", "1,5"):
            with self.subTest(value=value):
                result = self.tool.execute(
                    mode="check",
                    text=f"N={value}\n",
                    schema={"N": {"type": "float"}},
                )
                self.assertFalse(result["passed"])

    def test_bool_accepted_words_case_insensitive(self) -> None:
        for value in ("true", "FALSE", "Yes", "no", "1", "0", "TRUE"):
            with self.subTest(value=value):
                result = self.tool.execute(
                    mode="check",
                    text=f"B={value}\n",
                    schema={"B": {"type": "bool"}},
                )
                self.assertTrue(result["passed"])

    def test_bool_rejected_forms(self) -> None:
        for value in ("2", "on", "off", "trueish", "y", "", "yes/no"):
            with self.subTest(value=value):
                result = self.tool.execute(
                    mode="check",
                    text=f"B={value}\n",
                    schema={"B": {"type": "bool"}},
                )
                self.assertFalse(result["passed"])

    def test_url_accepted_forms(self) -> None:
        for value in ("http://h", "https://example.com/path?q=1",
                      "postgres://db:5432/x", "ftp://files.example.com",
                      "wss://ws.example.com/endpoint", "a+b-c.://host"):
            with self.subTest(value=value):
                result = self.tool.execute(
                    mode="check",
                    text=f"U={value}\n",
                    schema={"U": {"type": "url"}},
                )
                self.assertTrue(result["passed"])

    def test_url_rejected_forms(self) -> None:
        for value in ("localhost:8080", "http://", "://host",
                      "example.com/path", "1http://host", "", "/local/path",
                      "http:host"):
            with self.subTest(value=value):
                result = self.tool.execute(
                    mode="check",
                    text=f"U={value}\n",
                    schema={"U": {"type": "url"}},
                )
                self.assertFalse(result["passed"])

    def test_email_accepted_forms(self) -> None:
        for value in ("a@b.com", "first.last@sub.example.org",
                      "x+y@domain.name", "a!#%&'*+-/=?^_`{|}~@local.host",
                      "user123@123.com", "admin@localhost"):
            with self.subTest(value=value):
                result = self.tool.execute(
                    mode="check",
                    text=f"E={value}\n",
                    schema={"E": {"type": "email"}},
                )
                self.assertTrue(result["passed"])

    def test_email_rejected_forms(self) -> None:
        for value in (".a@b.com", "a.@b.com", "a..b@c.com",
                      "a@-b.com", "a@b-.com", "a@b..com", "a b@c.com",
                      "a@b_c.com", "a@b.com_", "plain", "a@b@c.com", "",
                      "a@b.c" + "d" * 250):
            with self.subTest(value=value):
                result = self.tool.execute(
                    mode="check",
                    text=f"E={value}\n",
                    schema={"E": {"type": "email"}},
                )
                self.assertFalse(result["passed"])

    def test_path_rules(self) -> None:
        ok = self.tool.execute(
            mode="check",
            text="P=/var/data\nQ=relative/cache\nR=~\n",
            schema={"P": {"type": "path"}, "Q": {"type": "path"},
                    "R": {"type": "path"}},
        )
        self.assertTrue(ok["passed"])
        # An embedded newline (via a double-quoted escape) is a control
        # character — not a single-line path.
        bad = self.tool.execute(
            mode="check",
            text='P="a\\nb"\n',
            schema={"P": {"type": "path"}},
        )
        self.assertFalse(bad["passed"])

    def test_string_accepts_anything_including_empty(self) -> None:
        result = self.tool.execute(
            mode="check",
            text="S=\nT=anything !@# goes\n",
            schema={"S": {"type": "string"}, "T": {"type": "string"}},
        )
        self.assertTrue(result["passed"])

    def test_quoted_values_are_type_checked_after_unescaping(self) -> None:
        result = self.tool.execute(
            mode="check",
            text='N="8080"\nM=\'1.5\'\n',
            schema={"N": {"type": "int"}, "M": {"type": "float"}},
        )
        self.assertTrue(result["passed"])

    def test_got_field_is_inferred_type(self) -> None:
        result = self.tool.execute(
            mode="check",
            text="N=abc\nB=2\n",
            schema={"N": {"type": "int"}, "B": {"type": "bool"}},
        )
        got = {m["var"]: m["got"] for m in result["type_mismatches"]}
        self.assertEqual(got, {"N": "string", "B": "int"})


class EnvSchemaCheckRequiredDefaultsTest(EnvSchemaToolTestCase):
    """check mode: required / optional / default handling."""

    def test_missing_required_fails(self) -> None:
        result = self.tool.execute(
            mode="check",
            text="A=1\n",
            schema={"A": {"type": "int"}, "MISSING": {"type": "string"}},
        )
        self.assertFalse(result["passed"])
        self.assertIn("missing required", result["result"])
        self.assertEqual(
            result["missing"],
            [{"var": "MISSING", "required": True, "has_default": False,
              "suggestion": "MISSING="}],
        )

    def test_required_defaults_to_true(self) -> None:
        result = self.tool.execute(
            mode="check",
            text="",
            schema={"X": {"type": "string"}},
        )
        self.assertFalse(result["passed"])
        self.assertTrue(result["missing"][0]["required"])

    def test_missing_optional_passes_but_listed(self) -> None:
        result = self.tool.execute(
            mode="check",
            text="A=1\n",
            schema={"A": {"type": "int"},
                    "OPT": {"type": "string", "required": False}},
        )
        self.assertTrue(result["passed"])
        self.assertEqual(
            result["missing"],
            [{"var": "OPT", "required": False, "has_default": False,
              "suggestion": "OPT="}],
        )
        self.assertEqual(result["applied_defaults"], [])

    def test_missing_with_default_passes_and_is_applied(self) -> None:
        result = self.tool.execute(
            mode="check",
            text="A=1\n",
            schema={"A": {"type": "int"},
                    "PORT": {"type": "int", "default": "8080"}},
        )
        self.assertTrue(result["passed"])
        self.assertEqual(
            result["missing"],
            [{"var": "PORT", "required": True, "has_default": True,
              "suggestion": "PORT=8080"}],
        )
        self.assertEqual(
            result["applied_defaults"], [{"var": "PORT", "default": "8080"}]
        )

    def test_default_is_type_checked_like_a_file_value(self) -> None:
        result = self.tool.execute(
            mode="check",
            text="",
            schema={"PORT": {"type": "int", "default": "not-a-number"}},
        )
        self.assertFalse(result["passed"])
        self.assertEqual(result["type_mismatches"][0]["var"], "PORT")
        self.assertEqual(
            result["type_mismatches"][0]["raw_value_preview"],
            "not-a-number",
        )
        # The default still counts as applied (it is the effective value
        # that failed the type contract).
        self.assertEqual(
            result["applied_defaults"],
            [{"var": "PORT", "default": "not-a-number"}],
        )

    def test_default_respects_enum_and_bounds(self) -> None:
        enum_bad = self.tool.execute(
            mode="check",
            text="",
            schema={"L": {"type": "string", "default": "loud",
                          "enum": ["debug", "info"]}},
        )
        self.assertFalse(enum_bad["passed"])
        self.assertEqual(enum_bad["violations"][0]["rule"], "enum")
        bounds_bad = self.tool.execute(
            mode="check",
            text="",
            schema={"N": {"type": "int", "default": "99",
                          "min": 0, "max": 10}},
        )
        self.assertFalse(bounds_bad["passed"])
        self.assertEqual(bounds_bad["violations"][0]["rule"], "max")

    def test_file_value_wins_over_default(self) -> None:
        result = self.tool.execute(
            mode="check",
            text="PORT=9090\n",
            schema={"PORT": {"type": "int", "default": "8080"}},
        )
        self.assertTrue(result["passed"])
        self.assertEqual(result["missing"], [])
        self.assertEqual(result["applied_defaults"], [])


class EnvSchemaCheckConstraintsTest(EnvSchemaToolTestCase):
    """check mode: enum / min / max rules."""

    def test_enum_pass_is_case_sensitive(self) -> None:
        ok = self.tool.execute(
            mode="check",
            text="L=debug\n",
            schema={"L": {"type": "string",
                          "enum": ["debug", "info", "warn"]}},
        )
        self.assertTrue(ok["passed"])
        bad = self.tool.execute(
            mode="check",
            text="L=DEBUG\n",
            schema={"L": {"type": "string",
                          "enum": ["debug", "info", "warn"]}},
        )
        self.assertFalse(bad["passed"])
        self.assertEqual(
            bad["violations"],
            [{"var": "L", "rule": "enum",
              "expected": ["debug", "info", "warn"], "got": "DEBUG"}],
        )

    def test_enum_on_int_type_compares_raw_value(self) -> None:
        ok = self.tool.execute(
            mode="check",
            text="N=2\n",
            schema={"N": {"type": "int", "enum": ["1", "2", "3"]}},
        )
        self.assertTrue(ok["passed"])
        bad = self.tool.execute(
            mode="check",
            text="N=+2\n",
            schema={"N": {"type": "int", "enum": ["1", "2", "3"]}},
        )
        self.assertFalse(bad["passed"])  # raw "+2" is not in the enum

    def test_min_max_int(self) -> None:
        schema = {"PORT": {"type": "int", "min": 1024, "max": 65535}}
        for value, rule in (("1024", None), ("65535", None), ("80", "min"),
                            ("70000", "max")):
            with self.subTest(value=value):
                result = self.tool.execute(
                    mode="check", text=f"PORT={value}\n", schema=schema
                )
                if rule is None:
                    self.assertTrue(result["passed"])
                    self.assertEqual(result["violations"], [])
                else:
                    self.assertFalse(result["passed"])
                    self.assertEqual(result["violations"][0]["rule"], rule)
                    self.assertEqual(
                        result["violations"][0]["expected"],
                        1024 if rule == "min" else 65535,
                    )
                    self.assertEqual(result["violations"][0]["got"], value)

    def test_min_max_float(self) -> None:
        schema = {"RATE": {"type": "float", "min": 0.0, "max": 1.0}}
        ok = self.tool.execute(
            mode="check", text="RATE=0.5\n", schema=schema
        )
        self.assertTrue(ok["passed"])
        bad = self.tool.execute(
            mode="check", text="RATE=1.5\n", schema=schema
        )
        self.assertEqual(bad["violations"][0]["rule"], "max")
        self.assertEqual(bad["violations"][0]["got"], "1.5")

    def test_min_only_and_max_only(self) -> None:
        min_only = self.tool.execute(
            mode="check",
            text="N=5\n",
            schema={"N": {"type": "int", "min": 10}},
        )
        self.assertEqual(min_only["violations"][0]["rule"], "min")
        max_only = self.tool.execute(
            mode="check",
            text="N=50\n",
            schema={"N": {"type": "int", "max": 10}},
        )
        self.assertEqual(max_only["violations"][0]["rule"], "max")

    def test_bounds_not_evaluated_when_type_fails(self) -> None:
        result = self.tool.execute(
            mode="check",
            text="N=abc\n",
            schema={"N": {"type": "int", "min": 0, "max": 10}},
        )
        self.assertEqual(result["type_mismatches"][0]["var"], "N")
        self.assertEqual(result["violations"], [])


class EnvSchemaCheckExtraTest(EnvSchemaToolTestCase):
    """check mode: undeclared extras."""

    def test_extras_listed_with_source_note_and_never_fail(self) -> None:
        result = self.tool.execute(
            mode="check",
            text="A=1\nSTRAY=x\nSTRAY=y\n",
            schema={"A": {"type": "int"}},
        )
        self.assertTrue(result["passed"])
        self.assertEqual(len(result["extra"]), 1)
        entry = result["extra"][0]
        self.assertEqual(entry["var"], "STRAY")
        self.assertEqual(entry["lines"], [2, 3])
        self.assertEqual(
            entry["note"], "defined at lines 2, 3; not declared in the schema"
        )
        # Extras never carry their value (an undeclared secret must not
        # leak through the report).
        self.assertNotIn("value", entry)

    def test_extra_secret_never_leaks(self) -> None:
        result = self.tool.execute(
            mode="check",
            text=BASIC_TEXT,
            schema={"API_HOST": {"type": "string"}},
        )
        self.assertTrue(result["passed"])
        extras = {e["var"] for e in result["extra"]}
        self.assertIn("API_KEY", extras)
        self.assertIn("DB_PASSWORD", extras)
        self.assert_no_secret_leak(result)


class EnvSchemaCheckMaskingTest(EnvSchemaToolTestCase):
    """check mode: secret-ish values are masked in every preview."""

    def test_type_mismatch_preview_masked(self) -> None:
        result = self.tool.execute(
            mode="check",
            text="API_KEY=sk-live-abcdef123456\n",
            schema={"API_KEY": {"type": "int"}},
        )
        self.assertFalse(result["passed"])
        self.assertEqual(
            result["type_mismatches"][0]["raw_value_preview"], "***"
        )
        self.assert_no_secret_leak(result)

    def test_long_non_secret_preview_truncated(self) -> None:
        result = self.tool.execute(
            mode="check",
            text="URL=" + "a" * 40 + "\n",
            schema={"URL": {"type": "int"}},
        )
        preview = result["type_mismatches"][0]["raw_value_preview"]
        self.assertEqual(preview, "a" * 24 + "...")
        self.assertEqual(len(preview), 27)

    def test_secret_markers_all_mask(self) -> None:
        for var in ("API_KEY", "MY_TOKEN", "DB_PASSWORD", "CLIENT_SECRET",
                    "SECRET_CODE", "_password", "Token"):
            with self.subTest(var=var):
                result = self.tool.execute(
                    mode="check",
                    text=f"{var}=sk-live-abcdef123456\n",
                    schema={"var": {"type": "string"}},
                )
                # Declared under a neutral name, the secret-named extra
                # must still never expose its value.
                self.assert_no_secret_leak(result)

    def test_numeric_violation_masks_secret_value(self) -> None:
        result = self.tool.execute(
            mode="check",
            text="MAX_TOKENS=999\n",
            schema={"MAX_TOKENS": {"type": "int", "max": 10}},
        )
        self.assertFalse(result["passed"])
        self.assertEqual(result["violations"][0]["got"], "***")


class EnvSchemaSuggestTest(EnvSchemaToolTestCase):
    """suggest_schema mode: inference matrix + masking."""

    def test_inference_matrix(self) -> None:
        result = self.tool.execute(mode="suggest_schema", text=BASIC_TEXT)
        self.assert_no_secret_leak(result)
        inferred = {var: entry["type"]
                    for var, entry in result["schema"].items()}
        self.assertEqual(
            inferred,
            {
                "API_HOST": "string",
                "API_PORT": "int",
                "RATE_LIMIT": "float",
                "DEBUG": "bool",
                "LOG_LEVEL": "string",
                "SITE_URL": "url",
                "ADMIN_EMAIL": "email",
                "DATA_DIR": "string",  # path is never inferred
                "API_KEY": "string",
                "DB_PASSWORD": "string",
            },
        )

    def test_inference_priority_number_before_bool(self) -> None:
        result = self.tool.execute(
            mode="suggest_schema", text="A=1\nB=0\nC=yes\nD=1.5\n"
        )
        types = {v: e["type"] for v, e in result["schema"].items()}
        self.assertEqual(
            types, {"A": "int", "B": "int", "C": "bool", "D": "float"}
        )

    def test_required_true_and_samples(self) -> None:
        result = self.tool.execute(
            mode="suggest_schema", text="HOST=example.com\nPORT=8080\n"
        )
        self.assertEqual(
            result["schema"],
            {
                "HOST": {"type": "string", "required": True,
                         "sample_masked": "example.com"},
                "PORT": {"type": "int", "required": True,
                         "sample_masked": "8080"},
            },
        )

    def test_secret_sample_masked_and_no_enum(self) -> None:
        text = "API_KEY=v1\nAPI_KEY=v2\nAPI_KEY=v3\n"
        result = self.tool.execute(mode="suggest_schema", text=text)
        entry = result["schema"]["API_KEY"]
        self.assertEqual(entry["sample_masked"], "***")
        self.assertNotIn("inferred_enum", entry)
        self.assertNotIn("v1", json.dumps(result))
        self.assertNotIn("v2", json.dumps(result))
        self.assertNotIn("v3", json.dumps(result))

    def test_enum_detection_cutoff(self) -> None:
        # 2, 3 and 4 distinct values suggest an enum ...
        for distinct in (2, 3, 4):
            with self.subTest(distinct=distinct):
                text = "".join(
                    f"MODE=v{i}\n" for i in range(distinct)
                )
                result = self.tool.execute(mode="suggest_schema", text=text)
                self.assertEqual(
                    result["schema"]["MODE"]["inferred_enum"],
                    [f"v{i}" for i in range(distinct)],
                )
        # ... 1 proves nothing and 5+ is noise.
        single = self.tool.execute(
            mode="suggest_schema", text="MODE=only\n"
        )
        self.assertNotIn("inferred_enum", single["schema"]["MODE"])
        noisy_text = "".join(f"MODE=v{i}\n" for i in range(5))
        noisy = self.tool.execute(mode="suggest_schema", text=noisy_text)
        self.assertNotIn("inferred_enum", noisy["schema"]["MODE"])

    def test_enum_uses_distinct_parsed_values_in_order(self) -> None:
        text = "MODE=a\nMODE=a\nMODE=b\nMODE=a\n"
        result = self.tool.execute(mode="suggest_schema", text=text)
        self.assertEqual(
            result["schema"]["MODE"]["inferred_enum"], ["a", "b"]
        )

    def test_suggest_output_round_trips_into_check(self) -> None:
        suggested = self.tool.execute(
            mode="suggest_schema", text=BASIC_TEXT
        )["schema"]
        result = self.tool.execute(
            mode="check", text=BASIC_TEXT, schema=suggested
        )
        self.assertTrue(result["passed"])
        self.assert_no_secret_leak(result)

    def test_last_wins_value_drives_inference(self) -> None:
        result = self.tool.execute(
            mode="suggest_schema", text="N=abc\nN=42\n"
        )
        self.assertEqual(result["schema"]["N"]["type"], "int")


class EnvSchemaDiffTest(EnvSchemaToolTestCase):
    """diff mode: structure + masking rules."""

    PROD = (
        "API_HOST=prod.example.com\n"
        "API_PORT=443\n"
        "DEBUG=false\n"
        "API_KEY=sk-live-abcdef123456\n"
        "DB_PASSWORD=hunter2-secret\n"
    )
    STAGING = (
        "API_HOST=staging.example.com\n"
        "API_PORT=443\n"
        "FEATURE_FLAG=beta\n"
        "API_KEY=sk-test-000000000000\n"
        "DB_PASSWORD=hunter2-secret\n"
    )

    def test_diff_structure(self) -> None:
        result = self.tool.execute(
            mode="diff", text=self.PROD, text_b=self.STAGING
        )
        self.assertEqual(result["mode"], "diff")
        self.assert_no_secret_leak(result)
        self.assertEqual(
            result["only_in_a"], [{"var": "DEBUG", "value": "false"}]
        )
        self.assertEqual(
            result["only_in_b"],
            [{"var": "FEATURE_FLAG", "value": "beta"}],
        )
        self.assertEqual(
            result["value_diffs"],
            [
                {"var": "API_HOST", "a": "prod.example.com",
                 "b": "staging.example.com", "masked": False},
                {"var": "API_KEY", "a": "***", "b": "***", "masked": True},
            ],
        )
        self.assertEqual(result["count"], 4)
        self.assertTrue(result["result"].startswith("4 difference"))

    def test_diff_masks_secret_only_in_sides(self) -> None:
        result = self.tool.execute(
            mode="diff",
            text="API_KEY=sk-live-abcdef123456\n",
            text_b="OTHER=1\n",
        )
        self.assertEqual(
            result["only_in_a"], [{"var": "API_KEY", "value": "***"}]
        )
        self.assert_no_secret_leak(result)

    def test_diff_never_reveals_secret_either_side(self) -> None:
        result = self.tool.execute(
            mode="diff",
            text="DB_PASSWORD=hunter2-secret\n",
            text_b="DB_PASSWORD=other-password\n",
        )
        self.assertEqual(
            result["value_diffs"],
            [{"var": "DB_PASSWORD", "a": "***", "b": "***", "masked": True}],
        )
        self.assert_no_secret_leak(result)
        self.assertNotIn("other-password", json.dumps(result))

    def test_diff_identical_and_empty(self) -> None:
        same = self.tool.execute(
            mode="diff", text="A=1\nB=2\n", text_b="B=2\nA=1\n"
        )
        self.assertEqual(same["count"], 0)
        self.assertEqual(same["value_diffs"], [])
        empty = self.tool.execute(mode="diff", text="", text_b="")
        self.assertEqual(empty["count"], 0)
        self.assertEqual(empty["only_in_a"], [])
        self.assertEqual(empty["only_in_b"], [])

    def test_diff_surfaces_malformed_lines_per_side(self) -> None:
        result = self.tool.execute(
            mode="diff", text="A=1\noops\n", text_b="A=1\n??? nope\n"
        )
        self.assertEqual(result["malformed_lines_a"],
                         [{"line": 2, "content": "oops"}])
        self.assertEqual(result["malformed_lines_b"],
                         [{"line": 2, "content": "??? nope"}])


class EnvSchemaParsingSemanticsTest(EnvSchemaToolTestCase):
    """dotenv parsing rules shared with EnvFileTool, via check/suggest."""

    def test_export_prefix_and_comments_and_spacing(self) -> None:
        result = self.tool.execute(
            mode="check",
            text=(
                "# header\n"
                "\n"
                "export PORT = 8080\n"
                "TOKEN_VALUE=abc   # inline comment\n"
                "HASHY=a#b\n"
                "EMPTY_AFTER=#data\n"
            ),
            schema={
                "PORT": {"type": "int"},
                "TOKEN_VALUE": {"type": "string"},
                "HASHY": {"type": "string"},
                "EMPTY_AFTER": {"type": "string"},
            },
        )
        self.assertTrue(result["passed"])
        self.assertEqual(result["malformed_lines"], [])

    def test_hash_glued_after_equals_is_data(self) -> None:
        result = self.tool.execute(
            mode="suggest_schema", text="V=#c\n"
        )
        self.assertEqual(result["schema"]["V"]["sample_masked"], "#c")

    def test_double_quote_escapes_and_trailing_junk(self) -> None:
        result = self.tool.execute(
            mode="suggest_schema",
            text='V="a\\nb" # trailing\nW="say \\"hi\\""\n',
        )
        self.assertEqual(result["schema"]["V"]["sample_masked"], "a\nb")
        self.assertEqual(result["schema"]["W"]["sample_masked"], 'say "hi"')

    def test_single_quotes_are_literal(self) -> None:
        result = self.tool.execute(
            mode="suggest_schema", text="V='a\\nb'\n"
        )
        self.assertEqual(result["schema"]["V"]["sample_masked"], "a\\nb")

    def test_first_equals_splits(self) -> None:
        result = self.tool.execute(
            mode="suggest_schema", text="FORMULA=a=b=c\n"
        )
        self.assertEqual(result["schema"]["FORMULA"]["sample_masked"], "a=b=c")

    def test_duplicates_last_wins_with_all_lines(self) -> None:
        result = self.tool.execute(
            mode="check",
            text="MODE=a\nMODE=b\n",
            schema={"MODE": {"type": "string"}},
        )
        self.assertTrue(result["passed"])

    def test_malformed_lines_recorded_not_fatal(self) -> None:
        result = self.tool.execute(
            mode="check",
            text="A=1\nnot an assignment\n9bad=x\nexport\n",
            schema={"A": {"type": "int"}},
        )
        self.assertTrue(result["passed"])
        self.assertEqual(
            result["malformed_lines"],
            [
                {"line": 2, "content": "not an assignment"},
                {"line": 3, "content": "9bad=x"},
                {"line": 4, "content": "export"},
            ],
        )

    def test_unterminated_quotes_are_structured_errors(self) -> None:
        for mode_kwargs in (
            {"mode": "check", "schema": {"A": {"type": "string"}}},
            {"mode": "suggest_schema"},
        ):
            with self.subTest(mode=mode_kwargs["mode"]):
                result = self.tool.execute(
                    text='OK=1\nBAD="unclosed\n', **mode_kwargs
                )
                self.assertEqual(
                    result["error"]["type"], "unterminated_quote"
                )
                self.assertIn("line 2", result["error"]["message"])
        diff = self.tool.execute(
            mode="diff", text="A=1\n", text_b="BAD='unclosed\n"
        )
        self.assertEqual(diff["error"]["type"], "unterminated_quote")


class EnvSchemaDegenerateTest(EnvSchemaToolTestCase):
    """Empty env / empty schema / empty diff inputs."""

    def test_empty_env_against_schema_reports_all_missing(self) -> None:
        result = self.tool.execute(
            mode="check",
            text="",
            schema={
                "A": {"type": "int"},
                "B": {"type": "string", "required": False},
                "C": {"type": "string", "default": "x"},
            },
        )
        self.assertFalse(result["passed"])
        self.assertEqual(
            [(m["var"], m["suggestion"]) for m in result["missing"]],
            [("A", "A="), ("B", "B="), ("C", "C=x")],
        )
        self.assertEqual(
            result["applied_defaults"], [{"var": "C", "default": "x"}]
        )
        self.assertEqual(result["extra"], [])

    def test_empty_schema_reports_all_extra_and_passes(self) -> None:
        result = self.tool.execute(mode="check", text=BASIC_TEXT, schema={})
        self.assertTrue(result["passed"])
        self.assertEqual(len(result["extra"]), 10)
        self.assertEqual(result["missing"], [])
        self.assert_no_secret_leak(result)

    def test_suggest_on_empty_env(self) -> None:
        result = self.tool.execute(mode="suggest_schema", text="")
        self.assertEqual(result["schema"], {})
        self.assertTrue(result["result"].startswith("0 variable"))


class EnvSchemaErrorMatrixTest(EnvSchemaToolTestCase):
    """Parameter validation errors (ValueError before any computation)."""

    def test_unknown_mode(self) -> None:
        self.assert_invalid(mode="lint", text="A=1\n", schema={})
        self.assert_invalid(mode=None, text="A=1\n")

    def test_text_type_errors(self) -> None:
        for bad in (None, 123, True, ["A=1"], b"A=1"):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="check", text=bad, schema={})
                self.assert_invalid(mode="suggest_schema", text=bad)
                self.assert_invalid(mode="diff", text=bad, text_b="")

    def test_diff_requires_text_b(self) -> None:
        self.assert_invalid(mode="diff", text="A=1\n")

    def test_check_requires_schema(self) -> None:
        self.assert_invalid(mode="check", text="A=1\n")
        for bad in (None, [], "A=int", 42, True, [("A", {})]):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="check", text="A=1\n", schema=bad)

    def test_schema_key_errors(self) -> None:
        for bad_key in ("9BAD", "with space", "A-B", "", "A.B", 42, True):
            with self.subTest(bad_key=bad_key):
                self.assert_invalid(
                    mode="check", text="A=1\n", schema={bad_key: {}}
                )

    def test_rule_shape_errors_name_the_variable(self) -> None:
        cases = (
            ({"X": "string"}, "must be a dict"),
            ({"X": ["int"]}, "must be a dict"),
            ({"X": {"unknown": 1}}, "unknown key"),
            ({"X": {"type": "list"}}, "unknown type"),
            ({"X": {"type": None}}, "unknown type"),
            ({"X": {"required": "yes"}}, "required must be a boolean"),
            ({"X": {"required": 1}}, "required must be a boolean"),
            ({"X": {"default": 8080}}, "default must be a string"),
            ({"X": {"default": True}}, "default must be a string"),
            ({"X": {"type": "int", "min": "0"}}, "min must be a number"),
            ({"X": {"type": "int", "min": True}}, "min must be a number"),
            ({"X": {"type": "int", "min": 10, "max": 0}}, "greater than max"),
            ({"X": {"type": "string", "min": 1}}, "only apply to int or float"),
            ({"X": {"type": "bool", "max": 1}}, "only apply to int or float"),
            ({"X": {"enum": "debug"}}, "enum must be a non-empty list"),
            ({"X": {"enum": []}}, "enum must be a non-empty list"),
            ({"X": {"enum": ["a", "a"]}}, "duplicate"),
            ({"X": {"enum": ["a", 1]}}, "enum entries must be strings"),
        )
        for schema, fragment in cases:
            with self.subTest(schema=schema):
                with self.assertRaises(ValueError) as ctx:
                    self.tool.execute(
                        mode="check", text="A=1\n", schema=schema
                    )
                self.assertIn("X", str(ctx.exception))
                self.assertIn(fragment, str(ctx.exception))

    def test_text_size_limit(self) -> None:
        self.assert_invalid(mode="suggest_schema", text="A=1\n" * 60_000)

    def test_schema_variable_limit(self) -> None:
        schema = {f"V{i}": {"type": "string"} for i in range(1_001)}
        self.assert_invalid(mode="check", text="A=1\n", schema=schema)


class EnvSchemaToolPackagingTest(unittest.TestCase):
    """Packaging / registration."""

    def test_class_defaults_and_export(self) -> None:
        self.assertIs(DirectEnvSchemaTool, EnvSchemaTool)
        tool = EnvSchemaTool()
        self.assertEqual(tool.name, "env_schema_tool")
        for word in ("check", "suggest_schema", "diff", "schema"):
            self.assertIn(word, tool.description)
        from agentuniverse.agent.action.tool.common_tool import __all__

        self.assertIn("EnvSchemaTool", __all__)


if __name__ == "__main__":
    unittest.main()
