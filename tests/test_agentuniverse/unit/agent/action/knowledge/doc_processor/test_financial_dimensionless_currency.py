"""Currency conversion must not change percentages or dimensionless ratios."""
import pytest

from agentuniverse.agent.action.knowledge.doc_processor.financial_indicator_extractor import FinancialIndicatorExtractor
from agentuniverse.agent.action.knowledge.store.document import Document


@pytest.mark.parametrize('text,metric,expected', [
    ('ROI 10%', 'roi', 10),
    ('net margin 20%', 'net_margin', 20),
    ('market share 30%', 'market_share', 30),
    ('churn rate 5%', 'churn_rate', 5),
    ('debt-to-equity ratio 2', 'debt_ratio', 2),
])
@pytest.mark.parametrize('currency', ['EUR', 'GBP', 'CNY'])
def test_currency_context_does_not_change_dimensionless_values(text, metric, expected, currency):
    source = Document(text=f'{currency} portfolio: {text}', metadata={'source': 'report'})
    values = []
    for normalize in [False, True]:
        processor = FinancialIndicatorExtractor(
            metrics=[metric], currency_normalization=normalize,
            extract_temporal=False, extract_comparisons=False, skip_on_error=False,
        )
        output = processor.process_docs([source])[0]
        values.append([item['value'] for item in output.metadata['financial_metrics'][metric]])
        assert output.id == source.id
    assert values == [[expected], [expected]]
    assert source.metadata == {'source': 'report'}


@pytest.mark.parametrize('text,metric,expected', [
    ('revenue €10', 'revenue', 10.9),
    ('profit £10', 'profit', 12.7),
    ('EPS ¥10', 'eps', 1.4),
])
def test_monetary_values_and_per_share_amounts_still_convert(text, metric, expected):
    processor = FinancialIndicatorExtractor(
        metrics=[metric], currency_normalization=True,
        extract_temporal=False, extract_comparisons=False, skip_on_error=False,
    )
    output = processor.process_docs([Document(text=text)])[0]
    amounts = output.metadata['financial_metrics'][metric]
    assert len(amounts) == 1
    assert amounts[0]['value'] == pytest.approx(expected)
