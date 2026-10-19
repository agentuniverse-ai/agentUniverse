#!/usr/bin/env python3
"""Text format converter tool.

Converts between Markdown, HTML, and plain text formats. Uses Python's
built-in ``html.parser`` and ``re`` — zero third-party dependency.

Supports: markdown_to_html, html_to_text, markdown_to_text.

Addresses #252 (more tools).
"""

# ruff: noqa: TRY003, TRY004

import logging
import re
from html.parser import HTMLParser
from typing import Any

from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger

logger = logging.getLogger(__name__)


class _HTMLToTextParser(HTMLParser):
    """Extract plain text from HTML, skipping script/style/noscript."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._parts: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript", "head", "meta", "link"):
            self._skip_depth += 1
        elif tag in ("p", "div", "br", "li", "tr", "h1", "h2", "h3",
                      "h4", "h5", "h6"):
            self._parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "head", "meta", "link"):
            if self._skip_depth > 0:
                self._skip_depth -= 1
        elif tag in ("p", "div", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6"):
            self._parts.append("\n")

    def handle_data(self, data):
        if self._skip_depth:
            return
        self._parts.append(data)

    def get_text(self) -> str:
        text = "".join(self._parts)
        # Collapse multiple newlines.
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()


class TextConverterTool(Tool):
    """Convert text between Markdown, HTML, and plain text.

    Attributes:
        max_input_chars: Maximum input length (default 100_000).
    """

    max_input_chars: int = 100_000

    def execute(self, mode: str, text: str = "", **kwargs) -> dict:
        try:
            op = self._normalize_mode(mode)
            if not isinstance(text, str) or not text:
                return self._error("validation_error", "text is required")
            if len(text) > self.max_input_chars:
                return self._error("validation_error",
                                   f"Input exceeds max_input_chars "
                                   f"({self.max_input_chars})")
            if op == "markdown_to_html":
                return self._ok(mode=op, converted=self._md_to_html(text))
            if op == "html_to_text":
                return self._ok(mode=op, converted=self._html_to_text(text))
            if op == "markdown_to_text":
                return self._ok(mode=op,
                                converted=self._html_to_text(
                                    self._md_to_html(text)))
            return self._error("validation_error", f"Unknown mode: {mode}")
        except (TypeError, ValueError) as exc:
            return self._error("validation_error", str(exc))
        except Exception as exc:
            return self._error("operation_error", str(exc))

    @staticmethod
    def _normalize_mode(mode: str) -> str:
        if not isinstance(mode, str):
            raise TypeError("mode must be a string")
        normalized = mode.strip().lower()
        allowed = {"markdown_to_html", "html_to_text", "markdown_to_text"}
        if normalized not in allowed:
            raise ValueError(
                f"mode must be one of: {', '.join(sorted(allowed))}")
        return normalized

    @staticmethod
    def _error(error_type: str, message: str) -> dict:
        return {"status": "error", "error_type": error_type, "error": message}

    @staticmethod
    def _ok(**kwargs) -> dict:
        return {"status": "success", **kwargs}

    @staticmethod
    def _md_to_html(md: str) -> str:
        """Convert basic Markdown to HTML (headings, bold, italic, code, lists)."""
        lines = md.split("\n")
        html_lines: list[str] = []
        in_code_block = False
        in_list = False

        for line in lines:
            stripped = line.strip()

            # Code fence.
            if stripped.startswith("```"):
                if in_code_block:
                    html_lines.append("</code></pre>")
                    in_code_block = False
                else:
                    html_lines.append("<pre><code>")
                    in_code_block = True
                continue
            if in_code_block:
                html_lines.append(line)
                continue

            # Headings.
            heading_match = re.match(r"^(#{1,6})\s+(.*)", stripped)
            if heading_match:
                if in_list:
                    html_lines.append("</ul>")
                    in_list = False
                level = len(heading_match.group(1))
                text = TextConverterTool._inline_md(heading_match.group(2))
                html_lines.append(f"<h{level}>{text}</h{level}>")
                continue

            # List items.
            list_match = re.match(r"^[-*+]\s+(.*)", stripped)
            if list_match:
                if not in_list:
                    html_lines.append("<ul>")
                    in_list = True
                html_lines.append(f"<li>{TextConverterTool._inline_md(list_match.group(1))}</li>")
                continue

            # Close list if we were in one.
            if in_list:
                html_lines.append("</ul>")
                in_list = False

            # Horizontal rule.
            if re.match(r"^(-{3,}|\*{3,}|_{3,})$", stripped):
                html_lines.append("<hr>")
                continue

            # Blockquote.
            if stripped.startswith(">"):
                html_lines.append(
                    f"<blockquote>{TextConverterTool._inline_md(stripped[1:].strip())}</blockquote>")
                continue

            # Paragraph or empty.
            if stripped:
                html_lines.append(f"<p>{TextConverterTool._inline_md(stripped)}</p>")
            else:
                html_lines.append("")

        if in_list:
            html_lines.append("</ul>")
        if in_code_block:
            html_lines.append("</code></pre>")

        return "\n".join(html_lines)

    @staticmethod
    def _inline_md(text: str) -> str:
        """Convert inline Markdown (bold, italic, code, links) to HTML."""
        # Inline code.
        text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
        # Bold.
        text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
        text = re.sub(r"__([^_]+)__", r"<strong>\1</strong>", text)
        # Italic.
        text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
        text = re.sub(r"_([^_]+)_", r"<em>\1</em>", text)
        # Links.
        text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
        return text

    @staticmethod
    def _html_to_text(html: str) -> str:
        parser = _HTMLToTextParser()
        parser.feed(html)
        parser.close()
        return parser.get_text()

    def _initialize_by_component_configer(self, configer: ComponentConfiger) \
            -> "TextConverterTool":
        super()._initialize_by_component_configer(configer)
        if hasattr(configer, "max_input_chars"):
            self.max_input_chars = configer.max_input_chars
        return self
