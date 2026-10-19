# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @FileName: test_question_detector.py

import unittest

from agentuniverse.agent.action.knowledge.doc_processor.question_detector import QuestionDetector
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer

# Nine sentences: five wh questions (What/Why/How/Can) and five
# declaratives. Hand-verified: 9 total sentences, 4 questions, ratio 4/9.
EN_MIXED = (
    "What is agentUniverse? It is a framework for agents. "
    "Why use it? Teams build multi-agent applications faster. "
    "How do I start? Install it with pip. "
    "Can I extend it? Yes, plugins cover many cases. "
    "The docs explain the rest."
)

# Five CJK sentences: one wh question (哪), one tagged question (是不是),
# three declaratives. Hand-verified: 5 total, 2 questions, ratio 0.4.
ZH_MIXED = (
    "今天天气很好。你去哪里吃饭？我不知道。"
    "这是不是一家新餐厅？我们试试看吧。"
)

# One sentence per English opener — every single one is a wh question.
EN_OPENER_SENTENCES = (
    "What is it? Why not? How so? When did it happen? Where is the file? "
    "Who told you? Which one works? Whose key is this? Is it ready? "
    "Are they here? Do you agree? Does it scale? Did she call? "
    "Can we start? Could you help? Would that work? Should we wait? "
    "Will it finish?"
)
EN_OPENERS = (
    "what", "why", "how", "when", "where", "who", "which", "whose",
    "is", "are", "do", "does", "did", "can", "could", "would", "should",
    "will",
)

# Abbreviations, initials, decimals and ellipses must never split a
# sentence. Hand-verified: exactly 6 sentences, none of them questions.
ABBREV_TEXT = (
    "Dr. Smith asked about the results. Ms. Lee replied quickly. "
    "Prof. Wang disagreed. See e.g. the appendix. J. K. Rowling wrote it. "
    "The value is 3.14 exactly."
)


def _doc(text: str, **metadata) -> Document:
    """Build a Document carrying `text` and optional metadata."""
    return Document(text=text, metadata=dict(metadata) or None)


class TestQuestionDetector(unittest.TestCase):
    """Comprehensive test suite for QuestionDetector."""

    def setUp(self):
        self.detector = QuestionDetector()
        self.query = Query(query_str="faq mining")

    def _create_configer(self, config_dict):
        """Create a ComponentConfiger from a plain dictionary."""
        cfg = Configer()
        cfg.value = config_dict
        configer = ComponentConfiger()
        configer.load_by_configer(cfg)
        return configer

    # ========== Initialization tests ==========

    def test_default_configuration(self):
        """Defaults: cap 50, one-word minimum, 'questions' /
        'question_count' / 'question_ratio' metadata keys."""
        d = QuestionDetector()
        self.assertEqual(d.max_questions, 50)
        self.assertEqual(d.min_words, 1)
        self.assertEqual(d.questions_key, "questions")
        self.assertEqual(d.count_key, "question_count")
        self.assertEqual(d.ratio_key, "question_ratio")

    def test_initialize_by_component_configer(self):
        """YAML-provided parameters are applied on initialization."""
        configer = self._create_configer({
            'name': 'question_detector',
            'description': 'question detector',
            'max_questions': 5,
            'min_words': 2,
            'questions_key': 'qs',
            'count_key': 'qc',
            'ratio_key': 'qr',
        })
        d = QuestionDetector()
        d._initialize_by_component_configer(configer)
        self.assertEqual(d.max_questions, 5)
        self.assertEqual(d.min_words, 2)
        self.assertEqual(d.questions_key, "qs")
        self.assertEqual(d.count_key, "qc")
        self.assertEqual(d.ratio_key, "qr")
        self.assertEqual(d.name, "question_detector")

    def test_invalid_configuration_raises(self):
        """Negative / fractional / boolean numerics and non-string keys
        all fail eagerly at load time."""
        base = {
            'name': 'd', 'description': 'd',
            'max_questions': 50, 'min_words': 1,
            'questions_key': 'questions', 'count_key': 'question_count',
            'ratio_key': 'question_ratio',
        }
        for key, value in (
            ('max_questions', -1),
            ('max_questions', 2.5),
            ('max_questions', True),
            ('min_words', 0),
            ('min_words', -3),
            ('min_words', 1.5),
            ('min_words', True),
            ('questions_key', 5),
            ('count_key', ['x']),
            ('ratio_key', {}),
        ):
            config = dict(base, **{key: value})
            with self.assertRaises(ValueError, msg=f"{key}={value!r}"):
                QuestionDetector()._initialize_by_component_configer(
                    self._create_configer(config))

    # ========== English wh questions ==========

    def test_all_english_openers_detected(self):
        """Every interrogative opener in the design list yields a wh hit
        whose opener is the lowercased first word."""
        doc = _doc(EN_OPENER_SENTENCES)
        result = self.detector.process_docs([doc], self.query)

        self.assertEqual(result[0].metadata["question_count"], 18)
        self.assertEqual(result[0].metadata["question_ratio"], 1.0)
        hits = result[0].metadata["questions"]
        self.assertEqual([h["opener"] for h in hits], list(EN_OPENERS))
        self.assertTrue(all(h["kind"] == "wh" for h in hits))

    def test_english_opener_without_question_mark(self):
        """Opener-based detection needs no terminal '?' — imperative-
        shaped 'How to configure this.' is still a wh question."""
        doc = _doc("How to configure this. Set the port next.")
        result = self.detector.process_docs([doc], self.query)
        self.assertEqual(result[0].metadata["question_count"], 1)
        hit = result[0].metadata["questions"][0]
        self.assertEqual(hit["kind"], "wh")
        self.assertEqual(hit["opener"], "how")
        self.assertEqual(hit["text"], "How to configure this.")

    def test_english_opener_only_at_sentence_start(self):
        """'what' mid-sentence is reportage, not a question; openers must
        anchor the first word (even after a leading quote)."""
        doc = _doc("Dr. Smith asked what happened. \"Why now?\" she added.")
        result = self.detector.process_docs([doc], self.query)
        self.assertEqual(result[0].metadata["question_count"], 1)
        hit = result[0].metadata["questions"][0]
        self.assertEqual(hit["opener"], "why")
        self.assertEqual(hit["text"], "\"Why now?\"")

    # ========== Chinese wh questions ==========

    def test_chinese_openers_matched_anywhere(self):
        """Chinese has no word boundaries or capitals, so interrogative
        tokens are matched inside the sentence: 这是什么？ reports 什么."""
        cases = {
            "为什么要这样做？": "为什么",
            "这是什么？": "什么",
            "怎么回事？": "怎么",
            "如何配置它。": "如何",
            "多少钱？": "多少",
            "几个人？": "几",
            "哪里有问题？": "哪",
        }
        for text, opener in cases.items():
            doc = _doc(text)
            result = self.detector.process_docs([doc], self.query)
            hits = result[0].metadata["questions"]
            self.assertEqual(len(hits), 1, text)
            self.assertEqual(hits[0]["kind"], "wh", text)
            self.assertEqual(hits[0]["opener"], opener, text)

    def test_why_narrows_over_shi_me(self):
        """为什么 wins over the 什么 nested at a later position."""
        doc = _doc("为什么要这样做？")
        hit = self.detector.process_docs([doc], self.query)[0] \
            .metadata["questions"][0]
        self.assertEqual(hit["opener"], "为什么")

    # ========== Polar questions ==========

    def test_polar_question_mark_ending(self):
        """Statement-shaped sentences ending in ? / ？ are polar with no
        opener."""
        for text in ("She left?", "你来了？"):
            doc = _doc(text)
            result = self.detector.process_docs([doc], self.query)
            hits = result[0].metadata["questions"]
            self.assertEqual(len(hits), 1, text)
            self.assertEqual(hits[0]["kind"], "polar", text)
            self.assertIsNone(hits[0]["opener"], text)

    def test_ma_suffix_polar(self):
        """Chinese statements ending with 吗 are polar questions even
        under 。 or no punctuation at all."""
        for text in ("你吃了吗。", "这是你的书吗？", "明天有空吗"):
            doc = _doc(text)
            result = self.detector.process_docs([doc], self.query)
            hits = result[0].metadata["questions"]
            self.assertEqual(len(hits), 1, text)
            self.assertEqual(hits[0]["kind"], "polar", text)
            self.assertIsNone(hits[0]["opener"], text)

    # ========== Tagged questions ==========

    def test_english_right_tag(self):
        """'..., right?' is tagged with opener 'right' — the question
        mark is required, 'right.' stays declarative."""
        doc = _doc("It's fixed now, right?")
        result = self.detector.process_docs([doc], self.query)
        hit = result[0].metadata["questions"][0]
        self.assertEqual(hit["kind"], "tagged")
        self.assertEqual(hit["opener"], "right")

        doc = _doc("It works, right.")
        result = self.detector.process_docs([doc], self.query)
        self.assertEqual(result[0].metadata["question_count"], 0)

    def test_chinese_tag_markers(self):
        """是不是 anywhere and 对吗 at the end are tagged questions with
        no question mark needed."""
        cases = {
            "这是不是你的伞。": "是不是",
            "这样做是对的，对吗。": "对吗",
            "这样做是对的，对吗？": "对吗",
        }
        for text, marker in cases.items():
            doc = _doc(text)
            result = self.detector.process_docs([doc], self.query)
            hits = result[0].metadata["questions"]
            self.assertEqual(len(hits), 1, text)
            self.assertEqual(hits[0]["kind"], "tagged", text)
            self.assertEqual(hits[0]["opener"], marker, text)

    def test_kind_priority_wh_over_tagged(self):
        """An opener (wh) outranks an inline marker in the same
        sentence."""
        for text in ("What is this, right?", "这是不是什么新花样？"):
            doc = _doc(text)
            result = self.detector.process_docs([doc], self.query)
            hit = result[0].metadata["questions"][0]
            self.assertEqual(hit["kind"], "wh", text)

    # ========== Segmentation guards ==========

    def test_abbreviations_initials_and_decimals_do_not_split(self):
        """Dr./Ms./Prof./e.g./J. K./3.14 leave the sentence whole:
        exactly 6 sentences, no questions."""
        doc = _doc(ABBREV_TEXT)
        result = self.detector.process_docs([doc], self.query)
        self.assertEqual(result[0].metadata["question_count"], 0)
        self.assertEqual(result[0].metadata["question_ratio"], 0.0)
        self.assertEqual(result[0].metadata["questions"], [])
        self.assertEqual(len(self.detector._sentences(ABBREV_TEXT)), 6)

    def test_ellipsis_splits_once_at_final_dot(self):
        """'...' splits only at its last dot; the following sentence
        starts at 'then' / 'what'."""
        doc = _doc("He paused... then he spoke.")
        result = self.detector.process_docs([doc], self.query)
        self.assertEqual(len(result[0].metadata["questions"]), 0)
        self.assertEqual(len(self.detector._sentences(
            "He paused... then he spoke.")), 2)

        doc = _doc("Wait... what happened?")
        result = self.detector.process_docs([doc], self.query)
        self.assertEqual(result[0].metadata["question_count"], 1)
        hit = result[0].metadata["questions"][0]
        self.assertEqual(hit["text"], "what happened?")
        self.assertEqual(hit["opener"], "what")

    def test_terminal_punctuation_run_stays_in_one_sentence(self):
        """'？！' terminates one sentence, not two; the 吗 makes it polar."""
        doc = _doc("真的吗？！")
        result = self.detector.process_docs([doc], self.query)
        self.assertEqual(result[0].metadata["question_count"], 1)
        hit = result[0].metadata["questions"][0]
        self.assertEqual(hit["text"], "真的吗？！")
        self.assertEqual(hit["kind"], "polar")

    def test_cjk_sentence_boundaries(self):
        """。！？ split Chinese text; declaratives are not questions."""
        doc = _doc("今天下雨了！他没带伞。怎么办？只好打车。")
        result = self.detector.process_docs([doc], self.query)
        self.assertEqual(result[0].metadata["question_count"], 1)
        self.assertEqual(result[0].metadata["questions"][0]["kind"], "wh")

    # ========== Mixed-document aggregates ==========

    def test_english_mixed_document_counts_and_ratio(self):
        """Hand-verified: 9 sentences, 4 questions, ratio 4/9."""
        doc = _doc(EN_MIXED)
        result = self.detector.process_docs([doc], self.query)
        meta = result[0].metadata
        self.assertEqual(meta["question_count"], 4)
        self.assertAlmostEqual(meta["question_ratio"], 4 / 9)
        self.assertEqual([h["opener"] for h in meta["questions"]],
                         ["what", "why", "how", "can"])

    def test_chinese_mixed_document_counts_and_ratio(self):
        """Hand-verified: 5 sentences, 2 questions (wh + tagged),
        ratio 0.4."""
        doc = _doc(ZH_MIXED)
        result = self.detector.process_docs([doc], self.query)
        meta = result[0].metadata
        self.assertEqual(meta["question_count"], 2)
        self.assertAlmostEqual(meta["question_ratio"], 0.4)
        self.assertEqual([h["kind"] for h in meta["questions"]],
                         ["wh", "tagged"])

    def test_ratio_third_and_tail_without_punctuation(self):
        """A final sentence lacking terminal punctuation still counts:
        3 sentences / 1 question -> 1/3; here the tail is the question."""
        doc = _doc("Nobody knows why. It stayed quiet. What happened")
        result = self.detector.process_docs([doc], self.query)
        meta = result[0].metadata
        self.assertEqual(meta["question_count"], 1)
        self.assertAlmostEqual(meta["question_ratio"], 1 / 3)
        self.assertEqual(meta["questions"][0]["text"], "What happened")

    def test_declarative_only_documents(self):
        """Pure declaratives pass through with empty hits, count 0 and
        ratio 0.0 — English and Chinese alike."""
        for text in ("The sky is blue. I like tea.", "天空很蓝。我喜欢喝茶。"):
            doc = _doc(text)
            result = self.detector.process_docs([doc], self.query)
            meta = result[0].metadata
            self.assertEqual(meta["questions"], [], text)
            self.assertEqual(meta["question_count"], 0, text)
            self.assertEqual(meta["question_ratio"], 0.0, text)

    # ========== Span invariants ==========

    def test_spans_reconstruct_text_exactly(self):
        """text == document.text[start:end] for every hit, spans are
        ordered, non-overlapping and inside the document."""
        for text in (EN_MIXED, ZH_MIXED, ABBREV_TEXT,
                     '"Are you sure?" she asked.'):
            doc = _doc(text)
            result = self.detector.process_docs([doc], self.query)
            previous_end = 0
            for hit in result[0].metadata["questions"]:
                start, end = hit["span"]
                self.assertEqual(text[start:end], hit["text"], text)
                self.assertGreaterEqual(start, previous_end, text)
                self.assertLess(start, end, text)
                self.assertLessEqual(end, len(text), text)
                previous_end = end

    def test_hit_structure(self):
        """Every hit carries exactly text / span / kind / opener with the
        documented types."""
        doc = _doc(EN_MIXED)
        result = self.detector.process_docs([doc], self.query)
        for hit in result[0].metadata["questions"]:
            self.assertEqual(set(hit), {"text", "span", "kind", "opener"})
            self.assertIsInstance(hit["text"], str)
            self.assertIsInstance(hit["span"], tuple)
            self.assertEqual(len(hit["span"]), 2)
            self.assertIn(hit["kind"], ("wh", "polar", "tagged"))
            self.assertTrue(hit["opener"] is None or
                            isinstance(hit["opener"], str))

    # ========== Cap and min_words ==========

    def test_max_questions_caps_list_not_count(self):
        """60 questions: the hit list is capped at the default 50 while
        question_count reports the true 60; order keeps the first hits."""
        doc = _doc("Why? " * 60)
        result = self.detector.process_docs([doc], self.query)
        meta = result[0].metadata
        self.assertEqual(meta["question_count"], 60)
        self.assertEqual(len(meta["questions"]), 50)
        self.assertEqual(meta["questions"][0]["text"], "Why?")
        self.assertEqual(meta["question_ratio"], 1.0)

        self.detector.max_questions = 5
        result = self.detector.process_docs([_doc("Why? " * 60)],
                                            self.query)
        self.assertEqual(len(result[0].metadata["questions"]), 5)
        self.assertEqual(result[0].metadata["question_count"], 60)

    def test_max_questions_zero_stamps_empty_list(self):
        """A cap of 0 stamps an empty list but keeps the real count."""
        self.detector.max_questions = 0
        doc = _doc("Why? Because.")
        result = self.detector.process_docs([doc], self.query)
        self.assertEqual(result[0].metadata["questions"], [])
        self.assertEqual(result[0].metadata["question_count"], 1)

    def test_min_words_default_keeps_single_word_questions(self):
        """With the default min_words=1 a lone 'Why?' (one word) counts,
        while a bare '?' (zero words) is not a sentence at all — it is
        ignored entirely, leaving exactly one sentence."""
        doc = _doc("Why? ? ?")
        result = self.detector.process_docs([doc], self.query)
        meta = result[0].metadata
        self.assertEqual(meta["question_count"], 1)
        self.assertEqual(len(meta["questions"]), 1)
        self.assertEqual(meta["question_ratio"], 1.0)

    def test_min_words_two_drops_short_segments(self):
        """min_words=2 ignores one-word segments entirely — neither
        sentence nor question, so the ratio stays defined."""
        self.detector.min_words = 2
        doc = _doc("Why? Because.")
        result = self.detector.process_docs([doc], self.query)
        meta = result[0].metadata
        self.assertEqual(meta["question_count"], 0)
        self.assertEqual(meta["question_ratio"], 0.0)

    # ========== Pipeline shape and metadata ==========

    def test_empty_batch_text_and_whitespace(self):
        """Empty batch returns []; empty / None / whitespace text stamps
        zeroed aggregates rather than failing."""
        self.assertEqual(self.detector.process_docs([], self.query), [])

        # The Document class requires an explicit id for None text.
        doc = Document(text=None, id="none-text", metadata=None)
        for text in ("", "   "):
            doc = _doc(text)
            result = self.detector.process_docs([doc], self.query)
            meta = result[0].metadata
            self.assertEqual(meta["questions"], [], repr(text))
            self.assertEqual(meta["question_count"], 0, repr(text))
            self.assertEqual(meta["question_ratio"], 0.0, repr(text))

    def test_documents_pass_through_untouched(self):
        """Text, id and order are unchanged; pre-existing metadata
        survives; stamps go through a copied mapping, never mutating the
        caller's original dict in place."""
        doc = _doc("What is it? Fine.", source="faq", rank=1)
        original_meta_ref = doc.metadata
        doc_id = doc.id

        result = self.detector.process_docs([doc], self.query)

        self.assertIs(result[0], doc)
        self.assertEqual(result[0].id, doc_id)
        self.assertEqual(result[0].text, "What is it? Fine.")
        self.assertEqual(doc.metadata["source"], "faq")
        self.assertEqual(doc.metadata["rank"], 1)
        self.assertNotIn("questions", original_meta_ref)
        self.assertIsNot(doc.metadata, original_meta_ref)

    def test_batch_documents_are_independent(self):
        """Each document is analysed on its own text; a question in one
        never leaks into another's metadata."""
        docs = [_doc("All quiet here."),
                _doc("What went wrong?"),
                _doc("很平静。")]
        result = self.detector.process_docs(docs, self.query)
        self.assertEqual([d.metadata["question_count"] for d in result],
                         [0, 1, 0])
        self.assertEqual(result[1].metadata["questions"][0]["kind"], "wh")

    def test_disabled_keys_stamp_nothing(self):
        """Empty key names disable each stamp independently."""
        self.detector.questions_key = ""
        self.detector.count_key = ""
        self.detector.ratio_key = ""
        doc = _doc("Why?", source="faq")
        result = self.detector.process_docs([doc], self.query)
        self.assertEqual(result[0].metadata, {"source": "faq"})

    def test_deterministic_across_runs(self):
        """Two detectors produce byte-identical hits and aggregates for
        the same input."""
        first = QuestionDetector().process_docs([_doc(EN_MIXED)],
                                                self.query)[0].metadata
        second = QuestionDetector().process_docs([_doc(EN_MIXED)],
                                                 self.query)[0].metadata
        self.assertEqual(first["questions"], second["questions"])
        self.assertEqual(first["question_count"], second["question_count"])
        self.assertEqual(first["question_ratio"], second["question_ratio"])

    # ========== Adversarial regression tests ==========

    def test_emphatic_question_exclamation_runs(self):
        """A question mark anywhere in the terminal punctuation run asks:
        'She left?!' and 'She left!?' are polar alike, English and
        Chinese; exclamation-only runs stay declarative."""
        for text in ("She left?!", "She left!?", "你来了？！",
                     "你来了！？", "真的吗？！"):
            doc = _doc(text)
            result = self.detector.process_docs([doc], self.query)
            hits = result[0].metadata["questions"]
            self.assertEqual(len(hits), 1, text)
            self.assertEqual(hits[0]["kind"], "polar", text)
            self.assertIsNone(hits[0]["opener"], text)

        for text in ("She left!", "Great!!", "太好了！", "走开！"):
            doc = _doc(text)
            result = self.detector.process_docs([doc], self.query)
            self.assertEqual(result[0].metadata["question_count"], 0, text)

    def test_all_openers_at_middle_and_unpunctuated_tail(self):
        """Every opener is recognised as a middle sentence and as the
        final sentence even when the terminal punctuation is missing."""
        for opener in EN_OPENERS:
            cap = opener.capitalize()
            doc = _doc(f"He nodded. {cap} it work? She smiled.")
            result = self.detector.process_docs([doc], self.query)
            hits = result[0].metadata["questions"]
            self.assertEqual(len(hits), 1, opener)
            self.assertEqual(hits[0]["opener"], opener)
            self.assertEqual(hits[0]["text"], f"{cap} it work?", opener)

            doc = _doc(f"He nodded. She smiled. {cap} it work")
            result = self.detector.process_docs([doc], self.query)
            hits = result[0].metadata["questions"]
            self.assertEqual(len(hits), 1, opener)
            self.assertEqual(hits[0]["opener"], opener)
            self.assertEqual(hits[0]["text"], f"{cap} it work", opener)

    def test_polar_vs_wh_verb_form(self):
        """'Does it work?' asks with an auxiliary (wh); 'It works?' is a
        statement with rising intonation (polar, no opener)."""
        doc = _doc("Does it work?")
        hit = self.detector.process_docs([doc], self.query)[0] \
            .metadata["questions"][0]
        self.assertEqual(hit["kind"], "wh")
        self.assertEqual(hit["opener"], "does")

        doc = _doc("It works?")
        hit = self.detector.process_docs([doc], self.query)[0] \
            .metadata["questions"][0]
        self.assertEqual(hit["kind"], "polar")
        self.assertIsNone(hit["opener"])

    def test_indirect_questions_not_matched(self):
        """Embedded/indirect questions are reportage, not questions:
        the interrogative word is not the first word, so none match."""
        for text in ("I asked what it is.", "He knows where she went.",
                     "Tell me why you care.", "I wonder if it works.",
                     "She asked whether he came.",
                     "She asked what time it is. I wonder why he left."):
            doc = _doc(text)
            result = self.detector.process_docs([doc], self.query)
            self.assertEqual(result[0].metadata["question_count"], 0, text)

    def test_ma_particle_versus_ba_particle(self):
        """Sentence-final 吗 asks (even under 。 or none); 吧 does not —
        but 吧 under a real question mark still asks, via polar."""
        for text in ("你吃了吗。", "你吃了吗", "这是你的书吗？"):
            doc = _doc(text)
            result = self.detector.process_docs([doc], self.query)
            hits = result[0].metadata["questions"]
            self.assertEqual(len(hits), 1, text)
            self.assertEqual(hits[0]["kind"], "polar", text)

        for text in ("我们走吧。", "快来看看吧！", "好吧，我知道了。",
                     "你说对吧。"):
            doc = _doc(text)
            result = self.detector.process_docs([doc], self.query)
            self.assertEqual(result[0].metadata["question_count"], 0, text)

        doc = _doc("你坐下吧？")
        result = self.detector.process_docs([doc], self.query)
        self.assertEqual(result[0].metadata["question_count"], 1)

    def test_semicolon_joined_questions_single_hit(self):
        """Semicolons are not sentence boundaries: two conceptually
        distinct questions joined by ';' yield exactly one wh hit whose
        span covers the whole sentence."""
        doc = _doc("Is this true; is that false?")
        result = self.detector.process_docs([doc], self.query)
        meta = result[0].metadata
        self.assertEqual(meta["question_count"], 1)
        self.assertEqual(meta["question_ratio"], 1.0)
        hit = meta["questions"][0]
        self.assertEqual(hit["kind"], "wh")
        self.assertEqual(hit["opener"], "is")
        self.assertEqual(hit["text"], "Is this true; is that false?")

    def test_hundred_sentence_corpus_against_reference(self):
        """A deterministic 100-sentence corpus with independently known
        labels: the count, the ratio and every hit's kind/text agree
        with the reference classification (list capped at 50 by
        default)."""
        patterns = (
            "What is item {i}?",             # wh
            "Why does item {i} fail?",       # wh
            "Item {i} works fine.",          # declarative
            "She tested item {i}?",          # polar
            "Item {i} is fixed, right?",     # tagged
            "他检查了第{i}个。",               # declarative
            "这是什么{i}？",                   # wh
            "Item {i} was delayed.",         # declarative
            "How did item {i} break?",       # wh
            "Can item {i} be saved?",        # wh
        )
        kinds = ("wh", "wh", None, "polar", "tagged", None, "wh",
                 None, "wh", "wh")
        corpus = [patterns[i % 10].format(i=i) for i in range(100)]
        expected = [(corpus[i], kinds[i % 10]) for i in range(100)
                    if kinds[i % 10] is not None]
        text = " ".join(corpus)

        doc = _doc(text)
        result = self.detector.process_docs([doc], self.query)
        meta = result[0].metadata
        self.assertEqual(meta["question_count"], len(expected))
        self.assertAlmostEqual(meta["question_ratio"],
                               len(expected) / 100.0)
        self.assertEqual(len(meta["questions"]), 50)  # default cap
        for hit, (exp_text, exp_kind) in zip(meta["questions"],
                                             expected):
            self.assertEqual(hit["text"], exp_text)
            self.assertEqual(hit["kind"], exp_kind)


if __name__ == '__main__':
    unittest.main()
