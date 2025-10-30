"""
AgentUniverse 统一异常处理模块

该模块提供了标准化的异常处理机制，用于改善错误信息的可读性和用户体验。
所有异常都包含错误代码、详细描述和解决建议。

主要特性：
- 统一的错误信息格式
- 错误代码系统
- 多语言支持（中英文）
- 解决建议和修复指导
- 详细的错误上下文信息
"""

from .agentuniverse_exception import (
    AgentUniverseException,
    AgentUniverseErrorCode,
    ErrorSeverity,
    ErrorCategory
)
from .config_exceptions import (
    ConfigFileNotFoundError,
    ConfigParseError,
    UnsupportedConfigFormatError,
    ConfigValidationError
)
from .service_exceptions import (
    ServiceNotFoundError,
    ServiceInitializationError,
    ServiceExecutionError
)
from .tool_exceptions import (
    ToolNotFoundError,
    ToolExecutionError,
    ToolParameterError,
    ToolTimeoutError
)
from .llm_exceptions import (
    LLMConnectionError,
    LLMAuthenticationError,
    LLMRateLimitError,
    LLMModelNotFoundError,
    LLMExecutionError
)
from .workflow_exceptions import (
    WorkflowNodeNotFoundError,
    WorkflowExecutionError,
    WorkflowValidationError,
    WorkflowGraphError
)

__all__ = [
    # 基础异常类
    'AgentUniverseException',
    'AgentUniverseErrorCode',
    'ErrorSeverity',
    'ErrorCategory',
    
    # 配置相关异常
    'ConfigFileNotFoundError',
    'ConfigParseError',
    'UnsupportedConfigFormatError',
    'ConfigValidationError',
    
    # 服务相关异常
    'ServiceNotFoundError',
    'ServiceInitializationError',
    'ServiceExecutionError',
    
    # 工具相关异常
    'ToolNotFoundError',
    'ToolExecutionError',
    'ToolParameterError',
    'ToolTimeoutError',
    
    # LLM相关异常
    'LLMConnectionError',
    'LLMAuthenticationError',
    'LLMRateLimitError',
    'LLMModelNotFoundError',
    'LLMExecutionError',
    
    # 工作流相关异常
    'WorkflowNodeNotFoundError',
    'WorkflowExecutionError',
    'WorkflowValidationError',
    'WorkflowGraphError',
]