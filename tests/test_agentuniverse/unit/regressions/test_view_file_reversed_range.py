import json

from agentuniverse.agent.action.tool.common_tool.view_file_tool import ViewFileTool


def test_view_file_rejects_reversed_line_range(tmp_path):
    source = tmp_path / "sample.txt"
    source.write_text("one\ntwo\nthree\n")
    tool = ViewFileTool(base_dir=str(tmp_path))

    result = json.loads(tool.execute("sample.txt", start_line=2, end_line=1))

    assert result["status"] == "error"
    assert result["error"] == "start_line must be less than or equal to end_line"
