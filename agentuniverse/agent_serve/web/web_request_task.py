#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @FileName: web_request_task.py.py
import asyncio
import enum
import json
import queue
import threading
import time
import uuid
import traceback
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, AsyncIterator

from flask import copy_current_request_context
from loguru import logger

# 只导入数据模型和数据库访问层，不导入自己
from agentuniverse.agent_serve.web.dal.entity.web_request_do import WebRequestDO
from agentuniverse.agent_serve.web.dal.web_request_library import WebRequestLibrary

from agentuniverse.base.util.logging.logging_util import LOGGER
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.base.tracing.au_trace_manager import AuTraceManager
from agentuniverse.base.util.logging.general_logger import get_context_prefix
from agentuniverse.base.util.logging.log_type_enum import LogTypeEnum
from agentuniverse.base.config.configer import Configer

EOF_SIGNAL = '{"type": "EOF"}'


@enum.unique
class TaskStateEnum(Enum):
    """All possible state of a web request task."""
    INIT = "init"
    RUNNING = "running"
    FINISHED = "finished"
    FAIL = "fail"
    CANCELED = "canceled"


# All valid transitions of request task.
VALID_TRANSITIONS = {
    (TaskStateEnum.INIT, TaskStateEnum.RUNNING),
    (TaskStateEnum.INIT, TaskStateEnum.FAIL),
    (TaskStateEnum.INIT, TaskStateEnum.CANCELED),
    (TaskStateEnum.RUNNING, TaskStateEnum.FINISHED),
    (TaskStateEnum.RUNNING, TaskStateEnum.FAIL),
    (TaskStateEnum.RUNNING, TaskStateEnum.CANCELED),
}


class ThreadWithReturnValue(threading.Thread):
    """Thread class with return value support."""

    def __init__(self, target=None, args=(), kwargs={}):
        super().__init__(target=target, args=args, kwargs=kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def result(self):
        self.join()
        return self._return


class WebRequestTask:
    """Web请求任务类，使用新的数据库表"""

    def __init__(self, func, saved=True, **kwargs):
        self.func: callable = func
        self.kwargs = kwargs
        request_id = AuTraceManager().get_trace_id()
        if not request_id:
            request_id = uuid.uuid4().hex
        self.request_id = request_id
        self.queue = queue.Queue(maxsize=1000)
        self.thread: Optional[ThreadWithReturnValue] = None
        self.state = TaskStateEnum.INIT.value
        self.saved = saved
        self.last_update_time = time.time()
        # 使用新的数据访问层和数据对象
        self.web_request_library = WebRequestLibrary(Configer())
        self.__request_do__ = self.add_request_do()

        self.async_queue = asyncio.Queue(maxsize=2000)
        self.async_task = None
        self.session_id = None
        self.title = None

    def update_request_do(self, force: bool = False):
        current_time = time.time()
        if_update = current_time - self.last_update_time >= self.web_request_library.update_interval

        if if_update or force:
            self.last_update_time = current_time
            self.web_request_library.update_request(self.__request_do__)

    def receive_steps(self):
        """Yield the stream data by getting data from the queue."""
        self.next_state(TaskStateEnum.RUNNING)
        first_chunk = True
        start_time = time.time()
        while True:
            output: str = self.queue.get()
            if output is None:
                break
            if output == EOF_SIGNAL:
                break
            if first_chunk:
                first_chunk = False
                cost_time = time.time() - start_time
                logger.bind(
                    log_type=LogTypeEnum.agent_first_token,
                    cost_time=cost_time,
                    context_prefix=get_context_prefix()
                ).info("Agent first token generated.")
            yield "data:" + json.dumps({"process": output},
                                       ensure_ascii=False) + "\n\n"
        try:
            if self.canceled():
                self.__request_do__.result['result'] = {
                    "result": "The task's tracking status has been canceled."}
            else:
                result = self.thread.result()
                if isinstance(result, OutputObject):
                    result = result.to_dict()

                yield "data:" + json.dumps({"result": result},
                                           ensure_ascii=False) + "\n\n "
                self.__request_do__.result['result'] = result
                self.next_state(TaskStateEnum.FINISHED)
            if self.saved:
                self.update_request_do(force=True)
        except Exception as e:
            LOGGER.error("web request task execute Fail: " + str(e) + traceback.format_exc())
            if self.saved:
                self.__request_do__.result['result'] = {"error_msg": str(e)}
                self.next_state(TaskStateEnum.FAIL)
                self.update_request_do(force=True)
            yield "data:" + json.dumps({"error": {"error_msg": str(e)}}) + "\n\n "

    def user_receive_steps(self):
        """Yield the stream data by getting data from the queue."""
        self.next_state(TaskStateEnum.RUNNING)
        first_chunk = True
        start_time = time.time()
        while True:
            output: str = self.queue.get()
            if output is None:
                break
            if output == EOF_SIGNAL:
                break
            if first_chunk:
                first_chunk = False
                cost_time = time.time() - start_time
                logger.bind(
                    log_type=LogTypeEnum.agent_first_token,
                    cost_time=cost_time,
                    context_prefix=get_context_prefix()
                ).info("Agent first token generated.")
            if isinstance(output, str):
                yield "data:" + output + "\n\n"
        try:
            if self.canceled():
                self.__request_do__.result['result'] = {
                    "result": "The task's tracking status has been canceled."}
            else:
                result = self.thread.result()
                if isinstance(result, OutputObject):
                    result = result.to_dict()
                self.__request_do__.result['result'] = result
                self.next_state(TaskStateEnum.FINISHED)
            if self.saved:
                self.update_request_do(force=True)
        except Exception as e:
            LOGGER.error("web request task execute Fail: " + str(e) + traceback.format_exc())
            if self.saved:
                self.__request_do__.result['result'] = {"error_msg": str(e)}
                self.next_state(TaskStateEnum.FAIL)
                self.update_request_do(force=True)
            yield "data:" + json.dumps({"error": {"error_msg": str(e)}}) + "\n\n "

    async def async_receive_steps(self) -> AsyncIterator[str]:
        self.next_state(TaskStateEnum.RUNNING)
        first_chunk = True
        start_time = time.time()
        while True:
            try:
                output: str = await asyncio.wait_for(self.async_queue.get(), timeout=0.5)
            except asyncio.TimeoutError:
                await asyncio.sleep(1)
                print("Waiting for data timed out. Retrying...")
                continue
            if output is None:
                break
            if output == EOF_SIGNAL:
                break
            if first_chunk:
                first_chunk = False
                cost_time = time.time() - start_time
                logger.bind(
                    log_type=LogTypeEnum.agent_first_token,
                    cost_time=cost_time,
                    context_prefix=get_context_prefix()
                ).info("LLM first token generated.")
            yield "data:" + json.dumps({"process": output},
                                       ensure_ascii=False) + "\n\n"
        try:
            if self.canceled():
                self.__request_do__.result['result'] = {
                    "result": "The task's tracking status has been canceled."}
            else:
                result = await self.async_task
                if isinstance(result, OutputObject):
                    result = result.to_dict()
                yield "data:" + json.dumps({"result": result},
                                           ensure_ascii=False) + "\n\n"
                self.__request_do__.result["result"] = result
            if self.saved:
                self.update_request_do(force=True)
        except Exception as e:
            LOGGER.error("web request task update request state Fail: " + str(e))
            if self.saved:
                self.__request_do__.result['result'] = {"error_msg": str(e)}
                self.next_state(TaskStateEnum.FAIL)
                self.update_request_do(force=True)
            yield "data:" + json.dumps({"error": {"error_msg": str(e)}}) + "\n\n"

    def append_steps(self):
        """Tracing async service running state and update it to database."""
        try:
            self.next_state(TaskStateEnum.RUNNING)
            while True:
                output: str = self.queue.get()
                if output is None:
                    break
                if output == EOF_SIGNAL:
                    break
                if output != "" and output != " ":
                    self.__request_do__.steps.append(output)
                if self.saved:
                    self.update_request_do()
            if self.canceled():
                self.__request_do__.result['result'] = {
                    "result": "The task's tracking status has been canceled."}
            else:
                result = self.thread.result()
                if isinstance(result, OutputObject):
                    result = result.to_dict()
                self.__request_do__.result['result'] = result
                self.next_state(TaskStateEnum.FINISHED)
            if self.saved:
                self.update_request_do(force=True)
        except Exception as e:
            LOGGER.error("web request task update request state Fail: " + str(e))
            self.__request_do__.result['result'] = {"error_msg": str(e)}
            self.next_state(TaskStateEnum.FAIL)
            if self.saved:
                self.update_request_do(force=True)

    def async_run(self):
        """Run the service in async mode."""
        self.kwargs['output_stream'] = self.queue
        self.thread = ThreadWithReturnValue(target=copy_current_request_context(self.func),
                                            kwargs=self.kwargs)
        self.thread.start()
        threading.Thread(target=self.append_steps).start()
        threading.Thread(target=self.check_state).start()

    def stream_run(self):
        """Run the service in a separate thread and yield result stream."""
        self.kwargs['output_stream'] = self.queue
        self.thread = ThreadWithReturnValue(target=copy_current_request_context(self.func),
                                            kwargs=self.kwargs)
        self.thread.start()
        return self.receive_steps()

    def user_stream_run(self):
        self.kwargs['output_stream'] = self.queue
        self.thread = ThreadWithReturnValue(target=copy_current_request_context(self.func),
                                            kwargs=self.kwargs)
        self.thread.start()
        return self.user_receive_steps()

    async def async_stream_run(self) -> AsyncIterator[str]:
        self.kwargs['output_stream'] = self.async_queue
        loop = asyncio.get_event_loop()
        self.async_task = loop.create_task(self.func(**self.kwargs))
        async for item in self.async_receive_steps():
            yield item

    def run(self):
        """Run the service synchronous and return the result."""
        self.next_state(TaskStateEnum.RUNNING)
        try:
            result = self.func(**self.kwargs)
            self.next_state(TaskStateEnum.FINISHED)
            self.__request_do__.result = {"result": result}
            return result
        except Exception as e:
            self.next_state(TaskStateEnum.FAIL)
            self.__request_do__.additional_args['error_msg'] = str(e)
            raise e
        finally:
            if self.saved:
                self.web_request_library.update_request(self.__request_do__)

    def next_state(self, next_state: TaskStateEnum):
        """Update request task state if the transition is valid."""
        if ((TaskStateEnum[self.__request_do__.state.upper()], next_state)
                in VALID_TRANSITIONS):
            self.__request_do__.state = next_state.value
        else:
            raise Exception("Invalid state transition")

    def check_state(self):
        """Keep check request task thread state every minute."""
        while True:
            if self.thread is not None and self.thread.is_alive():
                LOGGER.debug(
                    "web request:" + str(self.request_id) + " task thread alive")
                if self.saved:
                    self.web_request_library.update_gmt_modified(self.request_id)
                time.sleep(60)
                continue
            elif self.__request_do__.state == TaskStateEnum.RUNNING.value:
                time.sleep(60)
                if self.__request_do__.state == TaskStateEnum.RUNNING.value:
                    LOGGER.debug("web request:" + str(self.request_id) +
                                 " task thread stop but state not end")
                    self.__request_do__.state = TaskStateEnum.FAIL.value
                    if self.saved:
                        self.update_request_do(force=True)
            break

    def add_request_do(self):
        query_keys = ['question', 'query_content', 'query', 'request', 'input']
        query = next((self.kwargs[key] for key in query_keys if
                      self.kwargs.get(key) is not None),
                     "No relevant query was retrieved.")

        request_do = WebRequestDO(
            request_id=self.request_id,
            session_id=self.kwargs.get('session_id', ''),
            query=query,
            title = query,
            state=TaskStateEnum.INIT.value,
            result=dict(),
            steps=[],
            additional_args=dict(),
            gmt_create=datetime.now(),
            gmt_modified=datetime.now(),
        )
        if self.saved:
            self.web_request_library.add_request(request_do)
        return request_do

    def result(self):
        """Get the result from service running thread."""
        return self.thread.result()

    @staticmethod
    def is_validate(request_do: WebRequestDO):
        """If there is no update within ten minutes and the status is neither
        completed nor failed, the task is considered to have failed."""
        if (request_do.gmt_modified < datetime.now() - timedelta(minutes=10)
                and request_do.state != TaskStateEnum.FINISHED.value
                and request_do.state != TaskStateEnum.FAIL.value):
            LOGGER.error("web request task is validate fail" + str(request_do))
            request_do.state = TaskStateEnum.FAIL.value
            WebRequestLibrary(Configer()).update_request(request_do)

    def cancel(self):
        """Cancel the request task."""
        self.next_state(TaskStateEnum.CANCELED)
        if self.queue is not None:
            self.queue.put_nowait(EOF_SIGNAL)

    def request_state(self):
        """Return the request task state."""
        return self.__request_do__.state

    def canceled(self):
        """Whether task is canceled state."""
        return self.__request_do__.state == TaskStateEnum.CANCELED.value

    def finished(self):
        """Set task to finished state."""
        self.__request_do__.state = TaskStateEnum.FINISHED.value

    @staticmethod
    def query_request_state(request_id: str) -> dict | None:
        """Query the request data in database by given request_id."""
        request_do = WebRequestLibrary(Configer()).query_request_by_request_id(request_id)
        if request_do is None:
            return None
        WebRequestTask.is_validate(request_do)
        return {
            "state": request_do.state,
            "result": request_do.result,
            "steps": request_do.steps
        }
