#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: light_stemmer_tool.py

"""Deterministic English light word-stemming tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration): agents that normalize vocabulary for search or matching
need a stemmer, and the existing generic helpers do not provide one
(``RegexTool`` substitutes patterns and a stopword remover deletes
words — neither collapses ``ponies``/``poni``-style inflections). This
tool provides a **Porter-inspired light stemmer** — deliberately NOT a
full Porter implementation — with zero dependencies (no NLTK) and
fully deterministic output.

Three modes:

* ``stem`` — stem a single word (``word``) or a list of words
  (``words``, capped at 10,000 items).
* ``stem_text`` — tokenize a text (``text``) or a list of texts
  (``texts``) into alphabetic runs and return ``[{original, stem}]``
  pairs aligned with the input.
* ``group`` — group a list of words (``words``) by their stem,
  returning ``{stem: [originals]}`` (first-seen order, duplicates
  collapsed) for vocabulary collapsing.

The optional ``lowercase`` flag (default ``False``) lowercases every
input word before stemming. Suffix rules are defined over lowercase
text, so callers normalizing mixed-case vocabulary should enable it.

Algorithm — exact rule set
--------------------------

The stemmer applies four ordered passes. Within a pass, rules are
dispatched by *first suffix match*: the first rule whose suffix
matches the word is selected, and if its condition fails no other
rule of that pass fires (this mirrors the classic Porter dispatch).
``m`` below is the Porter measure — the number of vowel-consonant
transitions of the form ``[C](VC)^m[V]``, with ``y`` counting as a
vowel exactly when preceded by a consonant.

**Step 1a** (plural suffixes):

======= ========
input   output
======= ========
sses    ss
ies     i
ss      (keep)
s       '' — only when the word is longer than one character
======= ========

**Step 1b** (participle / trailing-e suffixes, first match wins):

===== ============================ ==========================================
rule  condition                   example
===== ============================ ==========================================
e     m(stem before the e) > 0    rate -> rat
eed   m(stem before eed) > 0      agreed -> agree
ed    stem before ed has a vowel  plastered -> plaster
ing   stem before ing has a vowel motoring -> motor
===== ============================ ==========================================

If the selected rule's condition fails the word is left unchanged
(``feed -> feed``: the ``eed`` rule matches but m("f") == 0).

**Step 1c**: ``y -> i`` when m(stem before the y) > 0 *and* the letter
before the y is a consonant (``happy -> happi``; ``sky`` and
``enjoy`` are unchanged).

**Step 2 lite** (first suffix match wins, every rule conditioned on
m(stem before the suffix) > 0):

========= ======== =========================
suffix    output   example
========= ======== =========================
ational   ate      relational -> relate
tional    tion     conditional -> condition
izer      ize      digitizer -> digitize
ness      ''       goodness -> good
========= ======== =========================

Divergences from full Porter (deliberate, this is the "light" part):

1. Only the subset above is implemented — full Porter steps 2 (the
   remaining ~20 suffixes), 3, 4 and 5 are absent, so e.g.
   ``rational`` stays ``rational`` (full Porter reaches ``ration``
   via the step-4 ``al`` rule) and ``formalize`` keeps its suffix.
2. The trailing-``e`` rule uses the laxer condition ``m > 0`` and
   runs inside step 1b (before ``eed``/``ed``/``ing`` and before
   step 2) instead of full Porter's step 5a ``m > 1`` (or ``m == 1``
   and not ``*o``) at the very end: ``rate -> rat`` and
   ``love -> lov`` here, ``rate``/``love`` under full Porter.
3. No step-1b cleanup: no ``AT -> ATE``/``BL -> BLE``/``IZ -> IZE``
   mapping, no doubled-consonant undo, and no ``e`` restoration for
   short results — ``running -> runn`` (full Porter: ``run``),
   ``hoping -> hop`` (full Porter: ``hope``).
4. Step 1c is stricter than full Porter's ``(*v*) Y -> I``: it also
   requires a consonant before the ``y``, so ``enjoy`` stays
   ``enjoy`` (full Porter: ``enjoi``).
5. The ``s -> ''`` rule keeps a single-letter word ``"s"`` intact as
   a safety guard.

Input validation is strict and happens before any computation:
malformed parameters (unknown mode, wrong types, both/neither of the
single- and list-shaped inputs, empty or non-alphabetic words,
hyphenated compounds, oversized words, more than 10,000 words or
tokens, text over 100,000 characters) raise a ``ValueError``.
Hyphenated compounds such as ``"state-of-the-art"`` are rejected
with a note suggesting to split on ``-`` and stem the parts —
silently stemming only one fragment would mislead vocabulary
normalization.
"""

import re
from typing import Any, ClassVar, Dict, List

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

_ALPHA_WORD = re.compile(r"\A[A-Za-z]+\Z")
# Tokens for stem_text: maximal runs of ASCII letters (punctuation,
# digits and other characters act as separators and are dropped).
_ALPHA_RUN = re.compile(r"[A-Za-z]+")


class LightStemmerTool(Tool):
    """Deterministic Porter-inspired light stemmer (pure stdlib, no NLTK).

    Attributes:
        max_words (int): Upper bound on list inputs (``words``) and on
            the token count of ``stem_text`` inputs.
        max_word_chars (int): Upper bound on a single word's length.
        max_text_chars (int): Upper bound on a single text's length.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "light_stemmer_tool"
    description: str = (
        "Deterministic English light word stemmer — pure Python stdlib, "
        "no NLTK, no network. Porter-inspired light rule set (NOT full "
        "Porter; divergences documented in the module docstring). "
        "mode='stem' stems one word or a list of words; mode='stem_text' "
        "tokenizes a text (or list of texts) into alphabetic runs and "
        "returns original/stem pairs; mode='group' groups a word list by "
        "stem for vocabulary collapsing. Optional lowercase=True "
        "lowercases input before stemming (recommended for suffix "
        "matching, which is defined over lowercase text)."
    )

    MODES: ClassVar[tuple] = ("stem", "stem_text", "group")

    max_words: int = 10_000
    max_word_chars: int = 1_000
    max_text_chars: int = 100_000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any = None,
        word: Any = None,
        words: Any = None,
        text: Any = None,
        texts: Any = None,
        lowercase: Any = None,
    ) -> Dict[str, Any]:
        """Run one stemming operation.

        Args:
            mode (str): One of ``stem`` / ``stem_text`` / ``group``.
            word (str): ``stem`` mode only — a single word to stem.
            words (list): ``stem``/``group`` modes — a non-empty list of
                words (max 10,000 items). ``group`` requires this.
            text (str): ``stem_text`` mode only — a single text.
            texts (list): ``stem_text`` mode only — a non-empty list of
                texts; the result is a list of per-text pair lists.
            lowercase (bool): Lowercase every input word before
                stemming (default ``False``).

        Returns:
            Dict[str, Any]: The operation result under ``result``
                (string for a single ``stem`` word; list otherwise;
                ``{stem: [originals]}`` mapping for ``group``) plus the
                call context (``mode``, ``lowercase``, and ``count`` /
                ``token_count`` / ``group_count`` depending on the
                mode).

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        clean_lowercase = self._validate_lowercase(lowercase)
        if mode == "stem":
            return self._run_stem(word, words, clean_lowercase)
        if mode == "stem_text":
            return self._run_stem_text(text, texts, clean_lowercase)
        return self._run_group(word, words, clean_lowercase)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"light_stemmer_tool: {message}")

    @classmethod
    def _validate_lowercase(cls, lowercase: Any) -> bool:
        """Validate the ``lowercase`` flag (None means ``False``)."""
        if lowercase is None:
            return False
        if isinstance(lowercase, bool):
            return lowercase
        cls._invalid(f"lowercase must be a boolean (got {lowercase!r})")

    @classmethod
    def _validate_word(cls, word: Any) -> str:
        """Validate a single input word (ASCII letters only)."""
        if word is None or isinstance(word, bool) or not isinstance(word, str):
            cls._invalid(f"word must be a non-empty ASCII-letter string (got {word!r})")
        if not word:
            cls._invalid("word must be a non-empty ASCII-letter string (got '')")
        if len(word) > 1000:
            cls._invalid(
                f"word exceeds the 1,000-character limit (got {len(word):,} characters)"
            )
        if not _ALPHA_WORD.match(word):
            if "-" in word:
                cls._invalid(
                    f"word must contain only ASCII English letters "
                    f"(got {word[:64]!r}) — hyphenated compounds are not "
                    "supported: split the word on '-' and stem each part"
                )
            cls._invalid(
                "word must contain only ASCII English letters, without "
                f"spaces, digits, apostrophes or accents (got {word[:64]!r})"
            )
        return word

    @classmethod
    def _validate_words(cls, words: Any) -> List[str]:
        """Validate a list of input words (non-empty, capped)."""
        if words is None or isinstance(words, bool) or not isinstance(words, list):
            cls._invalid(f"words must be a non-empty list of words (got {words!r})")
        if not words:
            cls._invalid("words must be a non-empty list of words (got [])")
        if len(words) > 10_000:
            cls._invalid(
                f"words exceeds the 10,000-item limit (got {len(words):,} items)"
            )
        for item in words:
            if item is None or isinstance(item, bool) or not isinstance(item, str):
                cls._invalid(f"every word must be a string (got {item!r})")
            cls._validate_word(item)
        return words

    @classmethod
    def _validate_text(cls, text: Any) -> str:
        """Validate a single input text."""
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
    def _validate_texts(cls, texts: Any) -> List[str]:
        """Validate a list of input texts (non-empty, capped)."""
        if texts is None or isinstance(texts, bool) or not isinstance(texts, list):
            cls._invalid(f"texts must be a non-empty list of strings (got {texts!r})")
        if not texts:
            cls._invalid("texts must be a non-empty list of strings (got [])")
        if len(texts) > 10_000:
            cls._invalid(
                f"texts exceeds the 10,000-item limit (got {len(texts):,} items)"
            )
        for item in texts:
            if item is None or isinstance(item, bool) or not isinstance(item, str):
                cls._invalid(f"every text must be a string (got {item!r})")
            cls._validate_text(item)
        return texts

    # ------------------------------------------------------------------ #
    # Modes
    # ------------------------------------------------------------------ #

    def _run_stem(
        self, word: Any, words: Any, lowercase: bool
    ) -> Dict[str, Any]:
        """Stem one word or a list of words."""
        if word is not None and words is not None:
            self._invalid("provide either word or words, not both")
        if word is not None:
            clean_word = self._validate_word(word)
            source = clean_word.lower() if lowercase else clean_word
            return {
                "mode": "stem",
                "lowercase": lowercase,
                "result": self.stem(source),
            }
        if words is None:
            self._invalid("stem mode requires a word (string) or words (list)")
        clean_words = self._validate_words(words)
        sources = [w.lower() if lowercase else w for w in clean_words]
        return {
            "mode": "stem",
            "lowercase": lowercase,
            "count": len(sources),
            "result": [self.stem(source) for source in sources],
        }

    def _run_stem_text(
        self, text: Any, texts: Any, lowercase: bool
    ) -> Dict[str, Any]:
        """Tokenize text(s) into alphabetic runs and pair original/stem."""
        if text is not None and texts is not None:
            self._invalid("provide either text or texts, not both")
        if text is not None:
            clean_text = self._validate_text(text)
            batch = [clean_text]
        elif texts is not None:
            batch = self._validate_texts(texts)
        else:
            self._invalid("stem_text mode requires a text (string) or texts (list)")

        per_text: List[List[Dict[str, str]]] = []
        total = 0
        for one in batch:
            pairs: List[Dict[str, str]] = []
            for token in _ALPHA_RUN.findall(one):
                total += 1
                if total > 10_000:
                    self._invalid(
                        "stem_text input produces more than the "
                        "10,000-token limit"
                    )
                source = token.lower() if lowercase else token
                pairs.append({"original": token, "stem": self.stem(source)})
            per_text.append(pairs)
        if text is not None:
            result: Any = per_text[0]
        else:
            result = per_text
        return {
            "mode": "stem_text",
            "lowercase": lowercase,
            "token_count": total,
            "result": result,
        }

    def _run_group(
        self, word: Any, words: Any, lowercase: bool
    ) -> Dict[str, Any]:
        """Group words by stem (first-seen order, duplicates collapsed)."""
        if words is None:
            self._invalid(
                "group mode requires words (a list of words to group)"
            )
        if word is not None:
            self._invalid(
                "group mode takes a words list, not a single word "
                "(a one-word group is the word itself)"
            )
        clean_words = self._validate_words(words)
        groups: Dict[str, List[str]] = {}
        for original in clean_words:
            source = original.lower() if lowercase else original
            stem = self.stem(source)
            bucket = groups.setdefault(stem, [])
            if original not in bucket:
                bucket.append(original)
        return {
            "mode": "group",
            "lowercase": lowercase,
            "group_count": len(groups),
            "result": groups,
        }

    # ------------------------------------------------------------------ #
    # The light stemmer itself
    # ------------------------------------------------------------------ #

    _VOWELS: ClassVar[frozenset] = frozenset("aeiou")

    # Step 2 lite rules, longest-suffix first (ational must be tried
    # before tional: "relational" ends in both).
    _STEP2_RULES: ClassVar[tuple] = (
        ("ational", "ate"),
        ("tional", "tion"),
        ("izer", "ize"),
        ("ness", ""),
    )

    @classmethod
    def _cv_forms(cls, word: str) -> List[str]:
        """Classify each letter as ``C`` or ``V`` per Porter's definition.

        A letter is a consonant if it is not ``a/e/i/o/u`` and it is
        not a ``y`` preceded by a consonant (so ``y`` in ``toy`` is a
        consonant while ``y`` in ``syzygy`` alternates).
        """
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
        """Porter measure ``m`` of a stem: the number of ``VC``
        transitions in the ``[C](VC)^m[V]`` form of ``stem``."""
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
        """Stem one lowercase word with the documented light rule set.

        The word is assumed to be validated (ASCII letters) and already
        lowercased when the caller enabled the ``lowercase`` option;
        suffix matching is case-sensitive by design.
        """
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
        # First suffix match selects the rule; a failed condition ends
        # the step (feed keeps its 'eed' because m("f") == 0).
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
