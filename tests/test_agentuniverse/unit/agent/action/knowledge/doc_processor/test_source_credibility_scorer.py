# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/06
# @FileName: test_source_credibility_scorer.py

import unittest

from agentuniverse.agent.action.knowledge.doc_processor.source_credibility_scorer import (
    SourceCredibilityScorer,
    _registered_domain,
    _wildcard_domain_match,
)
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer


def _doc(source, **extra):
    return Document(text=f"from {source}",
                    metadata={"source": source, **extra})


class TestSourceCredibilityScorer(unittest.TestCase):
    """Comprehensive test suite for SourceCredibilityScorer."""

    def setUp(self):
        self.scorer = SourceCredibilityScorer()
        self.query = Query(query_str="trust")

    def _create_configer(self, config_dict):
        """Create a ComponentConfiger from a plain dictionary."""
        cfg = Configer()
        cfg.value = config_dict
        configer = ComponentConfiger()
        configer.load_by_configer(cfg)
        return configer

    # ========== Initialization tests ==========

    def test_default_configuration(self):
        """Defaults: 'source' key, no floor, stamped 'credibility_score'."""
        s = SourceCredibilityScorer()
        self.assertEqual(s.source_key, "source")
        self.assertIsNone(s.credibility_map)
        self.assertEqual(s.min_score, 0.0)
        self.assertEqual(s.score_key, "credibility_score")
        self.assertEqual(s.default_score, 0.5)
        self.assertTrue(s.keep_no_source)

    def test_initialize_by_component_configer(self):
        """YAML-provided parameters (including a custom map) are applied,
        with map keys normalized to lowercase."""
        configer = self._create_configer({
            'name': 'source_credibility_scorer',
            'description': 'credibility scorer',
            'source_key': 'url',
            'credibility_map': {'MyCompany.COM': 0.95, '*.gov': 0.98},
            'min_score': 0.4,
            'score_key': 'trust',
            'default_score': 0.45,
            'keep_no_source': False,
        })
        s = SourceCredibilityScorer()
        s._initialize_by_component_configer(configer)
        self.assertEqual(s.source_key, "url")
        self.assertEqual(s.credibility_map,
                         {'mycompany.com': 0.95, '*.gov': 0.98})
        self.assertEqual(s.min_score, 0.4)
        self.assertEqual(s.score_key, "trust")
        self.assertEqual(s.default_score, 0.45)
        self.assertFalse(s.keep_no_source)
        self.assertEqual(s.name, "source_credibility_scorer")

    def test_invalid_configuration_raises(self):
        """Out-of-range scores, non-numeric values, non-string keys, a
        non-mapping credibility_map and an empty source_key all fail
        at initialization time."""
        base = {
            'name': 's', 'description': 'd', 'source_key': 'source',
            'credibility_map': {}, 'min_score': 0.0,
            'default_score': 0.5,
        }
        cases = [
            {'credibility_map': {'x.com': 1.5}},
            {'credibility_map': {'x.com': -0.1}},
            {'credibility_map': {'x.com': 'high'}},
            {'credibility_map': {'': 0.5}},
            {'credibility_map': ['not', 'a', 'map']},
            {'min_score': 1.2},
            {'default_score': -1},
            {'source_key': ''},
        ]
        for override in cases:
            with self.assertRaises(ValueError, msg=repr(override)):
                SourceCredibilityScorer()._initialize_by_component_configer(
                    self._create_configer(dict(base, **override)))

    # ========== Source extraction tests ==========

    def test_source_extraction_normalizes_urls(self):
        """Scheme, userinfo, port, path, query and case all collapse to the
        bare lowercase domain before any table lookup."""
        variants = [
            "https://www.Reuters.com/world/news",
            "HTTP://reuters.com:8080/a/b?x=1#frag",
            "reuters.com",
            "https://user:pass@reuters.com/feed",
        ]
        docs = [Document(text=f"v{i}", metadata={"source": v})
                for i, v in enumerate(variants)]
        results = self.scorer.process_docs(docs, self.query)
        for d in results:
            self.assertAlmostEqual(d.metadata["credibility_score"], 0.85,
                                   msg=d.text)
            # www.Reuters.com reduces to reuters.com in the matched rule
            self.assertTrue(
                d.metadata["credibility_score_matched"] in
                ("reuters.com", "www.reuters.com"))

    def test_non_string_source_treated_as_missing(self):
        """Non-string source values (ints, lists) count as missing sources."""
        s = self.scorer
        s.keep_no_source = False
        docs = [
            Document(text="int", metadata={"source": 42}),
            Document(text="list", metadata={"source": ["a"]}),
            Document(text="none", metadata={"source": None}),
        ]
        self.assertEqual(s.process_docs(docs, self.query), [])

    # ========== Built-in table tests ==========

    def test_builtin_tld_scores(self):
        """.gov/.edu/.org and institutional suffixes map to their priors."""
        s = self.scorer
        cases = {
            "https://www.cdc.gov/flu": 0.95,       # .gov
            "https://www.nih.gov/": 0.95,          # .gov (exact table too)
            "https://www.harvard.edu/admissions": 0.9,   # .edu
            "https://www.tsinghua.edu.cn/": 0.9,   # multi-label .edu.cn
            "https://www.un.org/depts": 0.75,      # .org
            "https://www.who.int/": 0.95,          # exact table
        }
        docs = [_doc(src) for src in cases]
        results = s.process_docs(docs, self.query)
        by_text = {d.text: d.metadata["credibility_score"] for d in results}
        for src, expected in cases.items():
            self.assertAlmostEqual(by_text[f"from {src}"], expected,
                                   places=4, msg=src)

    def test_builtin_exact_and_label_scores(self):
        """Well-known domains and non-domain source labels resolve through
        their respective built-in tables."""
        s = self.scorer
        domain_cases = {
            "https://en.wikipedia.org/wiki/RAG": 0.7,
            "https://stackoverflow.com/q/1": 0.6,
            "https://someone.blogspot.com/post": 0.35,
            "arxiv.org": 0.75,
        }
        label_cases = {"official": 0.9, "blog": 0.4, "rumor": 0.1,
                       "unknown": 0.5}
        docs = ([Document(text=f"d:{k}", metadata={"source": k})
                 for k in domain_cases] +
                [Document(text=f"l:{k}", metadata={"source": k})
                 for k in label_cases])
        results = s.process_docs(docs, self.query)
        scores = {d.text: d.metadata["credibility_score"] for d in results}
        for src, expected in domain_cases.items():
            self.assertAlmostEqual(scores[f"d:{src}"], expected, msg=src)
        for label, expected in label_cases.items():
            self.assertAlmostEqual(scores[f"l:{label}"], expected, msg=label)

    def test_unknown_source_uses_default_score(self):
        """Unrecognized domains and labels fall back to default_score."""
        s = self.scorer
        s.default_score = 0.42
        docs = [_doc("totally-unknown-site.xyz"),
                Document(text="label", metadata={"source": "misc_label"})]
        results = s.process_docs(docs, self.query)
        for d in results:
            self.assertEqual(d.metadata["credibility_score"], 0.42)
            self.assertNotIn("credibility_score_matched", d.metadata)

    # ========== Custom map / wildcard tests ==========

    def test_custom_map_overrides_builtin(self):
        """credibility_map wins over the built-in tables, including for
        domains the built-ins already score."""
        s = self.scorer
        s.credibility_map = {"wikipedia.org": 0.99, "shady.io": 0.05}
        docs = [_doc("en.wikipedia.org"), _doc("shady.io")]
        results = s.process_docs(docs, self.query)
        scores = {d.text: d.metadata["credibility_score"] for d in results}
        self.assertEqual(scores["from en.wikipedia.org"], 0.99)
        self.assertEqual(scores["from shady.io"], 0.05)

    def test_wildcard_domain_matching(self):
        """'*.gov' matches any subdomain of gov but not 'gov' itself; the
        longest custom wildcard wins over shorter ones."""
        s = self.scorer
        s.credibility_map = {"*.gov": 0.9, "*.city.gov": 0.8}
        docs = [_doc("cdc.gov"), _doc("a.b.gov"), _doc("nyc.city.gov"),
                _doc("gov")]
        results = s.process_docs(docs, self.query)
        scores = {d.text: d.metadata["credibility_score"] for d in results}
        self.assertEqual(scores["from cdc.gov"], 0.9)
        self.assertEqual(scores["from a.b.gov"], 0.9)
        self.assertEqual(scores["from nyc.city.gov"], 0.8)  # longest match
        self.assertEqual(scores["from gov"], 0.5)          # no match: default

    def test_wildcard_helper_semantics(self):
        """Direct checks of the wildcard matcher, including multi-wildcard."""
        self.assertTrue(_wildcard_domain_match("*.gov", "cdc.gov"))
        self.assertTrue(_wildcard_domain_match("*.gov", "a.b.c.gov"))
        self.assertFalse(_wildcard_domain_match("*.gov", "gov"))
        self.assertFalse(_wildcard_domain_match("*.gov", "gov.example.com"))
        self.assertTrue(_wildcard_domain_match("*.edu.*", "mit.edu.au"))
        self.assertFalse(_wildcard_domain_match("*.edu.*", "mit.edu"))
        self.assertTrue(_wildcard_domain_match("exact.com", "exact.com"))

    def test_registered_domain_helper(self):
        """Last-two-label reduction for exact-table lookups."""
        self.assertEqual(_registered_domain("a.b.cdc.gov"), "cdc.gov")
        self.assertEqual(_registered_domain("reuters.com"), "reuters.com")
        self.assertIsNone(_registered_domain("official"))

    # ========== Filtering behavior tests ==========

    def test_min_score_filters_documents(self):
        """Documents below min_score are dropped; equal-or-above survive."""
        s = self.scorer
        s.min_score = 0.7
        docs = [_doc("https://www.cdc.gov/"),        # 0.95 kept
                _doc("https://en.wikipedia.org/x"),  # 0.7 kept (boundary)
                _doc("https://someone.blogspot.com/"),  # 0.35 dropped
                _doc("https://medium.com/@x")]       # 0.4 dropped
        results = s.process_docs(docs, self.query)
        self.assertEqual([d.text for d in results],
                         ["from https://www.cdc.gov/",
                          "from https://en.wikipedia.org/x"])

    def test_keep_no_source_policy(self):
        """Documents without source metadata follow keep_no_source."""
        no_meta = Document(text="no metadata")
        no_key = Document(text="no key", metadata={"lang": "en"})
        self.assertEqual(
            self.scorer.process_docs([no_meta, no_key], self.query),
            [no_meta, no_key])
        self.scorer.keep_no_source = False
        self.assertEqual(
            self.scorer.process_docs([no_meta, no_key], self.query), [])

    def test_empty_score_key_and_empty_input(self):
        """Empty input yields empty output; an empty score_key skips
        stamping while filtering still applies."""
        self.assertEqual(self.scorer.process_docs([], self.query), [])
        s = self.scorer
        s.score_key = ""
        s.min_score = 0.5
        doc = _doc("https://en.wikipedia.org/x")
        result = s.process_docs([doc], self.query)
        self.assertEqual(len(result), 1)
        self.assertNotIn("credibility_score", result[0].metadata)

    def test_custom_source_key(self):
        """A different metadata field can carry the source."""
        s = self.scorer
        s.source_key = "origin"
        doc = Document(text="x", metadata={"origin": "https://www.nih.gov/"})
        result = s.process_docs([doc], self.query)
        self.assertEqual(result[0].metadata["credibility_score"], 0.95)


if __name__ == '__main__':
    unittest.main()
