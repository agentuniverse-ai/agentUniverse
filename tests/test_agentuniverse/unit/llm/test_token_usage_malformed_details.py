from pathlib import Path


def test_openai_usage_ignores_non_mapping_detail_blocks():
    source = Path("agentuniverse/llm/llm_output.py").read_text(encoding="utf-8")

    assert source.count("det_in = det_in if isinstance(det_in, dict) else {}") == 2
    assert source.count("det_out = det_out if isinstance(det_out, dict) else {}") == 2
