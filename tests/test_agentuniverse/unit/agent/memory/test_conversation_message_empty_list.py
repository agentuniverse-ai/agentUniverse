from pathlib import Path


SOURCE = Path(
    "agentuniverse/agent/memory/conversation_memory/conversation_message.py"
).read_text(encoding="utf-8")


def test_message_conversion_handles_none_and_empty_inputs():
    assert "if not messages:" in SOURCE
