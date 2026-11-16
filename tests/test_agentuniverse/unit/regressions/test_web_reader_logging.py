from agentuniverse.agent.action.knowledge.reader.web.rendered_web_page_reader import (
    RenderedWebPageReader,
)
from agentuniverse.agent.action.knowledge.reader.web.web_page_reader import WebPageReader


def test_web_page_reader_does_not_write_debug_output(monkeypatch, capsys):
    reader = WebPageReader()
    monkeypatch.setattr(reader, "_fetch_html", lambda url: "<html></html>")
    monkeypatch.setattr(reader, "_extract_main_text", lambda html, url: ("text", {}))

    reader.load_data("https://example.com")

    assert capsys.readouterr().out == ""


def test_rendered_web_page_reader_does_not_write_debug_output(monkeypatch, capsys):
    reader = RenderedWebPageReader()
    monkeypatch.setattr(reader, "_render_and_get_html", lambda url: "<html></html>")
    monkeypatch.setattr(
        "agentuniverse.agent.action.knowledge.reader.web.web_page_reader.WebPageReader._extract_main_text",
        lambda self, html, url: ("text", {}),
    )

    reader.load_data("https://example.com")

    assert capsys.readouterr().out == ""
