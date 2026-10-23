"""Overlapping patterns must not multiply one metric occurrence."""
import pytest

from agentuniverse.agent.action.knowledge.doc_processor.financial_indicator_extractor import FinancialIndicatorExtractor
from agentuniverse.agent.action.knowledge.store.document import Document


@pytest.mark.parametrize('text,metric,values', [
    ('Total revenue was $5 million.', 'revenue', [5_000_000]),
    ('Margin 20%.', 'margin', [20]),
    ('Diluted EPS: $1.25;', 'eps', [1.25]),
    ('Net loss of $3 million.', 'profit', [-3_000_000]),
    ('Gross profit: $7 million.', 'profit', [7_000_000]),
    ('Total revenue was $5 million. Total revenue was $5 million.', 'revenue', [5_000_000, 5_000_000]),
    ('Margin 20%. Margin 20%.', 'margin', [20, 20]),
    ('EPS: $1.25 and diluted EPS: $1.25;', 'eps', [1.25, 1.25]),
])
def test_public_extraction_counts_each_numeric_occurrence_once(text, metric, values):
    source = Document(text=text, metadata={'source': 'report'}, keywords={'original'})
    before = source.model_dump()
    result = FinancialIndicatorExtractor(
        metrics=[metric], currency_normalization=False, extract_comparisons=False,
        extract_temporal=False, skip_on_error=False).process_docs([source])
    assert len(result) == 1
    found = result[0].metadata['financial_metrics'][metric]
    assert sorted(item['value'] for item in found) == sorted(values)
    assert result[0].metadata['metric_count'] == len(values)
    assert result[0].text == source.text
    assert result[0].id == source.id
    assert source.model_dump() == before


def test_distinct_metric_names_share_an_occurrence_without_being_collapsed():
    result = FinancialIndicatorExtractor(
        metrics=['gross_margin', 'margin'], currency_normalization=False,
        extract_comparisons=False, extract_temporal=False).process_docs([
            Document(text='Gross margin 20%.')])[0]
    assert result.metadata['metric_count'] == 2
    assert {name: [item['value'] for item in values]
            for name, values in result.metadata['financial_metrics'].items()} == {
                'gross_margin': [20], 'margin': [20]}
