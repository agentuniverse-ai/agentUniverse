from types import SimpleNamespace

import pytest

from agentuniverse.agent.context.compressor.context_compressor_manager import (
    ContextCompressorManager,
)
from agentuniverse.agent.context.context_manager_manager import ContextManagerManager
from agentuniverse.agent.context.context_store_manager import ContextStoreManager
from agentuniverse.agent.context.router.context_router_manager import ContextRouterManager
from agentuniverse.base.agentuniverse import AgentUniverse
from agentuniverse.base.component.component_configer_util import ComponentConfigerUtil
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer

CONTEXT_COMPONENTS = (
    ComponentEnum.CONTEXT_STORE,
    ComponentEnum.CONTEXT_COMPRESSOR,
    ComponentEnum.CONTEXT_ROUTER,
    ComponentEnum.CONTEXT_MANAGER,
)

CONTEXT_MANAGERS = {
    ComponentEnum.CONTEXT_STORE: ContextStoreManager,
    ComponentEnum.CONTEXT_COMPRESSOR: ContextCompressorManager,
    ComponentEnum.CONTEXT_ROUTER: ContextRouterManager,
    ComponentEnum.CONTEXT_MANAGER: ContextManagerManager,
}


def test_app_configer_loads_context_component_packages():
    configer = Configer()
    configer.value = {
        "CORE_PACKAGE": {
            "context_manager": ["app.context.manager"],
            "context_store": ["app.context.store"],
            "context_compressor": ["app.context.compressor"],
            "context_router": ["app.context.router"],
        }
    }

    app_configer = AppConfiger().load_by_configer(configer)

    assert app_configer.core_context_manager_package_list == ["app.context.manager"]
    assert app_configer.core_context_store_package_list == ["app.context.store"]
    assert app_configer.core_context_compressor_package_list == ["app.context.compressor"]
    assert app_configer.core_context_router_package_list == ["app.context.router"]


@pytest.mark.parametrize("component_type", CONTEXT_COMPONENTS)
def test_context_components_use_the_generic_component_configer(component_type):
    assert ComponentConfigerUtil.get_component_config_clz_by_type(component_type) is ComponentConfiger


@pytest.mark.parametrize("component_type", CONTEXT_COMPONENTS)
def test_context_components_have_component_managers(component_type):
    assert ComponentConfigerUtil.get_component_manager_clz_by_type(component_type) is CONTEXT_MANAGERS[component_type]


def test_startup_scans_and_registers_context_components(monkeypatch):
    context_packages = {
        ComponentEnum.CONTEXT_STORE: ["app.context.store"],
        ComponentEnum.CONTEXT_COMPRESSOR: ["app.context.compressor"],
        ComponentEnum.CONTEXT_ROUTER: ["app.context.router"],
        ComponentEnum.CONTEXT_MANAGER: ["app.context.manager"],
    }
    app_configer_values = {
        "core_default_package_list": [],
        "core_context_store_package_list": context_packages[ComponentEnum.CONTEXT_STORE],
        "core_context_compressor_package_list": context_packages[ComponentEnum.CONTEXT_COMPRESSOR],
        "core_context_router_package_list": context_packages[ComponentEnum.CONTEXT_ROUTER],
        "core_context_manager_package_list": context_packages[ComponentEnum.CONTEXT_MANAGER],
    }
    for component_type in ComponentEnum:
        app_configer_values.setdefault(f"core_{component_type.value.lower()}_package_list", [])
    app_configer = SimpleNamespace(**app_configer_values)
    agent_universe = AgentUniverse()
    scanned = []
    registered = []

    def record_scan(package_list, _config_type, component_type):
        scanned.append((component_type, package_list))
        return [component_type]

    monkeypatch.setattr(agent_universe, "scan", record_scan)
    monkeypatch.setattr(
        agent_universe,
        "_AgentUniverse__register",
        lambda component_type, configers: registered.append((component_type, configers)),
    )

    agent_universe._AgentUniverse__scan_and_register(app_configer)

    assert [
        component_type for component_type, _package_list in scanned if component_type in CONTEXT_COMPONENTS
    ] == list(CONTEXT_COMPONENTS)
    for component_type, package_list in context_packages.items():
        assert (component_type, package_list) in scanned
        assert (component_type, [component_type]) in registered
