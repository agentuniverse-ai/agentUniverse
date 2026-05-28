# !/usr/bin/env python3
# -*- coding:utf-8 -*-

from flask import Blueprint

from agentuniverse.agent_serve.web.web_util import make_standard_response
from agentuniverse_product.service.admin_service.guardrail_service import AdminGuardrailService

admin_guardrail_bp = Blueprint("admin_guardrail", __name__, url_prefix="/api/v1/admin/guardrail")


@admin_guardrail_bp.route("/sessions/<string:session_id>", methods=["GET"])
def get_session_guardrail(session_id: str):
    return make_standard_response(
        success=True,
        result=AdminGuardrailService.get_session_diagnostics(session_id).model_dump(),
    )
