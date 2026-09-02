# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/01/05 10:00
# @Author  : kaichuan
# @FileName: test_retry.py
"""Unit tests for the retry decorator in base.annotation.retry."""

from unittest import mock

import pytest

from agentuniverse.base.annotation.retry import retry


class TestRetryDecorator:
    """Test the retry decorator behavior."""

    @pytest.fixture(autouse=True)
    def no_sleep(self):
        """Avoid real delays by patching time.sleep inside the module."""
        with mock.patch("agentuniverse.base.annotation.retry.time.sleep") as m:
            yield m

    def test_success_first_try_returns_value(self, no_sleep):
        """A function that succeeds immediately returns its value."""
        @retry(max_retries=3, delay=0.1)
        def ok():
            return "value"

        assert ok() == "value"
        no_sleep.assert_not_called()

    def test_success_after_failures(self, no_sleep):
        """The decorator retries until the wrapped function succeeds."""
        calls = {"n": 0}

        @retry(max_retries=5, delay=0.1)
        def flaky():
            calls["n"] += 1
            if calls["n"] < 3:
                raise ValueError("not yet")
            return "done"

        assert flaky() == "done"
        assert calls["n"] == 3
        # Two failures before success -> two sleeps of the configured delay
        assert no_sleep.call_count == 2
        no_sleep.assert_called_with(0.1)

    def test_exhausted_retries_raises(self, no_sleep):
        """After max_retries failed attempts a single Exception is raised."""
        @retry(max_retries=3, delay=0.1)
        def always_fails():
            raise RuntimeError("boom")

        with pytest.raises(Exception, match="Failed after 3 retries"):
            always_fails()
        with pytest.raises(Exception, match="boom"):
            always_fails()
        assert no_sleep.call_count == 4

    def test_single_attempt_no_sleep_on_final_failure(self, no_sleep):
        """With max_retries=1 no sleep occurs before re-raising."""
        @retry(max_retries=1)
        def fails():
            raise KeyError("k")

        with pytest.raises(Exception, match="Failed after 1 retries"):
            fails()
        no_sleep.assert_not_called()

    def test_preserves_function_metadata(self):
        """functools.wraps keeps the wrapped function's name and docstring."""
        @retry(max_retries=2, delay=0.1)
        def documented():
            """A documented helper."""

        assert documented.__name__ == "documented"
        assert documented.__doc__ == "A documented helper."

    def test_arguments_and_kwargs_forwarded(self, no_sleep):
        """Positional and keyword arguments are passed through unchanged."""
        @retry(max_retries=2, delay=0.1)
        def add(a, b=1):
            return a + b

        assert add(1, b=2) == 3
        assert add(5) == 6
