from agentuniverse.agent_serve.web import thread_with_result as thread_module


class RecordingRecoveredContext:
    def __init__(self):
        self.close_calls = 0

    def close(self):
        self.close_calls += 1


def install_recording_context(monkeypatch):
    recovered_context = RecordingRecoveredContext()
    monkeypatch.setattr(
        thread_module.ContextCoordinator,
        "save_context",
        staticmethod(lambda: object()),
    )
    monkeypatch.setattr(
        thread_module.ContextCoordinator,
        "recover_context",
        staticmethod(lambda context: recovered_context),
    )
    return recovered_context


def test_thread_closes_recovered_context(monkeypatch):
    recovered_context = install_recording_context(monkeypatch)
    thread = thread_module.ThreadWithReturnValue(target=lambda: "result")

    thread.start()

    assert thread.result() == "result"
    assert recovered_context.close_calls == 1


def test_executor_submit_closes_recovered_context(monkeypatch):
    recovered_context = install_recording_context(monkeypatch)

    with thread_module.ThreadPoolExecutorWithReturnValue() as executor:
        assert executor.submit(lambda: "result").result() == "result"

    assert recovered_context.close_calls == 1


def test_executor_map_closes_recovered_context(monkeypatch):
    recovered_context = install_recording_context(monkeypatch)

    with thread_module.ThreadPoolExecutorWithReturnValue() as executor:
        assert list(executor.map(lambda value: value * 2, [2])) == [4]

    assert recovered_context.close_calls == 1
