# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/3/22 17:00
# @Author  : hiro
# @Email   : hiromesh@qq.com
# @FileName: run_command_tool.py

import os
import json
import time
import threading
import subprocess
import shlex
import re
from enum import Enum
from typing import Dict, Optional, List
from dataclasses import dataclass

from agentuniverse.agent.action.tool.tool import Tool, ToolInput


class CommandSecurityValidator:
    """命令安全验证器"""
    
    # 允许的命令白名单
    ALLOWED_COMMANDS = {
        'ls', 'pwd', 'cat', 'grep', 'find', 'head', 'tail', 'wc', 'sort', 'uniq',
        'echo', 'date', 'whoami', 'id', 'ps', 'top', 'df', 'du', 'free', 'uptime',
        'git', 'npm', 'pip', 'python', 'python3', 'node', 'java', 'javac'
    }
    
    # 危险的命令模式
    DANGEROUS_PATTERNS = [
        r'rm\s+(-rf\s+)?/',  # 删除根目录
        r'mkfs\.',           # 格式化文件系统
        r'dd\s+if=',         # 磁盘操作
        r'fdisk',            # 磁盘分区
        r'parted',           # 磁盘分区
        r'mount\s+',         # 挂载操作
        r'umount',           # 卸载操作
        r'chmod\s+777',      # 危险权限设置
        r'chown\s+root',     # 改变所有者
        r'sudo\s+',          # 提权操作
        r'su\s+',            # 切换用户
        r'passwd',           # 修改密码
        r'useradd',          # 添加用户
        r'userdel',          # 删除用户
        r'systemctl',        # 系统服务控制
        r'service',          # 服务控制
        r'kill\s+-9',        # 强制杀死进程
        r'pkill',            # 杀死进程
        r'killall',          # 杀死所有进程
    ]
    
    @classmethod
    def validate_command(cls, command: str) -> bool:
        """验证命令是否安全"""
        if not command or not command.strip():
            return False
        
        # 分割命令
        try:
            parts = shlex.split(command)
            if not parts:
                return False
            
            cmd = parts[0].lower()
            
            # 检查命令是否在白名单中
            if cmd not in cls.ALLOWED_COMMANDS:
                return False
            
            # 检查危险模式
            for pattern in cls.DANGEROUS_PATTERNS:
                if re.search(pattern, command, re.IGNORECASE):
                    return False
            
            # 检查路径遍历
            if '..' in command or command.startswith('/'):
                # 只允许访问当前目录及其子目录
                if any(part.startswith('/') for part in parts[1:]):
                    return False
            
            return True
            
        except Exception:
            return False
    
    @classmethod
    def sanitize_command(cls, command: str) -> str:
        """清理命令，移除危险字符"""
        # 移除控制字符和特殊字符
        sanitized = re.sub(r'[;&|`$(){}[\]\\]', '', command)
        return sanitized.strip()


class CommandStatus(Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class CommandResult:
    thread_id: int
    stdout: str
    stderr: str
    start_time: float
    status: CommandStatus
    exit_code: Optional[int] = None
    end_time: Optional[float] = None

    @property
    def duration(self) -> float:
        if self.end_time is None:
            return time.time() - self.start_time
        return self.end_time - self.start_time

    @property
    def message(self) -> str:
        # Truncate stdout and stderr if they are too long
        max_output_length = 2000
        truncated_stdout = self._truncate_output(
            self.stdout, max_output_length)
        truncated_stderr = self._truncate_output(
            self.stderr, max_output_length)

        result_dict = {
            'thread_id': self.thread_id,
            'status': self.status.value,
            'stdout': truncated_stdout,
            'stderr': truncated_stderr,
            'exit_code': self.exit_code,
            'duration': self.duration
        }
        return json.dumps(result_dict)

    def _truncate_output(self, output: str, max_length: int) -> str:
        """Truncate output to keep beginning and end, removing middle when too long"""
        if not output or len(output) <= max_length:
            return output
        half_length = max_length // 2
        return output[:half_length] + "\n... [truncated output] ...\n" + output[-half_length:]


_command_results: Dict[int, CommandResult] = {}


class RunCommandTool(Tool):
    """
    Tool for executing shell commands either synchronously or asynchronously.
    """

    def execute(self, command: str, cwd: str, blocking: bool = True) -> str:
        return self._run_command(command, cwd, blocking)

    def _run_command(self, command: str, cwd: str, blocking: bool = True) -> str:
        # 验证命令安全性
        if not CommandSecurityValidator.validate_command(command):
            error_result = CommandResult(
                thread_id=threading.get_ident(),
                status=CommandStatus.ERROR,
                stdout="",
                stderr=f"Command rejected for security reasons: {command}",
                start_time=time.time(),
                end_time=time.time(),
                exit_code=1
            )
            return error_result.message
        
        # 清理命令
        sanitized_command = CommandSecurityValidator.sanitize_command(command)
        
        result = CommandResult(
            thread_id=threading.get_ident(),
            status=CommandStatus.RUNNING,
            stdout="",
            stderr="",
            start_time=time.time(),
        )

        def __run() -> None:
            try:
                # 使用安全的命令执行方式
                command_parts = shlex.split(sanitized_command)
                process = subprocess.Popen(
                    command_parts,  # 使用参数列表而不是字符串
                    cwd=cwd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    shell=False  # 禁用shell执行
                )

                stdout, stderr = process.communicate(timeout=30)  # 添加超时
                exit_code = process.returncode

                result.stdout = stdout
                result.stderr = stderr
                result.exit_code = exit_code
                result.end_time = time.time()
                result.status = CommandStatus.COMPLETED if exit_code == 0 else CommandStatus.ERROR

            except subprocess.TimeoutExpired:
                process.kill()
                result.stderr = "Command execution timeout"
                result.end_time = time.time()
                result.status = CommandStatus.ERROR
                result.exit_code = -1
            except Exception as e:
                result.stderr = f"Execution error: {str(e)}"
                result.end_time = time.time()
                result.status = CommandStatus.ERROR
                result.exit_code = -1

            _command_results[result.thread_id] = result

        if blocking:
            __run()
        else:
            thread = threading.Thread(target=__run)
            thread.start()
            result.thread_id = thread.ident
            _command_results[result.thread_id] = result

        return result.message


def get_command_result(thread_id: int) -> Optional[CommandResult]:
    return _command_results.get(thread_id)
