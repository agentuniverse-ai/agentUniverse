"""
工具相关异常类

处理工具执行、参数验证、超时等过程中的错误。
"""

from typing import Optional, List, Dict, Any
from .agentuniverse_exception import (
    AgentUniverseException,
    AgentUniverseErrorCode,
    ErrorSeverity,
    ErrorCategory
)


class ToolNotFoundError(AgentUniverseException):
    """工具未找到异常"""
    
    def __init__(
        self,
        tool_id: str,
        available_tools: Optional[List[str]] = None,
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        suggestions = [
            f"检查工具ID '{tool_id}' 是否正确",
            "确认工具是否已注册",
            "查看工具配置文件是否正确加载"
        ]
        
        if available_tools:
            suggestions.extend([
                f"可用的工具列表: {', '.join(available_tools)}",
                "检查工具名称拼写是否正确"
            ])
        
        suggestions.extend([
            "参考工具注册文档",
            "检查工具配置文件路径"
        ])
        
        super().__init__(
            error_code=AgentUniverseErrorCode.TOOL_NOT_FOUND,
            message=f"工具未找到: {tool_id}",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.TOOL,
            details=details or {
                "tool_id": tool_id,
                "available_tools": available_tools or []
            },
            suggestions=suggestions,
            original_exception=original_exception
        )


class ToolExecutionError(AgentUniverseException):
    """工具执行错误异常"""
    
    def __init__(
        self,
        tool_id: str,
        execution_error: str,
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        suggestions = [
            f"检查工具 '{tool_id}' 的执行参数是否正确",
            "验证工具依赖是否满足",
            "检查工具所需的资源是否可用",
            "查看工具执行日志获取更多信息",
            "参考工具使用文档"
        ]
        
        super().__init__(
            error_code=AgentUniverseErrorCode.TOOL_EXECUTION_ERROR,
            message=f"工具执行失败: {tool_id}",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.TOOL,
            details=details or {
                "tool_id": tool_id,
                "execution_error": execution_error
            },
            suggestions=suggestions,
            original_exception=original_exception
        )


class ToolParameterError(AgentUniverseException):
    """工具参数错误异常"""
    
    def __init__(
        self,
        tool_id: str,
        parameter_errors: List[str],
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        suggestions = [
            f"检查工具 '{tool_id}' 的参数配置:",
            *[f"  - {error}" for error in parameter_errors],
            "参考工具参数文档",
            "使用工具参数验证功能"
        ]
        
        super().__init__(
            error_code=AgentUniverseErrorCode.TOOL_PARAMETER_ERROR,
            message=f"工具参数错误: {tool_id}",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.TOOL,
            details=details or {
                "tool_id": tool_id,
                "parameter_errors": parameter_errors
            },
            suggestions=suggestions,
            original_exception=original_exception
        )


class ToolTimeoutError(AgentUniverseException):
    """工具执行超时异常"""
    
    def __init__(
        self,
        tool_id: str,
        timeout_seconds: int,
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        suggestions = [
            f"工具 '{tool_id}' 执行超时 ({timeout_seconds}秒)",
            "检查网络连接是否稳定",
            "尝试增加超时时间设置",
            "检查工具执行环境是否正常",
            "考虑使用异步执行方式"
        ]
        
        super().__init__(
            error_code=AgentUniverseErrorCode.TOOL_TIMEOUT,
            message=f"工具执行超时: {tool_id}",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.TOOL,
            details=details or {
                "tool_id": tool_id,
                "timeout_seconds": timeout_seconds
            },
            suggestions=suggestions,
            original_exception=original_exception
        )
