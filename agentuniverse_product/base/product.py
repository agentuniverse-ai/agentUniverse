# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/24 16:29
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: product.py
from typing import Optional
import os

from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_configer_util import ComponentConfigerUtil
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse_product.base.product_configer import ProductConfiger


class Product(ComponentBase):
    """The basic class of the product."""

    component_type: ComponentEnum = ComponentEnum.PRODUCT
    id: Optional[str] = None
    nickname: Optional[str] = None
    type: Optional[str] = None
    avatar: Optional[str] = None
    description: Optional[str] = None
    _instance: Optional[ComponentBase] = None

    @property
    def instance(self) -> ComponentBase:
        """Return the concrete component instance bound to this product."""
        return self._instance

    def get_ctime(self) -> float:
        """Return the product creation time."""
        return os.path.getctime(self.component_config_path)

    def get_mtime(self) -> float:
        """Return the product last modification time."""
        return os.path.getmtime(self.component_config_path)

    def get_instance_code(self) -> str:
        """Return the full name of the product."""
        appname = ApplicationConfigManager().app_configer.base_info_appname
        return f"{appname}.product.{self.id}"

    def initialize_by_component_configer(self,
                                         product_configer: ProductConfiger) -> 'Product':
        """Initialize the Product by the ProductConfiger object.

        Args:
            product_configer(ProductConfiger): A configer contains product basic info.
        Returns:
            Product: A Product instance.
        """
        if product_configer.nickname:
            self.nickname = product_configer.nickname
        if product_configer.id:
            self.id = product_configer.id
        if product_configer.type:
            self.type = product_configer.type
        if product_configer.avatar:
            self.avatar = product_configer.avatar
        if product_configer.description:
            self.description = product_configer.description
        self.init_instance()
        return self

    def init_instance(self):
        """Initialize the specific component instance corresponding to the product."""
        component_manager_clz = ComponentConfigerUtil.get_component_manager_clz_by_type(
            ComponentEnum.from_value(self.type))
        self._instance = component_manager_clz().get_instance_obj(self.id)
        if self._instance is None:
            raise ValueError(f"The aU instance corresponding to the product id does not exist,"
                             f" please check the product type and id parameters, product id is: {self.id}")
