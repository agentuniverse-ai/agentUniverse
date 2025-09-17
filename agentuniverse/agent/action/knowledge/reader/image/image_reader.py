# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/02/14 23:05
# @Author  : zhouxiaoji
# @Email   : zh_xiaoji@qq.com
# @FileName: image_reader.py

from pathlib import Path
from typing import Any, List, Optional, Dict, Union
import numpy as np
from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

SUPPORTED_FORMATS = {"jpg", "jpeg", "png", "bmp", "webp", "tiff"}


class ImageReader(Reader):
    """Image reader."""

    languages: List[str] = ["en", "ch_sim"]
    use_gpu: bool = False
    image_model: str = "microsoft/git-base-coco"
    _ocr_reader = None
    _description_pipeline = None

    def _initialize_by_component_configer(self, reader_configer: ComponentConfiger) -> "ImageReader":
        """Initialize the reader by the ComponentConfiger object.

        Args:
            reader_configer: A configer contains reader basic info.
        Returns:
            ImageReader: A reader instance.
        """
        super()._initialize_by_component_configer(reader_configer)
        if hasattr(reader_configer, "languages"):
            self.languages = reader_configer.languages
        if hasattr(reader_configer, "use_gpu"):
            self.use_gpu = reader_configer.use_gpu
        if hasattr(reader_configer, "image_model"):
            self.image_model = reader_configer.image_model
        return self

    def _get_ocr_reader(self):
        """Lazy initialization of OCR reader."""
        if self._ocr_reader is None:
            try:
                import easyocr
            except ImportError:
                raise ImportError("easyocr is required. Install with: pip install easyocr")
            self._ocr_reader = easyocr.Reader(self.languages, gpu=self.use_gpu)
        return self._ocr_reader

    def _get_description_pipeline(self):
        """Lazy initialization of image description pipeline."""
        if self._description_pipeline is None:
            try:
                from transformers import pipeline
            except ImportError:
                raise ImportError("transformers is required. Install with: pip install transformers")
            self._description_pipeline = pipeline("image-to-text", model=self.image_model)
        return self._description_pipeline

    def extract_text(self, image: Any) -> str:
        """Extract text from image using OCR."""
        reader = self._get_ocr_reader()
        results = reader.readtext(np.array(image))
        return "\n".join([text[1] for text in results])

    def generate_description(self, image: Any) -> str:
        """Generate description of the image content."""
        pipeline = self._get_description_pipeline()
        description = pipeline(image)[0]["generated_text"]
        return description

    def _load_data(self, file: Union[str, Path], ext_info: Optional[Dict] = None) -> List[Document]:
        """Load and process image file to extract text content.

        Args:
            file (Union[str, Path]): Path to the image file to be processed
            ext_info (Optional[Dict], optional): Additional metadata or processing parameters. Defaults to None.

        Returns:
            List[Document]: A list of Document objects containing the extracted text and metadata.

        Note:
            Current implementation converts image to text before embedding to maintain vector space
            consistency and semantic alignment with other document types in the knowledge base.
            However, a more optimal approach would be direct image-to-embedding conversion, which
            could better preserve visual semantic information and potentially improve retrieval
            quality for image-related queries.
        """
        try:
            from PIL import Image, ImageFile
        except ImportError as e:
            raise ImportError("PIL is required. Install with: pip install Pillow") from e

        def parse_metadata(image: ImageFile) -> Dict[str, Any]:
            width, height = image.size
            channels = len(image.getbands())
            mode = image.mode
            metadata: Dict[str, Any] = {
                "file_name": file.name,
                "format": image_format,
                "image_size": {"width": width, "height": height},
                "channel": channels,
                "color_mode": mode,
            }
            if ext_info is not None:
                metadata.update(ext_info)
            return metadata

        try:
            if isinstance(file, str):
                file = Path(file)
            if not file.exists():
                raise FileNotFoundError(f"Image file not found: {file}")

            image_format = file.suffix.lower().lstrip(".")
            if image_format not in SUPPORTED_FORMATS:
                raise ValueError(
                    f"Unsupported image format: {image_format}. Supported formats are: {', '.join(SUPPORTED_FORMATS)}"
                )

            image: ImageFile = Image.open(file)
            ocr_text: str = self.extract_text(image)
            image_description: str = self.generate_description(image)
            image_text = (
                f"{ocr_text}\n{image_description}"
                if (ocr_text.strip() and image_description.strip())
                else f"{ocr_text}{image_description}"
            )

            metadata = parse_metadata(image)
            metadata.update({"has_text": bool(ocr_text.strip()), "has_description": bool(image_description.strip())})
            return [Document(text=image_text, metadata=metadata)]
        except Exception as e:
            raise Exception(f"Error processing image {file}: {str(e)}")
