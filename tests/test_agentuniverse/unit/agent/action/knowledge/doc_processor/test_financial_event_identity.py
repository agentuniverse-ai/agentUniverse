"""Financial event identity must survive short or identical summaries."""
import pytest

from agentuniverse.agent.action.knowledge.doc_processor.financial_event_aggregator import FinancialEventAggregator
from agentuniverse.agent.action.knowledge.store.document import Document


@pytest.fixture
def processor():
    return FinancialEventAggregator(use_embeddings=False, use_llm=False, skip_on_error=False)


def test_short_news_retains_content_and_distinct_event_ids(processor):
    result = processor.process_docs([
        Document(id='apple', text='Apple earnings up.'),
        Document(id='bank', text='Bank faces lawsuit.'),
    ])
    assert len(result) == 2
    assert {doc.text for doc in result} == {'Apple earnings up.', 'Bank faces lawsuit.'}
    assert len({doc.id for doc in result}) == 2
    assert all(doc.id == doc.metadata['event_id'] for doc in result)


@pytest.mark.parametrize('text', ['Short.', '苹果公布财报。', 'No period', 'A sentence with enough characters to preserve existing extraction. Tail.'])
def test_extractive_summary_keeps_nonempty_first_sentence(processor, text):
    summary = processor._generate_extractive_summary([Document(text=text)])
    assert summary.strip()
    assert text.split('.')[0] in summary


def test_same_summary_keeps_independent_event_documents(processor):
    # Separate source identities can legitimately summarize to the same sentence.
    docs = [Document(id='source-a', text='Repeated headline.'), Document(id='source-b', text='Repeated headline.')]
    clusters = [processor._create_cluster([doc]) for doc in docs]
    result = [processor._aggregate_cluster(cluster, docs) for cluster in clusters]
    assert result[0].text == result[1].text
    assert result[0].id != result[1].id


def test_event_id_stable_across_summary_changes_and_source_order(processor):
    docs = [Document(id='a', text='First brief.'), Document(id='b', text='Second brief.')]
    first = processor._aggregate_cluster(processor._create_cluster(docs), docs)
    docs[0].text = 'Updated report with enough detail to change the summary.'
    second = processor._aggregate_cluster(processor._create_cluster(list(reversed(docs))), docs)
    assert first.text != second.text
    assert first.id == second.id


def test_summary_length_and_source_limits_remain_bounded(processor):
    docs = [Document(id=str(i), text=str(i) + 'x' * 500) for i in range(7)]
    summary = processor._generate_extractive_summary(docs)
    assert len(summary) <= 1000
    assert '6' not in summary
    assert processor._generate_extractive_summary([Document(text='')]) == ''
