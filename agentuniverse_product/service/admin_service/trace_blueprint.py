# !/usr/bin/env python3
# -*- coding:utf-8 -*-

from flask import Blueprint

from agentuniverse.agent_serve.web.web_util import make_standard_response
from agentuniverse_product.service.admin_service.trace_service import AdminTraceService

admin_trace_bp = Blueprint("admin_trace", __name__, url_prefix="/api/v1/admin/trace")


@admin_trace_bp.route("/sessions/<string:session_id>", methods=["GET"])
def get_session_trace(session_id: str):
    return make_standard_response(
        success=True,
        result=AdminTraceService.get_session_trace(session_id).model_dump(),
    )
