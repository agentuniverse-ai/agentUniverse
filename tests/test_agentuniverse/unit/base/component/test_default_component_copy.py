"""Default lookup honors the same component copy contract as named lookup."""

from copy import deepcopy
import threading
from typing import Any

from pydantic import Field
import pytest

from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.component.component_manager_base import ComponentManagerBase


class ClientComponent(ComponentBase):
    """SDK-style component: isolate options while sharing a non-copyable client."""

    component_type: ComponentEnum = ComponentEnum.LLM
    name: str = 'sample'
    client: Any = Field(default_factory=threading.Lock)
    options: dict = Field(default_factory=lambda: {'tags': ['original']})

    def create_copy(self):
        return self.model_copy(update={'options': deepcopy(self.options)})


@pytest.fixture
def registered_component():
    manager = ComponentManagerBase(ComponentEnum.LLM)
    component = ClientComponent(default_symbol=True)
    manager.register('test.llm.sample', component)
    return manager, component


@pytest.mark.parametrize('lookup', ['direct', 'alias'])
def test_default_lookup_preserves_component_copy_contract(registered_component, lookup):
    manager, original = registered_component

    if lookup == 'direct':
        copied = manager.get_default_instance(new_instance=True)
    else:
        copied = manager.get_instance_obj('__default_instance__', new_instance=True)

    assert copied is not original
    assert copied.client is original.client
    copied.options['tags'].append('copy-only')
    assert original.options == {'tags': ['original']}
    assert manager.get_default_instance() is original


def test_named_lookup_already_supports_noncopyable_client(registered_component):
    manager, original = registered_component

    copied = manager.get_instance_obj('sample', appname='test', new_instance=True)

    assert copied is not original
    assert copied.client is original.client
    copied.options['tags'].append('copy-only')
    assert original.options == {'tags': ['original']}


@pytest.mark.parametrize('lookup', ['direct', 'alias'])
def test_shared_default_lookup_still_returns_original(registered_component, lookup):
    manager, original = registered_component

    if lookup == 'direct':
        result = manager.get_default_instance(new_instance=False)
    else:
        result = manager.get_instance_obj('__default_instance__', new_instance=False)

    assert result is original


@pytest.mark.parametrize('new_instance', [True, False])
def test_missing_default_still_returns_none(new_instance):
    manager = ComponentManagerBase(ComponentEnum.LLM)

    assert manager.get_default_instance(new_instance=new_instance) is None
    assert manager.get_instance_obj('__default_instance__', new_instance=new_instance) is None
