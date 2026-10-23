"""Pinned, CPU-only CLIP image/text vectors with explicit offline loading."""

import asyncio
import base64
import copy
import io
import threading
from typing import Any

from pydantic import Field, PrivateAttr

from agentuniverse.agent.action.knowledge.embedding.embedding import Embedding


class LocalClipEmbedding(Embedding):
    """Encode text and original images in one normalized CLIP vector space.

    Install torch>=2.6 and transformers separately. Loading is cache-only by
    default; model downloads require explicit allow_download=True. Inference is
    serialized per instance and always runs on CPU in evaluation mode.
    """

    embedding_model_name: str = "openai/clip-vit-base-patch32"
    revision: str = Field(default="3d74acf9a28c67741b2f4f2ea7635f0aaf6f0268", pattern=r"^[0-9a-f]{40}$")
    embedding_dims: int = Field(default=512, strict=True, gt=0)
    allow_download: bool = False
    batch_size: int = Field(default=8, strict=True, ge=1, le=64)
    max_items: int = Field(default=128, strict=True, ge=1, le=4096)
    max_pixels: int = Field(default=25_000_000, strict=True, gt=0)
    max_image_bytes: int = Field(default=20_000_000, strict=True, gt=0)
    _model: Any = PrivateAttr(default=None)
    _processor: Any = PrivateAttr(default=None)
    _lock: Any = PrivateAttr(default_factory=threading.RLock)
    _loaded_spec: Any = PrivateAttr(default=None)

    def _initialize_by_component_configer(self, configer):
        super()._initialize_by_component_configer(configer)
        options = configer.configer.value.get("clip", {})
        allowed = {
            "embedding_model_name",
            "revision",
            "embedding_dims",
            "allow_download",
            "batch_size",
            "max_items",
            "max_pixels",
            "max_image_bytes",
        }
        if not isinstance(options, dict) or set(options) - allowed:
            raise ValueError("Unknown CLIP configuration option")
        if self._model is not None:
            raise ValueError("Cannot reconfigure a loaded CLIP instance")
        validated = type(self)(**options)
        for key in allowed:
            setattr(self, key, getattr(validated, key))
        return self

    def _load(self):
        spec = (self.embedding_model_name, self.revision, self.embedding_dims)
        if self._model is not None:
            if spec != self._loaded_spec:
                raise ValueError("Create a new instance to change the loaded model")
            return
        from transformers import CLIPModel, CLIPProcessor

        kwargs = dict(revision=self.revision, local_files_only=not self.allow_download)
        processor = CLIPProcessor.from_pretrained(self.embedding_model_name, **kwargs)
        model = CLIPModel.from_pretrained(self.embedding_model_name, weights_only=True, **kwargs)
        model.to("cpu").eval()
        if model.config.projection_dim != self.embedding_dims:
            raise ValueError("Configured embedding_dims differs from model projection_dim")
        self._processor, self._model, self._loaded_spec = processor, model, spec

    def _check_items(self, items):
        if not isinstance(items, list) or len(items) > self.max_items:
            raise ValueError("Expected a list bounded by max_items")

    def _normalize(self, features):
        import torch

        norms = features.norm(dim=-1, keepdim=True)
        if not torch.isfinite(features).all() or not torch.isfinite(norms).all() or (norms <= 0).any():
            raise ValueError("Invalid CLIP vector")
        if features.shape[-1] != self.embedding_dims:
            raise ValueError("CLIP vector dimension mismatch")
        return (features / norms).tolist()

    def get_embeddings(self, texts, **kwargs):
        """Encode strings without silently truncating CLIP's context window."""
        self._check_items(texts)
        if not texts:
            return []
        if any(not isinstance(text, str) or not text.strip() for text in texts):
            raise ValueError("CLIP texts must be nonempty strings")
        import torch

        with self._lock, torch.inference_mode():
            self._load()
            vectors = []
            for start in range(0, len(texts), self.batch_size):
                inputs = self._processor(
                    text=texts[start : start + self.batch_size], padding=True, truncation=False, return_tensors="pt"
                )
                if inputs["input_ids"].shape[1] > self._model.config.text_config.max_position_embeddings:
                    raise ValueError("Text exceeds the CLIP token window")
                vectors.extend(self._normalize(self._model.get_text_features(**inputs)))
            return vectors

    async def async_get_embeddings(self, texts, **kwargs):
        return await asyncio.to_thread(self.get_embeddings, texts, **kwargs)

    def get_image_embeddings(self, images):
        """Encode Pillow images; never fetch a URL or execute image captions."""
        import torch
        from PIL import Image, ImageOps

        self._check_items(images)
        if not images:
            return []
        for image in images:
            if not isinstance(image, Image.Image):
                raise TypeError("Expected Pillow images")
            if image.width * image.height > self.max_pixels:
                raise ValueError("Image exceeds max_pixels")
            if getattr(image, "n_frames", 1) != 1:
                raise ValueError("CLIP accepts only single-frame images")
        with self._lock, torch.inference_mode():
            self._load()
            vectors = []
            for start in range(0, len(images), self.batch_size):
                batch = []
                try:
                    for image in images[start : start + self.batch_size]:
                        with ImageOps.exif_transpose(image) as display, display.convert("RGBA") as rgba:
                            rgb = Image.new("RGB", rgba.size, "white")
                            rgb.paste(rgba, mask=rgba.getchannel("A"))
                            batch.append(rgb)
                    inputs = self._processor(images=batch, return_tensors="pt")
                    vectors.extend(self._normalize(self._model.get_image_features(**inputs)))
                finally:
                    for image in batch:
                        image.close()
            return vectors

    async def async_get_image_embeddings(self, images):
        return await asyncio.to_thread(self.get_image_embeddings, images)

    def embed_image_documents(self, documents):
        """Return copies of ImageDocuments with image_embedding and embedding.

        origin_image accepts Pillow pixels or strict base64 encoded image bytes,
        following ImageDocument's contract. Strings are never treated as URLs.
        """
        from PIL import Image

        from agentuniverse.agent.action.knowledge.store.image_document import ImageDocument

        self._check_items(documents)
        images, owned = [], []
        try:
            for doc in documents:
                if not isinstance(doc, ImageDocument):
                    raise TypeError("Expected ImageDocument")
                image = doc.origin_image
                if isinstance(image, str):
                    if len(image) > 4 * ((self.max_image_bytes + 2) // 3):
                        raise ValueError("Encoded image exceeds max_image_bytes")
                    raw = base64.b64decode(image, validate=True)
                    if len(raw) > self.max_image_bytes:
                        raise ValueError("Image exceeds max_image_bytes")
                    image = Image.open(io.BytesIO(raw))
                    owned.append(image)
                images.append(image)
            vectors = self.get_image_embeddings(images)
            result = []
            for doc, vector in zip(documents, vectors):
                cloned = doc.model_copy()
                cloned.metadata = copy.deepcopy(doc.metadata or {})
                cloned.metadata["clip_embedding"] = self.provenance()
                cloned.embedding = list(vector)
                cloned.image_embedding = list(vector)
                result.append(cloned)
            return result
        finally:
            for image in owned:
                image.close()

    def embed_query(self, query):
        """Return a copied Query; text vectors precede image vectors explicitly."""
        texts = query.query_text_bundles or ([query.query_str] if query.query_str else [])
        images = query.query_image_bundles or []
        if len(texts) + len(images) > self.max_items:
            raise ValueError("Query exceeds max_items")
        cloned = query.model_copy(deep=True)
        cloned.embeddings = self.get_embeddings(texts) + self.get_image_embeddings(images)
        cloned.ext_info = copy.deepcopy(query.ext_info or {})
        cloned.ext_info["clip_embedding"] = {
            **self.provenance(),
            "vector_modalities": ["text"] * len(texts) + ["image"] * len(images),
        }
        return cloned

    def provenance(self):
        return {
            "model": self.embedding_model_name,
            "revision": self.revision,
            "dimensions": self.embedding_dims,
            "normalization": "l2",
            "device": "cpu",
        }
