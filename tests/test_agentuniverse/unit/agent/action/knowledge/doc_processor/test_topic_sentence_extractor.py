# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @FileName: test_topic_sentence_extractor.py

import unittest

from agentuniverse.agent.action.knowledge.doc_processor.topic_sentence_extractor import TopicSentenceExtractor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer


def _fit(prefix: str, total: int) -> str:
    """A sentence of exactly `total` characters: `prefix` padded with
    'x' runs and closed by one period. The prefix must itself be free of
    score-triggering patterns (signpost openers, copula strings)."""
    assert len(prefix) + 2 <= total, (prefix, total)
    return prefix + "x" * (total - len(prefix) - 1) + "."


def _doc(text: str, **metadata) -> Document:
    """Build a Document carrying `text` and optional metadata."""
    return Document(text=text, metadata=dict(metadata) or None)


class TestTopicSentenceExtractor(unittest.TestCase):
    """Comprehensive offline test suite for TopicSentenceExtractor.

    Score arithmetic notes used throughout (default weights):
    first sentence +2.0, last sentence +0.5 (a lone sentence earns both,
    so a single-sentence paragraph starts at 2.5), length band +1.0 for
    40 <= len <= 120 chars, rambling -1.0 above 250 chars, signpost
    opener +1.5, definitional copula +0.5. Ties go to the earliest
    sentence. All crafted sentence lengths below were verified against
    len() by hand before being asserted on.
    """

    def setUp(self):
        self.extractor = TopicSentenceExtractor()
        self.query = Query(query_str="skeleton preview")

    def _create_configer(self, config_dict):
        """Create a ComponentConfiger from a plain dictionary."""
        cfg = Configer()
        cfg.value = config_dict
        configer = ComponentConfiger()
        configer.load_by_configer(cfg)
        return configer

    def _run(self, text, extractor=None):
        """Process one document, returning its metadata afterwards."""
        doc = _doc(text)
        result = (extractor or self.extractor).process_docs([doc],
                                                            self.query)
        self.assertIs(result[0], doc)
        return doc, doc.metadata

    # ========== Configuration tests ==========

    def test_default_configuration(self):
        """Defaults: 20-char paragraph minimum, the five documented cue
        weights, skeleton stamping off."""
        ex = TopicSentenceExtractor()
        self.assertEqual(ex.min_paragraph_chars, 20)
        self.assertEqual(ex.first_bonus, 2.0)
        self.assertEqual(ex.last_bonus, 0.5)
        self.assertEqual(ex.length_band_bonus, 1.0)
        self.assertEqual(ex.rambling_penalty, 1.0)
        self.assertEqual(ex.signpost_bonus, 1.5)
        self.assertEqual(ex.copula_bonus, 0.5)
        self.assertFalse(ex.doc_skeleton)

    def test_initialize_by_component_configer(self):
        """YAML-provided parameters are applied on initialization."""
        configer = self._create_configer({
            'name': 'topic_sentence_extractor',
            'description': 'topic sentence extractor',
            'min_paragraph_chars': 5,
            'first_bonus': 3,
            'last_bonus': 0,
            'length_band_bonus': 2.0,
            'rambling_penalty': 0.5,
            'signpost_bonus': 1,
            'copula_bonus': 0,
            'doc_skeleton': True,
        })
        ex = TopicSentenceExtractor()
        ex._initialize_by_component_configer(configer)
        self.assertEqual(ex.min_paragraph_chars, 5)
        self.assertEqual(ex.first_bonus, 3.0)
        self.assertEqual(ex.last_bonus, 0.0)
        self.assertEqual(ex.length_band_bonus, 2.0)
        self.assertEqual(ex.rambling_penalty, 0.5)
        self.assertEqual(ex.signpost_bonus, 1.0)
        self.assertEqual(ex.copula_bonus, 0.0)
        self.assertTrue(ex.doc_skeleton)
        self.assertEqual(ex.name, 'topic_sentence_extractor')

    def test_invalid_configuration_raises(self):
        """Negative, non-numeric or boolean weights and a bad paragraph
        minimum all fail at load time."""
        base = {
            'name': 't', 'description': 'd',
            'min_paragraph_chars': 20,
            'first_bonus': 2.0, 'last_bonus': 0.5,
            'length_band_bonus': 1.0, 'rambling_penalty': 1.0,
            'signpost_bonus': 1.5, 'copula_bonus': 0.5,
            'doc_skeleton': False,
        }
        for key, value in (
            ('min_paragraph_chars', -1),
            ('min_paragraph_chars', 2.5),
            ('min_paragraph_chars', True),
            ('first_bonus', -0.5),
            ('last_bonus', -1),
            ('length_band_bonus', -2),
            ('rambling_penalty', -0.1),
            ('signpost_bonus', -1.5),
            ('copula_bonus', -0.5),
            ('first_bonus', 'big'),
            ('signpost_bonus', True),
            ('copula_bonus', [1]),
        ):
            config = dict(base, **{key: value})
            with self.assertRaises(ValueError, msg=f"{key}={value!r}"):
                TopicSentenceExtractor()._initialize_by_component_configer(
                    self._create_configer(config))

    # ========== Position cue tests ==========

    def test_first_position_bonus(self):
        """Three identical-shape in-band sentences: the first wins with
        exactly first(2.0) + band(1.0) = 3.0."""
        text = " ".join([
            _fit("Plain filler alpha ", 80),
            _fit("Plain filler beta ", 80),
            _fit("Plain filler gamma ", 80),
        ])
        _, meta = self._run(text)
        entries = meta["topic_sentences"]
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["sentence_index"], 0)
        self.assertEqual(entries[0]["score"], 3.0)

    def test_first_bonus_is_decisive(self):
        """With the first bonus zeroed the in-band sentences tie at 1.0
        and the last one breaks it via its +0.5."""
        ex = TopicSentenceExtractor()
        ex.first_bonus = 0.0
        text = " ".join([
            _fit("Plain filler alpha ", 80),
            _fit("Plain filler beta ", 80),
            _fit("Plain filler gamma ", 80),
        ])
        _, meta = self._run(text, ex)
        entry = meta["topic_sentences"][0]
        # s0 = 1.0 (band), s1 = 1.0 (band), s2 = 1.0 + 0.5 (last)
        self.assertEqual(entry["sentence_index"], 2)
        self.assertEqual(entry["score"], 1.5)

    def test_last_position_bonus(self):
        """With the first bonus removed, a featureless short sentence
        loses to an equally featureless last sentence (0.0 vs 0.5)."""
        ex = TopicSentenceExtractor()
        ex.first_bonus = 0.0
        text = " ".join([
            _fit("Plain filler alpha ", 30),
            _fit("Plain filler beta ", 30),
        ])
        _, meta = self._run(text, ex)
        entry = meta["topic_sentences"][0]
        self.assertEqual(entry["sentence_index"], 1)
        self.assertEqual(entry["score"], 0.5)

    # ========== Length cue tests ==========

    def test_length_band_boundaries(self):
        """Single-sentence paragraphs at the band edges: base 2.5 (first
        + last), +1.0 inside 40..120, -1.0 above 250. Verified edges:
        39 -> 2.5, 40 -> 3.5, 120 -> 3.5, 121 -> 2.5, 250 -> 2.5,
        251 -> 1.5."""
        lengths = [39, 40, 120, 121, 250, 251]
        expected = [2.5, 3.5, 3.5, 2.5, 2.5, 1.5]
        text = "\n\n".join(_fit("Plain filler ", n) for n in lengths)
        _, meta = self._run(text)
        entries = meta["topic_sentences"]
        self.assertEqual([e["paragraph_index"] for e in entries],
                         list(range(6)))
        self.assertEqual([e["score"] for e in entries], expected)

    def test_length_band_decides_winner(self):
        """Without the first bonus, an out-of-band opener (0.0) loses to
        an in-band closer (0.5 + 1.0)."""
        ex = TopicSentenceExtractor()
        ex.first_bonus = 0.0
        text = " ".join([
            _fit("Plain filler alpha ", 39),
            _fit("Plain filler beta ", 40),
        ])
        _, meta = self._run(text, ex)
        entry = meta["topic_sentences"][0]
        self.assertEqual(entry["sentence_index"], 1)
        self.assertEqual(entry["score"], 1.5)

    def test_rambling_penalty_decides_winner(self):
        """Default weights: a 300-char rambling opener (2.0 - 1.0 = 1.0)
        loses to an in-band closer (0.5 + 1.0 = 1.5)."""
        text = " ".join([
            _fit("Plain rambling filler ", 300),
            _fit("Plain steady filler ", 80),
        ])
        _, meta = self._run(text)
        entry = meta["topic_sentences"][0]
        self.assertEqual(entry["sentence_index"], 1)
        self.assertEqual(entry["score"], 1.5)

    def test_single_sentence_paragraph(self):
        """A lone sentence is both first and last: 2.0 + 0.5 + band."""
        text = _fit("Plain filler ", 80)
        _, meta = self._run(text)
        entry = meta["topic_sentences"][0]
        self.assertEqual(entry["sentence_index"], 0)
        self.assertEqual(entry["score"], 3.5)

    # ========== Signpost cue tests ==========

    def test_signpost_openers(self):
        """In-band 60-char single-sentence paragraphs: each documented
        opener adds exactly +1.5 over the 3.5 baseline; 'Those...' and
        'Here you...' are deliberate non-matches."""
        baseline = _fit("Plain filler ", 60)
        openers = [
            _fit("This finding ", 60),
            _fit("These findings ", 60),
            _fit("Here we report ", 60),
            _fit("In this paper we ", 60),
            _fit("this lower case ", 60),
        ]
        non_matches = [
            _fit("Those findings ", 60),
            _fit("Here you see ", 60),
        ]
        paragraphs = [baseline] + openers + non_matches
        _, meta = self._run("\n\n".join(paragraphs))
        entries = meta["topic_sentences"]
        self.assertEqual(len(entries), len(paragraphs))
        scores = [e["score"] for e in entries]
        self.assertEqual(scores[0], 3.5)
        for score in scores[1:1 + len(openers)]:
            self.assertEqual(score, 5.0)
        for score in scores[1 + len(openers):]:
            self.assertEqual(score, 3.5)

    # ========== Copula cue tests ==========

    def test_copula_bonus(self):
        """Verified natural sentences: 'is a' (50 chars), 'are' (49) and
        是指 (34) each add +0.5 over a copula-free baseline (47)."""
        text = "\n\n".join([
            "A vector store is a database built for embeddings.",   # 50
            "Vector stores keep embeddings on disk reliably.",      # 47
            "The results are reproducible across random seeds.",    # 49
            "知识库是指经过清洗、切分并建立索引的结构化语料集合，可用于检索增强。",  # 34
        ])
        _, meta = self._run(text)
        scores = [e["score"] for e in meta["topic_sentences"]]
        self.assertEqual(scores, [4.0, 3.5, 4.0, 3.0])

    # ========== Combined arithmetic / tie tests ==========

    def test_stacked_cues_beat_position(self):
        """A middle sentence with signpost + copula + band (3.0) beats a
        featureless first (2.0) and last (0.5)."""
        text = " ".join([
            _fit("Plain filler alpha ", 30),                       # 2.0
            "This method is a practical default for offline runs.",  # 3.0
            _fit("Plain filler gamma ", 30),                       # 0.5
        ])
        _, meta = self._run(text)
        entry = meta["topic_sentences"][0]
        self.assertEqual(entry["sentence_index"], 1)
        self.assertEqual(entry["score"], 3.0)
        self.assertEqual(entry["text"],
                         "This method is a practical default for offline runs.")

    def test_tie_goes_to_earliest(self):
        """Default weights, hand-built 28-char tie: featureless first
        (2.0) vs signpost + copula middle (1.5 + 0.5 = 2.0, a true
        middle sentence in a 3-sentence paragraph) — the earliest
        sentence wins."""
        text = " ".join([
            _fit("Plain filler ", 28),          # first: 2.0
            "This settled setup is a tie.",      # 1.5 + 0.5 = 2.0
            _fit("Plain filler ", 28),          # last: 0.5
        ])
        _, meta = self._run(text)
        entry = meta["topic_sentences"][0]
        self.assertEqual(entry["sentence_index"], 0)
        self.assertEqual(entry["score"], 2.0)

    def test_tie_first_against_last(self):
        """With last_bonus raised to 2.0, three in-band sentences score
        3.0 / 1.0 / 3.0 — the tie resolves to the earliest."""
        ex = TopicSentenceExtractor()
        ex.last_bonus = 2.0
        text = " ".join([
            _fit("Plain filler alpha ", 80),   # 2.0 + 1.0 = 3.0
            _fit("Plain filler beta ", 80),    # 1.0
            _fit("Plain filler gamma ", 80),   # 2.0 + 1.0 = 3.0
        ])
        _, meta = self._run(text, ex)
        entry = meta["topic_sentences"][0]
        self.assertEqual(entry["sentence_index"], 0)
        self.assertEqual(entry["score"], 3.0)

    # ========== Paragraph admission tests ==========

    def test_min_paragraph_chars_skips_short(self):
        """A 10-char paragraph is skipped and leaves an index gap; the
        60-char paragraph after it is analysed with paragraph_index 1."""
        text = "Short one.\n\n" + _fit("Plain filler ", 60)
        _, meta = self._run(text)
        entries = meta["topic_sentences"]
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["paragraph_index"], 1)
        self.assertEqual(meta["topic_count"], 1)

    def test_min_paragraph_chars_boundary(self):
        """Exactly 20 trimmed characters are analysed; 19 are not."""
        _, meta = self._run(_fit("A", 20))
        self.assertEqual(meta["topic_count"], 1)
        _, meta = self._run(_fit("A", 19))
        self.assertEqual(meta["topic_count"], 0)
        self.assertEqual(meta["topic_sentences"], [])

    def test_min_paragraph_chars_override_admits_short(self):
        """A configured minimum of 5 admits the 10-char paragraph."""
        ex = TopicSentenceExtractor()
        ex.min_paragraph_chars = 5
        _, meta = self._run("Short one.", ex)
        self.assertEqual(meta["topic_count"], 1)

    # ========== Skeleton / cap tests ==========

    def test_skeleton_disabled_by_default(self):
        """No 'skeleton' key unless doc_skeleton is enabled."""
        _, meta = self._run(_fit("Plain filler ", 60))
        self.assertNotIn("skeleton", meta)

    def test_skeleton_join(self):
        """doc_skeleton joins the topic sentences with ' … '."""
        ex = TopicSentenceExtractor()
        ex.doc_skeleton = True
        paragraphs = [
            _fit("Plain filler alpha ", 60),
            _fit("Plain filler beta ", 60),
            _fit("Plain filler gamma ", 60),
        ]
        _, meta = self._run("\n\n".join(paragraphs), ex)
        topics = [e["text"] for e in meta["topic_sentences"]]
        self.assertEqual(meta["skeleton"], " … ".join(topics))

    def test_skeleton_empty_without_paragraphs(self):
        """A document with nothing to analyse gets an empty skeleton."""
        ex = TopicSentenceExtractor()
        ex.doc_skeleton = True
        _, meta = self._run("   \n\n  ", ex)
        self.assertEqual(meta["skeleton"], "")
        self.assertEqual(meta["topic_sentences"], [])
        self.assertEqual(meta["topic_count"], 0)

    def test_cap_and_uncapped_count(self):
        """60 analysable paragraphs yield 50 capped entries, uncapped
        topic_count 60, first-50 paragraph indices and a 50-part
        skeleton."""
        ex = TopicSentenceExtractor()
        ex.doc_skeleton = True
        text = "\n\n".join(_fit(f"Paragraph {i} filler ", 40)
                           for i in range(60))
        _, meta = self._run(text, ex)
        entries = meta["topic_sentences"]
        self.assertEqual(len(entries), 50)
        self.assertEqual(meta["topic_count"], 60)
        self.assertEqual([e["paragraph_index"] for e in entries],
                         list(range(50)))
        self.assertEqual(meta["skeleton"].count(" … "), 49)

    # ========== CJK tests ==========

    def test_cjk_extraction(self):
        """A Chinese paragraph: the 本文 opener (2.0 + 1.5 = 3.5) beats
        the 是指 middle (0.5) and the plain closer (0.5). All three
        sentences are under the 40-char band threshold."""
        first = "本文提出了一种面向知识库的主题句抽取方法，无需模型即可运行。"  # 30
        middle = "该方法是指对段落中每个句子打分并选出得分最高者的完整流程。"    # 29
        last = "后续工作将覆盖更多语言与更长的段落语料。"                      # 20
        _, meta = self._run("".join([first, middle, last]))
        entry = meta["topic_sentences"][0]
        self.assertEqual(entry["sentence_index"], 0)
        self.assertEqual(entry["score"], 3.5)
        self.assertEqual(entry["text"], first)

    def test_cjk_section_opener(self):
        """本节 is a signpost too: a 25-char single-sentence paragraph
        scores 2.5 + 1.5 = 4.0."""
        text = "本节介绍评分规则与实现细节，并提供完整的示例说明。"  # 25
        _, meta = self._run(text)
        entry = meta["topic_sentences"][0]
        self.assertEqual(entry["score"], 4.0)
        self.assertEqual(entry["text"], text)

    # ========== Pass-through / immutability tests ==========

    def test_empty_documents_pass_through(self):
        """Empty, whitespace-only and None texts stamp empty findings
        and never drop or reorder documents."""
        docs = [_doc(""), _doc("   \n\n  ")]
        none_doc = _doc("x")
        none_doc.text = None
        docs.append(none_doc)
        ex = TopicSentenceExtractor()
        ex.doc_skeleton = True
        result = ex.process_docs(list(docs), self.query)
        self.assertEqual(len(result), 3)
        for original, kept in zip(docs, result):
            self.assertIs(kept, original)
            self.assertEqual(kept.metadata["topic_sentences"], [])
            self.assertEqual(kept.metadata["topic_count"], 0)
            self.assertEqual(kept.metadata["skeleton"], "")

    def test_text_untouched_and_metadata_copied(self):
        """Existing metadata survives, the caller's original mapping is
        never mutated in place, and the text is untouched."""
        original_meta = {"keep": "me"}
        doc = _doc(_fit("Plain filler ", 60), keep="me")
        doc.metadata = original_meta
        before = doc.text
        self.extractor.process_docs([doc], self.query)
        self.assertEqual(doc.text, before)
        self.assertEqual(doc.metadata["keep"], "me")
        self.assertIn("topic_sentences", doc.metadata)
        self.assertNotIn("topic_sentences", original_meta)

    def test_spans_reconstruct_sentences(self):
        """Every entry's span slices the exact sentence text out of the
        untouched document text."""
        text = "\n\n".join([
            " ".join([
                _fit("Plain filler alpha ", 30),
                "This method is a practical default for offline runs.",
                _fit("Plain filler gamma ", 30),
            ]),
            "Short one.",
            "本文提出了一种面向知识库的主题句抽取方法，无需模型即可运行。"
            "该方法是指对段落中每个句子打分并选出得分最高者的完整流程。",
        ])
        doc, meta = self._run(text)
        self.assertEqual(doc.text, text)
        self.assertEqual(meta["topic_count"], 2)
        for entry in meta["topic_sentences"]:
            span = entry["span"]
            self.assertEqual(text[span["start"]:span["end"]], entry["text"])

    def test_determinism(self):
        """Two fresh documents with identical text receive identical
        metadata, and re-processing the same document is stable."""
        text = "\n\n".join([
            "This method is a practical default for offline runs. "
            + _fit("Plain filler ", 60),
            "知识库是指经过清洗、切分并建立索引的结构化语料集合，可用于检索增强。",
        ])
        _, first_meta = self._run(text)
        doc, second_meta = self._run(text)
        self.assertEqual(first_meta, second_meta)
        self.extractor.process_docs([doc], self.query)
        self.assertEqual(doc.metadata, second_meta)

    # ========== Sentence segmentation guards ==========

    def test_sentence_segmentation_guards(self):
        """Abbreviations, initials, decimals, ellipses, closing quotes,
        punctuation husks and CJK terminal runs all split correctly."""
        cases = [
            ("Dr. Smith arrived on time. The meeting began.",
             ["Dr. Smith arrived on time.", "The meeting began."]),
            ("J. K. Rowling wrote seven books.",
             ["J. K. Rowling wrote seven books."]),
            ("The value 3.14 approximates pi.",
             ["The value 3.14 approximates pi."]),
            ("Wait... then it stopped.",
             ["Wait...", "then it stopped."]),
            ('He said "stop." Then everyone sat.',
             ['He said "stop."', "Then everyone sat."]),
            ("Great! ?", ["Great!"]),
            ("真的吗？！我带了伞。", ["真的吗？！", "我带了伞。"]),
        ]
        for text, expected in cases:
            sentences = self.extractor._sentences(text, 0)
            self.assertEqual([body for _, _, body in sentences], expected,
                             msg=text)
            for start, end, body in sentences:
                self.assertEqual(text[start:end], body)


if __name__ == "__main__":
    unittest.main()
