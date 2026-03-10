# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/2/27
# @FileName: skill_manager.py

from agentuniverse.agent.action.skill.skill import Skill
from agentuniverse.base.annotation.singleton import singleton
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.component.component_manager_base import ComponentManagerBase
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager


@singleton
class SkillManager(ComponentManagerBase):
    """Singleton manager for Skill components."""

    def __init__(self):
        super().__init__(ComponentEnum.SKILL)

    def get_instance_obj(self, component_instance_name: str,
                         appname: str = None, new_instance: bool = True) -> Skill:
        """Return the Skill instance by name, with lazy-loading from configer map."""
        appname = appname or ApplicationConfigManager().app_configer.base_info_appname
        instance_code = f'{appname}.skill.{component_instance_name}'
        instance_obj = self._instance_obj_map.get(instance_code)

        if instance_obj is None:
            skill_configer_map = ApplicationConfigManager().app_configer.skill_configer_map
            if skill_configer_map and component_instance_name in skill_configer_map:
                configer = skill_configer_map[component_instance_name]
                instance_obj = Skill().initialize_by_component_configer(configer)
                if instance_obj:
                    self.register(instance_obj.get_instance_code(), instance_obj)

        if instance_obj and new_instance:
            return instance_obj.create_copy()
        return instance_obj
