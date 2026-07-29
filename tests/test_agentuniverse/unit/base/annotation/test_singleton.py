import time
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

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
