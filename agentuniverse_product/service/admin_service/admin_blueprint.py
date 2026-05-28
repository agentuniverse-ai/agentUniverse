# !/usr/bin/env python3
# -*- coding:utf-8 -*-

from flask import Blueprint, request

from agentuniverse.agent_serve.web.web_util import make_standard_response
from agentuniverse_product.service.admin_service.resource_service import AdminResourceService

admin_bp = Blueprint("admin_resources", __name__, url_prefix="/api/v1/admin/resources")


def _get_pagination_params():
    try:
        page = int(request.args.get("page", "1"))
        page_size = int(request.args.get("page_size", "20"))
    except ValueError:
        return None, None, "page and page_size must be integers."

    if page < 1:
        return None, None, "page must be greater than or equal to 1."
    if page_size < 1 or page_size > 100:
        return None, None, "page_size must be between 1 and 100."
    return page, page_size, None


def _resource_list_response(loader):
    page, page_size, error = _get_pagination_params()
    if error:
        return make_standard_response(success=False, message=error, status_code=400)
    return make_standard_response(
        success=True,
        result=loader(page=page, page_size=page_size).model_dump(),
    )


@admin_bp.route("/summary", methods=["GET"])
def get_summary():
    return make_standard_response(
        success=True,
        result=AdminResourceService.get_dashboard_summary().model_dump(),
    )


@admin_bp.route("/agents", methods=["GET"])
def get_agents():
    return _resource_list_response(AdminResourceService.get_all_agents)


@admin_bp.route("/tools", methods=["GET"])
def get_tools():
    return _resource_list_response(AdminResourceService.get_all_tools)


@admin_bp.route("/knowledge", methods=["GET"])
def get_knowledge():
    return _resource_list_response(AdminResourceService.get_all_knowledge)


@admin_bp.route("/workflows", methods=["GET"])
def get_workflows():
    return _resource_list_response(AdminResourceService.get_all_workflows)


@admin_bp.route("/llms", methods=["GET"])
def get_llms():
    return _resource_list_response(AdminResourceService.get_all_llms)


@admin_bp.route("/memories", methods=["GET"])
def get_memories():
    return _resource_list_response(AdminResourceService.get_all_memories)


@admin_bp.route("/sessions/<string:agent_id>", methods=["GET"])
def get_sessions(agent_id: str):
    return make_standard_response(
        success=True,
        result=AdminResourceService.get_agent_sessions(agent_id).model_dump(),
    )
