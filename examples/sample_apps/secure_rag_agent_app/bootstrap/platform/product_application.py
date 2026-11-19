# !/usr/bin/env python3
# -*- coding:utf-8 -*-

from agentuniverse.base.agentuniverse import AgentUniverse


class ProductApplication:
    """Product application entry (core mode only for demo)."""

    @classmethod
    def start(cls):
        AgentUniverse().start(core_mode=True)


if __name__ == "__main__":
    ProductApplication.start()
