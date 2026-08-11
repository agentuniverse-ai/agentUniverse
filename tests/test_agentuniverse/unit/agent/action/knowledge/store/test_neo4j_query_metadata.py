from pathlib import Path


SOURCE = Path(
    "agentuniverse/agent/action/knowledge/store/neo4j_store.py"
).read_text(encoding="utf-8")


def test_neo4j_query_normalizes_missing_metadata():
    assert "if query is None:" in SOURCE
    assert "query_ext_info = query.ext_info if isinstance(query.ext_info, dict) else {}" in SOURCE
    assert SOURCE.count("query_ext_info.get") >= 4
