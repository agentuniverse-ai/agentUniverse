#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: ngram_suggester_tool.py

"""N-gram frequency modeling and next-candidate suggestion tool built
purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency statistical text
utility: agents can build small n-gram language models from a sample
text and then ask for the most likely next words, character n-gram
frequencies, or a Laplace-smoothed average negative log probability of
a held-out text.

Four modes:

* ``model`` — build a word n-gram continuation table from ``text``.
  Sentences are split on ``.`` ``!`` ``?`` and their CJK equivalents
  (``。`` ``！`` ``？``); every sentence is padded with ``n - 1``
  leading ``<START>`` symbols and one trailing ``<END>`` symbol, and
  every length-``n`` window contributes one observation
  ``context (n-1 words, space-joined) -> next word``. The result maps
  each context to ``[word, count, probability]`` rows sorted by count
  descending then word ascending, truncated to ``top_k`` rows per
  context (default 10). Probabilities are relative to *all*
  continuations of the context, so the retained rows of a truncated
  context may sum to less than 1. For ``n = 1`` the context is the
  empty string (the empty tuple). Optional flags: ``lowercase``
  (default off) and ``min_token_length`` (tokens shorter than the
  limit are dropped before modeling; default 1 keeps everything).
* ``next`` — given the JSON produced by ``model`` and a context
  phrase of exactly ``n - 1`` words, return the candidate continuations,
  the retained candidate count sum, and whether the context was
  observed. Unseen contexts return a structured note instead of an
  empty guess.
* ``char_ngrams`` — character n-gram frequency table (``n`` 2..5).
  With ``cross_word=False`` (default) n-grams never cross whitespace
  and contain no spaces; with ``cross_word=True`` they are taken over
  the text with whitespace runs normalized to single spaces, so
  n-grams may contain spaces and cross word boundaries.
* ``perplexity-lite`` — average negative natural-log probability of
  the observed continuations of ``text`` under the model. Continuations
  found in the model use the model probability; unseen ones use
  add-one Laplace smoothing with the model vocabulary size: seen
  context with unseen next word gets ``1 / (context_count + V + 1)``,
  a fully unseen context gets ``1 / (V + 1)``. This is a simple
  Laplace-smoothed average negative log likelihood — it is **not**
  true perplexity and is deliberately named and documented as such.

Input validation is strict and happens before any computation:
malformed parameters (unknown mode, missing/empty text, ``n`` out of
range, non-integer counts, wrong boolean types, a context with the
wrong number of words, oversized inputs) raise a ``ValueError``,
mirroring the other common tools. Errors that depend on the *content
being processed* — a ``model`` JSON string that does not parse or does
not match the model-mode output shape — are returned as a structured
``error`` payload so an agent can react without catching exceptions.
"""

import json
import math
import re
from collections import Counter
from typing import Any, ClassVar, Dict, List, Tuple

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Sentence terminators (ASCII + CJK full-width forms).
_SENTENCE_SPLIT = re.compile("[.!?。！？]")
# Any run of whitespace, used to normalize the char-ngram corpus.
_WHITESPACE = re.compile(r"\s+")

START = "<START>"
END = "<END>"


class NgramSuggesterTool(Tool):
    """N-gram frequency modeling and next-candidate suggestion tool.

    Attributes:
        max_text_chars (int): Upper bound on ``text`` / ``context``
            input length; longer inputs are rejected before any work.
        max_model_chars (int): Upper bound on a ``model`` JSON string.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "ngram_suggester_tool"
    description: str = (
        "N-gram suggester tool — pure Python stdlib, no network "
        "required. Build a word n-gram continuation model with "
        "<START>/<END> sentence markers from a sample text "
        "(mode='model', n 1-5, optional lowercasing and minimum token "
        "length), suggest the most likely next words for a context "
        "phrase (mode='next'), list character n-gram frequencies "
        "(mode='char_ngrams', n 2-5, optional cross-word n-grams), and "
        "score a text under a model with a Laplace-smoothed average "
        "negative log probability (mode='perplexity-lite' — not true "
        "perplexity)."
    )

    MODES: ClassVar[tuple] = ("model", "next", "char_ngrams", "perplexity-lite")
    WORD_N_RANGE: ClassVar[tuple] = (1, 5)
    CHAR_N_RANGE: ClassVar[tuple] = (2, 5)
    TOP_K_RANGE: ClassVar[tuple] = (1, 1000)
    MIN_TOKEN_LENGTH_RANGE: ClassVar[tuple] = (1, 50)

    max_text_chars: int = 100_000
    max_model_chars: int = 1_000_000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        text: Any = None,
        n: Any = None,
        model: Any = None,
        context: Any = None,
        lowercase: Any = None,
        min_token_length: Any = None,
        top_k: Any = None,
        cross_word: Any = None,
    ) -> Dict[str, Any]:
        """Run one n-gram modeling / suggestion operation.

        Args:
            mode (str): One of ``model`` / ``next`` / ``char_ngrams`` /
                ``perplexity-lite``.
            text (str): The sample text. Required for the ``model``,
                ``char_ngrams`` and ``perplexity-lite`` modes; not used
                by ``next``.
            n (int): The n-gram order — 1 to 5 for ``model``, 2 to 5
                for ``char_ngrams``. Required for those two modes; the
                ``next`` and ``perplexity-lite`` modes read ``n`` from
                the model.
            model (dict | str): The model-mode output, as a dict or its
                JSON string. Required for ``next`` and
                ``perplexity-lite``; not used by the other modes.
            context (str): The ``next``-mode context phrase — exactly
                ``n - 1`` whitespace-separated words (the empty string
                for a unigram model). Defaults to ``""``.
            lowercase (bool): ``model`` mode — lowercase the text
                before tokenizing (default off).
            min_token_length (int): ``model`` mode — drop tokens shorter
                than this length before modeling (1 to 50, default 1).
            top_k (int): Rows kept per context (``model`` / ``next``) or
                table length (``char_ngrams``); 1 to 1000, default 10.
            cross_word (bool): ``char_ngrams`` mode — allow n-grams to
                cross word boundaries over whitespace-normalized text
                (default off).

        Returns:
            Dict[str, Any]: The operation result plus call context, or
                a structured ``error`` payload for content-level
                failures (model JSON that does not parse, or a model
                dict that does not match the model-mode output shape).

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        if mode == "model":
            return self._run_model(
                text, n, lowercase, min_token_length, top_k
            )
        if mode == "char_ngrams":
            return self._run_char_ngrams(text, n, cross_word, top_k)
        if mode == "next":
            return self._run_next(model, context)
        return self._run_perplexity_lite(text, model)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"ngram_suggester_tool: {message}")

    @classmethod
    def _validate_text(cls, text: Any) -> str:
        """Validate the ``text`` input (non-empty, bounded)."""
        if text is None or isinstance(text, bool) or not isinstance(text, str):
            cls._invalid(f"text must be a non-empty string (got {text!r})")
        if not text:
            cls._invalid("text must be a non-empty string (got '')")
        if len(text) > 100_000:
            cls._invalid(
                f"text exceeds the {100_000:,}-character limit "
                f"(got {len(text):,} characters)"
            )
        return text

    @classmethod
    def _validate_n(cls, n: Any, low: int, high: int) -> int:
        """Validate the n-gram order ``n`` (strict int within range)."""
        if isinstance(n, bool) or not isinstance(n, int):
            cls._invalid(f"n must be an integer between {low} and {high} (got {n!r})")
        if n < low or n > high:
            cls._invalid(f"n must be an integer between {low} and {high} (got {n})")
        return n

    @classmethod
    def _validate_bool(cls, value: Any, label: str, default: bool) -> bool:
        """Validate an optional boolean flag (None means the default)."""
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        cls._invalid(f"{label} must be a boolean (got {value!r})")

    @classmethod
    def _validate_int_option(
        cls, value: Any, label: str, default: int, low: int, high: int
    ) -> int:
        """Validate an optional integer option within an inclusive range."""
        if value is None:
            return default
        if isinstance(value, bool) or not isinstance(value, int):
            cls._invalid(
                f"{label} must be an integer between {low} and {high} (got {value!r})"
            )
        if value < low or value > high:
            cls._invalid(
                f"{label} must be an integer between {low} and {high} (got {value})"
            )
        return value

    @classmethod
    def _validate_model_param(cls, model: Any) -> Any:
        """Validate the ``model`` *parameter* (dict or JSON string only)."""
        if model is None:
            cls._invalid(
                "model is required for the next and perplexity-lite modes "
                "and must be the model-mode output dict or its JSON string "
                "(got None)"
            )
        if isinstance(model, bool) or not isinstance(model, (dict, str)):
            cls._invalid(
                "model must be the model-mode output dict or its JSON "
                f"string (got {model!r})"
            )
        if isinstance(model, str):
            if not model:
                cls._invalid("model must be a non-empty JSON string (got '')")
            if len(model) > 1_000_000:
                cls._invalid(
                    f"model exceeds the {1_000_000:,}-character limit "
                    f"(got {len(model):,} characters)"
                )
        return model

    @staticmethod
    def _error_result(
        context: Dict[str, Any], error_type: str, message: str
    ) -> Dict[str, Any]:
        """Build a structured error payload."""
        return {
            **context,
            "error": {"type": error_type, "message": str(message)[:500]},
        }

    # ------------------------------------------------------------------ #
    # Model-shape validation (content-level — structured errors)
    # ------------------------------------------------------------------ #

    @classmethod
    def _parse_model(cls, model: Any) -> Dict[str, Any]:
        """Parse and strictly validate a model-mode output.

        Returns the normalized model dict; raises ``_ModelShapeError``
        for content-level problems, which callers convert into a
        structured ``error`` payload.
        """
        if isinstance(model, str):
            try:
                parsed = json.loads(model)
            except json.JSONDecodeError as exc:
                raise _ModelJsonError(
                    "model string is not valid JSON: "
                    f"{exc.msg} (line {exc.lineno}, column {exc.colno})"
                )
            if isinstance(parsed, bool) or not isinstance(parsed, dict):
                raise _ModelShapeError(
                    "model must decode to a JSON object (model-mode output "
                    f"dict); got {type(parsed).__name__}"
                )
            model = parsed

        missing = [key for key in ("n", "table") if key not in model]
        if missing:
            raise _ModelShapeError(
                "model is missing required key(s): "
                f"{', '.join(missing)} — expected the model-mode output "
                "with keys n, table (and typically lowercase, "
                "min_token_length, vocabulary_size, total_contexts, "
                "total_continuations)"
            )
        n = model["n"]
        if isinstance(n, bool) or not isinstance(n, int):
            raise _ModelShapeError(f"model['n'] must be an integer (got {n!r})")
        if n < cls.WORD_N_RANGE[0] or n > cls.WORD_N_RANGE[1]:
            raise _ModelShapeError(
                f"model['n'] must be between 1 and 5 (got {n})"
            )
        table = model["table"]
        if not isinstance(table, dict):
            raise _ModelShapeError(
                "model['table'] must be a dict mapping context strings to "
                f"[word, count, probability] rows (got {type(table).__name__})"
            )
        for ctx, rows in table.items():
            if not isinstance(ctx, str):
                raise _ModelShapeError(
                    "model['table'] keys must be context strings "
                    f"(got non-string key {ctx!r})"
                )
            if not isinstance(rows, list):
                raise _ModelShapeError(
                    f"model['table'][{ctx!r}] must be a list of "
                    f"[word, count, probability] rows (got {type(rows).__name__})"
                )
            for row in rows:
                if not isinstance(row, list) or len(row) != 3:
                    raise _ModelShapeError(
                        f"model['table'][{ctx!r}] rows must be 3-item "
                        f"[word, count, probability] lists (got {row!r})"
                    )
                word, count, probability = row
                if isinstance(word, bool) or not isinstance(word, str) or not word:
                    raise _ModelShapeError(
                        f"model['table'][{ctx!r}] row words must be non-empty "
                        f"strings (got {word!r})"
                    )
                if isinstance(count, bool) or not isinstance(count, int) or count < 1:
                    raise _ModelShapeError(
                        f"model['table'][{ctx!r}] row counts must be integers "
                        f">= 1 (got {count!r} for word {word!r})"
                    )
                if (
                    isinstance(probability, bool)
                    or not isinstance(probability, (int, float))
                    or not (0 < probability <= 1)
                ):
                    raise _ModelShapeError(
                        f"model['table'][{ctx!r}] row probabilities must be "
                        f"numbers in (0, 1] (got {probability!r} for word {word!r})"
                    )
        lowercase = model.get("lowercase", False)
        if not isinstance(lowercase, bool):
            raise _ModelShapeError(
                f"model['lowercase'] must be a boolean (got {lowercase!r})"
            )
        min_token_length = model.get("min_token_length", 1)
        if (
            isinstance(min_token_length, bool)
            or not isinstance(min_token_length, int)
            or not (
                cls.MIN_TOKEN_LENGTH_RANGE[0]
                <= min_token_length
                <= cls.MIN_TOKEN_LENGTH_RANGE[1]
            )
        ):
            raise _ModelShapeError(
                "model['min_token_length'] must be an integer between 1 and "
                f"50 (got {min_token_length!r})"
            )
        vocabulary_size = model.get("vocabulary_size")
        if vocabulary_size is not None and (
            isinstance(vocabulary_size, bool)
            or not isinstance(vocabulary_size, int)
            or vocabulary_size < 0
        ):
            raise _ModelShapeError(
                "model['vocabulary_size'] must be an integer >= 0 "
                f"(got {vocabulary_size!r})"
            )
        return {
            "n": n,
            "table": table,
            "lowercase": lowercase,
            "min_token_length": min_token_length,
            "vocabulary_size": vocabulary_size,
        }

    # ------------------------------------------------------------------ #
    # Shared word-mode tokenization
    # ------------------------------------------------------------------ #

    @classmethod
    def _sentence_tokens(
        cls, text: str, lowercase: bool, min_token_length: int
    ) -> List[List[str]]:
        """Split text into sentences and filter the sentence tokens.

        Order of operations (documented): lowercase first, then drop
        tokens shorter than ``min_token_length``. Sentences with no
        surviving tokens are skipped.
        """
        sentences: List[List[str]] = []
        for segment in _SENTENCE_SPLIT.split(text):
            tokens = segment.split()
            if lowercase:
                tokens = [token.lower() for token in tokens]
            if min_token_length > 1:
                tokens = [t for t in tokens if len(t) >= min_token_length]
            if tokens:
                sentences.append(tokens)
        return sentences

    @classmethod
    def _continuations(
        cls, sentences: List[List[str]], n: int
    ) -> List[Tuple[str, str]]:
        """Yield (context_key, next_word) observations for every sentence.

        Each sentence is padded with ``n - 1`` leading ``<START>``
        symbols and one trailing ``<END>`` symbol; every length-``n``
        window contributes one observation. For ``n = 1`` the context
        key is the empty string (the empty tuple).
        """
        observations: List[Tuple[str, str]] = []
        for tokens in sentences:
            padded = [START] * (n - 1) + tokens + [END]
            for i in range(n - 1, len(padded)):
                context_key = " ".join(padded[i - (n - 1): i])
                observations.append((context_key, padded[i]))
        return observations

    # ------------------------------------------------------------------ #
    # model mode
    # ------------------------------------------------------------------ #

    def _run_model(
        self,
        text: Any,
        n: Any,
        lowercase: Any,
        min_token_length: Any,
        top_k: Any,
    ) -> Dict[str, Any]:
        """Build the word n-gram continuation table."""
        clean_text = self._validate_text(text)
        clean_n = self._validate_n(n, *self.WORD_N_RANGE)
        clean_lowercase = self._validate_bool(lowercase, "lowercase", False)
        clean_min_len = self._validate_int_option(
            min_token_length,
            "min_token_length",
            1,
            *self.MIN_TOKEN_LENGTH_RANGE,
        )
        clean_top_k = self._validate_int_option(
            top_k, "top_k", 10, *self.TOP_K_RANGE
        )

        sentences = self._sentence_tokens(
            clean_text, clean_lowercase, clean_min_len
        )
        observations = self._continuations(sentences, clean_n)

        # Raw counts: context -> {next word -> count}.
        raw: Dict[str, Counter] = {}
        for context_key, word in observations:
            raw.setdefault(context_key, Counter())[word] += 1

        vocabulary = {word for _, word in observations}
        table: Dict[str, List[List[Any]]] = {}
        truncated_contexts = 0
        total_continuations = 0
        for context_key in sorted(raw):
            counts = raw[context_key]
            context_total = sum(counts.values())
            total_continuations += context_total
            rows = sorted(
                counts.items(), key=lambda item: (-item[1], item[0])
            )
            if len(rows) > clean_top_k:
                truncated_contexts += 1
            table[context_key] = [
                [word, count, count / context_total]
                for word, count in rows[:clean_top_k]
            ]

        return {
            "mode": "model",
            "n": clean_n,
            "lowercase": clean_lowercase,
            "min_token_length": clean_min_len,
            "top_k": clean_top_k,
            "vocabulary_size": len(vocabulary),
            "total_contexts": len(table),
            "total_continuations": total_continuations,
            "truncated_contexts": truncated_contexts,
            "table": table,
        }

    # ------------------------------------------------------------------ #
    # next mode
    # ------------------------------------------------------------------ #

    def _run_next(self, model: Any, context: Any) -> Dict[str, Any]:
        """Suggest continuation candidates for one context phrase."""
        clean_model_param = self._validate_model_param(model)
        mode_context: Dict[str, Any] = {"mode": "next"}
        try:
            parsed = self._parse_model(clean_model_param)
        except _ModelJsonError as exc:
            return self._error_result(
                mode_context, error_type="invalid_model_json", message=str(exc)
            )
        except _ModelShapeError as exc:
            return self._error_result(
                mode_context, error_type="invalid_model", message=str(exc)
            )
        n = parsed["n"]
        table = parsed["table"]
        lowercase = parsed["lowercase"]

        if context is None:
            context = ""
        if isinstance(context, bool) or not isinstance(context, str):
            self._invalid(
                f"context must be a string of exactly {n - 1} "
                f"whitespace-separated words (got {context!r})"
            )
        if len(context) > self.max_text_chars:
            self._invalid(
                f"context exceeds the {self.max_text_chars:,}-character "
                f"limit (got {len(context):,} characters)"
            )
        tokens = context.lower().split() if lowercase else context.split()
        if len(tokens) != n - 1:
            self._invalid(
                f"context must contain exactly {n - 1} word(s) for an "
                f"n={n} model (got {len(tokens)}: {context!r})"
            )
        context_key = " ".join(tokens)

        result: Dict[str, Any] = {
            "mode": "next",
            "n": n,
            "context": context_key,
        }
        if context_key not in table:
            return {
                **result,
                "context_seen": False,
                "candidates": [],
                "total_count": 0,
                "note": {
                    "type": "unseen_context",
                    "message": (
                        f"context {context_key!r} was not observed in the "
                        "model, so it has no continuation candidates; "
                        "contexts in the model are space-joined token "
                        "tuples of exactly "
                        f"{n - 1} word(s)"
                    ),
                },
            }
        rows = table[context_key]
        return {
            **result,
            "context_seen": True,
            "candidates": [list(row) for row in rows],
            "total_count": sum(row[1] for row in rows),
        }

    # ------------------------------------------------------------------ #
    # char_ngrams mode
    # ------------------------------------------------------------------ #

    def _run_char_ngrams(
        self, text: Any, n: Any, cross_word: Any, top_k: Any
    ) -> Dict[str, Any]:
        """Build the character n-gram frequency table."""
        clean_text = self._validate_text(text)
        clean_n = self._validate_n(n, *self.CHAR_N_RANGE)
        clean_cross = self._validate_bool(cross_word, "cross_word", False)
        clean_top_k = self._validate_int_option(
            top_k, "top_k", 10, *self.TOP_K_RANGE
        )

        counts: Counter = Counter()
        if clean_cross:
            # Whitespace runs collapse to single spaces; n-grams may
            # contain spaces and cross word boundaries.
            normalized = " ".join(clean_text.split())
            for i in range(len(normalized) - clean_n + 1):
                counts[normalized[i: i + clean_n]] += 1
        else:
            # N-grams never cross whitespace and never contain spaces.
            for word in clean_text.split():
                for i in range(len(word) - clean_n + 1):
                    counts[word[i: i + clean_n]] += 1

        total_ngrams = sum(counts.values())
        ordered = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
        table = [
            [ngram, count, count / total_ngrams]
            for ngram, count in ordered[:clean_top_k]
        ]
        return {
            "mode": "char_ngrams",
            "n": clean_n,
            "cross_word": clean_cross,
            "top_k": clean_top_k,
            "total_ngrams": total_ngrams,
            "distinct_ngrams": len(counts),
            "table": table,
        }

    # ------------------------------------------------------------------ #
    # perplexity-lite mode
    # ------------------------------------------------------------------ #

    def _run_perplexity_lite(self, text: Any, model: Any) -> Dict[str, Any]:
        """Score a text's continuations under a model (Laplace NLL)."""
        clean_text = self._validate_text(text)
        clean_model_param = self._validate_model_param(model)
        mode_context: Dict[str, Any] = {"mode": "perplexity-lite"}
        try:
            parsed = self._parse_model(clean_model_param)
        except _ModelJsonError as exc:
            return self._error_result(
                mode_context, error_type="invalid_model_json", message=str(exc)
            )
        except _ModelShapeError as exc:
            return self._error_result(
                mode_context, error_type="invalid_model", message=str(exc)
            )
        n = parsed["n"]
        table = parsed["table"]
        if parsed["vocabulary_size"] is not None:
            vocabulary_size = parsed["vocabulary_size"]
        else:
            # Derive the vocabulary from the retained rows (the model
            # output normally carries the pre-truncation count).
            vocabulary_size = len(
                {row[0] for rows in table.values() for row in rows}
            )
        if vocabulary_size < 1:
            vocabulary_size = 1

        sentences = self._sentence_tokens(
            clean_text, parsed["lowercase"], parsed["min_token_length"]
        )
        observations = self._continuations(sentences, n)

        seen = 0
        unseen = 0
        neg_log_sum = 0.0
        for context_key, word in observations:
            rows = table.get(context_key)
            if rows is None:
                # Fully unseen context: add-one Laplace against V + 1.
                probability = 1.0 / (vocabulary_size + 1)
                unseen += 1
            else:
                probability = None
                context_count = 0
                for row_word, count, row_probability in rows:
                    context_count += count
                    if row_word == word:
                        probability = float(row_probability)
                if probability is None:
                    # Seen context, unseen continuation: add-one Laplace.
                    probability = (
                        1.0 / (context_count + vocabulary_size + 1)
                    )
                    unseen += 1
                else:
                    seen += 1
            neg_log_sum += -math.log(probability)

        num = len(observations)
        average = neg_log_sum / num if num else 0.0
        return {
            "mode": "perplexity-lite",
            "n": n,
            "num_continuations": num,
            "num_seen": seen,
            "num_unseen": unseen,
            "vocabulary_size": vocabulary_size,
            "average_neg_log_prob": average,
            "note": {
                "type": "laplace_smoothed_nll",
                "message": (
                    "This is the average negative natural-log probability "
                    "of the observed continuations, with add-one Laplace "
                    "smoothing for unseen ones (seen context + unseen word: "
                    "1/(context_count + V + 1); unseen context: 1/(V + 1)). "
                    "It is a simple smoothed NLL, NOT true perplexity."
                ),
            },
        }


class _ModelShapeError(Exception):
    """Internal marker for content-level model-shape problems."""


class _ModelJsonError(_ModelShapeError):
    """Internal marker for a model JSON string that does not parse."""
