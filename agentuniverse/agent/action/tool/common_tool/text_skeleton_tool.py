# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20 10:00
# @Author  : 123123213weqw
# @Email   :
# @FileName: text_skeleton_tool.py

import asyncio
import json
from typing import List, Tuple

from agentuniverse.agent.action.tool.tool import Tool

SKELETON_MODE = 'skeleton'
DIGEST_MODE = 'digest'
FIRST_SENTENCES_MODE = 'first_sentences'
LEAD_CHARS_MODE = 'lead_chars'
VALID_MODES = (SKELETON_MODE, DIGEST_MODE, FIRST_SENTENCES_MODE, LEAD_CHARS_MODE)

# Bounds for the lead-character window `n`.
MIN_N = 10
MAX_N = 500
DEFAULT_N = 60

# Bounds for the paragraph cap.
MIN_MAX_PARAGRAPHS = 1
MAX_MAX_PARAGRAPHS = 1000
DEFAULT_MAX_PARAGRAPHS = 200

_ASCII_TERMINATORS = '.!?'
_CJK_TERMINATORS = '\u3002\uff01\uff1f'  # CJK full stop, exclamation, question
_ALL_TERMINATORS = _ASCII_TERMINATORS + _CJK_TERMINATORS

# Omission marker appended when a lead-char excerpt truncates its paragraph.
ELLIPSIS = '\u2026'

# Conservative abbreviation guard: a '.' that terminates one of these tokens
# (case-insensitive) is not treated as a sentence boundary on its own.
_ABBREVIATIONS = frozenset({
    'mr', 'mrs', 'ms', 'dr', 'prof', 'sr', 'jr', 'st', 'vs', 'etc',
    'e.g', 'i.e', 'fig', 'no', 'inc', 'ltd', 'co', 'corp', 'dept', 'univ',
    'approx', 'apt', 'est', 'min', 'max', 'vol', 'pp', 'ed', 'al', 'ca',
    'cf', 'ph.d', 'a.m', 'p.m', 'u.s', 'u.k',
})

# Characters that may open a new sentence after a '.' boundary.
_OPENING_PUNCT = '"\'([{<\u201c\u2018\u300c\u300e\u300a'


def _is_cjk_char(ch: str) -> bool:
    """Return True when `ch` is a CJK / fullwidth code point."""
    code = ord(ch)
    return (0x2E80 <= code <= 0x9FFF
            or 0xF900 <= code <= 0xFAFF
            or 0xFF00 <= code <= 0xFFEF
            or 0x20000 <= code <= 0x3FFFD)


def _preceding_token(text: str, pos: int) -> str:
    """Return the alphanumeric/dot token ending immediately before `pos`."""
    start = pos
    while start > 0 and (text[start - 1].isalnum() or text[start - 1] == '.'):
        start -= 1
    return text[start:pos]


def _is_sentence_boundary(paragraph: str, term_start: int, after_end: int,
                          first_term: str) -> bool:
    """Decide whether the terminator run ending at `after_end` closes a sentence.

    Conservative rules:
      - end of paragraph always closes a sentence;
      - CJK terminators close a sentence immediately;
      - ASCII '.' closes a sentence only when followed by whitespace and a
        sentence-like opening char (uppercase, digit, opening punctuation or
        CJK), and the preceding token is not a guarded abbreviation;
      - '!' and '?' close a sentence when followed by whitespace.
    """
    if after_end >= len(paragraph):
        return True
    if first_term in _CJK_TERMINATORS:
        return True
    if not paragraph[after_end].isspace():
        return False
    if first_term == '.':
        token = _preceding_token(paragraph, term_start)
        if token.lower() in _ABBREVIATIONS:
            return False
        k = after_end
        while k < len(paragraph) and paragraph[k].isspace():
            k += 1
        if k >= len(paragraph):
            return True
        ch = paragraph[k]
        return (ch.isupper() or ch.isdigit() or ch in _OPENING_PUNCT
                or _is_cjk_char(ch))
    return True


def _split_sentences(paragraph: str) -> List[str]:
    """Split a single paragraph into sentences (conservative segmentation)."""
    sentences: List[str] = []
    total = len(paragraph)
    start = 0
    i = 0
    while i < total:
        ch = paragraph[i]
        if ch not in _ALL_TERMINATORS:
            i += 1
            continue
        j = i
        while j < total and paragraph[j] in _ALL_TERMINATORS:
            j += 1
        if _is_sentence_boundary(paragraph, i, j, ch):
            sentence = paragraph[start:j].strip()
            if sentence:
                sentences.append(sentence)
            start = j
        i = j
    tail = paragraph[start:].strip()
    if tail:
        sentences.append(tail)
    return sentences


def _split_paragraphs(text: str) -> List[Tuple[str, int, int]]:
    """Split text on blank lines; return (paragraph, start, end) code-point spans.

    Spans refer to the trimmed paragraph block inside the original text, so
    they are safe for direct slicing on any unicode content (CJK included).
    """
    paragraphs: List[Tuple[str, int, int]] = []
    lines = text.split('\n')
    offset = 0
    current_lines: List[str] = []
    current_start = 0
    for line in lines:
        if line.strip():
            if not current_lines:
                current_start = offset + (len(line) - len(line.lstrip()))
            current_lines.append(line)
        elif current_lines:
            block = '\n'.join(current_lines).strip()
            paragraphs.append((block, current_start, current_start + len(block)))
            current_lines = []
        offset += len(line) + 1
    if current_lines:
        block = '\n'.join(current_lines).strip()
        paragraphs.append((block, current_start, current_start + len(block)))
    return paragraphs


def _lead_excerpt(paragraph: str, n: int) -> str:
    """First `n` code points of `paragraph`, with an ellipsis when truncated."""
    if len(paragraph) > n:
        return paragraph[:n] + ELLIPSIS
    return paragraph


def _error(message: str) -> str:
    return json.dumps({'error': message, 'status': 'error'}, ensure_ascii=False)


class TextSkeletonTool(Tool):
    """Deterministic, pure-stdlib text skeleton / digest tool.

    Modes:
      - skeleton: per blank-line paragraph, join the first sentence, a
        lead-character excerpt and the last sentence with ' | '.
      - digest: one combined preview of the whole text plus total stats.
      - first_sentences: the classic outline-from-prose (first sentence per
        paragraph).
      - lead_chars: first N characters per paragraph.
    """

    def execute(self,
                text: str,
                mode: str = SKELETON_MODE,
                n: int = DEFAULT_N,
                include_first_sentence: bool = True,
                include_lead_chars: bool = True,
                include_last_sentence: bool = True,
                include_paragraph_index: bool = False,
                include_char_span: bool = False,
                max_paragraphs: int = DEFAULT_MAX_PARAGRAPHS) -> str:
        # ---- strict validation -------------------------------------------------
        if not isinstance(text, str):
            return _error('text must be a string.')
        if not text.strip():
            return _error('text is empty or contains only whitespace.')
        if mode not in VALID_MODES:
            return _error(
                f'Invalid mode: {mode!r}. Valid modes are: {", ".join(VALID_MODES)}.')
        if isinstance(n, bool) or not isinstance(n, int):
            return _error('n must be an integer.')
        if not MIN_N <= n <= MAX_N:
            return _error(f'n must be between {MIN_N} and {MAX_N}.')
        if mode == SKELETON_MODE and not (
                include_first_sentence or include_lead_chars or include_last_sentence):
            return _error(
                'At least one skeleton component must be enabled '
                '(include_first_sentence, include_lead_chars or include_last_sentence).')
        for name, value in (('include_first_sentence', include_first_sentence),
                            ('include_lead_chars', include_lead_chars),
                            ('include_last_sentence', include_last_sentence),
                            ('include_paragraph_index', include_paragraph_index),
                            ('include_char_span', include_char_span)):
            if not isinstance(value, bool):
                return _error(f'{name} must be a boolean.')
        if isinstance(max_paragraphs, bool) or not isinstance(max_paragraphs, int):
            return _error('max_paragraphs must be an integer.')
        if not MIN_MAX_PARAGRAPHS <= max_paragraphs <= MAX_MAX_PARAGRAPHS:
            return _error(
                f'max_paragraphs must be between {MIN_MAX_PARAGRAPHS} '
                f'and {MAX_MAX_PARAGRAPHS}.')

        # ---- paragraph extraction ---------------------------------------------
        paragraphs = _split_paragraphs(text)
        total_paragraphs = len(paragraphs)
        paragraphs_omitted = max(0, total_paragraphs - max_paragraphs)
        paragraphs = paragraphs[:max_paragraphs]

        try:
            if mode == SKELETON_MODE:
                return self._skeleton(
                    paragraphs, n,
                    include_first_sentence, include_lead_chars, include_last_sentence,
                    include_paragraph_index, include_char_span,
                    total_paragraphs, paragraphs_omitted)
            if mode == DIGEST_MODE:
                return self._digest(text, paragraphs,
                                    total_paragraphs, paragraphs_omitted)
            if mode == FIRST_SENTENCES_MODE:
                return self._first_sentences(paragraphs, total_paragraphs,
                                             paragraphs_omitted)
            return self._lead_chars(paragraphs, n, total_paragraphs,
                                    paragraphs_omitted)
        except Exception as e:  # pragma: no cover - defensive guard
            return _error(f'Failed to build text skeleton: {e}')

    async def async_execute(self, **kwargs):
        return await asyncio.to_thread(self.execute, **kwargs)

    # ---- mode implementations ------------------------------------------------
    def _skeleton(self, paragraphs, n,
                  include_first_sentence, include_lead_chars, include_last_sentence,
                  include_paragraph_index, include_char_span,
                  total_paragraphs, paragraphs_omitted) -> str:
        items = []
        for idx, (para, start, end) in enumerate(paragraphs):
            sentences = _split_sentences(para)
            components = []
            if include_first_sentence and sentences:
                components.append(sentences[0])
            if include_lead_chars:
                components.append(_lead_excerpt(para, n))
            # For single-sentence paragraphs the last sentence duplicates the
            # first, so it is only emitted when the first is disabled.
            if (include_last_sentence and sentences
                    and (len(sentences) > 1 or not include_first_sentence)):
                components.append(sentences[-1])
            item = {'skeleton': ' | '.join(components)}
            if include_paragraph_index:
                item['paragraph_index'] = idx
            if include_char_span:
                item['char_span'] = [start, end]
            items.append(item)
        result = {
            'mode': SKELETON_MODE,
            'paragraph_count': total_paragraphs,
            'n': n,
            'skeletons': items,
            'status': 'success',
        }
        if paragraphs_omitted:
            result['paragraphs_omitted'] = paragraphs_omitted
        return json.dumps(result, ensure_ascii=False)

    def _digest(self, text, paragraphs,
                total_paragraphs, paragraphs_omitted) -> str:
        first_sentences = [_split_sentences(p)[0] for p, _, _ in paragraphs]
        sentence_count = sum(len(_split_sentences(p)) for p, _, _ in paragraphs)
        head = first_sentences[0]
        if len(first_sentences) > 1:
            digest = f'{head} {ELLIPSIS} {first_sentences[-1]}'
        else:
            digest = head
        result = {
            'mode': DIGEST_MODE,
            'paragraph_count': total_paragraphs,
            'sentence_count': sentence_count,
            'char_count': len(text),
            'digest': digest,
            'status': 'success',
        }
        if paragraphs_omitted:
            result['paragraphs_omitted'] = paragraphs_omitted
        return json.dumps(result, ensure_ascii=False)

    def _first_sentences(self, paragraphs, total_paragraphs,
                         paragraphs_omitted) -> str:
        result = {
            'mode': FIRST_SENTENCES_MODE,
            'paragraph_count': total_paragraphs,
            'first_sentences': [
                _split_sentences(p)[0] for p, _, _ in paragraphs
            ],
            'status': 'success',
        }
        if paragraphs_omitted:
            result['paragraphs_omitted'] = paragraphs_omitted
        return json.dumps(result, ensure_ascii=False)

    def _lead_chars(self, paragraphs, n, total_paragraphs,
                    paragraphs_omitted) -> str:
        result = {
            'mode': LEAD_CHARS_MODE,
            'n': n,
            'paragraph_count': total_paragraphs,
            'leads': [_lead_excerpt(p, n) for p, _, _ in paragraphs],
            'status': 'success',
        }
        if paragraphs_omitted:
            result['paragraphs_omitted'] = paragraphs_omitted
        return json.dumps(result, ensure_ascii=False)
