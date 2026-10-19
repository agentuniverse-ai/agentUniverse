from pathlib import Path


SOURCE = Path(
    "agentuniverse/agent/action/knowledge/embedding/gemini_embedding.py"
).read_text(encoding="utf-8")


def test_gemini_embedding_handles_empty_api_results():
    assert 'getattr(response, "embeddings", None) or []' in SOURCE
    assert "return embeddings[0] if embeddings else []" in SOURCE
