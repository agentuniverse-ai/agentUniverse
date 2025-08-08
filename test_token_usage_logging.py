#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试 Token Usage 日志功能
"""

from agentuniverse.base.util.monitor.monitor import Monitor
from agentuniverse.llm.llm_output import LLMOutput, TokenUsage

def test_format_token_usage_methods():
    """测试 token usage 格式化方法"""
    print("=== 测试 Token Usage 格式化方法 ===")
    
    # 测试空的 token usage
    empty_usage = {}
    print(f"空 token usage - Summary: {Monitor._format_token_usage_summary(empty_usage)}")
    print(f"空 token usage - Details: {Monitor._format_token_usage_details(empty_usage)}")
    
    # 测试有效的 token usage
    valid_usage = {
        'text_in': 150,
        'text_out': 50
    }
    print(f"有效 token usage - Summary: {Monitor._format_token_usage_summary(valid_usage)}")
    print(f"有效 token usage - Details: {Monitor._format_token_usage_details(valid_usage)}")
    
    # 测试部分数据的 token usage
    partial_usage = {
        'text_in': 100
    }
    print(f"部分 token usage - Summary: {Monitor._format_token_usage_summary(partial_usage)}")
    print(f"部分 token usage - Details: {Monitor._format_token_usage_details(partial_usage)}")

def test_token_usage_integration():
    """测试 token usage 的集成功能"""
    print("\n=== 测试 Token Usage 集成功能 ===")
    
    # 创建监控实例
    monitor = Monitor()
    print(f"Monitor 实例创建成功: log_activate={monitor.log_activate}")
    
    # 测试 get_llm_token_usage 静态方法
    print("测试 get_llm_token_usage 方法:")
    
    # 创建模拟的 LLMOutput
    llm_output = LLMOutput()
    llm_output.text = "This is a test response"
    
    # 创建模拟的 TokenUsage
    token_usage = TokenUsage()
    token_usage.text_in = 100
    token_usage.text_out = 50
    
    llm_output.usage = token_usage
    
    # 模拟 LLM 输入
    llm_input = {
        'kwargs': {
            'messages': [
                {'role': 'user', 'content': 'Hello, how are you?'}
            ]
        }
    }
    
    # 测试获取 token usage
    class MockLLM:
        def get_num_tokens(self, text):
            return len(text.split())
    
    mock_llm = MockLLM()
    usage_result = Monitor.get_llm_token_usage(mock_llm, llm_input, llm_output)
    print(f"获取的 token usage: {usage_result}")
    
    # 测试格式化结果
    if usage_result:
        print(f"格式化摘要: {Monitor._format_token_usage_summary(usage_result)}")
        print(f"格式化详情: {Monitor._format_token_usage_details(usage_result)}")

if __name__ == "__main__":
    try:
        test_format_token_usage_methods()
        test_token_usage_integration()
        print("\n✅ 所有测试完成!")
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
