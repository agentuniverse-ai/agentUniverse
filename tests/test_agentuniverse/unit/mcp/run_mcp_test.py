#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接运行的 MCP 测试脚本，验证 ManagedExitStack、MCPSessionManager、MCPTool 的
同步和异步路径。

运行: python tests/test_agentuniverse/unit/mcp/run_mcp_test.py
"""
import asyncio
import os
import sys
import threading
import traceback

PYTHON = sys.executable
SERVER_SCRIPT = os.path.join(os.path.dirname(__file__), "mock_mcp_server.py")


def stdio_connect_args() -> dict:
    return {
        "transport": "stdio",
        "command": PYTHON,
        "args": [SERVER_SCRIPT],
    }


passed = 0
failed = 0


def run_test(name, fn):
    global passed, failed
    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"{'='*60}")
    try:
        fn()
        passed += 1
        print(f"\n  ✅ PASSED")
    except Exception:
        failed += 1
        print(f"\n  ❌ FAILED")
        traceback.print_exc()


# =========================================================================
#  Test 1: ManagedExitStack 基础能力
# =========================================================================

def test_managed_exit_stack():
    from mcp import StdioServerParameters, stdio_client, ClientSession
    from agentuniverse.base.context.mcp_session_manager import ManagedExitStack

    print("  创建 ManagedExitStack ...")
    stack = ManagedExitStack()

    try:
        print("  通过 stdio 连接 mock server ...")
        params = StdioServerParameters(
            command=PYTHON,
            args=[SERVER_SCRIPT],
            env={"PATH": os.environ.get("PATH", "")},
        )
        read, write = stack.enter_async_context(stdio_client(params))
        session = stack.enter_async_context(ClientSession(read, write))
        stack.run_async(session.initialize)
        print("  连接成功，session 已初始化")

        print("\n  调用 echo tool ...")
        result = stack.run_async(session.call_tool, "echo", {"message": "hello from stack"})
        text = result.content[0].text
        print(f"  结果: {text}")
        assert "Echo: hello from stack" in text

        print("\n  调用 add tool ...")
        result = stack.run_async(session.call_tool, "add", {"a": 17, "b": 25})
        text = result.content[0].text
        print(f"  结果: {text}")
        assert "42" in text

    finally:
        print("\n  关闭 stack ...")
        stack.close()
        print("  stack 已关闭")


# =========================================================================
#  Test 2: MCPSessionManager 同步连接 + session 缓存
# =========================================================================

def test_session_manager_sync():
    from agentuniverse.base.context.mcp_session_manager import MCPSessionManager

    mgr = MCPSessionManager()
    mgr.init_session()

    try:
        print("  同步获取 session (首次，会建立连接) ...")
        s1 = mgr.get_mcp_server_session(server_name="sync_test", **stdio_connect_args())
        print(f"  session 对象: {s1}")

        print("\n  再次获取同名 session (应命中缓存) ...")
        s2 = mgr.get_mcp_server_session(server_name="sync_test", **stdio_connect_args())
        print(f"  同一个对象? {s1 is s2}")
        assert s1 is s2, "缓存未生效"

        print("\n  通过 session 调用 echo tool ...")
        result = mgr.managed_stack.run_async(s1.call_tool, "echo", {"message": "session manager sync"})
        text = result.content[0].text
        print(f"  结果: {text}")
        assert "Echo: session manager sync" in text

    finally:
        print("\n  close_session ...")
        mgr.close_session()
        print("  已关闭")


# =========================================================================
#  Test 3: MCPSessionManager 异步连接
# =========================================================================

def test_session_manager_async():
    from agentuniverse.base.context.mcp_session_manager import MCPSessionManager

    mgr = MCPSessionManager()
    mgr.init_session()

    try:
        async def _run():
            print("  异步获取 session ...")
            session = await mgr.get_mcp_server_session_async(
                server_name="async_test", **stdio_connect_args()
            )
            print(f"  session 对象: {session}")

            print("\n  异步调用 add tool ...")
            result = await asyncio.to_thread(
                mgr.managed_stack.run_async,
                session.call_tool, "add", {"a": 100, "b": 200},
            )
            text = result.content[0].text
            print(f"  结果: {text}")
            assert "300" in text

        asyncio.run(_run())

    finally:
        print("\n  close_session ...")
        mgr.close_session()
        print("  已关闭")


# =========================================================================
#  Test 4: save / recover 跨线程共享 session
# =========================================================================

def test_save_recover_cross_thread():
    from agentuniverse.base.context.mcp_session_manager import MCPSessionManager

    mgr = MCPSessionManager()
    mgr.init_session()

    try:
        print("  主线程: 建立连接 ...")
        session = mgr.get_mcp_server_session(server_name="shared_srv", **stdio_connect_args())
        print(f"  主线程 session id: {id(session)}")

        print("\n  主线程: save_mcp_session ...")
        saved = mgr.save_mcp_session()
        print(f"  saved keys: {list(saved.keys())}")

        worker_results = {}
        worker_error = [None]

        def worker():
            try:
                mgr.recover_mcp_session(**saved)
                s = mgr.mcp_session_dict.get("shared_srv")
                worker_results["same_session"] = s is session
                worker_results["session_id"] = id(s)

                # 子线程通过共享 session 调用 tool
                result = mgr.managed_stack.run_async(
                    s.call_tool, "echo", {"message": "from worker thread"}
                )
                worker_results["text"] = result.content[0].text
            except Exception as e:
                worker_error[0] = e

        print("  启动子线程 ...")
        t = threading.Thread(target=worker)
        t.start()
        t.join(timeout=30)

        if worker_error[0]:
            raise worker_error[0]

        print(f"  子线程 session id: {worker_results['session_id']}")
        print(f"  是同一个 session? {worker_results['same_session']}")
        print(f"  子线程调用结果: {worker_results['text']}")
        assert worker_results["same_session"]
        assert "Echo: from worker thread" in worker_results["text"]

    finally:
        print("\n  主线程: close_session ...")
        mgr.close_session()
        print("  已关闭")


# =========================================================================
#  Test 5: MCPTempClient 获取 tool 元信息
# =========================================================================

def test_temp_client():
    from agentuniverse.base.context.mcp_session_manager import MCPTempClient

    print("  使用 MCPTempClient (with 语句) 连接 mock server ...")
    with MCPTempClient(stdio_connect_args()) as client:
        tools_list = client.list_tools()
        names = [t.name for t in tools_list.tools]
        print(f"  获取到的 tool 列表: {names}")
        for t in tools_list.tools:
            print(f"    - {t.name}: {t.description}")
        assert "echo" in names
        assert "add" in names
    print("  MCPTempClient 已自动关闭")


# =========================================================================
#  Test 6: MCPTool.execute 同步调用
# =========================================================================

def test_mcp_tool_sync():
    from agentuniverse.agent.action.tool.mcp_tool import MCPTool
    from agentuniverse.base.context.mcp_session_manager import MCPSessionManager

    mgr = MCPSessionManager()
    mgr.init_session()

    try:
        tool = MCPTool(
            name="test__echo",
            server_name="tool_sync_srv",
            transport="stdio",
            command=PYTHON,
            args=[SERVER_SCRIPT],
            origin_tool_name="echo",
            input_keys=["message"],
            description="Test echo tool",
            args_model_schema={
                "type": "object",
                "properties": {"message": {"type": "string"}},
                "required": ["message"],
            },
        )
        print(f"  创建 MCPTool: name={tool.name}, tool_name={tool.tool_name}")

        print("\n  调用 tool.execute(message='sync execute test') ...")
        result = tool.execute(message="sync execute test")
        text = result.content[0].text
        print(f"  结果: {text}")
        assert "Echo: sync execute test" in text

        print("\n  再创建一个 add tool ...")
        add_tool = MCPTool(
            name="test__add",
            server_name="tool_sync_srv",  # 同一个 server_name，应复用 session
            transport="stdio",
            command=PYTHON,
            args=[SERVER_SCRIPT],
            origin_tool_name="add",
            input_keys=["a", "b"],
            description="Test add tool",
            args_model_schema={
                "type": "object",
                "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}},
                "required": ["a", "b"],
            },
        )
        print("  调用 add_tool.execute(a=99, b=1) ...")
        result = add_tool.execute(a=99, b=1)
        text = result.content[0].text
        print(f"  结果: {text}")
        assert "100" in text

        print(f"\n  当前缓存的 session: {list(mgr.mcp_session_dict.keys())}")

    finally:
        mgr.close_session()
        print("  已关闭")


# =========================================================================
#  Test 7: MCPTool.async_execute 异步调用
# =========================================================================

def test_mcp_tool_async():
    from agentuniverse.agent.action.tool.mcp_tool import MCPTool
    from agentuniverse.base.context.mcp_session_manager import MCPSessionManager

    mgr = MCPSessionManager()
    mgr.init_session()

    try:
        echo_tool = MCPTool(
            name="test__echo_async",
            server_name="tool_async_srv",
            transport="stdio",
            command=PYTHON,
            args=[SERVER_SCRIPT],
            origin_tool_name="echo",
            input_keys=["message"],
            description="Test echo tool (async)",
            args_model_schema={
                "type": "object",
                "properties": {"message": {"type": "string"}},
                "required": ["message"],
            },
        )

        add_tool = MCPTool(
            name="test__add_async",
            server_name="tool_async_srv",  # 同 server，应复用
            transport="stdio",
            command=PYTHON,
            args=[SERVER_SCRIPT],
            origin_tool_name="add",
            input_keys=["a", "b"],
            description="Test add tool (async)",
            args_model_schema={
                "type": "object",
                "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}},
                "required": ["a", "b"],
            },
        )

        async def _run():
            print("  异步调用 echo_tool.async_execute(message='async execute test') ...")
            result = await echo_tool.async_execute(message="async execute test")
            text = result.content[0].text
            print(f"  结果: {text}")
            assert "Echo: async execute test" in text

            print("\n  异步调用 add_tool.async_execute(a=50, b=50) ...")
            result = await add_tool.async_execute(a=50, b=50)
            text = result.content[0].text
            print(f"  结果: {text}")
            assert "100" in text

            print(f"\n  当前缓存的 session: {list(mgr.mcp_session_dict.keys())}")
            print(f"  两个 tool 共享同一个 session? "
                  f"{'是' if len(mgr.mcp_session_dict) == 1 else '否'}")

        asyncio.run(_run())

    finally:
        mgr.close_session()
        print("  已关闭")


# =========================================================================
#  Main
# =========================================================================

if __name__ == "__main__":
    print(f"Mock MCP Server: {SERVER_SCRIPT}")
    print(f"Python: {PYTHON}")

    run_test("1. ManagedExitStack 基础连接 + 调用", test_managed_exit_stack)
    run_test("2. MCPSessionManager 同步连接 + 缓存", test_session_manager_sync)
    run_test("3. MCPSessionManager 异步连接", test_session_manager_async)
    run_test("4. save/recover 跨线程共享 session", test_save_recover_cross_thread)
    run_test("5. MCPTempClient 获取 tool 元信息", test_temp_client)
    run_test("6. MCPTool.execute 同步调用", test_mcp_tool_sync)
    run_test("7. MCPTool.async_execute 异步调用", test_mcp_tool_async)

    print(f"\n{'='*60}")
    print(f"  总计: {passed + failed} | 通过: {passed} | 失败: {failed}")
    print(f"{'='*60}")
    sys.exit(1 if failed else 0)
