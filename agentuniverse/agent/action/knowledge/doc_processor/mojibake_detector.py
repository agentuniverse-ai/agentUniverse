# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @FileName: mojibake_detector.py

import re
from typing import Dict, List

from pydantic import Field

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

# Characters CP1252 maps the C1 byte range (0x80-0x9F) onto, plus the five
# unmapped slots (0x81 0x8D 0x8F 0x90 0x9D) which pass through as controls.
# None of these codepoints occur in ordinary typed prose, so their presence
# right after a Latin-1 lead character is a CP1252-decoding signature.
_CP1252_C1_CHARS = frozenset(
    "\u0081\u008d\u008f\u0090\u009d"
    "\u20ac\u201a\u0192\u201e\u2026\u2020\u2021\u02c6\u2030"
    "\u0160\u2039\u0152\u017d\u2018\u2019\u201c\u201d\u2022"
    "\u2013\u2014\u02dc\u2122\u0161\u203a\u0153\u017e\u0178"
)


def _char_class(chars: str) -> str:
    """Render a set of characters as an escaped regex character class body."""
    return "".join(re.escape(ch) for ch in sorted(chars))


# Continuation bytes (0x80-0xBF) as they appear after a Latin-1 decode.
_LATIN1_CONT = "\u0080-\u00bf"
# Continuation bytes as they appear after a CP1252 decode: 0xA0-0xBF keep
# their Latin-1 identities while 0x80-0x9F become the C1-mapped characters.
_CP1252_CONT = "\u00a0-\u00bf" + _char_class(_CP1252_C1_CHARS)

# UTF-8 read as Latin-1: a valid multi-byte sequence re-emerges as a Latin-1
# lead character followed by continuation-range characters. Two-byte leads
# are C2-C3 (Â Ã), three-byte leads E0-EF (à-ï, covering â å ä ç ...),
# four-byte leads F0-F4 (ð-ô). Legitimate European words such as "São",
# "läuft" or "året" never match: the second character of the pattern must
# sit in the continuation range (Ã© matches, Ãa does not).
_RE_UTF8_AS_LATIN1 = re.compile(
    "[\u00c2\u00c3][" + _LATIN1_CONT + "]"
    "|[\u00e0-\u00ef][" + _LATIN1_CONT + "]{2}"
    "|[\u00f0-\u00f4][" + _LATIN1_CONT + "]{3}"
)

# UTF-8 read as CP1252: same structure, but at least one continuation
# character carries a CP1252-only identity (â€™ â€œ â€¦ Ã€ ...). Matches that
# overlap a Latin-1 pattern hit are credited to the Latin-1 signal only, so
# a sequence is never counted twice. A match is *strong* when at least two
# of its continuation characters carry C1-mapped identities (â€™, â€œ, ðŸ˜€);
# matches with only one such character (â€¦, and the é»… shape of French
# «café»… prose) are *weak* and need a second occurrence before the signal
# fires — the single-C1 shape is the one byte structure legitimate
# typography can also produce.
_RE_UTF8_AS_CP1252 = re.compile(
    "[\u00c2\u00c3][" + _CP1252_CONT + "]"
    "|[\u00e0-\u00ef][" + _CP1252_CONT + "]{2}"
    "|[\u00f0-\u00f4][" + _CP1252_CONT + "]{3}"
)

# Undecoded percent-encoding residue, e.g. %E4%B8%AD: consecutive %XX
# units forming a run of at least four characters. A lone %XX (three
# characters) is ignored, and runs inside URL tokens (whitespace-delimited
# tokens containing "://") never count at all — correctly escaped URLs
# such as https://example.com/wiki/%E4%B8%AD/%E6%96%87 are healthy text,
# not residue, no matter how many segments they escape.
_RE_PERCENT = re.compile("(?:%[0-9A-Fa-f]{2})+")
_RE_NONSPACE = re.compile(r"\S+")


def _percent_evidence(text: str):
    """Collect qualifying percent-encoding evidence from ``text``.

    Percent runs inside URL tokens are skipped entirely (see
    _RE_PERCENT); every remaining run of at least four characters
    contributes one hit per %XX unit, so a single contiguous blob such
    as %E5%8F%82%E6%95%B0 weighs as much evidence as the same bytes
    split across several runs.

    Args:
        text: Document text.

    Returns:
        tuple: (unit_count, run_spans) where unit_count is the number of
        qualifying %XX units and run_spans are the (start, end) spans of
        the qualifying runs, in positional order.
    """
    units = 0
    spans: List[tuple] = []
    for token in _RE_NONSPACE.finditer(text):
        if "://" in token.group():
            continue
        for match in _RE_PERCENT.finditer(token.group()):
            run = match.group()
            if len(run) >= 4:
                units += len(run) // 3
                spans.append((token.start() + match.start(),
                              token.start() + match.end()))
    return units, spans

# Undecoded HTML entity residue: numeric character references such as
# &#x4E2D; / &#20013; always count as residue, while a single named entity
# (&amp;) is too common in legitimate markup — only double-escaping runs
# such as &amp;amp; or &amp;#x4E2D; do.
_RE_HTML_NUMERIC = re.compile("&#(?:[0-9]{1,8}|[xX][0-9A-Fa-f]{1,6});")
_RE_HTML_NAMED_RUN = re.compile(
    "&(?:amp|lt|gt|quot|apos);"
    "(?:(?:amp|lt|gt|quot|apos)"
    "|#(?:[0-9]{1,8}|[xX][0-9A-Fa-f]{1,6}));+")

# Detector signals in canonical output order.
_SIGNAL_KINDS = (
    "replacement_char",
    "utf8_as_latin1",
    "utf8_as_cp1252",
    "percent_encoding",
    "html_entity",
)

# Weight each signal's hits contribute to the composite score before
# per-1000-character normalization. A replacement character is the loudest
# evidence (the decoder already gave up); percent and entity residue are
# weaker because URLs and markup leak into healthy corpora.
_SIGNAL_WEIGHTS = {
    "replacement_char": 2.0,
    "utf8_as_latin1": 1.0,
    "utf8_as_cp1252": 1.0,
    "percent_encoding": 0.5,
    "html_entity": 0.25,
}

# Minimum hits before a signal is recorded at all. The two byte-structure
# signals require two hits: one stray bigram can appear in legitimate
# European text or in text *about* encodings, while genuine corruption
# never stops at a single occurrence. The CP1252 signal admits a single
# hit only when that hit is strong (see _RE_UTF8_AS_CP1252); weak hits
# need this many occurrences.
_SIGNAL_MIN_HITS = {
    "replacement_char": 1,
    "utf8_as_latin1": 2,
    "utf8_as_cp1252": 1,
    "percent_encoding": 2,
    "html_entity": 2,
}
_CP1252_WEAK_MIN_HITS = 2

_VERDICTS = ("clean", "suspect", "corrupted")


class MojibakeDetector(DocProcessor):
    """Flag encoding-corrupted text (mojibake) into document metadata.

    Documents gathered by crawlers and file readers are routinely decoded
    with the wrong codec: UTF-8 bytes read as Latin-1 or CP1252 turn 中文
    into "ä¸­æ" and the curly apostrophe of "don’t" into "donâ€™t", failed
    byte sequences collapse into U+FFFD replacement characters, and
    sometimes text is never decoded at all and arrives full of %E4%B8%AD
    percent escapes or &#x4E2D; HTML entities. Feeding such documents into
    a knowledge base pollutes embeddings and retrieval with garbage tokens.
    This processor examines every document with five independent,
    purely-structural signals:

    1. replacement_char — U+FFFD replacement characters, the residue of a
       decoder that already gave up;
    2. utf8_as_latin1 — the exact Latin-1 rendering of UTF-8 multi-byte
       sequences: a lead character from Â/Ã (2-byte), à-ï (3-byte) or ð-ô
       (4-byte) followed by continuation-range characters (Ã©, Ã¼, the
       Latin-1 form of 中文, ...);
    3. utf8_as_cp1252 — the same structure where a continuation character
       carries a CP1252-only identity (â€™ â€œ â€¦ Ã€ ...); a single hit
       qualifies only when it is strong (at least two C1-mapped
       continuations, like â€™ or ðŸ˜€), while weaker shapes need a second
       occurrence;
    4. percent_encoding — percent-escape runs of at least four characters
       (%E4%B8%AD) outside URLs: runs inside URL tokens never count,
       because correctly escaped URLs are healthy text;
    5. html_entity — numeric character references (&#x4E2D; &#20013;) and
       repeated named-entity escaping (&amp;amp;).

    The detector is deliberately conservative about legitimate European
    text: "São", "läuft" and "året" contain ã/ä/å lawfully, but the
    byte-structure patterns demand that the *following* character sit in
    the continuation range (Ã© matches, Ãa does not), and the utf8_as_latin1
    signal additionally requires at least two hits before it is recorded,
    so isolated ambiguous bigrams never flag a document.

    Each recorded signal contributes a finding {kind, count, samples} with
    the first three matches as snippets (ten characters of context each)
    and their spans. Findings are aggregated into composite metadata:

    - metadata[score_key] = mojibake_score: the weighted hit count
      normalized per 1000 characters, rounded to two decimals — a rate
      estimate, so one corrupted apostrophe in a seven-character string is
      as alarming as a hundred in a long article;
    - metadata[verdict_key] = mojibake_verdict: "clean" when the score is
      below clean_below, "corrupted" when above corrupted_above, and
      "suspect" in between;
    - metadata[findings_key] = the finding list, empty for clean
      documents.

    The processor never modifies text, ids or other metadata fields — it
    is an analysis pass, complementary to TextNormalizer, which repairs
    unicode form problems but cannot tell corrupted text from healthy
    text. By default every document passes through stamped (filter mode
    off) so ingestion pipelines can quarantine or route on the verdict;
    with drop_corrupted enabled, documents whose verdict is "corrupted"
    are removed from the returned batch (the dropped document objects keep
    their stamps so callers holding the original list can see why).
    Everything is pure stdlib, deterministic and offline.

    Attributes:
        clean_below: Scores below this threshold yield verdict "clean".
        corrupted_above: Scores above this threshold yield verdict
            "corrupted"; scores in between yield "suspect".
        drop_corrupted: When true, documents whose verdict is "corrupted"
            are dropped from the output batch; when false (default) every
            document is stamped and kept.
        score_key: Metadata key the numeric score is written to; an empty
            value disables stamping.
        verdict_key: Metadata key the verdict string is written to; an
            empty value disables stamping.
        findings_key: Metadata key the finding list is written to; an
            empty value disables stamping.
        disabled_signals: Signal kinds to exclude from analysis, e.g.
            ["percent_encoding"] for URL-heavy corpora where percent
            residue is expected; unknown kinds are rejected at load time.
    """

    clean_below: float = 0.5
    corrupted_above: float = 5.0
    drop_corrupted: bool = False
    score_key: str = "mojibake_score"
    verdict_key: str = "mojibake_verdict"
    findings_key: str = "mojibake_findings"
    disabled_signals: List[str] = Field(default_factory=list)

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Stamp mojibake analysis into every document's metadata.

        Args:
            origin_docs: Documents to analyze, in batch order.
            query: Query object (unused; detection depends only on the
                documents' own text).

        Returns:
            List[Document]: All documents in original order, each stamped
            with score, verdict and findings; when drop_corrupted is
            enabled, documents whose verdict is "corrupted" are excluded
            (their original objects still carry the stamps).
        """
        if not origin_docs:
            return []

        kept: List[Document] = []
        for doc in origin_docs:
            findings, score, verdict = self._analyze(doc.text or "")
            self._stamp(doc, self.score_key, score)
            self._stamp(doc, self.verdict_key, verdict)
            self._stamp(doc, self.findings_key, findings)
            if self.drop_corrupted and verdict == "corrupted":
                continue
            kept.append(doc)
        return kept

    # ------------------------------------------------------------------ #
    # Analysis helpers
    # ------------------------------------------------------------------ #

    def _analyze(self, text: str):
        """Run every enabled signal over one text and aggregate results.

        Args:
            text: Document text (None treated as empty).

        Returns:
            tuple: (findings, score, verdict) where findings is the
            ordered list of {kind, count, samples} dicts, score is the
            rounded weighted hit count per 1000 characters and verdict is
            one of "clean" / "suspect" / "corrupted".
        """
        text = text or ""
        counts = self._signal_counts(text)
        findings = self._build_findings(text, counts)

        raw = sum(_SIGNAL_WEIGHTS[kind] * count
                  for kind, count in counts.items()
                  if count >= _SIGNAL_MIN_HITS[kind])
        length = max(len(text), 1)
        score = round(raw * 1000.0 / length, 2)
        return findings, score, self._verdict(score)

    def _signal_counts(self, text: str) -> Dict[str, int]:
        """Count qualifying hits for every enabled signal.

        Args:
            text: Document text.

        Returns:
            Dict[str, int]: Hits per signal kind, including signals below
            their minimum-hit threshold (filtered later, so callers of
            this helper see raw evidence). The one exception is
            utf8_as_cp1252: a lone weak hit is already folded to zero
            here, mirroring how a lone Latin-1 bigram is filtered later.
        """
        disabled = set(self.disabled_signals or [])

        # Latin-1 hits first: their spans suppress overlapping CP1252
        # matches so one corrupted sequence is never counted twice.
        latin1_spans: List[tuple] = []
        if "utf8_as_latin1" not in disabled:
            latin1_spans = [m.span() for m in _RE_UTF8_AS_LATIN1.finditer(text)]

        cp1252_count = 0
        if "utf8_as_cp1252" not in disabled:
            strong = False
            for match in _RE_UTF8_AS_CP1252.finditer(text):
                start, end = match.span()
                if any(start < le and ls < end
                       for ls, le in latin1_spans):
                    continue
                cp1252_count += 1
                if sum(1 for ch in match.group()
                       if ch in _CP1252_C1_CHARS) >= 2:
                    strong = True
            # Weak evidence (fewer than two C1-mapped continuations) is
            # folded to zero unless a second occurrence backs it up: the
            # single-C1 shape also arises from legitimate typography
            # (é»… in French «café»… prose), exactly like the stray
            # bigrams the Latin-1 signal already guards against.
            if not strong and cp1252_count < _CP1252_WEAK_MIN_HITS:
                cp1252_count = 0

        percent_count = 0
        if "percent_encoding" not in disabled:
            percent_count = _percent_evidence(text)[0]

        html_count = 0
        if "html_entity" not in disabled:
            html_count = (len(_RE_HTML_NUMERIC.findall(text))
                          + len(_RE_HTML_NAMED_RUN.findall(text)))

        replacement_count = (0 if "replacement_char" in disabled
                             else text.count("\ufffd"))

        return {
            "replacement_char": replacement_count,
            "utf8_as_latin1": len(latin1_spans),
            "utf8_as_cp1252": cp1252_count,
            "percent_encoding": percent_count,
            "html_entity": html_count,
        }

    def _build_findings(self, text: str,
                        counts: Dict[str, int]) -> List[dict]:
        """Assemble the per-signal finding list from raw hit counts.

        A signal appears in the list only when its hit count reaches the
        signal's minimum; samples carry ten characters of context around
        each of the first three matches.

        Args:
            text: Document text.
            counts: Raw hits per signal kind from _signal_counts.

        Returns:
            List[dict]: Findings {kind, count, samples} in canonical
            signal order; empty when nothing qualified.
        """
        findings: List[dict] = []
        for kind in _SIGNAL_KINDS:
            count = counts.get(kind, 0)
            if count < _SIGNAL_MIN_HITS[kind]:
                continue
            findings.append({
                "kind": kind,
                "count": count,
                "samples": self._samples(text, kind),
            })
        return findings

    def _samples(self, text: str, kind: str, limit: int = 3) -> List[dict]:
        """Collect the first matches of one signal as evidence snippets.

        Args:
            text: Document text.
            kind: Signal kind whose matches are sampled.
            limit: Maximum number of samples (default 3).

        Returns:
            List[dict]: Samples {snippet, start, end}; the snippet carries
            ten characters of context on each side of the match, the span
            marks the match itself.
        """
        if kind == "replacement_char":
            matches = [(i, i + 1) for i, ch in enumerate(text)
                       if ch == "\ufffd"]
        elif kind == "utf8_as_latin1":
            matches = [m.span() for m in _RE_UTF8_AS_LATIN1.finditer(text)]
        elif kind == "utf8_as_cp1252":
            latin1_spans = [m.span() for m in
                            _RE_UTF8_AS_LATIN1.finditer(text)]
            matches = [m.span() for m in _RE_UTF8_AS_CP1252.finditer(text)
                       if not any(m.start() < le and ls < m.end()
                                  for ls, le in latin1_spans)]
        elif kind == "percent_encoding":
            matches = _percent_evidence(text)[1]
        else:
            matches = ([m.span() for m in _RE_HTML_NUMERIC.finditer(text)]
                       + [m.span() for m in
                          _RE_HTML_NAMED_RUN.finditer(text)])
            matches.sort()

        samples = []
        for start, end in matches[:limit]:
            samples.append({
                "snippet": text[max(0, start - 10):min(len(text), end + 10)],
                "start": start,
                "end": end,
            })
        return samples

    def _verdict(self, score: float) -> str:
        """Map a score to its verdict under the configured thresholds.

        Args:
            score: Weighted hit count per 1000 characters.

        Returns:
            str: "clean" below clean_below, "corrupted" above
            corrupted_above, "suspect" in between (boundaries inclusive).
        """
        if score < self.clean_below:
            return "clean"
        if score > self.corrupted_above:
            return "corrupted"
        return "suspect"

    def _stamp(self, doc: Document, key: str, value) -> None:
        """Write one entry into document metadata via a copied mapping.

        The metadata mapping is copied before mutation so a mapping shared
        with other pipeline stages never observes surprising in-place
        edits; an empty key disables that single stamp.

        Args:
            doc: Document to stamp.
            key: Metadata key; empty disables stamping.
            value: Metadata value.
        """
        if not key:
            return
        meta = dict(doc.metadata or {})
        meta[key] = value
        doc.metadata = meta

    # ------------------------------------------------------------------ #
    # Configuration
    # ------------------------------------------------------------------ #

    def _initialize_by_component_configer(
            self, doc_processor_configer: ComponentConfiger) \
            -> 'MojibakeDetector':
        """Initialize and validate the detector from component configuration.

        Validation happens eagerly at load time: a misconfigured detector
        that silently stamped wrong verdicts would be far harder to notice
        in production than a startup failure.

        Args:
            doc_processor_configer: Configuration object.

        Returns:
            MojibakeDetector: The initialized instance.

        Raises:
            ValueError: On an invalid combination of parameter values.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        if hasattr(doc_processor_configer, "clean_below") and \
                doc_processor_configer.clean_below is not None:
            value = doc_processor_configer.clean_below
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError("clean_below must be a number")
            self.clean_below = float(value)
            if self.clean_below < 0:
                raise ValueError("clean_below must be >= 0")

        if hasattr(doc_processor_configer, "corrupted_above") and \
                doc_processor_configer.corrupted_above is not None:
            value = doc_processor_configer.corrupted_above
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError("corrupted_above must be a number")
            self.corrupted_above = float(value)

        if self.corrupted_above <= self.clean_below:
            raise ValueError("corrupted_above must be greater than "
                             "clean_below")

        if hasattr(doc_processor_configer, "drop_corrupted") and \
                doc_processor_configer.drop_corrupted is not None:
            self.drop_corrupted = bool(doc_processor_configer.drop_corrupted)

        for attr in ("score_key", "verdict_key", "findings_key"):
            if hasattr(doc_processor_configer, attr) and \
                    getattr(doc_processor_configer, attr) is not None:
                key = getattr(doc_processor_configer, attr)
                if not isinstance(key, str):
                    raise ValueError(f"{attr} must be a string")
                setattr(self, attr, key)

        if hasattr(doc_processor_configer, "disabled_signals") and \
                doc_processor_configer.disabled_signals is not None:
            signals = doc_processor_configer.disabled_signals
            if not isinstance(signals, (list, tuple)):
                raise ValueError("disabled_signals must be a list")
            for kind in signals:
                if not isinstance(kind, str) or kind not in _SIGNAL_KINDS:
                    raise ValueError(
                        "disabled_signals entries must be one of "
                        f"{', '.join(_SIGNAL_KINDS)}; got {kind!r}")
            self.disabled_signals = list(signals)

        return self
