# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/1/15 10:00
# @Author  : Auto
# @Email   : auto@example.com
# @FileName: agentuniverse_exception.py

from enum import Enum
from typing import Optional, Dict, Any, List


class ErrorSeverity(Enum):
    """错误严重程度枚举"""
    LOW = "low"           # 低严重程度，不影响核心功能
    MEDIUM = "medium"     # 中等严重程度，影响部分功能
    HIGH = "high"         # 高严重程度，影响核心功能
    CRITICAL = "critical" # 严重程度，系统无法继续运行


class ErrorCode(Enum):
    """通用错误代码枚举"""
    UNKNOWN_ERROR = "AU0001"
    INVALID_PARAMETER = "AU0002"
    RESOURCE_NOT_FOUND = "AU0003"
    PERMISSION_DENIED = "AU0004"
    NETWORK_ERROR = "AU0005"
    TIMEOUT_ERROR = "AU0006"
    CONFIGURATION_ERROR = "AU0007"
    VALIDATION_ERROR = "AU0008"
    OPERATION_FAILED = "AU0009"
    DEPENDENCY_ERROR = "AU0010"


class AgentUniverseException(Exception):
    """AgentUniverse统一异常基类
    
    提供标准化的错误信息格式，包含错误代码、严重程度、解决建议等
    """
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.UNKNOWN_ERROR,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        details: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        初始化异常
        
        Args:
            message: 错误消息
            error_code: 错误代码
            severity: 错误严重程度
            details: 错误详细信息
            suggestions: 解决建议列表
            context: 错误上下文信息
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.severity = severity
        self.details = details or {}
        self.suggestions = suggestions or []
        self.context = context or {}
    
    def __str__(self) -> str:
        """返回格式化的错误信息"""
        error_info = f"[{self.error_code.value}] {self.message}"
        
        if self.details:
            error_info += f"\n详细信息: {self.details}"
        
        if self.suggestions:
            error_info += f"\n解决建议:"
            for i, suggestion in enumerate(self.suggestions, 1):
                error_info += f"\n  {i}. {suggestion}"
        
        if self.context:
            error_info += f"\n上下文信息: {self.context}"
        
        return error_info
    
    def to_dict(self) -> Dict[str, Any]:
        """将异常信息转换为字典格式"""
        return {
            "error_code": self.error_code.value,
            "message": self.message,
            "severity": self.severity.value,
            "details": self.details,
            "suggestions": self.suggestions,
            "context": self.context
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentUniverseException':
        """从字典创建异常实例"""
        return cls(
            message=data["message"],
            error_code=ErrorCode(data["error_code"]),
            severity=ErrorSeverity(data["severity"]),
            details=data.get("details"),
            suggestions=data.get("suggestions"),
            context=data.get("context")
        )
