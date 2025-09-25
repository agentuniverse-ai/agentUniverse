# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/4/22 14:45
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: prompt_configer.py
from pathlib import Path
from typing import Optional

from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer


class PromptConfiger(ComponentConfiger):
    """The PromptConfiger class, which is used to load and manage the Prompt configuration."""

    def __init__(self, configer: Optional[Configer] = None):
        """Initialize the PromptConfiger."""
        super().__init__(configer)
        self.__metadata_version: Optional[str] = None

    @property
    def metadata_version(self) -> Optional[str]:
        """Return prompt version of the Prompt."""
        return self.__metadata_version

    def load(self) -> "PromptConfiger":
        """Load the configuration by the Configer object.
        Returns:
            PromptConfiger: the PromptConfiger object
        """
        return self.load_by_configer(self.__configer)

    def load_by_configer(self, configer: Configer) -> "PromptConfiger":
        """Load the configuration by the Configer object.
        Args:
            configer(Configer): the Configer object
        Returns:
            PromptConfiger: the PromptConfiger object
        """
        super().load_by_configer(configer)
        try:
            if configer.value.get("metadata"):
                self.__metadata_version = configer.value.get("metadata").get("version")
            else:
                path = Path(configer.path)
                self.__metadata_version = f"{path.parent.name}.{path.stem}"
            # set the prompt default module and class
            if self.meta_class is None:
                if self.metadata_module is None:
                    self.metadata_module = "agentuniverse.prompt.prompt"
                if self.metadata_class is None:
                    self.metadata_class = "Prompt"
        except Exception as e:
            raise Exception(f"Failed to parse the Prompt configuration: {e}")
        return self
