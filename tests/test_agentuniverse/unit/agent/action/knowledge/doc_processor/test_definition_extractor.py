# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20 00:00
# @Author  : AI Assistant
# @FileName: test_definition_extractor.py

import unittest

from agentuniverse.agent.action.knowledge.doc_processor.definition_extractor import DefinitionExtractor
from agentuniverse.agent.action.knowledge.store.document import Document


class _DummyConfiger:
    """Duck-typed stand-in for ComponentConfiger attribute access."""

    def __init__(self, **kwargs):
        self.name = 'definition_extractor'
        self.description = 'test configer'
        for key, value in kwargs.items():
            setattr(self, key, value)


class TestDefinitionExtractor(unittest.TestCase):
    """Offline unit tests for the DefinitionExtractor doc processor."""

    def setUp(self):
        self.extractor = DefinitionExtractor(name='test_definition_extractor')

    def _run(self, text, **kwargs):
        extractor = DefinitionExtractor(name='test', **kwargs) if kwargs else self.extractor
        doc = Document(text=text)
        result = extractor.process_docs([doc])
        return result[0]

    # ---------------------------------------------------------- EN patterns --

    def test_en_is_pattern(self):
        doc = self._run('An agent is a software entity that acts autonomously.')
        defs = doc.metadata['definitions']
        self.assertEqual(len(defs), 1)
        self.assertEqual(defs[0]['term'], 'agent')
        self.assertEqual(defs[0]['definition'], 'a software entity that acts autonomously')
        self.assertEqual(defs[0]['pattern'], 'is')
        self.assertFalse(defs[0]['truncated'])
        self.assertEqual(doc.metadata['definition_count'], 1)

    def test_en_are_pattern(self):
        doc = self._run('Neural networks are computational models inspired by the brain.')
        defs = doc.metadata['definitions']
        self.assertEqual(len(defs), 1)
        self.assertEqual(defs[0]['term'], 'Neural networks')
        self.assertEqual(defs[0]['definition'], 'computational models inspired by the brain')
        self.assertEqual(defs[0]['pattern'], 'are')

    def test_en_means_pattern(self):
        doc = self._run('Entropy means the measure of disorder in a system.')
        defs = doc.metadata['definitions']
        self.assertEqual(len(defs), 1)
        self.assertEqual(defs[0]['term'], 'Entropy')
        self.assertEqual(defs[0]['definition'], 'the measure of disorder in a system')
        self.assertEqual(defs[0]['pattern'], 'means')

    def test_en_refers_to_pattern(self):
        doc = self._run('Machine learning refers to methods that learn from data.')
        defs = doc.metadata['definitions']
        self.assertEqual(len(defs), 1)
        self.assertEqual(defs[0]['term'], 'Machine learning')
        self.assertEqual(defs[0]['definition'], 'methods that learn from data')
        self.assertEqual(defs[0]['pattern'], 'refers_to')

    def test_en_is_defined_as_pattern(self):
        doc = self._run('A prime number is defined as an integer greater than one.')
        defs = doc.metadata['definitions']
        self.assertEqual(len(defs), 1)
        self.assertEqual(defs[0]['term'], 'prime number')
        self.assertEqual(defs[0]['definition'], 'an integer greater than one')
        self.assertEqual(defs[0]['pattern'], 'is_defined_as')

    def test_en_relative_clause_pattern(self):
        doc = self._run('Paris, which is the capital of France, hosts the Olympics.')
        defs = doc.metadata['definitions']
        self.assertEqual(len(defs), 1)
        self.assertEqual(defs[0]['term'], 'Paris')
        self.assertEqual(defs[0]['definition'], 'the capital of France')
        self.assertEqual(defs[0]['pattern'], 'relative_clause')

    def test_en_definition_stops_at_comma(self):
        doc = self._run('A dog is a domestic animal, and it barks loudly.')
        defs = doc.metadata['definitions']
        self.assertEqual(len(defs), 1)
        self.assertEqual(defs[0]['term'], 'dog')
        self.assertEqual(defs[0]['definition'], 'a domestic animal')

    def test_en_multiple_hits_in_one_sentence(self):
        doc = self._run('A vector is a quantity, and a matrix is a rectangular array.')
        defs = doc.metadata['definitions']
        self.assertEqual(len(defs), 2)
        self.assertEqual([d['term'] for d in defs], ['vector', 'matrix'])
        self.assertEqual([d['definition'] for d in defs],
                         ['a quantity', 'a rectangular array'])

    def test_en_capitalized_multi_word_term(self):
        doc = self._run('The World Health Organization is a United Nations agency.')
        defs = doc.metadata['definitions']
        self.assertEqual(len(defs), 1)
        self.assertEqual(defs[0]['term'], 'World Health Organization')

    # ---------------------------------------------------------- ZH patterns --

    def test_zh_is_pattern(self):
        doc = self._run('联邦学习是一种分布式机器学习框架。')
        defs = doc.metadata['definitions']
        self.assertEqual(len(defs), 1)
        self.assertEqual(defs[0]['term'], '联邦学习')
        self.assertEqual(defs[0]['definition'], '一种分布式机器学习框架')
        self.assertEqual(defs[0]['pattern'], 'zh_is')
        self.assertFalse(defs[0]['truncated'])

    def test_zh_shizhi_pattern(self):
        doc = self._run('数据湖是指统一存储原始数据的系统。')
        defs = doc.metadata['definitions']
        self.assertEqual(len(defs), 1)
        self.assertEqual(defs[0]['term'], '数据湖')
        self.assertEqual(defs[0]['definition'], '统一存储原始数据的系统')
        self.assertEqual(defs[0]['pattern'], 'zh_refers_to')

    def test_zh_defined_as_pattern(self):
        doc = self._run('量子计算的定义为利用量子力学原理进行计算的技术。')
        defs = doc.metadata['definitions']
        self.assertEqual(len(defs), 1)
        self.assertEqual(defs[0]['term'], '量子计算')
        self.assertEqual(defs[0]['definition'], '利用量子力学原理进行计算的技术')
        self.assertEqual(defs[0]['pattern'], 'zh_defined_as')

    def test_zh_dingyi_without_de_pattern(self):
        doc = self._run('注意力机制定义为对输入进行加权的方法。')
        defs = doc.metadata['definitions']
        self.assertEqual(len(defs), 1)
        self.assertEqual(defs[0]['term'], '注意力机制')
        self.assertEqual(defs[0]['definition'], '对输入进行加权的方法')
        self.assertEqual(defs[0]['pattern'], 'zh_defined_as')

    def test_zh_suowei_pattern(self):
        doc = self._run('所谓元学习，是指学会如何学习的方法。')
        defs = doc.metadata['definitions']
        self.assertEqual(len(defs), 1)
        self.assertEqual(defs[0]['term'], '元学习')
        self.assertEqual(defs[0]['definition'], '学会如何学习的方法')
        self.assertEqual(defs[0]['pattern'], 'zh_suowei')

    def test_zh_mixed_alnum_term(self):
        doc = self._run('CPU使用率是衡量系统负载的重要指标。')
        defs = doc.metadata['definitions']
        self.assertEqual(len(defs), 1)
        self.assertEqual(defs[0]['term'], 'CPU使用率')
        self.assertEqual(defs[0]['definition'], '衡量系统负载的重要指标')

    def test_zh_definition_stops_at_comma(self):
        doc = self._run('向量数据库是专门存储向量的数据库，支持相似度检索。')
        defs = doc.metadata['definitions']
        self.assertEqual(len(defs), 1)
        self.assertEqual(defs[0]['definition'], '专门存储向量的数据库')

    # --------------------------------------------------------------- guards --

    def test_pronoun_terms_rejected_en(self):
        for text in ('It is a powerful tool.', 'They are useful gadgets.',
                     'This is a test sentence.'):
            doc = self._run(text)
            self.assertEqual(doc.metadata['definitions'], [], text)

    def test_pronoun_terms_rejected_zh(self):
        for text in ('这是测试句子。', '它是一种工具。'):
            doc = self._run(text)
            self.assertEqual(doc.metadata['definitions'], [], text)

    def test_there_is_here_is_not_definitions(self):
        for text in ('There is a book on the table.', 'Here is the summary.'):
            doc = self._run(text)
            self.assertEqual(doc.metadata['definitions'], [], text)

    def test_questions_excluded(self):
        text = 'What is a photon? A photon is a particle of light.'
        doc = self._run(text)
        defs = doc.metadata['definitions']
        self.assertEqual(len(defs), 1)
        self.assertEqual(defs[0]['term'], 'photon')
        self.assertEqual(defs[0]['definition'], 'a particle of light')

    def test_zh_question_excluded(self):
        doc = self._run('什么是向量数据库？')
        self.assertEqual(doc.metadata['definitions'], [])

    def test_single_stopword_term_rejected_en(self):
        doc = self._run('Often is an adverb.')
        self.assertEqual(doc.metadata['definitions'], [])

    def test_single_stopchar_term_rejected_zh(self):
        # 还 is isolated by a comma before the copula 是, so the term
        # candidate is the single stopword character 还.
        doc = self._run('总体来说，还是很高的。')
        self.assertEqual(doc.metadata['definitions'], [])

    def test_cjk_term_longer_than_12_chars_rejected(self):
        # A 20-character run before the copula is not a glossary term.
        doc = self._run('先进的高性能分布式云计算基础架构设施平台是未来趋势。')
        self.assertEqual(doc.metadata['definitions'], [])

    def test_empty_text(self):
        doc = self._run('')
        self.assertEqual(doc.metadata['definitions'], [])
        self.assertEqual(doc.metadata['definition_count'], 0)

    def test_whitespace_only_text(self):
        doc = self._run('   \n\t  ')
        self.assertEqual(doc.metadata['definitions'], [])

    def test_empty_document_list(self):
        self.assertEqual(self.extractor.process_docs([]), [])

    # ----------------------------------------------- truncation / cap / dedup --

    def test_definition_truncated_flag(self):
        long_def = 'q' * 250
        doc = self._run(f'Filibuster is {long_def}.')
        defs = doc.metadata['definitions']
        self.assertEqual(len(defs), 1)
        self.assertEqual(defs[0]['term'], 'Filibuster')
        self.assertTrue(defs[0]['truncated'])
        self.assertEqual(len(defs[0]['definition']), 200)

    def test_definition_exactly_at_limit_not_truncated(self):
        doc = self._run('Term is ' + 'q' * 200 + '.')
        defs = doc.metadata['definitions']
        self.assertEqual(len(defs), 1)
        self.assertFalse(defs[0]['truncated'])
        self.assertEqual(len(defs[0]['definition']), 200)

    def test_dedup_first_wins_and_repeats_counted(self):
        text = ('A vector is a quantity with direction. '
                'The vector is also a matrix element.')
        doc = self._run(text)
        defs = doc.metadata['definitions']
        self.assertEqual(len(defs), 1)
        self.assertEqual(defs[0]['definition'], 'a quantity with direction')
        self.assertEqual(doc.metadata['definition_repeats'], {'vector': 1})

    def test_dedup_case_insensitive(self):
        text = 'Entropy is a measure of disorder. entropy is central to physics.'
        doc = self._run(text)
        defs = doc.metadata['definitions']
        self.assertEqual(len(defs), 1)
        self.assertEqual(defs[0]['term'], 'Entropy')
        self.assertEqual(doc.metadata['definition_repeats'], {'entropy': 1})

    def test_dedup_disabled_keeps_repeats(self):
        text = 'A vector is a quantity. A vector is a matrix element.'
        doc = self._run(text, dedup_by_term=False)
        defs = doc.metadata['definitions']
        self.assertEqual(len(defs), 2)
        self.assertNotIn('definition_repeats', doc.metadata)

    def test_definitions_capped_at_50(self):
        text = ' '.join(f'Term{i} is a concept number {i}.' for i in range(55))
        doc = self._run(text)
        defs = doc.metadata['definitions']
        self.assertEqual(len(defs), 50)
        self.assertEqual(doc.metadata['definition_count'], 50)
        self.assertEqual(defs[0]['term'], 'Term0')
        self.assertEqual(defs[-1]['term'], 'Term49')

    def test_custom_cap_via_config(self):
        text = 'A is one. B is two. C is three.'
        doc = self._run(text, max_definitions=2)
        self.assertEqual(len(doc.metadata['definitions']), 2)
        self.assertEqual(doc.metadata['definition_count'], 2)

    # ------------------------------------------------------------- metadata --

    def test_no_definitions_passthrough(self):
        text = 'The quick brown fox jumps over the lazy dog.'
        original_text = text
        doc = self._run(text)
        self.assertEqual(doc.metadata['definitions'], [])
        self.assertEqual(doc.metadata['definition_count'], 0)
        self.assertEqual(doc.metadata['definition_repeats'], {})
        self.assertEqual(doc.text, original_text)

    def test_existing_metadata_preserved(self):
        doc = Document(text='An agent is a software entity.', metadata={'source': 'handbook'})
        result = self.extractor.process_docs([doc])
        self.assertEqual(result[0].metadata['source'], 'handbook')
        self.assertEqual(len(result[0].metadata['definitions']), 1)

    def test_multiple_documents_processed_independently(self):
        docs = [Document(text='A cat is a small pet.'), Document(text='No definitions here.')]
        result = self.extractor.process_docs(docs)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].metadata['definition_count'], 1)
        self.assertEqual(result[1].metadata['definition_count'], 0)

    def test_span_offsets_en(self):
        text = 'An agent is a tool.'
        # term starts at 3 ('agent'), definition ends before '.' at 18
        doc = self._run(text)
        self.assertEqual(doc.metadata['definitions'][0]['span'], [3, 18])

    def test_span_offsets_zh(self):
        text = '联邦学习是一种分布式机器学习框架。'
        doc = self._run(text)
        self.assertEqual(doc.metadata['definitions'][0]['span'], [0, 16])

    def test_span_offsets_multisentence(self):
        text = 'First sentence here. Entropy is a measure of disorder.'
        doc = self._run(text)
        defs = doc.metadata['definitions']
        self.assertEqual(len(defs), 1)
        term_start = text.index('Entropy')
        self.assertEqual(defs[0]['span'][0], term_start)
        self.assertEqual(text[defs[0]['span'][0]:defs[0]['span'][1]],
                         'Entropy is a measure of disorder')

    def test_mixed_language_document(self):
        text = ('Machine learning refers to methods that learn from data. '
                '联邦学习是一种分布式机器学习框架。')
        doc = self._run(text)
        defs = doc.metadata['definitions']
        self.assertEqual(len(defs), 2)
        self.assertEqual([d['pattern'] for d in defs], ['refers_to', 'zh_is'])
        self.assertEqual([d['span'][0] for d in defs],
                         sorted(d['span'][0] for d in defs))

    def test_determinism(self):
        text = ('A vector is a quantity. 联邦学习是一种分布式机器学习框架。 '
                'Entropy means the measure of disorder.')
        doc1 = self._run(text)
        doc2 = self._run(text)
        self.assertEqual(doc1.metadata['definitions'], doc2.metadata['definitions'])
        self.assertEqual(doc1.metadata['definition_count'],
                         doc2.metadata['definition_count'])
        self.assertEqual(doc1.metadata['definition_repeats'],
                         doc2.metadata['definition_repeats'])

    # ---------------------------------------------------- config validation --

    def test_invalid_max_definitions_rejected(self):
        with self.assertRaises(ValueError):
            self._run('A cat is a pet.', max_definitions=0)

    def test_invalid_max_definition_length_rejected(self):
        with self.assertRaises(ValueError):
            self._run('A cat is a pet.', max_definition_length=0)

    def test_invalid_max_term_words_rejected(self):
        with self.assertRaises(ValueError):
            self._run('A cat is a pet.', max_term_words=0)

    def test_invalid_dedup_by_term_type_rejected(self):
        # 'maybe' is neither a valid bool nor accepted by _validate_params,
        # so construction/validation raises (pydantic ValidationError is a
        # ValueError subclass).
        with self.assertRaises(ValueError):
            self._run('A cat is a pet.', dedup_by_term='maybe')

    def test_initialize_by_component_configer(self):
        configer = _DummyConfiger(max_definitions=5, max_definition_length=50,
                                  max_term_words=2, dedup_by_term=False)
        extractor = DefinitionExtractor(name='from_configer')
        extractor._initialize_by_component_configer(configer)
        self.assertEqual(extractor.max_definitions, 5)
        self.assertEqual(extractor.max_definition_length, 50)
        self.assertEqual(extractor.max_term_words, 2)
        self.assertFalse(extractor.dedup_by_term)
        self.assertEqual(extractor.name, 'definition_extractor')

    def test_initialize_by_component_configer_invalid(self):
        configer = _DummyConfiger(max_definitions=0)
        extractor = DefinitionExtractor(name='from_configer')
        with self.assertRaises(ValueError):
            extractor._initialize_by_component_configer(configer)

    def test_max_term_words_limits_term(self):
        doc = self._run('The very large language model family is a group.', max_term_words=2)
        defs = doc.metadata['definitions']
        self.assertEqual(len(defs), 1)
        self.assertEqual(defs[0]['term'].split(), ['model', 'family'])


if __name__ == '__main__':
    unittest.main()
