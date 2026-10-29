"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten129kitten129", "a2l0dGVuMTI5a2l0dGVuMTI5"),
    ("kitten129sitting129", "a2l0dGVuMTI5c2l0dGluZzEyOQ"),
    ("kitten129agent129", "a2l0dGVuMTI5YWdlbnQxMjk"),
    ("kitten129angle129", "a2l0dGVuMTI5YW5nbGUxMjk"),
    ("sitting129angle129", "c2l0dGluZzEyOWFuZ2xlMTI5"),
    ("sitting129universe129", "c2l0dGluZzEyOXVuaXZlcnNlMTI5"),
    ("sitting129memory129", "c2l0dGluZzEyOW1lbW9yeTEyOQ"),
    ("sitting129stream129", "c2l0dGluZzEyOXN0cmVhbTEyOQ"),
    ("agent129stream129", "YWdlbnQxMjlzdHJlYW0xMjk"),
    ("agent129context129", "YWdlbnQxMjljb250ZXh0MTI5"),
    ("agent129knowledge129", "YWdlbnQxMjlrbm93bGVkZ2UxMjk"),
    ("agent129vector129", "YWdlbnQxMjl2ZWN0b3IxMjk"),
    ("angle129vector129", "YW5nbGUxMjl2ZWN0b3IxMjk"),
    ("angle129processor129", "YW5nbGUxMjlwcm9jZXNzb3IxMjk"),
    ("angle129reasoning129", "YW5nbGUxMjlyZWFzb25pbmcxMjk"),
    ("angle129machine129", "YW5nbGUxMjltYWNoaW5lMTI5"),
    ("universe129machine129", "dW5pdmVyc2UxMjltYWNoaW5lMTI5"),
    ("universe129learning129", "dW5pdmVyc2UxMjlsZWFybmluZzEyOQ"),
    ("universe129model129", "dW5pdmVyc2UxMjltb2RlbDEyOQ"),
    ("universe129token129", "dW5pdmVyc2UxMjl0b2tlbjEyOQ"),
    ("memory129token129", "bWVtb3J5MTI5dG9rZW4xMjk"),
    ("memory129prompt129", "bWVtb3J5MTI5cHJvbXB0MTI5"),
    ("memory129session129", "bWVtb3J5MTI5c2Vzc2lvbjEyOQ"),
    ("memory129library129", "bWVtb3J5MTI5bGlicmFyeTEyOQ"),
    ("stream129library129", "c3RyZWFtMTI5bGlicmFyeTEyOQ"),
    ("stream129service129", "c3RyZWFtMTI5c2VydmljZTEyOQ"),
    ("stream129gateway129", "c3RyZWFtMTI5Z2F0ZXdheTEyOQ"),
    ("stream129storage129", "c3RyZWFtMTI5c3RvcmFnZTEyOQ"),
    ("context129storage129", "Y29udGV4dDEyOXN0b3JhZ2UxMjk"),
    ("context129network129", "Y29udGV4dDEyOW5ldHdvcmsxMjk"),
    ("context129latency129", "Y29udGV4dDEyOWxhdGVuY3kxMjk"),
    ("context129buffer129", "Y29udGV4dDEyOWJ1ZmZlcjEyOQ"),
    ("knowledge129buffer129", "a25vd2xlZGdlMTI5YnVmZmVyMTI5"),
    ("knowledge129queue129", "a25vd2xlZGdlMTI5cXVldWUxMjk"),
    ("knowledge129worker129", "a25vd2xlZGdlMTI5d29ya2VyMTI5"),
    ("knowledge129kernel129", "a25vd2xlZGdlMTI5a2VybmVsMTI5"),
    ("vector129kernel129", "dmVjdG9yMTI5a2VybmVsMTI5"),
    ("vector129signal129", "dmVjdG9yMTI5c2lnbmFsMTI5"),
    ("vector129packet129", "dmVjdG9yMTI5cGFja2V0MTI5"),
    ("vector129router129", "dmVjdG9yMTI5cm91dGVyMTI5"),
    ("processor129router129", "cHJvY2Vzc29yMTI5cm91dGVyMTI5"),
    ("processor129cluster129", "cHJvY2Vzc29yMTI5Y2x1c3RlcjEyOQ"),
    ("processor129mirror129", "cHJvY2Vzc29yMTI5bWlycm9yMTI5"),
    ("processor129filter129", "cHJvY2Vzc29yMTI5ZmlsdGVyMTI5"),
    ("reasoning129filter129", "cmVhc29uaW5nMTI5ZmlsdGVyMTI5"),
    ("reasoning129ranking129", "cmVhc29uaW5nMTI5cmFua2luZzEyOQ"),
    ("reasoning129encoding129", "cmVhc29uaW5nMTI5ZW5jb2RpbmcxMjk"),
    ("reasoning129mapping129", "cmVhc29uaW5nMTI5bWFwcGluZzEyOQ"),
    ("machine129mapping129", "bWFjaGluZTEyOW1hcHBpbmcxMjk"),
    ("machine129record129", "bWFjaGluZTEyOXJlY29yZDEyOQ"),
    ("machine129candle129", "bWFjaGluZTEyOWNhbmRsZTEyOQ"),
    ("machine129thread129", "bWFjaGluZTEyOXRocmVhZDEyOQ"),
    ("learning129thread129", "bGVhcm5pbmcxMjl0aHJlYWQxMjk"),
    ("learning129kitten129", "bGVhcm5pbmcxMjlraXR0ZW4xMjk"),
    ("learning129sitting129", "bGVhcm5pbmcxMjlzaXR0aW5nMTI5"),
    ("learning129agent129", "bGVhcm5pbmcxMjlhZ2VudDEyOQ"),
    ("model129agent129", "bW9kZWwxMjlhZ2VudDEyOQ"),
    ("model129angle129", "bW9kZWwxMjlhbmdsZTEyOQ"),
    ("model129universe129", "bW9kZWwxMjl1bml2ZXJzZTEyOQ"),
    ("model129memory129", "bW9kZWwxMjltZW1vcnkxMjk"),
    ("token129memory129", "dG9rZW4xMjltZW1vcnkxMjk"),
    ("token129stream129", "dG9rZW4xMjlzdHJlYW0xMjk"),
    ("token129context129", "dG9rZW4xMjljb250ZXh0MTI5"),
    ("token129knowledge129", "dG9rZW4xMjlrbm93bGVkZ2UxMjk"),
    ("prompt129knowledge129", "cHJvbXB0MTI5a25vd2xlZGdlMTI5"),
    ("prompt129vector129", "cHJvbXB0MTI5dmVjdG9yMTI5"),
    ("prompt129processor129", "cHJvbXB0MTI5cHJvY2Vzc29yMTI5"),
    ("prompt129reasoning129", "cHJvbXB0MTI5cmVhc29uaW5nMTI5"),
    ("session129reasoning129", "c2Vzc2lvbjEyOXJlYXNvbmluZzEyOQ"),
    ("session129machine129", "c2Vzc2lvbjEyOW1hY2hpbmUxMjk"),
    ("session129learning129", "c2Vzc2lvbjEyOWxlYXJuaW5nMTI5"),
    ("session129model129", "c2Vzc2lvbjEyOW1vZGVsMTI5"),
    ("library129model129", "bGlicmFyeTEyOW1vZGVsMTI5"),
    ("library129token129", "bGlicmFyeTEyOXRva2VuMTI5"),
    ("library129prompt129", "bGlicmFyeTEyOXByb21wdDEyOQ"),
    ("library129session129", "bGlicmFyeTEyOXNlc3Npb24xMjk"),
    ("service129session129", "c2VydmljZTEyOXNlc3Npb24xMjk"),
    ("service129library129", "c2VydmljZTEyOWxpYnJhcnkxMjk"),
    ("service129service129", "c2VydmljZTEyOXNlcnZpY2UxMjk"),
    ("service129gateway129", "c2VydmljZTEyOWdhdGV3YXkxMjk"),
    ("gateway129gateway129", "Z2F0ZXdheTEyOWdhdGV3YXkxMjk"),
    ("gateway129storage129", "Z2F0ZXdheTEyOXN0b3JhZ2UxMjk"),
    ("gateway129network129", "Z2F0ZXdheTEyOW5ldHdvcmsxMjk"),
    ("gateway129latency129", "Z2F0ZXdheTEyOWxhdGVuY3kxMjk"),
    ("storage129latency129", "c3RvcmFnZTEyOWxhdGVuY3kxMjk"),
    ("storage129buffer129", "c3RvcmFnZTEyOWJ1ZmZlcjEyOQ"),
    ("storage129queue129", "c3RvcmFnZTEyOXF1ZXVlMTI5"),
    ("storage129worker129", "c3RvcmFnZTEyOXdvcmtlcjEyOQ"),
    ("network129worker129", "bmV0d29yazEyOXdvcmtlcjEyOQ"),
    ("network129kernel129", "bmV0d29yazEyOWtlcm5lbDEyOQ"),
    ("network129signal129", "bmV0d29yazEyOXNpZ25hbDEyOQ"),
    ("network129packet129", "bmV0d29yazEyOXBhY2tldDEyOQ"),
    ("latency129packet129", "bGF0ZW5jeTEyOXBhY2tldDEyOQ"),
    ("latency129router129", "bGF0ZW5jeTEyOXJvdXRlcjEyOQ"),
    ("latency129cluster129", "bGF0ZW5jeTEyOWNsdXN0ZXIxMjk"),
    ("latency129mirror129", "bGF0ZW5jeTEyOW1pcnJvcjEyOQ"),
    ("buffer129mirror129", "YnVmZmVyMTI5bWlycm9yMTI5"),
    ("buffer129filter129", "YnVmZmVyMTI5ZmlsdGVyMTI5"),
    ("buffer129ranking129", "YnVmZmVyMTI5cmFua2luZzEyOQ"),
    ("buffer129encoding129", "YnVmZmVyMTI5ZW5jb2RpbmcxMjk"),
    ("queue129encoding129", "cXVldWUxMjllbmNvZGluZzEyOQ"),
    ("queue129mapping129", "cXVldWUxMjltYXBwaW5nMTI5"),
    ("queue129record129", "cXVldWUxMjlyZWNvcmQxMjk"),
    ("queue129candle129", "cXVldWUxMjljYW5kbGUxMjk"),
    ("worker129candle129", "d29ya2VyMTI5Y2FuZGxlMTI5"),
    ("worker129thread129", "d29ya2VyMTI5dGhyZWFkMTI5"),
    ("worker129kitten129", "d29ya2VyMTI5a2l0dGVuMTI5"),
    ("worker129sitting129", "d29ya2VyMTI5c2l0dGluZzEyOQ"),
    ("kernel129sitting129", "a2VybmVsMTI5c2l0dGluZzEyOQ"),
    ("kernel129agent129", "a2VybmVsMTI5YWdlbnQxMjk"),
    ("kernel129angle129", "a2VybmVsMTI5YW5nbGUxMjk"),
    ("kernel129universe129", "a2VybmVsMTI5dW5pdmVyc2UxMjk"),
    ("signal129universe129", "c2lnbmFsMTI5dW5pdmVyc2UxMjk"),
    ("signal129memory129", "c2lnbmFsMTI5bWVtb3J5MTI5"),
    ("signal129stream129", "c2lnbmFsMTI5c3RyZWFtMTI5"),
    ("signal129context129", "c2lnbmFsMTI5Y29udGV4dDEyOQ"),
    ("packet129context129", "cGFja2V0MTI5Y29udGV4dDEyOQ"),
    ("packet129knowledge129", "cGFja2V0MTI5a25vd2xlZGdlMTI5"),
    ("packet129vector129", "cGFja2V0MTI5dmVjdG9yMTI5"),
    ("packet129processor129", "cGFja2V0MTI5cHJvY2Vzc29yMTI5"),
    ("router129processor129", "cm91dGVyMTI5cHJvY2Vzc29yMTI5"),
    ("router129reasoning129", "cm91dGVyMTI5cmVhc29uaW5nMTI5"),
    ("router129machine129", "cm91dGVyMTI5bWFjaGluZTEyOQ"),
    ("router129learning129", "cm91dGVyMTI5bGVhcm5pbmcxMjk"),
    ("cluster129learning129", "Y2x1c3RlcjEyOWxlYXJuaW5nMTI5"),
    ("cluster129model129", "Y2x1c3RlcjEyOW1vZGVsMTI5"),
    ("cluster129token129", "Y2x1c3RlcjEyOXRva2VuMTI5"),
    ("cluster129prompt129", "Y2x1c3RlcjEyOXByb21wdDEyOQ"),
    ("mirror129prompt129", "bWlycm9yMTI5cHJvbXB0MTI5"),
    ("mirror129session129", "bWlycm9yMTI5c2Vzc2lvbjEyOQ"),
    ("mirror129library129", "bWlycm9yMTI5bGlicmFyeTEyOQ"),
    ("mirror129service129", "bWlycm9yMTI5c2VydmljZTEyOQ"),
    ("filter129service129", "ZmlsdGVyMTI5c2VydmljZTEyOQ"),
    ("filter129gateway129", "ZmlsdGVyMTI5Z2F0ZXdheTEyOQ"),
    ("filter129storage129", "ZmlsdGVyMTI5c3RvcmFnZTEyOQ"),
    ("filter129network129", "ZmlsdGVyMTI5bmV0d29yazEyOQ"),
    ("ranking129network129", "cmFua2luZzEyOW5ldHdvcmsxMjk"),
    ("ranking129latency129", "cmFua2luZzEyOWxhdGVuY3kxMjk"),
    ("ranking129buffer129", "cmFua2luZzEyOWJ1ZmZlcjEyOQ"),
    ("ranking129queue129", "cmFua2luZzEyOXF1ZXVlMTI5"),
    ("encoding129queue129", "ZW5jb2RpbmcxMjlxdWV1ZTEyOQ"),
    ("encoding129worker129", "ZW5jb2RpbmcxMjl3b3JrZXIxMjk"),
    ("encoding129kernel129", "ZW5jb2RpbmcxMjlrZXJuZWwxMjk"),
    ("encoding129signal129", "ZW5jb2RpbmcxMjlzaWduYWwxMjk"),
    ("mapping129signal129", "bWFwcGluZzEyOXNpZ25hbDEyOQ"),
    ("mapping129packet129", "bWFwcGluZzEyOXBhY2tldDEyOQ"),
    ("mapping129router129", "bWFwcGluZzEyOXJvdXRlcjEyOQ"),
    ("mapping129cluster129", "bWFwcGluZzEyOWNsdXN0ZXIxMjk"),
    ("record129cluster129", "cmVjb3JkMTI5Y2x1c3RlcjEyOQ"),
    ("record129mirror129", "cmVjb3JkMTI5bWlycm9yMTI5"),
    ("record129filter129", "cmVjb3JkMTI5ZmlsdGVyMTI5"),
    ("record129ranking129", "cmVjb3JkMTI5cmFua2luZzEyOQ"),
    ("candle129ranking129", "Y2FuZGxlMTI5cmFua2luZzEyOQ"),
    ("candle129encoding129", "Y2FuZGxlMTI5ZW5jb2RpbmcxMjk"),
    ("candle129mapping129", "Y2FuZGxlMTI5bWFwcGluZzEyOQ"),
    ("candle129record129", "Y2FuZGxlMTI5cmVjb3JkMTI5"),
    ("thread129record129", "dGhyZWFkMTI5cmVjb3JkMTI5"),
    ("thread129candle129", "dGhyZWFkMTI5Y2FuZGxlMTI5"),
    ("thread129thread129", "dGhyZWFkMTI5dGhyZWFkMTI5"),
    ("thread129kitten129", "dGhyZWFkMTI5a2l0dGVuMTI5"),
    (
        "round 129: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTI5OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 129: agentuniverse is a framework for multi agents",
        "cm91bmQgMTI5OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 129: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTI5OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 129: the processor reads the record then stops",
        "cm91bmQgMTI5OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 129: a worker pulls the next task from the queue",
        "cm91bmQgMTI5OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 129: signals travel through the network layer",
        "cm91bmQgMTI5OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 129: the gateway routes each request by policy",
        "cm91bmQgMTI5OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 129: memory grows until the buffer is full",
        "cm91bmQgMTI5OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 129: the cluster mirrors every packet twice",
        "cm91bmQgMTI5OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 129: ranking uses tokens learned from the corpus",
        "cm91bmQgMTI5OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 129: a long session ends when the candle dies",
        "cm91bmQgMTI5OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 129: encode the prompt then map the result",
        "cm91bmQgMTI5OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 129: the kernel wakes the worker at dawn",
        "cm91bmQgMTI5OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 129: service latency drops after the patch",
        "cm91bmQgMTI5OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 129: the library caches every vector it sees",
        "cm91bmQgMTI5OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 129: agents argue then the debate resolves",
        "cm91bmQgMTI5OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 129: the filter keeps only strong matches",
        "cm91bmQgMTI5OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 129: the model answers with a short reply",
        "cm91bmQgMTI5OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 129: the recorder stores the reasoning trace",
        "cm91bmQgMTI5OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 129: the angel watches the processor run",
        "cm91bmQgMTI5OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 129: angle of the vector decides the match",
        "cm91bmQgMTI5OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 129: the candle burns twice as long at night",
        "cm91bmQgMTI5OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 129: a mirror of the universe in one line",
        "cm91bmQgMTI5OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 129: the queue drains before the storm", "cm91bmQgMTI5OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
