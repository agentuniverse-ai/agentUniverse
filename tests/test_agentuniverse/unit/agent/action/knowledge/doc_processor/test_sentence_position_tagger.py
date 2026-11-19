# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @FileName: test_sentence_position_tagger.py

import unittest

from agentuniverse.agent.action.knowledge.doc_processor.sentence_position_tagger import SentencePositionTagger
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer

# A ten-sentence document used as the standard multi-sentence fixture.
TEN_SENTENCES = (
    "The committee published its annual report on Tuesday morning. "
    "It covers the full fiscal year and restates prior guidance. "
    "Revenue grew fourteen percent despite the spring slowdown. "
    "Operating costs fell after the two restructuring rounds. "
    "Management flagged currency exposure as the main risk. "
    "The board approved a renewed buyback programme. "
    "Auditors raised no going-concern qualifications this year. "
    "Two regional units will be consolidated into one. "
    "The report closes with a detailed capital plan. "
    "Overall the year ended stronger than anyone forecast."
)

# Three plain sentences — the minimal document with real bookends.
THREE_SENTENCES = "First sentence here. Body sentence follows. Closing line."

# Chinese three-sentence document mixing 。！？ terminals.
ZH_THREE = "今天天气很好。我们去公园散步吧！晚上一起吃饭。"


def _doc(text: str, **metadata) -> Document:
    """Build a Document carrying `text` and optional metadata."""
    return Document(text=text, metadata=dict(metadata) or None)


class TestSentencePositionTagger(unittest.TestCase):
    """Comprehensive test suite for SentencePositionTagger."""

    def setUp(self):
        self.tagger = SentencePositionTagger()
        self.query = Query(query_str="positions")

    def _create_configer(self, config_dict):
        """Create a ComponentConfiger from a plain dictionary."""
        cfg = Configer()
        cfg.value = config_dict
        configer = ComponentConfiger()
        configer.load_by_configer(cfg)
        return configer

    def _positions(self, text: str):
        """Run the tagger over one document and return its positions."""
        doc = _doc(text)
        self.tagger.process_docs([doc], self.query)
        return doc

    # ========== Initialization tests ==========

    def test_default_configuration(self):
        """Defaults: cap 200, tag_text off, 'sentence_positions' /
        'position_counts' metadata keys."""
        t = SentencePositionTagger()
        self.assertEqual(t.max_sentences, 200)
        self.assertFalse(t.tag_text)
        self.assertEqual(t.positions_key, "sentence_positions")
        self.assertEqual(t.counts_key, "position_counts")

    def test_initialize_by_component_configer(self):
        """YAML-provided parameters are applied on initialization."""
        configer = self._create_configer({
            'name': 'sentence_position_tagger',
            'description': 'sentence position tagger',
            'max_sentences': 10,
            'tag_text': True,
            'positions_key': 'roles',
            'counts_key': 'role_counts',
        })
        t = SentencePositionTagger()
        t._initialize_by_component_configer(configer)
        self.assertEqual(t.max_sentences, 10)
        self.assertTrue(t.tag_text)
        self.assertEqual(t.positions_key, "roles")
        self.assertEqual(t.counts_key, "role_counts")
        self.assertEqual(t.name, "sentence_position_tagger")

    def test_invalid_configuration_raises(self):
        """Negative / non-integer caps and non-string keys fail at load
        time; 0 is a legal cap (list disabled, counts stay)."""
        base = {
            'name': 't', 'description': 'd',
            'max_sentences': 5, 'tag_text': False,
            'positions_key': 'sentence_positions',
            'counts_key': 'position_counts',
        }
        for key, value in (
            ('max_sentences', -1),
            ('max_sentences', 1.5),
            ('max_sentences', True),
            ('positions_key', 5),
            ('counts_key', ['x']),
        ):
            config = dict(base, **{key: value})
            with self.assertRaises(ValueError, msg=f"{key}={value!r}"):
                SentencePositionTagger()._initialize_by_component_configer(
                    self._create_configer(config))

        t = SentencePositionTagger()
        t._initialize_by_component_configer(
            self._create_configer(dict(base, max_sentences=0)))
        self.assertEqual(t.max_sentences, 0)

    # ========== Role assignment ground truths ==========

    def test_single_sentence_all_body(self):
        """One sentence: no bookends are invented — the only sentence is
        body, and the text is never tagged."""
        doc = self._positions("Just one lonely sentence.")
        self.assertEqual([p["role"] for p in doc.metadata["sentence_positions"]],
                         ["body"])
        self.assertEqual(doc.metadata["position_counts"],
                         {"opening": 0, "body": 1, "closing": 0})
        self.assertEqual(doc.text, "Just one lonely sentence.")

    def test_two_sentences_all_body(self):
        """Two sentences: still below the 3-sentence threshold, so both
        are body — the first is NOT an opening."""
        doc = self._positions("Opening-ish first. Closing-ish second.")
        self.assertEqual([p["role"] for p in doc.metadata["sentence_positions"]],
                         ["body", "body"])
        self.assertEqual(doc.metadata["position_counts"],
                         {"opening": 0, "body": 2, "closing": 0})

    def test_three_sentences_opening_body_closing(self):
        """Three sentences: the minimal document with real bookends."""
        doc = self._positions(THREE_SENTENCES)
        self.assertEqual([p["role"] for p in doc.metadata["sentence_positions"]],
                         ["opening", "body", "closing"])
        self.assertEqual(doc.metadata["position_counts"],
                         {"opening": 1, "body": 1, "closing": 1})

    def test_ten_sentences_opening_eight_body_closing(self):
        """Ten sentences: first opening, last closing, eight body."""
        doc = self._positions(TEN_SENTENCES)
        roles = [p["role"] for p in doc.metadata["sentence_positions"]]
        self.assertEqual(roles,
                         ["opening"] + ["body"] * 8 + ["closing"])
        self.assertEqual(doc.metadata["position_counts"],
                         {"opening": 1, "body": 8, "closing": 1})

    def test_indexes_are_sequential(self):
        """Entries carry zero-based sequential indexes matching list
        order."""
        doc = self._positions(TEN_SENTENCES)
        self.assertEqual([p["index"] for p in
                          doc.metadata["sentence_positions"]],
                         list(range(10)))

    # ========== Segmentation tests ==========

    def test_abbreviation_guard(self):
        """Known abbreviations and initials do not split sentences."""
        doc = self._positions(
            "Dr. Smith arrived at noon. Ms. Lee greeted Prof. Wang "
            "warmly. Everyone sat down.")
        roles = [p["role"] for p in doc.metadata["sentence_positions"]]
        self.assertEqual(len(roles), 3)
        self.assertEqual(roles, ["opening", "body", "closing"])

    def test_decimal_and_ellipsis_guards(self):
        """Decimals ("3.14") do not split; an ellipsis splits only at its
        final dot."""
        doc = self._positions("Pi is about 3.14 in daily use. "
                              "Wait for it... Then it happened. "
                              "Nobody expected that outcome.")
        roles = [p["role"] for p in doc.metadata["sentence_positions"]]
        self.assertEqual(len(roles), 4)
        self.assertEqual(roles[0], "opening")
        self.assertEqual(roles[-1], "closing")

    def test_trailing_sentence_without_terminal_punctuation(self):
        """A final sentence lacking punctuation still counts and is the
        closing sentence."""
        text = "First sentence. Second here. Third lacks punctuation"
        doc = self._positions(text)
        roles = [p["role"] for p in doc.metadata["sentence_positions"]]
        self.assertEqual(roles, ["opening", "body", "closing"])
        self.assertEqual(
            doc.text[doc.metadata["sentence_positions"][2]["span"][0]:
                     doc.metadata["sentence_positions"][2]["span"][1]],
            "Third lacks punctuation")

    def test_punctuation_only_husk_dropped(self):
        """A bare '.' between sentences has no words and never counts as
        a sentence."""
        doc = self._positions("First sentence.  .  Second here. Third one.")
        roles = [p["role"] for p in doc.metadata["sentence_positions"]]
        self.assertEqual(roles, ["opening", "body", "closing"])

    def test_cjk_sentences(self):
        """CJK terminals 。！？ split correctly; spans slice the exact
        sentence texts out of the original string."""
        doc = self._positions(ZH_THREE)
        positions = doc.metadata["sentence_positions"]
        self.assertEqual([p["role"] for p in positions],
                         ["opening", "body", "closing"])
        self.assertEqual([doc.text[s:e] for _, _, (s, e) in
                          ((p["index"], p["role"], p["span"])
                           for p in positions)],
                         ["今天天气很好。", "我们去公园散步吧！", "晚上一起吃饭。"])

    def test_terminal_run_and_closing_quotes_stay_whole(self):
        """A terminal-punctuation run plus closing quotes belongs to the
        sentence it terminates."""
        text = '"He said so." Nobody argued the point. The room fell silent.'
        doc = self._positions(text)
        positions = doc.metadata["sentence_positions"]
        self.assertEqual(len(positions), 3)
        self.assertEqual(text[positions[0]["span"][0]:
                              positions[0]["span"][1]],
                         '"He said so."')

    # ========== Span invariants ==========

    def test_span_invariants(self):
        """Spans are ordered, non-overlapping, in-bounds and slice the
        exact sentence out of the original text."""
        for text in (TEN_SENTENCES, THREE_SENTENCES, ZH_THREE,
                     "One. Two. Three. Four. Five. Six. Seven. Eight."):
            doc = self._positions(text)
            last_end = 0
            for entry in doc.metadata["sentence_positions"]:
                start, end = entry["span"]
                self.assertGreaterEqual(start, last_end)
                self.assertGreater(end, start)
                self.assertLessEqual(end, len(text))
                self.assertEqual(text[start:end].strip(), text[start:end])
                self.assertGreater(len(text[start:end]), 0)
                last_end = end
            self.assertLessEqual(last_end, len(text))

    def test_spans_reconstruct_sentences(self):
        """Slicing every span yields exactly the sentence texts, and
        they appear in the original order."""
        text = TEN_SENTENCES
        doc = self._positions(text)
        slices = [text[p["span"][0]:p["span"][1]]
                  for p in doc.metadata["sentence_positions"]]
        self.assertEqual(slices[0], "The committee published its annual "
                                    "report on Tuesday morning.")
        self.assertEqual(slices[-1], "Overall the year ended stronger "
                                     "than anyone forecast.")
        for piece in slices:
            self.assertIn(piece, text)
        self.assertEqual(" ".join(slices), text)

    # ========== Counts arithmetic ==========

    def test_counts_sum_to_total_sentences(self):
        """The three counts sum to the total sentence count and equal
        the number of list entries below the cap."""
        for text, expected_total in ((TEN_SENTENCES, 10),
                                     (THREE_SENTENCES, 3),
                                     ("Only one.", 1),
                                     ("Apple. Banana.", 2)):
            doc = self._positions(text)
            counts = doc.metadata["position_counts"]
            self.assertEqual(sum(counts.values()), expected_total)
            self.assertEqual(len(doc.metadata["sentence_positions"]),
                             expected_total)

    def test_counts_arithmetic_roles_match(self):
        """The count of each role equals the number of entries stamped
        with that role."""
        doc = self._positions(TEN_SENTENCES)
        roles = [p["role"] for p in doc.metadata["sentence_positions"]]
        counts = doc.metadata["position_counts"]
        self.assertEqual(counts["opening"], roles.count("opening"))
        self.assertEqual(counts["body"], roles.count("body"))
        self.assertEqual(counts["closing"], roles.count("closing"))

    # ========== Cap behavior ==========

    def test_cap_limits_list_but_not_counts(self):
        """With 250 sentences and the default cap of 200 the list holds
        200 entries while the counts still total 250; the surviving
        entries are the first 200."""
        text = " ".join(f"Sentence number {i} here." for i in range(250))
        self.assertEqual(
            len(SentencePositionTagger()._sentences(text)), 250)
        doc = self._positions(text)
        positions = doc.metadata["sentence_positions"]
        self.assertEqual(len(positions), 200)
        self.assertEqual(positions[0]["index"], 0)
        self.assertEqual(positions[-1]["index"], 199)
        counts = doc.metadata["position_counts"]
        self.assertEqual(sum(counts.values()), 250)
        self.assertEqual(counts["opening"], 1)
        self.assertEqual(counts["body"], 248)
        self.assertEqual(counts["closing"], 1)

    def test_cap_zero_disables_list_only(self):
        """max_sentences=0 stamps an empty list while counts still
        describe the whole document."""
        self.tagger.max_sentences = 0
        doc = _doc(THREE_SENTENCES)
        self.tagger.process_docs([doc], self.query)
        self.assertEqual(doc.metadata["sentence_positions"], [])
        self.assertEqual(doc.metadata["position_counts"],
                         {"opening": 1, "body": 1, "closing": 1})

    # ========== tag_text mode ==========

    def test_tag_text_wraps_bookends(self):
        """tag_text wraps the opening and closing sentences with the
        marker literals and leaves the body untouched."""
        self.tagger.tag_text = True
        doc = _doc(THREE_SENTENCES)
        self.tagger.process_docs([doc], self.query)
        self.assertEqual(
            doc.text,
            "[[OPEN]]First sentence here.[[/OPEN]] Body sentence "
            "follows. [[CLOSE]]Closing line.[[/CLOSE]]")

    def test_tag_text_spans_reference_pre_tag_text(self):
        """In tag_text mode the recorded spans index the marker-free
        (pre-tag) text: slices of the ORIGINAL text, not the tagged
        output."""
        self.tagger.tag_text = True
        doc = _doc(THREE_SENTENCES)
        original = doc.text
        self.tagger.process_docs([doc], self.query)
        for entry in doc.metadata["sentence_positions"]:
            start, end = entry["span"]
            self.assertTrue(original[start:end].strip())
            self.assertIn(original[start:end], original)

    def test_tag_text_second_pass_is_noop(self):
        """Re-processing already-tagged output changes nothing: the text
        is identical and markers are never doubled; spans, roles and
        counts match the first pass."""
        self.tagger.tag_text = True
        doc = _doc(TEN_SENTENCES)
        self.tagger.process_docs([doc], self.query)
        first_text = doc.text
        first_positions = doc.metadata["sentence_positions"]
        first_counts = doc.metadata["position_counts"]
        self.assertEqual(first_text.count("[[OPEN]]"), 1)
        self.assertEqual(first_text.count("[[CLOSE]]"), 1)

        self.tagger.process_docs([doc], self.query)
        self.assertEqual(doc.text, first_text)
        self.assertEqual(doc.text.count("[[OPEN]]"), 1)
        self.assertEqual(doc.text.count("[[CLOSE]]"), 1)
        self.assertEqual(doc.metadata["sentence_positions"],
                         first_positions)
        self.assertEqual(doc.metadata["position_counts"], first_counts)

    def test_tag_text_third_pass_still_noop(self):
        """A third pass remains a no-op — the guard is idempotent."""
        self.tagger.tag_text = True
        doc = _doc("Alpha one. Beta two. Gamma three.")
        for _ in range(3):
            self.tagger.process_docs([doc], self.query)
        self.assertEqual(
            doc.text,
            "[[OPEN]]Alpha one.[[/OPEN]] Beta two. "
            "[[CLOSE]]Gamma three.[[/CLOSE]]")

    def test_tag_text_below_threshold_never_rewrites(self):
        """With fewer than 3 sentences tag_text leaves the text
        completely untouched (no markers, no stripping)."""
        self.tagger.tag_text = True
        for text in ("One sentence only.", "Two. Sentences."):
            doc = _doc(text)
            self.tagger.process_docs([doc], self.query)
            self.assertEqual(doc.text, text)
            self.assertEqual([p["role"] for p in
                              doc.metadata["sentence_positions"]],
                             ["body"] * (1 if text.startswith("One") else 2))

    def test_tag_text_strips_pre_existing_markers(self):
        """In tag_text mode marker literals already present in the input
        are stripped before analysis, so the roles describe the clean
        text rather than the leftovers of an earlier pass."""
        self.tagger.tag_text = True
        marked = ("[[OPEN]]The summit opened on Monday.[[/OPEN]] Delegates "
                  "agreed on targets. [[CLOSE]]A joint statement closed "
                  "the day.[[/CLOSE]]")
        doc = _doc(marked)
        self.tagger.process_docs([doc], self.query)
        self.assertEqual(doc.text, marked)  # re-wrapped identically: no-op
        self.assertEqual(doc.metadata["position_counts"],
                         {"opening": 1, "body": 1, "closing": 1})

    def test_tag_text_disabled_never_touches_text(self):
        """In default mode the text is never modified — not even when it
        already contains marker literals."""
        marked = "[[OPEN]]First here.[[/OPEN]] Body in the middle. " \
                 "[[CLOSE]]Last of all.[[/CLOSE]]"
        doc = self._positions(marked)
        self.assertEqual(doc.text, marked)

    def test_tag_text_cjk(self):
        """tag_text works on CJK sentences too."""
        self.tagger.tag_text = True
        doc = _doc(ZH_THREE)
        self.tagger.process_docs([doc], self.query)
        self.assertEqual(
            doc.text,
            "[[OPEN]]今天天气很好。[[/OPEN]]我们去公园散步吧！"
            "[[CLOSE]]晚上一起吃饭。[[/CLOSE]]")

    # ========== Empty / degenerate documents ==========

    def test_empty_batch(self):
        """An empty batch yields an empty output."""
        self.assertEqual(self.tagger.process_docs([], self.query), [])

    def test_empty_and_blank_documents(self):
        """Empty, blank and None-text documents produce an empty list
        and all-zero counts without raising."""
        blank_docs = [_doc(""), _doc("   "), Document(text=None, id="no-text")]
        for doc in blank_docs:
            self.tagger.process_docs([doc], self.query)
            self.assertEqual(doc.metadata["sentence_positions"], [])
            self.assertEqual(doc.metadata["position_counts"],
                             {"opening": 0, "body": 0, "closing": 0})

    def test_punctuation_only_document(self):
        """A document of pure punctuation yields no sentences."""
        doc = self._positions("？！。...")
        self.assertEqual(doc.metadata["sentence_positions"], [])
        self.assertEqual(doc.metadata["position_counts"],
                         {"opening": 0, "body": 0, "closing": 0})

    # ========== Pipeline-shape tests ==========

    def test_batch_documents_processed_independently(self):
        """Each document in a batch gets its own roles; order and ids
        are preserved."""
        docs = [_doc(THREE_SENTENCES), _doc("Solo sentence."),
                _doc(TEN_SENTENCES)]
        ids = [d.id for d in docs]
        result = self.tagger.process_docs(docs, self.query)
        self.assertEqual([d.id for d in result], ids)
        self.assertEqual([p["role"] for p in
                          result[0].metadata["sentence_positions"]],
                         ["opening", "body", "closing"])
        self.assertEqual([p["role"] for p in
                          result[1].metadata["sentence_positions"]],
                         ["body"])
        self.assertEqual(len(
            result[2].metadata["sentence_positions"]), 10)

    def test_metadata_preserved_and_copied_before_write(self):
        """Pre-existing metadata survives, and stamping writes through a
        copy rather than mutating the original mapping."""
        doc = _doc(THREE_SENTENCES, source="wiki", rank=7)
        meta_ref = doc.metadata
        self.tagger.process_docs([doc], self.query)

        self.assertEqual(doc.metadata["source"], "wiki")
        self.assertEqual(doc.metadata["rank"], 7)
        self.assertIn("sentence_positions", doc.metadata)
        self.assertIn("position_counts", doc.metadata)
        self.assertNotIn("sentence_positions", meta_ref)
        self.assertNotIn("position_counts", meta_ref)
        self.assertIsNot(doc.metadata, meta_ref)

    def test_disabled_keys_stamp_nothing(self):
        """Empty positions_key / counts_key disable both stamps."""
        self.tagger.positions_key = ""
        self.tagger.counts_key = ""
        doc = _doc(THREE_SENTENCES, source="wiki")
        self.tagger.process_docs([doc], self.query)
        self.assertEqual(doc.metadata, {"source": "wiki"})

    def test_id_and_text_untouched_in_default_mode(self):
        """Default mode never modifies text or id."""
        doc = _doc(THREE_SENTENCES)
        original_id = doc.id
        self.tagger.process_docs([doc], self.query)
        self.assertEqual(doc.text, THREE_SENTENCES)
        self.assertEqual(doc.id, original_id)

    def test_deterministic_across_runs(self):
        """Two fresh instances produce identical metadata for the same
        input — no hidden state or randomness."""
        doc_a = _doc(TEN_SENTENCES)
        doc_b = _doc(TEN_SENTENCES)
        SentencePositionTagger().process_docs([doc_a], self.query)
        SentencePositionTagger().process_docs([doc_b], self.query)
        self.assertEqual(doc_a.metadata["sentence_positions"],
                         doc_b.metadata["sentence_positions"])
        self.assertEqual(doc_a.metadata["position_counts"],
                         doc_b.metadata["position_counts"])

    def test_role_rule_helper(self):
        """The documented rule, checked directly: <3 all body; >=3 first
        opening, last closing, rest body."""
        role = SentencePositionTagger._role
        self.assertEqual([role(i, 1) for i in range(1)], ["body"])
        self.assertEqual([role(i, 2) for i in range(2)], ["body", "body"])
        self.assertEqual([role(i, 3) for i in range(3)],
                         ["opening", "body", "closing"])
        self.assertEqual([role(i, 4) for i in range(4)],
                         ["opening", "body", "body", "closing"])


if __name__ == '__main__':
    unittest.main()
