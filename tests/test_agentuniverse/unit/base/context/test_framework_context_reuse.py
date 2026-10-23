from agentuniverse.base.context.framework_context import FrameworkContext
from agentuniverse.base.context.framework_context_manager import FrameworkContextManager


def test_reused_scope_refreshes_absent_key_snapshot():
    manager = FrameworkContextManager()
    manager.clear_all_contexts()
    scope = FrameworkContext({"request_id": "scoped"})

    with scope:
        pass
    manager.clear_all_contexts()

    with scope:
        pass

    assert manager.get_context("request_id") is None
    manager.clear_all_contexts()


def test_reused_scope_restores_value_from_current_entry():
    manager = FrameworkContextManager()
    manager.clear_all_contexts()
    manager.set_context("request_id", "first")
    scope = FrameworkContext({"request_id": "scoped"})

    with scope:
        pass
    manager.set_context("request_id", "second")

    with scope:
        pass

    assert manager.get_context("request_id") == "second"
    manager.clear_all_contexts()
