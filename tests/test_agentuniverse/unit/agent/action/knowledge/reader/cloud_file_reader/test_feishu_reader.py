import importlib
import sys


def test_feishu_reader_imports_without_selenium(monkeypatch):
    monkeypatch.setitem(sys.modules, "selenium", None)
    module = importlib.import_module(
        "agentuniverse.agent.action.knowledge.reader.cloud_file_reader."
        "feishu_reader"
    )

    assert module.PublicFeishuReader is not None
