# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/5/14 14:41
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: chat_prompt.py
import base64
from typing import List, Optional
import re
from urllib.parse import urlparse

from langchain_core.prompts import ChatPromptTemplate

from agentuniverse.agent.memory.enum import ChatMessageEnum
from agentuniverse.agent.memory.message import Message
from agentuniverse.base.util.prompt_util import generate_chat_template
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

    def as_langchain(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages(Message.as_langchain_list(self.messages))

    def build_prompt(self, agent_prompt_model: AgentPromptModel, prompt_assemble_order: list[str]) -> "ChatPrompt":
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
        placeholder_pattern = re.compile(r"\{(.*?)}")
        for message in self.messages:
            matches = placeholder_pattern.findall(message.content)
            result.extend(matches)
        return result

    def generate_image_prompt(self, image_urls: list[str]) -> None:
        """Generate the prompt with image urls.

        Args:
            image_urls (list[str]): The image urls.
        """
        if image_urls:
            for image_url in image_urls:
                if isinstance(image_url, dict) and "url" in image_url:
                    content = [{"type": "image_url", "image_url": image_url}]
                    self.messages.append(Message(type=ChatMessageEnum.HUMAN.value, content=content))
                    continue
                parsed_url = urlparse(image_url)
                # Check if the URL is a valid HTTP or HTTPS URL.
                if parsed_url.scheme in ["http", "https"]:
                    content = [{"type": "image_url", "image_url": {"url": image_url}}]
                    self.messages.append(Message(type=ChatMessageEnum.HUMAN.value, content=content))
                # Check if the URL is a local file.
                elif parsed_url.scheme == "file" or not parsed_url.scheme:
                    if parsed_url.path.lower().endswith(image_extensions):
                        with open(parsed_url.path, "rb") as image_file:
                            base64_image = base64.b64encode(image_file.read()).decode(
                                "utf-8",
                            )
                            extension = parsed_url.path.lower().split(".")[-1]
                            mime_type = f"image/{extension}"
                            content = [
                                {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{base64_image}"}}
                            ]
                            self.messages.append(Message(type=ChatMessageEnum.HUMAN.value, content=content))

    def generate_audio_prompt(self, audio_url: str) -> None:
        """Generate the prompt with audio url.

        Args:
            audio_url (str): The audio url.
        """
        if audio_url:
            parsed_url = urlparse(audio_url)
            # Check if the URL is a valid HTTP or HTTPS URL.
            if parsed_url.scheme in ["http", "https"]:
                content = [{"type": "input_audio", "input_audio": {"data": audio_url}}]
                self.messages.append(Message(type=ChatMessageEnum.HUMAN.value, content=content))
