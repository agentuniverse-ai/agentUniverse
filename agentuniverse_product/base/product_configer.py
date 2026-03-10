# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/24 16:35
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: product_configer.py
from typing import Optional

from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer

PRODUCT_COMPONENT_TYPE = ['AGENT', 'KNOWLEDGE', 'TOOL', 'LLM', 'PLUGIN']


class ProductConfiger(ComponentConfiger):
    """The ProductConfiger class, used to load and manage the product configuration."""

    _ComponentConfiger__metadata_class: Optional[str] = None
    _ComponentConfiger__metadata_module: Optional[str] = None

    def __init__(self, configer: Optional[Configer] = None):
        """Initialize the ProductConfiger."""
        super().__init__(configer)
        self.__nickname: Optional[str] = None
        self.__id: Optional[str] = None
        self.__type: Optional[str] = None
        self.__avatar: Optional[str] = None
        self.__description: Optional[str] = None
        self.__set_default_meta_info()

    @property
    def nickname(self) -> Optional[str]:
        """Nickname field."""
        return self.__nickname

    @property
    def id(self) -> Optional[str]:
        """ID field."""
        return self.__id

    @property
    def type(self) -> Optional[str]:
        """Type field."""
        return self.__type

    @property
    def avatar(self) -> Optional[str]:
        """Avatar field."""
        return self.__avatar
    
    @property
    def description(self) -> Optional[str]:
        """Description field."""
        return self.__description

    def __set_default_meta_info(self):
        """Set default instantiated class of product."""
        if (not hasattr(self, '_ComponentConfiger__metadata_module')
                or self._ComponentConfiger__metadata_module is None):
            self._ComponentConfiger__metadata_module = ("agentuniverse_product."
                                                        "base.product")
        if (not hasattr(self, '_ComponentConfiger__metadata_class')
                or self._ComponentConfiger__metadata_class is None):
            self._ComponentConfiger__metadata_class = 'Product'

    def load(self) -> 'ProductConfiger':
        """Setting property using own configer member property.

        Returns:
            ProductConfiger: A ProductConfiger instance.
        """
        return self.load_by_configer(self.configer)

    def load_by_configer(self, configer: Configer) -> 'ProductConfiger':
        """Load the configuration by the Configer object.
        Args:
            configer(Configer): the Configer object
        Returns:
            ProductConfiger: the ProductConfiger object
        """
        super().load_by_configer(configer)
        self.__set_default_meta_info()
        try:
            self.__nickname = configer.value.get('nickname')
            if self.__nickname is None:
                raise ValueError(f"Product nickname is required parameter.")
            self.__id = configer.value.get('id')
            if self.__id is None:
                raise ValueError(f"Product id is required parameter.")
            self.__type = configer.value.get('type')
            self.__avatar = configer.value.get('avatar')
            self.__description = configer.value.get('description')
            if self.__type not in PRODUCT_COMPONENT_TYPE:
                raise ValueError(f"Invalid product type: {self.__type}")
        except Exception as e:
            raise Exception(f"Failed to parse the Product configuration: {e}")
        return self
