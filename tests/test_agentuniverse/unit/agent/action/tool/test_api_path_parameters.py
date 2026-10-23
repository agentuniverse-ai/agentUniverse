"""Path parameter data must not become URL routing or query syntax."""
from unittest.mock import patch

import httpx
import pytest

from agentuniverse.agent.action.tool.api_tool import APITool
from agentuniverse.agent.action.tool.tool import ToolInput


def tool():
    return APITool(openapi_spec={
        'url': 'https://example.test/items/{item}/details',
        'method': 'get',
        'operation': {'parameters': [
            {'name': 'item', 'in': 'path', 'required': True, 'schema': {'type': 'string'}},
            {'name': 'filter', 'in': 'query', 'schema': {'type': 'string'}},
        ]},
    })


@pytest.mark.parametrize('value,encoded', [
    ('folder/name', 'folder%2Fname'),
    ('name?admin=true', 'name%3Fadmin%3Dtrue'),
    ('name#section', 'name%23section'),
    ('100% done', '100%25%20done'),
    ('文档/一', '%E6%96%87%E6%A1%A3%2F%E4%B8%80'),
    ('{item}', '%7Bitem%7D'),
])
def test_scalar_path_value_reaches_transport_as_one_encoded_segment(value, encoded):
    observed = []

    def handler(request):
        observed.append(request)
        return httpx.Response(200, text='ok')

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        def request(url, **kwargs):
            return client.request('GET', url, **kwargs)

        with patch('agentuniverse.agent.action.tool.api_tool.ssrf_proxy.get', side_effect=request):
            output = tool().execute(ToolInput({'item': value, 'filter': 'active'}))

    assert output == 'ok'
    assert len(observed) == 1
    assert observed[0].url.raw_path.split(b'?')[0] == f'/items/{encoded}/details'.encode()
    assert dict(observed[0].url.params) == {'filter': 'active'}
    assert observed[0].url.fragment == ''


@pytest.mark.parametrize('value', [0, 42, 'plain-name'])
def test_simple_path_values_keep_their_existing_representation(value):
    with patch('agentuniverse.agent.action.tool.api_tool.ssrf_proxy.get',
               return_value=httpx.Response(200, text='ok')) as get:
        assert tool().execute(ToolInput({'item': value})) == 'ok'
    assert get.call_args.args[0] == f'https://example.test/items/{value}/details'
