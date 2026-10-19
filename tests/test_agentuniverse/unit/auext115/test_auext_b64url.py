"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten115kitten115", "a2l0dGVuMTE1a2l0dGVuMTE1"),
    ("kitten115sitting115", "a2l0dGVuMTE1c2l0dGluZzExNQ"),
    ("kitten115agent115", "a2l0dGVuMTE1YWdlbnQxMTU"),
    ("kitten115angle115", "a2l0dGVuMTE1YW5nbGUxMTU"),
    ("sitting115angle115", "c2l0dGluZzExNWFuZ2xlMTE1"),
    ("sitting115universe115", "c2l0dGluZzExNXVuaXZlcnNlMTE1"),
    ("sitting115memory115", "c2l0dGluZzExNW1lbW9yeTExNQ"),
    ("sitting115stream115", "c2l0dGluZzExNXN0cmVhbTExNQ"),
    ("agent115stream115", "YWdlbnQxMTVzdHJlYW0xMTU"),
    ("agent115context115", "YWdlbnQxMTVjb250ZXh0MTE1"),
    ("agent115knowledge115", "YWdlbnQxMTVrbm93bGVkZ2UxMTU"),
    ("agent115vector115", "YWdlbnQxMTV2ZWN0b3IxMTU"),
    ("angle115vector115", "YW5nbGUxMTV2ZWN0b3IxMTU"),
    ("angle115processor115", "YW5nbGUxMTVwcm9jZXNzb3IxMTU"),
    ("angle115reasoning115", "YW5nbGUxMTVyZWFzb25pbmcxMTU"),
    ("angle115machine115", "YW5nbGUxMTVtYWNoaW5lMTE1"),
    ("universe115machine115", "dW5pdmVyc2UxMTVtYWNoaW5lMTE1"),
    ("universe115learning115", "dW5pdmVyc2UxMTVsZWFybmluZzExNQ"),
    ("universe115model115", "dW5pdmVyc2UxMTVtb2RlbDExNQ"),
    ("universe115token115", "dW5pdmVyc2UxMTV0b2tlbjExNQ"),
    ("memory115token115", "bWVtb3J5MTE1dG9rZW4xMTU"),
    ("memory115prompt115", "bWVtb3J5MTE1cHJvbXB0MTE1"),
    ("memory115session115", "bWVtb3J5MTE1c2Vzc2lvbjExNQ"),
    ("memory115library115", "bWVtb3J5MTE1bGlicmFyeTExNQ"),
    ("stream115library115", "c3RyZWFtMTE1bGlicmFyeTExNQ"),
    ("stream115service115", "c3RyZWFtMTE1c2VydmljZTExNQ"),
    ("stream115gateway115", "c3RyZWFtMTE1Z2F0ZXdheTExNQ"),
    ("stream115storage115", "c3RyZWFtMTE1c3RvcmFnZTExNQ"),
    ("context115storage115", "Y29udGV4dDExNXN0b3JhZ2UxMTU"),
    ("context115network115", "Y29udGV4dDExNW5ldHdvcmsxMTU"),
    ("context115latency115", "Y29udGV4dDExNWxhdGVuY3kxMTU"),
    ("context115buffer115", "Y29udGV4dDExNWJ1ZmZlcjExNQ"),
    ("knowledge115buffer115", "a25vd2xlZGdlMTE1YnVmZmVyMTE1"),
    ("knowledge115queue115", "a25vd2xlZGdlMTE1cXVldWUxMTU"),
    ("knowledge115worker115", "a25vd2xlZGdlMTE1d29ya2VyMTE1"),
    ("knowledge115kernel115", "a25vd2xlZGdlMTE1a2VybmVsMTE1"),
    ("vector115kernel115", "dmVjdG9yMTE1a2VybmVsMTE1"),
    ("vector115signal115", "dmVjdG9yMTE1c2lnbmFsMTE1"),
    ("vector115packet115", "dmVjdG9yMTE1cGFja2V0MTE1"),
    ("vector115router115", "dmVjdG9yMTE1cm91dGVyMTE1"),
    ("processor115router115", "cHJvY2Vzc29yMTE1cm91dGVyMTE1"),
    ("processor115cluster115", "cHJvY2Vzc29yMTE1Y2x1c3RlcjExNQ"),
    ("processor115mirror115", "cHJvY2Vzc29yMTE1bWlycm9yMTE1"),
    ("processor115filter115", "cHJvY2Vzc29yMTE1ZmlsdGVyMTE1"),
    ("reasoning115filter115", "cmVhc29uaW5nMTE1ZmlsdGVyMTE1"),
    ("reasoning115ranking115", "cmVhc29uaW5nMTE1cmFua2luZzExNQ"),
    ("reasoning115encoding115", "cmVhc29uaW5nMTE1ZW5jb2RpbmcxMTU"),
    ("reasoning115mapping115", "cmVhc29uaW5nMTE1bWFwcGluZzExNQ"),
    ("machine115mapping115", "bWFjaGluZTExNW1hcHBpbmcxMTU"),
    ("machine115record115", "bWFjaGluZTExNXJlY29yZDExNQ"),
    ("machine115candle115", "bWFjaGluZTExNWNhbmRsZTExNQ"),
    ("machine115thread115", "bWFjaGluZTExNXRocmVhZDExNQ"),
    ("learning115thread115", "bGVhcm5pbmcxMTV0aHJlYWQxMTU"),
    ("learning115kitten115", "bGVhcm5pbmcxMTVraXR0ZW4xMTU"),
    ("learning115sitting115", "bGVhcm5pbmcxMTVzaXR0aW5nMTE1"),
    ("learning115agent115", "bGVhcm5pbmcxMTVhZ2VudDExNQ"),
    ("model115agent115", "bW9kZWwxMTVhZ2VudDExNQ"),
    ("model115angle115", "bW9kZWwxMTVhbmdsZTExNQ"),
    ("model115universe115", "bW9kZWwxMTV1bml2ZXJzZTExNQ"),
    ("model115memory115", "bW9kZWwxMTVtZW1vcnkxMTU"),
    ("token115memory115", "dG9rZW4xMTVtZW1vcnkxMTU"),
    ("token115stream115", "dG9rZW4xMTVzdHJlYW0xMTU"),
    ("token115context115", "dG9rZW4xMTVjb250ZXh0MTE1"),
    ("token115knowledge115", "dG9rZW4xMTVrbm93bGVkZ2UxMTU"),
    ("prompt115knowledge115", "cHJvbXB0MTE1a25vd2xlZGdlMTE1"),
    ("prompt115vector115", "cHJvbXB0MTE1dmVjdG9yMTE1"),
    ("prompt115processor115", "cHJvbXB0MTE1cHJvY2Vzc29yMTE1"),
    ("prompt115reasoning115", "cHJvbXB0MTE1cmVhc29uaW5nMTE1"),
    ("session115reasoning115", "c2Vzc2lvbjExNXJlYXNvbmluZzExNQ"),
    ("session115machine115", "c2Vzc2lvbjExNW1hY2hpbmUxMTU"),
    ("session115learning115", "c2Vzc2lvbjExNWxlYXJuaW5nMTE1"),
    ("session115model115", "c2Vzc2lvbjExNW1vZGVsMTE1"),
    ("library115model115", "bGlicmFyeTExNW1vZGVsMTE1"),
    ("library115token115", "bGlicmFyeTExNXRva2VuMTE1"),
    ("library115prompt115", "bGlicmFyeTExNXByb21wdDExNQ"),
    ("library115session115", "bGlicmFyeTExNXNlc3Npb24xMTU"),
    ("service115session115", "c2VydmljZTExNXNlc3Npb24xMTU"),
    ("service115library115", "c2VydmljZTExNWxpYnJhcnkxMTU"),
    ("service115service115", "c2VydmljZTExNXNlcnZpY2UxMTU"),
    ("service115gateway115", "c2VydmljZTExNWdhdGV3YXkxMTU"),
    ("gateway115gateway115", "Z2F0ZXdheTExNWdhdGV3YXkxMTU"),
    ("gateway115storage115", "Z2F0ZXdheTExNXN0b3JhZ2UxMTU"),
    ("gateway115network115", "Z2F0ZXdheTExNW5ldHdvcmsxMTU"),
    ("gateway115latency115", "Z2F0ZXdheTExNWxhdGVuY3kxMTU"),
    ("storage115latency115", "c3RvcmFnZTExNWxhdGVuY3kxMTU"),
    ("storage115buffer115", "c3RvcmFnZTExNWJ1ZmZlcjExNQ"),
    ("storage115queue115", "c3RvcmFnZTExNXF1ZXVlMTE1"),
    ("storage115worker115", "c3RvcmFnZTExNXdvcmtlcjExNQ"),
    ("network115worker115", "bmV0d29yazExNXdvcmtlcjExNQ"),
    ("network115kernel115", "bmV0d29yazExNWtlcm5lbDExNQ"),
    ("network115signal115", "bmV0d29yazExNXNpZ25hbDExNQ"),
    ("network115packet115", "bmV0d29yazExNXBhY2tldDExNQ"),
    ("latency115packet115", "bGF0ZW5jeTExNXBhY2tldDExNQ"),
    ("latency115router115", "bGF0ZW5jeTExNXJvdXRlcjExNQ"),
    ("latency115cluster115", "bGF0ZW5jeTExNWNsdXN0ZXIxMTU"),
    ("latency115mirror115", "bGF0ZW5jeTExNW1pcnJvcjExNQ"),
    ("buffer115mirror115", "YnVmZmVyMTE1bWlycm9yMTE1"),
    ("buffer115filter115", "YnVmZmVyMTE1ZmlsdGVyMTE1"),
    ("buffer115ranking115", "YnVmZmVyMTE1cmFua2luZzExNQ"),
    ("buffer115encoding115", "YnVmZmVyMTE1ZW5jb2RpbmcxMTU"),
    ("queue115encoding115", "cXVldWUxMTVlbmNvZGluZzExNQ"),
    ("queue115mapping115", "cXVldWUxMTVtYXBwaW5nMTE1"),
    ("queue115record115", "cXVldWUxMTVyZWNvcmQxMTU"),
    ("queue115candle115", "cXVldWUxMTVjYW5kbGUxMTU"),
    ("worker115candle115", "d29ya2VyMTE1Y2FuZGxlMTE1"),
    ("worker115thread115", "d29ya2VyMTE1dGhyZWFkMTE1"),
    ("worker115kitten115", "d29ya2VyMTE1a2l0dGVuMTE1"),
    ("worker115sitting115", "d29ya2VyMTE1c2l0dGluZzExNQ"),
    ("kernel115sitting115", "a2VybmVsMTE1c2l0dGluZzExNQ"),
    ("kernel115agent115", "a2VybmVsMTE1YWdlbnQxMTU"),
    ("kernel115angle115", "a2VybmVsMTE1YW5nbGUxMTU"),
    ("kernel115universe115", "a2VybmVsMTE1dW5pdmVyc2UxMTU"),
    ("signal115universe115", "c2lnbmFsMTE1dW5pdmVyc2UxMTU"),
    ("signal115memory115", "c2lnbmFsMTE1bWVtb3J5MTE1"),
    ("signal115stream115", "c2lnbmFsMTE1c3RyZWFtMTE1"),
    ("signal115context115", "c2lnbmFsMTE1Y29udGV4dDExNQ"),
    ("packet115context115", "cGFja2V0MTE1Y29udGV4dDExNQ"),
    ("packet115knowledge115", "cGFja2V0MTE1a25vd2xlZGdlMTE1"),
    ("packet115vector115", "cGFja2V0MTE1dmVjdG9yMTE1"),
    ("packet115processor115", "cGFja2V0MTE1cHJvY2Vzc29yMTE1"),
    ("router115processor115", "cm91dGVyMTE1cHJvY2Vzc29yMTE1"),
    ("router115reasoning115", "cm91dGVyMTE1cmVhc29uaW5nMTE1"),
    ("router115machine115", "cm91dGVyMTE1bWFjaGluZTExNQ"),
    ("router115learning115", "cm91dGVyMTE1bGVhcm5pbmcxMTU"),
    ("cluster115learning115", "Y2x1c3RlcjExNWxlYXJuaW5nMTE1"),
    ("cluster115model115", "Y2x1c3RlcjExNW1vZGVsMTE1"),
    ("cluster115token115", "Y2x1c3RlcjExNXRva2VuMTE1"),
    ("cluster115prompt115", "Y2x1c3RlcjExNXByb21wdDExNQ"),
    ("mirror115prompt115", "bWlycm9yMTE1cHJvbXB0MTE1"),
    ("mirror115session115", "bWlycm9yMTE1c2Vzc2lvbjExNQ"),
    ("mirror115library115", "bWlycm9yMTE1bGlicmFyeTExNQ"),
    ("mirror115service115", "bWlycm9yMTE1c2VydmljZTExNQ"),
    ("filter115service115", "ZmlsdGVyMTE1c2VydmljZTExNQ"),
    ("filter115gateway115", "ZmlsdGVyMTE1Z2F0ZXdheTExNQ"),
    ("filter115storage115", "ZmlsdGVyMTE1c3RvcmFnZTExNQ"),
    ("filter115network115", "ZmlsdGVyMTE1bmV0d29yazExNQ"),
    ("ranking115network115", "cmFua2luZzExNW5ldHdvcmsxMTU"),
    ("ranking115latency115", "cmFua2luZzExNWxhdGVuY3kxMTU"),
    ("ranking115buffer115", "cmFua2luZzExNWJ1ZmZlcjExNQ"),
    ("ranking115queue115", "cmFua2luZzExNXF1ZXVlMTE1"),
    ("encoding115queue115", "ZW5jb2RpbmcxMTVxdWV1ZTExNQ"),
    ("encoding115worker115", "ZW5jb2RpbmcxMTV3b3JrZXIxMTU"),
    ("encoding115kernel115", "ZW5jb2RpbmcxMTVrZXJuZWwxMTU"),
    ("encoding115signal115", "ZW5jb2RpbmcxMTVzaWduYWwxMTU"),
    ("mapping115signal115", "bWFwcGluZzExNXNpZ25hbDExNQ"),
    ("mapping115packet115", "bWFwcGluZzExNXBhY2tldDExNQ"),
    ("mapping115router115", "bWFwcGluZzExNXJvdXRlcjExNQ"),
    ("mapping115cluster115", "bWFwcGluZzExNWNsdXN0ZXIxMTU"),
    ("record115cluster115", "cmVjb3JkMTE1Y2x1c3RlcjExNQ"),
    ("record115mirror115", "cmVjb3JkMTE1bWlycm9yMTE1"),
    ("record115filter115", "cmVjb3JkMTE1ZmlsdGVyMTE1"),
    ("record115ranking115", "cmVjb3JkMTE1cmFua2luZzExNQ"),
    ("candle115ranking115", "Y2FuZGxlMTE1cmFua2luZzExNQ"),
    ("candle115encoding115", "Y2FuZGxlMTE1ZW5jb2RpbmcxMTU"),
    ("candle115mapping115", "Y2FuZGxlMTE1bWFwcGluZzExNQ"),
    ("candle115record115", "Y2FuZGxlMTE1cmVjb3JkMTE1"),
    ("thread115record115", "dGhyZWFkMTE1cmVjb3JkMTE1"),
    ("thread115candle115", "dGhyZWFkMTE1Y2FuZGxlMTE1"),
    ("thread115thread115", "dGhyZWFkMTE1dGhyZWFkMTE1"),
    ("thread115kitten115", "dGhyZWFkMTE1a2l0dGVuMTE1"),
    (
        "round 115: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTE1OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 115: agentuniverse is a framework for multi agents",
        "cm91bmQgMTE1OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 115: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTE1OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 115: the processor reads the record then stops",
        "cm91bmQgMTE1OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 115: a worker pulls the next task from the queue",
        "cm91bmQgMTE1OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 115: signals travel through the network layer",
        "cm91bmQgMTE1OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 115: the gateway routes each request by policy",
        "cm91bmQgMTE1OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 115: memory grows until the buffer is full",
        "cm91bmQgMTE1OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 115: the cluster mirrors every packet twice",
        "cm91bmQgMTE1OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 115: ranking uses tokens learned from the corpus",
        "cm91bmQgMTE1OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 115: a long session ends when the candle dies",
        "cm91bmQgMTE1OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 115: encode the prompt then map the result",
        "cm91bmQgMTE1OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 115: the kernel wakes the worker at dawn",
        "cm91bmQgMTE1OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 115: service latency drops after the patch",
        "cm91bmQgMTE1OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 115: the library caches every vector it sees",
        "cm91bmQgMTE1OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 115: agents argue then the debate resolves",
        "cm91bmQgMTE1OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 115: the filter keeps only strong matches",
        "cm91bmQgMTE1OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 115: the model answers with a short reply",
        "cm91bmQgMTE1OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 115: the recorder stores the reasoning trace",
        "cm91bmQgMTE1OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 115: the angel watches the processor run",
        "cm91bmQgMTE1OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 115: angle of the vector decides the match",
        "cm91bmQgMTE1OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 115: the candle burns twice as long at night",
        "cm91bmQgMTE1OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 115: a mirror of the universe in one line",
        "cm91bmQgMTE1OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 115: the queue drains before the storm", "cm91bmQgMTE1OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
