from unittest.mock import MagicMock, patch

import pytest

from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse_product.base.product import Product
from agentuniverse_product.service.admin_service.resource_service import AdminResourceService


def test_get_dashboard_summary():
    summary = AdminResourceService.get_dashboard_summary()
    assert summary.system_health == "OK"
    assert isinstance(summary.total_agents, int)
    assert isinstance(summary.total_tools, int)
    assert isinstance(summary.total_knowledge, int)
    assert isinstance(summary.total_workflows, int)


def test_get_resource_lists():
    agents = AdminResourceService.get_all_agents()
    tools = AdminResourceService.get_all_tools()
    knowledges = AdminResourceService.get_all_knowledge()
    workflows = AdminResourceService.get_all_workflows()

    assert isinstance(agents.total, int)
    assert isinstance(tools.total, int)
    assert isinstance(knowledges.total, int)
    assert isinstance(workflows.total, int)
    assert isinstance(agents.data, list)
    assert isinstance(tools.data, list)
    assert isinstance(knowledges.data, list)
    assert isinstance(workflows.data, list)


@pytest.mark.parametrize("agent_id", ["unknown-agent-id"])
def test_get_agent_sessions(agent_id):
    sessions = AdminResourceService.get_agent_sessions(agent_id)
    assert isinstance(sessions.total, int)
    assert isinstance(sessions.data, list)


@patch("agentuniverse_product.service.admin_service.resource_service.ProductManager")
def test_get_all_agents_mocked(mock_product_manager):
    p1 = Product()
    p1.id = "agent_001"
    p1.nickname = "Test Agent 1"
    p1.description = "desc1"
    p1.type = ComponentEnum.AGENT.value

    p2 = Product()
    p2.id = "agent_002"
    p2.nickname = "Test Agent 2"
    p2.description = "desc2"
    p2.type = ComponentEnum.AGENT.value

    # noise: other product types should be filtered out
    p3 = Product()
    p3.id = "tool_001"
    p3.nickname = "Tool"
    p3.type = ComponentEnum.TOOL.value

    instance_mock = MagicMock()
    instance_mock.get_instance_obj_list.return_value = [p1, p2, p3]
    mock_product_manager.return_value = instance_mock

    resp = AdminResourceService.get_all_agents()
    assert resp.total == 2
    assert len(resp.data) == 2
    assert {item.id for item in resp.data} == {"agent_001", "agent_002"}
    assert all(item.component_type == ComponentEnum.AGENT.value for item in resp.data)
