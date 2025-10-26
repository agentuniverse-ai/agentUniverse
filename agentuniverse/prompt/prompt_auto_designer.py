# !/usr/bin/env python3
# -*- coding:utf-8 -*-
"""小工具，用来把结构化输入快速拼成可用的 prompt。"""
from __future__ import annotations

import json
import re
from typing import Any, Callable, Dict, List, Optional

from pydantic import BaseModel, Field

from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.util.prompt_util import generate_template
from agentuniverse.llm.llm import LLM
from agentuniverse.llm.llm_manager import LLMManager
from agentuniverse.prompt.prompt import Prompt
from agentuniverse.prompt.prompt_manager import PromptManager
from agentuniverse.prompt.prompt_model import AgentPromptModel


class PromptAutoDesignerError(RuntimeError):
    """LLM 掉链子或者结果不对时就丢这个异常。"""


class PromptGenerationRequest(BaseModel):
    """生成 prompt 时最常用的那几块素材就靠它承载。"""

    scenario: str = Field(..., description="核心业务或应用场景。")
    objective: str = Field(..., description="该 prompt 需要驱动智能体完成的目标。")
    audience: Optional[str] = Field(default=None, description="面向的用户或风格要求。")
    tone: Optional[str] = Field(default=None, description="希望的语气与表述风格。")
    language: str = Field(default="中文", description="生成 prompt 所使用的语言。")
    inputs: List[str] = Field(default_factory=list, description="智能体将接收的关键输入。")
    outputs: List[str] = Field(default_factory=list, description="期望的输出内容形态。")
    constraints: List[str] = Field(default_factory=list, description="必须遵循的约束或限制条件。")
    additional_context: Optional[str] = Field(default=None, description="可选的背景信息、知识库说明等。")
    examples: Optional[str] = Field(default=None, description="示例问答或既有 prompt 片段。")


class PromptOptimizationRequest(BaseModel):
    """草稿已经有了，需要再雕琢就填这个模型。"""

    prompt: AgentPromptModel = Field(..., description="当前使用的 prompt 三段文案。")
    scenario: Optional[str] = Field(default=None, description="补充的场景描述。")
    objective: Optional[str] = Field(default=None, description="该 prompt 需要实现的目标。")
    issues: List[str] = Field(default_factory=list, description="当前 prompt 遇到的问题或痛点。")
    success_metrics: List[str] = Field(default_factory=list, description="衡量优化效果的指标。")
    style: Optional[str] = Field(default=None, description="目标语气或写作风格。")
    language: str = Field(default="中文", description="优化后 prompt 的语言。")
    additional_context: Optional[str] = Field(default=None, description="补充的上下文或边界。")


class PromptDesignResult(BaseModel):
    """生成阶段的产出，带上 prompt 文本和变量建议。"""

    prompt: AgentPromptModel
    prompt_text: str
    rationale: Optional[str] = None
    suggested_variables: List[str] = Field(default_factory=list)


class PromptOptimizationResult(BaseModel):
    """优化后的结果，附带变更记录和评分。"""

    prompt: AgentPromptModel
    prompt_text: str
    rationale: Optional[str] = None
    change_log: List[str] = Field(default_factory=list)
    score: Optional[float] = None


class PromptAutoDesigner:
    """主流程：拉模板、调 LLM、解析结果，全都打包在这。"""

    def __init__(
        self,
        generation_prompt_version: str = "auto_prompt.generator_cn",
        optimization_prompt_version: str = "auto_prompt.optimizer_cn",
        llm_name: Optional[str] = None,
        llm_factory: Optional[Callable[[], LLM]] = None,
    ):
        self.generation_prompt_version = generation_prompt_version
        self.optimization_prompt_version = optimization_prompt_version
        self.llm_name = llm_name
        self._llm_factory = llm_factory

    def generate_prompt(self, request: PromptGenerationRequest) -> PromptDesignResult:
        """把输入塞进模板，让 LLM 现写一份合适的 prompt。"""
        payload = self._build_generation_payload(request)
        raw = self._invoke_llm(self.generation_prompt_version, payload)
        parsed = self._parse_json(raw)
        prompt_model = self._build_prompt_model(parsed)
        prompt_text = generate_template(prompt_model, ["introduction", "target", "instruction"]).strip()
        return PromptDesignResult(
            prompt=prompt_model,
            prompt_text=prompt_text,
            rationale=self._safe_get(parsed, "rationale"),
            suggested_variables=self._ensure_list(parsed.get("suggested_variables")),
        )

    def optimize_prompt(self, request: PromptOptimizationRequest) -> PromptOptimizationResult:
        """基于旧 prompt 打补丁，返回改进版本。"""
        payload = self._build_optimization_payload(request)
        raw = self._invoke_llm(self.optimization_prompt_version, payload)
        parsed = self._parse_json(raw)
        prompt_model = self._build_prompt_model(parsed, fallback=request.prompt)
        prompt_text = generate_template(prompt_model, ["introduction", "target", "instruction"]).strip()
        score = parsed.get("score")
        normalized_score = self._coerce_float(score) if score is not None else None
        return PromptOptimizationResult(
            prompt=prompt_model,
            prompt_text=prompt_text,
            rationale=self._safe_get(parsed, "rationale"),
            change_log=self._ensure_list(parsed.get("change_log")),
            score=normalized_score,
        )

    def _invoke_llm(self, prompt_version: str, payload: dict[str, Any]) -> str:
        prompt = self._get_prompt(prompt_version)
        llm = self._resolve_llm()
        chain = prompt.as_langchain() | llm.as_langchain_runnable()
        try:
            return chain.invoke(payload)
        except Exception as exc:
            raise PromptAutoDesignerError(
                f"LLM 调用失败，prompt_version={prompt_version}, payload_keys={list(payload.keys())}"
            ) from exc

    def _resolve_llm(self) -> LLM:
        if self._llm_factory:
            llm = self._llm_factory()
        else:
            name = self.llm_name or "__default_instance__"
            llm = LLMManager().get_instance_obj(name)
        if llm is None:
            raise PromptAutoDesignerError("没有找到可用的 LLM 配置，请先在应用配置中注册默认模型。")
        if llm.component_type != ComponentEnum.LLM:
            raise PromptAutoDesignerError("llm_factory 返回的实例类型不正确。")
        return llm

    def _get_prompt(self, version: str) -> Prompt:
        prompt = PromptManager().get_instance_obj(version)
        if prompt is None:
            raise PromptAutoDesignerError(f"未注册 prompt 版本：{version}")
        return prompt.create_copy()

    def _build_generation_payload(self, request: PromptGenerationRequest) -> dict[str, str]:
        return {
            "scenario": request.scenario,
            "objective": request.objective,
            "audience": request.audience or "未指定",
            "tone": request.tone or "专业、清晰",
            "language": request.language,
            "inputs": self._format_bullets(request.inputs),
            "outputs": self._format_bullets(request.outputs),
            "constraints": self._format_bullets(request.constraints, fallback="暂无额外约束"),
            "context": request.additional_context or "无额外背景信息",
            "examples": request.examples or "暂无示例",
        }

    def _build_optimization_payload(self, request: PromptOptimizationRequest) -> dict[str, str]:
        current_prompt = generate_template(request.prompt, ["introduction", "target", "instruction"]).strip()
        return {
            "current_prompt": current_prompt or "当前提示词为空",
            "scenario": request.scenario or "未提供",
            "objective": request.objective or "未提供",
            "issues": self._format_bullets(request.issues, fallback="暂无明确问题"),
            "success_metrics": self._format_bullets(request.success_metrics, fallback="暂无成功指标"),
            "style": request.style or "保持内容准确、结构化的语气",
            "language": request.language,
            "context": request.additional_context or "无补充背景",
        }

    @staticmethod
    def _build_prompt_model(parsed: Dict[str, Any], fallback: Optional[AgentPromptModel] = None) -> AgentPromptModel:
        data = {
            "introduction": parsed.get("introduction"),
            "target": parsed.get("target"),
            "instruction": parsed.get("instruction"),
        }
        seed = AgentPromptModel(**data)
        if fallback:
            seed = seed + fallback
        if not seed:
            raise PromptAutoDesignerError("LLM 响应未提供有效的 prompt 内容。")
        return seed

    @staticmethod
    def _ensure_list(value: Any) -> List[str]:
        if value is None:
            return []
        if isinstance(value, list):
            return [str(item) for item in value]
        return [str(value)]

    @staticmethod
    def _format_bullets(values: List[str], fallback: str = "无") -> str:
        if not values:
            return fallback
        return "\n".join(f"- {value}" for value in values)

    @staticmethod
    def _coerce_float(value: Any) -> Optional[float]:
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            cleaned = re.findall(r"[-+]?[0-9]*\.?[0-9]+", value)
            if cleaned:
                return float(cleaned[0])
        return None

    @staticmethod
    def _parse_json(raw: str) -> Dict[str, Any]:
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            match = re.search(r"\{.*}", raw, flags=re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    pass
        raise PromptAutoDesignerError("LLM 响应不是有效的 JSON，请检查提示词模板或模型输出。")

    @staticmethod
    def _safe_get(payload: Dict[str, Any], key: str) -> Optional[str]:
        value = payload.get(key)
        if value is None:
            return None
        return str(value)
