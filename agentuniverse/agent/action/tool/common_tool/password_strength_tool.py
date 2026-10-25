#!/usr/bin/env python3
"""PasswordStrengthTool: offline password auditing with masked output.

Scores passwords against NIST SP 800-63B guidance and transparent entropy
estimates — character-pool entropy, repetition and sequence penalties (both
compared case-insensitively so alternating case cannot mask them), and a
common-password blocklist. Blocklist screening is an exact, case-insensitive
match; the blocklist embedded inside a longer password is NOT screened. The
tool never learns "the truth" about strength (offline heuristics cannot);
instead every finding names its reason so a caller can weigh it.

Guarantees:
- No network, no storage, no hashing against external databases.
- Output never contains password-DERIVED content: no preview, no masked
  form, not even a first character or per-position feedback is ever
  constructed from the password. The only structural fact reported is the
  numeric length. Caveat, stated honestly: verdict names, finding codes
  and note sentences are fixed constants that contain ordinary English
  words, so a password that itself contains one of those words (e.g.
  "information2026" vs the note word "information") coincides with part
  of a constant in the serialized output. Such collisions are provably
  not echoes — the same text is emitted for every password with the same
  shape — and the masking regression suite pins both halves: no password
  fragment of 4+ non-numeric characters appears in output over a random
  corpus, and every collision found for adversarial word-passwords also
  appears in the output of structurally identical unrelated passwords.

Modes:
  audit        -- full findings report with an overall verdict
  policy_check -- explicit rule-by-rule pass/fail against caller policy
  entropy      -- the numeric breakdown only
  compare      -- two passwords: which is stronger and why
"""

import math
import re
from typing import Any

from agentuniverse.agent.action.tool.tool import Tool

_MODES = ("audit", "policy_check", "entropy", "compare")

_MAX_PASSWORD_CHARS = 1024

# Public common-password blocklist (the classic top of every breached-list
# study). Lowercased for comparison; stored verbatim — these are published
# statistics, not secrets.
_COMMON = {
    "123456", "password", "123456789", "12345678", "12345", "qwerty",
    "1234567890", "1234", "111111", "1234567", "dragon", "123123", "abc123",
    "iloveyou", "monkey", "password1", "qwertyuiop", "admin", "letmein",
    "welcome", "login", "princess", "qwerty123", "solo", "passw0rd",
    "starwars", "master", "hello", "freedom", "whatever", "qazwsx",
    "trustno1", "baseball", "football", "superman", "batman", "shadow",
    "michael", "jennifer", "sunshine", "charlie", "jordan23", "hunter2",
    "zaq12wsx", "password123", "1q2w3e4r", "asdfgh", "1qaz2wsx", "p@ssw0rd",
    "changeme", "secret", "root", "toor", "guest", "test", "abcd1234",
}

_KEYBOARD_ROWS = ("qwertyuiop", "asdfghjkl", "zxcvbnm", "1234567890")
_ALPHABET_RUNS = "abcdefghijklmnopqrstuvwxyz"
_DIGIT_RUNS = "0123456789"

_SYMBOL_RE = re.compile(r"[^A-Za-z0-9]")


def _pool_size(password: str) -> int:
    pool = 0
    if re.search(r"[a-z]", password):
        pool += 26
    if re.search(r"[A-Z]", password):
        pool += 26
    if re.search(r"[0-9]", password):
        pool += 10
    if _SYMBOL_RE.search(password):
        pool += 33
    if any(ord(ch) > 127 for ch in password):
        pool += 100  # unicode supplement, deliberately conservative
    return max(pool, 1)


def _longest_run(password: str) -> tuple:
    """Longest keyboard or alphabet/digit contiguous run (length, kind)."""
    lower = password.lower()
    best_len, best_kind = 0, ""
    # Alphabet/digit runs first (more specific), keyboard rows only when
    # strictly longer, so "12345678" reports as a digit-run, not keyboard.
    for source, kind in ((_ALPHABET_RUNS, "alphabet-run"), (_DIGIT_RUNS, "digit-run")):
        for start in range(len(source)):
            for end in range(start + 3, len(source) + 1):
                frag = source[start:end]
                if frag in lower and end - start > best_len:
                    best_len, best_kind = end - start, kind
    for row in _KEYBOARD_ROWS:
        for start in range(len(row)):
            for end in range(start + 3, len(row) + 1):
                frag = row[start:end]
                if frag in lower and end - start > best_len:
                    best_len, best_kind = end - start, "keyboard-run"
    return best_len, best_kind


def _longest_repeat(password: str) -> int:
    """Longest consecutive repeat, compared case-insensitively ('aAa' is a
    run of 3) so alternating case cannot mask repetition from the auditor
    (sequence detection is already case-insensitive; this matches it)."""
    lower = password.lower()
    best_len = 0
    i = 0
    while i < len(lower):
        j = i
        while j + 1 < len(lower) and lower[j + 1] == lower[i]:
            j += 1
        if j - i + 1 > best_len:
            best_len = j - i + 1
        i = j + 1
    return best_len


def _entropy_detail(password: str) -> tuple:
    """Return (rounded entropy dict, exact unrounded effective bits).

    Tier verdicts and comparisons use the exact value so the 28/40/60-bit
    boundaries apply to the real quantity, not to its display rounding."""
    pool = _pool_size(password)
    raw = len(password) * math.log2(pool) if password else 0.0
    run_len, run_kind = _longest_run(password)
    rep_len = _longest_repeat(password)
    run_penalty = (run_len - 2) * 2.0 if run_len >= 3 else 0.0
    rep_penalty = (rep_len - 1) * 1.5 if rep_len >= 3 else 0.0
    common_hit = password.lower() in _COMMON
    common_penalty = raw * 0.9 if common_hit else 0.0
    effective = max(0.0, raw - run_penalty - rep_penalty - common_penalty)
    info = {
        "pool_size": pool,
        "raw_bits": round(raw, 1),
        "penalties": {
            "sequence": {"bits": round(run_penalty, 1), "run_length": run_len, "kind": run_kind},
            "repetition": {"bits": round(rep_penalty, 1), "run_length": rep_len},
            "common_password": {"bits": round(common_penalty, 1), "hit": common_hit},
        },
        "effective_bits": round(effective, 1),
    }
    return info, effective


def _entropy_bits(password: str) -> dict:
    return _entropy_detail(password)[0]


def _verdict(effective_bits: float, length: int, common_hit: bool) -> str:
    if common_hit:
        return "very_weak"
    if length < 8 or effective_bits < 28:
        return "weak"
    if effective_bits < 40:
        return "fair"
    if effective_bits < 60:
        return "moderate"
    return "strong"


class PasswordStrengthTool(Tool):
    """Offline password audit with masked output."""

    name: str = "password_strength_tool"
    description: str = (
        "Audit password strength offline: NIST SP 800-63B guidance findings, "
        "transparent entropy estimates with sequence/repetition/common-list "
        "penalties, and policy checks. Output never echoes the password."
    )
    tool_type: str = "api"

    def execute(self, mode: str = "audit", password: str = "",
                password_b: str = "", username: str = "",
                min_length: int = 8, max_length: int = 0,
                require_lower: bool = False, require_upper: bool = False,
                require_digit: bool = False, require_symbol: bool = False,
                **kwargs: Any) -> Any:
        """Run one password audit.

        - audit:        password (+ optional username for context checks)
        - policy_check: password against the explicit policy options
        - entropy:      numeric breakdown only
        - compare:      password vs password_b
        """
        if mode not in _MODES:
            raise ValueError(f"mode must be one of {_MODES}; got {mode!r:.64}")
        if username and not isinstance(username, str):
            raise ValueError(
                f"username must be a string, got {type(username).__name__}"
            )
        if mode == "compare":
            return self._compare(password, password_b)
        pwd = self._check_password(password)
        entropy, exact_bits = _entropy_detail(pwd)
        if mode == "entropy":
            return {"mode": "entropy", "length": len(pwd), **entropy}
        if mode == "policy_check":
            return self._policy(pwd, min_length, max_length, require_lower,
                                require_upper, require_digit, require_symbol)
        return self._audit(pwd, username, entropy, exact_bits)

    # ------------------------------------------------------------------ #

    @staticmethod
    def _check_password(password: Any) -> str:
        if not isinstance(password, str):
            raise ValueError(
                f"password must be a string, got {type(password).__name__}"
            )
        if len(password) > _MAX_PASSWORD_CHARS:
            raise ValueError(
                f"password longer than {_MAX_PASSWORD_CHARS} chars is out of scope"
            )
        return password

    def _audit(self, pwd: str, username: str, entropy: dict, exact_bits: float) -> dict:
        common_hit = entropy["penalties"]["common_password"]["hit"]
        findings = []
        if len(pwd) < 8:
            findings.append({"code": "too_short_nist_min",
                             "severity": "high",
                             "detail": "NIST SP 800-63B minimum is 8 characters"})
        elif len(pwd) < 15:
            findings.append({"code": "below_recommended_length",
                             "severity": "info",
                             "detail": "15+ characters recommended for user-chosen secrets"})
        if common_hit:
            findings.append({"code": "common_password",
                             "severity": "critical",
                             "detail": "matches a published top-common-password entry"})
        if entropy["penalties"]["sequence"]["run_length"] >= 4:
            findings.append({"code": "contains_sequence",
                             "severity": "medium",
                             "detail": "contains a "
                             + entropy["penalties"]["sequence"]["kind"]
                             + " of length "
                             + str(entropy["penalties"]["sequence"]["run_length"])})
        if entropy["penalties"]["repetition"]["run_length"] >= 3:
            findings.append({"code": "repeated_character",
                             "severity": "low",
                             "detail": "a single character (case-insensitive) repeats "
                             + str(entropy["penalties"]["repetition"]["run_length"])
                             + " times in a row"})
        if username:
            u = username.lower()
            if len(u) >= 3 and u in pwd.lower():
                findings.append({"code": "contains_username",
                                 "severity": "high",
                                 "detail": "password embeds the associated username"})
        classes = {
            "lower": bool(re.search(r"[a-z]", pwd)),
            "upper": bool(re.search(r"[A-Z]", pwd)),
            "digit": bool(re.search(r"[0-9]", pwd)),
            "symbol": bool(_SYMBOL_RE.search(pwd)),
            "unicode": any(ord(ch) > 127 for ch in pwd),
        }
        return {
            "mode": "audit",
            "length": len(pwd),
            "composition": classes,
            "entropy": entropy,
            "verdict": _verdict(exact_bits, len(pwd), common_hit),
            "findings": findings,
            "notes": [
                "Offline heuristics; a high score is necessary, not sufficient",
                "Composition rules are reported as information; NIST 800-63B "
                "discourages mandatory composition in favor of length and screening",
            ],
        }

    def _policy(self, pwd: str, min_length: int, max_length: int,
                require_lower: bool, require_upper: bool,
                require_digit: bool, require_symbol: bool) -> dict:
        if min_length < 0 or (max_length and max_length < min_length):
            raise ValueError("max_length must be >= min_length >= 0")
        rules = [
            {"rule": "min_length", "pass": len(pwd) >= min_length,
             "detail": f"{len(pwd)} vs {min_length}"},
        ]
        if max_length:
            rules.append({"rule": "max_length", "pass": len(pwd) <= max_length,
                          "detail": f"{len(pwd)} vs {max_length}"})
        for name, flag, pattern in (
            ("require_lower", require_lower, r"[a-z]"),
            ("require_upper", require_upper, r"[A-Z]"),
            ("require_digit", require_digit, r"[0-9]"),
            ("require_symbol", require_symbol, r"[^A-Za-z0-9]"),
        ):
            if flag:
                rules.append({"rule": name, "pass": bool(re.search(pattern, pwd)),
                              "detail": ""})
        rules.append({"rule": "not_common", "pass": pwd.lower() not in _COMMON,
                      "detail": "screened against the common-password blocklist"})
        return {
            "mode": "policy_check", "length": len(pwd),
            "rules": rules, "compliant": all(r["pass"] for r in rules),
        }

    def _compare(self, pwd_a: str, pwd_b: str) -> dict:
        a = self._check_password(pwd_a)
        b = self._check_password(pwd_b)
        ea, exact_a = _entropy_detail(a)
        eb, exact_b = _entropy_detail(b)
        va = _verdict(exact_a, len(a), ea["penalties"]["common_password"]["hit"])
        vb = _verdict(exact_b, len(b), eb["penalties"]["common_password"]["hit"])
        rank = {"very_weak": 0, "weak": 1, "fair": 2, "moderate": 3, "strong": 4}
        if rank[va] != rank[vb]:
            which, why = ("a", "verdict") if rank[va] > rank[vb] else ("b", "verdict")
        elif exact_a != exact_b:
            which = "a" if exact_a > exact_b else "b"
            why = "effective_bits"
        else:
            which, why = "tie", "identical verdicts and effective bits"
        return {
            "mode": "compare",
            "a": {"length": len(a), "effective_bits": ea["effective_bits"], "verdict": va},
            "b": {"length": len(b), "effective_bits": eb["effective_bits"], "verdict": vb},
            "stronger": which, "why": why,
        }
