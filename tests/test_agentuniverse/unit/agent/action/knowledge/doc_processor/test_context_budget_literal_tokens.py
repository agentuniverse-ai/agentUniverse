"""Literal tokenizer markers in retrieved documents remain ordinary text."""

from unittest.mock import patch

import pytest
import tiktoken

from agentuniverse.agent.action.knowledge.doc_processor import context_budget_compressor as cbc
from agentuniverse.agent.action.knowledge.store.document import Document


@pytest.fixture
def encoder():
    # Use a real tokenizer without downloading a vocabulary during the test.
    return tiktoken.Encoding(
        name="literal-marker-test",
        pat_str=r"[\s\S]",
        mergeable_ranks={bytes([i]): i for i in range(256)},
        special_tokens={"<|endoftext|>": 256, "<|fim_prefix|>": 257},
    )


@pytest.mark.parametrize("marker", ["<|endoftext|>", "<|fim_prefix|>"])
def test_counts_literal_markers_as_text(encoder, marker):
    text = f"Token example: {marker}"
    processor = cbc.ContextBudgetCompressor(counter="tiktoken", budget=100)
    original = Document(text=text)
    with patch.object(cbc, "_tiktoken_encoder", return_value=encoder):
        assert processor._count(text) == len(text)
        assert processor.process_docs([original]) == [original]


def test_truncates_document_containing_literal_marker(encoder):
    text = "Example: <|endoftext|> followed by more text"
    processor = cbc.ContextBudgetCompressor(counter="tiktoken", budget=23)
    original = Document(text=text, metadata={"source": "tokenizer.md"})
    with patch.object(cbc, "_tiktoken_encoder", return_value=encoder):
        result = processor.process_docs([original])
        assert result[0].text == text[:23]
        assert processor._count(result[0].text) <= processor.budget
    assert result[0].id == original.id
    assert result[0].metadata == {"source": "tokenizer.md", "truncated": True}
    assert original.text == text


def test_keeps_plain_text_counting(encoder):
    processor = cbc.ContextBudgetCompressor(counter="tiktoken", budget=5)
    with patch.object(cbc, "_tiktoken_encoder", return_value=encoder):
        result = processor.process_docs([Document(text="ordinary text")])
    assert result[0].text == "ordin"
