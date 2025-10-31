# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/10/28 12:17
# @Author  : jerry.zzw 
# @Email   : jerry.zzw@antgroup.com
# @FileName: character_util.py


def show_au_start_banner():
    python_art_text = f"""
╔═════════════════════════════════════════════════════════╗
║   █ █ █▀▀ █   █▀▀ █▀█ █▄█ █▀▀   ▀█▀ █▀█                 ║
║   █▄█ █▀▀ █   █   █ █ █ █ █▀▀    █  █ █                 ║
║   ▀ ▀ ▀▀▀ ▀▀▀ ▀▀▀ ▀▀▀ ▀ ▀ ▀▀▀    ▀  ▀▀▀                 ║
║   █▀█ █▀▀ █▀▀ █▀█ ▀█▀ █ █ █▀█ ▀█▀ █ █ █▀▀ █▀▄ █▀▀ █▀▀   ║
║   █▀█ █ █ █▀▀ █ █  █  █ █ █ █  █  █ █ █▀▀ █▀▄ ▀▀█ █▀▀   ║
║   ▀ ▀ ▀▀▀ ▀▀▀ ▀ ▀  ▀  ▀▀▀ ▀ ▀ ▀▀▀  ▀  ▀▀▀ ▀ ▀ ▀▀▀ ▀▀▀   ║
╚═════════════════════════════════════════════════════════╝
"""
    blue_colors = [33]
    print_gradient_text(python_art_text, blue_colors)


def print_gradient_text(text, colors_range):
    length = len(text)
    result = []

    for i, char in enumerate(text):
        if length > 1:
            color_index = int((i / (length - 1)) * (len(colors_range) - 1))
        else:
            color_index = 0

        color_code = colors_range[min(color_index, len(colors_range) - 1)]
        result.append(f"\033[38;5;{color_code}m{char}")

    print(''.join(result) + "\033[0m")


if __name__ == "__main__":
    show_au_start_banner()
