"""Knowledge reader for tab-separated value files."""
from pathlib import Path
from typing import BinaryIO, Dict, List, Optional, TextIO, Union

from agentuniverse.agent.action.knowledge.reader.file.csv_reader import CSVReader
from agentuniverse.agent.action.knowledge.store.document import Document


class TSVReader(CSVReader):
    """Read TSV files using the existing CSV parser with a tab delimiter."""

    def _load_data(self, file: Union[str, Path, TextIO, BinaryIO],
                   quotechar: str = '"',
                   ext_info: Optional[Dict] = None) -> List[Document]:
        """Load a TSV table as one knowledge document.

        Args:
            file: File path or a readable text/binary file object.
            quotechar: Character enclosing fields containing tabs or newlines.
            ext_info: Additional document metadata, following CSVReader rules.

        Returns:
            A document using CSVReader's text normalization and metadata.
        """
        return super()._load_data(file=file, delimiter="\t",
                                  quotechar=quotechar, ext_info=ext_info)
