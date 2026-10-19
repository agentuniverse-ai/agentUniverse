"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten187kitten187", "a2l0dGVuMTg3a2l0dGVuMTg3"),
    ("kitten187sitting187", "a2l0dGVuMTg3c2l0dGluZzE4Nw"),
    ("kitten187agent187", "a2l0dGVuMTg3YWdlbnQxODc"),
    ("kitten187angle187", "a2l0dGVuMTg3YW5nbGUxODc"),
    ("sitting187angle187", "c2l0dGluZzE4N2FuZ2xlMTg3"),
    ("sitting187universe187", "c2l0dGluZzE4N3VuaXZlcnNlMTg3"),
    ("sitting187memory187", "c2l0dGluZzE4N21lbW9yeTE4Nw"),
    ("sitting187stream187", "c2l0dGluZzE4N3N0cmVhbTE4Nw"),
    ("agent187stream187", "YWdlbnQxODdzdHJlYW0xODc"),
    ("agent187context187", "YWdlbnQxODdjb250ZXh0MTg3"),
    ("agent187knowledge187", "YWdlbnQxODdrbm93bGVkZ2UxODc"),
    ("agent187vector187", "YWdlbnQxODd2ZWN0b3IxODc"),
    ("angle187vector187", "YW5nbGUxODd2ZWN0b3IxODc"),
    ("angle187processor187", "YW5nbGUxODdwcm9jZXNzb3IxODc"),
    ("angle187reasoning187", "YW5nbGUxODdyZWFzb25pbmcxODc"),
    ("angle187machine187", "YW5nbGUxODdtYWNoaW5lMTg3"),
    ("universe187machine187", "dW5pdmVyc2UxODdtYWNoaW5lMTg3"),
    ("universe187learning187", "dW5pdmVyc2UxODdsZWFybmluZzE4Nw"),
    ("universe187model187", "dW5pdmVyc2UxODdtb2RlbDE4Nw"),
    ("universe187token187", "dW5pdmVyc2UxODd0b2tlbjE4Nw"),
    ("memory187token187", "bWVtb3J5MTg3dG9rZW4xODc"),
    ("memory187prompt187", "bWVtb3J5MTg3cHJvbXB0MTg3"),
    ("memory187session187", "bWVtb3J5MTg3c2Vzc2lvbjE4Nw"),
    ("memory187library187", "bWVtb3J5MTg3bGlicmFyeTE4Nw"),
    ("stream187library187", "c3RyZWFtMTg3bGlicmFyeTE4Nw"),
    ("stream187service187", "c3RyZWFtMTg3c2VydmljZTE4Nw"),
    ("stream187gateway187", "c3RyZWFtMTg3Z2F0ZXdheTE4Nw"),
    ("stream187storage187", "c3RyZWFtMTg3c3RvcmFnZTE4Nw"),
    ("context187storage187", "Y29udGV4dDE4N3N0b3JhZ2UxODc"),
    ("context187network187", "Y29udGV4dDE4N25ldHdvcmsxODc"),
    ("context187latency187", "Y29udGV4dDE4N2xhdGVuY3kxODc"),
    ("context187buffer187", "Y29udGV4dDE4N2J1ZmZlcjE4Nw"),
    ("knowledge187buffer187", "a25vd2xlZGdlMTg3YnVmZmVyMTg3"),
    ("knowledge187queue187", "a25vd2xlZGdlMTg3cXVldWUxODc"),
    ("knowledge187worker187", "a25vd2xlZGdlMTg3d29ya2VyMTg3"),
    ("knowledge187kernel187", "a25vd2xlZGdlMTg3a2VybmVsMTg3"),
    ("vector187kernel187", "dmVjdG9yMTg3a2VybmVsMTg3"),
    ("vector187signal187", "dmVjdG9yMTg3c2lnbmFsMTg3"),
    ("vector187packet187", "dmVjdG9yMTg3cGFja2V0MTg3"),
    ("vector187router187", "dmVjdG9yMTg3cm91dGVyMTg3"),
    ("processor187router187", "cHJvY2Vzc29yMTg3cm91dGVyMTg3"),
    ("processor187cluster187", "cHJvY2Vzc29yMTg3Y2x1c3RlcjE4Nw"),
    ("processor187mirror187", "cHJvY2Vzc29yMTg3bWlycm9yMTg3"),
    ("processor187filter187", "cHJvY2Vzc29yMTg3ZmlsdGVyMTg3"),
    ("reasoning187filter187", "cmVhc29uaW5nMTg3ZmlsdGVyMTg3"),
    ("reasoning187ranking187", "cmVhc29uaW5nMTg3cmFua2luZzE4Nw"),
    ("reasoning187encoding187", "cmVhc29uaW5nMTg3ZW5jb2RpbmcxODc"),
    ("reasoning187mapping187", "cmVhc29uaW5nMTg3bWFwcGluZzE4Nw"),
    ("machine187mapping187", "bWFjaGluZTE4N21hcHBpbmcxODc"),
    ("machine187record187", "bWFjaGluZTE4N3JlY29yZDE4Nw"),
    ("machine187candle187", "bWFjaGluZTE4N2NhbmRsZTE4Nw"),
    ("machine187thread187", "bWFjaGluZTE4N3RocmVhZDE4Nw"),
    ("learning187thread187", "bGVhcm5pbmcxODd0aHJlYWQxODc"),
    ("learning187kitten187", "bGVhcm5pbmcxODdraXR0ZW4xODc"),
    ("learning187sitting187", "bGVhcm5pbmcxODdzaXR0aW5nMTg3"),
    ("learning187agent187", "bGVhcm5pbmcxODdhZ2VudDE4Nw"),
    ("model187agent187", "bW9kZWwxODdhZ2VudDE4Nw"),
    ("model187angle187", "bW9kZWwxODdhbmdsZTE4Nw"),
    ("model187universe187", "bW9kZWwxODd1bml2ZXJzZTE4Nw"),
    ("model187memory187", "bW9kZWwxODdtZW1vcnkxODc"),
    ("token187memory187", "dG9rZW4xODdtZW1vcnkxODc"),
    ("token187stream187", "dG9rZW4xODdzdHJlYW0xODc"),
    ("token187context187", "dG9rZW4xODdjb250ZXh0MTg3"),
    ("token187knowledge187", "dG9rZW4xODdrbm93bGVkZ2UxODc"),
    ("prompt187knowledge187", "cHJvbXB0MTg3a25vd2xlZGdlMTg3"),
    ("prompt187vector187", "cHJvbXB0MTg3dmVjdG9yMTg3"),
    ("prompt187processor187", "cHJvbXB0MTg3cHJvY2Vzc29yMTg3"),
    ("prompt187reasoning187", "cHJvbXB0MTg3cmVhc29uaW5nMTg3"),
    ("session187reasoning187", "c2Vzc2lvbjE4N3JlYXNvbmluZzE4Nw"),
    ("session187machine187", "c2Vzc2lvbjE4N21hY2hpbmUxODc"),
    ("session187learning187", "c2Vzc2lvbjE4N2xlYXJuaW5nMTg3"),
    ("session187model187", "c2Vzc2lvbjE4N21vZGVsMTg3"),
    ("library187model187", "bGlicmFyeTE4N21vZGVsMTg3"),
    ("library187token187", "bGlicmFyeTE4N3Rva2VuMTg3"),
    ("library187prompt187", "bGlicmFyeTE4N3Byb21wdDE4Nw"),
    ("library187session187", "bGlicmFyeTE4N3Nlc3Npb24xODc"),
    ("service187session187", "c2VydmljZTE4N3Nlc3Npb24xODc"),
    ("service187library187", "c2VydmljZTE4N2xpYnJhcnkxODc"),
    ("service187service187", "c2VydmljZTE4N3NlcnZpY2UxODc"),
    ("service187gateway187", "c2VydmljZTE4N2dhdGV3YXkxODc"),
    ("gateway187gateway187", "Z2F0ZXdheTE4N2dhdGV3YXkxODc"),
    ("gateway187storage187", "Z2F0ZXdheTE4N3N0b3JhZ2UxODc"),
    ("gateway187network187", "Z2F0ZXdheTE4N25ldHdvcmsxODc"),
    ("gateway187latency187", "Z2F0ZXdheTE4N2xhdGVuY3kxODc"),
    ("storage187latency187", "c3RvcmFnZTE4N2xhdGVuY3kxODc"),
    ("storage187buffer187", "c3RvcmFnZTE4N2J1ZmZlcjE4Nw"),
    ("storage187queue187", "c3RvcmFnZTE4N3F1ZXVlMTg3"),
    ("storage187worker187", "c3RvcmFnZTE4N3dvcmtlcjE4Nw"),
    ("network187worker187", "bmV0d29yazE4N3dvcmtlcjE4Nw"),
    ("network187kernel187", "bmV0d29yazE4N2tlcm5lbDE4Nw"),
    ("network187signal187", "bmV0d29yazE4N3NpZ25hbDE4Nw"),
    ("network187packet187", "bmV0d29yazE4N3BhY2tldDE4Nw"),
    ("latency187packet187", "bGF0ZW5jeTE4N3BhY2tldDE4Nw"),
    ("latency187router187", "bGF0ZW5jeTE4N3JvdXRlcjE4Nw"),
    ("latency187cluster187", "bGF0ZW5jeTE4N2NsdXN0ZXIxODc"),
    ("latency187mirror187", "bGF0ZW5jeTE4N21pcnJvcjE4Nw"),
    ("buffer187mirror187", "YnVmZmVyMTg3bWlycm9yMTg3"),
    ("buffer187filter187", "YnVmZmVyMTg3ZmlsdGVyMTg3"),
    ("buffer187ranking187", "YnVmZmVyMTg3cmFua2luZzE4Nw"),
    ("buffer187encoding187", "YnVmZmVyMTg3ZW5jb2RpbmcxODc"),
    ("queue187encoding187", "cXVldWUxODdlbmNvZGluZzE4Nw"),
    ("queue187mapping187", "cXVldWUxODdtYXBwaW5nMTg3"),
    ("queue187record187", "cXVldWUxODdyZWNvcmQxODc"),
    ("queue187candle187", "cXVldWUxODdjYW5kbGUxODc"),
    ("worker187candle187", "d29ya2VyMTg3Y2FuZGxlMTg3"),
    ("worker187thread187", "d29ya2VyMTg3dGhyZWFkMTg3"),
    ("worker187kitten187", "d29ya2VyMTg3a2l0dGVuMTg3"),
    ("worker187sitting187", "d29ya2VyMTg3c2l0dGluZzE4Nw"),
    ("kernel187sitting187", "a2VybmVsMTg3c2l0dGluZzE4Nw"),
    ("kernel187agent187", "a2VybmVsMTg3YWdlbnQxODc"),
    ("kernel187angle187", "a2VybmVsMTg3YW5nbGUxODc"),
    ("kernel187universe187", "a2VybmVsMTg3dW5pdmVyc2UxODc"),
    ("signal187universe187", "c2lnbmFsMTg3dW5pdmVyc2UxODc"),
    ("signal187memory187", "c2lnbmFsMTg3bWVtb3J5MTg3"),
    ("signal187stream187", "c2lnbmFsMTg3c3RyZWFtMTg3"),
    ("signal187context187", "c2lnbmFsMTg3Y29udGV4dDE4Nw"),
    ("packet187context187", "cGFja2V0MTg3Y29udGV4dDE4Nw"),
    ("packet187knowledge187", "cGFja2V0MTg3a25vd2xlZGdlMTg3"),
    ("packet187vector187", "cGFja2V0MTg3dmVjdG9yMTg3"),
    ("packet187processor187", "cGFja2V0MTg3cHJvY2Vzc29yMTg3"),
    ("router187processor187", "cm91dGVyMTg3cHJvY2Vzc29yMTg3"),
    ("router187reasoning187", "cm91dGVyMTg3cmVhc29uaW5nMTg3"),
    ("router187machine187", "cm91dGVyMTg3bWFjaGluZTE4Nw"),
    ("router187learning187", "cm91dGVyMTg3bGVhcm5pbmcxODc"),
    ("cluster187learning187", "Y2x1c3RlcjE4N2xlYXJuaW5nMTg3"),
    ("cluster187model187", "Y2x1c3RlcjE4N21vZGVsMTg3"),
    ("cluster187token187", "Y2x1c3RlcjE4N3Rva2VuMTg3"),
    ("cluster187prompt187", "Y2x1c3RlcjE4N3Byb21wdDE4Nw"),
    ("mirror187prompt187", "bWlycm9yMTg3cHJvbXB0MTg3"),
    ("mirror187session187", "bWlycm9yMTg3c2Vzc2lvbjE4Nw"),
    ("mirror187library187", "bWlycm9yMTg3bGlicmFyeTE4Nw"),
    ("mirror187service187", "bWlycm9yMTg3c2VydmljZTE4Nw"),
    ("filter187service187", "ZmlsdGVyMTg3c2VydmljZTE4Nw"),
    ("filter187gateway187", "ZmlsdGVyMTg3Z2F0ZXdheTE4Nw"),
    ("filter187storage187", "ZmlsdGVyMTg3c3RvcmFnZTE4Nw"),
    ("filter187network187", "ZmlsdGVyMTg3bmV0d29yazE4Nw"),
    ("ranking187network187", "cmFua2luZzE4N25ldHdvcmsxODc"),
    ("ranking187latency187", "cmFua2luZzE4N2xhdGVuY3kxODc"),
    ("ranking187buffer187", "cmFua2luZzE4N2J1ZmZlcjE4Nw"),
    ("ranking187queue187", "cmFua2luZzE4N3F1ZXVlMTg3"),
    ("encoding187queue187", "ZW5jb2RpbmcxODdxdWV1ZTE4Nw"),
    ("encoding187worker187", "ZW5jb2RpbmcxODd3b3JrZXIxODc"),
    ("encoding187kernel187", "ZW5jb2RpbmcxODdrZXJuZWwxODc"),
    ("encoding187signal187", "ZW5jb2RpbmcxODdzaWduYWwxODc"),
    ("mapping187signal187", "bWFwcGluZzE4N3NpZ25hbDE4Nw"),
    ("mapping187packet187", "bWFwcGluZzE4N3BhY2tldDE4Nw"),
    ("mapping187router187", "bWFwcGluZzE4N3JvdXRlcjE4Nw"),
    ("mapping187cluster187", "bWFwcGluZzE4N2NsdXN0ZXIxODc"),
    ("record187cluster187", "cmVjb3JkMTg3Y2x1c3RlcjE4Nw"),
    ("record187mirror187", "cmVjb3JkMTg3bWlycm9yMTg3"),
    ("record187filter187", "cmVjb3JkMTg3ZmlsdGVyMTg3"),
    ("record187ranking187", "cmVjb3JkMTg3cmFua2luZzE4Nw"),
    ("candle187ranking187", "Y2FuZGxlMTg3cmFua2luZzE4Nw"),
    ("candle187encoding187", "Y2FuZGxlMTg3ZW5jb2RpbmcxODc"),
    ("candle187mapping187", "Y2FuZGxlMTg3bWFwcGluZzE4Nw"),
    ("candle187record187", "Y2FuZGxlMTg3cmVjb3JkMTg3"),
    ("thread187record187", "dGhyZWFkMTg3cmVjb3JkMTg3"),
    ("thread187candle187", "dGhyZWFkMTg3Y2FuZGxlMTg3"),
    ("thread187thread187", "dGhyZWFkMTg3dGhyZWFkMTg3"),
    ("thread187kitten187", "dGhyZWFkMTg3a2l0dGVuMTg3"),
    (
        "round 187: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTg3OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 187: agentuniverse is a framework for multi agents",
        "cm91bmQgMTg3OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 187: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTg3OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 187: the processor reads the record then stops",
        "cm91bmQgMTg3OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 187: a worker pulls the next task from the queue",
        "cm91bmQgMTg3OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 187: signals travel through the network layer",
        "cm91bmQgMTg3OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 187: the gateway routes each request by policy",
        "cm91bmQgMTg3OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 187: memory grows until the buffer is full",
        "cm91bmQgMTg3OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 187: the cluster mirrors every packet twice",
        "cm91bmQgMTg3OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 187: ranking uses tokens learned from the corpus",
        "cm91bmQgMTg3OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 187: a long session ends when the candle dies",
        "cm91bmQgMTg3OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 187: encode the prompt then map the result",
        "cm91bmQgMTg3OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 187: the kernel wakes the worker at dawn",
        "cm91bmQgMTg3OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 187: service latency drops after the patch",
        "cm91bmQgMTg3OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 187: the library caches every vector it sees",
        "cm91bmQgMTg3OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 187: agents argue then the debate resolves",
        "cm91bmQgMTg3OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 187: the filter keeps only strong matches",
        "cm91bmQgMTg3OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 187: the model answers with a short reply",
        "cm91bmQgMTg3OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 187: the recorder stores the reasoning trace",
        "cm91bmQgMTg3OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 187: the angel watches the processor run",
        "cm91bmQgMTg3OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 187: angle of the vector decides the match",
        "cm91bmQgMTg3OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 187: the candle burns twice as long at night",
        "cm91bmQgMTg3OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 187: a mirror of the universe in one line",
        "cm91bmQgMTg3OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 187: the queue drains before the storm", "cm91bmQgMTg3OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
