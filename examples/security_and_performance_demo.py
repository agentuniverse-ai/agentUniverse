#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AgentUniverse 安全和性能改进演示
展示新增的安全功能、缓存机制、监控和错误处理
"""

import time
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agentuniverse.base.exceptions import ValidationError, SecurityError, ExecutionError
from agentuniverse.base.error_handler import safe_execute, retry, error_handler_decorator
from agentuniverse.base.cache import cached, cached_method, CacheStats
from agentuniverse.base.monitoring import get_monitor, monitor_agent_execution, profile_operation
from agentuniverse.base.util.logging.logging_util import SensitiveInfoFilter


def demo_security_features():
    """演示安全功能"""
    print("🔒 安全功能演示")
    print("=" * 50)
    
    # 1. 敏感信息过滤演示
    print("1. 敏感信息过滤:")
    
    test_logs = [
        "User login with api_key=sk-1234567890abcdef",
        "Database connection: mongodb://user:password123@localhost:27017/db",
        "User email: john@example.com, phone: 13812345678",
        "Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    ]
    
    for log in test_logs:
        filtered = SensitiveInfoFilter.filter_sensitive_info(log)
        print(f"原始: {log}")
        print(f"过滤: {filtered}")
        print()
    
    # 2. 命令安全验证演示
    print("2. 命令安全验证:")
    
    from agentuniverse.agent.action.tool.common_tool.run_command_tool import CommandSecurityValidator
    
    test_commands = [
        ("ls", True, "安全的列表命令"),
        ("cat file.txt", True, "安全的文件读取"),
        ("rm -rf /", False, "危险的删除命令"),
        ("sudo passwd", False, "危险的提权命令"),
        ("ls; rm -rf /", False, "命令注入尝试"),
        ("cat /etc/passwd", False, "路径遍历尝试")
    ]
    
    for command, expected, description in test_commands:
        is_valid = CommandSecurityValidator.validate_command(command)
        status = "✅ 允许" if is_valid else "❌ 拒绝"
        print(f"{status} - {description}: {command}")
    
    print()


def demo_error_handling():
    """演示错误处理功能"""
    print("🛡️ 错误处理演示")
    print("=" * 50)
    
    # 1. 安全执行演示
    print("1. 安全执行:")
    
    def risky_function(x):
        if x < 0:
            raise ValueError("Negative number not allowed")
        return x * 2
    
    # 正常情况
    result = safe_execute(risky_function, 5)
    print(f"安全执行成功: {result}")
    
    # 异常情况
    result = safe_execute(risky_function, -1)
    print(f"安全执行异常: {result}")
    
    # 2. 重试机制演示
    print("\n2. 重试机制:")
    
    call_count = 0
    
    @retry(max_retries=3, delay=0.1)
    def flaky_service():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ConnectionError("Service temporarily unavailable")
        return f"Success after {call_count} attempts"
    
    try:
        result = flaky_service()
        print(f"重试成功: {result}")
    except Exception as e:
        print(f"重试失败: {e}")
    
    # 3. 错误处理装饰器演示
    print("\n3. 错误处理装饰器:")
    
    @error_handler_decorator({"operation": "demo"})
    def validated_function(value):
        if not isinstance(value, int):
            raise ValidationError("Value must be an integer", field_name="value")
        if value < 0:
            raise SecurityError("Negative values not allowed", security_violation="negative_input")
        return value * 2
    
    try:
        result = validated_function(5)
        print(f"验证成功: {result}")
    except Exception as e:
        print(f"验证失败: {e}")
    
    try:
        result = validated_function(-1)
    except Exception as e:
        print(f"安全验证失败: {e}")
    
    print()


def demo_caching():
    """演示缓存功能"""
    print("⚡ 缓存功能演示")
    print("=" * 50)
    
    # 1. 函数缓存演示
    print("1. 函数缓存:")
    
    call_count = 0
    
    @cached(cache_name="demo", ttl=60)
    def expensive_calculation(n):
        nonlocal call_count
        call_count += 1
        print(f"  执行计算: {n} (调用次数: {call_count})")
        time.sleep(0.1)  # 模拟耗时操作
        return n * n
    
    # 第一次调用
    result1 = expensive_calculation(5)
    print(f"结果1: {result1}")
    
    # 第二次调用（从缓存获取）
    result2 = expensive_calculation(5)
    print(f"结果2: {result2}")
    
    # 不同参数（重新计算）
    result3 = expensive_calculation(3)
    print(f"结果3: {result3}")
    
    # 2. 方法缓存演示
    print("\n2. 方法缓存:")
    
    class MathService:
        def __init__(self):
            self.compute_count = 0
        
        @cached_method(cache_name="math_service", ttl=60)
        def fibonacci(self, n):
            self.compute_count += 1
            print(f"  计算斐波那契: {n} (计算次数: {self.compute_count})")
            if n <= 1:
                return n
            return self.fibonacci(n-1) + self.fibonacci(n-2)
    
    math_service = MathService()
    
    # 计算斐波那契数列
    fib_result = math_service.fibonacci(10)
    print(f"斐波那契(10): {fib_result}")
    
    # 再次计算（应该从缓存获取）
    fib_result2 = math_service.fibonacci(10)
    print(f"斐波那契(10) 再次: {fib_result2}")
    
    # 3. 缓存统计演示
    print("\n3. 缓存统计:")
    stats = CacheStats.get_all_stats()
    for cache_name, cache_stats in stats.items():
        print(f"缓存 '{cache_name}': {cache_stats}")
    
    print()


def demo_monitoring():
    """演示监控功能"""
    print("📊 监控功能演示")
    print("=" * 50)
    
    monitor = get_monitor()
    
    # 1. Agent执行监控演示
    print("1. Agent执行监控:")
    
    @monitor_agent_execution("demo_agent")
    def simulate_agent_work(work_type):
        time.sleep(0.1)  # 模拟工作
        if work_type == "error":
            raise Exception("模拟错误")
        return f"完成 {work_type} 工作"
    
    # 模拟多次执行
    for i in range(5):
        try:
            result = simulate_agent_work("normal")
            print(f"  Agent执行成功: {result}")
        except Exception as e:
            print(f"  Agent执行失败: {e}")
    
    # 模拟错误执行
    try:
        simulate_agent_work("error")
    except Exception:
        pass
    
    # 获取Agent统计信息
    stats = monitor.get_agent_stats("demo_agent")
    print(f"\nAgent统计信息:")
    print(f"  总请求数: {stats.get('total_requests', 0)}")
    print(f"  成功请求数: {stats.get('successful_requests', 0)}")
    print(f"  失败请求数: {stats.get('failed_requests', 0)}")
    print(f"  错误率: {stats.get('error_rate', 0):.2%}")
    print(f"  平均响应时间: {stats.get('average_response_time', 0):.3f}秒")
    
    # 2. 性能分析演示
    print("\n2. 性能分析:")
    
    @profile_operation("demo_operation")
    def slow_operation():
        time.sleep(0.05)
        return "操作完成"
    
    # 执行多次操作
    for i in range(3):
        result = slow_operation()
        print(f"  执行操作: {result}")
    
    # 获取性能统计
    from agentuniverse.base.monitoring import get_performance_stats
    perf_stats = get_performance_stats("demo_operation")
    print(f"\n性能统计:")
    print(f"  执行次数: {perf_stats.get('count', 0)}")
    print(f"  最小耗时: {perf_stats.get('min', 0):.3f}秒")
    print(f"  最大耗时: {perf_stats.get('max', 0):.3f}秒")
    print(f"  平均耗时: {perf_stats.get('avg', 0):.3f}秒")
    
    # 3. 健康检查演示
    print("\n3. 健康检查:")
    
    def check_database():
        # 模拟数据库检查
        return True
    
    def check_external_service():
        # 模拟外部服务检查
        return False
    
    # 添加健康检查
    monitor.add_health_check("database", check_database)
    monitor.add_health_check("external_service", check_external_service)
    
    # 获取健康状态
    health = monitor.get_health_status()
    print(f"整体健康状态: {'健康' if health['overall_healthy'] else '不健康'}")
    print(f"健康比例: {health['healthy_ratio']:.1%}")
    
    for check_name, check_result in health['details'].items():
        status = "✅" if check_result['healthy'] else "❌"
        print(f"  {status} {check_name}: {'健康' if check_result['healthy'] else '不健康'}")
    
    print()


def main():
    """主函数"""
    print("🚀 AgentUniverse 安全和性能改进演示")
    print("=" * 60)
    print()
    
    try:
        demo_security_features()
        demo_error_handling()
        demo_caching()
        demo_monitoring()
        
        print("✅ 所有演示完成！")
        print("\n📝 改进总结:")
        print("1. 🔒 安全功能: 命令验证、输入验证、敏感信息过滤")
        print("2. 🛡️ 错误处理: 标准化异常、安全执行、重试机制")
        print("3. ⚡ 缓存系统: LRU缓存、装饰器缓存、统计信息")
        print("4. 📊 监控系统: Agent监控、性能分析、健康检查")
        print("5. 🧪 测试覆盖: 全面的单元测试和集成测试")
        
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
