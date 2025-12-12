# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/11 14:55
# @Author  : yiying.cy
# @Email   : yiying.cy@antgroup.com
# @FileName: prompt_optimization_agent.py


from agentuniverse.base.agentuniverse import AgentUniverse
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager

AgentUniverse().start(config_path='../../config/config.toml', core_mode=True)

def run_optimization():
    """Run the prompt optimization agent demo."""
    agent_name = 'demo_optimization_agent'
    instance: Agent = AgentManager().get_instance_obj(agent_name)

    if not instance:
        print(f"Agent '{agent_name}' not found.")
        return

    print(f"Running agent: {agent_name}")
    
    # Run the agent with specific inputs required for prompt optimization
    input_data1 = {
        "samples": [
            {"fund_info":"天弘标普500(QDII-FOF)C”是一只QDII-股票基金。近1年下行风险与最大回撤排名靠前，风控能力较强。","user_info":"用户的高弹性行业基金已配置较多。"},
            {"fund_info":"“中航机遇领航混合C”是一只混合型-偏股基金，投向通信行业。近1年超额收益率64.65%，优于98%同类基金，稳定投向通信赛道，持仓重合度57.45%。","user_info":"用户最近在科技、军工、医药等成长板块基金上积极布局。"},
            {"fund_info":"“嘉实上海金ETF联接C”是一只黄金基金，跟踪上海金指数。近1年最大回撤10.10%，优于88%同类基金。","user_info":"用户没有持有黄金基金。"},
            {"fund_info":"“国泰瑞悦3个月持有期债券(FOF)”是一只FOF-债券基金,近3年最大回撤修复天数26天，优于90%同策略基金，跌后恢复快。","user_info":"用户最近没有任何操作"},
            {"fund_info":"“金鹰红利价值灵活配置混合A”是一只混合型-灵活基金，属于成长风格，近3年滚动持有1年超额胜率91%，近3年最大回撤28.29%。","user_info":"用户最近卖出了一支基金"},
            {"fund_info":"天弘安康混合A是一只偏债混合基金，采用中波固收+策略，攻守兼备。近1年最大回撤1.98%。 " ,"user_info":"用户的债基持仓较多。"}
        ],
        "agent_name_for_optimization":"demo_answer_agent_to_be_adapted",
        "batch_size": 2,
        "max_iterations": 5,
        "scoring_standard": "总分100分,不满足金融合规要求或存在事实性错误则直接得0分。在符合金融合规要求且无事实性错误的前提下，按（1）具有说服力和吸引力（上限25分）（2）易于理解（上限25分）（3）风格鲜明生动（上限25分）（4）贴合用户兴趣（上限25分）给出总分评分。",
        "avg_score_threshold": 95
    }
    input_data2={
        "samples": [
                "Explain the concept of quantum computing.",
                "Explain why Apple Inc. is so popular among tech enthusiasts?",
                "Explain the main components of a computer system",
                "Explain how photosynthesis work in plants?"
        ],
        "initial_prompt": "Explain the following questions in simple terms.{input}",
        "batch_size": 2,
        "max_iterations": 4,
        "scoring_standard": "Total score is 100. 50 for perfectly explaining the question, 50 for explanation without any jargons ",
        "avg_score_threshold": 95
    }

    # Pass inputs as kwargs directly to run(), which will be validated by input_check()
    result = instance.run(**input_data1)
    final_prompt=result.get_data('output')[-1]['prompt']
    print("prompt after optimization:")
    print(final_prompt)


if __name__ == '__main__':
    run_optimization()
