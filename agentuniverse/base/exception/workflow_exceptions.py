"""
工作流相关异常类

处理工作流节点、执行、验证等过程中的错误。
"""

from typing import Optional, List, Dict, Any
from .agentuniverse_exception import (
    AgentUniverseException,
    AgentUniverseErrorCode,
    ErrorSeverity,
    ErrorCategory
)


class WorkflowNodeNotFoundError(AgentUniverseException):
    """工作流节点未找到异常"""
    
    def __init__(
        self,
        node_id: str,
        workflow_id: str,
        available_nodes: Optional[List[str]] = None,
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        suggestions = [
            f"检查工作流 '{workflow_id}' 中的节点ID '{node_id}' 是否正确",
            "确认节点是否已定义",
            "查看工作流配置文件是否正确加载"
        ]
        
        if available_nodes:
            suggestions.extend([
                f"可用的节点列表: {', '.join(available_nodes)}",
                "检查节点名称拼写是否正确"
            ])
        
        suggestions.extend([
            "参考工作流配置文档",
            "检查工作流配置文件路径"
        ])
        
        super().__init__(
            error_code=AgentUniverseErrorCode.WORKFLOW_NODE_NOT_FOUND,
            message=f"工作流节点未找到: {node_id}",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.WORKFLOW,
            details=details or {
                "node_id": node_id,
                "workflow_id": workflow_id,
                "available_nodes": available_nodes or []
            },
            suggestions=suggestions,
            original_exception=original_exception
        )


class WorkflowExecutionError(AgentUniverseException):
    """工作流执行错误异常"""
    
    def __init__(
        self,
        workflow_id: str,
        execution_error: str,
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        suggestions = [
            f"检查工作流 '{workflow_id}' 的执行参数",
            "验证工作流依赖是否满足",
            "检查工作流所需的资源是否可用",
            "查看工作流执行日志获取更多信息",
            "参考工作流使用文档"
        ]
        
        super().__init__(
            error_code=AgentUniverseErrorCode.WORKFLOW_EXECUTION_ERROR,
            message=f"工作流执行失败: {workflow_id}",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.WORKFLOW,
            details=details or {
                "workflow_id": workflow_id,
                "execution_error": execution_error
            },
            suggestions=suggestions,
            original_exception=original_exception
        )


class WorkflowValidationError(AgentUniverseException):
    """工作流验证错误异常"""
    
    def __init__(
        self,
        workflow_id: str,
        validation_errors: List[str],
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        suggestions = [
            f"检查工作流 '{workflow_id}' 的配置:",
            *[f"  - {error}" for error in validation_errors],
            "参考工作流配置模板",
            "使用工作流验证工具检查配置"
        ]
        
        super().__init__(
            error_code=AgentUniverseErrorCode.WORKFLOW_VALIDATION_ERROR,
            message=f"工作流验证失败: {workflow_id}",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.WORKFLOW,
            details=details or {
                "workflow_id": workflow_id,
                "validation_errors": validation_errors
            },
            suggestions=suggestions,
            original_exception=original_exception
        )


class WorkflowGraphError(AgentUniverseException):
    """工作流图错误异常"""
    
    def __init__(
        self,
        workflow_id: str,
        graph_error: str,
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        suggestions = [
            f"检查工作流 '{workflow_id}' 的图结构",
            "验证节点之间的连接是否正确",
            "检查是否存在循环依赖",
            "确认起始节点和结束节点是否正确定义",
            "参考工作流图设计文档"
        ]
        
        super().__init__(
            error_code=AgentUniverseErrorCode.WORKFLOW_GRAPH_ERROR,
            message=f"工作流图错误: {workflow_id}",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.WORKFLOW,
            details=details or {
                "workflow_id": workflow_id,
                "graph_error": graph_error
            },
            suggestions=suggestions,
            original_exception=original_exception
        )
