"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten747kitten747", "a2l0dGVuNzQ3a2l0dGVuNzQ3"),
    ("kitten747sitting747", "a2l0dGVuNzQ3c2l0dGluZzc0Nw"),
    ("kitten747agent747", "a2l0dGVuNzQ3YWdlbnQ3NDc"),
    ("kitten747angle747", "a2l0dGVuNzQ3YW5nbGU3NDc"),
    ("sitting747angle747", "c2l0dGluZzc0N2FuZ2xlNzQ3"),
    ("sitting747universe747", "c2l0dGluZzc0N3VuaXZlcnNlNzQ3"),
    ("sitting747memory747", "c2l0dGluZzc0N21lbW9yeTc0Nw"),
    ("sitting747stream747", "c2l0dGluZzc0N3N0cmVhbTc0Nw"),
    ("agent747stream747", "YWdlbnQ3NDdzdHJlYW03NDc"),
    ("agent747context747", "YWdlbnQ3NDdjb250ZXh0NzQ3"),
    ("agent747knowledge747", "YWdlbnQ3NDdrbm93bGVkZ2U3NDc"),
    ("agent747vector747", "YWdlbnQ3NDd2ZWN0b3I3NDc"),
    ("angle747vector747", "YW5nbGU3NDd2ZWN0b3I3NDc"),
    ("angle747processor747", "YW5nbGU3NDdwcm9jZXNzb3I3NDc"),
    ("angle747reasoning747", "YW5nbGU3NDdyZWFzb25pbmc3NDc"),
    ("angle747machine747", "YW5nbGU3NDdtYWNoaW5lNzQ3"),
    ("universe747machine747", "dW5pdmVyc2U3NDdtYWNoaW5lNzQ3"),
    ("universe747learning747", "dW5pdmVyc2U3NDdsZWFybmluZzc0Nw"),
    ("universe747model747", "dW5pdmVyc2U3NDdtb2RlbDc0Nw"),
    ("universe747token747", "dW5pdmVyc2U3NDd0b2tlbjc0Nw"),
    ("memory747token747", "bWVtb3J5NzQ3dG9rZW43NDc"),
    ("memory747prompt747", "bWVtb3J5NzQ3cHJvbXB0NzQ3"),
    ("memory747session747", "bWVtb3J5NzQ3c2Vzc2lvbjc0Nw"),
    ("memory747library747", "bWVtb3J5NzQ3bGlicmFyeTc0Nw"),
    ("stream747library747", "c3RyZWFtNzQ3bGlicmFyeTc0Nw"),
    ("stream747service747", "c3RyZWFtNzQ3c2VydmljZTc0Nw"),
    ("stream747gateway747", "c3RyZWFtNzQ3Z2F0ZXdheTc0Nw"),
    ("stream747storage747", "c3RyZWFtNzQ3c3RvcmFnZTc0Nw"),
    ("context747storage747", "Y29udGV4dDc0N3N0b3JhZ2U3NDc"),
    ("context747network747", "Y29udGV4dDc0N25ldHdvcms3NDc"),
    ("context747latency747", "Y29udGV4dDc0N2xhdGVuY3k3NDc"),
    ("context747buffer747", "Y29udGV4dDc0N2J1ZmZlcjc0Nw"),
    ("knowledge747buffer747", "a25vd2xlZGdlNzQ3YnVmZmVyNzQ3"),
    ("knowledge747queue747", "a25vd2xlZGdlNzQ3cXVldWU3NDc"),
    ("knowledge747worker747", "a25vd2xlZGdlNzQ3d29ya2VyNzQ3"),
    ("knowledge747kernel747", "a25vd2xlZGdlNzQ3a2VybmVsNzQ3"),
    ("vector747kernel747", "dmVjdG9yNzQ3a2VybmVsNzQ3"),
    ("vector747signal747", "dmVjdG9yNzQ3c2lnbmFsNzQ3"),
    ("vector747packet747", "dmVjdG9yNzQ3cGFja2V0NzQ3"),
    ("vector747router747", "dmVjdG9yNzQ3cm91dGVyNzQ3"),
    ("processor747router747", "cHJvY2Vzc29yNzQ3cm91dGVyNzQ3"),
    ("processor747cluster747", "cHJvY2Vzc29yNzQ3Y2x1c3Rlcjc0Nw"),
    ("processor747mirror747", "cHJvY2Vzc29yNzQ3bWlycm9yNzQ3"),
    ("processor747filter747", "cHJvY2Vzc29yNzQ3ZmlsdGVyNzQ3"),
    ("reasoning747filter747", "cmVhc29uaW5nNzQ3ZmlsdGVyNzQ3"),
    ("reasoning747ranking747", "cmVhc29uaW5nNzQ3cmFua2luZzc0Nw"),
    ("reasoning747encoding747", "cmVhc29uaW5nNzQ3ZW5jb2Rpbmc3NDc"),
    ("reasoning747mapping747", "cmVhc29uaW5nNzQ3bWFwcGluZzc0Nw"),
    ("machine747mapping747", "bWFjaGluZTc0N21hcHBpbmc3NDc"),
    ("machine747record747", "bWFjaGluZTc0N3JlY29yZDc0Nw"),
    ("machine747candle747", "bWFjaGluZTc0N2NhbmRsZTc0Nw"),
    ("machine747thread747", "bWFjaGluZTc0N3RocmVhZDc0Nw"),
    ("learning747thread747", "bGVhcm5pbmc3NDd0aHJlYWQ3NDc"),
    ("learning747kitten747", "bGVhcm5pbmc3NDdraXR0ZW43NDc"),
    ("learning747sitting747", "bGVhcm5pbmc3NDdzaXR0aW5nNzQ3"),
    ("learning747agent747", "bGVhcm5pbmc3NDdhZ2VudDc0Nw"),
    ("model747agent747", "bW9kZWw3NDdhZ2VudDc0Nw"),
    ("model747angle747", "bW9kZWw3NDdhbmdsZTc0Nw"),
    ("model747universe747", "bW9kZWw3NDd1bml2ZXJzZTc0Nw"),
    ("model747memory747", "bW9kZWw3NDdtZW1vcnk3NDc"),
    ("token747memory747", "dG9rZW43NDdtZW1vcnk3NDc"),
    ("token747stream747", "dG9rZW43NDdzdHJlYW03NDc"),
    ("token747context747", "dG9rZW43NDdjb250ZXh0NzQ3"),
    ("token747knowledge747", "dG9rZW43NDdrbm93bGVkZ2U3NDc"),
    ("prompt747knowledge747", "cHJvbXB0NzQ3a25vd2xlZGdlNzQ3"),
    ("prompt747vector747", "cHJvbXB0NzQ3dmVjdG9yNzQ3"),
    ("prompt747processor747", "cHJvbXB0NzQ3cHJvY2Vzc29yNzQ3"),
    ("prompt747reasoning747", "cHJvbXB0NzQ3cmVhc29uaW5nNzQ3"),
    ("session747reasoning747", "c2Vzc2lvbjc0N3JlYXNvbmluZzc0Nw"),
    ("session747machine747", "c2Vzc2lvbjc0N21hY2hpbmU3NDc"),
    ("session747learning747", "c2Vzc2lvbjc0N2xlYXJuaW5nNzQ3"),
    ("session747model747", "c2Vzc2lvbjc0N21vZGVsNzQ3"),
    ("library747model747", "bGlicmFyeTc0N21vZGVsNzQ3"),
    ("library747token747", "bGlicmFyeTc0N3Rva2VuNzQ3"),
    ("library747prompt747", "bGlicmFyeTc0N3Byb21wdDc0Nw"),
    ("library747session747", "bGlicmFyeTc0N3Nlc3Npb243NDc"),
    ("service747session747", "c2VydmljZTc0N3Nlc3Npb243NDc"),
    ("service747library747", "c2VydmljZTc0N2xpYnJhcnk3NDc"),
    ("service747service747", "c2VydmljZTc0N3NlcnZpY2U3NDc"),
    ("service747gateway747", "c2VydmljZTc0N2dhdGV3YXk3NDc"),
    ("gateway747gateway747", "Z2F0ZXdheTc0N2dhdGV3YXk3NDc"),
    ("gateway747storage747", "Z2F0ZXdheTc0N3N0b3JhZ2U3NDc"),
    ("gateway747network747", "Z2F0ZXdheTc0N25ldHdvcms3NDc"),
    ("gateway747latency747", "Z2F0ZXdheTc0N2xhdGVuY3k3NDc"),
    ("storage747latency747", "c3RvcmFnZTc0N2xhdGVuY3k3NDc"),
    ("storage747buffer747", "c3RvcmFnZTc0N2J1ZmZlcjc0Nw"),
    ("storage747queue747", "c3RvcmFnZTc0N3F1ZXVlNzQ3"),
    ("storage747worker747", "c3RvcmFnZTc0N3dvcmtlcjc0Nw"),
    ("network747worker747", "bmV0d29yazc0N3dvcmtlcjc0Nw"),
    ("network747kernel747", "bmV0d29yazc0N2tlcm5lbDc0Nw"),
    ("network747signal747", "bmV0d29yazc0N3NpZ25hbDc0Nw"),
    ("network747packet747", "bmV0d29yazc0N3BhY2tldDc0Nw"),
    ("latency747packet747", "bGF0ZW5jeTc0N3BhY2tldDc0Nw"),
    ("latency747router747", "bGF0ZW5jeTc0N3JvdXRlcjc0Nw"),
    ("latency747cluster747", "bGF0ZW5jeTc0N2NsdXN0ZXI3NDc"),
    ("latency747mirror747", "bGF0ZW5jeTc0N21pcnJvcjc0Nw"),
    ("buffer747mirror747", "YnVmZmVyNzQ3bWlycm9yNzQ3"),
    ("buffer747filter747", "YnVmZmVyNzQ3ZmlsdGVyNzQ3"),
    ("buffer747ranking747", "YnVmZmVyNzQ3cmFua2luZzc0Nw"),
    ("buffer747encoding747", "YnVmZmVyNzQ3ZW5jb2Rpbmc3NDc"),
    ("queue747encoding747", "cXVldWU3NDdlbmNvZGluZzc0Nw"),
    ("queue747mapping747", "cXVldWU3NDdtYXBwaW5nNzQ3"),
    ("queue747record747", "cXVldWU3NDdyZWNvcmQ3NDc"),
    ("queue747candle747", "cXVldWU3NDdjYW5kbGU3NDc"),
    ("worker747candle747", "d29ya2VyNzQ3Y2FuZGxlNzQ3"),
    ("worker747thread747", "d29ya2VyNzQ3dGhyZWFkNzQ3"),
    ("worker747kitten747", "d29ya2VyNzQ3a2l0dGVuNzQ3"),
    ("worker747sitting747", "d29ya2VyNzQ3c2l0dGluZzc0Nw"),
    ("kernel747sitting747", "a2VybmVsNzQ3c2l0dGluZzc0Nw"),
    ("kernel747agent747", "a2VybmVsNzQ3YWdlbnQ3NDc"),
    ("kernel747angle747", "a2VybmVsNzQ3YW5nbGU3NDc"),
    ("kernel747universe747", "a2VybmVsNzQ3dW5pdmVyc2U3NDc"),
    ("signal747universe747", "c2lnbmFsNzQ3dW5pdmVyc2U3NDc"),
    ("signal747memory747", "c2lnbmFsNzQ3bWVtb3J5NzQ3"),
    ("signal747stream747", "c2lnbmFsNzQ3c3RyZWFtNzQ3"),
    ("signal747context747", "c2lnbmFsNzQ3Y29udGV4dDc0Nw"),
    ("packet747context747", "cGFja2V0NzQ3Y29udGV4dDc0Nw"),
    ("packet747knowledge747", "cGFja2V0NzQ3a25vd2xlZGdlNzQ3"),
    ("packet747vector747", "cGFja2V0NzQ3dmVjdG9yNzQ3"),
    ("packet747processor747", "cGFja2V0NzQ3cHJvY2Vzc29yNzQ3"),
    ("router747processor747", "cm91dGVyNzQ3cHJvY2Vzc29yNzQ3"),
    ("router747reasoning747", "cm91dGVyNzQ3cmVhc29uaW5nNzQ3"),
    ("router747machine747", "cm91dGVyNzQ3bWFjaGluZTc0Nw"),
    ("router747learning747", "cm91dGVyNzQ3bGVhcm5pbmc3NDc"),
    ("cluster747learning747", "Y2x1c3Rlcjc0N2xlYXJuaW5nNzQ3"),
    ("cluster747model747", "Y2x1c3Rlcjc0N21vZGVsNzQ3"),
    ("cluster747token747", "Y2x1c3Rlcjc0N3Rva2VuNzQ3"),
    ("cluster747prompt747", "Y2x1c3Rlcjc0N3Byb21wdDc0Nw"),
    ("mirror747prompt747", "bWlycm9yNzQ3cHJvbXB0NzQ3"),
    ("mirror747session747", "bWlycm9yNzQ3c2Vzc2lvbjc0Nw"),
    ("mirror747library747", "bWlycm9yNzQ3bGlicmFyeTc0Nw"),
    ("mirror747service747", "bWlycm9yNzQ3c2VydmljZTc0Nw"),
    ("filter747service747", "ZmlsdGVyNzQ3c2VydmljZTc0Nw"),
    ("filter747gateway747", "ZmlsdGVyNzQ3Z2F0ZXdheTc0Nw"),
    ("filter747storage747", "ZmlsdGVyNzQ3c3RvcmFnZTc0Nw"),
    ("filter747network747", "ZmlsdGVyNzQ3bmV0d29yazc0Nw"),
    ("ranking747network747", "cmFua2luZzc0N25ldHdvcms3NDc"),
    ("ranking747latency747", "cmFua2luZzc0N2xhdGVuY3k3NDc"),
    ("ranking747buffer747", "cmFua2luZzc0N2J1ZmZlcjc0Nw"),
    ("ranking747queue747", "cmFua2luZzc0N3F1ZXVlNzQ3"),
    ("encoding747queue747", "ZW5jb2Rpbmc3NDdxdWV1ZTc0Nw"),
    ("encoding747worker747", "ZW5jb2Rpbmc3NDd3b3JrZXI3NDc"),
    ("encoding747kernel747", "ZW5jb2Rpbmc3NDdrZXJuZWw3NDc"),
    ("encoding747signal747", "ZW5jb2Rpbmc3NDdzaWduYWw3NDc"),
    ("mapping747signal747", "bWFwcGluZzc0N3NpZ25hbDc0Nw"),
    ("mapping747packet747", "bWFwcGluZzc0N3BhY2tldDc0Nw"),
    ("mapping747router747", "bWFwcGluZzc0N3JvdXRlcjc0Nw"),
    ("mapping747cluster747", "bWFwcGluZzc0N2NsdXN0ZXI3NDc"),
    ("record747cluster747", "cmVjb3JkNzQ3Y2x1c3Rlcjc0Nw"),
    ("record747mirror747", "cmVjb3JkNzQ3bWlycm9yNzQ3"),
    ("record747filter747", "cmVjb3JkNzQ3ZmlsdGVyNzQ3"),
    ("record747ranking747", "cmVjb3JkNzQ3cmFua2luZzc0Nw"),
    ("candle747ranking747", "Y2FuZGxlNzQ3cmFua2luZzc0Nw"),
    ("candle747encoding747", "Y2FuZGxlNzQ3ZW5jb2Rpbmc3NDc"),
    ("candle747mapping747", "Y2FuZGxlNzQ3bWFwcGluZzc0Nw"),
    ("candle747record747", "Y2FuZGxlNzQ3cmVjb3JkNzQ3"),
    ("thread747record747", "dGhyZWFkNzQ3cmVjb3JkNzQ3"),
    ("thread747candle747", "dGhyZWFkNzQ3Y2FuZGxlNzQ3"),
    ("thread747thread747", "dGhyZWFkNzQ3dGhyZWFkNzQ3"),
    ("thread747kitten747", "dGhyZWFkNzQ3a2l0dGVuNzQ3"),
    (
        "round 747: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNzQ3OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 747: agentuniverse is a framework for multi agents",
        "cm91bmQgNzQ3OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 747: knowledge stored as vectors enables retrieval",
        "cm91bmQgNzQ3OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 747: the processor reads the record then stops",
        "cm91bmQgNzQ3OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 747: a worker pulls the next task from the queue",
        "cm91bmQgNzQ3OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 747: signals travel through the network layer",
        "cm91bmQgNzQ3OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 747: the gateway routes each request by policy",
        "cm91bmQgNzQ3OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 747: memory grows until the buffer is full",
        "cm91bmQgNzQ3OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 747: the cluster mirrors every packet twice",
        "cm91bmQgNzQ3OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 747: ranking uses tokens learned from the corpus",
        "cm91bmQgNzQ3OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 747: a long session ends when the candle dies",
        "cm91bmQgNzQ3OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 747: encode the prompt then map the result",
        "cm91bmQgNzQ3OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 747: the kernel wakes the worker at dawn",
        "cm91bmQgNzQ3OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 747: service latency drops after the patch",
        "cm91bmQgNzQ3OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 747: the library caches every vector it sees",
        "cm91bmQgNzQ3OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 747: agents argue then the debate resolves",
        "cm91bmQgNzQ3OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 747: the filter keeps only strong matches",
        "cm91bmQgNzQ3OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 747: the model answers with a short reply",
        "cm91bmQgNzQ3OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 747: the recorder stores the reasoning trace",
        "cm91bmQgNzQ3OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 747: the angel watches the processor run",
        "cm91bmQgNzQ3OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 747: angle of the vector decides the match",
        "cm91bmQgNzQ3OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 747: the candle burns twice as long at night",
        "cm91bmQgNzQ3OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 747: a mirror of the universe in one line",
        "cm91bmQgNzQ3OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 747: the queue drains before the storm", "cm91bmQgNzQ3OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
