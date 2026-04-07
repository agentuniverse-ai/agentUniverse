# !/usr/bin/env python3
# -*- coding:utf-8 -*-

from flask import Blueprint

from agentuniverse.agent_serve.web.web_util import make_standard_response
from agentuniverse_product.service.admin_service.resource_service import AdminResourceService

admin_bp = Blueprint("admin_resources", __name__, url_prefix="/api/v1/admin/resources")


@admin_bp.route("/summary", methods=["GET"])
def get_summary():
    return make_standard_response(
        success=True,
        result=AdminResourceService.get_dashboard_summary().model_dump(),
    )


@admin_bp.route("/agents", methods=["GET"])
def get_agents():
    return make_standard_response(
        success=True,
        result=AdminResourceService.get_all_agents().model_dump(),
    )


@admin_bp.route("/tools", methods=["GET"])
def get_tools():
    return make_standard_response(
        success=True,
        result=AdminResourceService.get_all_tools().model_dump(),
    )


@admin_bp.route("/knowledge", methods=["GET"])
def get_knowledge():
    return make_standard_response(
        success=True,
        result=AdminResourceService.get_all_knowledge().model_dump(),
    )


@admin_bp.route("/workflows", methods=["GET"])
def get_workflows():
    return make_standard_response(
        success=True,
        result=AdminResourceService.get_all_workflows().model_dump(),
    )


@admin_bp.route("/sessions/<string:agent_id>", methods=["GET"])
def get_sessions(agent_id: str):
    return make_standard_response(
        success=True,
        result=AdminResourceService.get_agent_sessions(agent_id).model_dump(),
    )

