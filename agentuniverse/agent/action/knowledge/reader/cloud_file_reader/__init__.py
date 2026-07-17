# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Backward-compatibility shim for the old ``cloud_file_reader`` package.

This package was removed in favour of ``cloud/`` (PR #634).  The
implementations here are the **original** classes restored verbatim so
that existing user code using the old import paths continues to work.

.. deprecated::
    Import from ``agentuniverse.agent.action.knowledge.reader.cloud``
    instead.  This compatibility layer will be removed in a future
    release.
"""

import warnings

warnings.warn(
    "The 'cloud_file_reader' package is deprecated and will be removed "
    "in a future release.  Please import from "
    "'agentuniverse.agent.action.knowledge.reader.cloud' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from agentuniverse.agent.action.knowledge.reader.cloud_file_reader.feishu_reader import (  # noqa: F401, E501
    PublicFeishuReader,
)
from agentuniverse.agent.action.knowledge.reader.cloud_file_reader.yuque_reader import (  # noqa: F401, E501
    YuqueReader,
)
