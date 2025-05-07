# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/1/6 17:21
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: au_trace_context.py

import threading
import uuid
from typing import Optional


class AuTraceContext:
    def __init__(self, session_id: Optional[str] = None,
                 trace_id: Optional[str] = None,
                 span_id: Optional[str] = None):
        self._session_id = session_id
        self._trace_id = trace_id or self._generate_id()
        self._span_id = span_id or '0'
        self._span_id_counter = 0
        self._lock = threading.Lock()

    @classmethod
    def new_context(cls):
        return cls()

    @staticmethod
    def _generate_id() -> str:
        return uuid.uuid4().hex

    @property
    def session_id(self) -> str:
        return self._session_id

    @property
    def trace_id(self) -> str:
        return self._trace_id

    @property
    def span_id(self) -> str:
        return self._span_id

    def set_session_id(self, session_id: str):
        self._session_id = session_id

    def set_trace_id(self, trace_id: str):
        self._trace_id = trace_id

    def set_span_id(self, span_id: str):
        self._span_id = span_id

    def gen_child_span_id(self) -> str:
        with self._lock:
            child_span_id = self.span_id + '.' + str(self._span_id_counter)
            self._span_id_counter += 1
            return child_span_id


    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "trace_id": self.trace_id,
            "span_id": self.span_id
        }

    def __str__(self):
        return f"Context(session_id={self.session_id}, trace_id={self.trace_id}, span_id={self.span_id})"

    def __repr__(self):
        return self.__str__()
