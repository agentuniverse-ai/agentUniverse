"""Retry regressions using an offline byte tokenizer and real prompt utilities."""
import unittest
from unittest import mock

from langchain_core.prompts import PromptTemplate
import tiktoken

from agentuniverse.base.util.prompt_util import (
    process_llm_token, split_texts, truncate_content,
)


_BYTE_ENCODING = tiktoken.Encoding(
    name='prompt_retry_test_bytes', pat_str=r'(?s).',
    mergeable_ranks={bytes([value]): value for value in range(256)},
    special_tokens={})


class TokenCounter:
    """Inject transient count failures without network requests or model calls."""

    max_tokens = 32

    def __init__(self, failures_at=()):
        self.failures_at = set(failures_at)
        self.calls = 0

    def get_num_tokens(self, text):
        self.calls += 1
        if self.calls in self.failures_at:
            raise RuntimeError(f'counter attempt {self.calls}')
        return len(_BYTE_ENCODING.encode(text))

    def max_context_length(self):
        return 64


class TestPromptRetryOptions(unittest.TestCase):
    """A recovered operation must use the same options as a successful one."""

    def test_retry_retains_custom_chunk_size_and_overlap(self):
        text = 'abcdefghijklmnopqrstuvwxyz' * 4
        expected = split_texts([text], TokenCounter(), chunk_size=16, chunk_overlap=4)
        counter = TokenCounter(failures_at={1})
        self.assertEqual(
            expected, split_texts([text], counter, chunk_size=16, chunk_overlap=4))
        self.assertEqual(2, counter.calls)

    def test_retry_retains_zero_overlap(self):
        text = 'x' * 1800
        expected = split_texts([text], TokenCounter(), chunk_overlap=0)
        self.assertEqual(
            expected, split_texts([text], TokenCounter({1}), chunk_overlap=0))

    def test_late_failure_restarts_batch_with_original_options(self):
        texts = ['first document', 'second document is longer']
        expected = split_texts(texts, TokenCounter(), chunk_size=9, chunk_overlap=0)
        counter = TokenCounter(failures_at={2})
        self.assertEqual(
            expected, split_texts(texts, counter, chunk_size=9, chunk_overlap=0))
        self.assertEqual(4, counter.calls)

    def test_truncate_content_retains_requested_length_after_retry(self):
        content = 'x' * 1000
        counter = TokenCounter(failures_at={1})
        self.assertEqual('x' * 20, truncate_content(content, 20, counter))
        self.assertEqual(2, counter.calls)

    def test_prompt_processing_retains_its_input_budget_after_retry(self):
        counter = TokenCounter(failures_at={2})
        planner_input = {'background': 'x' * 1000}
        profile = {'llm_model': {'max_tokens': 32}}
        prompt = PromptTemplate.from_template('{background}')
        with mock.patch(
                'agentuniverse.base.util.prompt_util.LLMManager') as manager:
            manager.return_value.get_instance_obj.return_value = None
            process_llm_token(counter, prompt, profile, planner_input)
        self.assertEqual('x' * 32, planner_input['background'])
        self.assertEqual(3, counter.calls)

    def test_retry_false_surfaces_first_failure(self):
        counter = TokenCounter(failures_at={1, 2})
        with self.assertRaisesRegex(ValueError, 'counter attempt 1'):
            split_texts(['text'], counter, chunk_size=4, retry=False)
        self.assertEqual(1, counter.calls)

    def test_repeated_failure_stops_after_one_retry(self):
        counter = TokenCounter(failures_at={1, 2, 3})
        with self.assertRaisesRegex(ValueError, 'counter attempt 2'):
            split_texts(['text'], counter, chunk_size=4, chunk_overlap=0)
        self.assertEqual(2, counter.calls)

    def test_empty_batch_does_not_count_tokens(self):
        counter = TokenCounter(failures_at={1})
        self.assertEqual([], split_texts([], counter, chunk_size=4, chunk_overlap=0))
        self.assertEqual(0, counter.calls)
