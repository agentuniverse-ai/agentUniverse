"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten113kitten113", "a2l0dGVuMTEza2l0dGVuMTEz"),
    ("kitten113sitting113", "a2l0dGVuMTEzc2l0dGluZzExMw"),
    ("kitten113agent113", "a2l0dGVuMTEzYWdlbnQxMTM"),
    ("kitten113angle113", "a2l0dGVuMTEzYW5nbGUxMTM"),
    ("sitting113angle113", "c2l0dGluZzExM2FuZ2xlMTEz"),
    ("sitting113universe113", "c2l0dGluZzExM3VuaXZlcnNlMTEz"),
    ("sitting113memory113", "c2l0dGluZzExM21lbW9yeTExMw"),
    ("sitting113stream113", "c2l0dGluZzExM3N0cmVhbTExMw"),
    ("agent113stream113", "YWdlbnQxMTNzdHJlYW0xMTM"),
    ("agent113context113", "YWdlbnQxMTNjb250ZXh0MTEz"),
    ("agent113knowledge113", "YWdlbnQxMTNrbm93bGVkZ2UxMTM"),
    ("agent113vector113", "YWdlbnQxMTN2ZWN0b3IxMTM"),
    ("angle113vector113", "YW5nbGUxMTN2ZWN0b3IxMTM"),
    ("angle113processor113", "YW5nbGUxMTNwcm9jZXNzb3IxMTM"),
    ("angle113reasoning113", "YW5nbGUxMTNyZWFzb25pbmcxMTM"),
    ("angle113machine113", "YW5nbGUxMTNtYWNoaW5lMTEz"),
    ("universe113machine113", "dW5pdmVyc2UxMTNtYWNoaW5lMTEz"),
    ("universe113learning113", "dW5pdmVyc2UxMTNsZWFybmluZzExMw"),
    ("universe113model113", "dW5pdmVyc2UxMTNtb2RlbDExMw"),
    ("universe113token113", "dW5pdmVyc2UxMTN0b2tlbjExMw"),
    ("memory113token113", "bWVtb3J5MTEzdG9rZW4xMTM"),
    ("memory113prompt113", "bWVtb3J5MTEzcHJvbXB0MTEz"),
    ("memory113session113", "bWVtb3J5MTEzc2Vzc2lvbjExMw"),
    ("memory113library113", "bWVtb3J5MTEzbGlicmFyeTExMw"),
    ("stream113library113", "c3RyZWFtMTEzbGlicmFyeTExMw"),
    ("stream113service113", "c3RyZWFtMTEzc2VydmljZTExMw"),
    ("stream113gateway113", "c3RyZWFtMTEzZ2F0ZXdheTExMw"),
    ("stream113storage113", "c3RyZWFtMTEzc3RvcmFnZTExMw"),
    ("context113storage113", "Y29udGV4dDExM3N0b3JhZ2UxMTM"),
    ("context113network113", "Y29udGV4dDExM25ldHdvcmsxMTM"),
    ("context113latency113", "Y29udGV4dDExM2xhdGVuY3kxMTM"),
    ("context113buffer113", "Y29udGV4dDExM2J1ZmZlcjExMw"),
    ("knowledge113buffer113", "a25vd2xlZGdlMTEzYnVmZmVyMTEz"),
    ("knowledge113queue113", "a25vd2xlZGdlMTEzcXVldWUxMTM"),
    ("knowledge113worker113", "a25vd2xlZGdlMTEzd29ya2VyMTEz"),
    ("knowledge113kernel113", "a25vd2xlZGdlMTEza2VybmVsMTEz"),
    ("vector113kernel113", "dmVjdG9yMTEza2VybmVsMTEz"),
    ("vector113signal113", "dmVjdG9yMTEzc2lnbmFsMTEz"),
    ("vector113packet113", "dmVjdG9yMTEzcGFja2V0MTEz"),
    ("vector113router113", "dmVjdG9yMTEzcm91dGVyMTEz"),
    ("processor113router113", "cHJvY2Vzc29yMTEzcm91dGVyMTEz"),
    ("processor113cluster113", "cHJvY2Vzc29yMTEzY2x1c3RlcjExMw"),
    ("processor113mirror113", "cHJvY2Vzc29yMTEzbWlycm9yMTEz"),
    ("processor113filter113", "cHJvY2Vzc29yMTEzZmlsdGVyMTEz"),
    ("reasoning113filter113", "cmVhc29uaW5nMTEzZmlsdGVyMTEz"),
    ("reasoning113ranking113", "cmVhc29uaW5nMTEzcmFua2luZzExMw"),
    ("reasoning113encoding113", "cmVhc29uaW5nMTEzZW5jb2RpbmcxMTM"),
    ("reasoning113mapping113", "cmVhc29uaW5nMTEzbWFwcGluZzExMw"),
    ("machine113mapping113", "bWFjaGluZTExM21hcHBpbmcxMTM"),
    ("machine113record113", "bWFjaGluZTExM3JlY29yZDExMw"),
    ("machine113candle113", "bWFjaGluZTExM2NhbmRsZTExMw"),
    ("machine113thread113", "bWFjaGluZTExM3RocmVhZDExMw"),
    ("learning113thread113", "bGVhcm5pbmcxMTN0aHJlYWQxMTM"),
    ("learning113kitten113", "bGVhcm5pbmcxMTNraXR0ZW4xMTM"),
    ("learning113sitting113", "bGVhcm5pbmcxMTNzaXR0aW5nMTEz"),
    ("learning113agent113", "bGVhcm5pbmcxMTNhZ2VudDExMw"),
    ("model113agent113", "bW9kZWwxMTNhZ2VudDExMw"),
    ("model113angle113", "bW9kZWwxMTNhbmdsZTExMw"),
    ("model113universe113", "bW9kZWwxMTN1bml2ZXJzZTExMw"),
    ("model113memory113", "bW9kZWwxMTNtZW1vcnkxMTM"),
    ("token113memory113", "dG9rZW4xMTNtZW1vcnkxMTM"),
    ("token113stream113", "dG9rZW4xMTNzdHJlYW0xMTM"),
    ("token113context113", "dG9rZW4xMTNjb250ZXh0MTEz"),
    ("token113knowledge113", "dG9rZW4xMTNrbm93bGVkZ2UxMTM"),
    ("prompt113knowledge113", "cHJvbXB0MTEza25vd2xlZGdlMTEz"),
    ("prompt113vector113", "cHJvbXB0MTEzdmVjdG9yMTEz"),
    ("prompt113processor113", "cHJvbXB0MTEzcHJvY2Vzc29yMTEz"),
    ("prompt113reasoning113", "cHJvbXB0MTEzcmVhc29uaW5nMTEz"),
    ("session113reasoning113", "c2Vzc2lvbjExM3JlYXNvbmluZzExMw"),
    ("session113machine113", "c2Vzc2lvbjExM21hY2hpbmUxMTM"),
    ("session113learning113", "c2Vzc2lvbjExM2xlYXJuaW5nMTEz"),
    ("session113model113", "c2Vzc2lvbjExM21vZGVsMTEz"),
    ("library113model113", "bGlicmFyeTExM21vZGVsMTEz"),
    ("library113token113", "bGlicmFyeTExM3Rva2VuMTEz"),
    ("library113prompt113", "bGlicmFyeTExM3Byb21wdDExMw"),
    ("library113session113", "bGlicmFyeTExM3Nlc3Npb24xMTM"),
    ("service113session113", "c2VydmljZTExM3Nlc3Npb24xMTM"),
    ("service113library113", "c2VydmljZTExM2xpYnJhcnkxMTM"),
    ("service113service113", "c2VydmljZTExM3NlcnZpY2UxMTM"),
    ("service113gateway113", "c2VydmljZTExM2dhdGV3YXkxMTM"),
    ("gateway113gateway113", "Z2F0ZXdheTExM2dhdGV3YXkxMTM"),
    ("gateway113storage113", "Z2F0ZXdheTExM3N0b3JhZ2UxMTM"),
    ("gateway113network113", "Z2F0ZXdheTExM25ldHdvcmsxMTM"),
    ("gateway113latency113", "Z2F0ZXdheTExM2xhdGVuY3kxMTM"),
    ("storage113latency113", "c3RvcmFnZTExM2xhdGVuY3kxMTM"),
    ("storage113buffer113", "c3RvcmFnZTExM2J1ZmZlcjExMw"),
    ("storage113queue113", "c3RvcmFnZTExM3F1ZXVlMTEz"),
    ("storage113worker113", "c3RvcmFnZTExM3dvcmtlcjExMw"),
    ("network113worker113", "bmV0d29yazExM3dvcmtlcjExMw"),
    ("network113kernel113", "bmV0d29yazExM2tlcm5lbDExMw"),
    ("network113signal113", "bmV0d29yazExM3NpZ25hbDExMw"),
    ("network113packet113", "bmV0d29yazExM3BhY2tldDExMw"),
    ("latency113packet113", "bGF0ZW5jeTExM3BhY2tldDExMw"),
    ("latency113router113", "bGF0ZW5jeTExM3JvdXRlcjExMw"),
    ("latency113cluster113", "bGF0ZW5jeTExM2NsdXN0ZXIxMTM"),
    ("latency113mirror113", "bGF0ZW5jeTExM21pcnJvcjExMw"),
    ("buffer113mirror113", "YnVmZmVyMTEzbWlycm9yMTEz"),
    ("buffer113filter113", "YnVmZmVyMTEzZmlsdGVyMTEz"),
    ("buffer113ranking113", "YnVmZmVyMTEzcmFua2luZzExMw"),
    ("buffer113encoding113", "YnVmZmVyMTEzZW5jb2RpbmcxMTM"),
    ("queue113encoding113", "cXVldWUxMTNlbmNvZGluZzExMw"),
    ("queue113mapping113", "cXVldWUxMTNtYXBwaW5nMTEz"),
    ("queue113record113", "cXVldWUxMTNyZWNvcmQxMTM"),
    ("queue113candle113", "cXVldWUxMTNjYW5kbGUxMTM"),
    ("worker113candle113", "d29ya2VyMTEzY2FuZGxlMTEz"),
    ("worker113thread113", "d29ya2VyMTEzdGhyZWFkMTEz"),
    ("worker113kitten113", "d29ya2VyMTEza2l0dGVuMTEz"),
    ("worker113sitting113", "d29ya2VyMTEzc2l0dGluZzExMw"),
    ("kernel113sitting113", "a2VybmVsMTEzc2l0dGluZzExMw"),
    ("kernel113agent113", "a2VybmVsMTEzYWdlbnQxMTM"),
    ("kernel113angle113", "a2VybmVsMTEzYW5nbGUxMTM"),
    ("kernel113universe113", "a2VybmVsMTEzdW5pdmVyc2UxMTM"),
    ("signal113universe113", "c2lnbmFsMTEzdW5pdmVyc2UxMTM"),
    ("signal113memory113", "c2lnbmFsMTEzbWVtb3J5MTEz"),
    ("signal113stream113", "c2lnbmFsMTEzc3RyZWFtMTEz"),
    ("signal113context113", "c2lnbmFsMTEzY29udGV4dDExMw"),
    ("packet113context113", "cGFja2V0MTEzY29udGV4dDExMw"),
    ("packet113knowledge113", "cGFja2V0MTEza25vd2xlZGdlMTEz"),
    ("packet113vector113", "cGFja2V0MTEzdmVjdG9yMTEz"),
    ("packet113processor113", "cGFja2V0MTEzcHJvY2Vzc29yMTEz"),
    ("router113processor113", "cm91dGVyMTEzcHJvY2Vzc29yMTEz"),
    ("router113reasoning113", "cm91dGVyMTEzcmVhc29uaW5nMTEz"),
    ("router113machine113", "cm91dGVyMTEzbWFjaGluZTExMw"),
    ("router113learning113", "cm91dGVyMTEzbGVhcm5pbmcxMTM"),
    ("cluster113learning113", "Y2x1c3RlcjExM2xlYXJuaW5nMTEz"),
    ("cluster113model113", "Y2x1c3RlcjExM21vZGVsMTEz"),
    ("cluster113token113", "Y2x1c3RlcjExM3Rva2VuMTEz"),
    ("cluster113prompt113", "Y2x1c3RlcjExM3Byb21wdDExMw"),
    ("mirror113prompt113", "bWlycm9yMTEzcHJvbXB0MTEz"),
    ("mirror113session113", "bWlycm9yMTEzc2Vzc2lvbjExMw"),
    ("mirror113library113", "bWlycm9yMTEzbGlicmFyeTExMw"),
    ("mirror113service113", "bWlycm9yMTEzc2VydmljZTExMw"),
    ("filter113service113", "ZmlsdGVyMTEzc2VydmljZTExMw"),
    ("filter113gateway113", "ZmlsdGVyMTEzZ2F0ZXdheTExMw"),
    ("filter113storage113", "ZmlsdGVyMTEzc3RvcmFnZTExMw"),
    ("filter113network113", "ZmlsdGVyMTEzbmV0d29yazExMw"),
    ("ranking113network113", "cmFua2luZzExM25ldHdvcmsxMTM"),
    ("ranking113latency113", "cmFua2luZzExM2xhdGVuY3kxMTM"),
    ("ranking113buffer113", "cmFua2luZzExM2J1ZmZlcjExMw"),
    ("ranking113queue113", "cmFua2luZzExM3F1ZXVlMTEz"),
    ("encoding113queue113", "ZW5jb2RpbmcxMTNxdWV1ZTExMw"),
    ("encoding113worker113", "ZW5jb2RpbmcxMTN3b3JrZXIxMTM"),
    ("encoding113kernel113", "ZW5jb2RpbmcxMTNrZXJuZWwxMTM"),
    ("encoding113signal113", "ZW5jb2RpbmcxMTNzaWduYWwxMTM"),
    ("mapping113signal113", "bWFwcGluZzExM3NpZ25hbDExMw"),
    ("mapping113packet113", "bWFwcGluZzExM3BhY2tldDExMw"),
    ("mapping113router113", "bWFwcGluZzExM3JvdXRlcjExMw"),
    ("mapping113cluster113", "bWFwcGluZzExM2NsdXN0ZXIxMTM"),
    ("record113cluster113", "cmVjb3JkMTEzY2x1c3RlcjExMw"),
    ("record113mirror113", "cmVjb3JkMTEzbWlycm9yMTEz"),
    ("record113filter113", "cmVjb3JkMTEzZmlsdGVyMTEz"),
    ("record113ranking113", "cmVjb3JkMTEzcmFua2luZzExMw"),
    ("candle113ranking113", "Y2FuZGxlMTEzcmFua2luZzExMw"),
    ("candle113encoding113", "Y2FuZGxlMTEzZW5jb2RpbmcxMTM"),
    ("candle113mapping113", "Y2FuZGxlMTEzbWFwcGluZzExMw"),
    ("candle113record113", "Y2FuZGxlMTEzcmVjb3JkMTEz"),
    ("thread113record113", "dGhyZWFkMTEzcmVjb3JkMTEz"),
    ("thread113candle113", "dGhyZWFkMTEzY2FuZGxlMTEz"),
    ("thread113thread113", "dGhyZWFkMTEzdGhyZWFkMTEz"),
    ("thread113kitten113", "dGhyZWFkMTEza2l0dGVuMTEz"),
    (
        "round 113: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTEzOiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 113: agentuniverse is a framework for multi agents",
        "cm91bmQgMTEzOiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 113: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTEzOiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 113: the processor reads the record then stops",
        "cm91bmQgMTEzOiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 113: a worker pulls the next task from the queue",
        "cm91bmQgMTEzOiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 113: signals travel through the network layer",
        "cm91bmQgMTEzOiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 113: the gateway routes each request by policy",
        "cm91bmQgMTEzOiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 113: memory grows until the buffer is full",
        "cm91bmQgMTEzOiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 113: the cluster mirrors every packet twice",
        "cm91bmQgMTEzOiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 113: ranking uses tokens learned from the corpus",
        "cm91bmQgMTEzOiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 113: a long session ends when the candle dies",
        "cm91bmQgMTEzOiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 113: encode the prompt then map the result",
        "cm91bmQgMTEzOiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 113: the kernel wakes the worker at dawn",
        "cm91bmQgMTEzOiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 113: service latency drops after the patch",
        "cm91bmQgMTEzOiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 113: the library caches every vector it sees",
        "cm91bmQgMTEzOiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 113: agents argue then the debate resolves",
        "cm91bmQgMTEzOiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 113: the filter keeps only strong matches",
        "cm91bmQgMTEzOiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 113: the model answers with a short reply",
        "cm91bmQgMTEzOiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 113: the recorder stores the reasoning trace",
        "cm91bmQgMTEzOiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 113: the angel watches the processor run",
        "cm91bmQgMTEzOiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 113: angle of the vector decides the match",
        "cm91bmQgMTEzOiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 113: the candle burns twice as long at night",
        "cm91bmQgMTEzOiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 113: a mirror of the universe in one line",
        "cm91bmQgMTEzOiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 113: the queue drains before the storm", "cm91bmQgMTEzOiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
