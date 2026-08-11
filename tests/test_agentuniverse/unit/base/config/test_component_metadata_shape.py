from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer


def test_non_mapping_metadata_does_not_abort_component_loading():
    configer = Configer()
    configer.value = {"name": "example", "metadata": []}

    loaded = ComponentConfiger(configer).load()

    assert loaded.metadata_type is None
    assert loaded.configer is configer
