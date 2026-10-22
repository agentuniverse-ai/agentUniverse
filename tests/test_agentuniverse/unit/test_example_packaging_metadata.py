from pathlib import Path
from unittest import TestCase

import tomli

REPOSITORY_ROOT = Path(__file__).parents[3]
EXAMPLE_PROJECTS = (
    "examples/sample_apps/data_agent_app",
    "examples/sample_apps/difizen_app",
    "examples/sample_apps/discussion_group_app",
    "examples/sample_apps/openai_protocol_app",
    "examples/sample_apps/peer_agent_app",
    "examples/sample_apps/rag_app",
    "examples/sample_apps/react_agent_app",
    "examples/sample_apps/toolkit_demo_app",
    "examples/sample_apps/translation_agent_app",
    "examples/sample_apps/workflow_agent_app",
    "examples/third_party_examples/apps/app_with_goole_search_tool",
    "examples/third_party_examples/apps/medical_consultation_assistant_app",
)


class TestExamplePackagingMetadata(TestCase):

    def test_example_poetry_metadata_matches_each_project(self):
        for relative_path in EXAMPLE_PROJECTS:
            project_path = REPOSITORY_ROOT / relative_path
            with self.subTest(project=relative_path):
                with (project_path / "pyproject.toml").open("rb") as file:
                    poetry = tomli.load(file)["tool"]["poetry"]

                self.assertEqual(poetry["name"], project_path.name)
                self.assertEqual(
                    poetry["repository"],
                    f"https://github.com/agentuniverse-ai/agentUniverse/tree/master/{relative_path}",
                )

                self.assertEqual(len(poetry["packages"]), 1)
                package = poetry["packages"][0]
                self.assertEqual(package["include"], project_path.name)
                self.assertEqual(package["from"], "..")

                with (project_path / "pyproject.toml").open("rb") as file:
                    pyproject = tomli.load(file)
                self.assertEqual(
                    pyproject["tool"]["coverage"]["run"]["source"],
                    [project_path.name],
                )

                package_path = project_path / package["from"] / package["include"]
                self.assertTrue(package_path.is_dir())
                self.assertTrue((package_path / "__init__.py").is_file())

                readme = poetry.get("readme")
                if readme:
                    self.assertTrue((project_path / readme).is_file())
