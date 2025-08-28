# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/12 14:04
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: sls_sink.py

import asyncio
import queue
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional

import loguru
from aliyun.log.logclient import LogClient
from aliyun.log.logitem import LogItem
from aliyun.log.putlogsrequest import PutLogsRequest
from aliyun.log.putlogsresponse import PutLogsResponse
from loguru import logger


class AsyncSlsSender:
    def __init__(
        self,
        project: str,
        log_store: str,
        endpoint: str,
        access_key_id: str,
        access_key_secret: str,
        queue_max_size: int = 10_000,
        send_interval: float = 2.0,
        batch_size: int = 256,
        max_workers: int = 2,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ):
        self.project = project
        self.log_store = log_store
        self._client = LogClient(endpoint, access_key_id, access_key_secret)

        self._queue: asyncio.Queue[LogItem] = asyncio.Queue(queue_max_size)
        self._send_interval = send_interval
        self._batch_size = batch_size

        self._loop = loop or asyncio.get_running_loop()
        self._executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="sls_uploader")

        self._bg_task: Optional[asyncio.Task] = None
        self._shutdown = asyncio.Event()

    # ---------- public API ----------
    async def start(self) -> None:
        """启动后台批量发送任务（幂等）"""
        if self._bg_task is None or self._bg_task.done():
            self._bg_task = self._loop.create_task(self._worker())

    def put(self, item: LogItem, /) -> None:
        def _safe_put():
            try:
                self._queue.put_nowait(item)
            except asyncio.QueueFull:
                pass

        try:
            running = asyncio.get_running_loop()
        except RuntimeError:
            running = None

        if running is self._loop:
            _safe_put()
        else:
            self._loop.call_soon_threadsafe(_safe_put)

    async def aclose(self, timeout: float | None = 5.0) -> None:
        """
        优雅关闭：
        - 停止后台任务
        - Flush 剩余日志
        - 关闭线程池
        """
        if self._bg_task and not self._bg_task.done():
            self._shutdown.set()
            # 等待 task 结束；到时仍未结束就取消
            try:
                await asyncio.wait_for(self._bg_task, timeout)
            except asyncio.TimeoutError:
                self._bg_task.cancel()

        self._executor.shutdown(wait=True)

    # ---------- internal ----------
    async def _worker(self) -> None:
        """后台循环：批量收集 → 发送"""
        try:
            while not self._shutdown.is_set():
                await self._flush_once()
                try:
                    # 等待下一轮或被提前唤醒
                    await asyncio.wait_for(self._shutdown.wait(), timeout=self._send_interval)
                except asyncio.TimeoutError:
                    pass
            # 程序即将退出，把残余也发送掉
            await self._drain_queue()
        except asyncio.CancelledError:
            pass  # 避免 noisy 日志

    async def _flush_once(self) -> None:
        """取最多 batch_size 条日志并上传"""
        if self._queue.empty():
            return

        items: List[LogItem] = []
        while items.__len__() < self._batch_size and not self._queue.empty():
            try:
                items.append(self._queue.get_nowait())
            except asyncio.QueueEmpty:
                break

        if items:
            await self._upload(items)

    async def _drain_queue(self) -> None:
        """flush 全部剩余日志"""
        while not self._queue.empty():
            await self._flush_once()

    async def _upload(self, items: List[LogItem]) -> Optional[PutLogsResponse]:
        """把同步 put_logs 扔进线程池"""
        def _blocking_upload() -> PutLogsResponse:
            req = PutLogsRequest(self.project, self.log_store, "", "", items)
            return self._client.put_logs(req)

        return await self._loop.run_in_executor(self._executor, _blocking_upload)



class SlsSender:
    """A class to send log to aliyun simple log server."""

    def __init__(
            self,
            project: str,
            log_store: str,
            endpoint: str,
            access_key_id: str,
            access_key_secret: str,
            queue_max_size: int,
            send_interval: float):
        """Initialize a sls sender.

        Args:
            project (`str`):
                Project name of aliyun sls.
            log_store (`str`):
                Log store of aliyun sls.
            endpoint (`str`):
                Endpoint of aliyun sls.
            access_key_id (`str`):
                Project name of aliyun sls.
            access_key_secret (`str`):
                Project name of aliyun sls.
            queue_max_size (`int`):
                Log queue max size, sls sender use a queue to save the logs
                to be sent, a separate thread will upload logs to aliyun sls
                periodically.
            send_interval (`float`):
                Interval of the separate thread sending logs to aliyun sls.
        """
        self.project = project
        self.log_store = log_store
        self.client = LogClient(endpoint, access_key_id, access_key_secret)
        self.log_queue = queue.Queue(queue_max_size)
        self.send_interval = send_interval

        self.send_thread_stop_event = threading.Event()
        self.send_thread = None
        self._logger = loguru.logger

    def _send_put_logs_request(self,
                               log_item_list: List[LogItem],
                               topic: str = "",
                               source: str = "") -> Optional[PutLogsResponse]:
        """Send a batch of logs to aliyun sls.

        Args:
            log_item_list (`List[LogItem]`):
                A list of log items to be sent to aliyun sls.
            topic (`str`, defaults to `""`):
                An attribute used to identify a group of logs in aliyun sls.
            source (`str`, defaults to `""`):
                An identifier that allows to discern the source of the log.

        Returns:
            If logs sent successfully, returns a PutLogsResponse, else returns
            none and log the error in local log file.
        """
        try:
            put_request = PutLogsRequest(self.project, self.log_store, topic,
                                         source, log_item_list)
            put_response = self.client.put_logs(put_request)
        except Exception as e:
            print(f"send single log to sls failed: {str(e)}")
            return None
        return put_response

    def send_single_log(self,
                        message: str,
                        topic: str = "",
                        source: str = "") -> Optional[PutLogsResponse]:
        """Send a single log to aliyun sls.

        Args:
            message (`str`):
                The message to be sent to aliyun sls.
            topic (`str`, defaults to `""`):
                An attribute used to identify a group of logs in aliyun sls.
            source (`str`, defaults to `""`):
                An identifier that allows to discern the source of the log.

        Returns:
            If logs sent successfully, returns a PutLogsResponse, else returns
            none and log the error in local log file.
        """
        log_item_list = list()
        log_item = LogItem()
        log_item.set_contents(message)
        log_item_list.append(log_item)
        return self._send_put_logs_request(log_item_list, topic, source)

    def put_log_queue(self, log_item: LogItem):
        """Put a single log item into the waiting queue.

        Args:
            log_item (`LogItem`):
                The log item to be put into the queue.
        """
        try:
            self.log_queue.put(log_item, block=False)
        except queue.Full:
            self._logger.error("sls log queue is full, discard new log")

    def batch_send(self,
                   topic: str = "",
                   source: str = "") -> Optional[PutLogsResponse]:
        """Send all log items in waiting queue to aliyun sls.

        Args:
            topic (`str`, defaults to `""`):
                An attribute used to identify a group of logs in aliyun sls.
            source (`str`, defaults to `""`):
                An identifier that allows to discern the source of the log.

        Returns:
            If logs sent successfully, returns a PutLogsResponse, else returns
            none and log the error in local log file.
        """

        # Get all log items in waiting queue.
        size = self.log_queue.qsize()
        log_item_list = []
        if self.log_queue is not None and size > 0:
            for i in range(size):
                try:
                    log_item = self.log_queue.get(block=False)
                except queue.Empty:
                    self._logger.error(
                        "sls log queue shorter than expected, "
                        "all logs have been sent")
                    break
                log_item_list.append(log_item)

        # Send all log items to aliyun sls.
        length = len(log_item_list)
        if length > 0:
            return self._send_put_logs_request(log_item_list, topic, source)
        return None

    def start_batch_send_thread(self):
        """Start the log sending thread."""
        if self.send_thread is None or not self.send_thread.is_alive():
            self.send_thread_stop_event.clear()
            self.send_thread = threading.Thread(
                target=self._schedule_send_log,
                name="loop_send_log_thread", daemon=True)
            self.send_thread.start()

    def stop_batch_send_thread(self):
        """Stop the log sending thread."""
        if self.send_thread is not None:
            self.send_thread_stop_event.set()
            self.send_thread.join()
            self.send_thread = None

    def _schedule_send_log(self):
        """Create an infinite loop uploading logs in queue to aliyun sls."""
        while not self.send_thread_stop_event.is_set():
            self.batch_send()
            time.sleep(self.send_interval)


# ------------------------- Loguru sink ------------------------- #
class AsyncSlsSink:

    def __init__(self, sender: AsyncSlsSender):
        self._sender = sender

    def __call__(self, message):
        record = message.record
        item = LogItem(
            contents=[("content", message)],
            timestamp=int(record["time"].timestamp())
        )
        self._sender.put(item)


class SlsSink:
    """A custom loguru sink used to send logs to aliyun sls."""

    def __init__(self, sls_sender: SlsSender):
        """Initialize the sls sink."""
        self.sls_sender = sls_sender

    def __call__(self, message):
        """Construct the message to a sls log item and put it to the queue
         waiting for sls sender to send to the aliyun sls."""
        log_item = LogItem()
        log_item.set_time(int(message.record["time"].timestamp()))
        log_content = list()
        log_content.append(("content", str(message)))
        log_item.set_contents(log_content)
        self.sls_sender.put_log_queue(log_item)
