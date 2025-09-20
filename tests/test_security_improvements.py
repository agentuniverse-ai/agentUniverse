# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/19 12:00
# @Author  : AI Assistant
# @Email   : assistant@example.com
# @FileName: test_security_improvements.py

"""
测试安全改进功能
"""

import pytest
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agentuniverse.agent.action.tool.common_tool.run_command_tool import CommandSecurityValidator
from agentuniverse.agent.action.tool.tool import InputValidator
from agentuniverse.base.util.logging.logging_util import SensitiveInfoFilter


class TestCommandSecurityValidator:
    """测试命令安全验证器"""
    
    def test_allowed_commands(self):
        """测试允许的命令"""
        allowed_commands = [
            "ls",
            "pwd",
            "cat file.txt",
            "grep pattern file.txt",
            "find . -name '*.py'",
            "echo hello"
        ]
        
        for command in allowed_commands:
            assert CommandSecurityValidator.validate_command(command), f"Command '{command}' should be allowed"
    
    def test_dangerous_commands(self):
        """测试危险命令"""
        dangerous_commands = [
            "rm -rf /",
            "sudo rm -rf /",
            "chmod 777 /",
            "passwd",
            "useradd hacker",
            "systemctl stop network",
            "kill -9 1",
            "dd if=/dev/zero of=/dev/sda",
            "mkfs.ext4 /dev/sda1"
        ]
        
        for command in dangerous_commands:
            assert not CommandSecurityValidator.validate_command(command), f"Command '{command}' should be rejected"
    
    def test_command_injection_attempts(self):
        """测试命令注入尝试"""
        injection_commands = [
            "ls; rm -rf /",
            "cat file.txt && rm -rf /",
            "ls | rm -rf /",
            "ls `rm -rf /`",
            "ls $(rm -rf /)",
            "ls || rm -rf /",
            "ls > /dev/null; rm -rf /"
        ]
        
        for command in injection_commands:
            assert not CommandSecurityValidator.validate_command(command), f"Injection command '{command}' should be rejected"
    
    def test_path_traversal(self):
        """测试路径遍历"""
        traversal_commands = [
            "cat /etc/passwd",
            "ls /root",
            "cat ../../../etc/passwd",
            "find / -name secret"
        ]
        
        for command in traversal_commands:
            assert not CommandSecurityValidator.validate_command(command), f"Traversal command '{command}' should be rejected"
    
    def test_sanitize_command(self):
        """测试命令清理"""
        dirty_commands = [
            ("ls; rm -rf /", "ls rm -rf /"),
            ("cat file.txt && echo hello", "cat file.txt  echo hello"),
            ("ls | grep pattern", "ls  grep pattern")
        ]
        
        for dirty, expected in dirty_commands:
            sanitized = CommandSecurityValidator.sanitize_command(dirty)
            assert sanitized == expected, f"Sanitized command should be '{expected}', got '{sanitized}'"


class TestInputValidator:
    """测试输入验证器"""
    
    def test_valid_inputs(self):
        """测试有效输入"""
        valid_inputs = [
            ("normal_text", "This is normal text"),
            ("number", 123),
            ("list", [1, 2, 3]),
            ("dict", {"key": "value"})
        ]
        
        for key, value in valid_inputs:
            assert InputValidator.validate_input(key, value), f"Input '{key}' with value '{value}' should be valid"
    
    def test_xss_attempts(self):
        """测试XSS攻击尝试"""
        xss_inputs = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "data:text/html,<script>alert('xss')</script>",
            "vbscript:msgbox('xss')",
            "<img onload=alert('xss')>",
            "<div onerror=alert('xss')>"
        ]
        
        for xss_input in xss_inputs:
            assert not InputValidator.validate_input("test", xss_input), f"XSS input '{xss_input}' should be rejected"
    
    def test_sql_injection_attempts(self):
        """测试SQL注入尝试"""
        sql_inputs = [
            "'; DROP TABLE users; --",
            "1' UNION SELECT * FROM users --",
            "admin' OR '1'='1",
            "'; DELETE FROM users; --",
            "1; INSERT INTO users VALUES ('hacker', 'password');"
        ]
        
        for sql_input in sql_inputs:
            assert not InputValidator.validate_input("test", sql_input), f"SQL injection '{sql_input}' should be rejected"
    
    def test_dangerous_functions(self):
        """测试危险函数调用"""
        dangerous_inputs = [
            "eval('os.system(\"rm -rf /\")')",
            "exec('import os; os.system(\"rm -rf /\")')",
            "__import__('os').system('rm -rf /')",
            "subprocess.call(['rm', '-rf', '/'])",
            "os.system('rm -rf /')"
        ]
        
        for dangerous_input in dangerous_inputs:
            assert not InputValidator.validate_input("test", dangerous_input), f"Dangerous function '{dangerous_input}' should be rejected"
    
    def test_input_length_limit(self):
        """测试输入长度限制"""
        long_input = "x" * 20000  # 超过最大长度限制
        assert not InputValidator.validate_input("test", long_input), "Long input should be rejected"
    
    def test_sanitize_input(self):
        """测试输入清理"""
        dirty_input = "hello\x00world\x1f"
        sanitized = InputValidator.sanitize_input(dirty_input)
        assert sanitized == "helloworld", f"Sanitized input should be 'helloworld', got '{sanitized}'"


class TestSensitiveInfoFilter:
    """测试敏感信息过滤器"""
    
    def test_api_key_filtering(self):
        """测试API密钥过滤"""
        test_cases = [
            ("api_key=sk-1234567890abcdef", "api_key=\"***REDACTED***\""),
            ("apikey: abcdef123456", "apikey=\"***REDACTED***\""),
            ("API_KEY = 'secret_key_here'", "API_KEY=\"***REDACTED***\"")
        ]
        
        for input_text, expected in test_cases:
            filtered = SensitiveInfoFilter.filter_sensitive_info(input_text)
            assert "***REDACTED***" in filtered, f"API key should be redacted in: {input_text}"
    
    def test_password_filtering(self):
        """测试密码过滤"""
        test_cases = [
            ("password=mypassword123", "password=\"***REDACTED***\""),
            ("pwd: secretpass", "pwd=\"***REDACTED***\""),
            ("PASSWORD = 'admin123'", "PASSWORD=\"***REDACTED***\"")
        ]
        
        for input_text, expected in test_cases:
            filtered = SensitiveInfoFilter.filter_sensitive_info(input_text)
            assert "***REDACTED***" in filtered, f"Password should be redacted in: {input_text}"
    
    def test_token_filtering(self):
        """测试Token过滤"""
        test_cases = [
            ("token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9", "token=\"***REDACTED***\""),
            ("access_token: bearer_token_here", "access_token=\"***REDACTED***\""),
            ("TOKEN = 'jwt_token_string'", "TOKEN=\"***REDACTED***\"")
        ]
        
        for input_text, expected in test_cases:
            filtered = SensitiveInfoFilter.filter_sensitive_info(input_text)
            assert "***REDACTED***" in filtered, f"Token should be redacted in: {input_text}"
    
    def test_database_url_filtering(self):
        """测试数据库URL过滤"""
        test_cases = [
            ("mongodb://user:password@localhost:27017/db", "mongodb://***:***@localhost:27017/db"),
            ("mysql://root:secret@localhost:3306/test", "mysql://***:***@localhost:3306/test"),
            ("postgresql://admin:pass123@localhost:5432/mydb", "postgresql://***:***@localhost:5432/mydb")
        ]
        
        for input_text, expected in test_cases:
            filtered = SensitiveInfoFilter.filter_sensitive_info(input_text)
            assert "***:***@" in filtered, f"Database credentials should be redacted in: {input_text}"
    
    def test_email_filtering(self):
        """测试邮箱过滤"""
        test_cases = [
            ("user@example.com", "***@***.***"),
            ("admin@company.org", "***@***.***"),
            ("test.email@domain.co.uk", "***@***.***")
        ]
        
        for input_text, expected in test_cases:
            filtered = SensitiveInfoFilter.filter_sensitive_info(input_text)
            assert "***@***.***" in filtered, f"Email should be redacted in: {input_text}"
    
    def test_phone_number_filtering(self):
        """测试手机号过滤"""
        test_cases = [
            ("13812345678", "***"),
            ("+86 139 8765 4321", "***"),
            ("手机号: 15012345678", "手机号: ***")
        ]
        
        for input_text, expected in test_cases:
            filtered = SensitiveInfoFilter.filter_sensitive_info(input_text)
            assert "***" in filtered, f"Phone number should be redacted in: {input_text}"
    
    def test_mixed_sensitive_info(self):
        """测试混合敏感信息过滤"""
        mixed_input = """
        User login attempt:
        email: user@example.com
        password: secret123
        api_key: sk-1234567890
        phone: 13812345678
        """
        
        filtered = SensitiveInfoFilter.filter_sensitive_info(mixed_input)
        
        # 检查所有敏感信息都被过滤
        assert "***@***.***" in filtered
        assert "password=\"***REDACTED***\"" in filtered
        assert "api_key=\"***REDACTED***\"" in filtered
        assert "13812345678" not in filtered


if __name__ == "__main__":
    pytest.main([__file__])
