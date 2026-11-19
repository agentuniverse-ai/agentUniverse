#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest

from agentuniverse.agent.agent_model import AgentModel


class TestAgentModel(unittest.TestCase):
    def test_llm_params_returns_empty_mapping_without_llm_config(self):
        self.assertEqual(AgentModel(profile={}).llm_params(), {})

    def test_llm_params_keeps_supported_bind_values(self):
        model = AgentModel(profile={
            "llm_model": {
                "name": "default_llm",
                "prompt_processor": {"type": "truncate"},
                "model_name": "gpt-test",
                "temperature": 0.2,
            }
        })

        self.assertEqual(
            model.llm_params(),
            {"model": "gpt-test", "temperature": 0.2},
        )


if __name__ == "__main__":
    unittest.main()
