# -*- coding:utf-8 -*-
"""
审计日志相关逻辑
"""
from .models import ConfigAuditLog, Config


# class AuditObserver:
#     def notify(self, action: str, config: Config, operator: str, detail: str = None):
#         pass


class AuditObserver:
    def __init__(self, session_maker):
        self.session_maker = session_maker

    def notify(self, action: str, config: Config, operator: str, detail: str = None):
        session = self.session_maker()
        log = ConfigAuditLog(
            config_id=config.id,
            tenant_id=config.tenant_id,
            namespace=config.namespace,
            operator=operator,
            action=action,
            detail=detail
        )
        session.add(log)
        session.commit()
