# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @FileName: test_question_type_classifier.py

import unittest

from agentuniverse.agent.action.knowledge.doc_processor.question_type_classifier import QuestionTypeClassifier
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer

# A declarative filler sentence used between questions in mixed texts.
FILLER = "The service restarted at noon."

# Long question body used to exercise the 100-character preview cap.
LONG_TAIL = "configuration " * 20


class TestQuestionTypeClassifier(unittest.TestCase):
    """Comprehensive offline test suite for QuestionTypeClassifier."""

    def setUp(self):
        self.classifier = QuestionTypeClassifier()
        self.query = Query(query_str="faq mining")

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #

    def _create_configer(self, config_dict):
        """Create a ComponentConfiger from a plain dictionary."""
        cfg = Configer()
        cfg.value = config_dict
        configer = ComponentConfiger()
        configer.load_by_configer(cfg)
        return configer

    def _run(self, text, classifier=None):
        """Process one document and return its metadata."""
        doc = Document(text=text)
        out = (classifier or self.classifier).process_docs([doc], self.query)
        self.assertIs(out[0], doc)
        return doc.metadata

    def _assert_single(self, text, expected_type, classifier=None):
        """Assert the text yields exactly one hit of the expected type."""
        meta = self._run(text, classifier)
        hits = meta["question_types"]
        self.assertEqual(len(hits), 1,
                         f"{text!r} should yield exactly one hit, got {hits}")
        self.assertEqual(hits[0]["type"], expected_type,
                         f"{text!r} typed {hits[0]['type']!r}, "
                         f"expected {expected_type!r}")
        self.assertEqual(meta["question_type_counts"], {expected_type: 1})
        self.assertEqual(meta["dominant_question_type"], expected_type)
        return hits[0]

    # ========== English per-type ground truths ==========

    def test_english_what(self):
        """what/what's openers and mid-sentence what map to what."""
        self._assert_single("What is the capital of France?", "what")
        self._assert_single("What's the time?", "what")

    def test_english_who(self):
        """who/whom/whose all fold into the who type."""
        self._assert_single("Who wrote this document?", "who")
        self._assert_single("Whom should I send it to?", "who")
        self._assert_single("Whose book is this?", "who")

    def test_english_when(self):
        self._assert_single("When does the meeting start?", "when")

    def test_english_where(self):
        self._assert_single("Where are the logs stored?", "where")

    def test_english_why(self):
        self._assert_single("Why did the build fail?", "why")

    def test_english_how(self):
        """Plain how (no many/much follow-up) maps to how."""
        self._assert_single("How does this work?", "how")

    def test_english_quantity(self):
        """how many / how much two-word look-ahead maps to quantity."""
        self._assert_single("How many users are active?", "quantity")
        self._assert_single("How much does it cost?", "quantity")

    def test_english_which(self):
        self._assert_single("Which option is the default?", "which")

    def test_english_yes_no_auxiliaries(self):
        """Every auxiliary opener yields a yes_no question."""
        cases = (
            "Is the service running?",
            "Are you ready?",
            "Do you take sugar?",
            "Does it work?",
            "Did you finish the report?",
            "Can you help me?",
            "Could you repeat that?",
            "Would you come tomorrow?",
            "Should we start now?",
            "Will it compile?",
        )
        for sentence in cases:
            self._assert_single(sentence, "yes_no")

    def test_english_choice_via_or(self):
        """Standalone ' or ' between alternatives with no wh maps to choice."""
        self._assert_single("Tea or coffee?", "choice")

    def test_english_terminal_fallback(self):
        """Statement-shaped questions with rising intonation fall back to yes_no."""
        self._assert_single("She left?", "yes_no")
        self._assert_single("真的？", "yes_no")

    def test_english_opener_without_question_mark(self):
        """A wh opener makes the sentence interrogative even under a full stop."""
        self._assert_single("How to configure this.", "how")

    def test_mid_sentence_wh_word(self):
        """A wh word need not be first: 'You did what?' is typed by 'what'."""
        hit = self._assert_single("You did what?", "what")
        self.assertEqual(hit["text"], "You did what?")

    # ========== Chinese per-type ground truths ==========

    def test_chinese_what(self):
        self._assert_single("你在说什么？", "what")

    def test_chinese_who(self):
        self._assert_single("谁来了？", "who")
        self._assert_single("这是谁的错？", "who")

    def test_chinese_when(self):
        self._assert_single("何时出发？", "when")
        self._assert_single("会议什么时候开始？", "when")

    def test_chinese_where(self):
        self._assert_single("钥匙放在哪里？", "where")
        self._assert_single("他去哪儿了？", "where")

    def test_chinese_why(self):
        self._assert_single("他为什么迟到？", "why")

    def test_chinese_how(self):
        self._assert_single("这件事怎么解决？", "how")
        self._assert_single("该如何配置？", "how")

    def test_chinese_quantity(self):
        self._assert_single("这本书多少钱？", "quantity")
        self._assert_single("几点开会？", "quantity")

    def test_chinese_which(self):
        self._assert_single("哪个方案更好？", "which")
        self._assert_single("哪些物品需要报关？", "which")

    def test_chinese_yes_no(self):
        """Final 吗 and the A-not-A form 是不是 yield yes_no."""
        self._assert_single("你会说英语吗？", "yes_no")
        self._assert_single("他是不是忘了？", "yes_no")

    def test_chinese_choice_via_haishi(self):
        self._assert_single("你要咖啡还是茶？", "choice")

    # ========== Two-word precedence ==========

    def test_two_word_beats_single_english(self):
        """'How many ...' is quantity, not how."""
        self._assert_single("How many people came to the party?", "quantity")
        self._assert_single("How many?", "quantity")
        self._assert_single("How much?", "quantity")
        # Without the quantity follow-up the plain how type applies.
        self._assert_single("How so?", "how")

    def test_two_word_beats_single_chinese(self):
        """什么时候 outranks the 什么 nested inside it; 为什么 outranks 什么."""
        self._assert_single("你什么时候到？", "when")
        self._assert_single("为什么会这样？", "why")

    def test_english_beats_chinese(self):
        """English wh evidence outranks Chinese tokens in mixed sentences."""
        self._assert_single("What is the 什么情况 here?", "what")

    def test_aux_initial_beats_or(self):
        """Documented priority: auxiliary-initial alternative questions are yes_no."""
        self._assert_single("Would you like tea or coffee?", "yes_no")

    # ========== Declaratives are skipped ==========

    def test_declaratives_not_reported(self):
        """Declarative sentences produce no hits and empty aggregates."""
        for text in (
            "The service restarted at noon.",
            "会议结束了。",
            "He wondered what she meant.",
            "You can use tea or honey.",
            "The flag is red or blue.",
        ):
            meta = self._run(text)
            self.assertEqual(meta["question_types"], [], text)
            self.assertEqual(meta["question_type_counts"], {}, text)
            self.assertIsNone(meta["dominant_question_type"], text)

    def test_abbreviation_guard_keeps_sentence_whole(self):
        """'Dr.' does not split; the whole declarative is skipped."""
        meta = self._run("Dr. Smith asked what happened.")
        self.assertEqual(meta["question_types"], [])

    def test_documented_zh_token_limits(self):
        """还是/几 inside declaratives are heuristic false positives, documented."""
        meta = self._run("还是算了。")
        self.assertEqual(meta["question_types"][0]["type"], "choice")
        meta = self._run("几乎所有人都到了。")
        self.assertEqual(meta["question_types"][0]["type"], "quantity")

    # ========== Mixed text: spans, counts, dominant ==========

    def test_mixed_text_hits_and_order(self):
        """Hits keep document order; spans slice the original text exactly."""
        text = "What is a vector? The answer follows. Why use one? 谁负责？ Done."
        meta = self._run(text)
        hits = meta["question_types"]
        self.assertEqual([h["type"] for h in hits],
                         ["what", "why", "who"])
        starts = [h["span"][0] for h in hits]
        self.assertEqual(starts, sorted(starts))
        for hit in hits:
            start, end = hit["span"]
            self.assertEqual(text[start:end], hit["text"])
        self.assertEqual(meta["question_type_counts"],
                         {"what": 1, "why": 1, "who": 1})

    def test_dominant_type_most_common(self):
        """The most frequent type wins outright."""
        text = ("What is it? Why now? What else? Why bother? "
                "How so? What next?")
        meta = self._run(text)
        self.assertEqual(meta["question_type_counts"],
                         {"what": 3, "why": 2, "how": 1})
        self.assertEqual(meta["dominant_question_type"], "what")

    def test_dominant_type_tie_alphabetical(self):
        """Ties break alphabetically: how < what, what < why."""
        meta = self._run("What is it? Why now? How so? What else? Why me?")
        # what: 2, why: 2 -> "what"
        self.assertEqual(meta["dominant_question_type"], "what")
        meta = self._run("Why now? How so? Why me? How come?")
        # why: 2, how: 2 -> "how"
        self.assertEqual(meta["dominant_question_type"], "how")

    def test_cap_limits_list_not_counts(self):
        """Default cap 50 truncates the list; counts stay uncapped."""
        text = " ".join(["What is it?"] * 60)
        meta = self._run(text)
        self.assertEqual(len(meta["question_types"]), 50)
        self.assertEqual(meta["question_type_counts"], {"what": 60})
        self.assertEqual(meta["dominant_question_type"], "what")

    def test_cap_zero_keeps_counts(self):
        """max_question_types 0 empties the list but keeps the aggregates."""
        self.classifier.max_question_types = 0
        meta = self._run("What is it? Why now?")
        self.assertEqual(meta["question_types"], [])
        self.assertEqual(meta["question_type_counts"], {"what": 1, "why": 1})
        self.assertEqual(meta["dominant_question_type"], "what")

    def test_preview_truncation(self):
        """text is the first 100 chars; the span covers the full sentence."""
        question = f"What about this {LONG_TAIL}setting?"
        self.assertGreater(len(question), 100)
        hit = self._assert_single(question, "what")
        self.assertEqual(len(hit["text"]), 100)
        self.assertEqual(hit["text"], question[:100])
        start, end = hit["span"]
        self.assertEqual(question[start:end], question)

    def test_min_words_filter(self):
        """min_words 2 drops single-word questions but keeps longer ones."""
        self.classifier.min_words = 2
        meta = self._run("Why? Why now? ？")
        self.assertEqual([h["text"] for h in meta["question_types"]],
                         ["Why now?"])

    def test_punctuation_only_segment_dropped(self):
        """A bare question mark is zero words and never a question."""
        meta = self._run("？")
        self.assertEqual(meta["question_types"], [])
        self.assertEqual(meta["question_type_counts"], {})

    # ========== Document hygiene ==========

    def test_batch_documents_stamped_independently(self):
        """Each document in a batch gets its own aggregates."""
        docs = [Document(text="What is it?"), Document(text=" Done.")]
        out = self.classifier.process_docs(docs, self.query)
        self.assertEqual(out[0].metadata["question_type_counts"], {"what": 1})
        self.assertEqual(out[1].metadata["question_types"], [])
        self.assertIsNone(out[1].metadata["dominant_question_type"])

    def test_existing_metadata_preserved_and_not_mutated(self):
        """Pre-existing metadata survives; the source mapping is not edited."""
        source = {"src": "faq"}
        doc = Document(text="What is it?", metadata=source)
        self.classifier.process_docs([doc], self.query)
        self.assertEqual(list(source.keys()), ["src"])
        self.assertEqual(doc.metadata["src"], "faq")
        self.assertEqual(doc.metadata["question_type_counts"], {"what": 1})

    def test_text_and_id_untouched(self):
        """Processing never rewrites text or id."""
        doc = Document(text="What is it? Why now?")
        text_before, id_before = doc.text, doc.id
        self.classifier.process_docs([doc], self.query)
        self.assertEqual(doc.text, text_before)
        self.assertEqual(doc.id, id_before)

    def test_empty_and_blank_documents(self):
        """Empty, blank and question-free documents stamp empty aggregates."""
        for text in ("", "   ", "No questions here at all."):
            meta = self._run(text)
            self.assertEqual(meta["question_types"], [])
            self.assertEqual(meta["question_type_counts"], {})
            self.assertIsNone(meta["dominant_question_type"])

    def test_empty_batch(self):
        """An empty batch returns an empty list."""
        self.assertEqual(self.classifier.process_docs([], self.query), [])

    # ========== Determinism ==========

    def test_deterministic_across_runs(self):
        """Two fresh classifiers produce identical metadata."""
        text = ("What is it? Why now? How many? Tea or coffee? "
                "谁来了？ 你会来吗？ Filler text. 什么时候开会？")
        first = self._run(text)
        second = self._run(text, classifier=QuestionTypeClassifier())
        self.assertEqual(first, second)

    # ========== Configuration ==========

    def test_default_configuration(self):
        """Defaults: cap 50, min_words 1, preview 100, standard keys."""
        c = QuestionTypeClassifier()
        self.assertEqual(c.max_question_types, 50)
        self.assertEqual(c.min_words, 1)
        self.assertEqual(c.preview_chars, 100)
        self.assertEqual(c.question_types_key, "question_types")
        self.assertEqual(c.counts_key, "question_type_counts")
        self.assertEqual(c.dominant_key, "dominant_question_type")

    def test_initialize_by_component_configer(self):
        """YAML-provided parameters are applied on initialization."""
        configer = self._create_configer({
            'name': 'question_type_classifier',
            'description': 'classify question types',
            'max_question_types': 2,
            'min_words': 2,
            'preview_chars': 10,
            'question_types_key': 'qtypes',
            'counts_key': 'qcounts',
            'dominant_key': 'qdominant',
        })
        c = QuestionTypeClassifier()
        c._initialize_by_component_configer(configer)
        self.assertEqual(c.max_question_types, 2)
        self.assertEqual(c.min_words, 2)
        self.assertEqual(c.preview_chars, 10)
        self.assertEqual(c.question_types_key, "qtypes")
        self.assertEqual(c.counts_key, "qcounts")
        self.assertEqual(c.dominant_key, "qdominant")
        self.assertEqual(c.name, "question_type_classifier")

    def test_config_values_take_effect(self):
        """Configured cap, preview and min_words change the stamps."""
        configer = self._create_configer({
            'name': 'question_type_classifier',
            'description': 'classify question types',
            'max_question_types': 1,
            'preview_chars': 10,
        })
        c = QuestionTypeClassifier()
        c._initialize_by_component_configer(configer)
        meta = self._run("What is it? " * 3, classifier=c)
        self.assertEqual(len(meta["question_types"]), 1)
        self.assertEqual(len(meta["question_types"][0]["text"]), 10)
        self.assertEqual(meta["question_type_counts"], {"what": 3})

    def test_disabled_stamps_absent(self):
        """Empty-string keys disable the corresponding metadata stamps."""
        configer = self._create_configer({
            'name': 'question_type_classifier',
            'description': 'classify question types',
            'question_types_key': '',
            'dominant_key': '',
        })
        c = QuestionTypeClassifier()
        c._initialize_by_component_configer(configer)
        meta = self._run("What is it?", classifier=c)
        self.assertNotIn("question_types", meta)
        self.assertNotIn("dominant_question_type", meta)
        self.assertEqual(meta["question_type_counts"], {"what": 1})

    def test_invalid_configuration_raises(self):
        """Type and range violations fail component initialization."""
        bad_configs = (
            {'max_question_types': -1},
            {'max_question_types': '5'},
            {'max_question_types': 2.5},
            {'max_question_types': True},
            {'min_words': 0},
            {'min_words': '2'},
            {'min_words': True},
            {'preview_chars': 0},
            {'preview_chars': '10'},
            {'preview_chars': True},
            {'question_types_key': 7},
            {'counts_key': []},
            {'dominant_key': {}},
        )
        for bad in bad_configs:
            configer = self._create_configer(
                {'name': 'question_type_classifier',
                 'description': 'classify question types', **bad})
            c = QuestionTypeClassifier()
            with self.assertRaises(ValueError, msg=repr(bad)):
                c._initialize_by_component_configer(configer)

    def test_valid_boundary_configuration(self):
        """Boundary values pass validation."""
        configer = self._create_configer({
            'name': 'question_type_classifier',
            'description': 'classify question types',
            'max_question_types': 0,
            'preview_chars': 1,
        })
        c = QuestionTypeClassifier()
        c._initialize_by_component_configer(configer)
        self.assertEqual(c.max_question_types, 0)
        self.assertEqual(c.preview_chars, 1)


if __name__ == "__main__":
    unittest.main()
