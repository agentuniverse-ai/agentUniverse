# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/19 12:30
# @Author  : AI Assistant
# @Email   : assistant@example.com
# @FileName: test_performance_improvements.py

"""
测试性能改进功能
"""

import pytest
import time
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agentuniverse.base.cache import CacheManager, cached, cached_method, get_cache_key
from agentuniverse.base.monitoring import AgentMonitor, MetricsCollector, AlertRule
from agentuniverse.base.error_handler import ErrorHandler, safe_execute, retry


class TestCacheSystem:
    """测试缓存系统"""
    
    def test_cache_manager_basic_operations(self):
        """测试缓存管理器基本操作"""
        cache_manager = CacheManager()
        
        # 测试设置和获取
        cache_manager.set("test_cache", "key1", "value1", 3600)
        assert cache_manager.get("test_cache", "key1") == "value1"
        
        # 测试删除
        cache_manager.delete("test_cache", "key1")
        assert cache_manager.get("test_cache", "key1") is None
    
    def test_cache_ttl(self):
        """测试缓存TTL"""
        cache_manager = CacheManager()
        
        # 设置短期TTL
        cache_manager.set("test_cache", "key2", "value2", 0.1)  # 100ms
        assert cache_manager.get("test_cache", "key2") == "value2"
        
        # 等待过期
        time.sleep(0.2)
        assert cache_manager.get("test_cache", "key2") is None
    
    def test_cache_decorator(self):
        """测试缓存装饰器"""
        call_count = 0
        
        @cached(cache_name="test", ttl=3600)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # 第一次调用
        result1 = expensive_function(5)
        assert result1 == 10
        assert call_count == 1
        
        # 第二次调用（应该从缓存获取）
        result2 = expensive_function(5)
        assert result2 == 10
        assert call_count == 1  # 没有增加
        
        # 不同参数（应该重新计算）
        result3 = expensive_function(3)
        assert result3 == 6
        assert call_count == 2
    
    def test_cached_method_decorator(self):
        """测试方法缓存装饰器"""
        class TestClass:
            def __init__(self):
                self.call_count = 0
            
            @cached_method(cache_name="test_method", ttl=3600)
            def expensive_method(self, x):
                self.call_count += 1
                return x ** 2
        
        obj = TestClass()
        
        # 第一次调用
        result1 = obj.expensive_method(4)
        assert result1 == 16
        assert obj.call_count == 1
        
        # 第二次调用（应该从缓存获取）
        result2 = obj.expensive_method(4)
        assert result2 == 16
        assert obj.call_count == 1  # 没有增加
    
    def test_cache_key_generation(self):
        """测试缓存键生成"""
        key1 = get_cache_key("func", 1, 2, a=3, b=4)
        key2 = get_cache_key("func", 1, 2, a=3, b=4)
        key3 = get_cache_key("func", 1, 2, a=3, b=5)
        
        # 相同参数应该生成相同键
        assert key1 == key2
        
        # 不同参数应该生成不同键
        assert key1 != key3
    
    def test_lru_cache_eviction(self):
        """测试LRU缓存淘汰"""
        from agentuniverse.base.cache import LRUCache
        
        cache = LRUCache(max_size=3)
        
        # 添加3个条目
        cache.set("key1", "value1", 3600)
        cache.set("key2", "value2", 3600)
        cache.set("key3", "value3", 3600)
        
        # 访问key1使其变为最近使用
        cache.get("key1")
        
        # 添加第4个条目，应该淘汰key2（最旧的）
        cache.set("key4", "value4", 3600)
        
        assert cache.get("key1") == "value1"  # 应该还在
        assert cache.get("key2") is None      # 应该被淘汰
        assert cache.get("key3") == "value3"  # 应该还在
        assert cache.get("key4") == "value4"  # 新添加的


class TestMonitoringSystem:
    """测试监控系统"""
    
    def test_metrics_collector(self):
        """测试指标收集器"""
        collector = MetricsCollector()
        
        # 记录指标
        collector.record_metric("test_metric", 10.5, {"label": "value"})
        collector.record_metric("test_metric", 20.3, {"label": "value"})
        collector.record_metric("test_metric", 15.7, {"label": "value"})
        
        # 获取指标
        metrics = collector.get_metric("test_metric")
        assert len(metrics) == 3
        assert metrics[-1].value == 15.7
        
        # 获取最新值
        latest = collector.get_latest_value("test_metric")
        assert latest == 15.7
        
        # 获取平均值
        avg = collector.get_average("test_metric", 3600)
        assert abs(avg - (10.5 + 20.3 + 15.7) / 3) < 0.01
    
    def test_agent_monitor(self):
        """测试Agent监控"""
        monitor = AgentMonitor()
        
        # 记录执行
        monitor.record_agent_execution("test_agent", 1.5, True)
        monitor.record_agent_execution("test_agent", 2.0, True)
        monitor.record_agent_execution("test_agent", 0.5, False)
        
        # 获取统计信息
        stats = monitor.get_agent_stats("test_agent")
        assert stats["total_requests"] == 3
        assert stats["successful_requests"] == 2
        assert stats["failed_requests"] == 1
        assert stats["error_rate"] == 1/3
        assert abs(stats["average_response_time"] - (1.5 + 2.0 + 0.5) / 3) < 0.01
    
    def test_alert_rules(self):
        """测试告警规则"""
        monitor = AgentMonitor()
        
        # 添加自定义告警规则
        def high_error_rate(error_rate):
            return error_rate > 0.1
        
        monitor.add_alert_rule(AlertRule(
            name="custom_error_rate",
            condition=high_error_rate,
            severity="critical",
            message="Custom error rate is too high"
        ))
        
        # 模拟高错误率
        monitor.record_agent_execution("test_agent", 1.0, False)
        monitor.record_agent_execution("test_agent", 1.0, False)
        monitor.record_agent_execution("test_agent", 1.0, False)
        monitor.record_agent_execution("test_agent", 1.0, True)  # 75%错误率
        
        # 检查告警（这里只是测试规则添加，实际告警触发需要更复杂的逻辑）
        stats = monitor.get_agent_stats("test_agent")
        assert stats["error_rate"] == 0.75
        assert high_error_rate(stats["error_rate"])  # 应该触发告警条件


class TestErrorHandling:
    """测试错误处理"""
    
    def test_error_handler(self):
        """测试错误处理器"""
        handler = ErrorHandler()
        
        # 测试标准异常处理
        try:
            raise ValueError("Test error")
        except Exception as e:
            result = handler.handle_error(e)
            assert result["success"] is False
            assert "error" in result
            assert result["error"]["error_type"] == "ValueError"
    
    def test_safe_execute(self):
        """测试安全执行"""
        def success_function():
            return "success"
        
        def error_function():
            raise ValueError("Test error")
        
        # 测试成功执行
        result = safe_execute(success_function)
        assert result["success"] is True
        assert result["result"] == "success"
        assert result["error"] is None
        
        # 测试错误执行
        result = safe_execute(error_function)
        assert result["success"] is False
        assert result["result"] is None
        assert result["error"] is not None
    
    def test_retry_decorator(self):
        """测试重试装饰器"""
        call_count = 0
        
        @retry(max_retries=3, delay=0.1)
        def flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary error")
            return "success"
        
        # 应该重试2次后成功
        result = flaky_function()
        assert result == "success"
        assert call_count == 3
        
        # 测试重试次数用完的情况
        call_count = 0
        
        @retry(max_retries=2, delay=0.1)
        def always_failing_function():
            nonlocal call_count
            call_count += 1
            raise ValueError("Always fails")
        
        with pytest.raises(ValueError):
            always_failing_function()
        
        assert call_count == 3  # 1次原始调用 + 2次重试


class TestPerformanceProfiling:
    """测试性能分析"""
    
    def test_performance_profiler(self):
        """测试性能分析器"""
        from agentuniverse.base.monitoring import PerformanceProfiler
        
        profiler = PerformanceProfiler()
        
        # 测试计时
        with profiler.start_timer("test_operation") as timer:
            time.sleep(0.1)
        
        stats = profiler.get_stats("test_operation")
        assert stats["count"] == 1
        assert stats["min"] >= 0.1
        assert stats["max"] >= 0.1
        assert stats["avg"] >= 0.1
    
    def test_profile_decorator(self):
        """测试性能分析装饰器"""
        from agentuniverse.base.monitoring import profile_operation, get_performance_stats
        
        @profile_operation("decorated_function")
        def test_function():
            time.sleep(0.05)
            return "done"
        
        # 执行多次
        for _ in range(3):
            result = test_function()
            assert result == "done"
        
        # 检查统计信息
        stats = get_performance_stats("decorated_function")
        assert stats["count"] == 3
        assert stats["min"] >= 0.05
        assert stats["max"] >= 0.05
        assert stats["avg"] >= 0.05


if __name__ == "__main__":
    pytest.main([__file__])
