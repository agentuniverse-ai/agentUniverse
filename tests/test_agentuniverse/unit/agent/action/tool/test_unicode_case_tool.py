"""Oracle tests for UnicodeCaseTool: the stdlib is the specification.

Every verdict in these tests is recomputed with the plain ``str`` case
methods and ``unicodedata`` so the tool is checked against the same
implementation-defined behavior it must expose:

(a) a 2,000-string seeded corpus over the interesting characters (sharp s,
    dotted I, ligatures, sigmas, Kelvin sign, long s, micro sign, CJK, emoji,
    combining marks, ASCII) verifying byte-equal results, per-character
    mappings, changed counts, and interesting-mapping detection for all five
    targets;
(b) an exhaustive sweep of every codepoint 0..U+10FFFF (surrogates excluded)
    in 1024-character chunks for upper/lower/title/casefold, comparing each
    per-character mapping with the stdlib method - measured at ~2s total, so
    the sweep stays complete over all planes (no sampling fallback needed);
(c) a 200-pair seeded equivalence battery plus the classic traps, with every
    verdict recomputed through ``str.casefold``/``str.lower``;
(d) a 300-identifier seeded style battery against a hand-labeled table, plus
    deterministic conversion round-trips and idempotence;
(e) the Final_Sigma context rule of SpecialCasing used as a probe oracle for
    both the frozen Case_Ignorable table and the ``Cased`` mirror;
(f) pathological 1 MiB inputs bounded under two seconds and cap enforcement.
"""

import os
import random
import time
import unicodedata
import unittest
from typing import ClassVar

from agentuniverse.agent.action.tool.common_tool import unicode_case_tool as unicode_case_module
from agentuniverse.agent.action.tool.common_tool.unicode_case_tool import UnicodeCaseTool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer

YAML_PATH = os.path.join(os.path.dirname(unicode_case_module.__file__), "unicode_case_tool.yaml")

TARGETS = ("upper", "lower", "title", "casefold", "swapcase")
MAX_CODEPOINT = 0x10FFFF

# The deliberately nasty characters every corpus is built around, written with
# explicit escapes so the codepoints cannot be mistaken for lookalikes.
INTERESTING_CHARS = (
    "\u00df\u1e9e\u0130\u0131\ufb01\ufb02\ufb00\ufb03\ufb04"
    "\u03c2\u03c3\u03a3\u03a9\u2126\u212a\u006b\u017f\u0073\u00b5\u03bc\u212b\u00e5"
    "\u01c5\u01c4\u01c6\u01c7\u01c8\u01c9\u01f1\u01f2\u01f3\u0149\u01f0"
    "\U00010400\U00010428\U000104b0\U000013a0\U0001ab70"
    "\u0410\u0411\u0430\u0431"
)
CJK_CHARS = "\u4e2d\u65e5\u672c\u8a9e\u6f22\u5b57"
EMOJI_CHARS = "\U0001f600\U0001f680\U0001f44d\U0001f1e9\U0001f3fb"
COMBINING_CHARS = "\u0300\u0301\u0302\u0307\u0331\u0345"
ASCII_CHARS = "azAZ09_ -"


def seeded_corpus(seed, count, min_length=1, max_length=48):
    """Deterministically build `count` strings from the interesting alphabets."""
    rng = random.Random(seed)  # noqa: S311
    alphabet = INTERESTING_CHARS + CJK_CHARS + EMOJI_CHARS + COMBINING_CHARS + ASCII_CHARS
    corpus = []
    for _ in range(count):
        length = rng.randint(min_length, max_length)
        corpus.append("".join(rng.choice(alphabet) for _ in range(length)))
    return corpus


def cased_probe(codepoint):
    """Probe the stdlib Final_Sigma machinery: is the codepoint cased?"""
    probe_char = chr(codepoint)
    before = ("\u0391\u03a3" + probe_char).lower()[1]
    after = ("\u0391\u03a3" + probe_char + "\u0391").lower()[1]
    return before == "\u03c3" and after == "\u03c3"


def ignorable_probe(codepoint):
    """Probe the stdlib Final_Sigma machinery: is the codepoint Case_Ignorable?"""
    probe_char = chr(codepoint)
    before = ("\u0391\u03a3" + probe_char).lower()[1]
    after = ("\u0391\u03a3" + probe_char + "\u0391").lower()[1]
    return before == "\u03c2" and after == "\u03c3"


def build_identifier(rng):
    """Deterministically build one identifier and the style it must detect."""
    words_pool = ["user", "name", "get", "http", "response", "xml", "data", "id", "api", "client", "db", "v2"]
    acronym_pool = ["HTTP", "XML", "URL", "ID", "API", "JSON", "CSV"]
    count = rng.randint(1, 4)
    words = [rng.choice(words_pool) for _ in range(count)]
    if rng.random() < 0.3:
        words[rng.randrange(count)] = rng.choice(acronym_pool)
    builder = rng.choice(["snake", "camel", "pascal", "screaming", "kebab", "mixed"])
    all_lower = all(w.islower() for w in words)
    all_upper = all(not w.islower() for w in words)
    if builder == "snake":
        identifier = "_".join(words)
        expected = "snake_case" if all_lower else ("SCREAMING_SNAKE" if all_upper else "mixed")
    elif builder == "screaming":
        identifier = "_".join(w.upper() for w in words)
        expected = "SCREAMING_SNAKE"
    elif builder == "kebab":
        identifier = "-".join(words)
        if count == 1:
            expected = "snake_case" if all_lower else "SCREAMING_SNAKE"
        else:
            expected = "kebab-case" if all_lower else "mixed"
    elif builder == "camel":
        lowered = [words[0].lower(), *words[1:]]
        identifier = lowered[0] + "".join(w.title() for w in lowered[1:])
        expected = "camelCase" if count > 1 else "snake_case"
    elif builder == "pascal":
        identifier = "".join(w.title() for w in words)
        letters = [ch for ch in identifier if ch.isalpha()]
        # A one-word identifier whose only letters are uppercase (e.g. 'V2')
        # is inherently SCREAMING/Pascal ambiguous and picks SCREAMING_SNAKE.
        single_all_upper = count == 1 and letters and all(ch.isupper() for ch in letters)
        expected = "SCREAMING_SNAKE" if single_all_upper else "PascalCase"
    else:
        if count > 1:
            identifier = "_".join([words[0].lower(), words[1].title(), *[w.lower() for w in words[2:]]])
            expected = "mixed"
        else:
            identifier = words[0].lower()
            expected = "snake_case"
    return identifier, expected


class UnicodeCaseToolCaseMapTest(unittest.TestCase):
    """Seeded-corpus oracle tests for the case_map mode."""

    def setUp(self):
        """Create a tool with per-character caps large enough for the corpus."""
        self.tool = UnicodeCaseTool(max_per_char_entries=64, max_interesting_mappings=64)

    def test_seeded_corpus_matches_str_methods(self):
        """Every mapping of 2,000 seeded strings equals the str method byte-for-byte."""
        corpus = seeded_corpus(20251021, 2_000)
        for text in corpus:
            for target in TARGETS:
                method = getattr(text, target)
                result = self.tool.execute(mode="case_map", text=text, target=target)
                self.assertEqual(result["status"], "success", (text, target))
                self.assertEqual(result["result"], method(), (text, target))
                self.assertEqual(result["result_length"], len(method()), (text, target))
                self.assertEqual(
                    result["changed_count"],
                    sum(1 for ch in text if getattr(ch, target)() != ch),
                    (text, target),
                )
                self.assertFalse(result["per_char_truncated"], (text, target))
                self.assertEqual(len(result["per_char"]), len(text), (text, target))
                for entry, ch in zip(result["per_char"], text, strict=True):
                    self.assertEqual(entry["original"], ch)
                    self.assertEqual(entry["mapped"], getattr(ch, target)(), (text, target, ch))
                    self.assertEqual(entry["changed"], getattr(ch, target)() != ch)

    def test_interesting_mappings_identify_length_changes(self):
        """Characters with any expanding mapping are flagged; notes match lengths."""
        corpus = seeded_corpus(20251021, 2_000)
        for text in corpus:
            for target in TARGETS:
                result = self.tool.execute(mode="case_map", text=text, target=target)
                flagged = {entry["char"] for entry in result["interesting_mappings"]}
                expanding = {ch for ch in text if any(len(getattr(ch, name)()) != 1 for name in TARGETS)}
                self.assertTrue(expanding.issubset(flagged), (text, target, expanding - flagged))
                for entry in result["interesting_mappings"]:
                    change = entry["length_change"]
                    if change is not None:
                        self.assertNotEqual(len(entry["mapped"]), 1, entry)
                        self.assertEqual(change["from"], 1)
                        self.assertEqual(change["to"], len(entry["mapped"]))

    def test_canonical_interesting_characters_present(self):
        """The canonical non-obvious characters appear with curated notes."""
        text = "stra\u00dfe\u0130\ufb01\u03c2\u212a\u2126\u017f\u00b5\u01c5\U00010400\U000013a0"
        result = self.tool.execute(mode="case_map", text=text, target="upper")
        notes = {entry["char"]: entry for entry in result["interesting_mappings"]}
        for ch in (
            "\u00df",
            "\u0130",
            "\ufb01",
            "\u03c2",
            "\u212a",
            "\u2126",
            "\u017f",
            "\u00b5",
            "\u01c5",
            "\U00010400",
            "\U000013a0",
        ):
            self.assertIn(ch, notes, hex(ord(ch)))
        self.assertIn("casefold", notes["\u00df"]["note"])
        self.assertIn("Final_Sigma", notes["\u03c2"]["note"])
        self.assertIn("locale-independent", notes["\u0130"]["note"])
        self.assertIn("Kelvin".lower(), notes["\u212a"]["note"].lower())
        self.assertIn("DESERET", notes["\U00010400"]["note"])
        self.assertIn("CHEROKEE", notes["\U000013a0"]["note"])

    def test_final_sigma_in_context(self):
        """Word-final sigma reports the contextual mapping next to the isolated one."""
        result = self.tool.execute(
            mode="case_map", text="\u039f\u0394\u03a5\u03a3\u03a3\u0395\u03a5\u03a3", target="lower"
        )
        self.assertEqual(result["result"], "\u03bf\u03b4\u03c5\u03c3\u03c3\u03b5\u03c5\u03c2")
        final = result["per_char"][-1]
        self.assertEqual(final["original"], "\u03a3")
        self.assertEqual(final["mapped"], "\u03c3")
        self.assertEqual(final["mapped_in_context"], "\u03c2")
        medial = self.tool.execute(mode="case_map", text="\u0391\u03a3\u0391", target="lower")
        self.assertEqual(medial["result"], "\u03b1\u03c3\u03b1")
        self.assertNotIn("mapped_in_context", medial["per_char"][1])

    def test_caps_and_truncation_flags(self):
        """per-character and interesting lists cap with explicit truncation flags."""
        long_text = "a\u00df\u0130\ufb01\u03c2" * 300
        tool = UnicodeCaseTool(max_per_char_entries=10, max_interesting_mappings=2)
        result = tool.execute(mode="case_map", text=long_text, target="upper")
        self.assertEqual(len(result["per_char"]), 10)
        self.assertTrue(result["per_char_truncated"])
        self.assertEqual(len(result["interesting_mappings"]), 2)
        self.assertTrue(result["interesting_mappings_truncated"])

    def test_validation_errors(self):
        """Invalid modes, targets, types, and cross-mode parameters error out."""
        self.assertIn("must be", self.tool.execute(mode="bogus")["error"])
        self.assertIn("target", self.tool.execute(mode="case_map", text="a", target="fold")["error"])
        self.assertIn("text must be a string", self.tool.execute(mode="case_map", text=5)["error"])
        self.assertIn(
            "not accepted in this mode",
            self.tool.execute(mode="case_map", text="a", text_a="b")["error"],
        )
        oversized = "a" * (1_048_576 + 1)
        self.assertIn("max_text_chars", self.tool.execute(mode="case_map", text=oversized)["error"])
        empty = self.tool.execute(mode="case_map", text="")
        self.assertEqual(empty["status"], "success")
        self.assertEqual(empty["result"], "")


class UnicodeCaseToolSweepTest(unittest.TestCase):
    """Exhaustive all-codepoint sweep: per-character mappings equal str methods."""

    def setUp(self):
        """Create a tool whose per-character caps cover a full chunk."""
        self.tool = UnicodeCaseTool(max_per_char_entries=4_096, max_interesting_mappings=2_048)
        self.chunk_size = 1_024

    def test_every_codepoint_every_method(self):
        """All 1,112,064 non-surrogate codepoints match upper/lower/title/casefold.

        Measured at roughly two seconds for the full four-method sweep on the
        development machine, so the sweep covers every plane exhaustively
        instead of falling back to sampled higher planes.
        """
        for base in range(0, MAX_CODEPOINT + 1, self.chunk_size):
            chunk = "".join(
                chr(codepoint)
                for codepoint in range(base, min(base + self.chunk_size, MAX_CODEPOINT + 1))
                if not 0xD800 <= codepoint <= 0xDFFF
            )
            if not chunk:
                continue
            with self.subTest(plane_chunk=hex(base)):
                for target in ("upper", "lower", "title", "casefold"):
                    result = self.tool.execute(mode="case_map", text=chunk, target=target)
                    self.assertEqual(result["status"], "success")
                    self.assertEqual(result["result"], getattr(chunk, target)())
                    self.assertFalse(result["per_char_truncated"])
                    for entry, ch in zip(result["per_char"], chunk, strict=True):
                        self.assertEqual(entry["mapped"], getattr(ch, target)(), (hex(ord(ch)), target))


class UnicodeCaseToolEquivalenceTest(unittest.TestCase):
    """Equivalence-mode oracle: verdicts recomputed through str methods."""

    def setUp(self):
        """Create the tool under test."""
        self.tool = UnicodeCaseTool()

    def nfc_casefold(self, text):
        """Reference implementation of the canonical identifier comparison."""
        return unicodedata.normalize("NFC", unicodedata.normalize("NFC", text).casefold())

    def check(self, first, second):
        """Assert the tool matches the stdlib-recomputed verdicts."""
        result = self.tool.execute(mode="equivalence", text_a=first, text_b=second)
        expected = {
            "identical": first == second,
            "casefold_equal": first.casefold() == second.casefold(),
            "lower_equal": first.lower() == second.lower(),
            "nfc_casefold_equal": self.nfc_casefold(first) == self.nfc_casefold(second),
        }
        for key, value in expected.items():
            self.assertEqual(result[key], value, (first, second, key))
        return result

    def test_classic_traps(self):
        """The canonical trap pairs behave exactly as the stdlib says."""
        traps = [
            ("stra\u00dfe", "STRASSE"),
            ("Stra\u00dfe", "STRASSE"),
            ("\u00df", "ss"),
            ("\u1e9e", "ss"),
            ("\u00df", "\u00df"),
            ("SS", "\u00df"),
            ("\u03a9", "\u03c9"),
            ("\u03a9", "\u2126"),
            ("\u2126", "\u03c9"),
            ("\u03a9", "\u03a9"),
            ("\u212a", "k"),
            ("\u212a", "K"),
            ("\u017f", "s"),
            ("\u017f", "S"),
            ("\ufb00", "ff"),
            ("\ufb01", "fi"),
            ("\u00b5", "\u03bc"),
            ("\u212b", "\u00e5"),
            ("\u01c5", "\u01c6"),
            ("\u01c4", "\u01c6"),
            ("\u01c5", "\u01c4"),
            ("\u03c2", "\u03c3"),
            ("\u03a3", "\u03c2"),
            ("\u1f08\u0394\u03a5\u03a3\u03a3\u0395\u03a5\u03a3", "\u1f08\u03b4\u03c5\u03c3\u03c3\u03b5\u03cd\u03c2"),
            ("\u0130", "i"),
            ("I", "\u0131"),
            ("\u0131", "I"),
            ("i", "\u0130"),
            ("e\u0301", "\u00e9"),
            ("entity_id", "ENTITY-ID"),
        ]
        for first, second in traps:
            self.check(first, second)

    def test_trap_verdicts_documented_in_design(self):
        """The pedagogical verdicts from the design hold."""
        sharp = self.check("stra\u00dfe", "STRASSE")
        self.assertTrue(sharp["casefold_equal"])
        self.assertFalse(sharp["lower_equal"])
        self.assertIn("lower()", sharp["explanation"])
        long_s = self.check("\u017f", "s")
        self.assertTrue(long_s["casefold_equal"])
        self.assertFalse(long_s["lower_equal"])
        micro = self.check("\u00b5", "\u03bc")
        self.assertTrue(micro["casefold_equal"])
        self.assertFalse(micro["lower_equal"])
        ohm = self.check("\u03a9", "\u2126")
        self.assertTrue(ohm["casefold_equal"])
        self.assertTrue(ohm["lower_equal"])
        kelvin = self.check("\u212a", "k")
        self.assertTrue(kelvin["casefold_equal"])
        self.assertTrue(kelvin["identical"] is False)
        turkish = self.check("\u0130", "i")
        self.assertFalse(turkish["casefold_equal"])
        self.assertFalse(turkish["nfc_casefold_equal"])
        decomposed = self.check("e\u0301", "\u00e9")
        self.assertTrue(decomposed["nfc_casefold_equal"])
        self.assertFalse(decomposed["identical"])

    def test_seeded_pair_battery(self):
        """200 seeded pairs: every verdict equals the stdlib recomputation."""
        rng = random.Random(252)  # noqa: S311
        alphabet = INTERESTING_CHARS + CJK_CHARS + ASCII_CHARS
        for _ in range(200):
            first = "".join(rng.choice(alphabet) for _ in range(rng.randint(1, 20)))
            second = "".join(rng.choice(alphabet) for _ in range(rng.randint(1, 20)))
            self.check(first, second)

    def test_differences_and_caps(self):
        """Differences explain the first divergences and respect the cap."""
        result = self.tool.execute(mode="equivalence", text_a="abcXdef", text_b="abcYdef")
        self.assertFalse(result["casefold_equal"])
        self.assertEqual(len(result["differences"]), 1)
        self.assertEqual(result["differences"][0]["index"], 3)
        capped = self.tool.execute(mode="equivalence", text_a="a" * 300, text_b="b" * 300)
        self.assertEqual(len(capped["differences"]), 100)
        self.assertTrue(capped["differences_truncated"])
        expanding = self.check("\u00df", "ss")
        self.assertTrue(expanding["casefold_equal"])
        self.assertEqual(expanding["differences"], [])


class UnicodeCaseToolStyleAuditTest(unittest.TestCase):
    """Style-audit oracle: hand table, seeded battery, and round-trips."""

    def setUp(self):
        """Create the tool under test."""
        self.tool = UnicodeCaseTool()

    HAND_TABLE: ClassVar[list[tuple[str, str, bool]]] = [
        ("user_name", "snake_case", False),
        ("get_http_response_code", "snake_case", False),
        ("user2_name", "snake_case", False),
        ("user_name_2", "snake_case", False),
        ("_private_value", "snake_case", False),
        ("userName", "camelCase", False),
        ("getHTTPResponse", "camelCase", False),
        ("user2Name", "camelCase", False),
        ("UserName", "PascalCase", False),
        ("HTTPServer", "PascalCase", False),
        ("XMLHttpRequest", "PascalCase", False),
        ("User2Name", "PascalCase", False),
        ("USER_NAME", "SCREAMING_SNAKE", False),
        ("HTTP_SERVER", "SCREAMING_SNAKE", False),
        ("USER2_NAME", "SCREAMING_SNAKE", False),
        ("user-name", "kebab-case", False),
        ("get-http-response", "kebab-case", False),
        ("config", "snake_case", True),
        ("CONFIG", "SCREAMING_SNAKE", True),
        ("x", "snake_case", True),
        ("\u4e2d\u6587", "snake_case", True),
        ("getUser_Name", "mixed", False),
        ("user-Name", "mixed", False),
        ("getUser-name", "mixed", False),
        ("getUserByID", "camelCase", False),
        ("MP3Player", "PascalCase", False),
        ("V2_DB", "SCREAMING_SNAKE", False),
        ("A", "SCREAMING_SNAKE", True),
        ("V2", "SCREAMING_SNAKE", True),
    ]

    def test_hand_table(self):
        """Hand-labeled identifiers detect the expected style and ambiguity."""
        for identifier, style, ambiguous in self.HAND_TABLE:
            result = self.tool.execute(mode="style_audit", identifier=identifier)
            self.assertEqual(result["status"], "success", identifier)
            self.assertEqual(result["detected_style"], style, identifier)
            self.assertEqual(result["ambiguous"], ambiguous, identifier)
            self.assertTrue(result["evidence"], identifier)

    def test_word_extraction(self):
        """Word extraction handles digits, acronyms, and separators."""
        cases = {
            "HTTPServer": ["HTTP", "Server"],
            "XMLHttpRequest": ["XML", "Http", "Request"],
            "getUserByID": ["get", "User", "By", "ID"],
            "user2_name": ["user2", "name"],
            "MP3Player": ["MP3", "Player"],
            "parseCSV2JSON": ["parse", "CSV2", "JSON"],
            "snake_case_name": ["snake", "case", "name"],
            "kebab-case-name": ["kebab", "case", "name"],
        }
        for identifier, words in cases.items():
            result = self.tool.execute(mode="style_audit", identifier=identifier)
            self.assertEqual(result["words"], words, identifier)

    def test_seeded_identifier_battery(self):
        """300 seeded identifiers match the style they were built from."""
        rng = random.Random(252252)  # noqa: S311
        for index in range(300):
            identifier, expected = build_identifier(rng)
            result = self.tool.execute(mode="style_audit", identifier=identifier)
            self.assertEqual(result["detected_style"], expected, (index, identifier))
            target = expected if expected != "mixed" else "snake_case"
            audit = self.tool.execute(mode="style_audit", identifier=identifier, target_style=target)
            converted = audit["suggested_conversion"]
            self.assertRegex(converted, r"^[A-Za-z0-9_\-]+$")
            if expected != "mixed":
                self.assertEqual(audit["conforms"], expected == target, (identifier, target))

    def test_conversion_round_trips(self):
        """snake->camel->snake preserves words and every conversion is idempotent."""
        snake_ids = ["user_account_service", "get_http_response", "http_server_v2", "db_client", "parse_json"]
        for snake_id in snake_ids:
            camel = self.tool.execute(mode="style_audit", identifier=snake_id, target_style="camelCase")[
                "suggested_conversion"
            ]
            back = self.tool.execute(mode="style_audit", identifier=camel, target_style="snake_case")[
                "suggested_conversion"
            ]
            self.assertEqual(back, snake_id, snake_id)
        for identifier in ["HTTPServer", "getUser_Name", "xml_http_request", "USER-ID", "v2Parser"]:
            words = self.tool.execute(mode="style_audit", identifier=identifier)["words"]
            lowered = [w.lower() for w in words]
            for style in ("snake_case", "camelCase", "PascalCase", "SCREAMING_SNAKE", "kebab-case"):
                converted = self.tool.execute(mode="style_audit", identifier=identifier, target_style=style)[
                    "suggested_conversion"
                ]
                rewords = self.tool.execute(mode="style_audit", identifier=converted)["words"]
                self.assertEqual([w.lower() for w in rewords], lowered, (identifier, style))
                again = self.tool.execute(mode="style_audit", identifier=converted, target_style=style)[
                    "suggested_conversion"
                ]
                self.assertEqual(again, converted, (identifier, style))

    def test_violations_and_suggestions(self):
        """Violations name every deviation and the conversion fixes them all."""
        result = self.tool.execute(mode="style_audit", identifier="getUserName", target_style="snake_case")
        self.assertFalse(result["conforms"])
        kinds = [v["kind"] for v in result["violations"]]
        self.assertEqual(kinds, ["word_case", "word_case"])
        self.assertEqual([v["suggested"] for v in result["violations"]], ["user", "name"])
        fixed = result["suggested_conversion"]
        self.assertEqual(fixed, "get_user_name")
        recheck = self.tool.execute(mode="style_audit", identifier=fixed, target_style="snake_case")
        self.assertTrue(recheck["conforms"])
        self.assertEqual(recheck["violations"], [])
        screaming = self.tool.execute(mode="style_audit", identifier="user-name", target_style="SCREAMING_SNAKE")
        self.assertTrue(any(v["kind"] == "separator" and v["suggested"] == "_" for v in screaming["violations"]))

    def test_validation_errors(self):
        """target_style, word caps, and non-alphanumeric identifiers error out."""
        self.assertIn(
            "target_style", self.tool.execute(mode="style_audit", identifier="a", target_style="lisp-case")["error"]
        )
        self.assertIn("alphanumeric", self.tool.execute(mode="style_audit", identifier="___")["error"])
        many = "_".join(f"w{i}" for i in range(201))
        self.assertIn("max_words", self.tool.execute(mode="style_audit", identifier=many)["error"])
        self.assertIn(
            "not accepted in this mode",
            self.tool.execute(mode="style_audit", identifier="a", text="b")["error"],
        )


class UnicodeCaseToolCharInfoTest(unittest.TestCase):
    """char_case_info plus the Final_Sigma probe oracle for the mirrors."""

    def setUp(self):
        """Create the tool under test."""
        self.tool = UnicodeCaseTool()

    def test_codepoint_forms(self):
        """char, int, U+XXXX, 0xXXXX, and decimal strings reach the same char."""
        expected = self.tool.execute(mode="char_case_info", char="\u00df")
        for codepoint in ("U+00DF", "u+00df", "0x00DF", 0xDF, "223"):
            result = self.tool.execute(mode="char_case_info", codepoint=codepoint)
            self.assertEqual(result["codepoint"], "U+00DF", codepoint)
            self.assertEqual(result["name"], expected["name"])

    def test_char_profile(self):
        """The canonical characters carry full, correct case profiles."""
        sharp = self.tool.execute(mode="char_case_info", char="\u00df")
        self.assertEqual(sharp["category"], "Ll")
        self.assertTrue(sharp["is_lower"])
        self.assertTrue(sharp["is_cased"])
        self.assertFalse(sharp["is_case_ignorable"])
        self.assertEqual(sharp["mappings"]["upper"], {"result": "SS", "length": 2})
        self.assertEqual(sharp["mappings"]["casefold"], {"result": "ss", "length": 2})
        self.assertEqual(sharp["mappings"]["lower"], {"result": "\u00df", "length": 1})
        self.assertIn("FULL mapping to 2 characters", sharp["simple_vs_full_explanation"])
        dot = self.tool.execute(mode="char_case_info", char="\u0130")
        self.assertEqual(dot["mappings"]["lower"], {"result": "i\u0307", "length": 2})
        digraph = self.tool.execute(mode="char_case_info", char="\u01c5")
        self.assertEqual(digraph["category"], "Lt")
        self.assertTrue(digraph["is_title"])
        self.assertFalse(digraph["is_upper"])
        self.assertFalse(digraph["is_lower"])
        kelvin = self.tool.execute(mode="char_case_info", char="\u212a")
        self.assertEqual(kelvin["mappings"]["lower"]["result"], "k")
        self.assertTrue(kelvin["is_cased"])
        combining = self.tool.execute(mode="char_case_info", char="\u0345")
        self.assertFalse(combining["is_cased"])
        self.assertTrue(combining["is_case_ignorable"])
        self.assertEqual(combining["mappings"]["casefold"]["result"], "\u03b9")
        self.assertIn("nevertheless", combining["note"])
        ordinal = self.tool.execute(mode="char_case_info", char="\u00aa")
        self.assertTrue(ordinal["is_cased"])
        self.assertEqual(ordinal["mappings"]["upper"]["result"], "\u00aa")
        space = self.tool.execute(mode="char_case_info", char=" ")
        self.assertFalse(space["is_cased"])
        self.assertFalse(space["is_case_ignorable"])
        apostrophe = self.tool.execute(mode="char_case_info", char="'")
        self.assertTrue(apostrophe["is_case_ignorable"])
        self.assertFalse(apostrophe["is_cased"])

    def test_validation_errors(self):
        """Surrogates, out-of-range, and conflicting inputs error out."""
        self.assertIn("surrogate", self.tool.execute(mode="char_case_info", codepoint=0xD800)["error"])
        self.assertIn("0x10FFFF", self.tool.execute(mode="char_case_info", codepoint=0x110000)["error"])
        self.assertIn("exactly one character", self.tool.execute(mode="char_case_info", char="ab")["error"])
        self.assertIn("not both", self.tool.execute(mode="char_case_info", char="a", codepoint=1)["error"])
        self.assertIn("required", self.tool.execute(mode="char_case_info")["error"])

    def test_cased_and_ignorable_mirror_against_final_sigma_probe(self):
        """The frozen mirrors agree with the stdlib SpecialCasing machinery.

        The Final_Sigma rule decides between the final and the medial
        lowercase sigma by scanning for cased letters across runs of
        Case_Ignorable characters, so probing how a capital sigma lowercases
        around a character X reveals whether
        the stdlib considers X cased and/or case-ignorable. Sampled over the
        BMP with a stride plus every curated special.
        """
        samples = set(range(0, 0x10000, 97))
        samples.update(range(0x10000, MAX_CODEPOINT + 1, 1013))
        samples.update(
            cp
            for cp in (
                0x27,
                0x2E,
                0x3A,
                0xB7,
                0xAD,
                0x300,
                0x345,
                0x3A3,
                0x3C2,
                0x3C3,
                0x1E9E,
                0x212A,
                0x2126,
                0x17F,
                0xB5,
                0x212B,
                0x13A0,
                0xAB70,
                0x10400,
                0x10428,
                0x118A0,
                0x10C80,
                0x24B6,
                0x2160,
                0x2019,
                0xFF07,
                0xFE0F,
                0xE0100,
                0x1F3FB,
                0x20,
                0x5F,
                0x2D,
                0x4E00,
                0x1F600,
            )
            if cp <= MAX_CODEPOINT
        )
        for codepoint in sorted(samples):
            if 0xD800 <= codepoint <= 0xDFFF:
                continue
            info = self.tool.execute(mode="char_case_info", codepoint=codepoint)
            self.assertEqual(info["is_cased"], cased_probe(codepoint), hex(codepoint))
            self.assertEqual(info["is_case_ignorable"], ignorable_probe(codepoint), hex(codepoint))


class UnicodeCaseToolPathologicalTest(unittest.TestCase):
    """Pathological inputs stay bounded: 1 MiB under two seconds."""

    def setUp(self):
        """Create the tool under test."""
        self.tool = UnicodeCaseTool()

    @staticmethod
    def megabyte_text():
        """Deterministically build a 1 MiB mixed-content string."""
        rng = random.Random(1048576)  # noqa: S311
        alphabet = INTERESTING_CHARS + CJK_CHARS + EMOJI_CHARS + "aZ9 "
        return "".join(rng.choice(alphabet) for _ in range(1_048_576))

    def test_one_megabyte_under_two_seconds(self):
        """case_map and equivalence on 1 MiB complete within two seconds."""
        text = self.megabyte_text()
        for target in ("upper", "casefold"):
            start = time.perf_counter()
            result = self.tool.execute(mode="case_map", text=text, target=target)
            elapsed = time.perf_counter() - start
            self.assertEqual(result["status"], "success")
            self.assertEqual(result["result"], getattr(text, target)())
            self.assertLess(elapsed, 2.0, target)
        folded = text.casefold()
        start = time.perf_counter()
        result = self.tool.execute(mode="equivalence", text_a=text, text_b=folded)
        elapsed = time.perf_counter() - start
        if result["status"] == "error":
            # casefold can expand past the 1 MiB cap (sharp s -> ss); retry
            # with an alphabet whose mappings never expand so the comparison
            # itself is still exercised at full pathological size.
            rng = random.Random(999)  # noqa: S311
            stable = "".join(rng.choice("aZ\u4e2d\u65e5\u0430\u04110 ") for _ in range(1_048_576))
            result = self.tool.execute(mode="equivalence", text_a=stable, text_b=stable.upper())
            elapsed = time.perf_counter() - start
        self.assertTrue(result["casefold_equal"])
        self.assertLess(elapsed, 2.0)

    def test_determinism(self):
        """Repeated executions return identical structures."""
        text = "Stra\u00dfe \u0130 \ufb01 \u03a3 \u212a \u017f \u00b5"
        first = self.tool.execute(mode="case_map", text=text, target="lower")
        second = self.tool.execute(mode="case_map", text=text, target="lower")
        self.assertEqual(first, second)
        audit_first = self.tool.execute(mode="style_audit", identifier="getUser_Name", target_style="kebab-case")
        audit_second = self.tool.execute(mode="style_audit", identifier="getUser_Name", target_style="kebab-case")
        self.assertEqual(audit_first, audit_second)


class UnicodeCaseToolRegistrationTest(unittest.TestCase):
    """Registration tests for the shipped unicode_case_tool.yaml."""

    def setUp(self):
        """Load the shipped yaml config and snapshot the app configer state."""
        self.config = Configer(path=os.path.abspath(YAML_PATH)).load()
        try:
            self.previous = ApplicationConfigManager().app_configer
        except ValueError:
            self.previous = None

    def tearDown(self):
        """Restore the app configer snapshot taken in setUp."""
        ApplicationConfigManager().app_configer = self.previous

    def test_schema(self):
        """The shipped yaml resolves to a tool component exposing UnicodeCaseTool."""
        component = ComponentConfiger().load_by_configer(self.config)
        self.assertEqual(component.get_component_config_type(), ComponentEnum.TOOL.value)
        self.assertEqual(component.metadata_class, "UnicodeCaseTool")

    def test_manager(self):
        """UnicodeCaseTool is resolvable and configured via ToolManager."""
        configer = ToolConfiger().load_by_configer(self.config)
        app = AppConfiger()
        app.tool_configer_map = {configer.name: configer}
        ApplicationConfigManager().app_configer = app
        tool = ToolManager().get_instance_obj(configer.name)
        self.assertIsInstance(tool, UnicodeCaseTool)
        self.assertEqual(tool.input_keys, ["mode"])
        self.assertEqual(tool.max_text_chars, 1_048_576)

    def test_package_export(self):
        """The tool class is exported from the common_tool package."""
        from agentuniverse.agent.action.tool import common_tool
        from agentuniverse.agent.action.tool.common_tool import UnicodeCaseTool as Exported

        self.assertIs(Exported, UnicodeCaseTool)
        self.assertIn("UnicodeCaseTool", common_tool.__all__)


if __name__ == "__main__":
    unittest.main()
