from pathlib import Path


SOURCE = Path(
    "agentuniverse/agent/memory/memory.py"
).read_text(encoding="utf-8")


def test_memory_does_not_index_empty_storage_configuration():
    assert "if component_configer.memory_storages is not None:" in SOURCE
    assert "if not self.memory_retrieval_storage and self.memory_storages:" in SOURCE
