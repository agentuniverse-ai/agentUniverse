#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_token_estimator_tool.py

"""Offline unit tests for TokenEstimatorTool.

The tool never touches the network, and neither do these tests. Both
counting methods are exercised deterministically:

* the heuristic path is forced by patching the module-level encoder
  cache to ``{"encoder": None}`` (the same state a real
  tiktoken-unavailable environment produces) and asserted against the
  pinned formulas ``floor(cjk_chars * 1.5 + 0.5) +
  ceil(non_cjk_chars / 4)``;
* the tiktoken path is exercised with a stub encoder (tokens ==
  whitespace word count) for offline arithmetic, and additionally
  against the real ``cl100k_base`` encoding when tiktoken is
  importable and the encoding loads (skipped otherwise).

The per-message chat overhead arithmetic (4 framing + 2 role primer =
6 per message, the OpenAI cookbook approximation) is hand-verified
below, and the cost math is checked against hand-computed USD values
at both table and custom prices.
"""

import unittest
from unittest import mock

from agentuniverse.agent.action.tool.common_tool import TokenEstimatorTool
from agentuniverse.agent.action.tool.common_tool import (
    token_estimator_tool as token_estimator_module,
)
from agentuniverse.agent.action.tool.common_tool.token_estimator_tool import (
    TokenEstimatorTool as DirectTokenEstimatorTool,
)

OVERHEAD_PER_MESSAGE = 6  # 4 message framing + 2 role primer


class _FakeEncoder:
    """Deterministic stand-in for a tiktoken encoding.

    Encodes any text to exactly one token per whitespace-separated
    word (zero for the empty string) — a rule that is obviously
    different from both the real BPE counts and the character
    heuristic, so tests can tell exactly which path produced a number.
    """

    def encode(self, text: str) -> list[str]:
        return ["x"] * len(text.split())


def _real_encoder_or_none():
    """Try to load the real cl100k_base encoder without poisoning the
    module cache (returns None when tiktoken is unavailable)."""
    saved = dict(token_estimator_module._ENCODER_CACHE)
    try:
        return token_estimator_module._load_encoder()
    finally:
        token_estimator_module._ENCODER_CACHE.clear()
        token_estimator_module._ENCODER_CACHE.update(saved)


class TokenEstimatorToolTest(unittest.TestCase):
    """Offline deterministic test cases for TokenEstimatorTool."""

    def setUp(self) -> None:
        self.tool = TokenEstimatorTool()

    # ------------------------------------------------------------------ #
    # Helpers: force a counting method for the duration of one test
    # ------------------------------------------------------------------ #

    def force_heuristic(self) -> None:
        patcher = mock.patch.dict(
            token_estimator_module._ENCODER_CACHE, {"encoder": None}
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    def force_stub_encoder(self) -> None:
        patcher = mock.patch.dict(
            token_estimator_module._ENCODER_CACHE,
            {"encoder": _FakeEncoder()},
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    # ------------------------------------------------------------------ #
    # estimate mode — heuristic path (forced, formula pins)
    # ------------------------------------------------------------------ #

    def test_heuristic_ascii_formula_pins(self) -> None:
        self.force_heuristic()
        # ceil(chars / 4) for non-CJK text, pinned on the boundaries.
        for text, tokens in (
            ("", 0),
            ("a", 1),
            ("a" * 4, 1),
            ("a" * 7, 2),
            ("a" * 8, 2),
            ("a" * 9, 3),
            ("hello world", 3),  # 11 chars -> ceil(11 / 4) = 3
        ):
            with self.subTest(text=text[:16], n=len(text)):
                result = self.tool.execute(mode="estimate", text=text)
                self.assertEqual(result["method_used"], "heuristic")
                self.assertEqual(result["tokens"], tokens)
                self.assertEqual(result["chars"], len(text))
                self.assertEqual(result["words"], len(text.split()))
                self.assertNotIn("encoding", result)

    def test_heuristic_ascii_breakdown_fields(self) -> None:
        self.force_heuristic()
        result = self.tool.execute(mode="estimate", text="hello world")
        self.assertEqual(
            result,
            {
                "mode": "estimate",
                "tokens": 3,
                "chars": 11,
                "words": 2,
                "method_used": "heuristic",
                "cjk_chars": 0,
                "non_cjk_chars": 11,
                "cjk_tokens": 0,
                "non_cjk_tokens": 3,
            },
        )

    def test_heuristic_cjk_formula_pins(self) -> None:
        self.force_heuristic()
        # floor(cjk_chars * 1.5 + 0.5) with the rounding pinned.
        for text, cjk_chars, cjk_tokens in (
            ("中", 1, 2),        # floor(1.5 + 0.5) = 2
            ("世界", 2, 3),      # floor(3.0 + 0.5) = 3
            ("你好世界", 4, 6),   # floor(6.0 + 0.5) = 6
            ("한국어", 3, 5),     # hangul syllables are CJK: floor(4.5 + 0.5) = 5
            ("こんにちは", 5, 8),  # hiragana is CJK: floor(7.5 + 0.5) = 8
        ):
            with self.subTest(text=text):
                result = self.tool.execute(mode="estimate", text=text)
                self.assertEqual(result["method_used"], "heuristic")
                self.assertEqual(result["cjk_chars"], cjk_chars)
                self.assertEqual(result["non_cjk_chars"], 0)
                self.assertEqual(result["cjk_tokens"], cjk_tokens)
                self.assertEqual(result["non_cjk_tokens"], 0)
                self.assertEqual(result["tokens"], cjk_tokens)

    def test_heuristic_cjk_punctuation_and_fullwidth_are_cjk(self) -> None:
        self.force_heuristic()
        # U+3002 ideographic full stop (CJK symbols block) and U+FF01
        # fullwidth exclamation mark (fullwidth forms block).
        result = self.tool.execute(mode="estimate", text="。！")
        self.assertEqual(result["cjk_chars"], 2)
        self.assertEqual(result["non_cjk_chars"], 0)
        self.assertEqual(result["tokens"], 3)  # floor(2 * 1.5 + 0.5)

    def test_heuristic_mixed_text_combines_both_formulas(self) -> None:
        self.force_heuristic()
        # 6 non-CJK chars -> ceil(6 / 4) = 2; 2 CJK chars -> 3; total 5.
        result = self.tool.execute(mode="estimate", text="hello 世界")
        self.assertEqual(
            result,
            {
                "mode": "estimate",
                "tokens": 5,
                "chars": 8,
                "words": 2,
                "method_used": "heuristic",
                "cjk_chars": 2,
                "non_cjk_chars": 6,
                "cjk_tokens": 3,
                "non_cjk_tokens": 2,
            },
        )

    def test_heuristic_empty_text_is_zero(self) -> None:
        self.force_heuristic()
        result = self.tool.execute(mode="estimate", text="")
        self.assertEqual(result["tokens"], 0)
        self.assertEqual(result["chars"], 0)
        self.assertEqual(result["words"], 0)
        self.assertEqual(result["method_used"], "heuristic")

    # ------------------------------------------------------------------ #
    # estimate mode — tiktoken path (stub, then real when available)
    # ------------------------------------------------------------------ #

    def test_stub_tiktoken_reports_method_and_encoding(self) -> None:
        self.force_stub_encoder()
        result = self.tool.execute(mode="estimate", text="hello world")
        self.assertEqual(result["method_used"], "tiktoken")
        self.assertEqual(result["encoding"], "cl100k_base")
        # The stub counts whitespace words: "hello world" -> 2.
        self.assertEqual(result["tokens"], 2)
        self.assertEqual(result["chars"], 11)
        self.assertEqual(result["words"], 2)
        # No heuristic breakdown fields on the tiktoken path.
        self.assertNotIn("cjk_chars", result)

    def test_stub_tiktoken_empty_text_is_zero(self) -> None:
        self.force_stub_encoder()
        result = self.tool.execute(mode="estimate", text="")
        self.assertEqual(result["tokens"], 0)
        self.assertEqual(result["method_used"], "tiktoken")

    def test_real_tiktoken_known_counts(self) -> None:
        encoder = _real_encoder_or_none()
        if encoder is None:
            self.skipTest("tiktoken / cl100k_base not available")
        with mock.patch.dict(
            token_estimator_module._ENCODER_CACHE, {"encoder": encoder}
        ):
            for text, tokens in (
                ("hello", 1),
                ("hello world", 2),
                ("世界", 3),
                ("hello 世界", 5),
                ("", 0),
            ):
                with self.subTest(text=text):
                    result = self.tool.execute(mode="estimate", text=text)
                    self.assertEqual(result["method_used"], "tiktoken")
                    self.assertEqual(result["encoding"], "cl100k_base")
                    self.assertEqual(result["tokens"], tokens)

    def test_estimate_matches_encoder_encode_directly(self) -> None:
        encoder = _real_encoder_or_none()
        if encoder is None:
            self.skipTest("tiktoken / cl100k_base not available")
        text = "The quick brown fox jumps over the lazy dog."
        with mock.patch.dict(
            token_estimator_module._ENCODER_CACHE, {"encoder": encoder}
        ):
            result = self.tool.execute(mode="estimate", text=text)
        self.assertEqual(result["tokens"], len(encoder.encode(text)))
        self.assertEqual(result["chars"], len(text))
        self.assertEqual(result["words"], 9)

    # ------------------------------------------------------------------ #
    # estimate_chat mode — hand-verified overhead arithmetic
    # ------------------------------------------------------------------ #

    def test_chat_heuristic_overhead_arithmetic(self) -> None:
        self.force_heuristic()
        # "You are helpful." = 16 non-CJK chars -> ceil(16/4) = 4 tokens.
        # "hello world"     = 11 non-CJK chars -> ceil(11/4) = 3 tokens.
        # Per message: content + 4 framing + 2 role primer = content + 6.
        messages = [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "hello world"},
        ]
        result = self.tool.execute(mode="estimate_chat", messages=messages)
        self.assertEqual(result["mode"], "estimate_chat")
        self.assertEqual(result["method_used"], "heuristic")
        self.assertNotIn("encoding", result)
        self.assertEqual(result["message_count"], 2)
        self.assertEqual(result["overhead_tokens_per_message"], 6)
        self.assertEqual(
            result["messages"],
            [
                {
                    "role": "system",
                    "content_tokens": 4,
                    "overhead_tokens": 6,
                    "total_tokens": 10,
                },
                {
                    "role": "user",
                    "content_tokens": 3,
                    "overhead_tokens": 6,
                    "total_tokens": 9,
                },
            ],
        )
        # 4 + 3 content tokens, 2 * 6 overhead, 19 in total.
        self.assertEqual(result["total_content_tokens"], 7)
        self.assertEqual(result["total_overhead_tokens"], 12)
        self.assertEqual(result["total_tokens"], 19)
        self.assertEqual(result["total_chars"], 16 + 11)

    def test_chat_stub_tiktoken_overhead_arithmetic(self) -> None:
        self.force_stub_encoder()
        messages = [
            {"role": "user", "content": "hello world"},  # stub: 2 tokens
            {"role": "assistant", "content": "hi there"},  # stub: 2 tokens
            {"role": "user", "content": "one two three four"},  # 4 tokens
        ]
        result = self.tool.execute(mode="estimate_chat", messages=messages)
        self.assertEqual(result["method_used"], "tiktoken")
        self.assertEqual(result["encoding"], "cl100k_base")
        self.assertEqual(
            [m["total_tokens"] for m in result["messages"]],
            [8, 8, 10],  # 2 + 6, 2 + 6, 4 + 6
        )
        self.assertEqual(result["total_content_tokens"], 8)
        self.assertEqual(result["total_overhead_tokens"], 18)
        self.assertEqual(result["total_tokens"], 26)

    def test_chat_empty_content_still_pays_overhead(self) -> None:
        self.force_heuristic()
        result = self.tool.execute(
            mode="estimate_chat",
            messages=[{"role": "user", "content": ""}],
        )
        self.assertEqual(
            result["messages"],
            [
                {
                    "role": "user",
                    "content_tokens": 0,
                    "overhead_tokens": 6,
                    "total_tokens": 6,
                }
            ],
        )
        self.assertEqual(result["total_tokens"], 6)
        self.assertEqual(result["total_chars"], 0)

    def test_chat_all_roles_accepted(self) -> None:
        self.force_heuristic()
        messages = [
            {"role": role, "content": "a"} for role in self.tool.ROLES
        ]
        result = self.tool.execute(mode="estimate_chat", messages=messages)
        self.assertEqual(result["message_count"], len(self.tool.ROLES))
        # "a" -> ceil(1/4) = 1 content token, + 6 overhead each.
        self.assertEqual(result["total_tokens"], 7 * len(self.tool.ROLES))

    def test_chat_real_tiktoken_known_counts(self) -> None:
        encoder = _real_encoder_or_none()
        if encoder is None:
            self.skipTest("tiktoken / cl100k_base not available")
        with mock.patch.dict(
            token_estimator_module._ENCODER_CACHE, {"encoder": encoder}
        ):
            result = self.tool.execute(
                mode="estimate_chat",
                messages=[{"role": "user", "content": "hello world"}],
            )
        # cl100k_base encodes "hello world" to 2 tokens; + 6 overhead.
        self.assertEqual(result["method_used"], "tiktoken")
        self.assertEqual(result["total_content_tokens"], 2)
        self.assertEqual(result["total_overhead_tokens"], 6)
        self.assertEqual(result["total_tokens"], 8)

    # ------------------------------------------------------------------ #
    # cost mode — table prices (hand-computed USD values)
    # ------------------------------------------------------------------ #

    def test_cost_gpt4o_input_only(self) -> None:
        result = self.tool.execute(
            mode="cost", model="gpt-4o", input_tokens=1_000_000
        )
        self.assertEqual(
            result,
            {
                "mode": "cost",
                "model": "gpt-4o",
                "price_source": "table",
                "currency": "USD",
                "input_tokens": 1_000_000,
                "output_tokens": 0,
                "input_price_per_m": 2.5,
                "output_price_per_m": 10.0,
                "input_cost_usd": 2.5,
                "output_cost_usd": 0.0,
                "total_cost_usd": 2.5,
            },
        )

    def test_cost_gpt4o_input_output_split(self) -> None:
        result = self.tool.execute(
            mode="cost",
            model="gpt-4o",
            input_tokens=500_000,
            output_tokens=250_000,
        )
        self.assertEqual(result["input_cost_usd"], 1.25)
        self.assertEqual(result["output_cost_usd"], 2.5)
        self.assertEqual(result["total_cost_usd"], 3.75)

    def test_cost_table_values_hand_computed(self) -> None:
        cases = [
            ("gpt-4o", 1_000_000, 0, 2.5, 0.0, 2.5),
            ("gpt-4o-mini", 2_000_000, 1_000_000, 0.3, 0.6, 0.9),
            ("claude-sonnet", 200_000, 100_000, 0.6, 1.5, 2.1),
            ("gemini-flash", 1_000_000, 1_000_000, 0.075, 0.3, 0.375),
            ("deepseek-chat", 1_000_000, 1_000_000, 0.14, 0.28, 0.42),
            ("gpt-3.5-turbo", 3_000_000, 1_000_000, 1.5, 1.5, 3.0),
            ("claude-opus", 1_000_000, 1_000_000, 15.0, 75.0, 90.0),
            ("gemini-pro", 1_000_000, 500_000, 1.25, 2.5, 3.75),
            ("deepseek-reasoner", 1_000_000, 1_000_000, 0.55, 2.19, 2.74),
            ("o3", 1_000_000, 1_000_000, 2.0, 8.0, 10.0),
            ("o4-mini", 1_000_000, 1_000_000, 1.1, 4.4, 5.5),
            ("gpt-4-turbo", 500_000, 500_000, 5.0, 15.0, 20.0),
            ("claude-haiku", 1_000_000, 500_000, 0.8, 2.0, 2.8),
        ]
        for model, in_tok, out_tok, in_cost, out_cost, total in cases:
            with self.subTest(model=model):
                result = self.tool.execute(
                    mode="cost",
                    model=model,
                    input_tokens=in_tok,
                    output_tokens=out_tok,
                )
                self.assertEqual(result["model"], model)
                self.assertEqual(result["price_source"], "table")
                self.assertEqual(result["input_cost_usd"], in_cost)
                self.assertEqual(result["output_cost_usd"], out_cost)
                self.assertEqual(result["total_cost_usd"], total)

    def test_cost_table_covers_twelve_plus_models(self) -> None:
        self.assertGreaterEqual(len(TokenEstimatorTool.PRICE_TABLE), 12)
        for model, (price_in, price_out) in TokenEstimatorTool.PRICE_TABLE.items():
            with self.subTest(model=model):
                self.assertGreater(float(price_in), 0.0)
                self.assertGreater(float(price_out), 0.0)
                self.assertGreaterEqual(float(price_out), float(price_in))

    def test_cost_model_lookup_case_insensitive(self) -> None:
        lower = self.tool.execute(
            mode="cost", model="gpt-4o", input_tokens=1_000_000
        )
        upper = self.tool.execute(
            mode="cost", model="GPT-4O", input_tokens=1_000_000
        )
        self.assertEqual(lower["total_cost_usd"], 2.5)
        self.assertEqual(upper["total_cost_usd"], 2.5)
        self.assertEqual(upper["model"], "gpt-4o")

    def test_cost_output_only(self) -> None:
        result = self.tool.execute(
            mode="cost", model="gpt-4o-mini", output_tokens=1_000_000
        )
        self.assertEqual(result["input_tokens"], 0)
        self.assertEqual(result["input_cost_usd"], 0.0)
        self.assertEqual(result["output_cost_usd"], 0.6)
        self.assertEqual(result["total_cost_usd"], 0.6)

    def test_cost_single_token_precision(self) -> None:
        result = self.tool.execute(
            mode="cost", model="gemini-flash", input_tokens=1
        )
        self.assertEqual(result["input_cost_usd"], 7.5e-08)
        self.assertEqual(result["total_cost_usd"], 7.5e-08)

    def test_cost_zero_tokens(self) -> None:
        result = self.tool.execute(
            mode="cost", model="gpt-4o", input_tokens=0, output_tokens=0
        )
        self.assertEqual(result["total_cost_usd"], 0.0)

    # ------------------------------------------------------------------ #
    # cost mode — custom prices
    # ------------------------------------------------------------------ #

    def test_cost_custom_prices(self) -> None:
        result = self.tool.execute(
            mode="cost",
            input_tokens=100_000,
            output_tokens=50_000,
            input_price_per_m=3,
            output_price_per_m=15,
        )
        self.assertEqual(
            result,
            {
                "mode": "cost",
                "model": "custom",
                "price_source": "custom",
                "currency": "USD",
                "input_tokens": 100_000,
                "output_tokens": 50_000,
                "input_price_per_m": 3.0,
                "output_price_per_m": 15.0,
                "input_cost_usd": 0.3,
                "output_cost_usd": 0.75,
                "total_cost_usd": 1.05,
            },
        )

    def test_cost_custom_float_prices(self) -> None:
        result = self.tool.execute(
            mode="cost",
            input_tokens=2_000_000,
            input_price_per_m=0.15,
            output_price_per_m=0.6,
        )
        self.assertEqual(result["input_cost_usd"], 0.3)
        self.assertEqual(result["output_cost_usd"], 0.0)
        self.assertEqual(result["total_cost_usd"], 0.3)

    def test_cost_custom_zero_price_allowed(self) -> None:
        result = self.tool.execute(
            mode="cost",
            input_tokens=1_000_000,
            input_price_per_m=0,
            output_price_per_m=0,
        )
        self.assertEqual(result["total_cost_usd"], 0.0)

    # ------------------------------------------------------------------ #
    # Invalid inputs raise ValueError (strict validation)
    # ------------------------------------------------------------------ #

    def assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def test_invalid_mode(self) -> None:
        self.assert_invalid(mode="count", text="hello")
        self.assert_invalid(mode=None, text="hello")
        self.assert_invalid(mode=123)

    def test_invalid_estimate_text(self) -> None:
        for bad in (None, 123, True, b"hello", ["hello"]):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="estimate", text=bad)
        self.assert_invalid(mode="estimate")  # text is required
        self.assert_invalid(mode="estimate", text="a" * 100_001)

    def test_invalid_messages_container(self) -> None:
        for bad in (None, "user", 123, True, {"role": "user", "content": "x"}):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="estimate_chat", messages=bad)
        self.assert_invalid(mode="estimate_chat")  # messages required
        self.assert_invalid(mode="estimate_chat", messages=[])

    def test_invalid_message_shape(self) -> None:
        base = {"role": "user", "content": "hi"}
        bad_messages = [
            ["hello"],  # not a dict
            [123],
            [{"role": "user"}],  # missing content
            [{"content": "hi"}],  # missing role
            [{"role": "user", "content": "hi", "name": "n"}],  # extra key
            [dict(base, role="bot")],  # role not whitelisted
            [dict(base, role="USER")],  # roles are exact, not case-folded
            [dict(base, role=None)],
            [dict(base, role=123)],
            [dict(base, content=None)],
            [dict(base, content=123)],
            [dict(base, content=True)],
            [dict(base, content=["hi"])],
        ]
        for messages in bad_messages:
            with self.subTest(messages=messages):
                self.assert_invalid(mode="estimate_chat", messages=messages)

    def test_invalid_message_limits(self) -> None:
        oversized = [{"role": "user", "content": "a" * 100_001}]
        self.assert_invalid(mode="estimate_chat", messages=oversized)
        too_many = [
            {"role": "user", "content": "a"} for _ in range(201)
        ]
        self.assert_invalid(mode="estimate_chat", messages=too_many)
        # Exactly at the limits is fine.
        ok = self.tool.execute(
            mode="estimate_chat",
            messages=[{"role": "user", "content": "a" * 100_000}],
        )
        self.assertEqual(ok["message_count"], 1)

    def test_invalid_cost_missing_tokens(self) -> None:
        self.assert_invalid(mode="cost", model="gpt-4o")
        self.assert_invalid(
            mode="cost", input_price_per_m=3, output_price_per_m=15
        )

    def test_invalid_cost_token_counts(self) -> None:
        for bad in (-1, 1.5, True, "100", 100_000_000_001):
            with self.subTest(bad=bad):
                self.assert_invalid(
                    mode="cost", model="gpt-4o", input_tokens=bad
                )
                self.assert_invalid(
                    mode="cost", model="gpt-4o", output_tokens=bad
                )

    def test_invalid_cost_model(self) -> None:
        self.assert_invalid(mode="cost", model="gpt-5-turbo", input_tokens=1)
        self.assert_invalid(mode="cost", model="", input_tokens=1)
        self.assert_invalid(mode="cost", model=123, input_tokens=1)
        self.assert_invalid(mode="cost", model=True, input_tokens=1)

    def test_invalid_cost_model_and_custom_prices_exclusive(self) -> None:
        self.assert_invalid(
            mode="cost",
            model="gpt-4o",
            input_tokens=1,
            input_price_per_m=3,
            output_price_per_m=15,
        )

    def test_invalid_cost_custom_prices(self) -> None:
        # Half-given custom pricing is ambiguous.
        self.assert_invalid(mode="cost", input_tokens=1, input_price_per_m=3)
        self.assert_invalid(mode="cost", input_tokens=1, output_price_per_m=15)
        for bad in (-1, -0.01, 20_000, True, "3"):
            with self.subTest(bad=bad):
                self.assert_invalid(
                    mode="cost",
                    input_tokens=1,
                    input_price_per_m=bad,
                    output_price_per_m=15,
                )
                self.assert_invalid(
                    mode="cost",
                    input_tokens=1,
                    input_price_per_m=3,
                    output_price_per_m=bad,
                )

    # ------------------------------------------------------------------ #
    # Packaging / registration
    # ------------------------------------------------------------------ #

    def test_class_defaults_and_export(self) -> None:
        self.assertIs(DirectTokenEstimatorTool, TokenEstimatorTool)
        self.assertEqual(self.tool.name, "token_estimator_tool")
        self.assertIn("estimate", self.tool.description)
        self.assertEqual(TokenEstimatorTool.MESSAGE_OVERHEAD_TOKENS, 4)
        self.assertEqual(TokenEstimatorTool.ROLE_PRIMER_TOKENS, 2)
        from agentuniverse.agent.action.tool.common_tool import __all__

        self.assertIn("TokenEstimatorTool", __all__)


if __name__ == "__main__":
    unittest.main()
