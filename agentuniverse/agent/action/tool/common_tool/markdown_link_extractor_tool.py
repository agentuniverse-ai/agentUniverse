#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: markdown_link_extractor_tool.py

"""Markdown link extraction / auditing tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency scanner that reads
markdown SOURCE text and reports every link construct it contains.
It is deliberately distinct from the URL parsers already in the
project: it never fetches anything and never parses a URL string —
it recognizes the markdown *syntax* around URLs.

Three modes are supported:

* ``extract`` — scan markdown text and return every link found, in
  document order, each as ``{kind, text, url, title, span}`` plus the
  reference-resolution fields for reference links:

  - inline links ``[text](url "title")`` and inline images
    ``![alt](url)`` (``kind`` ``image``),
  - reference links ``[text][ref]`` (and the collapsed
    ``[text][]`` form) resolved against ``[ref]: url "title"``
    definition lines; reference labels match case-insensitively with
    collapsed whitespace, the first definition of a label wins, and
    a usage whose label has no definition is flagged
    (``resolved: false``, ``url: null``),
  - autolinks ``<https://example.com/>`` (any absolute URI scheme)
    and email autolinks ``<user@example.com>`` normalized to
    ``mailto:`` URLs,
  - optionally (``include_bare_urls``) bare ``http://`` /
    ``https://`` URLs running in plain text, with GFM-style trailing
    punctuation trimmed.

  ``span`` is ``[start, end)`` over the input text and always
  satisfies ``text[start:end] ==`` the raw markdown construct, so
  callers can highlight or replace the exact source range.

* ``audit`` — extract, then classify every link: schemes are checked
  against the ``http`` / ``https`` / ``mailto`` whitelist;
  ``javascript:`` / ``data:`` / ``vbscript:`` URLs are flagged
  ``dangerous``; fragment-only links (``#section``) are flagged
  ``anchor``; URLs without a scheme are flagged ``relative``; empty
  destinations are flagged ``empty``; unresolved reference links are
  flagged ``undefined``; any other scheme (e.g. ``ftp:``) is flagged
  ``unknown_scheme``. Duplicate URL occurrences are counted per link
  and summarized in ``duplicate_urls``.

* ``references`` — return just the reference-definition table with
  usage analysis: every ``[label]: url "title"`` line in document
  order with its span and usage count, the labels that are never
  used (``unused``) and the labels referenced without a definition
  (``undefined``).

Parsing rules (deterministic, CommonMark-inspired but documented
here): link constructs are recognized within single lines; backslash
escapes (``\\[`` / ``\\]``) suppress bracket semantics; the link text
may nest square brackets one level deep (``[outer [inner]](url)``);
link extraction never fires inside fenced code blocks (````` ``` ````
or ``~~~``, tracked line by line like the OutlineExtractor);
malformed markdown never raises — an unmatched bracket or a missing
``)`` simply means the construct is treated as literal text and is
not reported.

Input validation is strict and happens before any scanning:
a wrong ``mode``, a non-string ``text``, a non-boolean
``include_bare_urls`` or an oversized ``text`` raise a ``ValueError``,
mirroring the other common tools. The empty string is a valid
(documented) input meaning "no links".
"""

import re
from typing import Any, ClassVar

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Fenced code blocks: 0-3 leading spaces then 3+ backticks or tildes.
_FENCE_RE = re.compile(r" {0,3}(```+|~~~+)")
# Absolute-URI autolink: <scheme:rest> — no spaces/angle brackets inside.
_AUTOLINK_URI_RE = re.compile(
    r"<([A-Za-z][A-Za-z0-9+.\-]{1,31}):([^<>\x00-\x20]*)>"
)
# Email autolink (CommonMark): local-part@domain with a dotted domain.
_AUTOLINK_EMAIL_RE = re.compile(
    r"<([A-Za-z0-9._+\-]+@[A-Za-z0-9\-]+(?:\.[A-Za-z0-9\-]+)+)>"
)
# Bare http(s) URL, GFM-style: must start at a word boundary-ish edge.
_BARE_URL_RE = re.compile(r"(?:(?<=[\s\"'(\[<{>])|\A)(https?://[^\s<>]+)")
# Scheme prefix of a destination URL.
_SCHEME_RE = re.compile(r"\A([A-Za-z][A-Za-z0-9+.\-]*):")
# Characters GFM strips off the end of an autolinked bare URL.
_TRAILING_PUNCT = ".,;:!?"


class MarkdownLinkExtractorTool(Tool):
    """Extract and audit links from markdown source text (pure stdlib).

    Attributes:
        max_text_chars (int): Upper bound on the ``text`` input length;
            longer inputs are rejected before any scanning.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "markdown_link_extractor_tool"
    description: str = (
        "Markdown link extractor tool — pure Python stdlib, no network "
        "required. Scans markdown SOURCE text for link constructs: "
        "inline links/images [text](url \"title\"), reference links "
        "[text][ref] resolved against [ref]: url definitions "
        "(case-insensitive labels, undefined references flagged), "
        "autolinks <https://...> and optional bare URLs. mode='extract' "
        "returns every link with kind, text, url, title and an exact "
        "[start, end) source span; mode='audit' additionally classifies "
        "each link (ok/anchor/relative/empty/undefined/dangerous/"
        "unknown_scheme, with http/https/mailto whitelisted and "
        "javascript:/data:/vbscript: dangerous) and counts duplicate "
        "URLs; mode='references' returns the reference-definition table "
        "with unused/undefined analysis. Links inside fenced code "
        "blocks are never extracted."
    )

    MODES: ClassVar[tuple] = ("extract", "audit", "references")
    KINDS: ClassVar[tuple] = ("inline", "reference", "autolink", "image", "bare")
    VERDICTS: ClassVar[tuple] = (
        "ok",
        "anchor",
        "relative",
        "empty",
        "undefined",
        "dangerous",
        "unknown_scheme",
    )
    # Audit classification sets.
    SAFE_SCHEMES: ClassVar[tuple] = ("http", "https", "mailto")
    DANGEROUS_SCHEMES: ClassVar[tuple] = ("javascript", "data", "vbscript")

    max_text_chars: int = 100_000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any = None,
        text: Any = None,
        include_bare_urls: Any = None,
    ) -> dict[str, Any]:
        """Run one extraction / audit / reference-table pass.

        Args:
            mode (str): One of ``extract`` / ``audit`` / ``references``.
            text (str): The markdown source text to scan. The empty
                string is valid and yields an empty result.
            include_bare_urls (bool): Also report bare ``http(s)://``
                URLs found in plain text (outside any link construct).
                Defaults to ``False``. Applies to the ``extract`` and
                ``audit`` modes.

        Returns:
            Dict[str, Any]: For ``extract`` / ``audit`` a ``links``
            list (document order, each with ``kind``, ``text``, ``url``,
            ``title``, ``span`` and mode-specific extras) plus a
            ``summary``; for ``references`` the ``definitions`` table
            with ``unused`` / ``undefined`` analysis and a ``summary``.

        Raises:
            ValueError: If any parameter is malformed (before any
                scanning happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        clean_text = self._validate_text(text)
        bare = self._validate_bare_flag(include_bare_urls)

        definitions, links = self._scan(clean_text, include_bare_urls=bare)

        if mode == "references":
            return self._references_result(definitions, links)
        if mode == "audit":
            return self._audit_result(links)
        return self._extract_result(links)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any scanning)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"markdown_link_extractor_tool: {message}")

    def _validate_text(self, text: Any) -> str:
        """Validate the ``text`` input (empty string is allowed)."""
        if text is None or isinstance(text, bool) or not isinstance(text, str):
            self._invalid(f"text must be a string (got {text!r})")
        if len(text) > self.max_text_chars:
            self._invalid(
                f"text exceeds the {self.max_text_chars:,}-character limit "
                f"(got {len(text):,} characters)"
            )
        return text

    @classmethod
    def _validate_bare_flag(cls, include_bare_urls: Any) -> bool:
        """Validate the ``include_bare_urls`` switch."""
        if include_bare_urls is None:
            return False
        if isinstance(include_bare_urls, bool):
            return include_bare_urls
        cls._invalid(
            "include_bare_urls must be a boolean or None "
            f"(got {include_bare_urls!r})"
        )

    # ------------------------------------------------------------------ #
    # Scanning (single pass over lines: fences, definitions, constructs)
    # ------------------------------------------------------------------ #

    def _scan(
        self, text: str, include_bare_urls: bool
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """Walk the text line by line.

        Returns ``(definitions, links)`` in document order. Reference
        usages are resolved here against the first definition of each
        label (CommonMark first-wins rule).
        """
        definitions: list[dict[str, Any]] = []
        seen_labels: dict[str, dict[str, Any]] = {}
        links: list[dict[str, Any]] = []
        in_fence = False
        fence_marker = ""

        for line_start, line in _iter_lines(text):
            fence = _FENCE_RE.match(line)
            if fence:
                marker = fence.group(1)
                if not in_fence:
                    in_fence = True
                    fence_marker = marker
                elif marker[0] == fence_marker[0] and len(marker) >= len(
                    fence_marker
                ):
                    in_fence = False
                continue
            if in_fence:
                continue

            definition = self._parse_definition(line, line_start)
            if definition is not None:
                if definition["label"] not in seen_labels:
                    seen_labels[definition["label"]] = definition
                    definitions.append(definition)
                continue

            links.extend(
                self._scan_content_line(line, line_start, include_bare_urls)
            )

        self._resolve(links, seen_labels)
        return definitions, links

    def _scan_content_line(
        self, line: str, base: int, include_bare_urls: bool
    ) -> list[dict[str, Any]]:
        """Scan one ordinary content line for link constructs."""
        found: list[dict[str, Any]] = []
        n = len(line)
        i = 0
        while i < n:
            char = line[i]
            if char == "\\":
                i += 2  # skip the escaped character entirely
                continue
            if char == "<":
                link = self._parse_autolink(line, i, base)
                if link is not None:
                    found.append(link)
                    i = link["span"][1] - base
                    continue
                i += 1
                continue
            if char in "![":
                is_image = char == "!"
                open_idx = i + 1 if is_image else i
                if is_image and (open_idx >= n or line[open_idx] != "["):
                    i += 1
                    continue
                link = self._parse_bracket_link(
                    line, open_idx, base, is_image=is_image
                )
                if link is not None:
                    if is_image:
                        # The span of an image covers its '!' too.
                        link["span"][0] = base + i
                    found.append(link)
                    i = link["span"][1] - base
                    continue
                i += 1
                continue
            i += 1

        if not include_bare_urls:
            return found
        bare = self._scan_bare_urls(line, base, found)
        return sorted(found + bare, key=lambda link: link["span"][0])

    # ------------------------------------------------------------------ #
    # Individual construct parsers (return None when nothing matches)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _parse_autolink(line: str, start: int, base: int) -> dict[str, Any] | None:
        """Parse ``<scheme:rest>`` / ``<user@example.com>`` from *start*."""
        uri = _AUTOLINK_URI_RE.match(line, start)
        if uri is not None:
            destination = uri.group(0)[1:-1]
            return {
                "kind": "autolink",
                "text": destination,
                "url": destination,
                "title": None,
                "span": [base + start, base + uri.end()],
            }
        email = _AUTOLINK_EMAIL_RE.match(line, start)
        if email is not None:
            address = email.group(1)
            return {
                "kind": "autolink",
                "text": address,
                "url": f"mailto:{address}",
                "title": None,
                "span": [base + start, base + email.end()],
            }
        return None

    def _parse_bracket_link(
        self, line: str, open_idx: int, base: int, is_image: bool = False
    ) -> dict[str, Any] | None:
        """Parse ``[text](dest)`` / ``[text][ref]`` starting at *open_idx*.

        The opening ``[`` (or the ``[`` of ``![``) is at ``open_idx``.
        Returns ``None`` when the construct does not close.
        """
        n = len(line)
        text_start = open_idx + 1
        depth = 1
        j = text_start
        while j < n:
            char = line[j]
            if char == "\\":
                j += 2
                continue
            if char == "[":
                # Link text may nest square brackets one level only.
                if depth >= 2:
                    return None
                depth += 1
            elif char == "]":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        if j >= n:
            return None
        inner = line[text_start:j]
        kind = "image" if is_image else "inline"

        if j + 1 < n and line[j + 1] == "(":
            destination, title, cursor = self._parse_destination_and_title(
                line, j + 2
            )
            if destination is None:
                return None
            if cursor >= n or line[cursor] != ")":
                return None
            return {
                "kind": kind,
                "text": inner,
                "url": destination,
                "title": title,
                "span": [base + open_idx, base + cursor + 1],
            }

        if j + 1 < n and line[j + 1] == "[":
            # Full reference [text][ref] or collapsed [text][].
            k = j + 2
            while k < n and line[k] != "]":
                if line[k] == "[":
                    return None
                if line[k] == "\\":
                    k += 1
                k += 1
            if k >= n:
                return None
            label = line[j + 2 : k]
            if label == "":
                label = inner  # collapsed form [text][]
            return {
                "kind": "reference" if kind == "inline" else "image",
                "text": inner,
                "url": None,
                "title": None,
                "ref": label,
                "span": [base + open_idx, base + k + 1],
            }

        return None  # shortcut references are out of scope

    @staticmethod
    def _parse_destination_and_title(
        line: str, start: int
    ) -> tuple[str | None, str | None, int]:
        """Parse a destination plus optional quoted title from *start*.

        Used both for inline targets (``[t](dest "title")``) and
        reference definitions (``[l]: dest "title"``); the caller is
        responsible for validating what follows the returned cursor
        (a ``)`` for inline targets, end-of-line for definitions).
        """
        n = len(line)
        i = start
        while i < n and line[i] in " \t":
            i += 1
        if i >= n:
            return None, None, 0

        if line[i] == "<":
            close = line.find(">", i + 1)
            if close == -1:
                return None, None, 0
            destination = line[i + 1 : close]
            i = close + 1
        else:
            dest_start = i
            paren_depth = 0
            while i < n:
                char = line[i]
                if char in " \t":
                    break
                if char == "(":
                    paren_depth += 1
                elif char == ")":
                    if paren_depth == 0:
                        break
                    paren_depth -= 1
                i += 1
            destination = line[dest_start:i]

        title = None
        while i < n and line[i] in " \t":
            i += 1
        if i < n and line[i] in "\"'(":
            quote = line[i]
            if quote == "(":
                # Paren titles may nest balanced parentheses.
                depth = 1
                close = i + 1
                while close < n and depth > 0:
                    if line[close] == "(":
                        depth += 1
                    elif line[close] == ")":
                        depth -= 1
                    close += 1
                if depth > 0:
                    return None, None, 0
                title = line[i + 1 : close - 1]
                i = close
            else:
                close = line.find(quote, i + 1)
                if close == -1:
                    return None, None, 0
                title = line[i + 1 : close]
                i = close + 1
            while i < n and line[i] in " \t":
                i += 1
        return destination, title, i

    def _parse_definition(self, line: str, base: int) -> dict[str, Any] | None:
        """Parse a ``[label]: destination "title"`` line, if it is one."""
        stripped = line.lstrip(" ")
        indent = len(line) - len(stripped)
        if indent > 3 or not stripped.startswith("["):
            return None
        n = len(stripped)
        label_start = 1
        j = label_start
        while j < n:
            char = stripped[j]
            if char == "\\":
                j += 2
                continue
            if char == "[":
                return None
            if char == "]":
                break
            j += 1
        if j >= n or j == label_start or stripped[j + 1 : j + 2] != ":":
            return None
        raw_label = stripped[label_start:j]

        destination, title, cursor = self._parse_destination_and_title(
            stripped, j + 2
        )
        if destination is None:
            return None
        if stripped[cursor:].strip(" \t\r"):
            return None  # trailing garbage — not a definition
        return {
            "label": _normalize_label(raw_label),
            "raw_label": raw_label,
            "url": destination,
            "title": title,
            "span": [base + indent, base + indent + len(stripped.rstrip(" \t\r"))],
            "used_count": 0,
        }

    @staticmethod
    def _scan_bare_urls(
        line: str, base: int, found: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Find bare http(s) URLs in the segments no construct covers."""
        covered = sorted(
            (link["span"][0] - base, link["span"][1] - base) for link in found
        )
        bare: list[dict[str, Any]] = []
        for match in _BARE_URL_RE.finditer(line):
            start, end = match.span(1)
            if any(c_start <= start < c_end for c_start, c_end in covered):
                continue  # inside a recognized construct
            if any(start <= c_start < end for c_start, c_end in covered):
                continue  # runs into a construct — ambiguous, skip
            url = _trim_bare_url(match.group(1))
            if not url:
                continue
            bare.append(
                {
                    "kind": "bare",
                    "text": url,
                    "url": url,
                    "title": None,
                    "span": [base + start, base + start + len(url)],
                }
            )
        return bare

    # ------------------------------------------------------------------ #
    # Reference resolution
    # ------------------------------------------------------------------ #

    @staticmethod
    def _resolve(
        links: list[dict[str, Any]], definitions: dict[str, dict[str, Any]]
    ) -> None:
        """Resolve reference usages against the (first-wins) definitions."""
        for link in links:
            if "ref" not in link:
                continue
            definition = definitions.get(_normalize_label(link["ref"]))
            if definition is None:
                link["resolved"] = False
            else:
                link["resolved"] = True
                link["url"] = definition["url"]
                link["title"] = definition["title"]
                definition["used_count"] += 1

    # ------------------------------------------------------------------ #
    # Mode result builders
    # ------------------------------------------------------------------ #

    def _extract_result(self, links: list[dict[str, Any]]) -> dict[str, Any]:
        """Build the mode='extract' payload."""
        by_kind = {kind: 0 for kind in self.KINDS}
        undefined = 0
        for link in links:
            by_kind[link["kind"]] += 1
            if link.get("resolved") is False:
                undefined += 1
        return {
            "mode": "extract",
            "links": links,
            "summary": {
                "total": len(links),
                "by_kind": by_kind,
                "undefined_references": undefined,
            },
        }

    def _audit_result(self, links: list[dict[str, Any]]) -> dict[str, Any]:
        """Build the mode='audit' payload with per-link verdicts."""
        url_counts: dict[str, int] = {}
        for link in links:
            if link["url"]:
                url_counts[link["url"]] = url_counts.get(link["url"], 0) + 1

        by_verdict = {verdict: 0 for verdict in self.VERDICTS}
        audited: list[dict[str, Any]] = []
        for link in links:
            verdict, scheme = self._classify(link)
            duplicate_count = url_counts.get(link["url"]) or None
            issues = []
            if verdict == "dangerous":
                issues.append("dangerous_scheme")
            if (duplicate_count or 0) > 1:
                issues.append("duplicate")
            audited.append(
                {
                    **link,
                    "verdict": verdict,
                    "scheme": scheme,
                    "duplicate_count": duplicate_count,
                    "issues": issues,
                }
            )
            by_verdict[verdict] += 1

        duplicate_urls = {
            url: count for url, count in url_counts.items() if count > 1
        }
        return {
            "mode": "audit",
            "links": audited,
            "summary": {
                "total": len(audited),
                "by_verdict": by_verdict,
                "unique_urls": len(url_counts),
                "duplicate_urls": duplicate_urls,
            },
        }

    def _classify(self, link: dict[str, Any]) -> tuple[str, str | None]:
        """Return ``(verdict, scheme)`` for one link."""
        if link.get("resolved") is False:
            return "undefined", None
        url = link["url"] or ""
        if url == "":
            return "empty", None
        scheme_match = _SCHEME_RE.match(url)
        scheme = scheme_match.group(1).lower() if scheme_match else None
        if scheme is not None and scheme in self.DANGEROUS_SCHEMES:
            return "dangerous", scheme
        if url.startswith("#"):
            return "anchor", scheme
        if scheme is None:
            return "relative", None
        if scheme in self.SAFE_SCHEMES:
            return "ok", scheme
        return "unknown_scheme", scheme

    def _references_result(
        self, definitions: list[dict[str, Any]], links: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Build the mode='references' payload."""
        undefined = [
            {"ref": link["ref"], "span": link["span"]}
            for link in links
            if link.get("resolved") is False
        ]
        unused = [d["label"] for d in definitions if d["used_count"] == 0]
        table = [
            {
                "label": d["label"],
                "url": d["url"],
                "title": d["title"],
                "span": d["span"],
                "used_count": d["used_count"],
            }
            for d in definitions
        ]
        return {
            "mode": "references",
            "definitions": table,
            "unused": unused,
            "undefined": undefined,
            "summary": {
                "definitions": len(table),
                "unused": len(unused),
                "undefined": len(undefined),
            },
        }


# ---------------------------------------------------------------------- #
# Module-level helpers
# ---------------------------------------------------------------------- #


def _iter_lines(text: str):
    """Yield ``(start_offset, line)`` for every line, no newline chars."""
    offset = 0
    for line in text.split("\n"):
        yield offset, line
        offset += len(line) + 1


def _normalize_label(label: str) -> str:
    """Normalize a reference label: trim, collapse spaces, case-fold."""
    return re.sub(r"\s+", " ", label.strip()).casefold()


def _trim_bare_url(url: str) -> str:
    """Trim GFM trailing punctuation off a bare URL candidate."""
    trimmed = url.rstrip(_TRAILING_PUNCT)
    trimmed = trimmed.rstrip("'\"")
    while trimmed.endswith(")") and trimmed.count("(") < trimmed.count(")"):
        trimmed = trimmed[:-1]
    return trimmed
