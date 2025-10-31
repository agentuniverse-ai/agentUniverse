import json

import pytest

from agentuniverse.prompt.prompt_auto_designer import (
    PromptAutoDesigner,
    PromptAutoDesignerError,
    PromptGenerationRequest,
    PromptOptimizationRequest,
)
from agentuniverse.prompt.prompt_model import AgentPromptModel


def test_generate_prompt_success(monkeypatch):
    captured: dict = {}

    def fake_invoke(self, version, payload):
        captured["version"] = version
        captured["payload"] = payload
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

    designer = PromptAutoDesigner()
    request = PromptGenerationRequest(
        scenario="企业在线客服机器人",
        objective="快速回答常见问题并引用 FAQ 数据",
        audience="客服专员",
        tone="友好且专业",
        language="中文",
        inputs=["用户提问", "FAQ 检索结果"],
        outputs=["结构化回答", "引用来源"],
        constraints=["回答前先确认信息来源", "拒绝超出知识库范围的请求"],
        additional_context="机器人部署在官网，需要适配文字与语音双渠道。",
        examples="Q: 如何重置密码？\nA: 请前往账号设置...",
    )

    result = designer.generate_prompt(request)

    assert result.prompt.introduction == "你是企业知识库的智能体助手。"
    assert result.prompt.target.startswith("帮助客服")
    assert result.prompt_text.startswith("你是企业知识库的智能体助手。")
    assert result.suggested_variables == ["background", "input"]
    assert result.rationale == "针对客服流程强调输入来源。"
    assert captured["version"] == "auto_prompt.generator_cn"
    assert "- 用户提问" in captured["payload"]["inputs"]


def test_optimize_prompt_merges_fallback(monkeypatch):
    base_prompt = AgentPromptModel(
        introduction="你是一名财务分析助手。",
        target="帮助分析季度营收表现。",
        instruction="阅读背景信息并回答财务问题。",
    )

    def fake_invoke(self, version, payload):
        assert version == "auto_prompt.optimizer_cn"
        assert "季度营收" in payload["current_prompt"]
        return json.dumps(
            {
                "introduction": "你是一名上市公司财报分析顾问。",
                "instruction": "优先列出关键财务指标，再给出风险提示。",
                "rationale": "强化指标顺序并加入风险提醒。",
                "change_log": ["优化身份描述", "补充风险提示步骤"],
                "score": "92.5",
            }
        )

    monkeypatch.setattr(PromptAutoDesigner, "_invoke_llm", fake_invoke)

    designer = PromptAutoDesigner()
    request = PromptOptimizationRequest(
        prompt=base_prompt,
        scenario="上市公司财报解读",
        objective="总结营收并指出风险",
        issues=["未明确风险提示", "回答顺序不稳定"],
        success_metrics=["输出需覆盖收入、利润、风险三部分"],
        style="专业且有条理",
    )

    result = designer.optimize_prompt(request)

    assert result.prompt.introduction == "你是一名上市公司财报分析顾问。"
    assert result.prompt.target == "帮助分析季度营收表现。"
    assert result.prompt.instruction.startswith("优先列出关键财务指标")
    assert result.change_log == ["优化身份描述", "补充风险提示步骤"]
    assert result.score == pytest.approx(92.5, rel=1e-3)
    assert result.rationale == "强化指标顺序并加入风险提醒。"


def test_generate_prompt_invalid_json(monkeypatch):
    monkeypatch.setattr(PromptAutoDesigner, "_invoke_llm", lambda self, version, payload: "not-json")
    designer = PromptAutoDesigner()
    request = PromptGenerationRequest(
        scenario="安防巡检机器人",
        objective="生成巡检指令",
    )

    with pytest.raises(PromptAutoDesignerError):
        designer.generate_prompt(request)
