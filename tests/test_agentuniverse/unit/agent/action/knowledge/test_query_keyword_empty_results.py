from pathlib import Path


SOURCE = Path(
    "agentuniverse/agent/action/knowledge/query_paraphraser/query_keyword_extractor.py"
).read_text(encoding="utf-8")


def test_keyword_extractor_tolerates_empty_processor_results():
    assert "processed_docs = keyword_extractor_instance.process_docs(" in SOURCE
    assert "if not processed_docs:" in SOURCE
    assert "keywords = processed_docs[0].keywords or set()" in SOURCE
