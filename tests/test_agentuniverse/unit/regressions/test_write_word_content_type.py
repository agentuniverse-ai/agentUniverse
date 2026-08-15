import json

from agentuniverse.agent.action.tool.common_tool.write_word_tool import WriteWordDocumentTool


def test_write_word_rejects_non_string_content(tmp_path):
    target = tmp_path / "output.docx"

    result = json.loads(WriteWordDocumentTool().execute(str(target), content=None))

    assert result["status"] == "error"
    assert result["error"] == "content must be a string"
    assert not target.exists()
