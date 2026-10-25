"""Resolve dotted config paths without masking the resolver's own failures.

``parse_dynamic_str`` is documented as a way to keep a secret out of a YAML
file: the value is a dotted path and the real value comes from calling that
function. Only an unresolvable path may fall back to the original string -- a
resolver that raises must surface its error, otherwise the configured value
silently becomes the dotted path itself.
"""

import sys
import uuid

import pytest

from agentuniverse.base.config.component_configer.configers.sqldb_wrapper_config import (
    SQLDBWrapperConfiger,
)
from agentuniverse.base.config.configer import Configer
from agentuniverse.base.util.system_util import parse_dynamic_str


@pytest.fixture()
def module_factory(tmp_path, monkeypatch):
    """Create a throwaway importable module and drop it from sys.modules after."""
    created = []

    def _create(body: str) -> str:
        name = f"au_dynamic_resolver_{uuid.uuid4().hex}"
        (tmp_path / f"{name}.py").write_text(body, encoding="utf-8")
        monkeypatch.syspath_prepend(str(tmp_path))
        created.append(name)
        return name

    yield _create

    for name in created:
        sys.modules.pop(name, None)


def test_resolver_exception_is_propagated(module_factory):
    """A failing resolver must not degrade into the literal dotted path."""
    name = module_factory("def get_db_uri():\n    raise RuntimeError('DSN env var missing')\n")

    with pytest.raises(RuntimeError, match="DSN env var missing"):
        parse_dynamic_str(f"{name}.get_db_uri")


def test_resolved_value_is_returned(module_factory):
    name = module_factory("def get_db_uri():\n    return 'postgresql://app@db:5432/app'\n")

    assert parse_dynamic_str(f"{name}.get_db_uri") == "postgresql://app@db:5432/app"


def test_resolver_requiring_arguments_is_not_silently_accepted(module_factory):
    """A callable that cannot be called without arguments is a config error."""
    name = module_factory("def get_db_uri(host):\n    return f'postgresql://{host}/app'\n")

    with pytest.raises(TypeError):
        parse_dynamic_str(f"{name}.get_db_uri")


def test_unimportable_module_keeps_the_literal():
    assert parse_dynamic_str("au_no_such_module_for_this_test.fn") == (
        "au_no_such_module_for_this_test.fn"
    )


def test_missing_attribute_keeps_the_literal(module_factory):
    name = module_factory("def get_db_uri():\n    return 'x'\n")

    assert parse_dynamic_str(f"{name}.missing") == f"{name}.missing"


def test_non_callable_attribute_keeps_the_literal(module_factory):
    name = module_factory("NOT_CALLABLE = 'plain string'\n")

    assert parse_dynamic_str(f"{name}.NOT_CALLABLE") == f"{name}.NOT_CALLABLE"


def test_value_without_dot_keeps_the_literal():
    assert parse_dynamic_str("sqlite:///local.db") == "sqlite:///local.db"


def test_non_string_value_is_returned_unchanged():
    assert parse_dynamic_str(None) is None


def test_sql_db_config_surfaces_the_resolver_failure(module_factory, tmp_path):
    """The end-to-end path: the resolver error must not become db_uri."""
    name = module_factory("def get_db_uri():\n    raise RuntimeError('DSN env var missing')\n")
    yaml_path = tmp_path / "db.yaml"
    yaml_path.write_text(
        "name: 'demo_db'\n"
        "description: 'db used by the demo app'\n"
        f"db_uri: '{name}.get_db_uri'\n"
        "engine_args: {}\n"
        "sql_database_args: {}\n",
        encoding="utf-8",
    )

    with pytest.raises(Exception, match="DSN env var missing") as excinfo:
        SQLDBWrapperConfiger().load_by_configer(Configer(str(yaml_path)).load())

    # The literal path must never be handed to the caller as a resolved DSN.
    assert "Could not parse SQLAlchemy URL" not in str(excinfo.value)
