import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

from agentuniverse.agent.action.tool.common_tool.request_tool import RequestTool


class RequestToolTest(unittest.TestCase):
    """Test cases for RequestTool synchronous execution."""

    def test_execute_accepts_lowercase_method(self) -> None:
        requests_wrapper = SimpleNamespace(
            get=Mock(return_value='response body')
        )
        tool = RequestTool(
            method='get',
            json_parser=False
        )
        tool.requests_wrapper = requests_wrapper

        result = tool.execute('"https://example.com/resource"')

        self.assertEqual(result, 'response body')
        requests_wrapper.get.assert_called_once_with(
            'https://example.com/resource'
        )


class RequestToolAsyncTest(unittest.IsolatedAsyncioTestCase):
    """Test cases for RequestTool asynchronous execution."""

    async def test_async_get_uses_async_requests_wrapper(self) -> None:
        requests_wrapper = SimpleNamespace(
            aget=AsyncMock(return_value='response body')
        )
        tool = RequestTool(
            method='GET',
            json_parser=False
        )
        tool.requests_wrapper = requests_wrapper

        result = await tool.async_execute('"https://example.com/resource"')

        self.assertEqual(result, 'response body')
        requests_wrapper.aget.assert_awaited_once_with(
            'https://example.com/resource'
        )

    async def test_async_post_parses_json_input(self) -> None:
        requests_wrapper = SimpleNamespace(
            apost=AsyncMock(return_value={'created': True})
        )
        tool = RequestTool(
            method='POST',
            json_parser=True
        )
        tool.requests_wrapper = requests_wrapper

        result = await tool.async_execute(
            '{"url": "https://example.com/items", '
            '"data": {"name": "agentUniverse"}}'
        )

        self.assertEqual(result, {'created': True})
        requests_wrapper.apost.assert_awaited_once_with(
            'https://example.com/items',
            data={'name': 'agentUniverse'}
        )

    async def test_async_execute_rejects_unsupported_method(self) -> None:
        tool = RequestTool(
            method='PATCH',
            json_parser=False
        )
        tool.requests_wrapper = SimpleNamespace()

        with self.assertRaisesRegex(ValueError, 'Unsupported method: PATCH'):
            await tool.async_execute('https://example.com/resource')

    async def test_async_execute_accepts_lowercase_method(self) -> None:
        requests_wrapper = SimpleNamespace(
            apost=AsyncMock(return_value={'created': True})
        )
        tool = RequestTool(
            method='post',
            json_parser=True
        )
        tool.requests_wrapper = requests_wrapper

        result = await tool.async_execute(
            '{"url": "https://example.com/items", '
            '"data": {"name": "agentUniverse"}}'
        )

        self.assertEqual(result, {'created': True})
        requests_wrapper.apost.assert_awaited_once_with(
            'https://example.com/items',
            data={'name': 'agentUniverse'}
        )


if __name__ == '__main__':
    unittest.main()
