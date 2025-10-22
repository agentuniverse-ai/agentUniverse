# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/19 10:30
# @Author  : AI Assistant
# @Email   : assistant@example.com
# @FileName: error_handler.py

"""
AgentUniverse 错误处理器
"""

import traceback
import logging
from typing import Optional, Dict, Any, Callable, Type
from functools import wraps

from .exceptions import AgentUniverseException
from .util.logging.logging_util import LOGGER


class ErrorHandler:
    """统一错误处理器"""
    
    def __init__(self):
        self.error_handlers: Dict[Type[Exception], Callable] = {}
        self.default_handler = self._default_error_handler
    
    def register_handler(self, exception_type: Type[Exception], 
                        handler: Callable[[Exception], Any]):
        """注册特定异常类型的处理器"""
        self.error_handlers[exception_type] = handler
    
    def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> Any:
        """处理错误"""
        try:
            # 查找特定处理器
            for exc_type, handler in self.error_handlers.items():
                if isinstance(error, exc_type):
                    return handler(error, context)
            
            # 使用默认处理器
            return self.default_handler(error, context)
            
        except Exception as handler_error:
            LOGGER.error(f"Error in error handler: {handler_error}")
            return self._fallback_handler(error, context)
    
    def _default_error_handler(self, error: Exception, 
                              context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """默认错误处理器"""
        if isinstance(error, AgentUniverseException):
            return {
                "success": False,
                "error": error.to_dict(),
                "context": context or {}
            }
        else:
            return {
                "success": False,
                "error": {
                    "error_type": error.__class__.__name__,
                    "error_code": "UNKNOWN_ERROR",
                    "message": str(error),
                    "details": {
                        "traceback": traceback.format_exc()
                    }
                },
                "context": context or {}
            }
    
    def _fallback_handler(self, error: Exception, 
                         context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """备用错误处理器"""
        return {
            "success": False,
            "error": {
                "error_type": "ErrorHandlerFailure",
                "error_code": "HANDLER_ERROR",
                "message": "Failed to handle error properly",
                "details": {
                    "original_error": str(error),
                    "traceback": traceback.format_exc()
                }
            },
            "context": context or {}
        }


# 全局错误处理器实例
_global_error_handler = ErrorHandler()


def handle_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> Any:
    """处理错误的便捷函数"""
    return _global_error_handler.handle_error(error, context)


def register_error_handler(exception_type: Type[Exception], 
                          handler: Callable[[Exception], Any]):
    """注册错误处理器的便捷函数"""
    _global_error_handler.register_handler(exception_type, handler)


def safe_execute(func: Callable, *args, **kwargs) -> Dict[str, Any]:
    """安全执行函数，自动处理异常"""
    try:
        result = func(*args, **kwargs)
        return {
            "success": True,
            "result": result,
            "error": None
        }
    except Exception as error:
        return handle_error(error, {
            "function": func.__name__,
            "args": str(args),
            "kwargs": str(kwargs)
        })


def error_handler_decorator(context: Optional[Dict[str, Any]] = None):
    """错误处理装饰器"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as error:
                error_context = context or {}
                error_context.update({
                    "function": func.__name__,
                    "module": func.__module__
                })
                handled_error = handle_error(error, error_context)
                
                # 如果是AgentUniverse异常，直接抛出
                if isinstance(error, AgentUniverseException):
                    raise error
                
                # 其他异常转换为标准异常
                from .exceptions import ExecutionError
                raise ExecutionError(
                    message=f"Error in {func.__name__}: {str(error)}",
                    component_name=func.__module__,
                    details=handled_error.get("error", {})
                )
        
        return wrapper
    return decorator


class RetryHandler:
    """重试处理器"""
    
    def __init__(self, max_retries: int = 3, delay: float = 1.0, 
                 backoff_factor: float = 2.0):
        self.max_retries = max_retries
        self.delay = delay
        self.backoff_factor = backoff_factor
    
    def retry_on_error(self, func: Callable, *args, **kwargs) -> Any:
        """在错误时重试"""
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as error:
                last_error = error
                
                if attempt < self.max_retries:
                    wait_time = self.delay * (self.backoff_factor ** attempt)
                    LOGGER.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {error}")
                    import time
                    time.sleep(wait_time)
                else:
                    LOGGER.error(f"All {self.max_retries + 1} attempts failed")
                    break
        
        # 如果所有重试都失败，抛出最后一个错误
        raise last_error


def retry(max_retries: int = 3, delay: float = 1.0, backoff_factor: float = 2.0):
    """重试装饰器"""
    retry_handler = RetryHandler(max_retries, delay, backoff_factor)
    
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return retry_handler.retry_on_error(func, *args, **kwargs)
        return wrapper
    return decorator
