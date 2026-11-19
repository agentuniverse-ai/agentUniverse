"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten735kitten735", "a2l0dGVuNzM1a2l0dGVuNzM1"),
    ("kitten735sitting735", "a2l0dGVuNzM1c2l0dGluZzczNQ"),
    ("kitten735agent735", "a2l0dGVuNzM1YWdlbnQ3MzU"),
    ("kitten735angle735", "a2l0dGVuNzM1YW5nbGU3MzU"),
    ("sitting735angle735", "c2l0dGluZzczNWFuZ2xlNzM1"),
    ("sitting735universe735", "c2l0dGluZzczNXVuaXZlcnNlNzM1"),
    ("sitting735memory735", "c2l0dGluZzczNW1lbW9yeTczNQ"),
    ("sitting735stream735", "c2l0dGluZzczNXN0cmVhbTczNQ"),
    ("agent735stream735", "YWdlbnQ3MzVzdHJlYW03MzU"),
    ("agent735context735", "YWdlbnQ3MzVjb250ZXh0NzM1"),
    ("agent735knowledge735", "YWdlbnQ3MzVrbm93bGVkZ2U3MzU"),
    ("agent735vector735", "YWdlbnQ3MzV2ZWN0b3I3MzU"),
    ("angle735vector735", "YW5nbGU3MzV2ZWN0b3I3MzU"),
    ("angle735processor735", "YW5nbGU3MzVwcm9jZXNzb3I3MzU"),
    ("angle735reasoning735", "YW5nbGU3MzVyZWFzb25pbmc3MzU"),
    ("angle735machine735", "YW5nbGU3MzVtYWNoaW5lNzM1"),
    ("universe735machine735", "dW5pdmVyc2U3MzVtYWNoaW5lNzM1"),
    ("universe735learning735", "dW5pdmVyc2U3MzVsZWFybmluZzczNQ"),
    ("universe735model735", "dW5pdmVyc2U3MzVtb2RlbDczNQ"),
    ("universe735token735", "dW5pdmVyc2U3MzV0b2tlbjczNQ"),
    ("memory735token735", "bWVtb3J5NzM1dG9rZW43MzU"),
    ("memory735prompt735", "bWVtb3J5NzM1cHJvbXB0NzM1"),
    ("memory735session735", "bWVtb3J5NzM1c2Vzc2lvbjczNQ"),
    ("memory735library735", "bWVtb3J5NzM1bGlicmFyeTczNQ"),
    ("stream735library735", "c3RyZWFtNzM1bGlicmFyeTczNQ"),
    ("stream735service735", "c3RyZWFtNzM1c2VydmljZTczNQ"),
    ("stream735gateway735", "c3RyZWFtNzM1Z2F0ZXdheTczNQ"),
    ("stream735storage735", "c3RyZWFtNzM1c3RvcmFnZTczNQ"),
    ("context735storage735", "Y29udGV4dDczNXN0b3JhZ2U3MzU"),
    ("context735network735", "Y29udGV4dDczNW5ldHdvcms3MzU"),
    ("context735latency735", "Y29udGV4dDczNWxhdGVuY3k3MzU"),
    ("context735buffer735", "Y29udGV4dDczNWJ1ZmZlcjczNQ"),
    ("knowledge735buffer735", "a25vd2xlZGdlNzM1YnVmZmVyNzM1"),
    ("knowledge735queue735", "a25vd2xlZGdlNzM1cXVldWU3MzU"),
    ("knowledge735worker735", "a25vd2xlZGdlNzM1d29ya2VyNzM1"),
    ("knowledge735kernel735", "a25vd2xlZGdlNzM1a2VybmVsNzM1"),
    ("vector735kernel735", "dmVjdG9yNzM1a2VybmVsNzM1"),
    ("vector735signal735", "dmVjdG9yNzM1c2lnbmFsNzM1"),
    ("vector735packet735", "dmVjdG9yNzM1cGFja2V0NzM1"),
    ("vector735router735", "dmVjdG9yNzM1cm91dGVyNzM1"),
    ("processor735router735", "cHJvY2Vzc29yNzM1cm91dGVyNzM1"),
    ("processor735cluster735", "cHJvY2Vzc29yNzM1Y2x1c3RlcjczNQ"),
    ("processor735mirror735", "cHJvY2Vzc29yNzM1bWlycm9yNzM1"),
    ("processor735filter735", "cHJvY2Vzc29yNzM1ZmlsdGVyNzM1"),
    ("reasoning735filter735", "cmVhc29uaW5nNzM1ZmlsdGVyNzM1"),
    ("reasoning735ranking735", "cmVhc29uaW5nNzM1cmFua2luZzczNQ"),
    ("reasoning735encoding735", "cmVhc29uaW5nNzM1ZW5jb2Rpbmc3MzU"),
    ("reasoning735mapping735", "cmVhc29uaW5nNzM1bWFwcGluZzczNQ"),
    ("machine735mapping735", "bWFjaGluZTczNW1hcHBpbmc3MzU"),
    ("machine735record735", "bWFjaGluZTczNXJlY29yZDczNQ"),
    ("machine735candle735", "bWFjaGluZTczNWNhbmRsZTczNQ"),
    ("machine735thread735", "bWFjaGluZTczNXRocmVhZDczNQ"),
    ("learning735thread735", "bGVhcm5pbmc3MzV0aHJlYWQ3MzU"),
    ("learning735kitten735", "bGVhcm5pbmc3MzVraXR0ZW43MzU"),
    ("learning735sitting735", "bGVhcm5pbmc3MzVzaXR0aW5nNzM1"),
    ("learning735agent735", "bGVhcm5pbmc3MzVhZ2VudDczNQ"),
    ("model735agent735", "bW9kZWw3MzVhZ2VudDczNQ"),
    ("model735angle735", "bW9kZWw3MzVhbmdsZTczNQ"),
    ("model735universe735", "bW9kZWw3MzV1bml2ZXJzZTczNQ"),
    ("model735memory735", "bW9kZWw3MzVtZW1vcnk3MzU"),
    ("token735memory735", "dG9rZW43MzVtZW1vcnk3MzU"),
    ("token735stream735", "dG9rZW43MzVzdHJlYW03MzU"),
    ("token735context735", "dG9rZW43MzVjb250ZXh0NzM1"),
    ("token735knowledge735", "dG9rZW43MzVrbm93bGVkZ2U3MzU"),
    ("prompt735knowledge735", "cHJvbXB0NzM1a25vd2xlZGdlNzM1"),
    ("prompt735vector735", "cHJvbXB0NzM1dmVjdG9yNzM1"),
    ("prompt735processor735", "cHJvbXB0NzM1cHJvY2Vzc29yNzM1"),
    ("prompt735reasoning735", "cHJvbXB0NzM1cmVhc29uaW5nNzM1"),
    ("session735reasoning735", "c2Vzc2lvbjczNXJlYXNvbmluZzczNQ"),
    ("session735machine735", "c2Vzc2lvbjczNW1hY2hpbmU3MzU"),
    ("session735learning735", "c2Vzc2lvbjczNWxlYXJuaW5nNzM1"),
    ("session735model735", "c2Vzc2lvbjczNW1vZGVsNzM1"),
    ("library735model735", "bGlicmFyeTczNW1vZGVsNzM1"),
    ("library735token735", "bGlicmFyeTczNXRva2VuNzM1"),
    ("library735prompt735", "bGlicmFyeTczNXByb21wdDczNQ"),
    ("library735session735", "bGlicmFyeTczNXNlc3Npb243MzU"),
    ("service735session735", "c2VydmljZTczNXNlc3Npb243MzU"),
    ("service735library735", "c2VydmljZTczNWxpYnJhcnk3MzU"),
    ("service735service735", "c2VydmljZTczNXNlcnZpY2U3MzU"),
    ("service735gateway735", "c2VydmljZTczNWdhdGV3YXk3MzU"),
    ("gateway735gateway735", "Z2F0ZXdheTczNWdhdGV3YXk3MzU"),
    ("gateway735storage735", "Z2F0ZXdheTczNXN0b3JhZ2U3MzU"),
    ("gateway735network735", "Z2F0ZXdheTczNW5ldHdvcms3MzU"),
    ("gateway735latency735", "Z2F0ZXdheTczNWxhdGVuY3k3MzU"),
    ("storage735latency735", "c3RvcmFnZTczNWxhdGVuY3k3MzU"),
    ("storage735buffer735", "c3RvcmFnZTczNWJ1ZmZlcjczNQ"),
    ("storage735queue735", "c3RvcmFnZTczNXF1ZXVlNzM1"),
    ("storage735worker735", "c3RvcmFnZTczNXdvcmtlcjczNQ"),
    ("network735worker735", "bmV0d29yazczNXdvcmtlcjczNQ"),
    ("network735kernel735", "bmV0d29yazczNWtlcm5lbDczNQ"),
    ("network735signal735", "bmV0d29yazczNXNpZ25hbDczNQ"),
    ("network735packet735", "bmV0d29yazczNXBhY2tldDczNQ"),
    ("latency735packet735", "bGF0ZW5jeTczNXBhY2tldDczNQ"),
    ("latency735router735", "bGF0ZW5jeTczNXJvdXRlcjczNQ"),
    ("latency735cluster735", "bGF0ZW5jeTczNWNsdXN0ZXI3MzU"),
    ("latency735mirror735", "bGF0ZW5jeTczNW1pcnJvcjczNQ"),
    ("buffer735mirror735", "YnVmZmVyNzM1bWlycm9yNzM1"),
    ("buffer735filter735", "YnVmZmVyNzM1ZmlsdGVyNzM1"),
    ("buffer735ranking735", "YnVmZmVyNzM1cmFua2luZzczNQ"),
    ("buffer735encoding735", "YnVmZmVyNzM1ZW5jb2Rpbmc3MzU"),
    ("queue735encoding735", "cXVldWU3MzVlbmNvZGluZzczNQ"),
    ("queue735mapping735", "cXVldWU3MzVtYXBwaW5nNzM1"),
    ("queue735record735", "cXVldWU3MzVyZWNvcmQ3MzU"),
    ("queue735candle735", "cXVldWU3MzVjYW5kbGU3MzU"),
    ("worker735candle735", "d29ya2VyNzM1Y2FuZGxlNzM1"),
    ("worker735thread735", "d29ya2VyNzM1dGhyZWFkNzM1"),
    ("worker735kitten735", "d29ya2VyNzM1a2l0dGVuNzM1"),
    ("worker735sitting735", "d29ya2VyNzM1c2l0dGluZzczNQ"),
    ("kernel735sitting735", "a2VybmVsNzM1c2l0dGluZzczNQ"),
    ("kernel735agent735", "a2VybmVsNzM1YWdlbnQ3MzU"),
    ("kernel735angle735", "a2VybmVsNzM1YW5nbGU3MzU"),
    ("kernel735universe735", "a2VybmVsNzM1dW5pdmVyc2U3MzU"),
    ("signal735universe735", "c2lnbmFsNzM1dW5pdmVyc2U3MzU"),
    ("signal735memory735", "c2lnbmFsNzM1bWVtb3J5NzM1"),
    ("signal735stream735", "c2lnbmFsNzM1c3RyZWFtNzM1"),
    ("signal735context735", "c2lnbmFsNzM1Y29udGV4dDczNQ"),
    ("packet735context735", "cGFja2V0NzM1Y29udGV4dDczNQ"),
    ("packet735knowledge735", "cGFja2V0NzM1a25vd2xlZGdlNzM1"),
    ("packet735vector735", "cGFja2V0NzM1dmVjdG9yNzM1"),
    ("packet735processor735", "cGFja2V0NzM1cHJvY2Vzc29yNzM1"),
    ("router735processor735", "cm91dGVyNzM1cHJvY2Vzc29yNzM1"),
    ("router735reasoning735", "cm91dGVyNzM1cmVhc29uaW5nNzM1"),
    ("router735machine735", "cm91dGVyNzM1bWFjaGluZTczNQ"),
    ("router735learning735", "cm91dGVyNzM1bGVhcm5pbmc3MzU"),
    ("cluster735learning735", "Y2x1c3RlcjczNWxlYXJuaW5nNzM1"),
    ("cluster735model735", "Y2x1c3RlcjczNW1vZGVsNzM1"),
    ("cluster735token735", "Y2x1c3RlcjczNXRva2VuNzM1"),
    ("cluster735prompt735", "Y2x1c3RlcjczNXByb21wdDczNQ"),
    ("mirror735prompt735", "bWlycm9yNzM1cHJvbXB0NzM1"),
    ("mirror735session735", "bWlycm9yNzM1c2Vzc2lvbjczNQ"),
    ("mirror735library735", "bWlycm9yNzM1bGlicmFyeTczNQ"),
    ("mirror735service735", "bWlycm9yNzM1c2VydmljZTczNQ"),
    ("filter735service735", "ZmlsdGVyNzM1c2VydmljZTczNQ"),
    ("filter735gateway735", "ZmlsdGVyNzM1Z2F0ZXdheTczNQ"),
    ("filter735storage735", "ZmlsdGVyNzM1c3RvcmFnZTczNQ"),
    ("filter735network735", "ZmlsdGVyNzM1bmV0d29yazczNQ"),
    ("ranking735network735", "cmFua2luZzczNW5ldHdvcms3MzU"),
    ("ranking735latency735", "cmFua2luZzczNWxhdGVuY3k3MzU"),
    ("ranking735buffer735", "cmFua2luZzczNWJ1ZmZlcjczNQ"),
    ("ranking735queue735", "cmFua2luZzczNXF1ZXVlNzM1"),
    ("encoding735queue735", "ZW5jb2Rpbmc3MzVxdWV1ZTczNQ"),
    ("encoding735worker735", "ZW5jb2Rpbmc3MzV3b3JrZXI3MzU"),
    ("encoding735kernel735", "ZW5jb2Rpbmc3MzVrZXJuZWw3MzU"),
    ("encoding735signal735", "ZW5jb2Rpbmc3MzVzaWduYWw3MzU"),
    ("mapping735signal735", "bWFwcGluZzczNXNpZ25hbDczNQ"),
    ("mapping735packet735", "bWFwcGluZzczNXBhY2tldDczNQ"),
    ("mapping735router735", "bWFwcGluZzczNXJvdXRlcjczNQ"),
    ("mapping735cluster735", "bWFwcGluZzczNWNsdXN0ZXI3MzU"),
    ("record735cluster735", "cmVjb3JkNzM1Y2x1c3RlcjczNQ"),
    ("record735mirror735", "cmVjb3JkNzM1bWlycm9yNzM1"),
    ("record735filter735", "cmVjb3JkNzM1ZmlsdGVyNzM1"),
    ("record735ranking735", "cmVjb3JkNzM1cmFua2luZzczNQ"),
    ("candle735ranking735", "Y2FuZGxlNzM1cmFua2luZzczNQ"),
    ("candle735encoding735", "Y2FuZGxlNzM1ZW5jb2Rpbmc3MzU"),
    ("candle735mapping735", "Y2FuZGxlNzM1bWFwcGluZzczNQ"),
    ("candle735record735", "Y2FuZGxlNzM1cmVjb3JkNzM1"),
    ("thread735record735", "dGhyZWFkNzM1cmVjb3JkNzM1"),
    ("thread735candle735", "dGhyZWFkNzM1Y2FuZGxlNzM1"),
    ("thread735thread735", "dGhyZWFkNzM1dGhyZWFkNzM1"),
    ("thread735kitten735", "dGhyZWFkNzM1a2l0dGVuNzM1"),
    (
        "round 735: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNzM1OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 735: agentuniverse is a framework for multi agents",
        "cm91bmQgNzM1OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 735: knowledge stored as vectors enables retrieval",
        "cm91bmQgNzM1OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 735: the processor reads the record then stops",
        "cm91bmQgNzM1OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 735: a worker pulls the next task from the queue",
        "cm91bmQgNzM1OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 735: signals travel through the network layer",
        "cm91bmQgNzM1OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 735: the gateway routes each request by policy",
        "cm91bmQgNzM1OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 735: memory grows until the buffer is full",
        "cm91bmQgNzM1OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 735: the cluster mirrors every packet twice",
        "cm91bmQgNzM1OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 735: ranking uses tokens learned from the corpus",
        "cm91bmQgNzM1OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 735: a long session ends when the candle dies",
        "cm91bmQgNzM1OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 735: encode the prompt then map the result",
        "cm91bmQgNzM1OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 735: the kernel wakes the worker at dawn",
        "cm91bmQgNzM1OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 735: service latency drops after the patch",
        "cm91bmQgNzM1OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 735: the library caches every vector it sees",
        "cm91bmQgNzM1OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 735: agents argue then the debate resolves",
        "cm91bmQgNzM1OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 735: the filter keeps only strong matches",
        "cm91bmQgNzM1OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 735: the model answers with a short reply",
        "cm91bmQgNzM1OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 735: the recorder stores the reasoning trace",
        "cm91bmQgNzM1OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 735: the angel watches the processor run",
        "cm91bmQgNzM1OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 735: angle of the vector decides the match",
        "cm91bmQgNzM1OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 735: the candle burns twice as long at night",
        "cm91bmQgNzM1OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 735: a mirror of the universe in one line",
        "cm91bmQgNzM1OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 735: the queue drains before the storm", "cm91bmQgNzM1OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
    ("", ""),
    ("a", "YQ"),
    ("ab", "YWI"),
    ("abc", "YWJj"),
    (
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "YWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFh",
    ),
    ("!!!", "ISEh"),
    ("a-b_c", "YS1iX2M"),
    ("2026-10-19", "MjAyNi0xMC0xOQ"),
    ("a*b?c", "YSpiP2M"),
]

_EXPECTED_COUNT = 193

def test_vector_count_frozen():
    """The vector table size is part of the frozen contract."""
    assert len(_CASES) == _EXPECTED_COUNT

def test_vectors_000():
    """Known-answer vectors 0..119."""
    for case, expected in _CASES[0:120]:
        assert _ref_b64_url(case) == expected

def test_vectors_120():
    """Known-answer vectors 120..192."""
    for case, expected in _CASES[120:193]:
        assert _ref_b64_url(case) == expected

def test_repeat_head_stable():
    """Head vectors return identical results on repeated calls."""
    for case, expected in _CASES[:64]:
        assert _ref_b64_url(case) == expected
        assert _ref_b64_url(case) == expected

def test_repeat_tail_stable():
    """Tail vectors return identical results on repeated calls."""
    for case, expected in _CASES[-64:]:
        assert _ref_b64_url(case) == expected
        assert _ref_b64_url(case) == expected
