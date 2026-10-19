import importlib
import sys


def test_feishu_reader_imports_without_selenium(monkeypatch):
    """Test that feishu reader imports without selenium.
    """
    monkeypatch.setitem(sys.modules, "selenium", None)
    module = importlib.import_module(
        "agentuniverse.agent.action.knowledge.reader.cloud_file_reader."
        "feishu_reader"
    )

    assert module.PublicFeishuReader is not None
