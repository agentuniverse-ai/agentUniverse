#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Tests for agent template None.get guards + instrumentor bare except fix."""

import unittest


class TestAgentTemplateNoneGuard(unittest.TestCase):

    def test_react_agent_template_uses_safe_get(self):
        import inspect
        from agentuniverse.agent.template.react_agent_template import \
            ReActAgentTemplate
        src = inspect.getsource(ReActAgentTemplate)
        self.assertIn("profile.get('llm_model', {})", src)
        # The old unsafe form should not appear in code lines.
        code_lines = [l for l in src.split("\n")
                      if l.strip() and not l.strip().startswith("#")]
        for line in code_lines:
            self.assertNotIn(
                "profile.get('llm_model').get('name')", line,
                f"react_agent_template must use safe .get: {line!r}")

    def test_openai_protocol_template_uses_safe_get(self):
        import inspect
        from agentuniverse.agent.template.openai_protocol_template import \
            OpenAIProtocolTemplate
        src = inspect.getsource(OpenAIProtocolTemplate)
        self.assertIn("profile.get('llm_model', {})", src)

    def test_slave_rag_template_uses_value_error(self):
        import inspect
        from agentuniverse.agent.template.slave_rag_agent_template import \
            SlaveRagAgentTemplate
        src = inspect.getsource(SlaveRagAgentTemplate)
        self.assertIn("ValueError", src)
        self.assertNotIn("raise Exception(", src)


class TestLLMInstrumentorBareExcept(unittest.TestCase):

    def test_cleanup_uses_specific_except(self):
        import os
        # Walk up from this test file to find the repo root, then navigate
        # to the llm_instrumentor source.
        here = os.path.dirname(os.path.abspath(__file__))
        for _ in range(10):
            candidate = os.path.join(
                here, "agentuniverse", "base", "tracing", "otel",
                "instrumentation", "llm", "llm_instrumentor.py")
            if os.path.exists(candidate):
                filepath = candidate
                break
            here = os.path.dirname(here)
        else:
            self.skipTest("Could not locate llm_instrumentor.py")

        with open(filepath, encoding="utf-8") as f:
            src = f.read()
        start = src.index("def cleanup(self):")
        end = src.index("def ", start + 10)
        cleanup_src = src[start:end]
        self.assertNotIn("except:", cleanup_src,
                          "LLMSpanManager.cleanup must not use bare except:")
        self.assertIn("except Exception", cleanup_src)


if __name__ == "__main__":
    unittest.main(verbosity=2)
