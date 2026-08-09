#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Tests for small bugs: Claude print / parse_result, Excel use-after-close,
and stream_callback None.get chains.

The Claude fixes are verified at the source level (the anthropic/langchain
import chain is heavy and version-sensitive, so a behavioural test would
couple to unrelated dependency drift). Excel and stream_callback are tested
behaviourally.
"""

import unittest
from unittest.mock import MagicMock


class TestClaudeSourceFixes(unittest.TestCase):
    """parse_result must return an LLMOutput (never None); no print(chunk).

    Read the source file directly to avoid importing the module, whose
    langchain_anthropic dependency chain is version-sensitive and unrelated
    to this fix.
    """

    _SOURCE_PATH = (
        "agentuniverse/llm/default/claude_llm.py"
    )

    @classmethod
    def _source(cls) -> str:
        import os
        # Walk up from this test file to the repo root.
        here = os.path.dirname(os.path.abspath(__file__))
        for _ in range(8):
            candidate = os.path.join(here, *cls._SOURCE_PATH.split("/"))
            if os.path.exists(candidate):
                with open(candidate, encoding="utf-8") as f:
                    return f.read()
            here = os.path.dirname(here)
        raise FileNotFoundError(cls._SOURCE_PATH)

    def test_agenerate_stream_result_has_no_print(self):
        src = self._source()
        # The stray ``print(chunk)`` dumped every streaming chunk to stdout,
        # including PII-bearing content, and was never intended to ship.
        # Match the specific streaming-branch form, not a comment.
        self.assertNotIn(
            "async for chunk in chat_completion:\n            print(chunk)",
            src,
            "agenerate_stream_result must not print each chunk")

    def test_parse_result_does_not_return_none_on_empty_text(self):
        src = self._source()
        # The previous form did ``if not text:\n            return`` (implicit
        # None), which callers do not expect. The fix returns an LLMOutput.
        self.assertNotIn(
            "if not text:\n            return\n", src,
            "parse_result must not implicitly return None on empty text; "
            "return an empty LLMOutput instead")
        # And the fix returns LLMOutput on the empty path.
        self.assertIn("return LLMOutput(text=''", src)


class TestExcelGetInfoUseAfterClose(unittest.TestCase):
    """_get_excel_info must cache sheetnames before close()."""

    def test_sheet_names_cached_before_workbook_close(self):
        import inspect
        from agentuniverse.agent.action.tool.common_tool import excel_tool

        src = inspect.getsource(excel_tool.ExcelTool._get_excel_info)
        # The fix caches sheet_names into a local BEFORE workbook.close();
        # the return then uses the cached list, not workbook.sheetnames.
        self.assertIn("sheet_names = list(workbook.sheetnames)", src)
        self.assertIn("workbook.close()", src)
        # Confirm the close happens AFTER the cache line.
        self.assertLess(
            src.index("sheet_names = list(workbook.sheetnames)"),
            src.index("workbook.close()"),
            "sheet_names must be cached before workbook.close() to avoid "
            "use-after-close")
        # And the return uses the cached local, not workbook.sheetnames.
        self.assertIn('"total_sheets": len(sheet_names)', src)
        self.assertIn('"sheet_names": sheet_names', src)


class TestStreamCallbackPairId(unittest.TestCase):
    """_pair_id must not crash when run_id is missing."""

    def test_pair_id_handles_missing_run_id(self):
        from agentuniverse.agent.plan.planner.react_planner.stream_callback \
            import _pair_id
        from uuid import UUID

        # Missing run_id (the bug: kwargs.get('run_id') returned None, then
        # .hex raised AttributeError).
        pid = _pair_id("tool", None)
        self.assertTrue(pid.startswith("tool_"))
        self.assertEqual(len(pid), len("tool_") + 32)  # uuid4 hex

        # Missing run_id as a non-UUID value (some adapters pass strings).
        pid2 = _pair_id("tool", "not-a-uuid")
        self.assertTrue(pid2.startswith("tool_"))

        # Real UUID still produces the stable hex form.
        u = UUID("12345678-1234-1234-1234-123456789abc")
        pid3 = _pair_id("tool", u)
        self.assertEqual(pid3, f"tool_{u.hex}")

    def test_on_tool_end_uses_safe_pair_id(self):
        # The buggy form was specifically in on_tool_end, which receives
        # run_id via **kwargs (not a typed positional arg). on_tool_start
        # uses a typed `run_id: UUID` positional, so .hex is safe there.
        import inspect
        from agentuniverse.agent.plan.planner.react_planner \
            import stream_callback as sc_module

        for cls_name in ("StreamOutPutCallbackHandler",
                         "OpenAIProtocolStreamOutPutCallbackHandler"):
            cls = getattr(sc_module, cls_name)
            src = inspect.getsource(cls.on_tool_end)
            self.assertNotIn(
                "kwargs.get('run_id').hex", src,
                f"{cls_name}.on_tool_end must use _pair_id, not the bare "
                "kwargs.get('run_id').hex chain")


class TestStreamCallbackOnLLMEndGuards(unittest.TestCase):
    """on_llm_end must not crash on empty generations."""

    def test_on_llm_end_handles_empty_generations(self):
        from agentuniverse.agent.plan.planner.react_planner.stream_callback \
            import InvokeCallbackHandler
        from uuid import uuid4

        handler = InvokeCallbackHandler(source="src", llm_name="llm")
        # Empty generations list (LLM error / cancel) — previously
        # response.generations[0][0].text raised IndexError.
        response = MagicMock()
        response.generations = []
        with unittest.mock.patch(
            "agentuniverse.agent.plan.planner.react_planner."
            "stream_callback.ConversationMemoryModule"):
            # Should not raise.
            handler.on_llm_end(response, run_id=uuid4())

    def test_on_llm_end_handles_nested_empty(self):
        from agentuniverse.agent.plan.planner.react_planner.stream_callback \
            import InvokeCallbackHandler
        from uuid import uuid4

        handler = InvokeCallbackHandler(source="src", llm_name="llm")
        response = MagicMock()
        response.generations = [[]]  # outer non-empty, inner empty
        with unittest.mock.patch(
            "agentuniverse.agent.plan.planner.react_planner."
            "stream_callback.ConversationMemoryModule"):
            handler.on_llm_end(response, run_id=uuid4())


class TestStreamOutPutOnLLMNewTokenChunkGuard(unittest.TestCase):
    """on_llm_new_token must not crash when chunk is None."""

    def test_on_llm_new_token_handles_none_chunk(self):
        import asyncio
        from uuid import uuid4
        from agentuniverse.agent.plan.planner.react_planner.stream_callback \
            import StreamOutPutCallbackHandler

        queue = asyncio.Queue()
        handler = StreamOutPutCallbackHandler(queue, agent_info={})
        # chunk=None is permitted by the Optional type; the previous code
        # did chunk.text unconditionally and raised AttributeError.
        handler.on_llm_new_token("the_token", chunk=None, run_id=uuid4())
        item = queue.get_nowait()
        # Falls back to the positional token argument.
        self.assertEqual(item["data"]["chunk"], "the_token")


if __name__ == "__main__":
    unittest.main(verbosity=2)
