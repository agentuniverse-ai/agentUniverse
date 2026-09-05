# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/12 17:57
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: planner_product.py
from typing import Optional, List

from agentuniverse.agent.plan.planner.planner import Planner
from agentuniverse_product.base.product import Product
from agentuniverse_product.base.product_configer import ProductConfiger


class PlannerProduct(Product):
    """The basic class of the planner product."""

    member_keys: Optional[List[str]] = None
    _instance: Optional[Planner] = None

    @property
    def instance(self) -> Planner:
        """Get the planner instance corresponding to the planner product.

        Returns:
            Planner: The underlying planner instance.
        """
        return self._instance

    def initialize_by_component_configer(self,
                                         product_configer: ProductConfiger) -> 'Product':
        """Initialize the Product by the ProductConfiger object.

        Args:
            product_configer(ProductConfiger): A configer contains product basic info.
        Returns:
            Product: A Product instance.
        """
        super().initialize_by_component_configer(product_configer)
        if hasattr(product_configer, 'member_keys') and product_configer.member_keys:
            self.member_keys = product_configer.member_keys
        return self
