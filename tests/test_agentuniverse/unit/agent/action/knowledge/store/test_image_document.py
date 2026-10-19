# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_image_document.py

"""Unit tests for the ImageDocument knowledge model."""

import pytest

from agentuniverse.agent.action.knowledge.store.image_document import \
    ImageDocument


class TestImageDocument:
    """Test ImageDocument construction and image-specific fields."""

    def test_full_construction(self):
        doc = ImageDocument(text="hello", origin_image="img.png",
                            image_embedding=[0.1, 0.2],
                            ocr_text="recognized text",
                            ocr_text_embedding=[0.3, 0.4])
        assert doc.origin_image == "img.png"
        assert doc.image_embedding == [0.1, 0.2]
        assert doc.ocr_text == "recognized text"
        assert doc.ocr_text_embedding == [0.3, 0.4]

    def test_optional_fields_accept_none(self):
        doc = ImageDocument(text="hello", origin_image=None,
                            ocr_text=None, ocr_text_embedding=None)
        assert doc.origin_image is None
        assert doc.ocr_text is None
        assert doc.ocr_text_embedding is None
        assert doc.image_embedding == []

    def test_required_fields_must_be_provided(self):
        with pytest.raises(Exception):
            ImageDocument(text="hello")

    def test_deterministic_id_from_text(self):
        kwargs = {"origin_image": "img.png", "ocr_text": "x",
                  "ocr_text_embedding": None}
        assert (ImageDocument(text="hello", **kwargs).id
                == ImageDocument(text="hello", **kwargs).id)
        assert (ImageDocument(text="hello", **kwargs).id
                != ImageDocument(text="world", **kwargs).id)

    def test_inherited_document_fields(self):
        doc = ImageDocument(text="hello", origin_image="img.png",
                            ocr_text=None, ocr_text_embedding=None,
                            metadata={"width": 640})
        assert doc.text == "hello"
        assert doc.metadata == {"width": 640}
        assert doc.keywords == set()

    def test_explicit_id_is_preserved(self):
        doc = ImageDocument(id="img-1", text="hello", origin_image=None,
                            ocr_text=None, ocr_text_embedding=None)
        assert doc.id == "img-1"
