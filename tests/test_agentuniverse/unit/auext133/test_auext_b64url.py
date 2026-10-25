"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten133kitten133", "a2l0dGVuMTMza2l0dGVuMTMz"),
    ("kitten133sitting133", "a2l0dGVuMTMzc2l0dGluZzEzMw"),
    ("kitten133agent133", "a2l0dGVuMTMzYWdlbnQxMzM"),
    ("kitten133angle133", "a2l0dGVuMTMzYW5nbGUxMzM"),
    ("sitting133angle133", "c2l0dGluZzEzM2FuZ2xlMTMz"),
    ("sitting133universe133", "c2l0dGluZzEzM3VuaXZlcnNlMTMz"),
    ("sitting133memory133", "c2l0dGluZzEzM21lbW9yeTEzMw"),
    ("sitting133stream133", "c2l0dGluZzEzM3N0cmVhbTEzMw"),
    ("agent133stream133", "YWdlbnQxMzNzdHJlYW0xMzM"),
    ("agent133context133", "YWdlbnQxMzNjb250ZXh0MTMz"),
    ("agent133knowledge133", "YWdlbnQxMzNrbm93bGVkZ2UxMzM"),
    ("agent133vector133", "YWdlbnQxMzN2ZWN0b3IxMzM"),
    ("angle133vector133", "YW5nbGUxMzN2ZWN0b3IxMzM"),
    ("angle133processor133", "YW5nbGUxMzNwcm9jZXNzb3IxMzM"),
    ("angle133reasoning133", "YW5nbGUxMzNyZWFzb25pbmcxMzM"),
    ("angle133machine133", "YW5nbGUxMzNtYWNoaW5lMTMz"),
    ("universe133machine133", "dW5pdmVyc2UxMzNtYWNoaW5lMTMz"),
    ("universe133learning133", "dW5pdmVyc2UxMzNsZWFybmluZzEzMw"),
    ("universe133model133", "dW5pdmVyc2UxMzNtb2RlbDEzMw"),
    ("universe133token133", "dW5pdmVyc2UxMzN0b2tlbjEzMw"),
    ("memory133token133", "bWVtb3J5MTMzdG9rZW4xMzM"),
    ("memory133prompt133", "bWVtb3J5MTMzcHJvbXB0MTMz"),
    ("memory133session133", "bWVtb3J5MTMzc2Vzc2lvbjEzMw"),
    ("memory133library133", "bWVtb3J5MTMzbGlicmFyeTEzMw"),
    ("stream133library133", "c3RyZWFtMTMzbGlicmFyeTEzMw"),
    ("stream133service133", "c3RyZWFtMTMzc2VydmljZTEzMw"),
    ("stream133gateway133", "c3RyZWFtMTMzZ2F0ZXdheTEzMw"),
    ("stream133storage133", "c3RyZWFtMTMzc3RvcmFnZTEzMw"),
    ("context133storage133", "Y29udGV4dDEzM3N0b3JhZ2UxMzM"),
    ("context133network133", "Y29udGV4dDEzM25ldHdvcmsxMzM"),
    ("context133latency133", "Y29udGV4dDEzM2xhdGVuY3kxMzM"),
    ("context133buffer133", "Y29udGV4dDEzM2J1ZmZlcjEzMw"),
    ("knowledge133buffer133", "a25vd2xlZGdlMTMzYnVmZmVyMTMz"),
    ("knowledge133queue133", "a25vd2xlZGdlMTMzcXVldWUxMzM"),
    ("knowledge133worker133", "a25vd2xlZGdlMTMzd29ya2VyMTMz"),
    ("knowledge133kernel133", "a25vd2xlZGdlMTMza2VybmVsMTMz"),
    ("vector133kernel133", "dmVjdG9yMTMza2VybmVsMTMz"),
    ("vector133signal133", "dmVjdG9yMTMzc2lnbmFsMTMz"),
    ("vector133packet133", "dmVjdG9yMTMzcGFja2V0MTMz"),
    ("vector133router133", "dmVjdG9yMTMzcm91dGVyMTMz"),
    ("processor133router133", "cHJvY2Vzc29yMTMzcm91dGVyMTMz"),
    ("processor133cluster133", "cHJvY2Vzc29yMTMzY2x1c3RlcjEzMw"),
    ("processor133mirror133", "cHJvY2Vzc29yMTMzbWlycm9yMTMz"),
    ("processor133filter133", "cHJvY2Vzc29yMTMzZmlsdGVyMTMz"),
    ("reasoning133filter133", "cmVhc29uaW5nMTMzZmlsdGVyMTMz"),
    ("reasoning133ranking133", "cmVhc29uaW5nMTMzcmFua2luZzEzMw"),
    ("reasoning133encoding133", "cmVhc29uaW5nMTMzZW5jb2RpbmcxMzM"),
    ("reasoning133mapping133", "cmVhc29uaW5nMTMzbWFwcGluZzEzMw"),
    ("machine133mapping133", "bWFjaGluZTEzM21hcHBpbmcxMzM"),
    ("machine133record133", "bWFjaGluZTEzM3JlY29yZDEzMw"),
    ("machine133candle133", "bWFjaGluZTEzM2NhbmRsZTEzMw"),
    ("machine133thread133", "bWFjaGluZTEzM3RocmVhZDEzMw"),
    ("learning133thread133", "bGVhcm5pbmcxMzN0aHJlYWQxMzM"),
    ("learning133kitten133", "bGVhcm5pbmcxMzNraXR0ZW4xMzM"),
    ("learning133sitting133", "bGVhcm5pbmcxMzNzaXR0aW5nMTMz"),
    ("learning133agent133", "bGVhcm5pbmcxMzNhZ2VudDEzMw"),
    ("model133agent133", "bW9kZWwxMzNhZ2VudDEzMw"),
    ("model133angle133", "bW9kZWwxMzNhbmdsZTEzMw"),
    ("model133universe133", "bW9kZWwxMzN1bml2ZXJzZTEzMw"),
    ("model133memory133", "bW9kZWwxMzNtZW1vcnkxMzM"),
    ("token133memory133", "dG9rZW4xMzNtZW1vcnkxMzM"),
    ("token133stream133", "dG9rZW4xMzNzdHJlYW0xMzM"),
    ("token133context133", "dG9rZW4xMzNjb250ZXh0MTMz"),
    ("token133knowledge133", "dG9rZW4xMzNrbm93bGVkZ2UxMzM"),
    ("prompt133knowledge133", "cHJvbXB0MTMza25vd2xlZGdlMTMz"),
    ("prompt133vector133", "cHJvbXB0MTMzdmVjdG9yMTMz"),
    ("prompt133processor133", "cHJvbXB0MTMzcHJvY2Vzc29yMTMz"),
    ("prompt133reasoning133", "cHJvbXB0MTMzcmVhc29uaW5nMTMz"),
    ("session133reasoning133", "c2Vzc2lvbjEzM3JlYXNvbmluZzEzMw"),
    ("session133machine133", "c2Vzc2lvbjEzM21hY2hpbmUxMzM"),
    ("session133learning133", "c2Vzc2lvbjEzM2xlYXJuaW5nMTMz"),
    ("session133model133", "c2Vzc2lvbjEzM21vZGVsMTMz"),
    ("library133model133", "bGlicmFyeTEzM21vZGVsMTMz"),
    ("library133token133", "bGlicmFyeTEzM3Rva2VuMTMz"),
    ("library133prompt133", "bGlicmFyeTEzM3Byb21wdDEzMw"),
    ("library133session133", "bGlicmFyeTEzM3Nlc3Npb24xMzM"),
    ("service133session133", "c2VydmljZTEzM3Nlc3Npb24xMzM"),
    ("service133library133", "c2VydmljZTEzM2xpYnJhcnkxMzM"),
    ("service133service133", "c2VydmljZTEzM3NlcnZpY2UxMzM"),
    ("service133gateway133", "c2VydmljZTEzM2dhdGV3YXkxMzM"),
    ("gateway133gateway133", "Z2F0ZXdheTEzM2dhdGV3YXkxMzM"),
    ("gateway133storage133", "Z2F0ZXdheTEzM3N0b3JhZ2UxMzM"),
    ("gateway133network133", "Z2F0ZXdheTEzM25ldHdvcmsxMzM"),
    ("gateway133latency133", "Z2F0ZXdheTEzM2xhdGVuY3kxMzM"),
    ("storage133latency133", "c3RvcmFnZTEzM2xhdGVuY3kxMzM"),
    ("storage133buffer133", "c3RvcmFnZTEzM2J1ZmZlcjEzMw"),
    ("storage133queue133", "c3RvcmFnZTEzM3F1ZXVlMTMz"),
    ("storage133worker133", "c3RvcmFnZTEzM3dvcmtlcjEzMw"),
    ("network133worker133", "bmV0d29yazEzM3dvcmtlcjEzMw"),
    ("network133kernel133", "bmV0d29yazEzM2tlcm5lbDEzMw"),
    ("network133signal133", "bmV0d29yazEzM3NpZ25hbDEzMw"),
    ("network133packet133", "bmV0d29yazEzM3BhY2tldDEzMw"),
    ("latency133packet133", "bGF0ZW5jeTEzM3BhY2tldDEzMw"),
    ("latency133router133", "bGF0ZW5jeTEzM3JvdXRlcjEzMw"),
    ("latency133cluster133", "bGF0ZW5jeTEzM2NsdXN0ZXIxMzM"),
    ("latency133mirror133", "bGF0ZW5jeTEzM21pcnJvcjEzMw"),
    ("buffer133mirror133", "YnVmZmVyMTMzbWlycm9yMTMz"),
    ("buffer133filter133", "YnVmZmVyMTMzZmlsdGVyMTMz"),
    ("buffer133ranking133", "YnVmZmVyMTMzcmFua2luZzEzMw"),
    ("buffer133encoding133", "YnVmZmVyMTMzZW5jb2RpbmcxMzM"),
    ("queue133encoding133", "cXVldWUxMzNlbmNvZGluZzEzMw"),
    ("queue133mapping133", "cXVldWUxMzNtYXBwaW5nMTMz"),
    ("queue133record133", "cXVldWUxMzNyZWNvcmQxMzM"),
    ("queue133candle133", "cXVldWUxMzNjYW5kbGUxMzM"),
    ("worker133candle133", "d29ya2VyMTMzY2FuZGxlMTMz"),
    ("worker133thread133", "d29ya2VyMTMzdGhyZWFkMTMz"),
    ("worker133kitten133", "d29ya2VyMTMza2l0dGVuMTMz"),
    ("worker133sitting133", "d29ya2VyMTMzc2l0dGluZzEzMw"),
    ("kernel133sitting133", "a2VybmVsMTMzc2l0dGluZzEzMw"),
    ("kernel133agent133", "a2VybmVsMTMzYWdlbnQxMzM"),
    ("kernel133angle133", "a2VybmVsMTMzYW5nbGUxMzM"),
    ("kernel133universe133", "a2VybmVsMTMzdW5pdmVyc2UxMzM"),
    ("signal133universe133", "c2lnbmFsMTMzdW5pdmVyc2UxMzM"),
    ("signal133memory133", "c2lnbmFsMTMzbWVtb3J5MTMz"),
    ("signal133stream133", "c2lnbmFsMTMzc3RyZWFtMTMz"),
    ("signal133context133", "c2lnbmFsMTMzY29udGV4dDEzMw"),
    ("packet133context133", "cGFja2V0MTMzY29udGV4dDEzMw"),
    ("packet133knowledge133", "cGFja2V0MTMza25vd2xlZGdlMTMz"),
    ("packet133vector133", "cGFja2V0MTMzdmVjdG9yMTMz"),
    ("packet133processor133", "cGFja2V0MTMzcHJvY2Vzc29yMTMz"),
    ("router133processor133", "cm91dGVyMTMzcHJvY2Vzc29yMTMz"),
    ("router133reasoning133", "cm91dGVyMTMzcmVhc29uaW5nMTMz"),
    ("router133machine133", "cm91dGVyMTMzbWFjaGluZTEzMw"),
    ("router133learning133", "cm91dGVyMTMzbGVhcm5pbmcxMzM"),
    ("cluster133learning133", "Y2x1c3RlcjEzM2xlYXJuaW5nMTMz"),
    ("cluster133model133", "Y2x1c3RlcjEzM21vZGVsMTMz"),
    ("cluster133token133", "Y2x1c3RlcjEzM3Rva2VuMTMz"),
    ("cluster133prompt133", "Y2x1c3RlcjEzM3Byb21wdDEzMw"),
    ("mirror133prompt133", "bWlycm9yMTMzcHJvbXB0MTMz"),
    ("mirror133session133", "bWlycm9yMTMzc2Vzc2lvbjEzMw"),
    ("mirror133library133", "bWlycm9yMTMzbGlicmFyeTEzMw"),
    ("mirror133service133", "bWlycm9yMTMzc2VydmljZTEzMw"),
    ("filter133service133", "ZmlsdGVyMTMzc2VydmljZTEzMw"),
    ("filter133gateway133", "ZmlsdGVyMTMzZ2F0ZXdheTEzMw"),
    ("filter133storage133", "ZmlsdGVyMTMzc3RvcmFnZTEzMw"),
    ("filter133network133", "ZmlsdGVyMTMzbmV0d29yazEzMw"),
    ("ranking133network133", "cmFua2luZzEzM25ldHdvcmsxMzM"),
    ("ranking133latency133", "cmFua2luZzEzM2xhdGVuY3kxMzM"),
    ("ranking133buffer133", "cmFua2luZzEzM2J1ZmZlcjEzMw"),
    ("ranking133queue133", "cmFua2luZzEzM3F1ZXVlMTMz"),
    ("encoding133queue133", "ZW5jb2RpbmcxMzNxdWV1ZTEzMw"),
    ("encoding133worker133", "ZW5jb2RpbmcxMzN3b3JrZXIxMzM"),
    ("encoding133kernel133", "ZW5jb2RpbmcxMzNrZXJuZWwxMzM"),
    ("encoding133signal133", "ZW5jb2RpbmcxMzNzaWduYWwxMzM"),
    ("mapping133signal133", "bWFwcGluZzEzM3NpZ25hbDEzMw"),
    ("mapping133packet133", "bWFwcGluZzEzM3BhY2tldDEzMw"),
    ("mapping133router133", "bWFwcGluZzEzM3JvdXRlcjEzMw"),
    ("mapping133cluster133", "bWFwcGluZzEzM2NsdXN0ZXIxMzM"),
    ("record133cluster133", "cmVjb3JkMTMzY2x1c3RlcjEzMw"),
    ("record133mirror133", "cmVjb3JkMTMzbWlycm9yMTMz"),
    ("record133filter133", "cmVjb3JkMTMzZmlsdGVyMTMz"),
    ("record133ranking133", "cmVjb3JkMTMzcmFua2luZzEzMw"),
    ("candle133ranking133", "Y2FuZGxlMTMzcmFua2luZzEzMw"),
    ("candle133encoding133", "Y2FuZGxlMTMzZW5jb2RpbmcxMzM"),
    ("candle133mapping133", "Y2FuZGxlMTMzbWFwcGluZzEzMw"),
    ("candle133record133", "Y2FuZGxlMTMzcmVjb3JkMTMz"),
    ("thread133record133", "dGhyZWFkMTMzcmVjb3JkMTMz"),
    ("thread133candle133", "dGhyZWFkMTMzY2FuZGxlMTMz"),
    ("thread133thread133", "dGhyZWFkMTMzdGhyZWFkMTMz"),
    ("thread133kitten133", "dGhyZWFkMTMza2l0dGVuMTMz"),
    (
        "round 133: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTMzOiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 133: agentuniverse is a framework for multi agents",
        "cm91bmQgMTMzOiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 133: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTMzOiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 133: the processor reads the record then stops",
        "cm91bmQgMTMzOiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 133: a worker pulls the next task from the queue",
        "cm91bmQgMTMzOiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 133: signals travel through the network layer",
        "cm91bmQgMTMzOiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 133: the gateway routes each request by policy",
        "cm91bmQgMTMzOiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 133: memory grows until the buffer is full",
        "cm91bmQgMTMzOiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 133: the cluster mirrors every packet twice",
        "cm91bmQgMTMzOiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 133: ranking uses tokens learned from the corpus",
        "cm91bmQgMTMzOiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 133: a long session ends when the candle dies",
        "cm91bmQgMTMzOiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 133: encode the prompt then map the result",
        "cm91bmQgMTMzOiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 133: the kernel wakes the worker at dawn",
        "cm91bmQgMTMzOiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 133: service latency drops after the patch",
        "cm91bmQgMTMzOiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 133: the library caches every vector it sees",
        "cm91bmQgMTMzOiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 133: agents argue then the debate resolves",
        "cm91bmQgMTMzOiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 133: the filter keeps only strong matches",
        "cm91bmQgMTMzOiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 133: the model answers with a short reply",
        "cm91bmQgMTMzOiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 133: the recorder stores the reasoning trace",
        "cm91bmQgMTMzOiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 133: the angel watches the processor run",
        "cm91bmQgMTMzOiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 133: angle of the vector decides the match",
        "cm91bmQgMTMzOiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 133: the candle burns twice as long at night",
        "cm91bmQgMTMzOiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 133: a mirror of the universe in one line",
        "cm91bmQgMTMzOiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 133: the queue drains before the storm", "cm91bmQgMTMzOiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
