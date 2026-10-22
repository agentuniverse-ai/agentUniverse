"""Special-token spellings in source documents are ordinary content, offline."""

import pytest
import tiktoken

from agentuniverse.agent.action.knowledge.doc_processor import context_budget_compressor as cbc
from agentuniverse.agent.action.knowledge.store.document import Document


@pytest.fixture
def encoder(monkeypatch):
    """Use real BPE with a local byte vocabulary; no network or API calls."""
    encoding = tiktoken.Encoding(
        name="literal-token-regression", pat_str=r"(?s).+",
        mergeable_ranks={bytes([i]): i for i in range(256)},
        special_tokens={"<|endoftext|>": 256, "<|fim_prefix|>": 257})
    monkeypatch.setitem(cbc._TIKTOKEN_ENCODERS, encoding.name, encoding)
    return encoding


def processor(encoder, **kwargs):
    """Build the actual processor using the offline test encoding."""
    return cbc.ContextBudgetCompressor(
        counter="tiktoken", tiktoken_encoding=encoder.name, **kwargs)


@pytest.mark.parametrize("text", ["<|endoftext|>", "x<|fim_prefix|>y",
                                  "<|endoftext|><|fim_prefix|>"])
def test_counts_spelling_as_ordinary_tokens_not_control_ids(encoder, text):
    """Allowing a special token as one control ID would undercount document text."""
    count = processor(encoder)._count(text)
    assert count == len(encoder.encode_ordinary(text)) == len(text.encode())
    assert count > len(encoder.encode(text, allowed_special="all"))


@pytest.mark.parametrize("text", ["<|endoftext|> trailing", "a<|fim_prefix|>z",
                                  "中<|endoftext|>🙂abc", "ordinary plain text"])
@pytest.mark.parametrize("budget", [1, 5, 20, 100])
def test_public_processing_preserves_prefix_and_budget(encoder, text, budget):
    """Counting, truncating and checking a prefix must use the same policy."""
    original = Document(id="source", text=text, metadata={"source": "manual"})
    result = processor(encoder, budget=budget).process_docs([original])
    prefix = "".join(doc.text for doc in result)
    assert text.startswith(prefix)
    assert "\ufffd" not in prefix
    assert sum(len(encoder.encode_ordinary(doc.text)) for doc in result) <= budget
    if result:
        assert result[0].id == "source"
        assert result[0].metadata["source"] == "manual"
        if prefix != text:
            assert result[0].metadata["truncated"] is True
        else:
            assert result[0] is original
    assert original.text == text
    assert original.metadata == {"source": "manual"}


def test_whole_marker_prefix_is_recounted_without_raising(encoder):
    """The retained prefix may itself contain a complete special spelling."""
    marker = "<|endoftext|>"
    result = processor(encoder, budget=len(marker)).process_docs(
        [Document(text=marker + " trailing")])
    assert result[0].text == marker
    assert processor(encoder)._count(result[0].text) == len(marker)


def test_remaining_budget_after_an_earlier_document(encoder):
    """The boundary document receives only the unspent ordinary-token budget."""
    first = Document(text="abc")
    result = processor(encoder, budget=8).process_docs(
        [first, Document(text="<|endoftext|> trailing")])
    assert result[0] is first
    assert [doc.text for doc in result] == ["abc", "<|end"]
    assert sum(len(encoder.encode_ordinary(doc.text)) for doc in result) == 8


def test_truncation_disabled_stops_without_rejecting_literal_content(encoder):
    """An oversized literal-bearing document is omitted, not a tokenizer error."""
    assert processor(encoder, budget=2, truncate=False).process_docs(
        [Document(text="<|endoftext|>")]) == []


@pytest.mark.parametrize("counter", ["char", "word", "estimate"])
def test_other_counters_keep_literal_text(counter):
    """Non-token counters and the existing whole-document path stay unchanged."""
    original = Document(text="<|endoftext|>")
    assert cbc.ContextBudgetCompressor(counter=counter, budget=100).process_docs(
        [original]) == [original]
