# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @Author  : Yue Wang
# @FileName: fxmacrodata_tool.py

"""Bounded, fully offline FXMacroData-shaped reference tool.

Same public surface as the networked variant (modes history/calendar/catalogue/fx, identical result-key shapes) but zero network, credentials and wall-clock: a small embedded 2026 reference set answered by pure deterministic functions.
"""

import datetime as dt
from typing import Optional

from agentuniverse.agent.action.tool.tool import Tool

_MAX_LIMIT = 100
_EPOCH = dt.date(2026, 1, 1)
_INDICATORS = {'inflation': ('Inflation (CPI)', 3.1), 'policy_rate': ('Policy rate', 4.5),
               'unemployment': ('Unemployment rate', 4.2)}
# (base, quote) -> reference FX level; -0.3%..+0.3% deterministic daily drift around it.
_RATES = {('EUR', 'USD'): 1.08, ('USD', 'EUR'): 0.93, ('GBP', 'USD'): 1.27,
          ('USD', 'GBP'): 0.79, ('EUR', 'GBP'): 0.85, ('GBP', 'EUR'): 1.18}
_CALENDAR_MONTHS = (10, 11, 12)  # scheduled quarter of the fixed reference year
_FX_DEFAULT = (_EPOCH, _EPOCH + dt.timedelta(days=6))
_NOTICE = 'offline reference data: 12 monthly releases for 2026 (fixed window, no wall clock, no network).'


def _currency(value, field: str) -> str:
    if not isinstance(value, str) or not value.strip().isalpha() or len(value.strip()) != 3:
        raise ValueError(f"'{field}' must be a three-letter currency code (got {value!r}).")
    return value.strip().upper()


def _indicator(value) -> str:
    if not isinstance(value, str) or value.strip().lower() not in _INDICATORS:
        raise ValueError(f"'indicator' must be one of inflation, policy_rate, unemployment (got {value!r}).")
    return value.strip().lower()


def _limit(value) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= _MAX_LIMIT:
        raise ValueError(f"'limit' must be an integer from 1 to {_MAX_LIMIT} (got {value!r}).")
    return value


def _day(value, field: str) -> dt.date:
    text = value.strip() if isinstance(value, str) else ''
    if len(text) != 10 or text[4] != '-' or text[7] != '-':
        raise ValueError(f"'{field}' must be a YYYY-MM-DD date (got {value!r}).")
    try:
        return dt.date.fromisoformat(text)
    except ValueError:
        raise ValueError(f"'{field}' must be a real YYYY-MM-DD date (got {value!r}).") from None


def _window(start_date, end_date):
    """Optional YYYY-MM-DD window; unbounded sides default to the 2026 reference year."""
    if start_date is None and end_date is None:
        return None
    low = _EPOCH if start_date is None else _day(start_date, 'start_date')
    high = dt.date(2026, 12, 31) if end_date is None else _day(end_date, 'end_date')
    if low > high:
        raise ValueError(f"'start_date' must be on or before 'end_date' (got {low.isoformat()} > {high.isoformat()}).")
    return low, high


def _release_rows(currency: str, indicator: str) -> list:
    base = _INDICATORS[indicator][1]
    rows = []
    for month in range(1, 13):
        period = dt.date(2026, month, 1)
        published = period + dt.timedelta(days=14)
        rows.append({'period': period, 'value': round(base + 0.1 * (month - 1), 1),
                     'previous_value': round(base + 0.1 * (month - 2), 1) if month > 1 else None,
                     'announced_at_utc': f'{published.isoformat()}T14:30:00Z',
                     'announced_at_local': f'{published.isoformat()}T10:30:00-04:00',
                     'source_url': f'embedded://{currency}/{indicator}/{period.isoformat()}'})
    return rows


class FXMacroDataTool(Tool):
    """Bounded, offline FXMacroData-shaped reference: USD/EUR/GBP, fixed 2026 window."""

    name: str = 'fxmacrodata_tool'
    description: str = (
        'Bounded, offline FXMacroData-shaped reference: indicator release history, release calendar, '
        'indicator catalogue and daily FX rates for USD/EUR/GBP over a fixed 2026 window. No network, no wall clock, no credentials.')
    input_keys: list = ['mode']
    default_limit: int = 20

    def execute(self, mode: str, currency: Optional[str] = None, indicator: Optional[str] = None,
                base: Optional[str] = None, quote: Optional[str] = None, start_date: Optional[str] = None,
                end_date: Optional[str] = None, limit: Optional[int] = None) -> dict:
        """Run one bounded, offline lookup: success payload, or an error quoting the offending value."""
        args = {'currency': currency, 'indicator': indicator, 'base': base, 'quote': quote,
                'start_date': start_date, 'end_date': end_date,
                'limit': self.default_limit if limit is None else limit}
        handlers = {'history': self._history, 'calendar': self._calendar,
                    'catalogue': self._catalogue, 'fx': self._fx}
        try:
            if not isinstance(mode, str) or mode not in handlers:
                raise ValueError(f"'mode' must be one of history, calendar, catalogue, fx (got {mode!r}).")
            result = handlers[mode](args)
        except ValueError as error:
            return {'status': 'error', 'error': str(error)}
        except Exception:
            return {'status': 'error', 'error': 'FXMacroData reference lookup failed unexpectedly.'}
        return {'status': 'success', 'mode': mode, **result}

    def _history(self, args: dict) -> dict:
        currency = _currency(args['currency'], 'currency')
        indicator = _indicator(args['indicator'])
        bound = _limit(args['limit'])
        window = _window(args['start_date'], args['end_date'])
        rows = _release_rows(currency, indicator)
        if window:
            rows = [row for row in rows if window[0] <= row['period'] <= window[1]]
        limited = rows[:bound]
        return {'currency': currency, 'indicator': indicator, 'name': _INDICATORS[indicator][0],
                'releases': [dict(row, period=row['period'].isoformat()) for row in limited],
                'has_more': len(rows) > len(limited), 'notices': [_NOTICE]}

    def _calendar(self, args: dict) -> dict:
        currency = _currency(args['currency'], 'currency')
        indicator = _indicator(args['indicator']) if args['indicator'] is not None else None
        bound = _limit(args['limit'])
        events = []
        for month in _CALENDAR_MONTHS:
            published = (dt.date(2026, month, 1) + dt.timedelta(days=7)).isoformat()
            for slug in _INDICATORS:
                if indicator is not None and slug != indicator:
                    continue
                events.append({'release': slug, 'name': _INDICATORS[slug][0],
                               'release_time_utc': f'{published}T14:30:00Z',
                               'reference_period': f'2026-{month:02d}-01',
                               'importance': 'high' if slug == 'policy_rate' else 'medium'})
        return {'currency': currency, 'events': events[:bound]}

    def _catalogue(self, args: dict) -> dict:
        currency = _currency(args['currency'], 'currency')
        _limit(args['limit'])
        indicators = [{'indicator': slug, 'name': meta[0], 'unit': 'percent',
                       'latest_available_date': '2026-12-01', 'requires_api_key': False}
                      for slug, meta in _INDICATORS.items()]
        return {'currency': currency, 'indicators': indicators}

    def _fx(self, args: dict) -> dict:
        pair = (_currency(args['base'], 'base'), _currency(args['quote'], 'quote'))
        if pair[0] == pair[1]:
            raise ValueError(f"'base' and 'quote' must differ (got {pair[0]!r} and {pair[1]!r}).")
        bound = _limit(args['limit'])
        window = _window(args['start_date'], args['end_date']) or _FX_DEFAULT
        days = [window[0] + dt.timedelta(offset) for offset in range((window[1] - window[0]).days + 1)]
        capped = days[:bound]
        level = _RATES[pair]
        rates = [{'date': day.isoformat(),
                  'rate': round(level * (1 + 0.001 * ((day - _EPOCH).days % 7 - 3)), 6)} for day in capped]
        return {'pair': f'{pair[0]}/{pair[1]}', 'rates': rates, 'has_more': len(days) > len(capped)}
