# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Tests for GRR work pattern — YAML config, file structure, and syntax validation."""

import ast
import unittest
from pathlib import Path

import yaml


_ROOT = Path(__file__).parent.parent.parent.parent.parent.parent


class TestGRRFilesExist(unittest.TestCase):
    """Verify all GRR-related files exist."""

    def test_grr_work_pattern_py_exists(self):
        self.assertTrue((_ROOT / "agentuniverse/agent/work_pattern/grr_work_pattern.py").exists())

    def test_grr_work_pattern_yaml_exists(self):
        self.assertTrue((_ROOT / "agentuniverse/agent/work_pattern/grr_work_pattern.yaml").exists())

    def test_generating_agent_template_exists(self):
        self.assertTrue((_ROOT / "agentuniverse/agent/template/generating_agent_template.py").exists())

    def test_reviewing_agent_template_exists(self):
        self.assertTrue((_ROOT / "agentuniverse/agent/template/reviewing_agent_template.py").exists())

    def test_rewriting_agent_template_exists(self):
        self.assertTrue((_ROOT / "agentuniverse/agent/template/rewriting_agent_template.py").exists())

    def test_generating_agent_exists(self):
        self.assertTrue((_ROOT / "agentuniverse/agent/default/generating_agent/generating_agent.py").exists())

    def test_generating_agent_yaml_exists(self):
        self.assertTrue((_ROOT / "agentuniverse/agent/default/generating_agent/generating_agent.yaml").exists())

    def test_rewriting_agent_exists(self):
        self.assertTrue((_ROOT / "agentuniverse/agent/default/rewriting_agent/rewriting_agent.py").exists())

    def test_rewriting_agent_yaml_exists(self):
        self.assertTrue((_ROOT / "agentuniverse/agent/default/rewriting_agent/rewriting_agent.yaml").exists())


class TestGRRSyntax(unittest.TestCase):
    """Verify Python files have valid syntax."""

    def _check_syntax(self, rel_path):
        path = _ROOT / rel_path
        try:
            ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError as e:
            self.fail(f"Syntax error in {rel_path}: {e}")

    def test_grr_work_pattern_syntax(self):
        self._check_syntax("agentuniverse/agent/work_pattern/grr_work_pattern.py")

    def test_generating_template_syntax(self):
        self._check_syntax("agentuniverse/agent/template/generating_agent_template.py")

    def test_reviewing_template_syntax(self):
        self._check_syntax("agentuniverse/agent/template/reviewing_agent_template.py")

    def test_rewriting_template_syntax(self):
        self._check_syntax("agentuniverse/agent/template/rewriting_agent_template.py")

    def test_generating_agent_syntax(self):
        self._check_syntax("agentuniverse/agent/default/generating_agent/generating_agent.py")

    def test_rewriting_agent_syntax(self):
        self._check_syntax("agentuniverse/agent/default/rewriting_agent/rewriting_agent.py")


class TestGRRYamlConfig(unittest.TestCase):
    """Verify YAML configs are valid and have correct metadata."""

    def test_grr_work_pattern_yaml_valid(self):
        path = _ROOT / "agentuniverse/agent/work_pattern/grr_work_pattern.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        self.assertEqual(data["name"], "grr_work_pattern")
        self.assertEqual(data["metadata"]["type"], "WORK_PATTERN")
        self.assertEqual(data["metadata"]["class"], "GRRWorkPattern")
        self.assertIn("Generate-Review-Rewrite", data["description"])

    def test_generating_agent_yaml_valid(self):
        path = _ROOT / "agentuniverse/agent/default/generating_agent/generating_agent.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        self.assertEqual(data["metadata"]["type"], "AGENT")
        self.assertEqual(data["metadata"]["class"], "GeneratingAgentTemplate")
        self.assertEqual(data["info"]["name"], "GeneratingAgent")

    def test_rewriting_agent_yaml_valid(self):
        path = _ROOT / "agentuniverse/agent/default/rewriting_agent/rewriting_agent.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        self.assertEqual(data["metadata"]["type"], "AGENT")
        self.assertEqual(data["metadata"]["class"], "RewritingAgentTemplate")
        self.assertEqual(data["info"]["name"], "RewritingAgent")


class TestGRRCodeStructure(unittest.TestCase):
    """Verify GRR code structure matches PEER pattern."""

    def test_grr_work_pattern_has_invoke_method(self):
        """GRRWorkPattern must have invoke() like PEER's PeerWorkPattern."""
        path = _ROOT / "agentuniverse/agent/work_pattern/grr_work_pattern.py"
        tree = ast.parse(path.read_text(encoding="utf-8"))
        class_def = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == "GRRWorkPattern"]
        self.assertEqual(len(class_def), 1, "GRRWorkPattern class not found")
        methods = {n.name for n in ast.walk(class_def[0]) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
        for required in ["invoke", "async_invoke", "_validate_work_pattern_members", "set_by_agent_model"]:
            self.assertIn(required, methods, f"Missing method: {required}")

    def test_grr_work_pattern_has_three_agents(self):
        """GRRWorkPattern must declare generating, reviewing, rewriting agents."""
        path = _ROOT / "agentuniverse/agent/work_pattern/grr_work_pattern.py"
        tree = ast.parse(path.read_text(encoding="utf-8"))
        class_def = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == "GRRWorkPattern"]
        self.assertEqual(len(class_def), 1)
        # Check for agent attribute annotations
        assigns = [n for n in ast.walk(class_def[0]) if isinstance(n, ast.AnnAssign)]
        agent_names = {n.target.id for n in assigns if isinstance(n.target, ast.Name)}
        for required in ["generating", "reviewing", "rewriting"]:
            self.assertIn(required, agent_names, f"Missing agent annotation: {required}")

    def test_generating_template_has_required_methods(self):
        """GeneratingAgentTemplate must implement input_keys, output_keys, parse_input, parse_result."""
        path = _ROOT / "agentuniverse/agent/template/generating_agent_template.py"
        tree = ast.parse(path.read_text(encoding="utf-8"))
        class_def = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == "GeneratingAgentTemplate"]
        self.assertEqual(len(class_def), 1)
        methods = {n.name for n in ast.walk(class_def[0]) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
        for required in ["input_keys", "output_keys", "parse_input", "parse_result"]:
            self.assertIn(required, methods, f"Missing method: {required}")

    def test_rewriting_template_has_required_methods(self):
        """RewritingAgentTemplate must implement input_keys, output_keys, parse_input, parse_result."""
        path = _ROOT / "agentuniverse/agent/template/rewriting_agent_template.py"
        tree = ast.parse(path.read_text(encoding="utf-8"))
        class_def = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == "RewritingAgentTemplate"]
        self.assertEqual(len(class_def), 1)
        methods = {n.name for n in ast.walk(class_def[0]) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
        for required in ["input_keys", "output_keys", "parse_input", "parse_result"]:
            self.assertIn(required, methods, f"Missing method: {required}")

    def test_reviewing_template_has_required_methods(self):
        """ReviewingAgentTemplate must implement required methods."""
        path = _ROOT / "agentuniverse/agent/template/reviewing_agent_template.py"
        tree = ast.parse(path.read_text(encoding="utf-8"))
        class_def = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == "ReviewingAgentTemplate"]
        self.assertEqual(len(class_def), 1)
        methods = {n.name for n in ast.walk(class_def[0]) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
        for required in ["input_keys", "output_keys", "parse_input", "parse_result"]:
            self.assertIn(required, methods, f"Missing method: {required}")

    def test_default_agents_are_simple_subclasses(self):
        """Default agents should be thin wrappers around templates (like PEER)."""
        for agent_file, template_class in [
            ("agentuniverse/agent/default/generating_agent/generating_agent.py", "GeneratingAgentTemplate"),
            ("agentuniverse/agent/default/rewriting_agent/rewriting_agent.py", "RewritingAgentTemplate"),
        ]:
            path = _ROOT / agent_file
            tree = ast.parse(path.read_text(encoding="utf-8"))
            class_defs = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
            self.assertGreaterEqual(len(class_defs), 1, f"No class in {agent_file}")
            bases = [b.id for b in class_defs[0].bases if isinstance(b, ast.Name)]
            self.assertIn(template_class, bases,
                          f"{agent_file} should inherit from {template_class}, got {bases}")


class TestGRRWorkFlow(unittest.TestCase):
    """Verify GRR invoke flow structure via AST analysis."""

    def test_invoke_has_generate_review_rewrite_loop(self):
        """invoke() should contain a loop calling generate→review→[rewrite]."""
        path = _ROOT / "agentuniverse/agent/work_pattern/grr_work_pattern.py"
        tree = ast.parse(path.read_text(encoding="utf-8"))
        class_def = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == "GRRWorkPattern"][0]
        invoke = [n for n in ast.walk(class_def) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == "invoke"][0]

        # Check for for-loop (iteration)
        loops = [n for n in ast.walk(invoke) if isinstance(n, ast.For)]
        self.assertGreaterEqual(len(loops), 1, "invoke() must contain a for loop for iterations")

        # Check for calls to _invoke_generating, _invoke_reviewing, _invoke_rewriting
        calls = set()
        for node in ast.walk(invoke):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                calls.add(node.func.attr)
        for required in ["_invoke_generating", "_invoke_reviewing"]:
            self.assertIn(required, calls, f"invoke() must call {required}")
        # _invoke_rewriting is only called when score < threshold, check it exists
        self.assertIn("_invoke_rewriting", calls, "invoke() must call _invoke_rewriting conditionally")

    def test_invoke_checks_score_threshold(self):
        """invoke() should check reviewing_result score against eval_threshold."""
        path = _ROOT / "agentuniverse/agent/work_pattern/grr_work_pattern.py"
        source = path.read_text(encoding="utf-8")
        self.assertIn("eval_threshold", source, "Missing eval_threshold parameter")
        self.assertIn("score", source, "Missing score check")
        self.assertIn("break", source, "Missing early exit on high score")


if __name__ == "__main__":
    unittest.main()
