# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_planner_dto.py

"""Unit tests for the PlannerDTO."""

import pytest

from agentuniverse_product.service.model.planner_dto import PlannerDTO


class TestPlannerDTO:
    """Test PlannerDTO model defaults and construction."""

    def test_defaults(self):
        dto = PlannerDTO(id="p1")
        assert dto.nickname == ""
        assert dto.members == []
        assert dto.workflow_id is None

    def test_full_construction(self):
        dto = PlannerDTO(id="p1", nickname="planner", members=["m1", "m2"],
                         workflow_id="wf1")
        assert dto.nickname == "planner"
        assert dto.members == ["m1", "m2"]
        assert dto.workflow_id == "wf1"

    def test_id_is_required(self):
        with pytest.raises(Exception):
            PlannerDTO()
