from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.configer import Configer


def test_nullable_core_package_section_is_treated_as_empty():
    configer = Configer()
    configer.value = {"CORE_PACKAGE": None}

    loaded = AppConfiger().load_by_configer(configer)

    assert loaded.core_agent_package_list is None
