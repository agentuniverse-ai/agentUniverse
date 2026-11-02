# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Regression tests for ComponentBase.create_copy isolation.

https://github.com/agentuniverse-ai/agentUniverse/issues/1189

When ``model_copy(deep=True)`` fails, the copy must still isolate mutable
fields. A shallow ``model_copy()`` shares those fields with the original.
"""

import logging
import threading
from typing import Any
from unittest.mock import patch

from pydantic import Field
import pytest

from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.component.component_manager_base import ComponentManagerBase


class _CopyComponent(ComponentBase):
    """Minimal component with a mutable field used to check isolation."""

    component_type: ComponentEnum = ComponentEnum.DEFAULT
    name: str = 'sample'
    tags: list = Field(default_factory=list)


class _LockComponent(_CopyComponent):
    """Holds a runtime resource that neither deep-copy path can duplicate."""

    name: str = 'lock_holder'
    client: Any = Field(default_factory=threading.Lock)


def _fail_deep_model_copy(original):
    def _model_copy(self, *args, **kwargs):
        if kwargs.get('deep'):
            raise RuntimeError('simulated deep model_copy failure')
        return original(self, *args, **kwargs)

    return _model_copy


def test_create_copy_isolates_mutable_fields():
    component = _CopyComponent(tags=['alpha'])

    copied = component.create_copy()

    assert copied is not component
    assert copied.tags == ['alpha']
    copied.tags.append('beta')
    assert component.tags == ['alpha']
    assert copied.tags == ['alpha', 'beta']


def test_create_copy_fallback_isolates_when_deep_model_copy_fails(caplog):
    """Deep model_copy failure must not share mutable fields with the original."""
    component = _CopyComponent(tags=['alpha'])
    original_model_copy = ComponentBase.model_copy

    with caplog.at_level(
        logging.WARNING,
        logger='agentuniverse.base.component.component_base',
    ):
        with patch.object(
            ComponentBase,
            'model_copy',
            _fail_deep_model_copy(original_model_copy),
        ):
            copied = component.create_copy()

    assert copied is not component
    assert copied.tags is not component.tags
    copied.tags.append('gamma')
    assert component.tags == ['alpha']
    assert copied.tags == ['alpha', 'gamma']
    assert 'deep model_copy failed' in caplog.text


def test_create_copy_propagates_when_both_deep_paths_fail(caplog):
    """Both deep paths failing must raise. Shallow model_copy is not a fallback."""
    component = _CopyComponent(tags=['alpha'])

    def fail_deep_model_copy(self, *args, **kwargs):
        if kwargs.get('deep'):
            raise RuntimeError('simulated deep model_copy failure')
        raise AssertionError('shallow model_copy must not be used as fallback')

    with caplog.at_level(
        logging.WARNING,
        logger='agentuniverse.base.component.component_base',
    ):
        with patch.object(ComponentBase, 'model_copy', fail_deep_model_copy), patch(
            'copy.deepcopy',
            side_effect=TypeError('simulated deepcopy failure'),
        ):
            with pytest.raises(TypeError, match='simulated deepcopy failure'):
                component.create_copy()

    assert 'deep model_copy failed' in caplog.text
    assert component.tags == ['alpha']


def test_create_copy_raises_for_non_copyable_runtime_resource():
    component = _LockComponent(tags=['alpha'])

    with pytest.raises(TypeError):
        component.create_copy()

    assert component.tags == ['alpha']


def test_get_instance_obj_new_instance_isolates_when_deep_model_copy_fails():
    component = _CopyComponent(tags=['alpha'])
    manager = ComponentManagerBase(ComponentEnum.DEFAULT)
    manager.register('test.default.sample', component)
    original_model_copy = ComponentBase.model_copy

    with patch.object(
        ComponentBase,
        'model_copy',
        _fail_deep_model_copy(original_model_copy),
    ):
        copied = manager.get_instance_obj(
            'sample', appname='test', new_instance=True
        )

    assert copied is not component
    assert copied.tags is not component.tags
    copied.tags.append('beta')
    assert component.tags == ['alpha']


def test_get_instance_obj_without_new_instance_returns_registered_object():
    component = _CopyComponent(tags=['alpha'])
    manager = ComponentManagerBase(ComponentEnum.DEFAULT)
    manager.register('test.default.sample', component)

    assert manager.get_instance_obj(
        'sample', appname='test', new_instance=False
    ) is component
