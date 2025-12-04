#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/04 14:00
# @Author  : kaichuan
# @FileName: __init__.py
"""Context synchronization module for agentUniverse.

This module provides synchronization between Knowledge and Context systems,
enabling dynamic knowledge updates with conflict resolution.
"""

from agentuniverse.agent.context.sync.knowledge_context_synchronizer import (
    KnowledgeContextSynchronizer,
)

__all__ = [
    'KnowledgeContextSynchronizer',
]
