from agentuniverse.agent.action.knowledge.reader.file.txt_reader import LineTxtReader


def test_line_txt_reader_uses_independent_metadata(tmp_path):
    file_path = tmp_path / "lines.txt"
    file_path.write_text("first\nsecond\n", encoding="utf-8")

    documents = LineTxtReader().load_data(file_path, ext_info={"source": "test"})

    assert len(documents) == 2
    documents[0].metadata["source"] = "changed"
    assert documents[1].metadata["source"] == "test"
