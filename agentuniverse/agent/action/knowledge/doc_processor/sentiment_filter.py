# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/07/23
# @Author  : contributor
# @FileName: sentiment_filter.py

"""
Sentiment-based document filter (post-processor).

This processor scores the polarity of each recalled document with a small,
dependency-free bag-of-words sentiment model and keeps only the documents whose
detected sentiment matches the configured ``allowed_sentiment``. It addresses
the *sentiment filtering* direction of issue #248 and is intentionally
distinct from every other doc processor: none of them inspect the emotional
polarity of the text.

Design notes
------------

* **No third-party dependencies.** The lexicons are inlined and the scorer is
  plain Python, so the processor runs anywhere the framework runs (including
  offline / sandboxed runtimes) without pulling in NLTK / TextBlob / transformers.
* **Deterministic.** Given the same input text the score is always the same,
  which matters for reproducible retrieval pipelines and unit tests.
* **Language aware.** Two lexicons ship out of the box — English and Chinese —
  and the tokenizer picks the most fitting one per document (or an explicit
  override can be supplied). Mixed-language documents are scored against both
  lexicons and the strongest signal wins.
* **Transparent.** Every kept document carries the computed score, the
  detected polarity and the lexicon used in its ``metadata``, so downstream
  components can audit the decision.

Scoring model
-------------

For a document the processor lowercases the text, tokenizes it, and computes

    score = (positive_hits - negative_hits) / max(1, total_hits)

``score`` is therefore in ``[-1.0, +1.0]``. It is then mapped to a polarity:

* ``positive``  when ``score >= threshold``            (default ``0.05``)
* ``negative``  when ``score <= -threshold``
* ``neutral``   otherwise

A document additionally needs ``|score| >= min_confidence`` for its polarity to
be trusted at all — below that the text is treated as ``neutral`` regardless of
sign, which stops low-signal short snippets from being filed as positive or
negative. ``min_confidence`` defaults to ``0.0`` so the behaviour is opt-in.
"""

import logging
import re
import unicodedata
from typing import Dict, List, Optional, Set, Tuple

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import \
    DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger

logger = logging.getLogger(__name__)


class SentimentFilter(DocProcessor):
    """Keep only documents whose detected sentiment matches a target polarity.

    Attributes:
        allowed_sentiment: Which polarity to keep. One of ``positive``,
            ``negative``, ``neutral`` or ``all``. ``all`` disables filtering
            and is useful when you only want to *annotate* documents with
            their sentiment without dropping any.
        threshold: Absolute score boundary in ``(0.0, 1.0]`` that separates
            ``positive`` / ``negative`` from ``neutral``. A document with
            ``|score| < threshold`` is neutral.
        min_confidence: Minimum ``|score|`` required before a non-neutral
            polarity is trusted. Defaults to ``0.0`` (disabled).
        language: Force a specific lexicon — ``en``, ``zh`` or ``auto``
            (default). ``auto`` scores against every available lexicon and
            keeps the one with the largest absolute score.
        text_field: Metadata key to read the text from when ``Document.text``
            is empty. Falls back to ``Document.text`` when absent.
        score_key / polarity_key / language_key: Metadata keys under which the
            computed score, polarity and lexicon are stamped on every kept
            document. Set the relevant key to ``None`` to skip stamping.
    """

    # ------------------------------------------------------------------ #
    # Public configuration
    # ------------------------------------------------------------------ #
    allowed_sentiment: str = "positive"
    threshold: float = 0.05
    min_confidence: float = 0.0
    language: str = "auto"
    text_field: Optional[str] = None

    score_key: Optional[str] = "sentiment_score"
    polarity_key: Optional[str] = "sentiment_polarity"
    language_key: Optional[str] = "sentiment_language"

    # ------------------------------------------------------------------ #
    # Lexicons — intentionally compact, curated for retrieval noise reduction
    # ------------------------------------------------------------------ #
    _POSITIVE_EN: Set[str] = {
        "good", "great", "excellent", "amazing", "wonderful", "fantastic",
        "awesome", "best", "better", "love", "loved", "loves", "like", "liked",
        "likes", "happy", "glad", "pleased", "delighted", "perfect",
        "beautiful", "brilliant", "superb", "outstanding", "remarkable",
        "positive", "success", "successful", "win", "winning", "benefit",
        "beneficial", "improve", "improved", "improvement", "gain", "gains",
        "profit", "profitable", "strong", "stable", "growth", "grow",
        "recommend", "recommended", "favorite", "favourite", "enjoy",
        "enjoyed", "nice", "cool", "fun", "thank", "thanks", "grateful",
    }
    _NEGATIVE_EN: Set[str] = {
        "bad", "terrible", "awful", "horrible", "worst", "worse", "hate",
        "hated", "dislike", "disliked", "sad", "unhappy", "angry", "upset",
        "disappointed", "disappointing", "poor", "fail", "failed", "failure",
        "loss", "lose", "losing", "weak", "decline", "declining", "drop",
        "crash", "crashed", "risk", "risky", "danger", "dangerous", "problem",
        "issue", "bug", "broken", "error", "wrong", "negative", "ugly",
        "boring", "annoying", "frustrating", "painful", "difficult", "fear",
        "worried", "concern", "complaint", "fraud", "scam", "bankruptcy",
    }

    _POSITIVE_ZH: Set[str] = {
        "好", "很好", "非常好", "优秀", "优良", "卓越", "棒", "赞", "喜欢",
        "爱", "满意", "高兴", "快乐", "开心", "幸福", "成功", "胜利", "赢",
        "增长", "增长", "上涨", "收益", "利润", "盈利", "强", "稳定", "增长",
        "推荐", "值得", "棒", "完美", "美丽", "美好", "感谢", "谢谢", "棒",
        "积极", "正面", "改善", "提升", "加强", "突破", "创新", "机遇",
    }
    _NEGATIVE_ZH: Set[str] = {
        "坏", "差", "糟糕", "可怕", "最差", "讨厌", "不喜欢", "悲伤", "难过",
        "生气", "愤怒", "失望", "失败", "亏损", "损失", "跌", "下跌", "下滑",
        "弱", "风险", "危险", "问题", "故障", "错误", "负面", "消极", "丑",
        "无聊", "烦人", "痛苦", "困难", "恐惧", "担心", "忧虑", "投诉", "欺诈",
        "诈骗", "破产", "危机", "衰退", "警告", "违法",
    }

    _LEXICONS: Dict[str, Tuple[Set[str], Set[str]]] = {
        "en": (_POSITIVE_EN, _NEGATIVE_EN),
        "zh": (_POSITIVE_ZH, _NEGATIVE_ZH),
    }

    _VALID_SENTIMENTS = {"positive", "negative", "neutral", "all"}

    class Config:
        arbitrary_types_allowed = True

    # ------------------------------------------------------------------ #
    # DocProcessor entry point
    # ------------------------------------------------------------------ #
    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Filter documents by sentiment, annotating each kept document.

        Args:
            origin_docs: Recalled documents to filter.
            query: Optional query (unused — sentiment is text intrinsic).

        Returns:
            Documents whose detected sentiment matches ``allowed_sentiment``.
        """
        if not origin_docs:
            return []

        kept: List[Document] = []
        kept_by_polarity: Dict[str, int] = {
            "positive": 0, "negative": 0, "neutral": 0}
        for doc in origin_docs:
            text = self._extract_text(doc)
            score, polarity, lang = self._analyze(text)

            # Annotate the document in place so downstream stages can audit.
            self._stamp_metadata(doc, score, polarity, lang)

            kept_by_polarity[polarity] = kept_by_polarity.get(polarity, 0) + 1
            if self._matches(polarity):
                kept.append(doc)

        dropped = len(origin_docs) - len(kept)
        logger.info(
            "SentimentFilter[%s]: %d in -> %d kept (dropped %d); "
            "polarity distribution=%s",
            self.allowed_sentiment, len(origin_docs), len(kept), dropped,
            kept_by_polarity,
        )
        return kept

    # ------------------------------------------------------------------ #
    # Sentiment analysis (pure, deterministic)
    # ------------------------------------------------------------------ #
    def _analyze(self, text: str) -> Tuple[float, str, str]:
        """Score a piece of text and return ``(score, polarity, language)``.

        Args:
            text: Raw text to analyze.

        Returns:
            score: Polarity score in ``[-1.0, 1.0]``.
            polarity: One of ``positive`` / ``negative`` / ``neutral``.
            language: The lexicon that produced the score (``en`` / ``zh``).
        """
        if not text or not text.strip():
            return 0.0, "neutral", "none"

        normalized = self._normalize(text)

        if self.language == "auto":
            score, lang = self._score_auto(normalized)
        else:
            lang = self.language if self.language in self._LEXICONS else "en"
            score = self._score_with(normalized, self._LEXICONS[lang])

        polarity = self._polarity(score)
        return score, polarity, lang

    def _score_auto(self, normalized: str) -> Tuple[float, str]:
        """Score with every lexicon and keep the strongest absolute signal.

        Falling back to English when no lexicon registers any hit keeps the
        language label deterministic for neutral text.
        """
        best_score = 0.0
        best_lang = "en"
        for lang, (pos, neg) in self._LEXICONS.items():
            score = self._score_with(normalized, (pos, neg))
            if abs(score) > abs(best_score):
                best_score = score
                best_lang = lang
        return best_score, best_lang

    def _score_with(self, normalized: str,
                    lexicon: Tuple[Set[str], Set[str]]) -> float:
        """Compute the polarity score for ``normalized`` against one lexicon."""
        positive_words, negative_words = lexicon
        tokens = self._tokenize(normalized, positive_words, negative_words)
        if not tokens:
            return 0.0
        total = len(tokens)
        pos_hits = sum(1 for t in tokens if t in positive_words)
        neg_hits = sum(1 for t in tokens if t in negative_words)
        return (pos_hits - neg_hits) / total

    def _polarity(self, score: float) -> str:
        """Map a numeric score to a polarity label, honouring min_confidence."""
        if abs(score) < self.min_confidence:
            return "neutral"
        if score >= self.threshold:
            return "positive"
        if score <= -self.threshold:
            return "negative"
        return "neutral"

    def _matches(self, polarity: str) -> bool:
        """Whether a document with this polarity should be kept."""
        if self.allowed_sentiment == "all":
            return True
        return polarity == self.allowed_sentiment

    # ------------------------------------------------------------------ #
    # Text utilities
    # ------------------------------------------------------------------ #
    def _extract_text(self, doc: Document) -> str:
        """Return the text to analyze, falling back to a metadata field."""
        if doc.text:
            return doc.text
        if self.text_field and doc.metadata:
            value = doc.metadata.get(self.text_field)
            if isinstance(value, str):
                return value
        return ""

    @staticmethod
    def _normalize(text: str) -> str:
        """Lowercase and strip accents/diacritics for stable English matching.

        Chinese characters are unaffected by NFKC + lowercasing, so the same
        normalized string feeds both lexicons safely.
        """
        text = text.lower()
        # Decompose accents then drop combining marks — "café" -> "cafe".
        decomposed = unicodedata.normalize("NFKD", text)
        stripped = "".join(
            ch for ch in decomposed if not unicodedata.combining(ch))
        return stripped

    @staticmethod
    def _tokenize(text: str, positive_words: Set[str],
                  negative_words: Set[str]) -> List[str]:
        """Split text into polarity-relevant tokens.

        English / Latin tokens are matched on word boundaries; Chinese
        sentiment lexemes are single/double characters and are matched by a
        rolling substring scan (Chinese has no whitespace). Tokens that appear
        in neither lexicon are dropped to keep the denominator meaningful.
        """
        tokens: List[str] = []

        # Latin / word-based lexemes: words of length >= 1.
        word_pattern = re.compile(r"[a-z0-9]+")
        for match in word_pattern.findall(text):
            if match in positive_words or match in negative_words:
                tokens.append(match)

        # CJK lexemes: scan for any known positive/negative Chinese term.
        cjk_terms = positive_words | negative_words
        # Sort by length desc so longer terms ("非常好") win over ("好").
        for term in sorted(cjk_terms, key=len, reverse=True):
            if not SentimentFilter._has_cjk(term):
                continue
            count = text.count(term)
            if count:
                tokens.extend([term] * count)
                # Blank out matched spans so a shorter overlapping term is not
                # double counted (e.g. once "非常好" matches, "好" inside it).
                text = text.replace(term, " " * len(term))

        return tokens

    @staticmethod
    def _has_cjk(term: str) -> bool:
        """True if ``term`` contains any CJK Unified Ideograph."""
        return any("\u4e00" <= ch <= "\u9fff" for ch in term)

    # ------------------------------------------------------------------ #
    # Metadata stamping
    # ------------------------------------------------------------------ #
    def _stamp_metadata(self, doc: Document, score: float, polarity: str,
                        language: str) -> None:
        """Write the analysis result into the document metadata."""
        if not any([self.score_key, self.polarity_key, self.language_key]):
            return
        if doc.metadata is None:
            doc.metadata = {}
        if self.score_key:
            doc.metadata[self.score_key] = round(score, 6)
        if self.polarity_key:
            doc.metadata[self.polarity_key] = polarity
        if self.language_key:
            doc.metadata[self.language_key] = language

    # ------------------------------------------------------------------ #
    # Configuration loading
    # ------------------------------------------------------------------ #
    def _initialize_by_component_configer(
            self,
            doc_processor_configer: ComponentConfiger) -> 'SentimentFilter':
        """Initialize filter parameters from the component configuration.

        Args:
            doc_processor_configer: Configuration object containing the
                filter parameters declared in the YAML.

        Returns:
            The initialized filter instance.

        Raises:
            ValueError: If ``allowed_sentiment`` or ``language`` is unknown,
                or if ``threshold`` / ``min_confidence`` are out of range.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        if hasattr(doc_processor_configer, "allowed_sentiment"):
            self.allowed_sentiment = doc_processor_configer.allowed_sentiment
            if self.allowed_sentiment not in self._VALID_SENTIMENTS:
                raise ValueError(
                    f"Invalid allowed_sentiment: {self.allowed_sentiment}. "
                    f"Must be one of: {', '.join(sorted(self._VALID_SENTIMENTS))}"
                )

        if hasattr(doc_processor_configer, "threshold"):
            self.threshold = doc_processor_configer.threshold
            self._validate_range("threshold", self.threshold, 0.0, 1.0)

        if hasattr(doc_processor_configer, "min_confidence"):
            self.min_confidence = doc_processor_configer.min_confidence
            self._validate_range(
                "min_confidence", self.min_confidence, 0.0, 1.0)

        if hasattr(doc_processor_configer, "language"):
            self.language = doc_processor_configer.language
            if self.language not in {"auto"} and self.language not in self._LEXICONS:
                raise ValueError(
                    f"Invalid language: {self.language}. "
                    f"Must be one of: auto, {', '.join(sorted(self._LEXICONS))}"
                )

        if hasattr(doc_processor_configer, "text_field"):
            self.text_field = doc_processor_configer.text_field

        if hasattr(doc_processor_configer, "score_key"):
            self.score_key = doc_processor_configer.score_key
        if hasattr(doc_processor_configer, "polarity_key"):
            self.polarity_key = doc_processor_configer.polarity_key
        if hasattr(doc_processor_configer, "language_key"):
            self.language_key = doc_processor_configer.language_key

        return self

    @staticmethod
    def _validate_range(name: str, value: float, low: float, high: float) -> None:
        """Raise ValueError when ``value`` is outside ``[low, high]``."""
        if value < low or value > high:
            raise ValueError(
                f"{name} must be in [{low}, {high}], got {value}.")
