# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/4/2 18:02
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: mock_agent.py

import json


class MockOutPut:
    def __init__(self, output: dict):
        self.__output = output

    def to_json_str(self) -> str:
        try:  
            return json.dumps(self.__output, ensure_ascii=False)  
        except (TypeError, ValueError) as e:  
            raise ValueError(f"Failed to serialize output to JSON: {e}")"


class MockAgent:
    def __init__(self, run_result: dict):
        self.__run_result = MockOutPut(run_result)

    def run(self, **kwargs):
        return self.__run_result
