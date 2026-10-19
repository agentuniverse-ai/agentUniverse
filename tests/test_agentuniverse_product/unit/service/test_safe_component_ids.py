"""Product creation must reject IDs used as unsafe configuration paths."""

import pytest

from agentuniverse_product.service.agent_service.agent_service import AgentService
from agentuniverse_product.service.knowledge_service.knowledge_service import KnowledgeService
from agentuniverse_product.service.model.agent_dto import AgentDTO
from agentuniverse_product.service.model.knowledge_dto import KnowledgeDTO
from agentuniverse_product.service.model.plugin_dto import PluginDTO
from agentuniverse_product.service.model.tool_dto import ToolDTO
from agentuniverse_product.service.plugin_service.plugin_service import PluginService
from agentuniverse_product.service.tool_service.tool_service import ToolService
from agentuniverse_product.service.util.id_util import validate_component_id


@pytest.mark.parametrize("component_id", ["../outside", "..\\outside", "", ".", "a:b", "a\nb"])
def test_invalid_ids_are_rejected_before_product_creation(component_id):
    creators = [
        lambda: ToolService.create_tool(ToolDTO(id=component_id)),
        lambda: PluginService.create_plugin_with_openapi(PluginDTO(id=component_id)),
        lambda: AgentService.create_agent(AgentDTO(id=component_id)),
        lambda: KnowledgeService.create_knowledge(KnowledgeDTO(id=component_id)),
    ]
    for create in creators:
        with pytest.raises(ValueError, match="id must contain"):
            create()


@pytest.mark.parametrize("component_id", ["agent_1", "plugin-two", "A9"])
def test_valid_ids_keep_existing_product_naming(component_id):
    validate_component_id(component_id, "Tool")


@pytest.mark.parametrize("component_id", ["CON", "nul", "Com1", "LPT9"])
def test_windows_device_names_are_rejected(component_id):
    with pytest.raises(ValueError, match="reserved Windows filename"):
        validate_component_id(component_id, "Tool")


@pytest.mark.parametrize("component_id", ["console", "com0", "lpt10"])
def test_similar_nonreserved_ids_remain_valid(component_id):
    validate_component_id(component_id, "Tool")
