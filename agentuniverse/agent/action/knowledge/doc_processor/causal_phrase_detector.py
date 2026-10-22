# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @FileName: causal_phrase_detector.py

import re
from typing import List, Tuple

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

# --------------------------------------------------------------------- #
# Sentence segmentation constants (conservative family, same splitter
# semantics as SentenceLengthFilter / DiscourseConnectiveAnalyzer)
# --------------------------------------------------------------------- #

# Characters that terminate a sentence: Latin and CJK full stops,
# exclamation marks and question marks.
_TERMINAL_CHARS = ".!?。！？"

# Closing quotes / brackets swallowed into the finished sentence right
# after its terminal punctuation, so spans like '"Are you sure?"' stay whole.
_CLOSING_CHARS = "\"'”’」』》）】)]"

# English words that, when the only thing following them is a dot, do NOT
# end a sentence ("Dr. Smith asked..."). Lowercase; matched on the alpha run
# immediately before the dot. Single-letter initials ("J.", "e.g.") are
# handled separately by length, which is why they are absent here.
_ABBREVIATIONS = frozenset((
    "dr", "mr", "mrs", "ms", "prof", "sr", "jr", "st", "mt", "rev", "hon",
    "gen", "col", "capt", "lt", "sgt", "vs", "etc", "inc", "ltd", "co",
    "corp", "dept", "univ", "assn", "bros", "no", "nos", "vol", "vols",
    "fig", "figs", "eq", "approx", "est", "cf", "al", "ca", "ed", "eds",
    "pp", "ch", "sec", "para", "ph", "md", "ba", "ma", "msc", "jan", "feb",
    "mar", "apr", "jun", "jul", "aug", "sep", "sept", "oct", "nov", "dec",
))

# --------------------------------------------------------------------- #
# Clause / span constants
# --------------------------------------------------------------------- #

# Characters that split a sentence into clauses. Both scripts share one
# set: Latin commas / semicolons and their full-width CJK counterparts
# (comma, enumeration comma, semicolon).
_CLAUSE_SEPARATORS = ",;，、；"

# Punctuation and whitespace trimmed off the edges of extracted cause /
# effect spans. Terminal punctuation is included; quotes and dashes are
# deliberately NOT stripped, so spans like «the "stop" clause» keep their
# quoting.
_EDGE_STRIP = " \t\r\n,;:、，；：.。!！?？…"

# One leading English coordinating conjunction (with its whitespace) is
# dropped from an extracted span, so the cause of "A failed, and as a
# result, B" is "A failed" rather than "and".
_LEAD_CONJ_RE = re.compile(r"^(?:and|but|or|yet|so|then|thus|also)\s+",
                           re.IGNORECASE)

# The same conjunction words, used to recognize clause "husks" — clauses
# that are empty or nothing but a dangling conjunction ("..., and as a
# result, ...") and should be hopped when locating a connective's true
# antecedent clause.
_CONJUNCTION_WORDS = frozenset((
    "and", "but", "or", "yet", "so", "then", "thus", "also",
))

# Auxiliary / modal verbs used by the temporal-since guard: a "since"
# followed by a clause containing one of these reads as causal ("since
# inflation had eased") rather than as a bare date/noun phrase ("since
# Monday").
_AUXILIARIES = frozenset((
    "is", "are", "was", "were", "be", "been", "being", "am", "has", "have",
    "had", "do", "does", "did", "will", "would", "shall", "should", "can",
    "could", "may", "might", "must",
))

# Determiners that, directly before "results in" / "causes", signal a noun
# phrase rather than a causal verb ("the results in the appendix", "a cause
# for concern") and suppress the match.
_DETERMINERS = frozenset((
    "the", "a", "an", "this", "that", "these", "those", "his", "her",
    "its", "their", "our", "your", "my",
))

# Words that, right after a comma+"so", signal a non-causal "so"
# (purpose clause or intensifier) and suppress the match.
_SO_BLOCKERS = frozenset((
    "that", "much", "many", "few", "little", "less", "more", "as", "long",
    "far", "to", "such",
))

# --------------------------------------------------------------------- #
# Marker patterns (pure regex, no external dependencies)
# --------------------------------------------------------------------- #

# English prepositional causal markers: "because of X, Y",
# "due to X, Y", "as a result of X, Y".
_EN_PREP_RE = re.compile(r"(?<!\w)(because of|due to|as a result of)(?!\w)",
                         re.IGNORECASE)

# "X because Y" (reverse); the lookahead keeps "because of" for the
# prepositional pattern above.
_EN_BECAUSE_RE = re.compile(r"(?<!\w)because\b(?!\s+of\b)", re.IGNORECASE)

# "Y since X" (reverse, guarded by the temporal heuristic).
_EN_SINCE_RE = re.compile(r"(?<!\w)since\b", re.IGNORECASE)

# "X, so Y" — the comma is required by the extractor, not the regex.
_EN_SO_RE = re.compile(r"(?<!\w)so\b", re.IGNORECASE)

# Sentence-internal connectives "A, therefore B" / "A, and as a result, B".
# The inner lookahead keeps "as a result of X, Y" for the prepositional
# pattern above.
_EN_CONNECTIVE_RE = re.compile(
    r"(?<!\w)(as a result(?!\s+of\b)|therefore)(?!\w)", re.IGNORECASE)

# "X leads to Y" and its inflections.
_EN_LEADS_RE = re.compile(r"(?<!\w)(?:leads? to|led to|leading to)(?!\w)",
                          re.IGNORECASE)

# "X results in Y" and its inflections (noun-phrase guarded).
_EN_RESULTS_RE = re.compile(
    r"(?<!\w)(?:results? in|resulted in|resulting in)(?!\w)", re.IGNORECASE)

# "X causes Y" and its inflections (noun-phrase guarded). "caused by" is
# delegated to the dedicated reverse pattern below.
_EN_CAUSE_RE = re.compile(r"(?<!\w)(causes|caused|cause)(?!\w)",
                          re.IGNORECASE)

# "X was caused by Y" (reverse).
_EN_CAUSED_BY_RE = re.compile(r"(?<!\w)caused by(?!\w)", re.IGNORECASE)

# Chinese causal verb markers; an optional aspect particle 了 may attach
# to the verb and is consumed with it ("高温导致了变形").
_ZH_VERB_RE = re.compile(r"(?:导致|造成|引起|使得)了?")

# Chinese paired / prepositional / connective markers (plain substrings —
# the correct semantics for an unsegmented script).
_ZH_BECAUSE = "因为"
_ZH_SO = "所以"
_ZH_DUE = "由于"
_ZH_THEREFORE = "因此"

# Canonical marker label for the Chinese paired pattern.
_ZH_PAIR_MARKER = "因为...所以"

# Quote characters recognised by the quote-immunity mask. Straight single
# quotes / apostrophes between two alphanumeric characters ("don't") are
# treated as contractions, not quotes.
_QUOTE_OPENS = {"“", "「", "『"}
_QUOTE_CLOSES = {"”", "」", "』"}


def _quote_mask(text: str) -> bytes:
    """Mark which character positions of `text` sit inside quotes.

    A straight double quote toggles the double-quote state anywhere; a
    straight or curly apostrophe toggles the single-quote state only when
    it is not sandwiched between two alphanumeric characters, so the
    apostrophe in "don't" / "don’t" never opens a quote region. Curly and
    CJK corner quotes pair with their own closers. A character is masked
    when any quote level is currently open.

    Args:
        text: Full document text.

    Returns:
        bytes: One 0/1 flag per character; 1 means "inside a quote".
    """
    n = len(text)
    mask = bytearray(n)
    double = single = curly = corner = white = False
    for i, ch in enumerate(text):
        prev_alnum = i > 0 and text[i - 1].isalnum()
        next_alnum = i + 1 < n and text[i + 1].isalnum()
        if ch == '"':
            double = not double
        elif ch in _QUOTE_OPENS:
            if ch == "“":
                curly = True
            elif ch == "「":
                corner = True
            else:
                white = True
        elif ch in _QUOTE_CLOSES:
            if ch == "”":
                curly = False
            elif ch == "」":
                corner = False
            else:
                white = False
        elif ch in ("'", "‘", "’"):
            if not (prev_alnum and next_alnum):
                single = not single
        if double or single or curly or corner or white:
            mask[i] = 1
    return bytes(mask)


def _clean_span(text: str) -> str:
    """Trim a raw clause into a cause/effect span.

    Edge whitespace and punctuation are stripped, then one leading English
    coordinating conjunction ("and", "so", ...) is dropped so conjunction
    husks left by clause splitting do not leak into spans.

    Args:
        text: Raw clause text.

    Returns:
        str: The cleaned span; empty when nothing substantive remains.
    """
    value = text.strip(_EDGE_STRIP)
    match = _LEAD_CONJ_RE.match(value)
    if match:
        value = value[match.end():].strip(_EDGE_STRIP)
    return value


def _verbish(clause: str) -> bool:
    """Report whether an English clause carries a verb-ish token.

    The documented heuristic behind the temporal-since guard: a token
    counts as verb-ish when it is an auxiliary / modal ("had", "will")
    or a word of length >= 4 ending in "ed" or "ing" ("eased",
    "collapsing"; short words like "red" or "bed" are excluded by the
    length floor). "since Monday" / "since 2019" have no such token and
    are treated as temporal references.

    Args:
        clause: The text following "since".

    Returns:
        bool: True when the clause looks like a finite clause.
    """
    for token in re.findall(r"[A-Za-z]+", clause.lower()):
        if token in _AUXILIARIES:
            return True
        if len(token) >= 4 and token.endswith(("ed", "ing")):
            return True
    return False


def _next_word(sentence: str, pos: int) -> str:
    """Return the English word starting at or after `pos`, lowercased.

    Args:
        sentence: Sentence text.
        pos: Offset to scan from.

    Returns:
        str: The next alphabetic run, or "" when none follows.
    """
    i = pos
    while i < len(sentence) and sentence[i].isspace():
        i += 1
    match = re.match(r"[A-Za-z]+", sentence[i:])
    return match.group(0).lower() if match else ""


def _prev_word(sentence: str, pos: int) -> str:
    """Return the English word ending just before `pos`, lowercased.

    Args:
        sentence: Sentence text.
        pos: Offset to scan backwards from.

    Returns:
        str: The preceding alphabetic run, or "" when none precedes.
    """
    i = pos - 1
    while i >= 0 and sentence[i].isspace():
        i -= 1
    j = i
    while j >= 0 and sentence[j].isalpha():
        j -= 1
    return sentence[j + 1:i + 1].lower() if i > j else ""


def _rsep(sentence: str, pos: int) -> int:
    """Index of the last clause separator before `pos`, or -1.

    Args:
        sentence: Sentence text.
        pos: Exclusive upper bound of the scan.

    Returns:
        int: Separator index in [-1, pos).
    """
    for i in range(pos - 1, -1, -1):
        if sentence[i] in _CLAUSE_SEPARATORS:
            return i
    return -1


def _fsep(sentence: str, pos: int) -> int:
    """Index of the first clause separator at/after `pos`, or -1.

    Args:
        sentence: Sentence text.
        pos: Inclusive lower bound of the scan.

    Returns:
        int: Separator index in [pos, len(sentence)).
    """
    for i in range(pos, len(sentence)):
        if sentence[i] in _CLAUSE_SEPARATORS:
            return i
    return -1


def _next_clause(sentence: str, pos: int) -> Tuple[int, int]:
    """Bounds of the clause starting at `pos`.

    The clause runs to the next separator (exclusive) or to the end of
    the sentence.

    Args:
        sentence: Sentence text.
        pos: Offset the clause starts at.

    Returns:
        Tuple[int, int]: (start, end) with start == pos.
    """
    sep = _fsep(sentence, pos)
    return pos, (sep if sep >= 0 else len(sentence))


def _is_husk(clause: str) -> bool:
    """Report whether a clause is empty or only a dangling conjunction.

    Args:
        clause: Raw clause text.

    Returns:
        bool: True when nothing substantive remains after cleaning —
        the empty string or conjunction-only tokens like "and".
    """
    tokens = _clean_span(clause).split()
    return (not tokens or
            all(token.lower() in _CONJUNCTION_WORDS for token in tokens))


def _prev_clause(sentence: str, pos: int, extend: bool) -> Tuple[int, int]:
    """Bounds of the clause immediately before `pos`.

    With `extend`, a clause that is empty or only a dangling conjunction
    ("A failed, and as a result, B" — the clause before "as a result" is
    just "and"; "the deadline, because ..." — the clause between the
    comma and the marker is just a space) hops one separator further
    back, up to the sentence start, so the marker's true antecedent
    clause is found.

    Args:
        sentence: Sentence text.
        pos: Offset the clause ends at (usually a marker start).
        extend: Whether to hop back over empty / conjunction-only
            clauses.

    Returns:
        Tuple[int, int]: (start, end).
    """
    start = _rsep(sentence, pos) + 1
    end = pos
    while extend and start > 0 and _is_husk(sentence[start:end]):
        end = start - 1
        start = _rsep(sentence, end) + 1
    return start, end


class CausalPhraseDetector(DocProcessor):
    """Extract explicitly stated causal relations into document metadata.

    Risk reports and analysis notes argue in causes and effects: "the
    storm caused the outage", "因为预算不足所以项目延期". For a knowledge
    base these statements are far more useful as structured pairs than as
    plain text — a risk KB can surface "what leads to what" without an
    LLM pass at query time. This pre-processing component scans each
    document for a fixed table of explicit causal markers in English and
    Chinese, splits the surrounding clauses into cause and effect spans,
    and stamps the collected relations into document metadata. It never
    drops or rewrites documents; it is an analyzer, not a filter.

    It complements ``DiscourseConnectiveAnalyzer``: that component counts
    connective occurrences per rhetorical category, while this one
    extracts the actual RELATION SPANS (cause text, effect text, marker,
    matched region). Detection is entirely regex- and rule-based — pure
    Python, deterministic, offline, no model calls, no dependencies.

    Within each sentence (conservative splitter of the SentenceLengthFilter
    family: terminal ``. ! ? 。 ！ ？`` with abbreviation, initial, decimal
    and ellipsis guards) every marker match becomes a candidate relation:

    ============  ===========================  ====================  ========
    Language      Pattern (X = cause)          Extraction            Match
    ============  ===========================  ====================  ========
    EN            X because Y                  cause=Y effect=X      reverse
    EN            Because X, Y                 cause=X effect=Y      forward
    EN            because of X, Y              cause=X effect=Y      forward
    EN            due to X, Y                  cause=X effect=Y      forward
    EN            as a result of X, Y          cause=X effect=Y      forward
    EN            X, so Y                      cause=X effect=Y      forward
    EN            Y since X (guarded)          cause=X effect=Y      reverse
    EN            X leads to / led to /        cause=X effect=Y      forward
                  leading to Y
    EN            X results in / resulted in / cause=X effect=Y      forward
                  resulting in Y
    EN            X causes / cause / caused Y  cause=X effect=Y      forward
    EN            X (was) caused by Y          cause=Y effect=X      reverse
    EN            A, therefore B /             cause=A effect=B      forward
                  A, (and) as a result, B
    ZH            因为X所以Y (split at 所以)   cause=X effect=Y      forward
    ZH            由于X，Y                     cause=X effect=Y      forward
    ZH            X导致(了)Y                   cause=X effect=Y      forward
    ZH            X造成Y                       cause=X effect=Y      forward
    ZH            X引起Y                       cause=X effect=Y      forward
    ZH            X使得Y                       cause=X effect=Y      forward
    ZH            A，因此B                     cause=A effect=B      forward
    ============  ===========================  ====================  ========

    ``direction`` records the textual arrangement inside the matched
    region: "forward" when the cause clause precedes the effect clause
    ("X leads to Y"), "reverse" when the marker's left clause is the
    effect ("X because Y"). The ``cause`` / ``effect`` fields themselves
    are always normalized — cause first. Cause and effect spans are the
    comma-delimited clauses adjacent to the marker, trimmed of edge
    punctuation and one leading coordinating conjunction, and capped at
    ``span_char_limit`` characters (default 200) with per-hit
    ``cause_truncated`` / ``effect_truncated`` flags when longer.

    Guards, all deliberate precision-over-recall heuristics:

    * temporal "since" — "since" only matches when the clause after it
      contains a verb-ish token (an auxiliary/modal, or a word of length
      >= 4 ending in "ed"/"ing"). "Offline since 2019" has no verb and is
      skipped; clauses that do carry a finite verb ("since demand had
      collapsed") are treated as causal, accepting that purely temporal
      verb-bearing clauses remain a known limitation;
    * noun phrases — "the cause of", "the result of": a bare
      "cause(s)/(caused)" followed by "of"/"by" is skipped, and
      "results in"/"causes" directly preceded by a determiner ("the
      results in the appendix") is skipped as a noun reading;
    * purpose "so" — ", so" is skipped when the next word is "that",
      "much", "many" and a few other intensifier/purpose heads;
    * quote immunity — a marker inside a quoted region (straight or curly
      quotes, CJK corner quotes) never fires, so reported speech and
      citations are not mined; apostrophes inside contractions ("didn't")
      do not open quotes.

    Candidates whose cause or effect clause cleans to nothing are
    dropped (e.g. sentence-initial "Therefore, ..." has no antecedent
    within its sentence — cross-sentence anaphora is out of scope). When
    two candidates' regions overlap in one sentence, the earlier-starting
    one wins and the longer region wins ties, so "A because B, so C"
    yields exactly one relation (the "so" reading). Per document the
    metadata gains:

    * ``metadata[relations_key]`` (default ``causal_relations``) — the
      list of relation dicts ``{cause, effect, marker, span, direction,
      cause_truncated, effect_truncated}`` in document order, capped at
      ``max_relations`` (default 50) entries;
    * ``metadata[count_key]`` (default ``causal_count``) — the number of
      stamped relations (i.e. after the cap);
    * ``metadata[density_key]`` (default ``causal_density``) — stamped
      relations per 100 sentences, rounded to two decimals (0.0 for a
      document without sentences).

    An empty key string disables that individual stamp. Metadata mappings
    are copied before mutation; text, id and other metadata fields are
    never modified.

    Attributes:
        max_relations: Maximum number of relations stamped per document;
            extra detections are dropped. Integer in [1, 10000].
        span_char_limit: Maximum length of a cause or effect span; longer
            spans are cut and flagged truncated. Integer in [1, 10000].
        relations_key: Metadata key for the relation list; '' disables.
        count_key: Metadata key for the relation count; '' disables.
        density_key: Metadata key for relations per 100 sentences;
            '' disables.
    """

    max_relations: int = 50
    span_char_limit: int = 200
    relations_key: str = "causal_relations"
    count_key: str = "causal_count"
    density_key: str = "causal_density"

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Stamp causal relations into every document's metadata.

        Args:
            origin_docs: Documents to analyze, in batch order.
            query: Query object (unused; detection depends only on the
                documents' own text).

        Returns:
            List[Document]: The same document objects, all kept, each
            stamped with its causal relations, count and density.
        """
        for doc in origin_docs:
            relations, sentence_count = self._analyze(doc.text or "")
            capped = relations[:self.max_relations]
            if self.relations_key:
                self._stamp(doc, self.relations_key, capped)
            if self.count_key:
                self._stamp(doc, self.count_key, len(capped))
            if self.density_key:
                density = (round(len(capped) / sentence_count * 100, 2)
                           if sentence_count else 0.0)
                self._stamp(doc, self.density_key, density)
        return list(origin_docs)

    # ------------------------------------------------------------------ #
    # Detection
    # ------------------------------------------------------------------ #

    def _analyze(self, text: str) -> Tuple[List[dict], int]:
        """Extract every causal relation stated in one text.

        Args:
            text: Raw document text.

        Returns:
            Tuple[List[dict], int]: The relation dicts in document order
            and the number of sentences detected.
        """
        spans = self._sentence_spans(text)
        mask = _quote_mask(text)
        hits: List[dict] = []
        for start, end in spans:
            sentence = text[start:end]
            for hit in self._sentence_hits(sentence, start, mask):
                hits.append(hit)
        return hits, len(spans)

    def _sentence_hits(self, sentence: str, base: int,
                       mask: bytes) -> List[dict]:
        """Collect the surviving causal relations of one sentence.

        All pattern candidates are gathered, finalized (spans cleaned and
        capped) and then swept: sorted by (region start, longer region
        first, pattern order) and kept greedily while disjoint, so nested
        or crossing matches resolve deterministically.

        Args:
            sentence: One sentence's text.
            base: Offset of the sentence within the document, used for
                the quote-immunity lookup.
            mask: Per-character quote mask of the whole document.

        Returns:
            List[dict]: The kept relation dicts in textual order.
        """
        candidates = []
        for scanner in self._scanners():
            for candidate in scanner(sentence, base, mask):
                candidates.append(candidate)

        finalized = []
        for region_start, region_end, order, marker, direction, \
                cause_raw, effect_raw in candidates:
            # A region reaching the sentence end swallows its terminal
            # punctuation run; back it off so the span is content only.
            while region_end > region_start and \
                    sentence[region_end - 1] in _TERMINAL_CHARS:
                region_end -= 1
            cause = _clean_span(cause_raw)
            effect = _clean_span(effect_raw)
            if not cause or not effect:
                continue
            cause_truncated = effect_truncated = False
            if len(cause) > self.span_char_limit:
                cause, cause_truncated = cause[:self.span_char_limit], True
            if len(effect) > self.span_char_limit:
                effect, effect_truncated = effect[:self.span_char_limit], True
            finalized.append((region_start, region_end, order, marker,
                              direction, cause, effect, cause_truncated,
                              effect_truncated))

        finalized.sort(key=lambda c: (c[0], c[0] - c[1], c[2]))
        kept = []
        last_end = -1
        for cand in finalized:
            if cand[0] < last_end:
                continue
            last_end = cand[1]
            kept.append({
                "cause": cand[5],
                "effect": cand[6],
                "marker": cand[3],
                "span": sentence[cand[0]:cand[1]],
                "direction": cand[4],
                "cause_truncated": cand[7],
                "effect_truncated": cand[8],
            })
        return kept

    def _scanners(self) -> list:
        """Return the marker scanners in priority order.

        Order matters only for same-position ties (longer regions win
        first), which is why the prepositional "because of" / "as a
        result of" scanners run before the bare "because" / connective
        scanners that share their opening words.

        Returns:
            list: Callable(sentence, base, mask) -> candidate tuples.
        """
        return (
            self._scan_prep,
            self._scan_because,
            self._scan_since,
            self._scan_so,
            self._scan_connective,
            self._scan_leads,
            self._scan_results,
            self._scan_cause_verb,
            self._scan_caused_by,
            self._scan_zh_pair,
            self._scan_zh_due,
            self._scan_zh_verb,
            self._scan_zh_therefore,
        )

    # -- English scanners ---------------------------------------------- #

    def _scan_prep(self, sentence: str, base: int, mask: bytes) -> list:
        """Prepositional markers: "because of X, Y", "due to X, Y",
        "as a result of X, Y".

        The cause runs from the marker to the next separator, which is
        required; the effect is the clause after that separator.

        Args:
            sentence: Sentence text.
            base: Sentence offset in the document.
            mask: Quote mask of the document.

        Returns:
            list: Candidate tuples.
        """
        out = []
        for m in _EN_PREP_RE.finditer(sentence):
            if mask[base + m.start()]:
                continue
            sep = _fsep(sentence, m.end())
            if sep < 0:
                continue
            effect_start, effect_end = _next_clause(sentence, sep + 1)
            out.append((m.start(), effect_end, 0, m.group(1).lower(),
                        "forward", sentence[m.end():sep],
                        sentence[effect_start:effect_end]))
        return out

    def _scan_because(self, sentence: str, base: int, mask: bytes) -> list:
        """"X because Y" (reverse) and clause-initial "Because X, Y".

        With text before the marker the reading is reverse (effect left,
        cause right); with nothing before it the pattern degenerates to
        the forward lead reading "Because X, Y", which requires the
        comma after the cause clause.

        Args:
            sentence: Sentence text.
            base: Sentence offset in the document.
            mask: Quote mask of the document.

        Returns:
            list: Candidate tuples.
        """
        out = []
        for m in _EN_BECAUSE_RE.finditer(sentence):
            if mask[base + m.start()]:
                continue
            left_start, _ = _prev_clause(sentence, m.start(), True)
            if _clean_span(sentence[left_start:m.start()]):
                cause_start, cause_end = _next_clause(sentence, m.end())
                out.append((left_start, cause_end, 1, "because", "reverse",
                            sentence[cause_start:cause_end],
                            sentence[left_start:m.start()]))
            else:
                sep = _fsep(sentence, m.end())
                if sep < 0:
                    continue
                effect_start, effect_end = _next_clause(sentence, sep + 1)
                out.append((m.start(), effect_end, 1, "because", "forward",
                            sentence[m.end():sep],
                            sentence[effect_start:effect_end]))
        return out

    def _scan_since(self, sentence: str, base: int, mask: bytes) -> list:
        """"Y since X" (reverse), guarded against temporal "since".

        The match survives only when a left clause exists and the clause
        after "since" carries a verb-ish token (see ``_verbish``).

        Args:
            sentence: Sentence text.
            base: Sentence offset in the document.
            mask: Quote mask of the document.

        Returns:
            list: Candidate tuples.
        """
        out = []
        for m in _EN_SINCE_RE.finditer(sentence):
            if mask[base + m.start()]:
                continue
            left_start, _ = _prev_clause(sentence, m.start(), True)
            if not _clean_span(sentence[left_start:m.start()]):
                continue
            cause_start, cause_end = _next_clause(sentence, m.end())
            cause = sentence[cause_start:cause_end]
            if not _verbish(cause):
                continue
            out.append((left_start, cause_end, 2, "since", "reverse",
                        cause, sentence[left_start:m.start()]))
        return out

    def _scan_so(self, sentence: str, base: int, mask: bytes) -> list:
        """"X, so Y" — comma before "so" required, purpose blocked.

        "so that / so much / ..." after the comma is treated as a purpose
        or intensifier construction and skipped.

        Args:
            sentence: Sentence text.
            base: Sentence offset in the document.
            mask: Quote mask of the document.

        Returns:
            list: Candidate tuples.
        """
        out = []
        for m in _EN_SO_RE.finditer(sentence):
            if mask[base + m.start()]:
                continue
            j = m.start()
            while j > 0 and sentence[j - 1].isspace():
                j -= 1
            if j == 0 or sentence[j - 1] != ",":
                continue
            if _next_word(sentence, m.end()) in _SO_BLOCKERS:
                continue
            cause_start, _ = _prev_clause(sentence, j - 1, False)
            effect_start, effect_end = _next_clause(sentence, m.end())
            out.append((cause_start, effect_end, 3, "so", "forward",
                        sentence[cause_start:j - 1],
                        sentence[effect_start:effect_end]))
        return out

    def _scan_connective(self, sentence: str, base: int, mask: bytes) \
            -> list:
        """Sentence-internal "A, therefore B" / "A, (and) as a result, B".

        The cause is the clause before the connective, hopping over a
        conjunction-only clause when the connective is parenthetical
        (", and as a result,"); a comma directly after the connective is
        stepped over before the effect clause.

        Args:
            sentence: Sentence text.
            base: Sentence offset in the document.
            mask: Quote mask of the document.

        Returns:
            list: Candidate tuples.
        """
        out = []
        for m in _EN_CONNECTIVE_RE.finditer(sentence):
            if mask[base + m.start()]:
                continue
            cause_start, cause_end = _prev_clause(sentence, m.start(), True)
            k = m.end()
            while k < len(sentence) and sentence[k].isspace():
                k += 1
            if k < len(sentence) and sentence[k] in _CLAUSE_SEPARATORS:
                effect_start, effect_end = _next_clause(sentence, k + 1)
            else:
                effect_start, effect_end = _next_clause(sentence, m.end())
            out.append((cause_start, effect_end, 4, m.group(1).lower(),
                        "forward", sentence[cause_start:cause_end],
                        sentence[effect_start:effect_end]))
        return out

    def _scan_leads(self, sentence: str, base: int, mask: bytes) -> list:
        """"X leads to / lead to / led to / leading to Y".

        Args:
            sentence: Sentence text.
            base: Sentence offset in the document.
            mask: Quote mask of the document.

        Returns:
            list: Candidate tuples.
        """
        out = []
        for m in _EN_LEADS_RE.finditer(sentence):
            if mask[base + m.start()]:
                continue
            cause_start, _ = _prev_clause(sentence, m.start(), False)
            effect_start, effect_end = _next_clause(sentence, m.end())
            out.append((cause_start, effect_end, 5, m.group(0).lower(),
                        "forward", sentence[cause_start:m.start()],
                        sentence[effect_start:effect_end]))
        return out

    def _scan_results(self, sentence: str, base: int, mask: bytes) -> list:
        """"X results in Y" family, noun-phrase guarded.

        A determiner directly before the marker ("the results in the
        appendix") marks a noun reading and suppresses the match.

        Args:
            sentence: Sentence text.
            base: Sentence offset in the document.
            mask: Quote mask of the document.

        Returns:
            list: Candidate tuples.
        """
        out = []
        for m in _EN_RESULTS_RE.finditer(sentence):
            if mask[base + m.start()]:
                continue
            if _prev_word(sentence, m.start()) in _DETERMINERS:
                continue
            cause_start, _ = _prev_clause(sentence, m.start(), False)
            effect_start, effect_end = _next_clause(sentence, m.end())
            out.append((cause_start, effect_end, 6, m.group(0).lower(),
                        "forward", sentence[cause_start:m.start()],
                        sentence[effect_start:effect_end]))
        return out

    def _scan_cause_verb(self, sentence: str, base: int, mask: bytes) \
            -> list:
        """"X causes / cause / caused Y", noun-phrase guarded.

        Suppressed when followed by "of" ("the cause of the delay") or
        "by" (delegated to the "caused by" pattern), or preceded by a
        determiner ("a cause for concern" style noun readings).

        Args:
            sentence: Sentence text.
            base: Sentence offset in the document.
            mask: Quote mask of the document.

        Returns:
            list: Candidate tuples.
        """
        out = []
        for m in _EN_CAUSE_RE.finditer(sentence):
            if mask[base + m.start()]:
                continue
            following = _next_word(sentence, m.end())
            if following in ("of", "by"):
                continue
            if _prev_word(sentence, m.start()) in _DETERMINERS:
                continue
            cause_start, _ = _prev_clause(sentence, m.start(), False)
            effect_start, effect_end = _next_clause(sentence, m.end())
            out.append((cause_start, effect_end, 7, m.group(1).lower(),
                        "forward", sentence[cause_start:m.start()],
                        sentence[effect_start:effect_end]))
        return out

    def _scan_caused_by(self, sentence: str, base: int, mask: bytes) \
            -> list:
        """"X (was) caused by Y" (reverse).

        Args:
            sentence: Sentence text.
            base: Sentence offset in the document.
            mask: Quote mask of the document.

        Returns:
            list: Candidate tuples.
        """
        out = []
        for m in _EN_CAUSED_BY_RE.finditer(sentence):
            if mask[base + m.start()]:
                continue
            left_start, _ = _prev_clause(sentence, m.start(), True)
            cause_start, cause_end = _next_clause(sentence, m.end())
            out.append((left_start, cause_end, 8, "caused by", "reverse",
                        sentence[cause_start:cause_end],
                        sentence[left_start:m.start()]))
        return out

    # -- Chinese scanners ---------------------------------------------- #

    def _scan_zh_pair(self, sentence: str, base: int, mask: bytes) -> list:
        """"因为X所以Y" — the span splits at 所以.

        A 因为 without a closing 所以 in the same sentence yields no
        relation (its effect is often elliptical); a bare 所以 without
        因为 is likewise not extracted.

        Args:
            sentence: Sentence text.
            base: Sentence offset in the document.
            mask: Quote mask of the document.

        Returns:
            list: Candidate tuples.
        """
        out = []
        for m in re.finditer(_ZH_BECAUSE, sentence):
            if mask[base + m.start()]:
                continue
            so = sentence.find(_ZH_SO, m.end())
            if so < 0:
                continue
            effect_start, effect_end = _next_clause(sentence, so + len(_ZH_SO))
            out.append((m.start(), effect_end, 9, _ZH_PAIR_MARKER,
                        "forward", sentence[m.end():so],
                        sentence[effect_start:effect_end]))
        return out

    def _scan_zh_due(self, sentence: str, base: int, mask: bytes) -> list:
        """"由于X，Y" — the cause runs to the required separator.

        Args:
            sentence: Sentence text.
            base: Sentence offset in the document.
            mask: Quote mask of the document.

        Returns:
            list: Candidate tuples.
        """
        out = []
        for m in re.finditer(_ZH_DUE, sentence):
            if mask[base + m.start()]:
                continue
            sep = _fsep(sentence, m.end())
            if sep < 0:
                continue
            effect_start, effect_end = _next_clause(sentence, sep + 1)
            out.append((m.start(), effect_end, 10, _ZH_DUE, "forward",
                        sentence[m.end():sep],
                        sentence[effect_start:effect_end]))
        return out

    def _scan_zh_verb(self, sentence: str, base: int, mask: bytes) -> list:
        """"X导致(了)Y" / "X造成Y" / "X引起Y" / "X使得Y".

        An optional aspect 了 attached to the marker is consumed with it
        so it never leaks into the effect span; the recorded marker stays
        the canonical form.

        Args:
            sentence: Sentence text.
            base: Sentence offset in the document.
            mask: Quote mask of the document.

        Returns:
            list: Candidate tuples.
        """
        out = []
        for m in _ZH_VERB_RE.finditer(sentence):
            if mask[base + m.start()]:
                continue
            marker = m.group(0)
            canonical = marker[:-1] if marker.endswith("了") else marker
            cause_start, _ = _prev_clause(sentence, m.start(), False)
            effect_start, effect_end = _next_clause(sentence, m.end())
            out.append((cause_start, effect_end, 11, canonical, "forward",
                        sentence[cause_start:m.start()],
                        sentence[effect_start:effect_end]))
        return out

    def _scan_zh_therefore(self, sentence: str, base: int, mask: bytes) \
            -> list:
        """"A，因此B" — cause is the clause before 因此.

        A separator directly after 因此 ("A，因此，B") is stepped over
        before the effect clause. A sentence-initial 因此 without an
        antecedent clause yields nothing.

        Args:
            sentence: Sentence text.
            base: Sentence offset in the document.
            mask: Quote mask of the document.

        Returns:
            list: Candidate tuples.
        """
        out = []
        for m in re.finditer(_ZH_THEREFORE, sentence):
            if mask[base + m.start()]:
                continue
            cause_start, cause_end = _prev_clause(sentence, m.start(), True)
            k = m.end()
            if k < len(sentence) and sentence[k] in _CLAUSE_SEPARATORS:
                effect_start, effect_end = _next_clause(sentence, k + 1)
            else:
                effect_start, effect_end = _next_clause(sentence, m.end())
            out.append((cause_start, effect_end, 12, _ZH_THEREFORE,
                        "forward", sentence[cause_start:cause_end],
                        sentence[effect_start:effect_end]))
        return out

    # ------------------------------------------------------------------ #
    # Segmentation (conservative, same family as SentenceLengthFilter)
    # ------------------------------------------------------------------ #

    def _sentence_spans(self, text: str) -> List[Tuple[int, int]]:
        """Split text into word-bearing sentence spans.

        A sentence is a maximal run of non-terminal characters plus its
        terminating punctuation run and closing quotes. Boundaries are
        ``. ! ?`` and ``。！？``; the dot additionally respects the
        abbreviation, single-letter-initial, decimal and ellipsis guards,
        so "Dr. Smith asked. Ms. Lee replied." yields exactly two
        sentences. Leading whitespace is skipped; a segment must contain
        at least one alphanumeric character (CJK included) to count.

        Args:
            text: Raw document text.

        Returns:
            List[Tuple[int, int]]: (start, end) offsets of each sentence,
            in document order.
        """
        spans: List[Tuple[int, int]] = []
        length = len(text)
        start = 0
        while start < length and text[start].isspace():
            start += 1
        i = start
        while i < length:
            if text[i] in _TERMINAL_CHARS and self._is_boundary(text, i):
                end = i + 1
                while end < length and text[end] in _TERMINAL_CHARS:
                    end += 1
                while end < length and text[end] in _CLOSING_CHARS:
                    end += 1
                if self._has_word(text[start:end]):
                    spans.append((start, end))
                start = end
                while start < length and text[start].isspace():
                    start += 1
                i = start
            else:
                i += 1
        if start < length and self._has_word(text[start:length]):
            spans.append((start, length))
        return spans

    @staticmethod
    def _is_boundary(text: str, index: int) -> bool:
        """Report whether the terminal character at index really splits.

        Args:
            text: Full document text.
            index: Position of the candidate terminal character.

        Returns:
            bool: True when a sentence boundary, False for dots inside
            ellipses, decimals, abbreviations and initials. Non-dot
            terminals (! ? 。！？) always split.
        """
        if text[index] != ".":
            return True
        if index + 1 < len(text) and text[index + 1] == ".":
            return False
        if index > 0 and text[index - 1].isdigit() and \
                index + 1 < len(text) and text[index + 1].isdigit():
            return False
        j = index
        while j > 0 and text[j - 1].isalpha():
            j -= 1
        word = text[j:index]
        if len(word) == 1:
            return False
        return word.lower() not in _ABBREVIATIONS

    @staticmethod
    def _has_word(sentence: str) -> bool:
        """Report whether a segment carries at least one word.

        Args:
            sentence: Segment text.

        Returns:
            bool: True when the segment contains an alphanumeric
            character (CJK ideographs included).
        """
        return any(ch.isalnum() for ch in sentence)

    def _stamp(self, doc: Document, key: str, value) -> None:
        """Write one entry into document metadata via a copied mapping.

        The metadata mapping is copied before mutation so a mapping shared
        with other pipeline stages never observes surprising in-place edits.

        Args:
            doc: Document to stamp.
            key: Metadata key.
            value: Metadata value.
        """
        meta = dict(doc.metadata or {})
        meta[key] = value
        doc.metadata = meta

    # ------------------------------------------------------------------ #
    # Configuration
    # ------------------------------------------------------------------ #

    def _initialize_by_component_configer(
            self, doc_processor_configer: ComponentConfiger) \
            -> 'CausalPhraseDetector':
        """Initialize and validate the detector from component configuration.

        Validation happens eagerly at load time: a misconfigured detector
        that silently stamped truncated or unlimited metadata would be far
        harder to notice in production than a startup failure.

        Args:
            doc_processor_configer: Configuration object.

        Returns:
            CausalPhraseDetector: The initialized instance.

        Raises:
            ValueError: On an invalid combination of parameter values.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        if hasattr(doc_processor_configer, "max_relations") and \
                doc_processor_configer.max_relations is not None:
            cap = doc_processor_configer.max_relations
            if isinstance(cap, bool) or not isinstance(cap, int):
                raise ValueError("max_relations must be an integer")
            self.max_relations = cap
            if not 1 <= self.max_relations <= 10000:
                raise ValueError("max_relations must be in [1, 10000]")

        if hasattr(doc_processor_configer, "span_char_limit") and \
                doc_processor_configer.span_char_limit is not None:
            limit = doc_processor_configer.span_char_limit
            if isinstance(limit, bool) or not isinstance(limit, int):
                raise ValueError("span_char_limit must be an integer")
            self.span_char_limit = limit
            if not 1 <= self.span_char_limit <= 10000:
                raise ValueError("span_char_limit must be in [1, 10000]")

        for attr in ("relations_key", "count_key", "density_key"):
            if hasattr(doc_processor_configer, attr) and \
                    getattr(doc_processor_configer, attr) is not None:
                key = getattr(doc_processor_configer, attr)
                if not isinstance(key, str):
                    raise ValueError(f"{attr} must be a string")
                setattr(self, attr, key)

        return self
