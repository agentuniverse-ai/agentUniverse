import unittest
import tempfile
import os
import shutil
import time
from pathlib import Path
from agentuniverse.agent.action.knowledge.reader.file.sevenzip_reader import SevenZipReader

class TestSevenZipReaderBasic(unittest.TestCase):
    """SevenZipReader 基础功能测试"""
    def setUp(self):
        self.reader = SevenZipReader()
        self.temp_dir = tempfile.mkdtemp()
    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    def create_test_files(self):
        test_txt_path = os.path.join(self.temp_dir, "test.txt")
        with open(test_txt_path, 'w', encoding='utf-8') as f:
            f.write("这是一个测试文本文件，用于验证 7Z 读取器功能。")
        test_py_path = os.path.join(self.temp_dir, "test.py")
        with open(test_py_path, 'w', encoding='utf-8') as f:
            f.write("""#!/usr/bin/env python3
            def hello():
                print('Hello, 7Z Reader!')
            def process_data(data):
                return [x * 2 for x in data]""")
        test_json_path = os.path.join(self.temp_dir, "config.json")
        with open(test_json_path, 'w', encoding='utf-8') as f:
            f.write("""{"app_name": "7Z Reader Test", "version": "1.0.0", "features": ["compression", "extraction", "metadata"]}""")
        test_yaml_path = os.path.join(self.temp_dir, "settings.yaml")
        with open(test_yaml_path, 'w', encoding='utf-8') as f:
            f.write("""app:\n  name: "7Z Test Application"\n  debug: true\ndatabase:\n  host: "localhost"\n  port: 5432""")
        return [test_txt_path, test_py_path, test_json_path, test_yaml_path]
    def create_test_7z(self, files=None, password=None):
        try:
            import py7zr
        except ImportError:
            self.skipTest("py7zr not available for testing")
        if files is None:
            files = self.create_test_files()
        test_7z_path = os.path.join(self.temp_dir, "test_archive.7z")
        try:
            if password:
                with py7zr.SevenZipFile(test_7z_path, 'w', password=password) as archive:
                    for file_path in files:
                        archive.write(file_path, os.path.basename(file_path))
            else:
                with py7zr.SevenZipFile(test_7z_path, 'w') as archive:
                    for file_path in files:
                        archive.write(file_path, os.path.basename(file_path))
        except Exception as e:
            self.skipTest(f"Failed to create 7Z archive: {e}")
        return test_7z_path
    def test_load_data_success(self):
        try:
            import py7zr
        except ImportError:
            self.skipTest("py7zr not available for testing")
        test_7z_path = self.create_test_7z()
        documents = self.reader._load_data(test_7z_path)
        self.assertIsInstance(documents, list)
        self.assertGreater(len(documents), 0)
        file_names = [doc.metadata.get('file_name') for doc in documents]
        self.assertIn('test.txt', file_names)
        self.assertIn('test.py', file_names)
        self.assertIn('config.json', file_names)
    def test_load_data_with_custom_metadata(self):
        try:
            import py7zr
        except ImportError:
            self.skipTest("py7zr not available for testing")
        test_7z_path = self.create_test_7z()
        custom_metadata = {"source": "test_suite", "version": "2.0.0", "compression_format": "7Z", "test_scenario": "metadata_validation"}
        documents = self.reader._load_data(test_7z_path, ext_info=custom_metadata)
        self.assertGreater(len(documents), 0)
        doc = documents[0]
        self.assertEqual(doc.metadata['source'], 'test_suite')
        self.assertEqual(doc.metadata['version'], '2.0.0')
        self.assertEqual(doc.metadata['compression_format'], '7Z')
    def test_load_data_file_not_found(self):
        non_existent_file = os.path.join(self.temp_dir, "non_existent.7z")
        with self.assertRaises(FileNotFoundError):
            self.reader._load_data(non_existent_file)
    def test_metadata_structure(self):
        try:
            import py7zr
        except ImportError:
            self.skipTest("py7zr not available for testing")
        test_7z_path = self.create_test_7z()
        documents = self.reader._load_data(test_7z_path)
        self.assertGreater(len(documents), 0)
        doc = documents[0]
        required_fields = ['file_name', 'file_path', 'file_suffix', 'archive_root', 'archive_path', 'archive_depth']
        for field in required_fields:
            self.assertIn(field, doc.metadata)
        self.assertEqual(doc.metadata['archive_depth'], 0)
    def test_content_extraction_accuracy(self):
        try:
            import py7zr
        except ImportError:
            self.skipTest("py7zr not available for testing")
        test_content = "这是用于验证内容提取准确性的测试文本。"
        test_file = os.path.join(self.temp_dir, "content_test.txt")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        test_7z_path = self.create_test_7z(files=[test_file])
        documents = self.reader._load_data(test_7z_path)
        self.assertEqual(len(documents), 1)
        self.assertEqual(documents[0].text, test_content)

class TestSevenZipReaderComplexScenarios(unittest.TestCase):
    """SevenZipReader 复杂场景测试"""
    def setUp(self):
        self.reader = SevenZipReader()
        self.temp_dir = tempfile.mkdtemp()
    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    def create_complex_project_structure(self):
        project_dir = os.path.join(self.temp_dir, "complex_project")
        os.makedirs(project_dir, exist_ok=True)
        directories = ["src/utils", "src/models", "tests/unit", "tests/integration", "docs/api", "docs/tutorials", "config/environments", "data/raw", "data/processed", "logs/applications"]
        for directory in directories:
            os.makedirs(os.path.join(project_dir, directory), exist_ok=True)
        with open(os.path.join(project_dir, "README.md"), 'w', encoding='utf-8') as f:
            f.write("""# 复杂 7Z 项目\n这是一个用于测试 SevenZipReader 复杂场景的项目结构。\n## 功能特性\n- 多层目录结构\n- 多种文件格式支持\n- 完整的开发环境模拟""")
        with open(os.path.join(project_dir, "src", "main.py"), 'w', encoding='utf-8') as f:
            f.write("""#!/usr/bin/env python3\nimport sys\nimport json\nfrom utils.helpers import load_config\nfrom models.processor import DataProcessor\n\ndef main():\n    config = load_config()\n    processor = DataProcessor(config)\n    try:\n        data = processor.load_data()\n        result = processor.process(data)\n        processor.save_result(result)\n        print("Processing completed successfully")\n    except Exception as e:\n        print(f"Error: {e}")\n        sys.exit(1)\n\nif __name__ == "__main__":\n    main()""")
        with open(os.path.join(project_dir, "src", "utils", "helpers.py"), 'w', encoding='utf-8') as f:
            f.write("""import yaml\nimport json\n\ndef load_config():\n    with open('config/environments/development.yaml', 'r') as f:\n        return yaml.safe_load(f)\n\ndef setup_logging():\n    import logging\n    logging.basicConfig(level=logging.INFO)\n    return logging.getLogger(__name__)""")
        with open(os.path.join(project_dir, "src", "models", "processor.py"), 'w', encoding='utf-8') as f:
            f.write("""class DataProcessor:\n    def __init__(self, config):\n        self.config = config\n        self.logger = None\n    def load_data(self):\n        import pandas as pd\n        return pd.DataFrame({'id': [1, 2, 3], 'value': [100, 200, 300]})\n    def process(self, data):\n        data['processed'] = data['value'] * 2\n        return data\n    def save_result(self, result):\n        result.to_csv('data/processed/result.csv', index=False)""")
        with open(os.path.join(project_dir, "tests", "unit", "test_processor.py"), 'w', encoding='utf-8') as f:
            f.write("""import unittest\nfrom src.models.processor import DataProcessor\n\nclass TestDataProcessor(unittest.TestCase):\n    def setUp(self):\n        self.config = {'debug': True}\n        self.processor = DataProcessor(self.config)\n    def test_processor_initialization(self):\n        self.assertIsNotNone(self.processor)\n        self.assertEqual(self.processor.config, self.config)""")
        with open(os.path.join(project_dir, "tests", "integration", "test_main.py"), 'w', encoding='utf-8') as f:
            f.write("""import unittest\nimport sys\nimport os\nsys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))\n\nclass TestMainIntegration(unittest.TestCase):\n    def test_import_modules(self):\n        try:\n            from main import main\n            from utils.helpers import load_config\n            self.assertTrue(True)\n        except ImportError as e:\n            self.fail(f"Import failed: {e}")""")
        with open(os.path.join(project_dir, "config", "environments", "development.yaml"), 'w', encoding='utf-8') as f:
            f.write("""environment: "development"\ndebug: true\ndatabase:\n  host: "localhost"\n  port: 5432\n  name: "dev_db"\nlogging:\n  level: "DEBUG"\n  file: "logs/applications/app.log" """)
        with open(os.path.join(project_dir, "config", "environments", "production.yaml"), 'w', encoding='utf-8') as f:
            f.write("""environment: "production"\ndebug: false\ndatabase:\n  host: "db.production.com"\n  port: 5432\n  name: "prod_db"\nlogging:\n  level: "WARNING"\n  file: "/var/log/applications/app.log" """)
        with open(os.path.join(project_dir, "docs", "api", "rest_api.md"), 'w', encoding='utf-8') as f:
            f.write("""# REST API 文档\n## 用户端点\n### GET /api/users\n获取用户列表\n### POST /api/users\n创建新用户\n## 数据端点\n### GET /api/data\n获取数据""")
        with open(os.path.join(project_dir, "docs", "tutorials", "getting_started.md"), 'w', encoding='utf-8') as f:
            f.write("""# 入门教程\n## 安装依赖\n```bash\npip install -r requirements.txt\n```\n## 运行应用\n```bash\npython src/main.py\n```""")
        with open(os.path.join(project_dir, "data", "raw", "sample_data.json"), 'w', encoding='utf-8') as f:
            f.write("""[{"id": 1, "name": "项目A", "value": 100}, {"id": 2, "name": "项目B", "value": 200}, {"id": 3, "name": "项目C", "value": 300}]""")
        with open(os.path.join(project_dir, "data", "raw", "users.csv"), 'w', encoding='utf-8') as f:
            f.write("""id,username,email,department\n1,alice,alice@example.com,Engineering\n2,bob,bob@example.com,Marketing\n3,charlie,charlie@example.com,Sales""")
        return project_dir
    def create_nested_7z_structure(self):
        try:
            import py7zr
        except ImportError:
            self.skipTest("py7zr not available")
        base_dir = os.path.join(self.temp_dir, "nested")
        os.makedirs(base_dir, exist_ok=True)
        level3_dir = os.path.join(base_dir, "level3")
        os.makedirs(level3_dir, exist_ok=True)
        with open(os.path.join(level3_dir, "deep_config.json"), 'w', encoding='utf-8') as f:
            f.write("""{"level": 3, "description": "最深层的配置文件", "security": {"encryption": true, "access_level": "high"}}""")
        with open(os.path.join(level3_dir, "secret_data.txt"), 'w', encoding='utf-8') as f:
            f.write("这是嵌套在最深层的敏感数据文件。")
        level3_7z = os.path.join(base_dir, "level3_archive.7z")
        try:
            with py7zr.SevenZipFile(level3_7z, 'w') as archive:
                archive.writeall(level3_dir, 'level3')
        except Exception as e:
            self.skipTest(f"Failed to create level3 7Z: {e}")
        level2_dir = os.path.join(base_dir, "level2")
        os.makedirs(level2_dir, exist_ok=True)
        with open(os.path.join(level2_dir, "middle_document.md"), 'w', encoding='utf-8') as f:
            f.write("""# 中层文档\n这是第二层的文档文件。\n## 包含内容\n- 业务逻辑说明\n- 下一层的压缩包\n- 配置信息""")
        shutil.copy(level3_7z, level2_dir)
        with open(os.path.join(level2_dir, "business_rules.yaml"), 'w', encoding='utf-8') as f:
            f.write("""rules:\n  - name: "数据验证规则"\n    condition: "data.value > 0"\n    action: "accept"\n  - name: "安全规则"\n    condition: "user.role == 'admin'"\n    action: "grant_access" """)
        level2_7z = os.path.join(base_dir, "level2_archive.7z")
        try:
            with py7zr.SevenZipFile(level2_7z, 'w') as archive:
                archive.writeall(level2_dir, 'level2')
        except Exception as e:
            self.skipTest(f"Failed to create level2 7Z: {e}")
        level1_dir = os.path.join(base_dir, "level1")
        os.makedirs(level1_dir, exist_ok=True)
        with open(os.path.join(level1_dir, "project_overview.txt"), 'w', encoding='utf-8') as f:
            f.write("7Z 嵌套压缩包演示项目\n\n本项目展示了 SevenZipReader 处理多层嵌套 7Z 压缩包的能力。")
        shutil.copy(level2_7z, level1_dir)
        with open(os.path.join(level1_dir, "system_config.xml"), 'w', encoding='utf-8') as f:
            f.write("""<?xml version="1.0" encoding="UTF-8"?>\n<system>\n    <name>7Z嵌套演示系统</name>\n    <version>2.0.0</version>\n    <components>\n        <component>数据压缩模块</component>\n        <component>配置管理模块</component>\n        <component>嵌套处理模块</component>\n    </components>\n</system>""")
        final_7z = os.path.join(self.temp_dir, "nested_project.7z")
        try:
            with py7zr.SevenZipFile(final_7z, 'w') as archive:
                archive.writeall(level1_dir, 'level1')
        except Exception as e:
            self.skipTest(f"Failed to create final nested 7Z: {e}")
        return final_7z
    def test_complex_project_structure(self):
        try:
            import py7zr
        except ImportError:
            self.skipTest("py7zr not available")
        project_dir = self.create_complex_project_structure()
        sevenzip_path = os.path.join(self.temp_dir, "complex_project.7z")
        try:
            with py7zr.SevenZipFile(sevenzip_path, 'w') as archive:
                archive.writeall(project_dir, '')
        except Exception as e:
            self.skipTest(f"Failed to create project 7Z: {e}")
        documents = self.reader._load_data(sevenzip_path)
        self.assertGreater(len(documents), 10)
        file_types = set(doc.metadata.get('file_suffix') for doc in documents)
        expected_types = {'.py', '.yaml', '.md', '.json', '.csv'}
        for expected_type in expected_types:
            self.assertIn(expected_type, file_types)
        file_names = [doc.metadata.get('file_name') for doc in documents]
        self.assertIn('main.py', file_names)
        self.assertIn('development.yaml', file_names)
        self.assertIn('sample_data.json', file_names)
    def test_nested_7z_archives(self):
        try:
            import py7zr
        except ImportError:
            self.skipTest("py7zr not available")
        nested_7z = self.create_nested_7z_structure()
        documents = self.reader._load_data(nested_7z, max_depth=4)
        self.assertGreater(len(documents), 0)
        depths = set(doc.metadata.get('archive_depth') for doc in documents)
        self.assertTrue(len(depths) > 1)
        deep_files = [doc for doc in documents if doc.metadata.get('archive_depth', 0) > 1]
        self.assertGreater(len(deep_files), 0)
    def test_multiple_file_types_and_encodings(self):
        try:
            import py7zr
        except ImportError:
            self.skipTest("py7zr not available")
        files_dir = os.path.join(self.temp_dir, "mixed_files")
        os.makedirs(files_dir, exist_ok=True)
        files_content = {
            "document.txt": "这是 UTF-8 编码的文本文件内容",
            "script.py": "#!/usr/bin/env python3\nprint('Python 脚本文件')",
            "data.json": '{"类型": "测试", "数值": 123, "数组": [1, 2, 3]}',
            "config.yaml": "应用:\n  名称: 测试应用\n  端口: 8080\n调试: true",
            "code.js": "// JavaScript 文件\nconsole.log('Hello, 7Z Reader!');",
            "style.css": "/* CSS 文件 */\nbody { margin: 0; font-family: Arial; }",
            "page.html": "<!DOCTYPE html>\n<html>\n<head>\n    <title>测试页面</title>\n</head>\n<body>\n    <h1>Hello, 7Z Reader!</h1>\n</body>\n</html>",
            "database.sql": "-- SQL 脚本\nCREATE TABLE users (\n    id INT PRIMARY KEY,\n    name VARCHAR(100),\n    email VARCHAR(255)\n);",
            "log_file.log": "[2024-01-01 10:00:00] INFO: 应用程序启动\n[2024-01-01 10:00:01] DEBUG: 加载配置",
            "special_中文文件.md": "# 包含中文文件名的文件\n这是测试中文文件名支持的文件。"
        }
        for filename, content in files_content.items():
            with open(os.path.join(files_dir, filename), 'w', encoding='utf-8') as f:
                f.write(content)
        sevenzip_path = os.path.join(self.temp_dir, "mixed_files.7z")
        try:
            with py7zr.SevenZipFile(sevenzip_path, 'w') as archive:
                archive.writeall(files_dir, '')
        except Exception as e:
            self.skipTest(f"Failed to create mixed files 7Z: {e}")
        documents = self.reader._load_data(sevenzip_path)
        self.assertEqual(len(documents), len(files_content))
        found_suffixes = set(doc.metadata.get('file_suffix') for doc in documents)
        expected_suffixes = {'.txt', '.py', '.json', '.yaml', '.js', '.css', '.html', '.sql', '.log', '.md'}
        for suffix in expected_suffixes:
            self.assertIn(suffix, found_suffixes)
        chinese_files = [doc for doc in documents if '中文' in doc.metadata.get('file_name', '')]
        self.assertGreater(len(chinese_files), 0)

class TestSevenZipReaderSizeLimits(unittest.TestCase):
    """SevenZipReader 大小限制测试"""
    def setUp(self):
        self.reader = SevenZipReader()
        self.temp_dir = tempfile.mkdtemp()
    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    def test_max_file_size_limit(self):
        try:
            import py7zr
        except ImportError:
            self.skipTest("py7zr not available")
        large_file = os.path.join(self.temp_dir, "large_data.txt")
        with open(large_file, 'w', encoding='utf-8') as f:
            for i in range(20000):
                f.write(f"Line {i}: 这是用于测试大文件处理的数据行，包含一些变化内容以避免过度压缩。 {i * 123}\n")
        sevenzip_path = os.path.join(self.temp_dir, "large_file.7z")
        try:
            with py7zr.SevenZipFile(sevenzip_path, 'w') as archive:
                archive.write(large_file, 'large_data.txt')
        except Exception as e:
            self.skipTest(f"Failed to create large file 7Z: {e}")
        documents = self.reader._load_data(sevenzip_path, max_file_size=100 * 1024)
        self.assertIsInstance(documents, list)
        self.assertLessEqual(len(documents), 1)
    def test_max_total_size_limit(self):
        try:
            import py7zr
        except ImportError:
            self.skipTest("py7zr not available")
        files = []
        for i in range(5):
            filepath = os.path.join(self.temp_dir, f"data_file_{i}.txt")
            with open(filepath, 'w', encoding='utf-8') as f:
                content = f"文件 {i} 的内容:\n"
                content += "这是一些测试数据 " * 1000
                f.write(content)
            files.append(filepath)
        sevenzip_path = os.path.join(self.temp_dir, "multiple_files.7z")
        try:
            with py7zr.SevenZipFile(sevenzip_path, 'w') as archive:
                for file_path in files:
                    archive.write(file_path, os.path.basename(file_path))
        except Exception as e:
            self.skipTest(f"Failed to create multiple files 7Z: {e}")
        documents = self.reader._load_data(sevenzip_path, max_total_size=100 * 1024)
        self.assertIsInstance(documents, list)
        self.assertLess(len(documents), len(files))
    def test_max_files_limit(self):
        try:
            import py7zr
        except ImportError:
            self.skipTest("py7zr not available")
        files_dir = os.path.join(self.temp_dir, "many_files")
        os.makedirs(files_dir, exist_ok=True)
        file_count = 25
        for i in range(file_count):
            filepath = os.path.join(files_dir, f"small_file_{i:02d}.txt")
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"这是小文件 {i} 的内容。")
        sevenzip_path = os.path.join(self.temp_dir, "many_files.7z")
        try:
            with py7zr.SevenZipFile(sevenzip_path, 'w') as archive:
                archive.writeall(files_dir, '')
        except Exception as e:
            self.skipTest(f"Failed to create many files 7Z: {e}")
        documents = self.reader._load_data(sevenzip_path, max_files=10)
        self.assertLessEqual(len(documents), 10)
    def test_compression_ratio_detection(self):
        try:
            import py7zr
        except ImportError:
            self.skipTest("py7zr not available")
        test_file = os.path.join(self.temp_dir, "highly_compressible.txt")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("0" * (100 * 1024))
        sevenzip_path = os.path.join(self.temp_dir, "high_compression.7z")
        try:
            with py7zr.SevenZipFile(sevenzip_path, 'w') as archive:
                archive.write(test_file, 'highly_compressible.txt')
        except Exception as e:
            self.skipTest(f"Failed to create high compression 7Z: {e}")
        try:
            documents = self.reader._load_data(sevenzip_path, max_compression_ratio=10.0)
            self.assertIsInstance(documents, list)
        except ValueError as e:
            if "compression ratio" in str(e).lower():
                pass
            else:
                raise

class TestSevenZipReaderRealWorldScenarios(unittest.TestCase):
    """SevenZipReader 真实世界场景测试"""
    def setUp(self):
        self.reader = SevenZipReader()
        self.temp_dir = tempfile.mkdtemp()
    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    def create_software_distribution_package(self):
        dist_dir = os.path.join(self.temp_dir, "myapp_v2.0.0")
        os.makedirs(dist_dir, exist_ok=True)
        os.makedirs(os.path.join(dist_dir, "bin"), exist_ok=True)
        os.makedirs(os.path.join(dist_dir, "lib"), exist_ok=True)
        os.makedirs(os.path.join(dist_dir, "docs"), exist_ok=True)
        os.makedirs(os.path.join(dist_dir, "config"), exist_ok=True)
        os.makedirs(os.path.join(dist_dir, "examples"), exist_ok=True)
        with open(os.path.join(dist_dir, "INSTALL.txt"), 'w', encoding='utf-8') as f:
            f.write("""MyApp 2.0.0 安装说明\n========================\n系统要求:\n- Python 3.8+\n- 100MB 可用磁盘空间\n\n安装步骤:\n1. 解压此压缩包\n2. 运行 bin/install.py\n3. 按照提示完成配置\n\n技术支持:\n- 邮箱: support@myapp.com\n- 文档: docs/manual.html""")
        with open(os.path.join(dist_dir, "bin", "install.py"), 'w', encoding='utf-8') as f:
            f.write("""#!/usr/bin/env python3\nimport sys\nimport os\nimport shutil\n\ndef main():\n    print("MyApp 安装程序")\n    print("==============")\n    if sys.version_info < (3, 8):\n        print("错误: 需要 Python 3.8 或更高版本")\n        sys.exit(1)\n    lib_src = os.path.join(os.path.dirname(__file__), '../lib')\n    lib_dest = '/usr/local/lib/myapp'\n    try:\n        shutil.copytree(lib_src, lib_dest)\n        print(f"库文件已安装到: {lib_dest}")\n    except Exception as e:\n        print(f"安装库文件时出错: {e}")\n        sys.exit(1)\n    print("安装完成!")\n\nif __name__ == "__main__":\n    main()""")
        with open(os.path.join(dist_dir, "lib", "core.py"), 'w', encoding='utf-8') as f:
            f.write("""class ApplicationCore:\n    def __init__(self, config):\n        self.config = config\n        self.plugins = []\n    def initialize(self):\n        self._load_plugins()\n        self._setup_database()\n    def _load_plugins(self):\n        import os\n        plugin_dir = self.config.get('plugin_dir', './plugins')\n        if os.path.exists(plugin_dir):\n            for file in os.listdir(plugin_dir):\n                if file.endswith('.py'):\n                    self._load_plugin(os.path.join(plugin_dir, file))\n    def _load_plugin(self, plugin_path):\n        plugin_name = os.path.basename(plugin_path).replace('.py', '')\n        self.plugins.append(plugin_name)\n    def _setup_database(self):\n        db_config = self.config.get('database', {})\n        if db_config:\n            print(f"数据库配置: {db_config}")\n    def run(self):\n        print("MyApp 核心运行中...")\n        print(f"已加载插件: {self.plugins}")""")
        with open(os.path.join(dist_dir, "docs", "manual.html"), 'w', encoding='utf-8') as f:
            f.write("""<!DOCTYPE html>\n<html>\n<head>\n    <title>MyApp 用户手册</title>\n</head>\n<body>\n    <h1>MyApp 用户手册</h1>\n    <h2>快速开始</h2>\n    <ol>\n        <li>安装软件</li>\n        <li>配置参数</li>\n        <li>启动应用</li>\n    </ol>\n    <h2>功能特性</h2>\n    <ul>\n        <li>高性能数据处理</li>\n        <li>插件系统</li>\n        <li>多平台支持</li>\n    </ul>\n</body>\n</html>""")
        with open(os.path.join(dist_dir, "config", "app_config.yaml"), 'w', encoding='utf-8') as f:
            f.write("""# MyApp 配置文件模板\n# 复制此文件为 config.yaml 并修改相应配置\n\napplication:\n  name: "MyApp"\n  version: "2.0.0"\n  debug: false\n  log_level: "INFO"\n\ndatabase:\n  host: "localhost"\n  port: 5432\n  name: "myapp_db"\n  username: "db_user"\n  # password: "请在此设置密码"\n\nserver:\n  host: "0.0.0.0"\n  port: 8080\n  ssl_enabled: false\n\nplugins:\n  enabled: true\n  directory: "./plugins" """)
        with open(os.path.join(dist_dir, "examples", "basic_usage.py"), 'w', encoding='utf-8') as f:
            f.write("""#!/usr/bin/env python3\n\"\"\"\nMyApp 基础使用示例\n\"\"\"\n\nimport sys\nimport os\n\n# 添加 lib 目录到路径\nsys.path.append(os.path.join(os.path.dirname(__file__), '../lib'))\n\nfrom core import ApplicationCore\n\ndef main():\n    # 基础配置\n    config = {\n        'application': {\n            'name': '示例应用',\n            'debug': True\n        },\n        'database': {\n            'host': 'localhost',\n            'port': 5432,\n            'name': 'example_db'\n        }\n    }\n    \n    # 创建应用实例\n    app = ApplicationCore(config)\n    \n    # 初始化应用\n    app.initialize()\n    \n    # 运行应用\n    app.run()\n\nif __name__ == "__main__":\n    main()""")
        return dist_dir
    def test_software_distribution_package(self):
        try:
            import py7zr
        except ImportError:
            self.skipTest("py7zr not available")
        dist_dir = self.create_software_distribution_package()
        sevenzip_path = os.path.join(self.temp_dir, "myapp_distribution.7z")
        try:
            with py7zr.SevenZipFile(sevenzip_path, 'w') as archive:
                archive.writeall(dist_dir, 'myapp_v2.0.0')
        except Exception as e:
            self.skipTest(f"Failed to create distribution 7Z: {e}")
        documents = self.reader._load_data(sevenzip_path)
        self.assertGreater(len(documents), 5)
        install_docs = [d for d in documents if 'INSTALL' in d.metadata.get('file_name', '')]
        self.assertGreater(len(install_docs), 0)
        config_docs = [d for d in documents if 'config' in d.metadata.get('file_name', '').lower()]
        self.assertGreater(len(config_docs), 0)
        core_docs = [d for d in documents if d.metadata.get('file_name') == 'core.py']
        self.assertGreater(len(core_docs), 0)
    def test_documentation_archive_with_metadata(self):
        try:
            import py7zr
        except ImportError:
            self.skipTest("py7zr not available")
        doc_dir = os.path.join(self.temp_dir, "documentation")
        os.makedirs(doc_dir, exist_ok=True)
        os.makedirs(os.path.join(doc_dir, "api"), exist_ok=True)
        os.makedirs(os.path.join(doc_dir, "tutorials"), exist_ok=True)
        os.makedirs(os.path.join(doc_dir, "guides"), exist_ok=True)
        with open(os.path.join(doc_dir, "README.md"), 'w', encoding='utf-8') as f:
            f.write("""# 项目文档\n这是 SevenZipReader 测试用的文档存档。\n包含 API 文档、教程和指南。""")
        with open(os.path.join(doc_dir, "api", "rest_api.md"), 'w', encoding='utf-8') as f:
            f.write("""# REST API 参考\n## 认证端点\n### POST /auth/login\n用户登录\n### GET /auth/logout\n用户登出\n## 数据端点\n### GET /api/data\n获取数据列表\n### POST /api/data\n创建新数据""")
        with open(os.path.join(doc_dir, "tutorials", "quick_start.md"), 'w', encoding='utf-8') as f:
            f.write("""# 快速入门教程\n## 第一步：环境准备\n安装 Python 和必要依赖。\n## 第二步：配置应用\n修改配置文件。\n## 第三步：运行测试\n执行测试命令验证安装。""")
        with open(os.path.join(doc_dir, "guides", "development.md"), 'w', encoding='utf-8') as f:
            f.write("""# 开发指南\n## 代码规范\n- 遵循 PEP 8\n- 编写单元测试\n- 使用类型注解\n## 提交规范\n- 清晰的提交信息\n- 关联问题编号\n- 通过所有测试""")
        sevenzip_path = os.path.join(self.temp_dir, "documentation.7z")
        try:
            with py7zr.SevenZipFile(sevenzip_path, 'w') as archive:
                archive.writeall(doc_dir, '')
        except Exception as e:
            self.skipTest(f"Failed to create documentation 7Z: {e}")
        project_metadata = {"project": "SevenZipReader", "category": "documentation", "version": "2.0.0", "author": "Test Team", "description": "测试文档存档"}
        documents = self.reader._load_data(sevenzip_path, ext_info=project_metadata)
        self.assertGreater(len(documents), 3)
        for doc in documents:
            self.assertEqual(doc.metadata.get('project'), 'SevenZipReader')
            self.assertEqual(doc.metadata.get('category'), 'documentation')
        md_docs = [d for d in documents if d.metadata.get('file_suffix') == '.md']
        self.assertGreaterEqual(len(md_docs), 3)

class TestSevenZipReaderEdgeCases(unittest.TestCase):
    """SevenZipReader 边界情况测试"""
    def setUp(self):
        self.reader = SevenZipReader()
        self.temp_dir = tempfile.mkdtemp()
    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    def test_empty_7z_archive(self):
        try:
            import py7zr
        except ImportError:
            self.skipTest("py7zr not available")
        empty_7z_path = os.path.join(self.temp_dir, "empty.7z")
        try:
            with py7zr.SevenZipFile(empty_7z_path, 'w') as archive:
                pass
        except Exception as e:
            self.skipTest(f"Failed to create empty 7Z: {e}")
        documents = self.reader._load_data(empty_7z_path)
        self.assertIsInstance(documents, list)
        self.assertEqual(len(documents), 0)
    def test_special_characters_in_filenames(self):
        try:
            import py7zr
        except ImportError:
            self.skipTest("py7zr not available")
        special_files = {
            "测试文件_中文.txt": "包含中文文件名的测试文件",
            "file with spaces.txt": "包含空格的文件名",
            "file-with-dashes.txt": "包含连字符的文件名",
            "file.with.dots.txt": "包含点的文件名",
            "mixed_case_FILE.TXT": "混合大小写的文件名",
            "unicode_测试_文件🎉.txt": "包含Unicode表情的文件名",
        }
        files_dir = os.path.join(self.temp_dir, "special_names")
        os.makedirs(files_dir, exist_ok=True)
        for filename, content in special_files.items():
            with open(os.path.join(files_dir, filename), 'w', encoding='utf-8') as f:
                f.write(content)
        sevenzip_path = os.path.join(self.temp_dir, "special_names.7z")
        try:
            with py7zr.SevenZipFile(sevenzip_path, 'w') as archive:
                archive.writeall(files_dir, '')
        except Exception as e:
            self.skipTest(f"Failed to create special names 7Z: {e}")
        documents = self.reader._load_data(sevenzip_path)
        self.assertEqual(len(documents), len(special_files))
        extracted_names = [doc.metadata.get('file_name') for doc in documents]
        for original_name in special_files.keys():
            self.assertIn(original_name, extracted_names)
    def test_deep_directory_structure(self):
        try:
            import py7zr
        except ImportError:
            self.skipTest("py7zr not available")
        deep_dir = self.temp_dir
        depth = 8
        for i in range(depth):
            deep_dir = os.path.join(deep_dir, f"level_{i:02d}")
            os.makedirs(deep_dir, exist_ok=True)
        deep_file = os.path.join(deep_dir, "deep_nested_file.txt")
        with open(deep_file, 'w', encoding='utf-8') as f:
            f.write("这是位于深层嵌套目录中的文件。")
        mid_file = os.path.join(self.temp_dir, "level_00", "level_01", "mid_level_file.yaml")
        os.makedirs(os.path.dirname(mid_file), exist_ok=True)
        with open(mid_file, 'w', encoding='utf-8') as f:
            f.write("config:\n  level: mid\n  description: 中间层文件")
        sevenzip_path = os.path.join(self.temp_dir, "deep_structure.7z")
        try:
            with py7zr.SevenZipFile(sevenzip_path, 'w') as archive:
                archive.writeall(self.temp_dir, '')
        except Exception as e:
            self.skipTest(f"Failed to create deep structure 7Z: {e}")
        documents = self.reader._load_data(sevenzip_path)
        self.assertGreater(len(documents), 0)
        deep_files = [doc for doc in documents if 'deep_nested_file' in doc.metadata.get('file_name', '')]
        self.assertEqual(len(deep_files), 1)
        deep_doc = deep_files[0]
        self.assertIn('level_07', deep_doc.metadata.get('archive_path', ''))
    def test_path_handling_with_different_types(self):
        try:
            import py7zr
        except ImportError:
            self.skipTest("py7zr not available")
        test_file = os.path.join(self.temp_dir, "path_test.txt")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("路径处理测试文件")
        sevenzip_path = os.path.join(self.temp_dir, "path_test.7z")
        try:
            with py7zr.SevenZipFile(sevenzip_path, 'w') as archive:
                archive.write(test_file, 'path_test.txt')
        except Exception as e:
            self.skipTest(f"Failed to create path test 7Z: {e}")
        docs_str = self.reader._load_data(sevenzip_path)
        docs_path = self.reader._load_data(Path(sevenzip_path))
        self.assertEqual(len(docs_str), len(docs_path))
        if docs_str and docs_path:
            self.assertEqual(docs_str[0].text, docs_path[0].text)
            self.assertEqual(docs_str[0].metadata['file_name'], docs_path[0].metadata['file_name'])
    def test_mixed_text_encodings_and_formats(self):
        try:
            import py7zr
        except ImportError:
            self.skipTest("py7zr not available")
        files_dir = os.path.join(self.temp_dir, "mixed_encodings")
        os.makedirs(files_dir, exist_ok=True)
        with open(os.path.join(files_dir, "utf8_bom.txt"), 'w', encoding='utf-8-sig') as f:
            f.write("UTF-8 with BOM: 测试文本")
        with open(os.path.join(files_dir, "utf8_nobom.txt"), 'w', encoding='utf-8') as f:
            f.write("UTF-8 without BOM: 测试文本")
        with open(os.path.join(files_dir, "unicode_chars.txt"), 'w', encoding='utf-8') as f:
            f.write("Unicode 测试: 🌟🎉🚀 中文测试 ©®™")
        sevenzip_path = os.path.join(self.temp_dir, "mixed_encodings.7z")
        try:
            with py7zr.SevenZipFile(sevenzip_path, 'w') as archive:
                archive.writeall(files_dir, '')
        except Exception as e:
            self.skipTest(f"Failed to create mixed encodings 7Z: {e}")
        documents = self.reader._load_data(sevenzip_path)
        self.assertEqual(len(documents), 3)
        for doc in documents:
            self.assertIsInstance(doc.text, str)
            self.assertGreater(len(doc.text), 0)
            self.assertIn('测试', doc.text)

class TestSevenZipReaderPerformance(unittest.TestCase):
    """SevenZipReader 性能测试"""
    def setUp(self):
        self.reader = SevenZipReader()
        self.temp_dir = tempfile.mkdtemp()
    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    def test_large_number_of_small_files(self):
        try:
            import py7zr
        except ImportError:
            self.skipTest("py7zr not available")
        files_dir = os.path.join(self.temp_dir, "many_small_files")
        os.makedirs(files_dir, exist_ok=True)
        file_count = 100
        for i in range(file_count):
            filepath = os.path.join(files_dir, f"small_file_{i:03d}.txt")
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"这是小文件 {i} 的内容，用于性能测试。")
        sevenzip_path = os.path.join(self.temp_dir, "many_small_files.7z")
        try:
            with py7zr.SevenZipFile(sevenzip_path, 'w') as archive:
                archive.writeall(files_dir, '')
        except Exception as e:
            self.skipTest(f"Failed to create many small files 7Z: {e}")
        start_time = time.time()
        documents = self.reader._load_data(sevenzip_path, max_files=file_count)
        elapsed_time = time.time() - start_time
        self.assertLessEqual(len(documents), file_count)
        self.assertLess(elapsed_time, 30, f"处理 {file_count} 个文件耗时 {elapsed_time:.2f} 秒，超过性能要求")
        print(f"\n性能测试: 处理 {len(documents)}/{file_count} 个文件耗时 {elapsed_time:.2f} 秒")
    def test_reader_cache_efficiency(self):
        try:
            import py7zr
        except ImportError:
            self.skipTest("py7zr not available")
        files_dir = os.path.join(self.temp_dir, "cache_test")
        os.makedirs(files_dir, exist_ok=True)
        file_types = {'script.py': "print('Python script')", 'data.json': '{"test": "data"}', 'config.yaml': "app:\n  name: test", 'document.txt': "Text document content", 'readme.md': "# Markdown Document"}
        for filename, content in file_types.items():
            with open(os.path.join(files_dir, filename), 'w', encoding='utf-8') as f:
                f.write(content)
        sevenzip_path = os.path.join(self.temp_dir, "cache_test.7z")
        try:
            with py7zr.SevenZipFile(sevenzip_path, 'w') as archive:
                archive.writeall(files_dir, '')
        except Exception as e:
            self.skipTest(f"Failed to create cache test 7Z: {e}")
        self.reader._reader_cache.clear()
        documents1 = self.reader._load_data(sevenzip_path)
        cache_size_after_first = len(self.reader._reader_cache)
        self.assertGreater(cache_size_after_first, 0)
        documents2 = self.reader._load_data(sevenzip_path)
        cache_size_after_second = len(self.reader._reader_cache)
        self.assertEqual(cache_size_after_first, cache_size_after_second)
        self.assertEqual(len(documents1), len(documents2))

if __name__ == '__main__':
    unittest.main()