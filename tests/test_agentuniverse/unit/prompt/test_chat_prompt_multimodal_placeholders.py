from agentuniverse.agent.memory.message import Message
from agentuniverse.prompt.chat_prompt import ChatPrompt


def test_extract_placeholders_ignores_multimodal_content_lists():
    prompt = ChatPrompt()
    prompt.messages = [
        Message(type="human", content="Describe {{topic}}."),
        Message(
            type="human",
            content=[{"type": "image_url", "image_url": {"url": "https://example.com/a.png"}}],
        ),
    ]

    assert prompt.extract_placeholders() == ["topic"]
