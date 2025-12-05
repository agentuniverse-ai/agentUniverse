# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Server Application Entry Point
服务器应用程序入口点

This module provides the main entry point for starting the Simple Q&A Agent web server.
此模块提供启动简单问答智能体Web服务器的主入口点。

Usage / 使用方法:
    python bootstrap/intelligence/server_application.py

The server will start on http://localhost:8888 by default.
服务器将默认在 http://localhost:8888 启动。
"""

from agentuniverse.agent_serve.web.web_booster import start_web_server
from agentuniverse.base.agentuniverse import AgentUniverse


class ServerApplication:
    """
    Server application class for the Simple Q&A Agent.
    简单问答智能体的服务器应用程序类。

    This class initializes the agentUniverse framework and starts the web server.
    此类初始化 agentUniverse 框架并启动Web服务器。
    """

    @classmethod
    def start(cls):
        """
        Start the application by initializing agentUniverse and launching the web server.
        通过初始化 agentUniverse 并启动Web服务器来启动应用程序。

        Steps / 步骤:
        1. Initialize agentUniverse framework (loads all components from config)
           初始化 agentUniverse 框架（从配置加载所有组件）
        2. Start the web server to handle HTTP requests
           启动Web服务器以处理HTTP请求
        """
        # Initialize agentUniverse - this scans and registers all components
        # 初始化 agentUniverse - 扫描并注册所有组件
        AgentUniverse().start()

        # Start the web server - provides REST API endpoints for agent interaction
        # 启动Web服务器 - 提供用于智能体交互的REST API端点
        start_web_server()


if __name__ == "__main__":
    # Entry point when running this file directly
    # 直接运行此文件时的入口点
    ServerApplication.start()
