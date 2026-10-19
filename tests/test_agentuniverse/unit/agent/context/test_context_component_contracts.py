"""Regression contracts for inherited names and relevant RAM search ranking."""

from datetime import datetime, timedelta
from types import SimpleNamespace

import pytest

from agentuniverse.agent.context.context_model import (
    ContextMetadata,
    ContextPriority,
    ContextSegment,
    ContextType,
)
from agentuniverse.agent.context.store.ram_context_store import RamContextStore
from agentuniverse.base.component import component_base
from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_enum import ComponentEnum


class InheritedComponent(ComponentBase):
    """A component relying entirely on the base name field."""

    component_type: ComponentEnum = ComponentEnum.TOOL


class NamedComponent(InheritedComponent):
    """An existing component retaining its own default name."""

    name: str = "default_tool"


@pytest.mark.parametrize("component_class", [InheritedComponent, NamedComponent, RamContextStore])
def test_name_survives_serialization_and_copy(component_class, monkeypatch):
    """Constructor names remain real fields across serialization and copying."""
    monkeypatch.setattr(
        component_base,
        "ApplicationConfigManager",
        lambda: SimpleNamespace(app_configer=SimpleNamespace(base_info_appname="test_app")),
    )
    instance = component_class(name="custom_name")
    assert instance.model_dump()["name"] == "custom_name"
    restored = component_class.model_validate_json(instance.model_dump_json())
    copied = instance.create_copy()
    for candidate in (instance, restored, copied):
        assert candidate.name == "custom_name"
        assert candidate.get_instance_code() == (f"test_app.{candidate.component_type.value.lower()}.custom_name")
    copied.name = "copy_only"
    assert instance.name == restored.name == "custom_name"


@pytest.mark.parametrize(
    ("component_class", "expected"),
    [(InheritedComponent, ""), (NamedComponent, "default_tool"), (RamContextStore, "")],
)
def test_existing_default_names_remain_compatible(component_class, expected):
    """The base field does not replace defaults declared by subclasses."""
    instance = component_class()
    assert instance.name == instance.model_dump()["name"] == expected


def make_segment(
    identifier,
    *,
    content="Python reference",
    priority=ContextPriority.MEDIUM,
    context_type=ContextType.BACKGROUND,
    last_accessed=None,
):
    """Create an unexpired segment with deterministic decay for ordering tests."""
    return ContextSegment(
        id=identifier,
        type=context_type,
        content=content,
        tokens=2,
        priority=priority,
        metadata=ContextMetadata(decay_rate=0.0, last_accessed=last_accessed or datetime(2026, 1, 1)),
    )


@pytest.mark.parametrize("query", ["python", "  PyThOn\t"])
@pytest.mark.parametrize("top_k", [2, 10])
def test_priority_orders_only_relevant_results_without_touching_excluded_segments(query, top_k):
    """Priority still ranks matches; excluded results receive no access update."""
    store = RamContextStore()
    priorities = [ContextPriority.LOW, ContextPriority.HIGH, ContextPriority.MEDIUM]
    relevant = [make_segment(p.value, priority=p) for p in priorities]
    unrelated = make_segment("unrelated", content="Cooking", priority=ContextPriority.CRITICAL)
    store.add([unrelated, *relevant], session_id="session")
    before = unrelated.metadata.model_dump()

    result = store.search(query, "session", top_k=top_k)

    assert [item.id for item in result] == ["high", "medium", "low"][:top_k]
    assert unrelated.metadata.model_dump() == before
    assert [item.metadata.access_count for item in relevant] == [int(top_k > 2), 1, 1]


def test_equal_scores_use_last_accessed_as_tiebreaker():
    """Recency breaks exact score ties independently of insertion order."""
    store = RamContextStore()
    older = make_segment("older", last_accessed=datetime(2026, 1, 1))
    newer = make_segment("newer", last_accessed=datetime(2026, 1, 2))
    store.add([newer, older], session_id="session")
    assert [item.id for item in store.search("python", "session")] == ["newer", "older"]


def test_decay_still_ranks_relevant_results():
    """Relevance decay can outweigh priority without admitting nonmatches."""
    store = RamContextStore()
    decayed = make_segment("decayed", priority=ContextPriority.CRITICAL)
    decayed.metadata.relevance_score = 0.2
    fresh = make_segment("fresh", priority=ContextPriority.LOW)
    store.add([decayed, fresh], session_id="session")
    assert [item.id for item in store.search("python", "session")] == ["fresh", "decayed"]


def test_search_retains_session_type_and_expiration_filters():
    """Matching text does not override existing scope or TTL filters."""
    store = RamContextStore(ttl_hours=24)
    valid = make_segment("valid")
    wrong_type = make_segment("wrong_type", context_type=ContextType.SYSTEM)
    expired = make_segment("expired")
    expired.metadata.created_at = datetime.now() - timedelta(hours=48)
    other_session = make_segment("other_session")
    store.add([expired, wrong_type, valid], session_id="session")
    store.add([other_session], session_id="other")
    result = store.search("python", "session", context_type=ContextType.BACKGROUND)
    assert [item.id for item in result] == ["valid"]
    assert all(item.metadata.access_count == 0 for item in (expired, wrong_type, other_session))
