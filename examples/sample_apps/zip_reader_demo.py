#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/10/28 21:21
# @Author  : Saladday
# @Email   : fanjing.luo@zju.edu.cn
# @FileName: zip_reader_demo.py

"""
ZIP Reader Demo
演示ZipReader的基础用法、嵌套ZIP处理、自定义配置、安全限制等功能
"""

import io
import zipfile
from pathlib import Path
from agentuniverse.agent.action.knowledge.reader.file.zip_reader import ZipReader
from agentuniverse.agent.action.knowledge.reader.file.file_reader import FileReader


def create_sample_zip():
    """创建示例ZIP文件，包含多种文件类型和嵌套结构"""
    print("=" * 80)
    print("创建示例ZIP文件")
    print("=" * 80)
    
    zip_path = Path("sample_archive.zip")
    
    nested_zip = io.BytesIO()
    with zipfile.ZipFile(nested_zip, "w") as nested:
        nested.writestr("nested_docs/report.txt", "这是嵌套压缩包中的报告文档\n包含重要数据分析结果")
        nested.writestr("nested_docs/data.json", '{"type": "analysis", "status": "completed", "score": 95}')
        nested.writestr("nested_code/script.py", "def analyze_data():\n    return {'result': 'success'}")
    
    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.writestr("README.md", """# 示例项目文档

## 项目简介
这是一个演示项目，用于展示ZIP Reader的功能。

## 主要功能
1. 读取多种文件格式
2. 处理嵌套ZIP结构
3. 提取元数据信息
""")
        
        archive.writestr("docs/introduction.txt", """项目介绍文档

本项目展示了如何使用agentUniverse框架处理压缩包文件。
支持自动识别和解析多种文档格式。
""")
        
        archive.writestr("src/main.py", """#!/usr/bin/env python3

def main():
    print("Hello, agentUniverse!")
    process_data()

def process_data():
    data = load_data()
    result = analyze(data)
    return result

if __name__ == "__main__":
    main()
""")
        
        archive.writestr("src/utils.py", """def helper_function():
    return "utility"

def format_output(data):
    return f"Result: {data}"
""")
        
        archive.writestr("config/settings.json", """{
    "app_name": "ZipReaderDemo",
    "version": "1.0.0",
    "features": {
        "nested_zip": true,
        "multi_format": true,
        "metadata_extraction": true
    },
    "limits": {
        "max_file_size": "64MB",
        "max_total_size": "512MB"
    }
}""")
        
        archive.writestr("config/database.yml", """database:
  host: localhost
  port: 5432
  name: demo_db
  user: demo_user
  pool_size: 10
""")
        
        archive.writestr("data/users.csv", """姓名,年龄,部门,职位
张三,28,技术部,工程师
李四,32,产品部,产品经理
王五,25,设计部,设计师
赵六,30,技术部,架构师
""")
        
        archive.writestr("data/metrics.txt", """性能指标报告
==============
CPU使用率: 45%
内存使用率: 60%
磁盘使用率: 35%
网络吞吐量: 1.2Gbps
""")
        
        archive.writestr("logs/app.log", """[2025-10-28 10:00:00] INFO: 应用启动
[2025-10-28 10:00:01] INFO: 加载配置文件
[2025-10-28 10:00:02] INFO: 初始化数据库连接
[2025-10-28 10:00:03] INFO: 启动服务，监听端口 8080
[2025-10-28 10:05:00] DEBUG: 处理用户请求
[2025-10-28 10:05:01] INFO: 请求处理完成
""")
        
        archive.writestr("web/index.html", """<!DOCTYPE html>
<html>
<head>
    <title>ZIP Reader Demo</title>
</head>
<body>
    <h1>欢迎使用 ZIP Reader</h1>
    <p>这是一个演示页面</p>
</body>
</html>
""")
        
        archive.writestr("archives/nested_data.zip", nested_zip.getvalue())
    
    print(f"示例ZIP文件创建成功: {zip_path}")
    print(f"文件大小: {zip_path.stat().st_size:,} 字节")
    return zip_path


def demo_basic_usage(zip_path):
    """演示基础用法"""
    print("\n" + "=" * 80)
    print("演示1: 基础用法")
    print("=" * 80)
    
    reader = ZipReader()
    documents = reader.load_data(file=zip_path)
    
    print(f"\n成功读取ZIP文件: {zip_path}")
    print(f"提取的文档数量: {len(documents)}")
    
    file_types = {}
    for doc in documents:
        file_name = doc.metadata.get("file_name", "")
        ext = Path(file_name).suffix.lower() or "无扩展名"
        file_types[ext] = file_types.get(ext, 0) + 1
    
    print(f"\n文件类型统计:")
    for ext, count in sorted(file_types.items()):
        print(f"  {ext}: {count} 个文件")
    
    print(f"\n前3个文档预览:")
    for i, doc in enumerate(documents[:3], 1):
        metadata = doc.metadata
        print(f"\n  文档 {i}:")
        print(f"    文件名: {metadata.get('file_name', 'Unknown')}")
        print(f"    路径: {metadata.get('archive_path', 'Unknown')}")
        print(f"    深度: {metadata.get('archive_depth', 0)}")
        content_preview = doc.text[:100] + "..." if len(doc.text) > 100 else doc.text
        print(f"    内容: {content_preview}")


def demo_nested_zip(zip_path):
    """演示嵌套ZIP处理"""
    print("\n" + "=" * 80)
    print("演示2: 嵌套ZIP处理")
    print("=" * 80)
    
    reader = ZipReader()
    documents = reader.load_data(file=zip_path)
    
    nested_docs = [d for d in documents if "nested_data.zip" in d.metadata.get("archive_path", "")]
    
    print(f"\n在嵌套ZIP中找到 {len(nested_docs)} 个文档:")
    for doc in nested_docs:
        metadata = doc.metadata
        print(f"\n  {metadata.get('file_name', 'Unknown')}")
        print(f"     完整路径: {metadata.get('archive_path', 'Unknown')}")
        print(f"     嵌套深度: {metadata.get('archive_depth', 0)}")
        print(f"     内容长度: {len(doc.text)} 字符")


def demo_file_type_filtering(zip_path):
    """演示按文件类型过滤"""
    print("\n" + "=" * 80)
    print("演示3: 按文件类型过滤")
    print("=" * 80)
    
    reader = ZipReader()
    documents = reader.load_data(file=zip_path)
    
    py_files = [d for d in documents if d.metadata.get("file_name", "").endswith(".py")]
    print(f"\nPython文件 ({len(py_files)} 个):")
    for doc in py_files:
        print(f"  - {doc.metadata.get('archive_path', 'Unknown')}")
        print(f"    代码行数: {len(doc.text.splitlines())}")
    
    json_files = [d for d in documents if d.metadata.get("file_name", "").endswith(".json")]
    print(f"\nJSON文件 ({len(json_files)} 个):")
    for doc in json_files:
        print(f"  - {doc.metadata.get('archive_path', 'Unknown')}")
        print(f"    内容预览: {doc.text[:80]}...")
    
    md_files = [d for d in documents if d.metadata.get("file_name", "").endswith(".md")]
    print(f"\nMarkdown文件 ({len(md_files)} 个):")
    for doc in md_files:
        print(f"  - {doc.metadata.get('archive_path', 'Unknown')}")


def demo_custom_metadata(zip_path):
    """演示自定义元数据"""
    print("\n" + "=" * 80)
    print("演示4: 自定义元数据")
    print("=" * 80)
    
    custom_metadata = {
        "source": "演示数据集",
        "category": "技术文档",
        "project": "agentUniverse",
        "version": "1.0.0",
        "timestamp": "2025-10-28",
        "author": "Saladday"
    }
    
    reader = ZipReader()
    documents = reader.load_data(file=zip_path, ext_info=custom_metadata)
    
    print(f"\n已添加自定义元数据")
    print(f"\n第一个文档的完整元数据:")
    if documents:
        metadata = documents[0].metadata
        for key, value in sorted(metadata.items()):
            print(f"  {key}: {value}")


def demo_custom_configuration(zip_path):
    """演示自定义配置"""
    print("\n" + "=" * 80)
    print("演示5: 自定义Reader配置")
    print("=" * 80)
    
    reader = ZipReader(
        max_total_size=100 * 1024 * 1024,
        max_file_size=10 * 1024 * 1024,
        max_depth=3,
        max_files=500,
        max_compression_ratio=200,
        stream_chunk_size=512 * 1024
    )
    
    print("\n自定义配置:")
    print(f"  最大总大小: 100MB")
    print(f"  最大单文件大小: 10MB")
    print(f"  最大嵌套深度: 3层")
    print(f"  最大文件数量: 500个")
    print(f"  最大压缩比: 200")
    
    documents = reader.load_data(file=zip_path)
    print(f"\n使用自定义配置成功读取 {len(documents)} 个文档")


def demo_file_reader_integration(zip_path):
    """演示与FileReader的集成"""
    print("\n" + "=" * 80)
    print("演示6: 与FileReader集成")
    print("=" * 80)
    
    file_reader = FileReader()
    documents = file_reader.load_data(file_paths=[zip_path])
    
    print(f"\nFileReader自动识别ZIP格式")
    print(f"提取的文档数量: {len(documents)}")
    print(f"\nFileReader会自动调用ZipReader处理.zip文件")


def demo_error_handling():
    """演示错误处理和安全限制"""
    print("\n" + "=" * 80)
    print("演示7: 错误处理和安全限制")
    print("=" * 80)
    
    test_zip = Path("test_compression.zip")
    with zipfile.ZipFile(test_zip, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("repetitive.txt", "A" * 10000)
    
    strict_reader = ZipReader(max_compression_ratio=50)
    
    print("\n测试压缩比限制:")
    try:
        documents = strict_reader.load_data(file=test_zip)
        print(f"  通过检查，读取 {len(documents)} 个文档")
    except ValueError as e:
        print(f"  触发安全限制: {e}")
    finally:
        if test_zip.exists():
            test_zip.unlink()
    
    print("\n测试文件不存在:")
    try:
        reader = ZipReader()
        documents = reader.load_data(file="nonexistent.zip")
    except FileNotFoundError as e:
        print(f"  正确捕获异常: {type(e).__name__}")


def demo_content_search(zip_path):
    """演示内容搜索"""
    print("\n" + "=" * 80)
    print("演示8: 内容搜索")
    print("=" * 80)
    
    reader = ZipReader()
    documents = reader.load_data(file=zip_path)
    
    keywords = ["agentUniverse", "数据", "配置", "Python"]
    
    print(f"\n搜索关键词:")
    for keyword in keywords:
        matching_docs = [d for d in documents if keyword in d.text]
        print(f"\n  '{keyword}' - 找到 {len(matching_docs)} 个相关文档:")
        for doc in matching_docs[:3]:
            file_name = doc.metadata.get("file_name", "Unknown")
            path = doc.metadata.get("archive_path", "Unknown")
            print(f"    - {file_name} ({path})")


def demo_statistics(zip_path):
    """演示统计信息"""
    print("\n" + "=" * 80)
    print("演示9: 统计信息")
    print("=" * 80)
    
    reader = ZipReader()
    documents = reader.load_data(file=zip_path)
    
    total_chars = sum(len(doc.text) for doc in documents)
    total_words = sum(len(doc.text.split()) for doc in documents)
    
    depth_stats = {}
    for doc in documents:
        depth = doc.metadata.get("archive_depth", 0)
        depth_stats[depth] = depth_stats.get(depth, 0) + 1
    
    print(f"\n整体统计:")
    print(f"  文档总数: {len(documents)}")
    print(f"  总字符数: {total_chars:,}")
    print(f"  总词数: {total_words:,}")
    print(f"  平均文档长度: {total_chars // len(documents) if documents else 0} 字符")
    
    print(f"\n深度分布:")
    for depth in sorted(depth_stats.keys()):
        print(f"  深度 {depth}: {depth_stats[depth]} 个文档")
    
    if documents:
        largest_doc = max(documents, key=lambda d: len(d.text))
        smallest_doc = min(documents, key=lambda d: len(d.text))
        
        print(f"\n文档大小:")
        print(f"  最大: {largest_doc.metadata.get('file_name', 'Unknown')} ({len(largest_doc.text):,} 字符)")
        print(f"  最小: {smallest_doc.metadata.get('file_name', 'Unknown')} ({len(smallest_doc.text):,} 字符)")


def cleanup(zip_path):
    """清理示例文件"""
    print("\n" + "=" * 80)
    print("清理示例文件")
    print("=" * 80)
    
    if zip_path.exists():
        zip_path.unlink()
        print(f"已删除: {zip_path}")


def main():
    """主函数：运行所有演示"""
    print("\n")
    print("=" * 80)
    print("ZIP Reader 完整演示 - agentUniverse Knowledge Reader")
    print("=" * 80)
    
    zip_path = create_sample_zip()
    
    try:
        demo_basic_usage(zip_path)
        demo_nested_zip(zip_path)
        demo_file_type_filtering(zip_path)
        demo_custom_metadata(zip_path)
        demo_custom_configuration(zip_path)
        demo_file_reader_integration(zip_path)
        demo_error_handling()
        demo_content_search(zip_path)
        demo_statistics(zip_path)
        
        print("\n" + "=" * 80)
        print("演示完成")
        print("=" * 80)
        
        print("\n使用提示:")
        print("  1. ZipReader支持多种文件格式的自动识别和解析")
        print("  2. 可以处理嵌套的ZIP文件结构")
        print("  3. 提供丰富的安全限制配置")
        print("  4. 支持自定义元数据传递")
        print("  5. 与FileReader无缝集成")
        
        print("\n更多信息:")
        print("  - 文档: https://github.com/agentuniverse-ai/agentUniverse")
        print("  - 示例代码: examples/sample_apps/zip_reader_demo.py")
        print("  - 测试文件: tests/test_agentuniverse/unit/agent/action/knowledge/reader/file/test_zip_reader.py")
        
    finally:
        cleanup(zip_path)
    
    print("\n")


if __name__ == "__main__":
    main()
