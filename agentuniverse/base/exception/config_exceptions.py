# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/1/27 10:00
# @Author  : Auto
# @Email   : auto@example.com
# @FileName: config_exceptions.py

"""
配置相关异常类

处理配置文件加载、解析、验证等过程中的错误。
"""

from typing import Optional, List, Dict, Any
from .agentuniverse_exception import (
    AgentUniverseException,
    AgentUniverseErrorCode,
    ErrorSeverity,
    ErrorCategory
)


class ConfigFileNotFoundError(AgentUniverseException):
    """配置文件未找到异常"""
    
    def __init__(
        self,
        file_path: str,
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        suggestions = [
            f"检查文件路径是否正确: {file_path}",
            "确认文件是否存在",
            "检查文件权限是否足够",
            "查看项目根目录下的配置文件示例"
        ]
        
        super().__init__(
            error_code=AgentUniverseErrorCode.CONFIG_FILE_NOT_FOUND,
            message=f"配置文件未找到: {file_path}",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.CONFIGURATION,
            details=details or {"file_path": file_path},
            suggestions=suggestions,
            original_exception=original_exception
        )


class ConfigParseError(AgentUniverseException):
    """配置文件解析错误异常"""
    
    def __init__(
        self,
        file_path: str,
        parse_error: str,
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        suggestions = [
            f"检查配置文件格式是否正确: {file_path}",
            "验证YAML/TOML语法",
            "检查文件编码是否为UTF-8",
            "查看配置文件示例和文档",
            "使用在线YAML/TOML验证器检查语法"
        ]
        
        super().__init__(
            error_code=AgentUniverseErrorCode.CONFIG_PARSE_ERROR,
            message=f"配置文件解析失败: {file_path}",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.CONFIGURATION,
            details=details or {
                "file_path": file_path,
                "parse_error": parse_error
            },
            suggestions=suggestions,
            original_exception=original_exception
        )


class UnsupportedConfigFormatError(AgentUniverseException):
    """不支持的配置文件格式异常"""
    
    def __init__(
        self,
        file_path: str,
        file_format: str,
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        supported_formats = ["yaml", "yml", "toml"]
        suggestions = [
            f"当前文件格式 '{file_format}' 不支持",
            f"支持的格式: {', '.join(supported_formats)}",
            f"请将文件 {file_path} 转换为支持的格式",
            "参考项目文档中的配置文件示例"
        ]
        
        super().__init__(
            error_code=AgentUniverseErrorCode.CONFIG_FORMAT_UNSUPPORTED,
            message=f"不支持的配置文件格式: {file_format}",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.CONFIGURATION,
            details=details or {
                "file_path": file_path,
                "file_format": file_format,
                "supported_formats": supported_formats
            },
            suggestions=suggestions,
            original_exception=original_exception
        )


class ConfigValidationError(AgentUniverseException):
    """配置文件验证错误异常"""
    
    def __init__(
        self,
        file_path: str,
        validation_errors: List[str],
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        suggestions = [
            f"检查配置文件 {file_path} 中的以下问题:",
            *[f"  - {error}" for error in validation_errors],
            "参考配置文件模板和文档",
            "使用配置验证工具检查配置"
        ]
        
        super().__init__(
            error_code=AgentUniverseErrorCode.CONFIG_VALIDATION_ERROR,
            message=f"配置文件验证失败: {file_path}",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.CONFIGURATION,
            details=details or {
                "file_path": file_path,
                "validation_errors": validation_errors
            },
            suggestions=suggestions,
            original_exception=original_exception
        )
