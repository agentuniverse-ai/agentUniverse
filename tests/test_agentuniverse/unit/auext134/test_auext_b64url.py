"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten134kitten134", "a2l0dGVuMTM0a2l0dGVuMTM0"),
    ("kitten134sitting134", "a2l0dGVuMTM0c2l0dGluZzEzNA"),
    ("kitten134agent134", "a2l0dGVuMTM0YWdlbnQxMzQ"),
    ("kitten134angle134", "a2l0dGVuMTM0YW5nbGUxMzQ"),
    ("sitting134angle134", "c2l0dGluZzEzNGFuZ2xlMTM0"),
    ("sitting134universe134", "c2l0dGluZzEzNHVuaXZlcnNlMTM0"),
    ("sitting134memory134", "c2l0dGluZzEzNG1lbW9yeTEzNA"),
    ("sitting134stream134", "c2l0dGluZzEzNHN0cmVhbTEzNA"),
    ("agent134stream134", "YWdlbnQxMzRzdHJlYW0xMzQ"),
    ("agent134context134", "YWdlbnQxMzRjb250ZXh0MTM0"),
    ("agent134knowledge134", "YWdlbnQxMzRrbm93bGVkZ2UxMzQ"),
    ("agent134vector134", "YWdlbnQxMzR2ZWN0b3IxMzQ"),
    ("angle134vector134", "YW5nbGUxMzR2ZWN0b3IxMzQ"),
    ("angle134processor134", "YW5nbGUxMzRwcm9jZXNzb3IxMzQ"),
    ("angle134reasoning134", "YW5nbGUxMzRyZWFzb25pbmcxMzQ"),
    ("angle134machine134", "YW5nbGUxMzRtYWNoaW5lMTM0"),
    ("universe134machine134", "dW5pdmVyc2UxMzRtYWNoaW5lMTM0"),
    ("universe134learning134", "dW5pdmVyc2UxMzRsZWFybmluZzEzNA"),
    ("universe134model134", "dW5pdmVyc2UxMzRtb2RlbDEzNA"),
    ("universe134token134", "dW5pdmVyc2UxMzR0b2tlbjEzNA"),
    ("memory134token134", "bWVtb3J5MTM0dG9rZW4xMzQ"),
    ("memory134prompt134", "bWVtb3J5MTM0cHJvbXB0MTM0"),
    ("memory134session134", "bWVtb3J5MTM0c2Vzc2lvbjEzNA"),
    ("memory134library134", "bWVtb3J5MTM0bGlicmFyeTEzNA"),
    ("stream134library134", "c3RyZWFtMTM0bGlicmFyeTEzNA"),
    ("stream134service134", "c3RyZWFtMTM0c2VydmljZTEzNA"),
    ("stream134gateway134", "c3RyZWFtMTM0Z2F0ZXdheTEzNA"),
    ("stream134storage134", "c3RyZWFtMTM0c3RvcmFnZTEzNA"),
    ("context134storage134", "Y29udGV4dDEzNHN0b3JhZ2UxMzQ"),
    ("context134network134", "Y29udGV4dDEzNG5ldHdvcmsxMzQ"),
    ("context134latency134", "Y29udGV4dDEzNGxhdGVuY3kxMzQ"),
    ("context134buffer134", "Y29udGV4dDEzNGJ1ZmZlcjEzNA"),
    ("knowledge134buffer134", "a25vd2xlZGdlMTM0YnVmZmVyMTM0"),
    ("knowledge134queue134", "a25vd2xlZGdlMTM0cXVldWUxMzQ"),
    ("knowledge134worker134", "a25vd2xlZGdlMTM0d29ya2VyMTM0"),
    ("knowledge134kernel134", "a25vd2xlZGdlMTM0a2VybmVsMTM0"),
    ("vector134kernel134", "dmVjdG9yMTM0a2VybmVsMTM0"),
    ("vector134signal134", "dmVjdG9yMTM0c2lnbmFsMTM0"),
    ("vector134packet134", "dmVjdG9yMTM0cGFja2V0MTM0"),
    ("vector134router134", "dmVjdG9yMTM0cm91dGVyMTM0"),
    ("processor134router134", "cHJvY2Vzc29yMTM0cm91dGVyMTM0"),
    ("processor134cluster134", "cHJvY2Vzc29yMTM0Y2x1c3RlcjEzNA"),
    ("processor134mirror134", "cHJvY2Vzc29yMTM0bWlycm9yMTM0"),
    ("processor134filter134", "cHJvY2Vzc29yMTM0ZmlsdGVyMTM0"),
    ("reasoning134filter134", "cmVhc29uaW5nMTM0ZmlsdGVyMTM0"),
    ("reasoning134ranking134", "cmVhc29uaW5nMTM0cmFua2luZzEzNA"),
    ("reasoning134encoding134", "cmVhc29uaW5nMTM0ZW5jb2RpbmcxMzQ"),
    ("reasoning134mapping134", "cmVhc29uaW5nMTM0bWFwcGluZzEzNA"),
    ("machine134mapping134", "bWFjaGluZTEzNG1hcHBpbmcxMzQ"),
    ("machine134record134", "bWFjaGluZTEzNHJlY29yZDEzNA"),
    ("machine134candle134", "bWFjaGluZTEzNGNhbmRsZTEzNA"),
    ("machine134thread134", "bWFjaGluZTEzNHRocmVhZDEzNA"),
    ("learning134thread134", "bGVhcm5pbmcxMzR0aHJlYWQxMzQ"),
    ("learning134kitten134", "bGVhcm5pbmcxMzRraXR0ZW4xMzQ"),
    ("learning134sitting134", "bGVhcm5pbmcxMzRzaXR0aW5nMTM0"),
    ("learning134agent134", "bGVhcm5pbmcxMzRhZ2VudDEzNA"),
    ("model134agent134", "bW9kZWwxMzRhZ2VudDEzNA"),
    ("model134angle134", "bW9kZWwxMzRhbmdsZTEzNA"),
    ("model134universe134", "bW9kZWwxMzR1bml2ZXJzZTEzNA"),
    ("model134memory134", "bW9kZWwxMzRtZW1vcnkxMzQ"),
    ("token134memory134", "dG9rZW4xMzRtZW1vcnkxMzQ"),
    ("token134stream134", "dG9rZW4xMzRzdHJlYW0xMzQ"),
    ("token134context134", "dG9rZW4xMzRjb250ZXh0MTM0"),
    ("token134knowledge134", "dG9rZW4xMzRrbm93bGVkZ2UxMzQ"),
    ("prompt134knowledge134", "cHJvbXB0MTM0a25vd2xlZGdlMTM0"),
    ("prompt134vector134", "cHJvbXB0MTM0dmVjdG9yMTM0"),
    ("prompt134processor134", "cHJvbXB0MTM0cHJvY2Vzc29yMTM0"),
    ("prompt134reasoning134", "cHJvbXB0MTM0cmVhc29uaW5nMTM0"),
    ("session134reasoning134", "c2Vzc2lvbjEzNHJlYXNvbmluZzEzNA"),
    ("session134machine134", "c2Vzc2lvbjEzNG1hY2hpbmUxMzQ"),
    ("session134learning134", "c2Vzc2lvbjEzNGxlYXJuaW5nMTM0"),
    ("session134model134", "c2Vzc2lvbjEzNG1vZGVsMTM0"),
    ("library134model134", "bGlicmFyeTEzNG1vZGVsMTM0"),
    ("library134token134", "bGlicmFyeTEzNHRva2VuMTM0"),
    ("library134prompt134", "bGlicmFyeTEzNHByb21wdDEzNA"),
    ("library134session134", "bGlicmFyeTEzNHNlc3Npb24xMzQ"),
    ("service134session134", "c2VydmljZTEzNHNlc3Npb24xMzQ"),
    ("service134library134", "c2VydmljZTEzNGxpYnJhcnkxMzQ"),
    ("service134service134", "c2VydmljZTEzNHNlcnZpY2UxMzQ"),
    ("service134gateway134", "c2VydmljZTEzNGdhdGV3YXkxMzQ"),
    ("gateway134gateway134", "Z2F0ZXdheTEzNGdhdGV3YXkxMzQ"),
    ("gateway134storage134", "Z2F0ZXdheTEzNHN0b3JhZ2UxMzQ"),
    ("gateway134network134", "Z2F0ZXdheTEzNG5ldHdvcmsxMzQ"),
    ("gateway134latency134", "Z2F0ZXdheTEzNGxhdGVuY3kxMzQ"),
    ("storage134latency134", "c3RvcmFnZTEzNGxhdGVuY3kxMzQ"),
    ("storage134buffer134", "c3RvcmFnZTEzNGJ1ZmZlcjEzNA"),
    ("storage134queue134", "c3RvcmFnZTEzNHF1ZXVlMTM0"),
    ("storage134worker134", "c3RvcmFnZTEzNHdvcmtlcjEzNA"),
    ("network134worker134", "bmV0d29yazEzNHdvcmtlcjEzNA"),
    ("network134kernel134", "bmV0d29yazEzNGtlcm5lbDEzNA"),
    ("network134signal134", "bmV0d29yazEzNHNpZ25hbDEzNA"),
    ("network134packet134", "bmV0d29yazEzNHBhY2tldDEzNA"),
    ("latency134packet134", "bGF0ZW5jeTEzNHBhY2tldDEzNA"),
    ("latency134router134", "bGF0ZW5jeTEzNHJvdXRlcjEzNA"),
    ("latency134cluster134", "bGF0ZW5jeTEzNGNsdXN0ZXIxMzQ"),
    ("latency134mirror134", "bGF0ZW5jeTEzNG1pcnJvcjEzNA"),
    ("buffer134mirror134", "YnVmZmVyMTM0bWlycm9yMTM0"),
    ("buffer134filter134", "YnVmZmVyMTM0ZmlsdGVyMTM0"),
    ("buffer134ranking134", "YnVmZmVyMTM0cmFua2luZzEzNA"),
    ("buffer134encoding134", "YnVmZmVyMTM0ZW5jb2RpbmcxMzQ"),
    ("queue134encoding134", "cXVldWUxMzRlbmNvZGluZzEzNA"),
    ("queue134mapping134", "cXVldWUxMzRtYXBwaW5nMTM0"),
    ("queue134record134", "cXVldWUxMzRyZWNvcmQxMzQ"),
    ("queue134candle134", "cXVldWUxMzRjYW5kbGUxMzQ"),
    ("worker134candle134", "d29ya2VyMTM0Y2FuZGxlMTM0"),
    ("worker134thread134", "d29ya2VyMTM0dGhyZWFkMTM0"),
    ("worker134kitten134", "d29ya2VyMTM0a2l0dGVuMTM0"),
    ("worker134sitting134", "d29ya2VyMTM0c2l0dGluZzEzNA"),
    ("kernel134sitting134", "a2VybmVsMTM0c2l0dGluZzEzNA"),
    ("kernel134agent134", "a2VybmVsMTM0YWdlbnQxMzQ"),
    ("kernel134angle134", "a2VybmVsMTM0YW5nbGUxMzQ"),
    ("kernel134universe134", "a2VybmVsMTM0dW5pdmVyc2UxMzQ"),
    ("signal134universe134", "c2lnbmFsMTM0dW5pdmVyc2UxMzQ"),
    ("signal134memory134", "c2lnbmFsMTM0bWVtb3J5MTM0"),
    ("signal134stream134", "c2lnbmFsMTM0c3RyZWFtMTM0"),
    ("signal134context134", "c2lnbmFsMTM0Y29udGV4dDEzNA"),
    ("packet134context134", "cGFja2V0MTM0Y29udGV4dDEzNA"),
    ("packet134knowledge134", "cGFja2V0MTM0a25vd2xlZGdlMTM0"),
    ("packet134vector134", "cGFja2V0MTM0dmVjdG9yMTM0"),
    ("packet134processor134", "cGFja2V0MTM0cHJvY2Vzc29yMTM0"),
    ("router134processor134", "cm91dGVyMTM0cHJvY2Vzc29yMTM0"),
    ("router134reasoning134", "cm91dGVyMTM0cmVhc29uaW5nMTM0"),
    ("router134machine134", "cm91dGVyMTM0bWFjaGluZTEzNA"),
    ("router134learning134", "cm91dGVyMTM0bGVhcm5pbmcxMzQ"),
    ("cluster134learning134", "Y2x1c3RlcjEzNGxlYXJuaW5nMTM0"),
    ("cluster134model134", "Y2x1c3RlcjEzNG1vZGVsMTM0"),
    ("cluster134token134", "Y2x1c3RlcjEzNHRva2VuMTM0"),
    ("cluster134prompt134", "Y2x1c3RlcjEzNHByb21wdDEzNA"),
    ("mirror134prompt134", "bWlycm9yMTM0cHJvbXB0MTM0"),
    ("mirror134session134", "bWlycm9yMTM0c2Vzc2lvbjEzNA"),
    ("mirror134library134", "bWlycm9yMTM0bGlicmFyeTEzNA"),
    ("mirror134service134", "bWlycm9yMTM0c2VydmljZTEzNA"),
    ("filter134service134", "ZmlsdGVyMTM0c2VydmljZTEzNA"),
    ("filter134gateway134", "ZmlsdGVyMTM0Z2F0ZXdheTEzNA"),
    ("filter134storage134", "ZmlsdGVyMTM0c3RvcmFnZTEzNA"),
    ("filter134network134", "ZmlsdGVyMTM0bmV0d29yazEzNA"),
    ("ranking134network134", "cmFua2luZzEzNG5ldHdvcmsxMzQ"),
    ("ranking134latency134", "cmFua2luZzEzNGxhdGVuY3kxMzQ"),
    ("ranking134buffer134", "cmFua2luZzEzNGJ1ZmZlcjEzNA"),
    ("ranking134queue134", "cmFua2luZzEzNHF1ZXVlMTM0"),
    ("encoding134queue134", "ZW5jb2RpbmcxMzRxdWV1ZTEzNA"),
    ("encoding134worker134", "ZW5jb2RpbmcxMzR3b3JrZXIxMzQ"),
    ("encoding134kernel134", "ZW5jb2RpbmcxMzRrZXJuZWwxMzQ"),
    ("encoding134signal134", "ZW5jb2RpbmcxMzRzaWduYWwxMzQ"),
    ("mapping134signal134", "bWFwcGluZzEzNHNpZ25hbDEzNA"),
    ("mapping134packet134", "bWFwcGluZzEzNHBhY2tldDEzNA"),
    ("mapping134router134", "bWFwcGluZzEzNHJvdXRlcjEzNA"),
    ("mapping134cluster134", "bWFwcGluZzEzNGNsdXN0ZXIxMzQ"),
    ("record134cluster134", "cmVjb3JkMTM0Y2x1c3RlcjEzNA"),
    ("record134mirror134", "cmVjb3JkMTM0bWlycm9yMTM0"),
    ("record134filter134", "cmVjb3JkMTM0ZmlsdGVyMTM0"),
    ("record134ranking134", "cmVjb3JkMTM0cmFua2luZzEzNA"),
    ("candle134ranking134", "Y2FuZGxlMTM0cmFua2luZzEzNA"),
    ("candle134encoding134", "Y2FuZGxlMTM0ZW5jb2RpbmcxMzQ"),
    ("candle134mapping134", "Y2FuZGxlMTM0bWFwcGluZzEzNA"),
    ("candle134record134", "Y2FuZGxlMTM0cmVjb3JkMTM0"),
    ("thread134record134", "dGhyZWFkMTM0cmVjb3JkMTM0"),
    ("thread134candle134", "dGhyZWFkMTM0Y2FuZGxlMTM0"),
    ("thread134thread134", "dGhyZWFkMTM0dGhyZWFkMTM0"),
    ("thread134kitten134", "dGhyZWFkMTM0a2l0dGVuMTM0"),
    (
        "round 134: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTM0OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 134: agentuniverse is a framework for multi agents",
        "cm91bmQgMTM0OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 134: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTM0OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 134: the processor reads the record then stops",
        "cm91bmQgMTM0OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 134: a worker pulls the next task from the queue",
        "cm91bmQgMTM0OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 134: signals travel through the network layer",
        "cm91bmQgMTM0OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 134: the gateway routes each request by policy",
        "cm91bmQgMTM0OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 134: memory grows until the buffer is full",
        "cm91bmQgMTM0OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 134: the cluster mirrors every packet twice",
        "cm91bmQgMTM0OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 134: ranking uses tokens learned from the corpus",
        "cm91bmQgMTM0OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 134: a long session ends when the candle dies",
        "cm91bmQgMTM0OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 134: encode the prompt then map the result",
        "cm91bmQgMTM0OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 134: the kernel wakes the worker at dawn",
        "cm91bmQgMTM0OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 134: service latency drops after the patch",
        "cm91bmQgMTM0OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 134: the library caches every vector it sees",
        "cm91bmQgMTM0OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 134: agents argue then the debate resolves",
        "cm91bmQgMTM0OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 134: the filter keeps only strong matches",
        "cm91bmQgMTM0OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 134: the model answers with a short reply",
        "cm91bmQgMTM0OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 134: the recorder stores the reasoning trace",
        "cm91bmQgMTM0OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 134: the angel watches the processor run",
        "cm91bmQgMTM0OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 134: angle of the vector decides the match",
        "cm91bmQgMTM0OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 134: the candle burns twice as long at night",
        "cm91bmQgMTM0OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 134: a mirror of the universe in one line",
        "cm91bmQgMTM0OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 134: the queue drains before the storm", "cm91bmQgMTM0OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
