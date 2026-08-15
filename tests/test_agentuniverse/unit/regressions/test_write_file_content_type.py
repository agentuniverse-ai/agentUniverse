import json

from agentuniverse.agent.action.tool.common_tool.write_file_tool import WriteFileTool


def test_write_file_rejects_non_string_content(tmp_path):
    tool = WriteFileTool(base_dir=str(tmp_path))

    result = json.loads(tool.execute("output.txt", content=None))

    assert result["status"] == "error"
    assert result["error"] == "content must be a string"
    assert not (tmp_path / "output.txt").exists()
