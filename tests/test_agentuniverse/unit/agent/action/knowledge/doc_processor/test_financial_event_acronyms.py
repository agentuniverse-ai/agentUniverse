"""Financial event acronyms must not match substrings of ordinary words."""
import pytest

from agentuniverse.agent.action.knowledge.doc_processor.financial_event_aggregator import FinancialEventAggregator
from agentuniverse.agent.action.knowledge.store.document import Document


@pytest.mark.parametrize('text', [
    'The company studies bipolar battery materials.',
    'Markets are becoming multipolar.',
    'Acme improved voiceover quality.',
    'The labels are ipod, ceonline and cforward.',
    'The metric identifiers are market_ipo_value and ceo2.',
])
def test_ordinary_words_do_not_become_financial_events(text):
    processor = FinancialEventAggregator(use_embeddings=False, use_llm=False, skip_on_error=False)
    results = processor.process_docs([Document(text=text)])
    assert len(results) == 1
    assert results[0].metadata['event_type'] == 'general_news'
    assert 'general_news' in results[0].keywords


@pytest.mark.parametrize('text, expected', [
    ('Acme plans an IPO.', 'ipo'),
    ('Acme plans an ipo.', 'ipo'),
    ('Several IPOs were delayed.', 'ipo'),
    ('The CEOs and CFOs spoke today.', 'leadership_change'),
    ('The CEO spoke today.', 'leadership_change'),
    ('The CFO spoke today.', 'leadership_change'),
    ('董事会公布IPO计划。', 'ipo'),
    ('公司CEO接受采访。', 'leadership_change'),
    ('公司CFO接受采访。', 'leadership_change'),
    ('The CEO/CFO spoke today.', 'leadership_change'),
    ('An IPO-related briefing took place.', 'ipo'),
    ('The company was acquired yesterday.', 'merger'),
    ('The quarterly results were discussed.', 'earnings'),
    ('公司宣布收购另一家公司。', 'merger'),
])
def test_real_event_mentions_remain_recognized(text, expected):
    processor = FinancialEventAggregator(use_embeddings=False, use_llm=False, skip_on_error=False)
    results = processor.process_docs([Document(text=text)])
    assert results[0].metadata['event_type'] == expected


def test_false_acronym_does_not_outvote_real_event_keywords():
    processor = FinancialEventAggregator(use_embeddings=False, use_llm=False, skip_on_error=False)
    result = processor.process_docs([Document(text='Earnings from voiceover and cforward products improved.')])[0]
    assert result.metadata['event_type'] == 'earnings'
