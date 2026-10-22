"""Check temporary-client entry cleanup, including real SDK stdio cancellation."""

import asyncio
from contextlib import asynccontextmanager, suppress
import os
import sys
from unittest.mock import patch

import anyio
import pytest

from agentuniverse.base.context.mcp_session_manager import MCPTempClient, MCPSessionManager


@asynccontextmanager
async def tracked_resource(events, name):
    """Use real asynchronous cleanup and record its LIFO order."""
    events.append('open ' + name)
    try:
        yield name
    finally:
        await asyncio.sleep(0)
        events.append('close ' + name)


@pytest.mark.parametrize('failure_type', [
    asyncio.CancelledError, SystemExit, KeyboardInterrupt, BaseException, ValueError,
])
def test_failed_entry_closes_resources_before_propagating(failure_type):
    """Partially acquired resources close before the original failure escapes."""
    async def case():
        events = []
        failure = failure_type('entry failed')
        client = MCPTempClient({})
        original_stack = client.exit_stack

        async def connect(*, exit_stack, **kwargs):
            await exit_stack.enter_async_context(tracked_resource(events, 'transport'))
            await exit_stack.enter_async_context(tracked_resource(events, 'session'))
            raise failure

        with patch.object(MCPSessionManager(), 'connect_to_server', new=connect):
            try:
                with pytest.raises(failure_type) as raised:
                    await client.__aenter__()
                assert raised.value is failure
                assert client.exit_stack is original_stack
                assert client.session is None
                assert events == ['open transport', 'open session',
                                  'close session', 'close transport']
            finally:
                # The baseline must not leak its intentionally unfinished entry.
                await client.exit_stack.aclose()

    asyncio.run(case())


@pytest.mark.parametrize('body_failure', [None, ValueError, asyncio.CancelledError])
def test_successful_entry_keeps_resources_until_exit(body_failure):
    """Successful entry retains ownership through normal and exceptional bodies."""
    async def case():
        events = []
        session = object()
        client = MCPTempClient({})

        async def connect(*, exit_stack, **kwargs):
            await exit_stack.enter_async_context(tracked_resource(events, 'transport'))
            return session

        async def use_client():
            async with client as entered:
                assert entered is client and client.session is session
                assert events == ['open transport']
                if body_failure:
                    raise body_failure('body failed')

        with patch.object(MCPSessionManager(), 'connect_to_server', new=connect):
            if body_failure:
                with pytest.raises(body_failure):
                    await use_client()
            else:
                await use_client()
        assert events == ['open transport', 'close transport']

    asyncio.run(case())


PEER = r'''
import json, os, sys, threading
from pathlib import Path
# A failed test cannot leave this test-owned peer running indefinitely.
guard = threading.Timer(15, lambda: os._exit(99))
guard.daemon = True
guard.start()
Path(sys.argv[1]).write_text(str(os.getpid()), encoding='utf-8')
for line in sys.stdin:
    request = json.loads(line)
    if request.get('method') == 'initialize':
        # Deliberately withhold the reply after the real SDK acquires resources.
        Path(sys.argv[2]).write_text('initialize received', encoding='utf-8')
'''


def peer_running(pid):
    """Read the status of this test's child; never send a signal on Windows."""
    if sys.platform == 'win32':
        import pywintypes
        import win32api
        import win32con
        import win32process
        try:
            handle = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION, False, pid)
        except pywintypes.error as error:
            if error.winerror == 87:  # No such process.
                return False
            raise
        try:
            return win32process.GetExitCodeProcess(handle) == 259
        finally:
            handle.Close()
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


async def wait_for_file(path):
    """Wait for a bounded peer handshake barrier rather than guessing a delay."""
    async def wait():
        while not path.exists():
            await asyncio.sleep(0.01)
    await asyncio.wait_for(wait(), timeout=5)


@pytest.mark.parametrize('cancellation', ['asyncio', 'anyio'])
def test_cancelled_real_stdio_entry_reaps_peer_before_raising(tmp_path, cancellation):
    """Cancel a real ClientSession initialization and observe its child process."""
    async def case():
        pid_file = tmp_path / 'peer.pid'
        initialized = tmp_path / 'initialize.received'
        client = MCPTempClient({
            'transport': 'stdio', 'command': sys.executable,
            'args': ['-u', '-c', PEER, str(pid_file), str(initialized)],
        })
        observed = {}

        async def enter():
            with anyio.CancelScope() as scope:
                observed['scope'] = scope
                try:
                    await client.__aenter__()
                except BaseException as error:
                    observed['failure'] = error
                    observed['running_at_failure'] = peer_running(
                        int(pid_file.read_text(encoding='utf-8')))
                    raise
                finally:
                    # Cleanup in the owning task also makes the unfixed test safe.
                    await client.exit_stack.__aexit__(*sys.exc_info())

        task = asyncio.create_task(enter())
        try:
            await wait_for_file(initialized)
            pid = int(pid_file.read_text(encoding='utf-8'))
            assert peer_running(pid)
            if cancellation == 'asyncio':
                task.cancel('cancel initialization')
                with pytest.raises(asyncio.CancelledError):
                    await asyncio.wait_for(task, timeout=5)
            else:
                observed['scope'].cancel()
                await asyncio.wait_for(task, timeout=5)
            assert isinstance(observed['failure'], asyncio.CancelledError)
            assert observed['running_at_failure'] is False
            assert not peer_running(pid)
            assert client.session is None
        finally:
            if not task.done():
                task.cancel()
                with suppress(BaseException):
                    await asyncio.wait_for(task, timeout=5)

    asyncio.run(case())
