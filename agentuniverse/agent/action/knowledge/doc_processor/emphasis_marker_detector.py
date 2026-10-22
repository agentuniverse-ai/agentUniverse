# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @FileName: emphasis_marker_detector.py

import re
from typing import List

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

# Minimum number of letters a fully-uppercase ASCII token must contain to
# be reported as a 'caps' run; digits inside the token do not count.
_CAPS_MIN_LETTERS = 3

# Emphasis kinds reported by the detector.
_KIND_BOLD = 'bold'
_KIND_ITALIC = 'italic'
_KIND_CAPS = 'caps'
_KIND_HIGHLIGHT = 'highlight'

# Maximal runs of a single emphasis marker character on a line. Mixed
# marker characters (e.g. the '*_' in '_foo*_bar') split into separate
# runs instead of fusing into one ambiguous blob.
_MARKER_RUN_RE = re.compile(r'\*+|_+|=+')

# Fully-uppercase ASCII token: uppercase letters and digits, bounded by
# lookarounds so tokens glued to lowercase letters or digits of a wider
# mixed-case word (e.g. the 'SAPP' inside 'iOSAPP') never match. The
# lookarounds are ASCII alphanumerics only, so a caps run embedded
# directly in CJK text (no spaces) is still detected, and underscore
# separators act as token boundaries just like spaces: both fragments
# of 'FOO_BAR' report, and the caps run inside '__IMPORTANT__'
# overlaps its bold hit exactly as '**IMPORTANT**' does.
_CAPS_TOKEN_RE = re.compile(r'(?<![A-Za-z0-9])[A-Z0-9]+(?![A-Za-z0-9])')

# Opening code fence: three or more backticks or tildes after optional
# indentation. The info string (e.g. 'python') is not inspected.
_FENCE_OPEN_RE = re.compile(r'^(\s*)(`{3,}|~{3,})')


def _is_word_char(ch: str) -> bool:
    """Report whether a character counts as a word character for the
    simplified CommonMark intraword rule.

    Word characters are Unicode alphanumerics plus the underscore
    itself, mirroring CommonMark's intraword behaviour for non-Latin
    scripts: 'snake_case' underscores sit between word characters and
    therefore can never open or close emphasis, and neither do the
    underscores inside CJK or Cyrillic word chains such as
    '参数_说明_结束' or 'прилив_и_отлив', whose ideographs and letters
    CommonMark counts as word characters just like ASCII ones.

    Args:
        ch: Single character, or '' / None for line boundaries.

    Returns:
        bool: True for Unicode alphanumerics and '_'; False for
        anything else, including line boundaries, whitespace and
        punctuation.
    """
    if not ch:
        return False
    return ch.isalnum() or ch == '_'


class EmphasisMarkerDetector(DocProcessor):
    """Detect emphasis constructs and stamp them into document metadata.

    Authors emphasize terms on purpose — **bold**, *italic*, ==highlight==,
    SHOUTED acronyms — yet by embedding time those signals are usually
    thrown away: the chunker flattens the markers into the plain text and
    the salient terms lose the only ranking hint the author gave. This
    pre-processing component walks every document before that happens and
    records each emphasis construct as structured metadata: what kind it
    is, the emphasized text with markers stripped, and the half-open
    character span of the full construct including its markers (so a later
    stage can cut the noise out exactly, or lift the term out for keyword
    boosting). It targets the *emphasis / salient-term extraction*
    direction of issue #258.

    Four kinds are detected, in line-based scans that skip fenced code
    blocks:

    1. bold — ``**double asterisk**`` and ``__double underscore__`` runs.
       Underscore bold is also the 'underline' spelling of several
       rich-text dialects; both are reported as kind ``bold`` because in
       CommonMark they render identically.
    2. italic — single ``*asterisk*`` and ``_underscore_`` delimiters that
       are not part of a double run. ``**`` versus ``*`` is resolved by
       delimiter-run length: a run of exactly two marker characters opens
       bold, a run of exactly one opens italic, and runs of three or more
       (``***compound***``) are skipped entirely rather than guessed at.
    3. caps — fully-uppercase ASCII tokens of at least three letters
       ('NASA', 'ABC123'), optionally filtered against a configurable
       acronym allowlist (default empty, so every caps run is reported;
       populate the allowlist to silence known acronyms). Caps is the
       noisiest kind and should be treated as lower-confidence than the
       explicit marker kinds: it also fires on shouted words, initials
       and product codes that are not acronyms.
    4. highlight — the ``==double equals==`` extended-markdown highlight.

    The marker pairing rules are a documented simplification of CommonMark
    left/right flanking: an opening run must be followed by a
    non-whitespace character, a closing run must be preceded by one (so
    ``** padded **`` never matches), and content edges are therefore
    never whitespace. Per CommonMark's intraword rule — which applies to
    underscores only — an ``_`` run cannot open when preceded by a word
    character nor close when followed by one, where word characters are
    Unicode alphanumerics and the underscore; so ``snake_case_identifiers``
    and ``foo_bar`` never produce italic hits, and neither do the
    underscores inside CJK or Cyrillic word chains such as
    ``参数_说明_结束``, while ``__dunder__`` names at word boundaries do
    parse as bold exactly as CommonMark renders them. Delimiters pair per
    line in LIFO order within the same marker character and run length; a
    closer first looks through openers of a different length stacked
    above its match and discards them as stale (a lone ``*`` opened
    inside what turns out to be a bold run), so ``**a*b**`` stays one
    bold hit while ``*a**b*`` resolves to one italic; a closing run that
    matches nothing is discarded, and unmatched openers fall away at end
    of line, so ``**unclosed`` and ``text *`` report nothing. Emphasis
    never spans a line break under this simplified model, and constructs
    inside fenced code blocks (``` or ~~~ fences, tracked by line under
    any leading indentation, including unclosed fences that immunize the
    rest of the text) are immune. Inline backtick spans are not masked —
    only fences — so `` `**code**` `` still reports its bold run; this
    keeps the scan a single deterministic pass.

    Beyond the simplifications above, four more deviations from full
    CommonMark rendering are intentional and worth knowing when comparing
    detector output against a renderer: (1) flanking ignores punctuation
    classes, so a run separated from a word character only by punctuation
    still opens or closes — ``a*(foo)*`` reports an italic hit and
    ``bar**=== word**`` a bold hit where CommonMark renders both
    literally; (2) backslash escapes are not honored, so ``\\*foo\\*``
    reports the italic hit CommonMark would suppress, backslashes kept
    as content; (3) pairing is
    length-matched per marker character, so CommonMark's cross-length
    resolutions — the em nested inside the leftover bold markers of
    ``**a *b**``, or ``___ _world)__`` — resolve differently here (one
    bold hit for the first, nothing for the second); and (4) runs of
    three or more marker characters are skipped whole (already noted
    under the kinds above). For ordinary prose emphasis — space-flanked
    ``**bold**``, ``*italic*``, ``__bold__`` and ``_italic_`` — the
    simplified rules agree with CommonMark.

    Detected hits land in metadata as a list of ``{kind, text, span}``
    mappings sorted by span and capped at ``max_hits`` (default 100):
    ``text`` is the emphasized content with markers stripped and ``span``
    is ``[start, end)`` over the ORIGINAL text covering markers plus
    content (for caps the span is exactly the token). Sibling stamps:
    ``emphasis_counts`` maps each kind to its count within the capped
    list, and ``emphasis_terms`` lists the deduplicated emphasized texts
    in first-occurrence order capped at ``max_terms`` (default 20) — a
    ready-made salient-term hint for keyword extraction or retrieval
    boosting. A document with no emphasis at all passes through
    completely untouched (no metadata keys are added); when hits exist
    the metadata mapping is copied before stamping so shared mappings
    never observe in-place edits, and text / id / other metadata fields
    are never modified. Hits of different kinds may legitimately overlap
    (``**IMPORTANT**`` yields both a bold hit and a caps hit).

    The whole detector is pure Python, offline and deterministic: no
    model calls, no network, no external dependencies.

    Attributes:
        caps_allowlist: Known acronyms exempt from caps detection.
            Entries are case-insensitive (normalized to uppercase at
            load time and again at scan time); the default empty list
            reports every caps run.
        max_hits: Maximum number of hits stamped into the emphasis list;
            must be >= 1. Counts and terms are derived from the capped
            list so the three stamps always agree.
        max_terms: Maximum number of deduplicated terms stamped into the
            terms list; must be >= 1.
        emphasis_key: Metadata key the hit list is written to; an empty
            value disables that stamp.
        counts_key: Metadata key the per-kind counts are written to; an
            empty value disables that stamp.
        terms_key: Metadata key the deduplicated terms are written to; an
            empty value disables that stamp.
    """

    caps_allowlist: List[str] = []
    max_hits: int = 100
    max_terms: int = 20
    emphasis_key: str = 'emphasis'
    counts_key: str = 'emphasis_counts'
    terms_key: str = 'emphasis_terms'

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Stamp emphasis metadata onto every document in the batch.

        Args:
            origin_docs: Documents to scan, in batch order.
            query: Query object (unused; emphasis is a property of the
                documents' own text, not of any request).

        Returns:
            List[Document]: The same documents in the same order.
                Documents without any emphasis construct are returned
                completely untouched; the others carry the emphasis
                metadata stamps.
        """
        allowlist = {str(entry).upper()
                     for entry in (self.caps_allowlist or [])}
        for doc in origin_docs or []:
            hits = self._scan(doc.text or '', allowlist)
            if not hits:
                continue

            kept = hits[:self.max_hits]
            counts = {}
            terms = []
            seen = set()
            for hit in kept:
                kind = hit['kind']
                counts[kind] = counts.get(kind, 0) + 1
                term = hit['text']
                if term not in seen:
                    seen.add(term)
                    terms.append(term)
            terms = terms[:self.max_terms]

            if self.emphasis_key:
                self._stamp(doc, self.emphasis_key, kept)
            if self.counts_key:
                self._stamp(doc, self.counts_key, counts)
            if self.terms_key:
                self._stamp(doc, self.terms_key, terms)
        return origin_docs

    # ------------------------------------------------------------------ #
    # Scanning
    # ------------------------------------------------------------------ #

    def _scan(self, text: str, allowlist: set = None) -> List[dict]:
        """Scan one text for emphasis constructs outside code fences.

        Args:
            text: Document text (None treated as empty).
            allowlist: Uppercase acronyms exempt from caps detection.

        Returns:
            List[dict]: Hits ``{'kind', 'text', 'span'}`` in document
            order (sorted by span start; same-start hits shorter first).
            Nested constructs are reported individually — the wrapper
            first, then the construct nested inside it.
        """
        if allowlist is None:
            allowlist = {str(entry).upper()
                         for entry in (self.caps_allowlist or [])}

        hits: List[dict] = []
        in_fence = False
        fence_char = ''
        fence_len = 0
        offset = 0
        for line in (text or '').split('\n'):
            if in_fence:
                close_re = re.compile(
                    r'^\s*' + re.escape(fence_char) +
                    r'{%d,}\s*$' % fence_len)
                if close_re.match(line):
                    in_fence = False
            else:
                opener = _FENCE_OPEN_RE.match(line)
                if opener:
                    # The fence lines themselves are immune; scanning
                    # resumes only after the matching closing fence.
                    in_fence = True
                    fence_char = opener.group(2)[0]
                    fence_len = len(opener.group(2))
                else:
                    self._scan_line(line, offset, allowlist, hits)
            offset += len(line) + 1

        hits.sort(key=lambda hit: (hit['span'][0], hit['span'][1]))
        return hits

    def _scan_line(self, line: str, offset: int, allowlist: set,
                   hits: List[dict]) -> None:
        """Detect marker-constructed and caps emphasis on a single line.

        Args:
            line: One line of text (never a fence line).
            offset: Character offset of this line within the document,
                added to every span so spans index the original text.
            allowlist: Uppercase acronyms exempt from caps detection.
            hits: Output list hits are appended to.
        """
        # Per-marker-character stacks of open delimiters, each entry
        # (run_start, run_end, run_length). LIFO pairing within the same
        # character and length yields innermost-first nesting.
        stacks = {'*': [], '_': [], '=': []}
        for run in _MARKER_RUN_RE.finditer(line):
            start, end = run.span()
            char = line[start]
            length = end - start

            if char == '=':
                # Only the exactly-two '==' run is a highlight delimiter;
                # lone '=' (equations) and '===' (setext underlines)
                # never pair.
                if length != 2:
                    continue
            elif length > 2:
                # Runs of three or more '*'/'_' are compound markers
                # (e.g. '***bold-italic***'); skipped rather than guessed.
                continue

            kind = _KIND_HIGHLIGHT if char == '=' else \
                (_KIND_BOLD if length == 2 else _KIND_ITALIC)

            matched = self._match_opener(line, start, end, char,
                                         stacks[char])
            if matched is not None:
                run_start, run_end, _ = matched
                hits.append({
                    'kind': kind,
                    'text': line[run_end:start],
                    'span': [run_start + offset, end + offset],
                })
            elif self._opens(line, start, end, char):
                stacks[char].append((start, end, length))

        for match in _CAPS_TOKEN_RE.finditer(line):
            token = match.group()
            letters = sum(1 for ch in token if ch.isalpha())
            if letters >= _CAPS_MIN_LETTERS and token not in allowlist:
                hits.append({
                    'kind': _KIND_CAPS,
                    'text': token,
                    'span': [match.start() + offset, match.end() + offset],
                })

    @staticmethod
    def _opens(line: str, start: int, end: int, char: str) -> bool:
        """Decide whether a marker run can open emphasis on this line.

        Simplified CommonMark left flanking: the character after the run
        must exist and not be whitespace. Underscores additionally follow
        the intraword rule — an '_' run cannot open when preceded by a
        word character — so identifiers like 'snake_case' stay inert.

        Args:
            line: The line being scanned.
            start: Index of the first marker character.
            end: Index one past the last marker character.
            char: The marker character ('*', '_' or '=').

        Returns:
            bool: True when the run may open a construct.
        """
        if end >= len(line) or line[end].isspace():
            return False
        if char == '_' and _is_word_char(line[start - 1] if start else ''):
            return False
        return True

    @staticmethod
    def _match_opener(line: str, start: int, end: int, char: str,
                      stack: List[tuple]):
        """Find the opener a marker run closes, if any.

        Simplified CommonMark right flanking: the character before the
        run must not be whitespace, and the most recent unmatched opener
        for the same marker character must share the run length (a lone
        '*' never closes a '**' bold, which is how '*a**b*' resolves to
        one italic). When the top of the stack holds openers of a
        different length they are stale — a lone '*' opened inside what
        turns out to be a bold run — and are discarded in favor of the
        deeper length-matching opener, so '**a*b**' stays one bold.
        Underscore closers additionally cannot be followed by a word
        character (intraword rule).

        Args:
            line: The line being scanned.
            start: Index of the first marker character.
            end: Index one past the last marker character.
            char: The marker character ('*', '_' or '=').
            stack: Open delimiters for this marker character.

        Returns:
            tuple: The matched opener ``(run_start, run_end, length)``
            (removed from the stack together with everything above it),
            or None when the run closes nothing.
        """
        if not stack or start == 0 or line[start - 1].isspace():
            return None
        if char == '_' and _is_word_char(line[end] if end < len(line) else ''):
            return None
        for index in range(len(stack) - 1, -1, -1):
            if stack[index][2] == end - start:
                matched = stack[index]
                del stack[index:]
                return matched
        return None

    def _stamp(self, doc: Document, key: str, value) -> None:
        """Write one entry into document metadata via a copied mapping.

        The metadata mapping is copied before mutation so a mapping shared
        with other pipeline stages never observes surprising in-place
        edits.

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
            -> 'EmphasisMarkerDetector':
        """Initialize and validate the detector from component
        configuration.

        Validation happens eagerly at load time: a misconfigured
        detector that silently skipped constructs would be far harder to
        notice in production than a startup failure.

        Args:
            doc_processor_configer: Configuration object.

        Returns:
            EmphasisMarkerDetector: The initialized instance.

        Raises:
            ValueError: On an invalid combination of parameter values.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        if hasattr(doc_processor_configer, 'caps_allowlist') and \
                doc_processor_configer.caps_allowlist is not None:
            raw = doc_processor_configer.caps_allowlist
            if isinstance(raw, str) or not isinstance(raw, (list, tuple)):
                raise ValueError('caps_allowlist must be a list of strings')
            allowlist = []
            for entry in raw:
                if not isinstance(entry, str) or not entry.strip():
                    raise ValueError(
                        'caps_allowlist entries must be non-empty strings, '
                        f'got {entry!r}')
                allowlist.append(entry.strip().upper())
            self.caps_allowlist = allowlist

        if hasattr(doc_processor_configer, 'max_hits') and \
                doc_processor_configer.max_hits is not None:
            max_hits = doc_processor_configer.max_hits
            if isinstance(max_hits, bool) or not isinstance(max_hits, int):
                raise ValueError('max_hits must be an integer')
            self.max_hits = max_hits
            if self.max_hits < 1:
                raise ValueError('max_hits must be >= 1')

        if hasattr(doc_processor_configer, 'max_terms') and \
                doc_processor_configer.max_terms is not None:
            max_terms = doc_processor_configer.max_terms
            if isinstance(max_terms, bool) or not isinstance(max_terms, int):
                raise ValueError('max_terms must be an integer')
            self.max_terms = max_terms
            if self.max_terms < 1:
                raise ValueError('max_terms must be >= 1')

        for attr in ('emphasis_key', 'counts_key', 'terms_key'):
            if hasattr(doc_processor_configer, attr) and \
                    getattr(doc_processor_configer, attr) is not None:
                key = getattr(doc_processor_configer, attr)
                if not isinstance(key, str):
                    raise ValueError(f'{attr} must be a string')
                setattr(self, attr, key)

        return self
