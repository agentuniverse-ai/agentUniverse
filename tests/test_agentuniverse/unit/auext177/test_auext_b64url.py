"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten177kitten177", "a2l0dGVuMTc3a2l0dGVuMTc3"),
    ("kitten177sitting177", "a2l0dGVuMTc3c2l0dGluZzE3Nw"),
    ("kitten177agent177", "a2l0dGVuMTc3YWdlbnQxNzc"),
    ("kitten177angle177", "a2l0dGVuMTc3YW5nbGUxNzc"),
    ("sitting177angle177", "c2l0dGluZzE3N2FuZ2xlMTc3"),
    ("sitting177universe177", "c2l0dGluZzE3N3VuaXZlcnNlMTc3"),
    ("sitting177memory177", "c2l0dGluZzE3N21lbW9yeTE3Nw"),
    ("sitting177stream177", "c2l0dGluZzE3N3N0cmVhbTE3Nw"),
    ("agent177stream177", "YWdlbnQxNzdzdHJlYW0xNzc"),
    ("agent177context177", "YWdlbnQxNzdjb250ZXh0MTc3"),
    ("agent177knowledge177", "YWdlbnQxNzdrbm93bGVkZ2UxNzc"),
    ("agent177vector177", "YWdlbnQxNzd2ZWN0b3IxNzc"),
    ("angle177vector177", "YW5nbGUxNzd2ZWN0b3IxNzc"),
    ("angle177processor177", "YW5nbGUxNzdwcm9jZXNzb3IxNzc"),
    ("angle177reasoning177", "YW5nbGUxNzdyZWFzb25pbmcxNzc"),
    ("angle177machine177", "YW5nbGUxNzdtYWNoaW5lMTc3"),
    ("universe177machine177", "dW5pdmVyc2UxNzdtYWNoaW5lMTc3"),
    ("universe177learning177", "dW5pdmVyc2UxNzdsZWFybmluZzE3Nw"),
    ("universe177model177", "dW5pdmVyc2UxNzdtb2RlbDE3Nw"),
    ("universe177token177", "dW5pdmVyc2UxNzd0b2tlbjE3Nw"),
    ("memory177token177", "bWVtb3J5MTc3dG9rZW4xNzc"),
    ("memory177prompt177", "bWVtb3J5MTc3cHJvbXB0MTc3"),
    ("memory177session177", "bWVtb3J5MTc3c2Vzc2lvbjE3Nw"),
    ("memory177library177", "bWVtb3J5MTc3bGlicmFyeTE3Nw"),
    ("stream177library177", "c3RyZWFtMTc3bGlicmFyeTE3Nw"),
    ("stream177service177", "c3RyZWFtMTc3c2VydmljZTE3Nw"),
    ("stream177gateway177", "c3RyZWFtMTc3Z2F0ZXdheTE3Nw"),
    ("stream177storage177", "c3RyZWFtMTc3c3RvcmFnZTE3Nw"),
    ("context177storage177", "Y29udGV4dDE3N3N0b3JhZ2UxNzc"),
    ("context177network177", "Y29udGV4dDE3N25ldHdvcmsxNzc"),
    ("context177latency177", "Y29udGV4dDE3N2xhdGVuY3kxNzc"),
    ("context177buffer177", "Y29udGV4dDE3N2J1ZmZlcjE3Nw"),
    ("knowledge177buffer177", "a25vd2xlZGdlMTc3YnVmZmVyMTc3"),
    ("knowledge177queue177", "a25vd2xlZGdlMTc3cXVldWUxNzc"),
    ("knowledge177worker177", "a25vd2xlZGdlMTc3d29ya2VyMTc3"),
    ("knowledge177kernel177", "a25vd2xlZGdlMTc3a2VybmVsMTc3"),
    ("vector177kernel177", "dmVjdG9yMTc3a2VybmVsMTc3"),
    ("vector177signal177", "dmVjdG9yMTc3c2lnbmFsMTc3"),
    ("vector177packet177", "dmVjdG9yMTc3cGFja2V0MTc3"),
    ("vector177router177", "dmVjdG9yMTc3cm91dGVyMTc3"),
    ("processor177router177", "cHJvY2Vzc29yMTc3cm91dGVyMTc3"),
    ("processor177cluster177", "cHJvY2Vzc29yMTc3Y2x1c3RlcjE3Nw"),
    ("processor177mirror177", "cHJvY2Vzc29yMTc3bWlycm9yMTc3"),
    ("processor177filter177", "cHJvY2Vzc29yMTc3ZmlsdGVyMTc3"),
    ("reasoning177filter177", "cmVhc29uaW5nMTc3ZmlsdGVyMTc3"),
    ("reasoning177ranking177", "cmVhc29uaW5nMTc3cmFua2luZzE3Nw"),
    ("reasoning177encoding177", "cmVhc29uaW5nMTc3ZW5jb2RpbmcxNzc"),
    ("reasoning177mapping177", "cmVhc29uaW5nMTc3bWFwcGluZzE3Nw"),
    ("machine177mapping177", "bWFjaGluZTE3N21hcHBpbmcxNzc"),
    ("machine177record177", "bWFjaGluZTE3N3JlY29yZDE3Nw"),
    ("machine177candle177", "bWFjaGluZTE3N2NhbmRsZTE3Nw"),
    ("machine177thread177", "bWFjaGluZTE3N3RocmVhZDE3Nw"),
    ("learning177thread177", "bGVhcm5pbmcxNzd0aHJlYWQxNzc"),
    ("learning177kitten177", "bGVhcm5pbmcxNzdraXR0ZW4xNzc"),
    ("learning177sitting177", "bGVhcm5pbmcxNzdzaXR0aW5nMTc3"),
    ("learning177agent177", "bGVhcm5pbmcxNzdhZ2VudDE3Nw"),
    ("model177agent177", "bW9kZWwxNzdhZ2VudDE3Nw"),
    ("model177angle177", "bW9kZWwxNzdhbmdsZTE3Nw"),
    ("model177universe177", "bW9kZWwxNzd1bml2ZXJzZTE3Nw"),
    ("model177memory177", "bW9kZWwxNzdtZW1vcnkxNzc"),
    ("token177memory177", "dG9rZW4xNzdtZW1vcnkxNzc"),
    ("token177stream177", "dG9rZW4xNzdzdHJlYW0xNzc"),
    ("token177context177", "dG9rZW4xNzdjb250ZXh0MTc3"),
    ("token177knowledge177", "dG9rZW4xNzdrbm93bGVkZ2UxNzc"),
    ("prompt177knowledge177", "cHJvbXB0MTc3a25vd2xlZGdlMTc3"),
    ("prompt177vector177", "cHJvbXB0MTc3dmVjdG9yMTc3"),
    ("prompt177processor177", "cHJvbXB0MTc3cHJvY2Vzc29yMTc3"),
    ("prompt177reasoning177", "cHJvbXB0MTc3cmVhc29uaW5nMTc3"),
    ("session177reasoning177", "c2Vzc2lvbjE3N3JlYXNvbmluZzE3Nw"),
    ("session177machine177", "c2Vzc2lvbjE3N21hY2hpbmUxNzc"),
    ("session177learning177", "c2Vzc2lvbjE3N2xlYXJuaW5nMTc3"),
    ("session177model177", "c2Vzc2lvbjE3N21vZGVsMTc3"),
    ("library177model177", "bGlicmFyeTE3N21vZGVsMTc3"),
    ("library177token177", "bGlicmFyeTE3N3Rva2VuMTc3"),
    ("library177prompt177", "bGlicmFyeTE3N3Byb21wdDE3Nw"),
    ("library177session177", "bGlicmFyeTE3N3Nlc3Npb24xNzc"),
    ("service177session177", "c2VydmljZTE3N3Nlc3Npb24xNzc"),
    ("service177library177", "c2VydmljZTE3N2xpYnJhcnkxNzc"),
    ("service177service177", "c2VydmljZTE3N3NlcnZpY2UxNzc"),
    ("service177gateway177", "c2VydmljZTE3N2dhdGV3YXkxNzc"),
    ("gateway177gateway177", "Z2F0ZXdheTE3N2dhdGV3YXkxNzc"),
    ("gateway177storage177", "Z2F0ZXdheTE3N3N0b3JhZ2UxNzc"),
    ("gateway177network177", "Z2F0ZXdheTE3N25ldHdvcmsxNzc"),
    ("gateway177latency177", "Z2F0ZXdheTE3N2xhdGVuY3kxNzc"),
    ("storage177latency177", "c3RvcmFnZTE3N2xhdGVuY3kxNzc"),
    ("storage177buffer177", "c3RvcmFnZTE3N2J1ZmZlcjE3Nw"),
    ("storage177queue177", "c3RvcmFnZTE3N3F1ZXVlMTc3"),
    ("storage177worker177", "c3RvcmFnZTE3N3dvcmtlcjE3Nw"),
    ("network177worker177", "bmV0d29yazE3N3dvcmtlcjE3Nw"),
    ("network177kernel177", "bmV0d29yazE3N2tlcm5lbDE3Nw"),
    ("network177signal177", "bmV0d29yazE3N3NpZ25hbDE3Nw"),
    ("network177packet177", "bmV0d29yazE3N3BhY2tldDE3Nw"),
    ("latency177packet177", "bGF0ZW5jeTE3N3BhY2tldDE3Nw"),
    ("latency177router177", "bGF0ZW5jeTE3N3JvdXRlcjE3Nw"),
    ("latency177cluster177", "bGF0ZW5jeTE3N2NsdXN0ZXIxNzc"),
    ("latency177mirror177", "bGF0ZW5jeTE3N21pcnJvcjE3Nw"),
    ("buffer177mirror177", "YnVmZmVyMTc3bWlycm9yMTc3"),
    ("buffer177filter177", "YnVmZmVyMTc3ZmlsdGVyMTc3"),
    ("buffer177ranking177", "YnVmZmVyMTc3cmFua2luZzE3Nw"),
    ("buffer177encoding177", "YnVmZmVyMTc3ZW5jb2RpbmcxNzc"),
    ("queue177encoding177", "cXVldWUxNzdlbmNvZGluZzE3Nw"),
    ("queue177mapping177", "cXVldWUxNzdtYXBwaW5nMTc3"),
    ("queue177record177", "cXVldWUxNzdyZWNvcmQxNzc"),
    ("queue177candle177", "cXVldWUxNzdjYW5kbGUxNzc"),
    ("worker177candle177", "d29ya2VyMTc3Y2FuZGxlMTc3"),
    ("worker177thread177", "d29ya2VyMTc3dGhyZWFkMTc3"),
    ("worker177kitten177", "d29ya2VyMTc3a2l0dGVuMTc3"),
    ("worker177sitting177", "d29ya2VyMTc3c2l0dGluZzE3Nw"),
    ("kernel177sitting177", "a2VybmVsMTc3c2l0dGluZzE3Nw"),
    ("kernel177agent177", "a2VybmVsMTc3YWdlbnQxNzc"),
    ("kernel177angle177", "a2VybmVsMTc3YW5nbGUxNzc"),
    ("kernel177universe177", "a2VybmVsMTc3dW5pdmVyc2UxNzc"),
    ("signal177universe177", "c2lnbmFsMTc3dW5pdmVyc2UxNzc"),
    ("signal177memory177", "c2lnbmFsMTc3bWVtb3J5MTc3"),
    ("signal177stream177", "c2lnbmFsMTc3c3RyZWFtMTc3"),
    ("signal177context177", "c2lnbmFsMTc3Y29udGV4dDE3Nw"),
    ("packet177context177", "cGFja2V0MTc3Y29udGV4dDE3Nw"),
    ("packet177knowledge177", "cGFja2V0MTc3a25vd2xlZGdlMTc3"),
    ("packet177vector177", "cGFja2V0MTc3dmVjdG9yMTc3"),
    ("packet177processor177", "cGFja2V0MTc3cHJvY2Vzc29yMTc3"),
    ("router177processor177", "cm91dGVyMTc3cHJvY2Vzc29yMTc3"),
    ("router177reasoning177", "cm91dGVyMTc3cmVhc29uaW5nMTc3"),
    ("router177machine177", "cm91dGVyMTc3bWFjaGluZTE3Nw"),
    ("router177learning177", "cm91dGVyMTc3bGVhcm5pbmcxNzc"),
    ("cluster177learning177", "Y2x1c3RlcjE3N2xlYXJuaW5nMTc3"),
    ("cluster177model177", "Y2x1c3RlcjE3N21vZGVsMTc3"),
    ("cluster177token177", "Y2x1c3RlcjE3N3Rva2VuMTc3"),
    ("cluster177prompt177", "Y2x1c3RlcjE3N3Byb21wdDE3Nw"),
    ("mirror177prompt177", "bWlycm9yMTc3cHJvbXB0MTc3"),
    ("mirror177session177", "bWlycm9yMTc3c2Vzc2lvbjE3Nw"),
    ("mirror177library177", "bWlycm9yMTc3bGlicmFyeTE3Nw"),
    ("mirror177service177", "bWlycm9yMTc3c2VydmljZTE3Nw"),
    ("filter177service177", "ZmlsdGVyMTc3c2VydmljZTE3Nw"),
    ("filter177gateway177", "ZmlsdGVyMTc3Z2F0ZXdheTE3Nw"),
    ("filter177storage177", "ZmlsdGVyMTc3c3RvcmFnZTE3Nw"),
    ("filter177network177", "ZmlsdGVyMTc3bmV0d29yazE3Nw"),
    ("ranking177network177", "cmFua2luZzE3N25ldHdvcmsxNzc"),
    ("ranking177latency177", "cmFua2luZzE3N2xhdGVuY3kxNzc"),
    ("ranking177buffer177", "cmFua2luZzE3N2J1ZmZlcjE3Nw"),
    ("ranking177queue177", "cmFua2luZzE3N3F1ZXVlMTc3"),
    ("encoding177queue177", "ZW5jb2RpbmcxNzdxdWV1ZTE3Nw"),
    ("encoding177worker177", "ZW5jb2RpbmcxNzd3b3JrZXIxNzc"),
    ("encoding177kernel177", "ZW5jb2RpbmcxNzdrZXJuZWwxNzc"),
    ("encoding177signal177", "ZW5jb2RpbmcxNzdzaWduYWwxNzc"),
    ("mapping177signal177", "bWFwcGluZzE3N3NpZ25hbDE3Nw"),
    ("mapping177packet177", "bWFwcGluZzE3N3BhY2tldDE3Nw"),
    ("mapping177router177", "bWFwcGluZzE3N3JvdXRlcjE3Nw"),
    ("mapping177cluster177", "bWFwcGluZzE3N2NsdXN0ZXIxNzc"),
    ("record177cluster177", "cmVjb3JkMTc3Y2x1c3RlcjE3Nw"),
    ("record177mirror177", "cmVjb3JkMTc3bWlycm9yMTc3"),
    ("record177filter177", "cmVjb3JkMTc3ZmlsdGVyMTc3"),
    ("record177ranking177", "cmVjb3JkMTc3cmFua2luZzE3Nw"),
    ("candle177ranking177", "Y2FuZGxlMTc3cmFua2luZzE3Nw"),
    ("candle177encoding177", "Y2FuZGxlMTc3ZW5jb2RpbmcxNzc"),
    ("candle177mapping177", "Y2FuZGxlMTc3bWFwcGluZzE3Nw"),
    ("candle177record177", "Y2FuZGxlMTc3cmVjb3JkMTc3"),
    ("thread177record177", "dGhyZWFkMTc3cmVjb3JkMTc3"),
    ("thread177candle177", "dGhyZWFkMTc3Y2FuZGxlMTc3"),
    ("thread177thread177", "dGhyZWFkMTc3dGhyZWFkMTc3"),
    ("thread177kitten177", "dGhyZWFkMTc3a2l0dGVuMTc3"),
    (
        "round 177: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTc3OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 177: agentuniverse is a framework for multi agents",
        "cm91bmQgMTc3OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 177: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTc3OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 177: the processor reads the record then stops",
        "cm91bmQgMTc3OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 177: a worker pulls the next task from the queue",
        "cm91bmQgMTc3OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 177: signals travel through the network layer",
        "cm91bmQgMTc3OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 177: the gateway routes each request by policy",
        "cm91bmQgMTc3OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 177: memory grows until the buffer is full",
        "cm91bmQgMTc3OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 177: the cluster mirrors every packet twice",
        "cm91bmQgMTc3OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 177: ranking uses tokens learned from the corpus",
        "cm91bmQgMTc3OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 177: a long session ends when the candle dies",
        "cm91bmQgMTc3OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 177: encode the prompt then map the result",
        "cm91bmQgMTc3OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 177: the kernel wakes the worker at dawn",
        "cm91bmQgMTc3OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 177: service latency drops after the patch",
        "cm91bmQgMTc3OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 177: the library caches every vector it sees",
        "cm91bmQgMTc3OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 177: agents argue then the debate resolves",
        "cm91bmQgMTc3OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 177: the filter keeps only strong matches",
        "cm91bmQgMTc3OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 177: the model answers with a short reply",
        "cm91bmQgMTc3OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 177: the recorder stores the reasoning trace",
        "cm91bmQgMTc3OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 177: the angel watches the processor run",
        "cm91bmQgMTc3OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 177: angle of the vector decides the match",
        "cm91bmQgMTc3OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 177: the candle burns twice as long at night",
        "cm91bmQgMTc3OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 177: a mirror of the universe in one line",
        "cm91bmQgMTc3OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 177: the queue drains before the storm", "cm91bmQgMTc3OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
