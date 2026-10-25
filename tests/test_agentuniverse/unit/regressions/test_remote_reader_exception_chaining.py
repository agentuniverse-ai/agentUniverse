import sys
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from agentuniverse.agent.action.knowledge.reader.image.image_reader import ImageReader
from agentuniverse.agent.action.knowledge.reader.web.web_page_reader import WebPageReader


def test_web_reader_preserves_http_fallback_cause():
    httpx_error = OSError("httpx unavailable")
    requests_error = TimeoutError("requests unavailable")

    class FailingClient:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def get(self, *_args, **_kwargs):
            raise httpx_error

    fake_httpx = SimpleNamespace(Client=lambda **_kwargs: FailingClient())
    fake_requests = SimpleNamespace(
        get=lambda *_args, **_kwargs: (_ for _ in ()).throw(requests_error)
    )

    with patch.dict(sys.modules, {"httpx": fake_httpx, "requests": fake_requests}):
        with pytest.raises(RuntimeError) as raised:
            WebPageReader()._fetch_html("https://example.test")

    assert raised.value.__cause__ is requests_error
    assert "httpx unavailable" in str(raised.value)
    assert "requests unavailable" in str(raised.value)


def test_image_reader_preserves_processing_cause(tmp_path):
    path = tmp_path / "not-an-image.txt"
    path.write_text("not an image", encoding="utf-8")

    with pytest.raises(RuntimeError) as raised:
        ImageReader().load_data(path)

    assert isinstance(raised.value.__cause__, ValueError)
    assert "Unsupported image format" in str(raised.value.__cause__)
