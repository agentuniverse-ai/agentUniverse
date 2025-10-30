"""
LLM相关异常类

处理LLM连接、认证、执行等过程中的错误。
"""

from typing import Optional, List, Dict, Any
from .agentuniverse_exception import (
    AgentUniverseException,
    AgentUniverseErrorCode,
    ErrorSeverity,
    ErrorCategory
)


class LLMConnectionError(AgentUniverseException):
    """LLM连接错误异常"""
    
    def __init__(
        self,
        model_name: str,
        connection_error: str,
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        suggestions = [
            f"检查模型 '{model_name}' 的连接配置",
            "验证网络连接是否正常",
            "检查API端点是否正确",
            "确认防火墙设置是否允许连接",
            "尝试使用代理或VPN"
        ]
        
        super().__init__(
            error_code=AgentUniverseErrorCode.LLM_CONNECTION_ERROR,
            message=f"LLM连接失败: {model_name}",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.LLM,
            details=details or {
                "model_name": model_name,
                "connection_error": connection_error
            },
            suggestions=suggestions,
            original_exception=original_exception
        )


class LLMAuthenticationError(AgentUniverseException):
    """LLM认证错误异常"""
    
    def __init__(
        self,
        model_name: str,
        auth_error: str,
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        suggestions = [
            f"检查模型 '{model_name}' 的API密钥是否正确",
            "验证API密钥是否有效且未过期",
            "检查API密钥权限是否足够",
            "确认API密钥格式是否正确",
            "查看API提供商的使用限制"
        ]
        
        super().__init__(
            error_code=AgentUniverseErrorCode.LLM_AUTHENTICATION_ERROR,
            message=f"LLM认证失败: {model_name}",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.AUTHENTICATION,
            details=details or {
                "model_name": model_name,
                "auth_error": auth_error
            },
            suggestions=suggestions,
            original_exception=original_exception
        )


class LLMRateLimitError(AgentUniverseException):
    """LLM速率限制错误异常"""
    
    def __init__(
        self,
        model_name: str,
        rate_limit_info: str,
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        suggestions = [
            f"模型 '{model_name}' 达到速率限制",
            "等待一段时间后重试",
            "检查API使用配额",
            "考虑升级API套餐",
            "优化请求频率和批次大小"
        ]
        
        super().__init__(
            error_code=AgentUniverseErrorCode.LLM_RATE_LIMIT_ERROR,
            message=f"LLM速率限制: {model_name}",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.LLM,
            details=details or {
                "model_name": model_name,
                "rate_limit_info": rate_limit_info
            },
            suggestions=suggestions,
            original_exception=original_exception
        )


class LLMModelNotFoundError(AgentUniverseException):
    """LLM模型未找到异常"""
    
    def __init__(
        self,
        model_name: str,
        available_models: Optional[List[str]] = None,
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        suggestions = [
            f"检查模型名称 '{model_name}' 是否正确",
            "确认模型是否可用",
            "检查模型配置是否正确"
        ]
        
        if available_models:
            suggestions.extend([
                f"可用的模型列表: {', '.join(available_models)}",
                "检查模型名称拼写是否正确"
            ])
        
        suggestions.extend([
            "参考模型配置文档",
            "检查模型提供商的状态"
        ])
        
        super().__init__(
            error_code=AgentUniverseErrorCode.LLM_MODEL_NOT_FOUND,
            message=f"LLM模型未找到: {model_name}",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.LLM,
            details=details or {
                "model_name": model_name,
                "available_models": available_models or []
            },
            suggestions=suggestions,
            original_exception=original_exception
        )


class LLMExecutionError(AgentUniverseException):
    """LLM执行错误异常"""
    
    def __init__(
        self,
        model_name: str,
        execution_error: str,
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        suggestions = [
            f"检查模型 '{model_name}' 的执行参数",
            "验证输入内容是否符合模型要求",
            "检查模型状态是否正常",
            "查看模型执行日志",
            "尝试使用不同的模型参数"
        ]
        
        super().__init__(
            error_code=AgentUniverseErrorCode.LLM_EXECUTION_ERROR,
            message=f"LLM执行失败: {model_name}",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.LLM,
            details=details or {
                "model_name": model_name,
                "execution_error": execution_error
            },
            suggestions=suggestions,
            original_exception=original_exception
        )
