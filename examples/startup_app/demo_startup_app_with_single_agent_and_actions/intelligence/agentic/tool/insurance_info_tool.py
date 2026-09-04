# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/11/28 17:17
# @Author  : jijiawei
# @Email   : jijiawei.jjw@antgroup.com
# @FileName: insurance_info_tool.py
from agentuniverse.agent.action.tool.tool import Tool, ToolInput

from demo_startup_app_with_single_agent_and_actions.intelligence.utils.constant.prod_description import \
    PROD_A_DESCRIPTION, PROD_B_DESCRIPTION


class InsuranceInfoTool(Tool):
    """A tool that returns the description of the given insurance product."""

    def execute(self, input: str):
        """Return the description matching the given insurance product name.

        Args:
            input: The insurance product name (e.g. '保险产品A').

        Returns:
            The description of the matching product, defaulting to product B.
        """
        ins_name = input
        if ins_name == '保险产品A':
            return PROD_A_DESCRIPTION
        if ins_name == '保险产品B':
            return PROD_B_DESCRIPTION
        return PROD_B_DESCRIPTION
