# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/4/2 18:02
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: mock_agent.py

import json


class MockOutPut:
    """Mockoutput.
    """
    def __init__(self, output: dict):
        """Initialize the __init__ instance.
        """
        self.__output = output

    def to_json_str(self) -> str:
        """Serialize this object to a json string.
        """
        try:  
            return json.dumps(self.__output, ensure_ascii=False)  
        except (TypeError, ValueError) as e:  
            raise ValueError(f"Failed to serialize output to JSON: {e}")


class MockAgent:
    """Mockagent.
    """
    def __init__(self, run_result: dict):
        """Initialize the __init__ instance.
        """
        self.__run_result = MockOutPut(run_result)

    def run(self, **kwargs):
        """Run the mocked behavior.
        """
        return self.__run_result
