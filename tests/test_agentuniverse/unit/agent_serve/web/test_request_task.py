import asyncio
from types import SimpleNamespace

from agentuniverse.agent_serve.web.request_task import (
    EOF_SIGNAL,
    RequestTask,
    TaskStateEnum,
)


def test_async_receive_steps_marks_successful_task_finished():
    async def run_stream():
        request_task = RequestTask.__new__(RequestTask)
        request_task.async_queue = asyncio.Queue()
        request_task.async_queue.put_nowait(EOF_SIGNAL)
        request_task.async_task = asyncio.create_task(asyncio.sleep(0, result={"answer": "done"}))
        request_task.saved = False
        request_task.__request_do__ = SimpleNamespace(
            state=TaskStateEnum.INIT.value,
            result={},
        )

        stream = request_task.async_receive_steps()
        result_chunk = await anext(stream)
        state_at_result = request_task.request_state()
        await stream.aclose()
        return request_task, result_chunk, state_at_result

    request_task, result_chunk, state_at_result = asyncio.run(run_stream())

    assert state_at_result == TaskStateEnum.FINISHED.value
    assert request_task.request_state() == TaskStateEnum.FINISHED.value
    assert request_task.__request_do__.result == {"result": {"answer": "done"}}
    assert '"answer": "done"' in result_chunk
