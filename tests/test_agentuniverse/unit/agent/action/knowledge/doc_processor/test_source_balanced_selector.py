"""Selection invariants and configuration for source-balanced evidence."""

import inspect
import importlib
from itertools import product
from pathlib import Path

import pytest

from agentuniverse.agent.action.knowledge.doc_processor.source_balanced_selector import SourceBalancedSelector
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer


def documents(sources):
    return [Document(id=str(i), text=f"evidence {i}", metadata={"source": source})
            for i, source in enumerate(sources)]


@pytest.mark.parametrize("refill,top_n,expected", [
    (False, 3, [0, 3, 4]), (True, 3, [0, 3, 4]),
    (False, 5, [0, 3, 4]), (True, 5, [0, 1, 2, 3, 4]),
    (False, None, [0, 3, 4]), (True, None, [0, 3, 4]),
    (True, 0, []), (False, 1, [0]), (True, 100, [0, 1, 2, 3, 4]),
])
def test_selection_contract(refill, top_n, expected):
    docs = documents(["A", "A", "A", "B", "C"])
    before = [doc.model_dump() for doc in docs]
    result = SourceBalancedSelector(top_n=top_n, refill=refill).process_docs(docs)
    assert [doc.id for doc in result] == [str(i) for i in expected]
    assert all(doc is docs[int(doc.id)] for doc in result)
    assert [doc.model_dump() for doc in docs] == before


def test_unlabelled_identity_and_namespaces():
    docs = documents([None, "", " ", "document", "0", None])
    docs[0].metadata = None
    docs[-1].id = docs[0].id
    result = SourceBalancedSelector().process_docs(docs)
    assert [doc.id for doc in result] == ["0", "1", "2", "3", "4"]


def test_custom_key_exact_values_and_repeat_calls():
    docs = [Document(text=str(i), metadata={"publisher": source, "source": "same"},
                     embedding=[1.0], keywords={"key"})
            for i, source in enumerate(["A", "a", " A", "A"])]
    processor = SourceBalancedSelector(source_key="publisher")
    before = [doc.model_dump() for doc in docs]
    for _ in range(3):
        assert processor.process_docs(docs) == docs[:3]
    assert [doc.model_dump() for doc in docs] == before
    assert not hasattr(processor, "channel_key")


@pytest.mark.parametrize("value", [False, 1, 1.5, [], {}, ["A"]])
def test_invalid_source_values_raise_without_mutating(value):
    docs = documents(["A", value])
    before = [doc.model_dump() for doc in docs]
    with pytest.raises(ValueError, match="document index 1"):
        SourceBalancedSelector(top_n=1).process_docs(docs)
    assert [doc.model_dump() for doc in docs] == before


@pytest.mark.parametrize("options", [
    {"max_per_source": 0}, {"max_per_source": -1}, {"max_per_source": True},
    {"max_per_source": 1.5}, {"max_per_source": "2"}, {"top_n": -1},
    {"top_n": False}, {"top_n": "2"}, {"source_key": ""},
    {"source_key": " "}, {"refill": "false"}, {"refill": 1},
])
def test_invalid_constructor_options(options):
    with pytest.raises(ValueError):
        SourceBalancedSelector(**options)


def test_shipped_yaml_and_reconfiguration():
    path = Path(inspect.getfile(SourceBalancedSelector)).with_suffix(".yaml")
    config = Configer(str(path)).load()
    component = ComponentConfiger(config).load()
    cls = getattr(importlib.import_module(component.metadata_module), component.metadata_class)
    processor = cls().initialize_by_component_configer(component)
    assert processor.name == "source_balanced_selector"
    assert processor.top_n == 5
    config.set("top_n", None)
    config.set("max_per_source", 2)
    config.set("refill", True)
    processor.initialize_by_component_configer(ComponentConfiger(config).load())
    assert processor.process_docs(documents(["A", "A", "A"])) == documents(["A", "A"])
    config.set("max_per_source", 0)
    with pytest.raises(ValueError):
        processor.initialize_by_component_configer(ComponentConfiger(config).load())
    assert processor.max_per_source == 2


def test_runtime_assignment_is_validated_and_empty_batches_work():
    processor = SourceBalancedSelector()
    assert processor.process_docs([]) == []
    processor.top_n = -1
    with pytest.raises(ValueError):
        processor.process_docs(documents(["A"]))


@pytest.mark.parametrize("cap", [1, 2, 3])
def test_repeated_occurrences_are_capped_not_silently_deduplicated(cap):
    doc = Document(text="same", metadata={"source": "A"})
    result = SourceBalancedSelector(max_per_source=cap).process_docs([doc] * 4)
    assert len(result) == cap
    assert all(item is doc for item in result)


@pytest.mark.parametrize("key,value", [("top_n", True), ("refill", "false"), ("source_key", " ")])
def test_yaml_invalid_options_are_not_coerced(key, value):
    path = Path(inspect.getfile(SourceBalancedSelector)).with_suffix(".yaml")
    config = Configer(str(path)).load()
    config.set(key, value)
    with pytest.raises(ValueError):
        SourceBalancedSelector().initialize_by_component_configer(ComponentConfiger(config).load())


def test_exhaustive_small_sequences_match_reference():
    # 1,944 configurations; one test, not 1,944 independent tests.
    for sequence in product("ABC", repeat=4):
        docs = documents(sequence)
        for cap, limit, refill in product([1, 2], [0, 1, 2, 3, 4, None], [False, True]):
            eligible = [i for i, source in enumerate(sequence)
                        if sequence[:i].count(source) < cap]
            selected = eligible if limit is None else eligible[:limit]
            if refill and limit is not None:
                remaining = [i for i in range(len(docs)) if i not in selected]
                selected = sorted(selected + remaining[:max(0, limit - len(selected))])
            actual = SourceBalancedSelector(max_per_source=cap, top_n=limit, refill=refill).process_docs(docs)
            assert [doc.id for doc in actual] == [str(i) for i in selected]
