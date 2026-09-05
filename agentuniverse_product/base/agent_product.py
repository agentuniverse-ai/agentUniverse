# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/25 22:50
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: agent_product.py
from typing import Optional

from agentuniverse.agent.agent import Agent
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse_product.base.product import Product
from agentuniverse_product.base.product_configer import ProductConfiger


class AgentProduct(Product):
    """The basic class of the agent product."""

    opening_speech: Optional[str] = None
    _instance: Optional[Agent] = None

    @property
    def instance(self) -> Agent:
        """Get the agent instance corresponding to the agent product.

        Returns:
            Agent: The underlying agent instance.
        """
        return self._instance

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
        super().initialize_by_component_configer(product_configer)
        if hasattr(product_configer, 'opening_speech') and product_configer.opening_speech:
            self.opening_speech = product_configer.opening_speech
        return self
