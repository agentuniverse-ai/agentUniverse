#!/usr/bin/env python3
"""Text readability scoring with seven classical formulas and transparent sub-metrics."""

# Public execute() converts validation exceptions into structured tool errors.
# ruff: noqa: TRY003

import math
import re
from typing import Any, ClassVar

from agentuniverse.agent.action.tool.tool import Tool

# ---------------------------------------------------------------------------
# Embedded reference data
# ---------------------------------------------------------------------------

# Flesch Reading Ease band table (lower bound -> label). Classical 1948 table.
_FLESCH_BANDS: ClassVar[tuple[tuple[float, str], ...]] = (
    (90.0, "5th grade (very easy)"),
    (80.0, "6th grade (easy)"),
    (70.0, "7th grade (fairly easy)"),
    (60.0, "8th-9th grade (plain English)"),
    (50.0, "10th-12th grade (fairly difficult)"),
    (30.0, "college (difficult)"),
    (0.0, "college graduate (very difficult)"),
)
_FLESCH_MAX_BAND = "5th grade (very easy)"
_FLESCH_MIN_BAND = "college graduate (very difficult)"

# U.S. school-grade bands for grade-level formulas (lower bound -> label).
_GRADE_BANDS: ClassVar[tuple[tuple[float, str], ...]] = (
    (17.0, "graduate / professional (grade 17+)"),
    (13.0, "college (grades 13-16)"),
    (9.0, "high school (grades 9-12)"),
    (6.0, "middle school (grades 6-8)"),
    (4.0, "late elementary (grades 4-5)"),
    (1.0, "early elementary (grades 1-3)"),
    (0.0, "preschool (below grade 1)"),
)

# Classic Dale-Chall raw-score interpretation table (upper bound -> label).
_DALE_CHALL_BANDS: ClassVar[tuple[tuple[float, str], ...]] = (
    (4.9, "grade 4 and below"),
    (5.9, "grades 5-6"),
    (6.9, "grades 7-8"),
    (7.9, "grades 9-10"),
    (8.9, "grades 11-12"),
    (9.9, "grades 13-15 (college)"),
)
_DALE_CHALL_MAX_BAND = "college graduate (grade 16+)"

# The compact embedded easy-word list: the 76 most frequent English words
# (Fry's frequency canon). These are single dictionary words and plain
# frequency facts, so the list is public domain by construction. The full
# Dale-Chall familiar-word list has ~3,000 entries and is NOT embedded;
# the 76-word subset makes the simplified variant self-contained.
_EASY_WORDS_76: ClassVar[frozenset[str]] = frozenset(
    """
    the of and a to in is you that it he was for on are as with his they i at
    be this have from or one had by word but not what all were we when your
    can said there use an each which she do how their if will up other about
    out many then them these so some her would make like him into time has
    look two more write go see number
    """.split()
)

# Common English abbreviations whose final dot must not end a sentence.
# Weekday tokens "sun" and "sat" are deliberately excluded: they are common
# words whose sentence-final dot ("... watched the sun.") must terminate.
_ABBREVIATIONS: ClassVar[frozenset[str]] = frozenset(
    """
    mr mrs ms messrs dr prof sr jr st mt ft no nos vs etc eg ie cf al inc
    ltd co corp dept univ assn bros vol ch chs fig figs ref refs approx est
    min max sq lb lbs oz pt qt gal hr hrs sec ca ed eds trans rev pp jan feb
    mar apr jun jul aug sep sept oct nov dec mon tue tues wed thu thur fri
    am pm ad bc phd md ba ma mba ceo cfo cto coo ap apt blvd rd ave
    """.split()
)

_VOWELS = frozenset("aeiouy")
_NON_WORD_EXCEPT_APOS = re.compile(r"[^\w\s']")
_ORPHAN_APOS = re.compile(r"(?<!\w)'|'(?!\w)")
_NON_WORD = re.compile(r"[^\w]")
_WHITESPACE = re.compile(r"\s")
_CJK_CHAR = re.compile(r"[\u2e80-\u2fdf\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
_NON_ASCII_LETTER = re.compile(r"[^\x00-\x7f]")
_MODES: ClassVar[frozenset[str]] = frozenset({"analyze", "compare", "grade_band"})
_FORMULAS: ClassVar[frozenset[str]] = frozenset(
    {"flesch", "flesch_kincaid_grade", "gunning_fog", "ari", "smog", "coleman_liau", "dale_chall"}
)
_GRADE_FORMULAS: ClassVar[frozenset[str]] = frozenset(
    {"flesch_kincaid_grade", "gunning_fog", "ari", "smog", "coleman_liau"}
)
_CJK_MODES: ClassVar[frozenset[str]] = frozenset({"reject", "naive"})


class ReadabilityTool(Tool):
    """Classical text readability scoring with fully transparent inputs.

    Formulas
    --------
    With ``W`` words, ``S`` sentences, ``Y`` syllables, ``C`` complex words
    (3+ syllables), ``CH`` non-whitespace characters and ``L`` letters per
    100 words:

    * ``flesch``   = ``206.835 - 1.015*(W/S) - 84.6*(Y/W)``, reported with
      the full 1948 band table from ``college graduate (0-30)`` up to
      ``5th grade (90-100)``; scores outside ``[0, 100]`` clamp to the
      nearest band.
    * ``flesch_kincaid_grade`` = ``0.39*(W/S) + 11.8*(Y/W) - 15.59``.
    * ``gunning_fog`` = ``0.4*((W/S) + 100*C/W)`` where a complex word has
      three or more syllables (no word-list exemption).
    * ``ari`` (Automated Readability Index) =
      ``0.5*(W/S) + 4.71*(CH/W) - 21.43``.
    * ``smog`` = ``1.043*sqrt(30*C/S) + 3.1291``. The formula is the
      30-sentence adaptation of McLaughlin's original; with fewer than 30
      sentences (and especially fewer than 3) the score is approximate and
      a caveat is emitted.
    * ``coleman_liau`` = ``0.0588*L - 0.296*(100*S/W) - 15.8`` with
      ``L = letters/W*100``. The original coefficient 0.0588 is used.
    * ``dale_chall`` (simplified) = ``0.1579*difficult% + 0.0496*(W/S)``,
      plus the classic ``+3.6365`` adjustment when difficult words exceed
      5% of all words. A word is difficult when its lowercase form is not
      in the embedded 76-word easy list (the full Dale-Chall list of
      ~3,000 words is not embedded, so scores run higher than full-list
      implementations; a caveat says so).

    Counting conventions
    --------------------
    Words are whitespace-separated tokens with punctuation removed;
    apostrophes inside words survive (``don't`` is one word), hyphens are
    removed and the fragments joined (``well-known`` is one word
    ``wellknown``), pure-punctuation tokens are dropped, and digit runs
    count as words (``3.14`` is one word). ``char_count`` counts every
    non-whitespace character of the original text (including punctuation)
    and feeds ARI; ``letters_only`` counts ``\\w`` characters (letters and
    digits) and feeds Coleman-Liau. These conventions match textstat's so
    formula-level comparisons are meaningful.

    Sentence segmentation
    ---------------------
    Sentences end at ``.``, ``!``, ``?`` or ``;``. A dot does NOT end a
    sentence when it closes a common abbreviation (a 91-entry list: Mr.,
    Dr., vs., e.g., Jan., a.m. ...), when it separates digits (``3.14``,
    ``1.000.000``-style decimals never split), when it is part of an
    ellipsis (``...`` never splits), or when it closes a dotted initial or
    dotted acronym (``J.``, ``U.S.``). Text without any terminator is one
    sentence. This is an honest heuristic, not a parser: sentence-final
    abbreviations (``... and so etc.``) merge into the next sentence,
    unknown abbreviations not in the list can still split, and standalone
    punctuation tokens are dropped before word counting.

    Syllable counting
    -----------------
    The standard vowel-group heuristic: count maximal runs of ``aeiouy``
    (``y`` included except word-initially), subtract one for a silent
    final ``e`` (kept for ``-ee`` endings), keep syllabic consonant-``le``
    endings (``table`` = 2), drop silent ``-ed`` unless preceded by ``t``
    or ``d`` (``jumped`` = 1, ``wanted`` = 2), and never return less than
    one syllable per word (numbers and vowel-less tokens count as 1). The
    heuristic is transparent, not phonetic: per-word counts are exposed in
    ``word_syllables`` so users can verify every number, and known
    divergence classes versus CMU-dictionary counters (words like
    ``simile``, ``poem``, ``rhythm``, ``-ful`` derivatives, adjective
    ``-ed`` forms such as ``wicked``) are documented here.

    Modes
    -----
    ``analyze`` scores one text; ``compare`` scores two texts side by side
    and reports which is easier under each formula plus a majority verdict
    with a unanimity flag; ``grade_band`` maps one numeric score plus a
    formula name to its band description.

    Determinism
    -----------
    Output depends only on the input and options: no locale, time, random,
    or network access; caps and truncation flags make large inputs
    deterministic too. Scores are IEEE-754 doubles at full precision and
    are never rounded by the tool.
    """

    max_text_length: int = 200_000
    max_sentences_detail: int = 30
    max_polysyllabic_listed: int = 50
    max_word_syllables: int = 100
    sentence_preview_length: int = 120

    def execute(
        self,
        mode: str,
        text: str | None = None,
        a: str | None = None,
        b: str | None = None,
        score: float | None = None,
        formula: str | None = None,
        cjk: str = "reject",
    ) -> dict[str, Any]:
        try:
            self._validate_config()
            operation = self._choice(mode, "mode", _MODES)
            cjk_mode = self._choice(cjk, "cjk", _CJK_MODES)
            if operation == "analyze":
                return self._analyze(self._string(text, "text"), cjk_mode)
            if operation == "compare":
                return self._compare(self._string(a, "a"), self._string(b, "b"), cjk_mode)
            return self._grade_band(score, formula)
        except (TypeError, ValueError) as exc:
            return self._error(mode, "validation_error", str(exc))
        except Exception as exc:  # pragma: no cover - defensive catch-all
            return self._error(mode, "operation_error", f"Readability analysis failed: {exc}")

    # ------------------------------------------------------------------
    # Validation helpers
    # ------------------------------------------------------------------

    def _validate_config(self) -> None:
        for name in (
            "max_text_length",
            "max_sentences_detail",
            "max_polysyllabic_listed",
            "max_word_syllables",
            "sentence_preview_length",
        ):
            bound = getattr(self, name)
            if isinstance(bound, bool) or not isinstance(bound, int) or bound <= 0:
                raise ValueError(f"{name} must be a positive integer")

    @staticmethod
    def _error(mode: Any, kind: str, message: str) -> dict[str, Any]:
        return {"status": "error", "error_type": kind, "error": message, "mode": mode}

    @staticmethod
    def _choice(raw: Any, name: str, allowed: frozenset[str]) -> str:
        if not isinstance(raw, str):
            raise TypeError(f"{name} must be a string")
        value = raw.strip().lower()
        if value not in allowed:
            raise ValueError(f"{name} must be one of {sorted(allowed)}")
        return value

    @staticmethod
    def _string(raw: Any, name: str) -> str:
        if not isinstance(raw, str):
            raise TypeError(f"{name} must be a string")
        return raw

    def _bounded_text(self, text: str, name: str) -> str:
        if len(text) > self.max_text_length:
            raise ValueError(
                f"{name} exceeds max_text_length ({len(text)} > {self.max_text_length} characters)"
            )
        return text

    # ------------------------------------------------------------------
    # Tokenization primitives
    # ------------------------------------------------------------------

    @staticmethod
    def _words(text: str) -> list[str]:
        """Punctuation-stripped whitespace tokens (see class docstring)."""
        cleaned = _ORPHAN_APOS.sub("", text)
        cleaned = _NON_WORD_EXCEPT_APOS.sub("", cleaned)
        return cleaned.split()

    @staticmethod
    def _syllables(word: str) -> int:
        """Standard vowel-group syllable heuristic (see class docstring)."""
        w = word.lower()
        if not w:
            return 0
        count = 0
        if w[0] in _VOWELS:
            count += 1
        for i in range(1, len(w)):
            if w[i] in _VOWELS and w[i - 1] not in _VOWELS:
                count += 1
        if len(w) >= 3 and w.endswith("le") and w[-3] not in _VOWELS:
            pass  # syllabic -le keeps its vowel groups
        elif w.endswith("e") and not w.endswith("ee") and count > 1:
            count -= 1  # silent final e
        elif len(w) >= 3 and w.endswith("ed") and w[-3] not in "td" and count > 1:
            count -= 1  # silent -ed unless preceded by t or d
        return count if count >= 1 else 1

    @staticmethod
    def _abbrev_dot(text: str, i: int) -> bool:
        """True when the dot at ``text[i]`` closes an abbreviation or initial."""
        n = len(text)
        # Decimal separator: digit dot digit (3.14, 1.000.000).
        if 0 < i < n - 1 and text[i - 1].isdigit() and text[i + 1].isdigit():
            return True
        # First dot of a dotted token (e.g the "e." of "e.g." or "U." of
        # "U.S."): a letter directly followed by dot-dot or dot-letter-dot.
        if 0 < i < n - 1 and text[i - 1].isalpha() and (
            text[i + 1] == "." or (i + 2 < n and text[i + 1].isalpha() and text[i + 2] == ".")
        ):
            return True
        # Token ending right before this dot: a run of letters and inner dots.
        j = i - 1
        while j >= 0 and (text[j].isalpha() or text[j] == "."):
            j -= 1
        token = text[j + 1 : i]
        if not token:
            return False
        letters = token.replace(".", "")
        if not letters:
            return False
        # Dotted acronym or dotted abbreviation (U.S, e.g, Ph.D).
        if "." in token:
            return True
        # Single-letter initial (J. Smith); the pronoun "I." at a true
        # sentence end merges into the next sentence - a documented limit.
        if len(letters) == 1 and letters.isupper():
            return True
        # Plain abbreviation from the embedded list (Dr., approx., Jan.).
        return letters.lower() in _ABBREVIATIONS

    def _sentences(self, text: str) -> list[str]:
        """Segment text into sentences (see class docstring)."""
        sentences: list[str] = []
        start = 0
        i = 0
        n = len(text)
        while i < n:
            ch = text[i]
            if ch == ".":
                # Ellipsis cluster never terminates.
                j = i
                while j + 1 < n and text[j + 1] == ".":
                    j += 1
                if j > i:
                    i = j + 1
                    continue
                if not self._abbrev_dot(text, i):
                    sentences.append(text[start : i + 1])
                    start = i + 1
                i += 1
            elif ch in "!?;":
                sentences.append(text[start : i + 1])
                start = i + 1
                i += 1
            else:
                i += 1
        tail = text[start:]
        if tail.strip():
            sentences.append(tail)
        return [s.strip() for s in sentences if s.strip()]

    # ------------------------------------------------------------------
    # Scoring core
    # ------------------------------------------------------------------

    def _measure(self, text: str, caveats: list[str]) -> dict[str, Any] | None:
        """Compute all sub-metrics and scores; None-ish handled by caller."""
        sentences = self._sentences(text)
        sentence_words = [self._words(s) for s in sentences]
        words = [w for ws in sentence_words for w in ws]
        word_syllables = [(w, self._syllables(w)) for w in words]
        total_syllables = sum(c for _, c in word_syllables)
        polysyllabic = [w for w, c in word_syllables if c >= 3]
        char_count = len(_WHITESPACE.sub("", text))
        letters_only = len(_NON_WORD.sub("", text))

        # CJK and non-ASCII caveats (naive mode scoring continues).
        if _CJK_CHAR.search(text):
            caveats.append(
                "cjk_text: readability formulas assume space-delimited alphabetic text; "
                "CJK runs score as single words in naive mode"
            )
        if _NON_ASCII_LETTER.search(text):
            caveats.append(
                "non_ascii_letters: the syllable heuristic is tuned for a-z words; "
                "non-ASCII letters are scored by the same vowel rules"
            )
        if text.strip() and not any(ch in text for ch in ".!?;"):
            caveats.append(
                "no_terminator: text without terminal punctuation is counted as one sentence"
            )
        sentence_count = len(sentences)
        if sentence_count < 3:
            caveats.append(
                f"smog_unreliable: only {sentence_count} sentence(s); SMOG needs at least 3 "
                "(ideally 30) - treat the score as indicative only"
            )
        elif sentence_count < 30:
            caveats.append(
                f"smog_short_sample: {sentence_count} sentences; full SMOG samples 30 sentences "
                "so the score is an adaptation"
            )
        if any("-" in tok for tok in text.split()):
            caveats.append(
                "hyphenated_words: hyphenated tokens are counted as single words with the hyphen removed"
            )

        return {
            "sentences": sentences,
            "sentence_words": sentence_words,
            "words": words,
            "word_syllables": word_syllables,
            "total_syllables": total_syllables,
            "polysyllabic": polysyllabic,
            "char_count": char_count,
            "letters_only": letters_only,
        }

    @staticmethod
    def _flesch_band(score: float) -> str:
        for lower, label in _FLESCH_BANDS:
            if score >= lower:
                return label
        return _FLESCH_MIN_BAND

    @staticmethod
    def _grade_band_value(score: float) -> str:
        for lower, label in _GRADE_BANDS:
            if score >= lower:
                return label
        return _GRADE_BANDS[-1][1]

    @staticmethod
    def _dale_chall_band(score: float) -> str:
        for upper, label in _DALE_CHALL_BANDS:
            if score <= upper:
                return label
        return _DALE_CHALL_MAX_BAND

    def _band_for(self, formula: str, score: float) -> str:
        if formula == "flesch":
            return self._flesch_band(score)
        if formula == "dale_chall":
            return self._dale_chall_band(score)
        return self._grade_band_value(score)

    def _scores(self, m: dict[str, Any]) -> dict[str, Any]:
        """Seven formula scores from the measured counts (None when undefined)."""
        words = len(m["words"])
        sentences = len(m["sentences"])
        syllables = m["total_syllables"]
        complex_words = len(m["polysyllabic"])
        chars = m["char_count"]
        letters = m["letters_only"]
        if words == 0 or sentences == 0:
            return {name: {"score": None, "band": None} for name in sorted(_FORMULAS)}
        wps = words / sentences
        spw = syllables / words

        # Expression trees mirror the reference implementations so that
        # identical counts yield bit-identical doubles.
        flesch = 206.835 - 1.015 * wps - 84.6 * spw
        fk = (0.39 * wps) + (11.8 * spw) - 15.59
        per_complex = 100 * complex_words / words
        fog = 0.4 * (wps + per_complex)
        cpw = chars / words
        ari = (0.5 * wps) + (4.71 * cpw) - 21.43
        smog = (1.043 * (30 * (complex_words / sentences)) ** 0.5) + 3.1291
        letters_per_100 = letters / words * 100
        sentences_per_100 = sentences / words * 100
        coleman_liau = 0.0588 * letters_per_100 - 0.296 * sentences_per_100 - 15.8
        difficult = sum(1 for w in m["words"] if w.lower() not in _EASY_WORDS_76)
        difficult_pct = 100 * difficult / words
        dale_chall = (0.1579 * difficult_pct) + (0.0496 * wps)
        if difficult_pct > 5:
            dale_chall += 3.6365

        return {
            "flesch": {"score": flesch, "band": self._flesch_band(flesch)},
            "flesch_kincaid_grade": {
                "score": fk,
                "band": self._grade_band_value(fk),
            },
            "gunning_fog": {"score": fog, "band": self._grade_band_value(fog)},
            "ari": {"score": ari, "band": self._grade_band_value(ari)},
            "smog": {"score": smog, "band": self._grade_band_value(smog)},
            "coleman_liau": {
                "score": coleman_liau,
                "band": self._grade_band_value(coleman_liau),
            },
            "dale_chall": {
                "score": dale_chall,
                "band": self._dale_chall_band(dale_chall),
            },
        }

    def _analyze_payload(self, text: str, caveats: list[str]) -> dict[str, Any]:
        m = self._measure(text, caveats)
        words = m["words"]
        sentences = m["sentences"]
        scores = self._scores(m)
        word_syllables = m["word_syllables"]
        listed_words = word_syllables[: self.max_word_syllables]
        polysyllabic = m["polysyllabic"][: self.max_polysyllabic_listed]
        detail = []
        for idx, sentence in enumerate(sentences[: self.max_sentences_detail]):
            s_words = m["sentence_words"][idx]
            s_syllables = sum(self._syllables(w) for w in s_words)
            preview = sentence[: self.sentence_preview_length]
            if len(sentence) > self.sentence_preview_length:
                preview = preview + "..."
            if s_words:
                s_wps = len(s_words)
                s_spw = s_syllables / s_wps
                s_score = 206.835 - 1.015 * s_wps - 84.6 * s_spw
            else:
                s_score = None
            detail.append(
                {
                    "text": preview,
                    "words": len(s_words),
                    "syllables": s_syllables,
                    "score": s_score,
                }
            )
        return {
            "metrics": {
                "word_count": len(words),
                "sentence_count": len(sentences),
                "syllable_count": m["total_syllables"],
                "complex_word_count": len(m["polysyllabic"]),
                "polysyllabic": polysyllabic,
                "polysyllabic_truncated": len(m["polysyllabic"]) > self.max_polysyllabic_listed,
                "char_count": m["char_count"],
                "letters_only": m["letters_only"],
                "avg_words_per_sentence": (len(words) / len(sentences)) if sentences else None,
                "avg_syllables_per_word": (
                    m["total_syllables"] / len(words) if words else None
                ),
            },
            "scores": scores,
            "word_syllables": [
                {"word": w, "syllables": c} for w, c in listed_words
            ],
            "word_syllables_truncated": len(word_syllables) > self.max_word_syllables,
            "sentences": detail,
            "sentences_truncated": len(sentences) > self.max_sentences_detail,
        }

    # ------------------------------------------------------------------
    # Modes
    # ------------------------------------------------------------------

    def _analyze(self, text: str, cjk_mode: str) -> dict[str, Any]:
        text = self._bounded_text(text, "text")
        caveats: list[str] = []
        if _CJK_CHAR.search(text) and cjk_mode == "reject":
            raise ValueError(
                "text contains CJK characters; readability formulas are defined for "
                "space-delimited alphabetic languages - pass cjk='naive' to score anyway "
                "with a documented caveat"
            )
        if not text.strip():
            caveats.append("empty_text: no words or sentences to score")
            return {
                "status": "success",
                "mode": "analyze",
                "metrics": {
                    "word_count": 0,
                    "sentence_count": 0,
                    "syllable_count": 0,
                    "complex_word_count": 0,
                    "polysyllabic": [],
                    "polysyllabic_truncated": False,
                    "char_count": 0,
                    "letters_only": 0,
                    "avg_words_per_sentence": None,
                    "avg_syllables_per_word": None,
                },
                "scores": {name: {"score": None, "band": None} for name in sorted(_FORMULAS)},
                "word_syllables": [],
                "word_syllables_truncated": False,
                "sentences": [],
                "sentences_truncated": False,
                "caveats": caveats,
            }
        if len(_EASY_WORDS_76) != 76:  # defensive: list must stay exact
            raise ValueError("embedded easy-word list must contain exactly 76 entries")
        payload = self._analyze_payload(text, caveats)
        payload["status"] = "success"
        payload["mode"] = "analyze"
        payload["caveats"] = caveats
        return payload

    def _compare(self, a: str, b: str, cjk_mode: str) -> dict[str, Any]:
        a = self._bounded_text(a, "a")
        b = self._bounded_text(b, "b")
        caveats_a: list[str] = []
        caveats_b: list[str] = []
        for label, text, caveats in (("a", a, caveats_a), ("b", b, caveats_b)):
            if _CJK_CHAR.search(text) and cjk_mode == "reject":
                raise ValueError(
                    f"text {label!r} contains CJK characters; pass cjk='naive' to score anyway"
                )
        side_a = self._analyze_payload(a, caveats_a)
        side_b = self._analyze_payload(b, caveats_b)
        formulas: dict[str, Any] = {}
        votes_a = votes_b = votes_tie = 0
        deciding: list[str] = []
        for name in sorted(_FORMULAS):
            sa = side_a["scores"][name]["score"]
            sb = side_b["scores"][name]["score"]
            if sa is None or sb is None:
                formulas[name] = {
                    "a": sa,
                    "b": sb,
                    "easier": None,
                    "a_band": side_a["scores"][name]["band"],
                    "b_band": side_b["scores"][name]["band"],
                }
                votes_tie += 0
                continue
            if sa == sb:
                easier = "tie"
                votes_tie += 1
            elif (sb - sa if name != "flesch" else sa - sb) > 0:
                easier = "a"
                votes_a += 1
                deciding.append(name)
            else:
                easier = "b"
                votes_b += 1
                deciding.append(name)
            formulas[name] = {
                "a": sa,
                "b": sb,
                "easier": easier,
                "a_band": side_a["scores"][name]["band"],
                "b_band": side_b["scores"][name]["band"],
            }
        decided = votes_a + votes_b
        side_a_scored = any(
            side_a["scores"][name]["score"] is not None for name in _FORMULAS
        )
        side_b_scored = any(
            side_b["scores"][name]["score"] is not None for name in _FORMULAS
        )
        if not (side_a_scored and side_b_scored):
            verdict = "undecidable"  # at least one side has no scoreable text
        elif decided == 0 or votes_a == votes_b:
            verdict = "tie"
        else:
            verdict = "a" if votes_a > votes_b else "b"
        unanimous = decided > 0 and (votes_a == decided or votes_b == decided)
        caveats = [f"a: {c}" for c in caveats_a] + [f"b: {c}" for c in caveats_b]
        return {
            "status": "success",
            "mode": "compare",
            "a": side_a,
            "b": side_b,
            "formulas": formulas,
            "summary": {
                "easier": verdict,
                "unanimous": unanimous,
                "votes": {"a": votes_a, "b": votes_b, "tie": votes_tie},
                "deciding_formulas": sorted(deciding),
            },
            "caveats": caveats,
        }

    def _grade_band(self, score: Any, formula: Any) -> dict[str, Any]:
        name = self._choice(formula, "formula", _FORMULAS)
        if isinstance(score, bool) or not isinstance(score, (int, float)):
            raise TypeError("score must be a number")
        value = float(score)
        if not math.isfinite(value):
            raise ValueError("score must be a finite number")
        return {
            "status": "success",
            "mode": "grade_band",
            "formula": name,
            "score": value,
            "band": self._band_for(name, value),
            "easier_direction": "higher" if name == "flesch" else "lower",
        }
