# !/usr/bin/env python3
# -*- coding:utf-8 -*-

from flask import Blueprint

from agentuniverse.agent_serve.web.web_util import make_standard_response
from agentuniverse_product.service.admin_service.optimization_service import AdminOptimizationService

admin_optimization_bp = Blueprint(
    "admin_optimization",
    __name__,
    url_prefix="/api/v1/admin/optimization",
)


@admin_optimization_bp.route("/sessions/<string:session_id>", methods=["GET"])
def get_session_optimization(session_id: str):
    return make_standard_response(
        success=True,
        result=AdminOptimizationService.analyze_session(session_id).model_dump(),
    )
