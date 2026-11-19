#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: token_estimator_tool.py

"""LLM token counting and cost estimation tool for prompt budgeting.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network utility that agents can call before
sending a prompt: how many tokens is this text / this message list,
and how much would it cost on a given model. The same optional
dependency stance as the rest of the framework is taken —
``tiktoken`` is used when it is installed, and a documented
character-based heuristic is used otherwise.

Three modes:

* ``estimate`` — token count for a single text. When ``tiktoken`` is
  importable the count is a real BPE token count via the
  ``cl100k_base`` encoding (the GPT-4 / GPT-4o family encoding, also a
  reasonable proxy for other modern models); the result reports
  ``method_used: "tiktoken"``. If the import or the encoding load
  fails for any reason, the tool degrades to a pinned heuristic and
  reports ``method_used: "heuristic"`` so callers always know which
  arithmetic produced the number. The heuristic splits the text into
  CJK and non-CJK characters and computes exactly:

      cjk_tokens     = floor(cjk_chars * 1.5 + 0.5)   # 1.5 tokens per
                                                       # CJK character,
                                                       # rounded half up
      non_cjk_tokens = ceil(non_cjk_chars / 4)        # ~4 ASCII chars
                                                       # per token
      tokens         = cjk_tokens + non_cjk_tokens

  The result also carries exact character and whitespace word counts.

* ``estimate_chat`` — token count for a chat message list
  (``[{"role": ..., "content": ...}, ...]``). Each message's content
  is counted with the same tiktoken-or-heuristic logic, then the
  standard OpenAI chat framing overhead is added: a fixed 4 tokens per
  message plus 2 tokens for the role primer — 6 overhead tokens per
  message in total. This is the widely used approximation popularized
  by the OpenAI cookbook article *How to count tokens with tiktoken*
  (https://cookbook.openai.com/examples/how_to_count_tokens_with_tiktoken),
  which notes every message is wrapped in framing worth roughly four
  tokens with a couple more for the role/name. The tool pins the exact
  4 + 2 = 6 constants so budgets are reproducible. Per-message and
  cumulative totals are returned.

* ``cost`` — USD cost of a token volume: ``cost = input_tokens / 1e6 *
  input_price + output_tokens / 1e6 * output_price`` with an
  inputs/outputs split. Prices come from an embedded *indicative*
  table of 13 common models (USD per 1M tokens, in / out) or from
  explicit ``input_price_per_m`` / ``output_price_per_m`` arguments.
  The table is a 2026-era snapshot of list prices that WILL drift:
  it exists for quick budgeting only, and any real billing decision
  must override it with custom prices (or a subclass overriding
  ``PRICE_TABLE``) taken from the provider's current price page.

Input validation is strict and happens before any computation:
malformed parameters (wrong types, unknown mode / role / model, wrong
message shape, missing token counts or prices, oversized text or
message counts) raise a ``ValueError``, mirroring the other common
tools. Arithmetic is deterministic: tiktoken BPE counts are stable for
a fixed encoding, and both the heuristic formulas and the chat
overhead constants are pinned above.
"""

import math
from decimal import Decimal
from typing import Any, ClassVar

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

_ENCODING_NAME = "cl100k_base"

# Cache for the lazily loaded tiktoken encoder. The single key
# ``"encoder"`` holds either the loaded encoding or None once a load
# attempt has been made (None means "tiktoken unavailable", mirroring
# the optional-dependency pattern of ContextBudgetCompressor). Tests
# patch this dict to force either path deterministically.
_ENCODER_CACHE: dict[str, Any] = {}


def _load_encoder() -> Any:
    """Lazily load the ``cl100k_base`` tiktoken encoding.

    Returns the encoding object, or ``None`` when ``tiktoken`` is not
    installed or the encoding cannot be loaded (for example on a cold
    offline cache). The result — including failures — is cached so the
    import cost is paid at most once per process.
    """
    if "encoder" in _ENCODER_CACHE:
        return _ENCODER_CACHE["encoder"]
    encoder: Any = None
    try:
        import tiktoken

        encoder = tiktoken.get_encoding(_ENCODING_NAME)
    except Exception:  # noqa: BLE001 - any load failure means: fall back
        encoder = None
    _ENCODER_CACHE["encoder"] = encoder
    return encoder


class TokenEstimatorTool(Tool):
    """LLM token counting and cost estimation tool for prompt budgeting.

    Attributes:
        max_text_chars (int): Upper bound on the ``text`` input and on
            each chat message's ``content``; longer inputs are rejected
            before any computation.
        max_messages (int): Upper bound on the number of chat messages
            accepted by the ``estimate_chat`` mode.
        max_total_chars (int): Upper bound on the summed content length
            of a chat message list.
        max_tokens (int): Upper bound on token counts accepted by the
            ``cost`` mode.
        max_price_per_m (float): Upper bound on a custom price, USD per
            1M tokens.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "token_estimator_tool"
    description: str = (
        "Token estimator tool — LLM token counting and cost estimation "
        "for prompt budgeting, no network required. Single-text token "
        "count with character and word counts (mode='estimate'), chat "
        "message list token count with the standard 4 + 2 per-message "
        "framing overhead (mode='estimate_chat'), and USD cost of a "
        "token volume from an indicative 13-model price table or custom "
        "per-1M prices with an inputs/outputs split (mode='cost'). Uses "
        "tiktoken cl100k_base when installed, otherwise a documented "
        "CJK-aware character heuristic; the result always reports which "
        "method was used."
    )

    MODES: ClassVar[tuple] = ("estimate", "estimate_chat", "cost")
    ROLES: ClassVar[tuple] = (
        "system",
        "user",
        "assistant",
        "tool",
        "function",
    )
    # Standard OpenAI chat framing approximation (OpenAI cookbook,
    # "How to count tokens with tiktoken"): every message is wrapped in
    # ~4 framing tokens plus ~2 for the role primer. Pinned exactly so
    # budgets are reproducible.
    MESSAGE_OVERHEAD_TOKENS: ClassVar[int] = 4
    ROLE_PRIMER_TOKENS: ClassVar[int] = 2

    # Unicode blocks whose characters are counted by the heuristic's
    # 1.5-tokens-per-character rule (CJK ideographs, kana, hangul, CJK
    # punctuation and fullwidth forms, including the main extensions).
    CJK_RANGES: ClassVar[tuple] = (
        (0x3000, 0x303F),   # CJK symbols and punctuation
        (0x3040, 0x30FF),   # Hiragana + Katakana
        (0x3130, 0x318F),   # Hangul compatibility jamo
        (0x3400, 0x4DBF),   # CJK unified ideographs extension A
        (0x4E00, 0x9FFF),   # CJK unified ideographs
        (0xAC00, 0xD7AF),   # Hangul syllables
        (0xF900, 0xFAFF),   # CJK compatibility ideographs
        (0x20000, 0x2A6DF),  # CJK unified ideographs extension B
        (0x2A700, 0x2B73F),  # extension C
        (0x2B740, 0x2B81F),  # extension D
        (0x2B820, 0x2CEAF),  # extension E
        (0xFF00, 0xFFEF),   # halfwidth and fullwidth forms
    )

    # Indicative 2026-era list prices, USD per 1M tokens
    # (input, output). Stored as strings and converted through Decimal
    # so the cost arithmetic is exact. These WILL drift — override with
    # custom prices or a subclass for anything that touches billing.
    PRICE_TABLE: ClassVar[dict[str, tuple[str, str]]] = {
        "gpt-4o": ("2.5", "10"),
        "gpt-4o-mini": ("0.15", "0.6"),
        "o3": ("2", "8"),
        "o4-mini": ("1.1", "4.4"),
        "gpt-4-turbo": ("10", "30"),
        "gpt-3.5-turbo": ("0.5", "1.5"),
        "claude-opus": ("15", "75"),
        "claude-sonnet": ("3", "15"),
        "claude-haiku": ("0.8", "4"),
        "gemini-pro": ("1.25", "5"),
        "gemini-flash": ("0.075", "0.3"),
        "deepseek-chat": ("0.14", "0.28"),
        "deepseek-reasoner": ("0.55", "2.19"),
    }

    TOKENS_PER_MILLION: ClassVar[int] = 1_000_000

    max_text_chars: int = 100_000
    max_messages: int = 200
    max_total_chars: int = 1_000_000
    max_tokens: int = 100_000_000
    max_price_per_m: float = 10_000.0

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        text: Any = None,
        messages: Any = None,
        model: Any = None,
        input_tokens: Any = None,
        output_tokens: Any = None,
        input_price_per_m: Any = None,
        output_price_per_m: Any = None,
    ) -> dict[str, Any]:
        """Run one token estimation or cost computation.

        Args:
            mode (str): One of ``estimate`` / ``estimate_chat`` /
                ``cost``.
            text (str): The text to count. Required for ``estimate``
                (the empty string is allowed and counts as zero
                tokens); not used by the other modes.
            messages (list[dict]): Chat message list of
                ``{"role": ..., "content": ...}`` dicts. Required for
                ``estimate_chat``; roles are restricted to system /
                user / assistant / tool / function.
            model (str): ``cost`` mode only — a model name from the
                embedded indicative price table (case-insensitive),
                e.g. ``gpt-4o``. Mutually exclusive with the custom
                price arguments.
            input_tokens (int): ``cost`` mode only — input (prompt)
                token count; at least one of ``input_tokens`` /
                ``output_tokens`` must be given.
            output_tokens (int): ``cost`` mode only — output
                (completion) token count.
            input_price_per_m (float): ``cost`` mode only — custom
                input price, USD per 1M tokens; requires
                ``output_price_per_m`` too and excludes ``model``.
            output_price_per_m (float): ``cost`` mode only — custom
                output price, USD per 1M tokens.

        Returns:
            Dict[str, Any]: The estimation result, always including
            ``method_used`` (``tiktoken`` | ``heuristic``) for the
            counting modes and per-field USD amounts for ``cost``.

        Raises:
            ValueError: If any parameter is malformed (before any
            computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        if mode == "estimate":
            return self._run_estimate(self._validate_text(text))
        if mode == "estimate_chat":
            return self._run_estimate_chat(
                self._validate_messages(messages)
            )
        return self._run_cost(
            model,
            input_tokens,
            output_tokens,
            input_price_per_m,
            output_price_per_m,
        )

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"token_estimator_tool: {message}")

    def _validate_text(self, text: Any) -> str:
        """Validate the ``text`` input of the ``estimate`` mode.

        The empty string is a valid subject for token counting (it is
        zero tokens), unlike the encode/decode subjects of e.g. the
        text codec tool.
        """
        if text is None or isinstance(text, bool) or not isinstance(text, str):
            self._invalid(f"text must be a string (got {text!r})")
        if len(text) > self.max_text_chars:
            self._invalid(
                f"text exceeds the {self.max_text_chars:,}-character limit "
                f"(got {len(text):,} characters)"
            )
        return text

    def _validate_messages(self, messages: Any) -> list[dict[str, str]]:
        """Validate the chat ``messages`` list of ``estimate_chat``."""
        if isinstance(messages, bool) or not isinstance(messages, list):
            self._invalid(
                "messages must be a list of {'role': ..., 'content': ...} "
                f"dicts (got {messages!r})"
            )
        if not messages:
            self._invalid("messages must contain at least one message")
        if len(messages) > self.max_messages:
            self._invalid(
                f"messages exceed the {self.max_messages:,}-message limit "
                f"(got {len(messages):,})"
            )
        total_chars = 0
        for index, message in enumerate(messages):
            if isinstance(message, bool) or not isinstance(message, dict):
                self._invalid(
                    f"message {index} must be a dict with the keys 'role' "
                    f"and 'content' (got {message!r})"
                )
            if set(message.keys()) != {"role", "content"}:
                self._invalid(
                    f"message {index} must have exactly the keys 'role' and "
                    f"'content' (got {sorted(message.keys())})"
                )
            role = message["role"]
            content = message["content"]
            if isinstance(role, bool) or not isinstance(role, str):
                self._invalid(
                    f"message {index} role must be a string (got {role!r})"
                )
            if role not in self.ROLES:
                self._invalid(
                    f"message {index} role must be one of: "
                    f"{', '.join(self.ROLES)} (got {role!r})"
                )
            if (
                content is None
                or isinstance(content, bool)
                or not isinstance(content, str)
            ):
                self._invalid(
                    f"message {index} ({role}) content must be a string "
                    f"(got {content!r})"
                )
            if len(content) > self.max_text_chars:
                self._invalid(
                    f"message {index} ({role}) content exceeds the "
                    f"{self.max_text_chars:,}-character limit "
                    f"(got {len(content):,} characters)"
                )
            total_chars += len(content)
        if total_chars > self.max_total_chars:
            self._invalid(
                f"messages exceed the {self.max_total_chars:,}-character "
                f"total limit (got {total_chars:,} characters)"
            )
        return messages

    def _validate_token_count(self, name: str, value: Any) -> int:
        """Validate one token-count argument of the ``cost`` mode."""
        if value is None:
            return 0
        if isinstance(value, bool) or not isinstance(value, int):
            self._invalid(f"{name} must be a non-negative integer (got {value!r})")
        if value < 0:
            self._invalid(f"{name} must be a non-negative integer (got {value!r})")
        if value > self.max_tokens:
            self._invalid(
                f"{name} exceeds the {self.max_tokens:,}-token limit "
                f"(got {value:,})"
            )
        return value

    def _validate_custom_price(self, name: str, value: Any) -> Decimal:
        """Validate one custom price argument (USD per 1M tokens)."""
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            self._invalid(f"{name} must be a number, USD per 1M tokens (got {value!r})")
        price = Decimal(str(value))
        if price < 0:
            self._invalid(f"{name} must be a non-negative number (got {value!r})")
        if price > Decimal(str(self.max_price_per_m)):
            self._invalid(
                f"{name} exceeds the {self.max_price_per_m:,.0f} USD per 1M "
                f"tokens sanity limit (got {value!r})"
            )
        return price

    # ------------------------------------------------------------------ #
    # Token counting (tiktoken with heuristic fallback)
    # ------------------------------------------------------------------ #

    @classmethod
    def _count_tokens(cls, text: str) -> tuple[int, str]:
        """Count tokens in ``text`` with tiktoken or the heuristic.

        Returns ``(tokens, method_used)`` where ``method_used`` is
        ``"tiktoken"`` or ``"heuristic"``.
        """
        encoder = _load_encoder()
        if encoder is not None:
            return len(encoder.encode(text)), "tiktoken"
        tokens, _, _ = cls._heuristic_tokens(text)
        return tokens, "heuristic"

    @classmethod
    def _is_cjk(cls, char: str) -> bool:
        """Whether ``char`` falls in one of the pinned CJK blocks."""
        code = ord(char)
        return any(low <= code <= high for low, high in cls.CJK_RANGES)

    @classmethod
    def _heuristic_tokens(cls, text: str) -> tuple[int, int, int]:
        """The pinned character heuristic.

        Returns ``(tokens, cjk_chars, non_cjk_chars)`` with the exact
        formulas ``floor(cjk_chars * 1.5 + 0.5) +
        ceil(non_cjk_chars / 4)``.
        """
        cjk_chars = sum(1 for char in text if cls._is_cjk(char))
        non_cjk_chars = len(text) - cjk_chars
        cjk_tokens = math.floor(cjk_chars * 1.5 + 0.5)
        non_cjk_tokens = math.ceil(non_cjk_chars / 4)
        return cjk_tokens + non_cjk_tokens, cjk_chars, non_cjk_chars

    # ------------------------------------------------------------------ #
    # estimate mode
    # ------------------------------------------------------------------ #

    def _run_estimate(self, text: str) -> dict[str, Any]:
        """Count tokens, characters and words of a single text."""
        encoder = _load_encoder()
        result: dict[str, Any] = {
            "mode": "estimate",
            "tokens": None,
            "chars": len(text),
            "words": len(text.split()),
            "method_used": None,
        }
        if encoder is not None:
            result["tokens"] = len(encoder.encode(text))
            result["method_used"] = "tiktoken"
            result["encoding"] = _ENCODING_NAME
        else:
            tokens, cjk_chars, non_cjk_chars = self._heuristic_tokens(text)
            cjk_tokens = math.floor(cjk_chars * 1.5 + 0.5)
            result.update(
                {
                    "tokens": tokens,
                    "method_used": "heuristic",
                    "cjk_chars": cjk_chars,
                    "non_cjk_chars": non_cjk_chars,
                    "cjk_tokens": cjk_tokens,
                    "non_cjk_tokens": tokens - cjk_tokens,
                }
            )
        return result

    # ------------------------------------------------------------------ #
    # estimate_chat mode
    # ------------------------------------------------------------------ #

    def _run_estimate_chat(self, messages: list[dict[str, str]]) -> dict[str, Any]:
        """Count tokens of a chat message list with framing overhead."""
        overhead_per_message = (
            self.MESSAGE_OVERHEAD_TOKENS + self.ROLE_PRIMER_TOKENS
        )
        per_message: list[dict[str, Any]] = []
        total_content_tokens = 0
        total_chars = 0
        for message in messages:
            content = message["content"]
            content_tokens, _ = self._count_tokens(content)
            per_message.append(
                {
                    "role": message["role"],
                    "content_tokens": content_tokens,
                    "overhead_tokens": overhead_per_message,
                    "total_tokens": content_tokens + overhead_per_message,
                }
            )
            total_content_tokens += content_tokens
            total_chars += len(content)
        total_overhead = overhead_per_message * len(messages)
        # The counting method is a property of the encoder, not of any
        # individual message, so it is reported once at the top level.
        method_used = self._count_tokens("")[1]
        result: dict[str, Any] = {
            "mode": "estimate_chat",
            "method_used": method_used,
            "message_count": len(messages),
            "overhead_tokens_per_message": overhead_per_message,
            "messages": per_message,
            "total_content_tokens": total_content_tokens,
            "total_overhead_tokens": total_overhead,
            "total_tokens": total_content_tokens + total_overhead,
            "total_chars": total_chars,
        }
        if method_used == "tiktoken":
            result["encoding"] = _ENCODING_NAME
        return result

    # ------------------------------------------------------------------ #
    # cost mode
    # ------------------------------------------------------------------ #

    def _run_cost(
        self,
        model: Any,
        input_tokens: Any,
        output_tokens: Any,
        input_price_per_m: Any,
        output_price_per_m: Any,
    ) -> dict[str, Any]:
        """Compute the USD cost of a token volume at table or custom
        prices."""
        if input_tokens is None and output_tokens is None:
            self._invalid(
                "at least one of input_tokens / output_tokens is required "
                "for the cost mode"
            )
        has_model = model is not None
        has_custom_price = (
            input_price_per_m is not None or output_price_per_m is not None
        )
        if has_model and has_custom_price:
            self._invalid(
                "provide either a model from the price table or custom "
                "input/output prices, not both"
            )

        if has_model:
            if isinstance(model, bool) or not isinstance(model, str):
                self._invalid(
                    f"model must be a non-empty string (got {model!r})"
                )
            key = model.strip().lower()
            if not key:
                self._invalid("model must be a non-empty string (got '')")
            if key not in self.PRICE_TABLE:
                self._invalid(
                    f"unknown model {model!r} — available models: "
                    f"{', '.join(sorted(self.PRICE_TABLE))} "
                    "(pass input_price_per_m / output_price_per_m for "
                    "custom pricing)"
                )
            input_price = Decimal(self.PRICE_TABLE[key][0])
            output_price = Decimal(self.PRICE_TABLE[key][1])
            price_source = "table"
        else:
            if input_price_per_m is None or output_price_per_m is None:
                self._invalid(
                    "custom pricing requires both input_price_per_m and "
                    "output_price_per_m (USD per 1M tokens)"
                )
            input_price = self._validate_custom_price(
                "input_price_per_m", input_price_per_m
            )
            output_price = self._validate_custom_price(
                "output_price_per_m", output_price_per_m
            )
            key = "custom"
            price_source = "custom"

        clean_input_tokens = self._validate_token_count(
            "input_tokens", input_tokens
        )
        clean_output_tokens = self._validate_token_count(
            "output_tokens", output_tokens
        )

        million = Decimal(self.TOKENS_PER_MILLION)
        input_cost = (
            Decimal(clean_input_tokens) * input_price / million
        ).quantize(Decimal("0.0000000001"))
        output_cost = (
            Decimal(clean_output_tokens) * output_price / million
        ).quantize(Decimal("0.0000000001"))

        return {
            "mode": "cost",
            "model": key,
            "price_source": price_source,
            "currency": "USD",
            "input_tokens": clean_input_tokens,
            "output_tokens": clean_output_tokens,
            "input_price_per_m": float(input_price),
            "output_price_per_m": float(output_price),
            "input_cost_usd": float(input_cost),
            "output_cost_usd": float(output_cost),
            "total_cost_usd": float(input_cost + output_cost),
        }
