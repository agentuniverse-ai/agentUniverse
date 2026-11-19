# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @FileName: quote_attribution_analyzer.py

import re
from collections import deque
from typing import List, Optional, Tuple

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

# Quote styles recognized, paired within a single line so a quotation never
# leaks across a paragraph boundary: ASCII doubles, curly doubles, CJK
# corner brackets and German low-high marks. Apostrophes and single quotes
# are deliberately NOT delimiters — "don't" and "it's" would otherwise
# shatter English text into phantom quotations.
_QUOTE_RE = re.compile(r'"[^"\n]+"|“[^”\n]+”|「[^」\n]+」|„[^“\n]+“')

# English attribution verbs and the patterns built around them.
_EN_VERB_RE = re.compile(r'\b(?:said|says|told|added|noted|claimed|stated)\b')

# A capitalized token ("Alice", "Dr.", "O'Brien", "U.S."), optionally glued
# into a run with lowercase particles so "Ministry of Finance" or
# "Ludwig van Beethoven" survives as one name.
_NAME_RUN = (r"(?:[A-Z][\w.'’\-]*)"
             r"(?:\s+(?:[A-Z][\w.'’\-]*"
             r"|of|the|de|van|von|der|den|Jr\.|Sr\.|II|III|IV|V))*")

# A comma-separated appositive between the name and the verb, as in
# "Alice Weber, the finance director, said ..." — any mix of cases is
# allowed because role appositives are often capitalized ("CEO of Acme").
_APPOSITIVE = (r"(?:\s*,\s*[A-Za-z][\w'’\-]*"
               r"(?:\s+[A-Za-z][\w'’\-]*)*)*")

# Name immediately (modulo appositive/comma) before the verb.
_PRE_NAME_RE = re.compile(rf"\b({_NAME_RUN}){_APPOSITIVE}[,:]?\s*$")
# Pronoun immediately before the verb — checked before the name pattern so
# "He said" is never mistaken for a person named "He".
_PRE_PRONOUN_RE = re.compile(r'\b([Hh]e|[Ss]he|[Tt]hey)\s*$')
# Name after the verb — the journalistic post-position '"..." said Alice.'
_POST_NAME_RE = re.compile(rf'^[,:]?\s+({_NAME_RUN})\b')
# "According to NAME" introducing a sentence.
_ACCORDING_RE = re.compile(rf'\b([Aa]ccording to)\s+({_NAME_RUN})\b')

# Leading tokens that signal a sentence opener rather than a person; they
# are stripped from the front of a matched name run. Weekdays and months
# appear because news sentences open with "On Tuesday the ministry said".
_NAME_STOPWORDS = frozenset((
    'the', 'a', 'an', 'this', 'that', 'these', 'those', 'it', 'there',
    'he', 'she', 'they', 'we', 'you', 'i', 'what', 'who', 'when', 'where',
    'if', 'but', 'and', 'or', 'so', 'because', 'however', 'meanwhile',
    'on', 'in', 'at', 'for', 'with', 'from', 'by', 'about', 'after',
    'before', 'during', 'under', 'over', 'between', 'through', 'without',
    'within', 'across', 'among', 'around', 'toward', 'towards',
    'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday',
    'sunday', 'january', 'february', 'march', 'april', 'june', 'july',
    'august', 'september', 'october', 'november', 'december',
    'yesterday', 'today', 'tomorrow', 'last', 'next', 'according',
))

# Chinese attribution verbs. Single-character verbs (称, 说) and the
# two-character ones alike are only accepted when the character right
# after the verb is punctuation, a quote mark or whitespace — this kills
# the frequent compound words 称为 / 说明 / 小说 etc.
_ZH_VERB_RE = re.compile(r'表示|指出|认为|称|说')
_ZH_PRONOUNS = frozenset(('他', '她', '它', '他们', '她们'))
_ZH_NAME_RUN_RE = re.compile(r'([\u4e00-\u9fff]{1,4})$')
# Function characters that cling to the front of a name run ("该公司表示")
# and are stripped; no segmentation model is used, so this is a heuristic.
_ZH_STRIP_LEADING = '的了是在对向从被把让给跟并而但又也都还就才和与及其这那'
_ZH_AFTER_OK = ('，。：；、！？…“”‘’「」『』"\'.,:;!?()（）-—~')
# "据X报道" (according to X's report) introduces quoted coverage.
_ZH_REPORT_RE = re.compile(r'(据[\u4e00-\u9fff]{1,12}报道)')

# Sentence boundaries. Chinese terminators close a sentence immediately
# (no inter-word space); western ones require the next character to be
# whitespace, an opening quote or the end of the text, which keeps "3.5"
# and "example.org" intact. A '.' preceded by a known abbreviation
# (Dr., Mr., Inc., initials like "John F. Kennedy") never splits.
_EN_TERMINATORS = '.!?…'
_ZH_TERMINATORS = '。！？'
_CLOSERS = '”』」"\'）)]“'
_OPENERS = '“『「„'
_ABBREVIATIONS = frozenset((
    'mr', 'mrs', 'ms', 'dr', 'prof', 'sr', 'jr', 'st', 'vs', 'etc',
    'inc', 'ltd', 'co', 'fig', 'al', 'ed', 'eds', 'vol', 'pp',
))

# Characters allowed between a sentence-terminal quote and the end of its
# sentence when deciding whether the quote "ends" the sentence.
_TRAILING_OK = ' \t\r\n.,;:!?\'"”’』」）)]…。！？，；：'

# How far an attribution pattern may sit into the NEXT sentence and still
# count as the speaker of a sentence-terminal quote.
_EXTENSION_PREFIX_CHARS = 48

# Size of the character window examined before/after an English verb for
# the name or pronoun adjacent to it.
_VERB_WINDOW = 80


class QuoteAttributionAnalyzer(DocProcessor):
    """Pair direct quotes with their attributed speakers in document text.

    News wires, interview transcripts, earnings calls and committee
    reports all carry their most quotable knowledge inside quotation
    marks — but for a knowledge base the raw quotation is only half the
    fact. ``"We will not rest until every customer is refunded," said
    Alice Chen`` is useful precisely because *Alice Chen* is the one who
    committed to it. Retrieval over embeddings blurs that structure away;
    this analyzer recovers it on the way into the knowledge base and
    stamps every quote/speaker pair into document metadata, extending the
    flat ``quote`` kind of ``CitationExtractor`` into structured
    who-said-what records.

    The pipeline is pure ``re`` and character arithmetic — deterministic,
    offline and dependency-free:

    1. quoted spans are located in four styles — ASCII doubles ``"..."``,
       curly doubles ``“...”``, CJK corner brackets ``「...」`` and German
       low-high ``„...“`` — paired within a line;
    2. the text is split into sentences, honoring Chinese terminators
       (which need no following space), western abbreviation periods
       (``Dr.``, ``Mr.``, initials) and closing quotes glued to a
       terminator;
    3. the sentence containing each quote — with the interiors of every
       quote blanked out so the quoted words themselves cannot trigger a
       pattern — is searched for attribution patterns. When the quote
       ends its own sentence and nothing matched, the search extends into
       the next sentence, accepting patterns that start within its first
       48 characters (``"We are disappointed." Alice Weber said in a
       note.``);
    4. when several patterns match, the one nearest the quote wins;
       ties go to the leftmost.

    English patterns (checked per verb occurrence, in order): pronoun
    before the verb (``he/she/they said``), capitalized name run before
    the verb — titles such as ``Dr.`` / ``Mr.`` / ``President`` stay part
    of the name, lowercase particles (``of``, ``van``) glue multi-word
    names and comma appositives between name and verb are skipped — then
    the post-position after the verb (``said Alice Chen``); separately,
    ``according to NAME`` anywhere in the window. Chinese patterns: a
    name run of up to 4 hanzi immediately before 表示/称/说/指出/认为
    (single-character verbs must be followed by punctuation, so 称为 /
    说明 do not fire), the pronouns 他/她/它/他们/她们, and 据X报道.

    Pronoun backoff is a documented heuristic: ``he/she/they`` (and the
    Chinese equivalents) carry no name, so the analyzer looks back
    through the most recent ``speaker_lookback`` attribution events of
    the same document (default 2) and reuses the nearest name found —
    the "speaker tracking" approximation journalists' antecedents
    usually satisfy. A pronoun with no named antecedent in range, or a
    quote with no pattern at all, yields ``speaker_resolved='unknown'``.

    Findings land in metadata: ``quotes`` — a list of
    ``{quote, speaker, speaker_resolved, attribution_text, span}`` dicts
    in document order, capped at ``max_quotes`` (``speaker_resolved`` is
    ``'name'``, ``'pronoun'`` or ``'unknown'``; ``span`` is the
    ``(start, end)`` character range reproducing ``quote`` exactly,
    markers included); ``quote_count`` — the total number of quotes
    found, i.e. before capping, so consumers can detect truncation; and
    ``speakers`` — insertion-ordered ``{name: quote_count}`` over all
    successfully attributed quotes. Documents pass through unfiltered:
    text, id and ordering are untouched, and metadata mappings are
    copied before mutation.

    Known limits, kept honestly: attribution is lexical, not syntactic —
    a rewritten news sentence can defeat any pattern; the Chinese name
    run has no word segmentation, so long modifiers directly before a
    verb may survive into the name; and pronoun backoff assumes the last
    named speaker still holds, with no gender or number checking.

    Attributes:
        max_quotes: Maximum number of quote records kept in
            ``metadata[quotes_key]``; must be >= 1. The default 50 bounds
            metadata growth on quote-dense transcripts.
        speaker_lookback: How many previous attribution events are
            searched (most recent first) when resolving a pronoun; must
            be >= 1. The default 2 matches the typical one-topic-gap of
            news paragraphs.
        quotes_key: Metadata key for the quote record list; an empty
            value disables that stamp.
        count_key: Metadata key for the total (uncapped) quote count; an
            empty value disables that stamp.
        speakers_key: Metadata key for the deduplicated speaker tally;
            an empty value disables that stamp.
    """

    max_quotes: int = 50
    speaker_lookback: int = 2
    quotes_key: str = "quotes"
    count_key: str = "quote_count"
    speakers_key: str = "speakers"

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Stamp quote/speaker pairs into every document's metadata.

        Args:
            origin_docs: Documents to analyze, in batch order.
            query: Query object (unused; attribution depends only on the
                documents' own text).

        Returns:
            List[Document]: The same document objects, in the same
            order, each stamped with quote attribution metadata.
        """
        for doc in origin_docs:
            text = doc.text or ""
            quote_spans = [(m.start(), m.end())
                           for m in _QUOTE_RE.finditer(text)]
            sentences = self._sentence_spans(text)
            blanked = self._blank(text, quote_spans)

            # Speaker tracking: the last `speaker_lookback` attribution
            # events (resolved name or None), most recent last.
            recent = deque(maxlen=self.speaker_lookback)
            hits = []
            speaker_counts = {}

            for qs, qe in quote_spans:
                sent_idx = self._sentence_of(qs, sentences)
                candidates = []
                if sent_idx is not None:
                    lo, hi = sentences[sent_idx]
                    candidates = self._candidates(blanked, lo, hi)
                    if not candidates and self._is_terminal(qe, hi, text) \
                            and sent_idx + 1 < len(sentences):
                        nlo, nhi = sentences[sent_idx + 1]
                        candidates = self._candidates(
                            blanked, nlo, nhi,
                            prefix_limit=_EXTENSION_PREFIX_CHARS)
                best = self._pick((qs, qe), candidates)
                speaker, resolved = self._resolve(best, recent)
                recent.append(speaker if resolved != 'unknown' else None)
                attribution = None
                if best is not None:
                    cs, ce = best['span']
                    attribution = blanked[cs:ce].strip()
                hits.append({
                    'quote': text[qs:qe],
                    'speaker': speaker,
                    'speaker_resolved': resolved,
                    'attribution_text': attribution,
                    'span': (qs, qe),
                })
                if resolved != 'unknown':
                    speaker_counts[speaker] = \
                        speaker_counts.get(speaker, 0) + 1

            meta = dict(doc.metadata or {})
            if self.quotes_key:
                meta[self.quotes_key] = hits[:self.max_quotes]
            if self.count_key:
                meta[self.count_key] = len(hits)
            if self.speakers_key:
                meta[self.speakers_key] = speaker_counts
            doc.metadata = meta
        return origin_docs

    # ------------------------------------------------------------------ #
    # Sentence segmentation
    # ------------------------------------------------------------------ #

    @staticmethod
    def _sentence_spans(text: str) -> List[Tuple[int, int]]:
        """Split text into sentence (start, end) spans.

        A boundary fires after a run of terminators plus any glued
        closing quotes, when the next character is whitespace, an
        opening quote, the end of the text, or when the terminator was
        Chinese (Chinese needs no inter-sentence space). '.' preceded by
        a known abbreviation or a single uppercase initial never splits.

        Args:
            text: Document text.

        Returns:
            List[Tuple[int, int]]: Sentence spans in reading order; a
            text without any terminator yields one whole-text span.
        """
        spans = []
        n = len(text)
        start = 0
        i = 0
        while i < n:
            ch = text[i]
            if ch in _EN_TERMINATORS or ch in _ZH_TERMINATORS:
                if ch == '.' and QuoteAttributionAnalyzer._is_abbreviation(
                        text, i):
                    i += 1
                    continue
                zh = ch in _ZH_TERMINATORS
                j = i + 1
                while j < n and (text[j] in _EN_TERMINATORS
                                 or text[j] in _ZH_TERMINATORS
                                 or text[j] in _CLOSERS):
                    j += 1
                if j >= n or text[j].isspace() or text[j] in _OPENERS or zh:
                    if j > start:
                        spans.append((start, j))
                    while j < n and text[j].isspace():
                        j += 1
                    start = j
                i = j
                continue
            i += 1
        if start < n:
            spans.append((start, n))
        return spans

    @staticmethod
    def _is_abbreviation(text: str, dot: int) -> bool:
        """Report whether the '.' at ``dot`` ends an abbreviation.

        True for known title/company abbreviations (Dr., Mr., Inc., …)
        and for single uppercase initials ("John F. Kennedy"), so that
        "Dr. Maya Patel told …" stays one sentence.

        Args:
            text: Full text.
            dot: Index of the '.' character.

        Returns:
            bool: True when the period must not split a sentence.
        """
        k = dot - 1
        while k >= 0 and text[k].isalpha():
            k -= 1
        word = text[k + 1:dot].lower()
        if not word:
            return False
        if len(word) == 1 and text[dot - 1].isupper():
            return True
        return word in _ABBREVIATIONS

    @staticmethod
    def _sentence_of(pos: int, sentences: List[Tuple[int, int]]) \
            -> Optional[int]:
        """Return the index of the sentence containing offset ``pos``.

        Args:
            pos: Character offset (a quote start).
            sentences: Sentence spans from ``_sentence_spans``.

        Returns:
            Optional[int]: Sentence index, or None when out of range.
        """
        for idx, (lo, hi) in enumerate(sentences):
            if lo <= pos < hi:
                return idx
        return None

    @staticmethod
    def _is_terminal(quote_end: int, sent_end: int, text: str) -> bool:
        """Report whether a quote ends its sentence.

        True when nothing but trailing punctuation/whitespace follows the
        quote's closing mark until the sentence end.

        Args:
            quote_end: End offset of the quote span.
            sent_end: End offset of the containing sentence.
            text: Full text.

        Returns:
            bool: True when the quote is sentence-terminal.
        """
        return all(ch in _TRAILING_OK for ch in text[quote_end:sent_end])

    @staticmethod
    def _blank(text: str, spans: List[Tuple[int, int]]) -> str:
        """Replace every quote span (markers included) with spaces.

        Offsets are preserved, so positions in the returned string map
        one-to-one onto the original text while the quoted words can no
        longer trigger attribution patterns.

        Args:
            text: Original text.
            spans: Quote spans to blank out.

        Returns:
            str: Text with quote spans replaced by spaces.
        """
        chars = list(text)
        for start, end in spans:
            for k in range(start, end):
                chars[k] = ' '
        return ''.join(chars)

    # ------------------------------------------------------------------ #
    # Attribution pattern extraction
    # ------------------------------------------------------------------ #

    def _candidates(self, blanked: str, lo: int, hi: int,
                    prefix_limit: Optional[int] = None) -> List[dict]:
        """Collect attribution candidates inside a context window.

        Args:
            blanked: Text with quote spans blanked (offsets preserved).
            lo: Start offset of the window (sentence start).
            hi: End offset of the window (sentence end).
            prefix_limit: When set, only candidates starting within this
                many characters of ``lo`` are kept — used for the
                next-sentence extension of terminal quotes.

        Returns:
            List[dict]: Candidates as ``{kind, value, span}`` where kind
            is 'name' or 'pronoun' and span is an absolute (start, end)
            range covering the matched pattern.
        """
        ctx = blanked[lo:hi]
        out = []

        for m in _EN_VERB_RE.finditer(ctx):
            vs, ve = m.span()
            if prefix_limit is not None and vs > prefix_limit:
                continue
            pre = ctx[max(0, vs - _VERB_WINDOW):vs]
            pm = _PRE_PRONOUN_RE.search(pre)
            if pm:
                out.append({'kind': 'pronoun', 'value': pm.group(1),
                            'span': (lo + vs - len(pm.group(0)),
                                     lo + ve)})
                continue
            nm = _PRE_NAME_RE.search(pre)
            if nm:
                name = self._clean_en_name(nm.group(1))
                if name:
                    out.append({'kind': 'name', 'value': name,
                                'span': (lo + vs - len(nm.group(0)),
                                         lo + ve)})
                    continue
            xm = _POST_NAME_RE.match(ctx[ve:ve + _VERB_WINDOW])
            if xm:
                name = self._clean_en_name(xm.group(1))
                if name:
                    out.append({'kind': 'name', 'value': name,
                                'span': (lo + vs, lo + ve + len(xm.group(0)))})

        for m in _ACCORDING_RE.finditer(ctx):
            if prefix_limit is not None and m.start() > prefix_limit:
                continue
            name = self._clean_en_name(m.group(2))
            if name:
                out.append({'kind': 'name', 'value': name,
                            'span': (lo + m.start(), lo + m.end())})

        for m in _ZH_VERB_RE.finditer(ctx):
            vs, ve = m.span()
            if prefix_limit is not None and vs > prefix_limit:
                continue
            if ve < len(ctx) and ctx[ve] not in _ZH_AFTER_OK:
                continue
            rm = _ZH_NAME_RUN_RE.search(ctx[max(0, vs - 8):vs])
            if not rm:
                continue
            run = rm.group(1)
            if run in _ZH_PRONOUNS:
                out.append({'kind': 'pronoun', 'value': run,
                            'span': (lo + vs - len(run), lo + ve)})
                continue
            stripped = run.lstrip(_ZH_STRIP_LEADING)
            if len(stripped) >= 2:
                out.append({'kind': 'name', 'value': stripped,
                            'span': (lo + vs - len(run), lo + ve)})

        for m in _ZH_REPORT_RE.finditer(ctx):
            if prefix_limit is not None and m.start() > prefix_limit:
                continue
            name = m.group(0)[1:-2].lstrip(_ZH_STRIP_LEADING)
            if len(name) >= 2:
                out.append({'kind': 'name', 'value': name,
                            'span': (lo + m.start(), lo + m.end())})

        return out

    @staticmethod
    def _clean_en_name(run: str) -> Optional[str]:
        """Strip sentence-opener stopwords from the front of a name run.

        "On Tuesday the President said" first matches the run "On Tuesday
        the President"; dropping leading stopwords (on, Tuesday, the)
        recovers "President". Titles such as Dr./Mr./President are not
        in the stopword set, so they stay part of the name.

        Args:
            run: Whitespace-separated name run as matched.

        Returns:
            Optional[str]: The cleaned name, or None when nothing
            survives the strip (e.g. the run was only "It").
        """
        tokens = run.split()
        while tokens and tokens[0].lower().rstrip('.') in _NAME_STOPWORDS:
            tokens.pop(0)
        return ' '.join(tokens) or None

    # ------------------------------------------------------------------ #
    # Selection and resolution
    # ------------------------------------------------------------------ #

    @staticmethod
    def _pick(quote_span: Tuple[int, int],
              candidates: List[dict]) -> Optional[dict]:
        """Choose the candidate nearest the quote (ties: leftmost).

        Args:
            quote_span: (start, end) of the quote.
            candidates: Candidates from ``_candidates``.

        Returns:
            Optional[dict]: The winning candidate, or None when the list
            is empty.
        """
        best = None
        best_key = None
        for cand in candidates:
            key = (QuoteAttributionAnalyzer._distance(quote_span,
                                                      cand['span']),
                   cand['span'][0])
            if best is None or key < best_key:
                best, best_key = cand, key
        return best

    @staticmethod
    def _distance(quote_span: Tuple[int, int],
                  cand_span: Tuple[int, int]) -> int:
        """Character gap between a quote span and a candidate span.

        Args:
            quote_span: (start, end) of the quote.
            cand_span: (start, end) of the candidate pattern.

        Returns:
            int: 0 when overlapping, otherwise the character distance.
        """
        qs, qe = quote_span
        cs, ce = cand_span
        if ce <= qs:
            return qs - ce
        if cs >= qe:
            return cs - qe
        return 0

    @staticmethod
    def _resolve(cand: Optional[dict],
                 recent: deque) -> Tuple[Optional[str], str]:
        """Resolve a candidate into a (speaker, resolution mode) pair.

        Args:
            cand: Winning candidate (or None for an unattributed quote).
            recent: Speaker-tracking deque of the last attribution
                events (resolved names or None), most recent last.

        Returns:
            Tuple[Optional[str], str]: The speaker (None when unknown)
            and the resolution mode: 'name' for a directly matched name,
            'pronoun' for a pronoun resolved through backoff, 'unknown'
            otherwise.
        """
        if cand is None:
            return None, 'unknown'
        if cand['kind'] == 'name':
            return cand['value'], 'name'
        for name in reversed(recent):
            if name is not None:
                return name, 'pronoun'
        return None, 'unknown'

    # ------------------------------------------------------------------ #
    # Configuration
    # ------------------------------------------------------------------ #

    def _initialize_by_component_configer(
            self, doc_processor_configer: ComponentConfiger) \
            -> 'QuoteAttributionAnalyzer':
        """Initialize and validate the analyzer from component config.

        Validation happens eagerly at load time: a silently misconfigured
        analyzer would stamp wrong metadata deep inside an ingestion
        pipeline, far from the yaml that caused it.

        Args:
            doc_processor_configer: Configuration object.

        Returns:
            QuoteAttributionAnalyzer: The initialized instance.

        Raises:
            ValueError: On an invalid combination of parameter values.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        if hasattr(doc_processor_configer, 'max_quotes') and \
                doc_processor_configer.max_quotes is not None:
            cap = doc_processor_configer.max_quotes
            if isinstance(cap, bool) or not isinstance(cap, int):
                raise ValueError("max_quotes must be an integer")
            self.max_quotes = cap
            if self.max_quotes < 1:
                raise ValueError("max_quotes must be >= 1")

        if hasattr(doc_processor_configer, 'speaker_lookback') and \
                doc_processor_configer.speaker_lookback is not None:
            lookback = doc_processor_configer.speaker_lookback
            if isinstance(lookback, bool) or not isinstance(lookback, int):
                raise ValueError("speaker_lookback must be an integer")
            self.speaker_lookback = lookback
            if self.speaker_lookback < 1:
                raise ValueError("speaker_lookback must be >= 1")

        if hasattr(doc_processor_configer, 'quotes_key') and \
                doc_processor_configer.quotes_key is not None:
            key = doc_processor_configer.quotes_key
            if not isinstance(key, str):
                raise ValueError("quotes_key must be a string")
            self.quotes_key = key

        if hasattr(doc_processor_configer, 'count_key') and \
                doc_processor_configer.count_key is not None:
            key = doc_processor_configer.count_key
            if not isinstance(key, str):
                raise ValueError("count_key must be a string")
            self.count_key = key

        if hasattr(doc_processor_configer, 'speakers_key') and \
                doc_processor_configer.speakers_key is not None:
            key = doc_processor_configer.speakers_key
            if not isinstance(key, str):
                raise ValueError("speakers_key must be a string")
            self.speakers_key = key

        return self
