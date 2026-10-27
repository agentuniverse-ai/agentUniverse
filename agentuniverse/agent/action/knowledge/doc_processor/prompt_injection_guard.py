# !/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Heuristic prompt-injection screening for recalled documents."""

import re
from typing import List, Literal

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger


class PromptInjectionGuard(DocProcessor):
    """Filter or annotate documents containing common injection markers."""

    mode: Literal["filter", "annotate"] = "filter"
    patterns: List[str] = [
        r"\bignore\s+(?:all\s+)?(?:the\s+)?previous\s+instructions\b",
        r"\bdisregard\s+(?:all\s+)?(?:the\s+)?(?:previous|above)\s+instructions\b",
        r"\breveal\s+(?:the\s+)?(?:hidden|system)\s+prompt\b",
        r"\bshow\s+(?:me\s+)?(?:the\s+)?system\s+prompt\b",
        r"\byou\s+are\s+now\s+(?:a|an)\b",
        r"<\s*/?\s*system\s*>",
    ]
    metadata_key: str = "security_flags"

    def _initialize_by_component_configer(self,
                                          doc_processor_configer: ComponentConfiger) \
            -> 'PromptInjectionGuard':
        super()._initialize_by_component_configer(doc_processor_configer)
        for attribute in ("mode", "patterns", "metadata_key"):
            if hasattr(doc_processor_configer, attribute):
                setattr(self, attribute, getattr(doc_processor_configer, attribute))
        self._validate_configuration()
        return self

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        compiled_patterns = self._validate_configuration()

        result: List[Document] = []
        for document in origin_docs:
            matches = self._matched_patterns(document.text or "", compiled_patterns)
            if matches and self.mode == "filter":
                continue
            if matches and self.mode == "annotate":
                metadata = dict(document.metadata or {})
                existing_flags = metadata.get(self.metadata_key, [])
                if not isinstance(existing_flags, list):
                    existing_flags = [str(existing_flags)]
                metadata[self.metadata_key] = list(dict.fromkeys(
                    [*existing_flags, "prompt_injection"]
                ))
                metadata["prompt_injection_detected"] = True
                result.append(document.model_copy(update={"metadata": metadata}))
            else:
                result.append(document)
        return result

    def _validate_configuration(self) -> List[re.Pattern[str]]:
        if self.mode not in {"filter", "annotate"}:
            raise ValueError("mode must be either 'filter' or 'annotate'")
        if not isinstance(self.metadata_key, str) or not self.metadata_key.strip():
            raise ValueError("metadata_key must be a non-empty string")
        return self._compile_patterns()

    def _compile_patterns(self) -> List[re.Pattern[str]]:
        if not isinstance(self.patterns, list) or not self.patterns:
            raise ValueError("patterns must be a non-empty list")
        compiled = []
        for pattern in self.patterns:
            if not isinstance(pattern, str) or not pattern:
                raise ValueError("patterns must contain non-empty strings")
            try:
                compiled.append(re.compile(pattern, re.IGNORECASE | re.MULTILINE))
            except re.error as exc:
                raise ValueError(f"invalid prompt injection pattern: {pattern}") from exc
        return compiled

    @staticmethod
    def _matched_patterns(text: str,
                          patterns: List[re.Pattern[str]]) -> List[str]:
        return [pattern.pattern for pattern in patterns if pattern.search(text)]
