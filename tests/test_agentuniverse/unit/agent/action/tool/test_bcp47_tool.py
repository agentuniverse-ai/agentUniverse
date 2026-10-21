#!/usr/bin/env python3
"""Tests for Bcp47Tool: RFC 5646 oracles, canonicalization battery,
a 500-case property fuzz against an independent structural validator, and
RFC 4647 matching examples."""

import asyncio
import os
import random
import re
import unittest

from agentuniverse.agent.action.tool.common_tool import bcp47_tool as bcp47_module
from agentuniverse.agent.action.tool.common_tool.bcp47_tool import Bcp47Tool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer

YAML_PATH = os.path.join(os.path.dirname(bcp47_module.__file__), "bcp47_tool.yaml")

# ---------------------------------------------------------------------------
# Independent structural validator (RFC 5646 ABNF), used as the fuzz oracle.
# It shares no code with the tool implementation.
# ---------------------------------------------------------------------------

IRREGULAR = {
    "en-gb-oed", "i-ami", "i-bnn", "i-default", "i-enochian", "i-hak",
    "i-klingon", "i-lux", "i-mingo", "i-navajo", "i-pwn", "i-tao", "i-tay",
    "i-tsu", "sgn-be-fr", "sgn-be-nl", "sgn-ch-de",
}
REGULAR = {
    "art-lojban", "cel-gaulish", "no-bok", "no-nyn", "zh-guoyu", "zh-hakka",
    "zh-min", "zh-min-nan", "zh-xiang",
}
GRANDFATHERED_ALL = IRREGULAR | REGULAR

_PRIVATEUSE_RE = re.compile(r"^[xX](-[A-Za-z0-9]{1,8})+$")
_LANGTAG_RE = re.compile(
    r"^[A-Za-z]{2,8}"
    r"(?:-[A-Za-z]{3}){0,3}"
    r"(?:-[A-Za-z]{4})?"
    r"(?:-[A-Za-z]{2}|-\d{3})?"
    r"(?:-(?:[A-Za-z0-9]{5,8}|\d[A-Za-z0-9]{3}))*"
    r"(?:-[0-9A-WY-Za-wy-z](?:-[A-Za-z0-9]{2,8})+)*"
    r"(?:-[xX](?:-[A-Za-z0-9]{1,8})+)?$"
)


def independent_well_formed(tag: str) -> bool:
    """RFC 5646 well-formedness without registry knowledge."""
    if not tag:
        return False
    if tag.lower() in GRANDFATHERED_ALL:
        return True
    if _PRIVATEUSE_RE.match(tag):
        return True
    if not _LANGTAG_RE.match(tag):
        return False
    subtags = tag.split("-")[1:]
    # Everything after the 'x' marker is private use and exempt from the
    # variant/singleton rules below.
    head: list[str] = []
    for part in subtags:
        if len(part) == 1 and part.lower() == "x":
            break
        head.append(part)
    # The same variant MUST NOT occur twice (RFC 5646 section 2.2.5). A
    # singleton consumes its following 2-8 character subtags, which are
    # extension content rather than variants.
    variants: list[str] = []
    singletons: list[str] = []
    index = 0
    while index < len(head):
        part = head[index]
        if len(part) == 1:
            singletons.append(part.lower())
            index += 1
            while index < len(head) and len(head[index]) != 1:
                index += 1
            continue
        if len(part) >= 5 or (len(part) == 4 and part[0].isdigit()):
            variants.append(part.lower())
        index += 1
    if len(set(variants)) != len(variants):
        return False
    # The same extension singleton MUST NOT occur twice (RFC 5646 section 2.2.9).
    if len(set(singletons)) != len(singletons):
        return False
    return True


# ---------------------------------------------------------------------------
# Oracle (a): RFC 5646 syntax examples (section 2.2.1 and in-text examples).
# ---------------------------------------------------------------------------

RFC_WELL_FORMED_VALID = [
    "en", "fr", "de-CH", "en-CA", "hy-Latn-IT-arevela", "de-CH-1901",
    "sl-rozaj-biske", "zh-cmn-Hant", "en-Latn-GB-boont-r-extended-sequence-x-private",
    "en-a-bbb-x-a-ccc", "de-a-value", "mn-Cyrl-MN", "MN-cYRL-mn", "mN-cYrL-Mn",
    "sr-Latn-RS", "az-Arab-IR", "zh-Hant-CN", "en-US", "x-fr-CH", "zh-gan",
    "gan", "yue", "zh-yue", "zh-cmn", "cmn", "sr-Latn", "de-AT", "es-419",
    "sl-nedis", "de-CH-1996", "zh-yue-Hant-HK", "yue-Hant-HK", "nan-Hant",
    "nan-TW", "enochian-AQ", "enochian-Latn", "de-Latf-DE", "de-Latn-DE",
    "de-Deva", "de-DE-x-goethe", "i-klingon", "i-default", "i-enochian",
    "art-lojban", "no-bok", "no-nyn", "sgn-BE-FR", "en-GB-oed", "zh-min-nan",
    "zh-hakka", "x-foo-private",
]

RFC_MALFORMED = [
    "en--US", "a-DE", "a-value", "en-a-bbb-a-ccc", "tlh-a-b-foo",
    "de-DE-1901-1901", "-en", "en-", "e", "1234abc", "en-US-Latn",
    "en-1901-1901", "en-a-b-foo", "x-", "en--", "en US", "e1n",
]

# Well-formed but not valid: grammar passes, registry lookup fails.
WELL_FORMED_UNKNOWN = ["abcd", "abcd-US", "qqa", "en-Qqqq-GB", "en-1234", "zzz-GB"]

# ---------------------------------------------------------------------------
# Oracle (b): curated known-good canonicalization pairs (60).
# ---------------------------------------------------------------------------

CANONICAL_PAIRS = [
    ("in", "id"), ("iw", "he"), ("ji", "yi"), ("jw", "jv"), ("mo", "ro"),
    ("in-US", "id-US"), ("IW-us", "he-US"), ("en", "en"), ("EN", "en"),
    ("en-latn", "en-Latn"), ("EN-us", "en-US"), ("de-ch", "de-CH"),
    ("zh-cmn-Hant", "cmn-Hant"), ("zh-yue-Hant-HK", "yue-Hant-HK"),
    ("zh-Hans-CN", "zh-Hans-CN"), ("i-klingon", "tlh"), ("art-lojban", "jbo"),
    ("en-GB-oed", "en-GB-oxendict"), ("no-bok", "nb"), ("no-nyn", "nn"),
    ("zh-min-nan", "nan"), ("zh-hakka", "hak"), ("zh-xiang", "hsn"),
    ("i-lux", "lb"), ("i-navajo", "nv"), ("i-ami", "ami"), ("i-bnn", "bnn"),
    ("i-pwn", "pwn"), ("i-tao", "tao"), ("i-tay", "tay"), ("i-tsu", "tsu"),
    ("i-hak", "hak"), ("sgn-BE-FR", "sfb"), ("sgn-BE-NL", "vgt"),
    ("sgn-CH-DE", "sgg"), ("cel-gaulish", "xtg-x-cel-gaulish"),
    ("sh", "sr-Latn"), ("sh-IT", "sr-Latn-IT"), ("sh-Cyrl", "sr-Cyrl"),
    ("tl", "fil"), ("scc", "sr"), ("scr", "hr"), ("en-UK", "en-GB"),
    ("en-BU", "en-MM"), ("fr-ZR", "fr-CD"), ("de-TP", "de-TL"),
    ("es-FX", "es-FR"), ("MN-cYRL-mn", "mn-Cyrl-MN"),
    ("en-Latn-GB-boont-r-extended-sequence-x-private",
     "en-Latn-GB-boont-r-extended-sequence-x-private"),
    ("ja-Latn-heploc", "ja-Latn-alalc97"),
    ("en-u-ca-buddhist-t-t0-m0", "en-t-t0-m0-u-ca-buddhist"),
    ("SL-ROZAJ-BISKE", "sl-rozaj-biske"), ("ZH-hant", "zh-Hant"),
    ("en-gb-oed", "en-GB-oxendict"), ("sl-rozaj-biske-1994", "sl-rozaj-biske-1994"),
    ("nan-TW", "nan-TW"), ("de-Deva-DE", "de-Deva-DE"), ("es-419", "es-419"),
    ("und", "und"), ("nb", "nb"),
]


# ---------------------------------------------------------------------------
# Oracle (c): 500-case seeded property fuzz.
# ---------------------------------------------------------------------------

def _build_fuzz_cases() -> list[str]:
    rng = random.Random(20261021)
    languages = sorted(bcp47_module.LANGUAGES)
    scripts = sorted(bcp47_module.SCRIPTS)
    regions = sorted(bcp47_module.REGIONS)
    variants = sorted(bcp47_module.VARIANTS)
    extlangs_by_prefix: dict[str, list[str]] = {}
    for code, entry in bcp47_module.EXTLANGS.items():
        extlangs_by_prefix.setdefault(entry["prefix"], []).append(code)
    alphabet = "abcdefghijklmnopqrstuvwxyz0123456789"

    def extension_subtag() -> str:
        return "".join(rng.choice(alphabet) for _ in range(rng.randint(2, 8)))

    def private_subtag() -> str:
        return "".join(rng.choice(alphabet) for _ in range(rng.randint(1, 8)))

    valid_cases: list[str] = []
    for _ in range(280):
        parts = [rng.choice(languages)]
        if rng.random() < 0.2:
            options = extlangs_by_prefix.get(parts[0], [])
            if options:
                parts.append(rng.choice(options))
        if rng.random() < 0.35:
            parts.append(rng.choice(scripts))
        if rng.random() < 0.35:
            parts.append(rng.choice(regions))
        for variant in rng.sample(variants, min(len(variants), rng.randint(0, 2))):
            parts.append(variant)
        if rng.random() < 0.2:
            singleton = rng.choice(["u", "t"])
            parts.append(singleton)
            for _ in range(rng.randint(1, 3)):
                parts.append(extension_subtag())
        if rng.random() < 0.12:
            parts.append("x")
            for _ in range(rng.randint(1, 3)):
                parts.append(private_subtag())
        valid_cases.append("-".join(parts))

    mutated: list[str] = []
    mutations = 220
    for i in range(mutations):
        base = list(rng.choice(valid_cases).split("-"))
        kind = i % 11
        if kind == 0:  # case games must not change verdicts
            mutated.append(rng.choice([str.upper, str.lower])(rng.choice(valid_cases)))
            continue
        if kind == 1:  # 1-character language subtag
            base[0] = rng.choice("abq")
        elif kind == 2:  # 4-letter (reserved) language subtag
            base[0] = "abcd"
        elif kind == 3:  # 9-character subtag in variant position
            base.append("abcdefghi")
        elif kind == 4:  # unknown language code
            base[0] = "qqa"
        elif kind == 5:  # unknown region
            base.insert(1, "ZZ")
        elif kind == 6:  # misplaced script after region
            base.append("Latn")
        elif kind == 7:  # empty subtag
            base.insert(1, "")
        elif kind == 8:  # dangling singleton
            base.extend(["b", "foo"])
        elif kind == 9:  # multiple extensions, unknown singletons
            base.extend(["s", "cal", "z", "ext"])
        else:  # duplicate variant
            variant = [p for p in base if len(p) >= 5]
            base.append(variant[0] if variant else "rozaj")
        mutated.append("-".join(base))
    return valid_cases + mutated


FUZZ_CASES = _build_fuzz_cases()


class Bcp47ValidateOracleTest(unittest.TestCase):
    """Oracle (a): classify the RFC's own example tags."""

    def setUp(self):
        self.tool = Bcp47Tool()

    def test_rfc_examples_are_valid(self):
        for tag in RFC_WELL_FORMED_VALID:
            result = self.tool.execute(mode="validate", tag=tag)
            self.assertTrue(result["well_formed"], tag)
            self.assertTrue(result["valid"], f"{tag}: {result['errors']}")
            self.assertEqual(result["errors"], [], tag)

    def test_rfc_malformed_examples(self):
        for tag in RFC_MALFORMED:
            result = self.tool.execute(mode="validate", tag=tag)
            self.assertFalse(result["well_formed"], tag)
            self.assertFalse(result["valid"], tag)
            self.assertTrue(result["errors"], tag)

    def test_well_formed_but_unknown(self):
        for tag in WELL_FORMED_UNKNOWN:
            result = self.tool.execute(mode="validate", tag=tag)
            self.assertTrue(result["well_formed"], tag)
            self.assertFalse(result["valid"], tag)

    def test_structure_decomposition(self):
        result = self.tool.execute(mode="validate", tag="en-Latn-GB-boont-r-extended-sequence-x-private")
        structure = result["structure"]
        self.assertEqual(structure["lang"], "en")
        self.assertEqual(structure["script"], "Latn")
        self.assertEqual(structure["region"], "GB")
        self.assertEqual(structure["variants"], ["boont"])
        self.assertEqual(structure["extensions"][0]["singleton"], "r")
        self.assertEqual(structure["extensions"][0]["subtags"], ["extended", "sequence"])
        self.assertEqual(structure["privateuse"], "x-private")

    def test_error_spans(self):
        result = self.tool.execute(mode="validate", tag="en--US")
        spans = {(error["code"], tuple(error["span"])) for error in result["errors"]}
        self.assertIn(("empty_subtag", (3, 3)), spans)
        result = self.tool.execute(mode="validate", tag="a-DE")
        self.assertEqual(result["errors"][0]["code"], "language_shape")
        self.assertEqual(result["errors"][0]["span"], [0, 1])
        result = self.tool.execute(mode="validate", tag="en-US-Latn")
        misplaced = [e for e in result["errors"] if e["subtag"] == "Latn"]
        self.assertEqual(misplaced[0]["span"], [6, 10])

    def test_warnings(self):
        result = self.tool.execute(mode="validate", tag="en-Latn")
        codes = {warning["code"] for warning in result["warnings"]}
        self.assertIn("suppressed_script", codes)
        result = self.tool.execute(mode="validate", tag="i-klingon")
        codes = {warning["code"] for warning in result["warnings"]}
        self.assertIn("grandfathered_deprecated", codes)
        result = self.tool.execute(mode="validate", tag="in")
        codes = {warning["code"] for warning in result["warnings"]}
        self.assertIn("deprecated_subtag", codes)
        self.assertIn("case_form", codes)

    def test_grandfathered_structure(self):
        result = self.tool.execute(mode="validate", tag="i-klingon")
        self.assertEqual(result["type"], "grandfathered")
        self.assertTrue(result["valid"])
        self.assertEqual(result["canonical"], "tlh")


class Bcp47CanonicalizeTest(unittest.TestCase):
    """Oracle (b): curated known-good canonicalization battery."""

    def setUp(self):
        self.tool = Bcp47Tool()

    def test_battery(self):
        for source, expected in CANONICAL_PAIRS:
            result = self.tool.execute(mode="canonicalize", tag=source)
            self.assertEqual(result["status"], "ok", source)
            self.assertEqual(result["canonical"], expected, source)

    def test_idempotent(self):
        for source, _expected in CANONICAL_PAIRS:
            first = self.tool.execute(mode="canonicalize", tag=source)["canonical"]
            second = self.tool.execute(mode="canonicalize", tag=first)["canonical"]
            self.assertEqual(first, second, source)

    def test_notes_are_quotable(self):
        result = self.tool.execute(mode="canonicalize", tag="zh-cmn-Hant")
        self.assertTrue(any("folded extlang" in note for note in result["notes"]))
        result = self.tool.execute(mode="canonicalize", tag="in")
        self.assertTrue(any("preferred value 'id'" in note for note in result["notes"]))

    def test_malformed_tag_rejected(self):
        result = self.tool.execute(mode="canonicalize", tag="en--US")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "invalid_tag")


class Bcp47FuzzTest(unittest.TestCase):
    """Oracle (c): 500 seeded tags cross-checked against an independent
    structural validator, plus canonicalization idempotence."""

    def setUp(self):
        self.tool = Bcp47Tool()

    def test_500_cases_against_independent_validator(self):
        self.assertEqual(len(FUZZ_CASES), 500)
        checked = 0
        for tag in FUZZ_CASES:
            result = self.tool.execute(mode="validate", tag=tag)
            expected = independent_well_formed(tag)
            self.assertEqual(
                result["well_formed"], expected, f"{tag}: tool={result['well_formed']} oracle={expected}"
            )
            if expected:
                canonical = result["canonical"]
                self.assertTrue(canonical, tag)
                recheck = self.tool.execute(mode="validate", tag=canonical)
                self.assertTrue(recheck["well_formed"], (tag, canonical))
                again = self.tool.execute(mode="canonicalize", tag=canonical)["canonical"]
                self.assertEqual(canonical, again, tag)
                checked += 1
        self.assertGreater(checked, 200)

    def test_valid_walks_are_valid(self):
        generated = FUZZ_CASES[:280]
        for tag in generated:
            result = self.tool.execute(mode="validate", tag=tag)
            self.assertTrue(result["well_formed"], tag)
            self.assertTrue(result["valid"], f"{tag}: {result['errors']}")


class Bcp47MatchTest(unittest.TestCase):
    """Oracle (d): RFC 4647 section 3.3/3.4 examples."""

    def setUp(self):
        self.tool = Bcp47Tool()

    def test_basic_filtering_examples(self):
        # RFC 4647 section 3.3.1: 'de-de' matches 'de-DE-1996'...
        result = self.tool.execute(mode="match", tag="de-DE-1996", range="de-de")
        self.assertEqual(result["mechanism"], "filtering")
        self.assertEqual(result["matched"], "de-DE-1996")
        self.assertEqual(result["first_match"], 0)
        # ...but not 'de-Deva' or 'de-Latn-DE' (prefix must respect subtags).
        for tag in ("de-Deva", "de-Latn-DE"):
            result = self.tool.execute(mode="match", tag=tag, range="de-de")
            self.assertIsNone(result["matched"], tag)
        # Basic filtering also matches subtag-boundary prefixes.
        result = self.tool.execute(mode="match", tag="de-DE-x-goethe", range="de-de")
        self.assertEqual(result["matched"], "de-DE-x-goethe")

    def test_wildcard_matches_non_empty(self):
        result = self.tool.execute(mode="match", tag="de", range="*")
        self.assertEqual(result["matched"], "de")
        self.assertEqual(result["matched_via"], "*")

    def test_lookup_truncation_examples(self):
        # RFC 4647 section 3.4: range 'de-ch' yields 'de' or 'de-CH', never
        # 'de-CH-1996'.
        self.assertEqual(
            self.tool.execute(mode="match", tag="de", range="de-ch", mechanism="lookup")["matched"],
            "de",
        )
        self.assertEqual(
            self.tool.execute(mode="match", tag="de-CH", range="de-ch", mechanism="lookup")["matched"],
            "de-CH",
        )
        self.assertIsNone(
            self.tool.execute(mode="match", tag="de-CH-1996", range="de-ch", mechanism="lookup")["matched"]
        )

    def test_lookup_progressive_truncation(self):
        chain = "zh-Hant-CN-x-private1-private2"
        for tag in ("zh-Hant-CN", "zh-Hant", "zh"):
            result = self.tool.execute(mode="match", tag=tag, range=chain, mechanism="lookup")
            self.assertEqual(result["matched"], tag, tag)
            self.assertEqual(result["matched_via"], tag)
        self.assertIsNone(
            self.tool.execute(mode="match", tag="zh-Hans", range=chain, mechanism="lookup")["matched"]
        )

    def test_lookup_priority_list(self):
        result = self.tool.execute(mode="match", tag="zh-Hant", range="fr-FR, zh-Hant")
        self.assertEqual(result["mechanism"], "lookup")
        self.assertEqual(result["matched"], "zh-Hant")
        self.assertEqual(result["first_match"], 1)
        result = self.tool.execute(mode="match", tag="fr", range="fr-FR, zh-Hant")
        self.assertEqual(result["matched"], "fr")
        self.assertEqual(result["first_match"], 0)

    def test_lookup_skips_wildcard(self):
        result = self.tool.execute(mode="match", tag="de", range="*, de", mechanism="lookup")
        self.assertEqual(result["matched"], "de")
        self.assertEqual(result["first_match"], 1)

    def test_case_insensitive(self):
        result = self.tool.execute(mode="match", tag="FR-fr", range="fr-FR")
        self.assertEqual(result["matched"], "FR-fr")
        result = self.tool.execute(mode="match", tag="FR", range="fr-FR, zh", mechanism="lookup")
        self.assertEqual(result["matched"], "FR")

    def test_notes_are_quotable(self):
        result = self.tool.execute(mode="match", tag="de-DE-1996", range="de-de")
        self.assertTrue(any("RFC 4647" in note for note in result["notes"]))
        self.assertTrue(any("prefix" in note for note in result["notes"]))


class Bcp47ExplainTest(unittest.TestCase):
    """Explain mode breakdowns."""

    def setUp(self):
        self.tool = Bcp47Tool()

    def test_fr_ca(self):
        result = self.tool.execute(mode="explain", tag="fr-CA")
        self.assertIn("French", result["summary"])
        self.assertIn("Canada", result["summary"])
        types = [(row["type"], row["description"]) for row in result["breakdown"]]
        self.assertIn(("language", "French"), types)
        self.assertIn(("region", "Canada"), types)

    def test_grandfathered_explain(self):
        result = self.tool.execute(mode="explain", tag="i-klingon")
        self.assertEqual(result["canonical"], "tlh")
        self.assertIn("tlh", result["related_tags"])

    def test_related_tags(self):
        result = self.tool.execute(mode="explain", tag="en")
        self.assertTrue(any(tag.startswith("en-") for tag in result["related_tags"]))


class Bcp47InterfaceTest(unittest.TestCase):
    """Mode dispatch, validation errors, determinism, and async parity."""

    def setUp(self):
        self.tool = Bcp47Tool()

    def test_invalid_mode(self):
        result = self.tool.execute(mode="polish", tag="en")
        self.assertEqual(result["status"], "error")

    def test_rejects_empty_and_list_tags(self):
        self.assertEqual(self.tool.execute(mode="validate", tag="")["status"], "error")
        self.assertEqual(self.tool.execute(mode="validate", tag="en, fr")["status"], "error")
        self.assertEqual(self.tool.execute(mode="validate", tag=None)["status"], "error")

    def test_match_requires_range(self):
        self.assertEqual(self.tool.execute(mode="match", tag="en", range="")["status"], "error")
        self.assertEqual(self.tool.execute(mode="match", tag="en", range=None)["status"], "error")
        self.assertEqual(
            self.tool.execute(mode="match", tag="en", range="en", mechanism="grok")["status"],
            "error",
        )

    def test_tag_length_cap(self):
        self.assertEqual(self.tool.execute(mode="validate", tag="en" + "-x" * 400)["status"], "error")

    def test_deterministic(self):
        first = self.tool.execute(mode="validate", tag="zh-cmn-Hant-CN")
        second = self.tool.execute(mode="validate", tag="zh-cmn-Hant-CN")
        self.assertEqual(first, second)

    def test_async_matches_sync(self):
        sync = self.tool.execute(mode="validate", tag="hy-Latn-IT-arevela")
        async_result = asyncio.run(self.tool.async_execute(mode="validate", tag="hy-Latn-IT-arevela"))
        self.assertEqual(sync, async_result)

    def test_table_sizes(self):
        self.assertGreaterEqual(len(bcp47_module.LANGUAGES), 390)
        self.assertGreaterEqual(len(bcp47_module.REGIONS), 250)
        self.assertGreaterEqual(len(bcp47_module.SCRIPTS), 150)
        self.assertGreaterEqual(len(bcp47_module.VARIANTS), 40)
        self.assertEqual(len(bcp47_module.GRANDFATHERED), 26)
        self.assertGreaterEqual(len(bcp47_module.EXTLANGS), 15)

    def test_tables_are_frozen(self):
        with self.assertRaises(TypeError):
            bcp47_module.LANGUAGES["qqq"] = "injected"


class Bcp47RegistrationTest(unittest.TestCase):
    """Unit tests for registering the shipped bcp47_tool.yaml as a tool."""

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
        self.assertEqual(component.metadata_class, "Bcp47Tool")

    def test_manager(self):
        configer = ToolConfiger().load_by_configer(self.config)
        app = AppConfiger()
        app.tool_configer_map = {configer.name: configer}
        ApplicationConfigManager().app_configer = app
        tool = ToolManager().get_instance_obj(configer.name)
        self.assertIsInstance(tool, Bcp47Tool)
        self.assertEqual(tool.input_keys, ["mode", "tag"])

    def test_package_export(self):
        from agentuniverse.agent.action.tool.common_tool import Bcp47Tool as Exported
        self.assertIs(Exported, Bcp47Tool)


if __name__ == "__main__":
    unittest.main()
