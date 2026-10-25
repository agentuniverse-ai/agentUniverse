"""Word append inputs follow the same strict parser as plain-file writes."""
import json

import pytest

from agentuniverse.agent.action.tool.common_tool.write_word_tool import WriteWordDocumentTool


@pytest.fixture
def document():
    return pytest.importorskip('docx').Document


@pytest.mark.parametrize('append,expected', [
    (False, False), (True, True), ('false', False), (' FALSE ', False),
    ('0', False), ('off', False), ('true', True), ('yes', True), (0, False),
    (1, True), (None, False),
])
def test_append_inputs_control_actual_paragraphs(tmp_path, append, expected, document):
    path = tmp_path / 'existing.docx'
    doc = document()
    doc.add_paragraph('original')
    doc.save(path)
    result = json.loads(WriteWordDocumentTool().execute(str(path), 'new', append=append))
    assert result['status'] == 'success'
    assert result['append_mode'] is expected
    assert [p.text for p in document(path).paragraphs] == (
        ['original', 'new'] if expected else ['new']
    )


@pytest.mark.parametrize('append', ['maybe', '', 2, [], {}])
def test_invalid_append_preserves_existing_document(tmp_path, append, document):
    path = tmp_path / 'existing.docx'
    doc = document()
    doc.add_paragraph('original')
    doc.save(path)
    original = path.read_bytes()
    result = json.loads(WriteWordDocumentTool().execute(str(path), 'new', append=append))
    assert result['status'] == 'error'
    assert 'append' in result['error']
    assert path.read_bytes() == original


def test_invalid_append_creates_no_parent_directory(tmp_path):
    path = tmp_path / 'missing' / 'new.docx'
    result = json.loads(WriteWordDocumentTool().execute(str(path), 'new', append='invalid'))
    assert result['status'] == 'error'
    assert not path.parent.exists()


def test_omitted_append_retains_overwrite_default(tmp_path, document):
    path = tmp_path / 'default.docx'
    tool = WriteWordDocumentTool()
    tool.execute(str(path), 'old')
    result = json.loads(tool.execute(str(path), 'new'))
    assert result['append_mode'] is False
    assert [p.text for p in document(path).paragraphs] == ['new']
