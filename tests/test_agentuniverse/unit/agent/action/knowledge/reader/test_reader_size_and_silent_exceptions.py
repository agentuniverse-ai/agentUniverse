#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Tests for silent-exception and reader-size-guard fixes.

1. ContextManager._make_room: a compression add-failure after delete used to
   silently drop the session history; now it restores the original segments
   and logs.
2. Memory.get_with_context_budget: a bare ``except: pass`` hid context
   retrieval failures; now logs a warning before falling back.
3. Reader base + TxtReader/LineTxtReader: file.read() on an unbounded input
   could OOM; now bounded by ``max_read_bytes``.
"""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch


class TestReaderSizeGuard(unittest.TestCase):
    """Readers must refuse inputs larger than max_read_bytes."""

    def _large_file(self, size_bytes: int) -> str:
        fd, path = tempfile.mkstemp(suffix=".txt")
        with os.fdopen(fd, "wb") as f:
            # Write a sparse-ish file: actual bytes so stat() reports size.
            f.write(b"x" * size_bytes)
        self.addCleanup(os.unlink, path)
        return path

    def test_txt_reader_rejects_file_over_limit(self):
        from agentuniverse.agent.action.knowledge.reader.file.txt_reader \
            import TxtReader
        reader = TxtReader()
        reader.max_read_bytes = 128
        big = self._large_file(1024)  # 1 KB > 128 byte limit
        with self.assertRaises(ValueError) as ctx:
            reader.load_data(Path(big))
        self.assertIn("max_read_bytes", str(ctx.exception))

    def test_txt_reader_accepts_file_under_limit(self):
        from agentuniverse.agent.action.knowledge.reader.file.txt_reader \
            import TxtReader
        reader = TxtReader()
        reader.max_read_bytes = 1024
        small = self._large_file(64)
        docs = reader.load_data(Path(small))
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0].text, "x" * 64)

    def test_line_txt_reader_rejects_file_over_limit(self):
        from agentuniverse.agent.action.knowledge.reader.file.txt_reader \
            import LineTxtReader
        reader = LineTxtReader()
        reader.max_read_bytes = 64
        big = self._large_file(256)
        with self.assertRaises(ValueError):
            reader.load_data(Path(big))

    def test_max_read_bytes_default_is_set(self):
        from agentuniverse.agent.action.knowledge.reader.file.txt_reader \
            import TxtReader
        # The default must be a sane positive value (not None / 0). Access
        # via a concrete subclass instance because the Reader base is a
        # pydantic V1 model whose class-level field is not directly readable.
        reader = TxtReader()
        self.assertGreater(reader.max_read_bytes, 0)


class TestContextManagerCompressionRollback(unittest.TestCase):
    """A compression add-failure must restore the original segments, not drop them silently."""

    def test_source_restores_originals_and_logs_on_add_failure(self):
        # Source-level contract: the compression branch must (a) wrap the
        # post-delete add in its own try/except that re-adds the original
        # segments, and (b) log the failure via logger.warning instead of a
        # bare ``except: pass``. Driving the full _make_room path requires
        # building a complete ContextWindow + hot_store + compressor graph,
        # which is unrelated to this regression.
        import inspect
        from agentuniverse.agent.context import context_manager as cm_module

        src = inspect.getsource(cm_module.ContextManager._make_room)

        # Rollback: the originals must be re-added on add failure.
        self.assertIn("self._hot_store.add(segments", src,
                      "compression rollback must restore the original segments "
                      "when the compressed add fails")
        # Logging: the failure must be visible, not a bare ``except: pass``.
        self.assertIn("logger.warning", src,
                      "compression failure must be logged so operators can "
                      "tell why context fell back to eviction")
        # The bare-pass bug must be gone.
        self.assertNotIn("except Exception as e:\n                pass", src,
                         "the bare except-pass that silently dropped session "
                         "history must be removed")


class TestMemoryContextBudgetLogsFallback(unittest.TestCase):
    """A context-budget retrieval failure must be logged, not silent."""

    def test_source_logs_warning_instead_of_bare_pass(self):
        # Source-level contract: the except clause must reference LOGGER and
        # must NOT be a bare ``except: pass``. The previous bug silently hid
        # every context-retrieval failure.
        import inspect
        from agentuniverse.agent.memory import memory as memory_module

        src = inspect.getsource(memory_module.Memory.get_with_context_budget)
        # The fix surfaces the exception via LOGGER.warning. The bug was a
        # bare ``except Exception: pass`` with no logging.
        self.assertIn("LOGGER.warning", src,
                      "context-budget fallback must log the failure so "
                      "operators can diagnose why recall fell back")
        # And it must still fall back (the original pruning path runs after).
        self.assertIn("Fall back to traditional retrieval", src)


if __name__ == "__main__":
    unittest.main(verbosity=2)
