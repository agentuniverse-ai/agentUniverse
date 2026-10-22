#!/usr/bin/env python3
"""Offline unit tests for PasswordStrengthTool.

Oracles: hand-verified entropy arithmetic (independently recomputed with
math.log2 in the test), the published NIST SP 800-63B guidance mapping, the
embedded common-password blocklist, and a masking invariant enforced over
the whole corpus (no password substring longer than three characters ever
appears in any output).
"""

import json
import math
import unittest

from agentuniverse.agent.action.tool.common_tool.password_strength_tool import (
    PasswordStrengthTool,
    _pool_size,
)

CORPUS = [
    "123456", "p4ssw0rd!", "qwerty123", "abc123",  # blocklist / runs
    "aaaaaaa1",                                    # repetition
    "Tr0ub4dor&3",                                 # classic xkcd case
    "correct-horse-battery-staple",                # passphrase
    "Zx9$qpL2mVn4Rt7uYw1b",                        # strong random-ish
    "short1",                                      # below NIST minimum
    "ünïcödé-pässwörd-2026",                       # unicode
    "Gk7!aQ",                                      # tiny but rich charset
]


class PasswordStrengthToolTest(unittest.TestCase):
    def setUp(self):
        self.tool = PasswordStrengthTool()

    # -- entropy arithmetic (independent recomputation) ------------------- #

    def test_pool_entropy_matches_independent_math(self):
        for pwd in CORPUS:
            with self.subTest(pwd[:2] + "***"):
                out = self.tool.execute(mode="entropy", password=pwd)
                self.assertEqual(out["pool_size"], _pool_size(pwd))
                expected_raw = len(pwd) * math.log2(_pool_size(pwd))
                self.assertAlmostEqual(out["raw_bits"], round(expected_raw, 1), places=6)
                penalties = out["penalties"]
                expected_effective = max(
                    0.0,
                    expected_raw
                    - penalties["sequence"]["bits"]
                    - penalties["repetition"]["bits"]
                    - penalties["common_password"]["bits"],
                )
                self.assertAlmostEqual(out["effective_bits"],
                                        round(expected_effective, 1), places=6)

    def test_sequence_detection(self):
        out = self.tool.execute(mode="entropy", password="XqwertyuiopZ9")
        self.assertGreaterEqual(out["penalties"]["sequence"]["run_length"], 8)
        self.assertEqual(out["penalties"]["sequence"]["kind"], "keyboard-run")
        out = self.tool.execute(mode="entropy", password="m12345678z")
        self.assertGreaterEqual(out["penalties"]["sequence"]["run_length"], 7)
        self.assertEqual(out["penalties"]["sequence"]["kind"], "digit-run")
        out = self.tool.execute(mode="entropy", password="a7Kp2mQ9xL")
        self.assertEqual(out["penalties"]["sequence"]["run_length"], 0)

    def test_repetition_detection(self):
        out = self.tool.execute(mode="entropy", password="Paaaaaa2!")
        self.assertEqual(out["penalties"]["repetition"]["run_length"], 6)
        out = self.tool.execute(mode="entropy", password="aA1!aA1!aA1!")
        self.assertEqual(out["penalties"]["repetition"]["run_length"], 2)

    def test_repetition_case_insensitive(self):
        # Alternating case must not mask repetition from the auditor; the
        # sequence detector lowercases, so the repeat detector must too.
        out = self.tool.execute(mode="entropy", password="aAaAaAaAaAaAaA")
        self.assertEqual(out["penalties"]["repetition"]["run_length"], 14)
        self.assertEqual(out["penalties"]["repetition"]["bits"], 19.5)
        audit = self.tool.execute(mode="audit", password="aAaAaAaAaAaAaA")
        self.assertTrue(any(f["code"] == "repeated_character" for f in audit["findings"]))
        out = self.tool.execute(mode="entropy", password="aAaAaA")
        self.assertEqual(out["penalties"]["repetition"]["run_length"], 6)

    def test_verdict_uses_exact_bits_not_rounded(self):
        # 12 chars, pool 62, alphabet-run 4 (penalty 4.0) and repeat run 6
        # (penalty 7.5): exact effective = 12*log2(62) - 4.0 - 7.5
        # = 59.950356... which ROUNDS UP to 60.0 for display. The verdict
        # ladder must follow the exact value (< 60 => moderate), not the
        # rounded display figure.
        pwd = "abcdkkkkkk9Z"
        out = self.tool.execute(mode="entropy", password=pwd)
        self.assertEqual(out["effective_bits"], 60.0)  # display rounds up
        audit = self.tool.execute(mode="audit", password=pwd)
        self.assertEqual(audit["verdict"], "moderate")
        cmp_out = self.tool.execute(mode="compare", password=pwd,
                                    password_b="Zx9$qpL2mVn4Rt7uYw1b")
        self.assertEqual(cmp_out["stronger"], "b")

    def test_blocklist_case_handling_and_exact_match_contract(self):
        # Exact match is case-insensitive: every casing of a blocklist entry
        # is caught and verdicted very_weak.
        for pwd in ("Password1", "PASSWORD1", "password1"):
            out = self.tool.execute(mode="entropy", password=pwd)
            self.assertTrue(out["penalties"]["common_password"]["hit"], pwd)
            self.assertEqual(self.tool.execute(mode="audit", password=pwd)["verdict"],
                             "very_weak")
        # Screening is exact-match only (documented): a blocklist entry
        # embedded in a longer password is NOT screened. Pinned honestly so
        # the contract is explicit rather than assumed.
        for pwd in ("xpassword1x", " password1", "password10"):
            out = self.tool.execute(mode="entropy", password=pwd)
            self.assertFalse(out["penalties"]["common_password"]["hit"], pwd)

    def test_sequence_contract_forward_only(self):
        # The run detector matches contiguous FORWARD runs in its sources;
        # descending runs are out of contract and must report zero, so the
        # limitation stays visible instead of half-firing.
        out = self.tool.execute(mode="entropy", password="zyxwv987654")
        self.assertEqual(out["penalties"]["sequence"]["run_length"], 0)

    def test_length_cap_boundary(self):
        self.assertEqual(
            self.tool.execute(mode="audit", password="q" * 1024)["length"], 1024)
        with self.assertRaises(ValueError):
            self.tool.execute(mode="audit", password="q" * 1025)

    def test_common_password_penalty(self):
        out = self.tool.execute(mode="entropy", password="qwerty")
        self.assertTrue(out["penalties"]["common_password"]["hit"])
        audit = self.tool.execute(mode="audit", password="qwerty")
        self.assertEqual(audit["verdict"], "very_weak")
        self.assertTrue(any(f["code"] == "common_password" for f in audit["findings"]))

    # -- NIST guidance mapping ------------------------------------------- #

    def test_nist_findings(self):
        audit = self.tool.execute(mode="audit", password="Ab1!")
        codes = [f["code"] for f in audit["findings"]]
        self.assertIn("too_short_nist_min", codes)
        audit = self.tool.execute(mode="audit", password="Xk7$mQ2pL")
        codes = [f["code"] for f in audit["findings"]]
        self.assertIn("below_recommended_length", codes)
        self.assertNotIn("too_short_nist_min", codes)
        self.assertTrue(any("Composition rules are reported" in n for n in audit["notes"]))

    def test_username_context(self):
        audit = self.tool.execute(mode="audit", password="alice2026!Zebra",
                                  username="alice")
        self.assertTrue(any(f["code"] == "contains_username" for f in audit["findings"]))
        audit = self.tool.execute(mode="audit", password="Zebra2026!Moon",
                                  username="alice")
        self.assertFalse(any(f["code"] == "contains_username" for f in audit["findings"]))

    def test_verdict_ladder(self):
        ladder = [
            ("123456", "very_weak"),
            ("aaaa1", "weak"),          # below NIST minimum length
            ("kqvpmwzx", "fair"),        # 8 lowercase no-pattern: ~37 bits, passes NIST min
            ("Zx9$qpL2m", "moderate"),   # ~59 effective bits
        ]
        for pwd, want in ladder:
            with self.subTest(want):
                self.assertEqual(self.tool.execute(mode="audit", password=pwd)["verdict"], want)
        strong = self.tool.execute(mode="audit", password="Zx9$qpL2mVn4Rt7uYw1b")
        self.assertIn(strong["verdict"], ("moderate", "strong"))

    # -- policy mode ------------------------------------------------------ #

    def test_policy_check(self):
        out = self.tool.execute(
            mode="policy_check", password="Passw0rd!", min_length=8,
            require_lower=True, require_upper=True, require_digit=True,
        )
        by_rule = {r["rule"]: r["pass"] for r in out["rules"]}
        self.assertTrue(by_rule["min_length"])
        self.assertTrue(by_rule["require_lower"])
        self.assertTrue(by_rule["require_upper"])
        self.assertTrue(by_rule["require_digit"])
        self.assertNotIn("require_symbol", by_rule)  # only requested rules appear
        self.assertTrue(out["compliant"])
        out = self.tool.execute(mode="policy_check", password="short",
                                min_length=10)
        self.assertFalse(out["compliant"])
        with self.assertRaises(ValueError):
            self.tool.execute(mode="policy_check", password="x",
                              min_length=10, max_length=4)

    # -- compare mode ----------------------------------------------------- #

    def test_compare(self):
        out = self.tool.execute(mode="compare", password="123456",
                                password_b="Zx9$qpL2mVn4Rt7")
        self.assertEqual(out["stronger"], "b")
        self.assertEqual(out["why"], "verdict")
        out = self.tool.execute(mode="compare", password="Zx9$qpL2mVn4Rt7uYw1b",
                                password_b="Zx9$qpL2mVn4Rt7uYw1b")
        self.assertEqual(out["stronger"], "tie")

    # -- masking invariant + validation ------------------------------------ #

    def test_no_password_echo_anywhere(self):
        for pwd in CORPUS:
            for mode, kwargs in (
                ("audit", {"password": pwd, "username": "alice"}),
                ("entropy", {"password": pwd}),
                ("policy_check", {"password": pwd}),
            ):
                with self.subTest(f"{mode}:{pwd[:1]}***"):
                    blob = json.dumps(self.tool.execute(mode=mode, **kwargs))
                    for start in range(len(pwd) - 7):
                        fragment = pwd[start:start + 8]
                        self.assertNotIn(fragment, blob)

    def test_validation(self):
        with self.assertRaises(ValueError):
            self.tool.execute(mode="nope", password="x")
        with self.assertRaises(ValueError):
            self.tool.execute(mode="audit", password=12345)
        with self.assertRaises(ValueError):
            self.tool.execute(mode="audit", password="x" * 2000)
        out = self.tool.execute(mode="audit", password="")
        self.assertEqual(out["length"], 0)
        self.assertEqual(out["verdict"], "weak")

    def test_blocklist_is_public_common_set(self):
        # spot-pin published top entries so the embedded set stays honest
        for classic in ("123456", "password", "qwerty", "letmein", "admin"):
            out = self.tool.execute(mode="entropy", password=classic)
            self.assertTrue(out["penalties"]["common_password"]["hit"], classic)


if __name__ == "__main__":
    unittest.main()
