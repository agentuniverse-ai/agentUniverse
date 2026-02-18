#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接运行的 MCP HTTP 测试脚本，验证 ManagedExitStack、MCPSessionManager、MCPTool 的
同步和异步路径在 streamable-http 和 SSE 两种 HTTP 传输方式下的表现。

运行: python tests/test_agentuniverse/unit/mcp/run_mcp_http_test.py
"""
import asyncio
import os
import signal
import subprocess
import sys
import threading
import time
import traceback
import urllib.request
import urllib.error

PYTHON = sys.executable
HTTP_SERVER_SCRIPT = os.path.join(os.path.dirname(__file__), "mock_mcp_http_server.py")

STREAMABLE_HTTP_HOST = "127.0.0.1"
STREAMABLE_HTTP_PORT = 18765
STREAMABLE_HTTP_URL = f"http://{STREAMABLE_HTTP_HOST}:{STREAMABLE_HTTP_PORT}/mcp"

SSE_HOST = "127.0.0.1"
SSE_PORT = 18766
SSE_URL = f"http://{SSE_HOST}:{SSE_PORT}/sse"


# ---------------------------------------------------------------------------
# Server lifecycle helpers
# ---------------------------------------------------------------------------

def wait_for_server(proc: subprocess.Popen, host: str, port: int, timeout: float = 20):
    """Wait until the HTTP server is accepting and responding to requests.

    A TCP port check alone is insufficient — uvicorn may bind the port before
    the ASGI application is fully initialised, leading to 502 errors.
    This function sends an actual HTTP GET and treats *any* HTTP response
    (even 404/405) as "server is ready".
    """
    url = f"http://{host}:{port}/"
    deadline = time.time() + timeout
    while time.time() < deadline:
        # Ensure the subprocess hasn't crashed
        if proc.poll() is not None:
            raise RuntimeError(
                f"Server process exited unexpectedly with code {proc.returncode}"
            )
        try:
            urllib.request.urlopen(url, timeout=2)
            return  # 2xx — ready
        except urllib.error.HTTPError:
            return  # 4xx/5xx — still means the ASGI app is responding
        except (urllib.error.URLError, OSError):
            time.sleep(0.5)
    raise RuntimeError(f"Server on {host}:{port} did not become ready within {timeout}s")


def start_server(transport: str, host: str, port: int) -> subprocess.Popen:
    proc = subprocess.Popen(
        [
            PYTHON, HTTP_SERVER_SCRIPT,
            "--transport", transport,
            "--host", host,
            "--port", str(port),
        ],
        # Use DEVNULL to prevent pipe buffer saturation (uvicorn logs a lot)
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    wait_for_server(proc, host, port)
    return proc


def stop_server(proc: subprocess.Popen):
    if proc.poll() is None:
        proc.send_signal(signal.SIGTERM)
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=3)


def streamable_http_connect_args() -> dict:
    return {"transport": "streamable_http", "url": STREAMABLE_HTTP_URL}


def sse_connect_args() -> dict:
    return {"transport": "sse", "url": SSE_URL}


# ---------------------------------------------------------------------------
# Test runner
# ---------------------------------------------------------------------------

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
#  Test 1: ManagedExitStack — streamable-http 基础连接
# =========================================================================

def test_managed_exit_stack_streamable_http():
    from mcp import ClientSession
    from mcp.client.streamable_http import streamablehttp_client
    from agentuniverse.base.context.mcp_session_manager import ManagedExitStack

    print("  创建 ManagedExitStack ...")
    stack = ManagedExitStack()

    try:
        print(f"  通过 streamable-http 连接 {STREAMABLE_HTTP_URL} ...")
        read, write, _ = stack.enter_async_context(
            streamablehttp_client(STREAMABLE_HTTP_URL)
        )
        session = stack.enter_async_context(ClientSession(read, write))
        stack.run_async(session.initialize)
        print("  连接成功，session 已初始化")

        print("\n  调用 echo tool ...")
        result = stack.run_async(session.call_tool, "echo", {"message": "hello from http stack"})
        text = result.content[0].text
        print(f"  结果: {text}")
        assert "Echo: hello from http stack" in text

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
#  Test 2: ManagedExitStack — SSE 基础连接
# =========================================================================

def test_managed_exit_stack_sse():
    from mcp import ClientSession
    from mcp.client.sse import sse_client
    from agentuniverse.base.context.mcp_session_manager import ManagedExitStack

    print("  创建 ManagedExitStack ...")
    stack = ManagedExitStack()

    try:
        print(f"  通过 SSE 连接 {SSE_URL} ...")
        read, write = stack.enter_async_context(sse_client(SSE_URL))
        session = stack.enter_async_context(ClientSession(read, write))
        stack.run_async(session.initialize)
        print("  连接成功，session 已初始化")

        print("\n  调用 echo tool ...")
        result = stack.run_async(session.call_tool, "echo", {"message": "hello from sse"})
        text = result.content[0].text
        print(f"  结果: {text}")
        assert "Echo: hello from sse" in text

        print("\n  调用 add tool ...")
        result = stack.run_async(session.call_tool, "add", {"a": 7, "b": 8})
        text = result.content[0].text
        print(f"  结果: {text}")
        assert "15" in text

    finally:
        print("\n  关闭 stack ...")
        stack.close()
        print("  stack 已关闭")


# =========================================================================
#  Test 3: MCPSessionManager — streamable-http 同步连接 + 缓存
# =========================================================================

def test_session_manager_sync_http():
    from agentuniverse.base.context.mcp_session_manager import MCPSessionManager

    mgr = MCPSessionManager()
    mgr.init_session()

    try:
        print("  同步获取 session (首次，会建立连接) ...")
        s1 = mgr.get_mcp_server_session(server_name="http_sync_test", **streamable_http_connect_args())
        print(f"  session 对象: {s1}")

        print("\n  再次获取同名 session (应命中缓存) ...")
        s2 = mgr.get_mcp_server_session(server_name="http_sync_test", **streamable_http_connect_args())
        print(f"  同一个对象? {s1 is s2}")
        assert s1 is s2, "缓存未生效"

        print("\n  通过 session 调用 echo tool ...")
        result = mgr.managed_stack.run_async(s1.call_tool, "echo", {"message": "http session manager sync"})
        text = result.content[0].text
        print(f"  结果: {text}")
        assert "Echo: http session manager sync" in text

    finally:
        print("\n  close_session ...")
        mgr.close_session()
        print("  已关闭")


# =========================================================================
#  Test 4: MCPSessionManager — SSE 同步连接 + 缓存
# =========================================================================

def test_session_manager_sync_sse():
    from agentuniverse.base.context.mcp_session_manager import MCPSessionManager

    mgr = MCPSessionManager()
    mgr.init_session()

    try:
        print("  同步获取 SSE session ...")
        s1 = mgr.get_mcp_server_session(server_name="sse_sync_test", **sse_connect_args())
        print(f"  session 对象: {s1}")

        print("\n  再次获取 (应命中缓存) ...")
        s2 = mgr.get_mcp_server_session(server_name="sse_sync_test", **sse_connect_args())
        assert s1 is s2, "缓存未生效"

        print("\n  调用 add tool ...")
        result = mgr.managed_stack.run_async(s1.call_tool, "add", {"a": 100, "b": 200})
        text = result.content[0].text
        print(f"  结果: {text}")
        assert "300" in text

    finally:
        mgr.close_session()
        print("  已关闭")


# =========================================================================
#  Test 5: MCPSessionManager — streamable-http 异步连接
# =========================================================================

def test_session_manager_async_http():
    from agentuniverse.base.context.mcp_session_manager import MCPSessionManager

    mgr = MCPSessionManager()
    mgr.init_session()

    try:
        async def _run():
            print("  异步获取 streamable-http session ...")
            session = await mgr.get_mcp_server_session_async(
                server_name="http_async_test", **streamable_http_connect_args()
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
#  Test 6: save/recover 跨线程共享 — streamable-http
# =========================================================================

def test_save_recover_cross_thread_http():
    from agentuniverse.base.context.mcp_session_manager import MCPSessionManager

    mgr = MCPSessionManager()
    mgr.init_session()

    try:
        print("  主线程: 建立 HTTP 连接 ...")
        session = mgr.get_mcp_server_session(server_name="http_shared_srv", **streamable_http_connect_args())
        print(f"  主线程 session id: {id(session)}")

        print("\n  主线程: save_mcp_session ...")
        saved = mgr.save_mcp_session()
        print(f"  saved keys: {list(saved.keys())}")

        worker_results = {}
        worker_error = [None]

        def worker():
            try:
                mgr.recover_mcp_session(**saved)
                s = mgr.mcp_session_dict.get("http_shared_srv")
                worker_results["same_session"] = s is session
                worker_results["session_id"] = id(s)

                result = mgr.managed_stack.run_async(
                    s.call_tool, "echo", {"message": "from http worker thread"}
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
        assert "Echo: from http worker thread" in worker_results["text"]

    finally:
        print("\n  主线程: close_session ...")
        mgr.close_session()
        print("  已关闭")


# =========================================================================
#  Test 7: MCPTempClient — HTTP transports
# =========================================================================

def test_temp_client_http():
    from agentuniverse.base.context.mcp_session_manager import MCPTempClient

    print("  使用 MCPTempClient 连接 streamable-http server ...")
    with MCPTempClient(streamable_http_connect_args()) as client:
        tools_list = client.list_tools()
        names = [t.name for t in tools_list.tools]
        print(f"  获取到的 tool 列表: {names}")
        for t in tools_list.tools:
            print(f"    - {t.name}: {t.description}")
        assert "echo" in names
        assert "add" in names
    print("  MCPTempClient 已自动关闭")

    print("\n  使用 MCPTempClient 连接 SSE server ...")
    with MCPTempClient(sse_connect_args()) as client:
        tools_list = client.list_tools()
        names = [t.name for t in tools_list.tools]
        print(f"  获取到的 tool 列表: {names}")
        assert "echo" in names
        assert "add" in names
    print("  MCPTempClient 已自动关闭")


# =========================================================================
#  Test 8: MCPTool.execute — streamable-http 同步调用
# =========================================================================

def test_mcp_tool_sync_http():
    from agentuniverse.agent.action.tool.mcp_tool import MCPTool
    from agentuniverse.base.context.mcp_session_manager import MCPSessionManager

    mgr = MCPSessionManager()
    mgr.init_session()

    try:
        tool = MCPTool(
            name="http_test__echo",
            server_name="http_tool_sync_srv",
            transport="streamable_http",
            url=STREAMABLE_HTTP_URL,
            origin_tool_name="echo",
            input_keys=["message"],
            description="Test echo tool (http)",
            args_model_schema={
                "type": "object",
                "properties": {"message": {"type": "string"}},
                "required": ["message"],
            },
        )
        print(f"  创建 MCPTool: name={tool.name}, transport={tool.transport}")

        print("\n  调用 tool.execute(message='http sync execute test') ...")
        result = tool.execute(message="http sync execute test")
        text = result.content[0].text
        print(f"  结果: {text}")
        assert "Echo: http sync execute test" in text

        print("\n  再创建一个 add tool (同 server_name，应复用 session) ...")
        add_tool = MCPTool(
            name="http_test__add",
            server_name="http_tool_sync_srv",
            transport="streamable_http",
            url=STREAMABLE_HTTP_URL,
            origin_tool_name="add",
            input_keys=["a", "b"],
            description="Test add tool (http)",
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
#  Test 9: MCPTool.async_execute — streamable-http 异步调用
# =========================================================================

def test_mcp_tool_async_http():
    from agentuniverse.agent.action.tool.mcp_tool import MCPTool
    from agentuniverse.base.context.mcp_session_manager import MCPSessionManager

    mgr = MCPSessionManager()
    mgr.init_session()

    try:
        echo_tool = MCPTool(
            name="http_test__echo_async",
            server_name="http_tool_async_srv",
            transport="streamable_http",
            url=STREAMABLE_HTTP_URL,
            origin_tool_name="echo",
            input_keys=["message"],
            description="Test echo tool (http async)",
            args_model_schema={
                "type": "object",
                "properties": {"message": {"type": "string"}},
                "required": ["message"],
            },
        )

        add_tool = MCPTool(
            name="http_test__add_async",
            server_name="http_tool_async_srv",
            transport="streamable_http",
            url=STREAMABLE_HTTP_URL,
            origin_tool_name="add",
            input_keys=["a", "b"],
            description="Test add tool (http async)",
            args_model_schema={
                "type": "object",
                "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}},
                "required": ["a", "b"],
            },
        )

        async def _run():
            print("  异步调用 echo_tool.async_execute ...")
            result = await echo_tool.async_execute(message="http async execute test")
            text = result.content[0].text
            print(f"  结果: {text}")
            assert "Echo: http async execute test" in text

            print("\n  异步调用 add_tool.async_execute ...")
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
#  Test 10: MCPTool.execute — SSE 同步调用
# =========================================================================

def test_mcp_tool_sync_sse():
    from agentuniverse.agent.action.tool.mcp_tool import MCPTool
    from agentuniverse.base.context.mcp_session_manager import MCPSessionManager

    mgr = MCPSessionManager()
    mgr.init_session()

    try:
        tool = MCPTool(
            name="sse_test__echo",
            server_name="sse_tool_sync_srv",
            transport="sse",
            url=SSE_URL,
            origin_tool_name="echo",
            input_keys=["message"],
            description="Test echo tool (sse)",
            args_model_schema={
                "type": "object",
                "properties": {"message": {"type": "string"}},
                "required": ["message"],
            },
        )
        print(f"  创建 MCPTool: name={tool.name}, transport={tool.transport}")

        print("\n  调用 tool.execute(message='sse sync execute test') ...")
        result = tool.execute(message="sse sync execute test")
        text = result.content[0].text
        print(f"  结果: {text}")
        assert "Echo: sse sync execute test" in text

    finally:
        mgr.close_session()
        print("  已关闭")


# =========================================================================
#  Main
# =========================================================================

if __name__ == "__main__":
    print(f"Mock MCP HTTP Server: {HTTP_SERVER_SCRIPT}")
    print(f"Python: {PYTHON}")

    # --- Start servers ---
    print(f"\n{'='*60}")
    print(f"  启动 HTTP 服务器")
    print(f"{'='*60}")

    http_proc = None
    sse_proc = None

    try:
        print(f"  启动 streamable-http server on :{STREAMABLE_HTTP_PORT} ...")
        http_proc = start_server("streamable-http", STREAMABLE_HTTP_HOST, STREAMABLE_HTTP_PORT)
        print(f"  streamable-http server 已启动 (pid={http_proc.pid})")

        print(f"  启动 SSE server on :{SSE_PORT} ...")
        sse_proc = start_server("sse", SSE_HOST, SSE_PORT)
        print(f"  SSE server 已启动 (pid={sse_proc.pid})")

        # --- Run tests ---
        run_test("1.  ManagedExitStack — streamable-http 基础连接", test_managed_exit_stack_streamable_http)
        run_test("2.  ManagedExitStack — SSE 基础连接", test_managed_exit_stack_sse)
        run_test("3.  MCPSessionManager — streamable-http 同步连接 + 缓存", test_session_manager_sync_http)
        run_test("4.  MCPSessionManager — SSE 同步连接 + 缓存", test_session_manager_sync_sse)
        run_test("5.  MCPSessionManager — streamable-http 异步连接", test_session_manager_async_http)
        run_test("6.  save/recover 跨线程共享 — streamable-http", test_save_recover_cross_thread_http)
        run_test("7.  MCPTempClient — HTTP transports", test_temp_client_http)
        run_test("8.  MCPTool.execute — streamable-http 同步调用", test_mcp_tool_sync_http)
        run_test("9.  MCPTool.async_execute — streamable-http 异步调用", test_mcp_tool_async_http)
        run_test("10. MCPTool.execute — SSE 同步调用", test_mcp_tool_sync_sse)

    finally:
        # --- Stop servers ---
        print(f"\n{'='*60}")
        print(f"  停止 HTTP 服务器")
        print(f"{'='*60}")
        if http_proc:
            stop_server(http_proc)
            print(f"  streamable-http server 已停止")
        if sse_proc:
            stop_server(sse_proc)
            print(f"  SSE server 已停止")

    print(f"\n{'='*60}")
    print(f"  总计: {passed + failed} | 通过: {passed} | 失败: {failed}")
    print(f"{'='*60}")
    sys.exit(1 if failed else 0)
