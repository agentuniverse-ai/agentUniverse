# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/3/12 15:13
# @Author  : heji
# @Email   : lc299034@antgroup.com
# @FileName: agent_model.py
"""Agent model class."""
import importlib
import json
from copy import deepcopy
from typing import Any, Dict, Optional, Type
from typing import Callable


class AgentModelPropertyLoader:
    def __init__(self, model: "AgentModel"):
        self._model = model

    def __call__(self, attr_name: str) -> Dict[str, Any]:
        return getattr(self._model, f"_{attr_name}", {})


def _import_string(dotted_path: str) -> Callable:
    if ":" in dotted_path:
        module_path, attr_name = dotted_path.split(":", 1)
    else:
        module_path, attr_name = dotted_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, attr_name)


_PROPERTY_LOADER_CLS: Type[AgentModelPropertyLoader] = AgentModelPropertyLoader


def set_property_loader_cls(loader_cls: str) -> None:
    global _PROPERTY_LOADER_CLS
    _PROPERTY_LOADER_CLS = _import_string(loader_cls)


class AgentModel:

    _info: Dict[str, Any] = {}
    _profile: Dict[str, Any] = {}
    _plan: Dict[str, Any] = {}
    _memory: Dict[str, Any] = {}
    _action: Dict[str, Any] = {}
    _work_pattern: Dict[str, Any] = {}
    _property_loader: AgentModelPropertyLoader = None

    def __init__(self, **data):
        for name in (
        "info", "profile", "plan", "memory", "action", "work_pattern"):
            if name in data:
                setattr(self, f"_{name.lstrip('_')}", data.pop(name))

        self._property_loader = _PROPERTY_LOADER_CLS(self)

    @property
    def info(self) -> Dict[str, Any]:
        return self._property_loader("info")

    @info.setter
    def info(self, value: Dict[str, Any]):
        self._info = value

    @property
    def profile(self) -> Dict[str, Any]:
        return self._property_loader("profile")

    @profile.setter
    def profile(self, value: Dict[str, Any]):
        self._profile = value

    @property
    def plan(self) -> Dict[str, Any]:
        return self._property_loader("plan")

    @plan.setter
    def plan(self, value: Dict[str, Any]):
        self._plan = value

    @property
    def memory(self) -> Dict[str, Any]:
        return self._property_loader("memory")

    @memory.setter
    def memory(self, value: Dict[str, Any]):
        self._memory = value

    @property
    def action(self) -> Dict[str, Any]:
        return self._property_loader("action")

    @action.setter
    def action(self, value: Dict[str, Any]):
        self._action = value

    @property
    def work_pattern(self) -> Dict[str, Any]:
        return self._property_loader("work_pattern")

    @work_pattern.setter
    def work_pattern(self, value: Dict[str, Any]):
        self._work_pattern = value

    def llm_params(self) -> dict:
        """
        Returns:
            dict: The parameters for the LLM.
        """
        params = {}
        for key, value in self.profile.get('llm_model').items():
            if key == 'name' or key == 'prompt_processor':
                continue
            if key == 'model_name':
                params['model'] = value
            else:
                params[key] = value
        return params

    def to_dict(self, *, deep_copy: bool = True) -> Dict[str, Any]:
        d = {
            "info": self._info,
            "profile": self._profile,
            "plan": self._plan,
            "memory": self._memory,
            "action": self._action,
            "work_pattern": self._work_pattern,
        }
        return deepcopy(d) if deep_copy else d

    def to_json(self, *, ensure_ascii: bool = False,
                indent: Optional[int] = None) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=ensure_ascii,
                          indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentModel":
        data = deepcopy(data)

        return cls(
            info=data.get("info"),
            profile=data.get("profile"),
            plan=data.get("plan"),
            memory=data.get("memory"),
            action=data.get("action"),
            work_pattern=data.get("work_pattern"),
        )

    @classmethod
    def from_json(cls, s: str) -> "AgentModel":
        return cls.from_dict(json.loads(s))
