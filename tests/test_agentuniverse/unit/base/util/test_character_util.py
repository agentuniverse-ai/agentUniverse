# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/08/13 10:00
# @Author  : kaichuan
# @FileName: test_character_util.py
"""Unit tests for character_util gradient printing."""

import pytest

from agentuniverse.base.util.character_util import (
    print_gradient_text,
    show_au_start_banner,
)


class TestPrintGradientText:
    """Test print_gradient_text ANSI escape generation."""

    def test_single_color_applies_to_every_char(self, capsys):
        """A one-entry color range paints every character that color."""
        print_gradient_text("AB", [33])
        out = capsys.readouterr().out
        assert out == "\033[38;5;33mA\033[38;5;33mB\033[0m\n"

    def test_gradient_maps_positions_to_colors(self, capsys):
        """Each position in a 3-char text maps to its corresponding color."""
        print_gradient_text("ABC", [1, 2, 3])
        out = capsys.readouterr().out
        assert out == (
            "\033[38;5;1mA\033[38;5;2mB\033[38;5;3mC\033[0m\n")

    def test_single_char_uses_first_color(self, capsys):
        """A length-1 text uses the first color in the range."""
        print_gradient_text("X", [5, 6])
        out = capsys.readouterr().out
        assert out == "\033[38;5;5mX\033[0m\n"

    def test_last_char_uses_last_color(self, capsys):
        """The final character of a longer gradient gets the last color."""
        print_gradient_text("ABCDEFGH", [10, 20])
        out = capsys.readouterr().out
        # Every character but the last uses the first color, the last uses 20.
        assert out.count("\033[38;5;10m") == 7
        assert "\033[38;5;20mH" in out

    def test_output_terminates_with_reset(self, capsys):
        """The printed output always ends with the ANSI reset sequence."""
        print_gradient_text("hi", [1, 2, 3])
        out = capsys.readouterr().out
        assert out.endswith("\033[0m\n")


class TestShowAuStartBanner:
    """Test the startup banner helper."""

    def test_banner_prints_colored_text(self, capsys):
        """show_au_start_banner emits colored output ending in a reset."""
        show_au_start_banner()
        out = capsys.readouterr().out
        assert "\033[38;5;33m" in out
        assert out.rstrip("\n").endswith("\033[0m")
        assert len(out) > 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
