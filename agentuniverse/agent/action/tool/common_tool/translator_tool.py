#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Translation tool backed by the free Google Translate endpoint.

The tool wraps the public, key-less ``translate.googleapis.com`` endpoint so
that an agent can translate text between 100+ languages without registering an
API key. Network access is required, but no credentials are needed.
"""

# Public execute() converts validation exceptions into structured tool errors.
# ruff: noqa: TRY003

from typing import Any, ClassVar, Dict, Optional

import httpx
from pydantic import Field

from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.base.util.logging.logging_util import LOGGER

GOOGLE_TRANSLATE_ENDPOINT = "https://translate.googleapis.com/translate_a/single"


class TranslatorTool(Tool):
    """Translate text between 100+ languages using the free Google endpoint.

    The tool exposes a single ``translate`` operation. Source and target
    languages follow the two/three-letter ISO 639 codes used by Google
    Translate (for example ``en``, ``zh``, ``ja``, ``auto``). ``source`` may be
    set to ``auto`` to let Google detect the source language automatically.
    """

    description: str = (
        "Translate text between 100+ languages using the free Google "
        "Translate endpoint (no API key required)."
    )

    # Configurable defaults.
    default_source: str = Field(
        default="auto",
        description="Default source language code. Use 'auto' for detection.",
    )
    default_target: str = Field(
        default="en",
        description="Default target language code, e.g. 'en', 'zh', 'ja'.",
    )
    request_timeout: float = Field(
        default=15.0,
        description="HTTP request timeout in seconds.",
    )

    # Sampling of the supported languages; the upstream API accepts many more.
    SUPPORTED_LANGUAGES: ClassVar[frozenset[str]] = frozenset(
        {
            "auto", "af", "sq", "am", "ar", "hy", "az", "eu", "be", "bn",
            "bs", "bg", "ca", "ceb", "ny", "zh", "zh-CN", "zh-TW", "co",
            "hr", "cs", "da", "nl", "en", "eo", "et", "fi", "fr", "fy",
            "gl", "ka", "de", "el", "gu", "ht", "ha", "haw", "he", "hi",
            "hmn", "hu", "is", "ig", "id", "ga", "it", "ja", "jw", "kn",
            "kk", "km", "rw", "ko", "ku", "ky", "lo", "la", "lv", "lt",
            "lb", "mk", "mg", "ms", "ml", "mt", "mi", "mr", "mn", "my",
            "ne", "no", "or", "ps", "fa", "pl", "pt", "pa", "ro", "ru",
            "sm", "gd", "sr", "st", "sn", "sd", "si", "sk", "sl", "so",
            "es", "su", "sw", "sv", "tl", "tg", "ta", "tt", "te", "th",
            "tr", "tk", "uk", "ur", "ug", "uz", "vi", "cy", "xh", "yi",
            "yo", "zu",
        }
    )

    MAX_TEXT_CHARS: ClassVar[int] = 50_000

    def execute(
        self,
        text: str,
        source: Optional[str] = None,
        target: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Translate ``text`` and return a structured result.

        Args:
            text: The text to translate. Leading/trailing whitespace is
                stripped and the length is capped by ``MAX_TEXT_CHARS``.
            source: Source language code. Falls back to ``default_source``.
            target: Target language code. Falls back to ``default_target``.

        Returns:
            A dictionary with ``status`` plus the translation result. Network
            and validation failures are returned as ``error`` fields rather
            than raised.
        """
        try:
            normalized_text = self._validate_text(text)
            source_lang = self._resolve_language(source, self.default_source)
            target_lang = self._resolve_language(target, self.default_target)
            self._check_language_pair(source_lang, target_lang)

            translated, detected_source = self._request_translation(
                normalized_text, source_lang, target_lang
            )
            return {
                "status": "success",
                "translated_text": translated,
                "source_language": detected_source or source_lang,
                "target_language": target_lang,
                "original_text": normalized_text,
                "engine": "google_translate",
            }
        except (TypeError, ValueError) as exc:
            LOGGER.error(f"TranslatorTool validation error: {exc}")
            return self._error("validation_error", str(exc))
        except httpx.HTTPError as exc:
            LOGGER.error(f"TranslatorTool network error: {exc}")
            return self._error("network_error", str(exc))
        except Exception as exc:
            LOGGER.error(f"TranslatorTool operation failed: {exc}")
            return self._error("operation_error", f"Translation failed: {exc}")

    @staticmethod
    def _error(kind: str, message: str) -> Dict[str, Any]:
        return {"status": "error", "error_type": kind, "error": message}

    def _validate_text(self, value: Any) -> str:
        if not isinstance(value, str):
            raise TypeError("text must be a string")
        normalized = value.strip()
        if not normalized:
            raise ValueError("text must not be empty")
        if len(normalized) > self.MAX_TEXT_CHARS:
            raise ValueError(
                f"text exceeds MAX_TEXT_CHARS ({self.MAX_TEXT_CHARS})"
            )
        return normalized

    def _resolve_language(self, value: Any, fallback: str) -> str:
        if value is None:
            resolved = fallback
        else:
            if not isinstance(value, str):
                raise TypeError("language must be a string")
            resolved = value.strip()
        if not resolved:
            raise ValueError("language must not be empty")
        return resolved

    def _check_language_pair(self, source: str, target: str) -> None:
        normalized_source = source.lower()
        normalized_target = target.lower()
        if normalized_source not in self.SUPPORTED_LANGUAGES:
            raise ValueError(
                f"unsupported source language: {source!r}. "
                "See https://cloud.google.com/translate/docs/languages"
            )
        if normalized_target not in self.SUPPORTED_LANGUAGES:
            raise ValueError(
                f"unsupported target language: {target!r}. "
                "See https://cloud.google.com/translate/docs/languages"
            )
        if (
            normalized_source != "auto"
            and normalized_source == normalized_target
        ):
            raise ValueError("source and target must be different languages")

    def _request_translation(
        self, text: str, source: str, target: str
    ) -> tuple[str, str]:
        """Call the Google Translate endpoint and parse the response.

        Returns a ``(translated_text, detected_source_language)`` tuple. The
        detected source language is only meaningful when ``source == 'auto'``.
        """
        params = {
            "client": "gtx",
            "sl": source,
            "tl": target,
            "dt": "t",
            "q": text,
        }
        response = httpx.get(
            GOOGLE_TRANSLATE_ENDPOINT,
            params=params,
            timeout=self.request_timeout,
            headers={"User-Agent": "agentuniverse-translator-tool/1.0"},
        )
        response.raise_for_status()
        payload = response.json()
        return self._parse_google_response(payload)

    @staticmethod
    def _parse_google_response(payload: Any) -> tuple[str, str]:
        """Extract translation and detected source language from payload.

        Google returns a nested list. ``payload[0]`` is a list of segments,
        where each segment is ``[translated_chunk, original_chunk, ...]``.
        ``payload[2]`` holds the detected source language when ``sl=auto``.
        """
        if not isinstance(payload, list) or not payload:
            raise ValueError("unexpected Google Translate response: empty body")
        segments = payload[0]
        if not isinstance(segments, list) or not segments:
            raise ValueError("unexpected Google Translate response: no segments")
        translated_chunks: list[str] = []
        for segment in segments:
            if isinstance(segment, list) and segment and isinstance(segment[0], str):
                translated_chunks.append(segment[0])
        translated = "".join(translated_chunks)
        detected_source = ""
        if len(payload) > 2 and isinstance(payload[2], str):
            detected_source = payload[2]
        return translated, detected_source
