# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/12 15:39
# @Author  : jerry.zzw
# @Email   : jerry.zzw@antgroup.com
# @FileName: config_type_enum.py
from enum import Enum


class ConfigTypeEnum(Enum):
    """The enumeration of the supported configuration file types."""

    TOML = "toml"
    YAML = "yaml"
    JSON = "json"
    XML = "xml"
    PROPERTIES = "properties"
    INI = "ini"
    ENV = "env"
