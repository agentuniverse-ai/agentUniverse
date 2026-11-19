import unittest

from agentuniverse.agent.action.tool.common_tool import FXMacroDataTool
from agentuniverse.agent.action.tool.common_tool import fxmacrodata_tool as fxmodule


class FXMacroDataToolTest(unittest.TestCase):
    """One flat, ceremony-free test: frozen known answers + bounds + value-quoted errors.

    The implementation is deterministic and fully offline (embedded 2026 reference
    set, no wall clock), so these expectations are frozen exactly, forever.
    """

    def test_offline_reference_semantics(self):
        tool = FXMacroDataTool()
        # --- known answers (frozen) ---
        history = tool.execute(mode='history', currency='usd', indicator='inflation', limit=3)
        self.assertEqual({'status': 'success', 'mode': 'history', 'currency': 'USD',
                          'indicator': 'inflation', 'name': 'Inflation (CPI)'},
                         {key: history[key] for key in ('status', 'mode', 'currency', 'indicator', 'name')})
        self.assertEqual(history['releases'][0], {
            'period': '2026-01-01', 'value': 3.1, 'previous_value': None,
            'announced_at_utc': '2026-01-15T14:30:00Z', 'announced_at_local': '2026-01-15T10:30:00-04:00',
            'source_url': 'embedded://USD/inflation/2026-01-01'})
        self.assertEqual([row['value'] for row in history['releases']], [3.1, 3.2, 3.3])
        self.assertTrue(history['has_more'])
        self.assertEqual(history['notices'], [
            'offline reference data: 12 monthly releases for 2026 (fixed window, no wall clock, no network).'])
        full = tool.execute(mode='history', currency='USD', indicator='inflation', limit=100)
        self.assertEqual((len(full['releases']), full['releases'][-1]['value'], full['has_more']),
                         (12, 4.2, False))
        calendar = tool.execute(mode='calendar', currency='USD')
        self.assertEqual(len(calendar['events']), 9)
        self.assertEqual(calendar['events'][0], {
            'release': 'inflation', 'name': 'Inflation (CPI)', 'release_time_utc': '2026-10-08T14:30:00Z',
            'reference_period': '2026-10-01', 'importance': 'medium'})
        self.assertEqual([event['importance'] for event in tool.execute(
            mode='calendar', currency='USD', indicator='policy_rate', limit=100)['events']], ['high'] * 3)
        catalogue = tool.execute(mode='catalogue', currency='EUR')
        self.assertEqual([row['indicator'] for row in catalogue['indicators']],
                         ['inflation', 'policy_rate', 'unemployment'])
        self.assertEqual(catalogue['indicators'][2], {
            'indicator': 'unemployment', 'name': 'Unemployment rate', 'unit': 'percent',
            'latest_available_date': '2026-12-01', 'requires_api_key': False})
        fx = tool.execute(mode='fx', base='EUR', quote='USD')
        self.assertEqual(fx['pair'], 'EUR/USD')
        self.assertEqual((len(fx['rates']), fx['rates'][0], fx['rates'][-1]['rate'], fx['has_more']),
                         (7, {'date': '2026-01-01', 'rate': 1.07676}, 1.08324, False))
        windowed = tool.execute(mode='fx', base='USD', quote='GBP',
                                start_date='2026-02-01', end_date='2026-02-05', limit=3)
        self.assertEqual((windowed['rates'][0], windowed['has_more']),
                         ({'date': '2026-02-01', 'rate': 0.79}, True))
        # --- bounds discipline: every violation converts into a value-quoting error ---
        cases = [
            (dict(mode='history', currency='USA1', indicator='inflation'),
             "'currency' must be a three-letter currency code (got 'USA1')."),
            (dict(mode='history', currency='USD', indicator='nope'),
             "'indicator' must be one of inflation, policy_rate, unemployment (got 'nope')."),
            (dict(mode='history', currency='USD', indicator='inflation', limit=101),
             "'limit' must be an integer from 1 to 100 (got 101)."),
            (dict(mode='history', currency='USD', indicator='inflation', limit=0),
             "'limit' must be an integer from 1 to 100 (got 0)."),
            (dict(mode='history', currency='USD', indicator='inflation', limit='20'),
             "'limit' must be an integer from 1 to 100 (got '20')."),
            (dict(mode='bogus'), "'mode' must be one of history, calendar, catalogue, fx (got 'bogus')."),
            (dict(mode='fx', base='USD', quote='USD'),
             "'base' and 'quote' must differ (got 'USD' and 'USD')."),
            (dict(mode='fx', base='EUR', quote='USD', start_date='2026-02-01', end_date='2026-01-01'),
             "'start_date' must be on or before 'end_date' (got 2026-02-01 > 2026-01-01)."),
            (dict(mode='fx', base='EUR', quote='USD', start_date='2026-13-40'),
             "'start_date' must be a real YYYY-MM-DD date (got '2026-13-40')."),
        ]
        for kwargs, expected in cases:
            result = tool.execute(**kwargs)
            self.assertEqual(('error', expected), (result['status'], result['error']))
        # --- the discipline holds unconverted too: ValueError quotes the offending value ---
        with self.assertRaises(ValueError) as raised:
            fxmodule._limit(101)
        self.assertIn('101', str(raised.exception))
