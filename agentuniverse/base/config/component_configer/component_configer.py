# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/12 23:16
# @Author  : jerry.zzw 
# @Email   : jerry.zzw@antgroup.com
# @FileName: component_configer.py

# @Time    : 2025/1/27 10:30
# @Author  : Auto
# @Email   : auto@example.com
# @Note    : 优化错误信息处理，添加详细的错误描述和解决建议

import importlib
from typing import Optional

from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.configer import Configer
from agentuniverse.base.config.custom_configer.default_llm_configer import DefaultLLMConfiger
from agentuniverse.base.exception import ConfigValidationError


class ComponentConfiger(object):
    """The ComponentConfiger class, which is used to load and manage the component configuration."""

    def __init__(self, configer: Optional[Configer] = None):
        """Initialize the ComponentConfiger."""
        self.__configer: Optional[Configer] = configer
        self.__metadata_type: Optional[str] = None
        self.__metadata_module: Optional[str] = None
        self.__metadata_class: Optional[str] = None
        self.__meta_class: Optional[str] = None
        self.__yaml_func_instance = None
        self.__default_llm_configer: DefaultLLMConfiger = None

    @property
    def configer(self) -> Optional[Configer]:
        """Return the Configer object."""
        return self.__configer

    @property
    def metadata_type(self) -> Optional[str]:
        """Return the type of the component."""
        return self.__metadata_type

    @property
    def metadata_module(self) -> Optional[str]:
        """Return the module of the component."""
        return self.__metadata_module

    @metadata_module.setter
    def metadata_module(self, metadata_module: str):
        self.__metadata_module = metadata_module

    @property
    def metadata_class(self) -> Optional[str]:
        """Return the class of the component."""
        return self.__metadata_class

    @metadata_class.setter
    def metadata_class(self, metadata_class: str):
        self.__metadata_class = metadata_class

    @property
    def yaml_func_instance(self):
        return self.__yaml_func_instance

    @yaml_func_instance.setter
    def yaml_func_instance(self, value):
        self.__yaml_func_instance = value

    @property
    def default_llm_configer(self) -> DefaultLLMConfiger:
        return self.__default_llm_configer

    @default_llm_configer.setter
    def default_llm_configer(self, value: DefaultLLMConfiger):
        self.__default_llm_configer = value

    @property
    def meta_class(self) -> str:
        return self.__meta_class

    def load(self) -> 'ComponentConfiger':
        """Load the configuration by the Configer object.
        Returns:
            ComponentConfiger: the ComponentConfiger object
        """
        return self.load_by_configer(self.configer)

    def load_by_configer(self, configer: Configer) -> 'ComponentConfiger':
        """Load the configuration by the Configer object.
        Args:
            configer(Configer): the Configer object
        Returns:
            ComponentConfiger: the ComponentConfiger object
        """
        self.__configer = configer

        try:
            for k, v in configer.value.items():
                self.__dict__[k] = v
            if configer.value.get('metadata'):
                self.__metadata_type = configer.value.get('metadata').get('type')
                self.__metadata_module = configer.value.get('metadata').get('module')
                self.__metadata_class = configer.value.get('metadata').get('class')
            elif configer.path and 'prompt' in configer.path:
                self.__metadata_type = ComponentEnum.PROMPT.value
            self.__meta_class = configer.value.get('meta_class')
        except Exception as e:
            validation_errors = [
                f"配置解析失败: {str(e)}",
                "检查配置文件格式是否正确",
                "验证必需的配置字段是否存在"
            ]
            
            raise ConfigValidationError(
                file_path=configer.path or "unknown",
                validation_errors=validation_errors,
                details={
                    "config_keys": list(configer.value.keys()) if configer.value else [],
                    "metadata": configer.value.get('metadata') if configer.value else None
                },
                original_exception=e
            )

        return self

    def get_component_config_type(self) -> Optional[str]:
        """Return the type of the component.

        Returns:
            Optional[str]: the type of the component
        """
        if self.__meta_class:
            metadata_module = '.'.join(self.__meta_class.split('.')[:-1])
            metadata_class = self.__meta_class.split('.')[-1]
            module = importlib.import_module(metadata_module)
            clz = getattr(module, metadata_class)
            return clz().component_type.value
        else:
            return self.__metadata_type
