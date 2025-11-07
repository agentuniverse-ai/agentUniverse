from agentuniverse.agent.action.knowledge.reader.file.csv_reader import CSVReader
from agentuniverse.agent.action.knowledge.reader.file.txt_reader import TxtReader
from agentuniverse.agent.action.knowledge.reader.utils import detect_file_encoding


def test_detect_file_encoding_gb18030(tmp_path):
    sample_text = "示例文本"
    file_path = tmp_path / "sample.txt"
    file_path.write_text(sample_text, encoding="gb18030")

    detected = detect_file_encoding(file_path)
    assert detected in {"gb18030", "gbk"}


def test_txt_reader_handles_gbk(tmp_path):
    content = "第一行\n第二行"
    file_path = tmp_path / "gbk.txt"
    file_path.write_text(content, encoding="gb18030")

    reader = TxtReader()
    documents = reader.load_data(file_path)

    assert len(documents) == 1
    assert documents[0].text == content
    assert documents[0].metadata["file_name"] == file_path.name


def test_csv_reader_handles_utf8_bom(tmp_path):
    rows = ["col1,col2", "值1,值2"]
    file_path = tmp_path / "data.csv"
    file_path.write_text("\n".join(rows), encoding="utf-8-sig")

    reader = CSVReader()
    documents = reader.load_data(file_path)

    assert len(documents) == 1
    assert "值1" in documents[0].text
    assert documents[0].metadata["file_name"] == file_path.name
