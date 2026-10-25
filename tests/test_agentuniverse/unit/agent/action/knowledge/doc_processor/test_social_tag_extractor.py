# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @FileName: test_social_tag_extractor.py

import unittest

from agentuniverse.agent.action.knowledge.doc_processor.social_tag_extractor import SocialTagExtractor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer

# A mixed English post exercising all three kinds; spans below are
# hand-counted character offsets.
MIXED_POST = "Loving #MachineLearning and #AI, pinging @bob_smith about $AAPL not $5.50"
MIXED_POST_HITS = [
    {"kind": "hashtag", "text": "#MachineLearning", "span": (7, 23)},
    {"kind": "hashtag", "text": "#AI", "span": (28, 31)},
    {"kind": "mention", "text": "@bob_smith", "span": (41, 51)},
    {"kind": "cashtag", "text": "$AAPL", "span": (58, 63)},
]

# CJK post: hashtags glued directly to Chinese prose (no spaces), with
# full-width punctuation terminating the runs. Spans hand-counted.
CJK_POST = "中文标签测试：#人工智能，以及#大模型应用。"
CJK_POST_HITS = [
    {"kind": "hashtag", "text": "#人工智能", "span": (7, 12)},
    {"kind": "hashtag", "text": "#大模型应用", "span": (15, 21)},
]


def _doc(text: str, **metadata) -> Document:
    """Build a Document carrying `text` and optional metadata."""
    return Document(text=text, metadata=dict(metadata) or None)


class TestSocialTagExtractor(unittest.TestCase):
    """Comprehensive offline test suite for SocialTagExtractor."""

    def setUp(self):
        self.extractor = SocialTagExtractor()
        self.query = Query(query_str="social listening")

    def _create_configer(self, config_dict):
        """Create a ComponentConfiger from a plain dictionary."""
        cfg = Configer()
        cfg.value = config_dict
        configer = ComponentConfiger()
        configer.load_by_configer(cfg)
        return configer

    def _extract(self, text):
        return SocialTagExtractor._extract(text)

    # ========== Initialization tests ==========

    def test_default_configuration(self):
        """Defaults: cap 200, top 10 hashtags, standard metadata keys."""
        e = SocialTagExtractor()
        self.assertEqual(e.max_tags, 200)
        self.assertEqual(e.top_n, 10)
        self.assertEqual(e.tags_key, "social_tags")
        self.assertEqual(e.counts_key, "tag_counts")
        self.assertEqual(e.top_hashtags_key, "top_hashtags")

    def test_initialize_by_component_configer(self):
        """YAML-provided parameters are applied on initialization."""
        configer = self._create_configer({
            'name': 'social_tag_extractor',
            'description': 'social tag extractor',
            'max_tags': 50,
            'top_n': 3,
            'tags_key': 'tags',
            'counts_key': 'counts',
            'top_hashtags_key': 'top_tags',
        })
        e = SocialTagExtractor()
        e._initialize_by_component_configer(configer)
        self.assertEqual(e.max_tags, 50)
        self.assertEqual(e.top_n, 3)
        self.assertEqual(e.tags_key, "tags")
        self.assertEqual(e.counts_key, "counts")
        self.assertEqual(e.top_hashtags_key, "top_tags")
        self.assertEqual(e.name, "social_tag_extractor")

    def test_invalid_configuration_raises(self):
        """Out-of-range caps, non-integer caps and non-string keys all
        fail at load time."""
        base = {
            'name': 'e', 'description': 'd',
            'max_tags': 200, 'top_n': 10,
            'tags_key': 'social_tags', 'counts_key': 'tag_counts',
            'top_hashtags_key': 'top_hashtags',
        }
        for key, value in (
            ('max_tags', 0),
            ('max_tags', -3),
            ('max_tags', 2.5),
            ('max_tags', True),
            ('top_n', -1),
            ('top_n', 1.5),
            ('top_n', True),
            ('tags_key', 5),
            ('counts_key', ['x']),
            ('top_hashtags_key', {}),
        ):
            config = dict(base, **{key: value})
            with self.assertRaises(ValueError, msg=f"{key}={value!r}"):
                SocialTagExtractor()._initialize_by_component_configer(
                    self._create_configer(config))

    # ========== Hashtag ground-truth tests ==========

    def test_mixed_post_extraction_with_spans(self):
        """All three kinds are found in document order with hand-counted
        spans; the price $5.50 yields no cashtag."""
        self.assertEqual(self._extract(MIXED_POST), MIXED_POST_HITS)

    def test_cjk_hashtags(self):
        """CJK hashtags are recognized, may directly follow Chinese prose
        (no spaces), and full-width punctuation terminates the span."""
        self.assertEqual(self._extract(CJK_POST), CJK_POST_HITS)

    def test_cjk_hashtag_glued_to_cjk_text(self):
        """A hashtag may follow CJK characters immediately; the run
        extends to the end of the word-character sequence."""
        hits = self._extract("科技改变世界#人工智能很火")
        self.assertEqual(hits, [
            {"kind": "hashtag", "text": "#人工智能很火",
             "span": (6, 13)},
        ])

    def test_camel_case_and_embedded_digit_hashtags(self):
        """camelCase capitals stay inside the tag; digits are allowed
        after the first character."""
        hits = self._extract("watching #WorldCup2026 and #MachineLearning")
        self.assertEqual([h["text"] for h in hits],
                         ["#WorldCup2026", "#MachineLearning"])

    def test_underscore_hashtag_start(self):
        """An underscore may open a hashtag (letter/underscore rule)."""
        hits = self._extract("internal #_dev_note here")
        self.assertEqual([h["text"] for h in hits], ["#_dev_note"])

    def test_trailing_punctuation_trimmed_from_spans(self):
        """ASCII and CJK sentence punctuation adjacent to a tag is never
        part of the recorded span."""
        hits = self._extract("see #AI, #ml. (#人工智能)")
        self.assertEqual([h["text"] for h in hits],
                         ["#AI", "#ml", "#人工智能"])
        for hit in hits:
            self.assertFalse(hit["text"][-1] in ",.)")

    def test_pure_digit_and_glued_hash_rejected(self):
        """Issue references (#123, #1st), markers glued to a preceding
        ASCII word (C#, foo#bar) and doubled markers are not hashtags."""
        for text in ("see issue #123 and #456fix",
                     "code in C# and F#",
                     "foo#bar mid-word",
                     "##tag"):
            self.assertEqual(self._extract(text), [], text)

    def test_markdown_header_with_space_not_a_tag(self):
        """A markdown heading '# ' has no word character after '#'; the
        unspaced ATX variant still reads as a hashtag."""
        hits = self._extract("# Introduction\n#Title")
        self.assertEqual([h["text"] for h in hits], ["#Title"])

    # ========== Mention ground-truth tests ==========

    def test_valid_mentions(self):
        """Handles of letters, digits and underscores are recognized with
        hand-counted spans."""
        hits = self._extract("@alice and @Bob_02 chat")
        self.assertEqual(hits, [
            {"kind": "mention", "text": "@alice", "span": (0, 6)},
            {"kind": "mention", "text": "@Bob_02", "span": (11, 18)},
        ])

    def test_mention_length_boundaries(self):
        """Exactly 2 and exactly 30 handle characters match."""
        handle30 = "@" + "a" * 30
        self.assertEqual([h["text"] for h in self._extract("@ab ok")],
                         ["@ab"])
        self.assertEqual([h["text"] for h in self._extract(handle30)],
                         [handle30])

    def test_too_short_mention_rejected(self):
        """A single-character handle is below the minimum of 2."""
        self.assertEqual(self._extract("@x too short"), [])

    def test_email_local_part_not_a_mention(self):
        """An '@' glued to a preceding word is an e-mail separator; the
        real mention next to it is still found."""
        hits = self._extract("mail alice@example.com or @bob")
        self.assertEqual([h["text"] for h in hits], ["@bob"])

    def test_doubled_and_overlong_mentions_rejected(self):
        """'@@nope' is not a mention; handles longer than 30 characters
        are ignored rather than truncated mid-word."""
        self.assertEqual(self._extract("@@nope"), [])
        self.assertEqual(self._extract("@" + "a" * 31), [])

    def test_mention_adjacent_to_cjk_text(self):
        """CJK characters before '@' do not block the mention."""
        hits = self._extract("联系@alice看看")
        self.assertEqual([h["text"] for h in hits], ["@alice"])

    # ========== Cashtag ground-truth tests ==========

    def test_valid_cashtags(self):
        """Uppercase tickers are recognized with hand-counted spans; a
        trailing period stays outside the span."""
        hits = self._extract("I like $GOOG. She likes $TSLA")
        self.assertEqual(hits, [
            {"kind": "cashtag", "text": "$GOOG", "span": (7, 12)},
            {"kind": "cashtag", "text": "$TSLA", "span": (24, 29)},
        ])

    def test_single_and_ten_letter_cashtags(self):
        """The 1-10 letter bounds are inclusive on both ends."""
        ten = "$" + "A" * 10
        self.assertEqual([h["text"] for h in self._extract("$A " + ten)],
                         ["$A", ten])

    def test_price_rejected(self):
        """Prices never yield cashtags: a digit cannot follow '$'."""
        for text in ("cost $5.50 today", "$ 5.50", "$1,200"):
            self.assertEqual(self._extract(text), [], text)

    def test_lowercase_and_glued_dollar_rejected(self):
        """Lowercase spellings are not tickers; a '$' glued to a
        preceding ASCII word ('US$') does not match either."""
        for text in ("$aapl lowercase", "US$500 cash"):
            self.assertEqual(self._extract(text), [], text)

    def test_overlong_caps_run_rejected(self):
        """All-caps runs longer than 10 characters are ignored rather
        than cut into a fake ticker."""
        self.assertEqual(self._extract("$" + "A" * 11), [])

    def test_underscored_caps_identifier_rejected(self):
        """All-caps identifiers containing underscores are not tickers
        and are not cut into one."""
        self.assertEqual(self._extract("$PRICE_HIGH fell"), [])

    def test_dotted_ticker_suffix(self):
        """'$BRK.B' keeps the exchange-suffix dot out of the span."""
        self.assertEqual(self._extract("$BRK.B fell"), [
            {"kind": "cashtag", "text": "$BRK", "span": (0, 4)},
        ])

    # ========== Span invariants ==========

    def test_span_invariants_over_corpus(self):
        """For every hit over a varied corpus: the span slices the exact
        text, spans are sorted and non-overlapping, and the marker
        character matches the reported kind."""
        corpus = [
            MIXED_POST, CJK_POST,
            "#start tag and @mid mention with $END cashtag",
            "no markers at all in this one",
            "@only_a_mention",
            "$ONLY_A_CASHTAG and #only_a_hashtag",
            "emoji \U0001f600 mixed #tag123 done",
        ]
        markers = {"hashtag": "#", "mention": "@", "cashtag": "$"}
        for text in corpus:
            previous_end = -1
            for hit in self._extract(text):
                start, end = hit["span"]
                self.assertEqual(text[start:end], hit["text"], text)
                self.assertGreaterEqual(start, previous_end, text)
                self.assertLess(previous_end, end, text)
                self.assertTrue(hit["text"].startswith(
                    markers[hit["kind"]]), hit)
                previous_end = end

    # ========== Metadata stamping tests ==========

    def test_metadata_entries_stamped(self):
        """social_tags / tag_counts / top_hashtags land in metadata with
        the documented shapes."""
        doc = _doc(MIXED_POST)
        result = self.extractor.process_docs([doc], self.query)
        self.assertIs(result[0], doc)
        meta = doc.metadata
        self.assertEqual(meta["social_tags"], MIXED_POST_HITS)
        self.assertEqual(meta["tag_counts"],
                         {"hashtag": 2, "mention": 1, "cashtag": 1})
        self.assertEqual(meta["top_hashtags"],
                         [{"text": "#AI", "count": 1},
                          {"text": "#MachineLearning", "count": 1}])

    def test_duplicate_tags_counted_separately(self):
        """Repeated tags appear once per occurrence in social_tags and
        accumulate in tag_counts and top_hashtags."""
        doc = _doc("#AI rocks #AI again #ai once")
        self.extractor.process_docs([doc], self.query)
        self.assertEqual(len(doc.metadata["social_tags"]), 3)
        self.assertEqual(doc.metadata["tag_counts"]["hashtag"], 3)
        self.assertEqual(doc.metadata["top_hashtags"],
                         [{"text": "#AI", "count": 2},
                          {"text": "#ai", "count": 1}])

    def test_top_hashtags_ranking_and_tie_break(self):
        """Ranking is by descending frequency with alphabetical ties."""
        doc = _doc("#b #b #a #a #c")
        self.extractor.process_docs([doc], self.query)
        self.assertEqual(doc.metadata["top_hashtags"],
                         [{"text": "#a", "count": 2},
                          {"text": "#b", "count": 2},
                          {"text": "#c", "count": 1}])

    def test_top_n_truncates_ranking(self):
        """12 distinct hashtags yield the default top 10; a configured
        top_n=3 yields 3, both in alphabetical (tie) order."""
        text = " ".join(f"#tag{i:02d}" for i in range(12))
        doc = _doc(text)
        self.extractor.process_docs([doc], self.query)
        self.assertEqual(len(doc.metadata["top_hashtags"]), 10)
        self.assertEqual(doc.metadata["top_hashtags"][0],
                         {"text": "#tag00", "count": 1})

        self.extractor.top_n = 3
        doc2 = _doc(text)
        self.extractor.process_docs([doc2], self.query)
        self.assertEqual([t["text"] for t in doc2.metadata["top_hashtags"]],
                         ["#tag00", "#tag01", "#tag02"])

    def test_top_hashtags_empty_when_only_other_kinds(self):
        """A post with only mentions/cashtags still gets tag_counts and
        an empty (not missing) top_hashtags list."""
        doc = _doc("hey @alice look at $AAPL")
        self.extractor.process_docs([doc], self.query)
        self.assertEqual(doc.metadata["tag_counts"],
                         {"hashtag": 0, "mention": 1, "cashtag": 1})
        self.assertEqual(doc.metadata["top_hashtags"], [])

    def test_cap_truncates_list_but_not_counts(self):
        """max_tags slices social_tags in document order while
        tag_counts / top_hashtags keep covering every hit."""
        text = " ".join(f"#h{i}" for i in range(250))
        doc = _doc(text)
        self.extractor.process_docs([doc], self.query)
        self.assertEqual(len(doc.metadata["social_tags"]), 200)
        self.assertEqual(doc.metadata["social_tags"][0]["text"], "#h0")
        self.assertEqual(doc.metadata["tag_counts"]["hashtag"], 250)

        self.extractor.max_tags = 1
        doc2 = _doc("#a #b #a")
        self.extractor.process_docs([doc2], self.query)
        self.assertEqual(doc2.metadata["social_tags"],
                         [{"kind": "hashtag", "text": "#a", "span": (0, 2)}])
        self.assertEqual(doc2.metadata["tag_counts"]["hashtag"], 3)
        self.assertEqual(doc2.metadata["top_hashtags"],
                         [{"text": "#a", "count": 2},
                          {"text": "#b", "count": 1}])

    def test_cap_keeps_document_order_across_kinds(self):
        """The cap slices hits in document order across interleaved
        kinds, not per kind."""
        self.extractor.max_tags = 3
        doc = _doc("#one @alice #two $AAPL #three")
        self.extractor.process_docs([doc], self.query)
        self.assertEqual([t["text"] for t in doc.metadata["social_tags"]],
                         ["#one", "@alice", "#two"])
        self.assertEqual(doc.metadata["tag_counts"],
                         {"hashtag": 3, "mention": 1, "cashtag": 1})

    def test_disabled_keys_and_top_n_zero(self):
        """Empty keys disable the respective entry; top_n=0 disables
        top_hashtags while the other entries survive."""
        doc = _doc(MIXED_POST, src="feed")
        self.extractor.tags_key = ""
        self.extractor.process_docs([doc], self.query)
        self.assertNotIn("social_tags", doc.metadata)
        self.assertIn("tag_counts", doc.metadata)

        self.extractor = SocialTagExtractor()
        self.extractor.counts_key = ""
        doc = _doc(MIXED_POST)
        self.extractor.process_docs([doc], self.query)
        self.assertNotIn("tag_counts", doc.metadata)
        self.assertIn("social_tags", doc.metadata)

        self.extractor = SocialTagExtractor()
        self.extractor.top_hashtags_key = ""
        doc = _doc(MIXED_POST)
        self.extractor.process_docs([doc], self.query)
        self.assertNotIn("top_hashtags", doc.metadata)

        self.extractor = SocialTagExtractor()
        self.extractor.top_n = 0
        doc = _doc(MIXED_POST)
        self.extractor.process_docs([doc], self.query)
        self.assertNotIn("top_hashtags", doc.metadata)
        self.assertIn("social_tags", doc.metadata)

    def test_custom_metadata_keys(self):
        """Configured key names replace the defaults."""
        self.extractor.tags_key = "markers"
        self.extractor.counts_key = "marker_counts"
        self.extractor.top_hashtags_key = "top_markers"
        doc = _doc(MIXED_POST)
        self.extractor.process_docs([doc], self.query)
        self.assertIn("markers", doc.metadata)
        self.assertIn("marker_counts", doc.metadata)
        self.assertIn("top_markers", doc.metadata)
        for key in ("social_tags", "tag_counts", "top_hashtags"):
            self.assertNotIn(key, doc.metadata)

    # ========== Passthrough and integrity tests ==========

    def test_no_tags_passthrough(self):
        """Documents without markers keep their text and metadata
        untouched — None metadata stays None."""
        plain = _doc("just plain text, nothing social here")
        with_meta = _doc("still no markers", src="wire", rank=1)
        result = self.extractor.process_docs([plain, with_meta], self.query)
        self.assertEqual(len(result), 2)
        self.assertIsNone(plain.metadata)
        self.assertEqual(with_meta.metadata, {"src": "wire", "rank": 1})

    def test_text_and_id_never_modified(self):
        """Text, id and pre-existing metadata entries survive stamping;
        the stamp goes through a copied mapping."""
        doc = _doc(MIXED_POST, src="wire", rank=1)
        meta_ref = doc.metadata
        doc_id = doc.id

        result = self.extractor.process_docs([doc], self.query)

        self.assertEqual(result[0].text, MIXED_POST)
        self.assertEqual(doc.id, doc_id)
        self.assertEqual(doc.metadata["src"], "wire")
        self.assertEqual(doc.metadata["rank"], 1)
        self.assertIsNot(doc.metadata, meta_ref)
        for key in ("social_tags", "tag_counts", "top_hashtags"):
            self.assertNotIn(key, meta_ref)
            self.assertIn(key, doc.metadata)

    def test_empty_batch_and_blank_documents(self):
        """An empty batch yields []; empty and None texts pass through
        unstamped."""
        self.assertEqual(self.extractor.process_docs([], self.query), [])

        blank = _doc("")
        none_text = Document(id="none-text", text=None, metadata=None)
        result = self.extractor.process_docs([blank, none_text], self.query)
        self.assertEqual(len(result), 2)
        self.assertIsNone(blank.metadata)
        self.assertIsNone(none_text.metadata)

    def test_batch_documents_stamped_independently(self):
        """Each document in a batch is stamped from its own text only."""
        docs = [_doc("plain"), _doc("#solo hashtag"),
                _doc("@solo mention")]
        result = self.extractor.process_docs(docs, self.query)
        self.assertEqual([d.text for d in result],
                         ["plain", "#solo hashtag", "@solo mention"])
        self.assertIsNone(docs[0].metadata)
        self.assertEqual(docs[1].metadata["tag_counts"],
                         {"hashtag": 1, "mention": 0, "cashtag": 0})
        self.assertEqual(docs[2].metadata["tag_counts"],
                         {"hashtag": 0, "mention": 1, "cashtag": 0})

    def test_deterministic_across_runs_and_instances(self):
        """The same text yields byte-identical metadata under separate
        instances and repeated runs."""
        text = "#delta #alpha #delta @user $IBM #alpha #zeta @user"
        run_one = SocialTagExtractor().process_docs([_doc(text)], self.query)
        run_two = SocialTagExtractor().process_docs([_doc(text)], self.query)
        again = SocialTagExtractor().process_docs([run_one[0]], self.query)
        self.assertEqual(run_one[0].metadata, run_two[0].metadata)
        self.assertEqual(run_one[0].metadata["social_tags"],
                         again[0].metadata["social_tags"])
        self.assertEqual(run_one[0].metadata["top_hashtags"],
                         [{"text": "#alpha", "count": 2},
                          {"text": "#delta", "count": 2},
                          {"text": "#zeta", "count": 1}])


if __name__ == '__main__':
    unittest.main()
