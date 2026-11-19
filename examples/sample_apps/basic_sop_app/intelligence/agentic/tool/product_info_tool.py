# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/11/12 11:59
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: product_info_tool.py
from agentuniverse.agent.action.tool.tool import Tool, ToolInput
from basic_sop_app.intelligence.utils.constant import product_b_info, product_c_info


class SearchProductInfoTool(Tool):
    """Tool that composes insurance product descriptions for brands B and C from requested tags."""

    def execute(self, input: list):
        """Compose the product description texts for brands B and C.

        Args:
            input (list): Tags of the product clauses to include (e.g. 'A'-'L').
                The tag 'G' is skipped and 'K' is treated as 'L'.

        Returns:
            dict: Mapping of brand keys 'B' and 'C' to their extended descriptions.
        """
        product_info_item_list = input

        product_b_description = product_b_info.BASE_PRODUCT_DESCRIPTION
        product_c_description = product_c_info.BASE_PRODUCT_DESCRIPTION
        for item in product_info_item_list:
            if item == 'G':
                continue
            if item == 'K':
                product_b_description += product_b_info.PRODUCT_DESCRIPTION_MAP.get('L')
                product_c_description += product_c_info.PRODUCT_DESCRIPTION_MAP.get('L')
            else:
                product_b_description += product_b_info.PRODUCT_DESCRIPTION_MAP.get(item)
                product_c_description += product_c_info.PRODUCT_DESCRIPTION_MAP.get(item)

        return {'B': product_b_description, 'C': product_c_description}
