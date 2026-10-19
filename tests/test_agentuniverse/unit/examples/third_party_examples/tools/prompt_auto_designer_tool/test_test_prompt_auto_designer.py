# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/10/13
# @Author  : au-bot
# @FileName: test_test_prompt_auto_designer.py
"""Unit tests exercising the example prompt_auto_designer test scenarios."""

import pytest

from agentuniverse.prompt.prompt_model import AgentPromptModel
from examples.third_party_examples.tools.prompt_auto_designer_tool.prompt_auto_designer import (
    PromptAutoDesigner,
    PromptGenerationRequest,
    PromptOptimizationRequest,
)


class TestPromptAutoDesignerScenario:
    """Re-run the deterministic designer scenarios with a faked LLM call."""

    @pytest.fixture
    def designer(self):
        """Return a designer whose _invoke_llm never touches a real LLM."""
        return PromptAutoDesigner()

    def test_generate_prompt_success(self, designer, monkeypatch):
        """A valid JSON LLM reply yields a populated PromptDesignResult."""
        import json

        def fake_invoke(self, version, payload):
            return json.dumps(
                {
                    "introduction": "你是企业知识库的智能体助手。",
                    "target": "帮助客服在三步内给出准确答案。",
                    "instruction": "始终读取 background 并结合 input 给出结论。",
                    "rationale": "针对客服流程强调输入来源。",
                    "suggested_variables": ["background", "input"],
                }
            )

        monkeypatch.setattr(PromptAutoDesigner, "_invoke_llm", fake_invoke)
        request = PromptGenerationRequest(scenario="企业在线客服机器人", objective="快速回答问题")
        result = designer.generate_prompt(request)
        assert result.prompt.introduction == "你是企业知识库的智能体助手。"
        assert result.prompt_text.startswith("你是企业知识库的智能体助手。")
        assert result.suggested_variables == ["background", "input"]
        assert result.rationale == "针对客服流程强调输入来源。"

    def test_optimize_prompt_merges_fallback(self, designer, monkeypatch):
        """Optimization merges LLM fields with the fallback prompt."""
        import json

        base_prompt = AgentPromptModel(
            introduction="你是一名财务分析助手。",
            target="帮助分析季度营收表现。",
            instruction="阅读背景信息并回答财务问题。",
        )

        def fake_invoke(self, version, payload):
            return json.dumps(
                {
                    "introduction": "你是一名上市公司财报分析顾问。",
                    "instruction": "优先列出关键财务指标。",
                    "score": "92.5",
                    "change_log": ["优化身份描述"],
                }
            )

        monkeypatch.setattr(PromptAutoDesigner, "_invoke_llm", fake_invoke)
        request = PromptOptimizationRequest(
            prompt=base_prompt, scenario="上市公司财报解读", objective="总结营收并指出风险"
        )
        result = designer.optimize_prompt(request)
        assert result.prompt.introduction == "你是一名上市公司财报分析顾问。"
        assert result.prompt.target == "帮助分析季度营收表现。"
        assert result.score == pytest.approx(92.5)
        assert result.change_log == ["优化身份描述"]

    def test_generate_prompt_invalid_json(self, designer, monkeypatch):
        """Non-JSON LLM output raises PromptAutoDesignerError."""
        from examples.third_party_examples.tools.prompt_auto_designer_tool.prompt_auto_designer import (
            PromptAutoDesignerError,
        )

        monkeypatch.setattr(PromptAutoDesigner, "_invoke_llm", lambda self, version, payload: "not-json")
        request = PromptGenerationRequest(scenario="安防巡检机器人", objective="生成巡检指令")
        with pytest.raises(PromptAutoDesignerError):
            designer.generate_prompt(request)
