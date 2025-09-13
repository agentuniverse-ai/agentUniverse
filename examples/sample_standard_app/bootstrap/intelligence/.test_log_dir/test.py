import requests
import json
import time

base_url = "http://127.0.0.1:8888" # 确保是 8888 端口
headers = {"Content-Type": "application/json"} # POST 请求通常需要这个头部

print("--- 测试 Flask 服务器 (8888 端口) 的实际 API 端点 ---")

# 1. 测试 /echo (GET)
print("\n--- 测试 /echo (GET) ---")
try:
    response = requests.get(f"{base_url}/echo")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except requests.exceptions.ConnectionError:
    print("无法连接到服务器。请确保 server_application.py 正在运行。")
except Exception as e:
    print(f"发生错误: {e}")

# 2. 测试 /liveness (GET)
print("\n--- 测试 /liveness (GET) ---")
try:
    response = requests.get(f"{base_url}/liveness")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json() if response.text else 'No content'}")
except requests.exceptions.ConnectionError:
    print("无法连接到服务器。请确保 server_application.py 正在运行。")
except json.JSONDecodeError:
    print(f"响应不是有效的 JSON: {response.text}")
except Exception as e:
    print(f"发生错误: {e}")

# 3. 测试 /service_run (POST) - 同步调用
print("\n--- 测试 /service_run (POST) ---")
# 注意：'default_agent' 或其他真实的agent_id需要根据您的项目配置来。
# 如果没有实际的agent，这里会返回ServiceNotFoundError，这是正常行为。
payload_service_run = {
    "service_id": "default_agent", # 替换为你项目中实际存在的 Agent ID
    "params": {
        "input": "请问您是哪个 AgentUniverse 服务器？"
    },
    "saved": False
}
try:
    response = requests.post(f"{base_url}/service_run", headers=headers, data=json.dumps(payload_service_run))
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json() if response.text else 'No content'}")
except requests.exceptions.ConnectionError:
    print("无法连接到服务器。请确保 server_application.py 正在运行。")
except json.JSONDecodeError:
    print(f"响应不是有效的 JSON: {response.text}")
except Exception as e:
    print(f"发生错误: {e}")

# 4. 测试 /service_run_async (POST) - 异步调用
print("\n--- 测试 /service_run_async (POST) ---")
async_request_id = None
payload_service_async = {
    "service_id": "default_agent", # 替换为你项目中实际存在的 Agent ID
    "params": {
        "input": "这是一个异步调用测试。"
    },
    "saved": True
}
try:
    response = requests.post(f"{base_url}/service_run_async", headers=headers, data=json.dumps(payload_service_async))
    print(f"Status Code: {response.status_code}")
    json_response = response.json()
    print(f"Response: {json_response}")
    if json_response and json_response.get("success"):
        async_request_id = json_response.get("request_id")
        print(f"异步请求 ID: {async_request_id}")
    else:
        print("未能获取异步请求 ID。")
except requests.exceptions.ConnectionError:
    print("无法连接到服务器。请确保 server_application.py 正在运行。")
except json.JSONDecodeError:
    print(f"响应不是有效的 JSON: {response.text}")
except Exception as e:
    print(f"发生错误: {e}")

# 5. 测试 /service_run_result (GET) - 获取异步结果
if async_request_id:
    print("\n--- 测试 /service_run_result (GET) ---")
    # 稍等片刻，给异步任务一些执行时间
    print("等待 3 秒以获取异步结果...")
    time.sleep(3)
    try:
        # request_param 装饰器对于 GET 请求，通常会从查询参数中获取数据
        response = requests.get(f"{base_url}/service_run_result?request_id={async_request_id}")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json() if response.text else 'No content'}")
    except requests.exceptions.ConnectionError:
        print("无法连接到服务器。请确保 server_application.py 正在运行。")
    except json.JSONDecodeError:
        print(f"响应不是有效的 JSON: {response.text}")
    except Exception as e:
        print(f"发生错误: {e}")
else:
    print("\n跳过 /service_run_result 测试，因为未能获取异步请求 ID。")

# 6. 测试 /chat/completions (POST) - 遵循 OpenAI 协议
print("\n--- 测试 /chat/completions (POST, 非流式) ---")
# 同样，'default_agent' 或其他真实的agent_id需要根据您的项目配置来。
payload_chat_completions = {
    "model": "default_agent", # 替换为你项目中实际存在的 Agent ID
    "messages": [
        {"role": "user", "content": "请用一句话介绍一下AgentUniverse。"}
    ],
    "stream": False # 非流式请求
}
try:
    response = requests.post(f"{base_url}/chat/completions", headers=headers, data=json.dumps(payload_chat_completions))
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json() if response.text else 'No content'}")
except requests.exceptions.ConnectionError:
    print("无法连接到服务器。请确保 server_application.py 正在运行。")
except json.JSONDecodeError:
    print(f"响应不是有效的 JSON: {response.text}")
except Exception as e:
    print(f"发生错误: {e}")


# 7. 测试 /service_run_stream (POST) 或 /chat/completions (POST, 流式)
print("\n--- 测试 /chat/completions (POST, 流式) ---")
print("注意：此处只会打印接收到的每一行数据，直到连接关闭。")
payload_chat_stream = {
    "model": "default_agent", # 替换为你项目中实际存在的 Agent ID
    "messages": [
        {"role": "user", "content": "请详细介绍一下AgentUniverse的功能和优势。"}
    ],
    "stream": True # 流式请求
}
try:
    # stream=True 参数很重要，它让requests不会一次性下载所有内容
    with requests.post(f"{base_url}/chat/completions", headers=headers, data=json.dumps(payload_chat_stream), stream=True) as response:
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            for line in response.iter_lines(): # 逐行读取数据
                if line:
                    decoded_line = line.decode('utf-8')
                    print(f"Received: {decoded_line}")
        else:
            print(f"Error Response: {response.text}")
except requests.exceptions.ConnectionError:
    print("无法连接到服务器。请确保 server_application.py 正在运行。")
except Exception as e:
    print(f"发生错误: {e}")

