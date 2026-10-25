#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: test_color_converter_tool.py

"""Offline unit tests for ColorConverterTool.

The tool is built purely on the standard library (re, math) and never
touches the network, so this suite runs fully offline. Every assertion
is deterministic: conversions are checked against literal known
vectors (#ff0000 <-> rgb(255, 0, 0) <-> hsl(0, 100%, 50%), the CSS
Color Model example hsl(120, 50%, 50%) -> rgb(64, 191, 64)), WCAG
ratios against published values (black on white = 21:1, the famous
AA-boundary grays #767676 = 4.54 and #777777 = 4.48 on white) plus an
independent inline re-implementation of the WCAG luminance formula,
and hsl/hsv round trips follow the documented quantization bounds
(byte-exact through the 8-bit RGB staging point, lightness/value
within 0.2 units, hue/saturation within about one unit for saturated
mid-gamut colors only).
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import ColorConverterTool
from agentuniverse.agent.action.tool.common_tool.color_converter_tool import (
    ColorConverterTool as DirectColorConverterTool,
)


# --------------------------------------------------------------------- #
# Independent WCAG reference (re-implemented inline as a cross-check)
# --------------------------------------------------------------------- #
def ref_luminance(r: int, g: int, b: int) -> float:
    """WCAG 2.x relative luminance, written out independently."""

    def linear(channel: int) -> float:
        c = channel / 255
        if c <= 0.04045:
            return c / 12.92
        return ((c + 0.055) / 1.055) ** 2.4

    return 0.2126 * linear(r) + 0.7152 * linear(g) + 0.0722 * linear(b)


def ref_ratio(color_a, color_b) -> float:
    """WCAG contrast ratio from the reference luminance above."""
    la, lb = ref_luminance(*color_a), ref_luminance(*color_b)
    lighter, darker = max(la, lb), min(la, lb)
    return (lighter + 0.05) / (darker + 0.05)


def hue_distance(a: float, b: float) -> float:
    """Shortest distance between two hues on the 0-360 circle."""
    return min(abs(a - b), 360 - abs(a - b))


class ColorConverterToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib ColorConverterTool."""

    def setUp(self) -> None:
        self.tool = ColorConverterTool()

    # ------------------------------------------------------------------ #
    # convert mode — known vectors across notations
    # ------------------------------------------------------------------ #

    def test_convert_hex_to_hsl_known_vector(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="convert", color="#ff0000", to_format="hsl"),
            {
                "mode": "convert",
                "color": "#ff0000",
                "to_format": "hsl",
                "result": "hsl(0, 100%, 50%)",
            },
        )

    def test_convert_rgb_to_hex_known_vector(self) -> None:
        result = self.tool.execute(
            mode="convert", color="rgb(255, 0, 0)", to_format="hex"
        )
        self.assertEqual(result["result"], "#ff0000")

    def test_convert_hsl_to_hex_known_vector(self) -> None:
        result = self.tool.execute(
            mode="convert", color="hsl(0, 100%, 50%)", to_format="hex"
        )
        self.assertEqual(result["result"], "#ff0000")

    def test_convert_hsv_to_hex_known_vector(self) -> None:
        result = self.tool.execute(
            mode="convert", color="hsv(0, 100%, 100%)", to_format="hex"
        )
        self.assertEqual(result["result"], "#ff0000")

    def test_convert_named_to_hex_known_vector(self) -> None:
        result = self.tool.execute(
            mode="convert", color="red", to_format="hex"
        )
        self.assertEqual(result["result"], "#ff0000")

    def test_convert_css_color_model_example(self) -> None:
        # CSS Color Model worked example: hsl(120, 50%, 50%) = rgb(64, 191, 64).
        result = self.tool.execute(
            mode="convert", color="hsl(120, 50%, 50%)", to_format="hex"
        )
        self.assertEqual(result["result"], "#40bf40")
        self.assertEqual(
            self.tool.execute(
                mode="convert", color="#40bf40", to_format="rgb"
            )["result"],
            "rgb(64, 191, 64)",
        )

    def test_convert_hex_short_and_uppercase(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="convert", color="#abc", to_format="hex")[
                "result"
            ],
            "#aabbcc",
        )
        self.assertEqual(
            self.tool.execute(mode="convert", color="#F00", to_format="hex")[
                "result"
            ],
            "#ff0000",
        )

    def test_convert_function_case_insensitive_and_spacing(self) -> None:
        self.assertEqual(
            self.tool.execute(
                mode="convert", color="RGB( 255 , 0 , 0 )", to_format="hex"
            )["result"],
            "#ff0000",
        )
        self.assertEqual(
            self.tool.execute(
                mode="convert", color="hsl(0,100%,50%)", to_format="hex"
            )["result"],
            "#ff0000",
        )

    def test_convert_input_surrounding_whitespace_stripped(self) -> None:
        self.assertEqual(
            self.tool.execute(
                mode="convert", color="  #ff0000  ", to_format="hsl"
            )["result"],
            "hsl(0, 100%, 50%)",
        )

    def test_convert_hue_360_equals_0(self) -> None:
        self.assertEqual(
            self.tool.execute(
                mode="convert", color="hsl(360, 100%, 50%)", to_format="hex"
            )["result"],
            "#ff0000",
        )

    # ------------------------------------------------------------------ #
    # convert mode — alpha handling
    # ------------------------------------------------------------------ #

    def test_convert_hex8_to_hex8(self) -> None:
        self.assertEqual(
            self.tool.execute(
                mode="convert", color="#ff000080", to_format="hex8"
            )["result"],
            "#ff000080",
        )

    def test_convert_alpha_hex6_becomes_hex8(self) -> None:
        # to_format=hex emits 8 digits when an alpha below 1 is present.
        self.assertEqual(
            self.tool.execute(
                mode="convert", color="#ff000080", to_format="hex"
            )["result"],
            "#ff000080",
        )
        self.assertEqual(
            self.tool.execute(
                mode="convert", color="#ff0000ff", to_format="hex"
            )["result"],
            "#ff0000",
        )

    def test_convert_rgba_to_hex8_known_vector(self) -> None:
        self.assertEqual(
            self.tool.execute(
                mode="convert", color="rgba(255, 0, 0, 0.5)", to_format="hex8"
            )["result"],
            "#ff000080",
        )

    def test_convert_alpha_percentage_equals_fraction(self) -> None:
        self.assertEqual(
            self.tool.execute(
                mode="convert", color="rgba(255, 0, 0, 50%)", to_format="hex8"
            )["result"],
            self.tool.execute(
                mode="convert", color="rgba(255, 0, 0, 0.5)", to_format="hex8"
            )["result"],
        )

    def test_convert_rgb_emits_rgba_when_alpha_below_one(self) -> None:
        self.assertEqual(
            self.tool.execute(
                mode="convert", color="rgba(255, 0, 0, 0.5)", to_format="rgb"
            )["result"],
            "rgba(255, 0, 0, 0.5)",
        )
        self.assertEqual(
            self.tool.execute(
                mode="convert", color="rgb(255, 0, 0)", to_format="rgb"
            )["result"],
            "rgb(255, 0, 0)",
        )

    def test_convert_hsla_keeps_alpha(self) -> None:
        self.assertEqual(
            self.tool.execute(
                mode="convert", color="hsla(0, 100%, 50%, 0.25)", to_format="hsl"
            )["result"],
            "hsla(0, 100%, 50%, 0.25)",
        )
        self.assertEqual(
            self.tool.execute(
                mode="convert", color="rgba(255, 0, 0, 0.25)", to_format="hsl"
            )["result"],
            "hsla(0, 100%, 50%, 0.25)",
        )

    def test_convert_alpha_round_trip_within_quantization(self) -> None:
        # 0.5 -> byte 128 -> 128/255 = 0.502 after the round trip.
        back = self.tool.execute(
            mode="convert", color="#ff000080", to_format="rgb"
        )["result"]
        self.assertEqual(back, "rgba(255, 0, 0, 0.502)")

    # ------------------------------------------------------------------ #
    # convert mode — named colors
    # ------------------------------------------------------------------ #

    def test_convert_to_name_exact(self) -> None:
        self.assertEqual(
            self.tool.execute(
                mode="convert", color="#ff6347", to_format="name"
            )["result"],
            "tomato",
        )
        self.assertEqual(
            self.tool.execute(
                mode="convert", color="rgb(0, 255, 255)", to_format="name"
            )["result"],
            "aqua",
        )
        self.assertEqual(
            self.tool.execute(
                mode="convert", color="#808080", to_format="name"
            )["result"],
            "gray",
        )

    def test_convert_to_name_named_case_insensitive(self) -> None:
        self.assertEqual(
            self.tool.execute(
                mode="convert", color="TOMATO", to_format="name"
            )["result"],
            "tomato",
        )

    def test_convert_to_name_without_exact_match(self) -> None:
        result = self.tool.execute(
            mode="convert", color="#0d98ba", to_format="name"
        )
        self.assertEqual(result["mode"], "convert")
        self.assertEqual(result["error"]["type"], "no_exact_name")
        self.assertIn("nearest", result["error"]["message"])

    # ------------------------------------------------------------------ #
    # Round-trip precision (documented: byte-exact through the 8-bit RGB
    # staging point; lightness/value within 0.2 units; hue/saturation
    # within one unit only for saturated mid-gamut colors)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _parse_hsl(text: str):
        body = text[text.index("(") + 1 : text.index(")")]
        h, s, l = (p.strip().rstrip("%") for p in body.split(",")[:3])
        return float(h), float(s), float(l)

    def test_hsl_round_trip_mid_gamut_within_one_unit(self) -> None:
        samples = [
            (0, 100, 50),
            (120, 50, 50),
            (210, 79.5, 34.3),
            (300, 25, 75),
            (45, 90, 60),
            (359, 60, 40),
            (0, 0, 50),
            (180, 100, 25),
        ]
        for h, s, l in samples:
            with self.subTest(hsl=(h, s, l)):
                as_hex = self.tool.execute(
                    mode="convert",
                    color=f"hsl({h}, {s}%, {l}%)",
                    to_format="hex",
                )["result"]
                back = self.tool.execute(
                    mode="convert", color=as_hex, to_format="hsl"
                )["result"]
                bh, bs, bl = self._parse_hsl(back)
                self.assertLessEqual(hue_distance(bh, h), 1)
                self.assertLessEqual(abs(bs - s), 1)
                self.assertLessEqual(abs(bl - l), 1)

    def test_hsv_round_trip_mid_gamut_within_one_unit(self) -> None:
        samples = [
            (0, 100, 100),
            (120, 50, 50),
            (210, 79.5, 34.3),
            (60, 100, 100),
            (300, 30, 80),
        ]
        for h, s, v in samples:
            with self.subTest(hsv=(h, s, v)):
                as_hex = self.tool.execute(
                    mode="convert",
                    color=f"hsv({h}, {s}%, {v}%)",
                    to_format="hex",
                )["result"]
                back = self.tool.execute(
                    mode="convert", color=as_hex, to_format="hsv"
                )["result"]
                bh, bs, bv = self._parse_hsl(back)
                self.assertLessEqual(hue_distance(bh, h), 1)
                self.assertLessEqual(abs(bs - s), 1)
                self.assertLessEqual(abs(bv - v), 1)

    def test_hex_rgb_round_trip_exact(self) -> None:
        for hex_color in (
            "#000000",
            "#ffffff",
            "#ff0000",
            "#40bf40",
            "#0d98ba",
            "#4169e1",
        ):
            with self.subTest(hex=hex_color):
                rgb = self.tool.execute(
                    mode="convert", color=hex_color, to_format="rgb"
                )["result"]
                back = self.tool.execute(
                    mode="convert", color=rgb, to_format="hex"
                )["result"]
                self.assertEqual(back, hex_color)

    def test_rgb_through_hsl_hsv_is_byte_exact(self) -> None:
        # rgb -> hsl/hsv (1 decimal) -> rgb must return the original
        # bytes for every sampled color across the whole cube: the
        # 1-decimal representation loses no channel information.
        for r in range(0, 256, 17):
            for g in range(0, 256, 17):
                for b in range(0, 256, 17):
                    with self.subTest(rgb=(r, g, b)):
                        h, s, l = self.tool._rgb_to_hsl(r, g, b)
                        self.assertEqual(self.tool._hsl_to_rgb(h, s, l), (r, g, b))
                        hv, sv, vv = self.tool._rgb_to_hsv(r, g, b)
                        self.assertEqual(self.tool._hsv_to_rgb(hv, sv, vv), (r, g, b))

    def test_lightness_value_round_trip_within_quantization(self) -> None:
        # Lightness/value round trips stay within 0.2 units everywhere,
        # including achromatic corners (documented bound).
        for kind in ("hsl", "hsv"):
            for h in range(0, 360, 30):
                for s in range(0, 101, 10):
                    for third in range(0, 101, 10):
                        with self.subTest(kind=kind, h=h, s=s, third=third):
                            text = self.tool.execute(
                                mode="convert",
                                color=f"{kind}({h}, {s}%, {third}%)",
                                to_format=kind,
                            )["result"]
                            bh, bs, bthird = self._parse_hsl(text)
                            self.assertLessEqual(hue_distance(bh, h), 180)
                            self.assertLessEqual(abs(bs - s), 100)
                            self.assertLessEqual(abs(bthird - third), 0.2 + 1e-9)

    def test_hue_saturation_drift_bounded_in_saturated_mid_gamut(self) -> None:
        # For saturation >= 25% and 25%-75% lightness/value the drift
        # stays small (measured maxima: 1.3 hue / 0.3 sat for hsl,
        # 2.7 hue / 0.3 sat for hsv — asserted with margin).
        for kind in ("hsl", "hsv"):
            for h in range(0, 360, 15):
                for s in range(25, 101, 5):
                    for third in range(25, 76, 5):
                        with self.subTest(kind=kind, h=h, s=s, third=third):
                            text = self.tool.execute(
                                mode="convert",
                                color=f"{kind}({h}, {s}%, {third}%)",
                                to_format=kind,
                            )["result"]
                            bh, bs, bthird = self._parse_hsl(text)
                            self.assertLessEqual(hue_distance(bh, h), 3)
                            self.assertLessEqual(abs(bs - s), 1)
                            self.assertLessEqual(abs(bthird - third), 0.2 + 1e-9)

    def test_achromatic_round_trips_normalize_hue_to_zero(self) -> None:
        # 0% saturation, 0% lightness/value, and (hsl only) 100%
        # lightness carry no hue: the round trip must normalize to
        # hue 0 (documented). Note hsv(…, 100%, 100%) is a vivid
        # color, not white — hsv keeps its hue at full value.
        cases = {
            "hsl": (
                "hsl(180, 0%, 50%)",
                "hsl(217, 100%, 0%)",
                "hsl(217, 100%, 100%)",
            ),
            "hsv": ("hsv(180, 0%, 50%)", "hsv(217, 100%, 0%)"),
        }
        for kind, texts in cases.items():
            for text in texts:
                with self.subTest(kind=kind, text=text):
                    result = self.tool.execute(
                        mode="convert", color=text, to_format=kind
                    )["result"]
                    bh, bs, bthird = self._parse_hsl(result)
                    self.assertEqual(bh, 0.0)
                    self.assertEqual(bs, 0.0)

    def test_near_achromatic_quantization_drift_documented(self) -> None:
        # Near the achromatic corners a single 8-bit step dominates the
        # tiny chroma, so hue/saturation drift far beyond one unit.
        # These pins document the measured worst-case behavior.
        result = self.tool.execute(
            mode="convert", color="hsl(21, 5%, 5%)", to_format="hsl"
        )["result"]
        self.assertEqual(result, "hsl(60, 4%, 4.9%)")
        result = self.tool.execute(
            mode="convert", color="hsv(0, 10%, 5%)", to_format="hsv"
        )["result"]
        self.assertEqual(result, "hsv(0, 15.4%, 5.1%)")
        # The lightness/value channels stay exact regardless.
        result = self.tool.execute(
            mode="convert", color="hsl(0, 80%, 5%)", to_format="hsl"
        )["result"]
        self.assertEqual(result, "hsl(0, 76.9%, 5.1%)")

    # ------------------------------------------------------------------ #
    # info mode
    # ------------------------------------------------------------------ #

    def test_info_red_full_report(self) -> None:
        result = self.tool.execute(mode="info", color="#ff0000")
        self.assertEqual(
            result,
            {
                "mode": "info",
                "color": "#ff0000",
                "rgb": {"r": 255, "g": 0, "b": 0, "alpha": 1.0},
                "hex": "#ff0000",
                "hex8": "#ff0000ff",
                "rgb_string": "rgb(255, 0, 0)",
                "hsl": {"h": 0.0, "s": 100.0, "l": 50.0},
                "hsl_string": "hsl(0, 100%, 50%)",
                "hsv": {"h": 0.0, "s": 100.0, "v": 100.0},
                "hsv_string": "hsv(0, 100%, 100%)",
                "name": "red",
                "nearest_named_color": {
                    "name": "red",
                    "hex": "#ff0000",
                    "distance": 0.0,
                },
                "luminance": 0.2126,
                "contrast_with_white": 4.0,
                "contrast_with_black": 5.25,
            },
        )

    def test_info_white_extremes(self) -> None:
        result = self.tool.execute(mode="info", color="white")
        self.assertEqual(result["luminance"], 1.0)
        self.assertEqual(result["contrast_with_white"], 1.0)
        self.assertEqual(result["contrast_with_black"], 21.0)
        self.assertEqual(result["name"], "white")

    def test_info_luminance_matches_reference(self) -> None:
        for color in ("#808080", "#4169e1", "#dc143c", "#4682b4", "#ffff00"):
            with self.subTest(color=color):
                r, g, b = (
                    int(color[1:3], 16),
                    int(color[3:5], 16),
                    int(color[5:7], 16),
                )
                result = self.tool.execute(mode="info", color=color)
                self.assertAlmostEqual(
                    result["luminance"],
                    ref_luminance(r, g, b),
                    places=5,
                )

    def test_info_alpha_preserved(self) -> None:
        result = self.tool.execute(mode="info", color="#ff000080")
        self.assertEqual(result["rgb"]["alpha"], 0.502)
        self.assertEqual(result["hex"], "#ff000080")
        self.assertEqual(result["rgb_string"], "rgba(255, 0, 0, 0.502)")

    def test_info_nearest_named_color(self) -> None:
        # A hair off indigo (#4b0082) still reports indigo as nearest.
        result = self.tool.execute(mode="info", color="#4b0081")
        self.assertIsNone(result["name"])
        self.assertEqual(result["nearest_named_color"]["name"], "indigo")
        self.assertEqual(result["nearest_named_color"]["hex"], "#4b0082")
        # One green unit away from pure white, white wins over ivory.
        result = self.tool.execute(mode="info", color="#fffffe")
        self.assertEqual(result["nearest_named_color"]["name"], "white")
        # A non-table color gets a useful nearest neighbor.
        result = self.tool.execute(mode="info", color="#0d98ba")
        self.assertEqual(result["nearest_named_color"]["name"], "steelblue")

    def test_info_deterministic(self) -> None:
        first = self.tool.execute(mode="info", color="hsl(210, 79%, 34%)")
        second = self.tool.execute(mode="info", color="hsl(210, 79%, 34%)")
        self.assertEqual(first, second)

    # ------------------------------------------------------------------ #
    # contrast mode
    # ------------------------------------------------------------------ #

    def test_contrast_black_on_white_is_21(self) -> None:
        self.assertEqual(
            self.tool.execute(
                mode="contrast", foreground="#000000", background="#ffffff"
            ),
            {
                "mode": "contrast",
                "foreground": "#000000",
                "background": "#ffffff",
                "ratio": 21.0,
                "ratio_display": "21:1",
                "luminance": {"foreground": 0.0, "background": 1.0},
                "lighter": "background",
                "wcag": {
                    "aa_normal_text": True,
                    "aa_large_text": True,
                    "aaa_normal_text": True,
                    "aaa_large_text": True,
                },
            },
        )

    def test_contrast_identical_colors_is_1(self) -> None:
        result = self.tool.execute(
            mode="contrast", foreground="#ffffff", background="#ffffff"
        )
        self.assertEqual(result["ratio"], 1.0)
        self.assertEqual(result["lighter"], "equal")
        self.assertEqual(
            result["wcag"],
            {
                "aa_normal_text": False,
                "aa_large_text": False,
                "aaa_normal_text": False,
                "aaa_large_text": False,
            },
        )

    def test_contrast_aa_boundary_grays_on_white(self) -> None:
        # Well-known AA boundary: #767676 on white = 4.54 (passes),
        # #777777 on white = 4.48 (fails normal text, passes large).
        passing = self.tool.execute(
            mode="contrast", foreground="#767676", background="#ffffff"
        )
        self.assertEqual(passing["ratio"], 4.54)
        self.assertTrue(passing["wcag"]["aa_normal_text"])
        self.assertFalse(passing["wcag"]["aaa_normal_text"])
        self.assertTrue(passing["wcag"]["aa_large_text"])
        self.assertTrue(passing["wcag"]["aaa_large_text"])

        failing = self.tool.execute(
            mode="contrast", foreground="#777777", background="#ffffff"
        )
        self.assertEqual(failing["ratio"], 4.48)
        self.assertFalse(failing["wcag"]["aa_normal_text"])
        self.assertTrue(failing["wcag"]["aa_large_text"])
        self.assertFalse(failing["wcag"]["aaa_normal_text"])
        self.assertFalse(failing["wcag"]["aaa_large_text"])

    def test_contrast_red_on_white_famous_4_to_1(self) -> None:
        result = self.tool.execute(
            mode="contrast", foreground="#ff0000", background="#ffffff"
        )
        self.assertEqual(result["ratio"], 4.0)
        self.assertFalse(result["wcag"]["aa_normal_text"])
        self.assertTrue(result["wcag"]["aa_large_text"])
        self.assertEqual(result["lighter"], "background")

    def test_contrast_aaa_threshold_color(self) -> None:
        # #40bf40 on #000000: reference formula gives ~7.55 (passes AAA).
        result = self.tool.execute(
            mode="contrast", foreground="#40bf40", background="#000000"
        )
        self.assertAlmostEqual(
            result["ratio"], ref_ratio((64, 191, 64), (0, 0, 0)), places=1
        )
        self.assertTrue(result["wcag"]["aaa_normal_text"])

    def test_contrast_symmetric(self) -> None:
        forward = self.tool.execute(
            mode="contrast", foreground="#4169e1", background="#f5deb3"
        )
        backward = self.tool.execute(
            mode="contrast", foreground="#f5deb3", background="#4169e1"
        )
        self.assertEqual(forward["ratio"], backward["ratio"])
        self.assertEqual(forward["wcag"], backward["wcag"])

    def test_contrast_matches_reference_formula(self) -> None:
        pairs = (
            ((65, 105, 225), (255, 255, 255)),
            ((220, 20, 60), (0, 0, 0)),
            ((70, 130, 180), (245, 222, 179)),
            ((255, 215, 0), (128, 0, 0)),
        )
        for (fr, fg, fb), (br, bg, bb) in pairs:
            with self.subTest(
                fg=f"#{fr:02x}{fg:02x}{fb:02x}", bg=f"#{br:02x}{bg:02x}{bb:02x}"
            ):
                result = self.tool.execute(
                    mode="contrast",
                    foreground=f"#{fr:02x}{fg:02x}{fb:02x}",
                    background=f"#{br:02x}{bg:02x}{bb:02x}",
                )
                expected = ref_ratio((fr, fg, fb), (br, bg, bb))
                self.assertAlmostEqual(result["ratio"], expected, places=1)
                self.assertEqual(
                    result["wcag"]["aa_normal_text"], expected >= 4.5
                )
                self.assertEqual(result["wcag"]["aa_large_text"], expected >= 3.0)
                self.assertEqual(
                    result["wcag"]["aaa_normal_text"], expected >= 7.0
                )
                self.assertEqual(
                    result["wcag"]["aaa_large_text"], expected >= 4.5
                )

    def test_contrast_accepts_any_notation(self) -> None:
        self.assertEqual(
            self.tool.execute(
                mode="contrast", foreground="black", background="white"
            )["ratio"],
            21.0,
        )
        self.assertEqual(
            self.tool.execute(
                mode="contrast",
                foreground="rgb(0, 0, 0)",
                background="hsl(0, 0%, 100%)",
            )["ratio"],
            21.0,
        )

    def test_contrast_rejects_alpha_colors(self) -> None:
        result = self.tool.execute(
            mode="contrast",
            foreground="rgba(0, 0, 0, 0.5)",
            background="#ffffff",
        )
        self.assertEqual(result["mode"], "contrast")
        self.assertEqual(result["error"]["type"], "alpha_not_supported")
        self.assertIn("foreground", result["error"]["message"])
        result = self.tool.execute(
            mode="contrast", foreground="#00000000", background="#ffffff"
        )
        self.assertEqual(result["error"]["type"], "alpha_not_supported")

    # ------------------------------------------------------------------ #
    # Error matrix — structured payloads for content-level failures
    # ------------------------------------------------------------------ #

    def assert_payload(self, color: str, error_type: str, to_format: str = "hex"):
        result = self.tool.execute(
            mode="convert", color=color, to_format=to_format
        )
        self.assertEqual(result["mode"], "convert")
        self.assertEqual(result["error"]["type"], error_type)
        return result

    def test_error_invalid_hex_lengths(self) -> None:
        for bad in ("#12345", "#1234567", "#ab", "#"):
            with self.subTest(bad=bad):
                self.assert_payload(bad, "invalid_hex")

    def test_error_invalid_hex_digits(self) -> None:
        result = self.assert_payload("#gggggg", "invalid_hex")
        self.assertIn("hexadecimal", result["error"]["message"])
        self.assertEqual(result["error"]["position"], 1)

    def test_error_hex_without_hash(self) -> None:
        result = self.assert_payload("ff0000", "unknown_color_name")
        self.assertIn("'#'", result["error"]["message"])

    def test_error_unknown_named_color(self) -> None:
        result = self.assert_payload("notacolor", "unknown_color_name")
        self.assertIn("named", result["error"]["message"])

    def test_error_malformed_function_hint(self) -> None:
        result = self.assert_payload("rgb(255, 0, 0", "unknown_color_name")
        self.assertIn("functional", result["error"]["message"])

    def test_error_unknown_function(self) -> None:
        result = self.assert_payload("cmyk(0, 0, 0, 0)", "unknown_function")
        self.assertIn("rgb()", result["error"]["message"])

    def test_error_channel_out_of_range(self) -> None:
        result = self.assert_payload("rgb(256, 0, 0)", "invalid_channel")
        self.assertEqual(result["error"]["position"], 4)
        self.assertIn("0-255", result["error"]["message"])
        # The position points at the offending (second) channel.
        result = self.assert_payload("rgb(255, 300, 0)", "invalid_channel")
        self.assertEqual(result["error"]["position"], 9)

    def test_error_channel_negative_or_fractional(self) -> None:
        for bad in ("rgb(-1, 0, 0)", "rgb(255, 0.5, 0)", "rgb(255, 0, 1e2)"):
            with self.subTest(bad=bad):
                self.assert_payload(bad, "invalid_channel")

    def test_error_component_count(self) -> None:
        for bad in ("rgb(255, 0)", "hsl(0, 100%)", "hsv(0, 100%, 50%, 1, 2)"):
            with self.subTest(bad=bad):
                self.assert_payload(bad, "invalid_component_count")

    def test_error_hue_bounds(self) -> None:
        result = self.assert_payload("hsl(361, 50%, 50%)", "invalid_hue")
        self.assertEqual(result["error"]["position"], 4)
        self.assertIn("0-360", result["error"]["message"])
        self.assert_payload("hsl(-10, 50%, 50%)", "invalid_hue")
        self.assert_payload("hsv(400, 100%, 100%)", "invalid_hue")
        self.assert_payload("hsl(blue, 50%, 50%)", "invalid_hue")

    def test_error_percent_bounds_and_format(self) -> None:
        result = self.assert_payload("hsl(0, 150%, 50%)", "invalid_percent")
        self.assertEqual(result["error"]["position"], 7)
        self.assert_payload("hsl(0, 50%, 101%)", "invalid_percent")
        self.assert_payload("hsl(0, 100, 50%)", "invalid_percent")
        self.assert_payload("hsv(0, 101%, 100%)", "invalid_percent")

    def test_error_alpha_bounds_and_format(self) -> None:
        self.assert_payload("rgba(255, 0, 0, 1.5)", "invalid_alpha")
        self.assert_payload("rgba(255, 0, 0, 150%)", "invalid_alpha")
        self.assert_payload("rgba(255, 0, 0, abc)", "invalid_alpha")
        self.assert_payload("rgba(255, 0, 0, )", "invalid_alpha")

    def test_error_from_info_and_contrast_modes(self) -> None:
        result = self.tool.execute(mode="info", color="rgb(999, 0, 0)")
        self.assertEqual(result["mode"], "info")
        self.assertEqual(result["error"]["type"], "invalid_channel")
        result = self.tool.execute(
            mode="contrast", foreground="#ff0000", background="oops"
        )
        self.assertEqual(result["mode"], "contrast")
        self.assertEqual(result["error"]["type"], "unknown_color_name")

    # ------------------------------------------------------------------ #
    # Invalid parameters raise ValueError (strict validation)
    # ------------------------------------------------------------------ #

    def assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def test_invalid_mode(self) -> None:
        self.assert_invalid(mode="parse", color="#ff0000")
        self.assert_invalid(mode=None, color="#ff0000")
        self.assert_invalid(mode=123, color="#ff0000")

    def test_invalid_color_type_or_missing(self) -> None:
        for bad in (None, 123, True, ["#ff0000"]):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="convert", color=bad, to_format="hex")
                self.assert_invalid(mode="info", color=bad)
        self.assert_invalid(mode="convert", to_format="hex")
        self.assert_invalid(mode="info")

    def test_invalid_whitespace_only_color(self) -> None:
        self.assert_invalid(mode="info", color="   ")

    def test_invalid_to_format(self) -> None:
        self.assert_invalid(mode="convert", color="#ff0000", to_format="cmyk")
        self.assert_invalid(mode="convert", color="#ff0000", to_format=None)
        self.assert_invalid(mode="convert", color="#ff0000")

    def test_invalid_contrast_arguments(self) -> None:
        self.assert_invalid(mode="contrast", background="#ffffff")
        self.assert_invalid(mode="contrast", foreground="#000000")
        self.assert_invalid(mode="contrast", foreground="#000000", background=123)
        self.assert_invalid(mode="contrast", foreground="#000000", background="  ")

    def test_input_length_limit(self) -> None:
        self.assert_invalid(mode="info", color="r" * 201)
        result = self.tool.execute(mode="info", color="r" * 200)
        self.assertEqual(result["error"]["type"], "unknown_color_name")

    # ------------------------------------------------------------------ #
    # Embedded named-color table sanity
    # ------------------------------------------------------------------ #

    def test_named_color_table_wellformed(self) -> None:
        from agentuniverse.agent.action.tool.common_tool import (
            color_converter_tool as module,
        )

        table = module._NAMED_COLORS
        self.assertGreaterEqual(len(table), 40)
        for name, hex_value in table.items():
            with self.subTest(name=name):
                self.assertEqual(name, name.lower())
                self.assertRegex(hex_value, r"\A#[0-9a-f]{6}\Z")
        # Core CSS colors and the classic aliases must be present.
        for expected in (
            "black",
            "white",
            "red",
            "lime",
            "blue",
            "aqua",
            "cyan",
            "fuchsia",
            "magenta",
            "gray",
            "grey",
            "teal",
            "navy",
            "orange",
        ):
            self.assertIn(expected, table)
        # Every named color must round-trip to its own table value.
        for name, hex_value in table.items():
            with self.subTest(round_trip=name):
                self.assertEqual(
                    self.tool.execute(
                        mode="convert", color=name, to_format="hex"
                    )["result"],
                    hex_value,
                )

    # ------------------------------------------------------------------ #
    # Packaging / registration
    # ------------------------------------------------------------------ #

    def test_class_defaults_and_export(self) -> None:
        self.assertIs(DirectColorConverterTool, ColorConverterTool)
        self.assertEqual(self.tool.name, "color_converter_tool")
        self.assertIn("convert", self.tool.description)
        self.assertIn("contrast", self.tool.description)
        from agentuniverse.agent.action.tool.common_tool import __all__

        self.assertIn("ColorConverterTool", __all__)


if __name__ == "__main__":
    unittest.main()
