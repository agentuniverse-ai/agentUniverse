from agentuniverse.agent.action.knowledge.doc_processor.financial_event_aggregator import (
    FinancialEventAggregator,
)
from agentuniverse.agent.action.knowledge.store.document import Document


def test_financial_event_summary_keeps_short_text_and_event_identity():
    aggregator = FinancialEventAggregator(
        name="test_aggregator",
        use_embeddings=False,
        use_llm=False,
    )
    source = Document(id="apple", text="Apple earnings up.")

    result = aggregator.process_docs([source])

    assert len(result) == 1
    assert result[0].text == "Apple earnings up."
    assert result[0].id == result[0].metadata["event_id"]


def test_financial_events_with_same_summary_keep_distinct_ids():
    aggregator = FinancialEventAggregator(
        name="test_aggregator",
        use_embeddings=False,
        use_llm=False,
    )
    documents = [
        Document(id="event-a", text="Shared short summary. Alpha detail."),
        Document(id="event-b", text="Shared short summary. Beta detail."),
    ]

    result = aggregator.process_docs(documents)

    assert len(result) == 2
    assert {doc.id for doc in result} == {doc.metadata["event_id"] for doc in result}
    assert len({doc.id for doc in result}) == 2
