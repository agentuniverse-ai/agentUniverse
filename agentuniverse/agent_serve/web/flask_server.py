import time
import traceback
from concurrent.futures import TimeoutError

from flask import Flask, Response, g, request, make_response, \
    copy_current_request_context, jsonify
from loguru import logger
from werkzeug.exceptions import HTTPException
from werkzeug.local import LocalProxy

from agentuniverse.base.util.logging.general_logger import get_context_prefix
from agentuniverse.base.util.logging.log_type_enum import LogTypeEnum
from .request_task import RequestTask
from .web_request_task import WebRequestTask
from .thread_with_result import ThreadPoolExecutorWithReturnValue
from .web_util import request_param, service_run_queue, make_standard_response, \
    FlaskServerManager
from ..service_instance import ServiceInstance, ServiceNotFoundError
from ...base.context.context_coordinator import ContextCoordinator
from ...base.util.logging.logging_util import LOGGER

from agentuniverse.agent_serve.service_manager import ServiceManager
from examples.sample_standard_app.intelligence.db.database import init_app, get_db
import json
from datetime import datetime

# Patch original flask request so it can be dumped by loguru.
class SerializableRequest:
    def __init__(self, method, path, args, form, headers):
        self.method = method
        self.path = path
        self.args = args
        self.form = form
        self.headers = headers

    def __repr__(self):
        return f"<SerializableRequest method={self.method} path={self.path}>"


def localproxy_reduce_ex(self, protocol):
    real_obj = self._get_current_object()
    return (
        SerializableRequest,
        (real_obj.method, real_obj.path, dict(real_obj.args), dict(real_obj.form), dict(real_obj.headers)),
    )


LocalProxy.__reduce_ex__ = localproxy_reduce_ex


# log stream response
def timed_generator(generator, start_time, context_prefix):
    try:
        for data in generator:
            yield data
    finally:
        elapsed_time = time.time() - start_time
        logger.bind(
            log_type=LogTypeEnum.flask_response,
            flask_response="Stream finished",
            elapsed_time=elapsed_time,
            context_prefix=context_prefix
        ).info("Stream finished.")


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.json.ensure_ascii = False


@app.before_request
def before():
    logger.bind(
        log_type=LogTypeEnum.flask_request,
        flask_request=request,
        context_prefix=get_context_prefix()
    ).info("Before request.")
    g.start_time = time.time()


@app.after_request
def after_request(response):
    if not response.mimetype == "text/event-stream":
        logger.bind(
            log_type=LogTypeEnum.flask_response,
            flask_response=response,
            elapsed_time=time.time() - g.start_time,
            context_prefix=get_context_prefix()
        ).info("After request.")
    return response

@app.teardown_request
def teardown_resource(exception):
    """
    Clear the context
    """
    ContextCoordinator.end_context()


@app.route("/echo")
def echo():
    return 'Welcome to agentUniverse!!!'


@app.route("/liveness")
def liveness():
    return make_standard_response(success=True,
                                  result="liveness health check pass!")


@app.route("/service_run", methods=['POST'])
@request_param
def service_run(service_id: str, params: dict, saved: bool = False):
    """Synchronous invocation of an agent service.

    Request Args:
        service_id(`str`): The id of the agent service.
        params(`dict`): Json style params passed to service.
        saved(`bool`): Save the request and result into database.

    Return:
        Returns a dict containing two keys: success and result.
        success: This key holds a boolean value indicating the task was
            successfully or not.
        result: This key points to a nested dictionary that includes the
            result of the task.
    """
    try:
        params = {} if params is None else params
        request_task = RequestTask(ServiceInstance(service_id).run, saved,
                                   **params)
        with ThreadPoolExecutorWithReturnValue() as executor:
            future = executor.submit(copy_current_request_context(request_task.run))
            result = future.result(timeout=FlaskServerManager().sync_service_timeout)
    except TimeoutError:
        return make_standard_response(success=False,
                                      message="AU sync service timeout",
                                      status_code=504)

    return make_standard_response(success=True, result=result,
                                  request_id=request_task.request_id)

@app.route("/service_run_stream", methods=['POST'])
@request_param
def service_run_stream(service_id: str, params: dict, saved: bool = False):
    """Synchronous invocation of an agent service, return in stream form.

    Request Args:
        service_id(`str`): The id of the agent service.
        params(`dict`): Json style params passed to service.
        saved(`bool`): Save the request and result into database.

    Return:
        A SSE(Server-Sent Event) stream.
    """
    params = {} if params is None else params
    params['service_id'] = service_id
    params['streaming'] = True
    task = RequestTask(service_run_queue, saved, **params)
    context_prefix = get_context_prefix()
    response = Response(timed_generator(task.stream_run(), g.start_time, context_prefix), mimetype="text/event-stream")
    response.headers['X-Request-ID'] = task.request_id
    return response

@app.route("/agent/list", methods=['GET'])
def agent_list():
    try:
        service_manager = ServiceManager()
        services = service_manager.get_instance_obj_list()
        agent_list = []
        for service in services:
            if not hasattr(service, 'agent') or service.agent is None:
                continue
            agent = service.agent
            name = getattr(agent, 'name', None)
            description = service.description
            if not name:
                name = agent.agent_model.info.get("name") if hasattr(agent, 'agent_model') else None
            if name:
                # 返回 { name, service_id } 结构
                agent_list.append({
                    "agent_name": name,
                    "service_id": service.name,  # 或其他唯一标识，如 component_id
                    "description": description,
                })
        # 去重：可能多个 service 使用同一个 agent，但 service_id 不同
        return jsonify({
            "success": True,
            "data": agent_list
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Failed to fetch agent list",
            "error": str(e)
        }), 500

@app.route("/web_stream", methods=['POST'])  # 修改接口名称
@request_param
def web_stream(service_id: str, params: dict, saved: bool = True):
    """Web流式运行接口，使用新的数据库表"""
    params = {} if params is None else params
    params['service_id'] = service_id
    params['streaming'] = True

    # 使用新的 WebRequestTask
    task = WebRequestTask(service_run_queue, saved, **params)

    context_prefix = get_context_prefix()
    response = Response(timed_generator(task.stream_run(), g.start_time, context_prefix), mimetype="text/event-stream")
    response.headers['X-Request-ID'] = task.request_id
    return response

# 初始化数据库（注册关闭、初始化等钩子）
init_app(app)
@app.route('/session/list', methods=['GET'])
def sessions_list_all():
    try:
        db = get_db()

        query = '''
            SELECT 
                rt.session_id AS id,
                rt.title AS title,
                rt.service_id AS service_id
            FROM request_task rt
            INNER JOIN (
                SELECT 
                    session_id, 
                    MIN(gmt_create) AS first_created
                FROM request_task
                WHERE state = 'finished'
                  AND query IS NOT NULL
                  AND query != ''
                GROUP BY session_id
            ) first_msgs
            ON rt.session_id = first_msgs.session_id
               AND rt.gmt_create = first_msgs.first_created
            ORDER BY rt.gmt_create DESC
            LIMIT 50
        '''

        rows = db.execute(query).fetchall()

        sessions = [
            {"id": row["id"],
             "title": row["title"] or "新对话",
             "service_id": row["service_id"]}
            for row in rows
        ]
        return jsonify(sessions)

    except Exception as e:
        print(f"数据库查询错误: {e}")
        return jsonify({"error": "服务器内部错误"}), 500


@app.route('/session/update', methods=['PUT'])
def update_session():
    #利用sessionId，更新最近会话的title
    # 从 JSON 中获取 session_id 和新的 query
    data = request.get_json()
    session_id = data.get('session_id')
    new_title = data.get('title')

    if not session_id:
        return jsonify({"error": "Missing session_id in JSON body"}), 400
    if not new_title:
        return jsonify({"error": "Missing new query content"}), 400
    try:
        db = get_db()
        # 检查是否存在该会话
        cursor = db.execute(
            "SELECT 1 FROM request_task WHERE session_id = ? LIMIT 1",
            (session_id,)  # 注意这里是 (session_id,)，因为是单元素的元组
        )
        if not cursor.fetchone():
            return jsonify({"error": "Session not found"}), 404  # 错误消息也移除“no permission”
        # 更新该 session 的所有记录的 query
        db.execute(
            "UPDATE request_task SET title = ? WHERE session_id = ?",
            (new_title, session_id)
        )
        db.commit()

        return jsonify({
            "message": "Session updated successfully",
            "session_id": session_id,
            "new_query": new_title
        }), 200

    except Exception as e:
        print(f"更新会话错误: {e}")
        return jsonify({"error": "服务器内部错误"}), 500


@app.route('/session/delete', methods=['DELETE'])
def delete_session():
    # 从请求体中获取 session_id
    data = request.get_json()
    session_id = data.get('session_id') if data else None
    if not session_id:
        return jsonify({"error": "Missing session_id in JSON body"}), 400

    try:
        db = get_db()
        # 先检查是否存在
        cursor = db.execute(
            "SELECT 1 FROM request_task WHERE session_id = ? LIMIT 1",
            (session_id,)  # 注意这里是 (session_id,)
        )
        if not cursor.fetchone():
            return jsonify({"error": "Session not found"}), 404  # 错误消息也移除“no permission”

        # 删除该 session 的所有记录
        db.execute(
            "DELETE FROM request_task WHERE session_id = ?",
            (session_id,)  # 注意这里是 (session_id,)
        )
        db.commit()

        return jsonify({"message": "Session deleted successfully", "session_id": session_id}), 200

    except Exception as e:
        print(f"删除会话错误: {e}")
        return jsonify({"error": "服务器内部错误"}), 500


@app.route('/session/<session_id>/history', methods=['GET'])
def get_session_history(session_id):
    """
    获取指定 session_id 的完整聊天历史
    URL: GET /session/MRcNioQGmKH8GPw-vwm4O/history
    返回结构化消息列表，兼容前端卡片式渲染。
    """
    try:
        db = get_db()

        # 查询该 session_id 下所有 state 为 'finished' 的记录，按时间升序排列
        query = '''
                SELECT query, result, gmt_create, service_id
                FROM request_task
                WHERE session_id = ?
                  AND state = 'finished'
                  AND result IS NOT NULL
                  AND result != ''
                ORDER BY gmt_create ASC \
                '''

        rows = db.execute(query, (session_id,)).fetchall()

        if not rows:
            return jsonify([]), 200  # 没有记录返回空数组，而不是错误

        messages = []
        message_id_counter = 1  # 用于生成 msg_id

        for row in rows:
            try:
                # 直接使用 query 作为用户输入
                user_input = row["query"].strip() if row["query"] else ""
                service_id = row["service_id"]  # 新增：获取 service_id

                # 解析外层 result
                outer_result = json.loads(row["result"])
                inner_result_str = outer_result.get("result")

                if not inner_result_str:
                    continue

                # 兼容处理：inner_result_str 可能是字符串或已解析对象
                if isinstance(inner_result_str, str):
                    inner_result = json.loads(inner_result_str)
                else:
                    inner_result = inner_result_str

                # 提取AI输出
                ai_output = inner_result.get("output", "")

                # 如果 ai_output 是字典，提取 text 字段
                if isinstance(ai_output, dict):
                    ai_text = (ai_output.get("text") or "").strip()
                else:
                    ai_text = str(ai_output).strip()

                # ========== 用户消息 ==========
                if user_input:
                    user_msg_id = f"msg_{str(message_id_counter).zfill(3)}"
                    message_id_counter += 1

                    messages.append({
                        "id": user_msg_id,
                        "role": "user",
                        "content": user_input,
                        "service_id": service_id,  # ✅ 添加 service_id
                        "status": "success",
                        "gmt_create": _format_timestamp(row["gmt_create"])
                    })

                # ========== 助手消息 ==========
                if ai_text:
                    assistant_msg_id = f"msg_{str(message_id_counter).zfill(3)}"
                    message_id_counter += 1

                    messages.append({
                        "id": assistant_msg_id,
                        "role": "assistant",
                        "content": [
                            {
                                "card": "Markdown",
                                "props": {
                                    "children": ai_text,
                                    "speed": 100  # 可配置：打字速度（字符/秒）
                                }
                            }
                        ],
                        "service_id": service_id,  # ✅ 添加 service_id
                        "status": "success",
                        "gmt_create": _format_timestamp(row["gmt_create"])
                    })

            except (json.JSONDecodeError, KeyError, TypeError) as e:
                print(f"解析 result 失败: {e}, row={row}")
                continue  # 跳过解析失败的记录

        return jsonify(messages), 200

    except Exception as e:
        print(f"服务器内部错误: {e}")
        return jsonify({"error": "服务器内部错误"}), 500


# 辅助函数：标准化时间格式
def _format_timestamp(dt_str):
    """
    将数据库中的时间字符串转换为 ISO 8601 格式（带 T 和 Z）
    输入示例: '2025-09-08 21:54:51.566212'
    输出示例: '2025-09-08T21:54:51.566Z'
    """
    try:
        dt = datetime.fromisoformat(dt_str.split('.')[0])  # 忽略微秒部分
        return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    except Exception:
        return dt_str  # 若解析失败，原样返回


@app.route("/service_run_async", methods=['POST'])
@request_param
def service_run_async(service_id: str, params: dict, saved: bool = True):
    """Async invocation of an agent service, return the request id used to
    get result later.

    Request Args:
        service_id(`str`): The id of the agent service.
        params(`dict`): Json style params passed to service.
        saved(`bool`): Save the request and result into database.

    Return:
        Returns a dict containing two keys: success and result.
        success: This key holds a boolean value indicating the task was
            successfully or not.
        request_id: Stand for a single request taski, can be used in
            service_run_result api to get the result of async task.
    """
    params = {} if params is None else params
    params['service_id'] = service_id
    task = RequestTask(service_run_queue, saved, **params)
    task.async_run()
    return make_standard_response(success=True,
                                  request_id=task.request_id)


@app.route("/service_run_result", methods=['GET'])
@request_param
def service_run_result(request_id: str):
    """Get the async service result.

    Request Args:
        request_id(`str`): Request id returned by async run api.

    Return:
        Returns a dict containing two keys: success and result if request_id
        exists in database.
        success: This key holds a boolean value indicating the task was
            successfully or not.
        result: This key points to a nested dictionary that includes the
            result of the task.
    """
    data = RequestTask.query_request_state(request_id)
    if data is None:
        return make_standard_response(
            success=False,
            message=f"request {request_id} not found"
        )
    return make_standard_response(success=True, result=data,
                                  request_id=request_id)


@app.errorhandler(HTTPException)
def handle_http_exception(e):
    """A global exception handler handle flask origin http exceptions."""
    response = e.get_response()
    return response


@app.errorhandler(Exception)
def handle_exception(e):
    """A global non http exception handler"""
    LOGGER.error(traceback.format_exc())
    if isinstance(e, ServiceNotFoundError):
        return make_standard_response(success=False,
                                      message=str(e),
                                      status_code=404)
    return make_standard_response(success=False,
                                  message="Internal Server Error",
                                  status_code=500)


@app.route("/chat/completions", methods=['POST'])
@request_param
def openai_protocol_chat(model: str, messages: list):
    """
    OpenAI chat completion API.
    """
    stream = request.json.get("stream", False)
    params = {
        "service_id": model,
        "messages": messages,
        "stream": stream
    }
    if stream:
        task = RequestTask(service_run_queue, False, **params)
        context_prefix = get_context_prefix()
        response = Response(timed_generator(task.user_stream_run(), g.start_time, context_prefix), mimetype="text/event-stream")
        response.headers['X-Request-ID'] = task.request_id
        return response
    try:
        params = {} if params is None else params
        request_task = RequestTask(ServiceInstance(params.get('service_id')).run, False,
                                   **params)
        with ThreadPoolExecutorWithReturnValue() as executor:
            future = executor.submit(request_task.run)
            result = future.result(timeout=FlaskServerManager().sync_service_timeout)
    except TimeoutError:
        return make_standard_response(success=False,
                                      message="AU sync service timeout",
                                      status_code=504)
    response = make_response(result, 200)
    response.headers['X-Request-ID'] = request_task.request_id
    return response
