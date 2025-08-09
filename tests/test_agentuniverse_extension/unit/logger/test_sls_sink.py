# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/13 15:50
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: test_sls_sink.py

import os
import shutil
import time
import pytest
import datetime
from unittest.mock import patch

from agentuniverse.base.util.logging.logging_config import LoggingConfig
from agentuniverse_extension.logger.sls_sink import SlsSender, SlsSink

from tests.test_agentuniverse_extension.mock.logger.mock_log_client import LogClient




@patch('agentuniverse.logger.sls_sink.LogClient', new=LogClient)
def test_sls_log():
    sls_sender = SlsSender(LoggingConfig.sls_project,
                           LoggingConfig.sls_log_store,
                           LoggingConfig.sls_endpoint,
                           LoggingConfig.access_key_id,
                           LoggingConfig.access_key_secret,
                           LoggingConfig.sls_log_queue_max_size,
                           LoggingConfig.sls_log_send_interval)

    sls_sink = SlsSink(sls_sender)

    class Message:
        pass

    message = Message()
    message.record = {"time": datetime.datetime.now()}
    sls_sink(message)
    result = sls_sender.batch_send()
    assert result


if __name__ == "__main__":
    pytest.main([__file__, "-s"])
