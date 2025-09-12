# hf_llm.py
import os, json, time
from typing import Optional, List, Any, Iterator, Union
import requests

from agentuniverse.llm.llm import LLM
from agentuniverse.llm.llm_output import LLMOutput
from agentuniverse.base.config.component_configer.configers.llm_configer import LLMConfiger
from langchain_core.language_models import BaseLanguageModel

# 如需本地 transformers，可按需引入：from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

class HuggingFaceLLM(LLM):
    model_name: Optional[str] = "hf_llm"
    repo_id: Optional[str] = None           # e.g., "meta-llama/Meta-Llama-3.1-8B-Instruct"
    inference_api_url: Optional[str] = None # e.g., f"https://api-inference.huggingface.co/models/{repo_id}"
    api_key: Optional[str] = None
    use_inference_api: bool = True          # 改为 False 可切换到本地 transformers
    streaming: bool = False                 # Inference API 原生不友好流式；如需流式，建议换 TGI

    # def _headers(self):
    #     return {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}

    def _headers(self):
        base = {"Content-Type": "application/json"}
        if self.api_key:
            base["Authorization"] = f"Bearer {self.api_key}"
        return base


    def request_data(self, prompt: str, stop: Optional[List[str]] = None):
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": self.max_tokens or 512,
                "temperature": self.temperature or 0.1,
                "return_full_text": False,
            }
        }
        # HF Inference API 不原生支持 stop list，必要时在结果侧手动截断
        return payload

    def no_streaming_call(self, prompt: str, stop: Optional[List[str]] = None, **kwargs) -> LLMOutput:
        if self.use_inference_api:
            if not self.inference_api_url:
                self.inference_api_url = f"https://api-inference.huggingface.co/models/{self.repo_id}"
            # resp = requests.post(self.inference_api_url, headers=self._headers(),
            #                      data=json.dumps(self.request_data(prompt, stop)))

            resp = requests.post(
                self.inference_api_url,
                headers=self._headers(),
                data=json.dumps(self.request_data(prompt, stop)),
                timeout=self.request_timeout or 60,
            )

            resp.raise_for_status()
            data = resp.json()
            # Inference API 返回可能是 [{"generated_text": "..."}]
            if isinstance(data, list) and data and "generated_text" in data[0]:
                text = data[0]["generated_text"]
            else:
                # 兼容 text-generation 任务的其他返回格式
                text = data.get("generated_text") or json.dumps(data, ensure_ascii=False)
            return LLMOutput(text=text, raw=data)
        else:
            # 本地 transformers 方案（示例占位）
            # pipe = pipeline("text-generation", model=self.repo_id, device_map="auto")
            # out = pipe(prompt, max_new_tokens=self.max_tokens or 512, temperature=self.temperature or 0.1)
            # text = out[0]["generated_text"]
            text = "LOCAL_TRANSFORMERS_PLACEHOLDER"
            return LLMOutput(text=text, raw={"generated_text": text})

    def streaming_call(self, prompt: str, stop: Optional[List[str]] = None, **kwargs) -> Iterator[LLMOutput]:
        # 若要真流式，建议接 TGI：/generate 或 /generate_stream SSE
        # 这里给出一个“伪流式”示例：把完整文本拆块 yield
        full = self.no_streaming_call(prompt, stop).text
        for ch in full.split():
            yield LLMOutput(text=ch + " ", raw=None)

    # def call(self, *args: Any, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
    #     return self.streaming_call(*args, **kwargs) if self.streaming else self.no_streaming_call(*args, **kwargs)
    def call(self, *args: Any, **kwargs: Any):
        stream_flag = kwargs.pop("stream", None)
        if stream_flag is None:
            stream_flag = kwargs.pop("streaming", None)
        should_stream = bool(self.streaming if stream_flag is None else stream_flag)
        return self.streaming_call(*args, **kwargs) if should_stream else self.no_streaming_call(*args, **kwargs)


    def initialize_by_component_configer(self, configer: LLMConfiger):
        ext = configer.ext_info or {}
        self.repo_id = ext.get("repo_id", self.repo_id)
        self.api_key = ext.get("api_key", self.api_key or os.getenv("HF_API_KEY"))
        self.use_inference_api = ext.get("use_inference_api", True)
        self.inference_api_url = ext.get("inference_api_url", self.inference_api_url)
        super().initialize_by_component_configer(configer)
        return self

    # def as_langchain(self) -> BaseLanguageModel:
    #     from examples.startup_app.demo_startup_app_with_single_agent.intelligence.agentic.llm.langchian_instance.langchain_instance import LangChainInstance
    #     return LangChainInstance(streaming=self.streaming, llm=self, llm_type="HF")

    def as_langchain(self) -> BaseLanguageModel:
        from examples.startup_app.demo_startup_app_with_single_agent.intelligence.agentic.llm.langchian_instance.langchain_instance import LangChainInstance
        lc = LangChainInstance(llm=self, llm_type="HF")
        lc.streaming = self.streaming
        return lc

