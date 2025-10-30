# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/1/15 10:00
# @Author  : Auto
# @Email   : auto@example.com
# @FileName: config_exception.py

from enum import Enum
from typing import Optional, Dict, Any, List
from .agentuniverse_exception import AgentUniverseException, ErrorSeverity


class ConfigErrorCode(Enum):
    """配置相关错误代码"""
    FILE_NOT_FOUND = "CFG0001"
    UNSUPPORTED_FORMAT = "CFG0002"
    PARSE_ERROR = "CFG0003"
    VALIDATION_ERROR = "CFG0004"
    MISSING_REQUIRED_FIELD = "CFG0005"
    INVALID_VALUE = "CFG0006"
    ENVIRONMENT_VARIABLE_NOT_SET = "CFG0007"
    PLACEHOLDER_RESOLUTION_ERROR = "CFG0008"


class ConfigException(AgentUniverseException):
    """配置相关异常"""
    
    def __init__(
        self,
        message: str,
        error_code: ConfigErrorCode = ConfigErrorCode.PARSE_ERROR,
        severity: ErrorSeverity = ErrorSeverity.HIGH,
        config_path: Optional[str] = None,
        config_key: Optional[str] = None,
        **kwargs
    ):
        """
        初始化配置异常
        
        Args:
            message: 错误消息
            error_code: 错误代码
            severity: 错误严重程度
            config_path: 配置文件路径
            config_key: 配置键名
        """
        context = {}
        if config_path:
            context["config_path"] = config_path
        if config_key:
            context["config_key"] = config_key
        
        super().__init__(
            message=message,
            error_code=error_code,
            severity=severity,
            context=context,
            **kwargs
        )
    
    @classmethod
    def file_not_found(cls, file_path: str) -> 'ConfigException':
        """配置文件未找到异常"""
        return cls(
            message=f"配置文件未找到: {file_path}",
            error_code=ConfigErrorCode.FILE_NOT_FOUND,
            severity=ErrorSeverity.HIGH,
            config_path=file_path,
            suggestions=[
                f"检查文件路径是否正确: {file_path}",
                "确认文件是否存在",
                "检查文件权限是否足够",
                "参考文档确认配置文件位置"
            ]
        )
    
    @classmethod
    def unsupported_format(cls, file_format: str, supported_formats: List[str]) -> 'ConfigException':
        """不支持的文件格式异常"""
        return cls(
            message=f"不支持的文件格式: {file_format}",
            error_code=ConfigErrorCode.UNSUPPORTED_FORMAT,
            severity=ErrorSeverity.HIGH,
            details={"supported_formats": supported_formats},
            suggestions=[
                f"请使用支持的文件格式: {', '.join(supported_formats)}",
                f"将文件转换为支持的格式之一",
                "检查文件扩展名是否正确"
            ]
        )
    
    @classmethod
    def parse_error(cls, file_path: str, error_details: str) -> 'ConfigException':
        """配置文件解析错误异常"""
        return cls(
            message=f"配置文件解析失败: {file_path}",
            error_code=ConfigErrorCode.PARSE_ERROR,
            severity=ErrorSeverity.HIGH,
            config_path=file_path,
            details={"parse_error": error_details},
            suggestions=[
                "检查配置文件语法是否正确",
                "验证YAML/TOML格式是否有效",
                "检查是否有特殊字符或编码问题",
                "参考配置文件模板重新编写"
            ]
        )
    
    @classmethod
    def missing_required_field(cls, field_name: str, config_path: Optional[str] = None) -> 'ConfigException':
        """缺少必需字段异常"""
        return cls(
            message=f"缺少必需的配置字段: {field_name}",
            error_code=ConfigErrorCode.MISSING_REQUIRED_FIELD,
            severity=ErrorSeverity.HIGH,
            config_key=field_name,
            config_path=config_path,
            suggestions=[
                f"在配置文件中添加必需的字段: {field_name}",
                "参考配置文档确认必需字段列表",
                "检查字段名称拼写是否正确"
            ]
        )
    
    @classmethod
    def invalid_value(cls, field_name: str, value: Any, expected_type: str) -> 'ConfigException':
        """无效值异常"""
        return cls(
            message=f"配置字段 '{field_name}' 的值无效: {value}",
            error_code=ConfigErrorCode.INVALID_VALUE,
            severity=ErrorSeverity.HIGH,
            config_key=field_name,
            details={"actual_value": value, "expected_type": expected_type},
            suggestions=[
                f"请提供 {expected_type} 类型的值",
                f"检查字段 '{field_name}' 的值是否符合要求",
                "参考配置文档确认字段值的格式"
            ]
        )
    
    @classmethod
    def environment_variable_not_set(cls, var_name: str) -> 'ConfigException':
        """环境变量未设置异常"""
        return cls(
            message=f"必需的环境变量未设置: {var_name}",
            error_code=ConfigErrorCode.ENVIRONMENT_VARIABLE_NOT_SET,
            severity=ErrorSeverity.HIGH,
            config_key=var_name,
            suggestions=[
                f"设置环境变量: export {var_name}=your_value",
                f"在配置文件中设置 {var_name} 的值",
                "检查环境变量是否正确加载"
            ]
        )
