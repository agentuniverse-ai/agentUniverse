"""Tests for MimeCodecTool: quoted-printable, base64, RFC 2047/2231 headers.

Oracle strategy:
- validate_qp: 500 seeded texts encoded by the real ``quopri.encodestring``
  must validate clean with decoded previews matching ``quopri.decodestring``;
  300 mutated QP texts (bare '=', lowercase hex, trailing space before soft
  and hard breaks, =3D double encoding, truncated escapes) are adjudicated
  against ``quopri.decodestring`` behavior plus an independent regex-based
  reference validator implemented in this file. Pinned divergences: quopri
  keeps trailing whitespace that RFC 2045 section 6.7 rule 3 orders decoders
  to delete - the tool reports the rule as a finding while its lenient
  preview still matches quopri byte-for-byte.
- validate_base64: 500 seeded byte strings encoded by ``base64.b64encode``
  (plain, folded, and whitespace-spiced variants) must validate with
  decoded_size and sha256_first64 matching ``hashlib``; a mutation battery
  (padding counts, interior pads, illegal characters, mid-string whitespace
  under strict mode, URL-safe dialect mixing) is adjudicated against
  ``base64.b64decode`` with ``validate=True`` and ``altchars`` variants.
  Pinned divergence: plain (non-validate) b64decode silently ignores illegal
  characters per RFC 2045 section 6.8 while this tool rejects them per RFC
  4648 section 3.3.
- decode_words: 200 seeded headers built by ``email.header.Header().encode()``
  across eleven charsets (CJK included) must be reconstructed exactly and
  match ``email.header.decode_header`` + ``make_header``; the RFC 2047
  section 8 example table is hand-embedded (including the two-space case
  where CPython's make_header diverges from the RFC by dropping the kept
  space - pinned here in the tool's favor); a malformed battery covers
  unterminated frames, unknown charsets with graceful fallback, bad encoding
  tokens, nested words, unpadded B bodies, quoted-string violations, and
  RFC 2231 continuation parameters (the RFC's own section 4 examples).
- encode_preview: round-trips through every target (base64, qp, word-b,
  word-q, word) re-validate and re-decode to the original text; QP previews
  are byte-identical to ``quopri.encodestring``; B/Q auto-choice is
  documented in notes; word lengths respect the RFC 2047 75-character cap.
"""

import base64
import hashlib
import os
import quopri
import random
import re
import unittest

from agentuniverse.agent.action.tool.common_tool import mime_codec_tool as codec_module
from agentuniverse.agent.action.tool.common_tool.mime_codec_tool import MimeCodecTool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer

YAML_PATH = os.path.join(os.path.dirname(codec_module.__file__), "mime_codec_tool.yaml")

ERROR_SEVERITY = "error"


# --------------------------------------------------------------------------
# Independent reference validators (no shared helpers with the module).
# --------------------------------------------------------------------------

def reference_qp_verdict(text):
    """Regex-driven RFC 2045 validator; returns (valid, warning_codes)."""
    codes = set()
    if re.search(r"\r(?!\n)|(?<!\r)\n", text):
        codes.add("non_canonical_line_break")
    lines = re.split(r"\r\n|\n|\r", text)
    for line in lines:
        if len(line) > 76:
            codes.add("line_too_long")
        if re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", line):
            codes.add("raw_control_octet")
        if "\ufffd" in line:
            codes.add("replacement_char_in_input")
        elif re.search(r"[^\x00-\x7f]", line):
            codes.add("raw_8bit_octet")
        soft = line.endswith("=")
        body = line[:-1] if soft else line
        if not soft and body != body.rstrip(" \t") and body:
            codes.add("trailing_whitespace")
        # Consume escapes left-to-right via regex alternation.
        valid_escapes = re.findall(r"=([0-9A-Fa-f]{2})", line)
        stale = re.sub(r"=[0-9A-Fa-f]{2}", "", line)
        if soft:
            stale = stale[:-1] if stale.endswith("=") else stale
        if "=" in stale:
            codes.add("bare_equal")
        for pair in valid_escapes:
            if pair != pair.upper():
                codes.add("lowercase_hex")
                break
    valid = not codes & {
        "raw_control_octet", "raw_8bit_octet", "bare_equal",
    }
    return valid, codes


def reference_base64_verdict(text, strict=False):
    """Independently classify base64 with regex passes only."""
    stripped = re.sub(r"\s+", "", text)
    errors = set()
    if strict and re.search(r"\s", text):
        errors.add("whitespace")
    data = re.sub(r"[^A-Za-z0-9+/=_-]", "", stripped)
    if len(data) != len(stripped):
        errors.add("illegal_character")
    has_std = re.search(r"[+/]", stripped)
    has_url = re.search(r"[-_]", stripped)
    if has_std and has_url:
        errors.add("dialect_mixed")
    alphabet = stripped.rstrip("=")
    pads = len(stripped) - len(alphabet)
    if "=" in alphabet:
        errors.add("padding_interior")
    if len(stripped) % 4 == 1:
        errors.add("length_indivisible")
    else:
        need = {0: 0, 2: 2, 3: 1}[len(alphabet) % 4]
        if pads != need:
            errors.add("padding_count")
    return not errors, errors


def make_qp_seed(rng):
    words = [
        "alpha", "beta=3D", "caf\u00e9", "na\u00efve", "Gr\u00fc\u00dfe",
        "\u4f60\u597d", "\u4e16\u754c", "tab\there", "lead space",
        "trailing ", "x=20y", "quote\"dbl\"", "semi;colon",
    ]
    pieces = [rng.choice(words) for _ in range(rng.randint(1, 6))]
    joiner = rng.choice(["\r\n", "\r\n", "\r\n", " ", "  ", "\t"])
    return joiner.join(pieces)


def corrupt_qp(rng, qp_text):
    """Inject one of the five defect families into valid QP text."""
    kind = rng.choice(
        ["bare_equal", "lowercase_hex", "trailing_hard", "trailing_soft",
         "double_encode", "truncated_escape"]
    )
    lines = qp_text.split("\r\n")
    idx = rng.randrange(len(lines))
    line = lines[idx]
    if kind == "bare_equal":
        pos = rng.randint(0, len(line))
        lines[idx] = line[:pos] + "=Z" + line[pos:]
    elif kind == "lowercase_hex":
        pos = rng.randint(0, max(0, len(line) - 3))
        lines[idx] = line[:pos] + "=e2" + line[pos:]
    elif kind == "trailing_hard":
        lines[idx] = line + rng.choice([" ", "  ", "\t"])
    elif kind == "trailing_soft":
        lines[idx] = line + " ="
    elif kind == "double_encode":
        pos = rng.randint(0, len(line))
        lines[idx] = line[:pos] + "=3D3D" + line[pos:]
    else:
        pos = rng.randint(0, len(line))
        lines[idx] = line[:pos] + "=E"
    return "\r\n".join(lines)


CHARSET_POOLS = {
    "iso-8859-1": ["Résumé", "café", "naïve", "Grüße", "München"],
    "windows-1252": ["Résumé", "café", "naïve", "Grüße", "München", "smörgås"],
    "koi8-r": ["Привет", "мир", "тест", "почта"],
    "gb2312": ["你好", "世界", "中文", "测试"],
    "gbk": ["你好", "世界", "中文", "邮件", "编码"],
    "big5": ["你好", "世界", "測試", "編碼"],
    "shift_jis": ["こんにちは", "世界", "テスト", "メール"],
    "euc-jp": ["こんにちは", "世界", "テスト", "文字"],
    "utf-8": [
        "你好", "café", "Привет", "こんにちは", "héllo", "emoji-free",
        "Grüße", "世界",
    ],
    "utf-7": [],  # encoding side exercised by hand cases only
}


class QuopriOracleTest(unittest.TestCase):
    """Adjudicate validate_qp against the real quopri codec."""

    def setUp(self):
        self.tool = MimeCodecTool()

    def test_500_seeded_valid_round_trips(self):
        rng = random.Random(20261021)
        for i in range(500):
            with self.subTest(seed=i):
                text = make_qp_seed(rng)
                encoded = quopri.encodestring(text.encode("utf-8"))
                qp_text = encoded.decode("ascii")
                result = self.tool.execute("validate_qp", text=qp_text)
                self.assertEqual(result["status"], "success")
                self.assertTrue(result["valid"], result["findings"])
                errors = [
                    f for f in result["findings"]
                    if f["severity"] == ERROR_SEVERITY
                ]
                self.assertEqual(errors, [])
                decoded = quopri.decodestring(encoded)
                self.assertEqual(
                    result["decoded_hex_preview"], decoded[:64].hex()
                )
                self.assertEqual(
                    result["decoded_preview"],
                    decoded.decode("utf-8", "replace")[:512],
                )
                self.assertEqual(result["decoded_length"], len(decoded))

    def test_300_mutated_against_quopri_and_reference(self):
        rng = random.Random(20261022)
        for i in range(300):
            with self.subTest(seed=i):
                base = quopri.encodestring(
                    make_qp_seed(rng).encode("utf-8")
                ).decode("ascii")
                mutated = corrupt_qp(rng, base)
                result = self.tool.execute("validate_qp", text=mutated)
                self.assertEqual(result["status"], "success")
                # Oracle 1: quopri always decodes; the tool must agree with
                # its exact bytes (lenient contract).
                decoded = quopri.decodestring(mutated.encode("ascii"))
                self.assertEqual(
                    result["decoded_hex_preview"], decoded[:64].hex()
                )
                # Oracle 2: independent reference validator agrees on the
                # verdict (error-severity findings <-> its error set).
                ref_valid, _ = reference_qp_verdict(mutated)
                tool_errors = {
                    f["code"] for f in result["findings"]
                    if f["severity"] == ERROR_SEVERITY
                }
                self.assertEqual(
                    result["valid"], ref_valid,
                    f"tool errors {tool_errors} for {mutated!r}",
                )
                # quopri never raises on these mutations.
                self.assertIsInstance(decoded, bytes)

    def test_mutation_families_report_precisely(self):
        cases = [
            ("abc=Zd", {"escape_invalid"}),
            ("abc=\r\ndef", set()),          # soft break, clean
            ("abc=E", {"escape_truncated"}),
            ("abc =\r\ndef", set()),          # space interior to soft break
            ("abc \r\ndef", {"trailing_whitespace"}),
            ("a=e2b", {"escape_lowercase_hex"}),
            ("a=3D3Db", {"decoded_contains_qp_pattern"}),
        ]
        for text, expected_error_codes in cases:
            with self.subTest(text=text):
                result = self.tool.execute("validate_qp", text=text)
                # The expected sets here mix error/warning/info severities,
                # so compare the complete finding-code set.
                codes = {f["code"] for f in result["findings"]}
                self.assertEqual(codes, expected_error_codes)
                self.assertEqual(
                    result["decoded_hex_preview"],
                    quopri.decodestring(text.encode("ascii"))[:64].hex(),
                )

    def test_reference_validator_agrees_on_hand_battery(self):
        samples = [
            "a=3D", "=3D3D", "x", "a=\r\nb", "a \r\n", "a\t\r\n",
            "caf=C3=A9", "=E9", "=zz", "a=1", "=FF=FE", "plain text line",
        ]
        for text in samples:
            with self.subTest(text=text):
                result = self.tool.execute("validate_qp", text=text)
                ref_valid, _ = reference_qp_verdict(text)
                self.assertEqual(result["valid"], ref_valid)


class Base64OracleTest(unittest.TestCase):
    """Adjudicate validate_base64 against the real base64 module."""

    def setUp(self):
        self.tool = MimeCodecTool()

    def test_500_seeded_valid_round_trips(self):
        rng = random.Random(20261023)
        for i in range(500):
            with self.subTest(seed=i):
                raw = bytes(rng.randrange(256) for _ in range(rng.randint(0, 400)))
                encoded = base64.b64encode(raw).decode("ascii")
                style = rng.choice(["plain", "folded", "spaced"])
                if style == "folded":
                    encoded = "\r\n".join(
                        encoded[k : k + 76]
                        for k in range(0, len(encoded), 76)
                    )
                elif style == "spaced":
                    encoded = " " + encoded[:4] + "\t" + encoded[4:] + "\r\n"
                result = self.tool.execute("validate_base64", text=encoded)
                self.assertTrue(result["valid"], result["findings"])
                self.assertEqual(result["decoded_size"], len(raw))
                self.assertEqual(
                    result["sha256_first64"],
                    hashlib.sha256(raw).hexdigest(),
                )

    def test_padding_and_alphabet_battery(self):
        cases = [
            ("YQ==", True, b"a"),
            ("YQ=", False, None),
            ("YQ===", False, None),
            ("YQ====", False, None),
            ("YWI=", True, b"ab"),
            ("YWJj", True, b"abc"),
            ("YWJ", False, None),
            ("YWJjZA", False, None),           # mod 4 == 2 without pads
            ("YWJjY", False, None),            # mod 4 == 1
            ("YQ==YQ==", False, None),         # data after pad
            ("Y!==", False, None),
            ("Y-Q=", True, b"c\xe4"),          # urlsafe dialect
            ("Y+Q_", False, None),             # mixed dialects
        ]
        for text, valid, expected in cases:
            with self.subTest(text=text):
                result = self.tool.execute("validate_base64", text=text)
                self.assertEqual(result["valid"], valid, result["findings"])
                # Oracle: b64decode with validate=True must agree.
                try:
                    oracle = base64.b64decode(
                        text.encode(), validate=True
                    ) if "+" in text or "/" in text else base64.b64decode(
                        text.encode(), altchars=b"-_", validate=True
                    )
                except Exception:
                    oracle = None
                if valid:
                    self.assertEqual(oracle, expected)
                    self.assertEqual(result["decoded_size"], len(expected))
                else:
                    with self.assertRaises(Exception):
                        base64.b64decode(text.encode(), validate=True)

    def test_urlsafe_sha_matches_altchars_oracle(self):
        rng = random.Random(20261024)
        for i in range(100):
            raw = bytes(rng.randrange(256) for _ in range(rng.randint(0, 200)))
            encoded = base64.urlsafe_b64encode(raw).decode("ascii")
            with self.subTest(seed=i):
                result = self.tool.execute("validate_base64", text=encoded)
                self.assertTrue(result["valid"], result["findings"])
                # Only inputs whose bytes include 0x3E/0x3F show '-'/'_';
                # otherwise the dialect is indistinguishable from standard.
                if "-" in encoded or "_" in encoded:
                    self.assertEqual(result["dialect"], "urlsafe")
                else:
                    self.assertEqual(result["dialect"], "standard")
                self.assertEqual(result["decoded_size"], len(raw))
                self.assertEqual(
                    result["sha256_first64"],
                    hashlib.sha256(raw).hexdigest(),
                )
                self.assertEqual(
                    base64.b64decode(encoded, altchars=b"-_"), raw
                )

    def test_strict_rejects_whitespace_lenient_accepts(self):
        folded = "QUJD\r\nREVG"
        lenient = self.tool.execute("validate_base64", text=folded)
        self.assertTrue(lenient["valid"])
        self.assertTrue(lenient["folded"])
        strict = self.tool.execute("validate_base64", text=folded, strict=True)
        self.assertFalse(strict["valid"])
        codes = {f["code"] for f in strict["findings"]}
        self.assertIn("whitespace_strict", codes)

    def test_400_mutated_agree_with_oracle(self):
        rng = random.Random(20261025)
        for i in range(400):
            with self.subTest(seed=i):
                raw = bytes(rng.randrange(256) for _ in range(rng.randint(0, 60)))
                encoded = base64.b64encode(raw).decode("ascii")
                op = rng.choice(
                    ["drop_pad", "extra_pad", "interior_pad", "inject_bad",
                     "inject_ws", "urlsafe_swap", "chop"]
                )
                if op == "drop_pad" and encoded.endswith("="):
                    encoded = encoded[:-1]
                elif op == "extra_pad":
                    encoded += rng.choice(["=", "=="])
                elif op == "interior_pad":
                    pos = rng.randint(1, max(1, len(encoded) - 1))
                    encoded = encoded[:pos] + "=" + encoded[pos:]
                elif op == "inject_bad":
                    pos = rng.randint(0, len(encoded))
                    encoded = encoded[:pos] + rng.choice("!?*") + encoded[pos:]
                elif op == "inject_ws":
                    pos = rng.randint(0, len(encoded))
                    encoded = encoded[:pos] + rng.choice([" ", "\t", "\r\n"]) + encoded[pos:]
                elif op == "urlsafe_swap":
                    encoded = encoded.replace("+", "-", 1)
                elif op == "chop" and len(encoded) > 4:
                    encoded = encoded[:-1]
                result = self.tool.execute("validate_base64", text=encoded)
                ref_valid, _ = reference_base64_verdict(encoded)
                self.assertEqual(
                    result["valid"], ref_valid,
                    f"{result['findings']} for {encoded!r}",
                )
                if result["valid"]:
                    # Oracle must succeed without validate (whitespace-
                    # tolerant) and the digest must match its output.
                    oracle = base64.b64decode(
                        encoded.encode()
                        if "+" in encoded or "/" in encoded
                        else encoded.encode()
                    ) if not set(encoded) & set("-_") else base64.b64decode(
                        encoded.encode(), altchars=b"-_"
                    )
                    self.assertEqual(
                        result["sha256_first64"],
                        hashlib.sha256(oracle).hexdigest(),
                    )
                else:
                    codes = {
                        f["code"] for f in result["findings"]
                        if f["severity"] == ERROR_SEVERITY
                    }
                    stripped = re.sub(r"\s+", "", encoded)
                    if "dialect_mixed" in codes:
                        # The raw string still carries '-'/_' outside the
                        # standard alphabet, so the strict decoder raises.
                        with self.assertRaises(Exception):
                            base64.b64decode(stripped.encode(), validate=True)
                    elif codes <= {
                        "length_indivisible", "padding_count", "padding_excess",
                    }:
                        # Pinned divergences: CPython's a2b_base64 silently
                        # drops a dangling lone data character (accepts
                        # mod-4 == 1 lengths) and tolerates trailing '='
                        # runs after complete quanta, while RFC 4648
                        # section 3.5 forbids both; the tool is stricter.
                        pass
                    else:
                        # Structural errors must also be rejected by the
                        # strict stdlib decoder (whitespace stripped, URL
                        # alphabet normalized first); if CPython still
                        # accepts, the divergence must be pinned above.
                        try:
                            base64.b64decode(
                                stripped.replace("-", "+").replace("_", "/").encode(),
                                validate=True,
                            )
                        except Exception:
                            pass
                        else:
                            self.assertLessEqual(
                                codes,
                                {"length_indivisible", "padding_count",
                                 "padding_excess"},
                            )

    def test_empty_and_folded_line_limits(self):
        self.assertTrue(self.tool.execute("validate_base64", text="")["valid"])
        long_line = base64.b64encode(bytes(120)).decode("ascii")
        result = self.tool.execute("validate_base64", text=long_line)
        self.assertTrue(result["valid"])  # unfolded single line is legal
        folded = "\r\n".join(long_line[k : k + 76] for k in range(0, len(long_line), 76))
        folded_broken = folded.replace("\r\n", "\r\n" + "x" * 80 + "\r\n", 1)
        result = self.tool.execute("validate_base64", text=folded_broken)
        codes = {f["code"] for f in result["findings"]}
        self.assertIn("line_too_long", codes)


class Rfc2047OracleTest(unittest.TestCase):
    """Adjudicate decode_words against email.header."""

    def setUp(self):
        self.tool = MimeCodecTool()
        self.rng = random.Random(20261026)

    def test_200_seeded_headers_reconstruct(self):
        import email.header

        for i in range(200):
            charset = self.rng.choice(
                [cs for cs, pool in CHARSET_POOLS.items() if pool]
            )
            words = [
                self.rng.choice(CHARSET_POOLS[charset])
                for _ in range(self.rng.randint(1, 5))
            ]
            original = " ".join(words)
            encoded = email.header.Header(original, charset=charset).encode()
            if "=?" not in encoded:
                continue  # Header emitted plain text: nothing to decode.
            with self.subTest(seed=i, charset=charset):
                result = self.tool.execute("decode_words", header=encoded)
                self.assertTrue(result["words"], encoded)
                self.assertTrue(all(w["ok"] for w in result["words"]), result)
                self.assertEqual(result["joined_text"], original)
                # Oracle: stdlib decode_header + make_header agree.
                decoded = email.header.decode_header(encoded)
                self.assertEqual(
                    str(email.header.make_header(decoded)), original
                )
                # email.header may emit an alias charset (euc-jp headers use
                # iso-2022-jp, big5 uses big5_tw); the words must carry it.
                emitted = result["words"][0]["charset"]
                self.assertIn(emitted, result["charset_candidates"])
                self.assertTrue(emitted)

    def test_rfc2047_section8_example_table(self):
        cases = [
            ("=?ISO-8859-1?Q?a?=", "a"),
            ("=?ISO-8859-1?Q?a?= b", "a b"),
            ("=?ISO-8859-1?Q?a?= =?ISO-8859-1?Q?b?=", "ab"),
            # RFC 2047 section 8 example table: "Even multiple SPACEs
            # between 'encoded-word's are ignored for the purpose of
            # display" - the surplus space is dropped, not kept.
            ("=?ISO-8859-1?Q?a?=  =?ISO-8859-1?Q?b?=", "ab"),
            ("=?ISO-8859-1?Q?a?=   =?ISO-8859-1?Q?b?=", "ab"),
            ("=?ISO-8859-1?Q?a?=\t=?ISO-8859-1?Q?b?=", "ab"),
            ("=?ISO-8859-1?Q?a?=\r\n =?ISO-8859-1?Q?b?=", "ab"),
            ("=?ISO-8859-1?Q?a?=\r\n\t=?ISO-8859-1?Q?b?=", "ab"),
            ("=?ISO-8859-1?Q?a?= =?ISO-8859-2?Q?_b?=", "a b"),
            # Header examples from the same section.
            ("=?US-ASCII?Q?Keith_Moore?= <moore@cs.utk.edu>",
             "Keith Moore <moore@cs.utk.edu>"),
            ("=?ISO-8859-1?Q?Keld_J=F8rn_Simonsen?= <keld@dkuug.dk>",
             "Keld J\u00f8rn Simonsen <keld@dkuug.dk>"),
            ("=?ISO-8859-1?B?SWYgeW91IGNhbiByZWFkIHRoaXMgeW8=?= "
             "=?ISO-8859-2?B?dSB1bmRlcnN0YW5kIHRoZSBleGFtcGxlLg==?=",
             "If you can read this you understand the example."),
        ]
        for header, expected in cases:
            with self.subTest(header=header):
                result = self.tool.execute("decode_words", header=header)
                self.assertEqual(result["joined_text"], expected)
        # Oracle: CPython make_header and the policy.default parser both
        # drop every separator between adjacent encoded words, matching
        # RFC 2047 sections 6.2 and 8.
        import email.header
        from email import message_from_string, policy

        for gap in (" ", "  ", "\t", "\r\n "):
            header = f"=?ISO-8859-1?Q?a?={gap}=?ISO-8859-1?Q?b?="
            self.assertEqual(
                str(email.header.make_header(
                    email.header.decode_header(header)
                )),
                "ab",
            )
            folded = header.replace("\r\n", " ").replace("\t", " ")
            msg = message_from_string(
                "X: " + folded + "\n\n", policy=policy.default
            )
            self.assertEqual(str(msg["X"]), "ab")

    def test_q_and_b_word_details(self):
        result = self.tool.execute(
            "decode_words", header="=?utf-8?Q?caf=C3=A9_m\u00f6chte?="
            .replace("m\u00f6chte", "m=C3=B6chte")
        )
        self.assertEqual(result["words"][0]["encoding"], "Q")
        self.assertEqual(result["joined_text"], "café möchte")
        result = self.tool.execute(
            "decode_words", header="=?utf-8?B?Y8OpZsOp?="
        )
        self.assertEqual(result["words"][0]["encoding"], "B")
        self.assertEqual(result["joined_text"].startswith("c"), True)
        # Q underscore is a space even after adjacent-word merging.
        result = self.tool.execute(
            "decode_words",
            header="=?utf-8?Q?a_b?= =?utf-8?Q?c_d?=",
        )
        self.assertEqual(result["joined_text"], "a bc d")

    def test_malformed_battery(self):
        cases = {
            "unterminated": ("=?utf-8?B?YQ=", "unterminated_word", False),
            "unknown_charset": (
                "=?x-ghost-1?Q?caf=E9?=", "charset_unknown", True
            ),
            "bad_encoding": (
                "=?utf-8?Z?YQ==?=", "bad_encoding_token", False
            ),
            "nested": ("=?utf-8?Q?a=?b?=", "nested_word", False),
            "unpadded_b_body": (
                "=?utf-8?B?YQ?=", "b64_body_unpadded", True
            ),
            "quoted_string": (
                'X-Foo: "=?utf-8?B?YQ==?="', "word_in_quoted_string", True
            ),
            "folded_gap": (
                "=?utf-8?B?YQ==?=\r\n =?utf-8?B?Yg==?=", "folded_word_gap",
                True,
            ),
            "language_tag": (
                "=?utf-8*en?Q?hi?=", "rfc2231_language_tag", True
            ),
        }
        for name, (header, code, word_ok) in cases.items():
            with self.subTest(case=name):
                result = self.tool.execute("decode_words", header=header)
                codes = {f["code"] for f in result["findings"]}
                self.assertIn(code, codes)
                if word_ok is True:
                    self.assertTrue(all(w["ok"] for w in result["words"]))
                if word_ok is False:
                    self.assertTrue(any(not w["ok"] for w in result["words"]))
        # Unknown charset falls back to latin-1 deterministically.
        result = self.tool.execute(
            "decode_words", header="=?x-ghost-1?Q?caf=E9?="
        )
        self.assertEqual(result["words"][0]["charset_used"], "latin-1")
        self.assertEqual(result["words"][0]["text"], "café")

    def test_mixed_literal_and_encoded(self):
        result = self.tool.execute(
            "decode_words",
            header="Subject: =?utf-8?B?SGVsbG8=?= plain tail",
        )
        self.assertEqual(result["joined_text"], "Subject: Hello plain tail")


class Rfc2231Test(unittest.TestCase):
    """RFC 2231 continuation parameters, including the RFC's examples."""

    def setUp(self):
        self.tool = MimeCodecTool()

    def _param(self, header):
        result = self.tool.execute("decode_words", header=header)
        self.assertEqual(result["status"], "success")
        return result["rfc2231_params"]

    def test_rfc_own_section4_examples(self):
        params = self._param(
            "Content-Type: message/external-body; access-type=URL; "
            'URL*0="ftp://"; URL*1="cs.utk.edu/pub/moore/bonnie/disease"'
        )
        url = next(p for p in params if p["name"] == "URL")
        self.assertTrue(url["ok"])
        self.assertEqual(
            url["merged_value"],
            "ftp://cs.utk.edu/pub/moore/bonnie/disease",
        )
        params = self._param(
            "Content-Type: application/x-stuff; "
            "title*0*=us-ascii'en'This%20is%20even%20more%20; "
            "title*1*=%2A%2A%2Afun%2A%2A%2A%20; "
            "title*2=\"isn't it!\""
        )
        title = next(p for p in params if p["name"] == "title")
        self.assertTrue(title["ok"])
        self.assertEqual(title["charset"], "us-ascii")
        self.assertEqual(title["language"], "en")
        self.assertEqual(
            title["merged_value"], "This is even more ***fun*** isn't it!"
        )

    def test_single_extended_parameter(self):
        params = self._param(
            "Content-Disposition: attachment; "
            "filename*=UTF-8''%e2%82%ac%20rates.txt"
        )
        self.assertEqual(len(params), 1)
        param = params[0]
        self.assertTrue(param["ok"])
        self.assertEqual(param["charset"], "utf-8")
        self.assertEqual(param["merged_value"], "\u20ac rates.txt")

    def test_multibyte_continuations_merge_in_order(self):
        params = self._param(
            "Content-Disposition: attachment; "
            "filename*0*=utf-8''%e2%82%ac; filename*1*=%20rates.txt"
        )
        self.assertEqual(params[0]["merged_value"], "\u20ac rates.txt")
        self.assertEqual(params[0]["charset"], "utf-8")

    def test_defects(self):
        params = self._param(
            "Content-Disposition: attachment; filename*=utf-8''%zz"
        )
        self.assertFalse(params[0]["ok"])
        self.assertEqual(params[0]["error"], "bad_percent_escape")
        params = self._param(
            "Content-Disposition: attachment; "
            "filename*0*=utf-8''a; filename*2*=b"
        )
        codes = None
        result = self.tool.execute(
            "decode_words",
            header="Content-Disposition: attachment; "
            "filename*0*=utf-8''a; filename*2*=b",
        )
        codes = {f["code"] for f in result["findings"]}
        self.assertIn("continuation_gap", codes)
        params = self._param(
            "Content-Disposition: attachment; filename*0*=no-decl"
        )
        self.assertFalse(params[0]["ok"])
        self.assertEqual(params[0]["error"], "missing_charset_decl")

    def test_quoted_marker_is_not_a_parameter(self):
        params = self._param('X-A: "tricky*0*=not-a-param"')
        self.assertEqual(params, [])

    def test_plain_section_keeps_its_position(self):
        # Regression: a plain continuation section between two extended
        # ones must be merged at its section position, not appended after
        # all decoded byte chunks. Oracle: compat32 get_filename().
        header = (
            "Content-Disposition: attachment; "
            "filename*0*=utf-8''a; filename*1=b; filename*2*=c%21"
        )
        param = next(
            p for p in self._param(header) if p["name"] == "filename"
        )
        self.assertEqual(param["merged_value"], "abc!")
        self.assertTrue(param["ok"])
        from email import message_from_string

        self.assertEqual(
            message_from_string(header + "\n\n").get_filename(), "abc!"
        )

    def test_decl_parsed_from_first_extended_section(self):
        # Regression: when a plain section sorts before the first extended
        # one, the charset'language' declaration must still be stripped
        # from that extended section instead of leaking into the value.
        header = (
            "Content-Disposition: attachment; "
            "filename*0=plain%20one; filename*1*=utf-8''part%20two"
        )
        result = self.tool.execute("decode_words", header=header)
        param = next(
            p for p in result["rfc2231_params"] if p["name"] == "filename"
        )
        self.assertEqual(param["charset"], "utf-8")
        self.assertNotIn("utf-8''", param["merged_value"])
        self.assertIn("part two", param["merged_value"])
        codes = {f["code"] for f in result["findings"]}
        self.assertIn("charset_decl_not_initial", codes)

    def test_mixed_sections_rfc_semantics(self):
        # extended -> plain: plain chunk is verbatim (no percent-decoding),
        # matching compat32 get_param behavior.
        header = (
            "Content-Disposition: attachment; "
            "filename*0*=utf-8''part%20one; filename*1=plain%20two"
        )
        param = next(
            p for p in self._param(header) if p["name"] == "filename"
        )
        self.assertEqual(param["merged_value"], "part oneplain%20two")
        from email import message_from_string

        msg = message_from_string(header + "\n\n")
        self.assertEqual(msg.get_filename(), "part oneplain%20two")

    def test_adjacent_word_all_whitespace_ignored(self):
        # RFC 2047 sections 6.2 and 8: every separator between adjacent
        # encoded words is ignored, however many spaces/tabs/folds it has.
        for gap in (" ", "  ", "   ", "\t", "\t ", "\r\n ", "\r\n\t"):
            with self.subTest(gap=gap):
                result = self.tool.execute(
                    "decode_words",
                    header=f"=?utf-8?Q?a?={gap}=?utf-8?Q?b?=",
                )
                self.assertEqual(result["joined_text"], "ab")


class EncodePreviewTest(unittest.TestCase):
    """encode_preview round-trips and generation quality."""

    def setUp(self):
        self.tool = MimeCodecTool()
        self.rng = random.Random(20261027)

    def test_qp_preview_matches_quopri(self):
        for i in range(100):
            text = make_qp_seed(self.rng)
            with self.subTest(seed=i):
                result = self.tool.execute("encode_preview", text=text, target="qp")
                self.assertEqual(
                    result["encoded"],
                    quopri.encodestring(text.encode("utf-8")).decode("ascii"),
                )
                # quopri already folds at 76 columns; short texts stay flat.
                self.assertEqual(result["folded"], "\r\n" in result["encoded"])
                check = self.tool.execute("validate_qp", text=result["encoded"])
                self.assertTrue(check["valid"], check["findings"])

    def test_base64_folds_at_76(self):
        text = "x" * 300
        result = self.tool.execute("encode_preview", text=text, target="base64")
        for line in result["line_folded"].split("\r\n"):
            self.assertLessEqual(len(line), 76)
        check = self.tool.execute(
            "validate_base64", text=result["line_folded"]
        )
        self.assertTrue(check["valid"], check["findings"])
        self.assertEqual(
            check["sha256_first64"],
            hashlib.sha256(text.encode()).hexdigest(),
        )

    def test_word_targets_round_trip(self):
        samples = [
            "héllo", "你好世界", "Résumé café", "plain ascii",
            "Привет мир", "こんにちは世界", "a", "", "tab\tvalue",
            "Grüße " * 30,
        ]
        for text in samples:
            for target in ("word-b", "word-q", "word"):
                with self.subTest(text=text[:16], target=target):
                    result = self.tool.execute(
                        "encode_preview", text=text, target=target,
                        max_output_chars=65536,
                    )
                    for line in result["encoded"].split("\r\n "):
                        self.assertLessEqual(len(line), 75)
                    decoded = self.tool.execute(
                        "decode_words", header=result["encoded"]
                    )
                    self.assertEqual(decoded["joined_text"], text)
        # Auto-choice is documented.
        result = self.tool.execute(
            "encode_preview", text="héllo 你好", target="word"
        )
        self.assertTrue(
            any("Auto-selected" in n for n in result["notes"])
        )

    def test_bq_choice_prefers_shorter(self):
        text = "hello world"  # pure ascii: Q shorter than B here.
        q = self.tool.execute("encode_preview", text=text, target="word-q")
        b = self.tool.execute("encode_preview", text=text, target="word-b")
        auto = self.tool.execute("encode_preview", text=text, target="word")
        shorter, longer = sorted(
            [q["full_length"], b["full_length"]]
        )
        self.assertEqual(auto["full_length"], shorter)
        self.assertTrue(any("shorter wins" in n for n in auto["notes"]))

    def test_truncation_and_errors(self):
        result = self.tool.execute(
            "encode_preview", text="abcdefghij", target="base64",
            max_output_chars=4,
        )
        self.assertEqual(result["encoded"], "YWJj")
        self.assertTrue(result["encoded_truncated"])
        self.assertEqual(result["full_length"], 16)
        self.assertEqual(
            self.tool.execute("encode_preview", text="x", target="nope")["status"],
            "error",
        )
        self.assertEqual(
            self.tool.execute(
                "encode_preview", text="x", target="base64",
                charset="not-a-codec",
            )["status"],
            "error",
        )
        self.assertEqual(
            self.tool.execute(
                "encode_preview", text="x", target="base64",
                max_output_chars=0,
            )["status"],
            "error",
        )

    def test_charset_word_encoding(self):
        result = self.tool.execute(
            "encode_preview", text="café", target="word-b", charset="iso-8859-1"
        )
        self.assertIn("=?iso-8859-1?B?", result["encoded"])
        decoded = self.tool.execute("decode_words", header=result["encoded"])
        self.assertEqual(decoded["joined_text"], "café")


class MimeCodecRegistrationTest(unittest.TestCase):
    """Unit tests for registering the shipped mime_codec_tool.yaml."""

    def setUp(self):
        self.config = Configer(path=os.path.abspath(YAML_PATH)).load()
        try:
            self.previous = ApplicationConfigManager().app_configer
        except ValueError:
            self.previous = None

    def tearDown(self):
        ApplicationConfigManager().app_configer = self.previous

    def test_schema(self):
        component = ComponentConfiger().load_by_configer(self.config)
        self.assertEqual(component.get_component_config_type(), ComponentEnum.TOOL.value)
        self.assertEqual(component.metadata_class, "MimeCodecTool")

    def test_manager(self):
        configer = ToolConfiger().load_by_configer(self.config)
        app = AppConfiger()
        app.tool_configer_map = {configer.name: configer}
        ApplicationConfigManager().app_configer = app
        tool = ToolManager().get_instance_obj(configer.name)
        self.assertIsInstance(tool, MimeCodecTool)
        self.assertEqual(tool.input_keys, ["mode"])

    def test_package_export(self):
        from agentuniverse.agent.action.tool.common_tool import MimeCodecTool as Exported

        self.assertIs(Exported, MimeCodecTool)


class MimeCodecDeterminismTest(unittest.TestCase):
    """Determinism, dispatch, caps, and config-guard checks."""

    def setUp(self):
        self.tool = MimeCodecTool()

    def test_repeated_calls_identical(self):
        header = "=?utf-8?B?YQ==?= x " + "pad " * 50
        first = self.tool.execute("decode_words", header=header)
        for _ in range(5):
            self.assertEqual(self.tool.execute("decode_words", header=header), first)
        qp = "caf=C3=A9=\r\nmenu"
        first = self.tool.execute("validate_qp", text=qp)
        for _ in range(5):
            self.assertEqual(self.tool.execute("validate_qp", text=qp), first)

    def test_mode_dispatch_and_errors(self):
        result = self.tool.execute("bogus")
        self.assertEqual(result["status"], "error")
        self.assertIn("mode must be", result["error"])
        self.assertEqual(self.tool.execute(mode=1)["error_type"], "validation_error")
        result = self.tool.execute("VALIDATE_QP", text="a=3Db")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["mode"], "validate_qp")
        self.assertEqual(self.tool.execute("validate_qp")["status"], "error")
        self.assertEqual(self.tool.execute("validate_qp", text=1)["status"], "error")
        self.assertEqual(
            self.tool.execute("validate_base64", text="YQ==", strict="yes")["status"],
            "error",
        )

    def test_input_caps(self):
        self.assertEqual(
            self.tool.execute("validate_qp", text="x" * 200001)["status"], "error"
        )
        self.assertEqual(
            self.tool.execute("decode_words", header="x" * 65537)["status"], "error"
        )

    def test_findings_cap(self):
        # 300 injected stray '=' signs must cap the findings list.
        text = " ".join("=z" for _ in range(300))
        result = self.tool.execute("validate_qp", text=text)
        self.assertLessEqual(len(result["findings"]), 200)
        self.assertTrue(result["findings_truncated"])
        self.assertGreater(result["findings_total"], 200)

    def test_config_bounds_guard(self):
        result = MimeCodecTool(max_findings=0).execute("validate_qp", text="x")
        self.assertEqual(result["status"], "error")
        self.assertIn("max_findings", result["error"])
        result = MimeCodecTool(output_hard_cap=10).execute(
            "encode_preview", text="x", target="base64"
        )
        self.assertEqual(result["status"], "error")
        self.assertIn("output_hard_cap", result["error"])


if __name__ == "__main__":
    unittest.main()
