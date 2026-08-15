import sys
import types

from langchain_core.messages import HumanMessage, SystemMessage

anthropic_module = types.ModuleType("langchain_anthropic")
anthropic_chat_models = types.ModuleType("langchain_anthropic.chat_models")

class ChatAnthropic:
    pass

anthropic_module.ChatAnthropic = ChatAnthropic
anthropic_chat_models._tools_in_params = lambda params: False
sys.modules.setdefault("langchain_anthropic", anthropic_module)
sys.modules.setdefault("langchain_anthropic.chat_models", anthropic_chat_models)

from agentuniverse.llm.claude_langchain_instance import ClaudeLangChainInstance


def test_claude_message_normalization_does_not_mutate_input_list():
    system = SystemMessage(content="rules")
    messages = [HumanMessage(content="hello"), system]

    normalized = ClaudeLangChainInstance._normalize_messages(messages)

    assert messages[1] is system
    assert isinstance(messages[1], SystemMessage)
    assert isinstance(normalized[1], HumanMessage)
    assert normalized is not messages
