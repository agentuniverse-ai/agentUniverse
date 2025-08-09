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
        res = f"""采访中谈及第十次减持比亚迪，巴菲特称是为了便于伯克希尔进行更好的资金配置。而在今年2月，
        芒格在美国报纸和软件公司Daily Journal举行的虚拟年会上也曾谈及减持比亚迪的 ... 
        对比亚迪的减持可能反映出巴菲特对中国新能源汽车市场未来增长的预期调整，或是对比亚迪本身估值的重新评估。
        这也可能暗示着巴菲特认为当前比亚迪股价已经 ... 
        巴菲特从2022年8月底开始首次减持比亚迪，那个时候市场就有声音表示巴菲特要有计划有节奏地清仓比亚迪了。
        差不多两年的时间，伯克希尔哈撒韦对比亚迪的持仓 ... 
        究其原因，除了前文提到的比亚迪估值偏高以及巴菲特“减持效应”之外，当前宏观经济环境的变化也是关键影响因子。
        近期美联储释放鹰派加息信号，对全球成长板块 ...
         巴菲特持续减持什么原因？比亚迪回应：公司正在和对方沟通目前经营状况良好. 
         对此，华尔街分析表示：“从调仓动作来看，巴菲特正在从科技板块撤退，回归此前熟悉的行业。
         其中最明显的变化就是巴菲特又重新大手笔建仓买入安达保险。”. 
         公司战略：巴菲特曾表示，伯克希尔哈撒韦公司希望将更多的注意力放在美国市场，这可能是其减持在美国以外市场的投资，如比亚迪的原因之一。 
         这是2023年以来，港交所第5次披露伯克希尔哈撒韦减持比亚迪H股，也是2022年8月该公司首次减持以来的第11次披露。
         至上一次披露减持后，伯克希尔哈撒韦持有比例 ... 
         业内人士认为，9月电动车行业整体渗透率提升的增速已经放缓，比亚迪三季报业绩优异，
         除了销售增速较快以外，上游碳酸锂价格下滑也是原因之一，未来业绩增速会不 ... 
         不可否认的是，巴菲特首次减持短期内可能对比亚迪股价构成压力，也有部分投资者跟风减持，但具体走势要根据企业基本面来确定。 
         事实上，在汽车业务转暖的同时，比亚迪 ...
        """
        return res
