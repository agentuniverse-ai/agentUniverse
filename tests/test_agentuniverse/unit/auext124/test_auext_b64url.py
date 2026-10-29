"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten124kitten124", "a2l0dGVuMTI0a2l0dGVuMTI0"),
    ("kitten124sitting124", "a2l0dGVuMTI0c2l0dGluZzEyNA"),
    ("kitten124agent124", "a2l0dGVuMTI0YWdlbnQxMjQ"),
    ("kitten124angle124", "a2l0dGVuMTI0YW5nbGUxMjQ"),
    ("sitting124angle124", "c2l0dGluZzEyNGFuZ2xlMTI0"),
    ("sitting124universe124", "c2l0dGluZzEyNHVuaXZlcnNlMTI0"),
    ("sitting124memory124", "c2l0dGluZzEyNG1lbW9yeTEyNA"),
    ("sitting124stream124", "c2l0dGluZzEyNHN0cmVhbTEyNA"),
    ("agent124stream124", "YWdlbnQxMjRzdHJlYW0xMjQ"),
    ("agent124context124", "YWdlbnQxMjRjb250ZXh0MTI0"),
    ("agent124knowledge124", "YWdlbnQxMjRrbm93bGVkZ2UxMjQ"),
    ("agent124vector124", "YWdlbnQxMjR2ZWN0b3IxMjQ"),
    ("angle124vector124", "YW5nbGUxMjR2ZWN0b3IxMjQ"),
    ("angle124processor124", "YW5nbGUxMjRwcm9jZXNzb3IxMjQ"),
    ("angle124reasoning124", "YW5nbGUxMjRyZWFzb25pbmcxMjQ"),
    ("angle124machine124", "YW5nbGUxMjRtYWNoaW5lMTI0"),
    ("universe124machine124", "dW5pdmVyc2UxMjRtYWNoaW5lMTI0"),
    ("universe124learning124", "dW5pdmVyc2UxMjRsZWFybmluZzEyNA"),
    ("universe124model124", "dW5pdmVyc2UxMjRtb2RlbDEyNA"),
    ("universe124token124", "dW5pdmVyc2UxMjR0b2tlbjEyNA"),
    ("memory124token124", "bWVtb3J5MTI0dG9rZW4xMjQ"),
    ("memory124prompt124", "bWVtb3J5MTI0cHJvbXB0MTI0"),
    ("memory124session124", "bWVtb3J5MTI0c2Vzc2lvbjEyNA"),
    ("memory124library124", "bWVtb3J5MTI0bGlicmFyeTEyNA"),
    ("stream124library124", "c3RyZWFtMTI0bGlicmFyeTEyNA"),
    ("stream124service124", "c3RyZWFtMTI0c2VydmljZTEyNA"),
    ("stream124gateway124", "c3RyZWFtMTI0Z2F0ZXdheTEyNA"),
    ("stream124storage124", "c3RyZWFtMTI0c3RvcmFnZTEyNA"),
    ("context124storage124", "Y29udGV4dDEyNHN0b3JhZ2UxMjQ"),
    ("context124network124", "Y29udGV4dDEyNG5ldHdvcmsxMjQ"),
    ("context124latency124", "Y29udGV4dDEyNGxhdGVuY3kxMjQ"),
    ("context124buffer124", "Y29udGV4dDEyNGJ1ZmZlcjEyNA"),
    ("knowledge124buffer124", "a25vd2xlZGdlMTI0YnVmZmVyMTI0"),
    ("knowledge124queue124", "a25vd2xlZGdlMTI0cXVldWUxMjQ"),
    ("knowledge124worker124", "a25vd2xlZGdlMTI0d29ya2VyMTI0"),
    ("knowledge124kernel124", "a25vd2xlZGdlMTI0a2VybmVsMTI0"),
    ("vector124kernel124", "dmVjdG9yMTI0a2VybmVsMTI0"),
    ("vector124signal124", "dmVjdG9yMTI0c2lnbmFsMTI0"),
    ("vector124packet124", "dmVjdG9yMTI0cGFja2V0MTI0"),
    ("vector124router124", "dmVjdG9yMTI0cm91dGVyMTI0"),
    ("processor124router124", "cHJvY2Vzc29yMTI0cm91dGVyMTI0"),
    ("processor124cluster124", "cHJvY2Vzc29yMTI0Y2x1c3RlcjEyNA"),
    ("processor124mirror124", "cHJvY2Vzc29yMTI0bWlycm9yMTI0"),
    ("processor124filter124", "cHJvY2Vzc29yMTI0ZmlsdGVyMTI0"),
    ("reasoning124filter124", "cmVhc29uaW5nMTI0ZmlsdGVyMTI0"),
    ("reasoning124ranking124", "cmVhc29uaW5nMTI0cmFua2luZzEyNA"),
    ("reasoning124encoding124", "cmVhc29uaW5nMTI0ZW5jb2RpbmcxMjQ"),
    ("reasoning124mapping124", "cmVhc29uaW5nMTI0bWFwcGluZzEyNA"),
    ("machine124mapping124", "bWFjaGluZTEyNG1hcHBpbmcxMjQ"),
    ("machine124record124", "bWFjaGluZTEyNHJlY29yZDEyNA"),
    ("machine124candle124", "bWFjaGluZTEyNGNhbmRsZTEyNA"),
    ("machine124thread124", "bWFjaGluZTEyNHRocmVhZDEyNA"),
    ("learning124thread124", "bGVhcm5pbmcxMjR0aHJlYWQxMjQ"),
    ("learning124kitten124", "bGVhcm5pbmcxMjRraXR0ZW4xMjQ"),
    ("learning124sitting124", "bGVhcm5pbmcxMjRzaXR0aW5nMTI0"),
    ("learning124agent124", "bGVhcm5pbmcxMjRhZ2VudDEyNA"),
    ("model124agent124", "bW9kZWwxMjRhZ2VudDEyNA"),
    ("model124angle124", "bW9kZWwxMjRhbmdsZTEyNA"),
    ("model124universe124", "bW9kZWwxMjR1bml2ZXJzZTEyNA"),
    ("model124memory124", "bW9kZWwxMjRtZW1vcnkxMjQ"),
    ("token124memory124", "dG9rZW4xMjRtZW1vcnkxMjQ"),
    ("token124stream124", "dG9rZW4xMjRzdHJlYW0xMjQ"),
    ("token124context124", "dG9rZW4xMjRjb250ZXh0MTI0"),
    ("token124knowledge124", "dG9rZW4xMjRrbm93bGVkZ2UxMjQ"),
    ("prompt124knowledge124", "cHJvbXB0MTI0a25vd2xlZGdlMTI0"),
    ("prompt124vector124", "cHJvbXB0MTI0dmVjdG9yMTI0"),
    ("prompt124processor124", "cHJvbXB0MTI0cHJvY2Vzc29yMTI0"),
    ("prompt124reasoning124", "cHJvbXB0MTI0cmVhc29uaW5nMTI0"),
    ("session124reasoning124", "c2Vzc2lvbjEyNHJlYXNvbmluZzEyNA"),
    ("session124machine124", "c2Vzc2lvbjEyNG1hY2hpbmUxMjQ"),
    ("session124learning124", "c2Vzc2lvbjEyNGxlYXJuaW5nMTI0"),
    ("session124model124", "c2Vzc2lvbjEyNG1vZGVsMTI0"),
    ("library124model124", "bGlicmFyeTEyNG1vZGVsMTI0"),
    ("library124token124", "bGlicmFyeTEyNHRva2VuMTI0"),
    ("library124prompt124", "bGlicmFyeTEyNHByb21wdDEyNA"),
    ("library124session124", "bGlicmFyeTEyNHNlc3Npb24xMjQ"),
    ("service124session124", "c2VydmljZTEyNHNlc3Npb24xMjQ"),
    ("service124library124", "c2VydmljZTEyNGxpYnJhcnkxMjQ"),
    ("service124service124", "c2VydmljZTEyNHNlcnZpY2UxMjQ"),
    ("service124gateway124", "c2VydmljZTEyNGdhdGV3YXkxMjQ"),
    ("gateway124gateway124", "Z2F0ZXdheTEyNGdhdGV3YXkxMjQ"),
    ("gateway124storage124", "Z2F0ZXdheTEyNHN0b3JhZ2UxMjQ"),
    ("gateway124network124", "Z2F0ZXdheTEyNG5ldHdvcmsxMjQ"),
    ("gateway124latency124", "Z2F0ZXdheTEyNGxhdGVuY3kxMjQ"),
    ("storage124latency124", "c3RvcmFnZTEyNGxhdGVuY3kxMjQ"),
    ("storage124buffer124", "c3RvcmFnZTEyNGJ1ZmZlcjEyNA"),
    ("storage124queue124", "c3RvcmFnZTEyNHF1ZXVlMTI0"),
    ("storage124worker124", "c3RvcmFnZTEyNHdvcmtlcjEyNA"),
    ("network124worker124", "bmV0d29yazEyNHdvcmtlcjEyNA"),
    ("network124kernel124", "bmV0d29yazEyNGtlcm5lbDEyNA"),
    ("network124signal124", "bmV0d29yazEyNHNpZ25hbDEyNA"),
    ("network124packet124", "bmV0d29yazEyNHBhY2tldDEyNA"),
    ("latency124packet124", "bGF0ZW5jeTEyNHBhY2tldDEyNA"),
    ("latency124router124", "bGF0ZW5jeTEyNHJvdXRlcjEyNA"),
    ("latency124cluster124", "bGF0ZW5jeTEyNGNsdXN0ZXIxMjQ"),
    ("latency124mirror124", "bGF0ZW5jeTEyNG1pcnJvcjEyNA"),
    ("buffer124mirror124", "YnVmZmVyMTI0bWlycm9yMTI0"),
    ("buffer124filter124", "YnVmZmVyMTI0ZmlsdGVyMTI0"),
    ("buffer124ranking124", "YnVmZmVyMTI0cmFua2luZzEyNA"),
    ("buffer124encoding124", "YnVmZmVyMTI0ZW5jb2RpbmcxMjQ"),
    ("queue124encoding124", "cXVldWUxMjRlbmNvZGluZzEyNA"),
    ("queue124mapping124", "cXVldWUxMjRtYXBwaW5nMTI0"),
    ("queue124record124", "cXVldWUxMjRyZWNvcmQxMjQ"),
    ("queue124candle124", "cXVldWUxMjRjYW5kbGUxMjQ"),
    ("worker124candle124", "d29ya2VyMTI0Y2FuZGxlMTI0"),
    ("worker124thread124", "d29ya2VyMTI0dGhyZWFkMTI0"),
    ("worker124kitten124", "d29ya2VyMTI0a2l0dGVuMTI0"),
    ("worker124sitting124", "d29ya2VyMTI0c2l0dGluZzEyNA"),
    ("kernel124sitting124", "a2VybmVsMTI0c2l0dGluZzEyNA"),
    ("kernel124agent124", "a2VybmVsMTI0YWdlbnQxMjQ"),
    ("kernel124angle124", "a2VybmVsMTI0YW5nbGUxMjQ"),
    ("kernel124universe124", "a2VybmVsMTI0dW5pdmVyc2UxMjQ"),
    ("signal124universe124", "c2lnbmFsMTI0dW5pdmVyc2UxMjQ"),
    ("signal124memory124", "c2lnbmFsMTI0bWVtb3J5MTI0"),
    ("signal124stream124", "c2lnbmFsMTI0c3RyZWFtMTI0"),
    ("signal124context124", "c2lnbmFsMTI0Y29udGV4dDEyNA"),
    ("packet124context124", "cGFja2V0MTI0Y29udGV4dDEyNA"),
    ("packet124knowledge124", "cGFja2V0MTI0a25vd2xlZGdlMTI0"),
    ("packet124vector124", "cGFja2V0MTI0dmVjdG9yMTI0"),
    ("packet124processor124", "cGFja2V0MTI0cHJvY2Vzc29yMTI0"),
    ("router124processor124", "cm91dGVyMTI0cHJvY2Vzc29yMTI0"),
    ("router124reasoning124", "cm91dGVyMTI0cmVhc29uaW5nMTI0"),
    ("router124machine124", "cm91dGVyMTI0bWFjaGluZTEyNA"),
    ("router124learning124", "cm91dGVyMTI0bGVhcm5pbmcxMjQ"),
    ("cluster124learning124", "Y2x1c3RlcjEyNGxlYXJuaW5nMTI0"),
    ("cluster124model124", "Y2x1c3RlcjEyNG1vZGVsMTI0"),
    ("cluster124token124", "Y2x1c3RlcjEyNHRva2VuMTI0"),
    ("cluster124prompt124", "Y2x1c3RlcjEyNHByb21wdDEyNA"),
    ("mirror124prompt124", "bWlycm9yMTI0cHJvbXB0MTI0"),
    ("mirror124session124", "bWlycm9yMTI0c2Vzc2lvbjEyNA"),
    ("mirror124library124", "bWlycm9yMTI0bGlicmFyeTEyNA"),
    ("mirror124service124", "bWlycm9yMTI0c2VydmljZTEyNA"),
    ("filter124service124", "ZmlsdGVyMTI0c2VydmljZTEyNA"),
    ("filter124gateway124", "ZmlsdGVyMTI0Z2F0ZXdheTEyNA"),
    ("filter124storage124", "ZmlsdGVyMTI0c3RvcmFnZTEyNA"),
    ("filter124network124", "ZmlsdGVyMTI0bmV0d29yazEyNA"),
    ("ranking124network124", "cmFua2luZzEyNG5ldHdvcmsxMjQ"),
    ("ranking124latency124", "cmFua2luZzEyNGxhdGVuY3kxMjQ"),
    ("ranking124buffer124", "cmFua2luZzEyNGJ1ZmZlcjEyNA"),
    ("ranking124queue124", "cmFua2luZzEyNHF1ZXVlMTI0"),
    ("encoding124queue124", "ZW5jb2RpbmcxMjRxdWV1ZTEyNA"),
    ("encoding124worker124", "ZW5jb2RpbmcxMjR3b3JrZXIxMjQ"),
    ("encoding124kernel124", "ZW5jb2RpbmcxMjRrZXJuZWwxMjQ"),
    ("encoding124signal124", "ZW5jb2RpbmcxMjRzaWduYWwxMjQ"),
    ("mapping124signal124", "bWFwcGluZzEyNHNpZ25hbDEyNA"),
    ("mapping124packet124", "bWFwcGluZzEyNHBhY2tldDEyNA"),
    ("mapping124router124", "bWFwcGluZzEyNHJvdXRlcjEyNA"),
    ("mapping124cluster124", "bWFwcGluZzEyNGNsdXN0ZXIxMjQ"),
    ("record124cluster124", "cmVjb3JkMTI0Y2x1c3RlcjEyNA"),
    ("record124mirror124", "cmVjb3JkMTI0bWlycm9yMTI0"),
    ("record124filter124", "cmVjb3JkMTI0ZmlsdGVyMTI0"),
    ("record124ranking124", "cmVjb3JkMTI0cmFua2luZzEyNA"),
    ("candle124ranking124", "Y2FuZGxlMTI0cmFua2luZzEyNA"),
    ("candle124encoding124", "Y2FuZGxlMTI0ZW5jb2RpbmcxMjQ"),
    ("candle124mapping124", "Y2FuZGxlMTI0bWFwcGluZzEyNA"),
    ("candle124record124", "Y2FuZGxlMTI0cmVjb3JkMTI0"),
    ("thread124record124", "dGhyZWFkMTI0cmVjb3JkMTI0"),
    ("thread124candle124", "dGhyZWFkMTI0Y2FuZGxlMTI0"),
    ("thread124thread124", "dGhyZWFkMTI0dGhyZWFkMTI0"),
    ("thread124kitten124", "dGhyZWFkMTI0a2l0dGVuMTI0"),
    (
        "round 124: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTI0OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 124: agentuniverse is a framework for multi agents",
        "cm91bmQgMTI0OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 124: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTI0OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 124: the processor reads the record then stops",
        "cm91bmQgMTI0OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 124: a worker pulls the next task from the queue",
        "cm91bmQgMTI0OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 124: signals travel through the network layer",
        "cm91bmQgMTI0OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 124: the gateway routes each request by policy",
        "cm91bmQgMTI0OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 124: memory grows until the buffer is full",
        "cm91bmQgMTI0OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 124: the cluster mirrors every packet twice",
        "cm91bmQgMTI0OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 124: ranking uses tokens learned from the corpus",
        "cm91bmQgMTI0OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 124: a long session ends when the candle dies",
        "cm91bmQgMTI0OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 124: encode the prompt then map the result",
        "cm91bmQgMTI0OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 124: the kernel wakes the worker at dawn",
        "cm91bmQgMTI0OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 124: service latency drops after the patch",
        "cm91bmQgMTI0OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 124: the library caches every vector it sees",
        "cm91bmQgMTI0OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 124: agents argue then the debate resolves",
        "cm91bmQgMTI0OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 124: the filter keeps only strong matches",
        "cm91bmQgMTI0OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 124: the model answers with a short reply",
        "cm91bmQgMTI0OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 124: the recorder stores the reasoning trace",
        "cm91bmQgMTI0OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 124: the angel watches the processor run",
        "cm91bmQgMTI0OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 124: angle of the vector decides the match",
        "cm91bmQgMTI0OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 124: the candle burns twice as long at night",
        "cm91bmQgMTI0OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 124: a mirror of the universe in one line",
        "cm91bmQgMTI0OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 124: the queue drains before the storm", "cm91bmQgMTI0OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
