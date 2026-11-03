#
# !/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest

from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.component.component_manager_base import ComponentManagerBase

APP = 'unit_test_app'
CODE_FOO = f'{APP}.tool.foo'
CODE_BAR = f'{APP}.tool.bar'


class DummyComponent(ComponentBase):
    name: str = ''
    payload: str = ''


def make_manager() -> ComponentManagerBase:
    return ComponentManagerBase[DummyComponent](ComponentEnum.TOOL)


def make_component(name: str = 'foo', default_symbol: bool = False,
                   payload: str = '') -> DummyComponent:
    return DummyComponent(component_type=ComponentEnum.TOOL, name=name,
                          default_symbol=default_symbol, payload=payload)


class TestRegister(unittest.TestCase):
    def test_registered_instance_is_retrievable(self) -> None:
        manager = make_manager()
        manager.register(CODE_FOO, make_component())
        self.assertIs(manager.get_instance_obj('foo', appname=APP, new_instance=False),
                      manager._instance_obj_map[CODE_FOO])

    def test_duplicate_register_keeps_first_instance(self) -> None:
        manager = make_manager()
        first = make_component(payload='first')
        manager.register(CODE_FOO, first)
        manager.register(CODE_FOO, make_component(payload='second'))
        got = manager.get_instance_obj('foo', appname=APP, new_instance=False)
        self.assertEqual(got.payload, 'first')

    def test_default_symbol_registers_default_instance(self) -> None:
        manager = make_manager()
        default = make_component(name='foo', default_symbol=True)
        manager.register(CODE_FOO, default)
        self.assertIn('__default_instance__', manager.get_instance_name_list())
        self.assertIs(manager.get_default_instance(), default)
        self.assertIs(manager.get_instance_obj('__default_instance__', new_instance=False),
                      default)

    def test_later_default_symbol_replaces_default_instance(self) -> None:
        manager = make_manager()
        manager.register(CODE_FOO, make_component(name='foo', default_symbol=True))
        second = make_component(name='bar', default_symbol=True)
        manager.register(CODE_BAR, second)
        self.assertIs(manager.get_default_instance(), second)

    def test_unregister_removes_instance(self) -> None:
        manager = make_manager()
        manager.register(CODE_FOO, make_component())
        manager.unregister(CODE_FOO)
        self.assertIsNone(manager.get_instance_obj('foo', appname=APP))

    def test_unregister_missing_name_raises_key_error(self) -> None:
        manager = make_manager()
        with self.assertRaises(KeyError):
            manager.unregister(CODE_FOO)


class TestGetInstanceObj(unittest.TestCase):
    def test_new_instance_returns_independent_copy(self) -> None:
        manager = make_manager()
        manager.register(CODE_FOO, make_component(payload='original'))
        copy_a = manager.get_instance_obj('foo', appname=APP)
        copy_b = manager.get_instance_obj('foo', appname=APP)
        self.assertIsNot(copy_a, copy_b)
        self.assertIsNot(copy_a, manager._instance_obj_map[CODE_FOO])
        self.assertEqual(copy_a.payload, 'original')
        copy_a.payload = 'mutated'
        self.assertEqual(
            manager.get_instance_obj('foo', appname=APP, new_instance=False).payload,
            'original')

    def test_strict_false_returns_none_when_missing(self) -> None:
        manager = make_manager()
        self.assertIsNone(manager.get_instance_obj('missing', appname=APP))

    def test_strict_true_raises_with_actionable_message(self) -> None:
        manager = make_manager()
        with self.assertRaises(ValueError) as ctx:
            manager.get_instance_obj('missing', appname=APP, strict=True)
        message = str(ctx.exception)
        self.assertIn('missing', message)
        self.assertIn(f'{APP}.tool.missing', message)
        self.assertIn('TOOL', message)

    def test_default_instance_lookup_with_new_instance_copy(self) -> None:
        manager = make_manager()
        default = make_component(name='foo', default_symbol=True)
        manager.register(CODE_FOO, default)
        copied = manager.get_instance_obj('__default_instance__', new_instance=True)
        self.assertIsNot(copied, default)
        self.assertEqual(copied.name, 'foo')


class TestInstanceCollections(unittest.TestCase):
    def test_name_and_object_lists_reflect_registrations(self) -> None:
        manager = make_manager()
        foo = make_component(name='foo')
        manager.register(CODE_FOO, foo)
        self.assertIn(CODE_FOO, manager.get_instance_name_list())
        self.assertIn(foo, manager.get_instance_obj_list())
        manager.unregister(CODE_FOO)
        self.assertNotIn(CODE_FOO, manager.get_instance_name_list())
        self.assertNotIn(foo, manager.get_instance_obj_list())


if __name__ == '__main__':
    unittest.main()
