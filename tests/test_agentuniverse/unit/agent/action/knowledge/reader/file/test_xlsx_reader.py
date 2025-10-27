# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/19 10:30
# @Author  : Assistant
# @FileName: test_xlsx_reader.py
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from agentuniverse.agent.action.knowledge.reader.file.xlsx_reader import XlsxReader
from agentuniverse.agent.action.knowledge.store.document import Document


class TestXlsxReader:
    """Test cases for XlsxReader."""

    def setup_method(self):
        """Set up test fixtures."""
        self.reader = XlsxReader()

    def test_xlsx_reader_initialization(self):
        """Test XlsxReader initialization."""
        assert isinstance(self.reader, XlsxReader)

    @patch('openpyxl.load_workbook')
    def test_load_data_success(self, mock_load_workbook):
        """Test successful loading of Excel data."""
        # Mock workbook and worksheet
        mock_workbook = MagicMock()
        mock_worksheet = MagicMock()
        mock_worksheet.sheetnames = ['Sheet1']
        mock_worksheet.max_row = 3
        mock_worksheet.max_column = 2
        
        # Mock cell values
        mock_cells = [
            [MagicMock(value='Name'), MagicMock(value='Age')],
            [MagicMock(value='Alice'), MagicMock(value=25)],
            [MagicMock(value='Bob'), MagicMock(value=30)]
        ]
        
        def mock_cell(row, column):
            return mock_cells[row-1][column-1]
        
        mock_worksheet.cell = mock_cell
        mock_workbook.__getitem__.return_value = mock_worksheet
        mock_workbook.sheetnames = ['Sheet1']
        mock_load_workbook.return_value = mock_workbook

        # Test with string path
        result = self.reader._load_data('test.xlsx')
        
        assert len(result) == 1
        assert isinstance(result[0], Document)
        assert 'Name | Age' in result[0].text
        assert 'Alice | 25' in result[0].text
        assert 'Bob | 30' in result[0].text
        assert result[0].metadata['sheet_name'] == 'Sheet1'
        assert result[0].metadata['file_name'] == 'test.xlsx'

    @patch('openpyxl.load_workbook')
    def test_load_data_with_multiple_sheets(self, mock_load_workbook):
        """Test loading Excel data with multiple sheets."""
        # Mock workbook with multiple sheets
        mock_workbook = MagicMock()
        mock_workbook.sheetnames = ['Sheet1', 'Sheet2']
        
        # Mock first sheet
        mock_sheet1 = MagicMock()
        mock_sheet1.max_row = 2
        mock_sheet1.max_column = 2
        mock_sheet1.cell.return_value = MagicMock(value='Data1')
        
        # Mock second sheet
        mock_sheet2 = MagicMock()
        mock_sheet2.max_row = 2
        mock_sheet2.max_column = 2
        mock_sheet2.cell.return_value = MagicMock(value='Data2')
        
        def mock_getitem(sheet_name):
            if sheet_name == 'Sheet1':
                return mock_sheet1
            elif sheet_name == 'Sheet2':
                return mock_sheet2
            return None
        
        mock_workbook.__getitem__ = mock_getitem
        mock_load_workbook.return_value = mock_workbook

        result = self.reader._load_data('test.xlsx')
        
        assert len(result) == 2
        assert result[0].metadata['sheet_name'] == 'Sheet1'
        assert result[1].metadata['sheet_name'] == 'Sheet2'

    def test_load_data_import_error(self):
        """Test ImportError when openpyxl is not available."""
        with patch.dict('sys.modules', {'openpyxl': None}):
            with pytest.raises(ImportError) as exc_info:
                self.reader._load_data('test.xlsx')
            assert "openpyxl is required to read Excel files" in str(exc_info.value)

    @patch('openpyxl.load_workbook')
    def test_load_data_with_ext_info(self, mock_load_workbook):
        """Test loading data with additional metadata."""
        # Mock workbook
        mock_workbook = MagicMock()
        mock_worksheet = MagicMock()
        mock_worksheet.sheetnames = ['Sheet1']
        mock_worksheet.max_row = 1
        mock_worksheet.max_column = 1
        mock_worksheet.cell.return_value = MagicMock(value='Test')
        
        mock_workbook.__getitem__.return_value = mock_worksheet
        mock_workbook.sheetnames = ['Sheet1']
        mock_load_workbook.return_value = mock_workbook

        ext_info = {'custom_key': 'custom_value'}
        result = self.reader._load_data('test.xlsx', ext_info=ext_info)
        
        assert len(result) == 1
        assert result[0].metadata['custom_key'] == 'custom_value'
        assert result[0].metadata['file_name'] == 'test.xlsx'

    @patch('openpyxl.load_workbook')
    def test_load_data_empty_sheet(self, mock_load_workbook):
        """Test loading empty Excel sheet."""
        # Mock empty workbook
        mock_workbook = MagicMock()
        mock_worksheet = MagicMock()
        mock_worksheet.sheetnames = ['Sheet1']
        mock_worksheet.max_row = 0
        mock_worksheet.max_column = 0
        mock_worksheet.cell.return_value = MagicMock(value=None)
        
        mock_workbook.__getitem__.return_value = mock_worksheet
        mock_workbook.sheetnames = ['Sheet1']
        mock_load_workbook.return_value = mock_workbook

        result = self.reader._load_data('test.xlsx')
        
        # Empty sheet should not create any documents
        assert len(result) == 0

    def test_load_data_with_path_object(self):
        """Test loading data with Path object."""
        with patch('openpyxl.load_workbook') as mock_load_workbook:
            # Mock workbook
            mock_workbook = MagicMock()
            mock_worksheet = MagicMock()
            mock_worksheet.sheetnames = ['Sheet1']
            mock_worksheet.max_row = 1
            mock_worksheet.max_column = 1
            mock_worksheet.cell.return_value = MagicMock(value='Test')
            
            mock_workbook.__getitem__.return_value = mock_worksheet
            mock_workbook.sheetnames = ['Sheet1']
            mock_load_workbook.return_value = mock_workbook

            file_path = Path('test.xlsx')
            result = self.reader._load_data(file_path)
            
            assert len(result) == 1
            assert result[0].metadata['file_name'] == 'test.xlsx'
