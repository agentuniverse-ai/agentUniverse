# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/2/20 11:29
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: param_converter.py
from agentuniverse.agent.action.tool.tool import Tool, ToolInput
from agentuniverse.agent.output_object import OutputObject


class ParamConverterTool(Tool):
    """Tool that converts raw input parameters into the expected output format.

    Picks the parameter key ending with 'result' as the outer dictionary key
    and groups the remaining parameters into an inner OutputObject dictionary.
    """

    def execute(self, params: dict):
        """
        Convert input parameters to a specific dictionary format.

          Find the key ending with 'result' as the outer dictionary key, and other parameters form the inner dictionary.
          If there are no other parameters, use the original parameters as the inner dictionary.

          Args:
              params (dict): Input object containing parameters to be converted

          Returns:
              dict: Converted dictionary structure in format:
                  {
                      result_key: OutputObject({
                          param1: value1,
                          param2: value2,
                      })
                  }
              Returns empty dict if no key ending with 'result' is found
          """
        result_key = next((k for k in params.keys() if k.endswith('result')), None)

        if result_key is None:
            return {}

        inner_dict = {k: v for k, v in params.items() if k != result_key}

        if inner_dict:
            result_dict = {result_key: OutputObject(inner_dict)}
        else:
            result_dict = {result_key: OutputObject(params)}

        return result_dict
