from flask import Flask

from agentuniverse_product.service.admin_service.admin_auth_service import AdminAuthService


def test_auth_disabled_grants_super_admin(monkeypatch):
    monkeypatch.setenv("ADMIN_AUTH_ENABLED", "0")
    app = Flask(__name__)
    with app.test_request_context("/"):
        context = AdminAuthService.authenticate()

    assert context is not None
    assert context.role == "super_admin"
    assert context.auth_enabled is False


def test_auth_enabled_requires_bearer_token(monkeypatch):
    monkeypatch.setenv("ADMIN_AUTH_ENABLED", "1")
    monkeypatch.setenv("ADMIN_API_TOKENS", "secret-token:admin")
    app = Flask(__name__)
    with app.test_request_context("/"):
        assert AdminAuthService.authenticate() is None


def test_auth_enabled_accepts_valid_token(monkeypatch):
    monkeypatch.setenv("ADMIN_AUTH_ENABLED", "1")
    monkeypatch.setenv("ADMIN_API_TOKENS", "secret-token:admin,read-only:viewer")
    app = Flask(__name__)
    with app.test_request_context("/", headers={"Authorization": "Bearer secret-token"}):
        context = AdminAuthService.authenticate()

    assert context is not None
    assert context.role == "admin"
    assert context.auth_enabled is True


def test_role_allows_hierarchy():
    assert AdminAuthService.role_allows("admin", "viewer")
    assert AdminAuthService.role_allows("viewer", "viewer")
    assert not AdminAuthService.role_allows("viewer", "admin")


def test_write_methods_require_admin_role():
    assert AdminAuthService.required_role_for_request("POST") == "admin"
    assert AdminAuthService.required_role_for_request("GET") == "viewer"
