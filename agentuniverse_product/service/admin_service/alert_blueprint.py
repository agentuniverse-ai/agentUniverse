# !/usr/bin/env python3
# -*- coding:utf-8 -*-

from flask import Blueprint

from agentuniverse.agent_serve.web.web_util import make_standard_response
from agentuniverse_product.service.admin_service.alert_service import AdminAlertService

admin_alert_bp = Blueprint("admin_alerts", __name__, url_prefix="/api/v1/admin/alerts")


@admin_alert_bp.route("", methods=["GET"])
def get_alerts():
    return make_standard_response(
        success=True,
        result=AdminAlertService.get_active_alerts().model_dump(),
    )
