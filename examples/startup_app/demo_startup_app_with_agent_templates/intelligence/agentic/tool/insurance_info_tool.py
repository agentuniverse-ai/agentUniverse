# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/11/28 17:17
# @Author  : jijiawei
# @Email   : jijiawei.jjw@antgroup.com
# @FileName: insurance_info_tool.py
from agentuniverse.agent.action.tool.tool import Tool, ToolInput

from demo_startup_app_with_agent_templates.intelligence.utils.constant.prod_description import \
    PROD_A_DESCRIPTION, PROD_B_DESCRIPTION


class InsuranceInfoTool(Tool):
    def execute(self, ins_name: str):
        if ins_name == '保险产品A':
            return PROD_A_DESCRIPTION
        if ins_name == '保险产品B':
            return PROD_B_DESCRIPTION
        return PROD_B_DESCRIPTION
