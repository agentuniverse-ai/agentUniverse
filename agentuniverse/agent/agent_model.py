# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/3/12 15:13
# @Author  : heji
# @Email   : lc299034@antgroup.com
# @FileName: agent_model.py
"""Agent model class."""
from typing import Optional
from pydantic import BaseModel


class AgentModel(BaseModel):
    """Agent model containing configuration and metadata.

    Stores agent configuration including info, profile, plan, memory,
    action, and work_pattern settings. Provides utility methods for
    extracting LLM parameters.
    """

    info: Optional[dict] = dict()
    profile: Optional[dict] = dict()
    plan: Optional[dict] = dict()
    memory: Optional[dict] = dict()
    action: Optional[dict] = dict()
    work_pattern: Optional[dict] = dict()

    def llm_params(self) -> dict:
        """Extract LLM parameters from agent profile configuration.

        Returns:
            dict: Dictionary of LLM parameters excluding 'name' and 'prompt_processor'.
                  Maps 'model_name' to 'model' key.
        """
        params = {}
        for key, value in self.profile.get('llm_model').items():
            if key == 'name' or key == 'prompt_processor':
                continue
            if key == 'model_name':
                params['model'] = value
            else:
                params[key] = value
        return params
