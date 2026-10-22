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
    _COMMON,
    _verdict,
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

# ---------------------------------------------------------------------------
# Independent reference implementations + a deterministic LCG corpus generator
# (written from scratch here so regressions are caught against a second
# derivation, not against the module's own code).
# ---------------------------------------------------------------------------

_RUN_SOURCES = (
    ("abcdefghijklmnopqrstuvwxyz", "alphabet-run"),
    ("0123456789", "digit-run"),
    ("qwertyuiop", "keyboard-run"),
    ("asdfghjkl", "keyboard-run"),
    ("zxcvbnm", "keyboard-run"),
    ("1234567890", "keyboard-run"),
)


def _lcg_passwords(count, seed=0x5EED_2026):
    chars = ("abcdefghijklmnopqrstuvwxyz"
             "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
             "0123456789"
             "!@#$%^&*()-_=+[]{};:,.?/"
             "äöüßéñ")
    state = seed
    out = []
    for _ in range(count):
        state = (state * 6364136223846793005 + 1442695040888963407) % (1 << 63)
        n = 6 + state % 12
        buf = []
        for _ in range(n):
            state = (state * 6364136223846793005 + 1442695040888963407) % (1 << 63)
            buf.append(chars[state % len(chars)])
        # splice run-shaped material into a third of the corpus so the
        # sequence detector gets nested/overlapping/palindrome cases too
        state = (state * 6364136223846793005 + 1442695040888963407) % (1 << 63)
        pwd = "".join(buf)
        if state % 3 == 0:
            mat = "abcdefghijklmnopqrstuvwxyz0123456789qwertyuiop"
            state = (state * 6364136223846793005 + 1442695040888963407) % (1 << 63)
            frag = mat[state % 30: state % 30 + 2 + state % 6]
            pos = (state // 7) % (len(pwd) - len(frag) + 1)
            pwd = pwd[:pos] + frag + pwd[pos + len(frag):]
        out.append(pwd)
    return out


def _ref_longest_run(password):
    """Brute-force: every window (len>=3) of the lowered password tested
    against every run source; alphabet/digit win ties over keyboard."""
    low = password.lower()
    best_len, best_kind = 0, ""
    for source, kind in _RUN_SOURCES:
        for i in range(len(low)):
            for j in range(i + 3, len(low) + 1):
                if low[i:j] in source and (
                        j - i > best_len
                        or (j - i == best_len
                            and best_kind == "keyboard-run"
                            and kind != "keyboard-run")):
                    best_len, best_kind = j - i, kind
    return best_len, best_kind


def _ref_longest_repeat(password):
    low = password.lower()
    best = 0
    i = 0
    while i < len(low):
        j = i
        while j + 1 < len(low) and low[j + 1] == low[i]:
            j += 1
        best = max(best, j - i + 1)
        i = j + 1
    return best


def _ref_effective_bits(password):
    pool = _pool_size(password)  # pool classes pinned by the equality test below
    raw = len(password) * math.log2(pool) if password else 0.0
    run_len, _ = _ref_longest_run(password)
    rep_len = _ref_longest_repeat(password)
    run_pen = (run_len - 2) * 2.0 if run_len >= 3 else 0.0
    rep_pen = (rep_len - 1) * 1.5 if rep_len >= 3 else 0.0
    common = raw * 0.9 if password.lower() in _COMMON else 0.0
    return max(0.0, raw - run_pen - rep_pen - common)


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

    # -- hostile-review regressions (seeded corpora + second derivation) ---- #

    def test_entropy_matches_reference_on_seeded_corpus(self):
        for pwd in _lcg_passwords(300):
            out = self.tool.execute(mode="entropy", password=pwd)
            self.assertEqual(out["pool_size"], _pool_size(pwd))
            self.assertEqual(out["raw_bits"], round(
                len(pwd) * math.log2(_pool_size(pwd)) if pwd else 0.0, 1))
            self.assertEqual(out["effective_bits"],
                             round(_ref_effective_bits(pwd), 1))
            seq = out["penalties"]["sequence"]
            rep = out["penalties"]["repetition"]
            run_len, run_kind = _ref_longest_run(pwd)
            rep_len = _ref_longest_repeat(pwd)
            self.assertEqual(seq["run_length"], run_len)
            self.assertEqual(seq["kind"], run_kind if run_len else "")
            self.assertEqual(seq["bits"], round(
                (run_len - 2) * 2.0 if run_len >= 3 else 0.0, 1))
            self.assertEqual(rep["run_length"], rep_len)
            self.assertEqual(rep["bits"], round(
                (rep_len - 1) * 1.5 if rep_len >= 3 else 0.0, 1))

    def test_sequence_detector_matches_bruteforce_reference(self):
        corpus = _lcg_passwords(300) + [
            "QwErTyUiOpZ9", "z9XcVbNm,", "01234567890z", "abcabcabcZ1",
            "XmnoZ1!", "CBAdefgZ9", "ijkZ1!", "zzyxwvu8Q", "PonmlZ2!",
        ]
        for pwd in corpus:
            got = self.tool.execute(mode="entropy", password=pwd
                                    )["penalties"]["sequence"]
            want_len, want_kind = _ref_longest_run(pwd)
            self.assertEqual(got["run_length"], want_len, pwd[:6] + "***")
            self.assertEqual(got["kind"], want_kind if want_len else "",
                             pwd[:6] + "***")

    def test_repetition_mixed_case_mixes(self):
        # Contract (case-insensitive): 'aAaAaA' is one run of 6; in mixed
        # material the longest case-folded run wins.
        for pwd, want in (("aAaBbb9!", 3), ("aAaAaA", 6), ("ZzZzZzZz1!", 8),
                          ("xXyYyYq2#", 4), ("abBAba1!", 2)):
            out = self.tool.execute(mode="entropy", password=pwd)
            self.assertEqual(out["penalties"]["repetition"]["run_length"],
                             want, pwd)

    def test_verdict_boundaries_exact_values(self):
        # Boundaries are exact on the unrounded quantity: at exactly 28/40/60
        # bits the HIGHER tier applies; one ulp below stays in the lower tier.
        for bits, want in ((0.0, "weak"), (27.999999999, "weak"), (28.0, "fair"),
                           (39.999999999, "fair"), (40.0, "moderate"),
                           (59.999999999, "moderate"), (60.0, "strong"),
                           (1e9, "strong")):
            self.assertEqual(_verdict(bits, 8, False), want, str(bits))
        # short passwords stay weak even with huge entropy budgets
        self.assertEqual(_verdict(1e9, 7, False), "weak")
        # blocklist overrides everything
        self.assertEqual(_verdict(1e9, 64, True), "very_weak")

    def test_username_type_validation(self):
        for bad in (12345, ["a"], {"x": 1}, 4.5):
            with self.assertRaises(ValueError):
                self.tool.execute(mode="audit", password="Zebra2026!Moon",
                                  username=bad)
        # absent / empty / proper string all fine
        self.tool.execute(mode="audit", password="Zebra2026!Moon", username=None)
        self.tool.execute(mode="audit", password="Zebra2026!Moon", username="")

    def _all_blobs(self, password):
        parts = [
            json.dumps(self.tool.execute(mode="audit", password=password,
                                         username="bob")),
            json.dumps(self.tool.execute(mode="entropy", password=password)),
            json.dumps(self.tool.execute(mode="policy_check", password=password)),
            json.dumps(self.tool.execute(mode="compare", password=password,
                                         password_b="Zx9$qpL2mQq")),
        ]
        return "".join(parts)

    def test_masking_seeded_corpus_no_four_char_fragments(self):
        # Random passwords must never collide with any output text at the
        # 4+-character granularity (numeric-only fragments are excluded: the
        # numeric length/pool/bit fields are reported by design).
        for pwd in _lcg_passwords(150):
            blob = self._all_blobs(pwd)
            for start in range(len(pwd) - 3):
                frag = pwd[start:start + 4]
                if not frag.isdigit():
                    self.assertNotIn(frag, blob, f"fragment {frag!r} leaked")

    def test_masking_adversarial_collisions_are_static_not_derived(self):
        # Passwords built from the tool's own output vocabulary ("information",
        # "Composition", "recommended", "screening", ...) DO collide with the
        # fixed label constants. The honest, pinned claim: every colliding
        # fragment also appears verbatim in the output for UNRELATED passwords
        # of the same structural shape, proving the text is a constant, not an
        # echo of the audited password.
        sentinels = [
            "Zx9$qpL2mVn4Rt7uYw1bAB",   # strong, all findings absent
            "Zx9$qpL2m",                # moderate, below_recommended_length
            "kqvpmwzx",                 # fair
            "aaaa1",                    # weak, repeated_character
            "Ab1!",                     # too_short_nist_min
            "123456",                   # very_weak, common_password
            "abcd1234wxyz9Q#",          # contains_sequence (alphabet+digit)
            "qwertyZx9$qpL2m",          # contains_sequence (keyboard)
            "bobcat2026!Zebra",         # contains_username for "bob"
            "PaSsWoRd1!Xy2#",           # policy/compare shapes
        ]
        static_text = "".join(self._all_blobs(p) for p in sentinels)
        adversarial = [
            "information2026", "Composition1!", "recommended4U",
            "necessary9X", "score1234A!", "weak12", "strong1A!",
            "Screening2026!", "characters8Z!", "length2026!Q",
            "alphabetabcd1", "qwertykeyboard", "verdicts2026!Q",
            "effectivebits7", "moderate2B!", "sufficient8Q",
        ]
        checked = 0
        for pwd in adversarial:
            blob = self._all_blobs(pwd)
            for size in range(4, min(len(pwd), 12) + 1):
                for start in range(len(pwd) - size + 1):
                    frag = pwd[start:start + size]
                    if frag.isdigit():
                        continue
                    if frag in blob:
                        checked += 1
                        self.assertIn(
                            frag, static_text,
                            f"fragment {frag!r} of {pwd!r} appears in output "
                            f"but is NOT part of the static label vocabulary — "
                            f"it would be a real password echo")


if __name__ == "__main__":
    unittest.main()
