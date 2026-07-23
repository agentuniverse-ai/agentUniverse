#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Tests for bare except narrowing, raise Exception → ValueError, and request timeout fixes."""

import unittest


class TestRaiseExceptionToValueError(unittest.TestCase):

    def test_sqlite_conversation_uses_value_error(self):
        import inspect
        from agentuniverse.agent.memory.conversation_memory.memory_storage.\
            sqlite_conversation_memory_storage import SqliteMemoryStorage
        src = inspect.getsource(SqliteMemoryStorage._initialize_by_component_configer)
        self.assertIn("ValueError", src)
        self.assertNotIn("raise Exception(", src)

    def test_sql_alchemy_uses_value_error(self):
        import inspect
        from agentuniverse.agent.memory.memory_storage.sql_alchemy_memory_storage \
            import SqlAlchemyMemoryStorage
        src = inspect.getsource(SqlAlchemyMemoryStorage._initialize_by_component_configer)
        self.assertIn("ValueError", src)
        self.assertNotIn("raise Exception(", src)
        # Also check _init_db
        src2 = inspect.getsource(SqlAlchemyMemoryStorage._init_db)
        self.assertIn("ValueError", src2)


class TestBareExceptNarrowed(unittest.TestCase):

    def test_planning_agent_template_narrowed(self):
        import inspect
        from agentuniverse.agent.template.planning_agent_template import \
            PlanningAgentTemplate
        src = inspect.getsource(PlanningAgentTemplate)
        # No bare except: in code lines
        for line in src.split("\n"):
            if line.strip() == "except:":
                self.fail("planning_agent_template still has bare except:")

    def test_financial_indicator_extractor_narrowed(self):
        import os
        here = os.path.dirname(os.path.abspath(__file__))
        for _ in range(10):
            candidate = os.path.join(
                here, "agentuniverse", "agent", "action", "knowledge",
                "doc_processor", "financial_indicator_extractor.py")
            if os.path.exists(candidate):
                break
            here = os.path.dirname(here)
        with open(candidate) as f:
            src = f.read()
        for line in src.split("\n"):
            if line.strip() == "except:":
                self.fail("financial_indicator_extractor still has bare except:")

    def test_au_session_propagator_narrowed(self):
        import os
        here = os.path.dirname(os.path.abspath(__file__))
        for _ in range(10):
            candidate = os.path.join(
                here, "agentuniverse", "base", "tracing", "otel",
                "propagator", "au_session_propagator.py")
            if os.path.exists(candidate):
                break
            here = os.path.dirname(here)
        with open(candidate) as f:
            src = f.read()
        for line in src.split("\n"):
            if line.strip() == "except:":
                self.fail("au_session_propagator still has bare except:")

    def test_framework_context_manager_narrowed(self):
        import os
        here = os.path.dirname(os.path.abspath(__file__))
        for _ in range(10):
            candidate = os.path.join(
                here, "agentuniverse", "base", "context",
                "framework_context_manager.py")
            if os.path.exists(candidate):
                break
            here = os.path.dirname(here)
        with open(candidate) as f:
            src = f.read()
        for line in src.split("\n"):
            if line.strip() == "except:":
                self.fail("framework_context_manager still has bare except:")

    def test_component_base_narrowed(self):
        import inspect
        from agentuniverse.base.component.component_base import ComponentBase
        src = inspect.getsource(ComponentBase.create_copy)
        for line in src.split("\n"):
            if line.strip() == "except:":
                self.fail("component_base.create_copy still has bare except:")


class TestRequestTimeouts(unittest.TestCase):

    def test_pubmed_tool_has_timeout(self):
        import os
        here = os.path.dirname(os.path.abspath(__file__))
        for _ in range(10):
            candidate = os.path.join(
                here, "agentuniverse", "agent", "action", "tool",
                "common_tool", "pubmed_tool.py")
            if os.path.exists(candidate):
                break
            here = os.path.dirname(here)
        with open(candidate) as f:
            src = f.read()
        self.assertIn("timeout=30", src,
                      "pubmed_tool must have timeout on requests")

    def test_github_tool_has_timeout(self):
        import os
        here = os.path.dirname(os.path.abspath(__file__))
        for _ in range(10):
            candidate = os.path.join(
                here, "agentuniverse", "agent", "action", "tool",
                "common_tool", "github_tool.py")
            if os.path.exists(candidate):
                break
            here = os.path.dirname(here)
        with open(candidate) as f:
            src = f.read()
        self.assertIn("timeout=30", src,
                      "github_tool must have timeout on requests")

    def test_dashscope_embedding_has_timeout(self):
        import os
        here = os.path.dirname(os.path.abspath(__file__))
        for _ in range(10):
            candidate = os.path.join(
                here, "agentuniverse", "agent", "action", "knowledge",
                "embedding", "dashscope_embedding.py")
            if os.path.exists(candidate):
                break
            here = os.path.dirname(here)
        with open(candidate) as f:
            src = f.read()
        self.assertIn("timeout", src,
                      "dashscope_embedding must have timeout on requests.post")


if __name__ == "__main__":
    unittest.main(verbosity=2)
