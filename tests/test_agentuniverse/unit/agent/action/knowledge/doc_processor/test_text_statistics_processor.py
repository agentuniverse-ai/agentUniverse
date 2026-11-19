# -*- coding:utf-8 -*-

import pytest

from agentuniverse.agent.action.knowledge.doc_processor.text_statistics_processor import (
    TextStatisticsProcessor,
)
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer


def test_text_statistics_processor_adds_deterministic_unicode_metrics():
    document = Document(text="Hello 世界\nsecond line", metadata={"source": "test"})

    result = TextStatisticsProcessor().process_docs([document])

    assert result[0] is document
    assert result[0].text == "Hello 世界\nsecond line"
    assert result[0].metadata["source"] == "test"
    assert result[0].metadata["text_statistics"] == {
        "character_count": 20,
        "non_whitespace_count": 17,
        "line_count": 2,
        "word_count": 4,
    }


def test_text_statistics_processor_handles_empty_text_and_custom_key():
    document = Document(text="", metadata={"stats": {"old": 1}})

    TextStatisticsProcessor(metadata_key="stats", overwrite=False).process_docs([document])

    assert document.metadata["stats"] == {"old": 1}


def test_text_statistics_processor_rejects_empty_metadata_key():
    with pytest.raises(ValueError, match="metadata_key"):
        TextStatisticsProcessor(metadata_key=" ").process_docs([])


def test_text_statistics_processor_applies_yaml_configuration(tmp_path):
    config_path = tmp_path / "configured_text_statistics.yaml"
    config_path.write_text(
        """name: configured_text_statistics
description: configured processor
metadata_key: custom_stats
overwrite: false
metadata:
  type: DOC_PROCESSOR
  module: agentuniverse.agent.action.knowledge.doc_processor.text_statistics_processor
  class: TextStatisticsProcessor
""",
        encoding="utf-8",
    )

    configer = Configer(path=str(config_path)).load()
    component_configer = ComponentConfiger().load_by_configer(configer)
    processor = TextStatisticsProcessor().initialize_by_component_configer(component_configer)
    document = Document(text="new value", metadata={"custom_stats": {"old": 1}})

    processor.process_docs([document])

    assert processor.metadata_key == "custom_stats"
    assert processor.overwrite is False
    assert document.metadata["custom_stats"] == {"old": 1}
