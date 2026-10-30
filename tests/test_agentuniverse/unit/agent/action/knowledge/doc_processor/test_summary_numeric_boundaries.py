"""Extractive summaries must not split the digits of decimal facts."""

import pytest
from unittest.mock import Mock, patch

from agentuniverse.agent.action.knowledge.doc_processor.summarization_processor import SummarizationProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query


@pytest.mark.parametrize("number", ["3.14", "0.05", "-12.5", "+2.75", "1,234.56", "1.2.3"])
def test_numeric_dots_remain_inside_the_sentence(number):
    text = f"Measured value is {number}. Other results differ!"
    assert SummarizationProcessor._split_sentences(text) == [f"Measured value is {number}", "Other results differ"]


@pytest.mark.parametrize("punctuation", [".", "!", "?", "。", "！", "？", "…", "\n"])
def test_terminal_punctuation_still_splits(punctuation):
    assert SummarizationProcessor._split_sentences(f"First claim{punctuation}Second claim") == [
        "First claim",
        "Second claim",
    ]


def test_query_aware_summary_preserves_full_numeric_fact():
    result = SummarizationProcessor(max_sentences=1).process_docs(
        [
            Document(
                text="The measured accuracy is 98.75 percent. A different topic follows. Another unrelated sentence."
            )
        ],
        Query(query_str="accuracy"),
    )
    assert result[0].text == "The measured accuracy is 98.75 percent"


def test_short_text_passthrough_preserves_original_punctuation():
    text = "The value is 3.14."
    assert SummarizationProcessor(max_sentences=5).process_docs([Document(text=text)])[0].text == text


@pytest.mark.parametrize(
    "text,expected",
    [
        ("准确率为98.75%。召回率为92.50%！", ["准确率为98.75%", "召回率为92.50%"]),
        ("Value 3.14... Another claim.", ["Value 3.14", "Another claim"]),
        ("Value 3.14.\r\nOther 0.05.", ["Value 3.14", "Other 0.05"]),
        ("0.5", ["0.5"]),
        ("Count 12. Next count 34.", ["Count 12", "Next count 34"]),
    ],
)
def test_numeric_facts_with_multilingual_and_repeated_boundaries(text, expected):
    assert SummarizationProcessor._split_sentences(text) == expected


def test_summary_keeps_source_metadata_and_does_not_mutate_inputs():
    docs = [
        Document(text="Accuracy is 98.75 percent.", metadata={"source": "first"}),
        Document(text="Unrelated sentence. More unrelated information.", metadata={"source": "second"}),
    ]
    texts = [doc.text for doc in docs]
    summary = SummarizationProcessor(max_sentences=1).process_docs(docs, Query(query_str="accuracy"))[0]
    assert summary.text == "Accuracy is 98.75 percent"
    assert summary.metadata["source"] == "first"
    assert summary.metadata["source_doc_count"] == 2
    assert summary.metadata["summarization_mode"] == "extractive"
    assert [doc.text for doc in docs] == texts


def test_llm_mode_receives_original_decimal_text_without_sentence_splitting():
    processor = SummarizationProcessor(llm_name="fixture")
    llm = Mock()
    llm.call.return_value = Mock(text="Model summary.")
    text = "Accuracy is 98.75%. Another fact."
    with (
        patch.object(processor, "_get_llm", return_value=llm),
        patch.object(processor, "_split_sentences", side_effect=AssertionError("not extractive mode")),
    ):
        result = processor.process_docs([Document(text=text)])
    assert result[0].text == "Model summary."
    assert text in llm.call.call_args.kwargs["messages"][-1]["content"]
