"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten117kitten117", "a2l0dGVuMTE3a2l0dGVuMTE3"),
    ("kitten117sitting117", "a2l0dGVuMTE3c2l0dGluZzExNw"),
    ("kitten117agent117", "a2l0dGVuMTE3YWdlbnQxMTc"),
    ("kitten117angle117", "a2l0dGVuMTE3YW5nbGUxMTc"),
    ("sitting117angle117", "c2l0dGluZzExN2FuZ2xlMTE3"),
    ("sitting117universe117", "c2l0dGluZzExN3VuaXZlcnNlMTE3"),
    ("sitting117memory117", "c2l0dGluZzExN21lbW9yeTExNw"),
    ("sitting117stream117", "c2l0dGluZzExN3N0cmVhbTExNw"),
    ("agent117stream117", "YWdlbnQxMTdzdHJlYW0xMTc"),
    ("agent117context117", "YWdlbnQxMTdjb250ZXh0MTE3"),
    ("agent117knowledge117", "YWdlbnQxMTdrbm93bGVkZ2UxMTc"),
    ("agent117vector117", "YWdlbnQxMTd2ZWN0b3IxMTc"),
    ("angle117vector117", "YW5nbGUxMTd2ZWN0b3IxMTc"),
    ("angle117processor117", "YW5nbGUxMTdwcm9jZXNzb3IxMTc"),
    ("angle117reasoning117", "YW5nbGUxMTdyZWFzb25pbmcxMTc"),
    ("angle117machine117", "YW5nbGUxMTdtYWNoaW5lMTE3"),
    ("universe117machine117", "dW5pdmVyc2UxMTdtYWNoaW5lMTE3"),
    ("universe117learning117", "dW5pdmVyc2UxMTdsZWFybmluZzExNw"),
    ("universe117model117", "dW5pdmVyc2UxMTdtb2RlbDExNw"),
    ("universe117token117", "dW5pdmVyc2UxMTd0b2tlbjExNw"),
    ("memory117token117", "bWVtb3J5MTE3dG9rZW4xMTc"),
    ("memory117prompt117", "bWVtb3J5MTE3cHJvbXB0MTE3"),
    ("memory117session117", "bWVtb3J5MTE3c2Vzc2lvbjExNw"),
    ("memory117library117", "bWVtb3J5MTE3bGlicmFyeTExNw"),
    ("stream117library117", "c3RyZWFtMTE3bGlicmFyeTExNw"),
    ("stream117service117", "c3RyZWFtMTE3c2VydmljZTExNw"),
    ("stream117gateway117", "c3RyZWFtMTE3Z2F0ZXdheTExNw"),
    ("stream117storage117", "c3RyZWFtMTE3c3RvcmFnZTExNw"),
    ("context117storage117", "Y29udGV4dDExN3N0b3JhZ2UxMTc"),
    ("context117network117", "Y29udGV4dDExN25ldHdvcmsxMTc"),
    ("context117latency117", "Y29udGV4dDExN2xhdGVuY3kxMTc"),
    ("context117buffer117", "Y29udGV4dDExN2J1ZmZlcjExNw"),
    ("knowledge117buffer117", "a25vd2xlZGdlMTE3YnVmZmVyMTE3"),
    ("knowledge117queue117", "a25vd2xlZGdlMTE3cXVldWUxMTc"),
    ("knowledge117worker117", "a25vd2xlZGdlMTE3d29ya2VyMTE3"),
    ("knowledge117kernel117", "a25vd2xlZGdlMTE3a2VybmVsMTE3"),
    ("vector117kernel117", "dmVjdG9yMTE3a2VybmVsMTE3"),
    ("vector117signal117", "dmVjdG9yMTE3c2lnbmFsMTE3"),
    ("vector117packet117", "dmVjdG9yMTE3cGFja2V0MTE3"),
    ("vector117router117", "dmVjdG9yMTE3cm91dGVyMTE3"),
    ("processor117router117", "cHJvY2Vzc29yMTE3cm91dGVyMTE3"),
    ("processor117cluster117", "cHJvY2Vzc29yMTE3Y2x1c3RlcjExNw"),
    ("processor117mirror117", "cHJvY2Vzc29yMTE3bWlycm9yMTE3"),
    ("processor117filter117", "cHJvY2Vzc29yMTE3ZmlsdGVyMTE3"),
    ("reasoning117filter117", "cmVhc29uaW5nMTE3ZmlsdGVyMTE3"),
    ("reasoning117ranking117", "cmVhc29uaW5nMTE3cmFua2luZzExNw"),
    ("reasoning117encoding117", "cmVhc29uaW5nMTE3ZW5jb2RpbmcxMTc"),
    ("reasoning117mapping117", "cmVhc29uaW5nMTE3bWFwcGluZzExNw"),
    ("machine117mapping117", "bWFjaGluZTExN21hcHBpbmcxMTc"),
    ("machine117record117", "bWFjaGluZTExN3JlY29yZDExNw"),
    ("machine117candle117", "bWFjaGluZTExN2NhbmRsZTExNw"),
    ("machine117thread117", "bWFjaGluZTExN3RocmVhZDExNw"),
    ("learning117thread117", "bGVhcm5pbmcxMTd0aHJlYWQxMTc"),
    ("learning117kitten117", "bGVhcm5pbmcxMTdraXR0ZW4xMTc"),
    ("learning117sitting117", "bGVhcm5pbmcxMTdzaXR0aW5nMTE3"),
    ("learning117agent117", "bGVhcm5pbmcxMTdhZ2VudDExNw"),
    ("model117agent117", "bW9kZWwxMTdhZ2VudDExNw"),
    ("model117angle117", "bW9kZWwxMTdhbmdsZTExNw"),
    ("model117universe117", "bW9kZWwxMTd1bml2ZXJzZTExNw"),
    ("model117memory117", "bW9kZWwxMTdtZW1vcnkxMTc"),
    ("token117memory117", "dG9rZW4xMTdtZW1vcnkxMTc"),
    ("token117stream117", "dG9rZW4xMTdzdHJlYW0xMTc"),
    ("token117context117", "dG9rZW4xMTdjb250ZXh0MTE3"),
    ("token117knowledge117", "dG9rZW4xMTdrbm93bGVkZ2UxMTc"),
    ("prompt117knowledge117", "cHJvbXB0MTE3a25vd2xlZGdlMTE3"),
    ("prompt117vector117", "cHJvbXB0MTE3dmVjdG9yMTE3"),
    ("prompt117processor117", "cHJvbXB0MTE3cHJvY2Vzc29yMTE3"),
    ("prompt117reasoning117", "cHJvbXB0MTE3cmVhc29uaW5nMTE3"),
    ("session117reasoning117", "c2Vzc2lvbjExN3JlYXNvbmluZzExNw"),
    ("session117machine117", "c2Vzc2lvbjExN21hY2hpbmUxMTc"),
    ("session117learning117", "c2Vzc2lvbjExN2xlYXJuaW5nMTE3"),
    ("session117model117", "c2Vzc2lvbjExN21vZGVsMTE3"),
    ("library117model117", "bGlicmFyeTExN21vZGVsMTE3"),
    ("library117token117", "bGlicmFyeTExN3Rva2VuMTE3"),
    ("library117prompt117", "bGlicmFyeTExN3Byb21wdDExNw"),
    ("library117session117", "bGlicmFyeTExN3Nlc3Npb24xMTc"),
    ("service117session117", "c2VydmljZTExN3Nlc3Npb24xMTc"),
    ("service117library117", "c2VydmljZTExN2xpYnJhcnkxMTc"),
    ("service117service117", "c2VydmljZTExN3NlcnZpY2UxMTc"),
    ("service117gateway117", "c2VydmljZTExN2dhdGV3YXkxMTc"),
    ("gateway117gateway117", "Z2F0ZXdheTExN2dhdGV3YXkxMTc"),
    ("gateway117storage117", "Z2F0ZXdheTExN3N0b3JhZ2UxMTc"),
    ("gateway117network117", "Z2F0ZXdheTExN25ldHdvcmsxMTc"),
    ("gateway117latency117", "Z2F0ZXdheTExN2xhdGVuY3kxMTc"),
    ("storage117latency117", "c3RvcmFnZTExN2xhdGVuY3kxMTc"),
    ("storage117buffer117", "c3RvcmFnZTExN2J1ZmZlcjExNw"),
    ("storage117queue117", "c3RvcmFnZTExN3F1ZXVlMTE3"),
    ("storage117worker117", "c3RvcmFnZTExN3dvcmtlcjExNw"),
    ("network117worker117", "bmV0d29yazExN3dvcmtlcjExNw"),
    ("network117kernel117", "bmV0d29yazExN2tlcm5lbDExNw"),
    ("network117signal117", "bmV0d29yazExN3NpZ25hbDExNw"),
    ("network117packet117", "bmV0d29yazExN3BhY2tldDExNw"),
    ("latency117packet117", "bGF0ZW5jeTExN3BhY2tldDExNw"),
    ("latency117router117", "bGF0ZW5jeTExN3JvdXRlcjExNw"),
    ("latency117cluster117", "bGF0ZW5jeTExN2NsdXN0ZXIxMTc"),
    ("latency117mirror117", "bGF0ZW5jeTExN21pcnJvcjExNw"),
    ("buffer117mirror117", "YnVmZmVyMTE3bWlycm9yMTE3"),
    ("buffer117filter117", "YnVmZmVyMTE3ZmlsdGVyMTE3"),
    ("buffer117ranking117", "YnVmZmVyMTE3cmFua2luZzExNw"),
    ("buffer117encoding117", "YnVmZmVyMTE3ZW5jb2RpbmcxMTc"),
    ("queue117encoding117", "cXVldWUxMTdlbmNvZGluZzExNw"),
    ("queue117mapping117", "cXVldWUxMTdtYXBwaW5nMTE3"),
    ("queue117record117", "cXVldWUxMTdyZWNvcmQxMTc"),
    ("queue117candle117", "cXVldWUxMTdjYW5kbGUxMTc"),
    ("worker117candle117", "d29ya2VyMTE3Y2FuZGxlMTE3"),
    ("worker117thread117", "d29ya2VyMTE3dGhyZWFkMTE3"),
    ("worker117kitten117", "d29ya2VyMTE3a2l0dGVuMTE3"),
    ("worker117sitting117", "d29ya2VyMTE3c2l0dGluZzExNw"),
    ("kernel117sitting117", "a2VybmVsMTE3c2l0dGluZzExNw"),
    ("kernel117agent117", "a2VybmVsMTE3YWdlbnQxMTc"),
    ("kernel117angle117", "a2VybmVsMTE3YW5nbGUxMTc"),
    ("kernel117universe117", "a2VybmVsMTE3dW5pdmVyc2UxMTc"),
    ("signal117universe117", "c2lnbmFsMTE3dW5pdmVyc2UxMTc"),
    ("signal117memory117", "c2lnbmFsMTE3bWVtb3J5MTE3"),
    ("signal117stream117", "c2lnbmFsMTE3c3RyZWFtMTE3"),
    ("signal117context117", "c2lnbmFsMTE3Y29udGV4dDExNw"),
    ("packet117context117", "cGFja2V0MTE3Y29udGV4dDExNw"),
    ("packet117knowledge117", "cGFja2V0MTE3a25vd2xlZGdlMTE3"),
    ("packet117vector117", "cGFja2V0MTE3dmVjdG9yMTE3"),
    ("packet117processor117", "cGFja2V0MTE3cHJvY2Vzc29yMTE3"),
    ("router117processor117", "cm91dGVyMTE3cHJvY2Vzc29yMTE3"),
    ("router117reasoning117", "cm91dGVyMTE3cmVhc29uaW5nMTE3"),
    ("router117machine117", "cm91dGVyMTE3bWFjaGluZTExNw"),
    ("router117learning117", "cm91dGVyMTE3bGVhcm5pbmcxMTc"),
    ("cluster117learning117", "Y2x1c3RlcjExN2xlYXJuaW5nMTE3"),
    ("cluster117model117", "Y2x1c3RlcjExN21vZGVsMTE3"),
    ("cluster117token117", "Y2x1c3RlcjExN3Rva2VuMTE3"),
    ("cluster117prompt117", "Y2x1c3RlcjExN3Byb21wdDExNw"),
    ("mirror117prompt117", "bWlycm9yMTE3cHJvbXB0MTE3"),
    ("mirror117session117", "bWlycm9yMTE3c2Vzc2lvbjExNw"),
    ("mirror117library117", "bWlycm9yMTE3bGlicmFyeTExNw"),
    ("mirror117service117", "bWlycm9yMTE3c2VydmljZTExNw"),
    ("filter117service117", "ZmlsdGVyMTE3c2VydmljZTExNw"),
    ("filter117gateway117", "ZmlsdGVyMTE3Z2F0ZXdheTExNw"),
    ("filter117storage117", "ZmlsdGVyMTE3c3RvcmFnZTExNw"),
    ("filter117network117", "ZmlsdGVyMTE3bmV0d29yazExNw"),
    ("ranking117network117", "cmFua2luZzExN25ldHdvcmsxMTc"),
    ("ranking117latency117", "cmFua2luZzExN2xhdGVuY3kxMTc"),
    ("ranking117buffer117", "cmFua2luZzExN2J1ZmZlcjExNw"),
    ("ranking117queue117", "cmFua2luZzExN3F1ZXVlMTE3"),
    ("encoding117queue117", "ZW5jb2RpbmcxMTdxdWV1ZTExNw"),
    ("encoding117worker117", "ZW5jb2RpbmcxMTd3b3JrZXIxMTc"),
    ("encoding117kernel117", "ZW5jb2RpbmcxMTdrZXJuZWwxMTc"),
    ("encoding117signal117", "ZW5jb2RpbmcxMTdzaWduYWwxMTc"),
    ("mapping117signal117", "bWFwcGluZzExN3NpZ25hbDExNw"),
    ("mapping117packet117", "bWFwcGluZzExN3BhY2tldDExNw"),
    ("mapping117router117", "bWFwcGluZzExN3JvdXRlcjExNw"),
    ("mapping117cluster117", "bWFwcGluZzExN2NsdXN0ZXIxMTc"),
    ("record117cluster117", "cmVjb3JkMTE3Y2x1c3RlcjExNw"),
    ("record117mirror117", "cmVjb3JkMTE3bWlycm9yMTE3"),
    ("record117filter117", "cmVjb3JkMTE3ZmlsdGVyMTE3"),
    ("record117ranking117", "cmVjb3JkMTE3cmFua2luZzExNw"),
    ("candle117ranking117", "Y2FuZGxlMTE3cmFua2luZzExNw"),
    ("candle117encoding117", "Y2FuZGxlMTE3ZW5jb2RpbmcxMTc"),
    ("candle117mapping117", "Y2FuZGxlMTE3bWFwcGluZzExNw"),
    ("candle117record117", "Y2FuZGxlMTE3cmVjb3JkMTE3"),
    ("thread117record117", "dGhyZWFkMTE3cmVjb3JkMTE3"),
    ("thread117candle117", "dGhyZWFkMTE3Y2FuZGxlMTE3"),
    ("thread117thread117", "dGhyZWFkMTE3dGhyZWFkMTE3"),
    ("thread117kitten117", "dGhyZWFkMTE3a2l0dGVuMTE3"),
    (
        "round 117: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTE3OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 117: agentuniverse is a framework for multi agents",
        "cm91bmQgMTE3OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 117: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTE3OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 117: the processor reads the record then stops",
        "cm91bmQgMTE3OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 117: a worker pulls the next task from the queue",
        "cm91bmQgMTE3OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 117: signals travel through the network layer",
        "cm91bmQgMTE3OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 117: the gateway routes each request by policy",
        "cm91bmQgMTE3OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 117: memory grows until the buffer is full",
        "cm91bmQgMTE3OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 117: the cluster mirrors every packet twice",
        "cm91bmQgMTE3OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 117: ranking uses tokens learned from the corpus",
        "cm91bmQgMTE3OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 117: a long session ends when the candle dies",
        "cm91bmQgMTE3OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 117: encode the prompt then map the result",
        "cm91bmQgMTE3OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 117: the kernel wakes the worker at dawn",
        "cm91bmQgMTE3OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 117: service latency drops after the patch",
        "cm91bmQgMTE3OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 117: the library caches every vector it sees",
        "cm91bmQgMTE3OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 117: agents argue then the debate resolves",
        "cm91bmQgMTE3OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 117: the filter keeps only strong matches",
        "cm91bmQgMTE3OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 117: the model answers with a short reply",
        "cm91bmQgMTE3OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 117: the recorder stores the reasoning trace",
        "cm91bmQgMTE3OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 117: the angel watches the processor run",
        "cm91bmQgMTE3OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 117: angle of the vector decides the match",
        "cm91bmQgMTE3OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 117: the candle burns twice as long at night",
        "cm91bmQgMTE3OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 117: a mirror of the universe in one line",
        "cm91bmQgMTE3OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 117: the queue drains before the storm", "cm91bmQgMTE3OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
