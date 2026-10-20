from agentuniverse.base.config.component_configer.configers.prompt_configer import PromptConfiger
from agentuniverse.base.config.configer import Configer


def test_prompt_config_without_metadata_or_path_keeps_version_unset():
    configer = Configer()
    configer.value = {"name": "example_prompt"}

    loaded = PromptConfiger(configer).load()

    assert loaded.metadata_version is None
