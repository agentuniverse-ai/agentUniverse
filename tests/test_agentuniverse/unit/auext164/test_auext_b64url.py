"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten164kitten164", "a2l0dGVuMTY0a2l0dGVuMTY0"),
    ("kitten164sitting164", "a2l0dGVuMTY0c2l0dGluZzE2NA"),
    ("kitten164agent164", "a2l0dGVuMTY0YWdlbnQxNjQ"),
    ("kitten164angle164", "a2l0dGVuMTY0YW5nbGUxNjQ"),
    ("sitting164angle164", "c2l0dGluZzE2NGFuZ2xlMTY0"),
    ("sitting164universe164", "c2l0dGluZzE2NHVuaXZlcnNlMTY0"),
    ("sitting164memory164", "c2l0dGluZzE2NG1lbW9yeTE2NA"),
    ("sitting164stream164", "c2l0dGluZzE2NHN0cmVhbTE2NA"),
    ("agent164stream164", "YWdlbnQxNjRzdHJlYW0xNjQ"),
    ("agent164context164", "YWdlbnQxNjRjb250ZXh0MTY0"),
    ("agent164knowledge164", "YWdlbnQxNjRrbm93bGVkZ2UxNjQ"),
    ("agent164vector164", "YWdlbnQxNjR2ZWN0b3IxNjQ"),
    ("angle164vector164", "YW5nbGUxNjR2ZWN0b3IxNjQ"),
    ("angle164processor164", "YW5nbGUxNjRwcm9jZXNzb3IxNjQ"),
    ("angle164reasoning164", "YW5nbGUxNjRyZWFzb25pbmcxNjQ"),
    ("angle164machine164", "YW5nbGUxNjRtYWNoaW5lMTY0"),
    ("universe164machine164", "dW5pdmVyc2UxNjRtYWNoaW5lMTY0"),
    ("universe164learning164", "dW5pdmVyc2UxNjRsZWFybmluZzE2NA"),
    ("universe164model164", "dW5pdmVyc2UxNjRtb2RlbDE2NA"),
    ("universe164token164", "dW5pdmVyc2UxNjR0b2tlbjE2NA"),
    ("memory164token164", "bWVtb3J5MTY0dG9rZW4xNjQ"),
    ("memory164prompt164", "bWVtb3J5MTY0cHJvbXB0MTY0"),
    ("memory164session164", "bWVtb3J5MTY0c2Vzc2lvbjE2NA"),
    ("memory164library164", "bWVtb3J5MTY0bGlicmFyeTE2NA"),
    ("stream164library164", "c3RyZWFtMTY0bGlicmFyeTE2NA"),
    ("stream164service164", "c3RyZWFtMTY0c2VydmljZTE2NA"),
    ("stream164gateway164", "c3RyZWFtMTY0Z2F0ZXdheTE2NA"),
    ("stream164storage164", "c3RyZWFtMTY0c3RvcmFnZTE2NA"),
    ("context164storage164", "Y29udGV4dDE2NHN0b3JhZ2UxNjQ"),
    ("context164network164", "Y29udGV4dDE2NG5ldHdvcmsxNjQ"),
    ("context164latency164", "Y29udGV4dDE2NGxhdGVuY3kxNjQ"),
    ("context164buffer164", "Y29udGV4dDE2NGJ1ZmZlcjE2NA"),
    ("knowledge164buffer164", "a25vd2xlZGdlMTY0YnVmZmVyMTY0"),
    ("knowledge164queue164", "a25vd2xlZGdlMTY0cXVldWUxNjQ"),
    ("knowledge164worker164", "a25vd2xlZGdlMTY0d29ya2VyMTY0"),
    ("knowledge164kernel164", "a25vd2xlZGdlMTY0a2VybmVsMTY0"),
    ("vector164kernel164", "dmVjdG9yMTY0a2VybmVsMTY0"),
    ("vector164signal164", "dmVjdG9yMTY0c2lnbmFsMTY0"),
    ("vector164packet164", "dmVjdG9yMTY0cGFja2V0MTY0"),
    ("vector164router164", "dmVjdG9yMTY0cm91dGVyMTY0"),
    ("processor164router164", "cHJvY2Vzc29yMTY0cm91dGVyMTY0"),
    ("processor164cluster164", "cHJvY2Vzc29yMTY0Y2x1c3RlcjE2NA"),
    ("processor164mirror164", "cHJvY2Vzc29yMTY0bWlycm9yMTY0"),
    ("processor164filter164", "cHJvY2Vzc29yMTY0ZmlsdGVyMTY0"),
    ("reasoning164filter164", "cmVhc29uaW5nMTY0ZmlsdGVyMTY0"),
    ("reasoning164ranking164", "cmVhc29uaW5nMTY0cmFua2luZzE2NA"),
    ("reasoning164encoding164", "cmVhc29uaW5nMTY0ZW5jb2RpbmcxNjQ"),
    ("reasoning164mapping164", "cmVhc29uaW5nMTY0bWFwcGluZzE2NA"),
    ("machine164mapping164", "bWFjaGluZTE2NG1hcHBpbmcxNjQ"),
    ("machine164record164", "bWFjaGluZTE2NHJlY29yZDE2NA"),
    ("machine164candle164", "bWFjaGluZTE2NGNhbmRsZTE2NA"),
    ("machine164thread164", "bWFjaGluZTE2NHRocmVhZDE2NA"),
    ("learning164thread164", "bGVhcm5pbmcxNjR0aHJlYWQxNjQ"),
    ("learning164kitten164", "bGVhcm5pbmcxNjRraXR0ZW4xNjQ"),
    ("learning164sitting164", "bGVhcm5pbmcxNjRzaXR0aW5nMTY0"),
    ("learning164agent164", "bGVhcm5pbmcxNjRhZ2VudDE2NA"),
    ("model164agent164", "bW9kZWwxNjRhZ2VudDE2NA"),
    ("model164angle164", "bW9kZWwxNjRhbmdsZTE2NA"),
    ("model164universe164", "bW9kZWwxNjR1bml2ZXJzZTE2NA"),
    ("model164memory164", "bW9kZWwxNjRtZW1vcnkxNjQ"),
    ("token164memory164", "dG9rZW4xNjRtZW1vcnkxNjQ"),
    ("token164stream164", "dG9rZW4xNjRzdHJlYW0xNjQ"),
    ("token164context164", "dG9rZW4xNjRjb250ZXh0MTY0"),
    ("token164knowledge164", "dG9rZW4xNjRrbm93bGVkZ2UxNjQ"),
    ("prompt164knowledge164", "cHJvbXB0MTY0a25vd2xlZGdlMTY0"),
    ("prompt164vector164", "cHJvbXB0MTY0dmVjdG9yMTY0"),
    ("prompt164processor164", "cHJvbXB0MTY0cHJvY2Vzc29yMTY0"),
    ("prompt164reasoning164", "cHJvbXB0MTY0cmVhc29uaW5nMTY0"),
    ("session164reasoning164", "c2Vzc2lvbjE2NHJlYXNvbmluZzE2NA"),
    ("session164machine164", "c2Vzc2lvbjE2NG1hY2hpbmUxNjQ"),
    ("session164learning164", "c2Vzc2lvbjE2NGxlYXJuaW5nMTY0"),
    ("session164model164", "c2Vzc2lvbjE2NG1vZGVsMTY0"),
    ("library164model164", "bGlicmFyeTE2NG1vZGVsMTY0"),
    ("library164token164", "bGlicmFyeTE2NHRva2VuMTY0"),
    ("library164prompt164", "bGlicmFyeTE2NHByb21wdDE2NA"),
    ("library164session164", "bGlicmFyeTE2NHNlc3Npb24xNjQ"),
    ("service164session164", "c2VydmljZTE2NHNlc3Npb24xNjQ"),
    ("service164library164", "c2VydmljZTE2NGxpYnJhcnkxNjQ"),
    ("service164service164", "c2VydmljZTE2NHNlcnZpY2UxNjQ"),
    ("service164gateway164", "c2VydmljZTE2NGdhdGV3YXkxNjQ"),
    ("gateway164gateway164", "Z2F0ZXdheTE2NGdhdGV3YXkxNjQ"),
    ("gateway164storage164", "Z2F0ZXdheTE2NHN0b3JhZ2UxNjQ"),
    ("gateway164network164", "Z2F0ZXdheTE2NG5ldHdvcmsxNjQ"),
    ("gateway164latency164", "Z2F0ZXdheTE2NGxhdGVuY3kxNjQ"),
    ("storage164latency164", "c3RvcmFnZTE2NGxhdGVuY3kxNjQ"),
    ("storage164buffer164", "c3RvcmFnZTE2NGJ1ZmZlcjE2NA"),
    ("storage164queue164", "c3RvcmFnZTE2NHF1ZXVlMTY0"),
    ("storage164worker164", "c3RvcmFnZTE2NHdvcmtlcjE2NA"),
    ("network164worker164", "bmV0d29yazE2NHdvcmtlcjE2NA"),
    ("network164kernel164", "bmV0d29yazE2NGtlcm5lbDE2NA"),
    ("network164signal164", "bmV0d29yazE2NHNpZ25hbDE2NA"),
    ("network164packet164", "bmV0d29yazE2NHBhY2tldDE2NA"),
    ("latency164packet164", "bGF0ZW5jeTE2NHBhY2tldDE2NA"),
    ("latency164router164", "bGF0ZW5jeTE2NHJvdXRlcjE2NA"),
    ("latency164cluster164", "bGF0ZW5jeTE2NGNsdXN0ZXIxNjQ"),
    ("latency164mirror164", "bGF0ZW5jeTE2NG1pcnJvcjE2NA"),
    ("buffer164mirror164", "YnVmZmVyMTY0bWlycm9yMTY0"),
    ("buffer164filter164", "YnVmZmVyMTY0ZmlsdGVyMTY0"),
    ("buffer164ranking164", "YnVmZmVyMTY0cmFua2luZzE2NA"),
    ("buffer164encoding164", "YnVmZmVyMTY0ZW5jb2RpbmcxNjQ"),
    ("queue164encoding164", "cXVldWUxNjRlbmNvZGluZzE2NA"),
    ("queue164mapping164", "cXVldWUxNjRtYXBwaW5nMTY0"),
    ("queue164record164", "cXVldWUxNjRyZWNvcmQxNjQ"),
    ("queue164candle164", "cXVldWUxNjRjYW5kbGUxNjQ"),
    ("worker164candle164", "d29ya2VyMTY0Y2FuZGxlMTY0"),
    ("worker164thread164", "d29ya2VyMTY0dGhyZWFkMTY0"),
    ("worker164kitten164", "d29ya2VyMTY0a2l0dGVuMTY0"),
    ("worker164sitting164", "d29ya2VyMTY0c2l0dGluZzE2NA"),
    ("kernel164sitting164", "a2VybmVsMTY0c2l0dGluZzE2NA"),
    ("kernel164agent164", "a2VybmVsMTY0YWdlbnQxNjQ"),
    ("kernel164angle164", "a2VybmVsMTY0YW5nbGUxNjQ"),
    ("kernel164universe164", "a2VybmVsMTY0dW5pdmVyc2UxNjQ"),
    ("signal164universe164", "c2lnbmFsMTY0dW5pdmVyc2UxNjQ"),
    ("signal164memory164", "c2lnbmFsMTY0bWVtb3J5MTY0"),
    ("signal164stream164", "c2lnbmFsMTY0c3RyZWFtMTY0"),
    ("signal164context164", "c2lnbmFsMTY0Y29udGV4dDE2NA"),
    ("packet164context164", "cGFja2V0MTY0Y29udGV4dDE2NA"),
    ("packet164knowledge164", "cGFja2V0MTY0a25vd2xlZGdlMTY0"),
    ("packet164vector164", "cGFja2V0MTY0dmVjdG9yMTY0"),
    ("packet164processor164", "cGFja2V0MTY0cHJvY2Vzc29yMTY0"),
    ("router164processor164", "cm91dGVyMTY0cHJvY2Vzc29yMTY0"),
    ("router164reasoning164", "cm91dGVyMTY0cmVhc29uaW5nMTY0"),
    ("router164machine164", "cm91dGVyMTY0bWFjaGluZTE2NA"),
    ("router164learning164", "cm91dGVyMTY0bGVhcm5pbmcxNjQ"),
    ("cluster164learning164", "Y2x1c3RlcjE2NGxlYXJuaW5nMTY0"),
    ("cluster164model164", "Y2x1c3RlcjE2NG1vZGVsMTY0"),
    ("cluster164token164", "Y2x1c3RlcjE2NHRva2VuMTY0"),
    ("cluster164prompt164", "Y2x1c3RlcjE2NHByb21wdDE2NA"),
    ("mirror164prompt164", "bWlycm9yMTY0cHJvbXB0MTY0"),
    ("mirror164session164", "bWlycm9yMTY0c2Vzc2lvbjE2NA"),
    ("mirror164library164", "bWlycm9yMTY0bGlicmFyeTE2NA"),
    ("mirror164service164", "bWlycm9yMTY0c2VydmljZTE2NA"),
    ("filter164service164", "ZmlsdGVyMTY0c2VydmljZTE2NA"),
    ("filter164gateway164", "ZmlsdGVyMTY0Z2F0ZXdheTE2NA"),
    ("filter164storage164", "ZmlsdGVyMTY0c3RvcmFnZTE2NA"),
    ("filter164network164", "ZmlsdGVyMTY0bmV0d29yazE2NA"),
    ("ranking164network164", "cmFua2luZzE2NG5ldHdvcmsxNjQ"),
    ("ranking164latency164", "cmFua2luZzE2NGxhdGVuY3kxNjQ"),
    ("ranking164buffer164", "cmFua2luZzE2NGJ1ZmZlcjE2NA"),
    ("ranking164queue164", "cmFua2luZzE2NHF1ZXVlMTY0"),
    ("encoding164queue164", "ZW5jb2RpbmcxNjRxdWV1ZTE2NA"),
    ("encoding164worker164", "ZW5jb2RpbmcxNjR3b3JrZXIxNjQ"),
    ("encoding164kernel164", "ZW5jb2RpbmcxNjRrZXJuZWwxNjQ"),
    ("encoding164signal164", "ZW5jb2RpbmcxNjRzaWduYWwxNjQ"),
    ("mapping164signal164", "bWFwcGluZzE2NHNpZ25hbDE2NA"),
    ("mapping164packet164", "bWFwcGluZzE2NHBhY2tldDE2NA"),
    ("mapping164router164", "bWFwcGluZzE2NHJvdXRlcjE2NA"),
    ("mapping164cluster164", "bWFwcGluZzE2NGNsdXN0ZXIxNjQ"),
    ("record164cluster164", "cmVjb3JkMTY0Y2x1c3RlcjE2NA"),
    ("record164mirror164", "cmVjb3JkMTY0bWlycm9yMTY0"),
    ("record164filter164", "cmVjb3JkMTY0ZmlsdGVyMTY0"),
    ("record164ranking164", "cmVjb3JkMTY0cmFua2luZzE2NA"),
    ("candle164ranking164", "Y2FuZGxlMTY0cmFua2luZzE2NA"),
    ("candle164encoding164", "Y2FuZGxlMTY0ZW5jb2RpbmcxNjQ"),
    ("candle164mapping164", "Y2FuZGxlMTY0bWFwcGluZzE2NA"),
    ("candle164record164", "Y2FuZGxlMTY0cmVjb3JkMTY0"),
    ("thread164record164", "dGhyZWFkMTY0cmVjb3JkMTY0"),
    ("thread164candle164", "dGhyZWFkMTY0Y2FuZGxlMTY0"),
    ("thread164thread164", "dGhyZWFkMTY0dGhyZWFkMTY0"),
    ("thread164kitten164", "dGhyZWFkMTY0a2l0dGVuMTY0"),
    (
        "round 164: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTY0OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 164: agentuniverse is a framework for multi agents",
        "cm91bmQgMTY0OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 164: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTY0OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 164: the processor reads the record then stops",
        "cm91bmQgMTY0OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 164: a worker pulls the next task from the queue",
        "cm91bmQgMTY0OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 164: signals travel through the network layer",
        "cm91bmQgMTY0OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 164: the gateway routes each request by policy",
        "cm91bmQgMTY0OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 164: memory grows until the buffer is full",
        "cm91bmQgMTY0OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 164: the cluster mirrors every packet twice",
        "cm91bmQgMTY0OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 164: ranking uses tokens learned from the corpus",
        "cm91bmQgMTY0OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 164: a long session ends when the candle dies",
        "cm91bmQgMTY0OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 164: encode the prompt then map the result",
        "cm91bmQgMTY0OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 164: the kernel wakes the worker at dawn",
        "cm91bmQgMTY0OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 164: service latency drops after the patch",
        "cm91bmQgMTY0OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 164: the library caches every vector it sees",
        "cm91bmQgMTY0OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 164: agents argue then the debate resolves",
        "cm91bmQgMTY0OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 164: the filter keeps only strong matches",
        "cm91bmQgMTY0OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 164: the model answers with a short reply",
        "cm91bmQgMTY0OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 164: the recorder stores the reasoning trace",
        "cm91bmQgMTY0OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 164: the angel watches the processor run",
        "cm91bmQgMTY0OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 164: angle of the vector decides the match",
        "cm91bmQgMTY0OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 164: the candle burns twice as long at night",
        "cm91bmQgMTY0OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 164: a mirror of the universe in one line",
        "cm91bmQgMTY0OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 164: the queue drains before the storm", "cm91bmQgMTY0OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
