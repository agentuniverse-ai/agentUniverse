"""Keep uploaded CSV newline handling consistent with local files."""
import io

import pytest

from agentuniverse.agent.action.knowledge.reader.file.csv_reader import CSVReader


@pytest.mark.parametrize("newline", ["\n", "\r\n", "\r"], ids=["lf", "crlf", "cr"])
@pytest.mark.parametrize("source_type", ["path", "text", "binary"])
def test_record_endings_and_quoted_newlines(tmp_path, newline, source_type):
    text = (
        "name,note" + newline
        + '"张三","first\rsecond\nthird\r\nfourth"' + newline
        + '"李四","a,b ""quoted"""' + newline
    )
    expected = 'name, note\n张三, first\rsecond\nthird\r\nfourth\n李四, a,b "quoted"'
    if source_type == "path":
        source = tmp_path / "facts.csv"
        source.write_bytes(text.encode("utf-8"))
    else:
        source = io.StringIO(text) if source_type == "text" else io.BytesIO(text.encode("utf-8"))
        source.name = "uploads/facts.csv"
    ext_info = {"batch": "newline test"}
    try:
        documents = CSVReader().load_data(source, ext_info=ext_info)

        assert len(documents) == 1
        assert documents[0].text == expected
        assert documents[0].metadata == {"file_name": "facts.csv", "batch": "newline test"}
        assert ext_info == {"batch": "newline test"}
        if source_type != "path":
            assert not source.closed
    finally:
        if source_type != "path":
            source.close()


@pytest.mark.parametrize("binary", [False, True], ids=["text", "binary"])
def test_mixed_record_endings(binary):
    text = 'name,note\rAlice,"one\r\ntwo"\nBob,done\r\n'
    with (io.BytesIO(text.encode("utf-8")) if binary else io.StringIO(text)) as source:
        documents = CSVReader().load_data(source)

        assert documents[0].text == "name, note\nAlice, one\r\ntwo\nBob, done"
        assert documents[0].metadata == {"file_name": "unknown"}
        assert not source.closed


@pytest.mark.parametrize("binary", [False, True], ids=["text", "binary"])
def test_custom_delimiter_and_quote_character(binary):
    text = "name;note\r'张三';'left;right\rnext'\r"
    with (io.BytesIO(text.encode("utf-8")) if binary else io.StringIO(text)) as source:
        documents = CSVReader().load_data(source, delimiter=";", quotechar="'")

        assert documents[0].text == "name, note\n张三, left;right\rnext"


def test_gb18030_binary_upload_with_cr_records():
    with io.BytesIO("姓名,城市\r张三,北京\r".encode("gb18030")) as source:
        documents = CSVReader().load_data(source)

        assert documents[0].text == "姓名, 城市\n张三, 北京"
        assert not source.closed
