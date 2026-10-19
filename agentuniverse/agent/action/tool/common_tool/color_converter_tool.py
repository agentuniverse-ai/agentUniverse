#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: color_converter_tool.py

"""Color format conversion and WCAG contrast tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency color utility agents
can call for design-system plumbing: converting color notations,
inspecting a color, and checking whether a text/background pair passes
the WCAG accessibility thresholds.

The tool accepts every common CSS color notation and converts between
them, with three modes:

* ``convert`` — parse one color (hex ``#rgb`` / ``#rrggbb`` /
  ``#rrggbbaa``, functional ``rgb()`` / ``rgba()`` with integer
  channels 0-255, ``hsl()`` / ``hsla()`` with degrees and percent,
  ``hsv()`` / ``hsva()``, or one of the embedded common CSS named
  colors) and re-emit it in a target format: ``hex`` (6-digit, or
  8-digit when an alpha below 1 is present), ``hex8``, ``rgb`` (the
  ``rgba()`` form is emitted automatically when alpha < 1), ``hsl``,
  ``hsv`` or ``name`` (exact-match only; otherwise a structured error
  suggests the nearest embedded name).
* ``info`` — one color to *all* representations at once, plus the
  WCAG relative luminance, the contrast ratios against white and
  black, and the nearest embedded named color.
* ``contrast`` — two colors to the WCAG 2.x contrast ratio (1.0-21.0)
  with pass/fail verdicts for the AA / AAA thresholds of normal text
  (4.5 / 7.0) and large text (3.0 / 4.5).

Relative luminance follows WCAG exactly: each sRGB channel is
linearized (``c / 12.92`` for ``c <= 0.04045`` else
``((c + 0.055) / 1.055) ** 2.4``) and combined as
``0.2126 R + 0.7152 G + 0.0722 B``; the contrast ratio of two colors
is ``(L1 + 0.05) / (L2 + 0.05)`` with ``L1 >= L2``.

Precision: RGB channels are computed with the CSS Color Model
algorithm and rounded half-up; hue, saturation and lightness/value are
emitted with one decimal place, which keeps ``hsl -> rgb -> hsl`` (and
``hsv -> rgb -> hsv``) round trips within one unit of the input.

Input validation is strict and happens before any computation:
malformed parameters (wrong types, unknown mode or target format,
missing required arguments per mode, oversized input) raise a
``ValueError``, mirroring the other common tools. Errors that depend
on the *content being processed* — invalid hex digits or lengths,
channel values outside 0-255, hue outside 0-360, percentages outside
0-100, alpha outside 0-1, wrong argument counts, unknown function
names or color names — are returned as a structured ``error`` payload
including the character ``position`` of the offending part, so an
agent can react without catching exceptions.

Alpha handling: ``#rrggbbaa`` divides the alpha byte by 255;
functional notations accept an optional fourth component as a float in
0-1 or a percentage. Alpha is preserved by every conversion whose
target format can carry it. The ``contrast`` mode requires opaque
colors (WCAG defines no ratio for translucent ones) and returns a
structured error when either color has alpha below 1.

The named-color table is a curated compact subset (~48 entries
including the gray/grey, aqua/cyan and fuchsia/magenta aliases) of the
148 CSS named colors, so lookups stay small and reviewable; the
nearest-name search runs over this table in linearized RGB space with
deterministic (alphabetical) tie-breaking.
"""

import math
import re
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Strict hex: '#rgb', '#rrggbb' or '#rrggbbaa' (case-insensitive digits).
_HEX_COLOR = re.compile(r"\A#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3}(?:[0-9a-fA-F]{2})?)?\Z")
# Functional notation: name(...) with balanced outer parens (case-insensitive).
_FUNCTIONAL = re.compile(r"\A([a-zA-Z]+)\s*\((.*)\)\Z", re.DOTALL)
_UNSIGNED_INT = re.compile(r"\A\+?\d+\Z")

# Curated compact table of the most common CSS named colors (X11/CSS3
# values), including the aqua/cyan, fuchsia/magenta and gray/grey aliases.
_NAMED_COLORS: Dict[str, str] = {
    "aliceblue": "#f0f8ff",
    "aqua": "#00ffff",
    "azure": "#f0ffff",
    "beige": "#f5f5dc",
    "black": "#000000",
    "blue": "#0000ff",
    "brown": "#a52a2a",
    "chocolate": "#d2691e",
    "coral": "#ff7f50",
    "crimson": "#dc143c",
    "cyan": "#00ffff",
    "darkblue": "#00008b",
    "darkgray": "#a9a9a9",
    "darkgreen": "#006400",
    "darkred": "#8b0000",
    "dimgray": "#696969",
    "firebrick": "#b22222",
    "fuchsia": "#ff00ff",
    "gold": "#ffd700",
    "gray": "#808080",
    "green": "#008000",
    "grey": "#808080",
    "hotpink": "#ff69b4",
    "indigo": "#4b0082",
    "ivory": "#fffff0",
    "khaki": "#f0e68c",
    "lavender": "#e6e6fa",
    "lightblue": "#add8e6",
    "lightgray": "#d3d3d3",
    "lightgreen": "#90ee90",
    "lightyellow": "#ffffe0",
    "lime": "#00ff00",
    "magenta": "#ff00ff",
    "maroon": "#800000",
    "navy": "#000080",
    "olive": "#808000",
    "orange": "#ffa500",
    "orangered": "#ff4500",
    "pink": "#ffc0cb",
    "purple": "#800080",
    "red": "#ff0000",
    "royalblue": "#4169e1",
    "salmon": "#fa8072",
    "seagreen": "#2e8b57",
    "silver": "#c0c0c0",
    "skyblue": "#87ceeb",
    "slategray": "#708090",
    "steelblue": "#4682b4",
    "tan": "#d2b48c",
    "teal": "#008080",
    "tomato": "#ff6347",
    "turquoise": "#40e0d0",
    "violet": "#ee82ee",
    "wheat": "#f5deb3",
    "white": "#ffffff",
    "yellow": "#ffff00",
    "yellowgreen": "#9acd32",
}


class ColorConverterTool(Tool):
    """Color format conversion and WCAG contrast tool (pure stdlib).

    Attributes:
        max_input_chars (int): Upper bound on the length of each color
            string; longer inputs are rejected before any work.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "color_converter_tool"
    description: str = (
        "Color converter tool — pure Python stdlib, no network required. "
        "Convert between CSS color notations (mode='convert'): hex "
        "#rgb/#rrggbb/#rrggbbaa, rgb()/rgba() integer channels, "
        "hsl()/hsla() degrees-percents, hsv()/hsva() and ~48 embedded "
        "common named colors. Inspect one color (mode='info'): every "
        "representation, WCAG relative luminance, contrast against "
        "white/black and the nearest named color. Check accessibility "
        "(mode='contrast'): WCAG 2.x contrast ratio 1-21 of two opaque "
        "colors with AA/AAA pass/fail for normal (4.5/7.0) and large "
        "(3.0/4.5) text."
    )

    MODES: ClassVar[tuple] = ("convert", "info", "contrast")
    FORMATS: ClassVar[tuple] = ("hex", "hex8", "rgb", "hsl", "hsv", "name")
    # Functional prefixes this tool understands, mapped to their channel model.
    _FUNCTIONS: ClassVar[Dict[str, str]] = {
        "rgb": "rgb",
        "rgba": "rgb",
        "hsl": "hsl",
        "hsla": "hsl",
        "hsv": "hsv",
        "hsva": "hsv",
    }

    max_input_chars: int = 200

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        color: Any = None,
        to_format: Any = None,
        foreground: Any = None,
        background: Any = None,
    ) -> Dict[str, Any]:
        """Run one color operation.

        Args:
            mode (str): One of ``convert`` / ``info`` / ``contrast``.
            color (str): The color to convert or inspect — required for
                the ``convert`` and ``info`` modes.
            to_format (str): Target format for the ``convert`` mode —
                one of ``hex`` / ``hex8`` / ``rgb`` / ``hsl`` / ``hsv`` /
                ``name``.
            foreground (str): First color of the ``contrast`` pair (the
                text color in accessibility checks).
            background (str): Second color of the ``contrast`` pair
                (the surface color).

        Returns:
            Dict[str, Any]: The operation result (a ``result`` string
                for ``convert``, a full report for ``info`` and
                ``contrast``) or a structured ``error`` payload for
                content-level failures (invalid hex, out-of-range
                channels/hue/percentages/alpha, unknown function or
                color name), with the character ``position`` of the
                offending part when one can be pinpointed.

        Raises:
            ValueError: If any parameter is malformed (unknown mode or
                target format, wrong types, missing required arguments,
                oversized input) — before any computation happens.
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        if mode == "contrast":
            fg = self._validate_color_string(foreground, label="foreground")
            bg = self._validate_color_string(background, label="background")
            return self._run_contrast(fg, bg)
        clean_color = self._validate_color_string(color)
        if mode == "info":
            return self._run_info(clean_color)
        if to_format not in self.FORMATS:
            self._invalid(
                "to_format must be one of: "
                f"{', '.join(self.FORMATS)} (got {to_format!r})"
            )
        return self._run_convert(clean_color, to_format)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"color_converter_tool: {message}")

    @classmethod
    def _validate_color_string(cls, value: Any, label: str = "color") -> str:
        """Validate one color string argument (type, content, length)."""
        if value is None or isinstance(value, bool) or not isinstance(value, str):
            cls._invalid(f"{label} must be a non-empty color string (got {value!r})")
        stripped = value.strip()
        if not stripped:
            cls._invalid(f"{label} must be a non-empty color string (got {value!r})")
        # Literal bound (pydantic v2 fields are not reachable via `cls`);
        # kept in sync with the `max_input_chars` attribute above.
        if len(stripped) > 200:
            cls._invalid(
                f"{label} exceeds the {200}-character limit "
                f"(got {len(stripped)} characters)"
            )
        return stripped

    # ------------------------------------------------------------------ #
    # Parsing (content-level errors become structured payloads)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _error_result(
        context: Dict[str, Any],
        error_type: str,
        message: str,
        position: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Build a structured error payload."""
        error: Dict[str, Any] = {"type": error_type, "message": str(message)[:500]}
        if position is not None:
            error["position"] = position
        return {**context, "error": error}

    def parse(self, color: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Parse any supported notation to ``{r, g, b, alpha}`` channels.

        Returns the parsed channels on success, or a structured error
        payload (a dict carrying an ``error`` key) when the notation is
        syntactically or numerically invalid.
        """
        if color.startswith("#"):
            return self._parse_hex(color, context)
        match = _FUNCTIONAL.match(color)
        if match:
            return self._parse_functional(color, match, context)
        return self._parse_named(color, context)

    @classmethod
    def _parse_hex(
        cls, color: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Parse '#rgb', '#rrggbb' or '#rrggbbaa' strictly."""
        digits = color[1:]
        if not _HEX_COLOR.match(color):
            if not digits:
                return cls._error_result(
                    context,
                    error_type="invalid_hex",
                    message=(
                        "hex color must provide 3, 6 or 8 hexadecimal "
                        "digits after '#' — got bare '#'"
                    ),
                    position=1,
                )
            if re.match(r"\A#[0-9a-fA-F]+\Z", color):
                return cls._error_result(
                    context,
                    error_type="invalid_hex",
                    message=(
                        "hex color must have 3, 6 or 8 hex digits after '#' "
                        f"(#rgb, #rrggbb or #rrggbbaa) — got {len(digits)} "
                        f"(got {color[:64]!r})"
                    ),
                    position=1,
                )
            bad = next(
                (i for i, ch in enumerate(digits) if ch not in "0123456789abcdefABCDEF"),
                len(digits),
            )
            return cls._error_result(
                context,
                error_type="invalid_hex",
                message=(
                    "hex color must only contain hexadecimal digits "
                    f"(0-9, a-f) after '#' — found {digits[bad]!r} "
                    f"at position {bad + 1}"
                ),
                position=bad + 1,
            )
        if len(digits) == 3:
            channels = [int(ch * 2, 16) for ch in digits]
            alpha = 1.0
        elif len(digits) == 6:
            channels = [int(digits[i : i + 2], 16) for i in (0, 2, 4)]
            alpha = 1.0
        else:
            channels = [int(digits[i : i + 2], 16) for i in (0, 2, 4)]
            alpha = round(int(digits[6:8], 16) / 255, 4)
        r, g, b = channels
        return {"r": r, "g": g, "b": b, "alpha": alpha}

    @classmethod
    def _parse_named(
        cls, color: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Parse one of the embedded CSS named colors (case-insensitive)."""
        lower = color.lower()
        if lower not in _NAMED_COLORS:
            hint = ""
            if "(" in color or ")" in color:
                hint = (
                    "; the input looks like a functional notation — check "
                    "the spelling and that it is wrapped in balanced "
                    "parentheses"
                )
            return cls._error_result(
                context,
                error_type="unknown_color_name",
                message=(
                    f"{color[:64]!r} is not a recognized color: it is not "
                    "one of the embedded common CSS named colors, and hex "
                    f"colors must start with '#{hint}'. Try e.g. 'red', "
                    "'teal', 'rgb(255, 0, 0)', 'hsl(0, 100%, 50%)' or "
                    "'#ff0000'"
                ),
                position=0,
            )
        return cls._parse_hex(_NAMED_COLORS[lower], context)

    class _ComponentError(Exception):
        """Internal signal: one component failed with a ready payload."""

        def __init__(self, payload: Dict[str, Any]):
            super().__init__(payload["error"]["message"])
            self.payload = payload

    @classmethod
    def _parse_functional(
        cls, color: str, match: "re.Match", context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Parse rgb()/rgba(), hsl()/hsla() and hsv()/hsva() strictly.

        Each comma-separated component is validated individually so the
        error can carry the character position of the offending part.
        """
        func = match.group(1).lower()
        inner = match.group(2)
        model = cls._FUNCTIONS.get(func)
        if model is None:
            return cls._error_result(
                context,
                error_type="unknown_function",
                message=(
                    f"unknown color function {func!r} — supported: "
                    "rgb()/rgba(), hsl()/hsla(), hsv()/hsva() "
                    f"(got {color[:64]!r})"
                ),
                position=0,
            )
        raw_parts = inner.split(",")
        parts = [p.strip() for p in raw_parts]
        body_start = color.index("(") + 1
        # Character position where each comma-separated part starts.
        offsets: List[int] = []
        cursor = body_start
        for raw_part in raw_parts:
            offsets.append(cursor + (len(raw_part) - len(raw_part.lstrip())))
            cursor += len(raw_part) + 1
        label = {"rgb": "rgb", "hsl": "hsl", "hsv": "hsv"}[model]

        if len(parts) not in (3, 4):
            return cls._error_result(
                context,
                error_type="invalid_component_count",
                message=(
                    f"{label}() takes 3 components plus an optional alpha "
                    f"(comma-separated) — got {len(parts)} "
                    f"(got {color[:64]!r})"
                ),
                position=body_start,
            )
        if len(parts) == 4 and parts[3] == "":
            return cls._error_result(
                context,
                error_type="invalid_alpha",
                message="alpha component must not be empty",
                position=offsets[3],
            )

        def fail(error_type: str, message: str, offset: int) -> None:
            raise cls._ComponentError(
                cls._error_result(
                    context, error_type=error_type, message=message, position=offset
                )
            )

        def check_hue(part: str, offset: int) -> float:
            if not re.match(r"\A[+-]?(\d+\.?\d*|\.\d+)\Z", part):
                fail(
                    "invalid_hue",
                    f"hue must be a number of degrees (0-360) — got {part!r}",
                    offset,
                )
            value = float(part)
            if not 0.0 <= value <= 360.0:
                fail(
                    "invalid_hue",
                    f"hue must be within 0-360 degrees — got {value:g}",
                    offset,
                )
            return value % 360.0

        def check_percent(part: str, offset: int, what: str) -> float:
            if not part.endswith("%") or not re.match(
                r"\A[+-]?(\d+\.?\d*|\.\d+)%\Z", part
            ):
                fail(
                    "invalid_percent",
                    f"{what} must be a percentage between 0% and 100% "
                    f"(e.g. '50%') — got {part!r}",
                    offset,
                )
            value = float(part[:-1])
            if not 0.0 <= value <= 100.0:
                fail(
                    "invalid_percent",
                    f"{what} must be within 0%-100% — got {value:g}%",
                    offset,
                )
            return value / 100.0

        def check_channel(part: str, offset: int, what: str) -> int:
            if not _UNSIGNED_INT.match(part):
                fail(
                    "invalid_channel",
                    f"channel {what!r} must be an integer between 0 and "
                    f"255 — got {part!r}",
                    offset,
                )
            value = int(part)
            if not 0 <= value <= 255:
                fail(
                    "invalid_channel",
                    f"channel {what!r} must be within 0-255 — got {value}",
                    offset,
                )
            return value

        def check_alpha(part: str, offset: int) -> float:
            is_percent = part.endswith("%")
            body = part[:-1] if is_percent else part
            if not re.match(r"\A[+-]?(\d+\.?\d*|\.\d+)\Z", body):
                fail(
                    "invalid_alpha",
                    "alpha must be a number between 0 and 1 "
                    f"(or a percentage 0%-100%) — got {part!r}",
                    offset,
                )
            value = float(body) / (100.0 if is_percent else 1.0)
            if not 0.0 <= value <= 1.0:
                fail(
                    "invalid_alpha",
                    f"alpha must be within 0-1 (or 0%-100%) — got {part}",
                    offset,
                )
            return value

        try:
            if model == "rgb":
                r = check_channel(parts[0], offsets[0], "r")
                g = check_channel(parts[1], offsets[1], "g")
                b = check_channel(parts[2], offsets[2], "b")
                alpha = check_alpha(parts[3], offsets[3]) if len(parts) == 4 else 1.0
                return {"r": r, "g": g, "b": b, "alpha": alpha}
            h = check_hue(parts[0], offsets[0])
            s = check_percent(parts[1], offsets[1], "saturation")
            third_label = "lightness" if model == "hsl" else "value"
            third = check_percent(parts[2], offsets[2], third_label)
            alpha = check_alpha(parts[3], offsets[3]) if len(parts) == 4 else 1.0
            if model == "hsl":
                r, g, b = cls._hsl_to_rgb(h, s * 100.0, third * 100.0)
            else:
                r, g, b = cls._hsv_to_rgb(h, s * 100.0, third * 100.0)
            return {"r": r, "g": g, "b": b, "alpha": alpha}
        except cls._ComponentError as error:
            return error.payload

    # ------------------------------------------------------------------ #
    # Color math (CSS Color Model algorithms, half-up channel rounding)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _round_half_up(value: float) -> int:
        """Round to the nearest integer, halves away from zero's floor."""
        return int(math.floor(value + 0.5))

    @classmethod
    def _hsl_to_rgb(cls, h: float, s: float, l: float) -> Tuple[int, int, int]:
        """CSS hsl (degrees, %, %) to 8-bit rgb channels."""
        c = (1 - abs(2 * l / 100 - 1)) * s / 100
        hp = (h % 360) / 60
        x = c * (1 - abs(hp % 2 - 1))
        if hp < 1:
            r1, g1, b1 = c, x, 0.0
        elif hp < 2:
            r1, g1, b1 = x, c, 0.0
        elif hp < 3:
            r1, g1, b1 = 0.0, c, x
        elif hp < 4:
            r1, g1, b1 = 0.0, x, c
        elif hp < 5:
            r1, g1, b1 = x, 0.0, c
        else:
            r1, g1, b1 = c, 0.0, x
        m = l / 100 - c / 2
        return (
            cls._round_half_up((r1 + m) * 255),
            cls._round_half_up((g1 + m) * 255),
            cls._round_half_up((b1 + m) * 255),
        )

    @classmethod
    def _hsv_to_rgb(cls, h: float, s: float, v: float) -> Tuple[int, int, int]:
        """hsv (degrees, %, %) to 8-bit rgb channels."""
        c = v / 100 * s / 100
        hp = (h % 360) / 60
        x = c * (1 - abs(hp % 2 - 1))
        if hp < 1:
            r1, g1, b1 = c, x, 0.0
        elif hp < 2:
            r1, g1, b1 = x, c, 0.0
        elif hp < 3:
            r1, g1, b1 = 0.0, c, x
        elif hp < 4:
            r1, g1, b1 = 0.0, x, c
        elif hp < 5:
            r1, g1, b1 = x, 0.0, c
        else:
            r1, g1, b1 = c, 0.0, x
        m = v / 100 - c
        return (
            cls._round_half_up((r1 + m) * 255),
            cls._round_half_up((g1 + m) * 255),
            cls._round_half_up((b1 + m) * 255),
        )

    @classmethod
    def _rgb_to_hsl(cls, r: int, g: int, b: int) -> Tuple[float, float, float]:
        """8-bit rgb to (hue 0-360, saturation %, lightness %), 1 decimal."""
        rp, gp, bp = r / 255, g / 255, b / 255
        mx, mn = max(rp, gp, bp), min(rp, gp, bp)
        l = (mx + mn) / 2
        if mx == mn:
            return 0.0, 0.0, round(l * 100, 1)
        d = mx - mn
        s = d / ((mx + mn) if l <= 0.5 else (2 - mx - mn))
        if mx == rp:
            hp = ((gp - bp) / d) % 6
        elif mx == gp:
            hp = (bp - rp) / d + 2
        else:
            hp = (rp - gp) / d + 4
        h = hp * 60
        return round(h % 360, 1), round(s * 100, 1), round(l * 100, 1)

    @classmethod
    def _rgb_to_hsv(cls, r: int, g: int, b: int) -> Tuple[float, float, float]:
        """8-bit rgb to (hue 0-360, saturation %, value %), 1 decimal."""
        rp, gp, bp = r / 255, g / 255, b / 255
        mx, mn = max(rp, gp, bp), min(rp, gp, bp)
        v = mx
        if mx == 0:
            return 0.0, 0.0, 0.0
        s = (mx - mn) / mx
        if mx == mn:
            return 0.0, 0.0, round(v * 100, 1)
        d = mx - mn
        if mx == rp:
            hp = ((gp - bp) / d) % 6
        elif mx == gp:
            hp = (bp - rp) / d + 2
        else:
            hp = (rp - gp) / d + 4
        h = hp * 60
        return round(h % 360, 1), round(s * 100, 1), round(v * 100, 1)

    @staticmethod
    def _linearize(channel: float) -> float:
        """WCAG sRGB channel linearization (channel given in 0-1)."""
        return channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4

    @classmethod
    def relative_luminance(cls, r: int, g: int, b: int) -> float:
        """WCAG 2.x relative luminance of an opaque sRGB color (0-1)."""
        return round(
            0.2126 * cls._linearize(r / 255)
            + 0.7152 * cls._linearize(g / 255)
            + 0.0722 * cls._linearize(b / 255),
            6,
        )

    @staticmethod
    def contrast_ratio(l1: float, l2: float) -> float:
        """WCAG contrast ratio of two luminances (ordered internally)."""
        lighter, darker = max(l1, l2), min(l1, l2)
        return round((lighter + 0.05) / (darker + 0.05), 2)

    # ------------------------------------------------------------------ #
    # Formatting helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _fmt_number(value: float) -> str:
        """Render 1-decimal floats without a trailing '.0' when integral."""
        text = f"{value:.1f}".rstrip("0").rstrip(".")
        return text if text else "0"

    @classmethod
    def _fmt_alpha(cls, alpha: float) -> str:
        """Render alpha with up to 3 decimals, trailing zeros trimmed."""
        if alpha == 1.0:
            return "1"
        text = f"{alpha:.3f}".rstrip("0").rstrip(".")
        return text if text else "0"

    @classmethod
    def _to_hex(cls, channels: Dict[str, Any], force_alpha: bool) -> str:
        r, g, b = channels["r"], channels["g"], channels["b"]
        base = f"#{r:02x}{g:02x}{b:02x}"
        if force_alpha or channels["alpha"] < 1.0:
            a = cls._round_half_up(channels["alpha"] * 255)
            return f"{base}{a:02x}"
        return base

    @classmethod
    def _to_rgb_string(cls, channels: Dict[str, Any]) -> str:
        r, g, b = channels["r"], channels["g"], channels["b"]
        if channels["alpha"] < 1.0:
            return f"rgba({r}, {g}, {b}, {cls._fmt_alpha(channels['alpha'])})"
        return f"rgb({r}, {g}, {b})"

    @classmethod
    def _to_hsl_string(cls, channels: Dict[str, Any]) -> str:
        h, s, l = cls._rgb_to_hsl(channels["r"], channels["g"], channels["b"])
        if channels["alpha"] < 1.0:
            return (
                f"hsla({cls._fmt_number(h)}, {cls._fmt_number(s)}%, "
                f"{cls._fmt_number(l)}%, {cls._fmt_alpha(channels['alpha'])})"
            )
        return (
            f"hsl({cls._fmt_number(h)}, {cls._fmt_number(s)}%, "
            f"{cls._fmt_number(l)}%)"
        )

    @classmethod
    def _to_hsv_string(cls, channels: Dict[str, Any]) -> str:
        h, s, v = cls._rgb_to_hsv(channels["r"], channels["g"], channels["b"])
        if channels["alpha"] < 1.0:
            return (
                f"hsva({cls._fmt_number(h)}, {cls._fmt_number(s)}%, "
                f"{cls._fmt_number(v)}%, {cls._fmt_alpha(channels['alpha'])})"
            )
        return (
            f"hsv({cls._fmt_number(h)}, {cls._fmt_number(s)}%, "
            f"{cls._fmt_number(v)}%)"
        )

    @classmethod
    def exact_name(cls, r: int, g: int, b: int) -> Optional[str]:
        """Exact embedded named color for the rgb triple, if any.

        Aliases of one color resolve to the alphabetically first name
        (e.g. ``aqua`` over ``cyan``), keeping output deterministic.
        """
        target = f"#{r:02x}{g:02x}{b:02x}"
        for name in sorted(_NAMED_COLORS):
            if _NAMED_COLORS[name] == target:
                return name
        return None

    @classmethod
    def nearest_named_color(cls, r: int, g: int, b: int) -> Dict[str, Any]:
        """Nearest embedded named color in linearized-RGB space.

        Distance is the squared Euclidean distance over the WCAG
        linearized channels; ties break alphabetically for determinism.
        """
        lr, lg, lb = (
            cls._linearize(r / 255),
            cls._linearize(g / 255),
            cls._linearize(b / 255),
        )
        best_name: Optional[str] = None
        best_distance: Optional[float] = None
        for name in sorted(_NAMED_COLORS):
            hexvalue = _NAMED_COLORS[name]
            nr, ng, nb = int(hexvalue[1:3], 16), int(hexvalue[3:5], 16), int(hexvalue[5:7], 16)
            distance = (
                (cls._linearize(nr / 255) - lr) ** 2
                + (cls._linearize(ng / 255) - lg) ** 2
                + (cls._linearize(nb / 255) - lb) ** 2
            )
            if best_distance is None or distance < best_distance:
                best_name, best_distance = name, distance
        return {
            "name": best_name,
            "hex": _NAMED_COLORS[best_name],
            "distance": round(best_distance, 6),
        }

    # ------------------------------------------------------------------ #
    # Modes
    # ------------------------------------------------------------------ #

    def _run_convert(self, color: str, to_format: str) -> Dict[str, Any]:
        """Parse one color and re-emit it in the target format."""
        context = {"mode": "convert", "color": color, "to_format": to_format}
        channels = self.parse(color, context)
        if "error" in channels:
            return channels
        r, g, b, alpha = (
            channels["r"],
            channels["g"],
            channels["b"],
            channels["alpha"],
        )
        if to_format == "hex":
            result = self._to_hex(channels, force_alpha=False)
        elif to_format == "hex8":
            result = self._to_hex(channels, force_alpha=True)
        elif to_format == "rgb":
            result = self._to_rgb_string(channels)
        elif to_format == "hsl":
            result = self._to_hsl_string(channels)
        elif to_format == "hsv":
            result = self._to_hsv_string(channels)
        else:  # to_format == "name"
            name = self.exact_name(r, g, b)
            if name is None:
                nearest = self.nearest_named_color(r, g, b)
                return self._error_result(
                    context,
                    error_type="no_exact_name",
                    message=(
                        f"color #{r:02x}{g:02x}{b:02x} has no exact match "
                        f"among the embedded common CSS named colors; the "
                        f"nearest is {nearest['name']!r} ({nearest['hex']})"
                    ),
                )
            result = name
        return {**context, "result": result}

    def _run_info(self, color: str) -> Dict[str, Any]:
        """One color to every representation plus WCAG luminance data."""
        context = {"mode": "info", "color": color}
        channels = self.parse(color, context)
        if "error" in channels:
            return channels
        r, g, b, alpha = (
            channels["r"],
            channels["g"],
            channels["b"],
            channels["alpha"],
        )
        h, s, l = self._rgb_to_hsl(r, g, b)
        hv, sv, vv = self._rgb_to_hsv(r, g, b)
        luminance = self.relative_luminance(r, g, b)
        return {
            **context,
            "rgb": {"r": r, "g": g, "b": b, "alpha": alpha},
            "hex": self._to_hex(channels, force_alpha=False),
            "hex8": self._to_hex(channels, force_alpha=True),
            "rgb_string": self._to_rgb_string(channels),
            "hsl": {"h": h, "s": s, "l": l},
            "hsl_string": self._to_hsl_string(channels),
            "hsv": {"h": hv, "s": sv, "v": vv},
            "hsv_string": self._to_hsv_string(channels),
            "name": self.exact_name(r, g, b),
            "nearest_named_color": self.nearest_named_color(r, g, b),
            "luminance": luminance,
            "contrast_with_white": self.contrast_ratio(luminance, 1.0),
            "contrast_with_black": self.contrast_ratio(luminance, 0.0),
        }

    def _run_contrast(self, foreground: str, background: str) -> Dict[str, Any]:
        """WCAG contrast ratio of two opaque colors plus AA/AAA verdicts."""
        context = {"mode": "contrast", "foreground": foreground, "background": background}
        fg = self.parse(foreground, context)
        if "error" in fg:
            return fg
        bg = self.parse(background, context)
        if "error" in bg:
            return bg
        for label, channels in (("foreground", fg), ("background", bg)):
            if channels["alpha"] < 1.0:
                return self._error_result(
                    context,
                    error_type="alpha_not_supported",
                    message=(
                        f"{label} color has alpha "
                        f"{self._fmt_alpha(channels['alpha'])} < 1: the WCAG "
                        "contrast ratio is only defined for opaque colors — "
                        "composite the color over its background first"
                    ),
                )
        fg_l = self.relative_luminance(fg["r"], fg["g"], fg["b"])
        bg_l = self.relative_luminance(bg["r"], bg["g"], bg["b"])
        ratio = self.contrast_ratio(fg_l, bg_l)
        return {
            **context,
            "ratio": ratio,
            "ratio_display": f"{ratio:g}:1",
            "luminance": {"foreground": fg_l, "background": bg_l},
            "lighter": (
                "foreground" if fg_l > bg_l else "background" if bg_l > fg_l else "equal"
            ),
            "wcag": {
                "aa_normal_text": ratio >= 4.5,
                "aa_large_text": ratio >= 3.0,
                "aaa_normal_text": ratio >= 7.0,
                "aaa_large_text": ratio >= 4.5,
            },
        }
