#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/10/30 23:23
# @Author  : SaladDay
# @FileName: rar_reader_demo.py

"""
RAR Reader 演示

本演示展示了如何使用 RarReader 读取 RAR 压缩文件。
"""

import os
import tempfile
from pathlib import Path
from agentuniverse.agent.action.knowledge.reader.file.rar_reader import RarReader
from agentuniverse.agent.action.knowledge.reader.file.file_reader import FileReader


def create_sample_archive():
    """创建示例 RAR 压缩包用于演示"""
    print("\n" + "=" * 80)
    print("创建示例 RAR 压缩包...")
    print("=" * 80)
    
    temp_dir = tempfile.mkdtemp(prefix="rar_demo_")
    
    os.makedirs(os.path.join(temp_dir, "docs"), exist_ok=True)
    os.makedirs(os.path.join(temp_dir, "src"), exist_ok=True)
    os.makedirs(os.path.join(temp_dir, "config"), exist_ok=True)
    os.makedirs(os.path.join(temp_dir, "logs"), exist_ok=True)
    os.makedirs(os.path.join(temp_dir, "data"), exist_ok=True)
    
    with open(os.path.join(temp_dir, "README.md"), 'w', encoding='utf-8') as f:
        f.write("""# 示例项目

这是一个用于演示 RarReader 功能的示例项目。

## 功能特性
- 多格式支持
- 嵌套压缩包处理
- 安全限制
""")
    
    with open(os.path.join(temp_dir, "docs", "introduction.txt"), 'w', encoding='utf-8') as f:
        f.write("欢迎使用 agentUniverse！\n\n这是 RAR 读取器功能的演示。")
    
    with open(os.path.join(temp_dir, "src", "main.py"), 'w', encoding='utf-8') as f:
        f.write("""#!/usr/bin/env python3

def main():
    print("你好")
    process_data()

def process_data():
    data = load_data()
    result = analyze(data)
    return result
""")
    
    with open(os.path.join(temp_dir, "src", "utils.py"), 'w', encoding='utf-8') as f:
        f.write("""def helper_function():
    return True
""")
    
    with open(os.path.join(temp_dir, "config", "settings.json"), 'w', encoding='utf-8') as f:
        f.write("""{
    "app_name": "RAR读取器演示",
    "version": "1.0.0",
    "features": {
        "rar_support": true,
        "nested_archives": true,
        "security_limits": true
    }
}""")
    
    with open(os.path.join(temp_dir, "logs", "app.log"), 'w', encoding='utf-8') as f:
        f.write("""[2025-10-30 23:23:00] INFO: 应用程序已启动
[2025-10-30 23:23:01] INFO: 正在加载配置
[2025-10-30 23:23:02] INFO: 正在处理数据
""")
    
    with open(os.path.join(temp_dir, "data", "data.csv"), 'w', encoding='utf-8') as f:
        f.write("""姓名,年龄,城市
张三,30,北京
李四,25,上海
王五,35,广州
""")
    
    rar_path = os.path.join(temp_dir, "sample_archive.rar")
    
    try:
        import subprocess
        
        files_to_archive = [
            os.path.join(temp_dir, "README.md"),
            os.path.join(temp_dir, "docs"),
            os.path.join(temp_dir, "src"),
            os.path.join(temp_dir, "config"),
            os.path.join(temp_dir, "logs"),
            os.path.join(temp_dir, "data"),
        ]
        
        subprocess.run(
            ['rar', 'a', '-r', '-ep1', rar_path] + files_to_archive,
            check=True,
            capture_output=True,
            cwd=temp_dir
        )
        
        print(f"示例压缩包已创建: {rar_path}")
        return rar_path, temp_dir
        
    except FileNotFoundError:
        print("未找到 RAR 命令行工具，请先安装 RAR。")
        print("Ubuntu/Debian: sudo apt-get install rar")
        print("macOS: brew install rar")
        return None, temp_dir
    except subprocess.CalledProcessError as e:
        print(f"创建 RAR 压缩包失败: {e}")
        return None, temp_dir


def demo_rar_reader_direct(rar_path):
    """直接使用 RarReader"""
    print("\n" + "=" * 80)
    print("演示 1: 直接使用 RarReader")
    print("=" * 80)
    
    rar_reader = RarReader()
    
    try:
        documents = rar_reader.load_data(rar_path)
        
        print(f"\n成功加载 RAR 压缩包: {Path(rar_path).name}")
        print(f"提取的文档总数: {len(documents)}")
        
        print("\n提取的文件:")
        for i, doc in enumerate(documents, 1):
            metadata = doc.metadata
            print(f"\n  文档 {i}:")
            print(f"    文件名: {metadata.get('file_name')}")
            print(f"    路径: {metadata.get('archive_path')}")
            print(f"    深度: {metadata.get('archive_depth')}")
            print(f"    内容长度: {len(doc.text)} 字符")
            if len(doc.text) < 200:
                print(f"    内容: {doc.text[:200]}")
            else:
                print(f"    内容预览: {doc.text[:200]}...")
                
    except Exception as e:
        print(f"读取 RAR 文件错误: {e}")


def demo_file_reader_integration(rar_path):
    """FileReader 自动检测演示"""
    print("\n" + "=" * 80)
    print("演示 2: FileReader 集成")
    print("=" * 80)
    
    file_reader = FileReader()
    
    try:
        documents = file_reader.load_data([Path(rar_path)])
        
        print(f"\nFileReader 自动检测到 RAR 格式")
        print(f"提取的文档数: {len(documents)}")
        
        print("\nFileReader 会自动为 .rar 文件调用 RarReader")
        
    except Exception as e:
        print(f"FileReader 错误: {e}")


def demo_custom_metadata(rar_path):
    """自定义元数据演示"""
    print("\n" + "=" * 80)
    print("演示 3: 自定义元数据")
    print("=" * 80)
    
    rar_reader = RarReader()
    
    custom_metadata = {
        "project": "agentUniverse",
        "author": "SaladDay",
        "category": "技术文档",
        "timestamp": "2025-10-30",
        "source": "演示数据集"
    }
    
    try:
        documents = rar_reader.load_data(rar_path, ext_info=custom_metadata)
        
        print(f"\n已加载自定义元数据")
        print(f"文档数: {len(documents)}")
        
        if documents:
            print("\n第一个文档的元数据:")
            sample_doc = documents[0]
            for key, value in sample_doc.metadata.items():
                print(f"  {key}: {value}")
                
    except Exception as e:
        print(f"错误: {e}")


def demo_custom_config(rar_path):
    """自定义配置演示"""
    print("\n" + "=" * 80)
    print("演示 4: 自定义读取器配置")
    print("=" * 80)
    
    rar_reader = RarReader()
    
    config = {
        "max_total_size": 100 * 1024 * 1024,
        "max_file_size": 10 * 1024 * 1024,
        "max_depth": 3,
        "max_files": 500,
        "max_compression_ratio": 200.0
    }
    
    print("\n自定义配置:")
    print(f"  最大总大小: {config['max_total_size'] // 1024 // 1024}MB")
    print(f"  最大单文件大小: {config['max_file_size'] // 1024 // 1024}MB")
    print(f"  最大嵌套深度: {config['max_depth']} 层")
    print(f"  最大文件数: {config['max_files']}")
    print(f"  最大压缩比: {config['max_compression_ratio']}")
    
    try:
        documents = rar_reader.load_data(rar_path, **config)
        print(f"\n使用自定义配置处理成功: {len(documents)} 个文档")
        
    except Exception as e:
        print(f"错误: {e}")


def demo_filter_by_type(rar_path):
    """按文件类型过滤文档"""
    print("\n" + "=" * 80)
    print("演示 5: 按文件类型过滤")
    print("=" * 80)
    
    rar_reader = RarReader()
    
    try:
        documents = rar_reader.load_data(rar_path)
        
        by_type = {}
        for doc in documents:
            suffix = doc.metadata.get('file_suffix', 'unknown')
            if suffix not in by_type:
                by_type[suffix] = []
            by_type[suffix].append(doc)
        
        print("\n按文件类型分类的文档:")
        for suffix, docs in sorted(by_type.items()):
            print(f"\n  {suffix} 文件 ({len(docs)} 个文档):")
            for doc in docs:
                print(f"    - {doc.metadata.get('archive_path')}")
                
    except Exception as e:
        print(f"错误: {e}")


def demo_content_search(rar_path):
    """在 RAR 压缩包中搜索内容"""
    print("\n" + "=" * 80)
    print("演示 6: 内容搜索")
    print("=" * 80)
    
    rar_reader = RarReader()
    
    try:
        documents = rar_reader.load_data(rar_path)
        
        search_keywords = ["agentUniverse", "演示", "配置", "Python"]
        
        print("\n搜索关键词:\n")
        
        for keyword in search_keywords:
            matching_docs = []
            for doc in documents:
                if keyword.lower() in doc.text.lower():
                    matching_docs.append(doc)
            
            if matching_docs:
                print(f"  '{keyword}' - 在 {len(matching_docs)} 个文档中找到:")
                for doc in matching_docs:
                    print(f"    - {doc.metadata.get('file_name')} ({doc.metadata.get('archive_path')})")
            else:
                print(f"  '{keyword}' - 未找到")
                
    except Exception as e:
        print(f"错误: {e}")


def demo_statistics(rar_path):
    """显示压缩包统计信息"""
    print("\n" + "=" * 80)
    print("演示 7: 压缩包统计信息")
    print("=" * 80)
    
    rar_reader = RarReader()
    
    try:
        documents = rar_reader.load_data(rar_path)
        
        total_chars = sum(len(doc.text) for doc in documents)
        total_words = sum(len(doc.text.split()) for doc in documents)
        
        depths = {}
        for doc in documents:
            depth = doc.metadata.get('archive_depth', 0)
            depths[depth] = depths.get(depth, 0) + 1
        
        print(f"\n整体统计:")
        print(f"  文档总数: {len(documents)}")
        print(f"  总字符数: {total_chars:,}")
        print(f"  总词数: {total_words:,}")
        print(f"  平均文档长度: {total_chars // len(documents) if documents else 0} 字符")
        
        print(f"\n深度分布:")
        for depth in sorted(depths.keys()):
            print(f"  深度 {depth}: {depths[depth]} 个文档")
        
        if documents:
            max_doc = max(documents, key=lambda x: len(x.text))
            min_doc = min(documents, key=lambda x: len(x.text))
            
            print(f"\n文档大小:")
            print(f"  最大: {max_doc.metadata.get('file_name')} ({len(max_doc.text)} 字符)")
            print(f"  最小: {min_doc.metadata.get('file_name')} ({len(min_doc.text)} 字符)")
            
    except Exception as e:
        print(f"错误: {e}")


def demo_nested_rar(temp_dir):
    """多层嵌套 RAR 演示"""
    print("\n" + "=" * 80)
    print("演示 8: 多层嵌套 RAR 压缩包")
    print("=" * 80)
    
    rar_reader = RarReader()
    
    try:
        import subprocess
        
        nested_base = os.path.join(temp_dir, "nested_demo")
        os.makedirs(nested_base, exist_ok=True)
        
        print("\n创建多层嵌套结构...")
        
        level3_dir = os.path.join(nested_base, "level3")
        os.makedirs(level3_dir, exist_ok=True)
        with open(os.path.join(level3_dir, "第三层文件.txt"), 'w', encoding='utf-8') as f:
            f.write("这是嵌套在最深层的文件内容。\n包含重要的配置信息。")
        with open(os.path.join(level3_dir, "deep_config.json"), 'w', encoding='utf-8') as f:
            f.write('{"level": 3, "message": "深层配置", "secret": "深层秘密"}')
        
        level3_rar = os.path.join(nested_base, "level3.rar")
        subprocess.run(
            ['rar', 'a', '-r', '-ep1', level3_rar, level3_dir],
            check=True,
            capture_output=True,
            cwd=nested_base
        )
        print("  ✓ 创建第 3 层 RAR")
        
        level2_dir = os.path.join(nested_base, "level2")
        os.makedirs(level2_dir, exist_ok=True)
        with open(os.path.join(level2_dir, "第二层文件.txt"), 'w', encoding='utf-8') as f:
            f.write("这是第二层的文件。\n它包含了下一层的压缩包。")
        shutil.copy(level3_rar, level2_dir)
        with open(os.path.join(level2_dir, "中层数据.csv"), 'w', encoding='utf-8') as f:
            f.write("层级,名称,值\n2,中层A,200\n2,中层B,250")
        
        level2_rar = os.path.join(nested_base, "level2.rar")
        subprocess.run(
            ['rar', 'a', '-r', '-ep1', level2_rar, level2_dir],
            check=True,
            capture_output=True,
            cwd=nested_base
        )
        print("  ✓ 创建第 2 层 RAR（包含第 3 层）")
        
        level1_dir = os.path.join(nested_base, "level1")
        os.makedirs(level1_dir, exist_ok=True)
        with open(os.path.join(level1_dir, "第一层文件.txt"), 'w', encoding='utf-8') as f:
            f.write("这是顶层文件。\n项目包含多层嵌套的压缩包结构。")
        shutil.copy(level2_rar, level1_dir)
        with open(os.path.join(level1_dir, "顶层说明.md"), 'w', encoding='utf-8') as f:
            f.write("# 嵌套压缩包项目\n\n本项目演示了 RarReader 处理多层嵌套的能力。")
        
        nested_rar = os.path.join(nested_base, "nested_archive.rar")
        subprocess.run(
            ['rar', 'a', '-r', '-ep1', nested_rar, level1_dir],
            check=True,
            capture_output=True,
            cwd=nested_base
        )
        print("  ✓ 创建第 1 层 RAR（包含第 2 层）")
        print(f"\n已创建嵌套压缩包: {nested_rar}")
        
        print("\n正在提取嵌套压缩包...")
        documents = rar_reader.load_data(nested_rar, max_depth=5)
        
        print(f"\n成功提取 {len(documents)} 个文档")
        
        by_depth = {}
        for doc in documents:
            depth = doc.metadata.get('archive_depth', 0)
            if depth not in by_depth:
                by_depth[depth] = []
            by_depth[depth].append(doc)
        
        print("\n按嵌套深度分类:")
        for depth in sorted(by_depth.keys()):
            docs = by_depth[depth]
            print(f"\n  深度 {depth} ({len(docs)} 个文档):")
            for doc in docs:
                file_name = doc.metadata.get('file_name')
                archive_path = doc.metadata.get('archive_path')
                content_preview = doc.text[:50].replace('\n', ' ') if len(doc.text) > 50 else doc.text.replace('\n', ' ')
                print(f"    - {file_name}")
                print(f"      路径: {archive_path}")
                print(f"      内容: {content_preview}...")
        
        print("\n嵌套统计:")
        print(f"  最大嵌套深度: {max(by_depth.keys())}")
        print(f"  总文档数: {len(documents)}")
        
        nested_rars = [d for d in documents if d.metadata.get('file_suffix') == '.rar']
        if nested_rars:
            print(f"  包含的嵌套 RAR: {len(nested_rars)} 个")
        
    except FileNotFoundError:
        print("\n未找到 RAR 工具，跳过嵌套演示")
    except Exception as e:
        print(f"\n错误: {e}")


def cleanup(temp_dir):
    """清理临时文件"""
    print("\n" + "=" * 80)
    print("清理演示文件")
    print("=" * 80)
    
    import shutil
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"已删除: {temp_dir}")


if __name__ == "__main__":
    print("=" * 80)
    print("RAR Reader 演示 - agentUniverse")
    print("=" * 80)
    print("\n本演示展示了 RarReader 的功能:")
    print("  - 从 RAR 压缩包中读取各种文件格式")
    print("  - 嵌套 RAR 支持")
    print("  - 安全限制")
    print("  - 自定义元数据")
    print("  - FileReader 集成")
    
    rar_path, temp_dir = create_sample_archive()
    
    if rar_path and os.path.exists(rar_path):
        try:
            demo_rar_reader_direct(rar_path)
            demo_file_reader_integration(rar_path)
            demo_custom_metadata(rar_path)
            demo_custom_config(rar_path)
            demo_filter_by_type(rar_path)
            demo_content_search(rar_path)
            demo_statistics(rar_path)
            demo_nested_rar(temp_dir)
            
            print("\n" + "=" * 80)
            print("演示完成！")
            print("=" * 80)
            
            print("\n使用提示:")
            print("  1. RarReader 自动支持多种文件格式")
            print("  2. 可处理嵌套的 RAR 压缩包（默认最大深度：5 层）")
            print("  3. 安全限制可防护恶意压缩包")
            print("  4. 可为所有提取的文档添加自定义元数据")
            print("  5. FileReader 无缝集成 RarReader")
            
        finally:
            cleanup(temp_dir)
    else:
        print("\n创建示例压缩包失败，演示终止。")
        print("\n依赖要求:")
        print("  - pip install rarfile")
        print("  - 安装 RAR 命令行工具:")
        print("    - Ubuntu/Debian: sudo apt-get install rar")
        print("    - macOS: brew install rar")
        print("    - Windows: 从 https://www.rarlab.com/ 下载安装")
        
        if temp_dir and os.path.exists(temp_dir):
            cleanup(temp_dir)

