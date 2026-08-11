from types import SimpleNamespace
from unittest import TestCase

from agentuniverse.base.agentuniverse import AgentUniverse
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger


class TestAgentUniverseToolkitPackages(TestCase):

    @staticmethod
    def _scan_packages(core_package):
        app_configer = AppConfiger().load_by_configer(SimpleNamespace(value={
            "CORE_PACKAGE": core_package,
        }))
        agent_universe = AgentUniverse()
        scanned_packages = {}

        def record_scan(package_list, _config_type, component_enum):
            scanned_packages[component_enum] = package_list
            return []

        agent_universe.scan = record_scan
        agent_universe._AgentUniverse__register = lambda *_args: None
        agent_universe._AgentUniverse__scan_and_register(app_configer)
        return scanned_packages

    def test_toolkit_packages_fall_back_to_default_packages(self):
        scanned_packages = self._scan_packages({
            "default": ["example.default"],
            "tool": ["example.tools"],
        })

        self.assertEqual(
            scanned_packages[ComponentEnum.TOOLKIT],
            ["example.default", "agentuniverse.agent.action.toolkit"],
        )
        self.assertEqual(
            scanned_packages[ComponentEnum.TOOL],
            ["example.tools", "agentuniverse.agent.action.tool"],
        )

    def test_explicit_toolkit_packages_include_builtin_toolkits(self):
        scanned_packages = self._scan_packages({
            "default": ["example.default"],
            "tool": ["example.tools"],
            "toolkit": ["example.toolkits"],
        })

        self.assertEqual(
            scanned_packages[ComponentEnum.TOOLKIT],
            ["example.toolkits", "agentuniverse.agent.action.toolkit"],
        )
