import time
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/08/13 10:00
# @Author  : kaichuan
# @FileName: test_singleton.py
"""Unit tests for the singleton decorator."""

import pytest

from agentuniverse.base.annotation.singleton import singleton


def test_singleton_constructs_only_once_under_concurrency():
    worker_count = 16
    start = Barrier(worker_count)
    construction_count = 0

    @singleton
    class SharedComponent:
        def __init__(self):
            nonlocal construction_count
            time.sleep(0.02)
            construction_count += 1

    def create_component():
        start.wait()
        return SharedComponent()

    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        instances = list(executor.map(lambda _: create_component(), range(worker_count)))

    assert len({id(instance) for instance in instances}) == 1
    assert construction_count == 1
class TestSingleton:
    """Test the singleton decorator behavior."""

    def test_returns_same_instance(self):
        """Calling the decorated class twice returns the same object."""

        @singleton
        class Config:
            def __init__(self, value):
                self.value = value

        first = Config("a")
        second = Config("b")
        assert first is second
        assert first.value == "a"

    def test_constructor_called_once(self):
        """The underlying __init__ runs only on the first call."""
        calls = []

        @singleton
        class Service:
            def __init__(self):
                calls.append(1)

        Service()
        Service()
        Service()
        assert len(calls) == 1

    def test_kwargs_forwarded_to_init(self):
        """Keyword arguments from the first call reach the constructor."""

        @singleton
        class Client:
            def __init__(self, host, port=80):
                self.host = host
                self.port = port

        client = Client(host="example.com", port=443)
        assert client.host == "example.com"
        assert client.port == 443

    def test_distinct_classes_independent(self):
        """Different decorated classes keep separate instances."""

        @singleton
        class Alpha:
            pass

        @singleton
        class Beta:
            pass

        a1, a2 = Alpha(), Alpha()
        b1 = Beta()
        assert a1 is a2
        assert b1 is not a1
        assert b1.__class__ is Beta.__wrapped__

    def test_wraps_preserves_name(self):
        """The wrapper keeps the original class metadata."""

        @singleton
        class Named:
            pass

        assert Named.__name__ == "Named"
        assert Named.__wrapped__.__name__ == "Named"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
