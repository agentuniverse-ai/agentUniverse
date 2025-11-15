# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    :
# @Author  :
# @Email   :
# @FileName: mock_search_tool.py

from agentuniverse.agent.action.tool.tool import Tool, ToolInput


class MockSearchTool(Tool):
    """The demo google search mock tool.
    """

    def execute(self, input: str):
        # get top10 results from mock search.
        res = self.mock_api_res()
        return res

    async def async_execute(self, tool_input: ToolInput):
        input = tool_input.get_data("input")
        # get top10 results from mock search.
        res = self.mock_api_res()
        return res

    def mock_api_res(self):
        res = (
            "In a recent interview discussing the tenth reduction of BYD holdings, Buffett said it was to "
            "better allocate Berkshire's capital. Earlier this year, Munger also mentioned reducing BYD at the "
            "Daily Journal event. The reduction may reflect adjusted expectations for the EV market's growth in China "
            "or a reassessment of BYD's valuation. Some analysts believe the current price might already reflect "
            "optimistic expectations. Since August 2022, Berkshire began the first reduction and the market speculated "
            "it might gradually exit. Macro environment changes and higher rates have also impacted growth sectors. "
            "BYD responded that operations remain healthy. Wall Street analysis suggests the portfolio is rotating away "
            "from tech to more familiar sectors, with larger positions rebuilt in insurance."
        )
        return res
