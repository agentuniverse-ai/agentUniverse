"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten107kitten107", "a2l0dGVuMTA3a2l0dGVuMTA3"),
    ("kitten107sitting107", "a2l0dGVuMTA3c2l0dGluZzEwNw"),
    ("kitten107agent107", "a2l0dGVuMTA3YWdlbnQxMDc"),
    ("kitten107angle107", "a2l0dGVuMTA3YW5nbGUxMDc"),
    ("sitting107angle107", "c2l0dGluZzEwN2FuZ2xlMTA3"),
    ("sitting107universe107", "c2l0dGluZzEwN3VuaXZlcnNlMTA3"),
    ("sitting107memory107", "c2l0dGluZzEwN21lbW9yeTEwNw"),
    ("sitting107stream107", "c2l0dGluZzEwN3N0cmVhbTEwNw"),
    ("agent107stream107", "YWdlbnQxMDdzdHJlYW0xMDc"),
    ("agent107context107", "YWdlbnQxMDdjb250ZXh0MTA3"),
    ("agent107knowledge107", "YWdlbnQxMDdrbm93bGVkZ2UxMDc"),
    ("agent107vector107", "YWdlbnQxMDd2ZWN0b3IxMDc"),
    ("angle107vector107", "YW5nbGUxMDd2ZWN0b3IxMDc"),
    ("angle107processor107", "YW5nbGUxMDdwcm9jZXNzb3IxMDc"),
    ("angle107reasoning107", "YW5nbGUxMDdyZWFzb25pbmcxMDc"),
    ("angle107machine107", "YW5nbGUxMDdtYWNoaW5lMTA3"),
    ("universe107machine107", "dW5pdmVyc2UxMDdtYWNoaW5lMTA3"),
    ("universe107learning107", "dW5pdmVyc2UxMDdsZWFybmluZzEwNw"),
    ("universe107model107", "dW5pdmVyc2UxMDdtb2RlbDEwNw"),
    ("universe107token107", "dW5pdmVyc2UxMDd0b2tlbjEwNw"),
    ("memory107token107", "bWVtb3J5MTA3dG9rZW4xMDc"),
    ("memory107prompt107", "bWVtb3J5MTA3cHJvbXB0MTA3"),
    ("memory107session107", "bWVtb3J5MTA3c2Vzc2lvbjEwNw"),
    ("memory107library107", "bWVtb3J5MTA3bGlicmFyeTEwNw"),
    ("stream107library107", "c3RyZWFtMTA3bGlicmFyeTEwNw"),
    ("stream107service107", "c3RyZWFtMTA3c2VydmljZTEwNw"),
    ("stream107gateway107", "c3RyZWFtMTA3Z2F0ZXdheTEwNw"),
    ("stream107storage107", "c3RyZWFtMTA3c3RvcmFnZTEwNw"),
    ("context107storage107", "Y29udGV4dDEwN3N0b3JhZ2UxMDc"),
    ("context107network107", "Y29udGV4dDEwN25ldHdvcmsxMDc"),
    ("context107latency107", "Y29udGV4dDEwN2xhdGVuY3kxMDc"),
    ("context107buffer107", "Y29udGV4dDEwN2J1ZmZlcjEwNw"),
    ("knowledge107buffer107", "a25vd2xlZGdlMTA3YnVmZmVyMTA3"),
    ("knowledge107queue107", "a25vd2xlZGdlMTA3cXVldWUxMDc"),
    ("knowledge107worker107", "a25vd2xlZGdlMTA3d29ya2VyMTA3"),
    ("knowledge107kernel107", "a25vd2xlZGdlMTA3a2VybmVsMTA3"),
    ("vector107kernel107", "dmVjdG9yMTA3a2VybmVsMTA3"),
    ("vector107signal107", "dmVjdG9yMTA3c2lnbmFsMTA3"),
    ("vector107packet107", "dmVjdG9yMTA3cGFja2V0MTA3"),
    ("vector107router107", "dmVjdG9yMTA3cm91dGVyMTA3"),
    ("processor107router107", "cHJvY2Vzc29yMTA3cm91dGVyMTA3"),
    ("processor107cluster107", "cHJvY2Vzc29yMTA3Y2x1c3RlcjEwNw"),
    ("processor107mirror107", "cHJvY2Vzc29yMTA3bWlycm9yMTA3"),
    ("processor107filter107", "cHJvY2Vzc29yMTA3ZmlsdGVyMTA3"),
    ("reasoning107filter107", "cmVhc29uaW5nMTA3ZmlsdGVyMTA3"),
    ("reasoning107ranking107", "cmVhc29uaW5nMTA3cmFua2luZzEwNw"),
    ("reasoning107encoding107", "cmVhc29uaW5nMTA3ZW5jb2RpbmcxMDc"),
    ("reasoning107mapping107", "cmVhc29uaW5nMTA3bWFwcGluZzEwNw"),
    ("machine107mapping107", "bWFjaGluZTEwN21hcHBpbmcxMDc"),
    ("machine107record107", "bWFjaGluZTEwN3JlY29yZDEwNw"),
    ("machine107candle107", "bWFjaGluZTEwN2NhbmRsZTEwNw"),
    ("machine107thread107", "bWFjaGluZTEwN3RocmVhZDEwNw"),
    ("learning107thread107", "bGVhcm5pbmcxMDd0aHJlYWQxMDc"),
    ("learning107kitten107", "bGVhcm5pbmcxMDdraXR0ZW4xMDc"),
    ("learning107sitting107", "bGVhcm5pbmcxMDdzaXR0aW5nMTA3"),
    ("learning107agent107", "bGVhcm5pbmcxMDdhZ2VudDEwNw"),
    ("model107agent107", "bW9kZWwxMDdhZ2VudDEwNw"),
    ("model107angle107", "bW9kZWwxMDdhbmdsZTEwNw"),
    ("model107universe107", "bW9kZWwxMDd1bml2ZXJzZTEwNw"),
    ("model107memory107", "bW9kZWwxMDdtZW1vcnkxMDc"),
    ("token107memory107", "dG9rZW4xMDdtZW1vcnkxMDc"),
    ("token107stream107", "dG9rZW4xMDdzdHJlYW0xMDc"),
    ("token107context107", "dG9rZW4xMDdjb250ZXh0MTA3"),
    ("token107knowledge107", "dG9rZW4xMDdrbm93bGVkZ2UxMDc"),
    ("prompt107knowledge107", "cHJvbXB0MTA3a25vd2xlZGdlMTA3"),
    ("prompt107vector107", "cHJvbXB0MTA3dmVjdG9yMTA3"),
    ("prompt107processor107", "cHJvbXB0MTA3cHJvY2Vzc29yMTA3"),
    ("prompt107reasoning107", "cHJvbXB0MTA3cmVhc29uaW5nMTA3"),
    ("session107reasoning107", "c2Vzc2lvbjEwN3JlYXNvbmluZzEwNw"),
    ("session107machine107", "c2Vzc2lvbjEwN21hY2hpbmUxMDc"),
    ("session107learning107", "c2Vzc2lvbjEwN2xlYXJuaW5nMTA3"),
    ("session107model107", "c2Vzc2lvbjEwN21vZGVsMTA3"),
    ("library107model107", "bGlicmFyeTEwN21vZGVsMTA3"),
    ("library107token107", "bGlicmFyeTEwN3Rva2VuMTA3"),
    ("library107prompt107", "bGlicmFyeTEwN3Byb21wdDEwNw"),
    ("library107session107", "bGlicmFyeTEwN3Nlc3Npb24xMDc"),
    ("service107session107", "c2VydmljZTEwN3Nlc3Npb24xMDc"),
    ("service107library107", "c2VydmljZTEwN2xpYnJhcnkxMDc"),
    ("service107service107", "c2VydmljZTEwN3NlcnZpY2UxMDc"),
    ("service107gateway107", "c2VydmljZTEwN2dhdGV3YXkxMDc"),
    ("gateway107gateway107", "Z2F0ZXdheTEwN2dhdGV3YXkxMDc"),
    ("gateway107storage107", "Z2F0ZXdheTEwN3N0b3JhZ2UxMDc"),
    ("gateway107network107", "Z2F0ZXdheTEwN25ldHdvcmsxMDc"),
    ("gateway107latency107", "Z2F0ZXdheTEwN2xhdGVuY3kxMDc"),
    ("storage107latency107", "c3RvcmFnZTEwN2xhdGVuY3kxMDc"),
    ("storage107buffer107", "c3RvcmFnZTEwN2J1ZmZlcjEwNw"),
    ("storage107queue107", "c3RvcmFnZTEwN3F1ZXVlMTA3"),
    ("storage107worker107", "c3RvcmFnZTEwN3dvcmtlcjEwNw"),
    ("network107worker107", "bmV0d29yazEwN3dvcmtlcjEwNw"),
    ("network107kernel107", "bmV0d29yazEwN2tlcm5lbDEwNw"),
    ("network107signal107", "bmV0d29yazEwN3NpZ25hbDEwNw"),
    ("network107packet107", "bmV0d29yazEwN3BhY2tldDEwNw"),
    ("latency107packet107", "bGF0ZW5jeTEwN3BhY2tldDEwNw"),
    ("latency107router107", "bGF0ZW5jeTEwN3JvdXRlcjEwNw"),
    ("latency107cluster107", "bGF0ZW5jeTEwN2NsdXN0ZXIxMDc"),
    ("latency107mirror107", "bGF0ZW5jeTEwN21pcnJvcjEwNw"),
    ("buffer107mirror107", "YnVmZmVyMTA3bWlycm9yMTA3"),
    ("buffer107filter107", "YnVmZmVyMTA3ZmlsdGVyMTA3"),
    ("buffer107ranking107", "YnVmZmVyMTA3cmFua2luZzEwNw"),
    ("buffer107encoding107", "YnVmZmVyMTA3ZW5jb2RpbmcxMDc"),
    ("queue107encoding107", "cXVldWUxMDdlbmNvZGluZzEwNw"),
    ("queue107mapping107", "cXVldWUxMDdtYXBwaW5nMTA3"),
    ("queue107record107", "cXVldWUxMDdyZWNvcmQxMDc"),
    ("queue107candle107", "cXVldWUxMDdjYW5kbGUxMDc"),
    ("worker107candle107", "d29ya2VyMTA3Y2FuZGxlMTA3"),
    ("worker107thread107", "d29ya2VyMTA3dGhyZWFkMTA3"),
    ("worker107kitten107", "d29ya2VyMTA3a2l0dGVuMTA3"),
    ("worker107sitting107", "d29ya2VyMTA3c2l0dGluZzEwNw"),
    ("kernel107sitting107", "a2VybmVsMTA3c2l0dGluZzEwNw"),
    ("kernel107agent107", "a2VybmVsMTA3YWdlbnQxMDc"),
    ("kernel107angle107", "a2VybmVsMTA3YW5nbGUxMDc"),
    ("kernel107universe107", "a2VybmVsMTA3dW5pdmVyc2UxMDc"),
    ("signal107universe107", "c2lnbmFsMTA3dW5pdmVyc2UxMDc"),
    ("signal107memory107", "c2lnbmFsMTA3bWVtb3J5MTA3"),
    ("signal107stream107", "c2lnbmFsMTA3c3RyZWFtMTA3"),
    ("signal107context107", "c2lnbmFsMTA3Y29udGV4dDEwNw"),
    ("packet107context107", "cGFja2V0MTA3Y29udGV4dDEwNw"),
    ("packet107knowledge107", "cGFja2V0MTA3a25vd2xlZGdlMTA3"),
    ("packet107vector107", "cGFja2V0MTA3dmVjdG9yMTA3"),
    ("packet107processor107", "cGFja2V0MTA3cHJvY2Vzc29yMTA3"),
    ("router107processor107", "cm91dGVyMTA3cHJvY2Vzc29yMTA3"),
    ("router107reasoning107", "cm91dGVyMTA3cmVhc29uaW5nMTA3"),
    ("router107machine107", "cm91dGVyMTA3bWFjaGluZTEwNw"),
    ("router107learning107", "cm91dGVyMTA3bGVhcm5pbmcxMDc"),
    ("cluster107learning107", "Y2x1c3RlcjEwN2xlYXJuaW5nMTA3"),
    ("cluster107model107", "Y2x1c3RlcjEwN21vZGVsMTA3"),
    ("cluster107token107", "Y2x1c3RlcjEwN3Rva2VuMTA3"),
    ("cluster107prompt107", "Y2x1c3RlcjEwN3Byb21wdDEwNw"),
    ("mirror107prompt107", "bWlycm9yMTA3cHJvbXB0MTA3"),
    ("mirror107session107", "bWlycm9yMTA3c2Vzc2lvbjEwNw"),
    ("mirror107library107", "bWlycm9yMTA3bGlicmFyeTEwNw"),
    ("mirror107service107", "bWlycm9yMTA3c2VydmljZTEwNw"),
    ("filter107service107", "ZmlsdGVyMTA3c2VydmljZTEwNw"),
    ("filter107gateway107", "ZmlsdGVyMTA3Z2F0ZXdheTEwNw"),
    ("filter107storage107", "ZmlsdGVyMTA3c3RvcmFnZTEwNw"),
    ("filter107network107", "ZmlsdGVyMTA3bmV0d29yazEwNw"),
    ("ranking107network107", "cmFua2luZzEwN25ldHdvcmsxMDc"),
    ("ranking107latency107", "cmFua2luZzEwN2xhdGVuY3kxMDc"),
    ("ranking107buffer107", "cmFua2luZzEwN2J1ZmZlcjEwNw"),
    ("ranking107queue107", "cmFua2luZzEwN3F1ZXVlMTA3"),
    ("encoding107queue107", "ZW5jb2RpbmcxMDdxdWV1ZTEwNw"),
    ("encoding107worker107", "ZW5jb2RpbmcxMDd3b3JrZXIxMDc"),
    ("encoding107kernel107", "ZW5jb2RpbmcxMDdrZXJuZWwxMDc"),
    ("encoding107signal107", "ZW5jb2RpbmcxMDdzaWduYWwxMDc"),
    ("mapping107signal107", "bWFwcGluZzEwN3NpZ25hbDEwNw"),
    ("mapping107packet107", "bWFwcGluZzEwN3BhY2tldDEwNw"),
    ("mapping107router107", "bWFwcGluZzEwN3JvdXRlcjEwNw"),
    ("mapping107cluster107", "bWFwcGluZzEwN2NsdXN0ZXIxMDc"),
    ("record107cluster107", "cmVjb3JkMTA3Y2x1c3RlcjEwNw"),
    ("record107mirror107", "cmVjb3JkMTA3bWlycm9yMTA3"),
    ("record107filter107", "cmVjb3JkMTA3ZmlsdGVyMTA3"),
    ("record107ranking107", "cmVjb3JkMTA3cmFua2luZzEwNw"),
    ("candle107ranking107", "Y2FuZGxlMTA3cmFua2luZzEwNw"),
    ("candle107encoding107", "Y2FuZGxlMTA3ZW5jb2RpbmcxMDc"),
    ("candle107mapping107", "Y2FuZGxlMTA3bWFwcGluZzEwNw"),
    ("candle107record107", "Y2FuZGxlMTA3cmVjb3JkMTA3"),
    ("thread107record107", "dGhyZWFkMTA3cmVjb3JkMTA3"),
    ("thread107candle107", "dGhyZWFkMTA3Y2FuZGxlMTA3"),
    ("thread107thread107", "dGhyZWFkMTA3dGhyZWFkMTA3"),
    ("thread107kitten107", "dGhyZWFkMTA3a2l0dGVuMTA3"),
    (
        "round 107: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTA3OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 107: agentuniverse is a framework for multi agents",
        "cm91bmQgMTA3OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 107: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTA3OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 107: the processor reads the record then stops",
        "cm91bmQgMTA3OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 107: a worker pulls the next task from the queue",
        "cm91bmQgMTA3OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 107: signals travel through the network layer",
        "cm91bmQgMTA3OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 107: the gateway routes each request by policy",
        "cm91bmQgMTA3OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 107: memory grows until the buffer is full",
        "cm91bmQgMTA3OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 107: the cluster mirrors every packet twice",
        "cm91bmQgMTA3OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 107: ranking uses tokens learned from the corpus",
        "cm91bmQgMTA3OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 107: a long session ends when the candle dies",
        "cm91bmQgMTA3OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 107: encode the prompt then map the result",
        "cm91bmQgMTA3OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 107: the kernel wakes the worker at dawn",
        "cm91bmQgMTA3OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 107: service latency drops after the patch",
        "cm91bmQgMTA3OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 107: the library caches every vector it sees",
        "cm91bmQgMTA3OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 107: agents argue then the debate resolves",
        "cm91bmQgMTA3OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 107: the filter keeps only strong matches",
        "cm91bmQgMTA3OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 107: the model answers with a short reply",
        "cm91bmQgMTA3OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 107: the recorder stores the reasoning trace",
        "cm91bmQgMTA3OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 107: the angel watches the processor run",
        "cm91bmQgMTA3OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 107: angle of the vector decides the match",
        "cm91bmQgMTA3OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 107: the candle burns twice as long at night",
        "cm91bmQgMTA3OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 107: a mirror of the universe in one line",
        "cm91bmQgMTA3OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 107: the queue drains before the storm", "cm91bmQgMTA3OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
