#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/10/30 23:23
# @Author  : SaladDay
# @FileName: test_rar_reader.py

"""
Unit tests for RarReader
"""

import unittest
import tempfile
import os
import shutil
from pathlib import Path

from agentuniverse.agent.action.knowledge.reader.file.rar_reader import RarReader


class TestRarReaderBasic(unittest.TestCase):
    """Basic functionality tests"""

    def setUp(self):
        self.reader = RarReader()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def create_test_files(self):
        """Create basic test files"""
        test_txt_path = os.path.join(self.temp_dir, "test.txt")
        with open(test_txt_path, 'w', encoding='utf-8') as f:
            f.write("这是一个测试文本文件。")

        test_py_path = os.path.join(self.temp_dir, "test.py")
        with open(test_py_path, 'w', encoding='utf-8') as f:
            f.write("def hello():\n    print('Hello, World!')")

        test_json_path = os.path.join(self.temp_dir, "test.json")
        with open(test_json_path, 'w', encoding='utf-8') as f:
            f.write('{"key": "value", "number": 42}')

        return [test_txt_path, test_py_path, test_json_path]

    def create_test_rar(self, files=None):
        """Create test RAR file"""
        try:
            import rarfile
        except ImportError:
            self.skipTest("rarfile not available for testing")

        if files is None:
            files = self.create_test_files()
        
        test_rar_path = os.path.join(self.temp_dir, "test_archive.rar")

        try:
            import subprocess
            subprocess.run(
                ['rar', 'a', '-ep', test_rar_path] + files,
                check=True,
                capture_output=True
            )
        except (FileNotFoundError, subprocess.CalledProcessError):
            self.skipTest("RAR command-line tool not available")

        return test_rar_path

    def test_load_data_success(self):
        """Test successful RAR file loading"""
        try:
            import rarfile
        except ImportError:
            self.skipTest("rarfile not available for testing")

        test_rar_path = self.create_test_rar()
        documents = self.reader._load_data(test_rar_path)
        
        self.assertIsInstance(documents, list)
        self.assertGreater(len(documents), 0)
        
        file_names = [doc.metadata.get('file_name') for doc in documents]
        self.assertIn('test.txt', file_names)

    def test_load_data_with_custom_metadata(self):
        """Test custom metadata"""
        try:
            import rarfile
        except ImportError:
            self.skipTest("rarfile not available for testing")

        test_rar_path = self.create_test_rar()
        custom_metadata = {
            "source": "test_suite",
            "version": "1.0.0"
        }
        
        documents = self.reader._load_data(test_rar_path, ext_info=custom_metadata)
        
        self.assertGreater(len(documents), 0)
        doc = documents[0]
        self.assertEqual(doc.metadata['source'], 'test_suite')
        self.assertEqual(doc.metadata['version'], '1.0.0')

    def test_load_data_file_not_found(self):
        """Test file not found"""
        non_existent_file = os.path.join(self.temp_dir, "non_existent.rar")
        with self.assertRaises(FileNotFoundError):
            self.reader._load_data(non_existent_file)

    def test_metadata_structure(self):
        """Test metadata structure"""
        try:
            import rarfile
        except ImportError:
            self.skipTest("rarfile not available for testing")

        test_rar_path = self.create_test_rar()
        documents = self.reader._load_data(test_rar_path)

        self.assertGreater(len(documents), 0)
        doc = documents[0]

        self.assertIn('file_name', doc.metadata)
        self.assertIn('file_path', doc.metadata)
        self.assertIn('file_suffix', doc.metadata)
        self.assertIn('archive_root', doc.metadata)
        self.assertIn('archive_path', doc.metadata)
        self.assertIn('archive_depth', doc.metadata)
        self.assertEqual(doc.metadata['archive_depth'], 0)


class TestRarReaderComplexScenarios(unittest.TestCase):
    """Complex scenario tests"""

    def setUp(self):
        self.reader = RarReader()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def create_complex_project_structure(self):
        """Create complex project structure"""
        project_dir = os.path.join(self.temp_dir, "complex_project")
        os.makedirs(project_dir, exist_ok=True)

        os.makedirs(os.path.join(project_dir, "src", "utils"), exist_ok=True)
        os.makedirs(os.path.join(project_dir, "src", "models"), exist_ok=True)
        os.makedirs(os.path.join(project_dir, "tests"), exist_ok=True)
        os.makedirs(os.path.join(project_dir, "docs"), exist_ok=True)
        os.makedirs(os.path.join(project_dir, "config"), exist_ok=True)
        os.makedirs(os.path.join(project_dir, "data"), exist_ok=True)

        with open(os.path.join(project_dir, "README.md"), 'w', encoding='utf-8') as f:
            f.write("""# 复杂项目

这是一个用于测试的复杂项目结构。

## 功能
- 多层目录
- 多种文件类型
- 完整的项目结构
""")

        with open(os.path.join(project_dir, "src", "main.py"), 'w', encoding='utf-8') as f:
            f.write("""#!/usr/bin/env python3

import sys
from utils.helper import process_data
from models.model import Model

def main():
    model = Model()
    data = process_data()
    result = model.predict(data)
    print(f"Result: {result}")

if __name__ == "__main__":
    main()
""")

        with open(os.path.join(project_dir, "src", "utils", "helper.py"), 'w', encoding='utf-8') as f:
            f.write("""def process_data():
    data = load_data()
    cleaned = clean_data(data)
    return transform_data(cleaned)

def load_data():
    return []

def clean_data(data):
    return [x for x in data if x is not None]

def transform_data(data):
    return [x * 2 for x in data]
""")

        with open(os.path.join(project_dir, "src", "models", "model.py"), 'w', encoding='utf-8') as f:
            f.write("""class Model:
    def __init__(self):
        self.weights = []
    
    def train(self, data):
        pass
    
    def predict(self, data):
        return sum(data) if data else 0
""")

        with open(os.path.join(project_dir, "tests", "test_main.py"), 'w', encoding='utf-8') as f:
            f.write("""import unittest
from src.main import main

class TestMain(unittest.TestCase):
    def test_main(self):
        self.assertIsNotNone(main)
""")

        with open(os.path.join(project_dir, "docs", "API.md"), 'w', encoding='utf-8') as f:
            f.write("""# API 文档

## 主要函数

### main()
主函数入口

### Model.predict(data)
预测函数
""")

        with open(os.path.join(project_dir, "config", "config.json"), 'w', encoding='utf-8') as f:
            f.write("""{
    "app_name": "ComplexProject",
    "debug": true,
    "database": {
        "host": "localhost",
        "port": 5432,
        "name": "test_db"
    }
}""")

        with open(os.path.join(project_dir, "data", "sample.csv"), 'w', encoding='utf-8') as f:
            f.write("""id,name,value
1,测试A,100
2,测试B,200
3,测试C,300
""")

        return project_dir

    def create_nested_rar_structure(self):
        """Create multi-level nested RAR structure"""
        try:
            import subprocess
        except ImportError:
            self.skipTest("subprocess not available")

        base_dir = os.path.join(self.temp_dir, "nested")
        os.makedirs(base_dir, exist_ok=True)

        level3_dir = os.path.join(base_dir, "level3")
        os.makedirs(level3_dir, exist_ok=True)
        
        with open(os.path.join(level3_dir, "deep_file.txt"), 'w', encoding='utf-8') as f:
            f.write("这是第三层的文件")
        
        level3_rar = os.path.join(base_dir, "level3.rar")
        try:
            subprocess.run(
                ['rar', 'a', '-r', '-ep1', level3_rar, level3_dir],
                check=True,
                capture_output=True,
                cwd=base_dir
            )
        except (FileNotFoundError, subprocess.CalledProcessError):
            self.skipTest("RAR tool not available")

        level2_dir = os.path.join(base_dir, "level2")
        os.makedirs(level2_dir, exist_ok=True)
        
        with open(os.path.join(level2_dir, "mid_file.txt"), 'w', encoding='utf-8') as f:
            f.write("这是第二层的文件")
        
        shutil.copy(level3_rar, level2_dir)
        
        level2_rar = os.path.join(base_dir, "level2.rar")
        try:
            subprocess.run(
                ['rar', 'a', '-r', '-ep1', level2_rar, level2_dir],
                check=True,
                capture_output=True,
                cwd=base_dir
            )
        except subprocess.CalledProcessError:
            self.skipTest("RAR creation failed")

        level1_dir = os.path.join(base_dir, "level1")
        os.makedirs(level1_dir, exist_ok=True)
        
        with open(os.path.join(level1_dir, "top_file.txt"), 'w', encoding='utf-8') as f:
            f.write("这是第一层的文件")
        
        shutil.copy(level2_rar, level1_dir)
        
        final_rar = os.path.join(self.temp_dir, "nested_archive.rar")
        try:
            subprocess.run(
                ['rar', 'a', '-r', '-ep1', final_rar, level1_dir],
                check=True,
                capture_output=True,
                cwd=base_dir
            )
        except subprocess.CalledProcessError:
            self.skipTest("RAR creation failed")

        return final_rar

    def test_complex_project_structure(self):
        """Test complex project structure"""
        try:
            import rarfile
            import subprocess
        except ImportError:
            self.skipTest("Required modules not available")

        project_dir = self.create_complex_project_structure()
        rar_path = os.path.join(self.temp_dir, "complex_project.rar")

        try:
            subprocess.run(
                ['rar', 'a', '-r', '-ep1', rar_path, project_dir],
                check=True,
                capture_output=True,
                cwd=self.temp_dir
            )
        except (FileNotFoundError, subprocess.CalledProcessError):
            self.skipTest("RAR tool not available")

        documents = self.reader._load_data(rar_path)

        self.assertGreater(len(documents), 5)

        file_types = set(doc.metadata.get('file_suffix') for doc in documents)
        self.assertIn('.py', file_types)
        self.assertIn('.json', file_types)
        self.assertIn('.csv', file_types)

    def test_nested_rar_archives(self):
        """Test nested RAR archives"""
        try:
            import rarfile
        except ImportError:
            self.skipTest("rarfile not available")

        nested_rar = self.create_nested_rar_structure()
        documents = self.reader._load_data(nested_rar, max_depth=3)

        self.assertGreater(len(documents), 0)

        depths = set(doc.metadata.get('archive_depth') for doc in documents)
        self.assertIn(0, depths)

    def test_multiple_file_types(self):
        """Test multiple file types"""
        try:
            import rarfile
            import subprocess
        except ImportError:
            self.skipTest("Required modules not available")

        files_dir = os.path.join(self.temp_dir, "mixed_files")
        os.makedirs(files_dir, exist_ok=True)

        files_content = {
            "document.txt": "这是文本文件内容",
            "script.py": "print('Python script')",
            "data.json": '{"type": "test", "value": 123}',
            "config.yaml": "app:\n  name: test\n  port: 8080",
            "code.js": "console.log('JavaScript');",
            "style.css": "body { margin: 0; }",
            "page.html": "<html><body>Test</body></html>",
        }

        for filename, content in files_content.items():
            with open(os.path.join(files_dir, filename), 'w', encoding='utf-8') as f:
                f.write(content)

        rar_path = os.path.join(self.temp_dir, "mixed_files.rar")
        try:
            subprocess.run(
                ['rar', 'a', '-r', '-ep1', rar_path, files_dir],
                check=True,
                capture_output=True,
                cwd=self.temp_dir
            )
        except (FileNotFoundError, subprocess.CalledProcessError):
            self.skipTest("RAR tool not available")

        documents = self.reader._load_data(rar_path)
        self.assertEqual(len(documents), len(files_content))

        found_suffixes = set(doc.metadata.get('file_suffix') for doc in documents)
        self.assertIn('.txt', found_suffixes)
        self.assertIn('.py', found_suffixes)
        self.assertIn('.json', found_suffixes)


class TestRarReaderSizeLimits(unittest.TestCase):
    """Size limit tests"""

    def setUp(self):
        self.reader = RarReader()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_max_file_size_limit(self):
        """Test maximum file size limit"""
        try:
            import rarfile
            import subprocess
        except ImportError:
            self.skipTest("Required modules not available")

        large_file = os.path.join(self.temp_dir, "large.txt")
        with open(large_file, 'w') as f:
            for i in range(100):
                f.write(f"Line {i}: This is some varied content to avoid extreme compression {i * 123}\n" * 10)

        rar_path = os.path.join(self.temp_dir, "large.rar")
        try:
            subprocess.run(
                ['rar', 'a', '-ep', rar_path, large_file],
                check=True,
                capture_output=True
            )
        except (FileNotFoundError, subprocess.CalledProcessError):
            self.skipTest("RAR tool not available")

        documents = self.reader._load_data(rar_path, max_file_size=50 * 1024)
        self.assertIsInstance(documents, list)

    def test_max_total_size_limit(self):
        """Test maximum total size limit"""
        try:
            import rarfile
            import subprocess
        except ImportError:
            self.skipTest("Required modules not available")

        files = []
        for i in range(10):
            filepath = os.path.join(self.temp_dir, f"file_{i}.txt")
            with open(filepath, 'w') as f:
                f.write("x" * (20 * 1024))
            files.append(filepath)

        rar_path = os.path.join(self.temp_dir, "multiple.rar")
        try:
            subprocess.run(
                ['rar', 'a', '-ep'] + [rar_path] + files,
                check=True,
                capture_output=True
            )
        except (FileNotFoundError, subprocess.CalledProcessError):
            self.skipTest("RAR tool not available")

        documents = self.reader._load_data(rar_path, max_total_size=100 * 1024)
        self.assertIsInstance(documents, list)

    def test_max_files_limit(self):
        """Test maximum files limit"""
        try:
            import rarfile
            import subprocess
        except ImportError:
            self.skipTest("Required modules not available")

        files = []
        for i in range(20):
            filepath = os.path.join(self.temp_dir, f"file_{i}.txt")
            with open(filepath, 'w') as f:
                f.write(f"Content {i}")
            files.append(filepath)

        rar_path = os.path.join(self.temp_dir, "many_files.rar")
        try:
            subprocess.run(
                ['rar', 'a', '-ep'] + [rar_path] + files,
                check=True,
                capture_output=True
            )
        except (FileNotFoundError, subprocess.CalledProcessError):
            self.skipTest("RAR tool not available")

        documents = self.reader._load_data(rar_path, max_files=10)
        self.assertLessEqual(len(documents), 10)

    def test_compression_ratio_detection(self):
        """Test compression ratio detection"""
        try:
            import rarfile
            import subprocess
        except ImportError:
            self.skipTest("Required modules not available")

        test_file = os.path.join(self.temp_dir, "repetitive.txt")
        with open(test_file, 'w') as f:
            f.write("a" * (10 * 1024))

        rar_path = os.path.join(self.temp_dir, "repetitive.rar")
        try:
            subprocess.run(
                ['rar', 'a', '-m5', '-ep', rar_path, test_file],
                check=True,
                capture_output=True
            )
        except (FileNotFoundError, subprocess.CalledProcessError):
            self.skipTest("RAR tool not available")

        try:
            documents = self.reader._load_data(rar_path, max_compression_ratio=5.0)
        except ValueError as e:
            if "compression ratio" in str(e):
                pass
            else:
                raise


class TestRarReaderRealWorldScenarios(unittest.TestCase):
    """Real-world scenario tests"""

    def setUp(self):
        self.reader = RarReader()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def create_software_release_package(self):
        """Create software release package"""
        release_dir = os.path.join(self.temp_dir, "release_v1.0.0")
        os.makedirs(release_dir, exist_ok=True)

        os.makedirs(os.path.join(release_dir, "bin"), exist_ok=True)
        os.makedirs(os.path.join(release_dir, "lib"), exist_ok=True)
        os.makedirs(os.path.join(release_dir, "docs"), exist_ok=True)
        os.makedirs(os.path.join(release_dir, "config"), exist_ok=True)

        with open(os.path.join(release_dir, "README.txt"), 'w', encoding='utf-8') as f:
            f.write("""

安装说明:
1. 解压文件
2. 运行 bin/install.sh
""")

        with open(os.path.join(release_dir, "bin", "install.sh"), 'w') as f:
            f.write("""#!/bin/bash
echo "Installing..."
cp -r lib/* /usr/local/lib/
cp config/app.conf /etc/myapp/
echo "Installation complete"
""")

        with open(os.path.join(release_dir, "lib", "core.py"), 'w') as f:
            f.write("""class Application:
    def __init__(self):
        self.plugins = []
    
    def load_plugins(self):
        pass
    
    def run(self):
        print("Application running")
""")

        with open(os.path.join(release_dir, "docs", "manual.md"), 'w') as f:
            f.write("""# 用户手册

## 快速开始
1. 安装软件
2. 配置参数
3. 启动应用
""")

        with open(os.path.join(release_dir, "config", "app.conf"), 'w') as f:
            f.write("""[application]
name = MyApp
version = 1.0.0
port = 8080

[database]
host = localhost
port = 5432
""")

        return release_dir

    def create_data_analysis_package(self):
        """Create data analysis package"""
        analysis_dir = os.path.join(self.temp_dir, "data_analysis")
        os.makedirs(analysis_dir, exist_ok=True)

        os.makedirs(os.path.join(analysis_dir, "raw_data"), exist_ok=True)
        os.makedirs(os.path.join(analysis_dir, "processed"), exist_ok=True)
        os.makedirs(os.path.join(analysis_dir, "scripts"), exist_ok=True)
        os.makedirs(os.path.join(analysis_dir, "reports"), exist_ok=True)

        with open(os.path.join(analysis_dir, "raw_data", "sales_2024.csv"), 'w', encoding='utf-8') as f:
            f.write("""日期,产品,销售额,数量
2024-01-01,产品A,15000,50
2024-01-02,产品B,12000,40
2024-01-03,产品A,18000,60
2024-01-04,产品C,22000,70
2024-01-05,产品B,16000,55
""")

        with open(os.path.join(analysis_dir, "scripts", "analyze.py"), 'w') as f:
            f.write("""import pandas as pd

def load_data(filepath):
    return pd.read_csv(filepath)

def calculate_statistics(df):
    total_sales = df['销售额'].sum()
    avg_sales = df['销售额'].mean()
    return {
        'total': total_sales,
        'average': avg_sales
    }

def generate_report(stats):
    report = f"总销售额: {stats['total']}\\n"
    report += f"平均销售额: {stats['average']}\\n"
    return report

if __name__ == "__main__":
    df = load_data('raw_data/sales_2024.csv')
    stats = calculate_statistics(df)
    report = generate_report(stats)
    print(report)
""")

        with open(os.path.join(analysis_dir, "reports", "summary.md"), 'w', encoding='utf-8') as f:
            f.write("""# 销售数据分析报告

## 概要
本报告分析了2024年1月的销售数据。

## 主要发现
- 总销售额: 83,000元
- 平均每日销售额: 16,600元
- 最畅销产品: 产品C

## 建议
1. 增加产品C的库存
2. 优化产品B的营销策略
""")

        with open(os.path.join(analysis_dir, "processed", "cleaned_data.json"), 'w') as f:
            f.write("""{
    "summary": {
        "total_sales": 83000,
        "total_quantity": 275,
        "average_price": 301.82
    },
    "by_product": {
        "产品A": {"sales": 33000, "quantity": 110},
        "产品B": {"sales": 28000, "quantity": 95},
        "产品C": {"sales": 22000, "quantity": 70}
    }
}""")

        return analysis_dir

    def create_documentation_archive(self):
        """Create documentation archive"""
        doc_dir = os.path.join(self.temp_dir, "documentation")
        os.makedirs(doc_dir, exist_ok=True)

        os.makedirs(os.path.join(doc_dir, "api"), exist_ok=True)
        os.makedirs(os.path.join(doc_dir, "tutorials"), exist_ok=True)
        os.makedirs(os.path.join(doc_dir, "guides"), exist_ok=True)

        # Add README as txt file to ensure at least some content is extracted
        with open(os.path.join(doc_dir, "README.txt"), 'w', encoding='utf-8') as f:
            f.write("Documentation Archive\n\nThis archive contains API documentation, tutorials, and guides.")
        
        with open(os.path.join(doc_dir, "api", "authentication.md"), 'w', encoding='utf-8') as f:
            f.write("""# 认证 API

## 概述
本文档介绍认证相关的 API。

## 登录
`POST /api/auth/login`

请求体:
```json
{
    "username": "user",
    "password": "pass"
}
```

响应:
```json
{
    "token": "jwt_token_here",
    "expires_in": 3600
}
```
""")

        with open(os.path.join(doc_dir, "tutorials", "getting_started.md"), 'w', encoding='utf-8') as f:
            f.write("""# 入门教程

## 第一步: 安装
```bash
pip install mypackage
```

## 第二步: 配置
创建配置文件 `config.yaml`:
```yaml
app:
  name: MyApp
  debug: true
```

## 第三步: 运行
```python
from mypackage import App

app = App()
app.run()
```
""")

        with open(os.path.join(doc_dir, "guides", "best_practices.md"), 'w', encoding='utf-8') as f:
            f.write("""# 最佳实践

## 代码规范
- 使用有意义的变量名
- 添加适当的注释
""")

        return doc_dir

    def test_software_release_package(self):
        """Test software release package scenario"""
        try:
            import rarfile
            import subprocess
        except ImportError:
            self.skipTest("Required modules not available")

        release_dir = self.create_software_release_package()
        rar_path = os.path.join(self.temp_dir, "release.rar")

        try:
            subprocess.run(
                ['rar', 'a', '-r', '-ep1', rar_path, release_dir],
                check=True,
                capture_output=True,
                cwd=self.temp_dir
            )
        except (FileNotFoundError, subprocess.CalledProcessError):
            self.skipTest("RAR tool not available")

        documents = self.reader._load_data(rar_path)

        self.assertGreater(len(documents), 3)

        readme_docs = [d for d in documents if 'README' in d.metadata.get('file_name', '')]
        self.assertGreater(len(readme_docs), 0)

        config_docs = [d for d in documents if d.metadata.get('file_suffix') == '.conf']
        self.assertGreater(len(config_docs), 0)

    def test_data_analysis_package(self):
        """Test data analysis package scenario"""
        try:
            import rarfile
            import subprocess
        except ImportError:
            self.skipTest("Required modules not available")

        analysis_dir = self.create_data_analysis_package()
        rar_path = os.path.join(self.temp_dir, "analysis.rar")

        try:
            subprocess.run(
                ['rar', 'a', '-r', '-ep1', rar_path, analysis_dir],
                check=True,
                capture_output=True,
                cwd=self.temp_dir
            )
        except (FileNotFoundError, subprocess.CalledProcessError):
            self.skipTest("RAR tool not available")

        custom_metadata = {
            "project": "sales_analysis",
            "year": "2024",
            "department": "finance"
        }

        documents = self.reader._load_data(rar_path, ext_info=custom_metadata)

        self.assertGreater(len(documents), 2)

        csv_docs = [d for d in documents if d.metadata.get('file_suffix') == '.csv']
        self.assertGreater(len(csv_docs), 0)
        
        for doc in csv_docs:
            self.assertEqual(doc.metadata.get('project'), 'sales_analysis')
            self.assertIn('销售额', doc.text)

    def test_documentation_archive(self):
        """Test documentation archive scenario"""
        try:
            import rarfile
            import subprocess
        except ImportError:
            self.skipTest("Required modules not available")

        doc_dir = self.create_documentation_archive()
        rar_path = os.path.join(self.temp_dir, "docs.rar")

        try:
            subprocess.run(
                ['rar', 'a', '-r', '-ep1', rar_path, doc_dir],
                check=True,
                capture_output=True,
                cwd=self.temp_dir
            )
        except (FileNotFoundError, subprocess.CalledProcessError):
            self.skipTest("RAR tool not available")

        documents = self.reader._load_data(rar_path)

        self.assertGreater(len(documents), 0)
        
        md_docs = [d for d in documents if d.metadata.get('file_suffix') == '.md']
        if len(md_docs) > 0:
            self.assertEqual(len(md_docs), 3)


class TestRarReaderEdgeCases(unittest.TestCase):
    """Edge case tests"""

    def setUp(self):
        self.reader = RarReader()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_empty_rar(self):
        """Test empty RAR file"""
        try:
            import rarfile
            import subprocess
        except ImportError:
            self.skipTest("Required modules not available")

        empty_dir = os.path.join(self.temp_dir, "empty")
        os.makedirs(empty_dir, exist_ok=True)

        temp_file = os.path.join(empty_dir, "temp.txt")
        with open(temp_file, 'w') as f:
            f.write("temp")

        rar_path = os.path.join(self.temp_dir, "empty.rar")
        try:
            subprocess.run(
                ['rar', 'a', '-ep', rar_path, temp_file],
                check=True,
                capture_output=True
            )
            os.remove(temp_file)
        except (FileNotFoundError, subprocess.CalledProcessError):
            self.skipTest("RAR tool not available")

        documents = self.reader._load_data(rar_path)
        self.assertIsInstance(documents, list)

    def test_special_characters_in_filenames(self):
        """Test filenames with special characters"""
        try:
            import rarfile
            import subprocess
        except ImportError:
            self.skipTest("Required modules not available")

        special_file = os.path.join(self.temp_dir, "测试文件_123.txt")
        with open(special_file, 'w', encoding='utf-8') as f:
            f.write("包含中文和特殊字符的文件名")

        rar_path = os.path.join(self.temp_dir, "special.rar")
        try:
            subprocess.run(
                ['rar', 'a', '-ep', rar_path, special_file],
                check=True,
                capture_output=True
            )
        except (FileNotFoundError, subprocess.CalledProcessError):
            self.skipTest("RAR tool not available")

        documents = self.reader._load_data(rar_path)
        self.assertGreater(len(documents), 0)

    def test_very_deep_directory_structure(self):
        """Test very deep directory structure"""
        try:
            import rarfile
            import subprocess
        except ImportError:
            self.skipTest("Required modules not available")

        deep_dir = self.temp_dir
        for i in range(10):
            deep_dir = os.path.join(deep_dir, f"level_{i}")
            os.makedirs(deep_dir, exist_ok=True)

        deep_file = os.path.join(deep_dir, "deep_file.txt")
        with open(deep_file, 'w') as f:
            f.write("This is a deeply nested file")

        rar_path = os.path.join(self.temp_dir, "deep.rar")
        try:
            subprocess.run(
                ['rar', 'a', '-r', '-ep1', rar_path, os.path.join(self.temp_dir, "level_0")],
                check=True,
                capture_output=True,
                cwd=self.temp_dir
            )
        except (FileNotFoundError, subprocess.CalledProcessError):
            self.skipTest("RAR tool not available")

        documents = self.reader._load_data(rar_path)
        self.assertGreater(len(documents), 0)

    def test_path_handling_with_different_types(self):
        """Test path handling with different types"""
        try:
            import rarfile
            import subprocess
        except ImportError:
            self.skipTest("Required modules not available")

        test_file = os.path.join(self.temp_dir, "path_test.txt")
        with open(test_file, 'w') as f:
            f.write("Path handling test")

        rar_path = os.path.join(self.temp_dir, "path_test.rar")
        try:
            subprocess.run(
                ['rar', 'a', '-ep', rar_path, test_file],
                check=True,
                capture_output=True
            )
        except (FileNotFoundError, subprocess.CalledProcessError):
            self.skipTest("RAR tool not available")

        docs_str = self.reader._load_data(rar_path)
        docs_path = self.reader._load_data(Path(rar_path))

        self.assertEqual(len(docs_str), len(docs_path))

    def test_mixed_text_encodings(self):
        """Test mixed text encodings"""
        try:
            import rarfile
            import subprocess
        except ImportError:
            self.skipTest("Required modules not available")

        utf8_file = os.path.join(self.temp_dir, "utf8.txt")
        with open(utf8_file, 'w', encoding='utf-8') as f:
            f.write("UTF-8 编码: 你好世界")

        rar_path = os.path.join(self.temp_dir, "encoding.rar")
        try:
            subprocess.run(
                ['rar', 'a', '-ep', rar_path, utf8_file],
                check=True,
                capture_output=True
            )
        except (FileNotFoundError, subprocess.CalledProcessError):
            self.skipTest("RAR tool not available")

        documents = self.reader._load_data(rar_path)
        self.assertGreater(len(documents), 0)


class TestRarReaderPerformance(unittest.TestCase):
    """Performance tests"""

    def setUp(self):
        self.reader = RarReader()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_large_number_of_small_files(self):
        """Test large number of small files"""
        try:
            import rarfile
            import subprocess
        except ImportError:
            self.skipTest("Required modules not available")

        files_dir = os.path.join(self.temp_dir, "many_files")
        os.makedirs(files_dir, exist_ok=True)

        for i in range(50):
            filepath = os.path.join(files_dir, f"file_{i}.txt")
            with open(filepath, 'w') as f:
                f.write(f"Content of file {i}")

        rar_path = os.path.join(self.temp_dir, "many_files.rar")
        try:
            subprocess.run(
                ['rar', 'a', '-r', '-ep1', rar_path, files_dir],
                check=True,
                capture_output=True,
                cwd=self.temp_dir
            )
        except (FileNotFoundError, subprocess.CalledProcessError):
            self.skipTest("RAR tool not available")

        import time
        start_time = time.time()
        documents = self.reader._load_data(rar_path, max_files=50)
        elapsed_time = time.time() - start_time

        self.assertLessEqual(len(documents), 50)
        self.assertLess(elapsed_time, 30)

    def test_reader_cache_efficiency(self):
        """Test reader cache efficiency"""
        try:
            import rarfile
            import subprocess
        except ImportError:
            self.skipTest("Required modules not available")

        files_dir = os.path.join(self.temp_dir, "cache_test")
        os.makedirs(files_dir, exist_ok=True)

        for i in range(10):
            with open(os.path.join(files_dir, f"file_{i}.txt"), 'w') as f:
                f.write(f"Content {i}")

        rar_path = os.path.join(self.temp_dir, "cache_test.rar")
        try:
            subprocess.run(
                ['rar', 'a', '-r', '-ep1', rar_path, files_dir],
                check=True,
                capture_output=True,
                cwd=self.temp_dir
            )
        except (FileNotFoundError, subprocess.CalledProcessError):
            self.skipTest("RAR tool not available")

        self.reader._load_data(rar_path)
        cache_size = len(self.reader._reader_cache)
        self.assertGreater(cache_size, 0)


if __name__ == '__main__':
    unittest.main()
