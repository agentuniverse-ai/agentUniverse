# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/4/19 15:59
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: rpc_server.py

import json

from agentuniverse.agent_serve.service_instance import ServiceInstance
from ..request_task import RequestTask
from ..web_util import service_run_queue


def service_run(saved: bool, params: str, service_id: str):
    """Synchronous invocation of an agent service. Used in rpc implementation.

    Request Args:
        service_id(`str`): The id of the agent service.
        params(`str`): A Json String contains agent params passed to service.
        saved(`bool`): Save the request and result into database.

    Return:
        Returns a dict containing two keys: success and result.
        success: This key holds a boolean value indicating the task was
            successfully or not.
        result: This key points to a nested dictionary that includes the
            result of the task.
    """
    if params and params.strip():
        params = json.loads(params)
    else:
        params = {}
    request_task = RequestTask(ServiceInstance(service_id).run, saved,
                               **params)
    result = request_task.run()
    return {
        "success": True,
        "result": result,
        "message": None,
        "request_id": request_task.request_id
    }


def service_run_async(saved: bool, params: str, service_id: str):
    """Async invocation of an agent service, return the request id used to
    get result later. Used in rpc implementation.

    Request Args:
        service_id(`str`): The id of the agent service.
        params(`str`): A Json String contains agent params passed to service.
        saved(`bool`): Save the request and result into database.

    Return:
        Returns a dict containing two keys: success and request_id.
        success: This key holds a boolean value indicating the task was
            successfully or not.
        request_id: Stand for a single request task id, can be used in
            service_run_result api to get the result of async task.
    """
    if params and params.strip():
        params = json.loads(params)
    else:
        params = {}
    params['service_id'] = service_id
    task = RequestTask(service_run_queue, saved, **params)
    task.async_run()
    return {
        "success": True,
        "result": None,
        "message": None,
        "request_id": task.request_id
    }


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
        return {
            "success": False,
            "message": f"request {request_id} not found"
        }
    return {
        "success": True,
        "result": json.dumps(data, ensure_ascii=False),
        "message": None,
        "request_id": request_id
    }