from agentuniverse.agent.context.store.ram_context_store import RamContextStore


def test_component_base_accepts_and_preserves_name():
    component = RamContextStore(name="context-store")

    assert component.name == "context-store"
