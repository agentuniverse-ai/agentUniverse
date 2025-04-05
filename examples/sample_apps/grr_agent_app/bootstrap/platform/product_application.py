# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2/17/25
# @Author  : quesheng
# @Email   : huiyi.why@antgroup.com
from agentuniverse.base.agentuniverse import AgentUniverse
from agentuniverse_product.agentuniverse_product import AgentUniverseProduct


class ProductApplication:
    """
    Product application: agentUniverse-product portal.

    After startup, the system redirects to the aU-product homepage by default.
    """

    @classmethod
    def start(cls):
        AgentUniverse().start(core_mode=True)
        AgentUniverseProduct().start()


if __name__ == "__main__":
    ProductApplication.start()
