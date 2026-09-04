# !/usr/bin/env python3
# -*- coding:utf-8 -*-
import datetime
# @Time    : 2024/4/1 14:32
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: test_demo_agent.py
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
        """Start the AgentUniverse runtime for the demo app.

        Initializes the global runtime from ``config/config.toml`` so the
        agent instance can be retrieved in the test methods.
        """
        AgentUniverse().start(config_path='../../config/config.toml')

    def read_output(self, output_stream: queue.Queue):
        """Consume streamed agent output in a loop until the EOF marker.

        Args:
            output_stream (queue.Queue): Queue the agent writes streamed
                chunks into; reading stops on the EOF marker or an empty
                queue.
        """
        while True:
            try:
                res = output_stream.get()
                if res == '{"type": "EOF"}':
                    break
                print(datetime.datetime.now().isoformat(),res)
            except queue.Empty:
                break

    def test_demo_agent_stream(self):
        """Run the demo agent with an output stream.

        Fetches the ``demo_agent`` instance, consumes its streamed output in
        a background thread and prints the final run result.
        """
        output_stream = queue.Queue(10)
        instance: Agent = AgentManager().get_instance_obj('demo_agent')
        Thread(target=self.read_output, args=(output_stream,)).start()
        result = instance.run(input='你来自哪里，名字是什么,请详细介绍一下数据库', output_stream=output_stream,scene_code="billing_center_test")
        print(result)


if __name__ == '__main__':
    unittest.main()
