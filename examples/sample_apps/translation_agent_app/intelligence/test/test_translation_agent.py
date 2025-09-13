# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/4/1 14:32
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: test_rag_agent.py
import unittest

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.base.agentuniverse import AgentUniverse


class TranslationAgentTest(unittest.TestCase):
    """
    Test cases for the rag agent
    """

    def setUp(self) -> None:
        AgentUniverse().start(config_path='../../config/config.toml')

    def test_translation_agent_long(self):
        instance: Agent = AgentManager().get_instance_obj('translation_by_token_agent')
        with open('translation_data/long_text.txt', 'r') as f:
            data = f.read()

        output_object: OutputObject = instance.run(source_lang="英文", target_lang="中文",
                                                   source_text=data
                                                   )
        res_info = f"\nRag agent execution result is :\n"
        res_info += output_object.get_data('output')
        # 创建文件，并写入文件
        with open('translation_data/long_text_result.txt', 'w') as f:
            f.write(res_info)
        print(res_info)

    # def test_translation_agent_short(self):
    #     instance: Agent = AgentManager().get_instance_obj('translation_agent')
    #     with open('./translation_data/short_text.txt', 'r') as f:
    #         data = f.read()
    #
    #     output_object: OutputObject = instance.run(source_lang="英文", target_lang="中文",
    #                                                source_text=data
    #                                                )
    #     res_info = f"\nRag agent execution result is :\n"
    #     res_info += output_object.get_data('output')
    #     # 创建文件，并写入文件
    #     with open('./translation_data/short_text_result.txt', 'w') as f:
    #         f.write(res_info)
    #     print(res_info)


if __name__ == '__main__':
    unittest.main()
