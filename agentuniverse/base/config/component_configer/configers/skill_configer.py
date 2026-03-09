# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/2/27
# @FileName: skill_configer.py

from pathlib import Path
from typing import Optional, List

from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.util.logging.logging_util import LOGGER


class SkillConfiger(ComponentConfiger):
    """Parses SKILL.md files (YAML frontmatter + Markdown body).

    Unlike other configers that parse YAML files, SkillConfiger reads
    SKILL.md with ``---``-delimited YAML frontmatter and a Markdown
    instructions body.
    """

    def __init__(self, configer=None):
        super().__init__(configer)
        self.__name: Optional[str] = None
        self.__description: Optional[str] = None
        self.__instructions: Optional[str] = None
        self.__allowed_tools: Optional[List[str]] = None
        self.__allowed_toolkits: Optional[List[str]] = None
        self.__context: str = "inline"
        self.__sub_agent: Optional[str] = None
        self.__model: Optional[str] = None
        self.__max_iterations: int = 10
        self.__skill_path: str = ""
        self.__disable_model_invocation: bool = False
        self.__user_invocable: bool = True
        self.__version: Optional[str] = None
        self.__license: Optional[str] = None
        self.__compatibility: Optional[str] = None
        self.__metadata: Optional[dict] = None

    @classmethod
    def from_skill_md(cls, skill_md_path: str) -> 'SkillConfiger':
        """Parse a SKILL.md file into a SkillConfiger.

        Separates YAML frontmatter (between ``---`` delimiters) from
        the Markdown body.  Validates name vs directory name consistency.
        Supports allowed_tools in list or comma-separated string format.
        """
        content = Path(skill_md_path).read_text(encoding='utf-8')
        frontmatter, body = cls._parse_frontmatter(content)

        instance = cls()
        instance.__name = frontmatter.get('name')
        instance.__description = frontmatter.get('description')
        instance.__instructions = body.strip()

        # allowed_tools: support list and comma-separated string
        raw_tools = frontmatter.get('allowed_tools') or frontmatter.get('allowed-tools')
        if isinstance(raw_tools, str):
            instance.__allowed_tools = [t.strip() for t in raw_tools.split(',') if t.strip()]
        else:
            instance.__allowed_tools = raw_tools  # list or None

        # allowed_toolkits: support list and comma-separated string
        raw_toolkits = frontmatter.get('allowed_toolkits') or frontmatter.get('allowed-toolkits')
        if isinstance(raw_toolkits, str):
            instance.__allowed_toolkits = [t.strip() for t in raw_toolkits.split(',') if t.strip()]
        else:
            instance.__allowed_toolkits = raw_toolkits  # list or None

        instance.__context = frontmatter.get('context', 'inline')
        instance.__sub_agent = frontmatter.get('sub_agent') or frontmatter.get('sub-agent')
        instance.__model = frontmatter.get('model')
        instance.__max_iterations = frontmatter.get('max_iterations', 10)
        instance.__skill_path = str(Path(skill_md_path).parent)
        instance.__disable_model_invocation = frontmatter.get(
            'disable_model_invocation',
            frontmatter.get('disable-model-invocation', False)
        )
        instance.__user_invocable = frontmatter.get(
            'user_invocable',
            frontmatter.get('user-invocable', True)
        )
        instance.__version = frontmatter.get('version')
        instance.__license = frontmatter.get('license')
        instance.__compatibility = frontmatter.get('compatibility')
        instance.__metadata = frontmatter.get('metadata')

        # Validate name vs directory name consistency
        dir_name = Path(skill_md_path).parent.name
        if instance.__name and instance.__name != dir_name:
            LOGGER.warn(
                f"Skill name '{instance.__name}' does not match directory name "
                f"'{dir_name}' (file: {skill_md_path}). Consider keeping them consistent."
            )

        return instance

    @staticmethod
    def _parse_frontmatter(content: str) -> tuple:
        """Split '---\\nyaml\\n---\\nmarkdown' into (dict, str)."""
        import yaml
        if not content.startswith('---'):
            return {}, content
        parts = content.split('---', 2)
        # parts[0] is empty, parts[1] is YAML, parts[2] is Markdown
        if len(parts) < 3:
            return {}, content
        frontmatter = yaml.safe_load(parts[1]) or {}
        body = parts[2]
        return frontmatter, body

    # -- Properties --

    @property
    def name(self) -> Optional[str]:
        return self.__name

    @property
    def description(self) -> Optional[str]:
        return self.__description

    @property
    def instructions(self) -> Optional[str]:
        return self.__instructions

    @property
    def allowed_tools(self) -> Optional[List[str]]:
        return self.__allowed_tools

    @property
    def allowed_toolkits(self) -> Optional[List[str]]:
        return self.__allowed_toolkits

    @property
    def context(self) -> str:
        return self.__context

    @property
    def sub_agent(self) -> Optional[str]:
        return self.__sub_agent

    @property
    def model(self) -> Optional[str]:
        return self.__model

    @property
    def max_iterations(self) -> int:
        return self.__max_iterations

    @property
    def skill_path(self) -> str:
        return self.__skill_path

    @property
    def disable_model_invocation(self) -> bool:
        return self.__disable_model_invocation

    @property
    def user_invocable(self) -> bool:
        return self.__user_invocable

    @property
    def version(self) -> Optional[str]:
        return self.__version

    @property
    def license(self) -> Optional[str]:
        return self.__license

    @property
    def compatibility(self) -> Optional[str]:
        return self.__compatibility

    @property
    def metadata(self) -> Optional[dict]:
        return self.__metadata
