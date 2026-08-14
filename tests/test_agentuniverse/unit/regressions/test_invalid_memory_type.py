from types import SimpleNamespace

import pytest

from agentuniverse.agent.memory.memory import Memory


def test_invalid_memory_type_raises_descriptive_value_error():
    configer = SimpleNamespace(
        name="memory",
        description="memory",
        type="invalid",
    )

    with pytest.raises(ValueError, match="Unsupported memory type: invalid"):
        Memory().initialize_by_component_configer(configer)
