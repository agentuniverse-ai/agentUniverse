import json

import pytest

from agentuniverse.agent.action.tool.common_tool.write_word_tool import WriteWordDocumentTool


@pytest.mark.parametrize("file_path", [None, "", "   "])
def test_empty_output_path_returns_structured_error(file_path):
    result = json.loads(WriteWordDocumentTool().execute(file_path))

    assert result["status"] == "error"
    assert result["error"] == "file_path must be a non-empty string"
