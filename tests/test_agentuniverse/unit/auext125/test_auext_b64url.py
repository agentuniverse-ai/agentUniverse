"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten125kitten125", "a2l0dGVuMTI1a2l0dGVuMTI1"),
    ("kitten125sitting125", "a2l0dGVuMTI1c2l0dGluZzEyNQ"),
    ("kitten125agent125", "a2l0dGVuMTI1YWdlbnQxMjU"),
    ("kitten125angle125", "a2l0dGVuMTI1YW5nbGUxMjU"),
    ("sitting125angle125", "c2l0dGluZzEyNWFuZ2xlMTI1"),
    ("sitting125universe125", "c2l0dGluZzEyNXVuaXZlcnNlMTI1"),
    ("sitting125memory125", "c2l0dGluZzEyNW1lbW9yeTEyNQ"),
    ("sitting125stream125", "c2l0dGluZzEyNXN0cmVhbTEyNQ"),
    ("agent125stream125", "YWdlbnQxMjVzdHJlYW0xMjU"),
    ("agent125context125", "YWdlbnQxMjVjb250ZXh0MTI1"),
    ("agent125knowledge125", "YWdlbnQxMjVrbm93bGVkZ2UxMjU"),
    ("agent125vector125", "YWdlbnQxMjV2ZWN0b3IxMjU"),
    ("angle125vector125", "YW5nbGUxMjV2ZWN0b3IxMjU"),
    ("angle125processor125", "YW5nbGUxMjVwcm9jZXNzb3IxMjU"),
    ("angle125reasoning125", "YW5nbGUxMjVyZWFzb25pbmcxMjU"),
    ("angle125machine125", "YW5nbGUxMjVtYWNoaW5lMTI1"),
    ("universe125machine125", "dW5pdmVyc2UxMjVtYWNoaW5lMTI1"),
    ("universe125learning125", "dW5pdmVyc2UxMjVsZWFybmluZzEyNQ"),
    ("universe125model125", "dW5pdmVyc2UxMjVtb2RlbDEyNQ"),
    ("universe125token125", "dW5pdmVyc2UxMjV0b2tlbjEyNQ"),
    ("memory125token125", "bWVtb3J5MTI1dG9rZW4xMjU"),
    ("memory125prompt125", "bWVtb3J5MTI1cHJvbXB0MTI1"),
    ("memory125session125", "bWVtb3J5MTI1c2Vzc2lvbjEyNQ"),
    ("memory125library125", "bWVtb3J5MTI1bGlicmFyeTEyNQ"),
    ("stream125library125", "c3RyZWFtMTI1bGlicmFyeTEyNQ"),
    ("stream125service125", "c3RyZWFtMTI1c2VydmljZTEyNQ"),
    ("stream125gateway125", "c3RyZWFtMTI1Z2F0ZXdheTEyNQ"),
    ("stream125storage125", "c3RyZWFtMTI1c3RvcmFnZTEyNQ"),
    ("context125storage125", "Y29udGV4dDEyNXN0b3JhZ2UxMjU"),
    ("context125network125", "Y29udGV4dDEyNW5ldHdvcmsxMjU"),
    ("context125latency125", "Y29udGV4dDEyNWxhdGVuY3kxMjU"),
    ("context125buffer125", "Y29udGV4dDEyNWJ1ZmZlcjEyNQ"),
    ("knowledge125buffer125", "a25vd2xlZGdlMTI1YnVmZmVyMTI1"),
    ("knowledge125queue125", "a25vd2xlZGdlMTI1cXVldWUxMjU"),
    ("knowledge125worker125", "a25vd2xlZGdlMTI1d29ya2VyMTI1"),
    ("knowledge125kernel125", "a25vd2xlZGdlMTI1a2VybmVsMTI1"),
    ("vector125kernel125", "dmVjdG9yMTI1a2VybmVsMTI1"),
    ("vector125signal125", "dmVjdG9yMTI1c2lnbmFsMTI1"),
    ("vector125packet125", "dmVjdG9yMTI1cGFja2V0MTI1"),
    ("vector125router125", "dmVjdG9yMTI1cm91dGVyMTI1"),
    ("processor125router125", "cHJvY2Vzc29yMTI1cm91dGVyMTI1"),
    ("processor125cluster125", "cHJvY2Vzc29yMTI1Y2x1c3RlcjEyNQ"),
    ("processor125mirror125", "cHJvY2Vzc29yMTI1bWlycm9yMTI1"),
    ("processor125filter125", "cHJvY2Vzc29yMTI1ZmlsdGVyMTI1"),
    ("reasoning125filter125", "cmVhc29uaW5nMTI1ZmlsdGVyMTI1"),
    ("reasoning125ranking125", "cmVhc29uaW5nMTI1cmFua2luZzEyNQ"),
    ("reasoning125encoding125", "cmVhc29uaW5nMTI1ZW5jb2RpbmcxMjU"),
    ("reasoning125mapping125", "cmVhc29uaW5nMTI1bWFwcGluZzEyNQ"),
    ("machine125mapping125", "bWFjaGluZTEyNW1hcHBpbmcxMjU"),
    ("machine125record125", "bWFjaGluZTEyNXJlY29yZDEyNQ"),
    ("machine125candle125", "bWFjaGluZTEyNWNhbmRsZTEyNQ"),
    ("machine125thread125", "bWFjaGluZTEyNXRocmVhZDEyNQ"),
    ("learning125thread125", "bGVhcm5pbmcxMjV0aHJlYWQxMjU"),
    ("learning125kitten125", "bGVhcm5pbmcxMjVraXR0ZW4xMjU"),
    ("learning125sitting125", "bGVhcm5pbmcxMjVzaXR0aW5nMTI1"),
    ("learning125agent125", "bGVhcm5pbmcxMjVhZ2VudDEyNQ"),
    ("model125agent125", "bW9kZWwxMjVhZ2VudDEyNQ"),
    ("model125angle125", "bW9kZWwxMjVhbmdsZTEyNQ"),
    ("model125universe125", "bW9kZWwxMjV1bml2ZXJzZTEyNQ"),
    ("model125memory125", "bW9kZWwxMjVtZW1vcnkxMjU"),
    ("token125memory125", "dG9rZW4xMjVtZW1vcnkxMjU"),
    ("token125stream125", "dG9rZW4xMjVzdHJlYW0xMjU"),
    ("token125context125", "dG9rZW4xMjVjb250ZXh0MTI1"),
    ("token125knowledge125", "dG9rZW4xMjVrbm93bGVkZ2UxMjU"),
    ("prompt125knowledge125", "cHJvbXB0MTI1a25vd2xlZGdlMTI1"),
    ("prompt125vector125", "cHJvbXB0MTI1dmVjdG9yMTI1"),
    ("prompt125processor125", "cHJvbXB0MTI1cHJvY2Vzc29yMTI1"),
    ("prompt125reasoning125", "cHJvbXB0MTI1cmVhc29uaW5nMTI1"),
    ("session125reasoning125", "c2Vzc2lvbjEyNXJlYXNvbmluZzEyNQ"),
    ("session125machine125", "c2Vzc2lvbjEyNW1hY2hpbmUxMjU"),
    ("session125learning125", "c2Vzc2lvbjEyNWxlYXJuaW5nMTI1"),
    ("session125model125", "c2Vzc2lvbjEyNW1vZGVsMTI1"),
    ("library125model125", "bGlicmFyeTEyNW1vZGVsMTI1"),
    ("library125token125", "bGlicmFyeTEyNXRva2VuMTI1"),
    ("library125prompt125", "bGlicmFyeTEyNXByb21wdDEyNQ"),
    ("library125session125", "bGlicmFyeTEyNXNlc3Npb24xMjU"),
    ("service125session125", "c2VydmljZTEyNXNlc3Npb24xMjU"),
    ("service125library125", "c2VydmljZTEyNWxpYnJhcnkxMjU"),
    ("service125service125", "c2VydmljZTEyNXNlcnZpY2UxMjU"),
    ("service125gateway125", "c2VydmljZTEyNWdhdGV3YXkxMjU"),
    ("gateway125gateway125", "Z2F0ZXdheTEyNWdhdGV3YXkxMjU"),
    ("gateway125storage125", "Z2F0ZXdheTEyNXN0b3JhZ2UxMjU"),
    ("gateway125network125", "Z2F0ZXdheTEyNW5ldHdvcmsxMjU"),
    ("gateway125latency125", "Z2F0ZXdheTEyNWxhdGVuY3kxMjU"),
    ("storage125latency125", "c3RvcmFnZTEyNWxhdGVuY3kxMjU"),
    ("storage125buffer125", "c3RvcmFnZTEyNWJ1ZmZlcjEyNQ"),
    ("storage125queue125", "c3RvcmFnZTEyNXF1ZXVlMTI1"),
    ("storage125worker125", "c3RvcmFnZTEyNXdvcmtlcjEyNQ"),
    ("network125worker125", "bmV0d29yazEyNXdvcmtlcjEyNQ"),
    ("network125kernel125", "bmV0d29yazEyNWtlcm5lbDEyNQ"),
    ("network125signal125", "bmV0d29yazEyNXNpZ25hbDEyNQ"),
    ("network125packet125", "bmV0d29yazEyNXBhY2tldDEyNQ"),
    ("latency125packet125", "bGF0ZW5jeTEyNXBhY2tldDEyNQ"),
    ("latency125router125", "bGF0ZW5jeTEyNXJvdXRlcjEyNQ"),
    ("latency125cluster125", "bGF0ZW5jeTEyNWNsdXN0ZXIxMjU"),
    ("latency125mirror125", "bGF0ZW5jeTEyNW1pcnJvcjEyNQ"),
    ("buffer125mirror125", "YnVmZmVyMTI1bWlycm9yMTI1"),
    ("buffer125filter125", "YnVmZmVyMTI1ZmlsdGVyMTI1"),
    ("buffer125ranking125", "YnVmZmVyMTI1cmFua2luZzEyNQ"),
    ("buffer125encoding125", "YnVmZmVyMTI1ZW5jb2RpbmcxMjU"),
    ("queue125encoding125", "cXVldWUxMjVlbmNvZGluZzEyNQ"),
    ("queue125mapping125", "cXVldWUxMjVtYXBwaW5nMTI1"),
    ("queue125record125", "cXVldWUxMjVyZWNvcmQxMjU"),
    ("queue125candle125", "cXVldWUxMjVjYW5kbGUxMjU"),
    ("worker125candle125", "d29ya2VyMTI1Y2FuZGxlMTI1"),
    ("worker125thread125", "d29ya2VyMTI1dGhyZWFkMTI1"),
    ("worker125kitten125", "d29ya2VyMTI1a2l0dGVuMTI1"),
    ("worker125sitting125", "d29ya2VyMTI1c2l0dGluZzEyNQ"),
    ("kernel125sitting125", "a2VybmVsMTI1c2l0dGluZzEyNQ"),
    ("kernel125agent125", "a2VybmVsMTI1YWdlbnQxMjU"),
    ("kernel125angle125", "a2VybmVsMTI1YW5nbGUxMjU"),
    ("kernel125universe125", "a2VybmVsMTI1dW5pdmVyc2UxMjU"),
    ("signal125universe125", "c2lnbmFsMTI1dW5pdmVyc2UxMjU"),
    ("signal125memory125", "c2lnbmFsMTI1bWVtb3J5MTI1"),
    ("signal125stream125", "c2lnbmFsMTI1c3RyZWFtMTI1"),
    ("signal125context125", "c2lnbmFsMTI1Y29udGV4dDEyNQ"),
    ("packet125context125", "cGFja2V0MTI1Y29udGV4dDEyNQ"),
    ("packet125knowledge125", "cGFja2V0MTI1a25vd2xlZGdlMTI1"),
    ("packet125vector125", "cGFja2V0MTI1dmVjdG9yMTI1"),
    ("packet125processor125", "cGFja2V0MTI1cHJvY2Vzc29yMTI1"),
    ("router125processor125", "cm91dGVyMTI1cHJvY2Vzc29yMTI1"),
    ("router125reasoning125", "cm91dGVyMTI1cmVhc29uaW5nMTI1"),
    ("router125machine125", "cm91dGVyMTI1bWFjaGluZTEyNQ"),
    ("router125learning125", "cm91dGVyMTI1bGVhcm5pbmcxMjU"),
    ("cluster125learning125", "Y2x1c3RlcjEyNWxlYXJuaW5nMTI1"),
    ("cluster125model125", "Y2x1c3RlcjEyNW1vZGVsMTI1"),
    ("cluster125token125", "Y2x1c3RlcjEyNXRva2VuMTI1"),
    ("cluster125prompt125", "Y2x1c3RlcjEyNXByb21wdDEyNQ"),
    ("mirror125prompt125", "bWlycm9yMTI1cHJvbXB0MTI1"),
    ("mirror125session125", "bWlycm9yMTI1c2Vzc2lvbjEyNQ"),
    ("mirror125library125", "bWlycm9yMTI1bGlicmFyeTEyNQ"),
    ("mirror125service125", "bWlycm9yMTI1c2VydmljZTEyNQ"),
    ("filter125service125", "ZmlsdGVyMTI1c2VydmljZTEyNQ"),
    ("filter125gateway125", "ZmlsdGVyMTI1Z2F0ZXdheTEyNQ"),
    ("filter125storage125", "ZmlsdGVyMTI1c3RvcmFnZTEyNQ"),
    ("filter125network125", "ZmlsdGVyMTI1bmV0d29yazEyNQ"),
    ("ranking125network125", "cmFua2luZzEyNW5ldHdvcmsxMjU"),
    ("ranking125latency125", "cmFua2luZzEyNWxhdGVuY3kxMjU"),
    ("ranking125buffer125", "cmFua2luZzEyNWJ1ZmZlcjEyNQ"),
    ("ranking125queue125", "cmFua2luZzEyNXF1ZXVlMTI1"),
    ("encoding125queue125", "ZW5jb2RpbmcxMjVxdWV1ZTEyNQ"),
    ("encoding125worker125", "ZW5jb2RpbmcxMjV3b3JrZXIxMjU"),
    ("encoding125kernel125", "ZW5jb2RpbmcxMjVrZXJuZWwxMjU"),
    ("encoding125signal125", "ZW5jb2RpbmcxMjVzaWduYWwxMjU"),
    ("mapping125signal125", "bWFwcGluZzEyNXNpZ25hbDEyNQ"),
    ("mapping125packet125", "bWFwcGluZzEyNXBhY2tldDEyNQ"),
    ("mapping125router125", "bWFwcGluZzEyNXJvdXRlcjEyNQ"),
    ("mapping125cluster125", "bWFwcGluZzEyNWNsdXN0ZXIxMjU"),
    ("record125cluster125", "cmVjb3JkMTI1Y2x1c3RlcjEyNQ"),
    ("record125mirror125", "cmVjb3JkMTI1bWlycm9yMTI1"),
    ("record125filter125", "cmVjb3JkMTI1ZmlsdGVyMTI1"),
    ("record125ranking125", "cmVjb3JkMTI1cmFua2luZzEyNQ"),
    ("candle125ranking125", "Y2FuZGxlMTI1cmFua2luZzEyNQ"),
    ("candle125encoding125", "Y2FuZGxlMTI1ZW5jb2RpbmcxMjU"),
    ("candle125mapping125", "Y2FuZGxlMTI1bWFwcGluZzEyNQ"),
    ("candle125record125", "Y2FuZGxlMTI1cmVjb3JkMTI1"),
    ("thread125record125", "dGhyZWFkMTI1cmVjb3JkMTI1"),
    ("thread125candle125", "dGhyZWFkMTI1Y2FuZGxlMTI1"),
    ("thread125thread125", "dGhyZWFkMTI1dGhyZWFkMTI1"),
    ("thread125kitten125", "dGhyZWFkMTI1a2l0dGVuMTI1"),
    (
        "round 125: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTI1OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 125: agentuniverse is a framework for multi agents",
        "cm91bmQgMTI1OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 125: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTI1OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 125: the processor reads the record then stops",
        "cm91bmQgMTI1OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 125: a worker pulls the next task from the queue",
        "cm91bmQgMTI1OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 125: signals travel through the network layer",
        "cm91bmQgMTI1OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 125: the gateway routes each request by policy",
        "cm91bmQgMTI1OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 125: memory grows until the buffer is full",
        "cm91bmQgMTI1OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 125: the cluster mirrors every packet twice",
        "cm91bmQgMTI1OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 125: ranking uses tokens learned from the corpus",
        "cm91bmQgMTI1OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 125: a long session ends when the candle dies",
        "cm91bmQgMTI1OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 125: encode the prompt then map the result",
        "cm91bmQgMTI1OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 125: the kernel wakes the worker at dawn",
        "cm91bmQgMTI1OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 125: service latency drops after the patch",
        "cm91bmQgMTI1OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 125: the library caches every vector it sees",
        "cm91bmQgMTI1OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 125: agents argue then the debate resolves",
        "cm91bmQgMTI1OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 125: the filter keeps only strong matches",
        "cm91bmQgMTI1OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 125: the model answers with a short reply",
        "cm91bmQgMTI1OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 125: the recorder stores the reasoning trace",
        "cm91bmQgMTI1OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 125: the angel watches the processor run",
        "cm91bmQgMTI1OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 125: angle of the vector decides the match",
        "cm91bmQgMTI1OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 125: the candle burns twice as long at night",
        "cm91bmQgMTI1OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 125: a mirror of the universe in one line",
        "cm91bmQgMTI1OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 125: the queue drains before the storm", "cm91bmQgMTI1OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
