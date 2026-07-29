#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import asyncio
import builtins
import unittest
from unittest.mock import AsyncMock, Mock, patch

from agentuniverse.agent_serve.web.request_task import RequestTask


class RequestTaskTest(unittest.IsolatedAsyncioTestCase):
    async def test_async_receive_steps_logs_timeout_without_printing(self):
        task = object.__new__(RequestTask)
        task.async_queue = Mock()
        task.async_queue.get = AsyncMock()
        task.async_task = Mock(done=Mock(return_value=True))
        task.next_state = Mock()

        with patch("agentuniverse.agent_serve.web.request_task.asyncio.wait_for",
                   side_effect=asyncio.TimeoutError), \
                patch("agentuniverse.agent_serve.web.request_task.asyncio.sleep",
                      new=AsyncMock()), \
                patch("agentuniverse.agent_serve.web.request_task.LOGGER") as mock_logger, \
                patch.object(builtins, "print") as mock_print:
            async for _ in task.async_receive_steps():
                pass

        mock_logger.debug.assert_called_once_with(
            "Waiting for async request data timed out. Retrying..."
        )
        mock_logger.error.assert_called_once_with("Task finished without EOF")
        mock_print.assert_not_called()


if __name__ == "__main__":
    unittest.main()
