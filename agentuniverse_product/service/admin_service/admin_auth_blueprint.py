# !/usr/bin/env python3
# -*- coding:utf-8 -*-

from flask import Blueprint, g, request

from agentuniverse.agent_serve.web.web_util import make_standard_response
from agentuniverse_product.service.admin_service.admin_auth_service import AdminAuthService

admin_auth_bp = Blueprint("admin_auth", __name__, url_prefix="/api/v1/admin/auth")


def init_admin_api_auth(app, blueprints: tuple[Blueprint, ...]) -> None:
    """Register auth guard on all admin blueprints."""

    def _guard():
        context = AdminAuthService.authenticate()
        if context is None:
            return make_standard_response(
                success=False,
                result=None,
                message="Unauthorized",
                status_code=401,
            )

        min_role = AdminAuthService.required_role_for_request(request.method)
        if not AdminAuthService.role_allows(context.role, min_role):
            return make_standard_response(
                success=False,
                result=None,
                message="Forbidden",
                status_code=403,
            )

        g.admin_auth = context
        return None

    for blueprint in blueprints:
        blueprint.before_request(_guard)


@admin_auth_bp.route("/me", methods=["GET"])
def auth_me():
    context = getattr(g, "admin_auth", None)
    if context is None:
        return make_standard_response(
            success=False,
            result=None,
            message="Unauthorized",
            status_code=401,
        )

    return make_standard_response(
        success=True,
        result={
            "role": context.role,
            "auth_enabled": context.auth_enabled,
        },
    )
