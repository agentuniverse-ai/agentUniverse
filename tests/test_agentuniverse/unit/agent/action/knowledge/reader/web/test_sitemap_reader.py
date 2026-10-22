#!/usr/bin/env python3

import gzip
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import httpx
import pytest
import yaml
from pydantic import PrivateAttr, ValidationError

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.reader.web.sitemap_reader import SitemapReader
from agentuniverse.agent.action.knowledge.store.document import Document

ROOT = "https://docs.example.com/sitemap.xml"
NAMESPACE = "http://www.sitemaps.org/schemas/sitemap/0.9"


def urlset(*entries, namespace=True):
    ns = f' xmlns="{NAMESPACE}"' if namespace else ""
    body = []
    for entry in entries:
        fields = "".join(f"<{key}>{value}</{key}>" for key, value in entry.items())
        body.append(f"<url>{fields}</url>")
    return f'<?xml version="1.0"?><urlset{ns}>{"".join(body)}</urlset>'.encode()


def sitemap_index(*urls, namespace=True):
    ns = f' xmlns="{NAMESPACE}"' if namespace else ""
    items = "".join(f"<sitemap><loc>{url}</loc></sitemap>" for url in urls)
    return f'<?xml version="1.0"?><sitemapindex{ns}>{items}</sitemapindex>'.encode()


class StubPageReader(Reader):
    """Deterministic page reader used by content-mode tests."""

    _responses: dict = PrivateAttr()
    _calls: list[str] = PrivateAttr(default_factory=list)

    def __init__(self, responses):
        super().__init__()
        self._responses = responses

    @property
    def calls(self):
        return list(self._calls)

    def _load_data(self, url: str):
        self._calls.append(url)
        response = self._responses[url]
        if isinstance(response, Exception):
            raise response
        return response


@pytest.fixture
def reader():
    return SitemapReader()


def patch_sitemaps(reader, payloads):
    def fetch(_client, url, _max_bytes):
        value = payloads[url]
        if isinstance(value, Exception):
            raise value
        return value

    return patch.object(reader, "_fetch_sitemap", side_effect=fetch)


def test_urlset_inventory_preserves_metadata(reader):
    payload = urlset(
        {
            "loc": "https://docs.example.com/guide/start",
            "lastmod": "2026-08-10",
            "changefreq": "weekly",
            "priority": "0.8",
        }
    )
    with patch_sitemaps(reader, {ROOT: payload}):
        documents = reader.load_data(ROOT)

    assert len(documents) == 1
    document = documents[0]
    assert document.text == "https://docs.example.com/guide/start"
    assert document.metadata == {
        "source": "https://docs.example.com/guide/start",
        "url": "https://docs.example.com/guide/start",
        "sitemap_source": ROOT,
        "sitemap_depth": 0,
        "sitemap_lastmod": "2026-08-10",
        "sitemap_changefreq": "weekly",
        "sitemap_priority": "0.8",
        "content_loaded": False,
    }


def test_namespace_free_urlset_is_supported(reader):
    payload = urlset({"loc": "https://docs.example.com/a"}, namespace=False)
    with patch_sitemaps(reader, {ROOT: payload}):
        documents = reader.load_data(ROOT)
    assert [document.metadata["url"] for document in documents] == ["https://docs.example.com/a"]


def test_recursive_index_preserves_order_and_deduplicates(reader):
    first = "https://docs.example.com/first.xml"
    second = "https://docs.example.com/second.xml"
    payloads = {
        ROOT: sitemap_index(first, second),
        first: urlset(
            {"loc": "https://docs.example.com/a"},
            {"loc": "https://docs.example.com/shared"},
        ),
        second: urlset(
            {"loc": "https://docs.example.com/shared"},
            {"loc": "https://docs.example.com/b"},
        ),
    }
    with patch_sitemaps(reader, payloads):
        documents = reader.load_data(ROOT)

    assert [document.metadata["url"] for document in documents] == [
        "https://docs.example.com/a",
        "https://docs.example.com/shared",
        "https://docs.example.com/b",
    ]


def test_sitemap_cycle_is_visited_once(reader):
    child = "https://docs.example.com/child.xml"
    payloads = {
        ROOT: sitemap_index(child),
        child: sitemap_index(ROOT, "https://docs.example.com/pages.xml"),
        "https://docs.example.com/pages.xml": urlset({"loc": "https://docs.example.com/page"}),
    }
    with patch_sitemaps(reader, payloads) as fetch:
        documents = reader.load_data(ROOT)

    assert [document.metadata["url"] for document in documents] == ["https://docs.example.com/page"]
    assert [call.args[1] for call in fetch.call_args_list].count(ROOT) == 1


def test_max_depth_skips_deeper_sitemaps(reader):
    one = "https://docs.example.com/one.xml"
    two = "https://docs.example.com/two.xml"
    payloads = {
        ROOT: sitemap_index(one),
        one: sitemap_index(two),
        two: urlset({"loc": "https://docs.example.com/page"}),
    }
    with patch_sitemaps(reader, payloads) as fetch:
        documents = reader.load_data(ROOT, max_depth=1)

    assert documents == []
    assert two not in [call.args[1] for call in fetch.call_args_list]


def test_max_sitemaps_is_a_hard_bound(reader):
    one = "https://docs.example.com/one.xml"
    two = "https://docs.example.com/two.xml"
    payloads = {
        ROOT: sitemap_index(one, two),
        one: urlset({"loc": "https://docs.example.com/a"}),
        two: urlset({"loc": "https://docs.example.com/b"}),
    }
    with patch_sitemaps(reader, payloads), pytest.raises(ValueError, match="max_sitemaps exceeded"):
        reader.load_data(ROOT, max_sitemaps=2)


def test_max_urls_stops_selection_in_source_order(reader):
    payload = urlset(*({"loc": f"https://docs.example.com/{index}"} for index in range(5)))
    with patch_sitemaps(reader, {ROOT: payload}):
        documents = reader.load_data(ROOT, max_urls=2)
    assert [document.metadata["url"] for document in documents] == [
        "https://docs.example.com/0",
        "https://docs.example.com/1",
    ]


def test_include_and_exclude_patterns_are_applied_before_loading(reader):
    payload = urlset(
        {"loc": "https://docs.example.com/guide/start"},
        {"loc": "https://docs.example.com/guide/archive/old"},
        {"loc": "https://docs.example.com/blog/post"},
    )
    with patch_sitemaps(reader, {ROOT: payload}):
        documents = reader.load_data(
            ROOT,
            include_patterns=[r"/guide/"],
            exclude_patterns=[r"/archive/"],
        )
    assert [document.metadata["url"] for document in documents] == ["https://docs.example.com/guide/start"]


def test_modified_since_filters_old_dates_but_retains_unknown_dates(reader):
    payload = urlset(
        {"loc": "https://docs.example.com/old", "lastmod": "2025-12-31"},
        {"loc": "https://docs.example.com/new", "lastmod": "2026-08-10"},
        {"loc": "https://docs.example.com/missing"},
        {"loc": "https://docs.example.com/invalid", "lastmod": "not-a-date"},
    )
    with patch_sitemaps(reader, {ROOT: payload}):
        documents = reader.load_data(ROOT, modified_since="2026-01-01")
    assert [document.metadata["url"] for document in documents] == [
        "https://docs.example.com/new",
        "https://docs.example.com/missing",
        "https://docs.example.com/invalid",
    ]


def test_datetime_cutoff_is_normalized_to_utc(reader):
    payload = urlset(
        {
            "loc": "https://docs.example.com/page",
            "lastmod": "2026-08-15T08:00:00+08:00",
        }
    )
    cutoff = datetime(2026, 8, 15, tzinfo=timezone.utc)
    with patch_sitemaps(reader, {ROOT: payload}):
        documents = reader.load_data(ROOT, modified_since=cutoff)
    assert len(documents) == 1


def test_same_origin_filters_cross_origin_pages(reader):
    payload = urlset(
        {"loc": "https://docs.example.com/a"},
        {"loc": "https://cdn.example.net/b"},
    )
    with patch_sitemaps(reader, {ROOT: payload}):
        restricted = reader.load_data(ROOT)
    with patch_sitemaps(reader, {ROOT: payload}):
        unrestricted = reader.load_data(ROOT, same_origin_only=False)

    assert len(restricted) == 1
    assert len(unrestricted) == 2


def test_cross_origin_child_sitemap_is_reported(reader):
    child = "https://other.example.net/sitemap.xml"
    with patch_sitemaps(reader, {ROOT: sitemap_index(child)}):
        documents = reader.load_data(ROOT)

    assert len(documents) == 1
    summary = documents[0]
    assert summary.metadata["sitemap_error_summary"] is True
    assert "origin_filter" in summary.text
    assert child in summary.text


def test_nested_sitemap_failure_can_be_summarized(reader):
    child = "https://docs.example.com/broken.xml"
    with patch_sitemaps(
        reader,
        {ROOT: sitemap_index(child), child: ValueError("broken child")},
    ):
        documents = reader.load_data(ROOT, continue_on_error=True)

    assert documents[-1].metadata["error_count"] == 1
    assert "broken child" in documents[-1].text


def test_nested_sitemap_failure_can_fail_fast(reader):
    child = "https://docs.example.com/broken.xml"
    with (
        patch_sitemaps(
            reader,
            {ROOT: sitemap_index(child), child: ValueError("broken child")},
        ),
        pytest.raises(RuntimeError, match="broken child"),
    ):
        reader.load_data(ROOT, continue_on_error=False)


def test_root_sitemap_failure_is_always_raised(reader):
    with (
        patch_sitemaps(reader, {ROOT: ValueError("root unavailable")}),
        pytest.raises(RuntimeError, match="root unavailable"),
    ):
        reader.load_data(ROOT, continue_on_error=True)


def test_content_mode_delegates_and_merges_provenance(reader):
    page = "https://docs.example.com/guide"
    payload = urlset({"loc": page, "lastmod": "2026-08-14"})
    delegate = StubPageReader(
        {
            page: [
                Document(
                    text="Guide body",
                    metadata={"source": "page-reader", "extractor": "stub"},
                )
            ]
        }
    )
    with patch_sitemaps(reader, {ROOT: payload}):
        documents = reader.load_data(
            ROOT,
            load_content=True,
            page_reader=delegate,
            ext_info={"collection": "docs"},
        )

    assert delegate.calls == [page]
    assert len(documents) == 1
    assert documents[0].text == "Guide body"
    assert documents[0].metadata["source"] == "page-reader"
    assert documents[0].metadata["url"] == page
    assert documents[0].metadata["sitemap_source"] == ROOT
    assert documents[0].metadata["sitemap_lastmod"] == "2026-08-14"
    assert documents[0].metadata["content_loaded"] is True
    assert documents[0].metadata["collection"] == "docs"


def test_content_mode_preserves_entry_order_with_workers(reader):
    pages = [f"https://docs.example.com/{value}" for value in ("a", "b", "c")]
    payload = urlset(*({"loc": page} for page in pages))
    delegate = StubPageReader({page: [Document(text=page, metadata={})] for page in pages})
    with patch_sitemaps(reader, {ROOT: payload}):
        documents = reader.load_data(
            ROOT,
            load_content=True,
            page_reader=delegate,
            max_workers=3,
        )
    assert [document.text for document in documents] == pages


def test_page_failure_is_collected_without_fake_content(reader):
    good = "https://docs.example.com/good"
    bad = "https://docs.example.com/bad"
    payload = urlset({"loc": good}, {"loc": bad})
    delegate = StubPageReader(
        {
            good: [Document(text="good content", metadata={})],
            bad: RuntimeError("page failed"),
        }
    )
    with patch_sitemaps(reader, {ROOT: payload}):
        documents = reader.load_data(
            ROOT,
            load_content=True,
            page_reader=delegate,
            continue_on_error=True,
        )

    assert [document.text for document in documents[:-1]] == ["good content"]
    assert documents[-1].metadata["sitemap_error_summary"] is True
    assert bad in documents[-1].text
    assert "page failed" in documents[-1].text


def test_page_failure_can_fail_fast(reader):
    page = "https://docs.example.com/bad"
    delegate = StubPageReader({page: RuntimeError("page failed")})
    with patch_sitemaps(reader, {ROOT: urlset({"loc": page})}), pytest.raises(RuntimeError, match="page failed"):
        reader.load_data(
            ROOT,
            load_content=True,
            page_reader=delegate,
            continue_on_error=False,
        )


def test_inventory_ext_info_is_merged(reader):
    with patch_sitemaps(reader, {ROOT: urlset({"loc": "https://docs.example.com/page"})}):
        document = reader.load_data(ROOT, ext_info={"tenant": "alpha"})[0]
    assert document.metadata["tenant"] == "alpha"


def test_per_call_overrides_do_not_mutate_reader(reader):
    with patch_sitemaps(reader, {ROOT: urlset({"loc": "https://docs.example.com/page"})}):
        reader.load_data(
            ROOT,
            max_urls=1,
            max_sitemaps=1,
            max_depth=0,
            max_sitemap_bytes=2048,
            request_timeout=1.5,
            max_redirects=1,
            max_workers=1,
            same_origin_only=False,
        )
    assert reader.max_urls == 100
    assert reader.max_sitemaps == 20
    assert reader.max_depth == 3
    assert reader.max_sitemap_bytes == 5 * 1024 * 1024
    assert reader.request_timeout == 20
    assert reader.max_redirects == 5
    assert reader.max_workers == 4
    assert reader.same_origin_only is True


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("max_urls", 0),
        ("max_sitemaps", 101),
        ("max_depth", -1),
        ("max_sitemap_bytes", 100),
        ("request_timeout", 0),
        ("max_redirects", 21),
        ("max_workers", 17),
    ],
)
def test_invalid_per_call_limits_fail_before_fetch(reader, name, value):
    with patch.object(reader, "_fetch_sitemap") as fetch, pytest.raises(ValueError):
        reader.load_data(ROOT, **{name: value})
    fetch.assert_not_called()


@pytest.mark.parametrize("value", [True, "10", 1.5])
def test_invalid_integer_limit_types_fail_before_fetch(reader, value):
    with patch.object(reader, "_fetch_sitemap") as fetch, pytest.raises(TypeError):
        reader.load_data(ROOT, max_urls=value)
    fetch.assert_not_called()


def test_invalid_patterns_fail_before_fetch(reader):
    with (
        patch.object(reader, "_fetch_sitemap") as fetch,
        pytest.raises(ValueError, match="invalid include_patterns regex"),
    ):
        reader.load_data(ROOT, include_patterns=["["])
    fetch.assert_not_called()


def test_invalid_modified_since_fails_before_fetch(reader):
    with patch.object(reader, "_fetch_sitemap") as fetch, pytest.raises(ValueError, match="ISO-8601"):
        reader.load_data(ROOT, modified_since="yesterday")
    fetch.assert_not_called()


@pytest.mark.parametrize(
    ("argument", "value", "message"),
    [
        ("load_content", "yes", "load_content"),
        ("continue_on_error", 1, "continue_on_error"),
        ("ext_info", [], "ext_info"),
        ("page_reader", object(), "page_reader"),
    ],
)
def test_invalid_request_flags_fail_before_fetch(reader, argument, value, message):
    with patch.object(reader, "_fetch_sitemap") as fetch, pytest.raises(TypeError, match=message):
        reader.load_data(ROOT, **{argument: value})
    fetch.assert_not_called()


@pytest.mark.parametrize(
    "url",
    [
        "",
        "sitemap.xml",
        "ftp://example.com/sitemap.xml",
        "https://user:secret@example.com/sitemap.xml",
    ],
)
def test_invalid_root_urls_are_rejected(reader, url):
    with pytest.raises(ValueError):
        reader.load_data(url)


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        (b"", "empty"),
        (b"<not-sitemap />", "urlset or sitemapindex"),
        (b"<urlset>", "invalid sitemap XML"),
        (b"<!DOCTYPE foo><urlset />", "DTD"),
        (b"<urlset><url /></urlset>", "missing loc"),
        (b"<urlset><url><loc>/relative</loc></url></urlset>", "absolute HTTP"),
    ],
)
def test_invalid_sitemap_documents_are_rejected(reader, payload, message):
    with patch_sitemaps(reader, {ROOT: payload}), pytest.raises(RuntimeError, match=message):
        reader.load_data(ROOT)


def test_gzip_sitemap_is_decompressed(reader):
    payload = gzip.compress(urlset({"loc": "https://docs.example.com/compressed"}))

    def handler(_request):
        return httpx.Response(200, content=payload)

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        decoded = reader._fetch_sitemap(client, ROOT, 1024 * 1024)
    assert b"compressed" in decoded


def test_decompressed_gzip_size_is_bounded(reader):
    payload = gzip.compress(b"x" * 5000)

    def handler(_request):
        return httpx.Response(200, content=payload)

    with (
        httpx.Client(transport=httpx.MockTransport(handler)) as client,
        pytest.raises(ValueError, match="decompressed sitemap"),
    ):
        reader._fetch_sitemap(client, ROOT, 1024)


def test_streamed_response_size_is_bounded(reader):
    def handler(_request):
        return httpx.Response(200, content=b"x" * 2048)

    with (
        httpx.Client(transport=httpx.MockTransport(handler)) as client,
        pytest.raises(ValueError, match="max_sitemap_bytes"),
    ):
        reader._fetch_sitemap(client, ROOT, 1024)


def test_invalid_gzip_is_reported(reader):
    def handler(_request):
        return httpx.Response(
            200,
            content=b"not gzip",
            headers={"content-type": "application/gzip"},
        )

    with (
        httpx.Client(transport=httpx.MockTransport(handler)) as client,
        pytest.raises(ValueError, match="invalid gzip"),
    ):
        reader._fetch_sitemap(client, ROOT, 1024)


def test_already_decoded_gzip_response_is_accepted(reader):
    xml = urlset({"loc": "https://docs.example.com/already-decoded"})

    def handler(_request):
        return httpx.Response(
            200,
            content=xml,
            headers={"content-type": "application/gzip"},
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        payload = reader._fetch_sitemap(client, f"{ROOT}.gz", 4096)
    assert payload == xml


def test_page_reader_must_implement_reader(reader):
    with (
        patch_sitemaps(reader, {ROOT: urlset({"loc": "https://docs.example.com/page"})}),
        pytest.raises(TypeError, match="Reader instance"),
    ):
        reader.load_data(ROOT, load_content=True, page_reader=object())


def test_model_level_bounds_are_validated():
    with pytest.raises(ValidationError):
        SitemapReader(max_urls=0)
    with pytest.raises(ValidationError):
        SitemapReader(max_workers=100)
    with pytest.raises(ValidationError):
        SitemapReader(max_redirects=21)
    with pytest.raises(ValidationError):
        SitemapReader(user_agent="")


def test_component_yaml_matches_reader_contract():
    path = (
        Path(__file__).parents[8]
        / "agentuniverse"
        / "agent"
        / "action"
        / "knowledge"
        / "reader"
        / "web"
        / "sitemap_reader.yaml"
    )
    config = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert config["name"] == "default_sitemap_reader"
    assert config["metadata"] == {
        "type": "READER",
        "module": "agentuniverse.agent.action.knowledge.reader.web.sitemap_reader",
        "class": "SitemapReader",
    }
    assert config["max_urls"] == 100
    assert config["max_redirects"] == 5
    assert config["same_origin_only"] is True
