"""Keep DOCX table population linear in the number of written cells."""

from docx import Document
from docx.table import Table

from agentuniverse.agent.action.tool.common_tool.word_document_tool import WordDocumentTool


def test_create_table_does_not_rebuild_grid_per_cell(tmp_path, monkeypatch):
    rows = [[f'{row}:{col}' for col in range(5 if row % 2 else 3)]
            for row in range(20)]
    scans = []
    original = Table._cells.fget

    def counted_grid(table):
        scans.append(1)
        return original(table)

    monkeypatch.setattr(Table, '_cells', property(counted_grid))
    tool = WordDocumentTool(base_dir=str(tmp_path))
    result = tool.execute(mode='create', file_path='table.docx',
                          blocks=[{'type': 'table', 'rows': rows}])

    assert result['status'] == 'success', result
    # A full-table reconstruction per cell turns N writes into O(N squared).
    assert len(scans) <= 1
    table = Document(tmp_path / 'table.docx').tables[0]
    assert [[cell.text for cell in row.cells] for row in table.rows] == [
        row + [''] * (5 - len(row)) for row in rows]
