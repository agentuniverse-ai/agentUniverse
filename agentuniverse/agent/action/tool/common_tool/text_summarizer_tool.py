#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: text_summarizer_tool.py

"""Offline extractive text summarization tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency summarizer agents can
call on arbitrary text. No LLM is involved at any point: the tool never
references an LLM component, unlike the knowledge-module
``SummarizationProcessor`` (a recall post-processor whose primary mode
is abstractive LLM summarization of retrieved ``Document`` lists). This
tool is a standalone, agent-callable utility that scores and selects
sentences from a raw string, fully deterministically.

Two modes are supported:

* ``summarize`` — extractive summarization. The text is segmented into
  sentences (latin ``.!?`` plus their CJK ideographic equivalents,
  with an abbreviation guard so periods inside ``Dr.``, ``e.g.``,
  ``U.S.``, decimals such as ``3.14`` and domains such as
  ``example.com`` do not split a sentence), tokenized into words
  (latin runs or single CJK ideographs), and every sentence is scored
  by

  1. **normalized term weight** — the mean term frequency of the
     sentence's content tokens (stop words removed), which normalizes
     for sentence length, and
  2. **position bonus** — earlier sentences get a small multiplicative
     boost of up to ``+20%`` decaying linearly to ``+0%`` at the end.

  The top-N sentences are selected (ties broken by original position)
  and re-ordered by original position so the summary reads in document
  order. N comes from ``max_sentences`` (default 3) or, when ``ratio``
  is supplied, from ``ratio * sentence_count`` (rounded down, at least
  1; ``ratio`` takes precedence). The result carries the summary, the
  selected sentence indices and their scores.

* ``keywords`` — term extraction. Content-token term frequencies are
  normalized by the total content-token count and the ``top_k``
  heaviest terms are returned with counts and weights (ties broken
  alphabetically for full determinism).

Input validation is strict and happens before any computation:
malformed parameters (wrong types, empty or whitespace-only text,
unknown mode or language, ``ratio`` outside ``[0.1, 0.5]``,
``max_sentences`` outside ``[1, 100]``, ``top_k`` outside ``[1, 50]``,
oversized text) raise a ``ValueError``, mirroring the other common
tools. Errors that depend on the *content being processed* — text that
segments into zero sentences (e.g. bare punctuation) and text with no
content terms at all (every token a stop word) — are returned as a
structured ``error`` payload so an agent can react without catching
exceptions.
"""

import re
from collections import Counter
from typing import Any, ClassVar

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Latin word runs (apostrophes split, so possessives reduce to the base
# word once the "s" fragment is stop-worded) or single CJK ideographs.
_TOKEN_RE = re.compile(r"[A-Za-z0-9]+|[一-鿿]")
# Characters accumulated into the running word used by the guard.
_WORD_CHARS = frozenset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'")

# Sentence terminators. CJK terminators and the ellipsis always end a
# sentence; the latin period additionally passes through the
# abbreviation guard below. Escaped literals: ideographic full stop
# (U+3002), fullwidth exclamation mark (U+FF01), fullwidth question
# mark (U+FF1F) and ellipsis (U+2026).
_CJK_TERMINATORS = "\u3002\uff01\uff1f\u2026"
_LATIN_TERMINATORS = ".!?"

# Common English abbreviations whose trailing period must NOT split a
# sentence (matched case-insensitively against the word immediately
# before the period). Single letters (initials such as "J." or the "U."
# and "S." of "U.S.") and all-digit tokens (decimals such as "3.14")
# are guarded separately in _period_ends_sentence.
_ABBREVIATIONS = frozenset(
    {
        "mr",
        "mrs",
        "ms",
        "dr",
        "prof",
        "sr",
        "jr",
        "st",
        "vs",
        "etc",
        "inc",
        "ltd",
        "co",
        "corp",
        "dept",
        "univ",
        "assn",
        "approx",
        "min",
        "max",
        "no",
        "nos",
        "vol",
        "vols",
        "pp",
        "fig",
        "figs",
        "eq",
        "eqs",
        "al",
        "ca",
        "cf",
        "ed",
        "eds",
        "esq",
        "phd",
        "md",
        "ba",
        "ma",
        "msc",
        "usa",
        "eg",
        "ie",
    }
)

# Stop words removed before scoring. ``language`` selects exactly one
# list; tokenization itself always understands both scripts, so mixed
# text never fails.
_EN_STOP_WORDS = frozenset(
    {
        "a",
        "about",
        "above",
        "after",
        "again",
        "against",
        "all",
        "am",
        "an",
        "and",
        "any",
        "are",
        "as",
        "at",
        "be",
        "because",
        "been",
        "before",
        "being",
        "below",
        "between",
        "both",
        "but",
        "by",
        "can",
        "could",
        "did",
        "do",
        "does",
        "doing",
        "down",
        "during",
        "each",
        "few",
        "for",
        "from",
        "further",
        "had",
        "has",
        "have",
        "having",
        "he",
        "her",
        "here",
        "hers",
        "herself",
        "him",
        "himself",
        "his",
        "how",
        "i",
        "if",
        "in",
        "into",
        "is",
        "it",
        "its",
        "itself",
        "just",
        "me",
        "more",
        "most",
        "my",
        "myself",
        "no",
        "nor",
        "not",
        "now",
        "of",
        "off",
        "on",
        "once",
        "only",
        "or",
        "other",
        "our",
        "ours",
        "ourselves",
        "out",
        "over",
        "own",
        "s",
        "t",
        "don",
        "re",
        "ve",
        "ll",
        "d",
        "m",
        "o",
        "y",
        "ain",
        "aren",
        "couldn",
        "didn",
        "doesn",
        "hadn",
        "hasn",
        "haven",
        "isn",
        "wasn",
        "weren",
        "won",
        "wouldn",
        "same",
        "she",
        "should",
        "so",
        "some",
        "such",
        "than",
        "that",
        "the",
        "their",
        "theirs",
        "them",
        "themselves",
        "then",
        "there",
        "these",
        "they",
        "this",
        "those",
        "through",
        "to",
        "too",
        "under",
        "until",
        "up",
        "very",
        "was",
        "we",
        "were",
        "what",
        "when",
        "where",
        "which",
        "while",
        "who",
        "whom",
        "why",
        "will",
        "with",
        "you",
        "your",
        "yours",
        "yourself",
        "yourselves",
    }
)
_ZH_STOP_WORDS = frozenset(
    {
        "的",
        "了",
        "是",
        "在",
        "我",
        "你",
        "您",
        "他",
        "她",
        "它",
        "们",
        "和",
        "与",
        "就",
        "都",
        "而",
        "及",
        "跟",
        "着",
        "或",
        "没",
        "不",
        "很",
        "也",
        "被",
        "把",
        "让",
        "从",
        "到",
        "向",
        "对",
        "为",
        "以",
        "于",
        "将",
        "地",
        "得",
        "过",
        "个",
        "这",
        "那",
        "些",
        "什",
        "么",
        "哪",
        "谁",
        "怎",
        "样",
        "此",
        "因",
        "所",
        "但",
        "可",
        "然",
        "后",
        "已",
        "还",
        "再",
        "又",
        "只",
        "等",
        "啊",
        "吧",
        "呢",
        "吗",
        "呀",
        "哦",
        "嗯",
        "上",
        "下",
        "里",
        "会",
        "能",
        "要",
    }
)

# Multiplicative boost for the first sentence, decaying linearly to
# zero at the last sentence: 1 + _POSITION_BONUS * (1 - idx / total).
_POSITION_BONUS = 0.2

# Scores and keyword weights are rounded to this many decimals so the
# returned JSON is stable across platforms.
_ROUND_DIGITS = 6


class TextSummarizerTool(Tool):
    """Offline extractive summarization tool built purely on the stdlib.

    Attributes:
        max_text_chars (int): Upper bound on the ``text`` input length;
            longer inputs are rejected before any work.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True, protected_namespaces=())

    name: str = "text_summarizer_tool"
    description: str = (
        "Text summarizer tool — offline extractive summarization and "
        "keyword extraction in pure Python, no LLM and no network "
        "required. mode='summarize' scores sentences by normalized term "
        "frequency with a position bonus and returns the top-N "
        "sentences re-ordered by original position (N from "
        "max_sentences, default 3, or ratio, 0.1-0.5); mode='keywords' "
        "returns the top_k heaviest content terms with weights. "
        "language='en'/'zh' selects tokenization stop words."
    )

    MODES: ClassVar[tuple] = ("summarize", "keywords")
    LANGUAGES: ClassVar[tuple] = ("en", "zh")
    STOP_WORDS: ClassVar[dict[str, frozenset]] = {
        "en": _EN_STOP_WORDS,
        "zh": _ZH_STOP_WORDS,
    }

    max_text_chars: int = 100_000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any = None,
        text: Any = None,
        max_sentences: Any = None,
        ratio: Any = None,
        language: Any = None,
        top_k: Any = None,
    ) -> dict[str, Any]:
        """Run one summarization / keyword extraction.

        Args:
            mode (str): ``summarize`` or ``keywords``.
            text (str): The text to process. Required; a non-empty
                string of at most ``max_text_chars`` characters.
            max_sentences (int): Summarize mode — number of sentences
                to keep (default 3, range 1-100). Ignored when
                ``ratio`` is supplied.
            ratio (float): Summarize mode — alternative selection
                strategy keeping ``ratio * sentence_count`` sentences
                (rounded down, at least 1); range 0.1-0.5. Takes
                precedence over ``max_sentences``.
            language (str): ``en`` (default) or ``zh`` — selects the
                stop-word list used for scoring. Tokenization always
                understands both scripts, so mixed text is safe.
            top_k (int): Keywords mode — number of terms to return
                (default 10, range 1-50).

        Returns:
            Dict[str, Any]: For ``summarize``: the ``summary`` string,
            ``selected_indices`` and per-sentence ``scores``,
            ``sentence_count``, ``selected_count``, the ``strategy``
            used and the ``language``. For ``keywords``: the ``top_k``
            and a ``keywords`` list of ``{term, count, weight}``
            entries sorted by weight. Content-level failures (no
            sentences, no content terms) return a structured ``error``
            payload instead of raising.

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})")
        clean_language = self._validate_language(language)
        clean_text = self._validate_text(text)
        context: dict[str, Any] = {"mode": mode, "language": clean_language}
        sentences = self._segment_sentences(clean_text)
        if not sentences:
            return self._error_result(
                context,
                error_type="no_sentences",
                message=(
                    "text does not contain any sentence — at least one "
                    "non-empty segment terminated by a latin '.', '!' "
                    "or '?', a CJK terminator or a newline is required "
                    f"(got {clean_text[:64]!r})"
                ),
            )
        stop_words = self.STOP_WORDS[clean_language]
        _token_counts, sentence_tokens = self._tokenize(sentences)
        content_counts, content_per_sentence = self._drop_stop_words(sentence_tokens, stop_words)
        total_content = sum(content_counts.values())
        if total_content == 0:
            return self._error_result(
                context,
                error_type="no_content_terms",
                message=(
                    "text contains no content terms — every token is a " f"stop word for language {clean_language!r}"
                ),
            )
        if mode == "keywords":
            return self._run_keywords(context, top_k, content_counts, total_content)
        return self._run_summarize(
            context,
            clean_language,
            sentences,
            content_per_sentence,
            content_counts,
            max_sentences,
            ratio,
        )

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"text_summarizer_tool: {message}")

    def _validate_text(self, text: Any) -> str:
        """Validate the ``text`` input against the configured limit."""
        if text is None or isinstance(text, bool) or not isinstance(text, str):
            self._invalid(f"text must be a non-empty string (got {text!r})")
        if not text:
            self._invalid("text must be a non-empty string (got '')")
        if not text.strip():
            self._invalid("text must contain non-whitespace characters")
        if len(text) > self.max_text_chars:
            self._invalid(
                f"text exceeds the {self.max_text_chars:,}-character limit "
                f"(got {len(text):,} characters)"
            )
        return text

    @classmethod
    def _validate_language(cls, language: Any) -> str:
        """Validate the ``language`` hint (defaults to English)."""
        if language is None:
            return "en"
        if isinstance(language, bool) or not isinstance(language, str):
            cls._invalid(f"language must be one of: {', '.join(cls.LANGUAGES)} " f"(got {language!r})")
        clean = language.strip().lower()
        if clean not in cls.LANGUAGES:
            cls._invalid(f"language must be one of: {', '.join(cls.LANGUAGES)} " f"(got {language!r})")
        return clean

    @classmethod
    def _validate_max_sentences(cls, max_sentences: Any) -> int:
        """Validate the ``max_sentences`` selector."""
        if max_sentences is None:
            return 3
        if isinstance(max_sentences, bool) or not isinstance(max_sentences, int):
            cls._invalid(f"max_sentences must be an integer between 1 and 100 " f"(got {max_sentences!r})")
        if not 1 <= max_sentences <= 100:
            cls._invalid(f"max_sentences must be an integer between 1 and 100 " f"(got {max_sentences!r})")
        return max_sentences

    @classmethod
    def _validate_ratio(cls, ratio: Any) -> float | None:
        """Validate the ``ratio`` alternative selection strategy."""
        if ratio is None:
            return None
        if isinstance(ratio, bool) or not isinstance(ratio, (int, float)):
            cls._invalid(f"ratio must be a number between 0.1 and 0.5 (got {ratio!r})")
        if not 0.1 <= ratio <= 0.5:
            cls._invalid(f"ratio must be a number between 0.1 and 0.5 (got {ratio!r})")
        return float(ratio)

    @classmethod
    def _validate_top_k(cls, top_k: Any) -> int:
        """Validate the keywords-mode ``top_k`` selector."""
        if top_k is None:
            return 10
        if isinstance(top_k, bool) or not isinstance(top_k, int):
            cls._invalid(f"top_k must be an integer between 1 and 50 (got {top_k!r})")
        if not 1 <= top_k <= 50:
            cls._invalid(f"top_k must be an integer between 1 and 50 (got {top_k!r})")
        return top_k

    # ------------------------------------------------------------------ #
    # Sentence segmentation (with abbreviation guard)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _segment_sentences(text: str) -> list[str]:
        """Split ``text`` into sentences.

        Terminators are the latin ``.!?``, their CJK ideographic
        equivalents and the ellipsis (a run of two or more '.'
        collapses to a single ellipsis terminator first). Newlines
        terminate the current segment. A latin '.' does NOT terminate
        when (a) it is immediately followed by an alphanumeric
        character (decimals like ``3.14``, domains like
        ``example.com``), or (b) the word immediately before it is a
        common abbreviation (``Dr.``, ``e.g.`` ...), a single letter
        (initials, ``U.S.``) or all digits. Segments without any word
        character (bare punctuation) are dropped.
        """
        # Collapse '...' runs into a single ellipsis terminator so they
        # never produce empty fragments.
        collapsed = re.sub(r"\.{2,}", "…", text)
        sentences: list[str] = []
        buffer: list[str] = []
        word: list[str] = []
        total = len(collapsed)

        def _flush() -> None:
            segment = "".join(buffer).strip()
            # A sentence must carry at least one word character; bare
            # punctuation runs ('!!!', '。。。') are dropped so that
            # punctuation-only text surfaces as a no_sentences error.
            if segment and any(ch.isalnum() for ch in segment):
                sentences.append(segment)
            buffer.clear()

        index = 0
        while index < total:
            char = collapsed[index]
            if char in "\r\n":
                _flush()
                word.clear()
                index += 1
                continue
            buffer.append(char)
            if char in _WORD_CHARS:
                word.append(char)
            elif char in _CJK_TERMINATORS:
                _flush()
                word.clear()
            elif char in _LATIN_TERMINATORS:
                if char != "." or TextSummarizerTool._period_ends_sentence(collapsed, index, word):
                    _flush()
                    word.clear()
                else:
                    word.clear()
            else:
                word.clear()
            index += 1
        _flush()
        return sentences

    @staticmethod
    def _period_ends_sentence(text: str, index: int, word_run: list[str]) -> bool:
        """Decide whether the latin '.' at ``index`` ends its sentence.

        Returns False (guard applies, no boundary) when the next
        character is alphanumeric — decimals ``3.14``, domains
        ``example.com`` — or the word run before the period is a known
        abbreviation, a single letter (initials, ``U.S.``), or all
        digits.
        """
        if index + 1 < len(text) and text[index + 1].isalnum():
            return False
        token = "".join(word_run).rstrip("'").lower()
        if not token:
            return True
        return not (token in _ABBREVIATIONS or len(token) == 1 or token.isdigit())

    # ------------------------------------------------------------------ #
    # Tokenization and stop-word removal
    # ------------------------------------------------------------------ #

    @staticmethod
    def _tokenize(sentences: list[str]) -> tuple[Counter, list[list[str]]]:
        """Tokenize every sentence into (lowercased) word tokens.

        Latin runs become one token each; every CJK ideograph is its
        own token. Returns the document-wide token counter and the
        per-sentence token lists.
        """
        token_counts: Counter = Counter()
        sentence_tokens: list[list[str]] = []
        for sentence in sentences:
            tokens = [token.lower() if token.isascii() else token for token in _TOKEN_RE.findall(sentence)]
            sentence_tokens.append(tokens)
            token_counts.update(tokens)
        return token_counts, sentence_tokens

    @staticmethod
    def _drop_stop_words(sentence_tokens: list[list[str]], stop_words: frozenset) -> tuple[Counter, list[list[str]]]:
        """Remove stop words from the per-sentence token lists.

        Returns the document-wide content-token counter and the
        per-sentence content-token lists.
        """
        content_counts: Counter = Counter()
        content_per_sentence: list[list[str]] = []
        for tokens in sentence_tokens:
            content = [token for token in tokens if token not in stop_words]
            content_per_sentence.append(content)
            content_counts.update(content)
        return content_counts, content_per_sentence

    # ------------------------------------------------------------------ #
    # summarize mode
    # ------------------------------------------------------------------ #

    @staticmethod
    def _floor_product(ratio: float, total: int) -> int:
        """Floor ``ratio * total`` immune to binary-float rounding error.

        ``int(0.29 * 100)`` truncates the float product 28.999999999999996
        to 28 even though the exact product is 29. The epsilon-corrected
        floor lands on the mathematically expected value whenever the
        true product is (within 1e-9 of) an integer, and is unchanged
        otherwise.
        """
        return int(ratio * total + 1e-9)

    def _run_summarize(
        self,
        context: dict[str, Any],
        language: str,
        sentences: list[str],
        content_per_sentence: list[list[str]],
        content_counts: Counter,
        max_sentences: Any,
        ratio: Any,
    ) -> dict[str, Any]:
        """Score, select and re-order the top sentences."""
        clean_max = self._validate_max_sentences(max_sentences)
        clean_ratio = self._validate_ratio(ratio)
        total = len(sentences)
        if clean_ratio is not None:
            strategy = "ratio"
            keep = max(1, min(total, self._floor_product(clean_ratio, total)))
        else:
            strategy = "max_sentences"
            keep = min(clean_max, total)

        scores: list[float] = []
        for position, content in enumerate(content_per_sentence):
            raw = sum(content_counts[token] for token in content) / len(content) if content else 0.0
            position_weight = 1.0 + _POSITION_BONUS * (1.0 - position / total)
            scores.append(round(raw * position_weight, _ROUND_DIGITS))

        # Rank by score descending, ties broken by original position;
        # present the selection in original document order.
        ranked = sorted(range(total), key=lambda i: (-scores[i], i))[:keep]
        selected = sorted(ranked)
        separator = "" if language == "zh" else " "
        summary = separator.join(sentences[i] for i in selected)
        return {
            **context,
            "strategy": strategy,
            "sentence_count": total,
            "selected_count": len(selected),
            "selected_indices": selected,
            "scores": [scores[i] for i in selected],
            "summary": summary,
        }

    # ------------------------------------------------------------------ #
    # keywords mode
    # ------------------------------------------------------------------ #

    def _run_keywords(
        self,
        context: dict[str, Any],
        top_k: Any,
        content_counts: Counter,
        total_content: int,
    ) -> dict[str, Any]:
        """Return the heaviest content terms with normalized weights."""
        clean_top_k = self._validate_top_k(top_k)
        ranked = sorted(content_counts.items(), key=lambda item: (-item[1], item[0]))[:clean_top_k]
        keywords = [
            {
                "term": term,
                "count": count,
                "weight": round(count / total_content, _ROUND_DIGITS),
            }
            for term, count in ranked
        ]
        return {**context, "top_k": clean_top_k, "keywords": keywords}

    # ------------------------------------------------------------------ #
    # Error payloads (structured, returned instead of raising)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _error_result(context: dict[str, Any], error_type: str, message: str) -> dict[str, Any]:
        """Build a structured error payload."""
        return {
            **context,
            "error": {"type": error_type, "message": str(message)[:500]},
        }
