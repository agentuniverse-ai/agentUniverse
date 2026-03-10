# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/2/19 17:58
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: multimodal_agent.py
from agentuniverse.agent.template.rag_agent_template import RagAgentTemplate


class MultimodalAgent(RagAgentTemplate):
    """Multimodal agent.

    Inherits RagAgentTemplate which provides:
    - input_keys: ['input'], output_keys: ['output']
    - Standard parse_input / parse_result
    - AgentTemplate's execute flow with automatic memory, tool-calling loop,
      and output streaming via AgentContext
    """
    pass
