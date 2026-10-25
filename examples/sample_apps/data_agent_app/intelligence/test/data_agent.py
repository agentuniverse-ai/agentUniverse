# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/2 16:58
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: data_agent.py
from agentuniverse.base.agentuniverse import AgentUniverse
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager

AgentUniverse().start(config_path='../../config/config.toml', core_mode=True)


def data_process(queryset_path: str, turn: int, **kwargs):
    """Process the dataset with the given arguments and return the result.
    """
    instance: Agent = AgentManager().get_instance_obj('data_agent')
    instance.run(queryset_path=queryset_path, turn=turn, **kwargs)


if __name__ == '__main__':
    queryset_path_list = ["./data/queryset_cn.jsonl"]
    for path in queryset_path_list:
        data_process(queryset_path=path, turn=2)
