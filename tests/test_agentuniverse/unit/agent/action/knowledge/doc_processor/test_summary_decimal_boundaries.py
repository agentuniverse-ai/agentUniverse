"""Decimal points are part of financial facts, not sentence boundaries."""
import pytest
from agentuniverse.agent.action.knowledge.doc_processor.summarization_processor import SummarizationProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query


@pytest.mark.parametrize('sentence', ['Revenue reached 12.5 million dollars', 'Margin was -3.25 percent',
    '收入达到12.5亿元', 'The ratio is 0.05', 'Version 1.2.3 is supported'])
def test_numeric_periods_stay_inside_sentence(sentence):
    assert SummarizationProcessor._split_sentences(sentence + '. Other facts.') == [sentence, 'Other facts']


def test_summary_preserves_decimal_and_unit():
    text = 'Revenue reached 12.5 million dollars. Costs declined. Sales grew.'
    result = SummarizationProcessor(max_sentences=1).process_docs([Document(text=text)], Query(query_str='revenue'))
    assert result[0].text == 'Revenue reached 12.5 million dollars'


def test_terminal_period_after_number_and_cjk_boundaries():
    assert SummarizationProcessor._split_sentences('Count is 12. Next sentence!利润12.5亿元。继续增长？') == [
        'Count is 12', 'Next sentence', '利润12.5亿元', '继续增长']
