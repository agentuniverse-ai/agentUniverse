# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/12 11:43
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: dashscope_embedding.py
import aiohttp
import requests
from typing import List, Generator, Optional
from pydantic import Field
import json

from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.agent.action.knowledge.embedding.embedding import Embedding

# Dashscope support max 25 string in one batch, each string max tokens is 2048.
DASHSCOPE_MAX_BATCH_SIZE = 25
DASHSCOPE_EMBEDDING_URL = "https://dashscope.aliyuncs.com/api/v1/services/embeddings/text-embedding/text-embedding"


def batched(inputs: List,
            batch_size: int = DASHSCOPE_MAX_BATCH_SIZE) -> Generator[List, None, None]:
    # Split input string list, due to dashscope support 25 strings in one call.
    for i in range(0, len(inputs), batch_size):
        yield inputs[i:i + batch_size]


class DashscopeEmbedding(Embedding):
    """The Dashscope embedding class."""
    dashscope_api_key: Optional[str] = Field(
        default_factory=lambda: get_from_env("DASHSCOPE_API_KEY")
    )

    def get_embeddings(self, texts: List[str], **kwargs) -> List[List[float]]:
        """
        Retrieve text embeddings for a list of input texts.

        This function interfaces with the DashScope embedding API to obtain
        embeddings for a batch of input texts. It handles batching of input texts
        to ensure efficient API calls. Each text is processed using the specified
        embedding model.

        Args:
            texts (List[str]): A list of input texts to be embedded.

        Returns:
            List[List[float]]: A list of embeddings corresponding to the input texts.

        Raises:
            Exception: If the API call to DashScope fails, an exception is raised with
                       the respective error code and message.
        """
        def post(post_params):
            response = requests.post(
                url=DASHSCOPE_EMBEDDING_URL,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.dashscope_api_key}"
                },
                data=json.dumps(post_params, ensure_ascii=False).encode(
                    "utf-8"),
                timeout=300
            )
            resp_json = response.json()
            return resp_json
        if not self.dashscope_api_key:
            raise Exception("No DASHSCOPE_API_KEY in your environment.")
        result = []
        post_params = {
            "model": self.embedding_model_name,
            "input": {},
            "parameters": {
            }
        }
        if self.embedding_model_name == "text-embedding-v3":
            post_params["parameters"][
                "dimension"] = self.embedding_dims if self.embedding_dims else 1024
            post_params["parameters"][
                "output_type"] = kwargs["output_type"] if "output_type" in kwargs else "dense"
        post_params["parameters"]["text_type"] = kwargs["text_type"] if "text_type" in kwargs else "document"

        for batch in batched(texts):
            post_params["input"]["texts"] = batch
            resp_json: dict = post(post_params)
            data = resp_json.get("output")
            if data:
                data = data["embeddings"]
                batch_result = [d['embedding'] for d in data if 'embedding' in d]
                result += batch_result
            else:
                error_code = resp_json.get("code", "")
                error_message = resp_json.get("message", "")
                raise Exception(f"Failed to call dashscope embedding api, "
                                f"error code:{error_code}, "
                                f"error message:{error_message}")
        return result

    async def async_get_embeddings(self, texts: List[str], **kwargs) -> List[List[float]]:
        """
        Async version of get_embeddings.

        This function interfaces with the DashScope embedding API to obtain
        embeddings for a batch of input texts. It handles batching of input texts
        to ensure efficient API calls. Each text is processed using the specified
        embedding model.

        Args:
            texts (List[str]): A list of input texts to be embedded.

        Returns:
            List[List[float]]: A list of embeddings corresponding to the input texts.

        Raises:
            Exception: If the API call to DashScope fails, an exception is raised with
                       the respective error code and message.
        """
        async def async_post(post_params):
            async with aiohttp.ClientSession() as session:
                async with await session.post(
                        url=DASHSCOPE_EMBEDDING_URL,
                        headers={
                            "Content-Type": "application/json",
                            "Authorization": f"Bearer {self.dashscope_api_key}"
                        },
                        data=json.dumps(post_params, ensure_ascii=False).encode(
                            "utf-8"),
                        timeout=300,
                ) as resp:
                    resp_json = await resp.json()
            return resp_json
        if not self.dashscope_api_key:
            raise Exception("No DASHSCOPE_API_KEY in your environment.")
        result = []
        post_params = {
            "model": self.embedding_model_name,
            "input": {},
            "parameters": {
                "text_type": "query"
            }
        }
        if self.embedding_model_name == "text-embedding-v3":
            post_params["parameters"][
                "dimension"] = self.embedding_dims if self.embedding_dims else 1024
            post_params["parameters"][
                "output_type"] = kwargs[
                "output_type"] if "output_type" in kwargs else "dense"
        post_params["parameters"]["text_type"] = kwargs[
            "text_type"] if "text_type" in kwargs else "document"

        for batch in batched(texts):
            post_params["input"]["texts"] = batch
            resp_json: dict = await async_post(post_params)
            data = resp_json.get("output")
            if data:
                data = data["embeddings"]
                batch_result = [d['embedding'] for d in data if
                                'embedding' in d]
                result += batch_result
            else:
                error_code = resp_json.get("code", "")
                error_message = resp_json.get("message", "")
                raise Exception(f"Failed to call dashscope embedding api, "
                                f"error code:{error_code}, "
                                f"error message:{error_message}")
        return result