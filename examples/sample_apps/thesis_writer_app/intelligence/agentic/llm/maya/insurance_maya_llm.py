# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/25 16:39
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: insurance_maya_llm.py
import json
from typing import Any, Optional, List, Union, Iterator

import tiktoken
from agentuniverse.base.annotation.trace import trace_llm
from langchain_core.language_models import BaseLanguageModel
from agentuniverse.base.config.component_configer.configers.llm_configer import LLMConfiger
from agentuniverse.llm.llm import LLM
from agentuniverse.llm.llm_output import LLMOutput

from examples.startup_app.demo_startup_app_with_single_agent.intelligence.agentic.llm.langchian_instance.langchain_instance import \
    LangChainInstance


class InsuranceMayaLLM(LLM):
    """
    InsuranceMayaLLM是一个企业内部私有模型连接示例，通过配置sceneName（模型场景码）/ chainName（模型版本号）/ serviceId（模型服务ID）/ endpoint（模型url）等信息，联通私有模型服务。

    模型入参包括prompt/stop/temperature等信息；
    模型出参：
        1. 非流式：json格式，样例为
            {"success": True, "result": {
                "output_string": "This is the llm mock response."
            }}

        2. 流式：iterator，样例为
        [
            {"out_string": "This "},
            {"out_string": "is "},
            {"out_string": "the "},
            {"out_string": "llm "},
            {"out_string": "mock "},
            {"out_string": "response"},
            {"out_string": "."}
        ]
    """
    model_name: Optional[str] = "insurance_maya_llm"
    sceneName: Optional[str] = None
    chainName: Optional[str] = None
    serviceId: Optional[str] = None
    endpoint: str = "xxx"
    params_filed: str = "data"
    query_field: str = "query"

    @trace_llm
    def call(self, *args: Any, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        """
        Call the model on the inputs.
        """
        # 非流式调用
        if not self.streaming:
            return self.no_streaming_call(*args, **kwargs)
        # 流式调用
        else:
            return self.streaming_call(*args, **kwargs)

    @staticmethod
    def parse_output(result: dict) -> LLMOutput:
        """
        Parse the output of the model.
        """
        if "result" in result:
            text = result["result"]["output_string"]
        else:
            raise ValueError("No output found in response.")
        return LLMOutput(text=text, raw=result)

    @staticmethod
    def parse_stream_output(line: str) -> Union[None, LLMOutput]:
        """
        Parse the output of the model.
        """
        if not line:
            return None
        line = json.loads(line)
        return LLMOutput(text=line["out_string"], raw=line)

    def _call(self, *args: Any, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        return self.call(*args, **kwargs)

    async def _acall(self, *args: Any, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        return await self.acall(*args, **kwargs)

    def max_context_length(self) -> int:
        """Max context length.

          The total length of input tokens and generated tokens is limited by the openai model's context length.
          """
        return 128000

    def get_num_tokens(self, text: str) -> int:
        """Get the number of tokens present in the text.

        Useful for checking if an input will fit in an openai model's context window.

        Args:
            text: The string input to tokenize.

        Returns:
            The integer number of tokens in the text.
        """

        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))

    def request_stream_data(self, prompt: str, stop: str = ''):
        return {
            "sceneName": self.sceneName,
            "chainName": self.chainName,
            "serviceId": self.serviceId,
            "features": {self.params_filed: json.dumps({self.query_field: prompt, "sync": False}),
                         "temperature": self.temperature,
                         "stop_words": stop,
                         "max_output_length": self.max_tokens},
        }

    def request_data(self, prompt: str, stop: str = None):
        return {
            "sceneName": self.sceneName,
            "chainName": self.chainName,
            "serviceId": self.serviceId,
            "features": {self.params_filed: json.dumps({self.query_field: prompt, "sync": False}),
                         "temperature": self.temperature,
                         "stop_words": stop,
                         "max_output_length": self.max_tokens},
        }

    def no_streaming_call(self,
                          prompt: str,
                          stop: Optional[List[str]] = None,
                          model: Optional[str] = None,
                          temperature: Optional[float] = None,
                          stream: Optional[bool] = None,
                          **kwargs) -> LLMOutput:
        suffix = f"?model_name={self.model_name}"
        # 进行模型http调用
        # resp = requests.post(
        #     url=self.endpoint + suffix,
        #     headers={"Content-Type": "application/json"},
        #     data=json.dumps(self.request_data(prompt, stop[0] if stop else ''), ensure_ascii=False).encode("utf-8"),
        #     timeout=self.request_timeout,
        # )
        # resp = resp.json()
        resp = {"success": True, "result": {
            "output_string": "This is the llm mock response."
        }}
        try:
            if resp and resp["success"]:
                return self.parse_output(resp)
            else:
                raise Exception(resp)
        except Exception as e:
            raise e

    def streaming_call(self,
                       prompt: str,
                       stop: Optional[List[str]] = None,
                       model: Optional[str] = None,
                       temperature: Optional[float] = None,
                       stream: Optional[bool] = None,
                       **kwargs):
        suffix = f"?model_name={self.model_name}"
        # 进行模型http调用
        # with requests.post(
        #         url=self.endpoint + suffix,
        #         data=json.dumps(self.request_stream_data(prompt, stop[0] if stop else ''), ensure_ascii=False).encode(
        #             "utf-8"),
        #         timeout=self.request_timeout,
        #         headers={"Content-Type": "application/json"},
        #         stream=True
        # ) as resp:

        resp = [
            json.dumps({"out_string": "This "}),
            json.dumps({"out_string": "is "}),
            json.dumps({"out_string": "the "}),
            json.dumps({"out_string": "llm "}),
            json.dumps({"out_string": "mock "}),
            json.dumps({"out_string": "response"}),
            json.dumps({"out_string": "."})
        ]
        for line in resp:
            output = self.parse_stream_output(line)
            if output:
                yield output

    def set_by_agent_model(self, **kwargs) -> 'InsuranceMayaLLM':
        copied_obj = super().set_by_agent_model(**kwargs)
        if "ext_info" in kwargs:
            ext_info = kwargs.get("ext_info", self.ext_info)
            if "sceneName" in ext_info:
                copied_obj.sceneName = ext_info.get("sceneName", self.sceneName)
            if "chainName" in ext_info:
                copied_obj.chainName = ext_info.get("chainName", self.chainName)
            if "serviceId" in ext_info:
                copied_obj.serviceId = ext_info.get("serviceId", self.serviceId)
            if "endpoint" in ext_info:
                copied_obj.endpoint = ext_info.get("endpoint", self.endpoint)
            if "params_filed" in ext_info:
                copied_obj.params_filed = ext_info.get("params_filed", self.params_filed)
            if "query_field" in ext_info:
                copied_obj.query_field = ext_info.get("query_field", self.query_field)
        return copied_obj

    def initialize_by_component_configer(self, configer: LLMConfiger):
        """Initialize the agent model by component configer."""
        ext_info = configer.ext_info
        if not ext_info:
            return super().initialize_by_component_configer(configer)
        if "sceneName" in ext_info:
            self.sceneName = ext_info["sceneName"]
        if "chainName" in ext_info:
            self.chainName = ext_info["chainName"]
        if "serviceId" in ext_info:
            self.serviceId = ext_info["serviceId"]
        if "endpoint" in ext_info:
            self.endpoint = ext_info["endpoint"]
        if "params_filed" in ext_info:
            self.params_filed = ext_info["params_filed"]
        if "query_field" in ext_info:
            self.query_field = ext_info["query_field"]
        super().initialize_by_component_configer(configer)
        return self

    def as_langchain(self) -> BaseLanguageModel:
        """Convert the agentUniverse(aU) openai llm class to the langchain openai llm class."""
        return LangChainInstance(streaming=self.streaming, llm=self, llm_type="Maya")
