# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/2/27
# @FileName: skill.py

import re
from typing import Optional, List, Dict, Any

from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.application_config_manager import \
    ApplicationConfigManager


class Skill(ComponentBase):
    """A modular, reusable instruction + allowed-tools bundle.

    Skills are discovered by scanning directories for ``SKILL.md`` files.
    Each skill is a folder containing a ``SKILL.md`` (YAML frontmatter +
    Markdown instructions body) and optional ``scripts/``, ``references/``,
    ``assets/`` sub-directories.

    Attributes:
        name: Skill name (should match directory name).
        description: Functionality description used by LLM for semantic matching.
        instructions: Markdown body from SKILL.md.
        allowed_tools: Tool list (supports wildcard syntax, currently parse-only).
        context: "inline" (default) or "fork".
        sub_agent: Agent name for fork mode. When unset, uses the built-in
            SkillForkAgentTemplate. When set, resolves the named agent from
            AgentManager and delegates fork execution to it.
        model: Optional LLM override.
        max_iterations: Maximum tool-calling rounds.
        skill_path: Absolute path to the skill directory.
        disable_model_invocation: Whether to prevent LLM from auto-invoking.
        user_invocable: Whether visible in menus.
        version: Optional version string.
        license: Optional license string.
        compatibility: Optional platform compatibility note.
        metadata: Optional custom metadata dict.
    """

    component_type: ComponentEnum = ComponentEnum.SKILL

    name: str = ""
    description: Optional[str] = None
    instructions: str = ""
    allowed_tools: Optional[List[str]] = None
    context: str = "inline"
    sub_agent: Optional[str] = None
    model: Optional[str] = None
    max_iterations: int = 10
    skill_path: str = ""
    disable_model_invocation: bool = False
    user_invocable: bool = True
    version: Optional[str] = None
    license: Optional[str] = None
    compatibility: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def __init__(self, **kwargs):
        super().__init__(component_type=ComponentEnum.SKILL, **kwargs)

    def initialize_by_component_configer(self, component_configer) -> 'Skill':
        """Initialize the Skill from a SkillConfiger instance.

        Args:
            component_configer: A SkillConfiger parsed from SKILL.md.

        Returns:
            The initialized Skill instance.
        """
        self.name = component_configer.name or ""
        self.description = component_configer.description
        self.instructions = component_configer.instructions or ""
        self.allowed_tools = component_configer.allowed_tools
        self.context = component_configer.context or "inline"
        self.sub_agent = component_configer.sub_agent
        self.model = component_configer.model
        self.max_iterations = component_configer.max_iterations or 10
        self.skill_path = component_configer.skill_path or ""
        self.disable_model_invocation = component_configer.disable_model_invocation or False
        self.user_invocable = component_configer.user_invocable if component_configer.user_invocable is not None else True
        self.version = component_configer.version
        self.license = component_configer.license
        self.compatibility = component_configer.compatibility
        self.metadata = component_configer.metadata
        return self

    def get_instance_code(self) -> str:
        appname = ApplicationConfigManager().app_configer.base_info_appname
        return f"{appname}.skill.{self.name}"

    def create_copy(self) -> 'Skill':
        return self.model_copy(deep=True)

    def get_tool_names(self) -> List[str]:
        """Extract pure tool names from allowed_tools (strip wildcard constraints).

        Example:
            ["bash_executor(cmd:git *)", "file_reader"] -> ["bash_executor", "file_reader"]

        The original wildcard specs are preserved in allowed_tools for future
        permission system use.
        """
        if not self.allowed_tools:
            return []
        names = []
        for spec in self.allowed_tools:
            match = re.match(r'^([\w-]+)', spec.strip())
            if match:
                names.append(match.group(1))
        return names
