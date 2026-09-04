# !/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Unit tests for the AgentUniverse framework bootstrap class.

AgentUniverse is a singleton that manages framework initialization and
component registration.  The tests below cover its deterministic, pure
behaviors: singleton semantics, sub-config path resolution and package name
lookup, without triggering a full framework start.
"""

import pytest

from agentuniverse.base.agentuniverse import AgentUniverse
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.config_type_enum import ConfigTypeEnum


@pytest.fixture(scope="module")
def au_instance():
    """Provide the framework singleton instance."""
    return AgentUniverse()


class TestSingletonBehavior:
    """Tests for the singleton semantics of AgentUniverse."""

    def test_instance_is_shared(self, au_instance):
        assert AgentUniverse() is au_instance

    def test_instance_exposes_scan_and_start(self, au_instance):
        assert callable(au_instance.scan)
        assert callable(au_instance.start)


class TestParseSubConfigPath:
    """Tests for _AgentUniverse__parse_sub_config_path."""

    def test_none_input_returns_none(self, au_instance):
        resolver = au_instance._AgentUniverse__parse_sub_config_path
        assert resolver(None, "/app/config/config.toml") is None

    def test_empty_input_returns_none(self, au_instance):
        resolver = au_instance._AgentUniverse__parse_sub_config_path
        assert resolver("", "/app/config/config.toml") is None

    def test_absolute_path_returned_unchanged(self, au_instance):
        resolver = au_instance._AgentUniverse__parse_sub_config_path
        assert resolver("/etc/au/log.yaml", "/app/config/config.toml") == "/etc/au/log.yaml"

    def test_relative_path_resolved_against_reference(self, au_instance):
        resolver = au_instance._AgentUniverse__parse_sub_config_path
        assert resolver("conf/sub.yaml", "/app/config/config.toml") == "/app/config/conf/sub.yaml"


class TestPackageNameToPath:
    """Tests for _AgentUniverse__package_name_to_path."""

    def test_existing_package_resolves_to_path(self, au_instance):
        converter = au_instance._AgentUniverse__package_name_to_path
        path = converter("agentuniverse.base")
        assert path.endswith("agentuniverse/base")

    def test_missing_package_raises_import_error(self, au_instance):
        converter = au_instance._AgentUniverse__package_name_to_path
        with pytest.raises(ImportError):
            converter("agentuniverse.nonexistent_package_xyz")


class TestScan:
    """Tests for the component scan entry point."""

    def test_scan_with_empty_package_list_returns_empty(self, au_instance):
        assert au_instance.scan([], ConfigTypeEnum.YAML, ComponentEnum.LLM) == []


if __name__ == "__main__":
    pytest.main([__file__, "-s"])
