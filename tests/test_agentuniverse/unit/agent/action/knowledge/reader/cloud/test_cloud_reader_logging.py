import logging

import pytest

from agentuniverse.agent.action.knowledge.reader.cloud.confluence_reader import ConfluenceReader
from agentuniverse.agent.action.knowledge.reader.cloud.google_docs_reader import GoogleDocsReader
from agentuniverse.agent.action.knowledge.reader.cloud.notion_reader import NotionReader


@pytest.mark.parametrize(
    ("reader", "message"),
    [
        (ConfluenceReader(), "ConfluenceReader starting page load"),
        (GoogleDocsReader(), "GoogleDocsReader starting document load"),
        (NotionReader(), "NotionReader starting page or database load"),
    ],
)
def test_cloud_readers_log_diagnostics_without_stdout(reader, message, caplog, capsys):
    with caplog.at_level(logging.DEBUG):
        with pytest.raises(ValueError):
            reader.load_data("")

    captured = capsys.readouterr()
    assert captured.out == ""
    assert message in caplog.text
