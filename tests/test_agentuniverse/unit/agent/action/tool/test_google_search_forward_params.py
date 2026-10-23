import asyncio
from unittest.mock import patch

import pytest

from agentuniverse.agent.action.tool.common_tool.google_search_tool_v2 import (
    GoogleScholarSearchTool,
    GoogleSearchTool,
)


class _FakeSerper:
    instances = []

    def __init__(self, **kwargs):
        self.options = kwargs
        self.calls = []
        self.instances.append(self)

    def run(self, **kwargs):
        self.calls.append(kwargs)
        return "search result"

    async def arun(self, **kwargs):
        self.calls.append(kwargs)
        return "search result"


@pytest.fixture(autouse=True)
def reset_fake_wrapper():
    _FakeSerper.instances.clear()


def test_search_forwards_page_and_tbs_without_duplicate_keyword():
    with patch(
        "agentuniverse.agent.action.tool.common_tool.google_search_tool_v2.GoogleSerperAPIWrapper",
        _FakeSerper,
    ):
        GoogleSearchTool(serper_api_key="key").execute(
            "retrieval", k=3, page=2, tbs="qdr:y", location="Berlin"
        )

    wrapper = _FakeSerper.instances[0]
    assert wrapper.options["tbs"] == "qdr:y"
    assert wrapper.calls == [{"query": "retrieval", "page": 2, "location": "Berlin"}]


def test_async_search_forwards_extra_parameters():
    async def run():
        with patch(
            "agentuniverse.agent.action.tool.common_tool.google_search_tool_v2.GoogleSerperAPIWrapper",
            _FakeSerper,
        ):
            await GoogleSearchTool(serper_api_key="key").async_execute(
                "retrieval", page=3, tbs="qdr:m"
            )

    asyncio.run(run())

    wrapper = _FakeSerper.instances[0]
    assert wrapper.options["tbs"] == "qdr:m"
    assert wrapper.calls == [{"query": "retrieval", "page": 3}]


def test_scholar_forwards_region_and_filters():
    with patch(
        "agentuniverse.agent.action.tool.common_tool.google_search_tool_v2.GoogleSerperAPIWrapper",
        _FakeSerper,
    ):
        GoogleScholarSearchTool(serper_api_key="key").execute(
            "agents", gl="de", hl="de", tbs="qdr:y", page=2
        )

    wrapper = _FakeSerper.instances[0]
    assert wrapper.options["gl"] == "de"
    assert wrapper.options["hl"] == "de"
    assert wrapper.options["tbs"] == "qdr:y"
    assert wrapper.calls == [{"query": "site:scholar.google.com agents", "page": 2}]


def test_async_scholar_forwards_region_and_filters():
    async def run():
        with patch(
            "agentuniverse.agent.action.tool.common_tool.google_search_tool_v2.GoogleSerperAPIWrapper",
            _FakeSerper,
        ):
            await GoogleScholarSearchTool(serper_api_key="key").async_execute(
                "agents", gl="fr", hl="fr", tbs="qdr:w", location="Paris"
            )

    asyncio.run(run())

    wrapper = _FakeSerper.instances[0]
    assert wrapper.options["gl"] == "fr"
    assert wrapper.options["hl"] == "fr"
    assert wrapper.options["tbs"] == "qdr:w"
    assert wrapper.calls == [{"query": "site:scholar.google.com agents", "location": "Paris"}]
