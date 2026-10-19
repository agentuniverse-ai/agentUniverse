"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten733kitten733", "a2l0dGVuNzMza2l0dGVuNzMz"),
    ("kitten733sitting733", "a2l0dGVuNzMzc2l0dGluZzczMw"),
    ("kitten733agent733", "a2l0dGVuNzMzYWdlbnQ3MzM"),
    ("kitten733angle733", "a2l0dGVuNzMzYW5nbGU3MzM"),
    ("sitting733angle733", "c2l0dGluZzczM2FuZ2xlNzMz"),
    ("sitting733universe733", "c2l0dGluZzczM3VuaXZlcnNlNzMz"),
    ("sitting733memory733", "c2l0dGluZzczM21lbW9yeTczMw"),
    ("sitting733stream733", "c2l0dGluZzczM3N0cmVhbTczMw"),
    ("agent733stream733", "YWdlbnQ3MzNzdHJlYW03MzM"),
    ("agent733context733", "YWdlbnQ3MzNjb250ZXh0NzMz"),
    ("agent733knowledge733", "YWdlbnQ3MzNrbm93bGVkZ2U3MzM"),
    ("agent733vector733", "YWdlbnQ3MzN2ZWN0b3I3MzM"),
    ("angle733vector733", "YW5nbGU3MzN2ZWN0b3I3MzM"),
    ("angle733processor733", "YW5nbGU3MzNwcm9jZXNzb3I3MzM"),
    ("angle733reasoning733", "YW5nbGU3MzNyZWFzb25pbmc3MzM"),
    ("angle733machine733", "YW5nbGU3MzNtYWNoaW5lNzMz"),
    ("universe733machine733", "dW5pdmVyc2U3MzNtYWNoaW5lNzMz"),
    ("universe733learning733", "dW5pdmVyc2U3MzNsZWFybmluZzczMw"),
    ("universe733model733", "dW5pdmVyc2U3MzNtb2RlbDczMw"),
    ("universe733token733", "dW5pdmVyc2U3MzN0b2tlbjczMw"),
    ("memory733token733", "bWVtb3J5NzMzdG9rZW43MzM"),
    ("memory733prompt733", "bWVtb3J5NzMzcHJvbXB0NzMz"),
    ("memory733session733", "bWVtb3J5NzMzc2Vzc2lvbjczMw"),
    ("memory733library733", "bWVtb3J5NzMzbGlicmFyeTczMw"),
    ("stream733library733", "c3RyZWFtNzMzbGlicmFyeTczMw"),
    ("stream733service733", "c3RyZWFtNzMzc2VydmljZTczMw"),
    ("stream733gateway733", "c3RyZWFtNzMzZ2F0ZXdheTczMw"),
    ("stream733storage733", "c3RyZWFtNzMzc3RvcmFnZTczMw"),
    ("context733storage733", "Y29udGV4dDczM3N0b3JhZ2U3MzM"),
    ("context733network733", "Y29udGV4dDczM25ldHdvcms3MzM"),
    ("context733latency733", "Y29udGV4dDczM2xhdGVuY3k3MzM"),
    ("context733buffer733", "Y29udGV4dDczM2J1ZmZlcjczMw"),
    ("knowledge733buffer733", "a25vd2xlZGdlNzMzYnVmZmVyNzMz"),
    ("knowledge733queue733", "a25vd2xlZGdlNzMzcXVldWU3MzM"),
    ("knowledge733worker733", "a25vd2xlZGdlNzMzd29ya2VyNzMz"),
    ("knowledge733kernel733", "a25vd2xlZGdlNzMza2VybmVsNzMz"),
    ("vector733kernel733", "dmVjdG9yNzMza2VybmVsNzMz"),
    ("vector733signal733", "dmVjdG9yNzMzc2lnbmFsNzMz"),
    ("vector733packet733", "dmVjdG9yNzMzcGFja2V0NzMz"),
    ("vector733router733", "dmVjdG9yNzMzcm91dGVyNzMz"),
    ("processor733router733", "cHJvY2Vzc29yNzMzcm91dGVyNzMz"),
    ("processor733cluster733", "cHJvY2Vzc29yNzMzY2x1c3RlcjczMw"),
    ("processor733mirror733", "cHJvY2Vzc29yNzMzbWlycm9yNzMz"),
    ("processor733filter733", "cHJvY2Vzc29yNzMzZmlsdGVyNzMz"),
    ("reasoning733filter733", "cmVhc29uaW5nNzMzZmlsdGVyNzMz"),
    ("reasoning733ranking733", "cmVhc29uaW5nNzMzcmFua2luZzczMw"),
    ("reasoning733encoding733", "cmVhc29uaW5nNzMzZW5jb2Rpbmc3MzM"),
    ("reasoning733mapping733", "cmVhc29uaW5nNzMzbWFwcGluZzczMw"),
    ("machine733mapping733", "bWFjaGluZTczM21hcHBpbmc3MzM"),
    ("machine733record733", "bWFjaGluZTczM3JlY29yZDczMw"),
    ("machine733candle733", "bWFjaGluZTczM2NhbmRsZTczMw"),
    ("machine733thread733", "bWFjaGluZTczM3RocmVhZDczMw"),
    ("learning733thread733", "bGVhcm5pbmc3MzN0aHJlYWQ3MzM"),
    ("learning733kitten733", "bGVhcm5pbmc3MzNraXR0ZW43MzM"),
    ("learning733sitting733", "bGVhcm5pbmc3MzNzaXR0aW5nNzMz"),
    ("learning733agent733", "bGVhcm5pbmc3MzNhZ2VudDczMw"),
    ("model733agent733", "bW9kZWw3MzNhZ2VudDczMw"),
    ("model733angle733", "bW9kZWw3MzNhbmdsZTczMw"),
    ("model733universe733", "bW9kZWw3MzN1bml2ZXJzZTczMw"),
    ("model733memory733", "bW9kZWw3MzNtZW1vcnk3MzM"),
    ("token733memory733", "dG9rZW43MzNtZW1vcnk3MzM"),
    ("token733stream733", "dG9rZW43MzNzdHJlYW03MzM"),
    ("token733context733", "dG9rZW43MzNjb250ZXh0NzMz"),
    ("token733knowledge733", "dG9rZW43MzNrbm93bGVkZ2U3MzM"),
    ("prompt733knowledge733", "cHJvbXB0NzMza25vd2xlZGdlNzMz"),
    ("prompt733vector733", "cHJvbXB0NzMzdmVjdG9yNzMz"),
    ("prompt733processor733", "cHJvbXB0NzMzcHJvY2Vzc29yNzMz"),
    ("prompt733reasoning733", "cHJvbXB0NzMzcmVhc29uaW5nNzMz"),
    ("session733reasoning733", "c2Vzc2lvbjczM3JlYXNvbmluZzczMw"),
    ("session733machine733", "c2Vzc2lvbjczM21hY2hpbmU3MzM"),
    ("session733learning733", "c2Vzc2lvbjczM2xlYXJuaW5nNzMz"),
    ("session733model733", "c2Vzc2lvbjczM21vZGVsNzMz"),
    ("library733model733", "bGlicmFyeTczM21vZGVsNzMz"),
    ("library733token733", "bGlicmFyeTczM3Rva2VuNzMz"),
    ("library733prompt733", "bGlicmFyeTczM3Byb21wdDczMw"),
    ("library733session733", "bGlicmFyeTczM3Nlc3Npb243MzM"),
    ("service733session733", "c2VydmljZTczM3Nlc3Npb243MzM"),
    ("service733library733", "c2VydmljZTczM2xpYnJhcnk3MzM"),
    ("service733service733", "c2VydmljZTczM3NlcnZpY2U3MzM"),
    ("service733gateway733", "c2VydmljZTczM2dhdGV3YXk3MzM"),
    ("gateway733gateway733", "Z2F0ZXdheTczM2dhdGV3YXk3MzM"),
    ("gateway733storage733", "Z2F0ZXdheTczM3N0b3JhZ2U3MzM"),
    ("gateway733network733", "Z2F0ZXdheTczM25ldHdvcms3MzM"),
    ("gateway733latency733", "Z2F0ZXdheTczM2xhdGVuY3k3MzM"),
    ("storage733latency733", "c3RvcmFnZTczM2xhdGVuY3k3MzM"),
    ("storage733buffer733", "c3RvcmFnZTczM2J1ZmZlcjczMw"),
    ("storage733queue733", "c3RvcmFnZTczM3F1ZXVlNzMz"),
    ("storage733worker733", "c3RvcmFnZTczM3dvcmtlcjczMw"),
    ("network733worker733", "bmV0d29yazczM3dvcmtlcjczMw"),
    ("network733kernel733", "bmV0d29yazczM2tlcm5lbDczMw"),
    ("network733signal733", "bmV0d29yazczM3NpZ25hbDczMw"),
    ("network733packet733", "bmV0d29yazczM3BhY2tldDczMw"),
    ("latency733packet733", "bGF0ZW5jeTczM3BhY2tldDczMw"),
    ("latency733router733", "bGF0ZW5jeTczM3JvdXRlcjczMw"),
    ("latency733cluster733", "bGF0ZW5jeTczM2NsdXN0ZXI3MzM"),
    ("latency733mirror733", "bGF0ZW5jeTczM21pcnJvcjczMw"),
    ("buffer733mirror733", "YnVmZmVyNzMzbWlycm9yNzMz"),
    ("buffer733filter733", "YnVmZmVyNzMzZmlsdGVyNzMz"),
    ("buffer733ranking733", "YnVmZmVyNzMzcmFua2luZzczMw"),
    ("buffer733encoding733", "YnVmZmVyNzMzZW5jb2Rpbmc3MzM"),
    ("queue733encoding733", "cXVldWU3MzNlbmNvZGluZzczMw"),
    ("queue733mapping733", "cXVldWU3MzNtYXBwaW5nNzMz"),
    ("queue733record733", "cXVldWU3MzNyZWNvcmQ3MzM"),
    ("queue733candle733", "cXVldWU3MzNjYW5kbGU3MzM"),
    ("worker733candle733", "d29ya2VyNzMzY2FuZGxlNzMz"),
    ("worker733thread733", "d29ya2VyNzMzdGhyZWFkNzMz"),
    ("worker733kitten733", "d29ya2VyNzMza2l0dGVuNzMz"),
    ("worker733sitting733", "d29ya2VyNzMzc2l0dGluZzczMw"),
    ("kernel733sitting733", "a2VybmVsNzMzc2l0dGluZzczMw"),
    ("kernel733agent733", "a2VybmVsNzMzYWdlbnQ3MzM"),
    ("kernel733angle733", "a2VybmVsNzMzYW5nbGU3MzM"),
    ("kernel733universe733", "a2VybmVsNzMzdW5pdmVyc2U3MzM"),
    ("signal733universe733", "c2lnbmFsNzMzdW5pdmVyc2U3MzM"),
    ("signal733memory733", "c2lnbmFsNzMzbWVtb3J5NzMz"),
    ("signal733stream733", "c2lnbmFsNzMzc3RyZWFtNzMz"),
    ("signal733context733", "c2lnbmFsNzMzY29udGV4dDczMw"),
    ("packet733context733", "cGFja2V0NzMzY29udGV4dDczMw"),
    ("packet733knowledge733", "cGFja2V0NzMza25vd2xlZGdlNzMz"),
    ("packet733vector733", "cGFja2V0NzMzdmVjdG9yNzMz"),
    ("packet733processor733", "cGFja2V0NzMzcHJvY2Vzc29yNzMz"),
    ("router733processor733", "cm91dGVyNzMzcHJvY2Vzc29yNzMz"),
    ("router733reasoning733", "cm91dGVyNzMzcmVhc29uaW5nNzMz"),
    ("router733machine733", "cm91dGVyNzMzbWFjaGluZTczMw"),
    ("router733learning733", "cm91dGVyNzMzbGVhcm5pbmc3MzM"),
    ("cluster733learning733", "Y2x1c3RlcjczM2xlYXJuaW5nNzMz"),
    ("cluster733model733", "Y2x1c3RlcjczM21vZGVsNzMz"),
    ("cluster733token733", "Y2x1c3RlcjczM3Rva2VuNzMz"),
    ("cluster733prompt733", "Y2x1c3RlcjczM3Byb21wdDczMw"),
    ("mirror733prompt733", "bWlycm9yNzMzcHJvbXB0NzMz"),
    ("mirror733session733", "bWlycm9yNzMzc2Vzc2lvbjczMw"),
    ("mirror733library733", "bWlycm9yNzMzbGlicmFyeTczMw"),
    ("mirror733service733", "bWlycm9yNzMzc2VydmljZTczMw"),
    ("filter733service733", "ZmlsdGVyNzMzc2VydmljZTczMw"),
    ("filter733gateway733", "ZmlsdGVyNzMzZ2F0ZXdheTczMw"),
    ("filter733storage733", "ZmlsdGVyNzMzc3RvcmFnZTczMw"),
    ("filter733network733", "ZmlsdGVyNzMzbmV0d29yazczMw"),
    ("ranking733network733", "cmFua2luZzczM25ldHdvcms3MzM"),
    ("ranking733latency733", "cmFua2luZzczM2xhdGVuY3k3MzM"),
    ("ranking733buffer733", "cmFua2luZzczM2J1ZmZlcjczMw"),
    ("ranking733queue733", "cmFua2luZzczM3F1ZXVlNzMz"),
    ("encoding733queue733", "ZW5jb2Rpbmc3MzNxdWV1ZTczMw"),
    ("encoding733worker733", "ZW5jb2Rpbmc3MzN3b3JrZXI3MzM"),
    ("encoding733kernel733", "ZW5jb2Rpbmc3MzNrZXJuZWw3MzM"),
    ("encoding733signal733", "ZW5jb2Rpbmc3MzNzaWduYWw3MzM"),
    ("mapping733signal733", "bWFwcGluZzczM3NpZ25hbDczMw"),
    ("mapping733packet733", "bWFwcGluZzczM3BhY2tldDczMw"),
    ("mapping733router733", "bWFwcGluZzczM3JvdXRlcjczMw"),
    ("mapping733cluster733", "bWFwcGluZzczM2NsdXN0ZXI3MzM"),
    ("record733cluster733", "cmVjb3JkNzMzY2x1c3RlcjczMw"),
    ("record733mirror733", "cmVjb3JkNzMzbWlycm9yNzMz"),
    ("record733filter733", "cmVjb3JkNzMzZmlsdGVyNzMz"),
    ("record733ranking733", "cmVjb3JkNzMzcmFua2luZzczMw"),
    ("candle733ranking733", "Y2FuZGxlNzMzcmFua2luZzczMw"),
    ("candle733encoding733", "Y2FuZGxlNzMzZW5jb2Rpbmc3MzM"),
    ("candle733mapping733", "Y2FuZGxlNzMzbWFwcGluZzczMw"),
    ("candle733record733", "Y2FuZGxlNzMzcmVjb3JkNzMz"),
    ("thread733record733", "dGhyZWFkNzMzcmVjb3JkNzMz"),
    ("thread733candle733", "dGhyZWFkNzMzY2FuZGxlNzMz"),
    ("thread733thread733", "dGhyZWFkNzMzdGhyZWFkNzMz"),
    ("thread733kitten733", "dGhyZWFkNzMza2l0dGVuNzMz"),
    (
        "round 733: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNzMzOiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 733: agentuniverse is a framework for multi agents",
        "cm91bmQgNzMzOiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 733: knowledge stored as vectors enables retrieval",
        "cm91bmQgNzMzOiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 733: the processor reads the record then stops",
        "cm91bmQgNzMzOiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 733: a worker pulls the next task from the queue",
        "cm91bmQgNzMzOiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 733: signals travel through the network layer",
        "cm91bmQgNzMzOiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 733: the gateway routes each request by policy",
        "cm91bmQgNzMzOiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 733: memory grows until the buffer is full",
        "cm91bmQgNzMzOiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 733: the cluster mirrors every packet twice",
        "cm91bmQgNzMzOiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 733: ranking uses tokens learned from the corpus",
        "cm91bmQgNzMzOiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 733: a long session ends when the candle dies",
        "cm91bmQgNzMzOiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 733: encode the prompt then map the result",
        "cm91bmQgNzMzOiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 733: the kernel wakes the worker at dawn",
        "cm91bmQgNzMzOiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 733: service latency drops after the patch",
        "cm91bmQgNzMzOiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 733: the library caches every vector it sees",
        "cm91bmQgNzMzOiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 733: agents argue then the debate resolves",
        "cm91bmQgNzMzOiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 733: the filter keeps only strong matches",
        "cm91bmQgNzMzOiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 733: the model answers with a short reply",
        "cm91bmQgNzMzOiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 733: the recorder stores the reasoning trace",
        "cm91bmQgNzMzOiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 733: the angel watches the processor run",
        "cm91bmQgNzMzOiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 733: angle of the vector decides the match",
        "cm91bmQgNzMzOiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 733: the candle burns twice as long at night",
        "cm91bmQgNzMzOiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 733: a mirror of the universe in one line",
        "cm91bmQgNzMzOiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 733: the queue drains before the storm", "cm91bmQgNzMzOiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
