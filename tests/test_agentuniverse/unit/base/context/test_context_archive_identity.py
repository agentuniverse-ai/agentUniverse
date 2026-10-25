"""Archive readers and writers must share an initially empty archive."""
from contextvars import Context

import pytest

from agentuniverse.base.context.context_archive_utils import (
    get_current_context_archive,
    update_context_archive,
)
from agentuniverse.base.context.framework_context_manager import FrameworkContextManager


@pytest.mark.parametrize('initial', ['missing', 'none', 'empty', 'populated', 'cleared'])
def test_archive_reference_observes_later_updates(initial):
    def scenario():
        manager = FrameworkContextManager()
        manager.clear_all_contexts()
        if initial == 'none':
            manager.set_context('context_archive', None)
        elif initial == 'empty':
            manager.set_context('context_archive', {})
        elif initial == 'populated':
            manager.set_context('context_archive', {'old': {'data': 'old', 'description': 'old'}})
        archive = get_current_context_archive()
        if initial == 'cleared':
            archive['temporary'] = {'data': 'temporary', 'description': 'temporary'}
            archive.clear()
        update_context_archive('retrieval', 'evidence', 'retrieved context')
        assert archive['retrieval'] == {'data': 'evidence', 'description': 'retrieved context'}
        assert get_current_context_archive() is archive
        assert manager.get_context('context_archive') is archive
    Context().run(scenario)


def test_preinstalled_empty_archive_remains_live():
    def scenario():
        manager = FrameworkContextManager()
        manager.clear_all_contexts()
        archive = {}
        manager.set_context('context_archive', archive)
        update_context_archive('result', 'answer', 'description')
        assert archive['result']['data'] == 'answer'
    Context().run(scenario)
