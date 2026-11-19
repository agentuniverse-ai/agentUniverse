import asyncio
import unittest

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.work_pattern.secure_rag_work_pattern import SecureRagWorkPattern


class _Stub:

    def __init__(self, *results):
        self.results, self.calls = list(results), 0

    def run(self, **kwargs):
        self.calls += 1
        return OutputObject(self.results[min(self.calls - 1, len(self.results) - 1)])


def _ask(): return InputObject({'input': 'What is the capital of France?'})


def _wired(review, express):
    pattern = SecureRagWorkPattern()
    pattern.planning, pattern.executing = _Stub({'strategy': ['hybrid_retrieval']}), _Stub({'answer': 'Paris', 'contexts': ['ctx']})
    pattern.reviewing, pattern.expressing = review, express
    return pattern


class SecureRagWorkPatternTest(unittest.TestCase):

    def test_reference_semantics(self):
        passed = _wired(_Stub({'passed': True, 'score': 0.95, 'action': 'pass', 'sanitized_answer': 'Paris', 'reasons': []}),
                        _Stub({'final_answer': 'Paris', 'reasons': []}))
        rounds = passed.invoke(_ask(), {'retry_count': 1, 'eval_threshold': 0.6, 'security_threshold': 0.8})['result']
        self.assertEqual(rounds[0]['expressing_result'], {'final_answer': 'Paris', 'reasons': []})
        bare = SecureRagWorkPattern().invoke(_ask(), {})['result'][0]
        self.assertEqual(bare, {'planning_result': {'strategy': ['hybrid_retrieval']}, 'executing_result': {'answer': '', 'contexts': []},
                                'reviewing_result': {'passed': True, 'score': 1.0, 'action': 'pass', 'sanitized_answer': '', 'reasons': []},
                                'expressing_result': {'final_answer': '', 'reasons': []}})
        masked = _wired(_Stub({'passed': False, 'score': 0.3, 'action': 'mask', 'sanitized_answer': 'secret ***', 'reasons': ['sensitive']}),
                        _Stub({'final_answer': 'secret ***', 'reasons': ['sensitive']}))
        rounds = masked.invoke(_ask(), {'retry_count': 1})['result']
        self.assertEqual((rounds[0]['reviewing_result']['action'], rounds[0]['expressing_result']['final_answer'],
                          rounds[0]['expressing_result']['reasons']), ('mask', 'secret ***', ['sensitive']))
        blocked = SecureRagWorkPattern()
        blocked.reviewing = _Stub({'passed': False, 'score': 0.1, 'action': 'block', 'sanitized_answer': '', 'reasons': ['prohibited']})
        self.assertEqual(blocked.invoke(_ask(), {'retry_count': 1})['result'][0]['expressing_result'],
                         {'final_answer': '[内容因安全审查未通过被拦截]', 'reasons': ['prohibited']})
        review = _Stub({'passed': False, 'score': 0.2, 'action': 'mask', 'sanitized_answer': 'v1', 'reasons': ['retry']},
                       {'passed': True, 'score': 0.9, 'action': 'pass', 'sanitized_answer': 'clean', 'reasons': []})
        rounds = _wired(review, _Stub({'final_answer': 'clean', 'reasons': []})).invoke(
            _ask(), {'retry_count': 3, 'eval_threshold': 0.6})['result']
        self.assertEqual((len(rounds), rounds[-1]['reviewing_result']['passed'], review.calls), (2, True, 2))
        planning, executing = _Stub({'strategy': ['x']}), _Stub({'answer': 'kept', 'contexts': []})
        jumped = _wired(_Stub({'passed': True, 'score': 1.0, 'action': 'pass', 'sanitized_answer': 'kept', 'reasons': []}),
                        _Stub({'final_answer': 'kept', 'reasons': []}))
        jumped.planning, jumped.executing = planning, executing
        rounds = jumped.invoke(_ask(), {'retry_count': 2, 'jump_step': 'reviewing'})['result']
        self.assertEqual((len(rounds), planning.calls, executing.calls), (1, 0, 0))
        self.assertEqual((rounds[0]['planning_result'], rounds[0]['executing_result']),
                         ({'strategy': ['hybrid_retrieval']}, {'answer': '', 'contexts': []}))

    def test_bounded_inputs_async_parity_and_set_by_agent_model(self):
        pattern = _wired(_Stub({'passed': True, 'score': 1.0, 'action': 'pass', 'sanitized_answer': 'x', 'reasons': []}),
                         _Stub({'final_answer': 'x', 'reasons': []}))
        cases = [
            ({'retry_count': 0}, "'retry_count' must be an integer from 1 to 10 (got 0)."), ({'retry_count': 11}, "'retry_count' must be an integer from 1 to 10 (got 11)."),
            ({'retry_count': True}, "'retry_count' must be an integer from 1 to 10 (got True)."), ({'eval_threshold': 1.5}, "'eval_threshold' must be a number from 0.0 to 1.0 (got 1.5)."),
            ({'security_threshold': -0.1}, "'security_threshold' must be a number from 0.0 to 1.0 (got -0.1)."),
            ({'jump_step': 'planning2'}, "'jump_step' must be one of planning, executing, reviewing, expressing or None (got 'planning2').")]
        for spec, expected in cases:
            with self.assertRaises(ValueError) as raised:
                pattern.invoke(_ask(), spec)
            self.assertEqual(str(raised.exception), expected)
        with self.assertRaisesRegex(ValueError, r"dict or None \(got \['not', 'a', 'dict'\]\)"):
            pattern.invoke(_ask(), ['not', 'a', 'dict'])
        self.assertEqual(pattern.invoke(_ask(), {'retry_count': 2})['result'],
                         asyncio.run(pattern.async_invoke(_ask(), {'retry_count': 2}))['result'])
        pattern.planning = 42
        with self.assertRaisesRegex(ValueError, r"run\(\) or async_run\(\) \(got 42\)"):
            pattern.invoke(_ask(), {})
        pattern.name = 'bounded-secure-rag'
        agent = pattern.set_by_agent_model(planning=_Stub({'strategy': ['kw']}), executing=_Stub({'answer': 'A', 'contexts': []}))
        self.assertEqual((agent.name, agent.reviewing, agent.expressing), ('bounded-secure-rag', None, None))
        self.assertEqual(agent.invoke(_ask(), {'retry_count': 1})['result'][0]['expressing_result']['final_answer'], 'A')
