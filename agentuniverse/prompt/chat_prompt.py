# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/5/14 14:41
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: chat_prompt.py
import base64
import re
from typing import List
from urllib.parse import urlparse

from agentuniverse.agent.memory.enum import ChatMessageEnum
from agentuniverse.agent.memory.message import Message
from agentuniverse.base.util.prompt_util import generate_chat_template, \
    render_content
from agentuniverse.prompt.prompt import Prompt
from agentuniverse.prompt.prompt_model import AgentPromptModel

image_extensions = (
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
)


class ChatPrompt(Prompt):
    messages: List[Message] = []

    def build_prompt(self, agent_prompt_model: AgentPromptModel, prompt_assemble_order: list[str]) -> 'ChatPrompt':
        """Build the prompt class.

        Args:
            agent_prompt_model (AgentPromptModel): The user agent prompt model.
            prompt_assemble_order (list[str]): The prompt assemble ordered list.

        Returns:
            ChatPrompt: The chat prompt object.
        """
        self.messages = generate_chat_template(agent_prompt_model, prompt_assemble_order)
        self.input_variables = self.extract_placeholders()
        return self

    def extract_placeholders(self) -> List[str]:
        """Extract the placeholders from the messages.

        Returns:
            List[str]: The placeholders list.
        """
        result = []
        placeholder_pattern = re.compile(r'\{(.*?)}')
        for message in self.messages:
            content = message.content
            if content is None:
                continue

            if isinstance(content, str):
                result.extend(placeholder_pattern.findall(content))
            elif isinstance(content, list):
                # ContentT 的 list 分支: 每个元素可能是 str 或 dict
                for item in content:
                    if isinstance(item, str):
                        result.extend(placeholder_pattern.findall(item))
                    elif isinstance(item, dict):
                        # 只从 "text" 类型的 dict 项中提取占位符
                        text = item.get("text", "")
                        if text:
                            result.extend(placeholder_pattern.findall(text))

        # 保持顺序去重
        seen = set()
        deduped = []
        for name in result:
            if name not in seen:
                seen.add(name)
                deduped.append(name)
        return deduped

    def render(self, **kwargs) -> List[Message]:
        rendered_messages: List[Message] = []
        for message in self.messages:
            new_msg = message.model_copy(deep=True)
            new_msg.content = render_content(new_msg.content, kwargs)
            rendered_messages.append(new_msg)
        return rendered_messages

    def generate_image_prompt(self, image_urls: list[str]) -> None:
        """ Generate the prompt with image urls.

        Args:
            image_urls (list[str]): The image urls.
        """
        if not image_urls:
            return

        for image_url in image_urls:
            # 已经是带 url key 的 dict（如 {"url": "...", "detail": "high"}）
            if isinstance(image_url, dict) and "url" in image_url:
                content = [{"type": "image_url", "image_url": image_url}]
                self.messages.append(
                    Message(type=ChatMessageEnum.HUMAN, content=content)
                )
                continue

            parsed_url = urlparse(image_url)

            if parsed_url.scheme in ("http", "https"):
                content = [
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
                self.messages.append(
                    Message(type=ChatMessageEnum.HUMAN, content=content)
                )

            elif parsed_url.scheme == "file" or not parsed_url.scheme:
                if parsed_url.path.lower().endswith(image_extensions):
                    with open(parsed_url.path, "rb") as image_file:
                        base64_image = base64.b64encode(
                            image_file.read()
                        ).decode("utf-8")
                        extension = parsed_url.path.lower().split(".")[-1]
                        mime_type = f"image/{extension}"
                        content = [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{base64_image}"
                                },
                            }
                        ]
                        self.messages.append(
                            Message(type=ChatMessageEnum.HUMAN,
                                    content=content)
                        )

    def generate_audio_prompt(self, audio_url: str) -> None:
        """ Generate the prompt with audio url.

        Args:
            audio_url (str): The audio url.
        """
        if not audio_url:
            return

        parsed_url = urlparse(audio_url)
        if parsed_url.scheme in ("http", "https"):
            content = [
                {"type": "input_audio", "input_audio": {"data": audio_url}}
            ]
            self.messages.append(
                Message(type=ChatMessageEnum.HUMAN, content=content)
            )
