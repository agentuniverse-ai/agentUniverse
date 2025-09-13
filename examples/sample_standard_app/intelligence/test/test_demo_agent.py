# !/usr/bin/env python3
# -*- coding:utf-8 -*-
import datetime
# @Time    : 2024/4/1 14:32
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: test_rag_agent.py
import unittest
import queue
from threading import Thread

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.base.agentuniverse import AgentUniverse


class DemoAgentTest(unittest.TestCase):
    """
    Test cases for the rag agent
    """

    def setUp(self) -> None:
        AgentUniverse().start(config_path='../../config/config.toml')

    def read_output(self, output_stream: queue.Queue):
        while True:
            try:
                res = output_stream.get()
                if res == '{"type": "EOF"}':
                    break
                print(datetime.datetime.now().isoformat(),res)
            except queue.Empty:
                break

    def test_demo_agent_stream(self):
        output_stream = queue.Queue(10)
        instance: Agent = AgentManager().get_instance_obj('demo_agent')
        Thread(target=self.read_output, args=(output_stream,)).start()
        result = instance.run(input='你来自哪里，名字是什么,请详细介绍一下数据库', output_stream=output_stream,scene_code="billing_center_test")
        print(result)



if __name__ == '__main__':
    unittest.main()
