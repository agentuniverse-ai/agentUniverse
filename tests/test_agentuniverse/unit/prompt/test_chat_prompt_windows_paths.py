"""Windows drive-qualified image paths must reach the multimodal prompt."""

import base64
import os
from unittest.mock import mock_open, patch

import pytest

from agentuniverse.agent.agent_model import AgentModel
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.template.rag_agent_template import RagAgentTemplate
from agentuniverse.prompt.chat_prompt import ChatPrompt

PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aWQAAAABJRU5ErkJggg==")


@pytest.mark.parametrize(
    ("image_path", "mime_type"),
    [
        (r"C:\images\plain.png", "image/png"),
        ("D:/images/two words.png", "image/png"),
        (r"c:relative#1%20.png", "image/png"),
        (r"C:\images\图表 #1%20.PNG", "image/png"),
        ("D:/images/photo.JPG", "image/jpeg"),
    ],
)
def test_drive_qualified_image_paths_preserve_literal_characters(image_path, mime_type):
    image_file = mock_open(read_data=PNG)
    prompt = ChatPrompt()

    with patch("agentuniverse.prompt.chat_prompt.open", image_file, create=True):
        prompt.generate_image_prompt([image_path])

    image_file.assert_called_once_with(image_path, "rb")
    assert len(prompt.messages) == 1
    image_url = prompt.messages[0].content[0]["image_url"]["url"]
    prefix, encoded_image = image_url.split(",", 1)
    assert prefix == f"data:{mime_type};base64"
    assert base64.b64decode(encoded_image) == PNG


@pytest.mark.parametrize(
    "image_url",
    ["data:image/png;base64,aGVsbG8=", "s3://example-bucket/chart.png"],
)
def test_other_url_schemes_are_not_opened_as_local_files(image_url):
    image_file = mock_open(read_data=PNG)
    prompt = ChatPrompt()

    with patch("agentuniverse.prompt.chat_prompt.open", image_file, create=True):
        prompt.generate_image_prompt([image_url])

    image_file.assert_not_called()
    assert prompt.messages == []


@pytest.mark.skipif(os.name != "nt", reason="Requires a native Windows absolute image path")
def test_agent_prompt_includes_native_windows_image_path(tmp_path):
    image_path = tmp_path / "图表 #1%20.png"
    image_path.write_bytes(PNG)
    agent = RagAgentTemplate()
    agent.agent_model = AgentModel(
        info={"name": "windows-image-agent"},
        profile={"instruction": "Describe {input}"},
    )
    agent_input = agent.pre_parse_input(InputObject({"input": "the attached image", "image_urls": [str(image_path)]}))

    with patch("agentuniverse.agent.agent.PromptManager") as prompt_manager:
        prompt_manager.return_value.get_instance_obj.return_value = None
        prompt = agent.process_prompt(agent_input)

    messages = prompt.as_langchain().format_messages(input="the attached image")
    assert messages[0].content == "Describe the attached image"
    assert len(messages) == 2
    image_url = messages[1].content[0]["image_url"]["url"]
    prefix, encoded_image = image_url.split(",", 1)
    assert prefix == "data:image/png;base64"
    assert base64.b64decode(encoded_image) == PNG
