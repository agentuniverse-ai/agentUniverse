# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/11 14:55
# @Author  : agentuniverse
# @FileName: prompt_optimization_agent.py


import os
import sys

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agentuniverse.base.agentuniverse import AgentUniverse
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager

# Initialize AgentUniverse
config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'config', 'config.toml')
print(f"Loading config from: {config_path}")
AgentUniverse().start(config_path=config_path, core_mode=True)


def run_optimization():
    """Run the prompt optimization agent demo."""
    agent_name = 'demo_prompt_optimization_agent'
    instance: Agent = AgentManager().get_instance_obj(agent_name)

    if not instance:
        print(f"Agent '{agent_name}' not found.")
        return

    print(f"Running agent: {agent_name}")
    
    # Run the agent with specific inputs required for prompt optimization
    input_data = {
        "samples": [
            "天弘标普500(QDII-FOF)C”是一只QDII-股票基金。回撤控制能力强：近1年下行风险与最大回撤排名靠前，风控能力较强。",
            "“中航机遇领航混合C”是一只混合型-偏股基金，投向通信行业。近1年超额收益率64.65%，优于98%同赛道基金，稳定投向通信赛道，持仓重合度57.45%。",
            "“嘉实上海金ETF联接C”是一只黄金基金，跟踪上海金指数。近1年最大回撤10.10%，优于88%同指数基金。",
            "“国泰瑞悦3个月持有期债券(FOF)”是一只FOF-债券基金,近3年最大回撤修复天数26天，优于90%同策略基金，跌后恢复快。"
        ],
        "initial_prompt": "为下面的基金产品生成100字左右的推荐文案：{input}",
        "batch_size": 2,
        "max_iterations": 2,
        "scoring_standard": "总分100分,不满足金融合规要求或存在事实性错误则直接得0分。在符合金融合规要求且无事实性错误的前提下，按（1）具有说服力和吸引力（上限25分）（2）易于理解（上限25分）（3）风格鲜明（上限25分）（4）重点突出（上限25分）给出总分评分。",
        "avg_score_threshold": 90
    }
    
    # Pass inputs as kwargs directly to run(), which will be validated by input_check()
    result = instance.run(**input_data)
    
    print("Optimization Result:")
    print(result.get_data('output')[-1]['prompt'])


if __name__ == '__main__':
    run_optimization()
