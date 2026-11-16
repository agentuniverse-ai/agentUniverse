"""Command lookup handles must survive later invocations on reused threads."""
import json
import threading
from unittest.mock import patch

from agentuniverse.agent.action.tool.common_tool import run_command_tool as command_module
from agentuniverse.agent.action.tool.common_tool.command_status_tool import CommandStatusTool
from agentuniverse.agent.action.tool.common_tool.run_command_tool import RunCommandTool


def test_blocking_commands_keep_separate_results_across_tool_instances():
    first = json.loads(RunCommandTool(allow_command_execution=True).execute('echo first'))
    second = json.loads(RunCommandTool(allow_command_execution=True).execute('echo second'))

    assert first['thread_id'] != second['thread_id']
    status = CommandStatusTool()
    for result, expected in [(first, 'first'), (second, 'second')]:
        stored = json.loads(status.execute(str(result['thread_id'])))
        assert stored['status'] == 'completed'
        assert stored['stdout'].strip() == expected


def test_disabled_invocation_does_not_replace_completed_command():
    completed = json.loads(RunCommandTool(allow_command_execution=True).execute('echo retained'))
    disabled = json.loads(RunCommandTool().execute('echo never-executed'))

    assert disabled['status'] == 'error'
    assert disabled['thread_id'] != completed['thread_id']
    stored = json.loads(CommandStatusTool().execute(completed['thread_id']))
    assert stored['status'] == 'completed'
    assert stored['stdout'].strip() == 'retained'


def test_finished_background_commands_keep_their_original_handles():
    threads = []
    real_thread = threading.Thread

    def capture_thread(*args, **kwargs):
        thread = real_thread(*args, **kwargs)
        threads.append(thread)
        return thread

    tool = RunCommandTool(allow_command_execution=True)
    results = []
    with patch.object(command_module.threading, 'Thread', side_effect=capture_thread):
        for word in ['background-first', 'background-second']:
            result = json.loads(tool.execute(f'echo {word}', blocking=False))
            threads[-1].join(timeout=5)
            assert not threads[-1].is_alive()
            results.append((result['thread_id'], word))

    assert results[0][0] != results[1][0]
    for handle, expected in results:
        stored = json.loads(CommandStatusTool().execute(handle))
        assert stored['status'] == 'completed'
        assert stored['stdout'].strip() == expected


def test_concurrent_callers_keep_all_command_results():
    from concurrent.futures import ThreadPoolExecutor

    def run(index):
        result = json.loads(RunCommandTool(allow_command_execution=True).execute(f'echo job-{index}'))
        return result['thread_id'], f'job-{index}'

    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(run, range(12)))

    assert len({handle for handle, _ in results}) == len(results)
    for handle, expected in results:
        stored = json.loads(CommandStatusTool().execute(handle))
        assert stored['status'] == 'completed'
        assert stored['stdout'].strip() == expected
