# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/26 10:10
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: llm.py
# llm model name list
LLM_MODEL_NAME = {
    'demo_llm': ['gpt-4o', 'gpt-4o-mini', 'o1', 'o3-mini', 'qwen-max', 'qwen-long', 'qwen-plus',
                 'qwen-turbo', 'qwen2.5-72b-instruct', 'qwen2.5-7b-instruct'],
    'openai_llm': ['gpt-3.5-turbo', 'gpt-4-turbo', 'gpt-4o', 'gpt-4o-mini', 'o1', 'o1-mini', 'o3-mini'],
    'default_openai_llm': ['gpt-3.5-turbo', 'gpt-4-turbo', 'gpt-4o', 'gpt-4o-mini', 'o1', 'o1-mini', 'o3-mini'],
    'qwen_llm': ['qwen-max', 'qwen-long', 'qwen-plus', 'qwen-turbo', 'qwen-coder-plus',
                 'qwen2.5-72b-instruct', 'qwen2.5-32b-instruct', 'qwen2.5-14b-instruct', 'qwen2.5-7b-instruct'],
    'default_qwen_llm': ['qwen-max', 'qwen-long', 'qwen-plus', 'qwen-turbo', 'qwen-coder-plus',
                         'qwen2.5-72b-instruct', 'qwen2.5-32b-instruct', 'qwen2.5-14b-instruct', 'qwen2.5-7b-instruct'],
    'wenxin_llm': ['ERNIE-Speed-AppBuilder-8K-0516', 'ERNIE-Lite-8K-0725', 'ERNIE-Speed-128K', 'ERNIE-3.5-128K',
                   'ERNIE-3.5-8K-0701', 'ERNIE-4.0-8K-0613', 'ERNIE-4.0-8K-Preview', 'ERNIE-3.5-8K-Preview',
                   'ERNIE-Tiny-8K', 'ERNIE-4.0-8K-Latest', 'ERNIE-4.0-Turbo-8K','ERNIE-4.5-8K-Preview',
                   'ERNIE-4.5-Turbo-32K', 'ERNIE-4.5-Turbo-128K'],
    'default_wenxin_llm': ['ERNIE-Speed-AppBuilder-8K-0516', 'ERNIE-Lite-8K-0725', 'ERNIE-Speed-128K', 'ERNIE-3.5-128K',
                           'ERNIE-3.5-8K-0701', 'ERNIE-4.0-8K-0613', 'ERNIE-4.0-8K-Preview', 'ERNIE-3.5-8K-Preview',
                           'ERNIE-Tiny-8K', 'ERNIE-4.0-8K-Latest', 'ERNIE-4.0-Turbo-8K','ERNIE-4.5-8K-Preview',
                           'ERNIE-4.5-Turbo-32K', 'ERNIE-4.5-Turbo-128K'],
    'kimi_llm': ['moonshot-v1-8k', 'moonshot-v1-32k', 'moonshot-v1-128k'],
    'default_kimi_llm': ['moonshot-v1-8k', 'moonshot-v1-32k', 'moonshot-v1-128k'],
    'deepseek_llm': ['deepseek-chat', 'deepseek-coder', 'deepseek-reasoner', 'deepseek-v3', 'deepseek-r1',
                     'DeepSeek-R1', 'DeepSeek-V3'],
    'default_deepseek_llm': ['deepseek-chat', 'deepseek-coder', 'deepseek-reasoner', 'deepseek-v3', 'deepseek-r1',
                             'DeepSeek-R1', 'DeepSeek-V3'],
    'baichuan_llm': ['Baichuan4', 'Baichuan3-Turbo', 'Baichuan3-Turbo-128k', 'Baichuan2-Turbo', 'Baichuan2-Turbo-192k'],
    'default_baichuan_llm': ['Baichuan4', 'Baichuan3-Turbo', 'Baichuan3-Turbo-128k', 'Baichuan2-Turbo',
                             'Baichuan2-Turbo-192k'],
}
