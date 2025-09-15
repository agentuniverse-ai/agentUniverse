# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/09/14
# @Author  : Kang-Y-F
# @FileName: insurance_google_llm.py
#
# 说明：
# - 将原先的 DashScope 调用，改为 Google Gemini（google-generativeai SDK）。
# - 与你们框架的 LLM 接口保持一致：支持 non-streaming / streaming、as_langchain()。
# - API Key 读取顺序：ext_info.api_key > 环境变量 GOOGLE_API_KEY。

import os
from typing import Any, Optional, List, Union, Iterator, Dict

import google.generativeai as genai
from agentuniverse.base.annotation.trace import trace_llm
from langchain_core.language_models import BaseLanguageModel
from agentuniverse.base.config.component_configer.configers.llm_configer import LLMConfiger
from agentuniverse.llm.llm import LLM
from agentuniverse.llm.llm_output import LLMOutput

# 你项目里的 LangChain 包装器（保持不变）
from examples.startup_app.demo_startup_app_with_single_agent.intelligence.agentic.llm.langchian_instance.langchain_instance import \
    LangChainInstance


class GoogleGeminiLLM(LLM):
    """
    使用 Google Gemini 的 LLM 适配器。
    - 非流式：使用 model.generate_content(prompt)
    - 流式：使用 model.generate_content(prompt, stream=True)，逐块 yield
    """
    api_key: Optional[str] = None
    model_name: Optional[str] = "gemini-1.5-flash"
    # 以下字段在 Google 场景无硬性要求，保留占位以兼容框架/配置
    sceneName: Optional[str] = None
    chainName: Optional[str] = None
    serviceId: Optional[str] = None
    endpoint: str = ""         # 对于 Gemini API 不需要 endpoint
    params_filed: str = "data" # 无实际用途，仅保留
    query_field: str = "query" # 无实际用途，仅保留

    # 可选：额外生成参数（从 ext_info 里传）
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    candidate_count: Optional[int] = None
    safety_settings: Optional[Dict[str, str]] = None  # 如需自定义安全策略，可在 ext_info 传入

    # ------------------------------- 公共接口 -------------------------------

    @trace_llm
    def call(self, *args: Any, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        """根据 streaming 开关走非流式或流式。"""
        if not self.streaming:
            return self.no_streaming_call(*args, **kwargs)
        else:
            return self.streaming_call(*args, **kwargs)

    def _call(self, *args: Any, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        return self.call(*args, **kwargs)

    async def _acall(self, *args: Any, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        return await self.acall(*args, **kwargs)

    def max_context_length(self) -> int:
        # Gemini 模型的上下文长度由具体版本决定。给一个安全的较大值占位（比如 1.5-pro 支持到百万级 tokens）。
        # 这里只用于你们框架的上限判断，不会限制实际请求。
        return 1_000_000

    def get_num_tokens(self, text: str) -> int:
        """使用 Gemini 的计数接口（可选）。若失败则退回 len(text)。"""
        try:
            api_key = getattr(self, "api_key", None) or os.getenv("GOOGLE_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
            model = genai.GenerativeModel(self.model_name or "gemini-1.5-flash")
            r = model.count_tokens(text)
            return int(getattr(r, "total_tokens", 0)) or len(text)
        except Exception:
            return len(text)

    # ---------------------------- 非流式调用 -----------------------------

    def no_streaming_call(self,
                          prompt: str,
                          stop: Optional[List[str]] = None,
                          model: Optional[str] = None,
                          temperature: Optional[float] = None,
                          stream: Optional[bool] = None,
                          **kwargs) -> LLMOutput:
        api_key = getattr(self, "api_key", None) or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Missing Google API key. Set ext_info.api_key or env GOOGLE_API_KEY")

        genai.configure(api_key=api_key)

        model_id = model or self.model_name or "gemini-1.5-flash"
        generation_config = {
            "temperature": (temperature if temperature is not None else self.temperature),
            "max_output_tokens": self.max_tokens,
        }
        if self.top_p is not None:
            generation_config["top_p"] = self.top_p
        if self.top_k is not None:
            generation_config["top_k"] = self.top_k
        if stop:
            generation_config["stop_sequences"] = stop
        if self.candidate_count is not None:
            generation_config["candidate_count"] = self.candidate_count

        gmodel = genai.GenerativeModel(model_id)

        # 请求
        resp = gmodel.generate_content(
            prompt,
            generation_config=generation_config,
            safety_settings=self.safety_settings,
            request_options={"timeout": self.request_timeout},
        )

        # 取文本结果
        text = getattr(resp, "text", None)
        if not text:
            # 兜底解析
            try:
                cand = resp.candidates[0]
                text = cand.content.parts[0].text
            except Exception:
                raise RuntimeError(f"Unexpected Gemini response: {repr(resp)}")

        return LLMOutput(text=text, raw=resp.to_dict() if hasattr(resp, "to_dict") else {"resp": str(resp)})

    # ----------------------------- 流式调用 ------------------------------

    def streaming_call(self,
                       prompt: str,
                       stop: Optional[List[str]] = None,
                       model: Optional[str] = None,
                       temperature: Optional[float] = None,
                       stream: Optional[bool] = None,
                       **kwargs) -> Iterator[LLMOutput]:
        api_key = getattr(self, "api_key", None) or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Missing Google API key. Set ext_info.api_key or env GOOGLE_API_KEY")

        genai.configure(api_key=api_key)

        model_id = model or self.model_name or "gemini-1.5-flash"
        generation_config = {
            "temperature": (temperature if temperature is not None else self.temperature),
            "max_output_tokens": self.max_tokens,
        }
        if self.top_p is not None:
            generation_config["top_p"] = self.top_p
        if self.top_k is not None:
            generation_config["top_k"] = self.top_k
        if stop:
            generation_config["stop_sequences"] = stop
        if self.candidate_count is not None:
            generation_config["candidate_count"] = self.candidate_count

        gmodel = genai.GenerativeModel(model_id)

        try:
            resp = gmodel.generate_content(
                prompt,
                generation_config=generation_config,
                safety_settings=self.safety_settings,
                request_options={"timeout": self.request_timeout},
                stream=True,
            )
            for chunk in resp:
                # chunk.text 为增量文本（可能为空）
                piece = getattr(chunk, "text", None)
                if piece:
                    yield LLMOutput(text=piece, raw=None)
        except Exception as e:
            raise e

    # ----------------------------- 配置注入 ------------------------------

    def set_by_agent_model(self, **kwargs) -> 'GoogleGeminiLLM':
        """从 Agent 模型（含 ext_info）注入字段，保持与原实现一致的行为。"""
        copied_obj = super().set_by_agent_model(**kwargs)
        if "ext_info" in kwargs:
            ext_info = kwargs.get("ext_info", self.ext_info) or {}
            # 支持从 ext_info 里传入 api_key 和生成参数
            if "api_key" in ext_info:
                copied_obj.api_key = ext_info.get("api_key")
            if "top_p" in ext_info:
                copied_obj.top_p = ext_info.get("top_p")
            if "top_k" in ext_info:
                copied_obj.top_k = ext_info.get("top_k")
            if "candidate_count" in ext_info:
                copied_obj.candidate_count = ext_info.get("candidate_count")
            if "safety_settings" in ext_info:
                copied_obj.safety_settings = ext_info.get("safety_settings")
        return copied_obj

    def initialize_by_component_configer(self, configer: LLMConfiger):
        """从 LLM 组件配置注入。"""
        ext_info = configer.ext_info or {}
        if "api_key" in ext_info:
            self.api_key = ext_info.get("api_key")
        if "top_p" in ext_info:
            self.top_p = ext_info.get("top_p")
        if "top_k" in ext_info:
            self.top_k = ext_info.get("top_k")
        if "candidate_count" in ext_info:
            self.candidate_count = ext_info.get("candidate_count")
        if "safety_settings" in ext_info:
            self.safety_settings = ext_info.get("safety_settings")
        super().initialize_by_component_configer(configer)
        return self

    # LangChain 适配：沿用你们项目的包装器
    def as_langchain(self) -> BaseLanguageModel:
        return LangChainInstance(streaming=self.streaming, llm=self, llm_type="Google")

