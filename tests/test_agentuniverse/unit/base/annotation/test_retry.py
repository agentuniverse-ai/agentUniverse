# !/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Unit tests for agentuniverse.base.annotation.retry."""
import pytest

from agentuniverse.base.annotation.retry import retry


class _FlakyCaller:
    """Callable that fails a configurable number of times before succeeding."""

    def __init__(self, failures: int = 0, error: Exception = ValueError("boom")):
        self.failures = failures
        self.error = error
        self.calls = 0

    def __call__(self):
        self.calls += 1
        if self.calls <= self.failures:
            raise self.error
        return "ok"


@pytest.fixture
def recorded_sleeps(monkeypatch):
    """Replace time.sleep with a recorder to keep tests fast and deterministic."""
    sleeps = []
    monkeypatch.setattr("time.sleep", lambda delay: sleeps.append(delay))
    return sleeps


class TestRetry:
    """Tests for the retry decorator."""

    def test_success_without_retry(self, recorded_sleeps):
        caller = _FlakyCaller()

        @retry(max_retries=3, delay=0.1)
        def run():
            return caller()

        assert run() == "ok"
        assert caller.calls == 1
        assert recorded_sleeps == []

    def test_retries_until_success(self, recorded_sleeps):
        caller = _FlakyCaller(failures=2)

        @retry(max_retries=5, delay=0.5)
        def run():
            return caller()

        assert run() == "ok"
        assert caller.calls == 3
        assert recorded_sleeps == [0.5, 0.5]

    def test_exhaustion_raises_with_original_error(self, recorded_sleeps):
        caller = _FlakyCaller(failures=99, error=RuntimeError("broken"))

        @retry(max_retries=3, delay=0.2)
        def run():
            return caller()

        with pytest.raises(Exception) as exc_info:
            run()
        assert caller.calls == 3
        assert "Failed after 3 retries" in str(exc_info.value)
        assert "broken" in str(exc_info.value)
        assert recorded_sleeps == [0.2, 0.2]

    def test_single_retry_allows_one_attempt(self, recorded_sleeps):
        caller = _FlakyCaller(failures=1)

        @retry(max_retries=1, delay=1.0)
        def run():
            return caller()

        with pytest.raises(Exception):
            run()
        assert caller.calls == 1
        assert recorded_sleeps == []

    def test_wrapper_preserves_function_name(self):
        @retry(max_retries=2, delay=0.1)
        def sample_call():
            return 1

        assert sample_call.__name__ == "sample_call"
        assert sample_call() == 1
