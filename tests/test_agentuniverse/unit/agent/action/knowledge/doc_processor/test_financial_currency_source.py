"""Currency conversion must use the currency of the matched metric."""

import pytest

from agentuniverse.agent.action.knowledge.doc_processor.financial_indicator_extractor import (
    FinancialIndicatorExtractor, FinancialMetric,
)
from agentuniverse.agent.action.knowledge.store.document import Document


@pytest.mark.parametrize(
    "text, revenue, profit",
    [
        ("revenue of $100 million; profit of €20 million.", 100_000_000, 21_800_000),
        ("profit of €20 million; revenue of $100 million.", 100_000_000, 21_800_000),
        ("revenue of €100 million; profit of £20 million.", 109_000_000, 25_400_000),
        ("revenue of £100 million; profit of ¥20 million.", 127_000_000, 2_800_000),
        ("revenue of ¥100 million; profit of €20 million.", 14_000_000, 21_800_000),
    ],
)
def test_mixed_currency_metrics_are_normalized_independently(text, revenue, profit):
    processor = FinancialIndicatorExtractor(
        metrics=["revenue", "profit"], extract_temporal=False, extract_comparisons=False,
    )
    metrics = processor.process_docs([Document(text=text)])[0].metadata["financial_metrics"]
    assert len(metrics["revenue"]) == len(metrics["profit"]) == 1
    assert metrics["revenue"][0]["value"] == pytest.approx(revenue)
    assert metrics["profit"][0]["value"] == pytest.approx(profit)
    assert metrics["revenue"][0]["unit"] == metrics["profit"][0]["unit"] == "USD"


@pytest.mark.parametrize("symbol, value", [("$", 100), ("€", 109), ("£", 127), ("¥", 14)])
def test_single_currency_conversion_is_unchanged(symbol, value):
    processor = FinancialIndicatorExtractor(metrics=["revenue"], extract_comparisons=False)
    result = processor.process_docs([Document(text=f"revenue of {symbol}100")])[0]
    assert result.metadata["financial_metrics"]["revenue"][0]["value"] == pytest.approx(value)


def test_currency_normalization_can_still_be_disabled():
    processor = FinancialIndicatorExtractor(
        metrics=["revenue", "profit"], currency_normalization=False,
        extract_temporal=False, extract_comparisons=False,
    )
    result = processor.process_docs([Document(text="revenue of £100; profit of ¥20")])[0]
    assert result.metadata["financial_metrics"]["revenue"][0]["value"] == 100
    assert result.metadata["financial_metrics"]["profit"][0]["value"] == 20


def test_context_currency_label_is_used_when_match_has_no_marker():
    processor = FinancialIndicatorExtractor(metrics=["revenue"], extract_comparisons=False)
    result = processor.process_docs([Document(text="EUR revenue of 100 million")])[0]
    assert result.metadata["financial_metrics"]["revenue"][0]["value"] == pytest.approx(109_000_000)


def test_metric_without_raw_match_keeps_context_fallback():
    processor = FinancialIndicatorExtractor()
    metric = FinancialMetric(name="revenue", value=100, unit="EUR", context="EUR revenue")
    processor._normalize_currencies([metric])
    assert metric.value == pytest.approx(109)
    assert metric.unit == "USD"
