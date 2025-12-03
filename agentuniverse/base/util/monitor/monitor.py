# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/5/20 16:24
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: monitor.py
import datetime
import json
import os
from typing import Union, Optional, Dict, List
from collections import defaultdict
from loguru import logger

from pydantic import BaseModel

from agentuniverse.llm.llm_output import LLMOutput, TokenUsage
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.base.annotation.singleton import singleton
from agentuniverse.base.config.configer import Configer
from agentuniverse.base.context.framework_context_manager import FrameworkContextManager
from agentuniverse.base.util.logging.general_logger import get_context_prefix
from agentuniverse.base.util.logging.log_type_enum import LogTypeEnum
from agentuniverse.base.tracing.au_trace_manager import AuTraceManager

LLM_INVOCATION_SUBDIR = "llm_invocation"
AGENT_INVOCATION_SUBDIR = "agent_invocation"


@singleton
class Monitor(BaseModel):
    dir: Optional[str] = './monitor'
    activate: Optional[bool] = False
    log_activate: Optional[bool] = True

    def __init__(self, configer: Configer = None, **kwargs):
        super().__init__(**kwargs)
        if configer:
            config: dict = configer.value.get('MONITOR', {})
            self.dir = config.get('dir', './monitor')
            self.activate = config.get('activate', False)
            self.log_activate = config.get('log_activate', True)

    @staticmethod
    def trace_llm_input(source: str, llm_input: Union[str, dict]) -> None:
        """Trace the llm input."""
        logger.bind(
            log_type=LogTypeEnum.llm_input,
            llm_input=llm_input,
            context_prefix=get_context_prefix()
        ).info("Trace llm input.")

    @staticmethod
    def trace_llm_invocation(source: str, llm_input: Union[str, dict], llm_output: Union[str, dict],
                             cost_time: float = None) -> None:
        """
        Trace the llm invocation.

        This method will:
        1. 打印一条包含 token 使用量的结构化日志，便于集中日志检索。
        2. 在开启 Monitor.activate 的情况下，将调用明细（含 token 使用量）写入 jsonl 文件，
           方便后续做离线统计与分析。
        """
        used_token = Monitor.get_token_usage()

        # 1. 结构化日志，便于在日志系统中检索
        logger.bind(
            log_type=LogTypeEnum.llm_invocation,
            used_token=used_token,
            cost_time=cost_time,
            llm_output=llm_output,
            context_prefix=get_context_prefix()
        ).info("Trace llm invocation.")

        # 2. 按小时将调用明细落盘到 jsonl 文件，便于后续做离线统计
        monitor = Monitor()
        if monitor.activate:
            try:
                import jsonlines
            except ImportError:
                # 与 agent 监控保持一致：只在使用者显式开启监控时才需要额外依赖
                raise ImportError(
                    "jsonlines is required to trace llm invocation: `pip install jsonlines`"
                )

            date = datetime.datetime.now()
            record = {
                "source": source,
                "date": date.strftime("%Y-%m-%d %H:%M:%S"),
                "llm_input": llm_input,
                "llm_output": llm_output,
                "token_usage": used_token,
                "cost_time": cost_time,
            }

            filename = f"llm_{source}_{date.strftime('%Y-%m-%d-%H')}.jsonl"
            path_save = os.path.join(
                str(monitor._get_or_create_subdir(LLM_INVOCATION_SUBDIR)),
                filename
            )

            with jsonlines.open(path_save, 'a') as writer:
                writer.write(record)

    def trace_llm_token_usage(self, llm_obj: object, llm_input: dict, output: LLMOutput) -> None:
        """ Trace the token usage of the given LLM object.
        Args:
            llm_obj(object): LLM object.
            llm_input(dict): Dictionary of LLM input.
            output_str(str): LLM output.
        """
        trace_id = AuTraceManager().get_trace_id()

        # trace token usage for a complete request chain based on trace id
        if trace_id:
            token_usage: dict = self.get_llm_token_usage(llm_obj, llm_input,
                                                         output)
            old_token_usage: dict = FrameworkContextManager().get_context(trace_id + '_token_usage')
            if old_token_usage is not None:
                if token_usage:
                    Monitor.add_token_usage(token_usage)

    def trace_agent_input(self, source: str, agent_input: Union[str, dict]) -> None:
        """Trace the agent input."""
        if self.log_activate:
            logger.bind(
                log_type=LogTypeEnum.agent_input,
                agent_input=agent_input,
                context_prefix=get_context_prefix()
            ).info("Trace agent input.")

    def trace_agent_invocation(self, source: str, agent_input: Union[str, dict],
                               agent_output: OutputObject, cost_time: float = None) -> None:
        """Trace the agent invocation and save it to the monitor jsonl file."""
        # Get token usage for this agent invocation
        token_usage = Monitor.get_token_usage()
        
        if self.activate:
            try:
                import jsonlines
            except ImportError:
                raise ImportError(
                    "jsonlines is required to trace llm invocation: `pip install jsonlines`"
                )
            # get the current time
            date = datetime.datetime.now()
            agent_invocation = {
                "source": source,
                "date": date.strftime("%Y-%m-%d %H:%M:%S"),
                "agent_input": self.serialize_obj(agent_input),
                "agent_output": self.serialize_obj(agent_output),
                "token_usage": token_usage,
                "cost_time": cost_time,
            }
            # files are stored in hours
            filename = f"agent_{source}_{date.strftime('%Y-%m-%d-%H')}.jsonl"
            # file path to save
            path_save = os.path.join(str(self._get_or_create_subdir(AGENT_INVOCATION_SUBDIR)), filename)

            # write to jsonl
            with jsonlines.open(path_save, 'a') as writer:
                writer.write(agent_invocation)

        if self.log_activate:
            logger.bind(
                log_type=LogTypeEnum.agent_invocation,
                cost_time=cost_time,
                token_usage=token_usage,
                agent_output=agent_output,
                context_prefix=get_context_prefix()
            ).info("Trace agent invocation.")

    def trace_tool_input(self, source: str, tool_input: Union[str, dict]) -> None:
        """Trace the tool input."""
        if self.log_activate:
            logger.bind(
                log_type=LogTypeEnum.tool_input,
                tool_input=tool_input,
                context_prefix=get_context_prefix()
            ).info("Trace tool input.")

    def trace_tool_invocation(self, source: str, tool_input: Union[str, dict],
                              tool_output: Union[str, dict], cost_time: float = None) -> None:
        """Trace the tool invocation and save it to the monitor jsonl file."""
        if self.log_activate:
            logger.bind(
                log_type=LogTypeEnum.tool_invocation,
                cost_time=cost_time,
                tool_output=tool_output,
                context_prefix=get_context_prefix()
            ).info("Trace tool invocation.")

    @staticmethod
    def init_invocation_chain():
        """Initialize the invocation chain in the framework context."""
        trace_id = AuTraceManager().get_trace_id()
        if FrameworkContextManager().get_context(trace_id + '_invocation_chain') is None:
            FrameworkContextManager().set_context(trace_id + '_invocation_chain', [])

    @staticmethod
    def init_invocation_chain_bak():
        """Initialize the invocation chain bak version in the framework context."""
        trace_id = AuTraceManager().get_trace_id()
        if FrameworkContextManager().get_context(trace_id + '_invocation_chain_bak') is None:
            FrameworkContextManager().set_context(trace_id + '_invocation_chain_bak', [])

    @staticmethod
    def pop_invocation_chain():
        """Pop the last chain node in invocation chain."""
        trace_id = AuTraceManager().get_trace_id()
        if trace_id is not None:
            invocation_chain: list = FrameworkContextManager().get_context(
                trace_id + '_invocation_chain')
            if invocation_chain:
                invocation_chain.pop()
                FrameworkContextManager().set_context(
                    trace_id + '_invocation_chain', invocation_chain)

    @staticmethod
    def clear_invocation_chain():
        """Clear the invocation chain in the framework context."""
        trace_id = AuTraceManager().get_trace_id()
        if trace_id is not None:
            FrameworkContextManager().del_context(trace_id + '_invocation_chain')
            FrameworkContextManager().del_context(trace_id + '_invocation_chain_bak')

    @staticmethod
    def add_invocation_chain(source: dict):
        """Add the source to the invocation chain"""
        trace_id = AuTraceManager().get_trace_id()
        if trace_id is not None:
            invocation_chain = FrameworkContextManager().get_context(trace_id + '_invocation_chain')
            if invocation_chain is not None:
                invocation_chain = invocation_chain.copy()
                invocation_chain.append(source)
                FrameworkContextManager().set_context(trace_id + '_invocation_chain', invocation_chain)
            invocation_chain_bak = FrameworkContextManager().get_context(trace_id + '_invocation_chain_bak')
            if invocation_chain_bak is not None:
                invocation_chain_bak.append(source)

    @staticmethod
    def get_trace_id():
        """Get the trace id in the framework context."""
        return AuTraceManager().get_trace_id()

    @staticmethod
    def get_invocation_chain():
        """Get the invocation chain in the framework context."""
        trace_id = AuTraceManager().get_trace_id()
        current_chain = FrameworkContextManager().get_context(trace_id + '_invocation_chain')
        if isinstance(current_chain, list):
            return current_chain
        else:
            current_chain = []
            FrameworkContextManager().set_context(
                trace_id + '_invocation_chain', current_chain)
            return current_chain

    @staticmethod
    def get_invocation_chain_bak():
        """Get the invocation chain bak version in the framework context."""
        trace_id = AuTraceManager().get_trace_id()
        current_chain = FrameworkContextManager().get_context(
            trace_id + '_invocation_chain_bak')
        if isinstance(current_chain, list):
            return current_chain
        else:
            current_chain = []
            FrameworkContextManager().set_context(
                trace_id + '_invocation_chain_bak', current_chain)
            return current_chain

    @staticmethod
    def init_token_usage():
        """Initialize the token usage in the framework context."""
        trace_id = AuTraceManager().get_trace_id()
        if FrameworkContextManager().get_context(trace_id + '_token_usage') is None:
            FrameworkContextManager().set_context(trace_id + '_token_usage', {})

    @staticmethod
    def add_token_usage(cur_token_usage: dict):
        """Add the token usage to the framework context."""
        if cur_token_usage is None:
            return
        trace_id = AuTraceManager().get_trace_id()
        if trace_id is not None:
            old_token_usage: dict = FrameworkContextManager().get_context(trace_id + '_token_usage')
            if old_token_usage is not None:
                result_usage = {}
                for key, value in cur_token_usage.items():
                    try:
                        result_usage[key] = old_token_usage[key] + value if key in old_token_usage else value
                    except:
                        # not addable value
                        pass
                FrameworkContextManager().set_context(trace_id + '_token_usage', result_usage)

    @staticmethod
    def clear_token_usage():
        """Clear the token usage in the framework context."""
        trace_id = AuTraceManager().get_trace_id()
        if trace_id is not None:
            FrameworkContextManager().del_context(trace_id + '_token_usage')
        FrameworkContextManager().del_context('trace_id')

    @staticmethod
    def get_token_usage():
        """Get the token usage in the framework context."""
        trace_id = AuTraceManager().get_trace_id()
        return FrameworkContextManager().get_context(trace_id + '_token_usage', {}) if trace_id is not None else {}

    @staticmethod
    def get_invocation_chain_str() -> str:
        invocation_chain_str = ''
        invocation_chain = Monitor.get_invocation_chain()
        if len(invocation_chain) > 0:
            invocation_chain_str = ' -> '.join(
                [f"source: {d.get('source', '')}, type: {d.get('type', '')}" for
                 d in invocation_chain]
            )
            invocation_chain_str += ' | '
        return invocation_chain_str

    @staticmethod
    def get_llm_token_usage(llm_obj: object, llm_input: dict, output: LLMOutput) -> dict:
        """ Calculate the token usage of the given LLM object.
        Args:
            llm_obj(object): LLM object.
            llm_input(dict): Dictionary of LLM input.
            output(LLMOutput): LLM output.

        Returns:
            dict: Dictionary of token usage including the completion_tokens, prompt_tokens, and total_tokens.
        """
        try:
            if output.usage and output.usage.completion_tokens > 0 and output.usage.prompt_tokens > 0:
                return output.usage.to_dict()

            if llm_obj is None or llm_input is None:
                return {}
            messages = llm_input.get('kwargs', {}).pop('messages', None)

            input_str = ''
            if messages is not None and isinstance(messages, list):
                for m in messages:
                    if isinstance(m, dict):
                        input_str += str(m.get('role', '')) + '\n'
                        input_str += str(m.get('content', '')) + '\n'

                    elif isinstance(m, object):
                        if hasattr(m, 'role'):
                            role = m.role
                            if role is not None:
                                input_str += str(m.role) + '\n'
                        if hasattr(m, 'content'):
                            content = m.content
                            if content is not None:
                                input_str += str(m.content) + '\n'

            if input_str == '' or output.text == '':
                return {}

            # the number of input and output tokens is calculated by the llm `get_num_tokens` method.
            if hasattr(llm_obj, 'get_num_tokens'):
                output.usage = TokenUsage()
                output.usage.text_out = llm_obj.get_num_tokens(output.text)
                output.usage.text_in = llm_obj.get_num_tokens(input_str)
            return output.usage.to_dict()
        except Exception as e:
            return {}

    def _get_or_create_subdir(self, subdir: str) -> str:
        """Get or create a subdirectory if it doesn't exist in the monitor directory."""
        path = os.path.join(self.dir, subdir)
        os.makedirs(path, exist_ok=True)
        return path

    @staticmethod
    def default_serializer(obj):
        """Default serializer for objects."""
        if isinstance(obj, InputObject):
            return obj.to_dict()
        elif isinstance(obj, OutputObject):
            return obj.to_dict()
        elif isinstance(obj, BaseModel):
            try:
                return obj.dict()
            except TypeError:
                raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")
        else:
            raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

    def serialize_obj(self, obj):
        """Serialize an object and filter out non-serializable values."""
        filtered_obj = self.filter_and_serialize(obj)
        return json.loads(json.dumps(filtered_obj, default=self.default_serializer))

    def filter_and_serialize(self, obj):
        """Recursively filter out non-serializable values from an object."""

        def is_json_serializable(value):
            """Check if value is a JSON serializable object."""
            try:
                json.dumps(value, default=self.default_serializer)
                return True
            except (TypeError, OverflowError):
                return False

        def filter_dict(d):
            return {k: v for k, v in d.items() if is_json_serializable(v)}

        def recursive_filter(o):
            if isinstance(o, dict):
                return filter_dict({k: recursive_filter(v) for k, v in o.items()})
            elif isinstance(o, list):
                return [recursive_filter(i) for i in o if is_json_serializable(i)]
            else:
                return o

        return recursive_filter(obj)

    def get_llm_statistics(self, start_date: Optional[str] = None, 
                          end_date: Optional[str] = None,
                          source: Optional[str] = None) -> Dict:
        """
        统计LLM调用数据。
        
        Args:
            start_date: 开始日期，格式 "YYYY-MM-DD" 或 "YYYY-MM-DD HH:MM:SS"
            end_date: 结束日期，格式 "YYYY-MM-DD" 或 "YYYY-MM-DD HH:MM:SS"
            source: 过滤特定的LLM source，如果为None则统计所有source
            
        Returns:
            dict: 包含以下字段的统计结果：
                - total_calls: 总调用次数
                - total_tokens: 总token数
                - total_prompt_tokens: 总prompt tokens
                - total_completion_tokens: 总completion tokens
                - avg_cost_time: 平均响应时间（秒）
                - by_source: 按source分组的统计
        """
        try:
            import jsonlines
        except ImportError:
            raise ImportError("jsonlines is required: `pip install jsonlines`")
        
        llm_dir = self._get_or_create_subdir(LLM_INVOCATION_SUBDIR)
        if not os.path.exists(llm_dir):
            return {
                "total_calls": 0,
                "total_tokens": 0,
                "total_prompt_tokens": 0,
                "total_completion_tokens": 0,
                "avg_cost_time": 0.0,
                "by_source": {}
            }
        
        # Parse date filters
        start_dt = None
        end_dt = None
        if start_date:
            try:
                start_dt = datetime.datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                try:
                    start_dt = datetime.datetime.strptime(start_date, "%Y-%m-%d")
                except ValueError:
                    pass
        if end_date:
            try:
                end_dt = datetime.datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                try:
                    end_dt = datetime.datetime.strptime(end_date, "%Y-%m-%d")
                    end_dt = end_dt.replace(hour=23, minute=59, second=59)
                except ValueError:
                    pass
        
        stats = {
            "total_calls": 0,
            "total_tokens": 0,
            "total_prompt_tokens": 0,
            "total_completion_tokens": 0,
            "total_cost_time": 0.0,
            "by_source": defaultdict(lambda: {
                "calls": 0,
                "tokens": 0,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "cost_time": 0.0
            })
        }
        
        # Scan all jsonl files
        for filename in os.listdir(llm_dir):
            if not filename.startswith("llm_") or not filename.endswith(".jsonl"):
                continue
            
            file_source = filename.replace("llm_", "").split("_")[0]
            if source and file_source != source:
                continue
            
            filepath = os.path.join(llm_dir, filename)
            try:
                with jsonlines.open(filepath, 'r') as reader:
                    for record in reader:
                        record_date_str = record.get("date", "")
                        if record_date_str:
                            try:
                                record_date = datetime.datetime.strptime(record_date_str, "%Y-%m-%d %H:%M:%S")
                                if start_dt and record_date < start_dt:
                                    continue
                                if end_dt and record_date > end_dt:
                                    continue
                            except ValueError:
                                pass
                        
                        stats["total_calls"] += 1
                        source_stats = stats["by_source"][file_source]
                        source_stats["calls"] += 1
                        
                        token_usage = record.get("token_usage", {})
                        if isinstance(token_usage, dict):
                            total = token_usage.get("total_tokens", 0)
                            prompt = token_usage.get("prompt_tokens", 0)
                            completion = token_usage.get("completion_tokens", 0)
                            
                            stats["total_tokens"] += total
                            stats["total_prompt_tokens"] += prompt
                            stats["total_completion_tokens"] += completion
                            
                            source_stats["tokens"] += total
                            source_stats["prompt_tokens"] += prompt
                            source_stats["completion_tokens"] += completion
                        
                        cost_time = record.get("cost_time")
                        if cost_time is not None:
                            stats["total_cost_time"] += cost_time
                            source_stats["cost_time"] += cost_time
            except Exception as e:
                logger.warning(f"Error reading file {filename}: {e}")
                continue
        
        # Calculate averages
        if stats["total_calls"] > 0:
            stats["avg_cost_time"] = stats["total_cost_time"] / stats["total_calls"]
        else:
            stats["avg_cost_time"] = 0.0
        
        # Calculate averages for each source
        for source_key in stats["by_source"]:
            source_stats = stats["by_source"][source_key]
            if source_stats["calls"] > 0:
                source_stats["avg_cost_time"] = source_stats["cost_time"] / source_stats["calls"]
            else:
                source_stats["avg_cost_time"] = 0.0
        
        stats["by_source"] = dict(stats["by_source"])
        del stats["total_cost_time"]  # Remove intermediate field
        
        return stats

    def get_agent_statistics(self, start_date: Optional[str] = None,
                            end_date: Optional[str] = None,
                            source: Optional[str] = None) -> Dict:
        """
        统计Agent调用数据。
        
        Args:
            start_date: 开始日期，格式 "YYYY-MM-DD" 或 "YYYY-MM-DD HH:MM:SS"
            end_date: 结束日期，格式 "YYYY-MM-DD" 或 "YYYY-MM-DD HH:MM:SS"
            source: 过滤特定的Agent source，如果为None则统计所有source
            
        Returns:
            dict: 包含以下字段的统计结果：
                - total_calls: 总调用次数
                - total_tokens: 总token数
                - avg_cost_time: 平均响应时间（秒）
                - by_source: 按source分组的统计
        """
        try:
            import jsonlines
        except ImportError:
            raise ImportError("jsonlines is required: `pip install jsonlines`")
        
        agent_dir = self._get_or_create_subdir(AGENT_INVOCATION_SUBDIR)
        if not os.path.exists(agent_dir):
            return {
                "total_calls": 0,
                "total_tokens": 0,
                "avg_cost_time": 0.0,
                "by_source": {}
            }
        
        # Parse date filters
        start_dt = None
        end_dt = None
        if start_date:
            try:
                start_dt = datetime.datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                try:
                    start_dt = datetime.datetime.strptime(start_date, "%Y-%m-%d")
                except ValueError:
                    pass
        if end_date:
            try:
                end_dt = datetime.datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                try:
                    end_dt = datetime.datetime.strptime(end_date, "%Y-%m-%d")
                    end_dt = end_dt.replace(hour=23, minute=59, second=59)
                except ValueError:
                    pass
        
        stats = {
            "total_calls": 0,
            "total_tokens": 0,
            "total_cost_time": 0.0,
            "by_source": defaultdict(lambda: {
                "calls": 0,
                "tokens": 0,
                "cost_time": 0.0
            })
        }
        
        # Scan all jsonl files
        for filename in os.listdir(agent_dir):
            if not filename.startswith("agent_") or not filename.endswith(".jsonl"):
                continue
            
            file_source = filename.replace("agent_", "").split("_")[0]
            if source and file_source != source:
                continue
            
            filepath = os.path.join(agent_dir, filename)
            try:
                with jsonlines.open(filepath, 'r') as reader:
                    for record in reader:
                        record_date_str = record.get("date", "")
                        if record_date_str:
                            try:
                                record_date = datetime.datetime.strptime(record_date_str, "%Y-%m-%d %H:%M:%S")
                                if start_dt and record_date < start_dt:
                                    continue
                                if end_dt and record_date > end_dt:
                                    continue
                            except ValueError:
                                pass
                        
                        stats["total_calls"] += 1
                        source_stats = stats["by_source"][file_source]
                        source_stats["calls"] += 1
                        
                        token_usage = record.get("token_usage", {})
                        if isinstance(token_usage, dict):
                            total = token_usage.get("total_tokens", 0)
                            stats["total_tokens"] += total
                            source_stats["tokens"] += total
                        
                        cost_time = record.get("cost_time")
                        if cost_time is not None:
                            stats["total_cost_time"] += cost_time
                            source_stats["cost_time"] += cost_time
            except Exception as e:
                logger.warning(f"Error reading file {filename}: {e}")
                continue
        
        # Calculate averages
        if stats["total_calls"] > 0:
            stats["avg_cost_time"] = stats["total_cost_time"] / stats["total_calls"]
        else:
            stats["avg_cost_time"] = 0.0
        
        # Calculate averages for each source
        for source_key in stats["by_source"]:
            source_stats = stats["by_source"][source_key]
            if source_stats["calls"] > 0:
                source_stats["avg_cost_time"] = source_stats["cost_time"] / source_stats["calls"]
            else:
                source_stats["avg_cost_time"] = 0.0
        
        stats["by_source"] = dict(stats["by_source"])
        del stats["total_cost_time"]  # Remove intermediate field
        
        return stats

    def estimate_cost(self, token_usage: Dict, 
                     prompt_price_per_1k: float = 0.0,
                     completion_price_per_1k: float = 0.0) -> float:
        """
        估算token使用成本。
        
        Args:
            token_usage: token使用量字典，包含 prompt_tokens 和 completion_tokens
            prompt_price_per_1k: 每1000个prompt tokens的价格（单位：元或美元）
            completion_price_per_1k: 每1000个completion tokens的价格（单位：元或美元）
            
        Returns:
            float: 估算的总成本
        """
        prompt_tokens = token_usage.get("prompt_tokens", 0)
        completion_tokens = token_usage.get("completion_tokens", 0)
        
        prompt_cost = (prompt_tokens / 1000.0) * prompt_price_per_1k
        completion_cost = (completion_tokens / 1000.0) * completion_price_per_1k
        
        return prompt_cost + completion_cost

    def get_daily_summary(self, date: Optional[str] = None) -> Dict:
        """
        获取指定日期的每日汇总统计。
        
        Args:
            date: 日期，格式 "YYYY-MM-DD"，如果为None则使用今天
            
        Returns:
            dict: 包含LLM和Agent的统计汇总
        """
        if date is None:
            date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        start_date = f"{date} 00:00:00"
        end_date = f"{date} 23:59:59"
        
        llm_stats = self.get_llm_statistics(start_date, end_date)
        agent_stats = self.get_agent_statistics(start_date, end_date)
        
        return {
            "date": date,
            "llm": llm_stats,
            "agent": agent_stats
        }
