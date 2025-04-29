#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/03/02 02:50
# @Author  : zhouxiaoji
# @Email   : zh_xiaoji@qq.com
# @FileName: json_util.py
import json
import re
from typing import Dict, Any, Optional


def _extract_from_markdown(text: str) -> str:
    json_pattern = r"```(?:json\s*)?\n([\s\S]*?)\n*```"
    matches = re.findall(json_pattern, text)

    if matches:
        json_str = max(matches, key=len).strip()
        json_str = re.sub(r'^\s*```.*?\n?|\n?\s*```\s*$', '', json_str)
        return json_str
    direct_json_match = re.search(r'({[\s\S]*})', text)
    return direct_json_match.group(
        1).strip() if direct_json_match else text.strip()


def parse_json(text: str) -> Optional[Dict[str, Any]]:
    clean_text = text.strip()
    for _ in range(2):
        try:
            return json.loads(clean_text)
        except json.JSONDecodeError as e:
            clean_text = re.sub(
                r'"(.*?)"',
                lambda m:
                '"' + m.group(1).replace("\n", "\\n").replace("\t", "\\t") + '"',
                clean_text,
                flags=re.DOTALL)

    json_str = _extract_from_markdown(clean_text)
    json_str = re.sub(
        r'"(.*?)"',
        lambda m: '"' + m.group(1).replace("\n", "\\n").replace("\t", "\\t") + '"',
        json_str,
        flags=re.DOTALL)
    return json.loads(json_str)
