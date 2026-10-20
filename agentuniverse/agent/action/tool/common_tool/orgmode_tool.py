#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: orgmode_tool.py

"""Org-mode outline parsing / analysis tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency reader for Emacs
``org-mode`` notes. It complements the markdown ``OutlineExtractor``
(#3531): org-mode's ``*``-asterisk heading system, ``TODO`` workflow
keywords, ``:PROPERTIES:`` drawers and ``#+`` in-buffer settings are a
distinct format that markdown tooling cannot read, so agents working
with Emacs users' notes get a dedicated parser.

The tool supports three modes:

* ``parse`` — org text in, flattened outline tree out. Each heading
  becomes ``{level, text, todo_state, tags, priority, span, drawers}``:

  - ``level`` — 1 for ``*`` headings, 2 for ``**`` … org-mode outlines
    are only *deepened* with more asterisks; any ``*+`` count is parsed
    and the level is capped at 10 (org's documented default outline
    depth — deeper headlines are accepted but reported as level 10,
    with a warning noting the original star count).
  - ``text`` — the heading title after removing the ``TODO`` keyword,
    the ``[#A]`` / ``[#B]`` / ``[#C]`` priority cookie and the trailing
    ``:tag1:tag2:`` tags.
  - ``todo_state`` — ``TODO`` / ``DONE`` by default, or the custom
    keyword set declared with ``#+TODO:`` / ``#+SEQ_TODO:`` /
    ``#+TYP_TODO:`` headers (a declared set replaces the default).
  - ``tags`` — trailing ``:tag1:tag2:`` colon-delimited tags
    (org tag characters only: letters, digits and ``_ @ # %``).
  - ``priority`` — ``A`` / ``B`` / ``C`` from a ``[#A]``-style cookie.
  - ``span`` — 1-based inclusive ``[start_line, end_line]`` of the
    whole subtree (heading line through the line before the next
    heading of the same or shallower level).
  - ``drawers`` — ``:PROPERTIES:`` / ``:LOGBOOK:`` / custom drawers
    found inside the subtree are *skipped* (their content is never
    inspected) but noted as ``{"name", "span"}`` records.

  ``#+TITLE`` / ``#+AUTHOR`` / ``#+FILETAGS`` meta lines are extracted
  into a ``meta`` mapping. Lines inside ``#+BEGIN_SRC`` (and every
  other ``#+BEGIN_…`` / ``#+END_…`` block) are immune to heading,
  drawer and keyword detection, so a literal ``* not a headline`` in a
  source block stays content.
* ``todo_summary`` — agenda-style statistics: per-state heading counts,
  the done ratio (done headings over headings carrying any todo
  keyword), and the next-action list — for every top-level (level 1)
  subtree, the first heading in document order that is in a
  needs-action state.
* ``strip`` — clean text out: drawers and ``#+`` keyword lines (block
  markers included) removed; with ``body_only=True`` heading lines are
  dropped as well, leaving plain body text.

Input validation is strict and happens before any computation: a wrong
``mode`` / ``body_only``, a non-string or empty or oversized ``text``
raises a ``ValueError``, mirroring the other common tools. Format
quirks of the *content being processed* are tolerated with warnings
instead of failing: malformed ``#+TODO:`` lines, duplicate ``#+TITLE``
declarations, invalid tag characters, levels deeper than 10 and
unclosed drawers / blocks — each reported in the ``warnings`` list of
the result. Parsing is fully deterministic and offline.
"""

import re
from typing import Any, ClassVar

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# A headline: one or more asterisks at column 0, then at least one
# space/tab (org-syntax: STARS KEYWORD PRIORITY TITLE TAGS).
_HEADING_RE = re.compile(r"\A(\*+)[ \t]+(.*)\Z")
# In-buffer setting: "#+KEYWORD: VALUE" at column 0 (case-insensitive
# keyword, matching org's own parser).
_KEYWORD_RE = re.compile(r"\A#\+([A-Za-z_]+):[ \t]*(.*)\Z")
# Block delimiters: #+BEGIN_SRC … #+END_SRC and friends.
_BLOCK_BEGIN_RE = re.compile(r"\A#\+BEGIN_([A-Za-z0-9_-]+)", re.IGNORECASE)
_BLOCK_END_RE = re.compile(r"\A#\+END_([A-Za-z0-9_-]+)[ \t]*\Z", re.IGNORECASE)
# Drawer delimiters — ":PROPERTIES:", ":LOGBOOK:", any ":NAME:" on a
# line of its own (leading whitespace allowed, as org indents drawers).
_DRAWER_START_RE = re.compile(r"\A[ \t]*:([A-Za-z0-9_-]+):[ \t]*\Z")
_DRAWER_END_RE = re.compile(r"\A[ \t]*:END:[ \t]*\Z")
# Trailing tags: whitespace, then ":tag1:tag2:" (org tag characters
# only, every segment non-empty, surrounded by colons).
_TAGS_RE = re.compile(r"[ \t]+(:[A-Za-z0-9_@#%]+(?::[A-Za-z0-9_@#%]+)*:)[ \t]*\Z")
# A single valid tag / todo-keyword word.
_WORD_RE = re.compile(r"\A[A-Za-z0-9_@#%+-]+\Z")
# Todo workflow declarations: #+TODO / #+SEQ_TODO / #+TYP_TODO.
_TODO_KEY_RE = re.compile(r"\A(TODO|SEQ_TODO|TYP_TODO)\Z", re.IGNORECASE)
# Trailing "(t)"-style fast-access key on a declared todo keyword.
_SHORTCUT_RE = re.compile(r"\([^()]*\)\Z")
# Priority cookies: [#A], [#B], [#C] — and anything else that merely
# looks like one (warned about, kept in the title).
_PRIORITY_RE = re.compile(r"\A\[#([ABC])\](?:[ \t]+(.*))?\Z", re.DOTALL)
_PRIORITY_LIKE_RE = re.compile(r"\A\[#([A-Za-z])\](?:[ \t]|\Z)")


class OrgModeTool(Tool):
    """Org-mode outline parsing tool built purely on the stdlib.

    Attributes:
        max_text_chars (int): Upper bound on the ``text`` input length;
            longer inputs are rejected before any work.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "orgmode_tool"
    description: str = (
        "Org-mode tool — pure Python stdlib parsing of Emacs org-mode "
        "notes, no network required. mode='parse' turns org text into a "
        "flattened outline tree (per-heading level (capped at 10), "
        "title text, todo_state from TODO/DONE or custom #+TODO: "
        "workflows, trailing :tag: lists, [#A]/[#B]/[#C] priority, "
        "subtree line spans, skipped :PROPERTIES: drawers with spans "
        "noted) plus #+TITLE/#+AUTHOR/#+FILETAGS meta; "
        "#+BEGIN_SRC content is immune to heading detection. "
        "mode='todo_summary' returns per-state counts, the done ratio "
        "and the first-TODO-per-top-level-subtree next-action list. "
        "mode='strip' returns the text without drawers and #+ lines "
        "(optionally body-only, dropping headings too)."
    )

    MODES: ClassVar[tuple] = ("parse", "todo_summary", "strip")
    # org's documented default outline depth; deeper headlines are
    # parsed but their level is capped (with a warning).
    MAX_LEVEL: ClassVar[int] = 10
    # org's built-in workflow, used when no #+TODO-style line declares
    # a custom set.
    DEFAULT_NEEDS_ACTION: ClassVar[tuple] = ("TODO",)
    DEFAULT_DONE: ClassVar[tuple] = ("DONE",)

    max_text_chars: int = 100_000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any = None,
        text: Any = None,
        body_only: Any = None,
    ) -> dict[str, Any]:
        """Run one org-mode operation.

        Args:
            mode (str): One of ``parse`` / ``todo_summary`` / ``strip``.
            text (str): The org-mode document text. Required for every
                mode; CRLF line endings are normalized to LF.
            body_only (bool): Strip mode only — when True the heading
                lines are dropped as well, leaving plain body text.
                Defaults to False; not used by the other modes.

        Returns:
            Dict[str, Any]: The operation result. ``parse`` returns the
            ``meta`` mapping, the flattened ``outline`` node list and
            the heading count; ``todo_summary`` returns the workflow,
            per-state ``counts``, ``done_ratio`` and ``next_actions``;
            ``strip`` returns the cleaned text as ``result``. Every
            result carries a ``warnings`` list describing tolerated
            format quirks (malformed #+ lines, levels beyond the cap,
            unclosed drawers or blocks).

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        clean_text = self._validate_text(text)
        clean_body_only = self._validate_body_only(body_only)
        document = self._scan(clean_text)
        if mode == "parse":
            return document.to_parse_result()
        if mode == "todo_summary":
            return document.to_todo_summary_result()
        return document.to_strip_result(clean_body_only)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"orgmode_tool: {message}")

    @classmethod
    def _validate_text(cls, text: Any) -> str:
        """Validate the ``text`` input and normalize line endings."""
        if text is None or isinstance(text, bool) or not isinstance(text, str):
            cls._invalid(f"text must be a non-empty string (got {text!r})")
        if not text:
            cls._invalid("text must be a non-empty string (got '')")
        if len(text) > 100_000:
            cls._invalid(
                f"text exceeds the {100_000:,}-character limit "
                f"(got {len(text):,} characters)"
            )
        return text.replace("\r\n", "\n").replace("\r", "\n")

    @classmethod
    def _validate_body_only(cls, body_only: Any) -> bool:
        """Validate the strip-mode ``body_only`` selector."""
        if body_only is None:
            return False
        if isinstance(body_only, bool):
            return body_only
        cls._invalid(
            "body_only must be a boolean and is only used by the strip "
            f"mode (got {body_only!r})"
        )

    # ------------------------------------------------------------------ #
    # Document scanner — one pass to classify lines, then fix-ups
    # ------------------------------------------------------------------ #

    def _scan(self, text: str) -> "_OrgDocument":
        """Classify every line and build the outline.

        The scanner walks the document with a small amount of state —
        the currently open block (``#+BEGIN_…``) and drawer — and
        dispatches each line to heading, keyword, drawer or body
        handling. Heading titles are decomposed in a second step so
        that ``#+TODO:`` declarations anywhere in the buffer apply to
        every heading, exactly like org's in-buffer settings.
        Everything downstream (parse / todo_summary / strip) reads the
        resulting :class:`_OrgDocument`.
        """
        lines = text.split("\n")
        doc = _OrgDocument(lines)
        needs_action: list[str] = []
        done: list[str] = []
        workflow_declared = False
        seen_title = False
        seen_author = False
        block_name: str | None = None
        block_start = 0
        drawer: dict[str, Any] | None = None

        for index, line in enumerate(lines):
            number = index + 1

            # -- inside a literal/greater block: only the matching END
            #    delimiter is special; everything else is content.
            if block_name is not None:
                end = _BLOCK_END_RE.match(line)
                if end and end.group(1).upper() == block_name:
                    doc.kinds[index] = _KIND_KEYWORD
                    block_name = None
                else:
                    doc.kinds[index] = _KIND_BLOCK_CONTENT
                continue

            # -- inside a drawer: content is skipped, only :END: counts.
            if drawer is not None:
                doc.kinds[index] = _KIND_DRAWER
                if _DRAWER_END_RE.match(line):
                    drawer["span"][1] = number
                    doc.attach_drawer(drawer)
                    drawer = None
                continue

            # -- a headline: asterisks at column 0 plus whitespace.
            heading = _HEADING_RE.match(line)
            if heading is not None:
                doc.kinds[index] = _KIND_HEADING
                stars = len(heading.group(1))
                level = min(stars, self.MAX_LEVEL)
                if stars > self.MAX_LEVEL:
                    doc.warn(
                        f"line {number}: headline has {stars} asterisks; "
                        f"level capped at {self.MAX_LEVEL}"
                    )
                doc.headings.append(
                    {
                        "level": level,
                        "raw_title": heading.group(2),
                        "span": [number, len(lines)],  # end fixed up below
                        "drawers": [],
                    }
                )
                continue

            # -- in-buffer syntax at column 0: "#+KEYWORD: VALUE"
            #    settings and #+BEGIN_/#+END_ block delimiters. Every
            #    such line is a "keyword" line for strip purposes.
            if line.startswith("#+"):
                doc.kinds[index] = _KIND_KEYWORD
                begin = _BLOCK_BEGIN_RE.match(line)
                if begin is not None:
                    block_name = begin.group(1).upper()
                    block_start = number
                    continue
                keyword = _KEYWORD_RE.match(line)
                if keyword is None:
                    # A stray "#+END_SRC", "#+note" or the like — valid
                    # enough org to tolerate, stripped but not parsed.
                    continue
                key = keyword.group(1).upper()
                value = keyword.group(2).strip()
                if _TODO_KEY_RE.match(key):
                    declared_needs, declared_done = self._parse_todo_line(
                        value, doc, number
                    )
                    if declared_needs or declared_done:
                        workflow_declared = True
                        for is_done, words in (
                            (False, declared_needs),
                            (True, declared_done),
                        ):
                            for word in words:
                                side = done if is_done else needs_action
                                other = needs_action if is_done else done
                                if word in side or word in other:
                                    doc.warn(
                                        f"line {number}: duplicate todo "
                                        f"keyword {word!r} ignored"
                                    )
                                else:
                                    side.append(word)
                elif key == "TITLE":
                    if seen_title:
                        doc.warn(
                            f"line {number}: duplicate #+TITLE ignored — "
                            "the first declaration wins"
                        )
                    elif value:
                        doc.meta["title"] = value
                        seen_title = True
                    else:
                        doc.warn(f"line {number}: empty #+TITLE ignored")
                elif key == "AUTHOR":
                    if seen_author:
                        doc.warn(
                            f"line {number}: duplicate #+AUTHOR ignored — "
                            "the first declaration wins"
                        )
                    elif value:
                        doc.meta["author"] = value
                        seen_author = True
                    else:
                        doc.warn(f"line {number}: empty #+AUTHOR ignored")
                elif key == "FILETAGS":
                    doc.meta["filetags"].extend(
                        self._parse_filetags(value, doc, number)
                    )
                # Any other #+ keyword (#+OPTIONS, #+DATE, …) is valid
                # org and simply carried as a keyword line.
                continue

            # -- a drawer start: ":PROPERTIES:" (or any :NAME:) alone
            #    on its (possibly indented) line.
            drawer_start = _DRAWER_START_RE.match(line)
            if drawer_start is not None:
                doc.kinds[index] = _KIND_DRAWER
                drawer = {
                    "name": drawer_start.group(1).upper(),
                    "span": [number, len(lines)],
                }
                continue

            doc.kinds[index] = _KIND_BODY

        if block_name is not None:
            doc.warn(
                f"#+BEGIN_{block_name} block starting at line {block_start} "
                "is never closed — the rest of the file is block content"
            )
        if drawer is not None:
            doc.warn(
                f":{drawer['name']}: drawer starting at line "
                f"{drawer['span'][0]} is never closed"
            )
            doc.attach_drawer(drawer)

        if not workflow_declared:
            needs_action = list(self.DEFAULT_NEEDS_ACTION)
            done = list(self.DEFAULT_DONE)
        doc.workflow = (needs_action, done)

        keywords = needs_action + done
        for heading in doc.headings:
            (
                heading["todo_state"],
                heading["priority"],
                heading["text"],
                heading["tags"],
            ) = self._parse_heading_title(
                heading.pop("raw_title"), keywords, doc, heading["span"][0]
            )
        doc.finish()
        return doc

    # ------------------------------------------------------------------ #
    # Heading title decomposition
    # ------------------------------------------------------------------ #

    @classmethod
    def _parse_heading_title(
        cls,
        raw: str,
        keywords: list[str],
        doc: "_OrgDocument",
        number: int,
    ) -> tuple[Any, Any, str, list[str]]:
        """Split a raw heading tail into (todo, priority, title, tags).

        Follows the org-syntax order ``KEYWORD PRIORITY TITLE TAGS``.
        The trailing ``:tag1:tag2:`` group is peeled off first (it must
        be preceded by whitespace, exactly like org requires), then the
        optional todo keyword (an exact, case-sensitive match against
        the declared workflow) and the optional ``[#A]`` / ``[#B]`` /
        ``[#C]`` cookie are taken from the head.
        """
        rest = raw

        # Optional trailing tags — peeled first so that a heading like
        # "* TODO :urgent:" keeps its whitespace boundary.
        tags: list[str] = []
        tag_match = _TAGS_RE.search(rest)
        if tag_match is not None:
            tags = [tag for tag in tag_match.group(1).split(":") if tag]
            rest = rest[: tag_match.start()].rstrip()

        # Optional todo keyword — the first word, only if declared.
        todo_state = None
        pieces = rest.split(None, 1)
        if pieces and pieces[0] in keywords:
            todo_state = pieces[0]
            rest = pieces[1] if len(pieces) > 1 else ""

        # Optional priority cookie.
        priority = None
        if rest.startswith("[#"):
            cookie = _PRIORITY_RE.match(rest)
            if cookie is not None:
                priority = cookie.group(1)
                rest = cookie.group(2) or ""
            elif _PRIORITY_LIKE_RE.match(rest) is not None:
                doc.warn(
                    f"line {number}: priority cookie "
                    f"{rest.split()[0]!r} is not one of [#A]/[#B]/[#C] — "
                    "kept in the heading title"
                )

        return todo_state, priority, rest.strip(), tags

    # ------------------------------------------------------------------ #
    # #+TODO / #+SEQ_TODO / #+TYP_TODO workflow declarations
    # ------------------------------------------------------------------ #

    @classmethod
    def _parse_todo_line(
        cls, value: str, doc: "_OrgDocument", number: int
    ) -> tuple[list[str], list[str]]:
        """Parse a ``#+TODO: TODO(t) DOING | DONE(D)`` declaration.

        Returns the declared needs-action and done keywords (either
        may be empty — an entirely unparsable line is tolerated with a
        warning and contributes nothing). Without a ``|`` separator
        every declared keyword counts as a needs-action state, which
        mirrors org's own handling. Shortcut keys in parentheses and
        the old-style double quotes around keywords are stripped.
        """
        if not value:
            doc.warn(f"line {number}: #+TODO line without keywords ignored")
            return [], []
        if "|" in value:
            left, _, right = value.partition("|")
            sides = (left, right)
        else:
            sides = (value, "")
        result: list[list[str]] = [[], []]
        for side_index, chunk in enumerate(sides):
            for token in chunk.split():
                word = token
                if len(word) >= 2 and word[0] == '"' and word[-1] == '"':
                    word = word[1:-1]
                word = _SHORTCUT_RE.sub("", word).strip()
                if not word:
                    doc.warn(
                        f"line {number}: unparsable todo keyword {token!r} "
                        "ignored"
                    )
                elif not _WORD_RE.match(word):
                    doc.warn(
                        f"line {number}: todo keyword {word!r} is not a "
                        "single org word (letters, digits and _ @ # % + -) "
                        "— ignored"
                    )
                elif word not in result[0] and word not in result[1]:
                    result[side_index].append(word)
        return result[0], result[1]

    # ------------------------------------------------------------------ #
    # #+FILETAGS meta
    # ------------------------------------------------------------------ #

    @classmethod
    def _parse_filetags(
        cls, value: str, doc: "_OrgDocument", number: int
    ) -> list[str]:
        """Parse a ``#+FILETAGS:`` value into a tag list.

        Both org spellings are accepted: ``#+FILETAGS: :tag1:tag2:``
        and ``#+FILETAGS: tag1 tag2``. Invalid tokens are skipped with
        a warning.
        """
        if not value:
            doc.warn(f"line {number}: empty #+FILETAGS ignored")
            return []
        raw_tags = (
            value.strip(":").split(":")
            if value.lstrip().startswith(":")
            else value.split()
        )
        tags: list[str] = []
        for tag in raw_tags:
            tag = tag.strip()
            if not tag:
                continue
            if _WORD_RE.match(tag):
                tags.append(tag)
            else:
                doc.warn(
                    f"line {number}: file tag {tag!r} has invalid characters "
                    "(letters, digits and _ @ # % + - only) — ignored"
                )
        return tags


# --------------------------------------------------------------------- #
# Internal document model
# --------------------------------------------------------------------- #

_KIND_HEADING = "heading"
_KIND_KEYWORD = "keyword"
_KIND_DRAWER = "drawer"
_KIND_BLOCK_CONTENT = "block_content"
_KIND_BODY = "body"


class _OrgDocument:
    """Everything the scanner learned about one org-mode document."""

    def __init__(self, lines: list[str]) -> None:
        self.lines = lines
        self.line_count = len(lines)
        self.kinds: list[str] = [_KIND_BODY] * self.line_count
        self.headings: list[dict[str, Any]] = []
        self.preamble_drawers: list[dict[str, Any]] = []
        self.meta: dict[str, Any] = {"title": None, "author": None, "filetags": []}
        self.workflow: tuple[list[str], list[str]] = ([], [])
        self.warnings: list[str] = []

    # -- bookkeeping used while scanning ----------------------------- #

    def warn(self, message: str) -> None:
        """Record a warning once (identical messages are deduplicated)."""
        if message not in self.warnings:
            self.warnings.append(message)

    def attach_drawer(self, drawer: dict[str, Any]) -> None:
        """Attach a closed drawer to its innermost enclosing heading."""
        owner = None
        for heading in self.headings:
            if heading["span"][0] < drawer["span"][0]:
                owner = heading
            else:
                break
        record = {"name": drawer["name"], "span": list(drawer["span"])}
        if owner is None:
            self.preamble_drawers.append(record)
        else:
            owner["drawers"].append(record)

    def finish(self) -> None:
        """Fix up subtree end lines now that all headings are known."""
        for index, heading in enumerate(self.headings):
            for later in self.headings[index + 1 :]:
                if later["level"] <= heading["level"]:
                    heading["span"][1] = later["span"][0] - 1
                    break

    # -- mode result builders ----------------------------------------- #

    def _public_heading(self, heading: dict[str, Any]) -> dict[str, Any]:
        """The node shape agents see (internal keys dropped)."""
        return {
            "level": heading["level"],
            "text": heading["text"],
            "todo_state": heading["todo_state"],
            "tags": heading["tags"],
            "priority": heading["priority"],
            "span": list(heading["span"]),
            "drawers": heading["drawers"],
        }

    def to_parse_result(self) -> dict[str, Any]:
        needs_action, done = self.workflow
        result: dict[str, Any] = {
            "mode": "parse",
            "meta": {
                "title": self.meta["title"],
                "author": self.meta["author"],
                "filetags": list(self.meta["filetags"]),
                "todo_workflow": {
                    "needs_action": list(needs_action),
                    "done": list(done),
                },
            },
            "heading_count": len(self.headings),
            "outline": [self._public_heading(h) for h in self.headings],
        }
        if self.preamble_drawers:
            result["preamble_drawers"] = list(self.preamble_drawers)
        if self.warnings:
            result["warnings"] = list(self.warnings)
        return result

    def to_todo_summary_result(self) -> dict[str, Any]:
        needs_action, done = self.workflow
        counts: dict[str, int] = {word: 0 for word in needs_action + done}
        todo_headings = 0
        done_headings = 0
        for heading in self.headings:
            state = heading["todo_state"]
            if state is None:
                continue
            todo_headings += 1
            counts[state] += 1
            if state in done:
                done_headings += 1
        done_ratio = (
            round(done_headings / todo_headings, 4) if todo_headings else None
        )

        # Next actions: for every top-level (level 1) subtree — or the
        # whole outline when no level-1 heading exists — the first
        # heading in document order still in a needs-action state.
        roots = [h for h in self.headings if h["level"] == 1]
        if roots:
            boundaries = [(root, root["span"][0], root["span"][1]) for root in roots]
        elif self.headings:
            boundaries = [
                (
                    None,
                    self.headings[0]["span"][0],
                    self.headings[-1]["span"][1],
                )
            ]
        else:
            boundaries = []
        next_actions: list[dict[str, Any]] = []
        for root, start, end in boundaries:
            action = None
            for heading in self.headings:
                if (
                    start <= heading["span"][0] <= end
                    and heading["todo_state"] in needs_action
                ):
                    action = {
                        "level": heading["level"],
                        "text": heading["text"],
                        "todo_state": heading["todo_state"],
                        "line": heading["span"][0],
                    }
                    break
            next_actions.append(
                {
                    "subtree": self._subtree_label(root),
                    "next_action": action,
                }
            )

        result: dict[str, Any] = {
            "mode": "todo_summary",
            "workflow": {
                "needs_action": list(needs_action),
                "done": list(done),
            },
            "heading_count": len(self.headings),
            "todo_heading_count": todo_headings,
            "counts": counts,
            "done_headings": done_headings,
            "done_ratio": done_ratio,
            "next_actions": next_actions,
        }
        if self.warnings:
            result["warnings"] = list(self.warnings)
        return result

    def _subtree_label(self, root: dict[str, Any] | None) -> str | None:
        """Label of a next-action subtree (its heading title)."""
        return root["text"] if root is not None else None

    def to_strip_result(self, body_only: bool) -> dict[str, Any]:
        """Rebuild the text minus drawers, #+ lines (and headings)."""
        kept = [
            line
            for index, line in enumerate(self.lines)
            if self.kinds[index] not in (_KIND_DRAWER, _KIND_KEYWORD)
            and not (body_only and self.kinds[index] == _KIND_HEADING)
        ]
        result: dict[str, Any] = {
            "mode": "strip",
            "body_only": body_only,
            "line_count": len(kept),
            "result": "\n".join(kept),
        }
        if self.warnings:
            result["warnings"] = list(self.warnings)
        return result
