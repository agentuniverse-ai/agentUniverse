"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten157kitten157", "a2l0dGVuMTU3a2l0dGVuMTU3"),
    ("kitten157sitting157", "a2l0dGVuMTU3c2l0dGluZzE1Nw"),
    ("kitten157agent157", "a2l0dGVuMTU3YWdlbnQxNTc"),
    ("kitten157angle157", "a2l0dGVuMTU3YW5nbGUxNTc"),
    ("sitting157angle157", "c2l0dGluZzE1N2FuZ2xlMTU3"),
    ("sitting157universe157", "c2l0dGluZzE1N3VuaXZlcnNlMTU3"),
    ("sitting157memory157", "c2l0dGluZzE1N21lbW9yeTE1Nw"),
    ("sitting157stream157", "c2l0dGluZzE1N3N0cmVhbTE1Nw"),
    ("agent157stream157", "YWdlbnQxNTdzdHJlYW0xNTc"),
    ("agent157context157", "YWdlbnQxNTdjb250ZXh0MTU3"),
    ("agent157knowledge157", "YWdlbnQxNTdrbm93bGVkZ2UxNTc"),
    ("agent157vector157", "YWdlbnQxNTd2ZWN0b3IxNTc"),
    ("angle157vector157", "YW5nbGUxNTd2ZWN0b3IxNTc"),
    ("angle157processor157", "YW5nbGUxNTdwcm9jZXNzb3IxNTc"),
    ("angle157reasoning157", "YW5nbGUxNTdyZWFzb25pbmcxNTc"),
    ("angle157machine157", "YW5nbGUxNTdtYWNoaW5lMTU3"),
    ("universe157machine157", "dW5pdmVyc2UxNTdtYWNoaW5lMTU3"),
    ("universe157learning157", "dW5pdmVyc2UxNTdsZWFybmluZzE1Nw"),
    ("universe157model157", "dW5pdmVyc2UxNTdtb2RlbDE1Nw"),
    ("universe157token157", "dW5pdmVyc2UxNTd0b2tlbjE1Nw"),
    ("memory157token157", "bWVtb3J5MTU3dG9rZW4xNTc"),
    ("memory157prompt157", "bWVtb3J5MTU3cHJvbXB0MTU3"),
    ("memory157session157", "bWVtb3J5MTU3c2Vzc2lvbjE1Nw"),
    ("memory157library157", "bWVtb3J5MTU3bGlicmFyeTE1Nw"),
    ("stream157library157", "c3RyZWFtMTU3bGlicmFyeTE1Nw"),
    ("stream157service157", "c3RyZWFtMTU3c2VydmljZTE1Nw"),
    ("stream157gateway157", "c3RyZWFtMTU3Z2F0ZXdheTE1Nw"),
    ("stream157storage157", "c3RyZWFtMTU3c3RvcmFnZTE1Nw"),
    ("context157storage157", "Y29udGV4dDE1N3N0b3JhZ2UxNTc"),
    ("context157network157", "Y29udGV4dDE1N25ldHdvcmsxNTc"),
    ("context157latency157", "Y29udGV4dDE1N2xhdGVuY3kxNTc"),
    ("context157buffer157", "Y29udGV4dDE1N2J1ZmZlcjE1Nw"),
    ("knowledge157buffer157", "a25vd2xlZGdlMTU3YnVmZmVyMTU3"),
    ("knowledge157queue157", "a25vd2xlZGdlMTU3cXVldWUxNTc"),
    ("knowledge157worker157", "a25vd2xlZGdlMTU3d29ya2VyMTU3"),
    ("knowledge157kernel157", "a25vd2xlZGdlMTU3a2VybmVsMTU3"),
    ("vector157kernel157", "dmVjdG9yMTU3a2VybmVsMTU3"),
    ("vector157signal157", "dmVjdG9yMTU3c2lnbmFsMTU3"),
    ("vector157packet157", "dmVjdG9yMTU3cGFja2V0MTU3"),
    ("vector157router157", "dmVjdG9yMTU3cm91dGVyMTU3"),
    ("processor157router157", "cHJvY2Vzc29yMTU3cm91dGVyMTU3"),
    ("processor157cluster157", "cHJvY2Vzc29yMTU3Y2x1c3RlcjE1Nw"),
    ("processor157mirror157", "cHJvY2Vzc29yMTU3bWlycm9yMTU3"),
    ("processor157filter157", "cHJvY2Vzc29yMTU3ZmlsdGVyMTU3"),
    ("reasoning157filter157", "cmVhc29uaW5nMTU3ZmlsdGVyMTU3"),
    ("reasoning157ranking157", "cmVhc29uaW5nMTU3cmFua2luZzE1Nw"),
    ("reasoning157encoding157", "cmVhc29uaW5nMTU3ZW5jb2RpbmcxNTc"),
    ("reasoning157mapping157", "cmVhc29uaW5nMTU3bWFwcGluZzE1Nw"),
    ("machine157mapping157", "bWFjaGluZTE1N21hcHBpbmcxNTc"),
    ("machine157record157", "bWFjaGluZTE1N3JlY29yZDE1Nw"),
    ("machine157candle157", "bWFjaGluZTE1N2NhbmRsZTE1Nw"),
    ("machine157thread157", "bWFjaGluZTE1N3RocmVhZDE1Nw"),
    ("learning157thread157", "bGVhcm5pbmcxNTd0aHJlYWQxNTc"),
    ("learning157kitten157", "bGVhcm5pbmcxNTdraXR0ZW4xNTc"),
    ("learning157sitting157", "bGVhcm5pbmcxNTdzaXR0aW5nMTU3"),
    ("learning157agent157", "bGVhcm5pbmcxNTdhZ2VudDE1Nw"),
    ("model157agent157", "bW9kZWwxNTdhZ2VudDE1Nw"),
    ("model157angle157", "bW9kZWwxNTdhbmdsZTE1Nw"),
    ("model157universe157", "bW9kZWwxNTd1bml2ZXJzZTE1Nw"),
    ("model157memory157", "bW9kZWwxNTdtZW1vcnkxNTc"),
    ("token157memory157", "dG9rZW4xNTdtZW1vcnkxNTc"),
    ("token157stream157", "dG9rZW4xNTdzdHJlYW0xNTc"),
    ("token157context157", "dG9rZW4xNTdjb250ZXh0MTU3"),
    ("token157knowledge157", "dG9rZW4xNTdrbm93bGVkZ2UxNTc"),
    ("prompt157knowledge157", "cHJvbXB0MTU3a25vd2xlZGdlMTU3"),
    ("prompt157vector157", "cHJvbXB0MTU3dmVjdG9yMTU3"),
    ("prompt157processor157", "cHJvbXB0MTU3cHJvY2Vzc29yMTU3"),
    ("prompt157reasoning157", "cHJvbXB0MTU3cmVhc29uaW5nMTU3"),
    ("session157reasoning157", "c2Vzc2lvbjE1N3JlYXNvbmluZzE1Nw"),
    ("session157machine157", "c2Vzc2lvbjE1N21hY2hpbmUxNTc"),
    ("session157learning157", "c2Vzc2lvbjE1N2xlYXJuaW5nMTU3"),
    ("session157model157", "c2Vzc2lvbjE1N21vZGVsMTU3"),
    ("library157model157", "bGlicmFyeTE1N21vZGVsMTU3"),
    ("library157token157", "bGlicmFyeTE1N3Rva2VuMTU3"),
    ("library157prompt157", "bGlicmFyeTE1N3Byb21wdDE1Nw"),
    ("library157session157", "bGlicmFyeTE1N3Nlc3Npb24xNTc"),
    ("service157session157", "c2VydmljZTE1N3Nlc3Npb24xNTc"),
    ("service157library157", "c2VydmljZTE1N2xpYnJhcnkxNTc"),
    ("service157service157", "c2VydmljZTE1N3NlcnZpY2UxNTc"),
    ("service157gateway157", "c2VydmljZTE1N2dhdGV3YXkxNTc"),
    ("gateway157gateway157", "Z2F0ZXdheTE1N2dhdGV3YXkxNTc"),
    ("gateway157storage157", "Z2F0ZXdheTE1N3N0b3JhZ2UxNTc"),
    ("gateway157network157", "Z2F0ZXdheTE1N25ldHdvcmsxNTc"),
    ("gateway157latency157", "Z2F0ZXdheTE1N2xhdGVuY3kxNTc"),
    ("storage157latency157", "c3RvcmFnZTE1N2xhdGVuY3kxNTc"),
    ("storage157buffer157", "c3RvcmFnZTE1N2J1ZmZlcjE1Nw"),
    ("storage157queue157", "c3RvcmFnZTE1N3F1ZXVlMTU3"),
    ("storage157worker157", "c3RvcmFnZTE1N3dvcmtlcjE1Nw"),
    ("network157worker157", "bmV0d29yazE1N3dvcmtlcjE1Nw"),
    ("network157kernel157", "bmV0d29yazE1N2tlcm5lbDE1Nw"),
    ("network157signal157", "bmV0d29yazE1N3NpZ25hbDE1Nw"),
    ("network157packet157", "bmV0d29yazE1N3BhY2tldDE1Nw"),
    ("latency157packet157", "bGF0ZW5jeTE1N3BhY2tldDE1Nw"),
    ("latency157router157", "bGF0ZW5jeTE1N3JvdXRlcjE1Nw"),
    ("latency157cluster157", "bGF0ZW5jeTE1N2NsdXN0ZXIxNTc"),
    ("latency157mirror157", "bGF0ZW5jeTE1N21pcnJvcjE1Nw"),
    ("buffer157mirror157", "YnVmZmVyMTU3bWlycm9yMTU3"),
    ("buffer157filter157", "YnVmZmVyMTU3ZmlsdGVyMTU3"),
    ("buffer157ranking157", "YnVmZmVyMTU3cmFua2luZzE1Nw"),
    ("buffer157encoding157", "YnVmZmVyMTU3ZW5jb2RpbmcxNTc"),
    ("queue157encoding157", "cXVldWUxNTdlbmNvZGluZzE1Nw"),
    ("queue157mapping157", "cXVldWUxNTdtYXBwaW5nMTU3"),
    ("queue157record157", "cXVldWUxNTdyZWNvcmQxNTc"),
    ("queue157candle157", "cXVldWUxNTdjYW5kbGUxNTc"),
    ("worker157candle157", "d29ya2VyMTU3Y2FuZGxlMTU3"),
    ("worker157thread157", "d29ya2VyMTU3dGhyZWFkMTU3"),
    ("worker157kitten157", "d29ya2VyMTU3a2l0dGVuMTU3"),
    ("worker157sitting157", "d29ya2VyMTU3c2l0dGluZzE1Nw"),
    ("kernel157sitting157", "a2VybmVsMTU3c2l0dGluZzE1Nw"),
    ("kernel157agent157", "a2VybmVsMTU3YWdlbnQxNTc"),
    ("kernel157angle157", "a2VybmVsMTU3YW5nbGUxNTc"),
    ("kernel157universe157", "a2VybmVsMTU3dW5pdmVyc2UxNTc"),
    ("signal157universe157", "c2lnbmFsMTU3dW5pdmVyc2UxNTc"),
    ("signal157memory157", "c2lnbmFsMTU3bWVtb3J5MTU3"),
    ("signal157stream157", "c2lnbmFsMTU3c3RyZWFtMTU3"),
    ("signal157context157", "c2lnbmFsMTU3Y29udGV4dDE1Nw"),
    ("packet157context157", "cGFja2V0MTU3Y29udGV4dDE1Nw"),
    ("packet157knowledge157", "cGFja2V0MTU3a25vd2xlZGdlMTU3"),
    ("packet157vector157", "cGFja2V0MTU3dmVjdG9yMTU3"),
    ("packet157processor157", "cGFja2V0MTU3cHJvY2Vzc29yMTU3"),
    ("router157processor157", "cm91dGVyMTU3cHJvY2Vzc29yMTU3"),
    ("router157reasoning157", "cm91dGVyMTU3cmVhc29uaW5nMTU3"),
    ("router157machine157", "cm91dGVyMTU3bWFjaGluZTE1Nw"),
    ("router157learning157", "cm91dGVyMTU3bGVhcm5pbmcxNTc"),
    ("cluster157learning157", "Y2x1c3RlcjE1N2xlYXJuaW5nMTU3"),
    ("cluster157model157", "Y2x1c3RlcjE1N21vZGVsMTU3"),
    ("cluster157token157", "Y2x1c3RlcjE1N3Rva2VuMTU3"),
    ("cluster157prompt157", "Y2x1c3RlcjE1N3Byb21wdDE1Nw"),
    ("mirror157prompt157", "bWlycm9yMTU3cHJvbXB0MTU3"),
    ("mirror157session157", "bWlycm9yMTU3c2Vzc2lvbjE1Nw"),
    ("mirror157library157", "bWlycm9yMTU3bGlicmFyeTE1Nw"),
    ("mirror157service157", "bWlycm9yMTU3c2VydmljZTE1Nw"),
    ("filter157service157", "ZmlsdGVyMTU3c2VydmljZTE1Nw"),
    ("filter157gateway157", "ZmlsdGVyMTU3Z2F0ZXdheTE1Nw"),
    ("filter157storage157", "ZmlsdGVyMTU3c3RvcmFnZTE1Nw"),
    ("filter157network157", "ZmlsdGVyMTU3bmV0d29yazE1Nw"),
    ("ranking157network157", "cmFua2luZzE1N25ldHdvcmsxNTc"),
    ("ranking157latency157", "cmFua2luZzE1N2xhdGVuY3kxNTc"),
    ("ranking157buffer157", "cmFua2luZzE1N2J1ZmZlcjE1Nw"),
    ("ranking157queue157", "cmFua2luZzE1N3F1ZXVlMTU3"),
    ("encoding157queue157", "ZW5jb2RpbmcxNTdxdWV1ZTE1Nw"),
    ("encoding157worker157", "ZW5jb2RpbmcxNTd3b3JrZXIxNTc"),
    ("encoding157kernel157", "ZW5jb2RpbmcxNTdrZXJuZWwxNTc"),
    ("encoding157signal157", "ZW5jb2RpbmcxNTdzaWduYWwxNTc"),
    ("mapping157signal157", "bWFwcGluZzE1N3NpZ25hbDE1Nw"),
    ("mapping157packet157", "bWFwcGluZzE1N3BhY2tldDE1Nw"),
    ("mapping157router157", "bWFwcGluZzE1N3JvdXRlcjE1Nw"),
    ("mapping157cluster157", "bWFwcGluZzE1N2NsdXN0ZXIxNTc"),
    ("record157cluster157", "cmVjb3JkMTU3Y2x1c3RlcjE1Nw"),
    ("record157mirror157", "cmVjb3JkMTU3bWlycm9yMTU3"),
    ("record157filter157", "cmVjb3JkMTU3ZmlsdGVyMTU3"),
    ("record157ranking157", "cmVjb3JkMTU3cmFua2luZzE1Nw"),
    ("candle157ranking157", "Y2FuZGxlMTU3cmFua2luZzE1Nw"),
    ("candle157encoding157", "Y2FuZGxlMTU3ZW5jb2RpbmcxNTc"),
    ("candle157mapping157", "Y2FuZGxlMTU3bWFwcGluZzE1Nw"),
    ("candle157record157", "Y2FuZGxlMTU3cmVjb3JkMTU3"),
    ("thread157record157", "dGhyZWFkMTU3cmVjb3JkMTU3"),
    ("thread157candle157", "dGhyZWFkMTU3Y2FuZGxlMTU3"),
    ("thread157thread157", "dGhyZWFkMTU3dGhyZWFkMTU3"),
    ("thread157kitten157", "dGhyZWFkMTU3a2l0dGVuMTU3"),
    (
        "round 157: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTU3OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 157: agentuniverse is a framework for multi agents",
        "cm91bmQgMTU3OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 157: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTU3OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 157: the processor reads the record then stops",
        "cm91bmQgMTU3OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 157: a worker pulls the next task from the queue",
        "cm91bmQgMTU3OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 157: signals travel through the network layer",
        "cm91bmQgMTU3OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 157: the gateway routes each request by policy",
        "cm91bmQgMTU3OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 157: memory grows until the buffer is full",
        "cm91bmQgMTU3OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 157: the cluster mirrors every packet twice",
        "cm91bmQgMTU3OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 157: ranking uses tokens learned from the corpus",
        "cm91bmQgMTU3OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 157: a long session ends when the candle dies",
        "cm91bmQgMTU3OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 157: encode the prompt then map the result",
        "cm91bmQgMTU3OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 157: the kernel wakes the worker at dawn",
        "cm91bmQgMTU3OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 157: service latency drops after the patch",
        "cm91bmQgMTU3OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 157: the library caches every vector it sees",
        "cm91bmQgMTU3OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 157: agents argue then the debate resolves",
        "cm91bmQgMTU3OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 157: the filter keeps only strong matches",
        "cm91bmQgMTU3OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 157: the model answers with a short reply",
        "cm91bmQgMTU3OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 157: the recorder stores the reasoning trace",
        "cm91bmQgMTU3OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 157: the angel watches the processor run",
        "cm91bmQgMTU3OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 157: angle of the vector decides the match",
        "cm91bmQgMTU3OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 157: the candle burns twice as long at night",
        "cm91bmQgMTU3OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 157: a mirror of the universe in one line",
        "cm91bmQgMTU3OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 157: the queue drains before the storm", "cm91bmQgMTU3OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
