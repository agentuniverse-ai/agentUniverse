# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Unit tests for grpcio dependency specification and compatibility."""

from pathlib import Path
import unittest

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

from packaging.specifiers import SpecifierSet
from packaging.version import Version


class TestGrpcioDependency(unittest.TestCase):
    """Verify grpcio dependency specification in pyproject.toml."""

    def setUp(self):
        self.root_dir = Path(__file__).resolve().parents[3]
        self.pyproject_path = self.root_dir / "pyproject.toml"

    def test_grpcio_allows_modern_opentelemetry_versions(self):
        """Ensure grpcio is not pinned to 1.63.0 and allows >=1.63.2,<2.0.0."""
        self.assertTrue(self.pyproject_path.exists(), "pyproject.toml not found")
        with open(self.pyproject_path, "rb") as f:
            data = tomllib.load(f)

        dependencies = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
        grpcio_spec = dependencies.get("grpcio")
        self.assertIsNotNone(grpcio_spec, "grpcio not declared in dependencies")

        # The requirement must allow >=1.63.2 to satisfy opentelemetry-exporter-otlp-proto-grpc
        spec = SpecifierSet(grpcio_spec)
        self.assertIn(Version("1.63.2"), spec)
        self.assertIn(Version("1.70.0"), spec)
        self.assertIn(Version("1.84.1"), spec)

        # It must not allow breaking major 2.0.0
        self.assertNotIn(Version("2.0.0"), spec)

        # The previous restrictive pin 1.63.0 must no longer be the only accepted version
        self.assertNotEqual(grpcio_spec, "1.63.0")

    def test_grpc_server_booster_import(self):
        """Verify gRPC server components can be imported without compatibility regressions."""
        import grpc
        from agentuniverse.agent_serve.web.rpc.grpc import grpc_server_booster

        self.assertTrue(hasattr(grpc_server_booster, "AgentUniverseService"))
        self.assertTrue(hasattr(grpc_server_booster, "start_grpc_server"))


if __name__ == "__main__":
    unittest.main()
