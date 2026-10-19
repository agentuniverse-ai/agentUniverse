# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Unit tests for the demo prompt toolkit script."""

import asyncio
import contextlib
import io

from examples.third_party_examples.apps.prompt_toolkit_app.demo_prompt_toolkit import (
    demo_batch_generation,
    demo_export_functionality,
    demo_prompt_generation,
    demo_prompt_optimization,
    demo_quality_analysis,
    demo_scenario_analysis,
    main,
)


def _run(coro):
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        asyncio.run(coro())
    return buffer.getvalue()


class TestDemoPromptToolkit:
    def test_demo_prompt_generation_runs(self):
        output = _run(demo_prompt_generation)
        assert '=== Prompt Generation Demo ===' in output
        assert 'Generated Prompt:' in output
        assert 'Confidence Score:' in output

    def test_demo_prompt_optimization_runs(self):
        output = _run(demo_prompt_optimization)
        assert '=== Prompt Optimization Demo ===' in output
        assert 'Optimized Prompt:' in output

    def test_demo_scenario_analysis_runs(self):
        output = _run(demo_scenario_analysis)
        assert '=== Scenario Analysis Demo ===' in output
        assert 'Recommended Scenario:' in output

    def test_demo_batch_generation_runs(self):
        output = _run(demo_batch_generation)
        assert '=== Batch Generation Demo ===' in output
        assert output.count('Generated Prompt:') >= 3

    def test_demo_quality_analysis_runs(self):
        output = _run(demo_quality_analysis)
        assert '=== Quality Analysis Demo ===' in output
        assert 'Overall Score:' in output

    def test_demo_export_functionality_runs(self):
        output = _run(demo_export_functionality)
        assert '=== Export Functionality Demo ===' in output
        assert 'YAML Configuration:' in output
        assert 'JSON Configuration:' in output

    def test_main_completes_all_demos(self):
        output = _run(main)
        assert 'Demo completed successfully!' in output
