#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: multi_text_search_tool.py

"""Multi-text search tool — grep for agents, built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency way for an agent to
search, filter and count across a LIST of texts — log lines, document
chunks, knowledge snippets — instead of a single text (single-text
match/extract/replace is covered by ``RegexTool``). Four modes are
supported:

* ``search`` — scan ``texts`` (a list of strings) with one ``pattern``
  and return the matching indices plus, for every match, the exact
  character span and a context window of ``context_chars`` characters
  on either side of the span (edge-clamped to the entry).
* ``filter`` — return the matching entries themselves, with their
  indices and per-entry match counts; with ``invert=True`` the
  NON-matching entries are returned instead.
* ``count`` — exact per-entry match counts for every entry (including
  zeros) plus the total number of matches.
* ``index_of`` — given a batch of ``patterns``, return the index of the
  first entry that matches each pattern (``null`` when no entry does;
  with ``invert=True`` the first entry that does NOT match).

By default the pattern is a regular expression (compiled with the
optional ``flags`` — ``IGNORECASE``/``I``, ``MULTILINE``/``M``,
``DOTALL``/``S``, ``ASCII``/``A``). With ``regex=False`` the pattern is
matched as a literal substring (metacharacters are escaped, so a
pattern like ``a.c`` only matches the exact text ``a.c``), and the
``case_sensitive`` option selects case-sensitive or case-insensitive
matching in both modes. All spans and contexts are character (Unicode
code point) offsets into the original entry.

Input validation is strict and happens before any computation:
malformed parameters (a ``texts`` that is not a non-empty list of
strings, oversized lists or entries, an empty or non-string pattern,
an empty or oversized ``index_of`` pattern batch, unknown mode or
flag, non-boolean ``regex`` / ``case_sensitive`` / ``invert``,
``invert`` outside the ``filter`` / ``index_of`` modes, ``flags``
combined with ``regex=False``, an out-of-range ``context_chars``)
raise a ``ValueError``, mirroring the other common tools. A pattern
that fails to compile is content-dependent, so it is returned as a
structured ``error`` payload carrying the ``re.error`` message instead
of raising.

Resource guarding is done through input and result caps ONLY — the
tool never inspects patterns for catastrophic backtracking: at most
``max_texts`` entries of ``max_text_chars`` characters each are
accepted, at most ``max_patterns`` patterns per ``index_of`` batch,
and the ``search`` / ``filter`` modes stop collecting results once
``max_entries`` matching entries or ``max_matches`` total matches have
been recorded (the output then carries ``truncated: true`` with the
reason). ``count`` and ``index_of`` scan within those input caps and
are never truncated — their output is one line per entry or per
pattern. Note that an exponential-backtracking regex (for example
``(a+)+b``) can still be slow on adversarial inputs within the caps;
keep such patterns out of agent-facing calls.
"""

import re
from typing import Any, ClassVar, Dict, List, Optional, Pattern, Tuple, Union

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Regex flag names accepted in the `flags` option (regex mode only).
_FLAG_NAMES: Dict[str, int] = {
    "IGNORECASE": re.IGNORECASE,
    "I": re.IGNORECASE,
    "MULTILINE": re.MULTILINE,
    "M": re.MULTILINE,
    "DOTALL": re.DOTALL,
    "S": re.DOTALL,
    "ASCII": re.ASCII,
    "A": re.ASCII,
}


class MultiTextSearchTool(Tool):
    """Search / filter / count across a list of texts — grep for agents.

    Attributes:
        max_texts (int): Upper bound on the number of entries accepted
            in ``texts``; longer lists are rejected before any work.
        max_text_chars (int): Upper bound on the length of each entry
            (and of a single pattern).
        max_patterns (int): Upper bound on the ``index_of`` batch size.
        max_entries (int): Result cap — matching entries kept by the
            ``search`` / ``filter`` modes before truncation.
        max_matches (int): Result cap — total matches kept by the
            ``search`` mode (and counted by ``filter``) before
            truncation.
        max_context_chars (int): Upper bound for the per-call
            ``context_chars`` option.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "multi_text_search_tool"
    description: str = (
        "Multi-text search tool — grep for agents, pure Python stdlib, "
        "no network required. Searches a LIST of texts (log lines, "
        "document chunks, snippets) with one pattern (mode='search': "
        "matching indices plus per-match span and a context window; "
        "mode='filter': the matching entries themselves, or the "
        "non-matching ones with invert=True; mode='count': exact "
        "per-entry match counts; mode='index_of': first matching index "
        "for each pattern in a batch). Regex by default with optional "
        "flags (IGNORECASE, MULTILINE, DOTALL, ASCII), or literal "
        "substring matching with regex=False and a case option."
    )

    MODES: ClassVar[tuple] = ("search", "filter", "count", "index_of")
    INVERT_MODES: ClassVar[tuple] = ("filter", "index_of")

    max_texts: int = 5_000
    max_text_chars: int = 100_000
    max_patterns: int = 100
    max_entries: int = 100
    max_matches: int = 1_000
    max_context_chars: int = 1_000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any,
        texts: Any = None,
        pattern: Any = None,
        patterns: Any = None,
        regex: Any = True,
        case_sensitive: Any = True,
        flags: Any = None,
        context_chars: Any = 40,
        invert: Any = False,
    ) -> Dict[str, Any]:
        """Run one multi-text search operation.

        Args:
            mode (str): One of ``search`` / ``filter`` / ``count`` /
                ``index_of``.
            texts (List[str]): The list of texts to search. Required
                for every mode — a non-empty list of strings.
            pattern (str): The pattern to search with. Required for the
                ``search``, ``filter`` and ``count`` modes; must not be
                combined with ``patterns``.
            patterns (List[str]): A batch of patterns. Required for the
                ``index_of`` mode; must not be combined with
                ``pattern``.
            regex (bool): ``True`` (default) treats the pattern as a
                regular expression; ``False`` matches it as a literal
                substring (metacharacters are escaped).
            case_sensitive (bool): ``True`` (default) matches case
                sensitively; ``False`` matches case insensitively in
                both regex and literal modes.
            flags (str | List[str]): Optional regex flags — one name or
                a list of names from ``IGNORECASE``/``I``,
                ``MULTILINE``/``M``, ``DOTALL``/``S``, ``ASCII``/``A``.
                Regex mode only.
            context_chars (int): Characters of context on each side of
                a match span in ``search`` mode (default 40,
                edge-clamped to the entry).
            invert (bool): Return NON-matching entries (``filter``) or
                the first NON-matching index (``index_of``). Only
                valid in those two modes.

        Returns:
            Dict[str, Any]: The search result (matches / entries /
            counts / first indices plus the call context) or a
            structured ``error`` payload when a pattern fails to
            compile.

        Raises:
            ValueError: If any parameter is malformed (before any
            computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        clean_texts = self._validate_texts(texts)
        for option, value in (
            ("regex", regex),
            ("case_sensitive", case_sensitive),
            ("invert", invert),
        ):
            if not isinstance(value, bool):
                self._invalid(f"{option} must be a boolean (got {value!r})")
        if invert and mode not in self.INVERT_MODES:
            self._invalid(
                "invert is only supported for the "
                f"{', '.join(self.INVERT_MODES)} modes (got mode={mode!r})"
            )
        clean_context = self._validate_context_chars(context_chars)
        flag_bits, flag_names = self._validate_flags(flags, regex=bool(regex))
        clean_patterns = self._validate_patterns(mode, pattern, patterns)
        base: Dict[str, Any] = {
            "mode": mode,
            "regex": bool(regex),
            "case_sensitive": bool(case_sensitive),
        }
        if flag_names:
            base["flags"] = flag_names

        compiled = self._compile_all(
            clean_patterns,
            regex=bool(regex),
            case_sensitive=bool(case_sensitive),
            flag_bits=flag_bits,
        )
        if isinstance(compiled, tuple):
            failing_pattern, error = compiled
            return {
                **base,
                "pattern_count": len(clean_patterns),
                "error": {
                    "type": "invalid_regex",
                    "message": (
                        f"pattern {failing_pattern!r} failed to compile: "
                        f"{error}"
                    )[:500],
                },
            }

        if mode == "search":
            return self._run_search(
                clean_texts, compiled[0], clean_patterns[0], clean_context, base
            )
        if mode == "filter":
            return self._run_filter(
                clean_texts, compiled[0], clean_patterns[0], bool(invert), base
            )
        if mode == "count":
            return self._run_count(clean_texts, compiled[0], clean_patterns[0], base)
        return self._run_index_of(
            clean_texts, compiled, clean_patterns, bool(invert), base
        )

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"multi_text_search_tool: {message}")

    def _validate_texts(self, texts: Any) -> List[str]:
        """Validate the ``texts`` list: a non-empty list of bounded strings."""
        if not isinstance(texts, list):
            self._invalid(
                f"texts must be a non-empty list of strings (got {texts!r})"
            )
        if not texts:
            self._invalid("texts must be a non-empty list of strings (got [])")
        if len(texts) > self.max_texts:
            self._invalid(
                f"texts exceeds the {self.max_texts:,}-entry limit "
                f"(got {len(texts):,} entries)"
            )
        for position, entry in enumerate(texts):
            if isinstance(entry, bool) or not isinstance(entry, str):
                self._invalid(
                    "texts must contain only strings "
                    f"(got {entry!r} at position {position})"
                )
            if len(entry) > self.max_text_chars:
                self._invalid(
                    f"texts[{position}] exceeds the "
                    f"{self.max_text_chars:,}-character limit "
                    f"(got {len(entry):,} characters)"
                )
        return texts

    def _validate_context_chars(self, context_chars: Any) -> int:
        """Validate the ``context_chars`` window size."""
        if isinstance(context_chars, bool) or not isinstance(context_chars, int):
            self._invalid(
                f"context_chars must be an integer (got {context_chars!r})"
            )
        if context_chars < 0 or context_chars > self.max_context_chars:
            self._invalid(
                "context_chars must be between 0 and "
                f"{self.max_context_chars} (got {context_chars!r})"
            )
        return context_chars

    @classmethod
    def _validate_flags(cls, flags: Any, regex: bool) -> Tuple[int, List[str]]:
        """Normalize the ``flags`` option to ``(re flag bits, names)``.

        Accepts ``None``, a single flag name, or a list of flag names
        (regex mode only). Unknown names raise before any compilation.
        """
        if flags is None:
            return 0, []
        if not regex:
            cls._invalid(
                "flags are only valid in regex mode "
                "(regex=False matches a literal substring)"
            )
        if isinstance(flags, str):
            names = [flags]
        elif isinstance(flags, list) and all(
            isinstance(item, str) for item in flags
        ):
            names = list(flags)
        else:
            cls._invalid(
                "flags must be a flag name or a list of flag names from: "
                f"{', '.join(sorted(set(_FLAG_NAMES)))} (got {flags!r})"
            )
        if not names:
            cls._invalid("flags must not be an empty list (got [])")
        bits = 0
        seen: List[str] = []
        for name in names:
            upper = name.strip().upper()
            if upper not in _FLAG_NAMES:
                cls._invalid(
                    "flags must be a flag name or a list of flag names "
                    f"from: {', '.join(sorted(set(_FLAG_NAMES)))} "
                    f"(got {name!r})"
                )
            bits |= _FLAG_NAMES[upper]
            if upper not in seen:
                seen.append(upper)
        return bits, seen

    def _validate_patterns(
        self, mode: str, pattern: Any, patterns: Any
    ) -> List[str]:
        """Validate ``pattern`` / ``patterns`` into a list of patterns."""
        if mode == "index_of":
            if pattern is not None:
                self._invalid("index_of mode takes patterns (a list), not pattern")
            if not isinstance(patterns, list):
                self._invalid(
                    "patterns must be a non-empty list of non-empty "
                    f"strings (got {patterns!r})"
                )
            if not patterns:
                self._invalid(
                    "patterns must be a non-empty list of non-empty strings "
                    "(got [])"
                )
            if len(patterns) > self.max_patterns:
                self._invalid(
                    f"patterns exceeds the {self.max_patterns:,}-pattern "
                    f"limit (got {len(patterns):,} patterns)"
                )
            for position, item in enumerate(patterns):
                if isinstance(item, bool) or not isinstance(item, str):
                    self._invalid(
                        "patterns must contain only non-empty strings "
                        f"(got {item!r} at position {position})"
                    )
                if not item:
                    self._invalid(
                        "patterns must contain only non-empty strings "
                        f"(got '' at position {position})"
                    )
            return patterns
        if patterns is not None:
            self._invalid(
                f"patterns is only valid for the index_of mode (got mode={mode!r})"
            )
        if pattern is None or isinstance(pattern, bool) or not isinstance(pattern, str):
            self._invalid(f"pattern must be a non-empty string (got {pattern!r})")
        if not pattern:
            self._invalid("pattern must be a non-empty string (got '')")
        if len(pattern) > self.max_text_chars:
            self._invalid(
                f"pattern exceeds the {self.max_text_chars:,}-character limit "
                f"(got {len(pattern):,} characters)"
            )
        return [pattern]

    # ------------------------------------------------------------------ #
    # Pattern compilation (content errors → structured payload)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _compile_all(
        patterns: List[str], regex: bool, case_sensitive: bool, flag_bits: int
    ) -> Union[List[Pattern[str]], Tuple[str, re.error]]:
        """Compile every pattern, returning ``(pattern, re.error)`` on failure.

        Literal mode (``regex=False``) escapes the pattern so it matches
        the exact substring; case-insensitive matching adds
        ``re.IGNORECASE`` in both modes, which keeps spans aligned with
        the original text.
        """
        bits = flag_bits | (0 if case_sensitive else re.IGNORECASE)
        compiled: List[Pattern[str]] = []
        for item in patterns:
            source = item if regex else re.escape(item)
            try:
                compiled.append(re.compile(source, bits))
            except re.error as error:
                return item, error
        return compiled

    # ------------------------------------------------------------------ #
    # search mode
    # ------------------------------------------------------------------ #

    def _run_search(
        self,
        texts: List[str],
        compiled: Pattern[str],
        pattern: str,
        context_chars: int,
        base: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Collect matches with spans and edge-clamped context windows."""
        matches: List[Dict[str, Any]] = []
        matching_indices: List[int] = []
        entry_count = 0
        match_count = 0
        stop_reason: Optional[str] = None
        entries_scanned = 0
        for index, text in enumerate(texts):
            entries_scanned = index + 1
            first_in_entry = True
            for found in compiled.finditer(text):
                if match_count >= self.max_matches:
                    stop_reason = "max_matches"
                    break
                if first_in_entry and entry_count >= self.max_entries:
                    stop_reason = "max_entries"
                    break
                if first_in_entry:
                    matching_indices.append(index)
                    entry_count += 1
                    first_in_entry = False
                start, end = found.span()
                matches.append(
                    {
                        "index": index,
                        "start": start,
                        "end": end,
                        "matched": found.group(0),
                        "context": text[
                            max(0, start - context_chars) : min(
                                len(text), end + context_chars
                            )
                        ],
                    }
                )
                match_count += 1
            if stop_reason is not None:
                break
        return {
            **base,
            "pattern": pattern,
            "context_chars": context_chars,
            "total_entries": len(texts),
            "entries_scanned": entries_scanned,
            "matching_indices": matching_indices,
            "entry_count": entry_count,
            "match_count": match_count,
            "matches": matches,
            "truncated": stop_reason is not None,
            "truncation_reason": stop_reason,
        }

    # ------------------------------------------------------------------ #
    # filter mode
    # ------------------------------------------------------------------ #

    def _run_filter(
        self,
        texts: List[str],
        compiled: Pattern[str],
        pattern: str,
        invert: bool,
        base: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Keep the matching (or non-matching) entries themselves."""
        results: List[Dict[str, Any]] = []
        kept_indices: List[int] = []
        total_matches = 0
        stop_reason: Optional[str] = None
        entries_scanned = 0
        for index, text in enumerate(texts):
            entries_scanned = index + 1
            entry_matches = 0
            capped_in_entry = False
            if not invert:
                for _ in compiled.finditer(text):
                    if total_matches >= self.max_matches:
                        capped_in_entry = True
                        break
                    entry_matches += 1
                    total_matches += 1
                keep = entry_matches > 0
            else:
                keep = compiled.search(text) is None
            if keep:
                if len(results) >= self.max_entries:
                    stop_reason = "max_entries"
                    break
                kept_indices.append(index)
                if invert:
                    results.append({"index": index, "text": text})
                else:
                    results.append(
                        {"index": index, "text": text, "match_count": entry_matches}
                    )
            if capped_in_entry:
                stop_reason = "max_matches"
                break
        indices_key = (
            "non_matching_indices" if invert else "matching_indices"
        )
        payload: Dict[str, Any] = {
            **base,
            "pattern": pattern,
            "invert": invert,
            "total_entries": len(texts),
            "entries_scanned": entries_scanned,
            indices_key: kept_indices,
            "entry_count": len(results),
            "match_count": total_matches,
            "results": results,
            "truncated": stop_reason is not None,
            "truncation_reason": stop_reason,
        }
        return payload

    # ------------------------------------------------------------------ #
    # count mode
    # ------------------------------------------------------------------ #

    def _run_count(
        self,
        texts: List[str],
        compiled: Pattern[str],
        pattern: str,
        base: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Count matches in every entry exactly (output: one int per entry)."""
        counts: List[Dict[str, int]] = []
        total = 0
        entries_with_matches = 0
        for index, text in enumerate(texts):
            entry_count = sum(1 for _ in compiled.finditer(text))
            counts.append({"index": index, "count": entry_count})
            total += entry_count
            if entry_count:
                entries_with_matches += 1
        return {
            **base,
            "pattern": pattern,
            "total_entries": len(texts),
            "entries_scanned": len(texts),
            "entries_with_matches": entries_with_matches,
            "match_count": total,
            "counts": counts,
            "truncated": False,
            "truncation_reason": None,
        }

    # ------------------------------------------------------------------ #
    # index_of mode
    # ------------------------------------------------------------------ #

    def _run_index_of(
        self,
        texts: List[str],
        compiled_list: List[Pattern[str]],
        patterns: List[str],
        invert: bool,
        base: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Find the first matching (or non-matching) index per pattern."""
        results: List[Dict[str, Any]] = []
        found_count = 0
        for pattern, compiled in zip(patterns, compiled_list):
            first_index: Optional[int] = None
            for index, text in enumerate(texts):
                if (compiled.search(text) is not None) != invert:
                    first_index = index
                    break
            if first_index is not None:
                found_count += 1
            results.append({"pattern": pattern, "index": first_index})
        return {
            **base,
            "patterns": patterns,
            "invert": invert,
            "total_entries": len(texts),
            "pattern_count": len(patterns),
            "found_count": found_count,
            "results": results,
            "truncated": False,
            "truncation_reason": None,
        }
