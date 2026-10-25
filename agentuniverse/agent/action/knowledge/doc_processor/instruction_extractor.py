# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @FileName: instruction_extractor.py

import re
from bisect import bisect_right
from typing import List, Optional, Tuple

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

# Characters that terminate a sentence: Latin and CJK full stops,
# exclamation marks and question marks.
_TERMINAL_CHARS = ".!?。！？"

# Closing quotes / brackets swallowed into the finished sentence right
# after its terminal punctuation, so spans like '"Click OK?"' stay whole.
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

# A numbered-list item line: optional indentation, digits, then '.' or ')'
# followed by whitespace or end of line. The lookahead keeps "3.14 is pi"
# (decimal at line start) and "1.Install" (missing space) out of the item
# class, matching the intent of the r'^\s*\d+[.)]' pattern. No leading '^':
# the pattern is only ever used with Pattern.match(text, line_start,
# line_end), which anchors the match at line_start (a compiled '^' would
# still match at the string's real beginning, not at pos).
_NUMBERED_ITEM = re.compile(r"\s*\d+[.)](?=\s|$)")

# Heading and table row prefixes. Sentences starting on such a line are
# structural fragments, never instructions, and excluded lines also break
# numbered-step context when walking to the previous line.
_EXCLUDED_LINE_PREFIXES = "#|"

# Chinese imperative openers. A sentence beginning with one of these
# characters is an instruction (请输入密码。 / 务必检查配置。 / 先安装依赖。 /
# 然后重启服务。 / 接着点击确定。). Ordered for deterministic iteration.
_ZH_IMPERATIVE_MARKERS = ("请", "务必", "先", "然后", "接着")

# Second-person directive patterns, matched anywhere inside the sentence,
# case-insensitively: "you must", "you should", "you need to".
_EN_DIRECTIVE = re.compile(r"\byou\s+(?:must|should|need\s+to)\b",
                           re.IGNORECASE)

# Chinese second-person directive patterns, matched anywhere inside the
# sentence.
_ZH_DIRECTIVE = ("你需要", "你必须")

# First alphabetic run of a sentence, skipping leading punctuation, digits
# and quotes ("\"Click" -> "click"; "1." cannot leak in because digits are
# skipped too). CJK characters are deliberately NOT skipped, so an English
# verb buried after Chinese text (设置install参数) is not matched.
_FIRST_EN_WORD = re.compile(r"^[^A-Za-z\u4e00-\u9fff]*([A-Za-z]+)")

# Any alphanumeric or CJK character — the definition of a "word-bearing"
# token used by the word counter and the content checks.
_HAS_WORD_CHAR = re.compile(r"[A-Za-z0-9\u4e00-\u9fff]")

# The past-tense heuristic: a pure-alphabetic token of at least five
# letters ending in "ed" ("completed", "installed", "failed"). Used to
# reject noun-subject sentences like "Install completed successfully."
_PAST_TENSE = re.compile(r"[A-Za-z]{3,}ed")

# The bundled imperative verb list — exactly 120 common English verbs that
# open instruction sentences in manuals, SOPs and how-to documents. Curated
# in six groups:
#
#   1. task-mandated core actions (41): install open click select enter
#      press set add remove create delete run execute check verify ensure
#      avoid configure enable disable restart update copy paste save
#      download upload choose navigate scroll tap swipe type write read
#      connect disconnect launch close stop start
#   2. installation & lifecycle (9): uninstall reinstall upgrade downgrade
#      deploy initialize register activate deactivate
#   3. files & data (23): rename move cut load import export backup
#      restore archive extract compress unpack edit modify replace find
#      search filter sort merge split clean clear
#   4. build & execution (13): terminate build compile test debug commit
#      push pull fetch clone invoke schedule retry
#   5. UI interaction (9): hover drag drop deselect toggle expand collapse
#      minimize maximize
#   6. input, output & workflow (25): input fill insert print review
#      approve reject submit send share notify go visit browse locate
#      follow switch exit continue proceed repeat skip wait refresh reload
#
# Deliberate exclusions: "note" (overwhelmingly a noun/admonition label at
# line start: "Note that...") and similar admonition words (warning, tip,
# important), "log" ("Log entries are..."), and words that are nouns far
# more often than imperatives (step, file, list, option). Residual
# noun/verb ambiguity ("Search results appear", "Test cases cover") is
# reduced — not eliminated — by the past-tense guard documented in
# InstructionExtractor._imperative_verb.
_IMPERATIVE_VERB_LIST = (
    # 1. task-mandated core actions (41)
    "install", "open", "click", "select", "enter", "press", "set", "add",
    "remove", "create", "delete", "run", "execute", "check", "verify",
    "ensure", "avoid", "configure", "enable", "disable", "restart",
    "update", "copy", "paste", "save", "download", "upload", "choose",
    "navigate", "scroll", "tap", "swipe", "type", "write", "read",
    "connect", "disconnect", "launch", "close", "stop", "start",
    # 2. installation & lifecycle (9)
    "uninstall", "reinstall", "upgrade", "downgrade", "deploy",
    "initialize", "register", "activate", "deactivate",
    # 3. files & data (23)
    "rename", "move", "cut", "load", "import", "export", "backup",
    "restore", "archive", "extract", "compress", "unpack", "edit",
    "modify", "replace", "find", "search", "filter", "sort", "merge",
    "split", "clean", "clear",
    # 4. build & execution (13)
    "terminate", "build", "compile", "test", "debug", "commit", "push",
    "pull", "fetch", "clone", "invoke", "schedule", "retry",
    # 5. UI interaction (9)
    "hover", "drag", "drop", "deselect", "toggle", "expand", "collapse",
    "minimize", "maximize",
    # 6. input, output & workflow (25)
    "input", "fill", "insert", "print", "review", "approve", "reject",
    "submit", "send", "share", "notify", "go", "visit", "browse",
    "locate", "follow", "switch", "exit", "continue", "proceed",
    "repeat", "skip", "wait", "refresh", "reload",
)

# Membership view of the verb list. Iteration for classification always
# goes through _FIRST_EN_WORD + this set, so set ordering never leaks into
# results.
_IMPERATIVE_VERBS = frozenset(_IMPERATIVE_VERB_LIST)

# Line kinds produced by the line table.
_LINE_PLAIN = "plain"
_LINE_BLANK = "blank"
_LINE_ITEM = "item"
_LINE_EXCLUDED = "excluded"


class InstructionExtractor(DocProcessor):
    """Find imperative instruction sentences and stamp them into metadata.

    Manuals, SOPs and how-to documents are written as commands: "Install
    the package first.", "Click OK to continue.", "请输入用户名。", "You must
    back up the database before upgrading." Those action sentences are the
    part a knowledge base most wants to isolate — for procedure
    reconstruction, checklist mining and instruction-aware retrieval — yet
    they are buried in running prose. Existing pre-processing components
    cover neighbouring concerns (QuestionDetector finds questions,
    SentencePositionTagger-style utilities record where a sentence sits)
    but nothing identifies *instructions*. This component walks every
    document, splits it into sentences and classifies each sentence as an
    instruction or not — offline, deterministically, with no model call —
    then stamps the hits into ``metadata['instructions']`` with aggregate
    counts.

    Sentence segmentation is deliberately conservative and belongs to the
    same family as QuestionDetector: sentences end at ``. ! ?`` and their
    CJK counterparts ``。！？``， with three English guards on the dot — known
    abbreviations ("Dr. Smith asked..."), single-letter initials ("J. K.
    Rowling", "e.g.") and decimals ("3.14") do not split; a trailing
    terminal-punctuation run plus closing quotes belongs to the sentence
    it terminates. On top of that, document *structure* is respected:
    sentences never cross into a heading (``#``) or table row (``|``)
    line, never survive past the end of a numbered-item line or a blank
    (paragraph) line, and sentences starting on heading/table lines are
    dropped as structural fragments.

    A sentence counts as an instruction when, in priority order:

    1. **imperative** — it begins with a verb from the bundled list of 120
       common English imperative verbs (see ``_IMPERATIVE_VERB_LIST``),
       matched case-insensitively as a whole word with leading quotes and
       punctuation allowed. Two guards keep noun-subject sentences out:
       something must follow the verb (a bare "Install." is a husk), and
       the next word must not look like a past-tense verb — a pure
       alphabetic token ending in "ed" with at least three letters before
       the suffix — so "Install completed successfully." is rejected. The
       heuristic over-rejects participle adjectives ("Install required
       packages") and -ed nouns of five-plus letters, which is the
       conservative direction; short -ed words ("seed", "need") and
       residual noun/verb ambiguity with a non--ed second word ("Search
       results appear") pass through and are accepted.
    2. **zh_imperative** — it begins with a Chinese imperative marker
       (请 / 务必 / 先 / 然后 / 接着) followed by at least one more
       word-bearing character.
    3. **directive** — it contains a second-person directive: English
       "you must" / "you should" / "you need to" (case-insensitive) or
       Chinese 你需要 / 你必须.
    4. **step** — it has no independent evidence but lives in
       numbered-step context: it starts on a line beginning with a
       numbered marker ``N.`` / ``N)`` (the marker itself is excluded from
       the span, so ``text`` starts at the sentence), or it starts on a
       plain line whose immediately preceding line is a numbered item
       (markdown lazy continuation; a blank line ends the context). Step
       hits carry inherited, lower confidence — the context says "this is
       a procedure", the sentence itself may be prose.

    Negative guards applied before every channel: sentences ending in
    ``?`` / ``？`` are questions and never instructions, and heading /
    table-row fragments are excluded as described above.

    Each hit is ``{"kind": "imperative" | "zh_imperative" | "step" |
    "directive", "text": str, "span": (start, end), "verb": str | None}``
    where ``span`` are character offsets into the original document text
    with ``text == document.text[start:end]`` — spans are non-overlapping
    and ordered — and ``verb`` is the matched verb for English imperatives
    and None for every other kind.

    Aggregates land next to the list: ``metadata['instruction_count']``
    is the total number of instruction sentences found (never capped),
    and ``metadata['has_procedure']`` is True when at least
    ``procedure_threshold`` (default 3) sentences live in numbered-step
    context — the arithmetic for "this document documents a multi-step
    procedure". Segments with fewer than ``min_words`` words are ignored
    entirely.

    Every document passes through untouched — text, id and existing
    metadata entries are never modified, and metadata mappings are copied
    before mutation. The component is pure Python with zero dependencies
    and deterministic across runs and processes.

    Attributes:
        max_instructions: Maximum number of hits kept in
            ``metadata['instructions']``; must be >= 0. The count metadata
            is always the uncapped total, so a capped list never hides the
            true magnitude.
        min_words: Minimum number of words (whitespace tokens containing
            at least one alphanumeric character) for a segment to count
            as a sentence; must be >= 1.
        procedure_threshold: Number of numbered-context sentences required
            for ``metadata['has_procedure']`` to become True; must be
            >= 1.
        instructions_key: Metadata key the (capped) hit list is written
            to; an empty value disables that stamp.
        count_key: Metadata key the uncapped instruction count is written
            to; an empty value disables that stamp.
        has_procedure_key: Metadata key the procedure flag is written to;
            an empty value disables that stamp.
    """

    max_instructions: int = 100
    min_words: int = 1
    procedure_threshold: int = 3
    instructions_key: str = "instructions"
    count_key: str = "instruction_count"
    has_procedure_key: str = "has_procedure"

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Stamp detected instructions into every document's metadata.

        Args:
            origin_docs: Documents to analyse, in batch order.
            query: Query object (unused; detection depends only on the
                documents' own text).

        Returns:
            List[Document]: The same documents, in the same order, each
            carrying the instruction hits and aggregates in its metadata.
        """
        if not origin_docs:
            return []

        for doc in origin_docs:
            hits, numbered_sentences = self._analyze(doc.text or "")
            if self.instructions_key:
                self._stamp(doc, self.instructions_key,
                            hits[:self.max_instructions])
            if self.count_key:
                self._stamp(doc, self.count_key, len(hits))
            if self.has_procedure_key:
                self._stamp(doc, self.has_procedure_key,
                            numbered_sentences >= self.procedure_threshold)
        return origin_docs

    # ------------------------------------------------------------------ #
    # Detection
    # ------------------------------------------------------------------ #

    def _analyze(self, text: str) -> Tuple[List[dict], int]:
        """Segment text and classify every sentence.

        Args:
            text: Raw document text (None treated as empty).

        Returns:
            tuple: (hits, numbered_sentences) where hits is the ordered
            list of instruction dictionaries and numbered_sentences counts
            every sentence living in numbered-step context, classified as
            an instruction or not (each numbered item IS a step of the
            procedure, including question or declarative items).
        """
        hits: List[dict] = []
        numbered_sentences = 0
        for start, end, numbered in self._segments(text):
            if numbered:
                numbered_sentences += 1
            sentence = text[start:end]
            hit = self._classify(sentence, numbered)
            if hit is not None:
                hit["text"] = sentence
                hit["span"] = (start, end)
                hits.append(hit)
        return hits, numbered_sentences

    def _classify(self, sentence: str, numbered: bool) -> Optional[dict]:
        """Classify one sentence as an instruction, or not.

        Priority: question guard > imperative verb > Chinese imperative
        marker > second-person directive > numbered-step context. This
        makes "Install the package you need to keep." an imperative (verb
        evidence wins over the directive phrase) and "1. You must back up
        first." a directive rather than a step.

        Args:
            sentence: Sentence text, exactly as sliced from the document.
            numbered: Whether the sentence lives in numbered-step context.

        Returns:
            dict: ``{"kind": ..., "verb": ...}`` for an instruction,
            otherwise None.
        """
        if self._is_question(sentence):
            return None
        verb = self._imperative_verb(sentence)
        if verb is not None:
            return {"kind": "imperative", "verb": verb}
        marker = self._zh_marker(sentence)
        if marker is not None:
            return {"kind": "zh_imperative", "verb": None}
        if self._is_directive(sentence):
            return {"kind": "directive", "verb": None}
        if numbered:
            return {"kind": "step", "verb": None}
        return None

    @staticmethod
    def _is_question(sentence: str) -> bool:
        """Report whether a sentence terminates with a question mark.

        Terminal ``?`` / ``？`` (after stripping closing quotes) marks the
        sentence as a question — questions are never instructions, even
        when they open with an imperative verb ("Install this one?") or
        sit on a numbered line.

        Args:
            sentence: Sentence text.

        Returns:
            bool: True when the sentence asks rather than commands.
        """
        return sentence.rstrip(_CLOSING_CHARS).endswith(("?", "？"))

    @staticmethod
    def _imperative_verb(sentence: str) -> Optional[str]:
        """Return the imperative verb opening a sentence, if any.

        The first English word is extracted (leading punctuation, digits
        and quotes skipped) and looked up in the bundled verb list,
        case-insensitively. Two guards then apply:

        1. something word-bearing must follow the verb — a bare
           "Install." or "Click..." with nothing after it is a husk;
        2. the next word must not look like a past-tense verb: a pure
           alphabetic token ending in "ed" with at least three letters
           before the suffix ("completed", "failed"). This rejects the
           noun-subject pattern "Install completed successfully." /
           "Update failed on three nodes." at the cost of over-rejecting
           participle adjectives ("Install required packages") — the
           conservative direction. Short -ed words ("need", "seed",
           "red") stay below the letter threshold and pass.

        Args:
            sentence: Sentence text.

        Returns:
            str: The lowercased verb (e.g. "install"), or None.
        """
        match = _FIRST_EN_WORD.match(sentence)
        if match is None:
            return None
        word = match.group(1).lower()
        if word not in _IMPERATIVE_VERBS:
            return None
        rest = sentence[match.end(1):]
        for token in rest.split():
            if not _HAS_WORD_CHAR.search(token):
                continue
            # Strip punctuation from the token edges ("OK," -> "OK",
            # "Ctrl+C" keeps its plus because it is not an edge).
            first = last = -1
            for index, char in enumerate(token):
                if _HAS_WORD_CHAR.match(char):
                    if first < 0:
                        first = index
                    last = index
            core = token[first:last + 1]
            if _PAST_TENSE.fullmatch(core):
                return None
            return word
        return None

    @staticmethod
    def _zh_marker(sentence: str) -> Optional[str]:
        """Return the Chinese imperative marker opening a sentence.

        The marker (请 / 务必 / 先 / 然后 / 接着) must be the sentence's
        first character and must be followed by at least one more
        alphanumeric or CJK character, so the husk "请。" is rejected.

        Args:
            sentence: Sentence text.

        Returns:
            str: The matched marker (e.g. "请"), or None.
        """
        for marker in _ZH_IMPERATIVE_MARKERS:
            if sentence.startswith(marker):
                rest = sentence[len(marker):]
                if _HAS_WORD_CHAR.search(rest):
                    return marker
                return None
        return None

    @staticmethod
    def _is_directive(sentence: str) -> bool:
        """Report whether a sentence carries a second-person directive.

        English "you must" / "you should" / "you need to"
        (case-insensitive, word boundaries respected) or Chinese 你需要 /
        你必须 anywhere inside the sentence ("Before you proceed, you
        should read the guide."). Questions were already excluded by the
        caller's guard.

        Args:
            sentence: Sentence text.

        Returns:
            bool: True when a directive phrase is present.
        """
        if _EN_DIRECTIVE.search(sentence):
            return True
        return any(marker in sentence for marker in _ZH_DIRECTIVE)

    # ------------------------------------------------------------------ #
    # Segmentation
    # ------------------------------------------------------------------ #

    def _segments(self, text: str) -> List[Tuple[int, int, bool]]:
        """Split text into sentence spans with numbered-context flags.

        Family-style conservative segmentation (terminal characters with
        abbreviation / initial / decimal / ellipsis guards, terminal runs
        plus closing quotes swallowed, leading whitespace skipped), plus
        structure awareness:

        * a sentence never crosses into a heading (``#``) or table (``|``)
          line, past the end of a numbered-item line, or across a blank
          (paragraph) line — plain-to-plain line breaks are soft wraps
          and sentences continue across them;
        * sentences starting on heading/table lines are dropped entirely
          (structural fragments);
        * on a numbered-item line the ``N.`` / ``N)`` marker is excluded
          from the span, so ``text`` begins at the sentence itself;
        * the third tuple element reports numbered-step context: the
          sentence's own line carries a numbered marker, or its line is
          a plain lazy continuation of the immediately preceding
          numbered-item line (a blank or excluded line in between ends
          the context).

        Args:
            text: Raw document text.

        Returns:
            List[Tuple[int, int, bool]]: Ordered, non-overlapping
            (start, end, numbered) character offsets; every span holds at
            least ``min_words`` words.
        """
        text = text or ""
        length = len(text)
        if not length:
            return []

        lines, line_starts = self._line_table(text)
        segments: List[Tuple[int, int, bool]] = []

        def line_index_of(position: int) -> int:
            return bisect_right(line_starts, position) - 1

        def emit(start: int, end: int) -> None:
            if end <= start:
                return
            index = line_index_of(start)
            line = lines[index]
            if line["kind"] == _LINE_EXCLUDED:
                return
            if line["kind"] == _LINE_ITEM and start == line["content"]:
                # Skip the "N." marker so spans begin at the sentence.
                marker_end = line["marker_end"]
                while marker_end < end and text[marker_end].isspace():
                    marker_end += 1
                start = marker_end
                if start >= end:
                    return
            numbered = line["kind"] == _LINE_ITEM or (
                line["kind"] == _LINE_PLAIN and index > 0 and
                lines[index - 1]["kind"] == _LINE_ITEM)
            if self._word_count(text[start:end]) >= self.min_words:
                segments.append((start, end, numbered))

        start = 0
        while start < length and text[start].isspace():
            start += 1
        i = start
        while i < length:
            char = text[i]
            if char == "\n":
                index = line_index_of(i)
                current = lines[index]
                follow = lines[index + 1] if index + 1 < len(lines) else None
                hard_close = current["kind"] != _LINE_PLAIN or (
                    follow is not None and follow["kind"] != _LINE_PLAIN)
                if hard_close:
                    end = i
                    while end > start and text[end - 1].isspace():
                        end -= 1
                    emit(start, end)
                    start = i + 1
                    while start < length and text[start].isspace():
                        start += 1
                    i = start
                else:
                    i += 1
                continue
            if char in _TERMINAL_CHARS and self._is_boundary(text, i):
                end = i + 1
                # A run of terminal punctuation ("？！", "!!") plus any
                # closing quotes belongs to the sentence it terminates.
                while end < length and text[end] in _TERMINAL_CHARS:
                    end += 1
                while end < length and text[end] in _CLOSING_CHARS:
                    end += 1
                emit(start, end)
                start = end
                while start < length and text[start].isspace():
                    start += 1
                i = start
                continue
            i += 1
        # Trailing sentence without terminal punctuation.
        if start < length:
            end = length
            while end > start and text[end - 1].isspace():
                end -= 1
            emit(start, end)
        return segments

    @staticmethod
    def _line_table(text: str) -> Tuple[List[dict], List[int]]:
        """Classify every line of the text for structure-aware splitting.

        Args:
            text: Full document text.

        Returns:
            tuple: (lines, line_starts) where lines is a list of dicts
            with ``start`` / ``end`` (excluding the newline),
            ``content`` (first non-space offset), ``kind`` (plain, blank,
            item, excluded) and ``marker_end`` (end of the ``N.`` marker
            for item lines), and line_starts is the sorted list of line
            start offsets for bisect lookups.
        """
        lines: List[dict] = []
        position = 0
        length = len(text)
        while position < length:
            newline = text.find("\n", position)
            if newline == -1:
                end, follow = length, None
            else:
                end, follow = newline, newline + 1
            content = position
            while content < end and text[content].isspace():
                content += 1
            line = {"start": position, "end": end, "follow": follow,
                    "content": content, "kind": _LINE_PLAIN,
                    "marker_end": None}
            if content == end:
                line["kind"] = _LINE_BLANK
            elif text[content] in _EXCLUDED_LINE_PREFIXES:
                line["kind"] = _LINE_EXCLUDED
            else:
                marker = _NUMBERED_ITEM.match(text, position, end)
                if marker is not None:
                    line["kind"] = _LINE_ITEM
                    line["marker_end"] = marker.end()
            lines.append(line)
            position = end + 1 if newline != -1 else length
        return lines, [line["start"] for line in lines]

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
        # Ellipsis "..." splits only at its final dot.
        if index + 1 < len(text) and text[index + 1] == ".":
            return False
        # Decimal point inside a number.
        if index > 0 and text[index - 1].isdigit() and \
                index + 1 < len(text) and text[index + 1].isdigit():
            return False
        # Alpha run immediately before the dot.
        j = index
        while j > 0 and text[j - 1].isalpha():
            j -= 1
        word = text[j:index]
        # Single-letter initial: "J.", "e.g.", "a.m.".
        if len(word) == 1:
            return False
        return word.lower() not in _ABBREVIATIONS

    @staticmethod
    def _word_count(sentence: str) -> int:
        """Count word-bearing whitespace tokens in a sentence.

        A token counts when it contains at least one alphanumeric or CJK
        character; punctuation-only husks do not. CJK sentences without
        spaces count as a single word.

        Args:
            sentence: Sentence text.

        Returns:
            int: Number of word-bearing tokens.
        """
        return sum(1 for token in sentence.split()
                   if _HAS_WORD_CHAR.search(token))

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
            -> 'InstructionExtractor':
        """Initialize and validate the extractor from component config.

        Validation happens eagerly at load time: a misconfigured
        extractor that silently detected nothing would be far harder to
        notice in production than a startup failure.

        Args:
            doc_processor_configer: Configuration object.

        Returns:
            InstructionExtractor: The initialized instance.

        Raises:
            ValueError: On an invalid combination of parameter values.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        if hasattr(doc_processor_configer, "max_instructions") and \
                doc_processor_configer.max_instructions is not None:
            cap = doc_processor_configer.max_instructions
            if isinstance(cap, bool) or not isinstance(cap, int):
                raise ValueError("max_instructions must be an integer")
            self.max_instructions = cap
            if self.max_instructions < 0:
                raise ValueError("max_instructions must be >= 0")

        if hasattr(doc_processor_configer, "min_words") and \
                doc_processor_configer.min_words is not None:
            words = doc_processor_configer.min_words
            if isinstance(words, bool) or not isinstance(words, int):
                raise ValueError("min_words must be an integer")
            self.min_words = words
            if self.min_words < 1:
                raise ValueError("min_words must be >= 1")

        if hasattr(doc_processor_configer, "procedure_threshold") and \
                doc_processor_configer.procedure_threshold is not None:
            threshold = doc_processor_configer.procedure_threshold
            if isinstance(threshold, bool) or not isinstance(threshold, int):
                raise ValueError("procedure_threshold must be an integer")
            self.procedure_threshold = threshold
            if self.procedure_threshold < 1:
                raise ValueError("procedure_threshold must be >= 1")

        if hasattr(doc_processor_configer, "instructions_key") and \
                doc_processor_configer.instructions_key is not None:
            key = doc_processor_configer.instructions_key
            if not isinstance(key, str):
                raise ValueError("instructions_key must be a string")
            self.instructions_key = key

        if hasattr(doc_processor_configer, "count_key") and \
                doc_processor_configer.count_key is not None:
            key = doc_processor_configer.count_key
            if not isinstance(key, str):
                raise ValueError("count_key must be a string")
            self.count_key = key

        if hasattr(doc_processor_configer, "has_procedure_key") and \
                doc_processor_configer.has_procedure_key is not None:
            key = doc_processor_configer.has_procedure_key
            if not isinstance(key, str):
                raise ValueError("has_procedure_key must be a string")
            self.has_procedure_key = key

        return self
