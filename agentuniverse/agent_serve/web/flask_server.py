# @Time    : 2025/1/27 10:30
# @Author  : Auto
# @Email   : auto@example.com
# @Note    : 优化错误信息处理，添加详细的错误描述和解决建议

import time
import traceback
from concurrent.futures import TimeoutError

from flask import Flask, Response, g, request, make_response, \
    copy_current_request_context
from loguru import logger
from werkzeug.exceptions import HTTPException
from werkzeug.local import LocalProxy

from agentuniverse.base.util.logging.general_logger import get_context_prefix
from agentuniverse.base.util.logging.log_type_enum import LogTypeEnum
from agentuniverse.base.exception import AgentUniverseException
from .request_task import RequestTask
from .thread_with_result import ThreadPoolExecutorWithReturnValue
from .web_util import request_param, service_run_queue, make_standard_response, \
    FlaskServerManager
from ..service_instance import ServiceInstance, ServiceNotFoundError
from ...base.context.context_coordinator import ContextCoordinator
from ...base.util.logging.logging_util import LOGGER


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
        request_id: Stand for a single request task id, can be used in
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
    """A global non http exception handler with enhanced error information"""
    LOGGER.error(traceback.format_exc())
    
    # 处理AgentUniverse自定义异常
    if isinstance(e, AgentUniverseException):
        return make_standard_response(
            success=False,
            message=e.get_user_friendly_message("zh"),
            status_code=500,
            error_code=e.error_code.value,
            error_details=e.to_dict()
        )
    
    # 处理服务未找到异常
    if isinstance(e, ServiceNotFoundError):
        return make_standard_response(
            success=False,
            message=e.get_user_friendly_message("zh"),
            status_code=404,
            error_code=e.error_code.value,
            error_details=e.to_dict()
        )
    
    # 处理超时异常
    if isinstance(e, TimeoutError):
        return make_standard_response(
            success=False,
            message="请求处理超时，请稍后重试",
            status_code=408,
            error_code="AU_SYSTEM_TIMEOUT",
            error_details={
                "error_type": "TimeoutError",
                "suggestions": [
                    "检查网络连接是否稳定",
                    "尝试减少请求的复杂度",
                    "联系系统管理员"
                ]
            }
        )
    
    # 处理其他异常
    return make_standard_response(
        success=False,
        message="服务器内部错误，请联系系统管理员",
        status_code=500,
        error_code="AU_SYSTEM_INTERNAL_ERROR",
        error_details={
            "error_type": type(e).__name__,
            "error_message": str(e),
            "suggestions": [
                "检查请求参数是否正确",
                "查看服务器日志获取详细信息",
                "联系系统管理员"
            ]
        }
    )


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
