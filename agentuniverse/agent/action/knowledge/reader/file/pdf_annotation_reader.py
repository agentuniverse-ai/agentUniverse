"""Read PDF review annotations and raw page-space anchors without executing content."""

import hashlib
import io
import math
from copy import deepcopy
from pathlib import Path
from typing import ClassVar

from pydantic import StrictInt

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document


def _reference(value):
    if hasattr(value, "idnum"):
        return f"{value.idnum} {value.generation} R"
    return None


def _numbers(value, count=None, multiple=None):
    if (
        not isinstance(value, (list, tuple))
        or (count and len(value) != count)
        or (multiple and (not value or len(value) % multiple))
    ):
        raise ValueError("Invalid annotation coordinates")
    result = []
    for item in value:
        if isinstance(item, bool) or not isinstance(item, (int, float)) or not math.isfinite(float(item)):
            raise ValueError("Non-finite or non-numeric PDF coordinate")
        result.append(float(item))
    return result


def _string(obj, key):
    value = obj.get(key)
    if value is not None and not isinstance(value, str):
        raise ValueError(f"Unsupported PDF string in {key}")
    return value


class PdfAnnotationReader(Reader):
    """One Document per supported review annotation; coordinates are not quotations."""

    max_file_bytes: StrictInt = 32000000
    max_pages: StrictInt = 2000
    max_annotations: StrictInt = 20000
    max_document_chars: StrictInt = 200000
    max_total_chars: StrictInt = 10000000
    _OPTIONS: ClassVar[dict] = {
        "max_file_bytes": 128000000,
        "max_pages": 10000,
        "max_annotations": 100000,
        "max_document_chars": 2000000,
        "max_total_chars": 40000000,
    }
    _TYPES: ClassVar[set] = {"/Text", "/FreeText", "/Highlight", "/Underline", "/Squiggly", "/StrikeOut"}

    def _settings(self):
        for key, maximum in self._OPTIONS.items():
            value = getattr(self, key)
            if type(value) is not int or not 1 <= value <= maximum:
                raise ValueError(f"Invalid {key}; expected integer in 1..{maximum}")

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

    def load_annotations(self, file, ext_info=None):
        """Return Documents and omitted annotation/reply status report.

        Local, unencrypted PDFs only. Original page user-space coordinates are
        preserved with crop/media boxes, rotation and UserUnit, never normalized
        to pixels. No page text, attachments, actions or appearance extraction.
        """
        self._settings()
        if ext_info is not None and (not isinstance(ext_info, dict) or "pdf_annotation" in ext_info):
            raise ValueError("ext_info must be a dictionary without reserved pdf_annotation")
        path = Path(file).resolve()
        if path.suffix.lower() != ".pdf":
            raise ValueError("Expected local PDF")
        with path.open("rb") as stream:
            raw = stream.read(self.max_file_bytes + 1)
        if len(raw) > self.max_file_bytes:
            raise ValueError("max_file_bytes exceeded")
        try:
            from pypdf import PdfReader
            from pypdf.generic import DictionaryObject
        except ImportError as error:
            raise ImportError("PdfAnnotationReader requires agentUniverse[pdf_ext]") from error
        pdf = PdfReader(io.BytesIO(raw), strict=True)
        if pdf.is_encrypted:
            raise ValueError("Encrypted PDF is unsupported")
        if len(pdf.pages) > self.max_pages:
            raise ValueError("max_pages exceeded")
        digest = hashlib.sha256(raw).hexdigest()
        entries, references, omitted, count = [], {}, [], 0
        for page_index, page in enumerate(pdf.pages):
            annots = page.get("/Annots", [])
            if hasattr(annots, "get_object"):
                annots = annots.get_object()
            if not isinstance(annots, list):
                raise ValueError("Invalid page annotation array")
            for annotation_index, reference in enumerate(annots):
                count += 1
                if count > self.max_annotations:
                    raise ValueError("max_annotations exceeded")
                locator = f"page:{page_index + 1}/annotation:{annotation_index}"
                identifier = hashlib.sha256((digest + locator).encode()).hexdigest()
                ref = _reference(reference)
                if ref:
                    references.setdefault(ref, []).append(identifier)
                obj = reference.get_object() if hasattr(reference, "get_object") else reference
                if not isinstance(obj, DictionaryObject):
                    raise ValueError("Invalid annotation object")
                subtype = obj.get("/Subtype")
                if subtype not in self._TYPES:
                    omitted.append(
                        {
                            "page_number": page_index + 1,
                            "annotation_index": annotation_index,
                            "subtype": str(subtype),
                            "reason": "unsupported_annotation_type",
                        }
                    )
                    continue
                rect = _numbers(obj.get("/Rect"), count=4)
                quads = _numbers(obj.get("/QuadPoints"), multiple=8) if "/QuadPoints" in obj else None
                rotation = page.rotation
                user_unit = page.get("/UserUnit", 1)
                if (
                    not isinstance(rotation, int)
                    or rotation % 90
                    or not isinstance(user_unit, (int, float))
                    or not math.isfinite(float(user_unit))
                    or user_unit <= 0
                ):
                    raise ValueError("Invalid page rotation/UserUnit")
                reply = obj.raw_get("/IRT") if "/IRT" in obj else None
                flags = obj.get("/F", 0)
                if not isinstance(flags, int):
                    raise ValueError("Invalid annotation flags")
                info = {
                    "file_sha256": digest,
                    "file_path": str(path),
                    "page_number": page_index + 1,
                    "annotation_index": annotation_index,
                    "object_reference": ref,
                    "subtype": subtype[1:],
                    "contents": _string(obj, "/Contents"),
                    "author": _string(obj, "/T"),
                    "subject": _string(obj, "/Subj"),
                    "name": _string(obj, "/NM"),
                    "creation_date_raw": _string(obj, "/CreationDate"),
                    "modified_date_raw": _string(obj, "/M"),
                    "rect": rect,
                    "quad_points": quads,
                    "flags": flags,
                    "coordinate_space": "pdf_default_user_space_unrotated",
                    "media_box": _numbers(list(page.mediabox), count=4),
                    "crop_box": _numbers(list(page.cropbox), count=4),
                    "page_rotation": rotation,
                    "user_unit": float(user_unit),
                    "reply_to_reference": _reference(reply),
                    "reply_type": _string(obj, "/RT"),
                    "reply_status": "unresolved" if reply is not None else "none",
                    "has_rich_text": "/RC" in obj,
                    "has_action": "/A" in obj or "/AA" in obj,
                    "anchor_text_extracted": False,
                }
                entries.append((identifier, info))
        selected = {identifier for identifier, _ in entries}
        documents, total = [], 0
        for identifier, info in entries:
            if info["reply_status"] != "none":
                targets = references.get(info["reply_to_reference"], [])
                if len(targets) == 1:
                    info["reply_to_document_id"] = targets[0] if targets[0] in selected else None
                    info["reply_status"] = "resolved" if targets[0] in selected else "unsupported_target"
                elif len(targets) > 1:
                    info["reply_status"] = "ambiguous_target"
                else:
                    info["reply_status"] = "orphan_or_direct_reference"
            # Keep retrieval focused on the review, with exact geometry in metadata.
            comment = info["contents"] or "[No plain-text comment; see annotation metadata]"
            text = f"PDF {info['subtype']} annotation on page {info['page_number']}\n{comment}"
            total += len(text)
            metadata_chars = sum(len(value) for value in info.values() if isinstance(value, str))
            if max(len(text), metadata_chars) > self.max_document_chars or total > self.max_total_chars:
                raise ValueError("Annotation text budget exceeded")
            metadata = deepcopy(ext_info) if ext_info else {}
            metadata["pdf_annotation"] = deepcopy(info)
            documents.append(Document(id=identifier, text=text, metadata=metadata))
        return documents, {
            "file_sha256": digest,
            "page_count": len(pdf.pages),
            "annotation_count": count,
            "document_count": len(documents),
            "omitted_annotations": omitted,
        }

    def _load_data(self, file, ext_info=None):
        return self.load_annotations(file, ext_info)[0]
