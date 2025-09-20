# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/19 11:00
# @Author  : AI Assistant
# @Email   : assistant@example.com
# @FileName: cache.py

"""
AgentUniverse 智能缓存系统
"""

import time
import hashlib
import json
import threading
from typing import Any, Optional, Dict, Callable, Union
from functools import wraps
from dataclasses import dataclass
from collections import OrderedDict

from .util.logging.logging_util import LOGGER


@dataclass
class CacheEntry:
    """缓存条目"""
    value: Any
    timestamp: float
    ttl: float
    access_count: int = 0
    last_access: float = 0.0
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        return time.time() - self.timestamp > self.ttl
    
    def access(self):
        """访问缓存条目"""
        self.access_count += 1
        self.last_access = time.time()


class LRUCache:
    """LRU缓存实现"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        with self.lock:
            if key in self.cache:
                entry = self.cache[key]
                
                # 检查是否过期
                if entry.is_expired():
                    del self.cache[key]
                    return None
                
                # 更新访问信息
                entry.access()
                # 移动到末尾（最近使用）
                self.cache.move_to_end(key)
                return entry.value
            
            return None
    
    def set(self, key: str, value: Any, ttl: float = 3600.0):
        """设置缓存值"""
        with self.lock:
            # 如果键已存在，删除旧条目
            if key in self.cache:
                del self.cache[key]
            
            # 如果缓存已满，删除最旧的条目
            while len(self.cache) >= self.max_size:
                self.cache.popitem(last=False)
            
            # 添加新条目
            entry = CacheEntry(
                value=value,
                timestamp=time.time(),
                ttl=ttl
            )
            self.cache[key] = entry
    
    def delete(self, key: str) -> bool:
        """删除缓存条目"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False
    
    def clear(self):
        """清空缓存"""
        with self.lock:
            self.cache.clear()
    
    def cleanup_expired(self):
        """清理过期的缓存条目"""
        with self.lock:
            expired_keys = [
                key for key, entry in self.cache.items() 
                if entry.is_expired()
            ]
            for key in expired_keys:
                del self.cache[key]
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        with self.lock:
            return {
                "size": len(self.cache),
                "max_size": self.max_size,
                "hit_ratio": self._calculate_hit_ratio()
            }
    
    def _calculate_hit_ratio(self) -> float:
        """计算命中率"""
        total_access = sum(entry.access_count for entry in self.cache.values())
        if total_access == 0:
            return 0.0
        
        hit_count = sum(1 for entry in self.cache.values() if entry.access_count > 1)
        return hit_count / total_access if total_access > 0 else 0.0


class CacheManager:
    """缓存管理器"""
    
    def __init__(self):
        self.caches: Dict[str, LRUCache] = {}
        self.default_ttl = 3600.0  # 1小时
        self.cleanup_interval = 300.0  # 5分钟
        self.last_cleanup = time.time()
        self.lock = threading.RLock()
    
    def get_cache(self, name: str, max_size: int = 1000) -> LRUCache:
        """获取或创建缓存"""
        with self.lock:
            if name not in self.caches:
                self.caches[name] = LRUCache(max_size)
            return self.caches[name]
    
    def get(self, cache_name: str, key: str) -> Optional[Any]:
        """获取缓存值"""
        cache = self.get_cache(cache_name)
        return cache.get(key)
    
    def set(self, cache_name: str, key: str, value: Any, ttl: Optional[float] = None):
        """设置缓存值"""
        cache = self.get_cache(cache_name)
        ttl = ttl or self.default_ttl
        cache.set(key, value, ttl)
        
        # 定期清理过期缓存
        self._maybe_cleanup()
    
    def delete(self, cache_name: str, key: str) -> bool:
        """删除缓存条目"""
        cache = self.get_cache(cache_name)
        return cache.delete(key)
    
    def clear_cache(self, cache_name: str):
        """清空指定缓存"""
        cache = self.get_cache(cache_name)
        cache.clear()
    
    def clear_all(self):
        """清空所有缓存"""
        with self.lock:
            for cache in self.caches.values():
                cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """获取所有缓存的统计信息"""
        with self.lock:
            stats = {}
            for name, cache in self.caches.items():
                stats[name] = cache.get_stats()
            return stats
    
    def _maybe_cleanup(self):
        """可能清理过期缓存"""
        current_time = time.time()
        if current_time - self.last_cleanup > self.cleanup_interval:
            self.cleanup_expired()
            self.last_cleanup = current_time
    
    def cleanup_expired(self):
        """清理所有过期缓存"""
        with self.lock:
            for cache in self.caches.values():
                cache.cleanup_expired()


# 全局缓存管理器
_global_cache_manager = CacheManager()


def get_cache_key(*args, **kwargs) -> str:
    """生成缓存键"""
    # 将参数序列化为字符串
    key_data = {
        "args": args,
        "kwargs": kwargs
    }
    key_str = json.dumps(key_data, sort_keys=True, default=str)
    
    # 生成MD5哈希
    return hashlib.md5(key_str.encode()).hexdigest()


def cached(cache_name: str = "default", ttl: float = 3600.0, 
           max_size: int = 1000, key_func: Optional[Callable] = None):
    """缓存装饰器"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = get_cache_key(func.__name__, *args, **kwargs)
            
            # 尝试从缓存获取
            cache = _global_cache_manager.get_cache(cache_name, max_size)
            cached_result = cache.get(cache_key)
            
            if cached_result is not None:
                LOGGER.debug(f"Cache hit for {func.__name__}: {cache_key[:8]}...")
                return cached_result
            
            # 执行函数并缓存结果
            LOGGER.debug(f"Cache miss for {func.__name__}: {cache_key[:8]}...")
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


def cached_method(cache_name: str = "default", ttl: float = 3600.0,
                  max_size: int = 1000):
    """方法缓存装饰器"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # 包含实例信息生成缓存键
            instance_id = id(self)
            cache_key = get_cache_key(func.__name__, instance_id, *args, **kwargs)
            
            # 尝试从缓存获取
            cache = _global_cache_manager.get_cache(cache_name, max_size)
            cached_result = cache.get(cache_key)
            
            if cached_result is not None:
                return cached_result
            
            # 执行方法并缓存结果
            result = func(self, *args, **kwargs)
            cache.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


class CacheStats:
    """缓存统计信息"""
    
    @staticmethod
    def get_all_stats() -> Dict[str, Any]:
        """获取所有缓存统计"""
        return _global_cache_manager.get_stats()
    
    @staticmethod
    def get_cache_stats(cache_name: str) -> Dict[str, Any]:
        """获取指定缓存统计"""
        cache = _global_cache_manager.get_cache(cache_name)
        return cache.get_stats()
    
    @staticmethod
    def clear_cache(cache_name: str):
        """清空指定缓存"""
        _global_cache_manager.clear_cache(cache_name)
    
    @staticmethod
    def clear_all():
        """清空所有缓存"""
        _global_cache_manager.clear_all()
    
    @staticmethod
    def cleanup_expired():
        """清理过期缓存"""
        _global_cache_manager.cleanup_expired()


# 便捷函数
def cache_get(cache_name: str, key: str) -> Optional[Any]:
    """获取缓存值"""
    return _global_cache_manager.get(cache_name, key)


def cache_set(cache_name: str, key: str, value: Any, ttl: Optional[float] = None):
    """设置缓存值"""
    _global_cache_manager.set(cache_name, key, value, ttl)


def cache_delete(cache_name: str, key: str) -> bool:
    """删除缓存条目"""
    return _global_cache_manager.delete(cache_name, key)
