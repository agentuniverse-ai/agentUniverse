# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_knowledge_dto.py

"""Unit tests for the KnowledgeDTO."""

from agentuniverse_product.service.model.knowledge_dto import KnowledgeDTO


class TestKnowledgeDTO:
    """Test KnowledgeDTO model defaults and construction."""

    def test_defaults(self):
        dto = KnowledgeDTO()
        assert dto.id == ""
        assert dto.nickname == ""
        assert dto.description == ""
        assert dto.avatar == ""

    def test_full_construction(self):
        dto = KnowledgeDTO(id="k1", nickname="kb", description="docs",
                           avatar="a.png")
        assert dto.id == "k1"
        assert dto.nickname == "kb"
        assert dto.description == "docs"
        assert dto.avatar == "a.png"

    def test_optional_fields_accept_none(self):
        dto = KnowledgeDTO(id="k1", nickname=None)
        assert dto.nickname is None

    def test_equality(self):
        assert KnowledgeDTO(id="k1") == KnowledgeDTO(id="k1")
        assert KnowledgeDTO(id="k1") != KnowledgeDTO(id="k2")
