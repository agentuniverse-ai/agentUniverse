# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/19 10:00
# @Author  : Assistant
# @FileName: xlsx_reader.py
from pathlib import Path
from typing import Union, List, Optional, Dict

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document


class XlsxReader(Reader):
    """Excel (.xlsx) file reader.
    
    Used to read and parse Excel format files, supports multiple sheets and various data types.
    """

    def _load_data(self, file: Union[str, Path], ext_info: Optional[Dict] = None) -> List[Document]:
        """Parse Excel file.

        Args:
            file: Excel file path or file object
            ext_info: Additional metadata information

        Returns:
            List[Document]: List of documents containing Excel content

        Note:
            `openpyxl` is required to read Excel files: `pip install openpyxl`
        """
        try:
            import openpyxl
        except ImportError:
            raise ImportError(
                "openpyxl is required to read Excel files: "
                "`pip install openpyxl`"
            )

        if isinstance(file, str):
            file = Path(file)

        # Load the workbook
        workbook = openpyxl.load_workbook(file, data_only=True, read_only=True)
        document_list = []

        try:
            for worksheet in workbook.worksheets:
                sheet_name = worksheet.title
                max_row = worksheet.max_row
                max_col = worksheet.max_column
                sheet_data = []
                # Streaming values avoids allocating missing cells across the
                # worksheet's entire bounding rectangle.
                for values in worksheet.iter_rows(values_only=True):
                    row_data = [str(value) if value is not None else "" for value in values]
                    if any(cell.strip() for cell in row_data):
                        sheet_data.append(" | ".join(row_data))
                if sheet_data:
                    metadata = {
                        "file_name": file.name,
                        "sheet_name": sheet_name,
                        "max_row": max_row,
                        "max_col": max_col,
                    }
                    if ext_info is not None:
                        metadata.update(ext_info)
                    document_list.append(Document(text="\n".join(sheet_data), metadata=metadata))
        finally:
            workbook.close()

        return document_list
