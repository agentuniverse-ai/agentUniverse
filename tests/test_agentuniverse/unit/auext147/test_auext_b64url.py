"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten147kitten147", "a2l0dGVuMTQ3a2l0dGVuMTQ3"),
    ("kitten147sitting147", "a2l0dGVuMTQ3c2l0dGluZzE0Nw"),
    ("kitten147agent147", "a2l0dGVuMTQ3YWdlbnQxNDc"),
    ("kitten147angle147", "a2l0dGVuMTQ3YW5nbGUxNDc"),
    ("sitting147angle147", "c2l0dGluZzE0N2FuZ2xlMTQ3"),
    ("sitting147universe147", "c2l0dGluZzE0N3VuaXZlcnNlMTQ3"),
    ("sitting147memory147", "c2l0dGluZzE0N21lbW9yeTE0Nw"),
    ("sitting147stream147", "c2l0dGluZzE0N3N0cmVhbTE0Nw"),
    ("agent147stream147", "YWdlbnQxNDdzdHJlYW0xNDc"),
    ("agent147context147", "YWdlbnQxNDdjb250ZXh0MTQ3"),
    ("agent147knowledge147", "YWdlbnQxNDdrbm93bGVkZ2UxNDc"),
    ("agent147vector147", "YWdlbnQxNDd2ZWN0b3IxNDc"),
    ("angle147vector147", "YW5nbGUxNDd2ZWN0b3IxNDc"),
    ("angle147processor147", "YW5nbGUxNDdwcm9jZXNzb3IxNDc"),
    ("angle147reasoning147", "YW5nbGUxNDdyZWFzb25pbmcxNDc"),
    ("angle147machine147", "YW5nbGUxNDdtYWNoaW5lMTQ3"),
    ("universe147machine147", "dW5pdmVyc2UxNDdtYWNoaW5lMTQ3"),
    ("universe147learning147", "dW5pdmVyc2UxNDdsZWFybmluZzE0Nw"),
    ("universe147model147", "dW5pdmVyc2UxNDdtb2RlbDE0Nw"),
    ("universe147token147", "dW5pdmVyc2UxNDd0b2tlbjE0Nw"),
    ("memory147token147", "bWVtb3J5MTQ3dG9rZW4xNDc"),
    ("memory147prompt147", "bWVtb3J5MTQ3cHJvbXB0MTQ3"),
    ("memory147session147", "bWVtb3J5MTQ3c2Vzc2lvbjE0Nw"),
    ("memory147library147", "bWVtb3J5MTQ3bGlicmFyeTE0Nw"),
    ("stream147library147", "c3RyZWFtMTQ3bGlicmFyeTE0Nw"),
    ("stream147service147", "c3RyZWFtMTQ3c2VydmljZTE0Nw"),
    ("stream147gateway147", "c3RyZWFtMTQ3Z2F0ZXdheTE0Nw"),
    ("stream147storage147", "c3RyZWFtMTQ3c3RvcmFnZTE0Nw"),
    ("context147storage147", "Y29udGV4dDE0N3N0b3JhZ2UxNDc"),
    ("context147network147", "Y29udGV4dDE0N25ldHdvcmsxNDc"),
    ("context147latency147", "Y29udGV4dDE0N2xhdGVuY3kxNDc"),
    ("context147buffer147", "Y29udGV4dDE0N2J1ZmZlcjE0Nw"),
    ("knowledge147buffer147", "a25vd2xlZGdlMTQ3YnVmZmVyMTQ3"),
    ("knowledge147queue147", "a25vd2xlZGdlMTQ3cXVldWUxNDc"),
    ("knowledge147worker147", "a25vd2xlZGdlMTQ3d29ya2VyMTQ3"),
    ("knowledge147kernel147", "a25vd2xlZGdlMTQ3a2VybmVsMTQ3"),
    ("vector147kernel147", "dmVjdG9yMTQ3a2VybmVsMTQ3"),
    ("vector147signal147", "dmVjdG9yMTQ3c2lnbmFsMTQ3"),
    ("vector147packet147", "dmVjdG9yMTQ3cGFja2V0MTQ3"),
    ("vector147router147", "dmVjdG9yMTQ3cm91dGVyMTQ3"),
    ("processor147router147", "cHJvY2Vzc29yMTQ3cm91dGVyMTQ3"),
    ("processor147cluster147", "cHJvY2Vzc29yMTQ3Y2x1c3RlcjE0Nw"),
    ("processor147mirror147", "cHJvY2Vzc29yMTQ3bWlycm9yMTQ3"),
    ("processor147filter147", "cHJvY2Vzc29yMTQ3ZmlsdGVyMTQ3"),
    ("reasoning147filter147", "cmVhc29uaW5nMTQ3ZmlsdGVyMTQ3"),
    ("reasoning147ranking147", "cmVhc29uaW5nMTQ3cmFua2luZzE0Nw"),
    ("reasoning147encoding147", "cmVhc29uaW5nMTQ3ZW5jb2RpbmcxNDc"),
    ("reasoning147mapping147", "cmVhc29uaW5nMTQ3bWFwcGluZzE0Nw"),
    ("machine147mapping147", "bWFjaGluZTE0N21hcHBpbmcxNDc"),
    ("machine147record147", "bWFjaGluZTE0N3JlY29yZDE0Nw"),
    ("machine147candle147", "bWFjaGluZTE0N2NhbmRsZTE0Nw"),
    ("machine147thread147", "bWFjaGluZTE0N3RocmVhZDE0Nw"),
    ("learning147thread147", "bGVhcm5pbmcxNDd0aHJlYWQxNDc"),
    ("learning147kitten147", "bGVhcm5pbmcxNDdraXR0ZW4xNDc"),
    ("learning147sitting147", "bGVhcm5pbmcxNDdzaXR0aW5nMTQ3"),
    ("learning147agent147", "bGVhcm5pbmcxNDdhZ2VudDE0Nw"),
    ("model147agent147", "bW9kZWwxNDdhZ2VudDE0Nw"),
    ("model147angle147", "bW9kZWwxNDdhbmdsZTE0Nw"),
    ("model147universe147", "bW9kZWwxNDd1bml2ZXJzZTE0Nw"),
    ("model147memory147", "bW9kZWwxNDdtZW1vcnkxNDc"),
    ("token147memory147", "dG9rZW4xNDdtZW1vcnkxNDc"),
    ("token147stream147", "dG9rZW4xNDdzdHJlYW0xNDc"),
    ("token147context147", "dG9rZW4xNDdjb250ZXh0MTQ3"),
    ("token147knowledge147", "dG9rZW4xNDdrbm93bGVkZ2UxNDc"),
    ("prompt147knowledge147", "cHJvbXB0MTQ3a25vd2xlZGdlMTQ3"),
    ("prompt147vector147", "cHJvbXB0MTQ3dmVjdG9yMTQ3"),
    ("prompt147processor147", "cHJvbXB0MTQ3cHJvY2Vzc29yMTQ3"),
    ("prompt147reasoning147", "cHJvbXB0MTQ3cmVhc29uaW5nMTQ3"),
    ("session147reasoning147", "c2Vzc2lvbjE0N3JlYXNvbmluZzE0Nw"),
    ("session147machine147", "c2Vzc2lvbjE0N21hY2hpbmUxNDc"),
    ("session147learning147", "c2Vzc2lvbjE0N2xlYXJuaW5nMTQ3"),
    ("session147model147", "c2Vzc2lvbjE0N21vZGVsMTQ3"),
    ("library147model147", "bGlicmFyeTE0N21vZGVsMTQ3"),
    ("library147token147", "bGlicmFyeTE0N3Rva2VuMTQ3"),
    ("library147prompt147", "bGlicmFyeTE0N3Byb21wdDE0Nw"),
    ("library147session147", "bGlicmFyeTE0N3Nlc3Npb24xNDc"),
    ("service147session147", "c2VydmljZTE0N3Nlc3Npb24xNDc"),
    ("service147library147", "c2VydmljZTE0N2xpYnJhcnkxNDc"),
    ("service147service147", "c2VydmljZTE0N3NlcnZpY2UxNDc"),
    ("service147gateway147", "c2VydmljZTE0N2dhdGV3YXkxNDc"),
    ("gateway147gateway147", "Z2F0ZXdheTE0N2dhdGV3YXkxNDc"),
    ("gateway147storage147", "Z2F0ZXdheTE0N3N0b3JhZ2UxNDc"),
    ("gateway147network147", "Z2F0ZXdheTE0N25ldHdvcmsxNDc"),
    ("gateway147latency147", "Z2F0ZXdheTE0N2xhdGVuY3kxNDc"),
    ("storage147latency147", "c3RvcmFnZTE0N2xhdGVuY3kxNDc"),
    ("storage147buffer147", "c3RvcmFnZTE0N2J1ZmZlcjE0Nw"),
    ("storage147queue147", "c3RvcmFnZTE0N3F1ZXVlMTQ3"),
    ("storage147worker147", "c3RvcmFnZTE0N3dvcmtlcjE0Nw"),
    ("network147worker147", "bmV0d29yazE0N3dvcmtlcjE0Nw"),
    ("network147kernel147", "bmV0d29yazE0N2tlcm5lbDE0Nw"),
    ("network147signal147", "bmV0d29yazE0N3NpZ25hbDE0Nw"),
    ("network147packet147", "bmV0d29yazE0N3BhY2tldDE0Nw"),
    ("latency147packet147", "bGF0ZW5jeTE0N3BhY2tldDE0Nw"),
    ("latency147router147", "bGF0ZW5jeTE0N3JvdXRlcjE0Nw"),
    ("latency147cluster147", "bGF0ZW5jeTE0N2NsdXN0ZXIxNDc"),
    ("latency147mirror147", "bGF0ZW5jeTE0N21pcnJvcjE0Nw"),
    ("buffer147mirror147", "YnVmZmVyMTQ3bWlycm9yMTQ3"),
    ("buffer147filter147", "YnVmZmVyMTQ3ZmlsdGVyMTQ3"),
    ("buffer147ranking147", "YnVmZmVyMTQ3cmFua2luZzE0Nw"),
    ("buffer147encoding147", "YnVmZmVyMTQ3ZW5jb2RpbmcxNDc"),
    ("queue147encoding147", "cXVldWUxNDdlbmNvZGluZzE0Nw"),
    ("queue147mapping147", "cXVldWUxNDdtYXBwaW5nMTQ3"),
    ("queue147record147", "cXVldWUxNDdyZWNvcmQxNDc"),
    ("queue147candle147", "cXVldWUxNDdjYW5kbGUxNDc"),
    ("worker147candle147", "d29ya2VyMTQ3Y2FuZGxlMTQ3"),
    ("worker147thread147", "d29ya2VyMTQ3dGhyZWFkMTQ3"),
    ("worker147kitten147", "d29ya2VyMTQ3a2l0dGVuMTQ3"),
    ("worker147sitting147", "d29ya2VyMTQ3c2l0dGluZzE0Nw"),
    ("kernel147sitting147", "a2VybmVsMTQ3c2l0dGluZzE0Nw"),
    ("kernel147agent147", "a2VybmVsMTQ3YWdlbnQxNDc"),
    ("kernel147angle147", "a2VybmVsMTQ3YW5nbGUxNDc"),
    ("kernel147universe147", "a2VybmVsMTQ3dW5pdmVyc2UxNDc"),
    ("signal147universe147", "c2lnbmFsMTQ3dW5pdmVyc2UxNDc"),
    ("signal147memory147", "c2lnbmFsMTQ3bWVtb3J5MTQ3"),
    ("signal147stream147", "c2lnbmFsMTQ3c3RyZWFtMTQ3"),
    ("signal147context147", "c2lnbmFsMTQ3Y29udGV4dDE0Nw"),
    ("packet147context147", "cGFja2V0MTQ3Y29udGV4dDE0Nw"),
    ("packet147knowledge147", "cGFja2V0MTQ3a25vd2xlZGdlMTQ3"),
    ("packet147vector147", "cGFja2V0MTQ3dmVjdG9yMTQ3"),
    ("packet147processor147", "cGFja2V0MTQ3cHJvY2Vzc29yMTQ3"),
    ("router147processor147", "cm91dGVyMTQ3cHJvY2Vzc29yMTQ3"),
    ("router147reasoning147", "cm91dGVyMTQ3cmVhc29uaW5nMTQ3"),
    ("router147machine147", "cm91dGVyMTQ3bWFjaGluZTE0Nw"),
    ("router147learning147", "cm91dGVyMTQ3bGVhcm5pbmcxNDc"),
    ("cluster147learning147", "Y2x1c3RlcjE0N2xlYXJuaW5nMTQ3"),
    ("cluster147model147", "Y2x1c3RlcjE0N21vZGVsMTQ3"),
    ("cluster147token147", "Y2x1c3RlcjE0N3Rva2VuMTQ3"),
    ("cluster147prompt147", "Y2x1c3RlcjE0N3Byb21wdDE0Nw"),
    ("mirror147prompt147", "bWlycm9yMTQ3cHJvbXB0MTQ3"),
    ("mirror147session147", "bWlycm9yMTQ3c2Vzc2lvbjE0Nw"),
    ("mirror147library147", "bWlycm9yMTQ3bGlicmFyeTE0Nw"),
    ("mirror147service147", "bWlycm9yMTQ3c2VydmljZTE0Nw"),
    ("filter147service147", "ZmlsdGVyMTQ3c2VydmljZTE0Nw"),
    ("filter147gateway147", "ZmlsdGVyMTQ3Z2F0ZXdheTE0Nw"),
    ("filter147storage147", "ZmlsdGVyMTQ3c3RvcmFnZTE0Nw"),
    ("filter147network147", "ZmlsdGVyMTQ3bmV0d29yazE0Nw"),
    ("ranking147network147", "cmFua2luZzE0N25ldHdvcmsxNDc"),
    ("ranking147latency147", "cmFua2luZzE0N2xhdGVuY3kxNDc"),
    ("ranking147buffer147", "cmFua2luZzE0N2J1ZmZlcjE0Nw"),
    ("ranking147queue147", "cmFua2luZzE0N3F1ZXVlMTQ3"),
    ("encoding147queue147", "ZW5jb2RpbmcxNDdxdWV1ZTE0Nw"),
    ("encoding147worker147", "ZW5jb2RpbmcxNDd3b3JrZXIxNDc"),
    ("encoding147kernel147", "ZW5jb2RpbmcxNDdrZXJuZWwxNDc"),
    ("encoding147signal147", "ZW5jb2RpbmcxNDdzaWduYWwxNDc"),
    ("mapping147signal147", "bWFwcGluZzE0N3NpZ25hbDE0Nw"),
    ("mapping147packet147", "bWFwcGluZzE0N3BhY2tldDE0Nw"),
    ("mapping147router147", "bWFwcGluZzE0N3JvdXRlcjE0Nw"),
    ("mapping147cluster147", "bWFwcGluZzE0N2NsdXN0ZXIxNDc"),
    ("record147cluster147", "cmVjb3JkMTQ3Y2x1c3RlcjE0Nw"),
    ("record147mirror147", "cmVjb3JkMTQ3bWlycm9yMTQ3"),
    ("record147filter147", "cmVjb3JkMTQ3ZmlsdGVyMTQ3"),
    ("record147ranking147", "cmVjb3JkMTQ3cmFua2luZzE0Nw"),
    ("candle147ranking147", "Y2FuZGxlMTQ3cmFua2luZzE0Nw"),
    ("candle147encoding147", "Y2FuZGxlMTQ3ZW5jb2RpbmcxNDc"),
    ("candle147mapping147", "Y2FuZGxlMTQ3bWFwcGluZzE0Nw"),
    ("candle147record147", "Y2FuZGxlMTQ3cmVjb3JkMTQ3"),
    ("thread147record147", "dGhyZWFkMTQ3cmVjb3JkMTQ3"),
    ("thread147candle147", "dGhyZWFkMTQ3Y2FuZGxlMTQ3"),
    ("thread147thread147", "dGhyZWFkMTQ3dGhyZWFkMTQ3"),
    ("thread147kitten147", "dGhyZWFkMTQ3a2l0dGVuMTQ3"),
    (
        "round 147: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTQ3OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 147: agentuniverse is a framework for multi agents",
        "cm91bmQgMTQ3OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 147: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTQ3OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 147: the processor reads the record then stops",
        "cm91bmQgMTQ3OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 147: a worker pulls the next task from the queue",
        "cm91bmQgMTQ3OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 147: signals travel through the network layer",
        "cm91bmQgMTQ3OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 147: the gateway routes each request by policy",
        "cm91bmQgMTQ3OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 147: memory grows until the buffer is full",
        "cm91bmQgMTQ3OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 147: the cluster mirrors every packet twice",
        "cm91bmQgMTQ3OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 147: ranking uses tokens learned from the corpus",
        "cm91bmQgMTQ3OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 147: a long session ends when the candle dies",
        "cm91bmQgMTQ3OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 147: encode the prompt then map the result",
        "cm91bmQgMTQ3OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 147: the kernel wakes the worker at dawn",
        "cm91bmQgMTQ3OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 147: service latency drops after the patch",
        "cm91bmQgMTQ3OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 147: the library caches every vector it sees",
        "cm91bmQgMTQ3OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 147: agents argue then the debate resolves",
        "cm91bmQgMTQ3OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 147: the filter keeps only strong matches",
        "cm91bmQgMTQ3OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 147: the model answers with a short reply",
        "cm91bmQgMTQ3OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 147: the recorder stores the reasoning trace",
        "cm91bmQgMTQ3OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 147: the angel watches the processor run",
        "cm91bmQgMTQ3OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 147: angle of the vector decides the match",
        "cm91bmQgMTQ3OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 147: the candle burns twice as long at night",
        "cm91bmQgMTQ3OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 147: a mirror of the universe in one line",
        "cm91bmQgMTQ3OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 147: the queue drains before the storm", "cm91bmQgMTQ3OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
