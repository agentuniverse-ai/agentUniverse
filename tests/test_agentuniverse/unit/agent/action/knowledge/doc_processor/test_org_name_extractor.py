# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @FileName: test_org_name_extractor.py

import unittest

from agentuniverse.agent.action.knowledge.doc_processor.org_name_extractor import OrgNameExtractor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer


def _doc(text: str, **metadata) -> Document:
    """Build a Document carrying `text` and optional metadata."""
    return Document(text=text, metadata=dict(metadata) or None)


def _names(doc: Document) -> list:
    """Extract the stamped organization names of one document."""
    return [entry["name"] for entry in doc.metadata["organizations"]]


class TestOrgNameExtractor(unittest.TestCase):
    """Comprehensive test suite for OrgNameExtractor."""

    def setUp(self):
        self.extractor = OrgNameExtractor()
        self.query = Query(query_str="supplier onboarding")

    def _create_configer(self, config_dict):
        """Create a ComponentConfiger from a plain dictionary."""
        cfg = Configer()
        cfg.value = config_dict
        configer = ComponentConfiger()
        configer.load_by_configer(cfg)
        return configer

    # ========== Initialization tests ==========

    def test_default_configuration(self):
        """Defaults: cap 50, 'organizations' and 'org_count' keys."""
        extractor = OrgNameExtractor()
        self.assertEqual(extractor.max_orgs, 50)
        self.assertEqual(extractor.organizations_key, "organizations")
        self.assertEqual(extractor.count_key, "org_count")

    def test_initialize_by_component_configer(self):
        """YAML-provided parameters are applied on initialization."""
        configer = self._create_configer({
            'name': 'org_name_extractor',
            'description': 'org name extractor',
            'max_orgs': 5,
            'organizations_key': 'orgs',
            'count_key': 'org_total',
        })
        extractor = OrgNameExtractor()
        extractor._initialize_by_component_configer(configer)
        self.assertEqual(extractor.max_orgs, 5)
        self.assertEqual(extractor.organizations_key, "orgs")
        self.assertEqual(extractor.count_key, "org_total")
        self.assertEqual(extractor.name, "org_name_extractor")

    def test_invalid_configuration_raises(self):
        """Non-integer / out-of-range cap and non-string keys fail at
        load time."""
        base = {
            'name': 'e', 'description': 'd',
            'max_orgs': 10, 'organizations_key': 'organizations',
            'count_key': 'org_count',
        }
        for key, value in (
            ('max_orgs', 0),
            ('max_orgs', -3),
            ('max_orgs', 1.5),
            ('max_orgs', True),
            ('max_orgs', 'x'),
            ('organizations_key', 5),
            ('organizations_key', ['x']),
            ('count_key', 7),
            ('count_key', None.__class__),
        ):
            config = dict(base, **{key: value})
            with self.assertRaises(ValueError, msg=f"{key}={value!r}"):
                OrgNameExtractor()._initialize_by_component_configer(
                    self._create_configer(config))

    # ========== English extraction tests ==========

    def test_basic_en_suffixes(self):
        """Single-word names with the classic legal-form suffixes, plus
        multi-word 'of' names, all extracted with the suffix inside the
        name."""
        text = ("Bank of America Corp reported earnings; Siemens AG and "
                "Bosch GmbH rose.")
        doc = _doc(text)
        result = self.extractor.process_docs([doc], self.query)
        self.assertEqual(_names(doc), ["Bank of America Corp",
                                       "Siemens AG", "Bosch GmbH"])
        self.assertEqual(result, [doc])

    def test_ampersand_joins_and_suffix_with_period(self):
        """'&' joins inside names, 'Inc.'/'Co.' with period, '&' inside
        one token (AT&T) and a digit-leading word (3M)."""
        cases = {
            "Johnson & Johnson Inc. recalled the product.":
                ["Johnson & Johnson Inc."],
            "Procter & Gamble Co. raised prices.": ["Procter & Gamble Co."],
            "AT&T Inc and 3M Company joined the index.":
                ["AT&T Inc", "3M Company"],
            "McKinsey & Company advised.":
                ["McKinsey & Company"],
        }
        for text, expected in cases.items():
            doc = _doc(text)
            self.extractor.process_docs([doc], self.query)
            self.assertEqual(_names(doc), expected, text)

    def test_leading_article_trimmed(self):
        """'The' is trimmed off the stamped name and the span still
        addresses exactly the trimmed name in the original text."""
        text = "The ACME Widget & Tool Corporation shipped the parts."
        doc = _doc(text)
        self.extractor.process_docs([doc], self.query)
        self.assertEqual(_names(doc), ["ACME Widget & Tool Corporation"])
        start, end = doc.metadata["organizations"][0]["span"]
        self.assertEqual(text[start:end], "ACME Widget & Tool Corporation")
        self.assertFalse(doc.metadata["organizations"][0]
                         ["name"].startswith("The "))

    def test_generic_word_suffixes(self):
        """Group / Holdings / Partners / Labs / Technologies /
        Industries / Company act as suffixes after capitalized names."""
        text = ("Foo Labs, Acme Industries, X Technologies, Y Holdings "
                "and Z Partners joined.")
        doc = _doc(text)
        self.extractor.process_docs([doc], self.query)
        self.assertEqual(_names(doc), ["Foo Labs", "Acme Industries",
                                       "X Technologies", "Y Holdings",
                                       "Z Partners"])
        self.assertEqual(doc.metadata["org_count"], 5)

    def test_all_caps_suffix_variant(self):
        """Fully upper-cased suffixes in headline prose are matched."""
        doc = _doc("BAYER AG and SIEMENS GMBH PUBLISHED FIGURES.")
        self.extractor.process_docs([doc], self.query)
        self.assertEqual(_names(doc), ["BAYER AG", "SIEMENS GMBH"])

    def test_multi_suffix_chain_captured_whole(self):
        """Consecutive suffix words collapse into one name ending at the
        last suffix rather than truncating mid-chain."""
        doc = _doc("X Corporation Group Holdings is a chain.")
        self.extractor.process_docs([doc], self.query)
        self.assertEqual(_names(doc), ["X Corporation Group Holdings"])

    # ========== Guard tests (English) ==========

    def test_bare_suffix_not_matched(self):
        """A suffix without at least one leading name character never
        matches."""
        for text in (
            "Inc. is short for Incorporated.",
            "Corp. and Ltd. are suffixes.",
            "Co. kitchen was closed.",
        ):
            doc = _doc(text)
            self.extractor.process_docs([doc], self.query)
            self.assertEqual(doc.metadata["organizations"], [], text)
            self.assertEqual(doc.metadata["org_count"], 0, text)

    def test_article_only_head_rejected(self):
        """A head consisting of nothing but the article is not a name:
        'The Corporation announced...' and 'A Corp ...' yield nothing."""
        for text in (
            "The Corporation announced record earnings yesterday.",
            "The Group met yesterday to discuss fees.",
            "A Corp announced a merger.",
        ):
            doc = _doc(text)
            self.extractor.process_docs([doc], self.query)
            self.assertEqual(doc.metadata["organizations"], [], text)

    def test_article_fallback_before_connector(self):
        """Trimming may not leave a connector in front ('A & B Corp'
        must not become '& B Corp'), so the article is kept instead."""
        doc = _doc("A & B Corp announced a merger.")
        self.extractor.process_docs([doc], self.query)
        self.assertEqual(_names(doc), ["A & B Corp"])

    def test_lowercase_suffix_not_matched(self):
        """English suffixes are capitalization-sensitive: a lowercase
        mid-sentence 'inc'/'corp' never fires, only the capitalized
        spelling does."""
        doc = _doc("the company inc. filed a complaint about the acme "
                   "corp account.")
        self.extractor.process_docs([doc], self.query)
        self.assertEqual(doc.metadata["organizations"], [])

        doc = _doc("Apple Inc. shipped; later Apple Inc. shipped again.")
        self.extractor.process_docs([doc], self.query)
        self.assertEqual(_names(doc), ["Apple Inc."])

    def test_suffix_word_boundary(self):
        """'Corporation' does not fire inside 'Incorporated', 'Company'
        not inside 'Companies'; the exact forms do fire."""
        doc = _doc("Tyler Incorporated and Anderson Companies declined.")
        self.extractor.process_docs([doc], self.query)
        self.assertEqual(doc.metadata["organizations"], [])

        doc = _doc("Anderson Company settled the dispute.")
        self.extractor.process_docs([doc], self.query)
        self.assertEqual(_names(doc), ["Anderson Company"])

    def test_suffix_less_names_not_extracted(self):
        """The extractor is suffix-driven by design: 'IBM', 'Google' and
        a bare 'Johnson & Johnson' without any suffix anchor are not
        organizations in its eyes."""
        for text in (
            "IBM and Google declined to comment.",
            "Johnson & Johnson announced results.",
        ):
            doc = _doc(text)
            self.extractor.process_docs([doc], self.query)
            self.assertEqual(doc.metadata["organizations"], [], text)

    # ========== Guard tests (masking) ==========

    def test_no_match_inside_urls_or_emails(self):
        """URLs and emails are blanked before matching, so suffixes
        inside addresses never surface as mentions."""
        for text in (
            "Download https://example.com/files/Bayer AG report.pdf today.",
            "see https://zh.wikipedia.org/wiki/大众集团 for details.",
            "contact careers@AcmeCorp.com for the role.",
        ):
            doc = _doc(text)
            self.extractor.process_docs([doc], self.query)
            self.assertEqual(doc.metadata["organizations"], [], text)

    def test_mask_preserves_offsets_and_orgs_after_mask(self):
        """Masking keeps length (spans stay valid) and leaves later
        genuine mentions intact."""
        text = ("Visit www.bayer.com or email press@bayer-ag.de; "
                "Bayer AG rose.")
        masked = OrgNameExtractor._mask(text)
        self.assertEqual(len(masked), len(text))
        self.assertNotIn("bayer.com", masked)
        self.assertNotIn("bayer-ag.de", masked)
        self.assertIn("Bayer AG rose", masked)

        doc = _doc(text)
        self.extractor.process_docs([doc], self.query)
        self.assertEqual(_names(doc), ["Bayer AG"])

    def test_mask_uses_placeholder_not_whitespace(self):
        """The placeholder is NUL, not a space, so a capitalized word
        cannot glue itself to a suffix across a blanked URL."""
        masked = OrgNameExtractor._mask("Download https://a.io/x AG now")
        self.assertIn("\x00", masked)
        doc = _doc("Download https://a.io/x AG now.")
        self.extractor.process_docs([doc], self.query)
        self.assertEqual(doc.metadata["organizations"], [])

    # ========== Chinese extraction tests ==========

    def test_zh_company_suffixes_with_region_parens(self):
        """有限公司 anchored names, including region segments in full-
        width parens and a (集团) segment inside the name."""
        cases = {
            "华为技术有限公司今日发布公告。": ["华为技术有限公司"],
            "甲骨文（中国）软件系统有限公司注册于北京。":
                ["甲骨文（中国）软件系统有限公司"],
            "中国平安保险（集团）股份有限公司挂牌。":
                ["中国平安保险（集团）股份有限公司"],
            "华为技术有限公司的总部位于深圳。": ["华为技术有限公司"],
        }
        for text, expected in cases.items():
            doc = _doc(text)
            self.extractor.process_docs([doc], self.query)
            self.assertEqual(_names(doc), expected, text)

    def test_zh_longest_suffix_first(self):
        """股份有限公司 wins over the 有限公司 it contains, producing
        one full-span entry rather than two."""
        doc = _doc("平安银行股份有限公司发布年报。")
        self.extractor.process_docs([doc], self.query)
        self.assertEqual(_names(doc), ["平安银行股份有限公司"])
        self.assertEqual(doc.metadata["org_count"], 1)

    def test_zh_group_banks_securities_funds(self):
        """集团 / 银行 / 证券 / 基金 anchors, comma-separated without
        conjunction absorption."""
        doc = _doc("中信证券、招商银行双双发布公告，中国建筑集团、华夏基金回应。")
        self.extractor.process_docs([doc], self.query)
        self.assertEqual(_names(doc), ["中信证券", "招商银行",
                                       "中国建筑集团", "华夏基金"])

    def test_zh_universities_and_institutes(self):
        """大学 / 学院 / 研究院 / 研究所 anchors."""
        doc = _doc("北京大学派员出席；中国科学院物理研究所供稿。")
        self.extractor.process_docs([doc], self.query)
        self.assertEqual(_names(doc), ["北京大学", "中国科学院物理研究所"])

    def test_zh_interpunct_joins(self):
        """U+00B7 and U+2022 interpuncts join CJK runs of transliterated
        names such as 路威·酩轩集团."""
        for dot in ("\u00b7", "\u2022"):
            text = f"路威{dot}酩轩集团完成收购。"
            doc = _doc(text)
            self.extractor.process_docs([doc], self.query)
            self.assertEqual(_names(doc), [f"路威{dot}酩轩集团"])

    def test_zh_compound_tail_guard(self):
        """Suffixes followed by a word-continuation character are not
        organizations: 大学生, 银行卡, 基金会, 证券化 are compounds."""
        for text in (
            "他是一名大学生。",
            "先去办理银行卡和网银。",
            "中国红十字基金会接受了捐赠。",
            "资产证券化速度加快。",
        ):
            doc = _doc(text)
            self.extractor.process_docs([doc], self.query)
            self.assertEqual(doc.metadata["organizations"], [], text)

    def test_zh_sentence_after_suffix_allowed(self):
        """Characters that merely continue the sentence (的, verbs) do
        not block the suffix."""
        doc = _doc("清华大学培养了三位院士。")
        self.extractor.process_docs([doc], self.query)
        self.assertEqual(_names(doc), ["清华大学"])

    def test_zh_contiguous_run_absorption_documented(self):
        """Documented trade-off of the contiguous-run design: in scripts
        without word separators the run extends to the previous non-CJK
        boundary, so prose abutting a mention is absorbed into it. Run
        the extractor after a splitter for boundary-clean input."""
        doc = _doc("清华大学与中国科学院物理研究所合作。")
        self.extractor.process_docs([doc], self.query)
        self.assertEqual(_names(doc), ["清华大学与中国科学院物理研究所"])

    def test_mixed_script_ordered_by_span(self):
        """Chinese and English mentions in one document come out ordered
        by their position in the text."""
        text = "苹果公司和美国 Apple Inc.同步发布。"
        doc = _doc(text)
        self.extractor.process_docs([doc], self.query)
        self.assertEqual(_names(doc), ["苹果公司", "Apple Inc."])
        spans = [e["span"] for e in doc.metadata["organizations"]]
        self.assertEqual(spans, sorted(spans))
        self.assertLess(spans[0][0], spans[1][0])

    # ========== Dedup / cap / span tests ==========

    def test_dedup_case_insensitive_first_spelling_wins(self):
        """'APPLE INC.' deduplicates against 'Apple Inc.' keeping the
        first spelling and the first span; Chinese repeats dedupe too."""
        doc = _doc("Apple Inc. announced results. APPLE INC. shares rose.")
        self.extractor.process_docs([doc], self.query)
        self.assertEqual(_names(doc), ["Apple Inc."])
        self.assertEqual(doc.metadata["org_count"], 1)
        start, _ = doc.metadata["organizations"][0]["span"]
        self.assertEqual(start, 0)

        doc = _doc("华为集团宣布，华为集团确认。")
        self.extractor.process_docs([doc], self.query)
        self.assertEqual(_names(doc), ["华为集团"])
        self.assertEqual(doc.metadata["org_count"], 1)

    def test_max_orgs_cap(self):
        """The stamped list is capped while org_count keeps the pre-cap
        distinct total, so truncation is detectable."""
        self.extractor.max_orgs = 2
        doc = _doc("Alpha Inc, Beta Corp and Gamma Ltd all reported.")
        self.extractor.process_docs([doc], self.query)
        self.assertEqual(_names(doc), ["Alpha Inc", "Beta Corp"])
        self.assertEqual(doc.metadata["org_count"], 3)

    def test_span_invariants(self):
        """Every entry's span addresses exactly its name in the original
        text; spans are within bounds, sorted and non-overlapping."""
        text = ("The ACME Widget & Tool Corporation met Siemens AG in "
                "北京，华为技术有限公司、中信证券列席。")
        doc = _doc(text)
        self.extractor.process_docs([doc], self.query)
        entries = doc.metadata["organizations"]
        self.assertEqual(_names(doc), ["ACME Widget & Tool Corporation",
                                       "Siemens AG", "华为技术有限公司",
                                       "中信证券"])
        previous_end = -1
        for entry in entries:
            start, end = entry["span"]
            self.assertTrue(0 <= start < end <= len(text))
            self.assertEqual(text[start:end], entry["name"])
            self.assertGreaterEqual(start, previous_end)
            previous_end = end

    # ========== Pipeline-shape tests ==========

    def test_no_org_passthrough(self):
        """A document without organizations passes through with an empty
        list and zero count stamped — distinguishable from 'never ran'."""
        doc = _doc("a plain sentence without any organization here.")
        result = self.extractor.process_docs([doc], self.query)
        self.assertEqual(result, [doc])
        self.assertIs(result[0], doc)
        self.assertEqual(doc.text, "a plain sentence without any "
                         "organization here.")
        self.assertEqual(doc.metadata["organizations"], [])
        self.assertEqual(doc.metadata["org_count"], 0)

    def test_empty_batch(self):
        """An empty batch yields an empty list."""
        self.assertEqual(self.extractor.process_docs([], self.query), [])

    def test_extract_none_and_blank_text(self):
        """The extraction helper tolerates None and blank text."""
        self.assertEqual(OrgNameExtractor()._extract(None), ([], 0))
        self.assertEqual(OrgNameExtractor()._extract(""), ([], 0))
        self.assertEqual(OrgNameExtractor()._extract("   "), ([], 0))

    def test_documents_not_corrupted(self):
        """Text and id are untouched; pre-existing metadata survives;
        stamping writes through a copy rather than mutating the original
        mapping."""
        doc = _doc("Siemens AG won the tender.", source="wire", rank=1)
        original_meta_ref = doc.metadata
        original_id = doc.id

        result = self.extractor.process_docs([doc], self.query)

        self.assertEqual(result, [doc])
        self.assertEqual(doc.text, "Siemens AG won the tender.")
        self.assertEqual(doc.id, original_id)
        self.assertEqual(doc.metadata["source"], "wire")
        self.assertEqual(doc.metadata["rank"], 1)
        self.assertEqual(doc.metadata["org_count"], 1)
        self.assertNotIn("organizations", original_meta_ref)
        self.assertIsNot(doc.metadata, original_meta_ref)

    def test_disabled_keys_stamp_nothing(self):
        """Empty organizations_key / count_key disable both stamps."""
        self.extractor.organizations_key = ""
        self.extractor.count_key = ""
        doc = _doc("Siemens AG won the tender.", source="wire")
        result = self.extractor.process_docs([doc], self.query)
        self.assertEqual(result, [doc])
        self.assertEqual(doc.metadata, {"source": "wire"})

    def test_custom_keys_honored(self):
        """Custom metadata keys are used for both stamps."""
        self.extractor.organizations_key = "orgs"
        self.extractor.count_key = "org_total"
        doc = _doc("Siemens AG won the tender.")
        self.extractor.process_docs([doc], self.query)
        self.assertNotIn("organizations", doc.metadata)
        self.assertEqual(doc.metadata["org_total"], 1)
        self.assertEqual(doc.metadata["orgs"][0]["name"], "Siemens AG")

    def test_deterministic_and_repeatable(self):
        """Two instances and two consecutive runs produce byte-identical
        metadata; a fresh run over the same text is stable."""
        text = ("The ACME Widget & Tool Corporation met Siemens AG and "
                "华为技术有限公司 in Shanghai.")
        first, second = _doc(text), _doc(text)
        self.extractor.process_docs([first], self.query)
        self.extractor.process_docs([first], self.query)
        OrgNameExtractor().process_docs([second], self.query)
        self.assertEqual(first.metadata["organizations"],
                         second.metadata["organizations"])
        self.assertEqual(first.metadata["org_count"],
                         second.metadata["org_count"])
        self.assertEqual([e["name"] for e in first.metadata["organizations"]],
                         ["ACME Widget & Tool Corporation", "Siemens AG",
                          "华为技术有限公司"])

    def test_batch_documents_independent(self):
        """Each document is processed independently and batch order is
        preserved."""
        docs = [_doc("Alpha Inc reported."),
                _doc("nothing to see here"),
                _doc("Beta Corp replied.")]
        result = self.extractor.process_docs(docs, self.query)
        self.assertEqual(result, docs)
        self.assertEqual(_names(docs[0]), ["Alpha Inc"])
        self.assertEqual(docs[1].metadata["organizations"], [])
        self.assertEqual(_names(docs[2]), ["Beta Corp"])


if __name__ == '__main__':
    unittest.main()
