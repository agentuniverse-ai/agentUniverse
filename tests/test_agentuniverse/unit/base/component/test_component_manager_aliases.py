from unittest.mock import MagicMock

import pytest

from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.component.component_manager_base import ComponentManagerBase

APP_NAME = "test_app"
TARGET_CODE = "test_app.tool.current"


def make_manager():
    manager = ComponentManagerBase(ComponentEnum.TOOL)
    component = MagicMock()
    component.default_symbol = False
    component.create_copy.return_value = "component-copy"
    manager.register(TARGET_CODE, component)
    return manager, component


def test_alias_uses_normal_copy_and_raw_lookup_behavior():
    manager, component = make_manager()
    manager.register_alias("legacy", "current", appname=APP_NAME)

    assert manager.get_instance_obj("legacy", appname=APP_NAME) == "component-copy"
    assert manager.get_instance_obj("legacy", appname=APP_NAME, new_instance=False) is component


def test_aliases_are_canonicalized_and_introspectable():
    manager, _ = make_manager()
    manager.register_alias("legacy", "current", appname=APP_NAME)
    manager.register_alias("older", "legacy", appname=APP_NAME)

    aliases = manager.get_alias_map()

    assert aliases == {
        "test_app.tool.legacy": TARGET_CODE,
        "test_app.tool.older": TARGET_CODE,
    }
    aliases.clear()
    assert len(manager.get_alias_map()) == 2


def test_alias_collisions_and_missing_targets_are_rejected():
    manager, _ = make_manager()

    with pytest.raises(ValueError, match="name is already in use"):
        manager.register_alias("current", "current", appname=APP_NAME)
    with pytest.raises(ValueError, match="target component.*missing"):
        manager.register_alias("legacy", "missing", appname=APP_NAME)


def test_alias_cycle_attempt_collides_with_canonical_component():
    manager, _ = make_manager()
    manager.register_alias("legacy", "current", appname=APP_NAME)

    with pytest.raises(ValueError, match="name is already in use"):
        manager.register_alias("current", "legacy", appname=APP_NAME)


def test_unregister_alias_keeps_target_component():
    manager, component = make_manager()
    manager.register_alias("legacy", "current", appname=APP_NAME)

    manager.unregister_alias("legacy", appname=APP_NAME)

    assert manager.get_alias_map() == {}
    assert manager.get_instance_obj("current", appname=APP_NAME, new_instance=False) is component
    assert manager.get_instance_obj("legacy", appname=APP_NAME) is None


def test_strict_alias_lookup_preserves_strict_behavior():
    manager, _ = make_manager()
    manager.register_alias("legacy", "current", appname=APP_NAME)
    manager._instance_obj_map.pop(TARGET_CODE)

    with pytest.raises(ValueError, match="legacy.*not registered"):
        manager.get_instance_obj("legacy", appname=APP_NAME, strict=True)
