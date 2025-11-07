# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/09/16 23:00
# @Author  : Libres-coder
# @Email   : liudi1366@gmail.com
# @FileName: run_demo.py
"""Run Prompt Generator Demo.

This script runs the prompt generator demonstration showing various use cases
and functionality of the prompt generation system.
"""
import sys
import os
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Import and run demo
from intelligence.test.prompt_generator_demo import main as run_demo


def main():
    """Main function to run the demo."""
    print("Starting Prompt Generator Demo")
    print("=" * 60)

    try:
        run_demo()
    except Exception as e:
        print(f"\nDemo execution failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
