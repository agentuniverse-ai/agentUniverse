"""A sentence-ending full stop must not discard a decimal financial fact."""
import pytest

from agentuniverse.agent.action.knowledge.doc_processor.financial_indicator_extractor import FinancialIndicatorExtractor
from agentuniverse.agent.action.knowledge.store.document import Document


@pytest.mark.parametrize('text,metric,expected', [
    ('EPS: $1.25.', 'eps', [1.25]),
    ('Income: $12.75.', 'income', [12.75]),
    ('Assets: $1,234.50.', 'assets', [1234.5]),
    ('Debt ratio: 1.25.', 'debt_ratio', [1.25]),
    ('EPS: $-1.25.', 'eps', [-1.25]),
    ('EPS: $.25.', 'eps', [.25]),
    ('EPS: $12.', 'eps', [12]),
    ('EPS: $1.25', 'eps', [1.25]),
    ('Revenue: $1.25 million.', 'revenue', [1_250_000]),
    ('EPS: $1.2.3.', 'eps', []),
    ('EPS: $...', 'eps', []),
])
def test_sentence_final_decimal_extraction(text, metric, expected):
    source = Document(text=text, metadata={'source': 'report'}, keywords={'original'})
    before = source.model_dump()
    result = FinancialIndicatorExtractor(
        metrics=[metric], currency_normalization=False, extract_temporal=False,
        extract_comparisons=False, skip_on_error=False).process_docs([source])[0]
    values = result.metadata['financial_metrics'].get(metric, [])
    assert [entry['value'] for entry in values] == expected
    assert result.metadata['metric_count'] == len(expected)
    assert result.id == source.id
    assert result.text == source.text
    assert source.model_dump() == before
