#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: conflict_parser_tool.py

"""Git merge-conflict parser / resolver tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency conflict utility that
agents can call while repairing files left in a conflicted state by a
merge or rebase: inspecting the conflict regions, measuring how bad the
damage is, applying programmatic resolutions, or falling back to a naive
marker strip.

The tool understands both marker styles git produces:

* ``merge`` — ``<<<<<<< ours`` / ``=======`` / ``>>>>>>> theirs``
* ``diff3`` — ``<<<<<<< ours`` / ``||||||| base`` / ``=======`` /
  ``>>>>>>> theirs`` (the ``--diff3`` style, which also carries the
  common ancestor section)

and supports four modes:

* ``parse`` — split the text into structured conflict regions
  (``start_line``, ``ours`` lines, ``theirs`` lines, ``base`` lines or
  ``null`` for merge-style conflicts, ``marker_style``,
  ``resolved_flag``) plus the ``clean_lines`` count and the ``total``
  line count. Marker lines themselves are never part of ``ours`` /
  ``base`` / ``theirs``.
* ``stats`` — aggregate numbers: ``conflict_count``, total
  ``ours_lines`` / ``theirs_lines`` / ``base_lines``, and an overlap
  hint — the ``identical_count`` of conflicts whose ``ours`` and
  ``theirs`` sides are identical and are therefore trivially resolvable
  by picking either side.
* ``resolve`` — apply a list of resolutions ``{index, choose, ...}`` in
  index order, where ``choose`` is one of ``ours`` / ``theirs`` /
  ``base`` / ``custom`` / ``identical``: ``base`` requires a diff3-style
  conflict, ``custom`` replaces the whole conflict block with the exact
  ``custom_text`` (followed by the closing marker's line terminator; an
  empty ``custom_text`` removes the block entirely), and ``identical``
  is the documented shortcut for trivial conflicts (it verifies
  ``ours == theirs`` and keeps one copy).
  Unresolved conflicts are left untouched, so an agent can iterate; the
  result carries the resolved text and the ``remaining_conflicts``
  count.
* ``strip`` — the naive, lossy fallback: remove every conflict block
  keeping the ``ours`` side (default) or the ``theirs`` side, without
  inspecting the content. Documented as lossy because the dropped side
  is gone for good; prefer ``resolve``.

Marker recognition uses exactly seven-character git markers —
``^<{7} ?``, ``^\\|{7}``, ``^={7}$`` and ``^>{7} ?`` — with the optional
trailing label (``<<<<<<< HEAD``) tolerated on the opening and closing
markers. Line endings are preserved token-by-token (``\\n``, ``\\r`` and
``\\r\\n`` are all handled), so ``resolve`` and ``strip`` on text that
contains no conflict markers return the input byte-identically.

Input validation is strict and happens before any computation:
malformed parameters (wrong types, unknown mode / ``choose`` / ``keep``,
a ``custom`` resolution without ``custom_text``, duplicated or
out-of-range resolution indices, oversized text) raise a ``ValueError``,
mirroring the other common tools. Errors that depend on the *content
being processed* — an unclosed conflict (missing ``=======`` or
``>>>>>>>``), a stray marker outside any conflict, choosing ``base`` on
a merge-style conflict, or an ``identical`` resolution whose sides
actually differ — are returned as a structured ``error`` payload (with
the offending line or conflict index where applicable) so an agent can
react without catching exceptions.
"""

import re
from typing import Any, ClassVar

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Conflict-marker patterns: exactly seven characters, git style. The
# opening and closing markers tolerate an optional space + branch label
# ("<<<<<<< HEAD", ">>>>>>> feature/x"); the separator must be a bare
# seven-character line; the diff3 base marker carries no label.
_OURS_OPEN_RE = re.compile(r"^<{7} ?")
_BASE_OPEN_RE = re.compile(r"^\|{7}")
_SEPARATOR_RE = re.compile(r"^={7}$")
_THEIRS_CLOSE_RE = re.compile(r"^>{7} ?")

# Line tokenizer: every line together with its own terminator ("\r\n",
# "\n" or "\r"), so clean text round-trips byte-identically and mixed
# endings inside one document survive resolve/strip.
_LINE_RE = re.compile(r"[^\r\n]*(?:\r\n|\r|\n)|[^\r\n]+")


class ConflictParserTool(Tool):
    """Git merge-conflict parser / resolver built purely on the stdlib.

    Attributes:
        max_text_chars (int): Upper bound on the ``text`` /
            ``custom_text`` input length; longer inputs are rejected
            before any work.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "conflict_parser_tool"
    description: str = (
        "Merge-conflict parser tool — pure Python stdlib, no network "
        "required. Parses git merge/diff3 conflict markers into "
        "structured regions (mode='parse'), reports conflict statistics "
        "with a trivially-resolvable overlap hint (mode='stats'), "
        "applies programmatic resolutions choosing ours/theirs/base/"
        "custom or the identical shortcut (mode='resolve'), or naively "
        "strips markers keeping one side (mode='strip', lossy)."
    )

    MODES: ClassVar[tuple] = ("parse", "stats", "resolve", "strip")
    CHOOSE_VALUES: ClassVar[tuple] = (
        "ours", "theirs", "base", "custom", "identical",
    )
    KEEP_VALUES: ClassVar[tuple] = ("ours", "theirs")

    max_text_chars: int = 100_000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        text: Any = None,
        resolutions: Any = None,
        keep: Any = None,
    ) -> dict[str, Any]:
        """Run one conflict operation.

        Args:
            mode (str): One of ``parse`` / ``stats`` / ``resolve`` /
                ``strip``.
            text (str): The document text to process. May be empty (no
                conflicts), but must be a string.
            resolutions (list[dict]): ``resolve`` mode only — a list of
                ``{"index": int, "choose": "ours"|"theirs"|"base"|
                "custom"|"identical", "custom_text": str}`` entries.
                ``custom_text`` is required for ``choose="custom"`` and
                forbidden otherwise; indices are 0-based positions in
                the parsed conflict list and must not repeat.
            keep (str): ``strip`` mode only — ``"ours"`` (default) or
                ``"theirs"``: the side kept when conflict markers are
                removed.

        Returns:
            Dict[str, Any]: The operation result (``conflicts`` for
            parse, statistics for stats, the resolved / stripped text
            as ``result`` for resolve / strip) or a structured
            ``error`` payload for content-level failures (unclosed
            conflict, stray marker, invalid resolution target).

        Raises:
            ValueError: If any parameter is malformed (before any
            computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        clean_text = self._validate_text(text)
        if mode == "resolve":
            clean_resolutions = self._validate_resolutions(resolutions)
        else:
            if resolutions is not None:
                self._invalid(
                    "resolutions is only accepted in the resolve mode "
                    f"(got {resolutions!r})"
                )
            clean_resolutions = None
        if mode == "strip":
            clean_keep = self._validate_keep(keep)
        else:
            if keep is not None:
                self._invalid(
                    f"keep is only accepted in the strip mode (got {keep!r})"
                )
            clean_keep = None

        tokens = self._tokenize(clean_text)
        conflicts, parse_error = self._parse_tokens(tokens)
        if parse_error is not None:
            return {
                "mode": mode,
                "error": parse_error,
            }
        total = len(tokens)
        clean_lines = total - sum(
            conflict["end_index"] - conflict["start_index"] + 1
            for conflict in conflicts
        )

        if mode == "parse":
            return {
                "mode": "parse",
                "conflicts": [
                    self._conflict_payload(conflict) for conflict in conflicts
                ],
                "conflict_count": len(conflicts),
                "clean_lines": clean_lines,
                "total": total,
            }
        if mode == "stats":
            return self._run_stats(conflicts, clean_lines, total)
        if mode == "resolve":
            return self._run_resolve(
                tokens, conflicts, clean_resolutions, total
            )
        return self._run_strip(tokens, conflicts, clean_keep)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"conflict_parser_tool: {message}")

    @classmethod
    def _validate_text(cls, text: Any) -> str:
        """Validate the ``text`` input (also used for ``custom_text``).

        The empty string is a valid (conflict-free) document; anything
        that is not a string, and any string above the size limit, is
        rejected.
        """
        if text is None or isinstance(text, bool) or not isinstance(text, str):
            cls._invalid(f"text must be a string (got {text!r})")
        if len(text) > 100_000:
            cls._invalid(
                f"text exceeds the {100_000:,}-character limit "
                f"(got {len(text):,} characters)"
            )
        return text

    def _validate_resolutions(self, resolutions: Any) -> list[dict[str, Any]]:
        """Validate the ``resolve``-mode resolution list shape.

        Each entry must be a dict with an integer ``index`` (>= 0, not
        repeated), a whitelisted ``choose`` value, and a string
        ``custom_text`` that is required for ``choose='custom'`` and
        forbidden otherwise. Whether an index actually exists in the
        parsed document is checked later, once the text is parsed.
        """
        if resolutions is None:
            self._invalid(
                "resolutions must be a list of {index, choose, ...} dicts "
                "in the resolve mode (got None)"
            )
        if isinstance(resolutions, (str, bytes)) or not isinstance(
            resolutions, (list, tuple)
        ):
            self._invalid(
                "resolutions must be a list of {index, choose, ...} dicts "
                f"(got {resolutions!r})"
            )
        seen_indices: set[int] = set()
        cleaned: list[dict[str, Any]] = []
        for position, entry in enumerate(resolutions):
            if not isinstance(entry, dict):
                self._invalid(
                    f"resolutions[{position}] must be a dict with keys "
                    f"'index' and 'choose' (got {entry!r})"
                )
            index = entry.get("index")
            if (
                index is None
                or isinstance(index, bool)
                or not isinstance(index, int)
            ):
                self._invalid(
                    f"resolutions[{position}].index must be a non-negative "
                    f"integer (got {index!r})"
                )
            if index < 0:
                self._invalid(
                    f"resolutions[{position}].index must be a non-negative "
                    f"integer (got {index})"
                )
            if index in seen_indices:
                self._invalid(
                    f"resolutions[{position}].index {index} is duplicated — "
                    "each conflict can be resolved at most once"
                )
            seen_indices.add(index)
            choose = entry.get("choose")
            if choose not in self.CHOOSE_VALUES:
                self._invalid(
                    f"resolutions[{position}].choose must be one of: "
                    f"{', '.join(self.CHOOSE_VALUES)} (got {choose!r})"
                )
            custom_text = entry.get("custom_text")
            if choose == "custom":
                if custom_text is None or isinstance(custom_text, bool) or not isinstance(custom_text, str):
                    self._invalid(
                        f"resolutions[{position}] with choose='custom' "
                        f"requires a string custom_text (got {custom_text!r})"
                    )
                if len(custom_text) > 100_000:
                    self._invalid(
                        f"resolutions[{position}].custom_text exceeds the "
                        f"{100_000:,}-character limit "
                        f"(got {len(custom_text):,} characters)"
                    )
            elif custom_text is not None:
                self._invalid(
                    f"resolutions[{position}].custom_text is only accepted "
                    f"with choose='custom' (got choose={choose!r} with "
                    f"custom_text={custom_text!r})"
                )
            cleaned.append(
                {"index": index, "choose": choose, "custom_text": custom_text}
            )
        return cleaned

    def _validate_keep(self, keep: Any) -> str:
        """Validate the ``strip``-mode side selector."""
        if keep is None:
            return "ours"
        if keep not in self.KEEP_VALUES:
            self._invalid(
                f"keep must be one of: {', '.join(self.KEEP_VALUES)} "
                f"(got {keep!r})"
            )
        return keep

    # ------------------------------------------------------------------ #
    # Tokenization and conflict parsing
    # ------------------------------------------------------------------ #

    @staticmethod
    def _tokenize(text: str) -> list[tuple[str, str]]:
        """Split text into ``(content, terminator)`` line tokens.

        The terminator is ``"\\r\\n"``, ``"\\n"`` or ``"\\r"`` (empty for
        a final line without trailing newline). Joining ``content +
        terminator`` over all tokens reproduces the input exactly.
        """
        tokens: list[tuple[str, str]] = []
        for match in _LINE_RE.finditer(text):
            raw = match.group(0)
            if raw.endswith("\r\n"):
                tokens.append((raw[:-2], "\r\n"))
            elif raw.endswith(("\n", "\r")):
                tokens.append((raw[:-1], raw[-1:]))
            else:
                tokens.append((raw, ""))
        return tokens

    @staticmethod
    def _unexpected_marker_error(line: int, content: str) -> dict[str, Any]:
        """Build the structured error for a marker outside any conflict."""
        return {
            "type": "unexpected_marker",
            "message": (
                f"line {line} looks like a conflict marker "
                f"({content[:32]!r}) but no conflict is open — expected a "
                "'<<<<<<<' opening marker first"
            ),
            "line": line,
        }

    def _parse_tokens(
        self, tokens: list[tuple[str, str]]
    ) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
        """Run the conflict state machine over the line tokens.

        Returns the list of parsed conflicts (each carrying token
        indices and line tuples for byte-faithful reconstruction) and an
        error payload, or ``(conflicts, None)`` on success.
        """

        def unclosed(conflict: dict[str, Any], detail: str) -> dict[str, Any]:
            return {
                "type": "unclosed_conflict",
                "message": (
                    "conflict opened on line "
                    f"{conflict['start_line']} is not closed properly "
                    f"({detail}) — expected '<<<<<<< ours ... ======= ... "
                    ">>>>>>> theirs'"
                ),
                "line": conflict["start_line"],
            }

        conflicts: list[dict[str, Any]] = []
        state = "seeking"
        current: dict[str, Any] | None = None
        for index, (content, terminator) in enumerate(tokens):
            line = index + 1
            if state == "seeking":
                if _OURS_OPEN_RE.match(content):
                    current = {
                        "start_index": index,
                        "end_index": None,
                        "start_line": line,
                        "marker_style": None,
                        "ours": [],
                        "base": None,
                        "theirs": [],
                    }
                    state = "ours"
                elif (
                    _SEPARATOR_RE.match(content)
                    or _BASE_OPEN_RE.match(content)
                    or _THEIRS_CLOSE_RE.match(content)
                ):
                    return [], self._unexpected_marker_error(line, content)
                # Any other line is clean text.
            elif state == "ours":
                assert current is not None
                if _SEPARATOR_RE.match(content):
                    current["marker_style"] = "merge"
                    state = "theirs"
                elif _BASE_OPEN_RE.match(content):
                    current["marker_style"] = "diff3"
                    current["base"] = []
                    state = "base"
                elif _OURS_OPEN_RE.match(content):
                    return [], unclosed(
                        current,
                        f"another '<<<<<<<' opens on line {line} before a "
                        "'=======' separator was found",
                    )
                elif _THEIRS_CLOSE_RE.match(content):
                    return [], unclosed(
                        current,
                        f"a '>>>>>>>' closes on line {line} before a "
                        "'=======' separator was found",
                    )
                else:
                    current["ours"].append((content, terminator))
            elif state == "base":
                assert current is not None
                if _SEPARATOR_RE.match(content):
                    state = "theirs"
                elif (
                    _OURS_OPEN_RE.match(content)
                    or _BASE_OPEN_RE.match(content)
                    or _THEIRS_CLOSE_RE.match(content)
                ):
                    return [], unclosed(
                        current,
                        f"a stray marker ({content[:32]!r}) appears on line "
                        f"{line} inside the base section",
                    )
                else:
                    current["base"].append((content, terminator))
            else:  # state == "theirs"
                assert current is not None
                if _THEIRS_CLOSE_RE.match(content):
                    current["end_index"] = index
                    conflicts.append(current)
                    current = None
                    state = "seeking"
                elif (
                    _OURS_OPEN_RE.match(content)
                    or _SEPARATOR_RE.match(content)
                    or _BASE_OPEN_RE.match(content)
                ):
                    return [], unclosed(
                        current,
                        f"a stray marker ({content[:32]!r}) appears on line "
                        f"{line} before the '>>>>>>>' closing marker",
                    )
                else:
                    current["theirs"].append((content, terminator))
        if state != "seeking":
            assert current is not None
            if current["marker_style"] is None:
                detail = "the input ends after the 'ours' section"
            elif current["base"] is not None and state == "base":
                detail = "the input ends after the 'base' section"
            else:
                detail = "the input ends before the '>>>>>>>' closing marker"
            return [], unclosed(current, detail)
        return conflicts, None

    # ------------------------------------------------------------------ #
    # Mode implementations
    # ------------------------------------------------------------------ #

    @staticmethod
    def _contents(section: list[tuple[str, str]]) -> list[str]:
        """Line contents of a section, without terminators."""
        return [content for content, _ in section]

    @staticmethod
    def _verbatim(section: list[tuple[str, str]]) -> str:
        """Rejoin a section's lines byte-faithfully (own terminators)."""
        return "".join(content + terminator for content, terminator in section)

    def _conflict_payload(self, conflict: dict[str, Any]) -> dict[str, Any]:
        """Public parse-mode payload for one parsed conflict."""
        return {
            "start_line": conflict["start_line"],
            "ours": self._contents(conflict["ours"]),
            "base": (
                None
                if conflict["base"] is None
                else self._contents(conflict["base"])
            ),
            "theirs": self._contents(conflict["theirs"]),
            "marker_style": conflict["marker_style"],
            "resolved_flag": False,
        }

    def _run_stats(
        self,
        conflicts: list[dict[str, Any]],
        clean_lines: int,
        total: int,
    ) -> dict[str, Any]:
        """Aggregate conflict statistics with the overlap hint."""
        identical_count = sum(
            1
            for conflict in conflicts
            if self._contents(conflict["ours"])
            == self._contents(conflict["theirs"])
        )
        conflict_count = len(conflicts)
        return {
            "mode": "stats",
            "conflict_count": conflict_count,
            "ours_lines": sum(len(conflict["ours"]) for conflict in conflicts),
            "theirs_lines": sum(
                len(conflict["theirs"]) for conflict in conflicts
            ),
            "base_lines": sum(
                len(conflict["base"])
                for conflict in conflicts
                if conflict["base"] is not None
            ),
            "identical_count": identical_count,
            "clean_lines": clean_lines,
            "total": total,
            "overlap_hint": (
                f"{identical_count} of {conflict_count} conflicts have "
                "identical 'ours' and 'theirs' sides and are trivially "
                "resolvable (choose either side, or choose='identical')"
            ),
        }

    def _run_resolve(
        self,
        tokens: list[tuple[str, str]],
        conflicts: list[dict[str, Any]],
        resolutions: list[dict[str, Any]],
        total: int,
    ) -> dict[str, Any]:
        """Apply resolutions in index order and rebuild the text."""
        conflict_count = len(conflicts)
        for entry in sorted(resolutions, key=lambda item: item["index"]):
            index = entry["index"]
            if index >= conflict_count:
                if conflict_count:
                    self._invalid(
                        f"resolutions index {index} is out of range — the "
                        f"text contains {conflict_count} conflict(s), valid "
                        f"indices are 0..{conflict_count - 1}"
                    )
                self._invalid(
                    f"resolutions index {index} is out of range — the text "
                    "contains no conflicts"
                )

        replacements: dict[int, str] = {}
        for entry in sorted(resolutions, key=lambda item: item["index"]):
            index = entry["index"]
            conflict = conflicts[index]
            choose = entry["choose"]
            if choose == "ours":
                replacement = self._verbatim(conflict["ours"])
            elif choose == "theirs":
                replacement = self._verbatim(conflict["theirs"])
            elif choose == "base":
                if conflict["base"] is None:
                    return {
                        "mode": "resolve",
                        "error": {
                            "type": "invalid_resolution",
                            "message": (
                                f"resolution index {index} chooses 'base' "
                                f"but conflict {index} (line "
                                f"{conflict['start_line']}) is merge-style "
                                "and has no base section — only diff3-style "
                                "conflicts ('|||||||') carry one"
                            ),
                            "index": index,
                        },
                    }
                replacement = self._verbatim(conflict["base"])
            elif choose == "identical":
                if self._contents(conflict["ours"]) != self._contents(
                    conflict["theirs"]
                ):
                    return {
                        "mode": "resolve",
                        "error": {
                            "type": "invalid_resolution",
                            "message": (
                                f"resolution index {index} uses the "
                                "'identical' shortcut but conflict {index} "
                                f"(line {conflict['start_line']}) has "
                                "differing 'ours' and 'theirs' sides — "
                                "choose a side explicitly instead"
                            ),
                            "index": index,
                        },
                    }
                replacement = self._verbatim(conflict["ours"])
            else:  # choose == "custom"
                # custom_text is inserted verbatim, followed by the
                # closing marker's line terminator (if any) so the line
                # structure after the conflict stays intact; an empty
                # custom_text removes the conflict block entirely.
                closing_terminator = tokens[conflict["end_index"]][1]
                replacement = (
                    entry["custom_text"] + closing_terminator
                    if entry["custom_text"]
                    else ""
                )
            replacements[index] = replacement

        resolved_text, remaining = self._rebuild(
            tokens, conflicts, replacements
        )
        return {
            "mode": "resolve",
            "result": resolved_text,
            "resolved_count": len(replacements),
            "remaining_conflicts": remaining,
        }

    def _run_strip(
        self,
        tokens: list[tuple[str, str]],
        conflicts: list[dict[str, Any]],
        keep: str,
    ) -> dict[str, Any]:
        """Naively remove markers, keeping one whole side (lossy)."""
        replacements = {
            position: self._verbatim(conflict[keep])
            for position, conflict in enumerate(conflicts)
        }
        stripped_text, _ = self._rebuild(tokens, conflicts, replacements)
        return {"mode": "strip", "keep": keep, "result": stripped_text}

    @staticmethod
    def _rebuild(
        tokens: list[tuple[str, str]],
        conflicts: list[dict[str, Any]],
        replacements: dict[int, str],
    ) -> tuple[str, int]:
        """Rebuild the text, substituting resolved conflict blocks.

        Conflict blocks without a replacement are copied verbatim, so
        unresolved conflicts survive byte-identically.
        """
        block_starts = {
            conflict["start_index"]: position
            for position, conflict in enumerate(conflicts)
        }
        pieces: list[str] = []
        index = 0
        remaining = 0
        while index < len(tokens):
            if index in block_starts:
                position = block_starts[index]
                conflict = conflicts[position]
                if position in replacements:
                    pieces.append(replacements[position])
                else:
                    pieces.append(
                        "".join(
                            content + terminator
                            for content, terminator in tokens[
                                conflict["start_index"] : conflict["end_index"]
                                + 1
                            ]
                        )
                    )
                    remaining += 1
                index = conflict["end_index"] + 1
            else:
                content, terminator = tokens[index]
                pieces.append(content + terminator)
                index += 1
        return "".join(pieces), remaining
