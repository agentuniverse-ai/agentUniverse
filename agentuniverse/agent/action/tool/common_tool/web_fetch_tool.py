# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/5/15 10:00
# @FileName: web_fetch_tool.py

import re
import json

from agentuniverse.agent.action.tool.tool import Tool


class WebFetchTool(Tool):
    """Fetch content from a URL and extract readable text."""

    def execute(self, url: str, prompt: str = None,
                max_length: int = 50000) -> str:
        try:
            import requests
        except ImportError:
            return json.dumps({
                "error": "requests library is required. Install with: pip install requests",
                "status": "error"
            })

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; agentUniverse/1.0)'
            }
            response = requests.get(url, headers=headers, timeout=30,
                                    allow_redirects=True)
            response.raise_for_status()

            content_type = response.headers.get('Content-Type', '')
            if 'text/html' in content_type or 'text/xml' in content_type:
                text = self._html_to_text(response.text)
            else:
                text = response.text

            # Truncate if too long
            if len(text) > max_length:
                text = text[:max_length] + "\n\n[Content truncated]"

            result = {
                "url": response.url,
                "content": text,
                "status_code": response.status_code,
                "status": "success"
            }
            if prompt:
                result["prompt"] = prompt

            return json.dumps(result)

        except Exception as e:
            return json.dumps({
                "error": str(e),
                "url": url,
                "status": "error"
            })

    @staticmethod
    def _html_to_text(html: str) -> str:
        """Simple HTML to text conversion without external dependencies."""
        # Remove script and style blocks
        text = re.sub(r'<script[^>]*>[\s\S]*?</script>', '', html, flags=re.IGNORECASE)
        text = re.sub(r'<style[^>]*>[\s\S]*?</style>', '', text, flags=re.IGNORECASE)
        text = re.sub(r'<nav[^>]*>[\s\S]*?</nav>', '', text, flags=re.IGNORECASE)
        text = re.sub(r'<footer[^>]*>[\s\S]*?</footer>', '', text, flags=re.IGNORECASE)
        # Remove HTML comments
        text = re.sub(r'<!--[\s\S]*?-->', '', text)
        # Convert common block elements to newlines
        text = re.sub(r'<br\s*/?\s*>', '\n', text, flags=re.IGNORECASE)
        text = re.sub(r'</(p|div|h[1-6]|li|tr|blockquote)>', '\n', text, flags=re.IGNORECASE)
        # Remove remaining tags
        text = re.sub(r'<[^>]+>', '', text)
        # Decode common HTML entities
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        text = text.replace('&#39;', "'")
        text = text.replace('&nbsp;', ' ')
        # Collapse whitespace
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()
