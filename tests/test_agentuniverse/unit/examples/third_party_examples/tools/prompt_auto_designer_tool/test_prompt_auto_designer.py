# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/10/13
# @Author  : au-bot
# @FileName: test_prompt_auto_designer.py
"""Unit tests for PromptAutoDesigner pure helpers."""

import pytest

from examples.third_party_examples.tools.prompt_auto_designer_tool.prompt_auto_designer import (
    PromptAutoDesigner,
    PromptAutoDesignerError,
    PromptGenerationRequest,
)


class TestPromptAutoDesigner:
    """Test deterministic helpers of PromptAutoDesigner."""

    @pytest.fixture
    def designer(self):
        """Return a designer instance that never touches an LLM."""
        return PromptAutoDesigner()

    def test_ensure_list_variants(self):
        """_ensure_list normalizes None/list/scalar inputs."""
        assert PromptAutoDesigner._ensure_list(None) == []
        assert PromptAutoDesigner._ensure_list(["a", 1]) == ["a", "1"]
        assert PromptAutoDesigner._ensure_list("x") == ["x"]

    def test_format_bullets(self):
        """_format_bullets renders bullets and fallback text."""
        assert PromptAutoDesigner._format_bullets(["a", "b"]) == "- a\n- b"
        assert PromptAutoDesigner._format_bullets([], fallback="无") == "无"

    def test_coerce_float(self):
        """_coerce_float turns numbers and numeric strings into floats."""
        assert PromptAutoDesigner._coerce_float(3) == 3.0
        assert PromptAutoDesigner._coerce_float("92.5分") == 92.5
        assert PromptAutoDesigner._coerce_float("abc") is None
        assert PromptAutoDesigner._coerce_float(None) is None

    def test_parse_json_valid_and_wrapped(self):
        """_parse_json accepts plain and embedded JSON objects."""
        assert PromptAutoDesigner._parse_json('{"introduction": "x"}') == {"introduction": "x"}
        wrapped = PromptAutoDesigner._parse_json('prefix {"introduction": "x"} suffix')
        assert wrapped == {"introduction": "x"}

    def test_parse_json_raises_on_garbage(self):
        """_parse_json raises PromptAutoDesignerError for invalid text."""
        with pytest.raises(PromptAutoDesignerError):
            PromptAutoDesigner._parse_json("not json at all")

    def test_build_generation_payload_defaults(self):
        """Payload falls back to sensible defaults for empty fields."""
        request = PromptGenerationRequest(scenario="客服", objective="回答问题")
        payload = PromptAutoDesigner()._build_generation_payload(request)
        assert payload["scenario"] == "客服"
        assert payload["objective"] == "回答问题"
        assert payload["audience"] == "未指定"
        assert payload["language"] == "中文"
        assert payload["inputs"] == "无"

    def test_build_generation_payload_uses_inputs(self):
        """Provided inputs are rendered as bullet lines."""
        request = PromptGenerationRequest(scenario="s", objective="o", inputs=["提问", "检索结果"])
        payload = PromptAutoDesigner()._build_generation_payload(request)
        assert payload["inputs"] == "- 提问\n- 检索结果"
