"""Reusing a scope must snapshot only the context at its current entry."""
import pytest

from agentuniverse.base.context.framework_context import FrameworkContext
from agentuniverse.base.context.framework_context_manager import FrameworkContextManager


@pytest.fixture
def manager():
    manager = FrameworkContextManager()
    saved = manager.get_all_contexts()
    manager.clear_all_contexts()
    yield manager
    manager.clear_all_contexts()
    manager.set_all_contexts(saved)


@pytest.mark.parametrize('reset', ['clear', 'delete'])
@pytest.mark.parametrize('raise_in_body', [False, True])
def test_reused_scope_does_not_restore_stale_values(manager, reset, raise_in_body):
    manager.set_context('request_id', 'old-request')
    scope = FrameworkContext({'request_id': 'scoped-request'})
    with scope:
        assert manager.get_context('request_id') == 'scoped-request'
    assert manager.get_context('request_id') == 'old-request'
    if reset == 'clear':
        manager.clear_all_contexts()
    else:
        manager.del_context('request_id', force=True)

    def use_scope():
        with scope:
            assert manager.get_context('request_id') == 'scoped-request'
            if raise_in_body:
                raise RuntimeError('body failure')

    if raise_in_body:
        with pytest.raises(RuntimeError, match='body failure'):
            use_scope()
    else:
        use_scope()
    assert manager.get_context('request_id') is None


def test_reused_scope_restores_current_values(manager):
    scope = FrameworkContext({'request_id': 'scoped-request'})
    for previous in ['first', 'second', None]:
        manager.set_context('request_id', previous)
        with scope:
            assert manager.get_context('request_id') == 'scoped-request'
        assert manager.get_context('request_id') == previous


def test_reused_scope_refreshes_each_key_independently(manager):
    manager.set_context('request_id', 'old-request')
    manager.set_context('tenant', 'old-tenant')
    scope = FrameworkContext({'request_id': 'scoped-request', 'tenant': 'scoped-tenant'})
    with scope:
        pass
    manager.del_context('request_id', force=True)
    manager.set_context('tenant', 'new-tenant')
    with scope:
        assert manager.get_context('tenant') == 'scoped-tenant'
    assert manager.get_context('tenant') == 'new-tenant'
    assert manager.get_context('request_id') is None
