"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten139kitten139", "a2l0dGVuMTM5a2l0dGVuMTM5"),
    ("kitten139sitting139", "a2l0dGVuMTM5c2l0dGluZzEzOQ"),
    ("kitten139agent139", "a2l0dGVuMTM5YWdlbnQxMzk"),
    ("kitten139angle139", "a2l0dGVuMTM5YW5nbGUxMzk"),
    ("sitting139angle139", "c2l0dGluZzEzOWFuZ2xlMTM5"),
    ("sitting139universe139", "c2l0dGluZzEzOXVuaXZlcnNlMTM5"),
    ("sitting139memory139", "c2l0dGluZzEzOW1lbW9yeTEzOQ"),
    ("sitting139stream139", "c2l0dGluZzEzOXN0cmVhbTEzOQ"),
    ("agent139stream139", "YWdlbnQxMzlzdHJlYW0xMzk"),
    ("agent139context139", "YWdlbnQxMzljb250ZXh0MTM5"),
    ("agent139knowledge139", "YWdlbnQxMzlrbm93bGVkZ2UxMzk"),
    ("agent139vector139", "YWdlbnQxMzl2ZWN0b3IxMzk"),
    ("angle139vector139", "YW5nbGUxMzl2ZWN0b3IxMzk"),
    ("angle139processor139", "YW5nbGUxMzlwcm9jZXNzb3IxMzk"),
    ("angle139reasoning139", "YW5nbGUxMzlyZWFzb25pbmcxMzk"),
    ("angle139machine139", "YW5nbGUxMzltYWNoaW5lMTM5"),
    ("universe139machine139", "dW5pdmVyc2UxMzltYWNoaW5lMTM5"),
    ("universe139learning139", "dW5pdmVyc2UxMzlsZWFybmluZzEzOQ"),
    ("universe139model139", "dW5pdmVyc2UxMzltb2RlbDEzOQ"),
    ("universe139token139", "dW5pdmVyc2UxMzl0b2tlbjEzOQ"),
    ("memory139token139", "bWVtb3J5MTM5dG9rZW4xMzk"),
    ("memory139prompt139", "bWVtb3J5MTM5cHJvbXB0MTM5"),
    ("memory139session139", "bWVtb3J5MTM5c2Vzc2lvbjEzOQ"),
    ("memory139library139", "bWVtb3J5MTM5bGlicmFyeTEzOQ"),
    ("stream139library139", "c3RyZWFtMTM5bGlicmFyeTEzOQ"),
    ("stream139service139", "c3RyZWFtMTM5c2VydmljZTEzOQ"),
    ("stream139gateway139", "c3RyZWFtMTM5Z2F0ZXdheTEzOQ"),
    ("stream139storage139", "c3RyZWFtMTM5c3RvcmFnZTEzOQ"),
    ("context139storage139", "Y29udGV4dDEzOXN0b3JhZ2UxMzk"),
    ("context139network139", "Y29udGV4dDEzOW5ldHdvcmsxMzk"),
    ("context139latency139", "Y29udGV4dDEzOWxhdGVuY3kxMzk"),
    ("context139buffer139", "Y29udGV4dDEzOWJ1ZmZlcjEzOQ"),
    ("knowledge139buffer139", "a25vd2xlZGdlMTM5YnVmZmVyMTM5"),
    ("knowledge139queue139", "a25vd2xlZGdlMTM5cXVldWUxMzk"),
    ("knowledge139worker139", "a25vd2xlZGdlMTM5d29ya2VyMTM5"),
    ("knowledge139kernel139", "a25vd2xlZGdlMTM5a2VybmVsMTM5"),
    ("vector139kernel139", "dmVjdG9yMTM5a2VybmVsMTM5"),
    ("vector139signal139", "dmVjdG9yMTM5c2lnbmFsMTM5"),
    ("vector139packet139", "dmVjdG9yMTM5cGFja2V0MTM5"),
    ("vector139router139", "dmVjdG9yMTM5cm91dGVyMTM5"),
    ("processor139router139", "cHJvY2Vzc29yMTM5cm91dGVyMTM5"),
    ("processor139cluster139", "cHJvY2Vzc29yMTM5Y2x1c3RlcjEzOQ"),
    ("processor139mirror139", "cHJvY2Vzc29yMTM5bWlycm9yMTM5"),
    ("processor139filter139", "cHJvY2Vzc29yMTM5ZmlsdGVyMTM5"),
    ("reasoning139filter139", "cmVhc29uaW5nMTM5ZmlsdGVyMTM5"),
    ("reasoning139ranking139", "cmVhc29uaW5nMTM5cmFua2luZzEzOQ"),
    ("reasoning139encoding139", "cmVhc29uaW5nMTM5ZW5jb2RpbmcxMzk"),
    ("reasoning139mapping139", "cmVhc29uaW5nMTM5bWFwcGluZzEzOQ"),
    ("machine139mapping139", "bWFjaGluZTEzOW1hcHBpbmcxMzk"),
    ("machine139record139", "bWFjaGluZTEzOXJlY29yZDEzOQ"),
    ("machine139candle139", "bWFjaGluZTEzOWNhbmRsZTEzOQ"),
    ("machine139thread139", "bWFjaGluZTEzOXRocmVhZDEzOQ"),
    ("learning139thread139", "bGVhcm5pbmcxMzl0aHJlYWQxMzk"),
    ("learning139kitten139", "bGVhcm5pbmcxMzlraXR0ZW4xMzk"),
    ("learning139sitting139", "bGVhcm5pbmcxMzlzaXR0aW5nMTM5"),
    ("learning139agent139", "bGVhcm5pbmcxMzlhZ2VudDEzOQ"),
    ("model139agent139", "bW9kZWwxMzlhZ2VudDEzOQ"),
    ("model139angle139", "bW9kZWwxMzlhbmdsZTEzOQ"),
    ("model139universe139", "bW9kZWwxMzl1bml2ZXJzZTEzOQ"),
    ("model139memory139", "bW9kZWwxMzltZW1vcnkxMzk"),
    ("token139memory139", "dG9rZW4xMzltZW1vcnkxMzk"),
    ("token139stream139", "dG9rZW4xMzlzdHJlYW0xMzk"),
    ("token139context139", "dG9rZW4xMzljb250ZXh0MTM5"),
    ("token139knowledge139", "dG9rZW4xMzlrbm93bGVkZ2UxMzk"),
    ("prompt139knowledge139", "cHJvbXB0MTM5a25vd2xlZGdlMTM5"),
    ("prompt139vector139", "cHJvbXB0MTM5dmVjdG9yMTM5"),
    ("prompt139processor139", "cHJvbXB0MTM5cHJvY2Vzc29yMTM5"),
    ("prompt139reasoning139", "cHJvbXB0MTM5cmVhc29uaW5nMTM5"),
    ("session139reasoning139", "c2Vzc2lvbjEzOXJlYXNvbmluZzEzOQ"),
    ("session139machine139", "c2Vzc2lvbjEzOW1hY2hpbmUxMzk"),
    ("session139learning139", "c2Vzc2lvbjEzOWxlYXJuaW5nMTM5"),
    ("session139model139", "c2Vzc2lvbjEzOW1vZGVsMTM5"),
    ("library139model139", "bGlicmFyeTEzOW1vZGVsMTM5"),
    ("library139token139", "bGlicmFyeTEzOXRva2VuMTM5"),
    ("library139prompt139", "bGlicmFyeTEzOXByb21wdDEzOQ"),
    ("library139session139", "bGlicmFyeTEzOXNlc3Npb24xMzk"),
    ("service139session139", "c2VydmljZTEzOXNlc3Npb24xMzk"),
    ("service139library139", "c2VydmljZTEzOWxpYnJhcnkxMzk"),
    ("service139service139", "c2VydmljZTEzOXNlcnZpY2UxMzk"),
    ("service139gateway139", "c2VydmljZTEzOWdhdGV3YXkxMzk"),
    ("gateway139gateway139", "Z2F0ZXdheTEzOWdhdGV3YXkxMzk"),
    ("gateway139storage139", "Z2F0ZXdheTEzOXN0b3JhZ2UxMzk"),
    ("gateway139network139", "Z2F0ZXdheTEzOW5ldHdvcmsxMzk"),
    ("gateway139latency139", "Z2F0ZXdheTEzOWxhdGVuY3kxMzk"),
    ("storage139latency139", "c3RvcmFnZTEzOWxhdGVuY3kxMzk"),
    ("storage139buffer139", "c3RvcmFnZTEzOWJ1ZmZlcjEzOQ"),
    ("storage139queue139", "c3RvcmFnZTEzOXF1ZXVlMTM5"),
    ("storage139worker139", "c3RvcmFnZTEzOXdvcmtlcjEzOQ"),
    ("network139worker139", "bmV0d29yazEzOXdvcmtlcjEzOQ"),
    ("network139kernel139", "bmV0d29yazEzOWtlcm5lbDEzOQ"),
    ("network139signal139", "bmV0d29yazEzOXNpZ25hbDEzOQ"),
    ("network139packet139", "bmV0d29yazEzOXBhY2tldDEzOQ"),
    ("latency139packet139", "bGF0ZW5jeTEzOXBhY2tldDEzOQ"),
    ("latency139router139", "bGF0ZW5jeTEzOXJvdXRlcjEzOQ"),
    ("latency139cluster139", "bGF0ZW5jeTEzOWNsdXN0ZXIxMzk"),
    ("latency139mirror139", "bGF0ZW5jeTEzOW1pcnJvcjEzOQ"),
    ("buffer139mirror139", "YnVmZmVyMTM5bWlycm9yMTM5"),
    ("buffer139filter139", "YnVmZmVyMTM5ZmlsdGVyMTM5"),
    ("buffer139ranking139", "YnVmZmVyMTM5cmFua2luZzEzOQ"),
    ("buffer139encoding139", "YnVmZmVyMTM5ZW5jb2RpbmcxMzk"),
    ("queue139encoding139", "cXVldWUxMzllbmNvZGluZzEzOQ"),
    ("queue139mapping139", "cXVldWUxMzltYXBwaW5nMTM5"),
    ("queue139record139", "cXVldWUxMzlyZWNvcmQxMzk"),
    ("queue139candle139", "cXVldWUxMzljYW5kbGUxMzk"),
    ("worker139candle139", "d29ya2VyMTM5Y2FuZGxlMTM5"),
    ("worker139thread139", "d29ya2VyMTM5dGhyZWFkMTM5"),
    ("worker139kitten139", "d29ya2VyMTM5a2l0dGVuMTM5"),
    ("worker139sitting139", "d29ya2VyMTM5c2l0dGluZzEzOQ"),
    ("kernel139sitting139", "a2VybmVsMTM5c2l0dGluZzEzOQ"),
    ("kernel139agent139", "a2VybmVsMTM5YWdlbnQxMzk"),
    ("kernel139angle139", "a2VybmVsMTM5YW5nbGUxMzk"),
    ("kernel139universe139", "a2VybmVsMTM5dW5pdmVyc2UxMzk"),
    ("signal139universe139", "c2lnbmFsMTM5dW5pdmVyc2UxMzk"),
    ("signal139memory139", "c2lnbmFsMTM5bWVtb3J5MTM5"),
    ("signal139stream139", "c2lnbmFsMTM5c3RyZWFtMTM5"),
    ("signal139context139", "c2lnbmFsMTM5Y29udGV4dDEzOQ"),
    ("packet139context139", "cGFja2V0MTM5Y29udGV4dDEzOQ"),
    ("packet139knowledge139", "cGFja2V0MTM5a25vd2xlZGdlMTM5"),
    ("packet139vector139", "cGFja2V0MTM5dmVjdG9yMTM5"),
    ("packet139processor139", "cGFja2V0MTM5cHJvY2Vzc29yMTM5"),
    ("router139processor139", "cm91dGVyMTM5cHJvY2Vzc29yMTM5"),
    ("router139reasoning139", "cm91dGVyMTM5cmVhc29uaW5nMTM5"),
    ("router139machine139", "cm91dGVyMTM5bWFjaGluZTEzOQ"),
    ("router139learning139", "cm91dGVyMTM5bGVhcm5pbmcxMzk"),
    ("cluster139learning139", "Y2x1c3RlcjEzOWxlYXJuaW5nMTM5"),
    ("cluster139model139", "Y2x1c3RlcjEzOW1vZGVsMTM5"),
    ("cluster139token139", "Y2x1c3RlcjEzOXRva2VuMTM5"),
    ("cluster139prompt139", "Y2x1c3RlcjEzOXByb21wdDEzOQ"),
    ("mirror139prompt139", "bWlycm9yMTM5cHJvbXB0MTM5"),
    ("mirror139session139", "bWlycm9yMTM5c2Vzc2lvbjEzOQ"),
    ("mirror139library139", "bWlycm9yMTM5bGlicmFyeTEzOQ"),
    ("mirror139service139", "bWlycm9yMTM5c2VydmljZTEzOQ"),
    ("filter139service139", "ZmlsdGVyMTM5c2VydmljZTEzOQ"),
    ("filter139gateway139", "ZmlsdGVyMTM5Z2F0ZXdheTEzOQ"),
    ("filter139storage139", "ZmlsdGVyMTM5c3RvcmFnZTEzOQ"),
    ("filter139network139", "ZmlsdGVyMTM5bmV0d29yazEzOQ"),
    ("ranking139network139", "cmFua2luZzEzOW5ldHdvcmsxMzk"),
    ("ranking139latency139", "cmFua2luZzEzOWxhdGVuY3kxMzk"),
    ("ranking139buffer139", "cmFua2luZzEzOWJ1ZmZlcjEzOQ"),
    ("ranking139queue139", "cmFua2luZzEzOXF1ZXVlMTM5"),
    ("encoding139queue139", "ZW5jb2RpbmcxMzlxdWV1ZTEzOQ"),
    ("encoding139worker139", "ZW5jb2RpbmcxMzl3b3JrZXIxMzk"),
    ("encoding139kernel139", "ZW5jb2RpbmcxMzlrZXJuZWwxMzk"),
    ("encoding139signal139", "ZW5jb2RpbmcxMzlzaWduYWwxMzk"),
    ("mapping139signal139", "bWFwcGluZzEzOXNpZ25hbDEzOQ"),
    ("mapping139packet139", "bWFwcGluZzEzOXBhY2tldDEzOQ"),
    ("mapping139router139", "bWFwcGluZzEzOXJvdXRlcjEzOQ"),
    ("mapping139cluster139", "bWFwcGluZzEzOWNsdXN0ZXIxMzk"),
    ("record139cluster139", "cmVjb3JkMTM5Y2x1c3RlcjEzOQ"),
    ("record139mirror139", "cmVjb3JkMTM5bWlycm9yMTM5"),
    ("record139filter139", "cmVjb3JkMTM5ZmlsdGVyMTM5"),
    ("record139ranking139", "cmVjb3JkMTM5cmFua2luZzEzOQ"),
    ("candle139ranking139", "Y2FuZGxlMTM5cmFua2luZzEzOQ"),
    ("candle139encoding139", "Y2FuZGxlMTM5ZW5jb2RpbmcxMzk"),
    ("candle139mapping139", "Y2FuZGxlMTM5bWFwcGluZzEzOQ"),
    ("candle139record139", "Y2FuZGxlMTM5cmVjb3JkMTM5"),
    ("thread139record139", "dGhyZWFkMTM5cmVjb3JkMTM5"),
    ("thread139candle139", "dGhyZWFkMTM5Y2FuZGxlMTM5"),
    ("thread139thread139", "dGhyZWFkMTM5dGhyZWFkMTM5"),
    ("thread139kitten139", "dGhyZWFkMTM5a2l0dGVuMTM5"),
    (
        "round 139: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTM5OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 139: agentuniverse is a framework for multi agents",
        "cm91bmQgMTM5OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 139: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTM5OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 139: the processor reads the record then stops",
        "cm91bmQgMTM5OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 139: a worker pulls the next task from the queue",
        "cm91bmQgMTM5OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 139: signals travel through the network layer",
        "cm91bmQgMTM5OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 139: the gateway routes each request by policy",
        "cm91bmQgMTM5OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 139: memory grows until the buffer is full",
        "cm91bmQgMTM5OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 139: the cluster mirrors every packet twice",
        "cm91bmQgMTM5OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 139: ranking uses tokens learned from the corpus",
        "cm91bmQgMTM5OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 139: a long session ends when the candle dies",
        "cm91bmQgMTM5OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 139: encode the prompt then map the result",
        "cm91bmQgMTM5OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 139: the kernel wakes the worker at dawn",
        "cm91bmQgMTM5OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 139: service latency drops after the patch",
        "cm91bmQgMTM5OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 139: the library caches every vector it sees",
        "cm91bmQgMTM5OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 139: agents argue then the debate resolves",
        "cm91bmQgMTM5OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 139: the filter keeps only strong matches",
        "cm91bmQgMTM5OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 139: the model answers with a short reply",
        "cm91bmQgMTM5OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 139: the recorder stores the reasoning trace",
        "cm91bmQgMTM5OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 139: the angel watches the processor run",
        "cm91bmQgMTM5OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 139: angle of the vector decides the match",
        "cm91bmQgMTM5OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 139: the candle burns twice as long at night",
        "cm91bmQgMTM5OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 139: a mirror of the universe in one line",
        "cm91bmQgMTM5OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 139: the queue drains before the storm", "cm91bmQgMTM5OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
