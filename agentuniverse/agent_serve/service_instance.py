# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/1/27 10:30
# @Author  : Auto
# @Email   : auto@example.com
# @Note    : 优化错误信息处理，添加详细的错误描述和解决建议

from .service import Service
from .service_manager import ServiceManager
from agentuniverse.base.exception import ServiceNotFoundError


class ServiceInstance(object):
    """A service wrapper class, which should be directly called in project
    instead of Service class."""

    def __init__(self, service_code: str):
        """Initialize a service instance. Raise an ServiceNotFoundError when
        service code can't be found by service manager.

        Args:
            service_code (`str`):
                Unique code of the service.
        """
        self.__service_code = service_code
        service_manager: ServiceManager = ServiceManager()
        self.__service: Service = service_manager.get_instance_obj(
            service_code
        )
        if self.__service is None:
            # 获取可用服务列表
            available_services = list(service_manager.get_instance_dict().keys()) if hasattr(service_manager, 'get_instance_dict') else []
            
            raise ServiceNotFoundError(
                service_code=service_code,
                available_services=available_services,
                details={
                    "service_manager_type": type(service_manager).__name__,
                    "total_services": len(available_services)
                },
                original_exception=None
            )

    def run(self, **kwargs) -> str:
        """Call the service run."""
        return self.__service.run(**kwargs)
