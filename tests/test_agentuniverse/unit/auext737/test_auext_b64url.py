"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten737kitten737", "a2l0dGVuNzM3a2l0dGVuNzM3"),
    ("kitten737sitting737", "a2l0dGVuNzM3c2l0dGluZzczNw"),
    ("kitten737agent737", "a2l0dGVuNzM3YWdlbnQ3Mzc"),
    ("kitten737angle737", "a2l0dGVuNzM3YW5nbGU3Mzc"),
    ("sitting737angle737", "c2l0dGluZzczN2FuZ2xlNzM3"),
    ("sitting737universe737", "c2l0dGluZzczN3VuaXZlcnNlNzM3"),
    ("sitting737memory737", "c2l0dGluZzczN21lbW9yeTczNw"),
    ("sitting737stream737", "c2l0dGluZzczN3N0cmVhbTczNw"),
    ("agent737stream737", "YWdlbnQ3MzdzdHJlYW03Mzc"),
    ("agent737context737", "YWdlbnQ3Mzdjb250ZXh0NzM3"),
    ("agent737knowledge737", "YWdlbnQ3Mzdrbm93bGVkZ2U3Mzc"),
    ("agent737vector737", "YWdlbnQ3Mzd2ZWN0b3I3Mzc"),
    ("angle737vector737", "YW5nbGU3Mzd2ZWN0b3I3Mzc"),
    ("angle737processor737", "YW5nbGU3Mzdwcm9jZXNzb3I3Mzc"),
    ("angle737reasoning737", "YW5nbGU3MzdyZWFzb25pbmc3Mzc"),
    ("angle737machine737", "YW5nbGU3MzdtYWNoaW5lNzM3"),
    ("universe737machine737", "dW5pdmVyc2U3MzdtYWNoaW5lNzM3"),
    ("universe737learning737", "dW5pdmVyc2U3MzdsZWFybmluZzczNw"),
    ("universe737model737", "dW5pdmVyc2U3Mzdtb2RlbDczNw"),
    ("universe737token737", "dW5pdmVyc2U3Mzd0b2tlbjczNw"),
    ("memory737token737", "bWVtb3J5NzM3dG9rZW43Mzc"),
    ("memory737prompt737", "bWVtb3J5NzM3cHJvbXB0NzM3"),
    ("memory737session737", "bWVtb3J5NzM3c2Vzc2lvbjczNw"),
    ("memory737library737", "bWVtb3J5NzM3bGlicmFyeTczNw"),
    ("stream737library737", "c3RyZWFtNzM3bGlicmFyeTczNw"),
    ("stream737service737", "c3RyZWFtNzM3c2VydmljZTczNw"),
    ("stream737gateway737", "c3RyZWFtNzM3Z2F0ZXdheTczNw"),
    ("stream737storage737", "c3RyZWFtNzM3c3RvcmFnZTczNw"),
    ("context737storage737", "Y29udGV4dDczN3N0b3JhZ2U3Mzc"),
    ("context737network737", "Y29udGV4dDczN25ldHdvcms3Mzc"),
    ("context737latency737", "Y29udGV4dDczN2xhdGVuY3k3Mzc"),
    ("context737buffer737", "Y29udGV4dDczN2J1ZmZlcjczNw"),
    ("knowledge737buffer737", "a25vd2xlZGdlNzM3YnVmZmVyNzM3"),
    ("knowledge737queue737", "a25vd2xlZGdlNzM3cXVldWU3Mzc"),
    ("knowledge737worker737", "a25vd2xlZGdlNzM3d29ya2VyNzM3"),
    ("knowledge737kernel737", "a25vd2xlZGdlNzM3a2VybmVsNzM3"),
    ("vector737kernel737", "dmVjdG9yNzM3a2VybmVsNzM3"),
    ("vector737signal737", "dmVjdG9yNzM3c2lnbmFsNzM3"),
    ("vector737packet737", "dmVjdG9yNzM3cGFja2V0NzM3"),
    ("vector737router737", "dmVjdG9yNzM3cm91dGVyNzM3"),
    ("processor737router737", "cHJvY2Vzc29yNzM3cm91dGVyNzM3"),
    ("processor737cluster737", "cHJvY2Vzc29yNzM3Y2x1c3RlcjczNw"),
    ("processor737mirror737", "cHJvY2Vzc29yNzM3bWlycm9yNzM3"),
    ("processor737filter737", "cHJvY2Vzc29yNzM3ZmlsdGVyNzM3"),
    ("reasoning737filter737", "cmVhc29uaW5nNzM3ZmlsdGVyNzM3"),
    ("reasoning737ranking737", "cmVhc29uaW5nNzM3cmFua2luZzczNw"),
    ("reasoning737encoding737", "cmVhc29uaW5nNzM3ZW5jb2Rpbmc3Mzc"),
    ("reasoning737mapping737", "cmVhc29uaW5nNzM3bWFwcGluZzczNw"),
    ("machine737mapping737", "bWFjaGluZTczN21hcHBpbmc3Mzc"),
    ("machine737record737", "bWFjaGluZTczN3JlY29yZDczNw"),
    ("machine737candle737", "bWFjaGluZTczN2NhbmRsZTczNw"),
    ("machine737thread737", "bWFjaGluZTczN3RocmVhZDczNw"),
    ("learning737thread737", "bGVhcm5pbmc3Mzd0aHJlYWQ3Mzc"),
    ("learning737kitten737", "bGVhcm5pbmc3MzdraXR0ZW43Mzc"),
    ("learning737sitting737", "bGVhcm5pbmc3MzdzaXR0aW5nNzM3"),
    ("learning737agent737", "bGVhcm5pbmc3MzdhZ2VudDczNw"),
    ("model737agent737", "bW9kZWw3MzdhZ2VudDczNw"),
    ("model737angle737", "bW9kZWw3MzdhbmdsZTczNw"),
    ("model737universe737", "bW9kZWw3Mzd1bml2ZXJzZTczNw"),
    ("model737memory737", "bW9kZWw3MzdtZW1vcnk3Mzc"),
    ("token737memory737", "dG9rZW43MzdtZW1vcnk3Mzc"),
    ("token737stream737", "dG9rZW43MzdzdHJlYW03Mzc"),
    ("token737context737", "dG9rZW43Mzdjb250ZXh0NzM3"),
    ("token737knowledge737", "dG9rZW43Mzdrbm93bGVkZ2U3Mzc"),
    ("prompt737knowledge737", "cHJvbXB0NzM3a25vd2xlZGdlNzM3"),
    ("prompt737vector737", "cHJvbXB0NzM3dmVjdG9yNzM3"),
    ("prompt737processor737", "cHJvbXB0NzM3cHJvY2Vzc29yNzM3"),
    ("prompt737reasoning737", "cHJvbXB0NzM3cmVhc29uaW5nNzM3"),
    ("session737reasoning737", "c2Vzc2lvbjczN3JlYXNvbmluZzczNw"),
    ("session737machine737", "c2Vzc2lvbjczN21hY2hpbmU3Mzc"),
    ("session737learning737", "c2Vzc2lvbjczN2xlYXJuaW5nNzM3"),
    ("session737model737", "c2Vzc2lvbjczN21vZGVsNzM3"),
    ("library737model737", "bGlicmFyeTczN21vZGVsNzM3"),
    ("library737token737", "bGlicmFyeTczN3Rva2VuNzM3"),
    ("library737prompt737", "bGlicmFyeTczN3Byb21wdDczNw"),
    ("library737session737", "bGlicmFyeTczN3Nlc3Npb243Mzc"),
    ("service737session737", "c2VydmljZTczN3Nlc3Npb243Mzc"),
    ("service737library737", "c2VydmljZTczN2xpYnJhcnk3Mzc"),
    ("service737service737", "c2VydmljZTczN3NlcnZpY2U3Mzc"),
    ("service737gateway737", "c2VydmljZTczN2dhdGV3YXk3Mzc"),
    ("gateway737gateway737", "Z2F0ZXdheTczN2dhdGV3YXk3Mzc"),
    ("gateway737storage737", "Z2F0ZXdheTczN3N0b3JhZ2U3Mzc"),
    ("gateway737network737", "Z2F0ZXdheTczN25ldHdvcms3Mzc"),
    ("gateway737latency737", "Z2F0ZXdheTczN2xhdGVuY3k3Mzc"),
    ("storage737latency737", "c3RvcmFnZTczN2xhdGVuY3k3Mzc"),
    ("storage737buffer737", "c3RvcmFnZTczN2J1ZmZlcjczNw"),
    ("storage737queue737", "c3RvcmFnZTczN3F1ZXVlNzM3"),
    ("storage737worker737", "c3RvcmFnZTczN3dvcmtlcjczNw"),
    ("network737worker737", "bmV0d29yazczN3dvcmtlcjczNw"),
    ("network737kernel737", "bmV0d29yazczN2tlcm5lbDczNw"),
    ("network737signal737", "bmV0d29yazczN3NpZ25hbDczNw"),
    ("network737packet737", "bmV0d29yazczN3BhY2tldDczNw"),
    ("latency737packet737", "bGF0ZW5jeTczN3BhY2tldDczNw"),
    ("latency737router737", "bGF0ZW5jeTczN3JvdXRlcjczNw"),
    ("latency737cluster737", "bGF0ZW5jeTczN2NsdXN0ZXI3Mzc"),
    ("latency737mirror737", "bGF0ZW5jeTczN21pcnJvcjczNw"),
    ("buffer737mirror737", "YnVmZmVyNzM3bWlycm9yNzM3"),
    ("buffer737filter737", "YnVmZmVyNzM3ZmlsdGVyNzM3"),
    ("buffer737ranking737", "YnVmZmVyNzM3cmFua2luZzczNw"),
    ("buffer737encoding737", "YnVmZmVyNzM3ZW5jb2Rpbmc3Mzc"),
    ("queue737encoding737", "cXVldWU3MzdlbmNvZGluZzczNw"),
    ("queue737mapping737", "cXVldWU3MzdtYXBwaW5nNzM3"),
    ("queue737record737", "cXVldWU3MzdyZWNvcmQ3Mzc"),
    ("queue737candle737", "cXVldWU3MzdjYW5kbGU3Mzc"),
    ("worker737candle737", "d29ya2VyNzM3Y2FuZGxlNzM3"),
    ("worker737thread737", "d29ya2VyNzM3dGhyZWFkNzM3"),
    ("worker737kitten737", "d29ya2VyNzM3a2l0dGVuNzM3"),
    ("worker737sitting737", "d29ya2VyNzM3c2l0dGluZzczNw"),
    ("kernel737sitting737", "a2VybmVsNzM3c2l0dGluZzczNw"),
    ("kernel737agent737", "a2VybmVsNzM3YWdlbnQ3Mzc"),
    ("kernel737angle737", "a2VybmVsNzM3YW5nbGU3Mzc"),
    ("kernel737universe737", "a2VybmVsNzM3dW5pdmVyc2U3Mzc"),
    ("signal737universe737", "c2lnbmFsNzM3dW5pdmVyc2U3Mzc"),
    ("signal737memory737", "c2lnbmFsNzM3bWVtb3J5NzM3"),
    ("signal737stream737", "c2lnbmFsNzM3c3RyZWFtNzM3"),
    ("signal737context737", "c2lnbmFsNzM3Y29udGV4dDczNw"),
    ("packet737context737", "cGFja2V0NzM3Y29udGV4dDczNw"),
    ("packet737knowledge737", "cGFja2V0NzM3a25vd2xlZGdlNzM3"),
    ("packet737vector737", "cGFja2V0NzM3dmVjdG9yNzM3"),
    ("packet737processor737", "cGFja2V0NzM3cHJvY2Vzc29yNzM3"),
    ("router737processor737", "cm91dGVyNzM3cHJvY2Vzc29yNzM3"),
    ("router737reasoning737", "cm91dGVyNzM3cmVhc29uaW5nNzM3"),
    ("router737machine737", "cm91dGVyNzM3bWFjaGluZTczNw"),
    ("router737learning737", "cm91dGVyNzM3bGVhcm5pbmc3Mzc"),
    ("cluster737learning737", "Y2x1c3RlcjczN2xlYXJuaW5nNzM3"),
    ("cluster737model737", "Y2x1c3RlcjczN21vZGVsNzM3"),
    ("cluster737token737", "Y2x1c3RlcjczN3Rva2VuNzM3"),
    ("cluster737prompt737", "Y2x1c3RlcjczN3Byb21wdDczNw"),
    ("mirror737prompt737", "bWlycm9yNzM3cHJvbXB0NzM3"),
    ("mirror737session737", "bWlycm9yNzM3c2Vzc2lvbjczNw"),
    ("mirror737library737", "bWlycm9yNzM3bGlicmFyeTczNw"),
    ("mirror737service737", "bWlycm9yNzM3c2VydmljZTczNw"),
    ("filter737service737", "ZmlsdGVyNzM3c2VydmljZTczNw"),
    ("filter737gateway737", "ZmlsdGVyNzM3Z2F0ZXdheTczNw"),
    ("filter737storage737", "ZmlsdGVyNzM3c3RvcmFnZTczNw"),
    ("filter737network737", "ZmlsdGVyNzM3bmV0d29yazczNw"),
    ("ranking737network737", "cmFua2luZzczN25ldHdvcms3Mzc"),
    ("ranking737latency737", "cmFua2luZzczN2xhdGVuY3k3Mzc"),
    ("ranking737buffer737", "cmFua2luZzczN2J1ZmZlcjczNw"),
    ("ranking737queue737", "cmFua2luZzczN3F1ZXVlNzM3"),
    ("encoding737queue737", "ZW5jb2Rpbmc3MzdxdWV1ZTczNw"),
    ("encoding737worker737", "ZW5jb2Rpbmc3Mzd3b3JrZXI3Mzc"),
    ("encoding737kernel737", "ZW5jb2Rpbmc3MzdrZXJuZWw3Mzc"),
    ("encoding737signal737", "ZW5jb2Rpbmc3MzdzaWduYWw3Mzc"),
    ("mapping737signal737", "bWFwcGluZzczN3NpZ25hbDczNw"),
    ("mapping737packet737", "bWFwcGluZzczN3BhY2tldDczNw"),
    ("mapping737router737", "bWFwcGluZzczN3JvdXRlcjczNw"),
    ("mapping737cluster737", "bWFwcGluZzczN2NsdXN0ZXI3Mzc"),
    ("record737cluster737", "cmVjb3JkNzM3Y2x1c3RlcjczNw"),
    ("record737mirror737", "cmVjb3JkNzM3bWlycm9yNzM3"),
    ("record737filter737", "cmVjb3JkNzM3ZmlsdGVyNzM3"),
    ("record737ranking737", "cmVjb3JkNzM3cmFua2luZzczNw"),
    ("candle737ranking737", "Y2FuZGxlNzM3cmFua2luZzczNw"),
    ("candle737encoding737", "Y2FuZGxlNzM3ZW5jb2Rpbmc3Mzc"),
    ("candle737mapping737", "Y2FuZGxlNzM3bWFwcGluZzczNw"),
    ("candle737record737", "Y2FuZGxlNzM3cmVjb3JkNzM3"),
    ("thread737record737", "dGhyZWFkNzM3cmVjb3JkNzM3"),
    ("thread737candle737", "dGhyZWFkNzM3Y2FuZGxlNzM3"),
    ("thread737thread737", "dGhyZWFkNzM3dGhyZWFkNzM3"),
    ("thread737kitten737", "dGhyZWFkNzM3a2l0dGVuNzM3"),
    (
        "round 737: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNzM3OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 737: agentuniverse is a framework for multi agents",
        "cm91bmQgNzM3OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 737: knowledge stored as vectors enables retrieval",
        "cm91bmQgNzM3OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 737: the processor reads the record then stops",
        "cm91bmQgNzM3OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 737: a worker pulls the next task from the queue",
        "cm91bmQgNzM3OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 737: signals travel through the network layer",
        "cm91bmQgNzM3OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 737: the gateway routes each request by policy",
        "cm91bmQgNzM3OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 737: memory grows until the buffer is full",
        "cm91bmQgNzM3OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 737: the cluster mirrors every packet twice",
        "cm91bmQgNzM3OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 737: ranking uses tokens learned from the corpus",
        "cm91bmQgNzM3OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 737: a long session ends when the candle dies",
        "cm91bmQgNzM3OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 737: encode the prompt then map the result",
        "cm91bmQgNzM3OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 737: the kernel wakes the worker at dawn",
        "cm91bmQgNzM3OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 737: service latency drops after the patch",
        "cm91bmQgNzM3OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 737: the library caches every vector it sees",
        "cm91bmQgNzM3OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 737: agents argue then the debate resolves",
        "cm91bmQgNzM3OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 737: the filter keeps only strong matches",
        "cm91bmQgNzM3OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 737: the model answers with a short reply",
        "cm91bmQgNzM3OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 737: the recorder stores the reasoning trace",
        "cm91bmQgNzM3OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 737: the angel watches the processor run",
        "cm91bmQgNzM3OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 737: angle of the vector decides the match",
        "cm91bmQgNzM3OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 737: the candle burns twice as long at night",
        "cm91bmQgNzM3OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 737: a mirror of the universe in one line",
        "cm91bmQgNzM3OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 737: the queue drains before the storm", "cm91bmQgNzM3OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
