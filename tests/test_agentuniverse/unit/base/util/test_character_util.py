# -*- coding: utf-8 -*-
"""Unit tests for agentuniverse.base.util.character_util."""

from agentuniverse.base.util.character_util import (
    print_gradient_text,
    show_au_start_banner,
)


class TestPrintGradientText:
    """Tests for the ANSI gradient text printer."""

    def test_single_color_single_character(self, capsys):
        print_gradient_text("x", [33])
        captured = capsys.readouterr()
        assert captured.out == "\033[38;5;33mx\033[0m\n"

    def test_single_color_constant_throughout(self, capsys):
        print_gradient_text("ab", [33])
        captured = capsys.readouterr()
        assert captured.out == "\033[38;5;33ma\033[38;5;33mb\033[0m\n"

    def test_color_gradient_spread(self, capsys):
        print_gradient_text("abc", [10, 20])
        captured = capsys.readouterr()
        assert captured.out == (
            "\033[38;5;10ma\033[38;5;10mb\033[38;5;20mc\033[0m\n"
        )

    def test_gradient_with_three_colors(self, capsys):
        print_gradient_text("abcd", [1, 2, 3])
        captured = capsys.readouterr()
        assert captured.out == (
            "\033[38;5;1ma\033[38;5;1mb\033[38;5;2mc\033[38;5;3md\033[0m\n"
        )

    def test_empty_text_prints_only_reset(self, capsys):
        print_gradient_text("", [33])
        captured = capsys.readouterr()
        assert captured.out == "\033[0m\n"

    def test_does_not_modify_input_text(self, capsys):
        text = "hi"
        print_gradient_text(text, [33])
        capsys.readouterr()
        assert text == "hi"


class TestShowAuStartBanner:
    """Tests for the start-up banner printer."""

    def test_prints_banner_art(self, capsys):
        show_au_start_banner()
        captured = capsys.readouterr()
        assert "╔" in captured.out
        assert "╝" in captured.out
        assert captured.out.rstrip("\n").endswith("\033[0m")

    def test_returns_none(self):
        assert show_au_start_banner() is None
