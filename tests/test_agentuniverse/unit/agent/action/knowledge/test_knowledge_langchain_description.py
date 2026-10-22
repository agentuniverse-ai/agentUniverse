import asyncio

from agentuniverse.agent.action.knowledge.knowledge import Knowledge


def test_langchain_tool_description_keeps_input_guidance_with_custom_description():
    knowledge = Knowledge(
        name="test_knowledge",
        description="Custom knowledge description.",
    )

    tool = knowledge.as_langchain_tool()

    assert tool.description.startswith("Custom knowledge description.")
    assert '"query_str":' in tool.description
    assert '"similarity_top_k":' in tool.description


def test_async_langchain_tool_description_keeps_input_guidance_with_custom_description():
    knowledge = Knowledge(
        name="test_knowledge",
        description="Custom knowledge description.",
    )

    tool = asyncio.run(knowledge.async_as_langchain_tool())

    assert tool.description.startswith("Custom knowledge description.")
    assert '"query_str":' in tool.description
    assert '"similarity_top_k":' in tool.description
