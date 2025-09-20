# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/19 11:30
# @Author  : AI Assistant
# @Email   : assistant@example.com
# @FileName: monitoring.py

"""
AgentUniverse 监控和告警系统
"""

import time
import threading
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum
import statistics

from .util.logging.logging_util import LOGGER


class MetricType(Enum):
    """指标类型"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


@dataclass
class MetricValue:
    """指标值"""
    value: float
    timestamp: float
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class AlertRule:
    """告警规则"""
    name: str
    condition: Callable[[float], bool]
    severity: str = "warning"
    message: str = ""
    cooldown: float = 300.0  # 5分钟冷却时间
    last_triggered: float = 0.0


class MetricsCollector:
    """指标收集器"""
    
    def __init__(self, max_samples: int = 1000):
        self.max_samples = max_samples
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_samples))
        self.lock = threading.RLock()
    
    def record_metric(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """记录指标"""
        with self.lock:
            metric_value = MetricValue(
                value=value,
                timestamp=time.time(),
                labels=labels or {}
            )
            self.metrics[name].append(metric_value)
    
    def get_metric(self, name: str) -> List[MetricValue]:
        """获取指标数据"""
        with self.lock:
            return list(self.metrics.get(name, []))
    
    def get_latest_value(self, name: str) -> Optional[float]:
        """获取最新值"""
        with self.lock:
            if name in self.metrics and self.metrics[name]:
                return self.metrics[name][-1].value
            return None
    
    def get_average(self, name: str, duration: float = 300.0) -> Optional[float]:
        """获取平均值"""
        with self.lock:
            if name not in self.metrics:
                return None
            
            current_time = time.time()
            recent_values = [
                mv.value for mv in self.metrics[name]
                if current_time - mv.timestamp <= duration
            ]
            
            return statistics.mean(recent_values) if recent_values else None
    
    def get_percentile(self, name: str, percentile: float, duration: float = 300.0) -> Optional[float]:
        """获取百分位数"""
        with self.lock:
            if name not in self.metrics:
                return None
            
            current_time = time.time()
            recent_values = [
                mv.value for mv in self.metrics[name]
                if current_time - mv.timestamp <= duration
            ]
            
            if not recent_values:
                return None
            
            return statistics.quantiles(recent_values, n=100)[int(percentile) - 1]


class AlertManager:
    """告警管理器"""
    
    def __init__(self):
        self.rules: Dict[str, AlertRule] = {}
        self.lock = threading.RLock()
    
    def add_rule(self, rule: AlertRule):
        """添加告警规则"""
        with self.lock:
            self.rules[rule.name] = rule
    
    def check_alerts(self, metrics_collector: MetricsCollector):
        """检查告警"""
        with self.lock:
            current_time = time.time()
            
            for rule_name, rule in self.rules.items():
                # 检查冷却时间
                if current_time - rule.last_triggered < rule.cooldown:
                    continue
                
                # 获取最新指标值
                latest_value = metrics_collector.get_latest_value(rule_name)
                if latest_value is None:
                    continue
                
                # 检查告警条件
                if rule.condition(latest_value):
                    self._trigger_alert(rule, latest_value)
                    rule.last_triggered = current_time
    
    def _trigger_alert(self, rule: AlertRule, value: float):
        """触发告警"""
        message = rule.message or f"Alert triggered for {rule.name}: {value}"
        
        LOGGER.warning(f"[ALERT {rule.severity.upper()}] {message}")
        
        # 这里可以添加更多的告警通知方式
        # 例如：发送邮件、短信、Slack通知等


class HealthChecker:
    """健康检查器"""
    
    def __init__(self):
        self.checks: Dict[str, Callable] = {}
        self.results: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.RLock()
    
    def add_check(self, name: str, check_func: Callable[[], bool]):
        """添加健康检查"""
        with self.lock:
            self.checks[name] = check_func
    
    def run_checks(self) -> Dict[str, Dict[str, Any]]:
        """运行所有健康检查"""
        with self.lock:
            results = {}
            
            for name, check_func in self.checks.items():
                try:
                    start_time = time.time()
                    is_healthy = check_func()
                    duration = time.time() - start_time
                    
                    results[name] = {
                        "healthy": is_healthy,
                        "duration": duration,
                        "timestamp": time.time(),
                        "error": None
                    }
                except Exception as e:
                    results[name] = {
                        "healthy": False,
                        "duration": 0.0,
                        "timestamp": time.time(),
                        "error": str(e)
                    }
            
            self.results = results
            return results
    
    def get_overall_health(self) -> Dict[str, Any]:
        """获取整体健康状态"""
        results = self.run_checks()
        
        healthy_count = sum(1 for r in results.values() if r["healthy"])
        total_count = len(results)
        
        return {
            "overall_healthy": healthy_count == total_count,
            "healthy_ratio": healthy_count / total_count if total_count > 0 else 0,
            "total_checks": total_count,
            "healthy_checks": healthy_count,
            "unhealthy_checks": total_count - healthy_count,
            "details": results
        }


class AgentMonitor:
    """Agent监控器"""
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager()
        self.health_checker = HealthChecker()
        self.agent_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_response_time": 0.0,
            "last_request_time": 0.0,
            "error_rate": 0.0,
            "average_response_time": 0.0
        })
        self.lock = threading.RLock()
        
        # 设置默认告警规则
        self._setup_default_alerts()
    
    def _setup_default_alerts(self):
        """设置默认告警规则"""
        # 错误率告警
        self.alert_manager.add_rule(AlertRule(
            name="error_rate",
            condition=lambda x: x > 0.05,  # 错误率超过5%
            severity="critical",
            message="Agent error rate is too high",
            cooldown=60.0
        ))
        
        # 响应时间告警
        self.alert_manager.add_rule(AlertRule(
            name="response_time",
            condition=lambda x: x > 30.0,  # 响应时间超过30秒
            severity="warning",
            message="Agent response time is too slow",
            cooldown=120.0
        ))
    
    def record_agent_execution(self, agent_name: str, duration: float, success: bool):
        """记录Agent执行"""
        with self.lock:
            stats = self.agent_stats[agent_name]
            stats["total_requests"] += 1
            stats["total_response_time"] += duration
            stats["last_request_time"] = time.time()
            
            if success:
                stats["successful_requests"] += 1
            else:
                stats["failed_requests"] += 1
            
            # 计算错误率
            stats["error_rate"] = stats["failed_requests"] / stats["total_requests"]
            
            # 计算平均响应时间
            stats["average_response_time"] = stats["total_response_time"] / stats["total_requests"]
            
            # 记录指标
            self.metrics_collector.record_metric("error_rate", stats["error_rate"], 
                                               {"agent": agent_name})
            self.metrics_collector.record_metric("response_time", duration, 
                                               {"agent": agent_name})
            self.metrics_collector.record_metric("request_count", 1, 
                                               {"agent": agent_name})
    
    def get_agent_stats(self, agent_name: str) -> Dict[str, Any]:
        """获取Agent统计信息"""
        with self.lock:
            return self.agent_stats.get(agent_name, {}).copy()
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """获取所有Agent统计信息"""
        with self.lock:
            return {name: stats.copy() for name, stats in self.agent_stats.items()}
    
    def get_health_status(self) -> Dict[str, Any]:
        """获取健康状态"""
        return self.health_checker.get_overall_health()
    
    def check_alerts(self):
        """检查告警"""
        self.alert_manager.check_alerts(self.metrics_collector)
    
    def add_health_check(self, name: str, check_func: Callable[[], bool]):
        """添加健康检查"""
        self.health_checker.add_check(name, check_func)
    
    def add_alert_rule(self, rule: AlertRule):
        """添加告警规则"""
        self.alert_manager.add_rule(rule)


# 全局监控器实例
_global_monitor = AgentMonitor()


def get_monitor() -> AgentMonitor:
    """获取全局监控器"""
    return _global_monitor


def monitor_agent_execution(agent_name: str):
    """Agent执行监控装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            error = None
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                error = e
                raise
            finally:
                duration = time.time() - start_time
                _global_monitor.record_agent_execution(agent_name, duration, success)
        
        return wrapper
    return decorator


class PerformanceProfiler:
    """性能分析器"""
    
    def __init__(self):
        self.profiles: Dict[str, List[float]] = defaultdict(list)
        self.lock = threading.RLock()
    
    def start_timer(self, operation: str) -> 'TimerContext':
        """开始计时"""
        return TimerContext(operation, self)
    
    def record_time(self, operation: str, duration: float):
        """记录执行时间"""
        with self.lock:
            self.profiles[operation].append(duration)
    
    def get_stats(self, operation: str) -> Dict[str, float]:
        """获取统计信息"""
        with self.lock:
            if operation not in self.profiles or not self.profiles[operation]:
                return {}
            
            times = self.profiles[operation]
            return {
                "count": len(times),
                "min": min(times),
                "max": max(times),
                "avg": statistics.mean(times),
                "median": statistics.median(times),
                "p95": statistics.quantiles(times, n=20)[18] if len(times) > 1 else times[0],
                "p99": statistics.quantiles(times, n=100)[98] if len(times) > 1 else times[0]
            }


class TimerContext:
    """计时器上下文"""
    
    def __init__(self, operation: str, profiler: PerformanceProfiler):
        self.operation = operation
        self.profiler = profiler
        self.start_time = time.time()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        self.profiler.record_time(self.operation, duration)


# 全局性能分析器
_global_profiler = PerformanceProfiler()


def profile_operation(operation_name: str):
    """操作性能分析装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            with _global_profiler.start_timer(operation_name):
                return func(*args, **kwargs)
        return wrapper
    return decorator


def get_performance_stats(operation: str) -> Dict[str, float]:
    """获取性能统计"""
    return _global_profiler.get_stats(operation)
