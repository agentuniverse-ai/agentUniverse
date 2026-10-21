# !/usr/bin/env python3

"""Regression tests for #1189: ComponentBase.create_copy() isolation.

When pydantic ``model_copy(deep=True)`` fails, the previous implementation
fell back to a shallow ``model_copy()``, so mutable sub-objects were shared
with the original. The fallback must use ``copy.deepcopy`` instead.
"""

import threading
import unittest
from typing import Any
from unittest.mock import patch

from pydantic import Field

from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_enum import ComponentEnum


class _DummyComponent(ComponentBase):
    """Minimal ComponentBase subclass with a mutable field for isolation tests."""

    name: str = "dummy"
    tags: list = Field(default_factory=list)


class _LockHoldingComponent(ComponentBase):
    """Component holding a runtime resource that cannot be deep-copied."""

    name: str = "lock_holder"
    tags: list = Field(default_factory=list)
    lock: Any = Field(default_factory=threading.Lock)


class _SharedLockComponent(_LockHoldingComponent):
    """Compatibility pattern: override create_copy to share the runtime resource."""

    def create_copy(self):
        lock = self.lock
        self.lock = None
        try:
            copied = super().create_copy()
        finally:
            self.lock = lock
        copied.lock = lock
        return copied


class TestComponentBaseCreateCopyIsolation(unittest.TestCase):
    def _make_component(self):
        return _DummyComponent(
            component_type=ComponentEnum.DEFAULT,
            tags=["alpha"],
        )

    def test_create_copy_returns_distinct_instance(self):
        component = self._make_component()
        copied = component.create_copy()
        self.assertIsNot(copied, component)
        self.assertEqual(copied.tags, component.tags)

    def test_create_copy_isolates_mutable_fields(self):
        """Mutating the copy must not affect the original (happy path)."""
        component = self._make_component()
        copied = component.create_copy()
        copied.tags.append("beta")
        self.assertEqual(component.tags, ["alpha"])
        self.assertEqual(copied.tags, ["alpha", "beta"])

    def test_create_copy_fallback_still_isolates_on_deep_model_copy_failure(self):
        """When deep model_copy fails, deepcopy fallback must still isolate."""
        component = self._make_component()
        original_model_copy = ComponentBase.model_copy

        def flaky_model_copy(self, *args, **kwargs):
            if kwargs.get("deep", False):
                raise RuntimeError("simulated")
            return original_model_copy(self, *args, **kwargs)

        with patch.object(ComponentBase, "model_copy", flaky_model_copy):
            copied = component.create_copy()

        self.assertIsNot(copied, component)
        self.assertIsNot(copied.tags, component.tags)
        copied.tags.append("gamma")
        self.assertEqual(component.tags, ["alpha"])
        self.assertEqual(copied.tags, ["alpha", "gamma"])

    def test_create_copy_propagates_when_both_deep_paths_fail(self):
        """Both deep paths failing must raise (no silent shallow return)."""
        component = self._make_component()

        def fail_deep_model_copy(self, *args, **kwargs):
            if kwargs.get("deep", False):
                raise RuntimeError("simulated")
            return ComponentBase.model_copy(self, *args, **kwargs)

        with (
            patch.object(ComponentBase, "model_copy", fail_deep_model_copy),
            patch(
                "agentuniverse.base.component.component_base.copy.deepcopy",
                side_effect=TypeError("simulated deepcopy failure"),
            ),
            self.assertRaises(TypeError),
        ):
            component.create_copy()

    def test_create_copy_raises_for_non_deep_copyable_runtime_resource(self):
        """A lock cannot be deep-copied, so create_copy raises instead of returning a shallow copy."""
        component = _LockHoldingComponent(component_type=ComponentEnum.DEFAULT, tags=["alpha"])
        with self.assertRaises(TypeError):
            component.create_copy()

    def test_caller_handles_create_copy_failure(self):
        """Callers that can tolerate a shared instance catch the exception explicitly."""
        component = _LockHoldingComponent(component_type=ComponentEnum.DEFAULT, tags=["alpha"])
        try:
            instance = component.create_copy()
        except TypeError:
            instance = component
        self.assertIs(instance, component)

    def test_override_create_copy_shares_resource_and_isolates_data(self):
        """Subclass override keeps the runtime resource shared but nested data isolated."""
        component = _SharedLockComponent(component_type=ComponentEnum.DEFAULT, tags=["alpha"])
        copied = component.create_copy()
        self.assertIs(copied.lock, component.lock)
        copied.tags.append("beta")
        self.assertEqual(component.tags, ["alpha"])


if __name__ == "__main__":
    unittest.main()
