#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Unit test for SecureRagWorkPattern.

The pattern itself does not depend on a real LLM: planning/executing/reviewing/expressing
are injected AgentTemplate instances. This test uses stub templates to verify the
control flow of the work pattern (pass / mask / block / retry).
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.work_pattern.secure_rag_work_pattern import SecureRagWorkPattern


class StubAgentTemplate:
    name = 'stub'

    def __init__(self, result):
        self._result = result

    def run(self, **kwargs):
        from agentuniverse.agent.output_object import OutputObject
        return OutputObject(self._result)


def make_input(text='What is the capital of France?'):
    io = InputObject()
    io.add_data('input', text)
    return io


def test_pass_path():
    pattern = SecureRagWorkPattern()
    pattern.planning = StubAgentTemplate({'strategy': ['hybrid_retrieval']})
    pattern.executing = StubAgentTemplate({'answer': 'Paris', 'contexts': ['Paris is the capital of France.']})
    pattern.reviewing = StubAgentTemplate({
        'passed': True,
        'score': 0.95,
        'action': 'pass',
        'sanitized_answer': 'Paris',
        'reasons': [],
    })
    pattern.expressing = StubAgentTemplate({'final_answer': 'Paris', 'reasons': []})

    result = pattern.invoke(make_input(), {'retry_count': 1, 'eval_threshold': 0.6, 'security_threshold': 0.8})
    assert 'result' in result
    rounds = result['result']
    assert len(rounds) == 1
    expressing = rounds[0]['expressing_result']
    assert expressing['final_answer'] == 'Paris'
    assert rounds[0]['reviewing_result']['passed'] is True
    print('test_pass_path OK')


def test_mask_path():
    pattern = SecureRagWorkPattern()
    pattern.planning = StubAgentTemplate({'strategy': ['hybrid_retrieval']})
    pattern.executing = StubAgentTemplate({'answer': 'secret token abc123', 'contexts': []})
    pattern.reviewing = StubAgentTemplate({
        'passed': False,
        'score': 0.3,
        'action': 'mask',
        'sanitized_answer': 'secret token ***',
        'reasons': ['sensitive data detected'],
    })
    pattern.expressing = StubAgentTemplate({'final_answer': 'secret token ***', 'reasons': ['sensitive data detected']})

    result = pattern.invoke(make_input(), {'retry_count': 1})
    rounds = result['result']
    expressing = rounds[0]['expressing_result']
    assert expressing['final_answer'] == 'secret token ***'
    assert rounds[0]['reviewing_result']['action'] == 'mask'
    print('test_mask_path OK')


def test_block_path():
    pattern = SecureRagWorkPattern()
    pattern.planning = StubAgentTemplate({'strategy': ['hybrid_retrieval']})
    pattern.executing = StubAgentTemplate({'answer': 'forbidden content', 'contexts': []})
    pattern.reviewing = StubAgentTemplate({
        'passed': False,
        'score': 0.1,
        'action': 'block',
        'sanitized_answer': '',
        'reasons': ['prohibited topic'],
    })
    pattern.expressing = StubAgentTemplate({'final_answer': '[内容因安全审查未通过被拦截]', 'reasons': ['prohibited topic']})

    result = pattern.invoke(make_input(), {'retry_count': 1})
    rounds = result['result']
    expressing = rounds[0]['expressing_result']
    assert expressing['final_answer'] == '[内容因安全审查未通过被拦截]'
    assert rounds[0]['reviewing_result']['action'] == 'block'
    print('test_block_path OK')


def test_retry_until_pass():
    call_count = {'n': 0}

    class ReviewingStub:
        name = 'reviewing_stub'

        def run(self, **kwargs):
            call_count['n'] += 1
            from agentuniverse.agent.output_object import OutputObject
            if call_count['n'] < 2:
                return OutputObject({
                    'passed': False, 'score': 0.2, 'action': 'mask',
                    'sanitized_answer': 'sanitized v1', 'reasons': ['retry'],
                })
            return OutputObject({
                'passed': True, 'score': 0.9, 'action': 'pass',
                'sanitized_answer': 'clean answer', 'reasons': [],
            })

    pattern = SecureRagWorkPattern()
    pattern.planning = StubAgentTemplate({'strategy': ['hybrid_retrieval']})
    pattern.executing = StubAgentTemplate({'answer': 'answer', 'contexts': []})
    pattern.reviewing = ReviewingStub()
    pattern.expressing = StubAgentTemplate({'final_answer': 'clean answer', 'reasons': []})

    result = pattern.invoke(make_input(), {'retry_count': 3, 'eval_threshold': 0.6, 'security_threshold': 0.8})
    rounds = result['result']
    assert len(rounds) == 2, f'expected 2 rounds, got {len(rounds)}'
    assert rounds[1]['reviewing_result']['passed'] is True
    print('test_retry_until_pass OK')


if __name__ == '__main__':
    test_pass_path()
    test_mask_path()
    test_block_path()
    test_retry_until_pass()
    print('All SecureRagWorkPattern unit tests passed.')
