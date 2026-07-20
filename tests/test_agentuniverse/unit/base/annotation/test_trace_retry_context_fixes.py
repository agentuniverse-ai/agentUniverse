#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Tests for four independent bugs across trace, retry, and context layers.

1. trace.py: _default_agent_wrapper_async popped invocation chain twice
   (once explicitly, once via __exit__), corrupting the caller's chain node.
2. retry.py: raised bare Exception(...) discarding the original exception
   type and traceback.
3. au_trace_context.py: _get_current_span_id used span.context.span_id
   (wrong API) instead of span.get_span_context().span_id.
4. context_archive_utils.py: set a throwaway {} into the context manager
   but returned a different local dict, so mutations were lost.
"""

import unittest
from unittest.mock import MagicMock, patch


class TestTraceAsyncWrapperNoDoublePop(unittest.TestCase):
    """The async agent wrapper must not pop the invocation chain twice."""

    def test_async_wrapper_does_not_explicitly_pop(self):
        import inspect
        from agentuniverse.base.annotation import trace as trace_module

        src = inspect.getsource(trace_module._default_agent_wrapper_async)
        # The bug: an explicit Monitor.pop_invocation_chain() INSIDE the
        # `with InvocationChainContext(...)` block, which __exit__ also pops.
        # The fix removes the explicit pop; the with-block's __exit__ is the
        # sole pop. Check the source no longer has a bare pop before return.
        lines = src.split("\n")
        # Find lines that are inside the with-block and pop.
        pops_in_with = [
            l for l in lines
            if "Monitor.pop_invocation_chain()" in l
            and "return" not in l
            and "#" not in l.split("pop")[0]  # not a comment
        ]
        self.assertEqual(pops_in_with, [],
                         "async agent wrapper must not explicitly pop inside "
                         "the with-block (InvocationChainContext.__exit__ pops)")


class TestRetryPreservesOriginalException(unittest.TestCase):
    """retry must re-raise the original exception, not wrap it."""

    def test_original_exception_type_preserved(self):
        from agentuniverse.base.annotation.retry import retry

        class MyError(Exception):
            pass

        @retry(max_retries=2, delay=0)
        def always_fail():
            raise MyError("boom")

        with self.assertRaises(MyError) as ctx:
            always_fail()
        self.assertIn("boom", str(ctx.exception))

    def test_returns_value_on_success(self):
        from agentuniverse.base.annotation.retry import retry

        @retry(max_retries=3, delay=0)
        def succeeds_on_third_try():
            succeeds_on_third_try.calls += 1
            if succeeds_on_third_try.calls < 3:
                raise ValueError("not yet")
            return "ok"

        succeeds_on_third_try.calls = 0
        result = succeeds_on_third_try()
        self.assertEqual(result, "ok")
        self.assertEqual(succeeds_on_third_try.calls, 3)

    def test_source_does_not_raise_bare_exception(self):
        import inspect
        from agentuniverse.base.annotation.retry import retry

        src = inspect.getsource(retry)
        self.assertNotIn(
            'raise Exception(f"Failed after', src,
            "retry must re-raise the original exception, not a bare Exception")


class TestAuTraceContextGetCurrentSpanId(unittest.TestCase):
    """_get_current_span_id must use get_span_context(), not .context."""

    def test_source_uses_get_span_context(self):
        import inspect
        from agentuniverse.base.tracing.au_trace_context import AuTraceContext

        src = inspect.getsource(AuTraceContext._get_current_span_id)
        self.assertIn("get_span_context().span_id", src)
        # Check that no CODE line (non-comment) uses span.context.span_id.
        code_lines = [l.strip() for l in src.split("\n")
                      if l.strip() and not l.strip().startswith("#")]
        for line in code_lines:
            self.assertNotIn(
                "span.context.span_id", line,
                f"code line must not use span.context.span_id: {line!r}")


class TestContextArchiveUtilsSetSameDict(unittest.TestCase):
    """get_current_context_archive must set the SAME dict it returns."""

    def test_source_sets_context_archive_not_throwaway(self):
        import inspect
        from agentuniverse.base.context import context_archive_utils

        src = inspect.getsource(context_archive_utils.get_current_context_archive)
        # The fix: set_context('context_archive', context_archive) — the same
        # local dict — not set_context('context_archive', {}).
        self.assertIn(
            "set_context('context_archive', context_archive)", src,
            "must set the same dict object that is returned, not a throwaway {}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
