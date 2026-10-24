"""Ordinary prose after an amount must not become a million/billion suffix."""
import pytest

from agentuniverse.agent.action.knowledge.doc_processor.financial_indicator_extractor import FinancialIndicatorExtractor
from agentuniverse.agent.action.knowledge.store.document import Document


@pytest.mark.parametrize('metric,label', [
    ('revenue', 'revenue'), ('profit', 'profit'), ('assets', 'assets'),
    ('debt', 'debt'), ('free_cash_flow', 'free cash flow'),
])
@pytest.mark.parametrize('following', ['before tax', 'monthly'])
def test_ordinary_word_prefix_does_not_scale_amount(metric, label, following):
    processor = FinancialIndicatorExtractor(
        metrics=[metric], currency_normalization=False,
        extract_temporal=False, extract_comparisons=False, skip_on_error=False,
    )
    source = Document(text=f'{label} $10 {following}', metadata={'source': 'report'})

    output = processor.process_docs([source])[0]

    values = output.metadata['financial_metrics'][metric]
    assert [item['value'] for item in values] == [10]
    assert [item['scale'] for item in values] == ['units']
    assert output.id == source.id
    assert source.metadata == {'source': 'report'}


@pytest.mark.parametrize('following', [', but expenses were $8', ' millionaires', ' billionaires'])
def test_revenue_does_not_consume_prefix_of_following_word(following):
    metrics = FinancialIndicatorExtractor(metrics=['revenue'])._extract_metrics(f'revenue $10{following}')
    assert len(metrics) == 1
    assert metrics[0].value == 10
    assert not metrics[0].raw_match.rstrip().lower().endswith(('m', 'b'))


@pytest.mark.parametrize('suffix,expected', [
    ('million', 10_000_000), ('BILLION', 10_000_000_000),
    ('M', 10_000_000), ('b', 10_000_000_000),
    ('million-dollar', 10_000_000), ('M美元', 10_000_000),
    ('亿', 1_000_000_000), ('千万', 100_000_000),
])
def test_complete_scale_tokens_still_scale_amount(suffix, expected):
    metrics = FinancialIndicatorExtractor(metrics=['revenue'])._extract_metrics(f'revenue $10{suffix}')
    assert len(metrics) == 1
    assert metrics[0].value == expected


def test_adjacent_metrics_keep_their_own_scale_labels():
    processor = FinancialIndicatorExtractor(
        metrics=['revenue', 'profit'], currency_normalization=False,
        extract_temporal=False, extract_comparisons=False, skip_on_error=False,
    )
    document = Document(text='revenue $10 million; profit $2 billion')

    metrics = processor.process_docs([document])[0].metadata['financial_metrics']

    assert [(m['value'], m['scale']) for m in metrics['revenue']] == [(10_000_000, 'million')]
    assert [(m['value'], m['scale']) for m in metrics['profit']] == [(2_000_000_000, 'billion')]
