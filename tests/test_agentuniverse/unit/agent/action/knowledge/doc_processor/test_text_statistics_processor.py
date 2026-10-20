# -*- coding:utf-8 -*-

import pytest

from agentuniverse.agent.action.knowledge.doc_processor.text_statistics_processor import (
    TextStatisticsProcessor,
)
from agentuniverse.agent.action.knowledge.store.document import Document


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
