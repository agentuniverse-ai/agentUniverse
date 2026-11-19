# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @FileName: contradiction_signal_detector.py

import re
from typing import List, Optional, Tuple

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

# Sentence terminators (ASCII + CJK + newline; a newline is treated as a
# boundary because pre-processed knowledge text is frequently un-punctuated
# line-oriented content).
_SENTENCE_RE = re.compile(
    r'[^.!?\n。！？；;]+(?:[.!?\n。！？；;]+|$)')

# Word tokenizer: lowercased ASCII letter runs (apostrophes kept so that
# "n't" contractions stay recognizable) and individual CJK characters
# (Chinese is written without spaces, so per-character tokens are the only
# dependency-free approximation of word overlap).
_TOKEN_RE = re.compile(r"[a-z']+|[\u4e00-\u9fff]")

# Contrast markers whose appearance at the START of the later sentence
# suggests the claim is being flipped.
_CONTRAST_WORDS = frozenset(
    {"but", "however", "conversely"})
_CONTRAST_PHRASES = frozenset(
    {"on the contrary", "in contrast"})
_CONTRAST_CJK = frozenset({"但是", "然而", "相反"})

# Negation markers: ASCII tokens (plus "n't"-suffixed contractions such as
# "isn't") and CJK substrings / characters.
_NEGATION_WORDS = frozenset(
    {"not", "no", "never", "none", "without", "cannot"})
_NEGATION_CJK = frozenset({"无", "不", "没", "未"})

# English function words excluded from content-word overlap. Contrast and
# negation markers are excluded separately, as are apostrophe-bearing
# contractions.
_STOPWORDS = frozenset({
    "a", "an", "the", "and", "or", "nor", "if", "then", "else", "when",
    "while", "of", "at", "by", "for", "with", "about", "into", "through",
    "during", "to", "from", "in", "on", "off", "over", "under", "again",
    "further", "once", "here", "there", "all", "any", "both", "each",
    "few", "more", "most", "other", "some", "such", "only", "own", "same",
    "so", "than", "too", "very", "can", "will", "just", "should", "now",
    "is", "are", "was", "were", "be", "been", "being", "am", "have",
    "has", "had", "having", "do", "does", "did", "doing", "would",
    "could", "might", "must", "shall", "may", "i", "you", "he", "she",
    "it", "we", "they", "me", "him", "her", "us", "them", "my", "your",
    "his", "its", "our", "their", "mine", "yours", "hers", "ours",
    "theirs", "this", "that", "these", "those", "as", "until", "because",
    "why", "how", "what", "which", "who", "whom", "whose", "up", "out",
    "down", "also", "either", "neither", "yet", "still", "even", "ever",
    "nevertheless", "nonetheless", "whereas", "although", "though",
    "instead", "rather", "thus", "hence", "therefore", "moreover",
    "furthermore", "besides", "meanwhile", "however", "conversely",
    "before", "after", "between", "among", "within", "upon", "via",
    "per", "onto", "toward", "towards", "without",
})

# CJK function characters excluded from content overlap.
_CJK_STOP_CHARS = frozenset(
    "的了是在有个和与也就都能可要着过吗呢吧啊这那其之地得如但还于是"
    "并且或者因此所以然而不过只是还是非常对于从未被把让给跟同上下中"
    "大小多少好坏之等以后前再去来说着了呢吗")

# Confidence weight per tier; the risk grade sums these over all recorded
# signals (documented heuristic, NOT a calibrated probability).
_CONFIDENCE_WEIGHTS = {"high": 3, "medium": 2, "low": 1}

# Risk grade boundaries on the summed confidence weight.
_RISK_MEDIUM_AT = 3
_RISK_HIGH_AT = 6

# Hard bounds for configuration validation.
_MAX_WINDOW_SIZE = 5
_MAX_SENTENCE_LOOKAHEAD_TOKENS = 4


class ContradictionSignalDetector(DocProcessor):
    """Flag POTENTIAL contradictions in document text for review pipelines.

    Knowledge extracted from heterogeneous sources (FAQ revisions, crawled
    articles, merged product docs) routinely contains claims that quietly
    disagree with each other. Downstream retrieval happily serves both
    sides of a disagreement, and an LLM asked to answer from such a corpus
    either picks a side silently or hedges into uselessness. This processor
    scans each document's sentences and stamps lightweight *heuristic*
    contradiction *signals* into metadata, so review pipelines can route
    suspicious documents to a human instead of shipping them unchecked.

    This is explicitly a surface-form heuristic, NOT semantic NLI: it does
    not parse meaning, does not resolve coreference, and knows nothing
    about world knowledge. It pairs sentences that sit within a small
    window of each other and looks for three lexical patterns:

    - ``contrast_flip`` — the later sentence opens with a contrast marker
      (but / however / conversely / on the contrary / in contrast; 但是 /
      然而 / 相反) while sharing at least one content word with the
      earlier sentence: a classic "X is true. However, X ..." flip.
    - ``negation_repeat`` — the two sentences again share a content word,
      but exactly one of them carries a negation marker (not / no /
      never / n't / none / without; 无 / 不 / 没有 / 未): a polarity
      divergence over the same subject matter.
    - ``mutual_negation`` — both sentences open with the same first few
      words ("subject-ish" opener) and both contain negation while not
      being identical ("the system does not do X" vs "the system does
      not do Y"): rare, low confidence, occasionally a real conflict.

    Each signal records ``{kind, sentence_a_span, sentence_b_span,
    shared_terms (<= 5), confidence}`` where spans are ``[start, end)``
    character offsets into the document text. Confidence is
    ``high`` only for a contrast flip with >= 2 shared content terms,
    ``medium`` for weaker overlap and negation repeats, ``low`` for
    mutual negation. All metadata lands under configurable keys:
    ``contradiction_signals`` (list, capped at ``max_signals``),
    ``signal_count`` and a coarse ``contradiction_risk`` grade of
    none / low / medium / high derived from a documented count-x-
    confidence weight table. Documents are never filtered out, text and
    ids are never modified, and metadata mappings are copied before
    mutation.

    Overlap is computed on "content words": ASCII tokens lowercased and
    reduced by a deliberately crude suffix-stripping stemmer (trailing
    s / es / ed / ing, applied only when the remaining stem keeps at
    least three letters) and individual CJK characters (minus a function
    character list). Two sentences about entirely different topics that
    happen to share the word "however" therefore produce nothing, while
    "supports" vs "support" counts as overlap. Expect false positives
    (antonyms, scoped negations, reported speech) and false negatives
    (paraphrases, synonyms); the output is a triage queue for humans or
    a later semantic pass, not a verdict.

    Deterministic, offline, and dependency-free (pure stdlib regex).

    Attributes:
        window_size: Maximum sentence distance for a compared pair, in
            [1, 5]; the default 2 compares each sentence with the next
            two sentences.
        max_signals: Maximum number of signals recorded per document,
            in [1, 1000]; further signals are dropped (and ``signal_count``
            reflects the recorded list).
        max_shared_terms: Maximum shared content terms kept per signal,
            in [1, 20]; the list is sorted for determinism.
        signals_key: Metadata key for the signal list; empty disables.
        count_key: Metadata key for the recorded-signal count; empty
            disables.
        risk_key: Metadata key for the none/low/medium/high grade; empty
            disables.
    """

    window_size: int = 2
    max_signals: int = 30
    max_shared_terms: int = 5
    signals_key: str = "contradiction_signals"
    count_key: str = "signal_count"
    risk_key: str = "contradiction_risk"

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Stamp contradiction signals into each document's metadata.

        Args:
            origin_docs: Documents to scan, in batch order.
            query: Query object (unused; signals depend only on the
                documents' own text).

        Returns:
            List[Document]: The same documents, in the same order, with
            signal metadata stamped; nothing is filtered or rewritten.
        """
        for doc in origin_docs:
            signals = self._scan(doc.text or "")
            meta = dict(doc.metadata or {})
            if self.signals_key:
                meta[self.signals_key] = signals
            if self.count_key:
                meta[self.count_key] = len(signals)
            if self.risk_key:
                meta[self.risk_key] = self._risk_grade(signals)
            doc.metadata = meta
        return origin_docs

    # ------------------------------------------------------------------ #
    # Scanning
    # ------------------------------------------------------------------ #

    def _scan(self, text: str) -> List[dict]:
        """Collect contradiction signals across sentence pairs.

        Pairs are visited as (earlier, later) with sentence distance in
        ``[1, window_size]``; within one pair the kinds are evaluated in
        the fixed order contrast_flip, negation_repeat, mutual_negation,
        so at most one signal per kind per pair is produced and the output
        order is fully deterministic.

        Args:
            text: Document text (None treated as empty).

        Returns:
            List[dict]: Signals, capped at ``max_signals``.
        """
        sentences = self._split_sentences(text)
        signals: List[dict] = []
        for i, sent_a in enumerate(sentences):
            for j in range(i + 1, min(i + 1 + self.window_size,
                                      len(sentences))):
                sent_b = sentences[j]
                shared = self._shared_terms(sent_a, sent_b)
                if not shared:
                    # Every signal kind requires topical overlap; a bare
                    # "however" about something else is not a flip.
                    continue
                if self._starts_with_contrast(sent_b):
                    signals.append(self._make_signal(
                        "contrast_flip", sent_a, sent_b, shared))
                neg_a = self._has_negation(sent_a)
                neg_b = self._has_negation(sent_b)
                if neg_a != neg_b:
                    signals.append(self._make_signal(
                        "negation_repeat", sent_a, sent_b, shared))
                if neg_a and neg_b and self._same_opener(sent_a, sent_b) \
                        and sent_a["tokens"] != sent_b["tokens"]:
                    signals.append(self._make_signal(
                        "mutual_negation", sent_a, sent_b, shared))
                if len(signals) >= self.max_signals:
                    return signals[:self.max_signals]
        return signals[:self.max_signals]

    def _make_signal(self, kind: str, sent_a: dict, sent_b: dict,
                     shared: List[str]) -> dict:
        """Build one signal record from a flagged sentence pair.

        Args:
            kind: Signal kind (contrast_flip / negation_repeat /
                mutual_negation).
            sent_a: Earlier sentence record.
            sent_b: Later sentence record.
            shared: Sorted shared content terms (non-empty).

        Returns:
            dict: The signal record with confidence tier assigned.
        """
        if kind == "contrast_flip":
            confidence = "high" if len(shared) >= 2 else "medium"
        elif kind == "negation_repeat":
            confidence = "medium" if len(shared) >= 2 else "low"
        else:
            confidence = "low"
        return {
            "kind": kind,
            "sentence_a_span": [sent_a["start"], sent_a["end"]],
            "sentence_b_span": [sent_b["start"], sent_b["end"]],
            "shared_terms": shared[:self.max_shared_terms],
            "confidence": confidence,
        }

    @staticmethod
    def _risk_grade(signals: List[dict]) -> str:
        """Grade overall contradiction risk from the recorded signals.

        Heuristic weight table: each signal contributes high=3, medium=2,
        low=1; the summed weight maps to none (no signals), low (< 3),
        medium ([3, 6)) and high (>= 6). The numbers are tuned only so
        that a single strong flip alone does not shout "high" while a
        handful of independent flags escalate; they are not calibrated
        probabilities.

        Args:
            signals: Recorded signal records.

        Returns:
            str: One of none / low / medium / high.
        """
        if not signals:
            return "none"
        weight = sum(_CONFIDENCE_WEIGHTS[s["confidence"]]
                     for s in signals)
        if weight >= _RISK_HIGH_AT:
            return "high"
        if weight >= _RISK_MEDIUM_AT:
            return "medium"
        return "low"

    # ------------------------------------------------------------------ #
    # Sentence handling
    # ------------------------------------------------------------------ #

    @staticmethod
    def _split_sentences(text: str) -> List[dict]:
        """Split text into sentences with character spans and tokens.

        Sentences are delimited by terminal punctuation (. ! ? ; and
        their CJK counterparts) or newlines. Each record carries the
        ``[start, end)`` span of the trimmed sentence inside the original
        text plus its lowercased token list, so signal consumers can jump
        straight to the offending text.

        Args:
            text: Document text.

        Returns:
            List[dict]: Records with start / end / text / tokens keys.
        """
        sentences = []
        for match in _SENTENCE_RE.finditer(text):
            raw = match.group(0)
            stripped = raw.strip()
            if not stripped:
                continue
            start = match.start() + (len(raw) - len(raw.lstrip()))
            end = start + len(stripped)
            sentences.append({
                "start": start,
                "end": end,
                "text": stripped,
                "tokens": _TOKEN_RE.findall(stripped.lower()),
            })
        return sentences

    def _shared_terms(self, sent_a: dict, sent_b: dict) -> List[str]:
        """Compute the sorted shared content terms of two sentences.

        A content term is a non-stopword token: ASCII words lowercased
        and stemmed by trailing s / es / ed / ing stripping (only when
        the remaining stem keeps at least three letters, so "goes" and
        "us" survive intact rather than collapsing to noise), or a CJK
        character outside the function-character list. Apostrophe-bearing
        contractions and negation / contrast markers never count as
        content, so shared negations do not masquerade as topical
        overlap.

        Args:
            sent_a: First sentence record.
            sent_b: Second sentence record.

        Returns:
            List[str]: Sorted shared terms (possibly empty).
        """
        terms_a = {_stem(t) for t in sent_a["tokens"] if self._is_content(t)}
        terms_b = {_stem(t) for t in sent_b["tokens"] if self._is_content(t)}
        return sorted(terms_a & terms_b)

    @staticmethod
    def _is_content(token: str) -> bool:
        """Report whether one token counts as a content term.

        Args:
            token: Lowercased token (ASCII word or single CJK char).

        Returns:
            bool: True when the token carries topical content.
        """
        if "'" in token:
            # Contractions such as "don't" are pure function words here.
            return False
        if _is_cjk(token):
            return token not in _CJK_STOP_CHARS
        if token in _STOPWORDS or token in _CONTRAST_WORDS \
                or token in _NEGATION_WORDS:
            return False
        # Single letters carry no topical signal; two-letter words ("ai",
        # "ml", "ok") do.
        return len(token) >= 2

    @staticmethod
    def _has_negation(sent: dict) -> bool:
        """Report whether a sentence carries a negation marker.

        ASCII tokens are checked against the marker words plus any
        "n't"-suffixed contraction; CJK tokens against the negation
        characters (which also covers multi-character markers such as
        没有 and 不是, whose leading characters are 没 and 不).

        Args:
            sent: Sentence record.

        Returns:
            bool: True when at least one negation marker is present.
        """
        for token in sent["tokens"]:
            if token in _NEGATION_WORDS:
                return True
            if token.endswith("n't") and len(token) > 3:
                return True
            if _is_cjk(token) and token in _NEGATION_CJK:
                return True
        return False

    def _starts_with_contrast(self, sent: dict) -> bool:
        """Report whether a sentence opens with a contrast marker.

        ASCII markers match the leading tokens (multi-word phrases "on
        the contrary" / "in contrast" included); CJK markers match a
        string prefix of the sentence, because Chinese tokenization here
        is per character.

        Args:
            sent: Sentence record.

        Returns:
            bool: True when the sentence opens with a contrast marker.
        """
        tokens = sent["tokens"]
        head = tokens[:_MAX_SENTENCE_LOOKAHEAD_TOKENS]
        for size in (1, 2, 3):
            if len(head) >= size and " ".join(head[:size]) \
                    in _CONTRAST_PHRASES:
                return True
        if head and head[0] in _CONTRAST_WORDS:
            return True
        text = sent["text"]
        return any(text.startswith(marker) for marker in _CONTRAST_CJK)

    @staticmethod
    def _same_opener(sent_a: dict, sent_b: dict) -> bool:
        """Report whether two sentences share a "subject-ish" opener.

        The opener is the first up-to-3 tokens of each sentence (the
        shorter sentence's length bounds the comparison), a crude
        subject proxy that deliberately includes function words so "the
        system does not ..." matches "the system does not ...".

        Args:
            sent_a: First sentence record.
            sent_b: Second sentence record.

        Returns:
            bool: True when the openers are token-identical.
        """
        limit = min(3, len(sent_a["tokens"]), len(sent_b["tokens"]))
        if limit == 0:
            return False
        return sent_a["tokens"][:limit] == sent_b["tokens"][:limit]

    # ------------------------------------------------------------------ #
    # Configuration
    # ------------------------------------------------------------------ #

    def _initialize_by_component_configer(
            self, doc_processor_configer: ComponentConfiger) \
            -> 'ContradictionSignalDetector':
        """Initialize and validate the detector from component configuration.

        Validation happens eagerly at load time: a detector silently
        misconfigured to record nothing (or to record tens of thousands
        of signals per document) would corrupt every downstream review
        queue, and a startup failure is far easier to notice.

        Args:
            doc_processor_configer: Configuration object.

        Returns:
            ContradictionSignalDetector: The initialized instance.

        Raises:
            ValueError: On an invalid parameter value or type.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        if hasattr(doc_processor_configer, "window_size") and \
                doc_processor_configer.window_size is not None:
            window = doc_processor_configer.window_size
            if isinstance(window, bool) or not isinstance(window, int):
                raise ValueError("window_size must be an integer")
            self.window_size = window
            if not 1 <= self.window_size <= _MAX_WINDOW_SIZE:
                raise ValueError(
                    "window_size must be in [1, "
                    f"{_MAX_WINDOW_SIZE}]")

        if hasattr(doc_processor_configer, "max_signals") and \
                doc_processor_configer.max_signals is not None:
            cap = doc_processor_configer.max_signals
            if isinstance(cap, bool) or not isinstance(cap, int):
                raise ValueError("max_signals must be an integer")
            self.max_signals = cap
            if not 1 <= self.max_signals <= 1000:
                raise ValueError("max_signals must be in [1, 1000]")

        if hasattr(doc_processor_configer, "max_shared_terms") and \
                doc_processor_configer.max_shared_terms is not None:
            limit = doc_processor_configer.max_shared_terms
            if isinstance(limit, bool) or not isinstance(limit, int):
                raise ValueError("max_shared_terms must be an integer")
            self.max_shared_terms = limit
            if not 1 <= self.max_shared_terms <= 20:
                raise ValueError("max_shared_terms must be in [1, 20]")

        for attr, label in (("signals_key", "signals_key"),
                            ("count_key", "count_key"),
                            ("risk_key", "risk_key")):
            value = getattr(doc_processor_configer, attr, None)
            if value is not None:
                if not isinstance(value, str):
                    raise ValueError(f"{label} must be a string")
                setattr(self, attr, value)
        return self


def _is_cjk(token: str) -> bool:
    """Report whether a token is a CJK character.

    Args:
        token: Lowercased token.

    Returns:
        bool: True when the token is a single CJK ideograph.
    """
    return len(token) == 1 and '\u4e00' <= token <= '\u9fff'


def _stem(token: str) -> str:
    """Reduce an ASCII word by trailing s / es / ed / ing suffixes.

    The heuristic strips at most one suffix and only when what remains
    keeps at least three letters: "ing" and "ed" unconditionally
    ("supports" -> "support" via the "s" rule, "exported" -> "export",
    "banning" -> "bann"), "es" only after s / x / z / ch / sh endings so
    that real English plurals collapse ("watches" -> "watch",
    "batches" -> "batch") while "files" falls through to the plain "s"
    rule and becomes "file". Doubled final consonants are NOT repaired
    ("shipping" -> "shipp" never matches "ships" -> "ship"), a
    documented trade-off that keeps the stemmer pure and predictable.

    Args:
        token: Lowercased ASCII word.

    Returns:
        str: The stemmed token (possibly unchanged).
    """
    for suffix in ("ing", "ed"):
        if token.endswith(suffix) and len(token) - len(suffix) >= 3:
            return token[:-len(suffix)]
    if token.endswith("es"):
        stem = token[:-2]
        if len(stem) >= 3 and stem.endswith(("s", "x", "z", "ch", "sh")):
            return stem
    if token.endswith("s") and not token.endswith(("ss", "us", "is")) \
            and len(token) - 1 >= 3:
        return token[:-1]
    return token
