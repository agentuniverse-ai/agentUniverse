"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten101kitten101", "a2l0dGVuMTAxa2l0dGVuMTAx"),
    ("kitten101sitting101", "a2l0dGVuMTAxc2l0dGluZzEwMQ"),
    ("kitten101agent101", "a2l0dGVuMTAxYWdlbnQxMDE"),
    ("kitten101angle101", "a2l0dGVuMTAxYW5nbGUxMDE"),
    ("sitting101angle101", "c2l0dGluZzEwMWFuZ2xlMTAx"),
    ("sitting101universe101", "c2l0dGluZzEwMXVuaXZlcnNlMTAx"),
    ("sitting101memory101", "c2l0dGluZzEwMW1lbW9yeTEwMQ"),
    ("sitting101stream101", "c2l0dGluZzEwMXN0cmVhbTEwMQ"),
    ("agent101stream101", "YWdlbnQxMDFzdHJlYW0xMDE"),
    ("agent101context101", "YWdlbnQxMDFjb250ZXh0MTAx"),
    ("agent101knowledge101", "YWdlbnQxMDFrbm93bGVkZ2UxMDE"),
    ("agent101vector101", "YWdlbnQxMDF2ZWN0b3IxMDE"),
    ("angle101vector101", "YW5nbGUxMDF2ZWN0b3IxMDE"),
    ("angle101processor101", "YW5nbGUxMDFwcm9jZXNzb3IxMDE"),
    ("angle101reasoning101", "YW5nbGUxMDFyZWFzb25pbmcxMDE"),
    ("angle101machine101", "YW5nbGUxMDFtYWNoaW5lMTAx"),
    ("universe101machine101", "dW5pdmVyc2UxMDFtYWNoaW5lMTAx"),
    ("universe101learning101", "dW5pdmVyc2UxMDFsZWFybmluZzEwMQ"),
    ("universe101model101", "dW5pdmVyc2UxMDFtb2RlbDEwMQ"),
    ("universe101token101", "dW5pdmVyc2UxMDF0b2tlbjEwMQ"),
    ("memory101token101", "bWVtb3J5MTAxdG9rZW4xMDE"),
    ("memory101prompt101", "bWVtb3J5MTAxcHJvbXB0MTAx"),
    ("memory101session101", "bWVtb3J5MTAxc2Vzc2lvbjEwMQ"),
    ("memory101library101", "bWVtb3J5MTAxbGlicmFyeTEwMQ"),
    ("stream101library101", "c3RyZWFtMTAxbGlicmFyeTEwMQ"),
    ("stream101service101", "c3RyZWFtMTAxc2VydmljZTEwMQ"),
    ("stream101gateway101", "c3RyZWFtMTAxZ2F0ZXdheTEwMQ"),
    ("stream101storage101", "c3RyZWFtMTAxc3RvcmFnZTEwMQ"),
    ("context101storage101", "Y29udGV4dDEwMXN0b3JhZ2UxMDE"),
    ("context101network101", "Y29udGV4dDEwMW5ldHdvcmsxMDE"),
    ("context101latency101", "Y29udGV4dDEwMWxhdGVuY3kxMDE"),
    ("context101buffer101", "Y29udGV4dDEwMWJ1ZmZlcjEwMQ"),
    ("knowledge101buffer101", "a25vd2xlZGdlMTAxYnVmZmVyMTAx"),
    ("knowledge101queue101", "a25vd2xlZGdlMTAxcXVldWUxMDE"),
    ("knowledge101worker101", "a25vd2xlZGdlMTAxd29ya2VyMTAx"),
    ("knowledge101kernel101", "a25vd2xlZGdlMTAxa2VybmVsMTAx"),
    ("vector101kernel101", "dmVjdG9yMTAxa2VybmVsMTAx"),
    ("vector101signal101", "dmVjdG9yMTAxc2lnbmFsMTAx"),
    ("vector101packet101", "dmVjdG9yMTAxcGFja2V0MTAx"),
    ("vector101router101", "dmVjdG9yMTAxcm91dGVyMTAx"),
    ("processor101router101", "cHJvY2Vzc29yMTAxcm91dGVyMTAx"),
    ("processor101cluster101", "cHJvY2Vzc29yMTAxY2x1c3RlcjEwMQ"),
    ("processor101mirror101", "cHJvY2Vzc29yMTAxbWlycm9yMTAx"),
    ("processor101filter101", "cHJvY2Vzc29yMTAxZmlsdGVyMTAx"),
    ("reasoning101filter101", "cmVhc29uaW5nMTAxZmlsdGVyMTAx"),
    ("reasoning101ranking101", "cmVhc29uaW5nMTAxcmFua2luZzEwMQ"),
    ("reasoning101encoding101", "cmVhc29uaW5nMTAxZW5jb2RpbmcxMDE"),
    ("reasoning101mapping101", "cmVhc29uaW5nMTAxbWFwcGluZzEwMQ"),
    ("machine101mapping101", "bWFjaGluZTEwMW1hcHBpbmcxMDE"),
    ("machine101record101", "bWFjaGluZTEwMXJlY29yZDEwMQ"),
    ("machine101candle101", "bWFjaGluZTEwMWNhbmRsZTEwMQ"),
    ("machine101thread101", "bWFjaGluZTEwMXRocmVhZDEwMQ"),
    ("learning101thread101", "bGVhcm5pbmcxMDF0aHJlYWQxMDE"),
    ("learning101kitten101", "bGVhcm5pbmcxMDFraXR0ZW4xMDE"),
    ("learning101sitting101", "bGVhcm5pbmcxMDFzaXR0aW5nMTAx"),
    ("learning101agent101", "bGVhcm5pbmcxMDFhZ2VudDEwMQ"),
    ("model101agent101", "bW9kZWwxMDFhZ2VudDEwMQ"),
    ("model101angle101", "bW9kZWwxMDFhbmdsZTEwMQ"),
    ("model101universe101", "bW9kZWwxMDF1bml2ZXJzZTEwMQ"),
    ("model101memory101", "bW9kZWwxMDFtZW1vcnkxMDE"),
    ("token101memory101", "dG9rZW4xMDFtZW1vcnkxMDE"),
    ("token101stream101", "dG9rZW4xMDFzdHJlYW0xMDE"),
    ("token101context101", "dG9rZW4xMDFjb250ZXh0MTAx"),
    ("token101knowledge101", "dG9rZW4xMDFrbm93bGVkZ2UxMDE"),
    ("prompt101knowledge101", "cHJvbXB0MTAxa25vd2xlZGdlMTAx"),
    ("prompt101vector101", "cHJvbXB0MTAxdmVjdG9yMTAx"),
    ("prompt101processor101", "cHJvbXB0MTAxcHJvY2Vzc29yMTAx"),
    ("prompt101reasoning101", "cHJvbXB0MTAxcmVhc29uaW5nMTAx"),
    ("session101reasoning101", "c2Vzc2lvbjEwMXJlYXNvbmluZzEwMQ"),
    ("session101machine101", "c2Vzc2lvbjEwMW1hY2hpbmUxMDE"),
    ("session101learning101", "c2Vzc2lvbjEwMWxlYXJuaW5nMTAx"),
    ("session101model101", "c2Vzc2lvbjEwMW1vZGVsMTAx"),
    ("library101model101", "bGlicmFyeTEwMW1vZGVsMTAx"),
    ("library101token101", "bGlicmFyeTEwMXRva2VuMTAx"),
    ("library101prompt101", "bGlicmFyeTEwMXByb21wdDEwMQ"),
    ("library101session101", "bGlicmFyeTEwMXNlc3Npb24xMDE"),
    ("service101session101", "c2VydmljZTEwMXNlc3Npb24xMDE"),
    ("service101library101", "c2VydmljZTEwMWxpYnJhcnkxMDE"),
    ("service101service101", "c2VydmljZTEwMXNlcnZpY2UxMDE"),
    ("service101gateway101", "c2VydmljZTEwMWdhdGV3YXkxMDE"),
    ("gateway101gateway101", "Z2F0ZXdheTEwMWdhdGV3YXkxMDE"),
    ("gateway101storage101", "Z2F0ZXdheTEwMXN0b3JhZ2UxMDE"),
    ("gateway101network101", "Z2F0ZXdheTEwMW5ldHdvcmsxMDE"),
    ("gateway101latency101", "Z2F0ZXdheTEwMWxhdGVuY3kxMDE"),
    ("storage101latency101", "c3RvcmFnZTEwMWxhdGVuY3kxMDE"),
    ("storage101buffer101", "c3RvcmFnZTEwMWJ1ZmZlcjEwMQ"),
    ("storage101queue101", "c3RvcmFnZTEwMXF1ZXVlMTAx"),
    ("storage101worker101", "c3RvcmFnZTEwMXdvcmtlcjEwMQ"),
    ("network101worker101", "bmV0d29yazEwMXdvcmtlcjEwMQ"),
    ("network101kernel101", "bmV0d29yazEwMWtlcm5lbDEwMQ"),
    ("network101signal101", "bmV0d29yazEwMXNpZ25hbDEwMQ"),
    ("network101packet101", "bmV0d29yazEwMXBhY2tldDEwMQ"),
    ("latency101packet101", "bGF0ZW5jeTEwMXBhY2tldDEwMQ"),
    ("latency101router101", "bGF0ZW5jeTEwMXJvdXRlcjEwMQ"),
    ("latency101cluster101", "bGF0ZW5jeTEwMWNsdXN0ZXIxMDE"),
    ("latency101mirror101", "bGF0ZW5jeTEwMW1pcnJvcjEwMQ"),
    ("buffer101mirror101", "YnVmZmVyMTAxbWlycm9yMTAx"),
    ("buffer101filter101", "YnVmZmVyMTAxZmlsdGVyMTAx"),
    ("buffer101ranking101", "YnVmZmVyMTAxcmFua2luZzEwMQ"),
    ("buffer101encoding101", "YnVmZmVyMTAxZW5jb2RpbmcxMDE"),
    ("queue101encoding101", "cXVldWUxMDFlbmNvZGluZzEwMQ"),
    ("queue101mapping101", "cXVldWUxMDFtYXBwaW5nMTAx"),
    ("queue101record101", "cXVldWUxMDFyZWNvcmQxMDE"),
    ("queue101candle101", "cXVldWUxMDFjYW5kbGUxMDE"),
    ("worker101candle101", "d29ya2VyMTAxY2FuZGxlMTAx"),
    ("worker101thread101", "d29ya2VyMTAxdGhyZWFkMTAx"),
    ("worker101kitten101", "d29ya2VyMTAxa2l0dGVuMTAx"),
    ("worker101sitting101", "d29ya2VyMTAxc2l0dGluZzEwMQ"),
    ("kernel101sitting101", "a2VybmVsMTAxc2l0dGluZzEwMQ"),
    ("kernel101agent101", "a2VybmVsMTAxYWdlbnQxMDE"),
    ("kernel101angle101", "a2VybmVsMTAxYW5nbGUxMDE"),
    ("kernel101universe101", "a2VybmVsMTAxdW5pdmVyc2UxMDE"),
    ("signal101universe101", "c2lnbmFsMTAxdW5pdmVyc2UxMDE"),
    ("signal101memory101", "c2lnbmFsMTAxbWVtb3J5MTAx"),
    ("signal101stream101", "c2lnbmFsMTAxc3RyZWFtMTAx"),
    ("signal101context101", "c2lnbmFsMTAxY29udGV4dDEwMQ"),
    ("packet101context101", "cGFja2V0MTAxY29udGV4dDEwMQ"),
    ("packet101knowledge101", "cGFja2V0MTAxa25vd2xlZGdlMTAx"),
    ("packet101vector101", "cGFja2V0MTAxdmVjdG9yMTAx"),
    ("packet101processor101", "cGFja2V0MTAxcHJvY2Vzc29yMTAx"),
    ("router101processor101", "cm91dGVyMTAxcHJvY2Vzc29yMTAx"),
    ("router101reasoning101", "cm91dGVyMTAxcmVhc29uaW5nMTAx"),
    ("router101machine101", "cm91dGVyMTAxbWFjaGluZTEwMQ"),
    ("router101learning101", "cm91dGVyMTAxbGVhcm5pbmcxMDE"),
    ("cluster101learning101", "Y2x1c3RlcjEwMWxlYXJuaW5nMTAx"),
    ("cluster101model101", "Y2x1c3RlcjEwMW1vZGVsMTAx"),
    ("cluster101token101", "Y2x1c3RlcjEwMXRva2VuMTAx"),
    ("cluster101prompt101", "Y2x1c3RlcjEwMXByb21wdDEwMQ"),
    ("mirror101prompt101", "bWlycm9yMTAxcHJvbXB0MTAx"),
    ("mirror101session101", "bWlycm9yMTAxc2Vzc2lvbjEwMQ"),
    ("mirror101library101", "bWlycm9yMTAxbGlicmFyeTEwMQ"),
    ("mirror101service101", "bWlycm9yMTAxc2VydmljZTEwMQ"),
    ("filter101service101", "ZmlsdGVyMTAxc2VydmljZTEwMQ"),
    ("filter101gateway101", "ZmlsdGVyMTAxZ2F0ZXdheTEwMQ"),
    ("filter101storage101", "ZmlsdGVyMTAxc3RvcmFnZTEwMQ"),
    ("filter101network101", "ZmlsdGVyMTAxbmV0d29yazEwMQ"),
    ("ranking101network101", "cmFua2luZzEwMW5ldHdvcmsxMDE"),
    ("ranking101latency101", "cmFua2luZzEwMWxhdGVuY3kxMDE"),
    ("ranking101buffer101", "cmFua2luZzEwMWJ1ZmZlcjEwMQ"),
    ("ranking101queue101", "cmFua2luZzEwMXF1ZXVlMTAx"),
    ("encoding101queue101", "ZW5jb2RpbmcxMDFxdWV1ZTEwMQ"),
    ("encoding101worker101", "ZW5jb2RpbmcxMDF3b3JrZXIxMDE"),
    ("encoding101kernel101", "ZW5jb2RpbmcxMDFrZXJuZWwxMDE"),
    ("encoding101signal101", "ZW5jb2RpbmcxMDFzaWduYWwxMDE"),
    ("mapping101signal101", "bWFwcGluZzEwMXNpZ25hbDEwMQ"),
    ("mapping101packet101", "bWFwcGluZzEwMXBhY2tldDEwMQ"),
    ("mapping101router101", "bWFwcGluZzEwMXJvdXRlcjEwMQ"),
    ("mapping101cluster101", "bWFwcGluZzEwMWNsdXN0ZXIxMDE"),
    ("record101cluster101", "cmVjb3JkMTAxY2x1c3RlcjEwMQ"),
    ("record101mirror101", "cmVjb3JkMTAxbWlycm9yMTAx"),
    ("record101filter101", "cmVjb3JkMTAxZmlsdGVyMTAx"),
    ("record101ranking101", "cmVjb3JkMTAxcmFua2luZzEwMQ"),
    ("candle101ranking101", "Y2FuZGxlMTAxcmFua2luZzEwMQ"),
    ("candle101encoding101", "Y2FuZGxlMTAxZW5jb2RpbmcxMDE"),
    ("candle101mapping101", "Y2FuZGxlMTAxbWFwcGluZzEwMQ"),
    ("candle101record101", "Y2FuZGxlMTAxcmVjb3JkMTAx"),
    ("thread101record101", "dGhyZWFkMTAxcmVjb3JkMTAx"),
    ("thread101candle101", "dGhyZWFkMTAxY2FuZGxlMTAx"),
    ("thread101thread101", "dGhyZWFkMTAxdGhyZWFkMTAx"),
    ("thread101kitten101", "dGhyZWFkMTAxa2l0dGVuMTAx"),
    (
        "round 101: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTAxOiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 101: agentuniverse is a framework for multi agents",
        "cm91bmQgMTAxOiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 101: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTAxOiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 101: the processor reads the record then stops",
        "cm91bmQgMTAxOiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 101: a worker pulls the next task from the queue",
        "cm91bmQgMTAxOiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 101: signals travel through the network layer",
        "cm91bmQgMTAxOiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 101: the gateway routes each request by policy",
        "cm91bmQgMTAxOiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 101: memory grows until the buffer is full",
        "cm91bmQgMTAxOiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 101: the cluster mirrors every packet twice",
        "cm91bmQgMTAxOiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 101: ranking uses tokens learned from the corpus",
        "cm91bmQgMTAxOiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 101: a long session ends when the candle dies",
        "cm91bmQgMTAxOiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 101: encode the prompt then map the result",
        "cm91bmQgMTAxOiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 101: the kernel wakes the worker at dawn",
        "cm91bmQgMTAxOiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 101: service latency drops after the patch",
        "cm91bmQgMTAxOiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 101: the library caches every vector it sees",
        "cm91bmQgMTAxOiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 101: agents argue then the debate resolves",
        "cm91bmQgMTAxOiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 101: the filter keeps only strong matches",
        "cm91bmQgMTAxOiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 101: the model answers with a short reply",
        "cm91bmQgMTAxOiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 101: the recorder stores the reasoning trace",
        "cm91bmQgMTAxOiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 101: the angel watches the processor run",
        "cm91bmQgMTAxOiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 101: angle of the vector decides the match",
        "cm91bmQgMTAxOiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 101: the candle burns twice as long at night",
        "cm91bmQgMTAxOiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 101: a mirror of the universe in one line",
        "cm91bmQgMTAxOiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 101: the queue drains before the storm", "cm91bmQgMTAxOiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
