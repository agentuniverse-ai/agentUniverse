"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten127kitten127", "a2l0dGVuMTI3a2l0dGVuMTI3"),
    ("kitten127sitting127", "a2l0dGVuMTI3c2l0dGluZzEyNw"),
    ("kitten127agent127", "a2l0dGVuMTI3YWdlbnQxMjc"),
    ("kitten127angle127", "a2l0dGVuMTI3YW5nbGUxMjc"),
    ("sitting127angle127", "c2l0dGluZzEyN2FuZ2xlMTI3"),
    ("sitting127universe127", "c2l0dGluZzEyN3VuaXZlcnNlMTI3"),
    ("sitting127memory127", "c2l0dGluZzEyN21lbW9yeTEyNw"),
    ("sitting127stream127", "c2l0dGluZzEyN3N0cmVhbTEyNw"),
    ("agent127stream127", "YWdlbnQxMjdzdHJlYW0xMjc"),
    ("agent127context127", "YWdlbnQxMjdjb250ZXh0MTI3"),
    ("agent127knowledge127", "YWdlbnQxMjdrbm93bGVkZ2UxMjc"),
    ("agent127vector127", "YWdlbnQxMjd2ZWN0b3IxMjc"),
    ("angle127vector127", "YW5nbGUxMjd2ZWN0b3IxMjc"),
    ("angle127processor127", "YW5nbGUxMjdwcm9jZXNzb3IxMjc"),
    ("angle127reasoning127", "YW5nbGUxMjdyZWFzb25pbmcxMjc"),
    ("angle127machine127", "YW5nbGUxMjdtYWNoaW5lMTI3"),
    ("universe127machine127", "dW5pdmVyc2UxMjdtYWNoaW5lMTI3"),
    ("universe127learning127", "dW5pdmVyc2UxMjdsZWFybmluZzEyNw"),
    ("universe127model127", "dW5pdmVyc2UxMjdtb2RlbDEyNw"),
    ("universe127token127", "dW5pdmVyc2UxMjd0b2tlbjEyNw"),
    ("memory127token127", "bWVtb3J5MTI3dG9rZW4xMjc"),
    ("memory127prompt127", "bWVtb3J5MTI3cHJvbXB0MTI3"),
    ("memory127session127", "bWVtb3J5MTI3c2Vzc2lvbjEyNw"),
    ("memory127library127", "bWVtb3J5MTI3bGlicmFyeTEyNw"),
    ("stream127library127", "c3RyZWFtMTI3bGlicmFyeTEyNw"),
    ("stream127service127", "c3RyZWFtMTI3c2VydmljZTEyNw"),
    ("stream127gateway127", "c3RyZWFtMTI3Z2F0ZXdheTEyNw"),
    ("stream127storage127", "c3RyZWFtMTI3c3RvcmFnZTEyNw"),
    ("context127storage127", "Y29udGV4dDEyN3N0b3JhZ2UxMjc"),
    ("context127network127", "Y29udGV4dDEyN25ldHdvcmsxMjc"),
    ("context127latency127", "Y29udGV4dDEyN2xhdGVuY3kxMjc"),
    ("context127buffer127", "Y29udGV4dDEyN2J1ZmZlcjEyNw"),
    ("knowledge127buffer127", "a25vd2xlZGdlMTI3YnVmZmVyMTI3"),
    ("knowledge127queue127", "a25vd2xlZGdlMTI3cXVldWUxMjc"),
    ("knowledge127worker127", "a25vd2xlZGdlMTI3d29ya2VyMTI3"),
    ("knowledge127kernel127", "a25vd2xlZGdlMTI3a2VybmVsMTI3"),
    ("vector127kernel127", "dmVjdG9yMTI3a2VybmVsMTI3"),
    ("vector127signal127", "dmVjdG9yMTI3c2lnbmFsMTI3"),
    ("vector127packet127", "dmVjdG9yMTI3cGFja2V0MTI3"),
    ("vector127router127", "dmVjdG9yMTI3cm91dGVyMTI3"),
    ("processor127router127", "cHJvY2Vzc29yMTI3cm91dGVyMTI3"),
    ("processor127cluster127", "cHJvY2Vzc29yMTI3Y2x1c3RlcjEyNw"),
    ("processor127mirror127", "cHJvY2Vzc29yMTI3bWlycm9yMTI3"),
    ("processor127filter127", "cHJvY2Vzc29yMTI3ZmlsdGVyMTI3"),
    ("reasoning127filter127", "cmVhc29uaW5nMTI3ZmlsdGVyMTI3"),
    ("reasoning127ranking127", "cmVhc29uaW5nMTI3cmFua2luZzEyNw"),
    ("reasoning127encoding127", "cmVhc29uaW5nMTI3ZW5jb2RpbmcxMjc"),
    ("reasoning127mapping127", "cmVhc29uaW5nMTI3bWFwcGluZzEyNw"),
    ("machine127mapping127", "bWFjaGluZTEyN21hcHBpbmcxMjc"),
    ("machine127record127", "bWFjaGluZTEyN3JlY29yZDEyNw"),
    ("machine127candle127", "bWFjaGluZTEyN2NhbmRsZTEyNw"),
    ("machine127thread127", "bWFjaGluZTEyN3RocmVhZDEyNw"),
    ("learning127thread127", "bGVhcm5pbmcxMjd0aHJlYWQxMjc"),
    ("learning127kitten127", "bGVhcm5pbmcxMjdraXR0ZW4xMjc"),
    ("learning127sitting127", "bGVhcm5pbmcxMjdzaXR0aW5nMTI3"),
    ("learning127agent127", "bGVhcm5pbmcxMjdhZ2VudDEyNw"),
    ("model127agent127", "bW9kZWwxMjdhZ2VudDEyNw"),
    ("model127angle127", "bW9kZWwxMjdhbmdsZTEyNw"),
    ("model127universe127", "bW9kZWwxMjd1bml2ZXJzZTEyNw"),
    ("model127memory127", "bW9kZWwxMjdtZW1vcnkxMjc"),
    ("token127memory127", "dG9rZW4xMjdtZW1vcnkxMjc"),
    ("token127stream127", "dG9rZW4xMjdzdHJlYW0xMjc"),
    ("token127context127", "dG9rZW4xMjdjb250ZXh0MTI3"),
    ("token127knowledge127", "dG9rZW4xMjdrbm93bGVkZ2UxMjc"),
    ("prompt127knowledge127", "cHJvbXB0MTI3a25vd2xlZGdlMTI3"),
    ("prompt127vector127", "cHJvbXB0MTI3dmVjdG9yMTI3"),
    ("prompt127processor127", "cHJvbXB0MTI3cHJvY2Vzc29yMTI3"),
    ("prompt127reasoning127", "cHJvbXB0MTI3cmVhc29uaW5nMTI3"),
    ("session127reasoning127", "c2Vzc2lvbjEyN3JlYXNvbmluZzEyNw"),
    ("session127machine127", "c2Vzc2lvbjEyN21hY2hpbmUxMjc"),
    ("session127learning127", "c2Vzc2lvbjEyN2xlYXJuaW5nMTI3"),
    ("session127model127", "c2Vzc2lvbjEyN21vZGVsMTI3"),
    ("library127model127", "bGlicmFyeTEyN21vZGVsMTI3"),
    ("library127token127", "bGlicmFyeTEyN3Rva2VuMTI3"),
    ("library127prompt127", "bGlicmFyeTEyN3Byb21wdDEyNw"),
    ("library127session127", "bGlicmFyeTEyN3Nlc3Npb24xMjc"),
    ("service127session127", "c2VydmljZTEyN3Nlc3Npb24xMjc"),
    ("service127library127", "c2VydmljZTEyN2xpYnJhcnkxMjc"),
    ("service127service127", "c2VydmljZTEyN3NlcnZpY2UxMjc"),
    ("service127gateway127", "c2VydmljZTEyN2dhdGV3YXkxMjc"),
    ("gateway127gateway127", "Z2F0ZXdheTEyN2dhdGV3YXkxMjc"),
    ("gateway127storage127", "Z2F0ZXdheTEyN3N0b3JhZ2UxMjc"),
    ("gateway127network127", "Z2F0ZXdheTEyN25ldHdvcmsxMjc"),
    ("gateway127latency127", "Z2F0ZXdheTEyN2xhdGVuY3kxMjc"),
    ("storage127latency127", "c3RvcmFnZTEyN2xhdGVuY3kxMjc"),
    ("storage127buffer127", "c3RvcmFnZTEyN2J1ZmZlcjEyNw"),
    ("storage127queue127", "c3RvcmFnZTEyN3F1ZXVlMTI3"),
    ("storage127worker127", "c3RvcmFnZTEyN3dvcmtlcjEyNw"),
    ("network127worker127", "bmV0d29yazEyN3dvcmtlcjEyNw"),
    ("network127kernel127", "bmV0d29yazEyN2tlcm5lbDEyNw"),
    ("network127signal127", "bmV0d29yazEyN3NpZ25hbDEyNw"),
    ("network127packet127", "bmV0d29yazEyN3BhY2tldDEyNw"),
    ("latency127packet127", "bGF0ZW5jeTEyN3BhY2tldDEyNw"),
    ("latency127router127", "bGF0ZW5jeTEyN3JvdXRlcjEyNw"),
    ("latency127cluster127", "bGF0ZW5jeTEyN2NsdXN0ZXIxMjc"),
    ("latency127mirror127", "bGF0ZW5jeTEyN21pcnJvcjEyNw"),
    ("buffer127mirror127", "YnVmZmVyMTI3bWlycm9yMTI3"),
    ("buffer127filter127", "YnVmZmVyMTI3ZmlsdGVyMTI3"),
    ("buffer127ranking127", "YnVmZmVyMTI3cmFua2luZzEyNw"),
    ("buffer127encoding127", "YnVmZmVyMTI3ZW5jb2RpbmcxMjc"),
    ("queue127encoding127", "cXVldWUxMjdlbmNvZGluZzEyNw"),
    ("queue127mapping127", "cXVldWUxMjdtYXBwaW5nMTI3"),
    ("queue127record127", "cXVldWUxMjdyZWNvcmQxMjc"),
    ("queue127candle127", "cXVldWUxMjdjYW5kbGUxMjc"),
    ("worker127candle127", "d29ya2VyMTI3Y2FuZGxlMTI3"),
    ("worker127thread127", "d29ya2VyMTI3dGhyZWFkMTI3"),
    ("worker127kitten127", "d29ya2VyMTI3a2l0dGVuMTI3"),
    ("worker127sitting127", "d29ya2VyMTI3c2l0dGluZzEyNw"),
    ("kernel127sitting127", "a2VybmVsMTI3c2l0dGluZzEyNw"),
    ("kernel127agent127", "a2VybmVsMTI3YWdlbnQxMjc"),
    ("kernel127angle127", "a2VybmVsMTI3YW5nbGUxMjc"),
    ("kernel127universe127", "a2VybmVsMTI3dW5pdmVyc2UxMjc"),
    ("signal127universe127", "c2lnbmFsMTI3dW5pdmVyc2UxMjc"),
    ("signal127memory127", "c2lnbmFsMTI3bWVtb3J5MTI3"),
    ("signal127stream127", "c2lnbmFsMTI3c3RyZWFtMTI3"),
    ("signal127context127", "c2lnbmFsMTI3Y29udGV4dDEyNw"),
    ("packet127context127", "cGFja2V0MTI3Y29udGV4dDEyNw"),
    ("packet127knowledge127", "cGFja2V0MTI3a25vd2xlZGdlMTI3"),
    ("packet127vector127", "cGFja2V0MTI3dmVjdG9yMTI3"),
    ("packet127processor127", "cGFja2V0MTI3cHJvY2Vzc29yMTI3"),
    ("router127processor127", "cm91dGVyMTI3cHJvY2Vzc29yMTI3"),
    ("router127reasoning127", "cm91dGVyMTI3cmVhc29uaW5nMTI3"),
    ("router127machine127", "cm91dGVyMTI3bWFjaGluZTEyNw"),
    ("router127learning127", "cm91dGVyMTI3bGVhcm5pbmcxMjc"),
    ("cluster127learning127", "Y2x1c3RlcjEyN2xlYXJuaW5nMTI3"),
    ("cluster127model127", "Y2x1c3RlcjEyN21vZGVsMTI3"),
    ("cluster127token127", "Y2x1c3RlcjEyN3Rva2VuMTI3"),
    ("cluster127prompt127", "Y2x1c3RlcjEyN3Byb21wdDEyNw"),
    ("mirror127prompt127", "bWlycm9yMTI3cHJvbXB0MTI3"),
    ("mirror127session127", "bWlycm9yMTI3c2Vzc2lvbjEyNw"),
    ("mirror127library127", "bWlycm9yMTI3bGlicmFyeTEyNw"),
    ("mirror127service127", "bWlycm9yMTI3c2VydmljZTEyNw"),
    ("filter127service127", "ZmlsdGVyMTI3c2VydmljZTEyNw"),
    ("filter127gateway127", "ZmlsdGVyMTI3Z2F0ZXdheTEyNw"),
    ("filter127storage127", "ZmlsdGVyMTI3c3RvcmFnZTEyNw"),
    ("filter127network127", "ZmlsdGVyMTI3bmV0d29yazEyNw"),
    ("ranking127network127", "cmFua2luZzEyN25ldHdvcmsxMjc"),
    ("ranking127latency127", "cmFua2luZzEyN2xhdGVuY3kxMjc"),
    ("ranking127buffer127", "cmFua2luZzEyN2J1ZmZlcjEyNw"),
    ("ranking127queue127", "cmFua2luZzEyN3F1ZXVlMTI3"),
    ("encoding127queue127", "ZW5jb2RpbmcxMjdxdWV1ZTEyNw"),
    ("encoding127worker127", "ZW5jb2RpbmcxMjd3b3JrZXIxMjc"),
    ("encoding127kernel127", "ZW5jb2RpbmcxMjdrZXJuZWwxMjc"),
    ("encoding127signal127", "ZW5jb2RpbmcxMjdzaWduYWwxMjc"),
    ("mapping127signal127", "bWFwcGluZzEyN3NpZ25hbDEyNw"),
    ("mapping127packet127", "bWFwcGluZzEyN3BhY2tldDEyNw"),
    ("mapping127router127", "bWFwcGluZzEyN3JvdXRlcjEyNw"),
    ("mapping127cluster127", "bWFwcGluZzEyN2NsdXN0ZXIxMjc"),
    ("record127cluster127", "cmVjb3JkMTI3Y2x1c3RlcjEyNw"),
    ("record127mirror127", "cmVjb3JkMTI3bWlycm9yMTI3"),
    ("record127filter127", "cmVjb3JkMTI3ZmlsdGVyMTI3"),
    ("record127ranking127", "cmVjb3JkMTI3cmFua2luZzEyNw"),
    ("candle127ranking127", "Y2FuZGxlMTI3cmFua2luZzEyNw"),
    ("candle127encoding127", "Y2FuZGxlMTI3ZW5jb2RpbmcxMjc"),
    ("candle127mapping127", "Y2FuZGxlMTI3bWFwcGluZzEyNw"),
    ("candle127record127", "Y2FuZGxlMTI3cmVjb3JkMTI3"),
    ("thread127record127", "dGhyZWFkMTI3cmVjb3JkMTI3"),
    ("thread127candle127", "dGhyZWFkMTI3Y2FuZGxlMTI3"),
    ("thread127thread127", "dGhyZWFkMTI3dGhyZWFkMTI3"),
    ("thread127kitten127", "dGhyZWFkMTI3a2l0dGVuMTI3"),
    (
        "round 127: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTI3OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 127: agentuniverse is a framework for multi agents",
        "cm91bmQgMTI3OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 127: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTI3OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 127: the processor reads the record then stops",
        "cm91bmQgMTI3OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 127: a worker pulls the next task from the queue",
        "cm91bmQgMTI3OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 127: signals travel through the network layer",
        "cm91bmQgMTI3OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 127: the gateway routes each request by policy",
        "cm91bmQgMTI3OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 127: memory grows until the buffer is full",
        "cm91bmQgMTI3OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 127: the cluster mirrors every packet twice",
        "cm91bmQgMTI3OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 127: ranking uses tokens learned from the corpus",
        "cm91bmQgMTI3OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 127: a long session ends when the candle dies",
        "cm91bmQgMTI3OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 127: encode the prompt then map the result",
        "cm91bmQgMTI3OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 127: the kernel wakes the worker at dawn",
        "cm91bmQgMTI3OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 127: service latency drops after the patch",
        "cm91bmQgMTI3OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 127: the library caches every vector it sees",
        "cm91bmQgMTI3OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 127: agents argue then the debate resolves",
        "cm91bmQgMTI3OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 127: the filter keeps only strong matches",
        "cm91bmQgMTI3OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 127: the model answers with a short reply",
        "cm91bmQgMTI3OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 127: the recorder stores the reasoning trace",
        "cm91bmQgMTI3OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 127: the angel watches the processor run",
        "cm91bmQgMTI3OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 127: angle of the vector decides the match",
        "cm91bmQgMTI3OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 127: the candle burns twice as long at night",
        "cm91bmQgMTI3OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 127: a mirror of the universe in one line",
        "cm91bmQgMTI3OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 127: the queue drains before the storm", "cm91bmQgMTI3OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
