# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/07/21
# @FileName: language_filter.py

"""
Language filter — a knowledge post-processing DocProcessor.

Filters recalled documents by language, keeping only those that match the
configured target language(s). Useful for multi-lingual knowledge bases
where the agent should only receive documents in the user's language.

Two detection modes:
- **Library mode** (``langdetect`` installed): uses the well-tested
  ``langdetect`` library for accurate detection.
- **Script-based mode** (default, no dependency): a fast heuristic that
  inspects Unicode code-point ranges to classify text as CJK (Chinese/
  Japanese/Korean), Cyrillic, Arabic, Latin, etc. This covers the common
  case without requiring any third-party package.

Addresses #248 (knowledge post-processing components).
"""

import logging
import re
from typing import Dict, List, Optional, Set

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import \
    DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger

logger = logging.getLogger(__name__)

# Unicode code-point ranges for script detection.
_SCRIPT_RANGES = [
    ("zh", 0x4E00, 0x9FFF),     # CJK Unified Ideographs
    ("zh", 0x3400, 0x4DBF),     # CJK Extension A
    ("ja", 0x3040, 0x309F),     # Hiragana
    ("ja", 0x30A0, 0x30FF),     # Katakana
    ("ko", 0xAC00, 0xD7AF),     # Hangul Syllables
    ("ko", 0x1100, 0x11FF),     # Hangul Jamo
    ("ar", 0x0600, 0x06FF),     # Arabic
    ("ru", 0x0400, 0x04FF),     # Cyrillic
    ("th", 0x0E00, 0x0E7F),     # Thai
    ("he", 0x0590, 0x05FF),     # Hebrew
    ("hi", 0x0900, 0x097F),     # Devanagari
]

# Map from langdetect / script codes to ISO 639-1.
_LANG_ALIASES = {
    "zh-cn": "zh", "zh-tw": "zh", "zh-hans": "zh", "zh-hant": "zh",
    "ja-jp": "ja", "ko-kr": "ko", "en-us": "en", "en-gb": "en",
    "pt-br": "pt", "pt-pt": "pt",
}

_MIN_TEXT_LEN = 3


class LanguageFilter(DocProcessor):
    """Filter documents by language.

    Attributes:
        allowed_languages: Set of ISO 639-1 language codes to keep
            (e.g. ``{"en", "zh"}``). Documents detected as any other
            language are filtered out.
        min_confidence: Minimum confidence (0.0–1.0) for langdetect to
            accept the detection. Below this, the document is kept
            regardless (conservative — prefer false-keep over false-drop).
            Default 0.7. Ignored in script-based mode.
        use_langdetect: If True and langdetect is installed, use it.
            If False or langdetect is absent, fall back to script detection.
    """

    allowed_languages: Set[str] = {"en"}
    min_confidence: float = 0.7
    use_langdetect: bool = True

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        if not origin_docs:
            return []
        if not self.allowed_languages:
            return list(origin_docs)

        result: List[Document] = []
        dropped = 0
        for doc in origin_docs:
            text = (doc.text or "").strip()
            if len(text) < _MIN_TEXT_LEN:
                # Too short to detect — keep it (conservative).
                result.append(doc)
                continue

            lang = self._detect_language(text)
            if lang is None:
                # Could not detect — keep it.
                result.append(doc)
                continue

            if lang in self.allowed_languages:
                result.append(doc)
            else:
                dropped += 1

        if dropped > 0:
            logger.debug("LanguageFilter: dropped %d/%d documents "
                         "(allowed: %s)", dropped, len(origin_docs),
                         self.allowed_languages)
        return result

    def _detect_language(self, text: str) -> Optional[str]:
        """Detect the language of ``text``.

        Returns an ISO 639-1 code, or None if detection fails.
        """
        if self.use_langdetect:
            lang = self._detect_with_langdetect(text)
            if lang is not None:
                return lang
        return self._detect_with_script(text)

    @staticmethod
    def _detect_with_langdetect(text: str) -> Optional[str]:
        try:
            from langdetect import detect
            from langdetect.lang_detect_exception import LangDetectException
        except ImportError:
            return None

        try:
            raw = detect(text)
            return _LANG_ALIASES.get(raw.lower(), raw.lower()[:2])
        except LangDetectException:
            return None

    @staticmethod
    def _detect_with_script(text: str) -> Optional[str]:
        """Fast heuristic: classify by Unicode script distribution."""
        counts: Dict[str, int] = {}
        total = 0
        for char in text:
            cp = ord(char)
            if cp < 0x0041:  # ASCII control / space
                continue
            for lang, lo, hi in _SCRIPT_RANGES:
                if lo <= cp <= hi:
                    counts[lang] = counts.get(lang, 0) + 1
                    total += 1
                    break
            else:
                # Latin or other; count as 'en' if alphabetic.
                if char.isalpha():
                    counts["en"] = counts.get("en", 0) + 1
                    total += 1

        if total == 0:
            return None
        # Return the dominant script.
        dominant = max(counts, key=counts.get)
        return dominant

    def _initialize_by_component_configer(self,
                                          doc_processor_configer: ComponentConfiger) \
            -> "LanguageFilter":
        super()._initialize_by_component_configer(doc_processor_configer)
        if hasattr(doc_processor_configer, "allowed_languages"):
            self.allowed_languages = set(doc_processor_configer.allowed_languages)
        if hasattr(doc_processor_configer, "min_confidence"):
            self.min_confidence = doc_processor_configer.min_confidence
        if hasattr(doc_processor_configer, "use_langdetect"):
            self.use_langdetect = doc_processor_configer.use_langdetect
        return self
