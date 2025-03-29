from abc import ABC, abstractmethod
import re
from typing import Any, Dict, List, Optional
import random
import hashlib

from agentuniverse.agent.action.tool.enum import ToolTypeEnum
from agentuniverse.agent.action.tool.tool import ToolInput


class MaskingStrategy(ABC):
    """Abstract base class for masking strategies"""

    @abstractmethod
    def mask(self, value: str) -> str:
        """Mask the given value according to the strategy"""
        pass

class FullMaskingStrategy(MaskingStrategy):
    """Replace all characters with a masking character"""

    def __init__(self, mask_char: str = '*'):
        self.mask_char = mask_char

    def mask(self, value: str) -> str:
        return self.mask_char * len(value)

class PartialMaskingStrategy(MaskingStrategy):
    """Keep some characters visible while masking others"""

    def __init__(self, visible_start: int = 2, visible_end: int = 2, mask_char: str = '*'):
        self.visible_start = visible_start
        self.visible_end = visible_end
        self.mask_char = mask_char

    def mask(self, value: str) -> str:
        if len(value) <= (self.visible_start + self.visible_end):
            return value

        masked_part = self.mask_char * (len(value) - self.visible_start - self.visible_end)
        return value[:self.visible_start] + masked_part + value[-self.visible_end:]

class EmailMaskingStrategy(MaskingStrategy):
    """Specific strategy for masking email addresses"""

    def __init__(self, mask_char: str = '*'):
        self.mask_char = mask_char

    def mask(self, value: str) -> str:
        if '@' not in value:
            return value

        username, domain = value.split('@')
        if len(username) <= 2:
            masked_username = username
        else:
            masked_username = username[0] + self.mask_char * (len(username) - 2) + username[-1]

        return f"{masked_username}@{domain}"

class HashMaskingStrategy(MaskingStrategy):
    """Hash the entire value using SHA-256"""

    def mask(self, value: str) -> str:
        return hashlib.sha256(value.encode()).hexdigest()

class DataMasker:
    """数据脱敏工具"""

    strategies: Dict[str, MaskingStrategy] = {
        'full': FullMaskingStrategy(),
        'partial': PartialMaskingStrategy(),
        'email': EmailMaskingStrategy(),
        'hash': HashMaskingStrategy(),
        'id_card': PartialMaskingStrategy(visible_start=6, visible_end=4),
        'phone': PartialMaskingStrategy(visible_start=3, visible_end=4),
        'bank_card': PartialMaskingStrategy(visible_start=4, visible_end=4)
    }

    # 更新为中国大陆的敏感数据模式
    patterns: Dict[str, str] = {
        'email': r'^[\w\.-]+@[\w\.-]+\.\w+$',
        'id_card': r'^[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]$',
        'bank_card': r'^\d{16,19}$',
        'phone': r'^1[3-9]\d{9}$'
    }

    def __init__(self):
        super().__init__()
        self.tool_type = ToolTypeEnum.FUNC
        self.name = "data_masker"
        self.description = "Mask sensitive information in text like phone numbers, ID cards and names"
        self.input_keys = ["text"]

    def add_strategy(self, name: str, strategy: MaskingStrategy) -> None:
        """Add a new masking strategy"""
        self.strategies[name] = strategy

    def add_pattern(self, name: str, pattern: str) -> None:
        """Add a new pattern for identifying sensitive data"""
        self.patterns[name] = pattern

    def mask_value(self, value: Any, strategy_name: str = 'full') -> str:
        """Mask a single value using the specified strategy"""
        if not isinstance(value, str):
            value = str(value)

        strategy = self.strategies.get(strategy_name)
        if not strategy:
            raise ValueError(f"Unknown masking strategy: {strategy_name}")

        return strategy.mask(value)

    def detect_and_mask(self, value: Any) -> str:
        """自动检测并应用脱敏策略"""
        if not isinstance(value, str):
            value = str(value)

        # 定义匹配优先级（当多个正则可能匹配时）
        priority_order = ['id_card', 'bank_card', 'phone', 'email']

        for data_type in priority_order:
            pattern = self.patterns.get(data_type)
            if pattern and re.match(pattern, value):
                if data_type == 'id_card':
                    return self.strategies['id_card'].mask(value)
                elif data_type == 'bank_card':
                    return self.strategies['bank_card'].mask(value)
                elif data_type == 'phone':
                    return self.strategies['phone'].mask(value)
                elif data_type == 'email':
                    return self.strategies['email'].mask(value)

        # 其他未匹配的敏感数据类型保持原样
        return value

    def mask_dict(self, data: Dict[str, Any], fields_to_mask: Dict[str, str]) -> Dict[str, Any]:
        """Mask specified fields in a dictionary using designated strategies"""
        masked_data = data.copy()
        for field, strategy_name in fields_to_mask.items():
            if field in masked_data:
                masked_data[field] = self.mask_value(masked_data[field], strategy_name)
        return masked_data

    def execute(self, tool_input: ToolInput) -> str:
        self.input_check(tool_input.to_dict())
        return self.detect_and_mask(tool_input.get_data("text"))