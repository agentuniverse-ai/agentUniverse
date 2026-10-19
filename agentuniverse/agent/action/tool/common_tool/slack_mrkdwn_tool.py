#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: slack_mrkdwn_tool.py

"""Slack mrkdwn <-> standard Markdown conversion tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in integration)
with a zero-network, zero-dependency text converter aimed at chat-integration
agents: normalizing Slack message markup to standard Markdown for storage,
rendering or LLM consumption, preparing agent output for Slack posting, and
guessing which of the two dialects a piece of text is written in.

Supported constructs (the deterministic, well-defined subset):

``to_markdown`` (Slack mrkdwn -> standard Markdown):

* ``*bold*``         -> ``**bold**``  (mrkdwn bold is a *single* asterisk
  pair; ``**double stars**`` are literal in mrkdwn and pass through
  unchanged — emphasis delimiters are disambiguated by delimiter *character*,
  never by count).
* ``_italic_``       -> ``*italic*``  (mrkdwn italic is a single underscore
  pair; ``__double__`` passes through, and intraword underscores such as
  ``snake_case_name`` are never emphasized).
* ``~strike~``       -> ``~~strike~~`` (``~~double tildes~~`` pass through).
* Inline `` `code` `` spans and ``` fenced blocks are copied verbatim and
  shielded from every other transformation.
* ``<https://example.com|text>`` -> ``[text](https://example.com)``.
* ``<https://example.com>`` -> unchanged (already a valid CommonMark
  autolink).
* ``<@U123ABC>``     -> ``@U123ABC`` (raw user id; resolving ids to display
  names requires the Slack Web API, which this offline tool deliberately
  does not call — documented limitation).
* ``<@U123ABC|alice>`` -> ``@alice`` (the label, when Slack provided one,
  is used as the display name).
* ``<#C123ABC|general>`` -> ``#general``; ``<#C123ABC>`` -> ``#C123ABC``.
* ``<!here>`` / ``<@here>`` -> ``@here``; likewise ``<!channel>`` /
  ``<!everyone>``. Other special tokens (``<!date...>``, ``<!subteam^...>``)
  are left untouched.
* ``> quote`` lines are preserved (both dialects share the syntax) and the
  mrkdwn quote-to-end-of-message variant ``>>>`` becomes a ``> `` prefix on
  the remainder of its line and every following line (except lines inside
  fenced code blocks, which stay verbatim so the code is not corrupted).
* Numbered and bulleted lists are preserved unchanged.

``to_mrkdwn`` (standard Markdown -> Slack mrkdwn), the inverse mapping:

* ``**bold**``   -> ``*bold*``; ``*italic*`` -> ``_italic_``; ``_italic_``
  is already valid mrkdwn and passes through; ``~~strike~~`` -> ``~strike~``.
* ``[text](https://example.com)`` -> ``<https://example.com|text>``;
  ``<https://example.com>`` autolinks are already valid mrkdwn and pass
  through. Markdown images ``![alt](url)`` have no mrkdwn equivalent and
  are left untouched.
* ``@here`` / ``@channel`` / ``@everyone`` -> ``<!here>`` / ``<!channel>`` /
  ``<!everyone>``.
* ``@U123ABC`` / ``@W08LV...`` style raw Slack user ids -> ``<@U123ABC>``
  (best-effort, documented: plain handles such as ``@alice`` cannot be
  wrapped because mrkdwn requires the raw workspace id).
* ``> quote`` lines, lists, code spans and fenced blocks are preserved.

``detect`` — heuristic scoring of mrkdwn *signatures* (single-asterisk
emphasis spans, ``<@`` / ``<#`` / ``<!`` angle tokens, ``|``-labelled angle
links, ``>>>`` blocks) against Markdown signatures (double-asterisk bold,
``[text](url)`` links, double-tilde strikes, ATX headings). Returns a
verdict of ``mrkdwn`` / ``markdown`` / ``inconclusive`` plus the individual
signal counts; code spans and fenced blocks are ignored when scoring.

Round-trip property: for every construct of the supported subset,
``y = to_mrkdwn(to_markdown(x))`` is a fixed point of the same cycle
(``to_mrkdwn(to_markdown(y)) == y``), and for all constructs except labelled
mentions/channels the round trip is exact (``y == x``); ``<#C123|general>``
normalizes to its display form ``#general`` on the first cycle because the
channel id cannot be recovered from the name offline.

Input validation is strict and happens before any computation: an unknown
mode, a ``text`` that is not a non-empty string, text containing the NUL
placeholder character, or text above the length limit raises a
``ValueError``, mirroring the other common tools.
"""

import re
from typing import Any, Callable, ClassVar

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# --------------------------------------------------------------------- #
# Emphasis patterns. Delimiters are disambiguated by character, not by
# count: a doubled delimiter is literal and passes through untouched
# (the lookarounds refuse to match a delimiter adjacent to itself).
# Content must start and end with a non-space character so bullet lines
# such as "* item one" are never mistaken for emphasis.
# --------------------------------------------------------------------- #
_MRKDWN_BOLD = re.compile(  # mrkdwn *x*  -> markdown **x**
    r"(?<!\*)\*(?!\*)([^\s*](?:[^*\n]*?[^\s*])?)\*(?!\*)"
)
_MRKDWN_ITALIC = re.compile(  # mrkdwn _x_ -> markdown *x* (no intraword)
    r"(?<![\w_])_(?!_)([^\s_](?:[^_\n]*?[^\s_])?)_(?!_)(?![\w_])"
)
_MRKDWN_STRIKE = re.compile(  # mrkdwn ~x~ -> markdown ~~x~~
    r"(?<!~)~(?!~)([^\s~](?:[^~\n]*?[^\s~])?)~(?!~)"
)
_MD_ITALIC_STAR = re.compile(  # markdown *x* -> mrkdwn _x_
    r"(?<!\*)\*(?!\*)([^\s*](?:[^*\n]*?[^\s*])?)\*(?!\*)"
)
_MD_BOLD = re.compile(  # markdown **x** -> mrkdwn *x*
    r"(?<!\*)\*\*(?!\*)([^\s*](?:[^*\n]*?[^\s*])?)\*\*(?!\*)"
)
_MD_STRIKE = re.compile(  # markdown ~~x~~ -> mrkdwn ~x~
    r"(?<!~)~~(?!~)([^\s~](?:[^~\n]*?[^\s~])?)~~(?!~)"
)
_MD_LINK = re.compile(  # markdown [text](url) -> mrkdwn <url|text>
    r"(?<!!)\[([^\]\n]*)\]\(([^)\s|]+)\)"
)
# mrkdwn angle token: <content> or <content|label>.
_ANGLE_TOKEN = re.compile(r"<([^<>\n|]+)(?:\|([^<>\n]*))?>")
# mrkdwn special mentions <!here>/<@here> -> @here (Slack-side variants).
_SPECIAL_TARGETS = frozenset({"here", "channel", "everyone"})
_MD_SPECIAL_MENTION = re.compile(
    r"(?<![\w@<|])@(here|channel|everyone)(?!\w)"
)
# Raw Slack user ids look like U123ABC / W08LV1R4J2P (uppercase alnum).
_MD_USER_MENTION = re.compile(r"(?<![\w@<|])@([UW][A-Z0-9]{5,11})(?!\w)")
_MD_HEADING = re.compile(r"#{1,6}(?=\s)")

# Code protection.
_INLINE_CODE = re.compile(r"`([^`\n]+)`")
_FENCE_LINE = "```"
_PLACEHOLDER = "\x00{}\x00"
_PLACEHOLDER_RE = re.compile("\x00(\\d+)\x00")


class SlackMrkdwnTool(Tool):
    """Slack mrkdwn <-> standard Markdown converter on the pure stdlib.

    Attributes:
        max_text_chars (int): Upper bound on the ``text`` input length;
            longer inputs are rejected before any work.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "slack_mrkdwn_tool"
    description: str = (
        "Slack mrkdwn markup tool — pure Python stdlib, no network "
        "required. Convert Slack mrkdwn to standard Markdown "
        "(mode='to_markdown': *bold*->**bold**, _italic_->*italic*, "
        "~strike~->~~strike~~, <url|text>->[text](url), <@id>/<#id|name>/"
        "<!here> mentions, >>> blockquotes, code untouched), Markdown back "
        "to mrkdwn (mode='to_mrkdwn': inverse mapping incl. **bold**->"
        "*bold*, [text](url)-><url|text>, @here-><!here>), or score which "
        "dialect a text is written in (mode='detect')."
    )

    MODES: ClassVar[tuple] = ("to_markdown", "to_mrkdwn", "detect")

    max_text_chars: int = 100_000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(self, mode: str, text: Any = None) -> dict[str, Any]:
        """Run one mrkdwn conversion or detection.

        Args:
            mode (str): One of ``to_markdown`` / ``to_mrkdwn`` / ``detect``.
            text (str): The markup text to convert or analyse. Required
                for every mode; must be a non-empty string of at most
                ``max_text_chars`` characters and must not contain the
                NUL character (reserved as the internal code-placeholder
                marker).

        Returns:
            Dict[str, Any]: ``{"mode": ..., "result": ...}`` for the two
            conversion modes; for ``detect`` additionally the boolean
            ``is_mrkdwn``, both raw ``mrkdwn_score`` / ``markdown_score``
            values, a human-readable ``verdict`` and the per-signature
            ``signals`` counts.

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        clean_text = self._validate_text(text)
        if mode == "to_markdown":
            return {"mode": mode, "result": self._to_markdown(clean_text)}
        if mode == "to_mrkdwn":
            return {"mode": mode, "result": self._to_mrkdwn(clean_text)}
        return self._detect(clean_text)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"slack_mrkdwn_tool: {message}")

    @classmethod
    def _validate_text(cls, text: Any) -> str:
        """Validate the ``text`` input."""
        if text is None or isinstance(text, bool) or not isinstance(text, str):
            cls._invalid(f"text must be a non-empty string (got {text!r})")
        if not text:
            cls._invalid("text must be a non-empty string (got '')")
        if len(text) > 100_000:
            cls._invalid(
                f"text exceeds the {100_000:,}-character limit "
                f"(got {len(text):,} characters)"
            )
        if "\x00" in text:
            cls._invalid(
                "text must not contain the NUL character "
                "(reserved as an internal placeholder)"
            )
        return text

    # ------------------------------------------------------------------ #
    # Line plumbing shared by all modes
    # ------------------------------------------------------------------ #

    @staticmethod
    def _fence_mask(lines: list[str]) -> list[bool]:
        """Mark lines that belong to a fenced code block.

        A line starting with ````` toggles fence state; the opening line,
        every line until (and including) the closing fence line is masked
        so no transformation touches the code. An unterminated fence
        masks through the end of the text.
        """
        masked = [False] * len(lines)
        inside = False
        for index, line in enumerate(lines):
            if line.startswith(_FENCE_LINE):
                masked[index] = True
                inside = not inside
            elif inside:
                masked[index] = True
        return masked

    @classmethod
    def _map_inline_code(cls, line: str) -> tuple[str, list[str]]:
        """Replace inline code spans with placeholders, return the spans."""
        spans: list[str] = []

        def _stash(match: re.Match) -> str:
            spans.append(match.group(0))
            return _PLACEHOLDER.format(len(spans) - 1)

        return _INLINE_CODE.sub(_stash, line), spans

    @staticmethod
    def _restore_code(line: str, spans: list[str]) -> str:
        """Put stashed inline code spans back into the line."""

        def _unstash(match: re.Match) -> str:
            return spans[int(match.group(1))]

        return _PLACEHOLDER_RE.sub(_unstash, line)

    @classmethod
    def _apply_inline(
        cls, line: str, passes: list[Callable[[str], str]]
    ) -> str:
        """Run the given inline passes over one line, shielding code."""
        stashed, spans = cls._map_inline_code(line)
        for pass_fn in passes:
            stashed = pass_fn(stashed)
        return cls._restore_code(stashed, spans)

    # ------------------------------------------------------------------ #
    # mrkdwn -> Markdown
    # ------------------------------------------------------------------ #

    @classmethod
    def _to_markdown(cls, text: str) -> str:
        """Convert Slack mrkdwn text to standard Markdown."""
        lines = text.split("\n")
        masked = cls._fence_mask(lines)
        quote_from = None
        for index, line in enumerate(lines):
            if not masked[index] and (
                line == ">>>" or line.startswith(">>> ")
            ):
                quote_from = index
                break
        inline_passes: list[Callable[[str], str]] = [
            cls._angle_to_markdown,
            lambda s: _MRKDWN_BOLD.sub(r"**\1**", s),
            lambda s: _MRKDWN_ITALIC.sub(r"*\1*", s),
            lambda s: _MRKDWN_STRIKE.sub(r"~~\1~~", s),
        ]
        out: list[str] = []
        for index, line in enumerate(lines):
            if masked[index]:
                out.append(line)  # fenced code copied verbatim
                continue
            if quote_from is not None and index >= quote_from:
                if index == quote_from:
                    head = line[3:]
                    if head.startswith(" "):
                        head = head[1:]
                    line = head
                line = cls._apply_inline(line, inline_passes)
                out.append("> " + line if line else ">")
                continue
            out.append(cls._apply_inline(line, inline_passes))
        return "\n".join(out)

    @staticmethod
    def _angle_to_markdown(line: str) -> str:
        """Rewrite mrkdwn angle tokens to their Markdown equivalents."""

        def _convert(match: re.Match) -> str:
            content, label = match.group(1), match.group(2)
            if not label:
                label = None
            head = content[0]
            if head == "@":
                # <@U123ABC> -> @U123ABC (raw id; <@here> -> @here).
                # <@U123ABC|alice> -> @alice (label wins when present).
                return "@" + (label if label else content[1:])
            if head == "#":
                # <#C123ABC|general> -> #general; <#C123ABC> -> #C123ABC.
                return "#" + (label if label else content[1:])
            if head == "!":
                # <!here>/< !channel>/< !everyone> -> @here/@channel/@everyone.
                if content[1:] in _SPECIAL_TARGETS and label is None:
                    return "@" + content[1:]
                return match.group(0)  # <!date...>/<!subteam^...> untouched
            if label:
                # <https://example.com|text> -> [text](https://example.com)
                return f"[{label}]({content})"
            # Bare <https://...> is already a valid CommonMark autolink.
            return match.group(0)

        return _ANGLE_TOKEN.sub(_convert, line)

    # ------------------------------------------------------------------ #
    # Markdown -> mrkdwn
    # ------------------------------------------------------------------ #

    @classmethod
    def _to_mrkdwn(cls, text: str) -> str:
        """Convert standard Markdown text to Slack mrkdwn."""
        lines = text.split("\n")
        masked = cls._fence_mask(lines)
        # Single-star italic MUST run before double-star bold: after the
        # bold pass writes '*x*', the italic pattern would otherwise eat
        # the freshly created single-star bold delimiters.
        inline_passes: list[Callable[[str], str]] = [
            cls._links_to_mrkdwn,
            lambda s: _MD_ITALIC_STAR.sub(r"_\1_", s),
            lambda s: _MD_BOLD.sub(r"*\1*", s),
            lambda s: _MD_STRIKE.sub(r"~\1~", s),
            cls._mentions_to_mrkdwn,
        ]
        out = [
            line
            if masked[index]
            else cls._apply_inline(line, inline_passes)
            for index, line in enumerate(lines)
        ]
        return "\n".join(out)

    @staticmethod
    def _links_to_mrkdwn(line: str) -> str:
        """Rewrite Markdown links to mrkdwn angle links (images kept)."""

        def _convert(match: re.Match) -> str:
            label, target = match.group(1), match.group(2)
            return f"<{target}|{label}>" if label else f"<{target}>"

        return _MD_LINK.sub(_convert, line)

    @staticmethod
    def _mentions_to_mrkdwn(line: str) -> str:
        """Wrap raw Slack mentions back into mrkdwn tokens (best effort)."""
        line = _MD_SPECIAL_MENTION.sub(r"<!\1>", line)
        return _MD_USER_MENTION.sub(r"<@\1>", line)

    # ------------------------------------------------------------------ #
    # detect mode
    # ------------------------------------------------------------------ #

    @classmethod
    def _detect(cls, text: str) -> dict[str, Any]:
        """Score mrkdwn vs Markdown signatures and return a verdict."""
        lines = text.split("\n")
        masked = cls._fence_mask(lines)
        signals = {
            "single_star_emphasis": 0,
            "angle_mention_tokens": 0,
            "angle_pipe_links": 0,
            "triple_quote_blocks": 0,
            "double_star_bold": 0,
            "markdown_links": 0,
            "double_tilde_strike": 0,
            "atx_headings": 0,
        }
        for index, line in enumerate(lines):
            if masked[index]:
                continue
            if line == ">>>" or line.startswith(">>> "):
                signals["triple_quote_blocks"] += 1
            if _MD_HEADING.match(line):
                signals["atx_headings"] += 1
            stashed, _ = cls._map_inline_code(line)
            signals["single_star_emphasis"] += len(
                _MRKDWN_BOLD.findall(stashed)
            )
            signals["double_star_bold"] += len(_MD_BOLD.findall(stashed))
            signals["markdown_links"] += len(_MD_LINK.findall(stashed))
            signals["double_tilde_strike"] += len(
                _MD_STRIKE.findall(stashed)
            )
            for content, label in _ANGLE_TOKEN.findall(stashed):
                if content[0] in "@#!":
                    signals["angle_mention_tokens"] += 1
                elif label:
                    signals["angle_pipe_links"] += 1
        mrkdwn_score = (
            2 * signals["single_star_emphasis"]
            + 3 * signals["angle_mention_tokens"]
            + 3 * signals["angle_pipe_links"]
            + signals["triple_quote_blocks"]
        )
        markdown_score = (
            2 * signals["double_star_bold"]
            + 3 * signals["markdown_links"]
            + 2 * signals["double_tilde_strike"]
            + 2 * signals["atx_headings"]
        )
        if mrkdwn_score == 0 and markdown_score == 0:
            verdict = "inconclusive"
        elif mrkdwn_score > 0 and mrkdwn_score >= markdown_score:
            verdict = "mrkdwn"
        else:
            verdict = "markdown"
        return {
            "mode": "detect",
            "is_mrkdwn": verdict == "mrkdwn",
            "mrkdwn_score": mrkdwn_score,
            "markdown_score": markdown_score,
            "verdict": verdict,
            "signals": signals,
            "result": verdict,
        }
