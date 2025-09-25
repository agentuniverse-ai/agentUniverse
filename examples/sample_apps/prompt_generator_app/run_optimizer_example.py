# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/09/16 23:00
# @Author  : Libres-coder
# @Email   : liudi1366@gmail.com
# @FileName: run_optimizer_demo.py

"""Prompt optimizer demonstration application startup script.

Dedicated demonstration for prompt optimization functionality.
"""

import sys
import os
from pathlib import Path

# Add project root directory to Python path
app_root = Path(__file__).parent
project_root = app_root.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import optimizer demo modules
from intelligence.test.prompt_optimizer_demo import (
    demo_basic_prompt_optimization,
    demo_advanced_prompt_optimization,
    demo_yaml_prompt_optimization
)

if __name__ == '__main__':
    print("=" * 60)
    print("agentUniverse Prompt Optimizer Demonstration")
    print("=" * 60)

    demo_basic_prompt_optimization()
    print("\n" + "=" * 60)
    demo_advanced_prompt_optimization()
    print("\n" + "=" * 60)
    demo_yaml_prompt_optimization()

    print("\nPrompt optimizer demonstration completed!")
