"""Comparative percentages must preserve direction and occurrence identity."""

import pytest

from agentuniverse.agent.action.knowledge.doc_processor.financial_indicator_extractor import FinancialIndicatorExtractor
from agentuniverse.agent.action.knowledge.store.document import Document


@pytest.mark.parametrize(
    "text,kind,value",
    [
        ("Revenue YoY decline of 12%.", "yoy", -12),
        ("Profit QoQ decrease 2.5%.", "qoq", -2.5),
        ("Sales fell 7% YoY.", "yoy", -7),
        ("Revenue down 8% quarter-over-quarter.", "qoq", -8),
        ("Revenue -12% YoY.", "yoy", -12),
        ("Profit -2.5% QoQ.", "qoq", -2.5),
        ("Revenue +12% YoY.", "yoy", 12),
        ("Revenue YoY growth of 12%.", "yoy", 12),
        ("Revenue up 12% year-over-year.", "yoy", 12),
        ("营收同比下降12%。", "yoy", -12),
        ("利润环比减少2.5%。", "qoq", -2.5),
        ("营收同比增长12%。", "yoy", 12),
        ("Revenue grew by 12%.", "unknown", 12),
        ("Revenue decreased by 12%.", "unknown", -12),
        ("Revenue decreased by 12% YoY.", "yoy", -12),
        ("Revenue 12% decrease compared to last year.", "unknown", -12),
        ("Revenue YoY decline of -12%.", "yoy", -12),
        ("Revenue YoY growth of -12%.", "yoy", -12),
        ("Revenue QoQ growth of +2.5%.", "qoq", 2.5),
        ("Revenue FELL 1,234.5% YOY.", "yoy", -1234.5),
    ],
)
def test_comparison_direction_is_preserved_once(text, kind, value):
    processor = FinancialIndicatorExtractor(currency_normalization=False)
    comparisons = processor._detect_comparisons(text, [])
    assert [(item.comparison_type, item.change_percent) for item in comparisons] == [(kind, value)]


def test_separate_occurrences_with_same_value_are_not_collapsed():
    result = FinancialIndicatorExtractor()._detect_comparisons("Revenue rose 5% YoY. Profit fell 5% YoY.", [])
    assert [item.change_percent for item in result] == [5, -5]


def test_source_order_and_direction_are_local_to_each_occurrence():
    result = FinancialIndicatorExtractor()._detect_comparisons(
        "Revenue down 5% QoQ. Profit up 5% YoY. Cash increased by 2%.", []
    )
    assert [item.change_percent for item in result] == [-5, 5, 2]
    assert [item.comparison_type for item in result[:2]] == ["qoq", "yoy"]


def test_public_metadata_carries_the_negative_change():
    doc = Document(text="Revenue reached $100 million. Revenue YoY decline of 12%.")
    result = FinancialIndicatorExtractor(currency_normalization=False, skip_on_error=False).process_docs([doc])
    values = result[0].metadata["comparative_metrics"]
    assert len(values) == 1
    assert values[0]["change_percent"] == -12
    assert values[0]["comparison_type"] == "yoy"


@pytest.mark.parametrize("number,expected", [(".5", 0.5), ("-.5", -0.5), ("+.5", 0.5), ("1,234,567.89", 1234567.89)])
def test_complete_numeric_tokens(number, expected):
    result = FinancialIndicatorExtractor()._detect_comparisons(f"Revenue {number}% YoY.", [])
    assert [item.change_percent for item in result] == [expected]


@pytest.mark.parametrize("number", ["12,34", "1,234,56", "1.2.3", "--12", "+-12", "1,,234"])
@pytest.mark.parametrize("template", ["Revenue {}% YoY.", "Revenue YoY decline of {}%."])
def test_malformed_numbers_are_not_partially_extracted(number, template):
    assert FinancialIndicatorExtractor()._detect_comparisons(template.format(number), []) == []


@pytest.mark.parametrize(
    "text", ["Revenue abc12% YoY.", "Revenue YoYish decline of 12%.", "Revenue grew by 12% YoYish."]
)
def test_numeric_and_period_word_boundaries(text):
    comparisons = FinancialIndicatorExtractor()._detect_comparisons(text, [])
    assert not any(item.comparison_type == "yoy" for item in comparisons)
