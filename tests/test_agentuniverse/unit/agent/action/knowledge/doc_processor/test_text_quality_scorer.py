# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @FileName: test_text_quality_scorer.py

import random
import unittest

from agentuniverse.agent.action.knowledge.doc_processor.text_quality_scorer import TextQualityScorer
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer

# A 130-word news-like paragraph with regular sentences: scores high.
GOOD_EN = (
    "The central bank raised its benchmark interest rate by a quarter point "
    "on Tuesday, citing persistent inflation pressure in the services sector "
    "and a tight labour market. Policymakers voted eight to one in favor of "
    "the move, with the dissenting member preferring a larger half-point "
    "increase. Officials signalled that further tightening would depend on "
    "incoming data over the coming months, particularly the pace of wage "
    "growth and rental costs. Financial markets reacted quickly, with "
    "two-year yields rising several basis points while equity indices gave "
    "up early gains. Economists polled by the wire services had expected "
    "the smaller move after last month's softer consumer price report. The "
    "statement dropped previous language describing policy as accommodative "
    "and instead emphasised a balanced approach to both sides of the "
    "mandate. Analysts said the shift suggests the committee is nearing the "
    "end of its tightening cycle, though several cautioned that one meeting "
    "changes little by itself."
)

# Classic keyboard mash glued into one token: no spaces, no punctuation,
# one 200-character "word".
KEYBOARD_MASH = (
    "asdfkljhqwerzxcvvasdfkljhqwerzxcvbasdfkljhqwerzxcvmasdfkljhqwerzxcvn"
    "qwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopzxcvbnmzxcvbnmzxc"
    "oiuytrewqoiuytrewqoiuytrewqoiuytrewqoiuytrewqlkjhgfdsalkjhgfdsalkjh"
)

# Star-rating spam interleaved with digit runs: almost no letters.
SYMBOL_SOUP = (
    "★★★★★ ☆☆☆☆☆ !!! ★★★★★ ☆☆☆☆☆ ??? ★★★★★ ☆☆☆☆☆ 12345678901234567890 "
    "★★★★★ ☆☆☆☆☆ !!! ★★★★★ ☆☆☆☆☆ ??? ★★★★★ ☆☆☆☆☆ 12345678901234567890"
)

# A bare digit dump, as scraped from a log or a phone-number column.
DIGIT_DUMP = "2024101920241019202410192024101920241019202410192024101920241019"

# Well-formed Chinese prose with proper CJK punctuation: scores high on
# the CJK-aware path.
GOOD_ZH = (
    "知识库是智能问答系统的核心组件。在将文档写入知识库之前，需要对原始文本进行清洗、切分和质量评估，"
    "以保证检索结果的相关性和准确性。文本质量评分组件基于纯词法统计指标，对每一篇文档的内容质量给出零到一百分之间的确定性评分。"
    "评分过程不依赖任何外部模型或网络请求，同一篇文本在任何环境下都会得到完全相同的分数。"
    "低质量文档可以在入库前被识别并过滤，从而节省向量化计算的存储开销，同时避免垃圾内容污染召回结果。"
    "该组件与去重过滤器、阈值过滤器可以组合使用，构成完整的知识预处理流水线。"
)

# Spam loop: one six-character promotional phrase repeated without any
# punctuation — unique ratio far below 0.10 over 30+ units.
SPAM_ZH = (
    "低价促销加微信低价促销加微信低价促销加微信低价促销加微信低价促销加微信低价促销加微信"
    "低价促销加微信低价促销加微信低价促销加微信低价促销加微信低价促销加微信低价促销加微信"
)

# Random pronounceable-looking consonant salad with spaces but zero
# sentence punctuation: scores mediocre, clearly below GOOD_EN.
WORD_SALAD = (
    "qwjzh plfkr vxqzm brtwn kcldv mfxpq gzjwl nthrv sdbmk xqzpv lwfjb "
    "rkcmz vpqwx djfln mgzrq twbxk clvpf znqjm wxbdr fkplz qvmwj xbnrd "
    "pztvl kmjwc xrdnf bqvlz jpwmk tfxrd nvlzb qwjmk pxzrv bltwn"
)


def _doc(text: str, **metadata) -> Document:
    """Build a Document carrying `text` and optional metadata."""
    return Document(text=text, metadata=dict(metadata) or None)


class TestTextQualityScorer(unittest.TestCase):
    """Comprehensive test suite for TextQualityScorer."""

    def setUp(self):
        self.scorer = TextQualityScorer()
        self.query = Query(query_str="quality")

    def _create_configer(self, config_dict):
        """Create a ComponentConfiger from a plain dictionary."""
        cfg = Configer()
        cfg.value = config_dict
        configer = ComponentConfiger()
        configer.load_by_configer(cfg)
        return configer

    def _score(self, text: str) -> float:
        """Score one text directly through the analyzer."""
        return self.scorer._composite_score(self.scorer._analyze(text))

    # ========== Initialization tests ==========

    def test_default_configuration(self):
        """Defaults: no filtering, default weights, 0.30 CJK threshold and
        'quality_score' / 'quality_metrics' / 'quality_rejected' keys."""
        s = TextQualityScorer()
        self.assertIsNone(s.min_score)
        self.assertEqual(s.weights, {
            'alpha': 0.10, 'structure': 0.20, 'punctuation': 0.20,
            'diversity': 0.30, 'digit': 0.05, 'whitespace': 0.05,
            'length': 0.10,
        })
        self.assertEqual(s.cjk_threshold, 0.30)
        self.assertEqual(s.score_key, "quality_score")
        self.assertEqual(s.metrics_key, "quality_metrics")
        self.assertEqual(s.rejected_key, "quality_rejected")

    def test_default_weights_not_shared_between_instances(self):
        """Mutating one instance's weights must not leak into another."""
        a, b = TextQualityScorer(), TextQualityScorer()
        a.weights['alpha'] = 0.99
        self.assertEqual(b.weights['alpha'], 0.10)

    def test_initialize_by_component_configer(self):
        """YAML-provided parameters are applied on initialization."""
        configer = self._create_configer({
            'name': 'text_quality_scorer',
            'description': 'quality scorer',
            'min_score': 55,
            'weights': {'alpha': 1.0},
            'cjk_threshold': 0.5,
            'score_key': 'q',
            'metrics_key': 'qm',
            'rejected_key': 'rejected',
        })
        s = TextQualityScorer()
        s._initialize_by_component_configer(configer)
        self.assertEqual(s.min_score, 55.0)
        self.assertEqual(s.weights, {'alpha': 1.0})
        self.assertEqual(s.cjk_threshold, 0.5)
        self.assertEqual(s.score_key, "q")
        self.assertEqual(s.metrics_key, "qm")
        self.assertEqual(s.rejected_key, "rejected")
        self.assertEqual(s.name, "text_quality_scorer")

    def test_invalid_configuration_raises(self):
        """Out-of-range thresholds, bad weights and non-string keys all
        fail at load time."""
        base = {
            'name': 's', 'description': 'd', 'min_score': None,
            'weights': {'alpha': 1.0}, 'cjk_threshold': 0.3,
            'score_key': 'q', 'metrics_key': 'qm', 'rejected_key': 'r',
        }
        for key, value in (
            ('min_score', -1), ('min_score', 100.5), ('min_score', 'low'),
            ('min_score', True),
            ('cjk_threshold', 0), ('cjk_threshold', 1.5),
            ('cjk_threshold', False),
            ('weights', ['alpha']),
            ('weights', {'vowel_ratio': 1.0}),
            ('weights', {'alpha': -0.5}),
            ('weights', {'alpha': True}),
            ('weights', {'alpha': float('nan')}),
            ('weights', {'alpha': 0.0}),
            ('weights', {}),
            ('score_key', 5), ('metrics_key', None.__class__),
            ('rejected_key', ['x']),
        ):
            config = dict(base, **{key: value})
            with self.assertRaises(ValueError, msg=f"{key}={value!r}"):
                TextQualityScorer()._initialize_by_component_configer(
                    self._create_configer(config))

    # ========== Metric extraction tests ==========

    def test_latin_metrics_hand_computed(self):
        """A short mixed string pins every Latin-path metric by hand."""
        metrics = self.scorer._analyze("Hello, world! 123")
        self.assertEqual(metrics['length_chars'], 17)
        self.assertEqual(metrics['non_whitespace_chars'], 15)
        self.assertEqual(metrics['word_count'], 2)      # "123" has no letter
        self.assertEqual(metrics['mean_word_length'], 5.0)
        self.assertEqual(metrics['unique_word_ratio'], 1.0)
        self.assertAlmostEqual(metrics['alpha_ratio'], 10 / 15, places=6)
        self.assertAlmostEqual(metrics['digit_ratio'], 3 / 15, places=6)
        self.assertAlmostEqual(metrics['punctuation_ratio'], 2 / 15,
                               places=6)
        self.assertEqual(metrics['whitespace_irregularity'], 0.0)
        self.assertEqual(metrics['cjk_ratio'], 0.0)
        self.assertEqual(metrics['script'], 'latin')

    def test_cjk_metrics_hand_computed(self):
        """Chinese text takes the CJK-aware path: characters are the word
        units, CJK punctuation counts, mean Latin word length is None."""
        metrics = self.scorer._analyze("你好，世界。")
        self.assertEqual(metrics['length_chars'], 6)
        self.assertEqual(metrics['non_whitespace_chars'], 6)
        self.assertEqual(metrics['word_count'], 4)
        self.assertIsNone(metrics['mean_word_length'])
        self.assertEqual(metrics['unique_word_ratio'], 1.0)
        self.assertAlmostEqual(metrics['alpha_ratio'], 4 / 6, places=6)
        self.assertAlmostEqual(metrics['punctuation_ratio'], 2 / 6,
                               places=6)
        self.assertAlmostEqual(metrics['cjk_ratio'], 4 / 6, places=6)
        self.assertEqual(metrics['script'], 'cjk')

    def test_mixed_script_counts_words_and_characters_separately(self):
        """A mostly-Latin document carrying CJK terms keeps the Latin path
        while CJK characters join the word units."""
        metrics = self.scorer._analyze(
            "The report covers 中文 content, and the appendix covers more.")
        self.assertEqual(metrics['script'], 'latin')
        self.assertEqual(metrics['word_count'], 11)   # 9 Latin words + 2 CJK
        self.assertAlmostEqual(metrics['mean_word_length'],
                               46 / 9, places=6)

    def test_mean_word_length_ignores_attached_punctuation(self):
        """Punctuation riding on a token does not inflate its length."""
        metrics = self.scorer._analyze("Hello, world! don't ...")
        # alnum cores: 5 + 5 + 4 = 14 over 3 words
        self.assertAlmostEqual(metrics['mean_word_length'], 14 / 3,
                               places=6)

    def test_unique_word_ratio_lowercased(self):
        """Case-only variants collapse into one unit."""
        metrics = self.scorer._analyze("spam Spam SPAM other")
        self.assertAlmostEqual(metrics['unique_word_ratio'], 0.5, places=6)

    def test_whitespace_irregularity_detection(self):
        """Double spaces, tabs, 3+ newlines, mixed runs and edge whitespace
        are irregular; single spaces and blank-line breaks are not."""
        cases = {
            "a b c": 0.0,
            "a\n\nb": 0.0,          # one blank line stays regular
            "a  b": 1.0,            # double space
            "a\n\n\nb": 1.0,        # triple newline
            "a\tb": 1.0,            # tab anywhere
            "a\rb": 1.0,            # carriage return
            " a": 1.0,              # leading whitespace
            "a ": 1.0,              # trailing whitespace
            "a  \n  b": 1.0,        # mixed run of 3+ characters
        }
        for text, expected in cases.items():
            metrics = self.scorer._analyze(text)
            self.assertEqual(metrics['whitespace_irregularity'], expected,
                             msg=repr(text))

    def test_empty_and_none_text_metrics(self):
        """Empty and None texts yield all-zero ratios and 0 length."""
        for text in ("", None):
            metrics = self.scorer._analyze(text)
            self.assertEqual(metrics['length_chars'], 0)
            self.assertEqual(metrics['word_count'], 0)
            self.assertIsNone(metrics['mean_word_length'])
            self.assertEqual(metrics['unique_word_ratio'], 0.0)
            self.assertEqual(metrics['alpha_ratio'], 0.0)
            self.assertEqual(metrics['script'], 'latin')

    # ========== Scoring behavior tests ==========

    def test_well_written_english_scores_high(self):
        """Regular prose lands near the top of the scale."""
        score = self._score(GOOD_EN)
        self.assertGreaterEqual(score, 80.0)
        self.assertLessEqual(score, 100.0)

    def test_well_written_chinese_scores_high(self):
        """Well-formed CJK prose scores high on the CJK-aware path."""
        score = self._score(GOOD_ZH)
        self.assertGreaterEqual(score, 80.0)
        self.assertLessEqual(score, 100.0)

    def test_keyboard_mash_scores_low(self):
        """Glued keyboard mash — one giant word, no punctuation — scores
        low."""
        self.assertLessEqual(self._score(KEYBOARD_MASH), 40.0)

    def test_symbol_soup_scores_low(self):
        """Star-rating spam with digit runs scores very low."""
        self.assertLessEqual(self._score(SYMBOL_SOUP), 20.0)

    def test_digit_dump_scores_low(self):
        """A bare digit dump scores very low."""
        self.assertLessEqual(self._score(DIGIT_DUMP), 10.0)

    def test_letterless_documents_score_exactly_zero(self):
        """Empty, whitespace-only, symbol-only and digit-only documents —
        every text without a single letter or CJK character — score
        exactly 0, as documented (the old gate missed digit-only and
        punctuation-only soup)."""
        for text in (DIGIT_DUMP, "1" * 300, "!" * 300, "." * 150 + "," * 150,
                     "\u2605" * 300, "12345 !?@# \u2606\u2606 67890",
                     "   ", " \n\t\n  ", "", None):
            self.assertEqual(self._score(text), 0.0, msg=repr(text))

    def test_soup_gate_measured_over_non_whitespace_chars(self):
        """The symbol/digit-soup gate needs 100+ non-whitespace
        characters, not 100+ total characters: whitespace padding must
        not push a document under the gate."""
        s = TextQualityScorer()
        s.weights = {'length': 1.0}   # isolate: score = 100 * length ramp
        # Each unit has 7 non-whitespace chars (1 letter, 6 soup) joined
        # by regular " \n" separators (a 2-char mixed run stays regular).
        unit = "a\u2605\u2606" + "1234"
        self.assertEqual(len(unit), 7)
        padded = " \n".join([unit] * 12)   # 84 non-ws, 106 total chars
        dense = " \n".join([unit] * 15)    # 105 non-ws, 133 total chars
        metrics = s._analyze(padded)
        self.assertEqual(metrics['non_whitespace_chars'], 84)
        # 84 non-ws < 100: no soup gate despite the 106 total characters.
        self.assertAlmostEqual(s._composite_score(metrics), 41.25,
                               places=6)
        # 105 non-ws >= 100 with alpha ratio 15/105 < 0.20: gate applies.
        self.assertAlmostEqual(s._composite_score(s._analyze(dense)),
                               23.25, places=6)

    def test_cjk_path_ignores_latin_word_length(self):
        """On the CJK-aware path a stray short Latin token must not drag
        the structure sub-score down: Latin word length only contributes
        on the Latin path."""
        stray = GOOD_ZH + " x"
        metrics = self.scorer._analyze(stray)
        self.assertEqual(metrics['script'], 'cjk')
        self.assertEqual(metrics['mean_word_length'], 1.0)  # still reported
        with_stray = self._score(stray)
        self.assertGreaterEqual(with_stray, self._score(GOOD_ZH) - 1.0)
        self.assertGreaterEqual(with_stray, 80.0)
        # On the Latin path mean word length still contributes: 30
        # one-character words flatten the structure sub-score while 30
        # two-character words keep it maximal.
        s = TextQualityScorer()
        s.weights = {'structure': 1.0}
        import string
        short_words = " ".join(list(string.ascii_lowercase) + ["a", "b",
                                                                "c", "d"])
        long_words = " ".join(
            [a + b for a, b in zip(string.ascii_lowercase,
                                   string.ascii_lowercase)] +
            ["a1", "b1", "c1", "d1"])
        self.assertEqual(s._composite_score(s._analyze(short_words)), 0.0)
        self.assertEqual(s._composite_score(s._analyze(long_words)), 100.0)

    def test_chinese_spam_loop_scores_low(self):
        """A repeated promotional phrase without punctuation triggers the
        degenerate-repetition gate and scores low."""
        self.assertLessEqual(self._score(SPAM_ZH), 40.0)

    def test_word_salad_below_good_prose(self):
        """Spaced consonant salad without any sentence punctuation scores
        clearly below good prose of similar length."""
        self.assertLess(self._score(WORD_SALAD), self._score(GOOD_EN))
        self.assertLess(self._score(WORD_SALAD), 75.0)

    def test_empty_and_whitespace_documents_score_zero(self):
        """Empty, whitespace-only and None texts score exactly 0."""
        for text in ("", "   ", " \n\t\n  ", None):
            self.assertEqual(self._score(text), 0.0)

    def test_scores_bounded_for_random_texts(self):
        """A battery of seeded-random texts always stays within [0, 100]."""
        rng = random.Random(258)
        alphabet = "abcdefghijklmnopqrstuvwxyz ,.!阿天的们了我中"
        for _ in range(200):
            size = rng.randint(0, 500)
            text = "".join(rng.choice(alphabet) for _ in range(size))
            score = self._score(text)
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 100.0)

    def test_symbol_substitution_monotonically_decreases_score(self):
        """Progressively replacing prose words with star symbols never
        raises the score, and the decline is visible once alphabetic share
        leaves the healthy band."""
        words = GOOD_EN.split()
        scores = []
        rng = random.Random(42)
        positions = list(range(len(words)))
        rng.shuffle(positions)
        for step in range(0, 110, 10):
            text = " ".join("★★★" if i in positions[:step] else words[i]
                            for i in range(len(words)))
            scores.append(self._score(text))
        for lower, upper in zip(scores, scores[1:]):
            self.assertLessEqual(upper, lower + 1e-9)
        self.assertLess(scores[-1], scores[0])

    def test_repetition_monotonically_decreases_score(self):
        """Progressively replacing prose words with one repeated token never
        raises the score and ends far below the original."""
        words = GOOD_EN.split()
        scores = []
        for step in (0, 20, 40, 60, 80, len(words)):
            text = " ".join("spam" if i < step else words[i]
                            for i in range(len(words)))
            scores.append(self._score(text))
        for lower, upper in zip(scores, scores[1:]):
            self.assertLessEqual(upper, lower + 1e-9)
        self.assertLess(scores[-1], 40.0)

    def test_length_score_grows_with_document_size(self):
        """With only the length sub-score weighted, longer documents score
        strictly higher until the ramp saturates."""
        s = TextQualityScorer()
        s.weights = {'length': 1.0}
        self.assertEqual(s._composite_score(s._analyze("x" * 40)), 0.0)
        self.assertAlmostEqual(s._composite_score(s._analyze("x" * 120)),
                               50.0, places=6)
        self.assertEqual(s._composite_score(s._analyze("x" * 200)), 100.0)
        self.assertEqual(s._composite_score(s._analyze("x" * 500)), 100.0)

    def test_cjk_threshold_switches_script_path(self):
        """The CJK-aware path activates at the configured ratio."""
        latin_with_cjk = "alpha beta gamma delta epsilon zeta 你好"
        below = TextQualityScorer()
        below.cjk_threshold = 0.99
        self.assertEqual(below._analyze(latin_with_cjk)['script'], 'latin')
        above = TextQualityScorer()
        above.cjk_threshold = 0.01
        self.assertEqual(above._analyze(latin_with_cjk)['script'], 'cjk')

    def test_weights_change_the_composite(self):
        """Weighting only digit punishment turns an all-digit text to 0 and
        a letter-only text to 100; scaling all weights is a no-op."""
        s = TextQualityScorer()
        s.weights = {'digit': 1.0}
        self.assertEqual(s._composite_score(s._analyze(DIGIT_DUMP)), 0.0)
        self.assertEqual(
            s._composite_score(s._analyze("words only here now")), 100.0)

        scaled = TextQualityScorer()
        scaled.weights = {'digit': 0.3}
        self.assertEqual(s._composite_score(s._analyze(DIGIT_DUMP)),
                         scaled._composite_score(scaled._analyze(DIGIT_DUMP)))

    def test_determinism_across_instances_and_runs(self):
        """Scores and metrics are identical across instances and repeated
        runs — pure arithmetic, no randomness or environment dependence."""
        other = TextQualityScorer()
        for text in (GOOD_EN, GOOD_ZH, KEYBOARD_MASH, SPAM_ZH, ""):
            for _ in range(3):
                self.assertEqual(self.scorer._analyze(text),
                                 other._analyze(text))
                self.assertEqual(self._score(text), self._score(text))

    # ========== Pipeline behavior tests ==========

    def test_default_mode_keeps_all_and_stamps_metadata(self):
        """Without min_score every document is kept, stamped with score and
        metrics, in input order, and never marked rejected."""
        docs = [_doc(GOOD_EN, source="wire"),
                _doc(KEYBOARD_MASH, source="form"),
                _doc(GOOD_ZH, source="wiki")]
        result = self.scorer.process_docs(docs, self.query)
        self.assertEqual([d.text for d in result],
                         [GOOD_EN, KEYBOARD_MASH, GOOD_ZH])
        for doc in result:
            self.assertIsInstance(doc.metadata['quality_score'], float)
            metrics = doc.metadata['quality_metrics']
            self.assertEqual(metrics['length_chars'], len(doc.text))
            self.assertIn('script', metrics)
            self.assertIn('unique_word_ratio', metrics)
            self.assertNotIn('quality_rejected', doc.metadata)

    def test_score_and_metrics_consistent_with_direct_analysis(self):
        """Stamped values equal the analyzer's output for the same text."""
        doc = _doc(GOOD_EN)
        self.scorer.process_docs([doc], self.query)
        expected = self.scorer._analyze(GOOD_EN)
        self.assertEqual(doc.metadata['quality_metrics'], expected)
        self.assertAlmostEqual(doc.metadata['quality_score'],
                               round(self.scorer._composite_score(expected),
                                     4), places=6)

    def test_min_score_filters_low_quality_documents(self):
        """Documents below the threshold are dropped and marked rejected on
        their original objects; good ones pass untouched."""
        self.scorer.min_score = 60.0
        good, mash, zh = _doc(GOOD_EN), _doc(KEYBOARD_MASH), _doc(GOOD_ZH)
        result = self.scorer.process_docs([good, mash, zh], self.query)
        self.assertEqual([d.text for d in result], [GOOD_EN, GOOD_ZH])
        self.assertIs(result[0], good)
        self.assertIs(result[1], zh)
        self.assertTrue(mash.metadata['quality_rejected'])
        self.assertIn('quality_score', mash.metadata)
        self.assertIn('quality_metrics', mash.metadata)
        for kept in result:
            self.assertNotIn('quality_rejected', kept.metadata)

    def test_min_score_boundary_is_inclusive(self):
        """A document scoring exactly min_score is kept; one scoring just
        below is dropped."""
        s = TextQualityScorer()
        s.weights = {'length': 1.0}       # 'x' * 120 scores exactly 50.0
        s.min_score = 50.0
        kept = _doc("x" * 120)
        self.assertEqual(s.process_docs([kept], self.query), [kept])

        s.min_score = 50.01
        dropped = _doc("x" * 120)
        self.assertEqual(s.process_docs([dropped], self.query), [])
        self.assertTrue(dropped.metadata['quality_rejected'])

    def test_min_score_zero_keeps_everything(self):
        """min_score 0 keeps even empty documents (only < drops)."""
        self.scorer.min_score = 0.0
        docs = [_doc(""), _doc(KEYBOARD_MASH), _doc(GOOD_EN)]
        self.assertEqual(len(self.scorer.process_docs(docs, self.query)), 3)

    def test_empty_and_none_documents_survive_stamp_and_filter(self):
        """Empty / whitespace-only / None-text documents score 0, are kept
        by default and dropped once a threshold is set."""
        docs = [_doc(""), _doc("  \n  ")]
        result = self.scorer.process_docs(docs, self.query)
        self.assertEqual(len(result), 2)
        for doc in result:
            self.assertEqual(doc.metadata['quality_score'], 0.0)

        self.scorer.min_score = 1.0
        self.assertEqual(self.scorer.process_docs(docs, self.query), [])
        for doc in docs:
            self.assertTrue(doc.metadata['quality_rejected'])

    def test_disabled_metadata_keys_stamp_nothing(self):
        """Empty score/metrics/rejected keys disable all stamping."""
        self.scorer.score_key = ""
        self.scorer.metrics_key = ""
        self.scorer.rejected_key = ""
        self.scorer.min_score = 60.0
        good, mash = _doc(GOOD_EN, source="wire"), _doc(KEYBOARD_MASH)
        result = self.scorer.process_docs([good, mash], self.query)
        self.assertEqual(result, [good])
        self.assertEqual(good.metadata, {"source": "wire"})
        self.assertIsNone(mash.metadata)

    def test_input_documents_not_corrupted(self):
        """Text and id are untouched; pre-existing metadata entries survive
        on kept and dropped documents alike; and stamping writes through a
        copy rather than mutating the original mapping."""
        good = _doc(GOOD_EN, source="wire", rank=1)
        mash = _doc(KEYBOARD_MASH, source="form", rank=2)
        good_meta_ref, mash_meta_ref = good.metadata, mash.metadata
        self.scorer.min_score = 60.0

        result = self.scorer.process_docs([good, mash], self.query)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text, GOOD_EN)
        self.assertEqual(result[0].id, good.id)
        self.assertEqual(good.metadata["source"], "wire")
        self.assertEqual(good.metadata["rank"], 1)
        self.assertEqual(mash.text, KEYBOARD_MASH)
        self.assertEqual(mash.metadata["rank"], 2)
        # Stamps went through copied mappings: the caller's original dict
        # objects did not gain the new keys in place.
        self.assertNotIn("quality_score", good_meta_ref)
        self.assertNotIn("quality_rejected", mash_meta_ref)
        self.assertIsNot(good.metadata, good_meta_ref)

    def test_empty_input_returns_empty(self):
        """An empty batch yields an empty result."""
        self.assertEqual(self.scorer.process_docs([], self.query), [])

    def test_mixed_batch_order_preserved(self):
        """A mixed-quality batch filtered at 60 keeps its survivors in the
        original batch order."""
        self.scorer.min_score = 60.0
        docs = [_doc(SYMBOL_SOUP), _doc(GOOD_ZH), _doc(DIGIT_DUMP),
                _doc(GOOD_EN), _doc(SPAM_ZH)]
        result = self.scorer.process_docs(docs, self.query)
        self.assertEqual([d.text for d in result], [GOOD_ZH, GOOD_EN])


if __name__ == '__main__':
    unittest.main()
