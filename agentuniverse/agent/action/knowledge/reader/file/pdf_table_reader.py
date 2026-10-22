"""Conservative ruled-table extraction with explicit cross-page continuations."""
import hashlib
import io
import json
import math
import re
from copy import deepcopy
from pathlib import Path

from pydantic import Field, StrictFloat, StrictInt, StrictStr

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document


def _json(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False)


class PdfTableContinuationReader(Reader):
    """Merge only adjacent edge tables with matching explicit table captions.

    Requires a repeated nonempty header, matching ruled column boundaries and a
    literal continuation marker on the next caption. Other tables stay separate.
    No OCR, row-spanning-cell inference, missing-cell filling or semantic guessing.
    """
    caption_prefix: StrictStr = "Table"
    continuation_marker: StrictStr = "continued"
    edge_margin: StrictFloat = Field(default=84.0, ge=0, le=300)
    caption_lookback: StrictFloat = Field(default=60.0, gt=0, le=300)
    column_tolerance: StrictFloat = Field(default=3.0, ge=0, le=20)
    max_file_bytes: StrictInt = Field(default=32 * 1024 * 1024, ge=1)
    max_pages: StrictInt = Field(default=50, ge=1)
    max_tables: StrictInt = Field(default=200, ge=1)
    max_cells: StrictInt = Field(default=100_000, ge=1)
    max_page_chars: StrictInt = Field(default=50_000, ge=1)
    max_page_edges: StrictInt = Field(default=20_000, ge=1)
    max_output_chars: StrictInt = Field(default=10_000_000, ge=1)

    def _validate_options(self):
        for name in ("caption_prefix", "continuation_marker"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip() or len(value) > 64:
                raise ValueError(name + " must be a nonblank literal up to 64 characters")
        for name in ("edge_margin", "caption_lookback", "column_tolerance"):
            value = getattr(self, name)
            maximum = 20 if name == "column_tolerance" else 300
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not 0 <= value <= maximum or (name == "caption_lookback" and value == 0):
                raise ValueError("invalid geometry option: " + name)
        for name in ("max_file_bytes", "max_pages", "max_tables", "max_cells", "max_page_chars", "max_page_edges", "max_output_chars"):
            if type(getattr(self, name)) is not int or getattr(self, name) < 1:
                raise ValueError(name + " must be a positive integer")

    def _caption(self, page, bbox):
        top = max(0.0, bbox[1] - self.caption_lookback)
        if top >= bbox[1]:
            return None, False, None
        text = page.crop((bbox[0], top, bbox[2], bbox[1])).extract_text() or ""
        pattern = re.compile(r"^\s*" + re.escape(self.caption_prefix) + r"\s+([A-Za-z0-9][A-Za-z0-9._-]{0,31})(?![A-Za-z0-9._-])", re.IGNORECASE)
        marker = re.compile(r"(?<!\w)" + re.escape(self.continuation_marker) + r"(?!\w)", re.IGNORECASE)
        for line in reversed(text.splitlines()):
            match = pattern.match(line)
            if match:
                return match[1], bool(marker.search(line)), line
        return None, False, None

    def _continues(self, previous, current):
        if not previous["eligible"] or not current["eligible"] or not current["continued"]:
            return False
        if current["page"] != previous["page"] + 1 or not previous["last_on_page"] or current["table_index"] != 0:
            return False
        if previous["caption_id"] is None or previous["caption_id"] != current["caption_id"]:
            return False
        def normalize(header):
            return [" ".join(cell.split()) for cell in header]
        if normalize(previous["header"]) != normalize(current["header"]):
            return False
        if previous["page_height"] - previous["bbox"][3] > self.edge_margin or current["bbox"][1] > self.edge_margin:
            return False
        if abs(previous["page_width"] - current["page_width"]) > self.column_tolerance:
            return False
        left, right = previous["columns"], current["columns"]
        return len(left) == len(right) and all(abs(a - b) <= self.column_tolerance for a, b in zip(left, right))

    def _load_data(self, fpath, ext_info=None):
        self._validate_options()
        try:
            import pdfplumber
        except ImportError as error:
            raise ImportError("PDF table reading requires pdfplumber; install agentUniverse[pdf_table_ext]") from error
        if not isinstance(fpath, (str, Path)):
            raise TypeError("PDF table reading requires a local file path")
        path = Path(fpath).resolve(strict=True)
        if ext_info is not None and not isinstance(ext_info, dict):
            raise ValueError("ext_info must be a mapping")
        extra = deepcopy(ext_info or {})
        reserved = {"source", "file_name", "file_sha256", "pdf_table_segments", "pdf_header_assumption"}
        if reserved.intersection(extra):
            raise ValueError("ext_info cannot override PDF table provenance")
        _json(extra)
        with path.open("rb") as source:
            raw = source.read(self.max_file_bytes + 1)
        if len(raw) > self.max_file_bytes:
            raise ValueError("PDF exceeds max_file_bytes")
        digest = hashlib.sha256(raw).hexdigest()
        groups = []
        table_count = cell_count = 0
        previous = None
        with io.BytesIO(raw) as stream, pdfplumber.open(stream) as pdf:
            if len(pdf.pages) > self.max_pages:
                raise ValueError("PDF exceeds max_pages")
            for page in pdf.pages:
                try:
                    if len(page.chars) > self.max_page_chars or len(page.edges) > self.max_page_edges:
                        raise ValueError("PDF page exceeds character/edge limits")
                    tables = sorted(page.find_tables({"vertical_strategy": "lines", "horizontal_strategy": "lines"}),
                                    key=lambda table: (table.bbox[1], table.bbox[0]))
                    for index, table in enumerate(tables):
                        table_count += 1
                        if table_count > self.max_tables:
                            raise ValueError("PDF exceeds max_tables")
                        rows = table.extract()
                        cell_count += sum(len(row) for row in rows)
                        if cell_count > self.max_cells:
                            raise ValueError("PDF exceeds max_cells")
                        header = rows[0] if rows else []
                        caption_id, continued, caption = self._caption(page, table.bbox)
                        eligible = (len(header) >= 2 and all(isinstance(cell, str) and cell.strip() for cell in header)
                                    and all(len(row) == len(header) for row in rows)
                                    and all(len(row.cells) == len(header) and all(cell is not None for cell in row.cells)
                                            for row in table.rows))
                        columns = [coordinate for cell in table.rows[0].cells for coordinate in (cell[0], cell[2])] if eligible else []
                        part = {"page": page.page_number, "table_index": index, "bbox": list(table.bbox),
                                "page_width": page.width, "page_height": page.height,
                                "last_on_page": index == len(tables) - 1, "caption_id": caption_id,
                                "continued": continued, "caption": caption, "header": header,
                                "eligible": eligible, "columns": columns}
                        if previous is not None and self._continues(previous, part):
                            group = groups[-1]
                            start = len(group["rows"])
                            group["rows"].extend(rows[1:])
                            group["segments"].append({**part, "row_range": [start, len(group["rows"])]})
                        else:
                            groups.append({"header": header, "rows": rows[1:],
                                           "segments": [{**part, "row_range": [0, max(0, len(rows) - 1)]}]})
                        previous = part
                finally:
                    page.close()
        output = []
        output_chars = 0
        for group in groups:
            content = _json({"header": group["header"], "rows": group["rows"]})
            metadata = deepcopy(extra)
            metadata.update({"source": path.as_uri(), "file_name": path.name, "file_sha256": digest,
                             "pdf_table_segments": group["segments"], "pdf_header_assumption": "first_extracted_row"})
            output_chars += len(content) + len(_json(metadata))
            if output_chars > self.max_output_chars:
                raise ValueError("PDF tables exceed max_output_chars")
            identity = _json([path.as_uri(), digest, [(part["page"], part["table_index"]) for part in group["segments"]]])
            output.append(Document(id=hashlib.sha256(identity.encode("utf-8")).hexdigest(), text=content, metadata=metadata))
        return output

    def _initialize_by_component_configer(self, config):
        names = ("caption_prefix", "continuation_marker", "edge_margin", "caption_lookback", "column_tolerance",
                 "max_file_bytes", "max_pages", "max_tables", "max_cells", "max_page_chars", "max_page_edges", "max_output_chars")
        validated = PdfTableContinuationReader(**{name: getattr(config, name, getattr(self, name)) for name in names})
        validated._validate_options()
        super()._initialize_by_component_configer(config)
        for name in names:
            setattr(self, name, getattr(validated, name))
        return self
