from threading import Event

from agentuniverse.agent_serve.web.thread_with_result import (
    ThreadPoolExecutorWithReturnValue,
)


def test_cancelled_queued_future_does_not_run_callable():
    first_started = Event()
    release_first = Event()
    second_ran = Event()

    def block_worker():
        first_started.set()
        release_first.wait(timeout=2)

    with ThreadPoolExecutorWithReturnValue(max_workers=1) as executor:
        first = executor.submit(block_worker)
        assert first_started.wait(timeout=2)

        second = executor.submit(second_ran.set)
        assert second.cancel()
        release_first.set()

        first.result(timeout=2)

    assert second.cancelled()
    assert not second_ran.is_set()


def test_running_future_cannot_be_cancelled():
    started = Event()
    release = Event()

    def wait_for_release():
        started.set()
        release.wait(timeout=2)
        return "done"

    with ThreadPoolExecutorWithReturnValue(max_workers=1) as executor:
        future = executor.submit(wait_for_release)
        assert started.wait(timeout=2)
        assert not future.cancel()
        release.set()
        assert future.result(timeout=2) == "done"
