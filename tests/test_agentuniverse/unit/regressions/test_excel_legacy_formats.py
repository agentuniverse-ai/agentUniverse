"""Unsupported legacy formats must not receive mislabeled OOXML output."""
import asyncio
import json

import pytest
from openpyxl import load_workbook

from agentuniverse.agent.action.tool.common_tool.excel_tool import ExcelTool


@pytest.mark.parametrize('suffix', ['.xls', '.XLS', '.xlsb', '.XLSB'])
@pytest.mark.parametrize('asynchronous', [False, True])
def test_unsupported_write_does_not_create_file(tmp_path, suffix, asynchronous):
    path = tmp_path / ('new' + suffix)
    tool = ExcelTool(allowed_extensions=['.xlsx', '.xls', '.xlsb'])
    kwargs = {'file_path': str(path), 'mode': 'write', 'data': [['value'], [42]]}
    result = json.loads(asyncio.run(tool.async_execute(**kwargs)) if asynchronous
                        else tool.execute(**kwargs))
    assert result['status'] == 'error'
    assert 'convert' in result['error'].lower()
    assert not path.exists()


@pytest.mark.parametrize('mode', ['write', 'read', 'append', 'info'])
@pytest.mark.parametrize('suffix', ['.xls', '.xlsb'])
def test_unsupported_operations_preserve_existing_bytes(tmp_path, monkeypatch, mode, suffix):
    path = tmp_path / ('existing' + suffix)
    original = b'existing legacy file placeholder'
    path.write_bytes(original)
    tool = ExcelTool(allowed_extensions=['.xlsx', '.xls', '.xlsb'])

    def unexpected(*args, **kwargs):
        pytest.fail('Unsupported format should be rejected before file inspection')

    monkeypatch.setattr(tool, '_check_file_size', unexpected)
    result = json.loads(tool.execute(str(path), mode, data=[['changed']], overwrite=True))
    assert result['status'] == 'error'
    assert 'convert' in result['error'].lower()
    assert path.read_bytes() == original


@pytest.mark.parametrize('suffix', ['.xlsx', '.XLSX'])
def test_supported_xlsx_roundtrip_retained(tmp_path, suffix):
    path = tmp_path / ('supported' + suffix)
    tool = ExcelTool()
    assert json.loads(tool.execute(str(path), 'write', data=[['Name'], ['first']]))['status'] == 'success'
    assert json.loads(tool.execute(str(path), 'append', data=[['second']]))['status'] == 'success'
    assert json.loads(tool.execute(str(path), 'read'))['status'] == 'success'
    assert json.loads(tool.execute(str(path), 'info'))['status'] == 'success'
    book = load_workbook(path)
    try:
        assert list(book.active.values) == [('Name',), ('first',), ('second',)]
    finally:
        book.close()


def test_custom_allowlist_still_restricts_supported_formats(tmp_path):
    path = tmp_path / 'excluded.xlsx'
    result = json.loads(ExcelTool(allowed_extensions=[]).execute(str(path), 'write', data=[[1]]))
    assert result['status'] == 'error'
    assert not path.exists()


def test_default_and_custom_allowlist_contract(tmp_path):
    assert ExcelTool().allowed_extensions == ['.xlsx']
    tool = ExcelTool(allowed_extensions=['.xlsm', '.xltx', '.xltm'])
    for suffix in tool.allowed_extensions:
        assert tool._validate_path(str(tmp_path / ('custom' + suffix))) == {'valid': True}
