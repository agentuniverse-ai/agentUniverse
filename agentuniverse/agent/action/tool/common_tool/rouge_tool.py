#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: rouge_tool.py

"""ROUGE summary-overlap evaluation tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration): agents that produce summaries (for example with
``TextSummarizerTool``) need the standard way to *evaluate* them, and
the existing text tools do not provide it — ``TextDiffTool`` measures
edit distance between two texts and no tool computes the ROUGE family
(Lin 2004), the standard automatic summarization evaluation metrics.

Three modes:

* ``score`` — a candidate summary plus one reference (``reference``) or
  a reference list (``references``, capped at 10) to per-metric
  ``{precision, recall, f1}`` for each metric in ``metrics`` (default
  ``["rouge1", "rouge2", "rougeL"]``; any non-empty duplicate-free
  subset). With a reference list the reported scores are the
  per-component averages over the per-reference scores (the standard
  multi-reference averaging; each of precision / recall / f1 is
  averaged independently). ``lcs_detail`` is the diagnostic view of a
  single pair and ``summary`` the full multi-reference report.
* ``lcs_detail`` — one candidate plus one reference to the Longest
  Common Subsequence itself: the LCS token sequence, its length and
  the span positions — for every LCS token the token's index in the
  candidate token list and in the reference token list.
* ``summary`` — one candidate versus a reference set (``references``,
  at least one): per-reference scores, the average across references
  and the best (oracle) reference per metric — the standard
  multi-reference reporting. Best = highest f1, ties broken by lowest
  reference index, so the choice is fully deterministic.

Metrics (Lin 2004):

* ``rouge1`` / ``rouge2`` — n-gram overlap: the overlap of an n-gram
  type is ``min(candidate count, reference count)``; the summed
  overlap is divided by the candidate n-gram total (precision) and by
  the reference n-gram total (recall).
* ``rougeL`` — the Longest Common Subsequence of the two token
  sequences, computed with the standard dynamic program. This is
  **unit-weighted whole-sequence LCS per candidate/reference pair**
  (the sentence-level ROUGE-L of the original paper). It is NOT the
  summary-level "union LCS" variant (ROUGE-L with sentence splitting
  and union weighting) — a deliberate, documented choice so a single
  well-defined number is reported per pair.

F is the ROUGE F-beta ``((1 + beta^2) * P * R) / (R + beta^2 * P)``
with the ``beta`` option (default ``1`` → F1); ``beta > 1`` favors
recall, ``beta < 1`` favors precision. Any zero denominator yields
``0.0`` — in particular a text with no bigrams scores ``rouge2 = 0.0``
and an empty candidate or empty reference scores ``0.0`` on every
metric (documented convention; unlike a similarity ratio this does
NOT define empty-equals-empty as 1.0).

Tokenization follows the established family rule (identical to
``CollocationTool`` / ``TextHistogramTool``): a token is a maximal run
of alphanumeric characters (Unicode ``str.isalnum``) plus internal
apostrophes so English contractions stay together, with leading /
trailing apostrophes trimmed; every CJK ideograph (Han Ext A, URO and
compatibility blocks) is emitted as its own single-character token.
Matching is case-sensitive by default.

The ``stemming`` option (default off) lowercases every token and
applies the light Porter-1a-style stemmer of ``LightStemmerTool``
(#3866) — steps 1a / 1b / 1c / 2-lite, embedded here so the tool is
standalone on master — to pure-ASCII-alphabetic tokens only (the rule
set is defined over lowercase ASCII letters; CJK and other tokens are
matched case-insensitively as-is). This mirrors the ROUGE ``-m`` flag
semantics: ``cats`` / ``cat`` then count as an overlap. It is a light
rule set, deliberately not full Porter: divergences (no step-1b
cleanup, so ``running`` → ``runn`` rather than ``run``) are inherited
from and documented in ``LightStemmerTool``.

Input validation is strict and happens before any computation:
malformed parameters (unknown mode, wrong types, both or neither of
``reference`` / ``references``, an empty or oversized reference list,
a non-string reference or list member, an invalid ``metrics`` list,
non-positive or non-numeric ``beta``, non-boolean ``stemming``,
strings over 20,000 characters) raise a ``ValueError``, mirroring the
other common tools. Scores are reported at 4 decimal places.
"""

import math
import re
from typing import Any, ClassVar, Dict, List, Tuple

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Han ideographs (Ext A, URO, compatibility) — identical to
# CollocationTool / TextHistogramTool. Kana and Hangul are
# intentionally not included: this is a documented fallback, not full
# CJK support.
_CJK_RANGES: Tuple[Tuple[int, int], ...] = (
    (0x3400, 0x4DBF),
    (0x4E00, 0x9FFF),
    (0xF900, 0xFAFF),
)

# Pure ASCII letters — the input domain of the light stemmer.
_ASCII_ALPHA = re.compile(r"\A[A-Za-z]+\Z")


def _is_cjk(char: str) -> bool:
    """Return True for Han ideographs (Ext A, URO, compatibility)."""
    code = ord(char)
    return any(low <= code <= high for low, high in _CJK_RANGES)


class _LightStemmer:
    """The LightStemmerTool (#3866) rule set, embedded for standalone use.

    Steps 1a / 1b / 1c / 2-lite of the light Porter-inspired stemmer,
    operating on lowercase ASCII-letter words. The full rule set and
    its deliberate divergences from complete Porter are documented in
    ``light_stemmer_tool.py``; this copy is byte-for-byte the same
    logic so both tools agree on every word.
    """

    _VOWELS: ClassVar[frozenset] = frozenset("aeiou")

    _STEP2_RULES: ClassVar[tuple] = (
        ("ational", "ate"),
        ("tional", "tion"),
        ("izer", "ize"),
        ("ness", ""),
    )

    @classmethod
    def _cv_forms(cls, word: str) -> List[str]:
        """Classify each letter as ``C`` or ``V`` per Porter's definition."""
        forms: List[str] = []
        for index, char in enumerate(word):
            if char in cls._VOWELS:
                forms.append("V")
            elif char == "y" and index > 0 and forms[index - 1] == "C":
                forms.append("V")
            else:
                forms.append("C")
        return forms

    @classmethod
    def _measure(cls, stem: str) -> int:
        """Porter measure ``m`` — the number of ``VC`` transitions."""
        forms = cls._cv_forms(stem)
        return sum(
            1 for previous, current in zip(forms, forms[1:])
            if previous == "V" and current == "C"
        )

    @classmethod
    def _contains_vowel(cls, stem: str) -> bool:
        """Whether ``stem`` contains at least one vowel (Porter ``*v*``)."""
        return "V" in cls._cv_forms(stem)

    @classmethod
    def _ends_consonant(cls, stem: str) -> bool:
        """Whether the last letter of a non-empty ``stem`` is a consonant."""
        return bool(stem) and cls._cv_forms(stem)[-1] == "C"

    @classmethod
    def stem(cls, word: str) -> str:
        """Stem one lowercase ASCII-letter word with the light rule set."""
        # ---- Step 1a: plural suffixes (first match wins) ------------ #
        if word.endswith("sses"):
            word = word[:-2]  # sses -> ss
        elif word.endswith("ies"):
            word = word[:-3] + "i"  # ies -> i
        elif word.endswith("ss"):
            pass  # ss -> keep
        elif word.endswith("s") and len(word) > 1:
            word = word[:-1]  # trailing s -> '' (guard: "s" stays "s")

        # ---- Step 1b: participle / trailing-e suffixes -------------- #
        if word.endswith("e"):
            if cls._measure(word[:-1]) > 0:
                word = word[:-1]
        elif word.endswith("eed"):
            if cls._measure(word[:-3]) > 0:
                word = word[:-1]  # eed -> ee
        elif word.endswith("ed"):
            if cls._contains_vowel(word[:-2]):
                word = word[:-2]
        elif word.endswith("ing"):
            if cls._contains_vowel(word[:-3]):
                word = word[:-3]

        # ---- Step 1c: y -> i ---------------------------------------- #
        if word.endswith("y") and len(word) > 1:
            if cls._measure(word[:-1]) > 0 and cls._ends_consonant(word[:-1]):
                word = word[:-1] + "i"

        # ---- Step 2 lite: four common suffixes (first match wins) --- #
        for suffix, replacement in cls._STEP2_RULES:
            if word.endswith(suffix):
                if cls._measure(word[: -len(suffix)]) > 0:
                    word = word[: -len(suffix)] + replacement
                break

        return word


class RougeTool(Tool):
    """ROUGE summary-overlap evaluation tool (pure stdlib, no network).

    Input bounds (rejected before any computation): any single text
    (candidate or reference) is capped at :obj:`MAX_TEXT_CHARS`
    characters and the reference list at :obj:`MAX_REFERENCES` items.
    Empty strings are accepted with a documented convention — any zero
    denominator scores ``0.0``, so an empty candidate or reference is
    ``0.0`` on every metric.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "rouge_tool"
    description: str = (
        "ROUGE summary-overlap evaluation tool — pure Python stdlib, no "
        "network required. Implements the standard ROUGE family (Lin "
        "2004) for evaluating a candidate summary against reference "
        "summary(s): rouge1 / rouge2 (n-gram overlap counts, "
        "min-per-type clamping) and rougeL (Longest Common Subsequence, "
        "unit-weighted whole-sequence LCS per pair), each reported as "
        "{precision, recall, f1} at 4 decimal places with a beta option "
        "for the F formula (default 1 = F1). mode='score' scores a "
        "candidate against one reference or a reference list "
        "(multi-reference averaging); mode='lcs_detail' returns the LCS "
        "itself with its length and span positions; mode='summary' "
        "reports per-reference scores plus the average and the best "
        "(oracle) reference per metric. Tokenization follows the "
        "established family rule (alphanumeric runs with internal "
        "apostrophes, CJK ideographs as single-character tokens); "
        "case-sensitive by default, optional stemming=True lowercases "
        "and applies the light Porter-style stemmer of LightStemmerTool."
    )

    MODES: ClassVar[tuple] = ("score", "lcs_detail", "summary")
    METRICS: ClassVar[tuple] = ("rouge1", "rouge2", "rougeL")

    DEFAULT_BETA: ClassVar[float] = 1.0
    # Scores are reported at this precision.
    SCORE_DECIMALS: ClassVar[int] = 4
    # Input bounds (see the class docstring).
    MAX_TEXT_CHARS: ClassVar[int] = 20_000
    MAX_REFERENCES: ClassVar[int] = 10

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any = None,
        candidate: Any = None,
        reference: Any = None,
        references: Any = None,
        metrics: Any = None,
        beta: Any = None,
        stemming: Any = None,
    ) -> Dict[str, Any]:
        """Run one ROUGE evaluation.

        Args:
            mode (str): One of ``score`` / ``lcs_detail`` / ``summary``.
            candidate (str): The candidate summary to evaluate (may be
                empty — any zero denominator scores 0.0).
            reference (str): ``score`` mode — a single reference
                summary; ``lcs_detail`` mode — the one required
                reference. Provide this or ``references``, never both.
            references (list[str]): ``score`` / ``summary`` modes — the
                reference set (1 to 10 strings); ``summary`` requires
                it and ``lcs_detail`` rejects it.
            metrics (list[str]): Non-empty duplicate-free subset of
                ``["rouge1", "rouge2", "rougeL"]`` (default: all
                three).
            beta (float): The F-beta weight, ``beta > 0`` — F = ((1 +
                beta^2) * P * R) / (R + beta^2 * P); default ``1``
                (F1). ``beta > 1`` favors recall, ``< 1`` precision.
            stemming (bool): Lowercase every token and apply the light
                Porter-style stemmer (LightStemmerTool rules) to
                ASCII-alphabetic tokens; default ``False``
                (case-sensitive raw tokens).

        Returns:
            Dict[str, Any]: The mode result — ``scores`` (``score``),
            the LCS detail (``lcs_detail``) or the per-reference /
            average / best report (``summary``) as described in the
            module docstring.

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        clean_stemming = self._validate_stemming(stemming)
        clean_beta = self._validate_beta(beta)
        clean_metrics = self._validate_metrics(metrics)
        clean_candidate = self._validate_text(candidate, "candidate")

        if mode == "lcs_detail":
            if references is not None:
                self._invalid(
                    "lcs_detail mode takes a single reference, not a "
                    "references list"
                )
            if reference is None:
                self._invalid("lcs_detail mode requires a reference string")
            clean_reference = self._validate_text(reference, "reference")
            return self._run_lcs_detail(
                clean_candidate, clean_reference, clean_stemming
            )

        if mode == "summary":
            if reference is not None:
                self._invalid(
                    "summary mode takes a references list, not a single "
                    "reference (use score mode for one reference)"
                )
            clean_references = self._validate_references(references)
            return self._run_summary(
                clean_candidate,
                clean_references,
                clean_metrics,
                clean_beta,
                clean_stemming,
            )

        # score mode: exactly one of reference / references.
        if reference is not None and references is not None:
            self._invalid("provide either reference or references, not both")
        if reference is not None:
            if not isinstance(reference, str) or isinstance(reference, bool):
                self._invalid(f"reference must be a string (got {reference!r})")
            clean_references = [self._validate_text(reference, "reference")]
        elif references is not None:
            clean_references = self._validate_references(references)
        else:
            self._invalid("score mode requires a reference or references")
        return self._run_score(
            clean_candidate,
            clean_references,
            clean_metrics,
            clean_beta,
            clean_stemming,
        )

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"rouge_tool: {message}")

    @classmethod
    def _validate_text(cls, value: Any, label: str) -> str:
        """Validate a text input (empty allowed — convention defined)."""
        if value is None or isinstance(value, bool) or not isinstance(value, str):
            cls._invalid(f"{label} must be a string (got {value!r})")
        if len(value) > cls.MAX_TEXT_CHARS:
            cls._invalid(
                f"{label} exceeds the {cls.MAX_TEXT_CHARS:,}-character "
                f"limit (got {len(value):,} characters)"
            )
        return value

    @classmethod
    def _validate_references(cls, value: Any) -> List[str]:
        """Validate the reference set (non-empty, capped list of texts)."""
        if isinstance(value, bool) or not isinstance(value, list) or not value:
            cls._invalid(
                "references must be a non-empty list of strings with at "
                f"most {cls.MAX_REFERENCES} items (got {value!r}) — at "
                "least one reference is required"
            )
        if len(value) > cls.MAX_REFERENCES:
            cls._invalid(
                f"references exceeds the {cls.MAX_REFERENCES}-item limit "
                f"(got {len(value)} items)"
            )
        for index, item in enumerate(value):
            if item is None or isinstance(item, bool) or not isinstance(item, str):
                cls._invalid(
                    f"references[{index}] must be a string (got {item!r})"
                )
            if len(item) > cls.MAX_TEXT_CHARS:
                cls._invalid(
                    f"references[{index}] exceeds the "
                    f"{cls.MAX_TEXT_CHARS:,}-character limit "
                    f"(got {len(item):,} characters)"
                )
        return value

    @classmethod
    def _validate_metrics(cls, value: Any) -> Tuple[str, ...]:
        """Validate the ``metrics`` selection (default: all three)."""
        if value is None:
            return cls.METRICS
        if isinstance(value, bool) or not isinstance(value, list) or not value:
            cls._invalid(
                "metrics must be a non-empty list drawn from: "
                f"{', '.join(cls.METRICS)} (got {value!r})"
            )
        seen = []
        for item in value:
            if item not in cls.METRICS:
                cls._invalid(
                    "metrics must be a non-empty list drawn from: "
                    f"{', '.join(cls.METRICS)} (got {value!r})"
                )
            if item in seen:
                cls._invalid(
                    f"metrics must not contain duplicates (got {value!r})"
                )
            seen.append(item)
        return tuple(seen)

    @classmethod
    def _validate_beta(cls, value: Any) -> float:
        """Validate the F-beta ``beta`` weight (positive, finite)."""
        if value is None:
            return cls.DEFAULT_BETA
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            cls._invalid(f"beta must be a positive number (got {value!r})")
        number = float(value)
        if not math.isfinite(number) or number <= 0.0:
            cls._invalid(f"beta must be a positive number (got {number!r})")
        return number

    @classmethod
    def _validate_stemming(cls, value: Any) -> bool:
        """Validate the ``stemming`` flag."""
        if value is None:
            return False
        if not isinstance(value, bool):
            cls._invalid(f"stemming must be a boolean (got {value!r})")
        return value

    # ------------------------------------------------------------------ #
    # Tokenization (established family rule) and stemming
    # ------------------------------------------------------------------ #

    @classmethod
    def _tokenize(cls, text: str, stemming: bool) -> List[str]:
        """Split text into tokens; optionally lowercase and stem them.

        A token is a maximal run of alphanumeric characters (Unicode
        ``str.isalnum``) plus internal apostrophes (leading / trailing
        apostrophes trimmed); every CJK ideograph is emitted as its own
        single-character token. With ``stemming`` every token is
        lowercased and pure-ASCII-alphabetic tokens additionally go
        through the light stemmer (the ROUGE ``-m`` flag semantics).
        """
        tokens: List[str] = []
        run: List[str] = []

        def flush() -> None:
            if run:
                word = "".join(run).strip("'")
                if word:
                    tokens.append(word)
                run.clear()

        for char in text:
            if _is_cjk(char):
                flush()
                tokens.append(char)
            elif char.isalnum() or char == "'":
                run.append(char)
            else:
                flush()
        flush()

        if stemming:
            return [
                _LightStemmer.stem(token.lower())
                if _ASCII_ALPHA.match(token)
                else token.lower()
                for token in tokens
            ]
        return tokens

    # ------------------------------------------------------------------ #
    # Core ROUGE functions (pure, deterministic)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _ngram_list(tokens: List[str], n: int) -> List[Tuple[str, ...]]:
        """The n-grams of a token list as a plain list of tuples."""
        return [tuple(tokens[index:index + n]) for index in range(len(tokens) - n + 1)]

    @classmethod
    def _ngram_overlap(
        cls, cand_tokens: List[str], ref_tokens: List[str], n: int
    ) -> Tuple[int, int, int]:
        """Return ``(overlap, candidate_total, reference_total)`` n-grams.

        The overlap of an n-gram type is ``min(candidate count,
        reference count)`` — the standard ROUGE-N clamping that keeps
        repeated words honest (a candidate repeating one reference word
        ten times overlaps it exactly once).
        """
        cand_counts: Dict[Tuple[str, ...], int] = {}
        for gram in cls._ngram_list(cand_tokens, n):
            cand_counts[gram] = cand_counts.get(gram, 0) + 1
        ref_counts: Dict[Tuple[str, ...], int] = {}
        for gram in cls._ngram_list(ref_tokens, n):
            ref_counts[gram] = ref_counts.get(gram, 0) + 1
        overlap = sum(
            min(count, ref_counts.get(gram, 0))
            for gram, count in cand_counts.items()
        )
        cand_total = max(len(cand_tokens) - n + 1, 0)
        ref_total = max(len(ref_tokens) - n + 1, 0)
        return overlap, cand_total, ref_total

    @classmethod
    def _lcs_table(
        cls, cand_tokens: List[str], ref_tokens: List[str]
    ) -> List[List[int]]:
        """The standard LCS dynamic-programming table.

        ``table[i][j]`` is the LCS length of the first ``i`` candidate
        tokens and the first ``j`` reference tokens.
        """
        rows, cols = len(cand_tokens), len(ref_tokens)
        table = [[0] * (cols + 1) for _ in range(rows + 1)]
        for i in range(1, rows + 1):
            for j in range(1, cols + 1):
                if cand_tokens[i - 1] == ref_tokens[j - 1]:
                    table[i][j] = table[i - 1][j - 1] + 1
                else:
                    table[i][j] = max(table[i - 1][j], table[i][j - 1])
        return table

    @classmethod
    def _lcs_backtrack(
        cls, cand_tokens: List[str], ref_tokens: List[str]
    ) -> List[Tuple[int, int]]:
        """The LCS match positions ``(candidate_index, reference_index)``.

        The backtrack walks the DP table from ``(m, n)``: equal tokens
        are taken as matches; otherwise the larger subproblem value is
        followed, and on a tie the candidate side (``i - 1``) is
        preferred — a fixed rule that makes the returned subsequence
        deterministic even when several distinct LCS of equal length
        exist.
        """
        table = cls._lcs_table(cand_tokens, ref_tokens)
        pairs: List[Tuple[int, int]] = []
        i, j = len(cand_tokens), len(ref_tokens)
        while i > 0 and j > 0:
            if cand_tokens[i - 1] == ref_tokens[j - 1]:
                pairs.append((i - 1, j - 1))
                i -= 1
                j -= 1
            elif table[i - 1][j] >= table[i][j - 1]:
                i -= 1
            else:
                j -= 1
        pairs.reverse()
        return pairs

    @classmethod
    def _pair_scores(
        cls,
        cand_tokens: List[str],
        ref_tokens: List[str],
        metric: str,
        beta: float,
    ) -> Dict[str, float]:
        """The raw (unrounded) P / R / F of one pair for one metric."""
        if metric == "rougeL":
            overlap = len(cls._lcs_backtrack(cand_tokens, ref_tokens))
            cand_total, ref_total = len(cand_tokens), len(ref_tokens)
        else:
            overlap, cand_total, ref_total = cls._ngram_overlap(
                cand_tokens, ref_tokens, 1 if metric == "rouge1" else 2
            )
        precision = overlap / cand_total if cand_total else 0.0
        recall = overlap / ref_total if ref_total else 0.0
        beta_sq = beta * beta
        denominator = recall + beta_sq * precision
        f_score = (
            (1.0 + beta_sq) * precision * recall / denominator
            if denominator
            else 0.0
        )
        return {"precision": precision, "recall": recall, "f1": f_score}

    # ------------------------------------------------------------------ #
    # score mode (single reference or multi-reference averaging)
    # ------------------------------------------------------------------ #

    def _run_score(
        self,
        candidate: str,
        references: List[str],
        metrics: Tuple[str, ...],
        beta: float,
        stemming: bool,
    ) -> Dict[str, Any]:
        """Score a candidate against one reference or a reference list.

        With several references the reported scores are the per-
        component arithmetic means over the per-reference scores (each
        of precision / recall / f1 averaged independently, computed
        unrounded and rounded once at the end).
        """
        cand_tokens = self._tokenize(candidate, stemming)
        per_reference: List[Dict[str, Dict[str, Dict[str, float]]]] = []
        for reference in references:
            ref_tokens = self._tokenize(reference, stemming)
            scores = {
                metric: self._pair_scores(
                    cand_tokens, ref_tokens, metric, beta
                )
                for metric in metrics
            }
            per_reference.append(scores)

        if len(per_reference) == 1:
            scores = {
                metric: self._rounded(per_reference[0][metric])
                for metric in metrics
            }
        else:
            count = len(per_reference)
            scores = {
                metric: self._rounded({
                    component: sum(
                        entry[metric][component] for entry in per_reference
                    ) / count
                    for component in ("precision", "recall", "f1")
                })
                for metric in metrics
            }
        return {
            "mode": "score",
            "candidate": candidate,
            "references": list(references),
            "reference_count": len(references),
            "metrics": list(metrics),
            "beta": beta,
            "stemming": stemming,
            "scores": scores,
        }

    @classmethod
    def _rounded(
        cls, values: Dict[str, float]
    ) -> Dict[str, float]:
        """Round every component of a P / R / F mapping at 4 dp."""
        return {
            component: round(value, cls.SCORE_DECIMALS)
            for component, value in values.items()
        }

    # ------------------------------------------------------------------ #
    # lcs_detail mode
    # ------------------------------------------------------------------ #

    def _run_lcs_detail(
        self, candidate: str, reference: str, stemming: bool
    ) -> Dict[str, Any]:
        """Return the LCS of one candidate / reference pair in full."""
        cand_tokens = self._tokenize(candidate, stemming)
        ref_tokens = self._tokenize(reference, stemming)
        pairs = self._lcs_backtrack(cand_tokens, ref_tokens)
        spans = [
            {
                "token": cand_tokens[cand_index],
                "candidate_index": cand_index,
                "reference_index": ref_index,
            }
            for cand_index, ref_index in pairs
        ]
        return {
            "mode": "lcs_detail",
            "candidate": candidate,
            "reference": reference,
            "stemming": stemming,
            "candidate_tokens": cand_tokens,
            "reference_tokens": ref_tokens,
            "candidate_token_count": len(cand_tokens),
            "reference_token_count": len(ref_tokens),
            "lcs_length": len(pairs),
            "lcs_tokens": [span["token"] for span in spans],
            "spans": spans,
        }

    # ------------------------------------------------------------------ #
    # summary mode (per-reference + average + best / oracle)
    # ------------------------------------------------------------------ #

    def _run_summary(
        self,
        candidate: str,
        references: List[str],
        metrics: Tuple[str, ...],
        beta: float,
        stemming: bool,
    ) -> Dict[str, Any]:
        """Full multi-reference report: per-reference, average, best.

        Best (oracle) = the reference with the highest f1 per metric,
        ties broken by the lowest reference index, reported with its
        index and full P / R / F.
        """
        cand_tokens = self._tokenize(candidate, stemming)
        per_reference: List[Dict[str, Any]] = []
        raw: List[Dict[str, Dict[str, float]]] = []
        for index, reference in enumerate(references):
            ref_tokens = self._tokenize(reference, stemming)
            pair = {
                metric: self._pair_scores(
                    cand_tokens, ref_tokens, metric, beta
                )
                for metric in metrics
            }
            raw.append(pair)
            per_reference.append(
                {
                    "reference": reference,
                    "index": index,
                    "scores": {
                        metric: self._rounded(pair[metric])
                        for metric in metrics
                    },
                }
            )

        count = len(references)
        average = {
            metric: self._rounded({
                component: sum(entry[metric][component] for entry in raw) / count
                for component in ("precision", "recall", "f1")
            })
            for metric in metrics
        }

        best: Dict[str, Dict[str, Any]] = {}
        for metric in metrics:
            chosen = 0
            for index in range(1, count):
                if raw[index][metric]["f1"] > raw[chosen][metric]["f1"]:
                    chosen = index
            best[metric] = {
                "reference_index": chosen,
                **self._rounded(raw[chosen][metric]),
            }

        return {
            "mode": "summary",
            "candidate": candidate,
            "references": list(references),
            "reference_count": count,
            "metrics": list(metrics),
            "beta": beta,
            "stemming": stemming,
            "per_reference": per_reference,
            "average": average,
            "best": best,
        }
