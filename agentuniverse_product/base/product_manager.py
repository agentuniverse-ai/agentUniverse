# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/24 16:34
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: product_manager.py
from agentuniverse.base.annotation.singleton import singleton
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.component.component_manager_base import ComponentManagerBase
from agentuniverse_product.base.product import Product


@singleton
class ProductManager(ComponentManagerBase[Product]):
    """A singleton manager class of the product."""

    def __init__(self):
        """Initialize the product manager with the PRODUCT component type."""
        super().__init__(ComponentEnum.PRODUCT)
