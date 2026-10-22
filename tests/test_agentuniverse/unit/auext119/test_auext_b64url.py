"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten119kitten119", "a2l0dGVuMTE5a2l0dGVuMTE5"),
    ("kitten119sitting119", "a2l0dGVuMTE5c2l0dGluZzExOQ"),
    ("kitten119agent119", "a2l0dGVuMTE5YWdlbnQxMTk"),
    ("kitten119angle119", "a2l0dGVuMTE5YW5nbGUxMTk"),
    ("sitting119angle119", "c2l0dGluZzExOWFuZ2xlMTE5"),
    ("sitting119universe119", "c2l0dGluZzExOXVuaXZlcnNlMTE5"),
    ("sitting119memory119", "c2l0dGluZzExOW1lbW9yeTExOQ"),
    ("sitting119stream119", "c2l0dGluZzExOXN0cmVhbTExOQ"),
    ("agent119stream119", "YWdlbnQxMTlzdHJlYW0xMTk"),
    ("agent119context119", "YWdlbnQxMTljb250ZXh0MTE5"),
    ("agent119knowledge119", "YWdlbnQxMTlrbm93bGVkZ2UxMTk"),
    ("agent119vector119", "YWdlbnQxMTl2ZWN0b3IxMTk"),
    ("angle119vector119", "YW5nbGUxMTl2ZWN0b3IxMTk"),
    ("angle119processor119", "YW5nbGUxMTlwcm9jZXNzb3IxMTk"),
    ("angle119reasoning119", "YW5nbGUxMTlyZWFzb25pbmcxMTk"),
    ("angle119machine119", "YW5nbGUxMTltYWNoaW5lMTE5"),
    ("universe119machine119", "dW5pdmVyc2UxMTltYWNoaW5lMTE5"),
    ("universe119learning119", "dW5pdmVyc2UxMTlsZWFybmluZzExOQ"),
    ("universe119model119", "dW5pdmVyc2UxMTltb2RlbDExOQ"),
    ("universe119token119", "dW5pdmVyc2UxMTl0b2tlbjExOQ"),
    ("memory119token119", "bWVtb3J5MTE5dG9rZW4xMTk"),
    ("memory119prompt119", "bWVtb3J5MTE5cHJvbXB0MTE5"),
    ("memory119session119", "bWVtb3J5MTE5c2Vzc2lvbjExOQ"),
    ("memory119library119", "bWVtb3J5MTE5bGlicmFyeTExOQ"),
    ("stream119library119", "c3RyZWFtMTE5bGlicmFyeTExOQ"),
    ("stream119service119", "c3RyZWFtMTE5c2VydmljZTExOQ"),
    ("stream119gateway119", "c3RyZWFtMTE5Z2F0ZXdheTExOQ"),
    ("stream119storage119", "c3RyZWFtMTE5c3RvcmFnZTExOQ"),
    ("context119storage119", "Y29udGV4dDExOXN0b3JhZ2UxMTk"),
    ("context119network119", "Y29udGV4dDExOW5ldHdvcmsxMTk"),
    ("context119latency119", "Y29udGV4dDExOWxhdGVuY3kxMTk"),
    ("context119buffer119", "Y29udGV4dDExOWJ1ZmZlcjExOQ"),
    ("knowledge119buffer119", "a25vd2xlZGdlMTE5YnVmZmVyMTE5"),
    ("knowledge119queue119", "a25vd2xlZGdlMTE5cXVldWUxMTk"),
    ("knowledge119worker119", "a25vd2xlZGdlMTE5d29ya2VyMTE5"),
    ("knowledge119kernel119", "a25vd2xlZGdlMTE5a2VybmVsMTE5"),
    ("vector119kernel119", "dmVjdG9yMTE5a2VybmVsMTE5"),
    ("vector119signal119", "dmVjdG9yMTE5c2lnbmFsMTE5"),
    ("vector119packet119", "dmVjdG9yMTE5cGFja2V0MTE5"),
    ("vector119router119", "dmVjdG9yMTE5cm91dGVyMTE5"),
    ("processor119router119", "cHJvY2Vzc29yMTE5cm91dGVyMTE5"),
    ("processor119cluster119", "cHJvY2Vzc29yMTE5Y2x1c3RlcjExOQ"),
    ("processor119mirror119", "cHJvY2Vzc29yMTE5bWlycm9yMTE5"),
    ("processor119filter119", "cHJvY2Vzc29yMTE5ZmlsdGVyMTE5"),
    ("reasoning119filter119", "cmVhc29uaW5nMTE5ZmlsdGVyMTE5"),
    ("reasoning119ranking119", "cmVhc29uaW5nMTE5cmFua2luZzExOQ"),
    ("reasoning119encoding119", "cmVhc29uaW5nMTE5ZW5jb2RpbmcxMTk"),
    ("reasoning119mapping119", "cmVhc29uaW5nMTE5bWFwcGluZzExOQ"),
    ("machine119mapping119", "bWFjaGluZTExOW1hcHBpbmcxMTk"),
    ("machine119record119", "bWFjaGluZTExOXJlY29yZDExOQ"),
    ("machine119candle119", "bWFjaGluZTExOWNhbmRsZTExOQ"),
    ("machine119thread119", "bWFjaGluZTExOXRocmVhZDExOQ"),
    ("learning119thread119", "bGVhcm5pbmcxMTl0aHJlYWQxMTk"),
    ("learning119kitten119", "bGVhcm5pbmcxMTlraXR0ZW4xMTk"),
    ("learning119sitting119", "bGVhcm5pbmcxMTlzaXR0aW5nMTE5"),
    ("learning119agent119", "bGVhcm5pbmcxMTlhZ2VudDExOQ"),
    ("model119agent119", "bW9kZWwxMTlhZ2VudDExOQ"),
    ("model119angle119", "bW9kZWwxMTlhbmdsZTExOQ"),
    ("model119universe119", "bW9kZWwxMTl1bml2ZXJzZTExOQ"),
    ("model119memory119", "bW9kZWwxMTltZW1vcnkxMTk"),
    ("token119memory119", "dG9rZW4xMTltZW1vcnkxMTk"),
    ("token119stream119", "dG9rZW4xMTlzdHJlYW0xMTk"),
    ("token119context119", "dG9rZW4xMTljb250ZXh0MTE5"),
    ("token119knowledge119", "dG9rZW4xMTlrbm93bGVkZ2UxMTk"),
    ("prompt119knowledge119", "cHJvbXB0MTE5a25vd2xlZGdlMTE5"),
    ("prompt119vector119", "cHJvbXB0MTE5dmVjdG9yMTE5"),
    ("prompt119processor119", "cHJvbXB0MTE5cHJvY2Vzc29yMTE5"),
    ("prompt119reasoning119", "cHJvbXB0MTE5cmVhc29uaW5nMTE5"),
    ("session119reasoning119", "c2Vzc2lvbjExOXJlYXNvbmluZzExOQ"),
    ("session119machine119", "c2Vzc2lvbjExOW1hY2hpbmUxMTk"),
    ("session119learning119", "c2Vzc2lvbjExOWxlYXJuaW5nMTE5"),
    ("session119model119", "c2Vzc2lvbjExOW1vZGVsMTE5"),
    ("library119model119", "bGlicmFyeTExOW1vZGVsMTE5"),
    ("library119token119", "bGlicmFyeTExOXRva2VuMTE5"),
    ("library119prompt119", "bGlicmFyeTExOXByb21wdDExOQ"),
    ("library119session119", "bGlicmFyeTExOXNlc3Npb24xMTk"),
    ("service119session119", "c2VydmljZTExOXNlc3Npb24xMTk"),
    ("service119library119", "c2VydmljZTExOWxpYnJhcnkxMTk"),
    ("service119service119", "c2VydmljZTExOXNlcnZpY2UxMTk"),
    ("service119gateway119", "c2VydmljZTExOWdhdGV3YXkxMTk"),
    ("gateway119gateway119", "Z2F0ZXdheTExOWdhdGV3YXkxMTk"),
    ("gateway119storage119", "Z2F0ZXdheTExOXN0b3JhZ2UxMTk"),
    ("gateway119network119", "Z2F0ZXdheTExOW5ldHdvcmsxMTk"),
    ("gateway119latency119", "Z2F0ZXdheTExOWxhdGVuY3kxMTk"),
    ("storage119latency119", "c3RvcmFnZTExOWxhdGVuY3kxMTk"),
    ("storage119buffer119", "c3RvcmFnZTExOWJ1ZmZlcjExOQ"),
    ("storage119queue119", "c3RvcmFnZTExOXF1ZXVlMTE5"),
    ("storage119worker119", "c3RvcmFnZTExOXdvcmtlcjExOQ"),
    ("network119worker119", "bmV0d29yazExOXdvcmtlcjExOQ"),
    ("network119kernel119", "bmV0d29yazExOWtlcm5lbDExOQ"),
    ("network119signal119", "bmV0d29yazExOXNpZ25hbDExOQ"),
    ("network119packet119", "bmV0d29yazExOXBhY2tldDExOQ"),
    ("latency119packet119", "bGF0ZW5jeTExOXBhY2tldDExOQ"),
    ("latency119router119", "bGF0ZW5jeTExOXJvdXRlcjExOQ"),
    ("latency119cluster119", "bGF0ZW5jeTExOWNsdXN0ZXIxMTk"),
    ("latency119mirror119", "bGF0ZW5jeTExOW1pcnJvcjExOQ"),
    ("buffer119mirror119", "YnVmZmVyMTE5bWlycm9yMTE5"),
    ("buffer119filter119", "YnVmZmVyMTE5ZmlsdGVyMTE5"),
    ("buffer119ranking119", "YnVmZmVyMTE5cmFua2luZzExOQ"),
    ("buffer119encoding119", "YnVmZmVyMTE5ZW5jb2RpbmcxMTk"),
    ("queue119encoding119", "cXVldWUxMTllbmNvZGluZzExOQ"),
    ("queue119mapping119", "cXVldWUxMTltYXBwaW5nMTE5"),
    ("queue119record119", "cXVldWUxMTlyZWNvcmQxMTk"),
    ("queue119candle119", "cXVldWUxMTljYW5kbGUxMTk"),
    ("worker119candle119", "d29ya2VyMTE5Y2FuZGxlMTE5"),
    ("worker119thread119", "d29ya2VyMTE5dGhyZWFkMTE5"),
    ("worker119kitten119", "d29ya2VyMTE5a2l0dGVuMTE5"),
    ("worker119sitting119", "d29ya2VyMTE5c2l0dGluZzExOQ"),
    ("kernel119sitting119", "a2VybmVsMTE5c2l0dGluZzExOQ"),
    ("kernel119agent119", "a2VybmVsMTE5YWdlbnQxMTk"),
    ("kernel119angle119", "a2VybmVsMTE5YW5nbGUxMTk"),
    ("kernel119universe119", "a2VybmVsMTE5dW5pdmVyc2UxMTk"),
    ("signal119universe119", "c2lnbmFsMTE5dW5pdmVyc2UxMTk"),
    ("signal119memory119", "c2lnbmFsMTE5bWVtb3J5MTE5"),
    ("signal119stream119", "c2lnbmFsMTE5c3RyZWFtMTE5"),
    ("signal119context119", "c2lnbmFsMTE5Y29udGV4dDExOQ"),
    ("packet119context119", "cGFja2V0MTE5Y29udGV4dDExOQ"),
    ("packet119knowledge119", "cGFja2V0MTE5a25vd2xlZGdlMTE5"),
    ("packet119vector119", "cGFja2V0MTE5dmVjdG9yMTE5"),
    ("packet119processor119", "cGFja2V0MTE5cHJvY2Vzc29yMTE5"),
    ("router119processor119", "cm91dGVyMTE5cHJvY2Vzc29yMTE5"),
    ("router119reasoning119", "cm91dGVyMTE5cmVhc29uaW5nMTE5"),
    ("router119machine119", "cm91dGVyMTE5bWFjaGluZTExOQ"),
    ("router119learning119", "cm91dGVyMTE5bGVhcm5pbmcxMTk"),
    ("cluster119learning119", "Y2x1c3RlcjExOWxlYXJuaW5nMTE5"),
    ("cluster119model119", "Y2x1c3RlcjExOW1vZGVsMTE5"),
    ("cluster119token119", "Y2x1c3RlcjExOXRva2VuMTE5"),
    ("cluster119prompt119", "Y2x1c3RlcjExOXByb21wdDExOQ"),
    ("mirror119prompt119", "bWlycm9yMTE5cHJvbXB0MTE5"),
    ("mirror119session119", "bWlycm9yMTE5c2Vzc2lvbjExOQ"),
    ("mirror119library119", "bWlycm9yMTE5bGlicmFyeTExOQ"),
    ("mirror119service119", "bWlycm9yMTE5c2VydmljZTExOQ"),
    ("filter119service119", "ZmlsdGVyMTE5c2VydmljZTExOQ"),
    ("filter119gateway119", "ZmlsdGVyMTE5Z2F0ZXdheTExOQ"),
    ("filter119storage119", "ZmlsdGVyMTE5c3RvcmFnZTExOQ"),
    ("filter119network119", "ZmlsdGVyMTE5bmV0d29yazExOQ"),
    ("ranking119network119", "cmFua2luZzExOW5ldHdvcmsxMTk"),
    ("ranking119latency119", "cmFua2luZzExOWxhdGVuY3kxMTk"),
    ("ranking119buffer119", "cmFua2luZzExOWJ1ZmZlcjExOQ"),
    ("ranking119queue119", "cmFua2luZzExOXF1ZXVlMTE5"),
    ("encoding119queue119", "ZW5jb2RpbmcxMTlxdWV1ZTExOQ"),
    ("encoding119worker119", "ZW5jb2RpbmcxMTl3b3JrZXIxMTk"),
    ("encoding119kernel119", "ZW5jb2RpbmcxMTlrZXJuZWwxMTk"),
    ("encoding119signal119", "ZW5jb2RpbmcxMTlzaWduYWwxMTk"),
    ("mapping119signal119", "bWFwcGluZzExOXNpZ25hbDExOQ"),
    ("mapping119packet119", "bWFwcGluZzExOXBhY2tldDExOQ"),
    ("mapping119router119", "bWFwcGluZzExOXJvdXRlcjExOQ"),
    ("mapping119cluster119", "bWFwcGluZzExOWNsdXN0ZXIxMTk"),
    ("record119cluster119", "cmVjb3JkMTE5Y2x1c3RlcjExOQ"),
    ("record119mirror119", "cmVjb3JkMTE5bWlycm9yMTE5"),
    ("record119filter119", "cmVjb3JkMTE5ZmlsdGVyMTE5"),
    ("record119ranking119", "cmVjb3JkMTE5cmFua2luZzExOQ"),
    ("candle119ranking119", "Y2FuZGxlMTE5cmFua2luZzExOQ"),
    ("candle119encoding119", "Y2FuZGxlMTE5ZW5jb2RpbmcxMTk"),
    ("candle119mapping119", "Y2FuZGxlMTE5bWFwcGluZzExOQ"),
    ("candle119record119", "Y2FuZGxlMTE5cmVjb3JkMTE5"),
    ("thread119record119", "dGhyZWFkMTE5cmVjb3JkMTE5"),
    ("thread119candle119", "dGhyZWFkMTE5Y2FuZGxlMTE5"),
    ("thread119thread119", "dGhyZWFkMTE5dGhyZWFkMTE5"),
    ("thread119kitten119", "dGhyZWFkMTE5a2l0dGVuMTE5"),
    (
        "round 119: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTE5OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 119: agentuniverse is a framework for multi agents",
        "cm91bmQgMTE5OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 119: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTE5OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 119: the processor reads the record then stops",
        "cm91bmQgMTE5OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 119: a worker pulls the next task from the queue",
        "cm91bmQgMTE5OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 119: signals travel through the network layer",
        "cm91bmQgMTE5OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 119: the gateway routes each request by policy",
        "cm91bmQgMTE5OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 119: memory grows until the buffer is full",
        "cm91bmQgMTE5OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 119: the cluster mirrors every packet twice",
        "cm91bmQgMTE5OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 119: ranking uses tokens learned from the corpus",
        "cm91bmQgMTE5OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 119: a long session ends when the candle dies",
        "cm91bmQgMTE5OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 119: encode the prompt then map the result",
        "cm91bmQgMTE5OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 119: the kernel wakes the worker at dawn",
        "cm91bmQgMTE5OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 119: service latency drops after the patch",
        "cm91bmQgMTE5OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 119: the library caches every vector it sees",
        "cm91bmQgMTE5OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 119: agents argue then the debate resolves",
        "cm91bmQgMTE5OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 119: the filter keeps only strong matches",
        "cm91bmQgMTE5OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 119: the model answers with a short reply",
        "cm91bmQgMTE5OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 119: the recorder stores the reasoning trace",
        "cm91bmQgMTE5OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 119: the angel watches the processor run",
        "cm91bmQgMTE5OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 119: angle of the vector decides the match",
        "cm91bmQgMTE5OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 119: the candle burns twice as long at night",
        "cm91bmQgMTE5OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 119: a mirror of the universe in one line",
        "cm91bmQgMTE5OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 119: the queue drains before the storm", "cm91bmQgMTE5OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
