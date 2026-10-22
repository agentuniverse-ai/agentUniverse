#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Static HTML fragment safety analysis tool (stdlib-only tokenizer)."""

import re
from bisect import bisect_right
from collections import Counter
from html import unescape
from html.parser import HTMLParser
from typing import Any, ClassVar

from agentuniverse.agent.action.tool.tool import Tool


class _CapViolation(Exception):
    """Raised internally when an input exceeds a configured safety cap."""


_EVENT_ATTR_RE = re.compile(r"^on[a-z]+")
_TAG_NAME_RE = re.compile(r"^[a-z][a-z0-9-]*$")
_SCHEME_RE = re.compile(r"^([a-z][a-z0-9+.\-]*):")
_CONTROL_RE = re.compile("[\x00-\x1f\x7f`]")
_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
_HTML_COMMENT_OPEN_RE = re.compile(r"<!--.*$", re.S)
_CSS_COMMENT_RE = re.compile(r"/\*.*?\*/", re.S)
_CSS_HEX_ESCAPE_RE = re.compile(r"\\([0-9a-fA-F]{1,6})[ \t\n\r\f]?")
_CSS_CHAR_ESCAPE_RE = re.compile(r"\\(.)", re.S)
_IE_CONDITIONAL_RE = re.compile(r"\[\s*if\b|\[\s*endif", re.I)
_RAW_TAG_RE = re.compile(r"<([a-zA-Z][a-zA-Z0-9-]*)")
_STYLE_SCHEME_RE = re.compile(r"(?:javascript|vbscript|livescript|mocha|jscript)\s*:")
_STYLE_EXPRESSION_RE = re.compile(r"expression\s*\(")
# Legacy script-executing CSS binding constructs (old Firefox -moz-binding,
# IE behavior). Same historical class as expression().
_STYLE_BINDING_RE = re.compile(r"(?:-moz-binding|behavior)\s*:")
_EMBEDDED_TAG_RE = re.compile(r"<(?:script|iframe|object|embed|svg|math|base|form)\b", re.I)
_EMBEDDED_HANDLER_RE = re.compile(r"\son[a-z]+\s*=", re.I)
_SWALLOWED_HANDLER_RE = re.compile(r"(?i)^on[a-z]+\s*=")
_DATA_MIME_RE = re.compile(r"data:\s*([^;,]*)")
_URL_IN_REFRESH_RE = re.compile(r"(?i)url\s*=\s*(.*)$")
_CHARSET_RE = re.compile(r"(?i)charset\s*=\s*([\w.\-]+)")
_SCRIPT_CLOSE_RE = re.compile(r"</script\s*>", re.I)
_STYLE_CLOSE_RE = re.compile(r"</style\s*>", re.I)

# Elements html.parser treats as raw text (CDATA content elements).
_RAW_TEXT_ELEMENTS = frozenset({"script", "style"})

# Void elements: never pushed on the nesting stack.
_VOID_ELEMENTS = frozenset({
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
})

# Dangerous elements with per-tag reasoning. Severity maps the realistic
# execution or hijack impact of each element in an HTML fragment context.
_DANGEROUS_TAGS: ClassVar[dict[str, tuple[str, str]]] = {
    "script": ("high", "script element executes embedded or referenced JavaScript"),
    "iframe": ("high", "iframe embeds a nested browsing context whose src/srcdoc can execute script"),
    "object": ("high", "object loads plugin or external content that can execute code"),
    "embed": ("high", "embed loads plugin or external content that can execute code"),
    "base": ("high", "base rewrites resolution of every relative URL in the document"),
    "svg": ("high", "svg hosts script execution via script, onload or animate handlers"),
    "math": ("medium", "math markup is a historical mutation-XSS vector in sanitizers"),
    "form": ("medium", "form enables UI redress and credential capture against attacker actions"),
    "input": ("medium", "input supports hidden fields and autofocus-driven UI tricks"),
    "link": ("medium", "link fetches external resources and historically executed HTML imports"),
    "meta": ("medium", "meta refresh redirects navigation and meta charset enables charset confusion"),
}

# URL-bearing attributes probed for dangerous schemes.
_URL_ATTRS = frozenset({
    "href", "src", "action", "formaction", "data", "poster", "background",
    "cite", "longdesc", "usemap", "dynsrc", "lowsrc", "xlink:href",
    "profile", "manifest", "codebase", "classid", "archive", "folder",
})

# Attributes on <param> elements whose value is a URL.
_PARAM_URL_ATTRS = frozenset({"url", "src", "href", "data", "movie", "value"})

# SVG animation elements that can retarget href/xlink:href at runtime.
_ANIMATION_ELEMENTS = frozenset({"animate", "set", "animatetransform", "animatemotion", "animatecolor"})

# href-like attribute names an <animate>/<set> attributeName may target.
_HREF_ATTR_NAMES = frozenset({"href", "xlink:href"})

# Value-bearing attributes of animation elements probed for dangerous URLs.
_ANIMATION_VALUE_ATTRS = ("from", "to", "by", "values")

# Maximum number of tokenizer-dropped tag occurrences reported per tag name
# by the raw-source cross-check; more occurrences only inflate output.
_RAW_EXTRA_REPORT_CAP = 50

# Maximum nesting of abrupt-comment / srcdoc re-audit passes.
_NESTED_AUDIT_DEPTH = 2

_DANGEROUS_SCHEMES = frozenset({
    "javascript", "vbscript", "livescript", "mocha", "jscript",
})

# data: URI media types that execute script when navigated to or embedded.
_ACTIVE_DATA_MIMES = frozenset({
    "text/html", "image/svg+xml", "application/xhtml+xml", "text/xml",
    "application/xml", "application/xslt+xml", "text/javascript",
    "application/javascript", "text/ecmascript", "application/ecmascript",
})

_UTF8_CHARSETS = frozenset({"utf-8", "utf8"})


def _css_unescape(text: str) -> str:
    """Decode CSS escape sequences (hex and single-character forms)."""

    def hex_repl(match):
        code = int(match.group(1), 16)
        if 0 < code <= 0x10FFFF:
            return chr(code)
        return match.group(0)

    text = _CSS_HEX_ESCAPE_RE.sub(hex_repl, text)
    return _CSS_CHAR_ESCAPE_RE.sub(r"\1", text)


def _probe(value: str) -> str:
    """Return the normalized form of an attribute value used for detection.

    The value arrives once entity-decoded from the tokenizer. This helper
    attempts a second decode round (double-encoding defense), removes HTML
    and CSS comment constructs, decodes CSS escapes, strips control
    characters and backticks (browser scheme obfuscation), trims edges,
    and lowercases. It is a detection aid only; the finding evidence
    always shows the raw slice.
    """
    text = unescape(value or "")
    for _ in range(3):
        cleaned = text
        # The comment regexes are only applied when their closing delimiter
        # is present; on delimiter-free input they cannot match, and the
        # backtracking scan would be quadratic in the value length.
        if "<!--" in cleaned and "-->" in cleaned:
            cleaned = _HTML_COMMENT_RE.sub("", cleaned)
        if "<!--" in cleaned:
            cleaned = _HTML_COMMENT_OPEN_RE.sub("", cleaned)
        if "/*" in cleaned and "*/" in cleaned:
            cleaned = _CSS_COMMENT_RE.sub("", cleaned)
        cleaned = _css_unescape(cleaned)
        if cleaned == text:
            break
        text = cleaned
    text = _CONTROL_RE.sub("", text)
    return text.strip().lower()


def _scheme_of(probed: str) -> str | None:
    match = _SCHEME_RE.match(probed)
    return match.group(1) if match else None


def _classify_url(value: str) -> tuple[str, str] | None:
    """Classify a URL value as ``(code, detail)`` or ``None`` when safe."""
    probed = _probe(value)
    scheme = _scheme_of(probed)
    if scheme is None:
        return None
    if scheme in _DANGEROUS_SCHEMES:
        return ("DANGEROUS_URL_SCHEME", f"{scheme}: URL scheme executes script")
    if scheme == "data":
        rest = probed[len("data:"):].split(",", 1)[0]
        mime = rest.split(";")[0].strip()
        if mime in _ACTIVE_DATA_MIMES:
            return ("DANGEROUS_URL_SCHEME", f"data: URI with active mime {mime}")
        return ("DATA_URI", f"data: URI with mime {mime or 'empty'}")
    return None


def _inline_danger(probed: str) -> str | None:
    """Detect a dangerous scheme anywhere in a probed blob (unanchored)."""
    match = _STYLE_SCHEME_RE.search(probed)
    if match:
        return match.group(0).split(":")[0]
    mime = _DATA_MIME_RE.search(probed)
    if mime and mime.group(1).strip() in _ACTIVE_DATA_MIMES:
        return f"data:{mime.group(1).strip()}"
    return None


def _truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + "..."


def _sorted_counter(counter: Counter) -> dict[str, int]:
    return dict(sorted(counter.items(), key=lambda item: (-item[1], item[0])))


class _FragmentTokenizer(HTMLParser):
    """Byte-accurate event tokenizer for an HTML fragment.

    Events carry exact ``(line, col)`` positions from ``getpos()`` and are
    collected once per document; every analysis mode walks the same event
    stream, so all modes agree on the parse. Attribute lists keep first
    occurrence per name (DOM semantics, mirroring lxml) while the raw
    attribute sequence stays available on the event.
    """

    def __init__(self, source: str, max_tags: int, max_depth: int) -> None:
        super().__init__(convert_charrefs=False)
        self._source = source
        line_starts = [0]
        for index, char in enumerate(source):
            if char == "\n":
                line_starts.append(index + 1)
        self._line_starts = line_starts
        self._max_tags = max_tags
        self._max_depth = max_depth
        self.events: list[dict[str, Any]] = []
        self.stack: list[str] = []
        self.max_depth_seen = 0
        self.tag_count = 0

    # -- helpers -------------------------------------------------------
    def _offset(self) -> int:
        line, col = self.getpos()
        return self._line_starts[line - 1] + col

    def offset_at(self, line: int, col: int) -> int:
        """Map an event's (line, col) back to a source offset."""
        return self._line_starts[line - 1] + col

    def _decode_entity(self, prefix: str, name: str) -> str:
        """Decode an entity using its exact source form (semicolon-aware)."""
        offset = self._offset()
        end = offset + len(prefix) + len(name)
        if end < len(self._source) and self._source[end] == ";":
            end += 1
        return unescape(self._source[offset:end])

    # -- tag handlers --------------------------------------------------
    def handle_starttag(self, tag, attrs):
        self._record_start(tag, attrs, self_closing=False)

    def handle_startendtag(self, tag, attrs):
        self._record_start(tag, attrs, self_closing=True)

    def _record_start(self, tag, attrs, self_closing):
        self.tag_count += 1
        if self.tag_count > self._max_tags:
            raise _CapViolation(f"fragment exceeds max_tags={self._max_tags}")
        deduped: list[tuple[str, str | None]] = []
        seen = set()
        for name, value in attrs:
            if name in seen:
                continue
            seen.add(name)
            deduped.append((name, value))
        if not self_closing and tag not in _VOID_ELEMENTS:
            self.stack.append(tag)
            if len(self.stack) > self._max_depth:
                raise _CapViolation(f"fragment exceeds max_depth={self._max_depth}")
            if len(self.stack) > self.max_depth_seen:
                self.max_depth_seen = len(self.stack)
        elif self_closing:
            self.max_depth_seen = max(self.max_depth_seen, len(self.stack) + 1)
        self.events.append({
            "kind": "start",
            "tag": tag,
            "attrs": deduped,
            "raw_attrs": list(attrs),
            "line": self.getpos()[0],
            "col": self.getpos()[1],
            "raw": self.get_starttag_text() or "",
            "self_closing": self_closing,
            "depth": len(self.stack),
        })

    def handle_endtag(self, tag):
        if tag in self.stack:
            while self.stack:
                popped = self.stack.pop()
                if popped == tag:
                    break
        self.events.append({
            "kind": "end", "tag": tag,
            "line": self.getpos()[0], "col": self.getpos()[1],
        })

    # -- text and entity handlers ----------------------------------------
    def handle_data(self, data):
        raw_parent = self.stack[-1] if self.stack and self.stack[-1] in _RAW_TEXT_ELEMENTS else None
        self.events.append({
            "kind": "data", "text": data, "raw_parent": raw_parent,
            "offset": self._offset(),
            "line": self.getpos()[0], "col": self.getpos()[1],
        })

    def handle_entityref(self, name):
        self.events.append({
            "kind": "entityref", "name": name, "decoded": self._decode_entity("&", name),
            "raw": f"&{name};",
            "line": self.getpos()[0], "col": self.getpos()[1],
        })

    def handle_charref(self, name):
        self.events.append({
            "kind": "charref", "name": name, "decoded": self._decode_entity("&#", name),
            "raw": f"&#{name};",
            "line": self.getpos()[0], "col": self.getpos()[1],
        })

    def handle_comment(self, data):
        offset = self._offset()
        # HTML5 closes "<!-->" and "<!--->" as empty comments immediately.
        # html.parser instead scans for the next "--!?>" and swallows the
        # intervening markup into the comment; flag that here so audit mode
        # can re-parse the hidden region as the live markup browsers see.
        abrupt = self._source.startswith("<!-->", offset) or self._source.startswith("<!--->", offset)
        self.events.append({
            "kind": "comment", "text": data, "abrupt": abrupt, "offset": offset,
            "line": self.getpos()[0], "col": self.getpos()[1],
        })

    def handle_decl(self, decl):
        self.events.append({
            "kind": "decl", "text": decl,
            "line": self.getpos()[0], "col": self.getpos()[1],
        })

    def handle_pi(self, data):
        self.events.append({
            "kind": "pi", "text": data,
            "line": self.getpos()[0], "col": self.getpos()[1],
        })

    def unknown_decl(self, data):
        self.events.append({
            "kind": "unknown_decl", "text": data,
            "line": self.getpos()[0], "col": self.getpos()[1],
        })


def _tokenize(html: str, max_tags: int, max_depth: int) -> _FragmentTokenizer:
    tokenizer = _FragmentTokenizer(html, max_tags, max_depth)
    tokenizer.feed(html)
    tokenizer.close()
    return tokenizer


def _blank_raw_text_spans(source: str, word: str, close_re: re.Pattern) -> str:
    """Blank ``<word ...>`` ... ``</word>`` (or EOF) spans, offsets preserved.

    Linear-time equivalent of ``<word\\b[^>]*>.*?(?:</word\\s*>|\\Z)``: the
    regex form backtracks quadratically when many ``<word`` starts never see
    a ``>``. Semantics are identical: the open tag ends at the first ``>``
    after the tag word (``[^>]*`` cannot cross one) and the span runs to the
    first close tag or end of input.
    """
    open_needle = "<" + word
    low = source.lower()
    word_end = 1 + len(word)
    out: list[str] = []
    i = 0
    n = len(source)
    while True:
        start = low.find(open_needle, i)
        if start < 0:
            out.append(source[i:])
            return "".join(out)
        # \b after the tag word: the next character must not be a word char.
        following = source[start + word_end:start + word_end + 1]
        if following and (following.isalnum() or following == "_"):
            out.append(source[i:start + 1])
            i = start + 1
            continue
        gt = source.find(">", start + word_end)
        if gt < 0:
            # No ">" anywhere ahead: no open tag can complete, so the regex
            # would leave the remainder untouched.
            out.append(source[i:])
            return "".join(out)
        match = close_re.search(source, gt + 1)
        end = match.end() if match else n
        out.append(source[i:start])
        out.append(" " * (end - start))
        i = end


def _blank_comment_spans(source: str) -> str:
    """Blank ``<!-- ... -->`` spans, offsets preserved (linear time)."""
    out: list[str] = []
    i = 0
    while True:
        start = source.find("<!--", i)
        if start < 0:
            out.append(source[i:])
            return "".join(out)
        close = source.find("-->", start + 4)
        if close < 0:
            # No "-->" anywhere ahead: no comment span can match, so the
            # regex would leave the remainder untouched.
            out.append(source[i:])
            return "".join(out)
        end = close + 3
        out.append(source[i:start])
        out.append(" " * (end - start))
        i = end


def _mask_raw_spans(source: str) -> str:
    """Blank out script/style/comment spans, preserving offsets."""
    masked = _blank_raw_text_spans(source, "script", _SCRIPT_CLOSE_RE)
    masked = _blank_raw_text_spans(masked, "style", _STYLE_CLOSE_RE)
    masked = _blank_comment_spans(masked)
    return masked


def _line_starts_of(source: str) -> list[int]:
    starts = [0]
    starts.extend(i + 1 for i, char in enumerate(source) if char == "\n")
    return starts


def _line_col_at(starts: list[int], offset: int) -> tuple[int, int]:
    index = bisect_right(starts, offset) - 1
    return index + 1, offset - starts[index]


class HtmlAuditTool(Tool):
    """Audit HTML fragments for dangerous constructs without executing them.

    The tool is a static analyzer: it never renders, fetches, or mutates the
    fragment. Four modes are supported: ``audit`` (dangerous-construct
    findings with exact line numbers), ``allowlist_diff`` (used tags vs an
    allowed set, report only), ``text`` (visible text with script/style
    content dropped), and ``stats`` (tag/attr histograms, depth, form, link
    and entity census). Parsing is stdlib-only (``html.parser`` +
    ``html.unescape``).
    """

    MODES: ClassVar[frozenset[str]] = frozenset({"audit", "allowlist_diff", "text", "stats"})

    max_input_chars: int = 1_000_000
    max_tags: int = 20_000
    max_depth: int = 400
    max_findings: int = 500
    max_evidence_chars: int = 120
    max_text_chars: int = 200_000

    def execute(
        self,
        html: str,
        mode: str,
        allowed_tags: list[str] | set[str] | tuple[str, ...] | None = None,
    ) -> dict[str, Any]:
        try:
            self._validate_config()
            normalized_mode = self._validate_mode(mode)
            source = self._validate_html(html)
            tokenizer = _tokenize(source, self.max_tags, self.max_depth)
            if normalized_mode == "allowlist_diff":
                allowed = self._validate_allowed_tags(allowed_tags)
                return self._allowlist_diff(source, tokenizer, allowed)
            if normalized_mode == "text":
                return self._text_mode(source, tokenizer)
            if normalized_mode == "stats":
                return self._stats_mode(source, tokenizer)
            return self._audit_mode(source, tokenizer)
        except _CapViolation as exc:
            return {"status": "error", "error_type": "input_too_large", "error": str(exc)}
        except ValueError as exc:
            return {"status": "error", "error_type": "validation_error", "error": str(exc)}

    # -- validation ----------------------------------------------------
    def _validate_config(self) -> None:
        for name in ("max_input_chars", "max_tags", "max_depth", "max_findings",
                     "max_evidence_chars", "max_text_chars"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")

    @staticmethod
    def _validate_mode(mode: str) -> str:
        if not isinstance(mode, str):
            raise ValueError("mode must be a string")
        normalized = mode.strip().lower()
        if normalized not in HtmlAuditTool.MODES:
            allowed = ", ".join(sorted(HtmlAuditTool.MODES))
            raise ValueError(f"mode must be one of: {allowed}")
        return normalized

    def _validate_html(self, html: str) -> str:
        if not isinstance(html, str):
            raise ValueError("html must be a string")
        if len(html) > self.max_input_chars:
            raise ValueError(f"html exceeds max_input_chars={self.max_input_chars}")
        if not html.strip():
            raise ValueError("html must be a non-empty fragment")
        return html

    @staticmethod
    def _validate_allowed_tags(allowed_tags) -> list[str]:
        if isinstance(allowed_tags, str) or not isinstance(allowed_tags, (list, set, tuple)):
            raise ValueError("allowed_tags must be a list, set, or tuple of tag names")
        normalized = []
        for item in allowed_tags:
            if not isinstance(item, str):
                raise ValueError("allowed_tags entries must be strings")
            tag = item.strip().lower()
            if not _TAG_NAME_RE.match(tag):
                # Truncate the echoed entry: values can be arbitrarily long
                # and the error must not become an unbounded echo.
                raise ValueError(
                    f"invalid allowed_tags entry: {_truncate(repr(item), 60)}")
            if tag not in normalized:
                normalized.append(tag)
        if not normalized:
            raise ValueError("allowed_tags must contain at least one tag name")
        return normalized

    # -- shared helpers --------------------------------------------------
    def _finding(self, code: str, severity: str, element: str | None,
                 attr: str | None, evidence: str, reason: str,
                 line: int, col: int) -> dict[str, Any]:
        return {
            "line": line,
            "col": col,
            "code": code,
            "severity": severity,
            "element": element,
            "attr": attr,
            "evidence": _truncate(evidence.replace("\n", " ").strip(), self.max_evidence_chars),
            "reason": reason,
        }

    def _audit_events(self, source: str, events: list[dict[str, Any]],
                      depth: int = 0) -> list[dict[str, Any]]:
        """Core audit pass over one event stream (also used for srcdoc and
        abrupt-comment re-audit)."""
        findings: list[dict[str, Any]] = []
        starts: list[int] | None = None
        for event in events:
            kind = event["kind"]
            if kind == "start":
                findings.extend(self._audit_start(event, depth))
            elif kind == "comment":
                if event.get("abrupt"):
                    if starts is None:
                        starts = _line_starts_of(source)
                    evidence_end = min(len(source), event["offset"] + self.max_evidence_chars)
                    findings.append(self._finding(
                        "ABRUPT_COMMENT", "medium", "#comment", None,
                        source[event["offset"]:evidence_end],
                        "browsers close <!--> (or <!--->) as an empty comment immediately; "
                        "the following markup is live and can smuggle payloads past filters",
                        event["line"], event["col"]))
                    findings.extend(self._audit_abrupt_hidden(source, event, starts, depth))
                if _IE_CONDITIONAL_RE.search(event["text"]):
                    findings.append(self._finding(
                        "IE_CONDITIONAL_COMMENT", "medium", "#comment", None,
                        f"<!--{event['text']}-->",
                        "comment contains an IE conditional hack that can smuggle markup past filters",
                        event["line"], event["col"]))
            elif kind == "data":
                if starts is None:
                    starts = _line_starts_of(source)
                findings.extend(self._audit_data(event, starts))
        return findings

    def _audit_abrupt_hidden(self, source: str, event: dict[str, Any],
                             starts: list[int], depth: int) -> list[dict[str, Any]]:
        """Re-audit the markup html.parser hid inside an abruptly-closed comment.

        Browsers treat everything after ``<!-->``/``<!--->`` as live markup;
        html.parser swallows it while scanning for the next ``-->``. The
        hidden slice is re-tokenized and its findings are remapped to the
        original source coordinates.
        """
        if depth >= _NESTED_AUDIT_DEPTH:
            return []
        offset = event["offset"]
        prefix_len = 6 if source.startswith("<!--->", offset) else 5
        close_at = offset + 4 + len(event["text"])
        if source[close_at:close_at + 3] == "-->" or source[close_at:close_at + 4] == "--!>":
            hidden_end = close_at
        else:
            hidden_end = len(source)
        hidden = source[offset + prefix_len:hidden_end]
        if not hidden.strip():
            return []
        try:
            tokenizer = _tokenize(hidden, self.max_tags, self.max_depth)
        except _CapViolation:
            return []
        inner = self._audit_events(hidden, tokenizer.events, depth + 1)
        remapped: list[dict[str, Any]] = []
        for finding in inner:
            inner_offset = tokenizer.offset_at(finding["line"], finding["col"])
            line, col = _line_col_at(starts, offset + prefix_len + inner_offset)
            finding["line"], finding["col"] = line, col
            remapped.append(finding)
        return remapped

    def _audit_start(self, event: dict[str, Any], srcdoc_depth: int = 0) -> list[dict[str, Any]]:
        findings: list[dict[str, Any]] = []
        tag = event["tag"]
        attrs = event["attrs"]
        line, col = event["line"], event["col"]
        raw = event["raw"]

        if tag == "plaintext":
            findings.append(self._finding(
                "PLAINTEXT_ELEMENT", "medium", tag, None, raw,
                "plaintext element disables parsing of the rest of the document and defeats downstream sanitizers",
                line, col))
        elif tag == "xmp":
            findings.append(self._finding(
                "XMP_ELEMENT", "medium", tag, None, raw,
                "xmp element disables parsing of the rest of the document and defeats downstream sanitizers",
                line, col))
        elif tag in _DANGEROUS_TAGS:
            severity, reason = _DANGEROUS_TAGS[tag]
            findings.append(self._finding(
                "DANGEROUS_TAG", severity, tag, None, raw, reason, line, col))

        attr_map = dict(attrs)
        for name, value in attrs:
            value = value or ""
            if _SWALLOWED_HANDLER_RE.match(value):
                findings.append(self._finding(
                    "EVENT_HANDLER_ATTR", "high", tag, name,
                    f'{name}={value}',
                    "on* handler text was swallowed into an empty attribute value and still reaches filters",
                    line, col))
            if _EVENT_ATTR_RE.match(name):
                findings.append(self._finding(
                    "EVENT_HANDLER_ATTR", "high", tag, name,
                    f'{name}="{value}"',
                    "on* attribute binds script execution to an element event",
                    line, col))
            if name == "srcdoc":
                findings.append(self._finding(
                    "SRCDOC_ATTR", "medium", tag, name,
                    f'srcdoc="{value}"',
                    "srcdoc embeds a nested HTML document that requires recursive auditing",
                    line, col))
                inner = self._audit_nested(value, srcdoc_depth + 1)
                if inner:
                    findings.append(self._finding(
                        "SRCDOC_DANGEROUS_CONTENT", "high", tag, name,
                        f'srcdoc="{value}"',
                        f"srcdoc content contains dangerous constructs: {', '.join(sorted(inner))}",
                        line, col))
            elif name == "style":
                findings.extend(self._audit_style_value(tag, name, value, line, col))
            elif name == "srcset":
                for candidate in value.split(","):
                    url = candidate.strip().split(" ")[0] if candidate.strip() else ""
                    result = _classify_url(url)
                    if result:
                        code, detail = result
                        findings.append(self._finding(
                            code, "high" if code == "DANGEROUS_URL_SCHEME" else "low",
                            tag, name, f'srcset="{value}"', detail, line, col))
            elif name in _URL_ATTRS or (tag == "param" and name in _PARAM_URL_ATTRS):
                result = _classify_url(value)
                if result:
                    code, detail = result
                    findings.append(self._finding(
                        code, "high" if code == "DANGEROUS_URL_SCHEME" else "low",
                        tag, name, f'{name}="{value}"', detail, line, col))
            if _EMBEDDED_TAG_RE.search(value):
                findings.append(self._finding(
                    "EMBEDDED_HTML_IN_ATTR", "medium", tag, name,
                    f'{name}="{value}"',
                    "attribute value embeds markup for a dangerous element after entity decoding",
                    line, col))

        if tag == "meta":
            findings.extend(self._audit_meta(event, attr_map, line, col))
        if tag in _ANIMATION_ELEMENTS and (attr_map.get("attributename") or "").strip().lower() in _HREF_ATTR_NAMES:
            findings.extend(self._audit_animation_values(event, attr_map, line, col))
        if tag in ("a", "area") and (attr_map.get("target") or "").strip().lower() == "_blank":
            rel_value = attr_map.get("rel") or ""
            rel = " ".join(rel_value.lower().split())
            tokens = set(rel.split()) - {""}
            if not ({"noopener", "noreferrer"} & tokens):
                findings.append(self._finding(
                    "TARGET_NO_REL", "info", tag, "target",
                    f'target="_blank" rel="{rel_value}"',
                    "target=_blank link lacks rel=noopener/noreferrer; legacy browsers expose window.opener",
                    line, col))
        if tag == "input" and (attr_map.get("type") or "").strip().lower() == "hidden" and "autofocus" in attr_map:
            findings.append(self._finding(
                "HIDDEN_AUTOFOCUS", "medium", tag, "autofocus",
                raw,
                "hidden autofocused input steals focus and can drive UI-redress tricks",
                line, col))
        return findings

    def _audit_animation_values(self, event, attr_map, line, col) -> list[dict[str, Any]]:
        """Flag <animate>/<set> elements that retarget href/xlink:href.

        SVG animation elements assign their from/to/by/values attributes to
        the attribute named by attributeName; targeting href turns the value
        into a navigable URL (a published SVG XSS vector class).
        """
        findings: list[dict[str, Any]] = []
        tag = event["tag"]
        for name in _ANIMATION_VALUE_ATTRS:
            value = attr_map.get(name) or ""
            if not value:
                continue
            candidates = value.split(",") if name == "values" else [value]
            for candidate in candidates:
                result = _classify_url(candidate.strip())
                if result:
                    code, detail = result
                    findings.append(self._finding(
                        code, "high" if code == "DANGEROUS_URL_SCHEME" else "low",
                        tag, name, f'{name}="{value}"', detail, line, col))
        return findings

    def _audit_meta(self, event, attr_map, line, col) -> list[dict[str, Any]]:
        findings: list[dict[str, Any]] = []
        http_equiv = (attr_map.get("http-equiv") or "").strip().lower()
        raw = event["raw"]
        if http_equiv == "refresh":
            content = attr_map.get("content", "") or ""
            findings.append(self._finding(
                "META_REFRESH", "medium", "meta", "http-equiv",
                raw, "meta refresh forces navigation redirect", line, col))
            match = _URL_IN_REFRESH_RE.search(_probe(content))
            if match:
                result = _classify_url(match.group(1).split(";")[0].strip())
                if result:
                    code, detail = result
                    findings.append(self._finding(
                        code, "high" if code == "DANGEROUS_URL_SCHEME" else "low",
                        "meta", "content", raw, detail, line, col))
        charset = attr_map.get("charset", "")
        if charset:
            if charset.strip().lower() not in _UTF8_CHARSETS:
                findings.append(self._finding(
                    "META_CHARSET", "info", "meta", "charset", raw,
                    f"non-UTF-8 charset {charset.strip()!r} enables charset-confusion attacks",
                    line, col))
        elif http_equiv == "content-type":
            match = _CHARSET_RE.search(attr_map.get("content", "") or "")
            if match and match.group(1).lower() not in _UTF8_CHARSETS:
                findings.append(self._finding(
                    "META_CHARSET", "info", "meta", "content", raw,
                    f"non-UTF-8 charset {match.group(1)!r} enables charset-confusion attacks",
                    line, col))
        return findings

    def _audit_style_value(self, tag, name, value, line, col) -> list[dict[str, Any]]:
        findings: list[dict[str, Any]] = []
        probed = _probe(value)
        evidence = f'style="{value}"'
        if _STYLE_SCHEME_RE.search(probed):
            findings.append(self._finding(
                "STYLE_JS_URL", "high", tag, name, evidence,
                "style value references a script-executing URL scheme",
                line, col))
        elif _STYLE_BINDING_RE.search(probed):
            findings.append(self._finding(
                "STYLE_BINDING", "medium", tag, name, evidence,
                "style value uses -moz-binding or behavior, legacy script-executing CSS constructs",
                line, col))
        elif _STYLE_EXPRESSION_RE.search(probed):
            findings.append(self._finding(
                "STYLE_EXPRESSION", "medium", tag, name, evidence,
                "style value uses expression(), a legacy script-executing CSS construct",
                line, col))
        return findings

    def _audit_data(self, event, starts: list[int]) -> list[dict[str, Any]]:
        findings: list[dict[str, Any]] = []
        text = event["text"]
        stripped = text.lstrip()
        # Point data findings at the line/column where the quoted evidence
        # actually begins (the raw data run may start lines earlier).
        lead = len(text) - len(stripped)
        line, col = _line_col_at(starts, event["offset"] + lead)
        if event["raw_parent"] == "style":
            probed = _probe(text)
            evidence = text
            if _STYLE_SCHEME_RE.search(probed):
                findings.append(self._finding(
                    "STYLE_JS_URL", "high", "style", None, evidence,
                    "style element content references a script-executing URL scheme",
                    line, col))
            elif _STYLE_BINDING_RE.search(probed):
                findings.append(self._finding(
                    "STYLE_BINDING", "medium", "style", None, evidence,
                    "style element content uses -moz-binding or behavior, legacy script-executing CSS constructs",
                    line, col))
            elif _STYLE_EXPRESSION_RE.search(probed):
                findings.append(self._finding(
                    "STYLE_EXPRESSION", "medium", "style", None, evidence,
                    "style element content uses expression()",
                    line, col))
        elif event["raw_parent"] is None and re.search(r"<[a-zA-Z]", text):
            findings.append(self._finding(
                "MALFORMED_MARKUP", "info", "#text", None, text,
                "text contains markup-like data that the tokenizer treated as text",
                line, col))
        return findings

    def _audit_cdata_events(self, events) -> list[dict[str, Any]]:
        """Probe concatenated unknown declarations (CDATA smuggling)."""
        decl_events = [e for e in events if e["kind"] == "unknown_decl"]
        if not decl_events:
            return []
        joined = "".join(
            text[len("CDATA["):] if text.startswith("CDATA[") else text
            for text in (e["text"] for e in decl_events))
        if _classify_url(joined) or _inline_danger(_probe(joined)):
            first = decl_events[0]
            return [self._finding(
                "DANGEROUS_URL_SCHEME", "high", "#cdata", None,
                joined,
                "CDATA declarations smuggle a dangerous URL scheme when concatenated",
                first["line"], first["col"])]
        return []

    def _audit_nested(self, value: str, depth: int) -> list[str]:
        """Audit srcdoc content; returns the dangerous codes found inside.

        Recursion is bounded so srcdoc-in-srcdoc chains cannot loop.
        """
        if depth > _NESTED_AUDIT_DEPTH:
            return ["SRCDOC_CHAIN_DEPTH"]
        try:
            tokenizer = _tokenize(value, self.max_tags, self.max_depth)
        except _CapViolation:
            return ["input_too_large"]
        nested = self._audit_events(value, tokenizer.events, depth)
        return sorted({f["code"] for f in nested if f["severity"] in ("high", "medium")})

    def _audit_raw_source(self, source: str, events: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], bool]:
        """Cross-check the raw source for tags the tokenizer dropped.

        html.parser silently drops unterminated start tags at end of input,
        so every ``<tag`` occurrence outside script/style/comment spans is
        matched against recorded tag events; unmatched occurrences are
        reported and probed for dangerous schemes or event handlers.
        Returns ``(findings, capped)`` where ``capped`` says whether more
        occurrences existed than were reported.
        """
        findings: list[dict[str, Any]] = []
        masked = _mask_raw_spans(source)
        starts = _line_starts_of(source)
        event_counts: Counter = Counter()
        for event in events:
            if event["kind"] == "start":
                event_counts[event["tag"]] += 1
        raw_occurrences: dict[str, list[int]] = {}
        counts: Counter = Counter()
        for match in _RAW_TAG_RE.finditer(masked):
            name = match.group(1).lower()
            counts[name] += 1
            raw_occurrences.setdefault(name, []).append(match.start())
        # Occurrences recovered per tag name are capped: probing thousands of
        # identical dropped tags is quadratic work for no extra signal, and
        # the returned findings list is capped by max_findings anyway.
        report_cap = max(_RAW_EXTRA_REPORT_CAP, self.max_findings)
        capped = False
        for name in sorted(counts):
            extra = counts[name] - event_counts.get(name, 0)
            if extra <= 0:
                continue
            if extra > report_cap:
                capped = True
            for offset in raw_occurrences[name][-min(extra, report_cap):]:
                end = masked.find(">", offset)
                end = len(masked) if end < 0 else min(end + 1, offset + 300)
                slice_text = source[offset:end]
                line, col = _line_col_at(starts, offset)
                probed = _probe(slice_text)
                scheme = _inline_danger(probed)
                matched = False
                if name in _DANGEROUS_TAGS:
                    severity, reason = _DANGEROUS_TAGS[name]
                    findings.append(self._finding(
                        "DANGEROUS_TAG", severity, name, None, slice_text,
                        f"unterminated dangerous element: {reason}", line, col))
                    matched = True
                if scheme:
                    findings.append(self._finding(
                        "DANGEROUS_URL_SCHEME", "high", name, None, slice_text,
                        f"unterminated tag smuggles a {scheme}: URL scheme",
                        line, col))
                    matched = True
                elif _EMBEDDED_HANDLER_RE.search(slice_text) or _SWALLOWED_HANDLER_RE.match(probed):
                    findings.append(self._finding(
                        "EVENT_HANDLER_ATTR", "high", name, None, slice_text,
                        "unterminated tag smuggles an on* event handler",
                        line, col))
                    matched = True
                if not matched:
                    findings.append(self._finding(
                        "MALFORMED_MARKUP", "info", name, None, slice_text,
                        "tag-like sequence was dropped by the tokenizer (unterminated or malformed)",
                        line, col))
        return findings, capped

    def _audit_mode(self, source: str, tokenizer: _FragmentTokenizer) -> dict[str, Any]:
        findings = self._audit_events(source, tokenizer.events)
        findings.extend(self._audit_cdata_events(tokenizer.events))
        raw_findings, raw_capped = self._audit_raw_source(source, tokenizer.events)
        findings.extend(raw_findings)
        findings.sort(key=lambda f: (f["line"], f["col"]))
        counts = Counter(f["severity"] for f in findings)
        finding_counts = {
            "total": len(findings),
            "high": counts.get("high", 0),
            "medium": counts.get("medium", 0),
            "low": counts.get("low", 0),
            "info": counts.get("info", 0),
        }
        truncated = len(findings) > self.max_findings or raw_capped
        return {
            "status": "success",
            "mode": "audit",
            "html_chars": len(source),
            "element_count": tokenizer.tag_count,
            "findings": findings[: self.max_findings],
            "finding_counts": finding_counts,
            "truncated": truncated,
        }

    # -- allowlist diff ----------------------------------------------------
    def _allowlist_diff(self, source: str, tokenizer: _FragmentTokenizer,
                        allowed: list[str]) -> dict[str, Any]:
        tag_lines: dict[str, list[int]] = {}
        tag_counts: Counter = Counter()
        for event in tokenizer.events:
            if event["kind"] != "start":
                continue
            tag = event["tag"]
            tag_counts[tag] += 1
            lines = tag_lines.setdefault(tag, [])
            if len(lines) < 5 and event["line"] not in lines:
                lines.append(event["line"])
        used = sorted(tag_counts)
        allowed_set = set(allowed)
        disallowed = [
            {"tag": tag, "count": tag_counts[tag], "lines": tag_lines[tag]}
            for tag in sorted(tag_counts, key=lambda t: (-tag_counts[t], t))
            if tag not in allowed_set
        ]
        unknown_allowed = sorted(allowed_set - set(tag_counts))
        return {
            "status": "success",
            "mode": "allowlist_diff",
            "allowed_tags": allowed,
            "used_tags": used,
            "disallowed_tags": disallowed,
            "unknown_allowed_tags": unknown_allowed,
            "stats": {
                "element_count": tokenizer.tag_count,
                "unique_used_tags": len(used),
                "disallowed_total": sum(item["count"] for item in disallowed),
            },
        }

    # -- text extraction ---------------------------------------------------
    def _text_mode(self, source: str, tokenizer: _FragmentTokenizer) -> dict[str, Any]:
        parts: list[str] = []
        skipped: Counter = Counter()
        for event in tokenizer.events:
            kind = event["kind"]
            if kind == "data":
                if event["raw_parent"] in _RAW_TEXT_ELEMENTS:
                    if event["text"].strip():
                        skipped[event["raw_parent"]] += 1
                else:
                    parts.append(event["text"])
            elif kind in ("entityref", "charref"):
                parts.append(event["decoded"])
        text = re.sub(r"\s+", " ", "".join(parts)).strip()
        truncated = len(text) > self.max_text_chars
        return {
            "status": "success",
            "mode": "text",
            "text": text[: self.max_text_chars],
            "text_chars": len(text),
            "truncated": truncated,
            "skipped_invisible": [
                {"element": element, "count": skipped[element]}
                for element in sorted(skipped)
            ],
        }

    # -- stats ---------------------------------------------------------------
    def _stats_mode(self, source: str, tokenizer: _FragmentTokenizer) -> dict[str, Any]:
        events = tokenizer.events
        tag_histogram: Counter = Counter()
        attr_histogram: Counter = Counter()
        entity_census: Counter = Counter()
        link_schemes: Counter = Counter()
        forms: list[dict[str, Any]] = []
        orphan_inputs = 0
        open_forms: list[dict[str, Any]] = []
        for event in events:
            kind = event["kind"]
            if kind == "start":
                tag = event["tag"]
                tag_histogram[tag] += 1
                for name, _value in event["attrs"]:
                    attr_histogram[name] += 1
                attr_map = dict(event["attrs"])
                if tag == "form":
                    action = attr_map.get("action")
                    record = {
                        # Attribute values can be arbitrarily long; echo them
                        # truncated like every other piece of evidence.
                        "action": _truncate(action, self.max_evidence_chars) if action else action,
                        "method": (attr_map.get("method") or "get").strip().lower(),
                        "input_count": 0,
                        "inputs": [],
                    }
                    forms.append(record)
                    open_forms.append(record)
                elif tag == "input":
                    name = attr_map.get("name")
                    snapshot = {"type": (attr_map.get("type") or "text").strip().lower(),
                                "name": _truncate(name, self.max_evidence_chars) if name else name}
                    if open_forms:
                        current = open_forms[-1]
                        current["input_count"] += 1
                        if len(current["inputs"]) < 20:
                            current["inputs"].append(snapshot)
                    else:
                        orphan_inputs += 1
                urls: list[str] = []
                for name, value in event["attrs"]:
                    value = value or ""
                    if name == "srcset":
                        urls.extend(c.strip().split(" ")[0] for c in value.split(",") if c.strip())
                    elif name in _URL_ATTRS or (tag == "param" and name in _PARAM_URL_ATTRS):
                        urls.append(value)
                for url in urls:
                    scheme = _scheme_of(_probe(url))
                    if scheme is None:
                        link_schemes["relative"] += 1
                    else:
                        link_schemes[scheme] += 1
            elif kind == "end":
                if event["tag"] == "form" and open_forms:
                    open_forms.pop()
            elif kind in ("entityref", "charref"):
                entity_census[event["raw"]] += 1
        return {
            "status": "success",
            "mode": "stats",
            "html_chars": len(source),
            "element_count": tokenizer.tag_count,
            "tag_histogram": _sorted_counter(tag_histogram),
            "attr_histogram": _sorted_counter(attr_histogram),
            "max_depth": tokenizer.max_depth_seen,
            "forms": forms,
            "orphan_input_count": orphan_inputs,
            "link_inventory": {
                "total": sum(link_schemes.values()),
                "by_scheme": _sorted_counter(link_schemes),
            },
            "entity_census": _sorted_counter(entity_census),
        }
