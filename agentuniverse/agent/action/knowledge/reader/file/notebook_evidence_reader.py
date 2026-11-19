"""Read notebook cell evidence without executing or trusting cached outputs."""

import hashlib
import json
import math
import re
from copy import deepcopy
from pathlib import Path
from typing import ClassVar

from pydantic import StrictBool, StrictInt

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON object key in notebook")
        result[key] = value
    return result


def _constant(value):
    raise ValueError("Non-finite JSON number in notebook")


def _float(value):
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("Non-finite JSON number in notebook")
    return result


def _text(value):
    # The nbformat schema accepts strings or lists of strings on disk.
    return value if isinstance(value, str) else "".join(value)


def _digest(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class NotebookEvidenceReader(Reader):
    """Extract separate source/output Documents from local nbformat 4.0–4.5.

    Output Documents require explicit opt-in and carry an unverified-cache
    warning in both text and metadata. No kernels, renderers or attachment
    decoders are started. Input order is retained, never execution-count order.
    """

    include_text_outputs: StrictBool = False
    include_error_outputs: StrictBool = False
    max_file_bytes: StrictInt = 20000000
    max_cells: StrictInt = 5000
    max_outputs: StrictInt = 10000
    max_source_chars: StrictInt = 200000
    max_output_chars: StrictInt = 200000
    max_total_chars: StrictInt = 2000000

    _OPTIONS: ClassVar[tuple] = (
        "include_text_outputs",
        "include_error_outputs",
        "max_file_bytes",
        "max_cells",
        "max_outputs",
        "max_source_chars",
        "max_output_chars",
        "max_total_chars",
    )

    def _settings(self):
        for key in self._OPTIONS[:2]:
            if type(getattr(self, key)) is not bool:
                raise ValueError(f"{key} must be a boolean")
        ceilings = (100000000, 50000, 100000, 2000000, 2000000, 20000000)
        for key, ceiling in zip(self._OPTIONS[2:], ceilings):
            value = getattr(self, key)
            if type(value) is not int or not 1 <= value <= ceiling:
                raise ValueError(f"{key} must be between 1 and {ceiling}")

    def _initialize_by_component_configer(self, config):
        candidate = self.model_copy(deep=True)
        for key in self._OPTIONS:
            if key in config.configer.value:
                setattr(candidate, key, config.configer.value[key])
        candidate._settings()
        super()._initialize_by_component_configer(config)
        for key in self._OPTIONS:
            setattr(self, key, getattr(candidate, key))
        return self

    def _read(self, path):
        with path.open("rb") as stream:
            raw = stream.read(self.max_file_bytes + 1)
        if len(raw) > self.max_file_bytes:
            raise ValueError("Notebook exceeds max_file_bytes")
        try:
            notebook = json.loads(
                raw.decode("utf-8"), object_pairs_hook=_object, parse_constant=_constant, parse_float=_float
            )
        except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
            raise ValueError("Notebook must be finite-depth UTF-8 JSON") from error
        if not isinstance(notebook, dict):
            raise ValueError("Notebook must be a JSON object")
        major, minor = notebook.get("nbformat"), notebook.get("nbformat_minor")
        if type(major) is not int or major != 4 or type(minor) is not int or not 0 <= minor <= 5:
            raise ValueError("Only nbformat 4.0 through 4.5 are supported; no automatic conversion")
        cells = notebook.get("cells")
        if not isinstance(cells, list) or len(cells) > self.max_cells:
            raise ValueError("Notebook cells must be a list within max_cells")
        seen, outputs_count = set(), 0
        for index, cell in enumerate(cells):
            if not isinstance(cell, dict):
                raise ValueError(f"Cell {index} must be an object")
            # Reject before nbformat.validate, which can otherwise repair IDs.
            if minor == 5:
                identifier = cell.get("id")
                if not isinstance(identifier, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", identifier):
                    raise ValueError(f"Cell {index} has a missing or invalid id")
                if identifier in seen:
                    raise ValueError(f"Cell {index} has a duplicate id")
                seen.add(identifier)
            outputs = cell.get("outputs", [])
            if not isinstance(outputs, list):
                raise ValueError(f"Cell {index} outputs must be a list")
            outputs_count += len(outputs)
            if outputs_count > self.max_outputs:
                raise ValueError("Notebook exceeds max_outputs")
        try:
            import nbformat
        except ImportError as error:
            raise ImportError("NotebookEvidenceReader requires agentUniverse[notebook_ext]") from error
        try:
            nbformat.validate(notebook, version=4, version_minor=minor)
        except nbformat.ValidationError as error:
            location = "/" + "/".join(str(part) for part in error.absolute_path)
            raise ValueError(f"Invalid notebook schema at {location}") from error
        return notebook, hashlib.sha256(raw).hexdigest()

    def _output(self, output):
        kind = output["output_type"]
        if kind == "error":
            if not self.include_error_outputs:
                return None, "error_outputs_disabled"
            return output["ename"] + ": " + output["evalue"] + "\n" + "\n".join(output["traceback"]), None
        if not self.include_text_outputs:
            return None, "text_outputs_disabled"
        if kind == "stream":
            return _text(output["text"]), None
        if "text/plain" in output["data"]:
            return _text(output["data"]["text/plain"]), None
        return None, "no_plain_text_representation"

    def load_notebook(self, file, ext_info=None, notebook_id=None):
        """Return ``(documents, report)`` with snapshot-scoped source pointers.

        Args:
            file: Local UTF-8 .ipynb file. No URL fetching or kernel execution.
            ext_info: Optional metadata copied independently into each Document.
            notebook_id: Stable caller namespace for cross-directory imports.
                Defaults to the absolute file URI. IDs also include the raw
                file digest: a new snapshot intentionally has different IDs.

        Raises:
            ValueError: Invalid schema, ambiguous IDs or exceeded resource limits.
            ImportError: The optional nbformat dependency is not installed.
            OSError: The local file could not be read.
        """
        self._settings()
        if ext_info is not None and not isinstance(ext_info, dict):
            raise ValueError("ext_info must be a dictionary")
        if ext_info and "notebook_evidence" in ext_info:
            raise ValueError("notebook_evidence is reserved source metadata")
        path = Path(file).resolve()
        if path.suffix.lower() != ".ipynb":
            raise ValueError("Expected a local .ipynb file")
        if notebook_id is None:
            notebook_id = path.as_uri()
        if not isinstance(notebook_id, str) or not notebook_id.strip() or len(notebook_id) > 4096:
            raise ValueError("notebook_id must be a nonempty string of at most 4096 characters")
        notebook, raw_sha = self._read(path)
        documents, omitted, total_chars = [], [], 0
        notebook_key = json.dumps([notebook_id, raw_sha], ensure_ascii=True)
        language = notebook["metadata"].get("language_info", {}).get("name")

        def append(text, info, identifier):
            nonlocal total_chars
            total_chars += len(text)
            if total_chars > self.max_total_chars:
                raise ValueError("Notebook extraction exceeds max_total_chars; no partial result returned")
            metadata = deepcopy(ext_info) if ext_info else {}
            metadata["notebook_evidence"] = deepcopy(info)
            documents.append(Document(id=identifier, text=text, metadata=metadata))

        for index, cell in enumerate(notebook["cells"]):
            cell_key = "id:" + cell["id"] if "id" in cell else f"index:{index}"
            source_id = _digest(notebook_key + ":" + cell_key + ":source")
            source = _text(cell["source"])
            if len(source) > self.max_source_chars:
                raise ValueError(f"Cell {index} exceeds max_source_chars")
            info = {
                "notebook_id": notebook_id,
                "file_path": str(path),
                "file_name": path.name,
                "file_sha256": raw_sha,
                "nbformat": 4,
                "nbformat_minor": notebook["nbformat_minor"],
                "cell_index": index,
                "cell_id": cell.get("id"),
                "cell_key": cell_key,
                "cell_type": cell["cell_type"],
                "language": language,
                "execution_count": cell.get("execution_count"),
                "kind": "source",
                "json_pointer": f"/cells/{index}/source",
                "source_document_id": source_id,
                "text_sha256": _digest(source),
                "execution_verified": False,
                "output_count": len(cell.get("outputs", [])),
                "attachment_names": sorted(cell.get("attachments", {})),
                "raw_format": cell["metadata"].get("format") if cell["cell_type"] == "raw" else None,
            }
            append(source, info, source_id)
            for output_index, output in enumerate(cell.get("outputs", [])):
                content, reason = self._output(output)
                pointer = f"/cells/{index}/outputs/{output_index}"
                if reason:
                    omitted.append({"json_pointer": pointer, "reason": reason})
                    continue
                if len(content) > self.max_output_chars:
                    raise ValueError(f"Output {pointer} exceeds max_output_chars")
                output_info = dict(info)
                output_info.update(
                    {
                        "kind": "cached_output",
                        "json_pointer": pointer,
                        "output_index": output_index,
                        "output_type": output["output_type"],
                        "output_execution_count": output.get("execution_count"),
                        "stream_name": output.get("name"),
                        "cache_status": "unverified",
                        "selected_mime": "text/plain" if "data" in output else None,
                        "available_mime_types": sorted(output.get("data", {})),
                        "payload_sha256": _digest(content),
                    }
                )
                rendered = "[UNVERIFIED NOTEBOOK CACHED OUTPUT; not executed by this reader]\n" + content
                output_info["text_sha256"] = _digest(rendered)
                append(rendered, output_info, _digest(notebook_key + ":" + cell_key + f":output:{output_index}"))
        report = {
            "file_sha256": raw_sha,
            "cell_count": len(notebook["cells"]),
            "document_count": len(documents),
            "omitted_outputs": omitted,
            "execution_verified": False,
            "total_chars": total_chars,
        }
        return documents, report

    def _load_data(self, file, ext_info=None, notebook_id=None):
        return self.load_notebook(file, ext_info, notebook_id)[0]
