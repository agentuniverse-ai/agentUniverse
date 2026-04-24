# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Simple Q&A Agent Test Script
简单问答智能体测试脚本

This script demonstrates how to use the Simple Q&A Agent programmatically.
此脚本演示如何以编程方式使用简单问答智能体。

Usage / 使用方法:
    # From the repository root / 从仓库根目录
    cd examples/sample_apps/simple_qa_agent_app
    python intelligence/test/simple_qa_agent_test.py

Requirements / 要求:
    - DASHSCOPE_API_KEY must be set in config/custom_key.toml
    - 必须在 config/custom_key.toml 中设置 DASHSCOPE_API_KEY
"""

from agentuniverse.base.agentuniverse import AgentUniverse
from agentuniverse.agent.agent_manager import AgentManager


def test_simple_qa_agent():
    """
    Test the Simple Q&A Agent with example questions.
    用示例问题测试简单问答智能体。
    """
    print("=" * 80)
    print("Simple Q&A Agent Test / 简单问答智能体测试")
    print("=" * 80)
    print()

    # Initialize agentUniverse framework / 初始化 agentUniverse 框架
    print("Initializing agentUniverse... / 正在初始化 agentUniverse...")
    AgentUniverse().start(config_path='../../config/config.toml', core_mode=True)
    print("✓ agentUniverse initialized successfully / agentUniverse 初始化成功")
    print()

    # Get the agent instance / 获取智能体实例
    print("Loading Simple Q&A Agent... / 正在加载简单问答智能体...")
    agent = AgentManager().get_instance_obj('simple_qa_agent')
    print("✓ Agent loaded successfully / 智能体加载成功")
    print()

    # Test questions (English and Chinese) / 测试问题（英文和中文）
    test_questions = [
        {
            'lang': 'English',
            'question': 'What is the capital of France?'
        },
        {
            'lang': '中文',
            'question': '什么是人工智能？'
        },
        {
            'lang': 'English',
            'question': 'Explain machine learning in simple terms.'
        }
    ]

    # Run tests / 运行测试
    for i, test in enumerate(test_questions, 1):
        print(f"Test {i} / 测试 {i}")
        print(f"Language / 语言: {test['lang']}")
        print(f"Question / 问题: {test['question']}")
        print("-" * 80)

        try:
            # Call the agent / 调用智能体
            result = agent.run(input=test['question'])

            # Display the response / 显示响应
            print("Response / 响应:")
            print(result.get('output', 'No output available'))
            print()

        except Exception as e:
            print(f"❌ Error / 错误: {str(e)}")
            print()

        print("=" * 80)
        print()

    print("✓ All tests completed / 所有测试完成")
    print()


def test_interactive_mode():
    """
    Interactive mode for testing the agent with custom questions.
    用于使用自定义问题测试智能体的交互模式。
    """
    print("=" * 80)
    print("Interactive Mode / 交互模式")
    print("=" * 80)
    print("Type your questions below. Type 'exit' or 'quit' to stop.")
    print("在下面输入您的问题。输入 'exit' 或 'quit' 停止。")
    print()

    # Initialize agentUniverse framework / 初始化 agentUniverse 框架
    AgentUniverse().start(config_path='../../config/config.toml', core_mode=True)
    agent = AgentManager().get_instance_obj('simple_qa_agent')

    while True:
        # Get user input / 获取用户输入
        user_input = input("Your question / 您的问题: ").strip()

        # Check for exit commands / 检查退出命令
        if user_input.lower() in ['exit', 'quit', '退出']:
            print("\nGoodbye! / 再见！")
            break

        # Skip empty input / 跳过空输入
        if not user_input:
            continue

        try:
            # Call the agent / 调用智能体
            result = agent.run(input=user_input)

            # Display the response / 显示响应
            print("\nAgent / 智能体:")
            print(result.get('output', 'No output available'))
            print()

        except Exception as e:
            print(f"\n❌ Error / 错误: {str(e)}\n")


if __name__ == "__main__":
    import sys

    print()
    print("╔═══════════════════════════════════════════════════════════════════════════╗")
    print("║               Simple Q&A Agent Test Script                                ║")
    print("║               简单问答智能体测试脚本                                       ║")
    print("╚═══════════════════════════════════════════════════════════════════════════╝")
    print()

    # Check if interactive mode is requested / 检查是否请求交互模式
    if len(sys.argv) > 1 and sys.argv[1] in ['-i', '--interactive']:
        test_interactive_mode()
    else:
        # Run automated tests / 运行自动化测试
        test_simple_qa_agent()

        # Offer interactive mode / 提供交互模式
        print()
        print("Would you like to try interactive mode? / 您想尝试交互模式吗？")
        print("Run: python intelligence/test/simple_qa_agent_test.py -i")
        print("运行: python intelligence/test/simple_qa_agent_test.py -i")
        print()
