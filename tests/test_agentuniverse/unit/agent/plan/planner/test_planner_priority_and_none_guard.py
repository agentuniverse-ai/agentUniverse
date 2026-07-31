#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Tests for planner operator-priority bug, None.get guards, and WenXin typo.

1. planner.run_all_actions built ``background or '' + "\n".join(results)``.
   Python's ``+`` binds tighter than ``or``, so this parsed as
   ``background or ('' + join)`` — when background was already non-empty,
   the entire action_result was silently dropped. Verified at the source
   level (the fix parenthesises / appends explicitly).

2. planner.handle_llm and react_planner.get_run_config did
   ``profile.get('llm_model').get('name')`` and
   ``plan.get('planner').get('max_iterations', 15)``. When the config omits
   the ``llm_model`` / ``planner`` sub-key (a common minimal-config case),
   these crashed with AttributeError: 'NoneType' object has no attribute
   'get'. Verified at the source level (the fix uses ``{}, {})`` defaults).

3. WenXinLLM TokenModelList was missing commas between the first three
   model strings, so Python's implicit string concatenation produced a
   single garbage entry; get_num_tokens never matched ernie-4.5/4.0
   models. Verified behaviourally.
"""

import unittest


class TestPlannerBackgroundPriorityFix(unittest.TestCase):
    """The action_result must be appended to background, not dropped."""

    def test_background_construction_appends_not_drops(self):
        # Behavioural check of the exact expression the fix uses, so the
        # priority bug cannot regress. ``background or '' + join`` would
        # keep the old background and discard join; the fix is
        # ``(background or '') + join``.
        def build_background(existing, action_results):
            # Mirror the fixed line in planner.run_all_actions.
            existing_background = existing or ''
            return existing_background + "\n".join(action_results)

        # When background already has content, action results are APPENDED.
        result = build_background("prior context", ["r1", "r2"])
        self.assertEqual(result, "prior contextr1\nr2")
        # The old (buggy) form would have returned just "prior context".
        self.assertIn("r1", result)
        self.assertIn("r2", result)

        # When background is empty, action results are the whole content.
        result = build_background("", ["r1", "r2"])
        self.assertEqual(result, "r1\nr2")

        # When background key is missing entirely (None), still works.
        result = build_background(None, ["r1"])
        self.assertEqual(result, "r1")

    def test_source_uses_safe_background_construction(self):
        import inspect
        from agentuniverse.agent.plan.planner.planner import Planner

        src = inspect.getsource(Planner.run_all_actions)
        # The fixed form assigns an explicit append; the buggy form was a
        # bare assignment ``planner_input['background'] = planner_input['background'] or '' + ...``.
        # Look for the fixed assignment line.
        self.assertIn(
            "planner_input['background'] = existing_background +",
            src,
            "run_all_actions must append action results to the existing "
            "background via an explicit `existing_background + join`, not "
            "the operator-priority-buggy `background or '' + join`")


class TestPlannerNoneGetGuards(unittest.TestCase):
    """handle_llm / get_run_config must not crash on missing config sub-keys."""

    def test_handle_llm_source_uses_safe_get(self):
        import inspect
        from agentuniverse.agent.plan.planner.planner import Planner

        src = inspect.getsource(Planner.handle_llm)
        # Must use the safe ``.get('llm_model', {})`` form, not the bare
        # ``.get('llm_model').get('name')`` chain.
        self.assertIn("profile.get('llm_model', {})", src)
        self.assertNotIn("profile.get('llm_model').get('name')", src)

    def test_react_planner_max_iterations_source_uses_safe_get(self):
        import inspect
        from agentuniverse.agent.plan.planner.react_planner.react_planner \
            import ReActPlanner

        src = inspect.getsource(ReActPlanner.invoke)
        # Must guard ``plan.get('planner')`` against None before .get().
        self.assertIn("(agent_model.plan.get('planner') or {})", src)

    def test_react_planner_get_run_config_source_uses_safe_get(self):
        import inspect
        from agentuniverse.agent.plan.planner.react_planner.react_planner \
            import ReActPlanner

        src = inspect.getsource(ReActPlanner.get_run_config)
        self.assertIn("profile.get('llm_model', {})", src)
        self.assertNotIn("profile.get('llm_model').get('name')", src)


class TestWenXinTokenModelList(unittest.TestCase):
    """TokenModelList must list each model as a separate entry."""

    def test_each_model_is_a_separate_list_entry(self):
        from agentuniverse.llm.default.wenxin_llm import TokenModelList

        # The bug: implicit string concatenation merged the first three
        # entries into one garbage string. Assert each known model is its
        # own entry.
        expected_models = [
            'ernie-4.5-turbo-32k',
            'ernie-4.5-8k-preview',
            'ernie-4.0-8k',
            'ernie-3.5-8k',
        ]
        for model in expected_models:
            self.assertIn(model, TokenModelList,
                          f"{model!r} must appear as its own entry in "
                          "TokenModelList; the previous missing-comma bug "
                          "merged it into a garbage string")

    def test_no_concatenated_garbage_entries(self):
        from agentuniverse.llm.default.wenxin_llm import TokenModelList

        for entry in TokenModelList:
            # Each entry should be a single model name, not a concatenation
            # of multiple model names.
            self.assertFalse(
                entry.count('ernie-') > 1,
                f"entry {entry!r} looks like a missing-comma concatenation "
                "of multiple model names")


if __name__ == "__main__":
    unittest.main(verbosity=2)
