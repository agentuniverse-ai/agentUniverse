"""Regression coverage for automatic agent modules under repeated directory names."""
import importlib
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

from agentuniverse.base.config.component_configer.configers.agent_configer import AgentConfiger
from agentuniverse.base.config.configer import Configer
from agentuniverse.base.util.system_util import get_module_path


class TestAgentModuleRoot(unittest.TestCase):
    """Use real package files and YAML loading, with only the app root supplied."""

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.base = Path(self.directory.name)
        self.package = 'au_module_root_fixture'

    def make_agent(self, root, relative=('intelligence', 'agents'), metadata=''):
        directory = root
        directory.mkdir(parents=True, exist_ok=True)
        (directory / '__init__.py').touch()
        for part in relative:
            directory /= part
            directory.mkdir(exist_ok=True)
            (directory / '__init__.py').touch()
        python_path = directory / 'demo_agent.py'
        python_path.write_text('MARKER = "local agent"\n', encoding='utf-8')
        yaml_path = directory / 'demo_agent.yaml'
        yaml_path.write_text('info:\n  name: demo_agent\n' + metadata, encoding='utf-8')
        return yaml_path, python_path

    def load_agent(self, root, yaml_path):
        with mock.patch(
                'agentuniverse.base.config.component_configer.configers.'
                'agent_configer.get_project_root_path', return_value=root):
            return AgentConfiger().load_by_configer(Configer(str(yaml_path)).load())

    def assert_imports_agent(self, root, yaml_path, python_path, expected):
        agent = self.load_agent(root, yaml_path)
        with mock.patch.object(sys, 'path', [str(root.parent), *sys.path]):
            importlib.invalidate_caches()
            try:
                module = importlib.import_module(agent.metadata_module)
                self.assertEqual(expected, agent.metadata_module)
                self.assertEqual(python_path.resolve(), Path(module.__file__).resolve())
                self.assertEqual('local agent', module.MARKER)
            finally:
                for name in list(sys.modules):
                    if name == self.package or name.startswith(self.package + '.'):
                        del sys.modules[name]

    def test_ancestor_with_same_name_does_not_become_package_root(self):
        root = self.base / self.package / 'workspace' / self.package
        yaml_path, python_path = self.make_agent(root)
        self.assert_imports_agent(
            root, yaml_path, python_path,
            f'{self.package}.intelligence.agents.demo_agent')

    def test_nested_same_name_package_is_retained(self):
        root = self.base / 'workspace' / self.package
        yaml_path, python_path = self.make_agent(root, ('intelligence', self.package))
        self.assert_imports_agent(
            root, yaml_path, python_path,
            f'{self.package}.intelligence.{self.package}.demo_agent')

    def test_repeated_names_above_and_below_root(self):
        root = self.base / self.package / 'workspace' / self.package
        yaml_path, python_path = self.make_agent(root, ('intelligence', self.package))
        self.assert_imports_agent(
            root, yaml_path, python_path,
            f'{self.package}.intelligence.{self.package}.demo_agent')

    def test_existing_two_argument_helper_remains_supported(self):
        root = self.base / self.package
        yaml_path, _ = self.make_agent(root)
        self.assertEqual(
            f'{self.package}.intelligence.agents.demo_agent',
            get_module_path(str(yaml_path), self.package))

    def test_explicit_module_is_preserved(self):
        root = self.base / self.package / 'workspace' / self.package
        yaml_path, _ = self.make_agent(
            root, metadata='metadata:\n  module: explicit.package.agent\n')
        self.assertEqual('explicit.package.agent', self.load_agent(root, yaml_path).metadata_module)

    def test_explicit_meta_class_does_not_infer_a_module(self):
        root = self.base / self.package / 'workspace' / self.package
        yaml_path, _ = self.make_agent(root, metadata='meta_class: explicit.package.Agent\n')
        agent = self.load_agent(root, yaml_path)
        self.assertIsNone(agent.metadata_module)
        self.assertEqual('explicit.package.Agent', agent.meta_class)

    def test_missing_python_sibling_still_fails(self):
        root = self.base / self.package
        yaml_path, python_path = self.make_agent(root)
        python_path.unlink()
        with self.assertRaisesRegex(Exception, 'Corresponding Python file not found'):
            self.load_agent(root, yaml_path)

    def test_inferred_agent_must_be_inside_the_known_project(self):
        root = self.base / self.package
        yaml_path, _ = self.make_agent(self.base / 'other' / self.package)
        with self.assertRaisesRegex(Exception, 'outside the project root'):
            self.load_agent(root, yaml_path)

    def test_root_level_agent_has_no_extra_module_segment(self):
        root = self.base / self.package
        yaml_path, python_path = self.make_agent(root, ())
        self.assert_imports_agent(
            root, yaml_path, python_path, f'{self.package}.demo_agent')
