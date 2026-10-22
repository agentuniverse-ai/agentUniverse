"""Operator-owned sensitive-word filtering for Knowledge documents.

The filter intentionally contains no built-in policy vocabulary. Operators can
provide literal terms inline or through UTF-8 word-list files, then use the
component in a Knowledge ``insert_processors``, ``update_processors``, or
``post_processors`` pipeline. It does not inspect Agent, Tool, or arbitrary LLM
input/output traffic. Only ``Document.text`` is scanned; identifiers, embeddings,
keywords, and existing metadata values are not treated as filter input.

Matching is deterministic and dependency-free. Text and terms are normalized
with Unicode compatibility decomposition, invisible format characters are
ignored, and matching is case-insensitive by default. Terms whose normalized
form is ASCII use whole-word boundaries while other terms (including Chinese)
use substring matching.
When terms overlap at the same position, the longest match wins.

Only aggregate match counts and the configured action are written to document
metadata. The vocabulary, matched text, and match positions are never emitted in
metadata, logs, exceptions, ``repr()``, or ``model_dump()``.
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from pydantic import Field, PrivateAttr

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

_ALLOWED_ACTIONS = frozenset({"mask", "drop_document", "raise"})


class SensitiveWordDetectedError(RuntimeError):
    """Raised when a ``raise`` policy detects configured terms.

    The exception deliberately exposes aggregate counts only.
    """

    def __init__(self, match_count: int, document_count: int) -> None:
        self.match_count = match_count
        self.document_count = document_count
        message = (
            f"Sensitive-word policy blocked {match_count} match(es) " f"across {document_count} Knowledge document(s)."
        )
        super().__init__(message)


@dataclass(frozen=True)
class _Boundary:
    left: bool
    right: bool


@dataclass
class _TrieNode:
    children: dict[str, _TrieNode] = field(default_factory=dict)
    boundary: _Boundary | None = None


@dataclass(frozen=True)
class _Match:
    start: int
    end: int


class SensitiveWordFilter(DocProcessor):
    """Apply an operator-provided sensitive-word policy to Knowledge documents.

    Attributes:
        enabled: Whether this configuration is usable. The shipped component
            configuration is disabled because the framework must not invent an
            operator's policy vocabulary. An application configuration must set
            this to ``True`` and provide at least one effective term.
        words: Literal inline terms. Hidden from representation and serialization.
        word_list_paths: UTF-8/UTF-8-BOM files containing one literal term per
            line. Relative paths resolve from the component YAML directory.
            Empty lines and lines beginning with ``#`` are ignored.
        action: ``mask``, ``drop_document``, or ``raise``.
        replacement: Replacement used by the ``mask`` action.
        case_sensitive: Whether matching preserves case. Defaults to ``False``.
        ascii_word_boundary: Whether ASCII terms require whole-word boundaries.
            Non-ASCII terms always use substring matching.
        metadata_key: Metadata key containing aggregate ``action`` and
            ``match_count`` values. Set to ``None`` or an empty string to omit.
    """

    enabled: bool = True
    words: Any = Field(default_factory=list, repr=False, exclude=True)
    word_list_paths: Any = Field(default_factory=list, repr=False, exclude=True)
    action: str = "mask"
    replacement: str = "[FILTERED]"
    case_sensitive: bool = False
    ascii_word_boundary: bool = True
    metadata_key: str | None = "sensitive_word_filter"

    _trie: _TrieNode | None = PrivateAttr(default=None)
    _matcher_fingerprint: tuple[object, ...] | None = PrivateAttr(default=None)

    def _process_docs(
        self,
        origin_docs: list[Document],
        query: Query = None,
    ) -> list[Document]:
        """Filter document text according to the configured action."""
        self._ensure_ready()

        matches_by_document = [self._find_matches(doc.text or "") for doc in origin_docs]
        if self.action == "raise":
            match_count = sum(len(matches) for matches in matches_by_document)
            if match_count:
                matched_document_count = sum(bool(matches) for matches in matches_by_document)
                raise SensitiveWordDetectedError(match_count, matched_document_count)

        result: list[Document] = []
        for doc, matches in zip(origin_docs, matches_by_document, strict=True):
            if self.action == "drop_document" and matches:
                continue
            if self.action == "mask" and matches:
                doc.text = self._mask_text(doc.text or "", matches)
            self._stamp_metadata(doc, len(matches))
            result.append(doc)
        return result

    def _ensure_ready(self) -> None:
        self._validate_configuration()
        if not self.enabled:
            message = (
                "SensitiveWordFilter is disabled. Define an application-level "
                "component configuration with enabled=true and a non-empty words "
                "or word_list_paths value before adding it to a Knowledge pipeline."
            )
            raise ValueError(message)
        if self._trie is None:
            base_directory = (
                Path(self.component_config_path).resolve().parent if self.component_config_path else Path.cwd()
            )
            self._build_matcher(base_directory)
        elif self._matcher_fingerprint != self._matcher_configuration_state():
            message = (
                "SensitiveWordFilter matcher configuration changed after initialization. "
                "Create and initialize a new component instance instead of mutating its vocabulary or matching options."
            )
            raise ValueError(message)

    def _build_matcher(self, base_directory: Path) -> None:
        """Load, validate, normalize, and compile the configured vocabulary."""
        self._validate_configuration()
        if not self.enabled:
            self._trie = None
            self._matcher_fingerprint = None
            return

        raw_terms = list(self.words)
        raw_terms.extend(self._load_word_lists(base_directory))

        normalized_terms: dict[str, _Boundary] = {}
        for index, term in enumerate(raw_terms):
            normalized = self._validate_and_normalize_term(term, index)
            if normalized in normalized_terms:
                continue
            is_ascii = normalized.isascii()
            normalized_terms[normalized] = _Boundary(
                left=(self.ascii_word_boundary and is_ascii and self._is_ascii_word_char(normalized[0])),
                right=(self.ascii_word_boundary and is_ascii and self._is_ascii_word_char(normalized[-1])),
            )

        if not normalized_terms:
            message = (
                "SensitiveWordFilter requires at least one effective literal term "
                "from words or word_list_paths when enabled=true."
            )
            raise ValueError(message)

        root = _TrieNode()
        for term, boundary in normalized_terms.items():
            node = root
            for character in term:
                node = node.children.setdefault(character, _TrieNode())
            node.boundary = boundary
        self._trie = root
        self._matcher_fingerprint = self._matcher_configuration_state()

    def _validate_configuration(self) -> None:
        if not isinstance(self.enabled, bool):
            message = "enabled must be a boolean."
            raise TypeError(message)
        if not isinstance(self.words, list):
            message = "words must be a list of literal strings."
            raise TypeError(message)
        if not isinstance(self.word_list_paths, list):
            message = "word_list_paths must be a list of file paths."
            raise TypeError(message)
        if not isinstance(self.action, str):
            actions = ", ".join(sorted(_ALLOWED_ACTIONS))
            message = f"action must be a string with one of these values: {actions}."
            raise TypeError(message)
        if self.action not in _ALLOWED_ACTIONS:
            actions = ", ".join(sorted(_ALLOWED_ACTIONS))
            message = f"action must be one of: {actions}."
            raise ValueError(message)
        if not isinstance(self.replacement, str):
            message = "replacement must be a string."
            raise TypeError(message)
        if not isinstance(self.case_sensitive, bool):
            message = "case_sensitive must be a boolean."
            raise TypeError(message)
        if not isinstance(self.ascii_word_boundary, bool):
            message = "ascii_word_boundary must be a boolean."
            raise TypeError(message)
        if self.metadata_key is not None and not isinstance(self.metadata_key, str):
            message = "metadata_key must be a string or null."
            raise TypeError(message)

    def _matcher_configuration_state(self) -> tuple[object, ...]:
        """Return a non-logging snapshot of fields used to compile the trie."""
        words = tuple(self.words) if isinstance(self.words, list) else None
        paths = tuple(self.word_list_paths) if isinstance(self.word_list_paths, list) else None
        return words, paths, self.case_sensitive, self.ascii_word_boundary

    def _load_word_lists(self, base_directory: Path) -> list[str]:
        terms: list[str] = []
        for path_index, configured_path in enumerate(self.word_list_paths):
            if not isinstance(configured_path, str) or not configured_path.strip():
                message = f"word_list_paths[{path_index}] must be a non-empty string."
                raise ValueError(message)
            path = Path(configured_path).expanduser()
            if not path.is_absolute():
                path = base_directory / path
            path = path.resolve()
            if not path.is_file():
                message = f"word_list_paths[{path_index}] is not a readable file: {path}"
                raise ValueError(message)
            try:
                lines = path.read_text(encoding="utf-8-sig").splitlines()
            except UnicodeDecodeError as exc:
                message = f"word_list_paths[{path_index}] must be valid UTF-8: {path}"
                raise ValueError(message) from exc
            except OSError as exc:
                message = f"word_list_paths[{path_index}] could not be read: {path}"
                raise ValueError(message) from exc
            terms.extend(line.strip() for line in lines if line.strip() and not line.lstrip().startswith("#"))
        return terms

    def _validate_and_normalize_term(self, term: object, index: int) -> str:
        if not isinstance(term, str) or not term.strip():
            message = f"Sensitive-word entry {index} must be a non-empty string."
            raise ValueError(message)
        stripped = term.strip()
        if any(character in stripped for character in ("\x00", "\r", "\n")):
            message = f"Sensitive-word entry {index} must contain exactly one line and no null bytes."
            raise ValueError(message)
        normalized = self._normalize_value(stripped)
        if not normalized:
            message = f"Sensitive-word entry {index} becomes empty after Unicode normalization."
            raise ValueError(message)
        return normalized

    def _find_matches(self, text: str) -> list[_Match]:
        normalized_text, offsets = self._normalize_text_with_offsets(text)
        if not normalized_text:
            return []

        matches: list[_Match] = []
        start = 0
        while start < len(normalized_text):
            node = self._trie
            cursor = start
            best_end: int | None = None
            while node is not None and cursor < len(normalized_text):
                node = node.children.get(normalized_text[cursor])
                if node is None:
                    break
                cursor += 1
                if node.boundary is not None and self._boundaries_match(
                    normalized_text,
                    start,
                    cursor,
                    node.boundary,
                ):
                    best_end = cursor
            if best_end is None:
                start += 1
                continue

            matched_offsets = offsets[start:best_end]
            original_match = _Match(min(matched_offsets), max(matched_offsets) + 1)
            matches.append(original_match)
            start = best_end
        return self._merge_source_matches(matches)

    @staticmethod
    def _merge_source_matches(matches: list[_Match]) -> list[_Match]:
        """Restore source order and merge only genuinely overlapping spans."""
        merged: list[_Match] = []
        for match in sorted(matches, key=lambda item: (item.start, item.end)):
            if merged and match.start < merged[-1].end:
                previous = merged[-1]
                merged[-1] = _Match(min(previous.start, match.start), max(previous.end, match.end))
            else:
                merged.append(match)
        return merged

    def _boundaries_match(
        self,
        text: str,
        start: int,
        end: int,
        boundary: _Boundary,
    ) -> bool:
        if boundary.left and start > 0 and self._blocks_ascii_boundary(text[start - 1]):
            return False
        return not (boundary.right and end < len(text) and self._blocks_ascii_boundary(text[end]))

    def _normalize_text_with_offsets(self, text: str) -> tuple[str, list[int]]:
        normalized_characters = self._normalized_characters(text)
        return (
            "".join(character for character, _ in normalized_characters),
            [source_index for _, source_index in normalized_characters],
        )

    def _normalize_value(self, value: str) -> str:
        return "".join(character for character, _ in self._normalized_characters(value))

    def _normalized_characters(self, value: str) -> list[tuple[str, int]]:
        """Normalize text while retaining source offsets for safe masking.

        Unicode canonical ordering can reorder combining marks that originate
        from different source code points. Keeping the source index beside each
        normalized character lets matching use the correctly ordered form while
        masking the complete corresponding span in the original text.
        """
        decomposed_characters: list[tuple[str, int]] = []
        for source_index, source_character in enumerate(value):
            if unicodedata.category(source_character) == "Cf":
                continue
            for decomposed_character in unicodedata.normalize("NFKD", source_character):
                if unicodedata.category(decomposed_character) != "Cf":
                    decomposed_characters.append((decomposed_character, source_index))

        folded_characters: list[tuple[str, int]] = []
        for decomposed_character, source_index in self._canonical_order(decomposed_characters):
            folded = decomposed_character if self.case_sensitive else decomposed_character.casefold()
            for normalized_character in unicodedata.normalize("NFKD", folded):
                if unicodedata.category(normalized_character) != "Cf":
                    folded_characters.append((normalized_character, source_index))
        return self._canonical_order(folded_characters)

    @staticmethod
    def _canonical_order(characters: list[tuple[str, int]]) -> list[tuple[str, int]]:
        """Apply Unicode canonical combining-class ordering without losing offsets."""
        ordered: list[tuple[str, int]] = []
        pending_marks: list[tuple[str, int]] = []
        for character in characters:
            if unicodedata.combining(character[0]) == 0:
                ordered.extend(sorted(pending_marks, key=lambda item: unicodedata.combining(item[0])))
                pending_marks = []
                ordered.append(character)
            else:
                pending_marks.append(character)
        ordered.extend(sorted(pending_marks, key=lambda item: unicodedata.combining(item[0])))
        return ordered

    @staticmethod
    def _is_ascii_word_char(character: str) -> bool:
        return character.isascii() and (character.isalnum() or character == "_")

    @classmethod
    def _blocks_ascii_boundary(cls, character: str) -> bool:
        return cls._is_ascii_word_char(character) or unicodedata.category(character).startswith("M")

    def _mask_text(self, text: str, matches: list[_Match]) -> str:
        pieces: list[str] = []
        cursor = 0
        for match in matches:
            pieces.append(text[cursor : match.start])
            pieces.append(self.replacement)
            cursor = match.end
        pieces.append(text[cursor:])
        return "".join(pieces)

    def _stamp_metadata(self, document: Document, match_count: int) -> None:
        if not self.metadata_key:
            return
        metadata = dict(document.metadata or {})
        metadata[self.metadata_key] = {
            "action": self.action,
            "match_count": match_count,
        }
        document.metadata = metadata

    def _initialize_by_component_configer(
        self,
        doc_processor_configer: ComponentConfiger,
    ) -> SensitiveWordFilter:
        """Initialize and eagerly validate a component configuration."""
        super()._initialize_by_component_configer(doc_processor_configer)
        for attribute in (
            "enabled",
            "words",
            "word_list_paths",
            "action",
            "replacement",
            "case_sensitive",
            "ascii_word_boundary",
            "metadata_key",
        ):
            if hasattr(doc_processor_configer, attribute):
                setattr(self, attribute, getattr(doc_processor_configer, attribute))

        config_path = getattr(getattr(doc_processor_configer, "configer", None), "path", None)
        base_directory = Path(config_path).resolve().parent if config_path else Path.cwd()
        self._build_matcher(base_directory)
        return self
