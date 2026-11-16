from pathlib import Path


SOURCE = Path(
    "agentuniverse/agent/action/knowledge/doc_processor/hierarchical_regex_text_splitter.py"
).read_text(encoding="utf-8")


def test_hierarchical_splitter_returns_for_empty_input():
    assert "if not origin_docs:" in SOURCE
    assert "return []" in SOURCE
