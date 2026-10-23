"""Exercise RequestTool and native LangChain request wrappers without network."""

import asyncio
import json
from contextlib import asynccontextmanager
from types import SimpleNamespace
from unittest.mock import AsyncMock
from urllib.parse import parse_qs, urlsplit

import aiohttp
import pytest
import requests
from langchain_community.utilities.requests import GenericRequestsWrapper

from agentuniverse.agent.action.tool.common_tool.request_tool import RequestTool


@pytest.mark.parametrize("method", ["GET", "POST", "PUT", "DELETE"])
@pytest.mark.parametrize("parsed", [False, True], ids=["direct", "json-input"])
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
def test_transport_options_reach_native_wrapper(monkeypatch, method, parsed, asynchronous):
    observed = {}
    expected = {"ok": True}

    def send(session, request, **kwargs):
        observed.update(method=request.method, url=request.url, body=request.body, options=kwargs)
        response = requests.Response()
        response.status_code = 200
        response._content = json.dumps(expected).encode()
        return response

    @asynccontextmanager
    async def request(session, method, url, **kwargs):
        observed.update(method=method.upper(), url=url, options=kwargs)
        yield SimpleNamespace(json=AsyncMock(return_value=expected))

    monkeypatch.setattr(requests.Session, "send", send)
    monkeypatch.setattr(aiohttp.ClientSession, "request", request)
    tool = RequestTool(method=method, json_parser=parsed)
    # Mirror normal configuration initialization: assign the native wrapper
    # after constructing the tool (the pinned LangChain wrapper is Pydantic V1).
    tool.requests_wrapper = GenericRequestsWrapper(response_content_type="json")
    params = {"q": "a/b & 中文", "tag": ["first", "second"]}
    options = {"url": "https://example.invalid/items", "params": params, "timeout": 1.25}
    body = {"value": "payload"}
    if method in {"POST", "PUT"}:
        options["data"] = body

    if asynchronous:
        if parsed:
            result = asyncio.run(tool.async_execute(json.dumps(options)))
        else:
            result = asyncio.run(tool.async_execute_by_method(**options))
    elif parsed:
        result = tool.execute(json.dumps(options))
    else:
        result = tool.execute_by_method(**options)

    assert result == expected
    assert observed["method"] == method
    assert observed["options"]["timeout"] == 1.25
    if asynchronous:
        assert observed["options"]["params"] == params
        if method in {"POST", "PUT"}:
            assert observed["options"]["json"] == body
    else:
        assert parse_qs(urlsplit(observed["url"]).query) == {
            "q": ["a/b & 中文"], "tag": ["first", "second"]}
        if method in {"POST", "PUT"}:
            assert json.loads(observed["body"]) == body
