import os
import tempfile
import shutil
from pathlib import Path
# 导入7Z读取器和通用文件读取器
from agentuniverse.agent.action.knowledge.reader.file.sevenzip_reader import SevenZipReader
from agentuniverse.agent.action.knowledge.reader.file.file_reader import FileReader


def create_sample_7z_archive():
    """创建示例 7Z 压缩包用于演示"""
    print("\n" + "=" * 80)
    print("创建示例 7Z 压缩包...")
    print("=" * 80)

    # 创建临时目录用于存储演示文件
    temp_dir = tempfile.mkdtemp(prefix="7z_demo_")

    # 创建多个子目录结构
    os.makedirs(os.path.join(temp_dir, "docs"), exist_ok=True)
    os.makedirs(os.path.join(temp_dir, "src"), exist_ok=True)
    os.makedirs(os.path.join(temp_dir, "config"), exist_ok=True)
    os.makedirs(os.path.join(temp_dir, "logs"), exist_ok=True)
    os.makedirs(os.path.join(temp_dir, "data"), exist_ok=True)

    # 创建README.md文件
    with open(os.path.join(temp_dir, "README.md"), 'w', encoding='utf-8') as f:
        f.write("""# 7Z 读取器演示项目
                这是一个用于演示 SevenZipReader 功能的示例项目。
                ## 功能特性
                - 多格式文件支持
                - 嵌套7Z压缩包处理
                - 安全限制和压缩炸弹防护
                - 自动文件类型检测
                """)

    # 创建文档文件
    with open(os.path.join(temp_dir, "docs", "introduction.txt"), 'w', encoding='utf-8') as f:
        f.write("欢迎使用 agentUniverse 7Z 读取器！\n\n这是 7Z 读取器功能的演示文件。")

    # 创建Python源代码文件
    with open(os.path.join(temp_dir, "src", "main.py"), 'w', encoding='utf-8') as f:
        f.write("""#!/usr/bin/env python3
                def main():
                    print("7Z 读取器演示程序")
                    process_data()
                    
                def process_data():
                    data = load_data()
                    result = analyze(data)
                    return result
                    
                def load_data():
                    return {"sample": "data"}
                    
                def analyze(data):
                    return f"分析结果: {data}"
                    
                if __name__ == "__main__":
                    main()
                """)

    # 创建工具函数文件
    with open(os.path.join(temp_dir, "src", "utils.py"), 'w', encoding='utf-8') as f:
        f.write("""def helper_function():
                '''辅助函数示例'''
                return True

            def data_processor(input_data):
                '''数据处理函数'''
                processed = {}
                for key, value in input_data.items():
                    processed[key] = str(value).upper()
                return processed
            """)

    # 创建配置文件
    with open(os.path.join(temp_dir, "config", "settings.json"), 'w', encoding='utf-8') as f:
        f.write("""{
            "app_name": "7Z读取器演示",
            "version": "2.0.0",
            "features": {
                "7z_support": true,
                "nested_archives": true,
                "security_limits": true,
                "multiple_formats": true
            },
            "compression": {
                "method": "LZMA2",
                "level": 5
            }
        }""")

    # 创建YAML配置文件
    with open(os.path.join(temp_dir, "config", "app_config.yaml"), 'w', encoding='utf-8') as f:
        f.write("""# 应用程序配置
                app:
                name: "7Z Reader Demo"
                version: "2.0.0"
                
                database:
                host: "localhost"
                port: 5432
                name: "demo_db"

                logging:
                level: "INFO"
                file: "app.log"
                """)

    # 创建日志文件
    with open(os.path.join(temp_dir, "logs", "app.log"), 'w', encoding='utf-8') as f:
        f.write("""[2025-10-30 23:23:00] INFO: 7Z 读取器应用程序已启动
                [2025-10-30 23:23:01] INFO: 正在加载配置文件
                [2025-10-30 23:23:02] INFO: 初始化 7Z 处理模块
                [2025-10-30 23:23:03] INFO: 准备处理压缩文件
                """)

    # 创建数据文件
    with open(os.path.join(temp_dir, "data", "employees.csv"), 'w', encoding='utf-8') as f:
        f.write("""id,姓名,部门,工资,入职日期
                1,张三,技术部,15000,2020-01-15
                2,李四,销售部,12000,2019-03-20
                3,王五,技术部,16000,2018-07-10
                4,赵六,人事部,11000,2021-05-30
                """)

    # 创建XML数据文件
    with open(os.path.join(temp_dir, "data", "products.xml"), 'w', encoding='utf-8') as f:
        f.write("""<?xml version="1.0" encoding="UTF-8"?>
            <products>
                <product id="1">
                    <name>笔记本电脑</name>
                    <category>电子产品</category>
                    <price>5999.00</price>
                    <stock>50</stock>
                </product>
                <product id="2">
                    <name>无线鼠标</name>
                    <category>电子产品</category>
                    <price>89.00</price>
                    <stock>200</stock>
                </product>
                <product id="3">
                    <name>机械键盘</name>
                    <category>电子产品</category>
                    <price>399.00</price>
                    <stock>100</stock>
                </product>
            </products>
            """)

    # 定义7Z文件路径
    sevenzip_path = os.path.join(temp_dir, "sample_archive.7z")

    try:
        import py7zr
        
        # 使用py7zr创建7Z压缩包
        with py7zr.SevenZipFile(sevenzip_path, 'w') as archive:
            # 添加所有文件和目录到压缩包
            archive.writeall(temp_dir, '')
        
        print(f"示例7Z压缩包已创建: {sevenzip_path}")
        print("包含的文件:")
        with py7zr.SevenZipFile(sevenzip_path, 'r') as archive:
            for file_info in archive.files:
                print(f"  - {file_info.filename} ({file_info.uncompressed} 字节)")
        
        return sevenzip_path, temp_dir

    except ImportError:
        print("未找到 py7zr 库，请先安装: pip install py7zr")
        return None, temp_dir
    except Exception as e:
        print(f"创建 7Z 压缩包失败: {e}")
        return None, temp_dir


def demo_sevenzip_reader_direct(sevenzip_path):
    """直接使用 SevenZipReader"""
    print("\n" + "=" * 80)
    print("演示 1: 直接使用 SevenZipReader")
    print("=" * 80)

    # 创建7Z读取器实例
    sevenzip_reader = SevenZipReader()

    try:
        # 加载7Z文件数据
        documents = sevenzip_reader.load_data(sevenzip_path)

        print(f"\n成功加载 7Z 压缩包: {Path(sevenzip_path).name}")
        print(f"提取的文档总数: {len(documents)}")

        print("\n提取的文件详情:")
        # 遍历所有提取的文档
        for i, doc in enumerate(documents, 1):
            metadata = doc.metadata
            print(f"\n  文档 {i}:")
            print(f"    文件名: {metadata.get('file_name')}")
            print(f"    路径: {metadata.get('archive_path')}")
            print(f"    深度: {metadata.get('archive_depth')}")
            print(f"    后缀: {metadata.get('file_suffix')}")
            print(f"    内容长度: {len(doc.text)} 字符")
            
            # 显示内容预览（针对不同文件类型）
            if metadata.get('file_suffix') in ['.json', '.yaml', '.yml', '.xml']:
                # 结构化文件显示更多内容
                preview_length = min(300, len(doc.text))
                if len(doc.text) <= preview_length:
                    print(f"    内容:\n{doc.text}")
                else:
                    print(f"    内容预览:\n{doc.text[:preview_length]}...")
            else:
                # 文本文件显示前200字符
                preview_length = min(200, len(doc.text))
                if len(doc.text) <= preview_length:
                    print(f"    内容: {doc.text}")
                else:
                    print(f"    内容预览: {doc.text[:preview_length]}...")

    except Exception as e:
        print(f"读取 7Z 文件错误: {e}")


def demo_file_reader_integration(sevenzip_path):
    """FileReader 自动检测演示"""
    print("\n" + "=" * 80)
    print("演示 2: FileReader 集成")
    print("=" * 80)

    # 创建通用文件读取器
    file_reader = FileReader()

    try:
        # FileReader会自动检测文件类型并调用合适的读取器
        documents = file_reader.load_data([Path(sevenzip_path)])

        print(f"\nFileReader 自动检测到 7Z 格式")
        print(f"提取的文档数: {len(documents)}")

        print("\nFileReader 会自动为 .7z 文件调用 SevenZipReader")
        
        # 显示一些统计信息
        if documents:
            file_types = {}
            for doc in documents:
                suffix = doc.metadata.get('file_suffix', 'unknown')
                file_types[suffix] = file_types.get(suffix, 0) + 1
            
            print("\n文件类型分布:")
            for suffix, count in sorted(file_types.items()):
                print(f"  {suffix}: {count} 个文件")

    except Exception as e:
        print(f"FileReader 错误: {e}")


def demo_custom_metadata(sevenzip_path):
    """自定义元数据演示"""
    print("\n" + "=" * 80)
    print("演示 3: 自定义元数据")
    print("=" * 80)

    sevenzip_reader = SevenZipReader()

    # 定义自定义元数据
    custom_metadata = {
        "project": "agentUniverse",
        "module": "SevenZipReader",
        "author": "SaladDay",
        "category": "技术演示",
        "timestamp": "2025-10-30",
        "source": "7Z演示数据集",
        "compression_method": "LZMA2",
        "purpose": "功能验证和演示"
    }

    try:
        # 使用自定义元数据加载数据
        documents = sevenzip_reader.load_data(sevenzip_path, ext_info=custom_metadata)

        print(f"\n已加载自定义元数据")
        print(f"文档数: {len(documents)}")

        if documents:
            print("\n第一个文档的完整元数据:")
            sample_doc = documents[0]
            # 显示所有元数据键值对
            for key, value in sample_doc.metadata.items():
                print(f"  {key}: {value}")

    except Exception as e:
        print(f"错误: {e}")


def demo_custom_config(sevenzip_path):
    """自定义配置演示"""
    print("\n" + "=" * 80)
    print("演示 4: 自定义读取器配置")
    print("=" * 80)

    sevenzip_reader = SevenZipReader()

    # 定义自定义配置参数
    config = {
        "max_total_size": 200 * 1024 * 1024,  # 200MB
        "max_file_size": 20 * 1024 * 1024,    # 20MB
        "max_depth": 4,                       # 4层嵌套深度
        "max_files": 1000,                    # 最多1000个文件
        "max_compression_ratio": 500.0        # 最大压缩比500
    }

    print("\n自定义配置:")
    print(f"  最大总大小: {config['max_total_size'] // 1024 // 1024}MB")
    print(f"  最大单文件大小: {config['max_file_size'] // 1024 // 1024}MB")
    print(f"  最大嵌套深度: {config['max_depth']} 层")
    print(f"  最大文件数: {config['max_files']}")
    print(f"  最大压缩比: {config['max_compression_ratio']}")

    try:
        # 使用自定义配置加载数据
        documents = sevenzip_reader.load_data(sevenzip_path, **config)
        print(f"\n使用自定义配置处理成功: {len(documents)} 个文档")

    except Exception as e:
        print(f"错误: {e}")


def demo_filter_by_type(sevenzip_path):
    """按文件类型过滤文档"""
    print("\n" + "=" * 80)
    print("演示 5: 按文件类型过滤")
    print("=" * 80)

    sevenzip_reader = SevenZipReader()

    try:
        documents = sevenzip_reader.load_data(sevenzip_path)

        # 按文件后缀分类文档
        by_type = {}
        for doc in documents:
            suffix = doc.metadata.get('file_suffix', 'unknown')
            if suffix not in by_type:
                by_type[suffix] = []
            by_type[suffix].append(doc)

        print("\n按文件类型分类的文档:")
        # 按文件类型排序显示
        for suffix, docs in sorted(by_type.items()):
            print(f"\n  {suffix} 文件 ({len(docs)} 个文档):")
            for doc in docs:
                file_path = doc.metadata.get('archive_path')
                size = len(doc.text)
                print(f"    - {file_path} ({size} 字符)")

    except Exception as e:
        print(f"错误: {e}")


def demo_content_search(sevenzip_path):
    """在 7Z 压缩包中搜索内容"""
    print("\n" + "=" * 80)
    print("演示 6: 内容搜索")
    print("=" * 80)

    sevenzip_reader = SevenZipReader()

    try:
        documents = sevenzip_reader.load_data(sevenzip_path)

        # 定义搜索关键词
        search_keywords = ["7Z", "读取器", "配置", "Python", "数据", "XML"]

        print("\n在压缩包内容中搜索关键词:\n")

        # 对每个关键词进行搜索
        for keyword in search_keywords:
            matching_docs = []
            for doc in documents:
                if keyword.lower() in doc.text.lower():
                    matching_docs.append(doc)

            # 显示搜索结果
            if matching_docs:
                print(f"  '{keyword}' - 在 {len(matching_docs)} 个文档中找到:")
                for doc in matching_docs:
                    file_name = doc.metadata.get('file_name')
                    archive_path = doc.metadata.get('archive_path')
                    # 显示匹配内容的片段
                    text_lower = doc.text.lower()
                    keyword_pos = text_lower.find(keyword.lower())
                    start = max(0, keyword_pos - 20)
                    end = min(len(doc.text), keyword_pos + len(keyword) + 20)
                    snippet = doc.text[start:end].replace('\n', ' ')
                    print(f"    - {file_name}")
                    print(f"      路径: {archive_path}")
                    print(f"      片段: ...{snippet}...")
            else:
                print(f"  '{keyword}' - 未找到")

    except Exception as e:
        print(f"错误: {e}")


def demo_statistics(sevenzip_path):
    """显示压缩包统计信息"""
    print("\n" + "=" * 80)
    print("演示 7: 压缩包统计信息")
    print("=" * 80)

    sevenzip_reader = SevenZipReader()

    try:
        documents = sevenzip_reader.load_data(sevenzip_path)

        # 计算总体统计信息
        total_chars = sum(len(doc.text) for doc in documents)
        total_words = sum(len(doc.text.split()) for doc in documents)
        total_lines = sum(doc.text.count('\n') + 1 for doc in documents)  # 估算行数

        # 按嵌套深度统计
        depths = {}
        for doc in documents:
            depth = doc.metadata.get('archive_depth', 0)
            depths[depth] = depths.get(depth, 0) + 1

        print(f"\n整体统计:")
        print(f"  文档总数: {len(documents)}")
        print(f"  总字符数: {total_chars:,}")
        print(f"  总词数: {total_words:,}")
        print(f"  总行数: {total_lines:,}")
        print(f"  平均文档长度: {total_chars // len(documents) if documents else 0} 字符")

        print(f"\n深度分布:")
        for depth in sorted(depths.keys()):
            print(f"  深度 {depth}: {depths[depth]} 个文档")

        if documents:
            # 找到最大和最小的文档
            max_doc = max(documents, key=lambda x: len(x.text))
            min_doc = min(documents, key=lambda x: len(x.text))

            print(f"\n文档大小:")
            print(f"  最大: {max_doc.metadata.get('file_name')} ({len(max_doc.text)} 字符)")
            print(f"  最小: {min_doc.metadata.get('file_name')} ({len(min_doc.text)} 字符)")

        # 文件类型统计
        file_types = {}
        for doc in documents:
            suffix = doc.metadata.get('file_suffix', 'unknown')
            if suffix not in file_types:
                file_types[suffix] = {'count': 0, 'total_chars': 0}
            file_types[suffix]['count'] += 1
            file_types[suffix]['total_chars'] += len(doc.text)

        print(f"\n文件类型详细统计:")
        for suffix, stats in sorted(file_types.items()):
            avg_chars = stats['total_chars'] // stats['count']
            print(f"  {suffix}: {stats['count']} 文件, 平均 {avg_chars} 字符")

    except Exception as e:
        print(f"错误: {e}")


def demo_nested_7z(temp_dir):
    """多层嵌套 7Z 演示"""
    print("\n" + "=" * 80)
    print("演示 8: 多层嵌套 7Z 压缩包")
    print("=" * 80)

    sevenzip_reader = SevenZipReader()

    try:
        import py7zr

        # 创建嵌套演示的基础目录
        nested_base = os.path.join(temp_dir, "nested_demo")
        os.makedirs(nested_base, exist_ok=True)

        print("\n创建多层嵌套结构...")

        # 创建第3层（最深层）
        level3_dir = os.path.join(nested_base, "level3")
        os.makedirs(level3_dir, exist_ok=True)
        with open(os.path.join(level3_dir, "深层配置.json"), 'w', encoding='utf-8') as f:
            f.write("""{
                "level": 3,
                "description": "最深层的配置文件",
                "settings": {
                    "compression": "maximum",
                    "encryption": true,
                    "password_protected": false
                }
            }""")
        with open(os.path.join(level3_dir, "数据备份.csv"), 'w', encoding='utf-8') as f:
            f.write("""id,项目,数值,状态
                1,项目A,100.5,完成
                2,项目B,250.75,进行中
                3,项目C,89.25,待开始
                """)

        # 创建第3层7Z压缩包
        level3_7z = os.path.join(nested_base, "level3.7z")
        with py7zr.SevenZipFile(level3_7z, 'w') as archive:
            archive.writeall(level3_dir, 'level3')
        print("  ✓ 创建第 3 层 7Z")

        # 创建第2层
        level2_dir = os.path.join(nested_base, "level2")
        os.makedirs(level2_dir, exist_ok=True)
        with open(os.path.join(level2_dir, "中层说明.md"), 'w', encoding='utf-8') as f:
            f.write("""# 中层文档
                这是第二层的文档文件。
                包含业务逻辑和下一层的压缩包。
                ## 功能模块
                - 数据处理
                - 配置管理
                - 压缩包嵌套
                """)
        # 将第3层7Z复制到第2层
        shutil.copy(level3_7z, level2_dir)
        with open(os.path.join(level2_dir, "业务数据.yaml"), 'w', encoding='utf-8') as f:
            f.write("""departments:
                - name: "技术部"
                    employees: 25
                    budget: 500000
                - name: "销售部" 
                    employees: 18
                    budget: 300000
                - name: "人事部"
                    employees: 8
                    budget: 150000
                """)

        # 创建第2层7Z压缩包（包含第3层7Z）
        level2_7z = os.path.join(nested_base, "level2.7z")
        with py7zr.SevenZipFile(level2_7z, 'w') as archive:
            archive.writeall(level2_dir, 'level2')
        print("  ✓ 创建第 2 层 7Z（包含第 3 层）")

        # 创建第1层（最外层）
        level1_dir = os.path.join(nested_base, "level1")
        os.makedirs(level1_dir, exist_ok=True)
        with open(os.path.join(level1_dir, "项目总览.txt"), 'w', encoding='utf-8') as f:
            f.write("7Z 嵌套压缩包演示项目\n\n本项目展示了 SevenZipReader 处理多层嵌套 7Z 压缩包的能力。\n包含完整的业务数据和技术配置。")
        # 将第2层7Z复制到第1层
        shutil.copy(level2_7z, level1_dir)
        with open(os.path.join(level1_dir, "系统配置.xml"), 'w', encoding='utf-8') as f:
            f.write("""<?xml version="1.0" encoding="UTF-8"?>
                    <system>
                        <name>7Z嵌套演示系统</name>
                        <version>2.0.0</version>
                        <modules>
                            <module>数据压缩</module>
                            <module>配置管理</module>
                            <module>嵌套处理</module>
                        </modules>
                    </system>
                    """)

        # 创建最外层7Z压缩包
        nested_7z = os.path.join(nested_base, "nested_archive.7z")
        with py7zr.SevenZipFile(nested_7z, 'w') as archive:
            archive.writeall(level1_dir, 'level1')
        print("  ✓ 创建第 1 层 7Z（包含第 2 层）")
        print(f"\n已创建嵌套压缩包: {nested_7z}")

        print("\n正在提取嵌套压缩包...")
        # 使用SevenZipReader处理嵌套压缩包
        documents = sevenzip_reader.load_data(nested_7z, max_depth=5)

        print(f"\n成功提取 {len(documents)} 个文档")

        # 按嵌套深度分类文档
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
                content_preview = doc.text[:60].replace('\n', ' ') if len(doc.text) > 60 else doc.text.replace('\n', ' ')
                print(f"    - {file_name}")
                print(f"      路径: {archive_path}")
                print(f"      预览: {content_preview}...")

        print("\n嵌套统计:")
        print(f"  最大嵌套深度: {max(by_depth.keys())}")
        print(f"  总文档数: {len(documents)}")

        # 统计嵌套的7Z文件数量
        nested_7zs = [d for d in documents if d.metadata.get('file_suffix') == '.7z']
        if nested_7zs:
            print(f"  包含的嵌套 7Z: {len(nested_7zs)} 个")

        # 显示嵌套结构
        print("\n嵌套结构分析:")
        for depth in sorted(by_depth.keys()):
            print(f"  深度 {depth}:")
            for doc in by_depth[depth]:
                if doc.metadata.get('file_suffix') == '.7z':
                    print(f"    📦 {doc.metadata.get('file_name')} (嵌套压缩包)")
                else:
                    print(f"    📄 {doc.metadata.get('file_name')}")

    except ImportError:
        print("\n未找到 py7zr 库，跳过嵌套演示")
    except Exception as e:
        print(f"\n错误: {e}")


def demo_advanced_features(sevenzip_path):
    """高级功能演示"""
    print("\n" + "=" * 80)
    print("演示 9: 高级功能")
    print("=" * 80)

    sevenzip_reader = SevenZipReader()

    try:
        documents = sevenzip_reader.load_data(sevenzip_path)

        print("\n高级分析:")

        # 1. 文件路径分析
        print("\n1. 文件路径分析:")
        all_paths = [doc.metadata.get('archive_path', '') for doc in documents]
        for path in sorted(all_paths):
            print(f"   {path}")

        # 2. 内容关键词提取
        print("\n2. 内容关键词统计:")
        common_keywords = {
            '配置': 0, '数据': 0, '文件': 0, '项目': 0, 
            '处理': 0, '读取': 0, '压缩': 0, '演示': 0
        }
        
        for doc in documents:
            text_lower = doc.text.lower()
            for keyword in common_keywords.keys():
                if keyword in text_lower:
                    common_keywords[keyword] += 1

        for keyword, count in sorted(common_keywords.items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                print(f"   '{keyword}': 出现在 {count} 个文档中")

        # 3. 文档相关性分析
        print("\n3. 文档相关性分析:")
        config_docs = [doc for doc in documents if 'config' in doc.metadata.get('archive_path', '').lower()]
        code_docs = [doc for doc in documents if any(ext in doc.metadata.get('file_suffix', '') for ext in ['.py', '.json', '.yaml', '.xml'])]
        data_docs = [doc for doc in documents if 'data' in doc.metadata.get('archive_path', '').lower()]
        
        print(f"   配置文件: {len(config_docs)} 个")
        print(f"   代码文件: {len(code_docs)} 个") 
        print(f"   数据文件: {len(data_docs)} 个")

    except Exception as e:
        print(f"错误: {e}")


def cleanup(temp_dir):
    """清理临时文件"""
    print("\n" + "=" * 80)
    print("清理演示文件")
    print("=" * 80)

    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"已删除临时目录: {temp_dir}")


if __name__ == "__main__":
    print("=" * 80)
    print("SevenZip Reader 演示 - agentUniverse")
    print("=" * 80)
    print("\n本演示展示了 SevenZipReader 的功能:")
    print("  - 从 7Z 压缩包中读取各种文件格式")
    print("  - 嵌套 7Z 压缩包支持")
    print("  - 安全限制和压缩炸弹防护")
    print("  - 自定义元数据")
    print("  - FileReader 集成")
    print("  - 内容搜索和分析")

    # 创建示例压缩包
    sevenzip_path, temp_dir = create_sample_7z_archive()

    if sevenzip_path and os.path.exists(sevenzip_path):
        try:
            # 执行所有演示函数
            demo_sevenzip_reader_direct(sevenzip_path)
            demo_file_reader_integration(sevenzip_path)
            demo_custom_metadata(sevenzip_path)
            demo_custom_config(sevenzip_path)
            demo_filter_by_type(sevenzip_path)
            demo_content_search(sevenzip_path)
            demo_statistics(sevenzip_path)
            demo_nested_7z(temp_dir)
            demo_advanced_features(sevenzip_path)

            print("\n" + "=" * 80)
            print("演示完成！")
            print("=" * 80)

            print("\n使用提示:")
            print("  1. SevenZipReader 自动支持多种文件格式（Python、JSON、XML、YAML等）")
            print("  2. 可处理嵌套的 7Z 压缩包（默认最大深度：5 层）")
            print("  3. 安全限制可防护恶意压缩包和压缩炸弹")
            print("  4. 可为所有提取的文档添加自定义元数据")
            print("  5. FileReader 无缝集成 SevenZipReader")
            print("  6. 支持内容搜索和高级分析功能")

            print("\n依赖要求:")
            print("  - pip install py7zr")

        finally:
            # 清理临时文件
            cleanup(temp_dir)
    else:
        print("\n创建示例压缩包失败，演示终止。")
        print("\n依赖要求:")
        print("  - pip install py7zr")
        print("  - 无需外部命令行工具，纯Python实现")

        if temp_dir and os.path.exists(temp_dir):
            cleanup(temp_dir)
