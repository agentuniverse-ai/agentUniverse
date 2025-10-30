# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/1/27 10:00
# @Author  : Auto
# @Email   : auto@example.com
# @FileName: service_exceptions.py

"""
服务相关异常类

处理服务管理、初始化、执行等过程中的错误。
"""

from typing import Optional, List, Dict, Any
from .agentuniverse_exception import (
    AgentUniverseException,
    AgentUniverseErrorCode,
    ErrorSeverity,
    ErrorCategory
)


class ServiceNotFoundError(AgentUniverseException):
    """服务未找到异常"""
    
    def __init__(
        self,
        service_code: str,
        available_services: Optional[List[str]] = None,
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        suggestions = [
            f"检查服务代码 '{service_code}' 是否正确",
            "确认服务是否已注册",
            "查看服务配置文件是否正确加载"
        ]
        
        if available_services:
            suggestions.extend([
                f"可用的服务列表: {', '.join(available_services)}",
                "检查服务名称拼写是否正确"
            ])
        
        suggestions.extend([
            "参考服务注册文档",
            "检查服务配置文件路径"
        ])
        
        super().__init__(
            error_code=AgentUniverseErrorCode.SERVICE_NOT_FOUND,
            message=f"服务未找到: {service_code}",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.SERVICE,
            details=details or {
                "service_code": service_code,
                "available_services": available_services or []
            },
            suggestions=suggestions,
            original_exception=original_exception
        )


class ServiceInitializationError(AgentUniverseException):
    """服务初始化错误异常"""
    
    def __init__(
        self,
        service_code: str,
        init_error: str,
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        suggestions = [
            f"检查服务 '{service_code}' 的配置是否正确",
            "验证服务依赖是否满足",
            "检查服务所需的资源是否可用",
            "查看服务初始化日志获取更多信息",
            "参考服务配置文档"
        ]
        
        super().__init__(
            error_code=AgentUniverseErrorCode.SERVICE_INITIALIZATION_ERROR,
            message=f"服务初始化失败: {service_code}",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.SERVICE,
            details=details or {
                "service_code": service_code,
                "init_error": init_error
            },
            suggestions=suggestions,
            original_exception=original_exception
        )


class ServiceExecutionError(AgentUniverseException):
    """服务执行错误异常"""
    
    def __init__(
        self,
        service_code: str,
        execution_error: str,
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        suggestions = [
            f"检查服务 '{service_code}' 的执行参数是否正确",
            "验证服务状态是否正常",
            "检查服务资源使用情况",
            "查看服务执行日志",
            "尝试重启服务"
        ]
        
        super().__init__(
            error_code=AgentUniverseErrorCode.SERVICE_EXECUTION_ERROR,
            message=f"服务执行失败: {service_code}",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.SERVICE,
            details=details or {
                "service_code": service_code,
                "execution_error": execution_error
            },
            suggestions=suggestions,
            original_exception=original_exception
        )
