# !/usr/bin/env python3
# -*- coding:utf-8 -*-

import enum
from enum import Enum


@enum.unique
class ToolTypeEnum(Enum):
    API = 'api'
    FUNC = 'func'
