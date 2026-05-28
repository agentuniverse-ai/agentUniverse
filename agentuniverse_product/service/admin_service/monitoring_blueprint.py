# !/usr/bin/env python3
# -*- coding:utf-8 -*-

from flask import Blueprint, request

from agentuniverse.agent_serve.web.web_util import make_standard_response
from agentuniverse_product.service.admin_service.monitoring_service import AdminMonitoringService

admin_monitoring_bp = Blueprint("admin_monitoring", __name__, url_prefix="/api/v1/admin/metrics")


@admin_monitoring_bp.route("/llm", methods=["GET"])
def get_llm_metrics():
    return make_standard_response(
        success=True,
        result=AdminMonitoringService.get_llm_metrics(
            start=request.args.get("start"),
            end=request.args.get("end"),
        ).model_dump(),
    )
