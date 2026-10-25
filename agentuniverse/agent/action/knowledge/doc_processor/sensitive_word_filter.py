# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/15
# @Author  : dxz0069
# @FileName: sensitive_word_filter.py

import os
from typing import List, Optional, Tuple

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

HITS_METADATA_KEY = "sensitive_word_hits"


class SensitiveWordFilter(DocProcessor):
    """Word list based sensitive content interception and masking.

    Scans every document with an Aho-Corasick automaton built from the
    configured word list and then either masks the matched words inside the
    text or blocks whole documents that contain them:

    - mode `mask`: every match is replaced by `mask_char` repeated to the
      length of the word, the document itself is kept.
    - mode `block`: documents whose unique match count reaches
      `block_threshold` are dropped from the result, others pass through.

    Words can be configured inline (`words`) and/or loaded from a word file
    (`word_file`, one word per line, `#` starts a comment). Matching is
    case-insensitive by default.

    Attributes:
        words: The inline sensitive word list.
        word_file: Path of a word list file, one word per line.
        mode: `mask` to replace matches, `block` to drop documents.
        mask_char: The character used to mask matches in `mask` mode.
        case_sensitive: Whether matching is case sensitive (default False).
        block_threshold: Unique match count at which a document is blocked.
        record_hits: Whether to write the matched words into document
            metadata under `sensitive_word_hits`.
    """

    words: List[str] = []
    word_file: Optional[str] = None
    mode: str = "mask"
    mask_char: str = "*"
    case_sensitive: bool = False
    block_threshold: int = 1
    record_hits: bool = True

    _automaton: Optional[list] = None

    def _combined_words(self) -> List[str]:
        """Merge the inline word list with the word file content.

        Returns:
            The deduplicated sensitive word list, keeping configuration
            order.
        """
        combined = []
        seen = set()
        for word in list(self.words):
            normalized = word.strip()
            if normalized and normalized not in seen:
                seen.add(normalized)
                combined.append(normalized)
        if self.word_file:
            with open(self.word_file, "r", encoding="utf-8") as file:
                for line in file:
                    normalized = line.strip()
                    if normalized and not normalized.startswith("#") and normalized not in seen:
                        seen.add(normalized)
                        combined.append(normalized)
        return combined

    def _build_automaton(self) -> list:
        """Build an Aho-Corasick automaton over the combined word list.

        The automaton is a list of nodes; node 0 is the root. Each node is a
        dict with `next` (character to node id), `fail` (suffix link) and
        `output` (word index ending here).

        Returns:
            The automaton node list.

        Raises:
            ValueError: If no word is configured at all.
        """
        words = self._combined_words()
        if not words:
            raise ValueError(
                "SensitiveWordFilter: no sensitive words configured. Provide "
                "words or word_file.")
        root = {"next": {}, "fail": 0, "output": []}
        automaton = [root]
        for word_index, word in enumerate(words):
            node = 0
            for char in self._match_case(word):
                if char not in automaton[node]["next"]:
                    automaton[node]["next"][char] = len(automaton)
                    automaton.append({"next": {}, "fail": 0, "output": []})
                node = automaton[node]["next"][char]
            automaton[node]["output"].append(word_index)
        # breadth first construction of the failure links
        queue = list(automaton[0]["next"].values())
        while queue:
            next_queue = []
            for node in queue:
                fail = automaton[node]["fail"]
                for char, child in automaton[node]["next"].items():
                    next_queue.append(child)
                    follower = fail
                    while follower and char not in automaton[follower]["next"]:
                        follower = automaton[follower]["fail"]
                    automaton[child]["fail"] = automaton[follower]["next"].get(char, 0)
                    if automaton[child]["fail"] == child:
                        automaton[child]["fail"] = 0
                    automaton[child]["output"] = automaton[child]["output"] + \
                        automaton[automaton[child]["fail"]]["output"]
            queue = next_queue
        self._automaton = automaton
        return automaton

    def _match_case(self, text: str) -> str:
        return text if self.case_sensitive else text.lower()

    def _search(self, text: str) -> List[Tuple[int, int, str]]:
        """Find all matches of the word list in the text.

        Args:
            text: The text to scan.

        Returns:
            A list of (start, end, word) matches; overlapping matches are
            all reported, masking resolves them left to right.
        """
        words = self._combined_words()
        if self._automaton is None:
            self._build_automaton()
        automaton = self._automaton
        haystack = self._match_case(text or "")
        matches: List[Tuple[int, int, str]] = []
        node = 0
        for position, char in enumerate(haystack):
            while node and char not in automaton[node]["next"]:
                node = automaton[node]["fail"]
            node = automaton[node]["next"].get(char, 0)
            for word_index in automaton[node]["output"]:
                word = words[word_index]
                start = position - len(word) + 1
                matches.append((start, start + len(word), word))
        return sorted(matches)

    def _process_docs(self, origin_docs: List[Document], query: Query = None) -> List[Document]:
        """Mask or block documents according to the configured mode.

        Args:
            origin_docs: List of documents to be processed.
            query: Query object (unused).

        Returns:
            The processed document list.
        """
        if not origin_docs:
            return []
        processed: List[Document] = []
        for doc in origin_docs:
            matches = self._search(doc.text or "")
            unique_words = sorted({word for _, _, word in matches})
            if self.record_hits and unique_words:
                metadata = dict(doc.metadata or {})
                metadata[HITS_METADATA_KEY] = unique_words
                doc.metadata = metadata
            if self.mode == "block":
                if len(unique_words) >= self.block_threshold:
                    continue
                processed.append(doc)
            else:
                doc.text = self._mask(doc.text or "", matches)
                processed.append(doc)
        return processed

    def _mask(self, text: str, matches: List[Tuple[int, int, str]]) -> str:
        """Replace matched ranges with the mask character.

        Overlapping and adjacent matches are merged into one range so no
        fragment of a sensitive word stays visible, e.g. words `abcd` and
        `cdef` in `xabcdefy` produce one six character mask.

        Args:
            text: The original text.
            matches: The (start, end, word) matches.

        Returns:
            The masked text.
        """
        if not matches:
            return text
        pieces = []
        cursor = 0
        current_start, current_end = matches[0][0], matches[0][1]
        for start, end, _ in matches[1:]:
            if start <= current_end:
                current_end = max(current_end, end)
                continue
            pieces.append(text[cursor:current_start])
            pieces.append(self.mask_char * (current_end - current_start))
            cursor = current_end
            current_start, current_end = start, end
        pieces.append(text[cursor:current_start])
        pieces.append(self.mask_char * (current_end - current_start))
        pieces.append(text[current_end:])
        return "".join(pieces)

    def _initialize_by_component_configer(self, doc_processor_configer: ComponentConfiger) -> 'SensitiveWordFilter':
        """Initialize the filter from the component configuration.

        Args:
            doc_processor_configer: Configuration object.

        Returns:
            The initialized filter instance.

        Raises:
            ValueError: If the mode is invalid, no word source is configured
                or the word file does not exist.
        """
        super()._initialize_by_component_configer(doc_processor_configer)
        if hasattr(doc_processor_configer, "words"):
            self.words = doc_processor_configer.words
        if hasattr(doc_processor_configer, "word_file"):
            self.word_file = doc_processor_configer.word_file
        if hasattr(doc_processor_configer, "mode"):
            if doc_processor_configer.mode not in ("mask", "block"):
                raise ValueError(
                    f"SensitiveWordFilter: invalid mode '{doc_processor_configer.mode}', "
                    "must be 'mask' or 'block'.")
            self.mode = doc_processor_configer.mode
        if hasattr(doc_processor_configer, "mask_char"):
            self.mask_char = doc_processor_configer.mask_char
        if hasattr(doc_processor_configer, "case_sensitive"):
            self.case_sensitive = bool(doc_processor_configer.case_sensitive)
        if hasattr(doc_processor_configer, "block_threshold"):
            self.block_threshold = int(doc_processor_configer.block_threshold)
        if hasattr(doc_processor_configer, "record_hits"):
            self.record_hits = bool(doc_processor_configer.record_hits)
        if self.word_file and not os.path.exists(self.word_file):
            raise ValueError(
                f"SensitiveWordFilter: word_file '{self.word_file}' does not exist.")
        if not self.words and not self.word_file:
            raise ValueError(
                "SensitiveWordFilter: no sensitive words configured. Provide "
                "words or word_file.")
        return self
