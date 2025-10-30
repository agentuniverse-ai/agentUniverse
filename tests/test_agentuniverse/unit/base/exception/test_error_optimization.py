# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/1/27 10:30
# @Author  : Auto
# @Email   : auto@example.com
# @FileName: test_error_optimization.py

"""
错误信息优化测试用例

测试新的错误处理机制是否能够提供更直观和有用的错误信息。
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch

from agentuniverse.base.exception import (
    AgentUniverseException,
    AgentUniverseErrorCode,
    ErrorSeverity,
    ErrorCategory,
    ConfigFileNotFoundError,
    ConfigParseError,
    UnsupportedConfigFormatError,
    ConfigValidationError,
    ServiceNotFoundError,
    ServiceInitializationError,
    ServiceExecutionError,
    ToolNotFoundError,
    ToolExecutionError,
    ToolParameterError,
    ToolTimeoutError,
    LLMConnectionError,
    LLMAuthenticationError,
    LLMRateLimitError,
    LLMModelNotFoundError,
    LLMExecutionError,
    WorkflowNodeNotFoundError,
    WorkflowExecutionError,
    WorkflowValidationError,
    WorkflowGraphError
)


class TestAgentUniverseException:
    """测试基础异常类"""
    
    def test_basic_exception_creation(self):
        """测试基础异常创建"""
        exc = AgentUniverseException(
            error_code=AgentUniverseErrorCode.CONFIG_FILE_NOT_FOUND,
            message="测试错误消息",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.CONFIGURATION,
            details={"file_path": "/test/path"},
            suggestions=["检查文件路径", "确认文件存在"]
        )
        
        assert exc.error_code == AgentUniverseErrorCode.CONFIG_FILE_NOT_FOUND
        assert exc.message == "测试错误消息"
        assert exc.severity == ErrorSeverity.HIGH
        assert exc.category == ErrorCategory.CONFIGURATION
        assert exc.details == {"file_path": "/test/path"}
        assert exc.suggestions == ["检查文件路径", "确认文件存在"]
    
    def test_exception_to_dict(self):
        """测试异常转换为字典"""
        exc = AgentUniverseException(
            error_code=AgentUniverseErrorCode.CONFIG_FILE_NOT_FOUND,
            message="测试错误消息",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.CONFIGURATION
        )
        
        result = exc.to_dict()
        assert result["error_code"] == "AU_CONFIG_1001"
        assert result["message"] == "测试错误消息"
        assert result["severity"] == "high"
        assert result["category"] == "configuration"
    
    def test_user_friendly_message_zh(self):
        """测试中文用户友好消息"""
        exc = AgentUniverseException(
            error_code=AgentUniverseErrorCode.CONFIG_FILE_NOT_FOUND,
            message="配置文件未找到",
            suggestions=["检查文件路径", "确认文件存在"]
        )
        
        message = exc.get_user_friendly_message("zh")
        assert "❌ 配置文件未找到" in message
        assert "💡 解决建议:" in message
        assert "1. 检查文件路径" in message
        assert "2. 确认文件存在" in message


class TestConfigExceptions:
    """测试配置相关异常"""
    
    def test_config_file_not_found_error(self):
        """测试配置文件未找到异常"""
        exc = ConfigFileNotFoundError(
            file_path="/test/config.yaml",
            details={"absolute_path": "/absolute/test/config.yaml"}
        )
        
        assert exc.error_code == AgentUniverseErrorCode.CONFIG_FILE_NOT_FOUND
        assert "配置文件未找到: /test/config.yaml" in str(exc)
        assert "检查文件路径是否正确" in exc.suggestions
    
    def test_config_parse_error(self):
        """测试配置解析错误异常"""
        exc = ConfigParseError(
            file_path="/test/config.yaml",
            parse_error="YAML格式错误: line 5, column 10",
            details={"file_type": "YAML", "error_line": 5}
        )
        
        assert exc.error_code == AgentUniverseErrorCode.CONFIG_PARSE_ERROR
        assert "配置文件解析失败: /test/config.yaml" in str(exc)
        assert "检查配置文件格式是否正确" in exc.suggestions
    
    def test_unsupported_config_format_error(self):
        """测试不支持的配置格式异常"""
        exc = UnsupportedConfigFormatError(
            file_path="/test/config.json",
            file_format="json",
            details={"supported_formats": ["yaml", "toml"]}
        )
        
        assert exc.error_code == AgentUniverseErrorCode.CONFIG_FORMAT_UNSUPPORTED
        assert "不支持的配置文件格式: json" in str(exc)
        assert "支持的格式: yaml, toml" in exc.suggestions


class TestServiceExceptions:
    """测试服务相关异常"""
    
    def test_service_not_found_error(self):
        """测试服务未找到异常"""
        exc = ServiceNotFoundError(
            service_code="test_service",
            available_services=["service1", "service2"],
            details={"service_manager_type": "ServiceManager"}
        )
        
        assert exc.error_code == AgentUniverseErrorCode.SERVICE_NOT_FOUND
        assert "服务未找到: test_service" in str(exc)
        assert "可用的服务列表: service1, service2" in exc.suggestions
    
    def test_service_initialization_error(self):
        """测试服务初始化错误异常"""
        exc = ServiceInitializationError(
            service_code="test_service",
            init_error="依赖服务未启动",
            details={"dependency": "database"}
        )
        
        assert exc.error_code == AgentUniverseErrorCode.SERVICE_INITIALIZATION_ERROR
        assert "服务初始化失败: test_service" in str(exc)
        assert "检查服务依赖是否满足" in exc.suggestions


class TestToolExceptions:
    """测试工具相关异常"""
    
    def test_tool_not_found_error(self):
        """测试工具未找到异常"""
        exc = ToolNotFoundError(
            tool_id="test_tool",
            available_tools=["tool1", "tool2"],
            details={"tool_manager_type": "ToolManager"}
        )
        
        assert exc.error_code == AgentUniverseErrorCode.TOOL_NOT_FOUND
        assert "工具未找到: test_tool" in str(exc)
        assert "可用的工具列表: tool1, tool2" in exc.suggestions
    
    def test_tool_parameter_error(self):
        """测试工具参数错误异常"""
        exc = ToolParameterError(
            tool_id="test_tool",
            parameter_errors=["缺少必需参数: input", "参数类型错误: output"],
            details={"missing_keys": ["input"], "provided_keys": ["output"]}
        )
        
        assert exc.error_code == AgentUniverseErrorCode.TOOL_PARAMETER_ERROR
        assert "工具参数错误: test_tool" in str(exc)
        assert "缺少必需参数: input" in exc.suggestions


class TestLLMExceptions:
    """测试LLM相关异常"""
    
    def test_llm_connection_error(self):
        """测试LLM连接错误异常"""
        exc = LLMConnectionError(
            model_name="gpt-4",
            connection_error="连接超时",
            details={"timeout": 30, "api_base": "https://api.openai.com"}
        )
        
        assert exc.error_code == AgentUniverseErrorCode.LLM_CONNECTION_ERROR
        assert "LLM连接失败: gpt-4" in str(exc)
        assert "检查模型 'gpt-4' 的连接配置" in exc.suggestions
    
    def test_llm_authentication_error(self):
        """测试LLM认证错误异常"""
        exc = LLMAuthenticationError(
            model_name="gpt-4",
            auth_error="API密钥无效",
            details={"api_key": "sk-***"}
        )
        
        assert exc.error_code == AgentUniverseErrorCode.LLM_AUTHENTICATION_ERROR
        assert "LLM认证失败: gpt-4" in str(exc)
        assert "检查模型 'gpt-4' 的API密钥是否正确" in exc.suggestions


class TestWorkflowExceptions:
    """测试工作流相关异常"""
    
    def test_workflow_node_not_found_error(self):
        """测试工作流节点未找到异常"""
        exc = WorkflowNodeNotFoundError(
            node_id="test_node",
            workflow_id="test_workflow",
            available_nodes=["node1", "node2"],
            details={"node_type": "tool"}
        )
        
        assert exc.error_code == AgentUniverseErrorCode.WORKFLOW_NODE_NOT_FOUND
        assert "工作流节点未找到: test_node" in str(exc)
        assert "检查工作流 'test_workflow' 中的节点ID 'test_node' 是否正确" in exc.suggestions
    
    def test_workflow_execution_error(self):
        """测试工作流执行错误异常"""
        exc = WorkflowExecutionError(
            workflow_id="test_workflow",
            execution_error="节点执行失败",
            details={"failed_node": "test_node"}
        )
        
        assert exc.error_code == AgentUniverseErrorCode.WORKFLOW_EXECUTION_ERROR
        assert "工作流执行失败: test_workflow" in str(exc)
        assert "检查工作流 'test_workflow' 的执行参数" in exc.suggestions


class TestErrorCodeEnum:
    """测试错误代码枚举"""
    
    def test_error_code_values(self):
        """测试错误代码值"""
        assert AgentUniverseErrorCode.CONFIG_FILE_NOT_FOUND.value == "AU_CONFIG_1001"
        assert AgentUniverseErrorCode.SERVICE_NOT_FOUND.value == "AU_SERVICE_2001"
        assert AgentUniverseErrorCode.TOOL_NOT_FOUND.value == "AU_TOOL_3001"
        assert AgentUniverseErrorCode.LLM_CONNECTION_ERROR.value == "AU_LLM_4001"
        assert AgentUniverseErrorCode.WORKFLOW_NODE_NOT_FOUND.value == "AU_WORKFLOW_5001"
    
    def test_error_code_categories(self):
        """测试错误代码分类"""
        config_codes = [code for code in AgentUniverseErrorCode if code.value.startswith("AU_CONFIG_")]
        service_codes = [code for code in AgentUniverseErrorCode if code.value.startswith("AU_SERVICE_")]
        tool_codes = [code for code in AgentUniverseErrorCode if code.value.startswith("AU_TOOL_")]
        llm_codes = [code for code in AgentUniverseErrorCode if code.value.startswith("AU_LLM_")]
        workflow_codes = [code for code in AgentUniverseErrorCode if code.value.startswith("AU_WORKFLOW_")]
        
        assert len(config_codes) > 0
        assert len(service_codes) > 0
        assert len(tool_codes) > 0
        assert len(llm_codes) > 0
        assert len(workflow_codes) > 0


class TestErrorSeverityAndCategory:
    """测试错误严重程度和分类"""
    
    def test_error_severity_values(self):
        """测试错误严重程度值"""
        assert ErrorSeverity.LOW.value == "low"
        assert ErrorSeverity.MEDIUM.value == "medium"
        assert ErrorSeverity.HIGH.value == "high"
        assert ErrorSeverity.CRITICAL.value == "critical"
    
    def test_error_category_values(self):
        """测试错误分类值"""
        assert ErrorCategory.CONFIGURATION.value == "configuration"
        assert ErrorCategory.SERVICE.value == "service"
        assert ErrorCategory.TOOL.value == "tool"
        assert ErrorCategory.LLM.value == "llm"
        assert ErrorCategory.WORKFLOW.value == "workflow"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
