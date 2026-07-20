#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Tests for Monitor and AuTraceContext fixes.

1. Monitor.get_llm_token_usage previously did ``.pop('messages')`` on the
   caller's input dict, silently removing messages so later use (retry,
   logging) found it missing. Now uses .get.
2. Monitor.add_token_usage had a bare ``except:`` that swallowed every
   exception (including KeyboardInterrupt) when a token field was not
   addable. Now narrowed to TypeError with a debug log.
3. AuTraceContext.add_current_token_usage_to_parent mutated the shared
   _token_count_dict without the instance lock, losing updates under
   concurrent LLM sub-calls. Now both branches hold the lock.
"""

import unittest
from unittest.mock import MagicMock, patch


class TestMonitorGetLLMTokenUsageNoMutation(unittest.TestCase):
    """get_llm_token_usage must not mutate the caller's llm_input."""

    def test_get_llm_token_usage_does_not_pop_messages(self):
        from agentuniverse.base.util.monitor.monitor import Monitor

        # Build an llm_input whose kwargs contain messages; the LLM output
        # has no usage so the code walks the messages path.
        messages = [{"role": "user", "content": "hello world"}]
        llm_input = {"kwargs": {"messages": messages}}
        llm_obj = MagicMock()
        llm_obj.get_num_tokens.return_value = 2
        output = MagicMock()
        output.usage = None
        output.text = "response"

        Monitor.get_llm_token_usage(output, llm_obj, llm_input)

        # messages must still be present in the caller's dict (the bug: .pop
        # removed it).
        self.assertIn("messages", llm_input["kwargs"],
                      "get_llm_token_usage must not pop messages from the "
                      "caller's input dict")
        self.assertEqual(llm_input["kwargs"]["messages"], messages)


class TestMonitorAddTokenUsageBareExcept(unittest.TestCase):
    """add_token_usage must not swallow non-addable fields silently."""

    def test_non_addable_field_is_skipped_not_crashing(self):
        from agentuniverse.base.util.monitor.monitor import Monitor

        with patch("agentuniverse.base.util.monitor.monitor.AuTraceManager") \
                as trace_mgr, \
             patch("agentuniverse.base.util.monitor.monitor."
                   "FrameworkContextManager") as ctx_mgr:
            trace_mgr.return_value.get_trace_id.return_value = "trace1"
            ctx_mgr.return_value.get_context.return_value = {
                "prompt_tokens": 10,
                "weird_field": "not_a_number",
            }
            # cur_token_usage has a weird_field that can't be added to a str.
            cur = {"prompt_tokens": 5, "weird_field": 5}
            # Must not raise (the bare except caught everything; the narrowed
            # TypeError should still skip the field gracefully).
            Monitor.add_token_usage(cur)
            # The set_context call carries the merged result.
            set_call = ctx_mgr.return_value.set_context.call_args
            result = set_call.args[1]
            self.assertEqual(result["prompt_tokens"], 15)

    def test_add_token_usage_source_does_not_bare_except(self):
        import inspect
        from agentuniverse.base.util.monitor.monitor import Monitor

        src = inspect.getsource(Monitor.add_token_usage)
        # The bare ``except:`` must be gone.
        self.assertNotIn("except:", src,
                         "add_token_usage must not use a bare except; narrow "
                         "to TypeError")
        self.assertIn("except TypeError", src)


class TestAuTraceContextTokenLock(unittest.TestCase):
    """add_current_token_usage_to_parent must hold the instance lock."""

    def test_source_uses_lock_in_parent_branch(self):
        import inspect
        from agentuniverse.base.tracing.au_trace_context import AuTraceContext

        src = inspect.getsource(AuTraceContext.add_current_token_usage_to_parent)
        # Both += branches must be inside `with self._token_count_lock:`.
        # Count the lock acquisitions vs the += operations.
        self.assertGreaterEqual(src.count("with self._token_count_lock"), 2,
                                "both parent-id and parent-span branches must "
                                "hold the lock when mutating the shared dict")

    def test_parent_token_usage_accumulates_under_lock(self):
        from agentuniverse.base.tracing.au_trace_context import AuTraceContext
        from agentuniverse.llm.llm_output import TokenUsage

        ctx = AuTraceContext()
        ctx._token_count_dict = {"parent_span": TokenUsage()}
        # Simulate two concurrent reports to the same parent. TokenUsage
        # stores text_in / text_out; prompt_tokens is a derived property.
        t1 = TokenUsage(text_in=10, text_out=5)
        t2 = TokenUsage(text_in=20, text_out=8)
        ctx.add_current_token_usage_to_parent(t1, parent_span_id="parent_span")
        ctx.add_current_token_usage_to_parent(t2, parent_span_id="parent_span")
        total = ctx._token_count_dict["parent_span"]
        self.assertEqual(total.prompt_tokens, 30)
        self.assertEqual(total.completion_tokens, 13)


if __name__ == "__main__":
    unittest.main(verbosity=2)
