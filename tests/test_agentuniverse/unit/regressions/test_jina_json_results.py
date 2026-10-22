"""Jina's documented structured-result strings must be valid JSON."""
import json
from unittest.mock import Mock, patch

import pytest

from agentuniverse.agent.action.tool.common_tool.jina_ai_tool import JinaAITool


@pytest.mark.parametrize('mode,data', [
    ('search', [{'title': '研究 "quoted"', 'description': "author's result", 'available': True, 'extra': None}]),
    ('search', []),
    ('check_fact', {'result': False, 'reason': 'line\nnext', 'references': [{'quote': '研究'}], 'extra': None}),
    ('check_fact', {}),
    ('search', None),
    ('check_fact', None),
])
def test_execute_returns_json_for_structured_results(mode, data):
    response = Mock()
    response.json.return_value = {'code': 200, 'data': data}
    with patch('agentuniverse.agent.action.tool.common_tool.jina_ai_tool.requests.get', return_value=response) as request:
        result = JinaAITool(mode=mode, api_key='offline-placeholder').execute(input='example')
    assert isinstance(result, str)
    assert json.loads(result) == data
    assert request.call_count == 1


@pytest.mark.parametrize('mode', ['search', 'check_fact'])
@pytest.mark.parametrize('response', [None, 'HTTP Error: offline failure'])
def test_existing_error_and_absent_response_behavior(mode, response):
    with patch.object(JinaAITool, '_make_api_request', return_value=response):
        assert JinaAITool(mode=mode, api_key='offline-placeholder').execute(input='example') == response


def test_read_mode_still_returns_plain_text():
    with patch.object(JinaAITool, '_make_api_request', return_value={'data': {'content': 'plain text'}}):
        assert JinaAITool(api_key='offline-placeholder').execute(input='https://example.org') == 'plain text'
