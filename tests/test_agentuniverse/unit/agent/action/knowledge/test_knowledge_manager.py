# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/20 10:00
# @Author  : au_qa
# @FileName: test_knowledge_manager.py
"""Unit tests for the singleton KnowledgeManager."""

from types import SimpleNamespace

import pytest

from agentuniverse.agent.action.knowledge.knowledge_manager import \
    KnowledgeManager


@pytest.fixture
def manager():
    """Return the process-wide KnowledgeManager singleton."""
    return KnowledgeManager()


@pytest.fixture
def component():
    """Return a lightweight storable knowledge object."""
    return SimpleNamespace(default_symbol=False)


class TestKnowledgeManager:
    """Test the registry behavior of KnowledgeManager."""

    @pytest.fixture(autouse=True)
    def restore_registry(self):
        """Unregister only the names added during each test."""
        mgr = KnowledgeManager()
        before = set(mgr.get_instance_name_list())
        yield
        for name in set(mgr.get_instance_name_list()) - before:
            mgr.unregister(name)

    def test_singleton_identity(self, manager):
        """KnowledgeManager() always returns the same instance."""
        assert KnowledgeManager() is manager

    def test_register_adds_instance_to_list(self, manager, component):
        """A registered knowledge name appears in the instance list."""
        manager.register('ut_knowledge_alice', component)
        name_list = manager.get_instance_name_list()
        assert isinstance(name_list, list)
        assert 'ut_knowledge_alice' in name_list

    def test_duplicate_register_keeps_first(self, manager, component):
        """Re-registering an existing name keeps the original object."""
        second = SimpleNamespace(default_symbol=False)
        manager.register('ut_knowledge_dup', component)
        manager.register('ut_knowledge_dup', second)
        assert manager._instance_obj_map['ut_knowledge_dup'] is component

    def test_unregister_removes_instance(self, manager, component):
        """Unregistering removes the name from the instance list."""
        manager.register('ut_knowledge_remove', component)
        manager.unregister('ut_knowledge_remove')
        assert manager.get_instance_name_list() == []

    def test_register_default_symbol_adds_default_instance(self, manager):
        """A default-symbol knowledge becomes the default instance."""
        default_comp = SimpleNamespace(default_symbol=True)
        manager.register('ut_knowledge_default', default_comp)
        assert '__default_instance__' in manager.get_instance_name_list()
        assert manager._instance_obj_map['__default_instance__'] is default_comp

    def test_register_non_default_symbol_keeps_default_slot(self,
                                                           manager,
                                                           component):
        """Registering without the default symbol leaves the slot empty."""
        manager.register('ut_knowledge_plain', component)
        assert '__default_instance__' not in manager.get_instance_name_list()

    def test_register_requires_default_symbol_attribute(self, manager):
        """An object without default_symbol cannot be registered."""
        with pytest.raises(AttributeError):
            manager.register('ut_knowledge_bad', SimpleNamespace())


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
