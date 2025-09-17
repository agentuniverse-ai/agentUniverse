# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/26 10:34
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: web_util.py
import asyncio
import inspect
import queue
import json

from flask import request, make_response, jsonify

from ..service_instance import ServiceInstance
from ...agent.agent import Agent
from ...agent.agent_manager import AgentManager
from ...base.util.logging.logging_util import LOGGER
from ...base.annotation.singleton import singleton


@singleton
class FlaskServerManager:
    _sync_service_timeout = 30

    @property
    def sync_service_timeout(self):
        return self._sync_service_timeout

    @sync_service_timeout.setter
    def sync_service_timeout(self, timeout):
        self._sync_service_timeout = timeout


def request_param(func):
    """An annotation used to parse the flask request params."""

    def wrapper(*args, **kwargs):
        if request.method == "GET":
            req_data = request.args.to_dict()
        # Get the post params from body according to different content type.
        else:
            if "application/json" in request.headers.get("Content-Type"):
                raw_data = request.data.decode("utf-8")
                req_data = json.loads(raw_data)
            else:
                req_data = request.form.to_dict()
        # Get the func arguments name and type.
        sig = inspect.signature(func)
        for name, param in sig.parameters.items():
            if name == "kwargs":
                for key in req_data:
                    if key not in kwargs:
                        kwargs[key] = req_data[key]
                continue
            if name == "saved":
                if "saved" in req_data:
                    kwargs["saved"] = req_data["saved"]
                else:
                    kwargs["saved"] = sig.parameters["saved"].default
                continue
            if name == "session_id":
                kwargs[name] = request.headers.get("X-Session-Id")
            elif param.annotation in (str, int, dict, list, bool):
                kwargs[name] = req_data.get(name, param.default)
            else:
                kwargs[name] = param.annotation(**req_data)
        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


def service_run_queue(service_id, **kwargs):
    """The func used in a separate thread to run an agent service. The result
    will be saved in a queue if one is provided."""
    stream: queue.Queue = kwargs.get("output_stream")
    try:
        res = ServiceInstance(service_id).run(**kwargs)
        return res
    finally:
        if stream:
            stream.put_nowait('{"type": "EOF"}')


def agent_run_queue(agent_id, **kwargs):
    """The func used in a separate thread to run an agent, and the result will be saved in a queue if provided.

    Args:
        agent_id: The agent id
        **kwargs: Arbitrary keyword arguments.
    """
    stream: queue.Queue = kwargs.get("output_stream")
    try:
        agent: Agent = AgentManager().get_instance_obj(agent_id)
        res = agent.run(**kwargs)
        return res
    finally:
        if stream:
            stream.put_nowait('{"type": "EOF"}')


async def async_agent_run_queue(agent_id, **kwargs):
    stream: asyncio.Queue = kwargs.get("output_stream")
    try:
        agent: Agent = await asyncio.to_thread(AgentManager().get_instance_obj, agent_id)
        res = await asyncio.to_thread(agent.run, **kwargs)
        return res
    finally:
        if stream:
            await asyncio.to_thread(stream.put_nowait, '{"type": "EOF"}')


def make_standard_response(success: bool, result=None, message: str = None, request_id: str = None, status_code=200):
    """Construct a standard flask response."""
    response_data = {"success": success, "result": result, "message": message, "request_id": request_id}
    LOGGER.info(f"AU_FLASK_RESPONSE: {response_data}")
    return make_response(jsonify(response_data), status_code)
