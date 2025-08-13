import time
import traceback
from concurrent.futures import TimeoutError
import json

from flask import Flask, Response, g, request, make_response, \
    copy_current_request_context, jsonify
from loguru import logger
from werkzeug.exceptions import HTTPException
from werkzeug.local import LocalProxy

from agentuniverse.base.util.logging.general_logger import get_context_prefix
from agentuniverse.base.util.logging.log_type_enum import LogTypeEnum
# from tests.test_agentuniverse.mock.agent_serve.mock_service_manager import ServiceManager
from .request_task import RequestTask
from .thread_with_result import ThreadPoolExecutorWithReturnValue
from .web_util import request_param, service_run_queue, make_standard_response, \
    FlaskServerManager
from ..service_instance import ServiceInstance, ServiceNotFoundError
from ...base.context.context_coordinator import ContextCoordinator
from ...base.util.logging.logging_util import LOGGER
from agentuniverse.agent_serve.service_manager import ServiceManager
from examples.sample_standard_app.intelligence.db.database import init_app, get_db


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

@app.route("/agent/list", methods=['GET'])
def agent_list():
    try:
        service_manager = ServiceManager()
        services = service_manager.get_instance_obj_list()
        print(services)

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
        # 是否去重看业务需求
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


@app.route("/service_run_stream", methods=['POST'])
@request_param
def service_run_stream(service_id: str = None,
                       params: dict = None,
                       saved: bool = True,
                       ):
    params = {} if params is None else params
    params['service_id'] = service_id
    params['streaming'] = True
    session_id = request.headers.get('X-Session-Id') or request.headers.get('X-Session-ID')
    if session_id:
        params['session_id'] = session_id.strip()
    else:
        # 可选：生成一个临时 session_id，或拒绝请求
        # params['session_id'] = generate_temp_session_id()
        pass  # 或抛出异常

    task = RequestTask(service_run_queue, saved, **params)
    print("Session ID before creating task:", params.get('session_id'))

    context_prefix = get_context_prefix()

    try:
        start_time = g.start_time
    except:
        start_time = None

    response = Response(
        timed_generator(task.stream_run(), start_time, context_prefix),
        mimetype="text/event-stream"
    )
    response.headers['X-Request-ID'] = task.request_id
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    print("All headers:", dict(request.headers))

    return response

# app = Flask(__name__)
# 初始化数据库（注册关闭、初始化等钩子）
init_app(app)
@app.route('/session/list', methods=['GET'])
def sessions_list():
    user_id = request.headers.get('X-User-Id') or request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    try:
        db = get_db()
        # ✅ 改为使用 query 字段，并取第一个非空 query 作为 title 展示
        query = '''
        SELECT 
            session_id AS id,
            query AS title,
            MIN(gmt_create) AS first_created
        FROM request_task 
        WHERE state = 'finished' 
          AND query IS NOT NULL 
          AND query != ''
          AND user_id = ?
        GROUP BY session_id
        ORDER BY first_created DESC
        LIMIT 50
        '''
        rows = db.execute(query, (user_id,)).fetchall()

        sessions = [
            {"id": row["id"], "title": row["title"]}
            for row in rows
        ]
        return jsonify(sessions)

    except Exception as e:
        print(f"数据库查询错误: {e}")
        return jsonify({"error": "服务器内部错误"}), 500

@app.route('/session/update', methods=['PUT'])
def update_session():
    user_id = request.headers.get('X-User-Id') or request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    # 从 JSON 中获取 session_id 和新的 query
    data = request.get_json()
    session_id = data.get('session_id')
    new_query = data.get('query')

    if not session_id:
        return jsonify({"error": "Missing session_id in JSON body"}), 400
    if not new_query:
        return jsonify({"error": "Missing new query content"}), 400

    try:
        db = get_db()

        # 检查是否存在该会话
        cursor = db.execute(
            "SELECT 1 FROM request_task WHERE session_id = ? AND user_id = ? LIMIT 1",
            (session_id, user_id)
        )
        if not cursor.fetchone():
            return jsonify({"error": "Session not found or no permission"}), 404

        # 更新该 session 的所有记录的 query（或只更新第一条作为代表）
        # 这里我们更新所有属于该 session 的记录
        db.execute(
            "UPDATE request_task SET query = ? WHERE session_id = ? AND user_id = ?",
            (new_query, session_id, user_id)
        )
        db.commit()

        return jsonify({
            "message": "Session updated successfully",
            "session_id": session_id,
            "new_query": new_query
        }), 200

    except Exception as e:
        print(f"更新会话错误: {e}")
        return jsonify({"error": "服务器内部错误"}), 500

@app.route('/session/delete', methods=['DELETE'])
def delete_session():
    # 从 header 或 query 获取 user_id
    user_id = request.headers.get('X-User-Id') or request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    # 从请求体中获取 session_id
    data = request.get_json()
    session_id = data.get('session_id') if data else None
    if not session_id:
        return jsonify({"error": "Missing session_id in JSON body"}), 400

    try:
        db = get_db()
        # 先检查是否存在
        cursor = db.execute(
            "SELECT 1 FROM request_task WHERE session_id = ? AND user_id = ? LIMIT 1",
            (session_id, user_id)
        )
        if not cursor.fetchone():
            return jsonify({"error": "Session not found or no permission"}), 404

        # 删除该 session 的所有记录
        db.execute(
            "DELETE FROM request_task WHERE session_id = ? AND user_id = ?",
            (session_id, user_id)
        )
        db.commit()

        return jsonify({"message": "Session deleted successfully", "session_id": session_id}), 200

    except Exception as e:
        print(f"删除会话错误: {e}")
        return jsonify({"error": "服务器内部错误"}), 500

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
