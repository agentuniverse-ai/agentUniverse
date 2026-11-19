#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Text statistics tool backed only on the Python standard library.

The tool computes a wide range of readability and structural metrics for a
piece of text: character/word/sentence/paragraph counts, average lengths,
estimated reading time and a readability complexity score. Zero third-party
dependencies.
"""

# Public execute() converts validation exceptions into structured tool errors.
# ruff: noqa: TRY003

import math
import re
from typing import Any, Dict, List, Optional

from pydantic import Field

from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.base.util.logging.logging_util import LOGGER

# Word boundary that keeps apostrophes/hyphens inside a word ("don't", "well-known").
WORD_PATTERN = re.compile(r"[A-Za-z0-9']+(?:[-'][A-Za-z0-9']+)*")
# Sentence terminators. Handles common abbreviations best-effort.
SENTENCE_SPLIT = re.compile(r"[.!?]+(?:[\"')\]]?)|\u3002|\uff01|\uff1f")
# Paragraphs are blocks separated by two or more newlines (also handle CRLF).
PARAGRAPH_SPLIT = re.compile(r"\n\s*\n")
# Syllable counting is language specific; this is an English heuristic.
VOWEL_GROUPS = re.compile(r"[aeiouy]+", re.IGNORECASE)

MAX_TEXT_CHARS = 1_000_000


class TextStatisticsTool(Tool):
    """Compute character, word, sentence, paragraph and readability metrics."""

    description: str = (
        "Analyze text to compute counts, average lengths, estimated reading "
        "time and a readability complexity score. Zero dependencies."
    )

    words_per_minute: int = Field(
        default=200,
        description="Reading speed in words per minute for time estimates.",
    )
    min_syllables: int = Field(
        default=1,
        description="Minimum syllables returned per word by the heuristic.",
    )

    def execute(
        self,
        text: str,
        words_per_minute: Optional[int] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Analyze ``text`` and return a structured statistics report."""
        try:
            normalized = self._validate_text(text)
            wpm = self._resolve_wpm(words_per_minute)
            words = self._words(normalized)
            sentences = self._sentences(normalized)
            paragraphs = self._paragraphs(normalized)
            syllables = self._total_syllables(words)
            char_counts = self._char_counts(normalized)
            averages = self._averages(
                len(words), len(sentences), len(paragraphs), syllables
            )
            reading_time = self._reading_time(len(words), wpm)
            averages["chars_per_word"] = round(
                char_counts["no_spaces"] / len(words), 2
            ) if words else 0.0
            complexity = self._complexity(
                len(words), len(sentences), syllables, char_counts
            )
            return {
                "status": "success",
                "mode": "analyze",
                "counts": {
                    "characters": char_counts["total"],
                    "characters_no_spaces": char_counts["no_spaces"],
                    "letters": char_counts["letters"],
                    "digits": char_counts["digits"],
                    "whitespace": char_counts["whitespace"],
                    "words": len(words),
                    "unique_words": len({w.lower() for w in words}),
                    "sentences": len(sentences),
                    "paragraphs": len(paragraphs),
                    "syllables": syllables,
                },
                "averages": averages,
                "reading_time_seconds": reading_time["seconds"],
                "reading_time": reading_time["human"],
                "words_per_minute": wpm,
                "complexity": complexity,
                "longest_word": max(words, key=len) if words else "",
            }
        except (TypeError, ValueError) as exc:
            LOGGER.error(f"TextStatisticsTool validation error: {exc}")
            return self._error("validation_error", str(exc))
        except Exception as exc:
            LOGGER.error(f"TextStatisticsTool operation failed: {exc}")
            return self._error("operation_error", f"Text analysis failed: {exc}")

    # ------------------------------------------------------------------ helpers
    @staticmethod
    def _error(kind: str, message: str) -> Dict[str, Any]:
        return {"status": "error", "error_type": kind, "error": message}

    def _validate_text(self, value: Any) -> str:
        if not isinstance(value, str):
            raise TypeError("text must be a string")
        if len(value) > MAX_TEXT_CHARS:
            raise ValueError(
                f"text exceeds MAX_TEXT_CHARS ({MAX_TEXT_CHARS})"
            )
        return value

    def _resolve_wpm(self, value: Any) -> int:
        if value is None:
            return self.words_per_minute
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError("words_per_minute must be an integer")
        if value < 1 or value > 2000:
            raise ValueError("words_per_minute must be between 1 and 2000")
        return value

    @staticmethod
    def _words(text: str) -> List[str]:
        return WORD_PATTERN.findall(text)

    def _sentences(self, text: str) -> List[str]:
        raw = SENTENCE_SPLIT.split(text)
        sentences = [chunk.strip() for chunk in raw if chunk and chunk.strip()]
        # A bare fragment with no terminator still counts as a sentence.
        if not sentences and text.strip():
            return [text.strip()]
        return sentences

    @staticmethod
    def _paragraphs(text: str) -> List[str]:
        if not text.strip():
            return []
        blocks = PARAGRAPH_SPLIT.split(text)
        return [block.strip() for block in blocks if block.strip()]

    @staticmethod
    def _char_counts(text: str) -> Dict[str, int]:
        total = len(text)
        whitespace = sum(1 for c in text if c.isspace())
        letters = sum(1 for c in text if c.isalpha())
        digits = sum(1 for c in text if c.isdigit())
        return {
            "total": total,
            "no_spaces": total - whitespace,
            "letters": letters,
            "digits": digits,
            "whitespace": whitespace,
        }

    def _count_syllables(self, word: str) -> int:
        """Heuristic English syllable counter.

        Counts vowel groups, subtracts silent trailing ``e`` and floors the
        result at ``min_syllables`` (default 1) so every word contributes.
        """
        if not word:
            return 0
        groups = VOWEL_GROUPS.findall(word)
        count = len(groups)
        lowered = word.lower()
        # Subtract silent 'e' at the end (e.g. "name" -> 1, "the" -> 1).
        if count > 1 and lowered.endswith("e"):
            count -= 1
        return max(self.min_syllables, count)

    def _total_syllables(self, words: List[str]) -> int:
        return sum(self._count_syllables(w) for w in words)

    @staticmethod
    def _averages(
        words: int, sentences: int, paragraphs: int, syllables: int
    ) -> Dict[str, float]:
        words_per_sentence = words / sentences if sentences else 0.0
        sentences_per_paragraph = sentences / paragraphs if paragraphs else 0.0
        words_per_paragraph = words / paragraphs if paragraphs else 0.0
        syllables_per_word = syllables / words if words else 0.0
        return {
            "words_per_sentence": round(words_per_sentence, 2),
            "sentences_per_paragraph": round(sentences_per_paragraph, 2),
            "words_per_paragraph": round(words_per_paragraph, 2),
            "syllables_per_word": round(syllables_per_word, 2),
            "chars_per_word": 0.0,
        }

    @staticmethod
    def _reading_time(words: int, wpm: int) -> Dict[str, Any]:
        seconds = (words / wpm) * 60 if wpm else 0.0
        total = int(round(seconds))
        minutes, secs = divmod(total, 60)
        return {"seconds": round(seconds, 2), "human": f"{minutes}m {secs}s"}

    def _complexity(
        self,
        words: int,
        sentences: int,
        syllables: int,
        char_counts: Dict[str, int],
    ) -> Dict[str, Any]:
        """Flesch Reading Ease plus a derived 0-100 difficulty score.

        The Flesch scale rewards short words and short sentences. We invert it
        so higher = more complex, then clamp to 0-100.
        """
        if words == 0 or sentences == 0:
            return {
                "flesch_reading_ease": None,
                "flesch_kincaid_grade": None,
                "difficulty_score": 0,
                "difficulty_label": "n/a",
            }
        syllables_per_word = syllables / words
        words_per_sentence = words / sentences
        flesch_ease = 206.835 - 84.6 * syllables_per_word - 1.015 * words_per_sentence
        flesch_ease = round(max(0.0, min(100.0, flesch_ease)), 2)
        grade = round(0.39 * words_per_sentence + 11.8 * syllables_per_word - 15.59, 2)
        grade = max(0.0, grade)
        difficulty = round(100.0 - flesch_ease, 2)
        return {
            "flesch_reading_ease": flesch_ease,
            "flesch_kincaid_grade": grade,
            "difficulty_score": difficulty,
            "difficulty_label": self._difficulty_label(difficulty),
        }

    @staticmethod
    def _difficulty_label(score: float) -> str:
        if score >= 70:
            return "very difficult"
        if score >= 55:
            return "difficult"
        if score >= 40:
            return "moderate"
        if score >= 25:
            return "easy"
        return "very easy"
