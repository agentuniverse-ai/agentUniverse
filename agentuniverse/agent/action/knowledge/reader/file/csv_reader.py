# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/2/2 22:00
# @Author  : wangyapei
# @FileName: csv_reader.py

import csv
from pathlib import Path
from typing import List, Union, Optional, Dict

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document


class CSVReader(Reader):
    """CSV file reader.

    Used to read and parse CSV format files, supports local file paths or file objects as input.
    """

    def _load_data(
        self, file: Union[str, Path], delimiter: str = ",", quotechar: str = '"', ext_info: Optional[Dict] = None
    ) -> List[Document]:
        """Parse CSV file.

        Args:
            file: CSV file path or file object
            delimiter: CSV delimiter, default is comma
            quotechar: Quote character, default is double quote
            ext_info: Additional metadata information

        Returns:
            List[Document]: List of documents containing CSV content

        Raises:
            FileNotFoundError: Raised when file does not exist
            ValueError: Raised when file reading fails
        """
        try:
            if isinstance(file, str):
                file = Path(file)

            if isinstance(file, Path):
                if not file.exists():
                    raise FileNotFoundError(f"File not found: {file}")
                file_content = file.open(newline="", mode="r", encoding="utf-8")
            else:
                file.seek(0)
                file_content = file

            csv_content = []
            with file_content as csvfile:
                csv_reader = csv.reader(csvfile, delimiter=delimiter, quotechar=quotechar)
                for row in csv_reader:
                    # Filter out completely empty rows
                    if any(cell.strip() for cell in row):
                        # Remove empty values at the end of row
                        while row and not row[-1].strip():
                            row.pop()
                        # Only add non-empty values to result
                        csv_content.append(", ".join(filter(None, row)))

            # Combine all valid rows into final text
            final_content = "\n".join(csv_content)

            # Get metadata
            metadata = {"file_name": getattr(file, "name", "unknown")}
            if ext_info:
                metadata.update(ext_info)
            # print(f"csv_content: {final_content} \n metadata: {metadata}")
            return [Document(text=final_content, metadata=metadata)]
        except Exception as e:
            raise ValueError(f"Failed to read CSV file: {str(e)}") from e
