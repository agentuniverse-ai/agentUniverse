# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @FileName: paragraph_role_tagger.py

import re
from typing import Dict, List, Optional, Tuple

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import \
    DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger

# Weight of a cue phrase whose first character starts inside the early
# window (the beginning of the paragraph).
_EARLY_WEIGHT = 2
# Weight of a cue phrase found anywhere else in the paragraph.
_ANYWHERE_WEIGHT = 1

# Canonical display order of the five discourse roles.
_ALL_ROLES = ('intro', 'transition', 'contrast', 'conclusion',
              'elaboration')

# Tie-breaking priority (highest first): when several roles finish with
# equal scores, the earliest role in this order wins. Contrast ranks above
# conclusion because a contrasting connective almost always marks the true
# pivot of a paragraph; elaboration carries no cues of its own and only
# acts as the default, so it ranks last and never wins a positive tie.
_ROLE_PRIORITY = ('contrast', 'conclusion', 'transition', 'intro',
                  'elaboration')

# Cue phrases per role. English cues are stored lowercase and matched
# case-insensitively; Chinese cues match verbatim.
_CUE_PHRASES = {
    'intro': ('in this article', 'we will', 'first of all',
              '本文将', '首先'),
    'transition': ('in addition', 'furthermore', 'moreover', 'next',
                   'second', '此外', '其次', '接下来'),
    'contrast': ('however', 'on the other hand', 'nevertheless',
                 'in contrast', 'but', '但是', '然而'),
    'conclusion': ('in conclusion', 'in summary', 'to sum up', 'finally',
                   '因此', '总之', '最后'),
}

# Cues that only count when they begin a sentence: 'but' works as a
# discourse connective at a sentence start, while mid-sentence 'but'
# merely joins clauses inside one.
_SENTENCE_START_ONLY = frozenset({'but'})

# Example markers recorded as the reported cue of the default elaboration
# role; they never contribute score.
_EXAMPLE_CUES = ('for example', 'such as', 'e.g.', '例如')

# A colon-list is a colon whose paragraph remainder still contains an
# enumeration separator; it counts as elaboration evidence without
# contributing a phrase cue.
_COLON_CHARS = (':', '：')
_LIST_SEPARATORS = (',', '，', ';', '；', '、')

# Word unit for the early window: one CJK ideograph, or a maximal run of
# other non-space characters (punctuation merges into the adjacent run —
# a deliberate approximation that keeps the rule deterministic).
_WORD_UNIT_RE = re.compile(r'[\u4e00-\u9fff]|[^\s\u4e00-\u9fff]+')

# Paragraph separator: a newline, any number of blank (space/tab/CR-only)
# lines, and the newline that ends the last blank line. A single newline
# (a soft wrap) is NOT a paragraph boundary.
_SEPARATOR_RE = re.compile(r'\r?\n[ \t\r]*(?:\r?\n[ \t\r]*)*\r?\n')

# Sentence terminators and closing quotes/brackets skipped when deciding
# whether a position begins a sentence.
_TERMINATORS = '.!?;:…。！？；：'
_CLOSERS = '"\'»」』）)]》>'


def _is_ascii_alnum(char: str) -> bool:
    """Report whether a single character is an ASCII letter or digit.

    Args:
        char: Character to test.

    Returns:
        bool: True for [0-9A-Za-z], False otherwise.
    """
    return char.isascii() and char.isalnum()


class ParagraphRoleTagger(DocProcessor):
    """Classify each paragraph's discourse role via cue phrases.

    Long-form knowledge documents follow a discourse structure — they
    open with framing, chain arguments with transitions, pivot on
    contrasts and close with conclusions — and downstream stages
    (context assembly, summarization, chunk weighting) benefit from
    knowing which paragraph plays which part. This pre-processing
    component reads every document, splits it into paragraphs on blank
    lines (the family rule shared with the other paragraph-aware
    processors) and tags each paragraph with one of five roles:
    ``intro``, ``transition``, ``contrast``, ``conclusion`` or
    ``elaboration``. It keys on cue phrases inside the paragraph text,
    which distinguishes it from heading-keyword or sentence-position
    approaches: roles follow what the writing says, not where the
    splitter placed a heading or a sentence.

    Scoring is deliberately simple and fully deterministic. For each
    paragraph the tagger scans a fixed bilingual cue table (English and
    Chinese phrases per role, see ``_CUE_PHRASES``). A cue whose first
    character starts within the early window — the first ``early_words``
    word units, where each whitespace token counts as one word and each
    CJK ideograph counts individually, so the window is tight for both
    scripts — earns weight 2; the same cue elsewhere in the paragraph
    still earns weight 1. English cues match case-insensitively and only
    on word boundaries, so 'Secondhand' does not fire the transition cue
    'second' and 'crew will' does not fire 'we will'; the cue 'but'
    counts only at a sentence start (after terminal punctuation or at
    the paragraph opening). Each role sums the weights of its matched
    cues; the highest score wins and ties resolve through the documented
    priority ``contrast > conclusion > transition > intro >
    elaboration``. The first paragraph receives a ``positional_bonus``
    added to intro's score and the last paragraph the same bonus added
    to conclusion's; the bonus applies only when that role already
    matched at least one cue, so a cue-free first or last paragraph
    still falls through to the default instead of being promoted.

    Elaboration is the default role: it has no discourse cues and zero
    score, and wins exactly when every other role scored zero. Example
    markers ('for example' / 'such as' / 'e.g.' / '例如') and
    colon-lists (a colon whose paragraph remainder contains an
    enumeration separator) never add score — they are recorded as
    evidence, with the earliest example marker reported as the
    paragraph's cue and everything else reporting ``None``. A pure
    narrative document without any cue therefore comes out uniformly
    elaboration, which is the intended documented behaviour.

    Bookkeeping lands in document metadata (mappings are copied before
    mutation; text, id and other fields are never touched):

    * ``metadata[roles_key]`` — a list of ``{paragraph_index, role,
      cue, span}`` entries in paragraph order, capped at
      ``max_role_entries`` (default 50) to bound metadata size;
      ``paragraph_index`` keeps the true index, ``cue`` is the canonical
      matched cue phrase or ``None``, and ``span`` is the ``[start,
      end)`` character range of the paragraph inside the original text.
    * ``metadata[counts_key]`` — per-role counts covering every
      paragraph, not just the capped entries.
    * ``metadata[pattern_key]`` — ``'<role>-heavy'`` when one role
      covers strictly more than half of the paragraphs, else
      ``'balanced'`` (exactly half counts as balanced); empty documents
      are ``'balanced'``.

    The whole pipeline is pure Python, offline, dependency-free and
    deterministic: same input, same metadata, across processes and
    PYTHONHASHSEED values.

    Attributes:
        early_words: Number of leading word units that form the early
            window; must be >= 1. Default 8.
        positional_bonus: Bonus added to intro for the first paragraph
            and to conclusion for the last paragraph when that role
            already matched a cue; must be >= 0. Default 0.5.
        max_role_entries: Maximum number of per-paragraph entries written
            to ``metadata[roles_key]``; must be >= 1. Default 50.
        roles_key: Metadata key for the per-paragraph role list; an
            empty value disables the stamp.
        counts_key: Metadata key for the per-role counts; an empty value
            disables the stamp.
        pattern_key: Metadata key for the dominant pattern; an empty
            value disables the stamp.
    """

    early_words: int = 8
    positional_bonus: float = 0.5
    max_role_entries: int = 50
    roles_key: str = 'paragraph_roles'
    counts_key: str = 'role_counts'
    pattern_key: str = 'dominant_pattern'

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Tag every document's paragraphs with discourse roles.

        Args:
            origin_docs: Documents to tag, in batch order.
            query: Query object (unused; roles depend only on the
                documents' own text).

        Returns:
            List[Document]: The same document objects, in the same
            order, each stamped with paragraph roles, per-role counts
            and the dominant pattern in its metadata.
        """
        for doc in origin_docs:
            text = doc.text or ''
            spans = self._paragraph_spans(text)
            total = len(spans)
            entries: List[Dict] = []
            counts = {role: 0 for role in _ALL_ROLES}
            for index, (start, end) in enumerate(spans):
                content = text[start:end]
                role, cue = self._tag_paragraph(content, index, total)
                counts[role] += 1
                if len(entries) < self.max_role_entries:
                    entries.append({
                        'paragraph_index': index,
                        'role': role,
                        'cue': cue,
                        'span': [start, end],
                    })
            if self.roles_key:
                self._stamp(doc, self.roles_key, entries)
            if self.counts_key:
                self._stamp(doc, self.counts_key, counts)
            if self.pattern_key:
                self._stamp(doc, self.pattern_key,
                            self._dominant_pattern(counts, total))
        return origin_docs

    # ------------------------------------------------------------------ #
    # Paragraph segmentation
    # ------------------------------------------------------------------ #

    @staticmethod
    def _paragraph_spans(text: str) -> List[Tuple[int, int]]:
        """Split text into blank-line-separated paragraph content spans.

        Paragraphs are the blocks between runs of blank lines (a blank
        line carries only spaces/tabs); a single newline inside a block
        is a soft wrap and stays inside the paragraph. Leading and
        trailing whitespace of each block is excluded from the span, and
        whitespace-only blocks are dropped entirely.

        Args:
            text: Document text (None treated as empty).

        Returns:
            List[Tuple[int, int]]: [start, end) character spans of the
            paragraph contents, in document order.
        """
        spans: List[Tuple[int, int]] = []
        prev_end = 0
        for separator in _SEPARATOR_RE.finditer(text):
            ParagraphRoleTagger._append_span(spans, text, prev_end,
                                             separator.start())
            prev_end = separator.end()
        ParagraphRoleTagger._append_span(spans, text, prev_end, len(text))
        return spans

    @staticmethod
    def _append_span(spans: List[Tuple[int, int]], text: str,
                     start: int, end: int) -> None:
        """Append the stripped content span of one raw block, if any.

        Args:
            spans: Accumulator list of (start, end) tuples.
            text: Full document text.
            start: Raw block start offset.
            end: Raw block end offset.
        """
        segment = text[start:end]
        left = len(segment) - len(segment.lstrip())
        right = len(segment) - len(segment.rstrip())
        if start + left < end - right:
            spans.append((start + left, end - right))

    # ------------------------------------------------------------------ #
    # Role scoring
    # ------------------------------------------------------------------ #

    def _tag_paragraph(self, content: str, index: int,
                       total: int) -> Tuple[str, Optional[str]]:
        """Decide the discourse role of one paragraph.

        Args:
            content: Paragraph text.
            index: Zero-based paragraph index within the document.
            total: Total number of paragraphs in the document.

        Returns:
            Tuple[str, Optional[str]]: (role, canonical cue phrase that
            decided the role, or None for the cue-free default).
        """
        scores, matches = self._score_matches(content)
        if index == 0 and scores['intro'] >= 1.0:
            scores['intro'] += self.positional_bonus
        if index == total - 1 and scores['conclusion'] >= 1.0:
            scores['conclusion'] += self.positional_bonus

        best = max(scores.values())
        if best <= 0.0:
            # Elaboration default: no discourse cue scored at all.
            # Example markers and colon-lists are evidence only.
            found = []
            for example in _EXAMPLE_CUES:
                for offset in self._find_cue(content, example):
                    found.append((offset, example))
            cue = min(found)[1] if found else None
            return 'elaboration', cue

        for role in _ROLE_PRIORITY:
            if scores[role] == best:
                decided = min(matches[role],
                              key=lambda m: (-m[1], m[0]))
                return role, decided[2]
        # Unreachable: _ROLE_PRIORITY covers every role.
        return 'elaboration', None

    def _score_matches(self, content: str
                       ) -> Tuple[Dict[str, float], Dict[str, List]]:
        """Score every cue role over one paragraph.

        Args:
            content: Paragraph text.

        Returns:
            Tuple[Dict[str, float], Dict[str, List]]: Per-role score
            sums and per-role lists of (offset, weight, cue) matches.
        """
        boundary = self._early_boundary(content)
        scores = {role: 0.0 for role in _ALL_ROLES}
        matches: Dict[str, List] = {role: [] for role in _ALL_ROLES}
        for role, cues in _CUE_PHRASES.items():
            for cue in cues:
                for offset in self._find_cue(content, cue):
                    weight = _EARLY_WEIGHT if offset < boundary \
                        else _ANYWHERE_WEIGHT
                    matches[role].append((offset, weight, cue))
            scores[role] = float(sum(w for _, w, _ in matches[role]))
        return scores, matches

    def _role_scores(self, content: str, index: int,
                     total: int) -> Dict[str, float]:
        """Expose per-role scores (with positional bonuses) for tests.

        Args:
            content: Paragraph text.
            index: Zero-based paragraph index within the document.
            total: Total number of paragraphs in the document.

        Returns:
            Dict[str, float]: Score of each role for this paragraph.
        """
        scores, _ = self._score_matches(content)
        if index == 0 and scores['intro'] >= 1.0:
            scores['intro'] += self.positional_bonus
        if index == total - 1 and scores['conclusion'] >= 1.0:
            scores['conclusion'] += self.positional_bonus
        return scores

    def _early_boundary(self, content: str) -> int:
        """Compute the character offset that ends the early window.

        The window covers the first ``early_words`` word units (each CJK
        ideograph is one unit, each whitespace-separated run of other
        characters is one). A paragraph with fewer units makes the whole
        paragraph early.

        Args:
            content: Paragraph text.

        Returns:
            int: Offset just past the last early word unit.
        """
        seen = 0
        for match in _WORD_UNIT_RE.finditer(content):
            seen += 1
            if seen >= self.early_words:
                return match.end()
        return len(content)

    def _find_cue(self, content: str, cue: str) -> List[int]:
        """Find every valid occurrence offset of a cue phrase.

        Matching is case-insensitive and length-preserving (the slice is
        lowered only for comparison). A cue delimited by ASCII
        alphanumerics must not touch ASCII alphanumerics on either side,
        so 'Secondhand' never fires 'second'. Cues listed in
        ``_SENTENCE_START_ONLY`` must additionally begin a sentence.

        Args:
            content: Paragraph text.
            cue: Canonical lowercase cue phrase.

        Returns:
            List[int]: Start offsets of valid occurrences, ascending.
        """
        offsets: List[int] = []
        length = len(cue)
        if length == 0 or length > len(content):
            return offsets
        for i in range(len(content) - length + 1):
            if content[i:i + length].lower() != cue:
                continue
            if _is_ascii_alnum(cue[0]) and i > 0 and \
                    _is_ascii_alnum(content[i - 1]):
                continue
            if _is_ascii_alnum(cue[-1]) and i + length < len(content) \
                    and _is_ascii_alnum(content[i + length]):
                continue
            if cue in _SENTENCE_START_ONLY and \
                    not self._is_sentence_start(content, i):
                continue
            offsets.append(i)
        return offsets

    @staticmethod
    def _is_sentence_start(content: str, offset: int) -> bool:
        """Report whether an offset begins a sentence.

        A position starts a sentence when everything before it, after
        dropping trailing whitespace and closing quotes/brackets, is
        empty (paragraph opening) or ends with terminal punctuation.

        Args:
            content: Paragraph text.
            offset: Candidate start offset.

        Returns:
            bool: True when the offset begins a sentence.
        """
        j = offset - 1
        while j >= 0 and (content[j].isspace() or content[j] in _CLOSERS):
            j -= 1
        return j < 0 or content[j] in _TERMINATORS

    @staticmethod
    def _has_colon_list(content: str) -> bool:
        """Report whether the paragraph contains a colon-list.

        A colon-list is a colon (ASCII or fullwidth) whose paragraph
        remainder contains at least one enumeration separator (comma,
        semicolon or enumeration comma, ASCII or fullwidth).

        Args:
            content: Paragraph text.

        Returns:
            bool: True when a colon-list is present.
        """
        for index, char in enumerate(content):
            if char in _COLON_CHARS:
                return any(sep in content[index + 1:]
                           for sep in _LIST_SEPARATORS)
        return False

    @staticmethod
    def _dominant_pattern(counts: Dict[str, int], total: int) -> str:
        """Summarize the role distribution of one document.

        One role covering strictly more than half of the paragraphs
        (integer arithmetic: ``best * 2 > total``) yields
        ``'<role>-heavy'``; anything else — including an exact half and
        empty documents — yields ``'balanced'``.

        Args:
            counts: Per-role paragraph counts.
            total: Total number of paragraphs.

        Returns:
            str: The dominant pattern label.
        """
        if total <= 0:
            return 'balanced'
        best = max(counts.values())
        if best * 2 > total:
            for role in _ALL_ROLES:
                if counts[role] == best:
                    return f'{role}-heavy'
        return 'balanced'

    @staticmethod
    def _stamp(doc: Document, key: str, value) -> None:
        """Write one entry into document metadata via a copied mapping.

        The metadata mapping is copied before mutation so a mapping
        shared with other pipeline stages never observes surprising
        in-place edits.

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
            -> 'ParagraphRoleTagger':
        """Initialize and validate the tagger from component configuration.

        Validation happens eagerly at load time: a silently
        misconfigured tagger stamping wrong metadata would be far harder
        to notice in production than a startup failure.

        Args:
            doc_processor_configer: Configuration object.

        Returns:
            ParagraphRoleTagger: The initialized instance.

        Raises:
            ValueError: On an invalid combination of parameter values.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        if hasattr(doc_processor_configer, 'early_words') and \
                doc_processor_configer.early_words is not None:
            early_words = doc_processor_configer.early_words
            if isinstance(early_words, bool) or \
                    not isinstance(early_words, int):
                raise ValueError('early_words must be an integer')
            self.early_words = early_words
            if self.early_words < 1:
                raise ValueError('early_words must be >= 1')

        if hasattr(doc_processor_configer, 'positional_bonus') and \
                doc_processor_configer.positional_bonus is not None:
            bonus = doc_processor_configer.positional_bonus
            if isinstance(bonus, bool) or \
                    not isinstance(bonus, (int, float)):
                raise ValueError('positional_bonus must be a number')
            self.positional_bonus = float(bonus)
            if self.positional_bonus < 0:
                raise ValueError('positional_bonus must be >= 0')

        if hasattr(doc_processor_configer, 'max_role_entries') and \
                doc_processor_configer.max_role_entries is not None:
            max_entries = doc_processor_configer.max_role_entries
            if isinstance(max_entries, bool) or \
                    not isinstance(max_entries, int):
                raise ValueError('max_role_entries must be an integer')
            self.max_role_entries = max_entries
            if self.max_role_entries < 1:
                raise ValueError('max_role_entries must be >= 1')

        for attr in ('roles_key', 'counts_key', 'pattern_key'):
            if hasattr(doc_processor_configer, attr) and \
                    getattr(doc_processor_configer, attr) is not None:
                key = getattr(doc_processor_configer, attr)
                if not isinstance(key, str):
                    raise ValueError(f'{attr} must be a string')
                setattr(self, attr, key)

        return self
