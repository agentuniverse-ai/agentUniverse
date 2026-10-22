# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @FileName: passive_voice_detector.py

import re
from bisect import bisect_right
from typing import List, Optional, Tuple

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

# --------------------------------------------------------------------- #
# English pattern tables
# --------------------------------------------------------------------- #

# Finite and non-finite forms of "to be" that anchor an English passive.
BE_FORMS = frozenset(
    {"am", "is", "are", "was", "were", "be", "been", "being"})

# Negated be-forms folded into one token by the tokenizer; each carries an
# implicit "not", so the participle is expected directly after them.
NT_BE_FORMS = frozenset({"isn't", "aren't", "wasn't", "weren't"})

# A single adverb may sit between the be-form and the participle
# ("was not submitted", "is widely adopted").
INTERVENING_ADVERBS = frozenset({
    "not", "never", "often", "rarely", "sometimes", "always", "usually",
    "frequently", "already", "just", "still", "also", "indeed", "strongly",
    "widely", "heavily", "quickly", "clearly", "nearly", "almost", "fully",
    "partially",
})

# ~90 common irregular past participles that do not end in "-ed".
IRREGULAR_PARTICIPLES = frozenset({
    "arisen", "become", "begun", "bent", "bitten", "blown", "born", "bought",
    "broken", "brought", "built", "burnt", "burst", "cast", "caught",
    "chosen", "come", "cost", "cut", "dealt", "done", "drawn", "driven",
    "drunk", "eaten", "fallen", "fed", "felt", "fought", "found", "flown",
    "forbidden", "forgotten", "forgiven", "frozen", "gotten", "given",
    "gone", "grown", "heard", "held", "hidden", "hit", "hurt", "kept",
    "known", "laid", "led", "left", "lent", "let", "lost", "made", "meant",
    "met", "paid", "put", "quit", "read", "ridden", "risen", "run", "said",
    "seen", "sold", "sent", "set", "shaken", "shot", "shut", "shown",
    "sung", "sunk", "sat", "slept", "spoken", "spent", "split", "spread",
    "stolen", "stood", "struck", "sworn", "taken", "taught", "told",
    "thought", "thrown", "understood", "worn", "won", "withdrawn",
    "written",
})

# Adjectives ending in "-ed" that follow a be-form but describe a state,
# not a passive action; never counted.
ADJECTIVAL_STOPLIST = frozenset({"interested", "tired", "excited"})

# "be used to" / "be supposed to" are semi-auxiliaries, not passives; the
# guard applies only when the participle is immediately followed by "to".
SEMI_AUXILIARY_STOPLIST = frozenset({"used", "supposed"})

# Minimum length for a bare "-ed" token to count as a regular participle;
# this excludes "red", "bed" and other three-letter words that merely end
# in those letters.
MINIMUM_ED_LENGTH = 4

# Word tokens: letters plus an optional ASCII clitic such as "wasn't".
WORD_TOKEN_PATTERN = re.compile(r"[A-Za-z]+(?:'[A-Za-z]{1,2})?")

# Function words that terminate a "by"-agent noun phrase.
AGENT_BOUNDARY_WORDS = frozenset({
    "of", "in", "on", "at", "to", "for", "with", "and", "or", "but", "when",
    "while", "because", "before", "after", "since", "as", "than", "so", "if",
    "that", "which", "who", "where",
})

# "by X" counts as the agent when "by" appears within this many tokens
# after the participle; the agent phrase itself is capped separately.
AGENT_WINDOW = 5
AGENT_MAX_WORDS = 3

# --------------------------------------------------------------------- #
# Chinese pattern tables
# --------------------------------------------------------------------- #

# Passive markers of Mandarin prose. The bare marker 受 is only matched at
# the start of a word (never directly after another Han character), which
# suppresses the many verbs ending in 受 such as 接受, 享受 or 忍受.
ZH_PASSIVE_PATTERNS = (
    re.compile(r"被[一-龥]{1,8}"),
    re.compile(r"(?<![一-龥])受(?![到])[一-龥]{1,8}"),
    re.compile(r"受到[一-龥]{1,8}"),
    re.compile(r"遭到[一-龥]{1,8}"),
    re.compile(r"由[一-龥]{1,12}所[一-龥]{1,8}"),
)

# --------------------------------------------------------------------- #
# Shared tables
# --------------------------------------------------------------------- #

# Sentence segmentation: any run of characters that are not sentence
# terminators (Western and Chinese) or line breaks is one sentence.
SENTENCE_SEGMENT_PATTERN = re.compile(r"[^.!?。！？；;\n]+")


class PassiveVoiceDetector(DocProcessor):
    """Measure passive-voice density per document and record it as metadata.

    Heavy passive voice is a classic writing-quality smell: documentation
    guides read better in the active voice, and regulatory or legal text
    leans on passives to leave the acting party unstated. This processor
    scans every document for passive constructions in English and Chinese,
    writes a per-document report into document metadata, and keeps every
    document — it is an analyzer, not a filter. Downstream agents (or a
    human reviewer's dashboard) can then rank documents by style_flag
    without re-reading them. It addresses the pre-processing/analysis
    direction of issue #258 and is complementary to readability or
    emphasis markers: those answer "how hard is the text" and "what does
    it stress", while this one answers "who does the text hide".

    The English matcher is token-based and deliberately conservative in
    scope: a passive is a be-form (am/is/are/was/were/be/been/being, plus
    the contractions isn't/aren't/wasn't/weren't), optionally followed by
    one interposed adverb (not/never/often/...), followed by a past
    participle — either a regular "-ed" form of at least four letters or
    one of ~90 common irregular participles (done, given, taken, seen,
    ...). Progressive and perfect passives ("is being reviewed", "has been
    reviewed") are caught by their inner be-form + participle pair. Three
    adjectival guards keep state descriptions from counting as passives:
    "interested/tired/excited" after a be-form are skipped outright, and
    "used/supposed" are skipped when immediately followed by "to" ("is
    used to convert files"). When the token "by" follows the participle
    within five tokens of the same sentence, the following (up to three
    word) noun phrase is recorded as the agent, preserving original
    capitalization; hits without such an agent carry null.

    The Chinese matcher recognizes the markers 被, 受, 受到, 遭到 and the
    由 ... 所 construction, each followed by a bounded run of Han
    characters as the verb. The bare marker 受 is only matched at the
    start of a word — not directly after another Han character — so verbs
    merely ending in 受 (接受, 享受, ...) do not fire. No agent is
    extracted for Chinese hits.

    Both matchers only ever look at the characters of the text: the
    component is deterministic, offline, dependency-free (pure standard
    library) and safe to run before or after any other processor. The
    report written to ``metadata[output_key]`` contains:

    - ``passive_count``: total passive constructions found;
    - ``total_sentences``: sentence count (segments split on Western and
      Chinese terminators and line breaks);
    - ``passive_ratio``: fraction of sentences containing at least one
      passive, rounded to four decimals (0.0 when there are no
      sentences);
    - ``passive_density_per_100``: passive constructions per 100
      sentences, rounded to two decimals;
    - ``style_flag``: ``active`` (ratio below moderate_threshold),
      ``moderate`` (ratio in [moderate_threshold, heavy_threshold]) or
      ``heavy`` (ratio above heavy_threshold); defaults 10% / 25%;
    - ``hits``: per-hit records ``{text, span, lang, agent}`` — matched
      surface text, ``[start, end]`` character span, ``en``/``zh``, and
      the agent phrase or null (English only) — sorted by span and
      capped at ``max_hits`` entries;
    - ``hits_truncated``: whether the cap dropped any records (counting
      itself is never capped).

    Metadata mappings are copied before mutation; text, id and all other
    fields are left untouched.

    Attributes:
        moderate_threshold: Ratio at or above which style_flag becomes
            ``moderate``; float in [0, 1], default 0.10.
        heavy_threshold: Ratio strictly above which style_flag becomes
            ``heavy``; float in [0, 1], default 0.25; must exceed
            moderate_threshold.
        max_hits: Maximum number of per-hit records written into
            metadata (earliest spans kept); must be >= 1. Detection keeps
            counting past the cap.
        output_key: Metadata key the report dict is written to; an empty
            value disables stamping entirely.
    """

    moderate_threshold: float = 0.10
    heavy_threshold: float = 0.25
    max_hits: int = 50
    output_key: str = "passive_voice"

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Analyze every document and stamp its passive-voice report.

        Args:
            origin_docs: Documents to analyze, in batch order.
            query: Query object (unused; analysis depends only on the
                documents' own text).

        Returns:
            List[Document]: The same documents in the same order, each
            carrying its report in metadata[output_key].
        """
        if not origin_docs:
            return []
        for doc in origin_docs:
            report = self._analyze(doc.text or "")
            if self.output_key:
                meta = dict(doc.metadata or {})
                meta[self.output_key] = report
                doc.metadata = meta
        return list(origin_docs)

    # ------------------------------------------------------------------ #
    # Analysis core
    # ------------------------------------------------------------------ #

    def _analyze(self, text: str) -> dict:
        """Compute the passive-voice report for one text.

        Args:
            text: Document text (None already normalized to "").

        Returns:
            dict: Report as described in the class docstring.
        """
        text = text or ""
        sentences = self._sentences(text)
        tokens = self._tokens(text, sentences)

        candidates: List[Tuple[int, int, str, Optional[str]]] = []
        candidates.extend(self._english_hits(text, tokens))
        candidates.extend(self._chinese_hits(text))

        # Drop overlapping candidates (possible among the Chinese
        # patterns) and fix a single deterministic order: by span start,
        # then span end.
        candidates.sort(key=lambda hit: (hit[0], hit[1]))
        hits: List[Tuple[int, int, str, Optional[str]]] = []
        for cand in candidates:
            start, end = cand[0], cand[1]
            if any(start < kept[1] and kept[0] < end for kept in hits):
                continue
            hits.append(cand)

        total_sentences = len(sentences)
        passive_count = len(hits)
        hit_sentences = set()
        sentence_starts = [span[0] for span in sentences]
        for start, _, _, _ in hits:
            index = bisect_right(sentence_starts, start) - 1
            if index >= 0:
                hit_sentences.add(index)

        if total_sentences:
            ratio = round(len(hit_sentences) / total_sentences, 4)
            density = round(passive_count / total_sentences * 100, 2)
        else:
            ratio = 0.0
            density = 0.0

        if ratio > self.heavy_threshold:
            style_flag = "heavy"
        elif ratio >= self.moderate_threshold:
            style_flag = "moderate"
        else:
            style_flag = "active"

        recorded = [{
            "text": text[start:end],
            "span": [start, end],
            "lang": lang,
            "agent": agent,
        } for start, end, lang, agent in hits[:self.max_hits]]

        return {
            "passive_count": passive_count,
            "total_sentences": total_sentences,
            "passive_ratio": ratio,
            "passive_density_per_100": density,
            "style_flag": style_flag,
            "hits": recorded,
            "hits_truncated": passive_count > len(recorded),
        }

    @staticmethod
    def _sentences(text: str) -> List[Tuple[int, int]]:
        """Split text into (start, end) sentence segments.

        Segments are runs of characters between Western or Chinese
        sentence terminators and line breaks; runs that are blank after
        stripping are not sentences.

        Args:
            text: Document text.

        Returns:
            List[Tuple[int, int]]: Sentence spans in document order.
        """
        return [(m.start(), m.end())
                for m in SENTENCE_SEGMENT_PATTERN.finditer(text)
                if m.group().strip()]

    @staticmethod
    def _tokens(text: str,
                sentences: List[Tuple[int, int]]) -> List[Tuple[str, int, int, int]]:
        """Tokenize English word tokens and tag each with its sentence.

        Args:
            text: Document text.
            sentences: Sentence spans from _sentences.

        Returns:
            List[Tuple[str, int, int, int]]: (lowercased word, start,
            end, sentence index) tuples in document order.
        """
        tokens = []
        sentence_index = 0
        for match in WORD_TOKEN_PATTERN.finditer(text):
            while sentence_index + 1 < len(sentences) and \
                    match.start() >= sentences[sentence_index + 1][0]:
                sentence_index += 1
            tokens.append((match.group().lower(), match.start(),
                           match.end(), sentence_index))
        return tokens

    def _english_hits(self, text: str,
                      tokens: List[Tuple[str, int, int, int]]) \
            -> List[Tuple[int, int, str, Optional[str]]]:
        """Find English passives: be-form (+ adverb) + past participle.

        Args:
            text: Original document text (for agent-phrase slices).
            tokens: Token list from _tokens.

        Returns:
            List[Tuple[int, int, str, Optional[str]]]: (start, end,
            'en', agent-or-None) tuples, one per matched construction.
        """
        hits = []
        for i, (word, start, _, sentence) in enumerate(tokens):
            if word in NT_BE_FORMS:
                # Negation is folded into the contraction; the
                # participle must follow directly.
                participle_index = i + 1
            elif word in BE_FORMS:
                participle_index = i + 1
                if participle_index < len(tokens) and \
                        tokens[participle_index][3] == sentence and \
                        tokens[participle_index][0] in INTERVENING_ADVERBS:
                    participle_index += 1
            else:
                continue
            if participle_index >= len(tokens):
                continue
            candidate, cand_start, cand_end, cand_sentence = \
                tokens[participle_index]
            if cand_sentence != sentence:
                continue
            next_word = None
            if participle_index + 1 < len(tokens) and \
                    tokens[participle_index + 1][3] == cand_sentence:
                next_word = tokens[participle_index + 1][0]
            if not self._is_en_participle(candidate, next_word):
                continue
            agent = self._by_agent(text, tokens, participle_index,
                                   cand_sentence)
            hits.append((start, cand_end, "en", agent))
        return hits

    @staticmethod
    def _is_en_participle(word: str, next_word: Optional[str]) -> bool:
        """Decide whether a token is the participle of a passive.

        Args:
            word: Lowercased candidate token.
            next_word: Lowercased token after it (same sentence), if any.

        Returns:
            bool: True when the token passes the adjectival guards and
            is a regular "-ed" form or a known irregular participle.
        """
        if word in ADJECTIVAL_STOPLIST:
            return False
        if word in SEMI_AUXILIARY_STOPLIST and next_word == "to":
            return False
        if word in IRREGULAR_PARTICIPLES:
            return True
        return word.endswith("ed") and len(word) >= MINIMUM_ED_LENGTH

    @staticmethod
    def _by_agent(text: str,
                  tokens: List[Tuple[str, int, int, int]],
                  participle_index: int, sentence: int,
                  ) -> Optional[str]:
        """Extract the "by X" agent phrase of one English passive.

        The token "by" must appear within AGENT_WINDOW tokens after the
        participle, inside the same sentence. The agent phrase then runs
        from the token after "by" up to the first boundary word (of, in,
        on, ...) or sentence end, capped at AGENT_MAX_WORDS tokens; it
        is sliced from the original text so capitalization survives.

        Args:
            text: Original document text.
            tokens: Token list from _tokens.
            participle_index: Index of the participle token.
            sentence: Sentence index of the passive.

        Returns:
            Optional[str]: Agent surface text, or None when no in-window
            "by" introduces one.
        """
        for by_index in range(participle_index + 1,
                              participle_index + 1 + AGENT_WINDOW):
            if by_index >= len(tokens):
                break
            if tokens[by_index][3] != sentence:
                break
            word = tokens[by_index][0]
            # A fresh be-form opens a new construction: a "by" behind it
            # belongs to that construction, not to this one.
            if word in BE_FORMS or word in NT_BE_FORMS:
                break
            if word != "by":
                continue
            words = []
            for agent_index in range(by_index + 1,
                                     by_index + 1 + AGENT_MAX_WORDS):
                if agent_index >= len(tokens):
                    break
                word, word_start, word_end, word_sentence = \
                    tokens[agent_index]
                if word_sentence != sentence or \
                        word in AGENT_BOUNDARY_WORDS:
                    break
                words.append((word_start, word_end))
            if not words:
                return None
            return text[words[0][0]:words[-1][1]]
        return None

    @staticmethod
    def _chinese_hits(text: str) -> List[Tuple[int, int, str, Optional[str]]]:
        """Find Chinese passives via the marker patterns.

        Args:
            text: Document text.

        Returns:
            List[Tuple[int, int, str, Optional[str]]]: (start, end,
            'zh', None) tuples for every marker match; agents are an
            English-only feature.
        """
        hits = []
        for pattern in ZH_PASSIVE_PATTERNS:
            for match in pattern.finditer(text):
                hits.append((match.start(), match.end(), "zh", None))
        return hits

    # ------------------------------------------------------------------ #
    # Configuration
    # ------------------------------------------------------------------ #

    @staticmethod
    def _read_ratio(configer: ComponentConfiger, key: str) -> Optional[float]:
        """Read one threshold from the configer, validating type/range.

        Args:
            configer: Configuration object.
            key: Attribute name.

        Returns:
            Optional[float]: The threshold, or None when absent.

        Raises:
            ValueError: On a non-numeric value or one outside [0, 1].
        """
        if not hasattr(configer, key) or getattr(configer, key) is None:
            return None
        value = getattr(configer, key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{key} must be a number")
        if not 0 <= value <= 1:
            raise ValueError(f"{key} must be in [0, 1]")
        return float(value)

    def _initialize_by_component_configer(
            self, doc_processor_configer: ComponentConfiger) \
            -> 'PassiveVoiceDetector':
        """Initialize and validate the detector from component configuration.

        Validation happens eagerly at load time: a silently mis-scoped
        style flag would skew every downstream writing-QA decision built
        on it.

        Args:
            doc_processor_configer: Configuration object.

        Returns:
            PassiveVoiceDetector: The initialized instance.

        Raises:
            ValueError: On an invalid combination of parameter values.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        moderate = self._read_ratio(doc_processor_configer,
                                    "moderate_threshold")
        if moderate is not None:
            self.moderate_threshold = moderate
        heavy = self._read_ratio(doc_processor_configer, "heavy_threshold")
        if heavy is not None:
            self.heavy_threshold = heavy
        if self.moderate_threshold >= self.heavy_threshold:
            raise ValueError(
                "moderate_threshold must be strictly less than "
                f"heavy_threshold, got {self.moderate_threshold} >= "
                f"{self.heavy_threshold}")

        if hasattr(doc_processor_configer, "max_hits") and \
                doc_processor_configer.max_hits is not None:
            max_hits = doc_processor_configer.max_hits
            if isinstance(max_hits, bool) or not isinstance(max_hits, int):
                raise ValueError("max_hits must be an integer")
            self.max_hits = max_hits
            if self.max_hits < 1:
                raise ValueError("max_hits must be >= 1")

        if hasattr(doc_processor_configer, "output_key") and \
                doc_processor_configer.output_key is not None:
            output_key = doc_processor_configer.output_key
            if not isinstance(output_key, str):
                raise ValueError("output_key must be a string")
            self.output_key = output_key

        return self
