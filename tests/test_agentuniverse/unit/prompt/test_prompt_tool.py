#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/15
# @Author  : dxz0069
# @FileName: test_prompt_tool.py

import asyncio
import json
import unittest
from unittest.mock import MagicMock

from agentuniverse.prompt.prompt_model import AgentPromptModel
from agentuniverse.prompt.prompt_tool import GeneratedPrompt, PromptTool


def _llm_returning(text):
    llm = MagicMock()
    output = MagicMock()
    output.text = text
    llm.call.return_value = output

    async def _acall(**kwargs):
        return output

    llm.acall = _acall
    return llm


VALID_JSON = json.dumps({
    "introduction": "You are an airline customer service agent.",
    "target": "Answer traveler questions accurately and briefly.",
    "instruction": "Greet the traveler, answer the {user_question} using the FAQ, escalate on complaints.",
    "input_variables": ["user_question"],
})


class TestGeneratedPrompt(unittest.TestCase):
    """Test cases for the GeneratedPrompt result object."""

    def test_as_agent_prompt_model(self):
        generated = GeneratedPrompt(introduction='i', target='t', instruction='x')
        model = generated.as_agent_prompt_model()
        self.assertIsInstance(model, AgentPromptModel)
        self.assertEqual(model.introduction, 'i')
        self.assertEqual(model.target, 't')
        self.assertEqual(model.instruction, 'x')

    def test_to_yaml_config(self):
        generated = GeneratedPrompt(
            introduction="You are a 'helpful' agent.",
            target='Answer questions.',
            instruction='Answer the {question}.',
            input_variables=['question'],
        )
        yaml_config = generated.to_yaml_config(name='my_prompt')
        self.assertIn("name: 'my_prompt'", yaml_config)
        self.assertIn('type: \'PROMPT\'', yaml_config)
        self.assertIn('"You are a \'helpful\' agent."', yaml_config)
        self.assertIn('input_variables: [question]', yaml_config)
        parsed = json.loads(
            [line for line in yaml_config.splitlines() if line.startswith('introduction:')][0]
            .split('introduction: ', 1)[1])
        self.assertEqual(parsed, "You are a 'helpful' agent.")

    def test_to_yaml_config_skips_empty_sections(self):
        generated = GeneratedPrompt(target='only target')
        yaml_config = generated.to_yaml_config()
        self.assertIn('target: "only target"', yaml_config)
        self.assertNotIn('introduction:', yaml_config)
        self.assertNotIn('instruction:', yaml_config)
        self.assertNotIn('input_variables:', yaml_config)


class TestPromptTool(unittest.TestCase):
    """Test cases for the PromptTool, run against a mocked LLM."""

    def setUp(self):
        self.tool = PromptTool(llm=_llm_returning(VALID_JSON))

    def test_generate(self):
        result = self.tool.generate(scenario='airline customer service')
        self.assertEqual(result.introduction, 'You are an airline customer service agent.')
        self.assertEqual(result.input_variables, ['user_question'])
        messages = self.tool.llm.call.call_args.kwargs['messages']
        self.assertEqual(messages[0]['role'], 'system')
        self.assertIn('airline customer service', messages[1]['content'])
        self.assertFalse(self.tool.llm.call.call_args.kwargs['streaming'])

    def test_generate_includes_optional_blocks(self):
        self.tool.generate(scenario='s', content='FAQ pages', target='be brief',
                           )
        user_content = self.tool.llm.call.call_args.kwargs['messages'][1]['content']
        self.assertIn('FAQ pages', user_content)
        self.assertIn('Required target: be brief', user_content)

    def test_generate_rejects_empty_scenario(self):
        with self.assertRaises(ValueError):
            self.tool.generate(scenario='   ')

    def test_generate_with_language(self):
        tool = PromptTool(llm=_llm_returning(VALID_JSON), language='中文')
        tool.generate(scenario='s')
        user_content = tool.llm.call.call_args.kwargs['messages'][1]['content']
        self.assertIn('Write the prompt in 中文', user_content)

    def test_optimize(self):
        result = self.tool.optimize(introduction='old intro', instruction='old {q}',
                                    feedback='too vague')
        self.assertEqual(result.target, 'Answer traveler questions accurately and briefly.')
        messages = self.tool.llm.call.call_args.kwargs['messages']
        self.assertIn('old intro', messages[1]['content'])
        self.assertIn('too vague', messages[1]['content'])

    def test_optimize_rejects_empty_prompt(self):
        with self.assertRaises(ValueError):
            self.tool.optimize()

    def test_agenerate_and_aoptimize(self):
        result = asyncio.run(self.tool.agenerate(scenario='s'))
        self.assertEqual(result.input_variables, ['user_question'])
        result = asyncio.run(self.tool.aoptimize(instruction='x'))
        self.assertEqual(result.instruction.startswith('Greet'), True)

    def test_parse_fenced_json(self):
        tool = PromptTool(llm=_llm_returning(f'```json\n{VALID_JSON}\n```'))
        result = tool.generate(scenario='s')
        self.assertEqual(result.introduction, 'You are an airline customer service agent.')

    def test_parse_json_embedded_in_prose(self):
        tool = PromptTool(llm=_llm_returning(
            'Here is your prompt:\n' + VALID_JSON + '\nHope it helps!'))
        result = tool.generate(scenario='s')
        self.assertEqual(result.target, 'Answer traveler questions accurately and briefly.')

    def test_parse_invalid_answer_yields_empty_prompt(self):
        tool = PromptTool(llm=_llm_returning('no json here at all'))
        result = tool.generate(scenario='s')
        self.assertIsNone(result.introduction)
        self.assertEqual(result.input_variables, [])

    def test_parse_empty_answer_raises(self):
        tool = PromptTool(llm=_llm_returning(''))
        with self.assertRaises(ValueError):
            tool.generate(scenario='s')

    def test_extract_json_handles_nested_braces_in_strings(self):
        payload = '{"introduction": "uses {placeholder} inside", "target": "t"}'
        parsed = PromptTool._extract_json('answer: ' + payload)
        self.assertEqual(parsed['introduction'], 'uses {placeholder} inside')

    def test_missing_llm_raises(self):
        tool = PromptTool(llm_name='no_such_llm')
        with unittest.mock.patch('agentuniverse.llm.llm_manager.LLMManager') as manager:
            manager.return_value.get_instance_obj.return_value = None
            with self.assertRaises(ValueError):
                tool.generate(scenario='s')


if __name__ == '__main__':
    unittest.main()
