# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    :
# @Author  :
# @Email   :
# @FileName: test_search_tools_demo.py

import os
import sys
import asyncio

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from sample_standard_app.intelligence.agentic.tool.custom.google_search_tool import GoogleSearchTool, GoogleScholarSearchTool


def test_google_search():
    """测试Google搜索工具"""
    print("=" * 50)
    print("测试Google搜索工具")
    print("=" * 50)
    
    # 创建Google搜索工具实例
    search_tool = GoogleSearchTool()
    
    # 测试普通搜索
    print("\n1. 普通搜索测试:")
    result = search_tool.execute(input="人工智能最新发展")
    print(result)
    
    # 测试图片搜索
    print("\n2. 图片搜索测试:")
    result = search_tool.execute(input="美丽的风景", search_type="images", k=3)
    print(result)
    
    # 测试新闻搜索
    print("\n3. 新闻搜索测试:")
    result = search_tool.execute(input="科技新闻", search_type="news", gl="cn", hl="zh")
    print(result)


def test_google_scholar_search():
    """测试Google学术搜索工具"""
    print("\n" + "=" * 50)
    print("测试Google学术搜索工具")
    print("=" * 50)
    
    # 创建Google学术搜索工具实例
    scholar_tool = GoogleScholarSearchTool()
    
    # 测试基础学术搜索
    print("\n1. 基础学术搜索测试:")
    result = scholar_tool.execute(input="机器学习算法")
    print(result)
    
    # 测试按年份筛选
    print("\n2. 按年份筛选测试:")
    result = scholar_tool.execute(input="深度学习", year="2020..2024")
    print(result)
    
    # 测试按作者筛选
    print("\n3. 按作者筛选测试:")
    result = scholar_tool.execute(input="神经网络", author="Geoffrey Hinton")
    print(result)


async def test_async_search():
    """测试异步搜索功能"""
    print("\n" + "=" * 50)
    print("测试异步搜索功能")
    print("=" * 50)
    
    search_tool = GoogleSearchTool()
    scholar_tool = GoogleScholarSearchTool()
    
    # 并发执行多个搜索
    print("\n并发执行多个搜索:")
    tasks = [
        search_tool.async_execute(input="Python编程"),
        scholar_tool.async_execute(input="人工智能", year="2023..2024"),
        search_tool.async_execute(input="机器学习", search_type="news")
    ]
    
    results = await asyncio.gather(*tasks)
    
    for i, result in enumerate(results, 1):
        print(f"\n搜索结果 {i}:")
        print(result)


def main():
    """主函数"""
    print("搜索工具演示测试")
    print(f"当前工作目录: {os.getcwd()}")
    
    # 检查API密钥
    serper_key = os.getenv("SERPER_API_KEY")
    if serper_key:
        print(f"✅ 检测到SERPER_API_KEY: {serper_key[:10]}...")
    else:
        print("⚠️  未检测到SERPER_API_KEY，将显示模拟结果")
    
    try:
        # 测试Google搜索
        test_google_search()
        
        # 测试Google学术搜索
        test_google_scholar_search()
        
        # 测试异步搜索
        asyncio.run(test_async_search())
        
        print("\n" + "=" * 50)
        print("所有测试完成！")
        print("=" * 50)
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
