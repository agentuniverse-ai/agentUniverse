from pathlib import Path


SOURCE = Path(
    "agentuniverse/llm/default/aws_bedrock_llm.py"
).read_text(encoding="utf-8")


def test_bedrock_response_parsing_handles_empty_content():
    assert "output = response.get('output')" in SOURCE
    assert "isinstance(content, list) and content" in SOURCE
    assert "text = first_content.get('text', '')" in SOURCE
