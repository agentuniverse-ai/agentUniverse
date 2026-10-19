# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    :
# @Author  :
# @Email   :
# @FileName: test_demo_phase2.py
"""Unit tests for the pure console helpers of the Phase 2 demo.

The demo script is interactive, so only its deterministic formatting helpers
``print_banner`` and ``print_metrics`` are exercised here.
"""

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[5]
                       / 'examples' / 'context_engineering'))

from demo_phase2 import print_banner, print_metrics

BANNER_SEPARATOR = "=" * 80


def _metrics(**overrides):
    metrics = {'session_id': 'demo_session', 'max_tokens': 1000,
               'input_budget': 800, 'total_tokens': 200,
               'available_tokens': 600, 'utilization': 0.25,
               'is_over_budget': False, 'segment_count': 5}
    metrics.update(overrides)
    return metrics


class TestPrintBanner:
    """Test the print_banner demo helper."""

    def test_banner_contains_text(self, capsys):
        print_banner("Demo Title")
        captured = capsys.readouterr().out
        assert "Demo Title" in captured

    def test_banner_has_separator_lines(self, capsys):
        print_banner("Demo Title")
        captured = capsys.readouterr().out
        assert captured.count(BANNER_SEPARATOR) == 2

    def test_banner_accepts_empty_text(self, capsys):
        print_banner("")
        captured = capsys.readouterr().out
        assert captured.count(BANNER_SEPARATOR) == 2


class TestPrintMetrics:
    """Test the print_metrics demo helper."""

    def test_prints_session_and_token_fields(self, capsys):
        print_metrics(_metrics())
        captured = capsys.readouterr().out
        assert "Session: demo_session" in captured
        assert "Max Tokens: 1000" in captured
        assert "Total Tokens: 200" in captured
        assert "Available Tokens: 600" in captured
        assert "Segment Count: 5" in captured

    def test_utilization_is_percentage_formatted(self, capsys):
        print_metrics(_metrics(utilization=0.25))
        captured = capsys.readouterr().out
        assert "Utilization: 25.0%" in captured

    def test_over_budget_true_marks_yes(self, capsys):
        print_metrics(_metrics(is_over_budget=True))
        captured = capsys.readouterr().out
        assert "Over Budget: YES" in captured

    def test_over_budget_false_marks_no(self, capsys):
        print_metrics(_metrics(is_over_budget=False))
        captured = capsys.readouterr().out
        assert "Over Budget: NO" in captured

    def test_missing_key_raises_key_error(self, capsys):
        metrics = _metrics()
        del metrics['session_id']
        with pytest.raises(KeyError):
            print_metrics(metrics)
