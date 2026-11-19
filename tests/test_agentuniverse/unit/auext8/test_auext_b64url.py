"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten8kitten8", "a2l0dGVuOGtpdHRlbjg"),
    ("kitten8sitting8", "a2l0dGVuOHNpdHRpbmc4"),
    ("kitten8agent8", "a2l0dGVuOGFnZW50OA"),
    ("kitten8angle8", "a2l0dGVuOGFuZ2xlOA"),
    ("sitting8angle8", "c2l0dGluZzhhbmdsZTg"),
    ("sitting8universe8", "c2l0dGluZzh1bml2ZXJzZTg"),
    ("sitting8memory8", "c2l0dGluZzhtZW1vcnk4"),
    ("sitting8stream8", "c2l0dGluZzhzdHJlYW04"),
    ("agent8stream8", "YWdlbnQ4c3RyZWFtOA"),
    ("agent8context8", "YWdlbnQ4Y29udGV4dDg"),
    ("agent8knowledge8", "YWdlbnQ4a25vd2xlZGdlOA"),
    ("agent8vector8", "YWdlbnQ4dmVjdG9yOA"),
    ("angle8vector8", "YW5nbGU4dmVjdG9yOA"),
    ("angle8processor8", "YW5nbGU4cHJvY2Vzc29yOA"),
    ("angle8reasoning8", "YW5nbGU4cmVhc29uaW5nOA"),
    ("angle8machine8", "YW5nbGU4bWFjaGluZTg"),
    ("universe8machine8", "dW5pdmVyc2U4bWFjaGluZTg"),
    ("universe8learning8", "dW5pdmVyc2U4bGVhcm5pbmc4"),
    ("universe8model8", "dW5pdmVyc2U4bW9kZWw4"),
    ("universe8token8", "dW5pdmVyc2U4dG9rZW44"),
    ("memory8token8", "bWVtb3J5OHRva2VuOA"),
    ("memory8prompt8", "bWVtb3J5OHByb21wdDg"),
    ("memory8session8", "bWVtb3J5OHNlc3Npb244"),
    ("memory8library8", "bWVtb3J5OGxpYnJhcnk4"),
    ("stream8library8", "c3RyZWFtOGxpYnJhcnk4"),
    ("stream8service8", "c3RyZWFtOHNlcnZpY2U4"),
    ("stream8gateway8", "c3RyZWFtOGdhdGV3YXk4"),
    ("stream8storage8", "c3RyZWFtOHN0b3JhZ2U4"),
    ("context8storage8", "Y29udGV4dDhzdG9yYWdlOA"),
    ("context8network8", "Y29udGV4dDhuZXR3b3JrOA"),
    ("context8latency8", "Y29udGV4dDhsYXRlbmN5OA"),
    ("context8buffer8", "Y29udGV4dDhidWZmZXI4"),
    ("knowledge8buffer8", "a25vd2xlZGdlOGJ1ZmZlcjg"),
    ("knowledge8queue8", "a25vd2xlZGdlOHF1ZXVlOA"),
    ("knowledge8worker8", "a25vd2xlZGdlOHdvcmtlcjg"),
    ("knowledge8kernel8", "a25vd2xlZGdlOGtlcm5lbDg"),
    ("vector8kernel8", "dmVjdG9yOGtlcm5lbDg"),
    ("vector8signal8", "dmVjdG9yOHNpZ25hbDg"),
    ("vector8packet8", "dmVjdG9yOHBhY2tldDg"),
    ("vector8router8", "dmVjdG9yOHJvdXRlcjg"),
    ("processor8router8", "cHJvY2Vzc29yOHJvdXRlcjg"),
    ("processor8cluster8", "cHJvY2Vzc29yOGNsdXN0ZXI4"),
    ("processor8mirror8", "cHJvY2Vzc29yOG1pcnJvcjg"),
    ("processor8filter8", "cHJvY2Vzc29yOGZpbHRlcjg"),
    ("reasoning8filter8", "cmVhc29uaW5nOGZpbHRlcjg"),
    ("reasoning8ranking8", "cmVhc29uaW5nOHJhbmtpbmc4"),
    ("reasoning8encoding8", "cmVhc29uaW5nOGVuY29kaW5nOA"),
    ("reasoning8mapping8", "cmVhc29uaW5nOG1hcHBpbmc4"),
    ("machine8mapping8", "bWFjaGluZThtYXBwaW5nOA"),
    ("machine8record8", "bWFjaGluZThyZWNvcmQ4"),
    ("machine8candle8", "bWFjaGluZThjYW5kbGU4"),
    ("machine8thread8", "bWFjaGluZTh0aHJlYWQ4"),
    ("learning8thread8", "bGVhcm5pbmc4dGhyZWFkOA"),
    ("learning8kitten8", "bGVhcm5pbmc4a2l0dGVuOA"),
    ("learning8sitting8", "bGVhcm5pbmc4c2l0dGluZzg"),
    ("learning8agent8", "bGVhcm5pbmc4YWdlbnQ4"),
    ("model8agent8", "bW9kZWw4YWdlbnQ4"),
    ("model8angle8", "bW9kZWw4YW5nbGU4"),
    ("model8universe8", "bW9kZWw4dW5pdmVyc2U4"),
    ("model8memory8", "bW9kZWw4bWVtb3J5OA"),
    ("token8memory8", "dG9rZW44bWVtb3J5OA"),
    ("token8stream8", "dG9rZW44c3RyZWFtOA"),
    ("token8context8", "dG9rZW44Y29udGV4dDg"),
    ("token8knowledge8", "dG9rZW44a25vd2xlZGdlOA"),
    ("prompt8knowledge8", "cHJvbXB0OGtub3dsZWRnZTg"),
    ("prompt8vector8", "cHJvbXB0OHZlY3Rvcjg"),
    ("prompt8processor8", "cHJvbXB0OHByb2Nlc3Nvcjg"),
    ("prompt8reasoning8", "cHJvbXB0OHJlYXNvbmluZzg"),
    ("session8reasoning8", "c2Vzc2lvbjhyZWFzb25pbmc4"),
    ("session8machine8", "c2Vzc2lvbjhtYWNoaW5lOA"),
    ("session8learning8", "c2Vzc2lvbjhsZWFybmluZzg"),
    ("session8model8", "c2Vzc2lvbjhtb2RlbDg"),
    ("library8model8", "bGlicmFyeThtb2RlbDg"),
    ("library8token8", "bGlicmFyeTh0b2tlbjg"),
    ("library8prompt8", "bGlicmFyeThwcm9tcHQ4"),
    ("library8session8", "bGlicmFyeThzZXNzaW9uOA"),
    ("service8session8", "c2VydmljZThzZXNzaW9uOA"),
    ("service8library8", "c2VydmljZThsaWJyYXJ5OA"),
    ("service8service8", "c2VydmljZThzZXJ2aWNlOA"),
    ("service8gateway8", "c2VydmljZThnYXRld2F5OA"),
    ("gateway8gateway8", "Z2F0ZXdheThnYXRld2F5OA"),
    ("gateway8storage8", "Z2F0ZXdheThzdG9yYWdlOA"),
    ("gateway8network8", "Z2F0ZXdheThuZXR3b3JrOA"),
    ("gateway8latency8", "Z2F0ZXdheThsYXRlbmN5OA"),
    ("storage8latency8", "c3RvcmFnZThsYXRlbmN5OA"),
    ("storage8buffer8", "c3RvcmFnZThidWZmZXI4"),
    ("storage8queue8", "c3RvcmFnZThxdWV1ZTg"),
    ("storage8worker8", "c3RvcmFnZTh3b3JrZXI4"),
    ("network8worker8", "bmV0d29yazh3b3JrZXI4"),
    ("network8kernel8", "bmV0d29yazhrZXJuZWw4"),
    ("network8signal8", "bmV0d29yazhzaWduYWw4"),
    ("network8packet8", "bmV0d29yazhwYWNrZXQ4"),
    ("latency8packet8", "bGF0ZW5jeThwYWNrZXQ4"),
    ("latency8router8", "bGF0ZW5jeThyb3V0ZXI4"),
    ("latency8cluster8", "bGF0ZW5jeThjbHVzdGVyOA"),
    ("latency8mirror8", "bGF0ZW5jeThtaXJyb3I4"),
    ("buffer8mirror8", "YnVmZmVyOG1pcnJvcjg"),
    ("buffer8filter8", "YnVmZmVyOGZpbHRlcjg"),
    ("buffer8ranking8", "YnVmZmVyOHJhbmtpbmc4"),
    ("buffer8encoding8", "YnVmZmVyOGVuY29kaW5nOA"),
    ("queue8encoding8", "cXVldWU4ZW5jb2Rpbmc4"),
    ("queue8mapping8", "cXVldWU4bWFwcGluZzg"),
    ("queue8record8", "cXVldWU4cmVjb3JkOA"),
    ("queue8candle8", "cXVldWU4Y2FuZGxlOA"),
    ("worker8candle8", "d29ya2VyOGNhbmRsZTg"),
    ("worker8thread8", "d29ya2VyOHRocmVhZDg"),
    ("worker8kitten8", "d29ya2VyOGtpdHRlbjg"),
    ("worker8sitting8", "d29ya2VyOHNpdHRpbmc4"),
    ("kernel8sitting8", "a2VybmVsOHNpdHRpbmc4"),
    ("kernel8agent8", "a2VybmVsOGFnZW50OA"),
    ("kernel8angle8", "a2VybmVsOGFuZ2xlOA"),
    ("kernel8universe8", "a2VybmVsOHVuaXZlcnNlOA"),
    ("signal8universe8", "c2lnbmFsOHVuaXZlcnNlOA"),
    ("signal8memory8", "c2lnbmFsOG1lbW9yeTg"),
    ("signal8stream8", "c2lnbmFsOHN0cmVhbTg"),
    ("signal8context8", "c2lnbmFsOGNvbnRleHQ4"),
    ("packet8context8", "cGFja2V0OGNvbnRleHQ4"),
    ("packet8knowledge8", "cGFja2V0OGtub3dsZWRnZTg"),
    ("packet8vector8", "cGFja2V0OHZlY3Rvcjg"),
    ("packet8processor8", "cGFja2V0OHByb2Nlc3Nvcjg"),
    ("router8processor8", "cm91dGVyOHByb2Nlc3Nvcjg"),
    ("router8reasoning8", "cm91dGVyOHJlYXNvbmluZzg"),
    ("router8machine8", "cm91dGVyOG1hY2hpbmU4"),
    ("router8learning8", "cm91dGVyOGxlYXJuaW5nOA"),
    ("cluster8learning8", "Y2x1c3RlcjhsZWFybmluZzg"),
    ("cluster8model8", "Y2x1c3Rlcjhtb2RlbDg"),
    ("cluster8token8", "Y2x1c3Rlcjh0b2tlbjg"),
    ("cluster8prompt8", "Y2x1c3Rlcjhwcm9tcHQ4"),
    ("mirror8prompt8", "bWlycm9yOHByb21wdDg"),
    ("mirror8session8", "bWlycm9yOHNlc3Npb244"),
    ("mirror8library8", "bWlycm9yOGxpYnJhcnk4"),
    ("mirror8service8", "bWlycm9yOHNlcnZpY2U4"),
    ("filter8service8", "ZmlsdGVyOHNlcnZpY2U4"),
    ("filter8gateway8", "ZmlsdGVyOGdhdGV3YXk4"),
    ("filter8storage8", "ZmlsdGVyOHN0b3JhZ2U4"),
    ("filter8network8", "ZmlsdGVyOG5ldHdvcms4"),
    ("ranking8network8", "cmFua2luZzhuZXR3b3JrOA"),
    ("ranking8latency8", "cmFua2luZzhsYXRlbmN5OA"),
    ("ranking8buffer8", "cmFua2luZzhidWZmZXI4"),
    ("ranking8queue8", "cmFua2luZzhxdWV1ZTg"),
    ("encoding8queue8", "ZW5jb2Rpbmc4cXVldWU4"),
    ("encoding8worker8", "ZW5jb2Rpbmc4d29ya2VyOA"),
    ("encoding8kernel8", "ZW5jb2Rpbmc4a2VybmVsOA"),
    ("encoding8signal8", "ZW5jb2Rpbmc4c2lnbmFsOA"),
    ("mapping8signal8", "bWFwcGluZzhzaWduYWw4"),
    ("mapping8packet8", "bWFwcGluZzhwYWNrZXQ4"),
    ("mapping8router8", "bWFwcGluZzhyb3V0ZXI4"),
    ("mapping8cluster8", "bWFwcGluZzhjbHVzdGVyOA"),
    ("record8cluster8", "cmVjb3JkOGNsdXN0ZXI4"),
    ("record8mirror8", "cmVjb3JkOG1pcnJvcjg"),
    ("record8filter8", "cmVjb3JkOGZpbHRlcjg"),
    ("record8ranking8", "cmVjb3JkOHJhbmtpbmc4"),
    ("candle8ranking8", "Y2FuZGxlOHJhbmtpbmc4"),
    ("candle8encoding8", "Y2FuZGxlOGVuY29kaW5nOA"),
    ("candle8mapping8", "Y2FuZGxlOG1hcHBpbmc4"),
    ("candle8record8", "Y2FuZGxlOHJlY29yZDg"),
    ("thread8record8", "dGhyZWFkOHJlY29yZDg"),
    ("thread8candle8", "dGhyZWFkOGNhbmRsZTg"),
    ("thread8thread8", "dGhyZWFkOHRocmVhZDg"),
    ("thread8kitten8", "dGhyZWFkOGtpdHRlbjg"),
    (
        "round 8: the quick brown fox jumps over the lazy dog",
        "cm91bmQgODogdGhlIHF1aWNrIGJyb3duIGZveCBqdW1wcyBvdmVyIHRoZSBsYXp5IGRvZw",
    ),
    (
        "round 8: agentuniverse is a framework for multi agents",
        "cm91bmQgODogYWdlbnR1bml2ZXJzZSBpcyBhIGZyYW1ld29yayBmb3IgbXVsdGkgYWdlbnRz",
    ),
    (
        "round 8: knowledge stored as vectors enables retrieval",
        "cm91bmQgODoga25vd2xlZGdlIHN0b3JlZCBhcyB2ZWN0b3JzIGVuYWJsZXMgcmV0cmlldmFs",
    ),
    (
        "round 8: the processor reads the record then stops",
        "cm91bmQgODogdGhlIHByb2Nlc3NvciByZWFkcyB0aGUgcmVjb3JkIHRoZW4gc3RvcHM",
    ),
    (
        "round 8: a worker pulls the next task from the queue",
        "cm91bmQgODogYSB3b3JrZXIgcHVsbHMgdGhlIG5leHQgdGFzayBmcm9tIHRoZSBxdWV1ZQ",
    ),
    (
        "round 8: signals travel through the network layer",
        "cm91bmQgODogc2lnbmFscyB0cmF2ZWwgdGhyb3VnaCB0aGUgbmV0d29yayBsYXllcg",
    ),
    (
        "round 8: the gateway routes each request by policy",
        "cm91bmQgODogdGhlIGdhdGV3YXkgcm91dGVzIGVhY2ggcmVxdWVzdCBieSBwb2xpY3k",
    ),
    (
        "round 8: memory grows until the buffer is full",
        "cm91bmQgODogbWVtb3J5IGdyb3dzIHVudGlsIHRoZSBidWZmZXIgaXMgZnVsbA",
    ),
    (
        "round 8: the cluster mirrors every packet twice",
        "cm91bmQgODogdGhlIGNsdXN0ZXIgbWlycm9ycyBldmVyeSBwYWNrZXQgdHdpY2U",
    ),
    (
        "round 8: ranking uses tokens learned from the corpus",
        "cm91bmQgODogcmFua2luZyB1c2VzIHRva2VucyBsZWFybmVkIGZyb20gdGhlIGNvcnB1cw",
    ),
    (
        "round 8: a long session ends when the candle dies",
        "cm91bmQgODogYSBsb25nIHNlc3Npb24gZW5kcyB3aGVuIHRoZSBjYW5kbGUgZGllcw",
    ),
    (
        "round 8: encode the prompt then map the result",
        "cm91bmQgODogZW5jb2RlIHRoZSBwcm9tcHQgdGhlbiBtYXAgdGhlIHJlc3VsdA",
    ),
    ("round 8: the kernel wakes the worker at dawn", "cm91bmQgODogdGhlIGtlcm5lbCB3YWtlcyB0aGUgd29ya2VyIGF0IGRhd24"),
    (
        "round 8: service latency drops after the patch",
        "cm91bmQgODogc2VydmljZSBsYXRlbmN5IGRyb3BzIGFmdGVyIHRoZSBwYXRjaA",
    ),
    (
        "round 8: the library caches every vector it sees",
        "cm91bmQgODogdGhlIGxpYnJhcnkgY2FjaGVzIGV2ZXJ5IHZlY3RvciBpdCBzZWVz",
    ),
    (
        "round 8: agents argue then the debate resolves",
        "cm91bmQgODogYWdlbnRzIGFyZ3VlIHRoZW4gdGhlIGRlYmF0ZSByZXNvbHZlcw",
    ),
    ("round 8: the filter keeps only strong matches", "cm91bmQgODogdGhlIGZpbHRlciBrZWVwcyBvbmx5IHN0cm9uZyBtYXRjaGVz"),
    ("round 8: the model answers with a short reply", "cm91bmQgODogdGhlIG1vZGVsIGFuc3dlcnMgd2l0aCBhIHNob3J0IHJlcGx5"),
    (
        "round 8: the recorder stores the reasoning trace",
        "cm91bmQgODogdGhlIHJlY29yZGVyIHN0b3JlcyB0aGUgcmVhc29uaW5nIHRyYWNl",
    ),
    ("round 8: the angel watches the processor run", "cm91bmQgODogdGhlIGFuZ2VsIHdhdGNoZXMgdGhlIHByb2Nlc3NvciBydW4"),
    (
        "round 8: angle of the vector decides the match",
        "cm91bmQgODogYW5nbGUgb2YgdGhlIHZlY3RvciBkZWNpZGVzIHRoZSBtYXRjaA",
    ),
    (
        "round 8: the candle burns twice as long at night",
        "cm91bmQgODogdGhlIGNhbmRsZSBidXJucyB0d2ljZSBhcyBsb25nIGF0IG5pZ2h0",
    ),
    ("round 8: a mirror of the universe in one line", "cm91bmQgODogYSBtaXJyb3Igb2YgdGhlIHVuaXZlcnNlIGluIG9uZSBsaW5l"),
    ("round 8: the queue drains before the storm", "cm91bmQgODogdGhlIHF1ZXVlIGRyYWlucyBiZWZvcmUgdGhlIHN0b3Jt"),
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
