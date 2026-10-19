"""Validate truncation against the full formatted prompt, without model calls."""
import math
import unittest
from unittest import mock

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
import tiktoken

from agentuniverse.base.util.prompt_util import process_llm_token


_ENCODING = tiktoken.Encoding(
    name='prompt_budget_test_bytes', pat_str=r'(?s).',
    mergeable_ranks={bytes([value]): value for value in range(256)},
    special_tokens={})


class ByteCounter:
    """Use a real offline tokenizer with a small deterministic context budget."""

    max_tokens = 32

    def __init__(self, encoding=_ENCODING, failures_at=()):
        self.calls = 0
        self.encoding = encoding
        self.failures_at = set(failures_at)

    def max_context_length(self):
        return 64

    def get_num_tokens(self, text):
        self.calls += 1
        if self.calls in self.failures_at:
            raise RuntimeError('temporary tokenizer failure')
        return len(self.encoding.encode(text))


class TestPromptTemplateBudget(unittest.TestCase):
    """The selected variable shares the input budget with the whole template."""

    def setUp(self):
        patcher = mock.patch('agentuniverse.base.util.prompt_util.LLMManager')
        self.manager = patcher.start()
        self.manager.return_value.get_instance_obj.return_value = None
        self.addCleanup(patcher.stop)
        self.counter = ByteCounter()
        self.profile = {'llm_model': {'max_tokens': 32}}

    def process(self, prompt, values, **kwargs):
        process_llm_token(self.counter, prompt, self.profile, values, **kwargs)

    def assert_fits(self, prompt, values, budget=32):
        formatted = prompt.format(**{
            key: values[key] for key in prompt.input_variables})
        self.assertLessEqual(len(_ENCODING.encode(formatted)), budget)

    def test_fixed_instruction_is_included(self):
        prompt = PromptTemplate.from_template('instruction:{background}')
        values = {'background': 'x' * 1000}
        self.process(prompt, values)
        self.assert_fits(prompt, values)
        self.assertTrue(('x' * 1000).startswith(values['background']))

    def test_other_variables_keep_their_values_and_budget(self):
        prompt = PromptTemplate.from_template('{question}:{background}')
        values = {'question': 'fixed question', 'background': 'x' * 1000, 'extra': object()}
        extra = values['extra']
        self.process(prompt, values)
        self.assert_fits(prompt, values)
        self.assertEqual('fixed question', values['question'])
        self.assertIs(extra, values['extra'])

    def test_repeated_variable_is_counted_each_time(self):
        prompt = PromptTemplate.from_template('{background}|{background}')
        values = {'background': 'x' * 1000}
        self.process(prompt, values)
        self.assert_fits(prompt, values)

    def test_chat_roles_and_messages_are_included(self):
        prompt = ChatPromptTemplate.from_messages([
            ('system', 'short rules'), ('human', '{background}')])
        values = {'background': 'x' * 1000}
        self.process(prompt, values)
        self.assert_fits(prompt, values)

    def test_unicode_prefix_fits_without_splitting_characters(self):
        prompt = PromptTemplate.from_template('问:{background}')
        content = '你好💡' * 100
        values = {'background': content}
        self.process(prompt, values)
        self.assert_fits(prompt, values)
        self.assertTrue(content.startswith(values['background']))
        values['background'].encode('utf-8')

    def test_fixed_prompt_can_use_the_entire_budget(self):
        prompt = PromptTemplate.from_template('i' * 32 + '{background}')
        values = {'background': 'x' * 1000}
        self.process(prompt, values)
        self.assertEqual('', values['background'])
        self.assert_fits(prompt, values)

    def test_oversized_fixed_prompt_reports_error_without_mutation(self):
        prompt = PromptTemplate.from_template('i' * 33 + '{background}')
        values = {'background': 'x' * 1000}
        with self.assertRaisesRegex(ValueError, 'budget'):
            self.process(prompt, values)
        self.assertEqual('x' * 1000, values['background'])

    def test_unused_selected_variable_cannot_fix_an_oversized_prompt(self):
        prompt = PromptTemplate.from_template('{question}')
        values = {'question': 'q' * 100, 'background': 'x' * 1000}
        with self.assertRaisesRegex(ValueError, 'background'):
            self.process(prompt, values)
        self.assertEqual('x' * 1000, values['background'])

    def test_custom_selected_variable_is_supported(self):
        prompt = PromptTemplate.from_template('history:{history}')
        values = {'history': 'h' * 1000}
        self.process(prompt, values, var_to_process='history')
        self.assert_fits(prompt, values)

    def test_explicit_zero_output_reservation_is_retained(self):
        self.profile['llm_model']['max_tokens'] = 0
        prompt = PromptTemplate.from_template('instruction:{background}')
        values = {'background': 'x' * 1000}
        self.process(prompt, values)
        self.assert_fits(prompt, values, budget=64)

    def test_fitting_prompt_is_unchanged(self):
        prompt = PromptTemplate.from_template('short:{background}')
        values = {'background': 'text'}
        self.process(prompt, values)
        self.assertEqual({'background': 'text'}, values)

    def test_large_content_uses_logarithmically_many_counts(self):
        prompt = PromptTemplate.from_template('rule:{background}')
        values = {'background': 'x' * 100000}
        self.process(prompt, values)
        self.assert_fits(prompt, values)
        self.assertLessEqual(self.counter.calls, 2 + math.ceil(math.log2(100000)))

    def test_stuff_processor_still_uses_its_summary(self):
        self.profile['llm_model']['prompt_processor'] = {'type': 'stuff'}
        prompt = PromptTemplate.from_template('rules:{background}')
        values = {'background': 'x' * 1000}
        with mock.patch('agentuniverse.base.util.prompt_util.summarize_by_stuff',
                        return_value='summary') as summarize:
            self.process(prompt, values)
        self.assertEqual('summary', values['background'])
        summarize.assert_called_once()

    def test_token_merges_across_variable_boundary_are_counted_in_context(self):
        ranks = {bytes([value]): value for value in range(256)}
        ranks.update({b'ab': 256, b'abc': 257})
        encoding = tiktoken.Encoding(
            name='prompt_budget_test_merges', pat_str=r'(?s).+',
            mergeable_ranks=ranks, special_tokens={})
        self.counter = ByteCounter(encoding=encoding)
        prompt = PromptTemplate.from_template('a{background}')
        content = 'bc' * 100
        values = {'background': content}
        self.process(prompt, values)
        self.assertLessEqual(len(encoding.encode(prompt.format(**values))), 32)
        self.assertTrue(content.startswith(values['background']))

    def test_transient_count_failure_recovers_with_a_fitting_prompt(self):
        self.counter = ByteCounter(failures_at={2})
        prompt = PromptTemplate.from_template('instruction:{background}')
        values = {'background': 'x' * 1000}
        self.process(prompt, values)
        self.assert_fits(prompt, values)
        self.assertGreaterEqual(self.counter.calls, 3)

    def test_second_count_failure_does_not_retry_or_mutate_input(self):
        self.counter = ByteCounter(failures_at={2, 5})
        prompt = PromptTemplate.from_template('instruction:{background}')
        values = {'background': 'x' * 1000}
        with self.assertRaisesRegex(ValueError, 'Count prompt tokens failed'):
            self.process(prompt, values)
        self.assertEqual(5, self.counter.calls)
        self.assertEqual('x' * 1000, values['background'])
