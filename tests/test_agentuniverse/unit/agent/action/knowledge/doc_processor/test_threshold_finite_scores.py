"""Verify score-based filtering through the real processor and documents."""

from decimal import Decimal
import unittest

from agentuniverse.agent.action.knowledge.doc_processor.threshold_filter import ThresholdFilter
from agentuniverse.agent.action.knowledge.store.document import Document


INVALID_SCORES = (float('nan'), float('inf'), float('-inf'),
                  'NaN', 'Infinity', '-Infinity', '1e9999',
                  Decimal('NaN'), Decimal('Infinity'), 10 ** 1000)


class ThresholdFiniteScoresTests(unittest.TestCase):
    def test_topk_does_not_promote_invalid_scores(self):
        for score in INVALID_SCORES:
            with self.subTest(score=repr(score)):
                bad = Document(text='invalid score', metadata={'relevance_score': score})
                good = Document(text='relevant document', metadata={'relevance_score': 0.9})
                processor = ThresholdFilter(
                    filters=[{'type': 'topk', 'k': 1}], preserve_order=False)
                self.assertEqual(processor.process_docs([bad, good]), [good])

    def test_percentile_does_not_promote_invalid_scores(self):
        for score in INVALID_SCORES:
            with self.subTest(score=repr(score)):
                bad = Document(text='invalid score', metadata={'relevance_score': score})
                good = Document(text='relevant document', metadata={'relevance_score': 0.9})
                processor = ThresholdFilter(
                    filters=[{'type': 'percentile', 'percentile': 0.5}], preserve_order=False)
                self.assertEqual(processor.process_docs([bad, good]), [good])

    def test_score_range_uses_configured_fallback(self):
        for score in INVALID_SCORES:
            with self.subTest(score=repr(score)):
                doc = Document(text='use fallback', metadata={'relevance_score': score})
                processor = ThresholdFilter(
                    filters=[{'type': 'score', 'min_score': 0.6, 'max_score': 0.7}],
                    default_score=0.65)
                self.assertEqual(processor.process_docs([doc]), [doc])

    def test_fallback_can_rank_between_finite_scores(self):
        for score in INVALID_SCORES:
            with self.subTest(score=repr(score)):
                bad = Document(text='fallback', metadata={'custom_score': score})
                high = Document(text='high', metadata={'custom_score': '0.9'})
                low = Document(text='low', metadata={'custom_score': 0.2})
                processor = ThresholdFilter(
                    filters=[{'type': 'topk', 'k': 3}], preserve_order=False,
                    score_field='custom_score', default_score=0.5)
                self.assertEqual(processor.process_docs([bad, low, high]), [high, bad, low])

    def test_non_finite_fallback_is_rejected_when_scores_are_used(self):
        for default in (float('nan'), float('inf'), float('-inf')):
            for filter_config in ({'type': 'score'}, {'type': 'topk'},
                                  {'type': 'percentile'}):
                with self.subTest(default=default, filter=filter_config):
                    processor = ThresholdFilter(filters=[filter_config], default_score=default)
                    with self.assertRaisesRegex(ValueError, 'default_score.*finite'):
                        processor.process_docs([Document(text='document')])

    def test_finite_scores_numeric_strings_and_ties_keep_their_order(self):
        docs = [Document(text='negative', metadata={'relevance_score': -2.0}),
                Document(text='zero', metadata={'relevance_score': 0}),
                Document(text='positive string', metadata={'relevance_score': '0.9'}),
                Document(text='positive decimal', metadata={'relevance_score': Decimal('0.9')})]
        processor = ThresholdFilter(filters=[{'type': 'topk'}], preserve_order=False)
        self.assertEqual(processor.process_docs(docs), [docs[2], docs[3], docs[1], docs[0]])

    def test_existing_missing_and_non_numeric_fallback_is_preserved(self):
        docs = [Document(text='missing', metadata={}),
                Document(text='null', metadata={'relevance_score': None}),
                Document(text='text', metadata={'relevance_score': 'not a score'}),
                Document(text='list', metadata={'relevance_score': []})]
        processor = ThresholdFilter(
            filters=[{'type': 'score', 'min_score': 0.2, 'max_score': 0.3}], default_score=0.25)
        self.assertEqual(processor.process_docs(docs), docs)

    def test_input_metadata_and_document_objects_are_preserved(self):
        score = float('nan')
        doc = Document(text='fallback', metadata={'relevance_score': score, 'source': 'fixture'})
        metadata = doc.metadata
        processor = ThresholdFilter(filters=[{'type': 'topk'}])
        result = processor.process_docs([doc])
        self.assertIs(result[0], doc)
        self.assertIs(doc.metadata, metadata)
        self.assertIs(doc.metadata['relevance_score'], score)
        self.assertEqual(doc.metadata['source'], 'fixture')

    def test_preserve_order_restores_input_order_after_selection(self):
        docs = [Document(text='fallback', metadata={'relevance_score': float('nan')}),
                Document(text='low', metadata={'relevance_score': -1}),
                Document(text='high', metadata={'relevance_score': 1})]
        processor = ThresholdFilter(filters=[{'type': 'topk', 'k': 2}])
        self.assertEqual(processor.process_docs(docs), [docs[0], docs[2]])

    def test_score_free_paths_do_not_parse_unused_scores(self):
        doc = Document(text='keep', metadata={'relevance_score': float('nan')})
        for filters in ([], [{'type': 'length', 'min_length': 1}]):
            with self.subTest(filters=filters):
                processor = ThresholdFilter(filters=filters)
                self.assertEqual(processor.process_docs([doc]), [doc])
                self.assertEqual(processor.process_docs([]), [])


if __name__ == '__main__':
    unittest.main()
