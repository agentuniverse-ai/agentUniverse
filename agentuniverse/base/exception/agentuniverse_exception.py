# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/1/27 10:00
# @Author  : Auto
# @Email   : auto@example.com
# @FileName: agentuniverse_exception.py

"""
AgentUniverse 基础异常类

提供统一的异常处理基类，包含错误代码、严重程度、解决建议等标准化信息。
"""

from enum import Enum
from typing import Optional, Dict, Any, List
import traceback


class ErrorSeverity(Enum):
    """错误严重程度枚举"""
    LOW = "low"           # 低严重程度，不影响核心功能
    MEDIUM = "medium"     # 中等严重程度，部分功能受影响
    HIGH = "high"         # 高严重程度，核心功能受影响
    CRITICAL = "critical" # 严重程度，系统无法正常运行


class ErrorCategory(Enum):
    """错误分类枚举"""
    CONFIGURATION = "configuration"  # 配置相关错误
    SERVICE = "service"             # 服务相关错误
    TOOL = "tool"                   # 工具相关错误
    LLM = "llm"                     # LLM相关错误
    WORKFLOW = "workflow"           # 工作流相关错误
    DATABASE = "database"           # 数据库相关错误
    NETWORK = "network"             # 网络相关错误
    AUTHENTICATION = "authentication" # 认证相关错误
    VALIDATION = "validation"       # 验证相关错误
    SYSTEM = "system"               # 系统相关错误


class AgentUniverseErrorCode(Enum):
    """AgentUniverse 错误代码枚举"""
    
    # 配置相关错误 (1000-1999)
    CONFIG_FILE_NOT_FOUND = "AU_CONFIG_1001"
    CONFIG_PARSE_ERROR = "AU_CONFIG_1002"
    CONFIG_FORMAT_UNSUPPORTED = "AU_CONFIG_1003"
    CONFIG_VALIDATION_ERROR = "AU_CONFIG_1004"
    CONFIG_MISSING_REQUIRED_FIELD = "AU_CONFIG_1005"
    
    # 服务相关错误 (2000-2999)
    SERVICE_NOT_FOUND = "AU_SERVICE_2001"
    SERVICE_INITIALIZATION_ERROR = "AU_SERVICE_2002"
    SERVICE_EXECUTION_ERROR = "AU_SERVICE_2003"
    SERVICE_TIMEOUT = "AU_SERVICE_2004"
    
    # 工具相关错误 (3000-3999)
    TOOL_NOT_FOUND = "AU_TOOL_3001"
    TOOL_EXECUTION_ERROR = "AU_TOOL_3002"
    TOOL_PARAMETER_ERROR = "AU_TOOL_3003"
    TOOL_TIMEOUT = "AU_TOOL_3004"
    TOOL_AUTHENTICATION_ERROR = "AU_TOOL_3005"
    
    # LLM相关错误 (4000-4999)
    LLM_CONNECTION_ERROR = "AU_LLM_4001"
    LLM_AUTHENTICATION_ERROR = "AU_LLM_4002"
    LLM_RATE_LIMIT_ERROR = "AU_LLM_4003"
    LLM_MODEL_NOT_FOUND = "AU_LLM_4004"
    LLM_EXECUTION_ERROR = "AU_LLM_4005"
    LLM_TOKEN_LIMIT_EXCEEDED = "AU_LLM_4006"
    
    # 工作流相关错误 (5000-5999)
    WORKFLOW_NODE_NOT_FOUND = "AU_WORKFLOW_5001"
    WORKFLOW_EXECUTION_ERROR = "AU_WORKFLOW_5002"
    WORKFLOW_VALIDATION_ERROR = "AU_WORKFLOW_5003"
    WORKFLOW_GRAPH_ERROR = "AU_WORKFLOW_5004"
    
    # 数据库相关错误 (6000-6999)
    DATABASE_CONNECTION_ERROR = "AU_DATABASE_6001"
    DATABASE_QUERY_ERROR = "AU_DATABASE_6002"
    DATABASE_AUTHENTICATION_ERROR = "AU_DATABASE_6003"
    
    # 网络相关错误 (7000-7999)
    NETWORK_CONNECTION_ERROR = "AU_NETWORK_7001"
    NETWORK_TIMEOUT = "AU_NETWORK_7002"
    NETWORK_SSL_ERROR = "AU_NETWORK_7003"
    
    # 系统相关错误 (8000-8999)
    SYSTEM_RESOURCE_ERROR = "AU_SYSTEM_8001"
    SYSTEM_PERMISSION_ERROR = "AU_SYSTEM_8002"
    SYSTEM_DEPENDENCY_ERROR = "AU_SYSTEM_8003"


class AgentUniverseException(Exception):
    """
    AgentUniverse 基础异常类
    
    提供统一的异常处理机制，包含：
    - 错误代码
    - 错误严重程度
    - 错误分类
    - 详细描述
    - 解决建议
    - 错误上下文信息
    """
    
    def __init__(
        self,
        error_code: AgentUniverseErrorCode,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        category: ErrorCategory = ErrorCategory.SYSTEM,
        details: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[str]] = None,
        original_exception: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        初始化异常
        
        Args:
            error_code: 错误代码
            message: 错误消息
            severity: 错误严重程度
            category: 错误分类
            details: 详细信息
            suggestions: 解决建议
            original_exception: 原始异常
            context: 错误上下文
        """
        self.error_code = error_code
        self.message = message
        self.severity = severity
        self.category = category
        self.details = details or {}
        self.suggestions = suggestions or []
        self.original_exception = original_exception
        self.context = context or {}
        
        # 生成完整的错误消息
        full_message = self._generate_full_message()
        super().__init__(full_message)
    
    def _generate_full_message(self) -> str:
        """生成完整的错误消息"""
        lines = [
            f"[{self.error_code.value}] {self.message}",
            f"严重程度: {self.severity.value}",
            f"错误分类: {self.category.value}"
        ]
        
        if self.details:
            lines.append("详细信息:")
            for key, value in self.details.items():
                lines.append(f"  - {key}: {value}")
        
        if self.suggestions:
            lines.append("解决建议:")
            for i, suggestion in enumerate(self.suggestions, 1):
                lines.append(f"  {i}. {suggestion}")
        
        if self.context:
            lines.append("错误上下文:")
            for key, value in self.context.items():
                lines.append(f"  - {key}: {value}")
        
        if self.original_exception:
            lines.append(f"原始异常: {type(self.original_exception).__name__}: {str(self.original_exception)}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """将异常转换为字典格式"""
        return {
            "error_code": self.error_code.value,
            "message": self.message,
            "severity": self.severity.value,
            "category": self.category.value,
            "details": self.details,
            "suggestions": self.suggestions,
            "context": self.context,
            "original_exception": str(self.original_exception) if self.original_exception else None,
            "traceback": traceback.format_exc() if self.original_exception else None
        }
    
    def get_user_friendly_message(self, language: str = "zh") -> str:
        """获取用户友好的错误消息"""
        if language == "zh":
            return self._get_chinese_message()
        else:
            return self._get_english_message()
    
    def _get_chinese_message(self) -> str:
        """获取中文错误消息"""
        lines = [f"❌ {self.message}"]
        
        if self.suggestions:
            lines.append("\n💡 解决建议:")
            for i, suggestion in enumerate(self.suggestions, 1):
                lines.append(f"   {i}. {suggestion}")
        
        return "\n".join(lines)
    
    def _get_english_message(self) -> str:
        """获取英文错误消息"""
        lines = [f"❌ {self.message}"]
        
        if self.suggestions:
            lines.append("\n💡 Suggestions:")
            for i, suggestion in enumerate(self.suggestions, 1):
                lines.append(f"   {i}. {suggestion}")
        
        return "\n".join(lines)
    
    def __str__(self) -> str:
        """字符串表示"""
        return self._generate_full_message()
    
    def __repr__(self) -> str:
        """详细表示"""
        return (f"AgentUniverseException(error_code={self.error_code.value}, "
                f"message='{self.message}', severity={self.severity.value}, "
                f"category={self.category.value})")