"""Opt-in Tesseract word evidence in display and original image coordinates."""

import hashlib
import io
import json
import math
from pathlib import Path
from typing import Literal, Optional, Tuple

from pydantic import Field, StrictInt

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document


def _original_point(x, y, orientation, width, height):
    """Invert EXIF orientation for continuous pixel-edge coordinates."""
    return {
        1: (x, y),
        2: (width - x, y),
        3: (width - x, height - y),
        4: (x, height - y),
        5: (y, x),
        6: (y, height - x),
        7: (width - y, height - x),
        8: (width - y, x),
    }[orientation]


class OcrEvidenceReader(Reader):
    """Read a single local raster with explicit, non-fallback OCR provenance.

    Boxes are [left, top, right, bottom] pixel edges, with an exclusive bottom
    and right edge. Crop is in the EXIF-normalized full-image coordinate space.
    Confidence is the engine's 0..100 score, not a calibrated probability.
    """

    engine: Literal["tesseract"] = "tesseract"
    language: str = Field(default="eng", pattern=r"^[A-Za-z0-9_+/-]+$")
    page_segmentation: int = Field(default=6, strict=True, ge=3, le=13)
    low_confidence_threshold: float = Field(default=60, ge=0, le=100, allow_inf_nan=False)
    crop: Optional[Tuple[StrictInt, StrictInt, StrictInt, StrictInt]] = None
    timeout_seconds: float = Field(default=30, gt=0, le=300, allow_inf_nan=False)
    max_bytes: int = Field(default=20_000_000, strict=True, gt=0)
    max_pixels: int = Field(default=25_000_000, strict=True, gt=0)
    max_words: int = Field(default=20_000, strict=True, gt=0)

    def _initialize_by_component_configer(self, configer):
        super()._initialize_by_component_configer(configer)
        options = configer.configer.value.get("ocr", {})
        allowed = {
            "engine",
            "language",
            "page_segmentation",
            "low_confidence_threshold",
            "crop",
            "timeout_seconds",
            "max_bytes",
            "max_pixels",
            "max_words",
        }
        if not isinstance(options, dict) or set(options) - allowed:
            raise ValueError("Unknown OCR configuration option")
        validated = type(self)(**options)
        for key in allowed:
            setattr(self, key, getattr(validated, key))
        return self

    def _load_data(self, file, ext_info=None):
        """Return one page document, including an explicit empty OCR result.

        Raises on malformed images, multipage input, engine failures or budgets.
        No automatic orientation detection, rescaling or deskew is performed.
        """
        import pytesseract
        from PIL import Image, ImageOps

        path = Path(file)
        with path.open("rb") as stream:
            raw = stream.read(self.max_bytes + 1)
        if len(raw) > self.max_bytes:
            raise ValueError("OCR source exceeds max_bytes")
        digest = hashlib.sha256(raw).hexdigest()
        with Image.open(io.BytesIO(raw)) as image:
            if getattr(image, "n_frames", 1) != 1:
                raise ValueError("OCR evidence requires a single-frame image")
            width, height = image.size
            if width * height > self.max_pixels:
                raise ValueError("OCR source exceeds max_pixels")
            orientation = image.getexif().get(274, 1)
            if orientation not in range(1, 9):
                raise ValueError("Invalid EXIF orientation")
            with ImageOps.exif_transpose(image) as display:
                dw, dh = display.size
                crop = self.crop or (0, 0, dw, dh)
                left, top, right, bottom = crop
                if not (0 <= left < right <= dw and 0 <= top < bottom <= dh):
                    raise ValueError("OCR crop is outside display image")
                with display.crop(crop).convert("RGBA") as rgba, Image.new("RGB", rgba.size, "white") as pixels:
                    pixels.paste(rgba, mask=rgba.getchannel("A"))
                    # Fixed structured options only; no arbitrary CLI config.
                    data = pytesseract.image_to_data(
                        pixels,
                        lang=self.language,
                        config=f"--psm {self.page_segmentation}",
                        output_type=pytesseract.Output.DICT,
                        timeout=self.timeout_seconds,
                    )
        words = self._words(data, crop, orientation, width, height)
        lines = {}
        for word in words:
            key = tuple(word["line_id"])
            lines.setdefault(key, []).append(word["text"])
        text = "\n".join(" ".join(values) for values in lines.values())
        evidence = {
            "version": 1,
            "engine": self.engine,
            "engine_version": str(pytesseract.get_tesseract_version()),
            "language": self.language,
            "page_segmentation": self.page_segmentation,
            "source_sha256": digest,
            "original_size": [width, height],
            "display_size": [dw, dh],
            "exif_orientation": orientation,
            "crop_display": list(crop),
            "alpha_background": "white",
            "coordinate_convention": "pixel_edges_xyxy",
            "confidence_scale": "tesseract_0_100_not_probability",
            "low_confidence_threshold": self.low_confidence_threshold,
            "status": "recognized" if words else "empty",
            "words": words,
        }
        metadata = dict(ext_info or {})
        metadata.update(file_name=path.name, source=str(path.resolve()), ocr_evidence=evidence)
        identity = hashlib.sha256(json.dumps(evidence, sort_keys=True).encode()).hexdigest()
        return [Document(id=f"ocr:{identity}", text=text, metadata=metadata)]

    def _words(self, data, crop, orientation, width, height):
        keys = (
            "text",
            "level",
            "conf",
            "left",
            "top",
            "width",
            "height",
            "page_num",
            "block_num",
            "par_num",
            "line_num",
            "word_num",
        )
        if not isinstance(data, dict) or any(key not in data for key in keys):
            raise ValueError("Malformed Tesseract result")
        count = len(data["text"])
        if any(len(data[key]) != count for key in keys):
            raise ValueError("Inconsistent Tesseract result columns")
        words = []
        for i in range(count):
            if int(data["level"][i]) != 5 or not data["text"][i].strip():
                continue
            if len(words) >= self.max_words:
                raise ValueError("OCR result exceeds max_words")
            confidence = float(data["conf"][i])
            if not math.isfinite(confidence) or not 0 <= confidence <= 100:
                raise ValueError("Invalid word confidence")
            x, y, w, h = (int(data[key][i]) for key in ("left", "top", "width", "height"))
            if not (0 <= x < x + w <= crop[2] - crop[0] and 0 <= y < y + h <= crop[3] - crop[1]):
                raise ValueError("Invalid word bounding box")
            x, y = x + crop[0], y + crop[1]
            corners = [
                _original_point(px, py, orientation, width, height)
                for px, py in ((x, y), (x + w, y), (x + w, y + h), (x, y + h))
            ]
            words.append(
                {
                    "text": data["text"][i],
                    "confidence": confidence,
                    "low_confidence": confidence < self.low_confidence_threshold,
                    "bbox_display": [x, y, x + w, y + h],
                    "bbox_original": [
                        min(p[0] for p in corners),
                        min(p[1] for p in corners),
                        max(p[0] for p in corners),
                        max(p[1] for p in corners),
                    ],
                    "line_id": [int(data[key][i]) for key in ("page_num", "block_num", "par_num", "line_num")],
                    "word_num": int(data["word_num"][i]),
                }
            )
        return words
