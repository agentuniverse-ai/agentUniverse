# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/06
# @FileName: test_temporal_decay_filter.py

import math
import unittest
from datetime import datetime, timedelta, timezone

from agentuniverse.agent.action.knowledge.doc_processor.temporal_decay_filter import TemporalDecayFilter
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer

# Fixed reference instant: 2026-10-01T00:00:00Z.
REFERENCE = datetime(2026, 10, 1, tzinfo=timezone.utc).timestamp()
DAY = 86400.0


def _aged(days: float, **metadata) -> Document:
    """Build a document timestamped `days` before the fixed reference."""
    ts = datetime(2026, 10, 1, tzinfo=timezone.utc) - timedelta(days=days)
    return Document(text=f"doc aged {days}d", metadata={"timestamp": ts, **metadata})


class TestTemporalDecayFilter(unittest.TestCase):
    """Comprehensive test suite for TemporalDecayFilter."""

    def setUp(self):
        self.filter = TemporalDecayFilter()
        self.filter.reference_time = REFERENCE
        self.query = Query(query_str="freshness")

    def _create_configer(self, config_dict):
        """Create a ComponentConfiger from a plain dictionary."""
        cfg = Configer()
        cfg.value = config_dict
        configer = ComponentConfiger()
        configer.load_by_configer(cfg)
        return configer

    # ========== Initialization tests ==========

    def test_default_configuration(self):
        """Defaults: 30-day half-life, 0.1 floor, keep missing, default keys."""
        f = TemporalDecayFilter()
        self.assertEqual(f.timestamp_key, "timestamp")
        self.assertEqual(f.half_life_days, 30.0)
        self.assertEqual(f.min_score, 0.1)
        self.assertIsNone(f.max_age_days)
        self.assertEqual(f.decay_score_key, "decay_score")
        self.assertEqual(f.missing_timestamp, "keep")

    def test_initialize_by_component_configer(self):
        """YAML-provided parameters are applied on initialization."""
        configer = self._create_configer({
            'name': 'temporal_decay_filter',
            'description': 'decay filter',
            'timestamp_key': 'published_at',
            'half_life_days': 7.0,
            'min_score': 0.3,
            'max_age_days': 90.0,
            'decay_score_key': 'freshness',
            'missing_timestamp': 'drop',
        })
        f = TemporalDecayFilter()
        f._initialize_by_component_configer(configer)
        self.assertEqual(f.timestamp_key, "published_at")
        self.assertEqual(f.half_life_days, 7.0)
        self.assertEqual(f.min_score, 0.3)
        self.assertEqual(f.max_age_days, 90.0)
        self.assertEqual(f.decay_score_key, "freshness")
        self.assertEqual(f.missing_timestamp, "drop")
        self.assertEqual(f.name, "temporal_decay_filter")

    def test_invalid_configuration_raises(self):
        """Non-positive half-life, out-of-range min_score, bad policy and
        non-positive max_age_days all fail at initialization time."""
        base = {
            'name': 'f', 'description': 'd',
            'timestamp_key': 'timestamp', 'half_life_days': 30.0,
            'min_score': 0.1, 'max_age_days': None,
            'missing_timestamp': 'keep',
        }
        for key, value in (
            ('half_life_days', 0),
            ('half_life_days', -5),
            ('min_score', 0),
            ('min_score', 1.5),
            ('max_age_days', -1),
            ('missing_timestamp', 'skip'),
            ('timestamp_key', ''),
        ):
            config = dict(base, **{key: value})
            with self.assertRaises(ValueError, msg=key):
                TemporalDecayFilter()._initialize_by_component_configer(
                    self._create_configer(config))

    # ========== Decay math tests ==========

    def test_half_life_score_is_one_half(self):
        """A document exactly one half-life old scores 0.5."""
        f = TemporalDecayFilter()
        f.half_life_days = 30.0
        f.reference_time = REFERENCE
        self.assertAlmostEqual(f._decay_score(30.0), 0.5, places=9)
        self.assertAlmostEqual(f._decay_score(60.0), 0.25, places=9)

    def test_score_formula_matches_exponential_decay(self):
        """score == exp(-ln(2) * age_days / half_life_days)."""
        f = TemporalDecayFilter()
        f.half_life_days = 7.0
        for age in (0.5, 1.0, 3.25, 9.0, 21.0):
            expected = math.exp(-math.log(2) * age / 7.0)
            self.assertAlmostEqual(f._decay_score(age), expected, places=9)

    def test_future_timestamp_scores_one(self):
        """Clock-skewed future timestamps clamp to 1.0, never amplify."""
        docs = [_aged(-2.0)]  # two days in the future
        result = self.filter.process_docs(docs, self.query)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].metadata["decay_score"], 1.0)

    # ========== Filtering behavior tests ==========

    def test_old_documents_below_min_score_are_dropped(self):
        """With a 30-day half-life and 0.25 floor, 30-day-old docs (0.5)
        survive while 70-day-old docs (~0.198) are dropped."""
        self.filter.half_life_days = 30.0
        self.filter.min_score = 0.25
        fresh, old = _aged(30.0), _aged(70.0)
        result = self.filter.process_docs([fresh, old], self.query)
        self.assertEqual([d.text for d in result], ["doc aged 30.0d"])

    def test_max_age_days_hard_cap_overrides_curve(self):
        """A document above min_score but older than max_age_days is dropped."""
        self.filter.half_life_days = 365.0   # slow decay: 100d-old scores ~0.83
        self.filter.min_score = 0.1
        self.filter.max_age_days = 90.0
        result = self.filter.process_docs([_aged(100.0)], self.query)
        self.assertEqual(result, [])

    def test_score_written_to_metadata_key(self):
        """The decay score lands under the configured metadata key."""
        self.filter.decay_score_key = "freshness"
        result = self.filter.process_docs([_aged(30.0)], self.query)
        self.assertAlmostEqual(result[0].metadata["freshness"], 0.5, places=5)

    def test_empty_decay_score_key_skips_stamping(self):
        """An empty decay_score_key leaves metadata untouched."""
        self.filter.decay_score_key = ""
        doc = _aged(1.0)
        result = self.filter.process_docs([doc], self.query)
        self.assertEqual(len(result), 1)
        self.assertNotIn("decay_score", result[0].metadata)
        self.assertNotIn("", result[0].metadata)

    # ========== Timestamp parsing tests ==========

    def test_supported_timestamp_shapes(self):
        """Epoch seconds, epoch millis, ISO strings (Z / offset / naive) and
        datetime objects all resolve to the same instant; date-only strings
        denote that date's UTC midnight."""
        f = self.filter
        f.half_life_days = 30.0
        target = datetime(2026, 9, 16, 12, 0, 0, tzinfo=timezone.utc)
        midnight = datetime(2026, 9, 16, tzinfo=timezone.utc)
        variants = [
            (target, target),                                    # datetime
            (target.timestamp(), target),                        # epoch seconds
            (int(target.timestamp() * 1000), target),            # epoch millis
            ("2026-09-16T12:00:00Z", target),                    # ISO + Z
            ("2026-09-16T12:00:00+00:00", target),               # ISO offset
            ("2026-09-16T12:00:00", target),                     # naive ISO
            ("2026-09-16", midnight),                            # date only
        ]
        docs = [Document(text=f"v{i}", metadata={"timestamp": raw})
                for i, (raw, _) in enumerate(variants)]
        results = f.process_docs(docs, self.query)
        scores = {d.text: d.metadata["decay_score"] for d in results}
        for i, (_, instant) in enumerate(variants):
            expected = f._decay_score((REFERENCE - instant.timestamp()) / DAY)
            self.assertAlmostEqual(scores[f"v{i}"], expected,
                                   places=4, msg=variants[i][0])

    def test_unparsable_timestamp_treated_as_missing(self):
        """Garbage strings and boolean values count as missing timestamps."""
        f = self.filter
        f.missing_timestamp = "drop"
        docs = [
            Document(text="str", metadata={"timestamp": "not-a-date"}),
            Document(text="bool", metadata={"timestamp": True}),
            Document(text="list", metadata={"timestamp": [1, 2]}),
        ]
        self.assertEqual(f.process_docs(docs, self.query), [])

    def test_missing_timestamp_keep_and_drop(self):
        """missing_timestamp policy controls documents with no timestamp,
        including documents with no metadata at all."""
        no_meta = Document(text="no metadata")
        no_key = Document(text="no key", metadata={"other": 1})
        self.assertEqual(
            self.filter.process_docs([no_meta, no_key], self.query),
            [no_meta, no_key])
        self.filter.missing_timestamp = "drop"
        self.assertEqual(
            self.filter.process_docs([no_meta, no_key], self.query), [])

    # ========== Pipeline-shape tests ==========

    def test_order_preserved_and_empty_input(self):
        """Survivors keep their input order; empty input yields empty output."""
        self.assertEqual(self.filter.process_docs([], self.query), [])
        self.filter.min_score = 0.2   # 60d-old scores 0.25, 400d-old ~0.0095
        docs = [_aged(60.0), _aged(1.0), _aged(400.0), _aged(2.0)]
        result = self.filter.process_docs(docs, self.query)
        self.assertEqual([d.text for d in result],
                         ["doc aged 60.0d", "doc aged 1.0d", "doc aged 2.0d"])

    def test_input_metadata_not_mutated_for_dropped_docs(self):
        """Dropped documents never gain a decay score; kept documents get a
        copied metadata dict rather than an in-place shared mutation."""
        dropped = _aged(400.0)
        kept = _aged(0.0)
        original_meta = dict(kept.metadata)
        self.filter.process_docs([dropped, kept], self.query)
        self.assertNotIn("decay_score", dropped.metadata)
        self.assertNotIn("decay_score", original_meta)
        self.assertEqual(kept.metadata["decay_score"], 1.0)


if __name__ == '__main__':
    unittest.main()
