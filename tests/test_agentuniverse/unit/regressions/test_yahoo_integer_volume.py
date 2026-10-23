"""Keep exact integer volumes through public quote/history rendering."""
from types import SimpleNamespace

import pandas as pd
import pytest

from agentuniverse.agent.action.tool.common_tool.yahoo_finance_tool import YahooFinanceTool


@pytest.mark.parametrize('volume', [2**53 + 1, 2**63 - 1, -(2**53 + 1)])
@pytest.mark.parametrize('mode', ['quote', 'history'])
def test_execute_preserves_integer_volume(monkeypatch, volume, mode):
    frame = pd.DataFrame({
        'Open': [1.0], 'High': [2.0], 'Low': [0.5], 'Close': [1.5],
        'Volume': pd.Series([volume], dtype='int64'),
    })
    frame.index = pd.DatetimeIndex(['2026-01-02'], name='Date')
    ticker = SimpleNamespace(
        info={'regularMarketVolume': volume},
        history=lambda **kwargs: frame,
    )
    monkeypatch.setattr(YahooFinanceTool, '_get_ticker', lambda self, symbol: ticker)
    result = YahooFinanceTool().execute(mode=mode, symbol='TEST')
    assert f'{volume:,}' in result


@pytest.mark.parametrize('value, expected', [
    ('9007199254740993', '9,007,199,254,740,993'),
    (None, '-'), (1234, '1,234'), (1234.9, '1,234'),
    ('1234.9', '1,234'), ('1e3', '1,000'), ('unknown', 'unknown'),
])
def test_integer_formatter_compatibility(value, expected):
    assert YahooFinanceTool._fmt_int(value) == expected
