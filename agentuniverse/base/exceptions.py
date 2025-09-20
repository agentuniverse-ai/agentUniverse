# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/19 10:00
# @Author  : AI Assistant
# @Email   : assistant@example.com
# @FileName: exceptions.py

"""
AgentUniverse 标准异常类
"""

from typing import Optional, Dict, Any


class AgentUniverseException(Exception):
    """AgentUniverse 基础异常类"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, 
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "UNKNOWN_ERROR"
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details
        }


class ConfigurationError(AgentUniverseException):
    """配置错误"""
    
    def __init__(self, message: str, config_key: Optional[str] = None, 
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "CONFIG_ERROR", details)
        self.config_key = config_key


class ValidationError(AgentUniverseException):
    """验证错误"""
    
    def __init__(self, message: str, field_name: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "VALIDATION_ERROR", details)
        self.field_name = field_name


class ExecutionError(AgentUniverseException):
    """执行错误"""
    
    def __init__(self, message: str, component_name: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "EXECUTION_ERROR", details)
        self.component_name = component_name


class SecurityError(AgentUniverseException):
    """安全错误"""
    
    def __init__(self, message: str, security_violation: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "SECURITY_ERROR", details)
        self.security_violation = security_violation


class ResourceError(AgentUniverseException):
    """资源错误"""
    
    def __init__(self, message: str, resource_type: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "RESOURCE_ERROR", details)
        self.resource_type = resource_type


class TimeoutError(AgentUniverseException):
    """超时错误"""
    
    def __init__(self, message: str, timeout_duration: Optional[float] = None,
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "TIMEOUT_ERROR", details)
        self.timeout_duration = timeout_duration


class NetworkError(AgentUniverseException):
    """网络错误"""
    
    def __init__(self, message: str, url: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "NETWORK_ERROR", details)
        self.url = url


class AuthenticationError(AgentUniverseException):
    """认证错误"""
    
    def __init__(self, message: str, auth_type: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "AUTH_ERROR", details)
        self.auth_type = auth_type


class AuthorizationError(AgentUniverseException):
    """授权错误"""
    
    def __init__(self, message: str, required_permission: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "AUTHZ_ERROR", details)
        self.required_permission = required_permission


class RateLimitError(AgentUniverseException):
    """速率限制错误"""
    
    def __init__(self, message: str, retry_after: Optional[int] = None,
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "RATE_LIMIT_ERROR", details)
        self.retry_after = retry_after


class ServiceUnavailableError(AgentUniverseException):
    """服务不可用错误"""
    
    def __init__(self, message: str, service_name: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "SERVICE_UNAVAILABLE", details)
        self.service_name = service_name


class DataError(AgentUniverseException):
    """数据错误"""
    
    def __init__(self, message: str, data_type: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "DATA_ERROR", details)
        self.data_type = data_type


class BusinessLogicError(AgentUniverseException):
    """业务逻辑错误"""
    
    def __init__(self, message: str, business_rule: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "BUSINESS_ERROR", details)
        self.business_rule = business_rule
