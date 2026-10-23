from agentuniverse.agent.action.knowledge.doc_processor.financial_event_aggregator import (
    FinancialEventAggregator,
)
from agentuniverse.agent.action.knowledge.store.document import Document


def _event_id(source_ids):
    processor = FinancialEventAggregator()
    documents = [Document(id=source_id, text="same event") for source_id in source_ids]
    return processor._generate_event_id(documents)


def test_source_id_delimiters_do_not_collide():
    assert _event_id(["a|b", "c"]) != _event_id(["a", "b|c"])
    assert _event_id(["a|b", "c"]) != _event_id(["a", "b", "c"])


def test_source_order_is_still_irrelevant():
    assert _event_id(["source|2", "source\\1"]) == _event_id(["source\\1", "source|2"])


def test_ordinary_source_ids_keep_existing_identity():
    assert _event_id(["a", "b"]) == "event_d07262410206"
