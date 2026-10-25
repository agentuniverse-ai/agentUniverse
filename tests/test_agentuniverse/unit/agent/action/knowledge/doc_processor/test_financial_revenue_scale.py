"""Amount-before-revenue extraction must retain the monetary scale."""

import pytest

from agentuniverse.agent.action.knowledge.doc_processor.financial_indicator_extractor import (
    FinancialIndicatorExtractor,
)
from agentuniverse.agent.action.knowledge.store.document import Document


@pytest.mark.parametrize(
    "text, expected",
    [
        ("$3 million in revenue", 3_000_000),
        ("$3 billion revenue", 3_000_000_000),
        ("$3M in revenue", 3_000_000),
        ("$3B revenue", 3_000_000_000),
        ("$1,250.5 million in revenue", 1_250_500_000),
        ("$-2.5 billion in revenue", -2_500_000_000),
        ("$3 MILLION IN REVENUE", 3_000_000),
        ("$3b revenue", 3_000_000_000),
        ("€3 million in revenue", 3_000_000),
        ("revenue of $3 million", 3_000_000),
        ("revenue of $3 billion", 3_000_000_000),
        ("revenue of $3", 3),
        ("revenue of $0 million", 0),
    ],
)
def test_revenue_value_includes_scale(text, expected):
    processor = FinancialIndicatorExtractor(
        metrics=["revenue"], extract_temporal=False,
        extract_comparisons=False, currency_normalization=False,
    )
    source = Document(text=text, metadata={"source": "regression"})

    result = processor.process_docs([source])

    assert len(result) == 1
    metrics = result[0].metadata["financial_metrics"]["revenue"]
    assert len(metrics) == 1
    assert metrics[0]["value"] == expected
    assert result[0].id == source.id
    assert result[0].text == text
    assert result[0].metadata["source"] == "regression"
    assert source.metadata == {"source": "regression"}


def test_no_amount_does_not_invent_revenue():
    processor = FinancialIndicatorExtractor(metrics=["revenue"])
    result = processor.process_docs([Document(text="There were no monetary figures.")])
    assert result[0].metadata["metric_count"] == 0
    assert result[0].metadata["financial_metrics"] == {}
