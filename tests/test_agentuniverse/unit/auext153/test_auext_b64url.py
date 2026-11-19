"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten153kitten153", "a2l0dGVuMTUza2l0dGVuMTUz"),
    ("kitten153sitting153", "a2l0dGVuMTUzc2l0dGluZzE1Mw"),
    ("kitten153agent153", "a2l0dGVuMTUzYWdlbnQxNTM"),
    ("kitten153angle153", "a2l0dGVuMTUzYW5nbGUxNTM"),
    ("sitting153angle153", "c2l0dGluZzE1M2FuZ2xlMTUz"),
    ("sitting153universe153", "c2l0dGluZzE1M3VuaXZlcnNlMTUz"),
    ("sitting153memory153", "c2l0dGluZzE1M21lbW9yeTE1Mw"),
    ("sitting153stream153", "c2l0dGluZzE1M3N0cmVhbTE1Mw"),
    ("agent153stream153", "YWdlbnQxNTNzdHJlYW0xNTM"),
    ("agent153context153", "YWdlbnQxNTNjb250ZXh0MTUz"),
    ("agent153knowledge153", "YWdlbnQxNTNrbm93bGVkZ2UxNTM"),
    ("agent153vector153", "YWdlbnQxNTN2ZWN0b3IxNTM"),
    ("angle153vector153", "YW5nbGUxNTN2ZWN0b3IxNTM"),
    ("angle153processor153", "YW5nbGUxNTNwcm9jZXNzb3IxNTM"),
    ("angle153reasoning153", "YW5nbGUxNTNyZWFzb25pbmcxNTM"),
    ("angle153machine153", "YW5nbGUxNTNtYWNoaW5lMTUz"),
    ("universe153machine153", "dW5pdmVyc2UxNTNtYWNoaW5lMTUz"),
    ("universe153learning153", "dW5pdmVyc2UxNTNsZWFybmluZzE1Mw"),
    ("universe153model153", "dW5pdmVyc2UxNTNtb2RlbDE1Mw"),
    ("universe153token153", "dW5pdmVyc2UxNTN0b2tlbjE1Mw"),
    ("memory153token153", "bWVtb3J5MTUzdG9rZW4xNTM"),
    ("memory153prompt153", "bWVtb3J5MTUzcHJvbXB0MTUz"),
    ("memory153session153", "bWVtb3J5MTUzc2Vzc2lvbjE1Mw"),
    ("memory153library153", "bWVtb3J5MTUzbGlicmFyeTE1Mw"),
    ("stream153library153", "c3RyZWFtMTUzbGlicmFyeTE1Mw"),
    ("stream153service153", "c3RyZWFtMTUzc2VydmljZTE1Mw"),
    ("stream153gateway153", "c3RyZWFtMTUzZ2F0ZXdheTE1Mw"),
    ("stream153storage153", "c3RyZWFtMTUzc3RvcmFnZTE1Mw"),
    ("context153storage153", "Y29udGV4dDE1M3N0b3JhZ2UxNTM"),
    ("context153network153", "Y29udGV4dDE1M25ldHdvcmsxNTM"),
    ("context153latency153", "Y29udGV4dDE1M2xhdGVuY3kxNTM"),
    ("context153buffer153", "Y29udGV4dDE1M2J1ZmZlcjE1Mw"),
    ("knowledge153buffer153", "a25vd2xlZGdlMTUzYnVmZmVyMTUz"),
    ("knowledge153queue153", "a25vd2xlZGdlMTUzcXVldWUxNTM"),
    ("knowledge153worker153", "a25vd2xlZGdlMTUzd29ya2VyMTUz"),
    ("knowledge153kernel153", "a25vd2xlZGdlMTUza2VybmVsMTUz"),
    ("vector153kernel153", "dmVjdG9yMTUza2VybmVsMTUz"),
    ("vector153signal153", "dmVjdG9yMTUzc2lnbmFsMTUz"),
    ("vector153packet153", "dmVjdG9yMTUzcGFja2V0MTUz"),
    ("vector153router153", "dmVjdG9yMTUzcm91dGVyMTUz"),
    ("processor153router153", "cHJvY2Vzc29yMTUzcm91dGVyMTUz"),
    ("processor153cluster153", "cHJvY2Vzc29yMTUzY2x1c3RlcjE1Mw"),
    ("processor153mirror153", "cHJvY2Vzc29yMTUzbWlycm9yMTUz"),
    ("processor153filter153", "cHJvY2Vzc29yMTUzZmlsdGVyMTUz"),
    ("reasoning153filter153", "cmVhc29uaW5nMTUzZmlsdGVyMTUz"),
    ("reasoning153ranking153", "cmVhc29uaW5nMTUzcmFua2luZzE1Mw"),
    ("reasoning153encoding153", "cmVhc29uaW5nMTUzZW5jb2RpbmcxNTM"),
    ("reasoning153mapping153", "cmVhc29uaW5nMTUzbWFwcGluZzE1Mw"),
    ("machine153mapping153", "bWFjaGluZTE1M21hcHBpbmcxNTM"),
    ("machine153record153", "bWFjaGluZTE1M3JlY29yZDE1Mw"),
    ("machine153candle153", "bWFjaGluZTE1M2NhbmRsZTE1Mw"),
    ("machine153thread153", "bWFjaGluZTE1M3RocmVhZDE1Mw"),
    ("learning153thread153", "bGVhcm5pbmcxNTN0aHJlYWQxNTM"),
    ("learning153kitten153", "bGVhcm5pbmcxNTNraXR0ZW4xNTM"),
    ("learning153sitting153", "bGVhcm5pbmcxNTNzaXR0aW5nMTUz"),
    ("learning153agent153", "bGVhcm5pbmcxNTNhZ2VudDE1Mw"),
    ("model153agent153", "bW9kZWwxNTNhZ2VudDE1Mw"),
    ("model153angle153", "bW9kZWwxNTNhbmdsZTE1Mw"),
    ("model153universe153", "bW9kZWwxNTN1bml2ZXJzZTE1Mw"),
    ("model153memory153", "bW9kZWwxNTNtZW1vcnkxNTM"),
    ("token153memory153", "dG9rZW4xNTNtZW1vcnkxNTM"),
    ("token153stream153", "dG9rZW4xNTNzdHJlYW0xNTM"),
    ("token153context153", "dG9rZW4xNTNjb250ZXh0MTUz"),
    ("token153knowledge153", "dG9rZW4xNTNrbm93bGVkZ2UxNTM"),
    ("prompt153knowledge153", "cHJvbXB0MTUza25vd2xlZGdlMTUz"),
    ("prompt153vector153", "cHJvbXB0MTUzdmVjdG9yMTUz"),
    ("prompt153processor153", "cHJvbXB0MTUzcHJvY2Vzc29yMTUz"),
    ("prompt153reasoning153", "cHJvbXB0MTUzcmVhc29uaW5nMTUz"),
    ("session153reasoning153", "c2Vzc2lvbjE1M3JlYXNvbmluZzE1Mw"),
    ("session153machine153", "c2Vzc2lvbjE1M21hY2hpbmUxNTM"),
    ("session153learning153", "c2Vzc2lvbjE1M2xlYXJuaW5nMTUz"),
    ("session153model153", "c2Vzc2lvbjE1M21vZGVsMTUz"),
    ("library153model153", "bGlicmFyeTE1M21vZGVsMTUz"),
    ("library153token153", "bGlicmFyeTE1M3Rva2VuMTUz"),
    ("library153prompt153", "bGlicmFyeTE1M3Byb21wdDE1Mw"),
    ("library153session153", "bGlicmFyeTE1M3Nlc3Npb24xNTM"),
    ("service153session153", "c2VydmljZTE1M3Nlc3Npb24xNTM"),
    ("service153library153", "c2VydmljZTE1M2xpYnJhcnkxNTM"),
    ("service153service153", "c2VydmljZTE1M3NlcnZpY2UxNTM"),
    ("service153gateway153", "c2VydmljZTE1M2dhdGV3YXkxNTM"),
    ("gateway153gateway153", "Z2F0ZXdheTE1M2dhdGV3YXkxNTM"),
    ("gateway153storage153", "Z2F0ZXdheTE1M3N0b3JhZ2UxNTM"),
    ("gateway153network153", "Z2F0ZXdheTE1M25ldHdvcmsxNTM"),
    ("gateway153latency153", "Z2F0ZXdheTE1M2xhdGVuY3kxNTM"),
    ("storage153latency153", "c3RvcmFnZTE1M2xhdGVuY3kxNTM"),
    ("storage153buffer153", "c3RvcmFnZTE1M2J1ZmZlcjE1Mw"),
    ("storage153queue153", "c3RvcmFnZTE1M3F1ZXVlMTUz"),
    ("storage153worker153", "c3RvcmFnZTE1M3dvcmtlcjE1Mw"),
    ("network153worker153", "bmV0d29yazE1M3dvcmtlcjE1Mw"),
    ("network153kernel153", "bmV0d29yazE1M2tlcm5lbDE1Mw"),
    ("network153signal153", "bmV0d29yazE1M3NpZ25hbDE1Mw"),
    ("network153packet153", "bmV0d29yazE1M3BhY2tldDE1Mw"),
    ("latency153packet153", "bGF0ZW5jeTE1M3BhY2tldDE1Mw"),
    ("latency153router153", "bGF0ZW5jeTE1M3JvdXRlcjE1Mw"),
    ("latency153cluster153", "bGF0ZW5jeTE1M2NsdXN0ZXIxNTM"),
    ("latency153mirror153", "bGF0ZW5jeTE1M21pcnJvcjE1Mw"),
    ("buffer153mirror153", "YnVmZmVyMTUzbWlycm9yMTUz"),
    ("buffer153filter153", "YnVmZmVyMTUzZmlsdGVyMTUz"),
    ("buffer153ranking153", "YnVmZmVyMTUzcmFua2luZzE1Mw"),
    ("buffer153encoding153", "YnVmZmVyMTUzZW5jb2RpbmcxNTM"),
    ("queue153encoding153", "cXVldWUxNTNlbmNvZGluZzE1Mw"),
    ("queue153mapping153", "cXVldWUxNTNtYXBwaW5nMTUz"),
    ("queue153record153", "cXVldWUxNTNyZWNvcmQxNTM"),
    ("queue153candle153", "cXVldWUxNTNjYW5kbGUxNTM"),
    ("worker153candle153", "d29ya2VyMTUzY2FuZGxlMTUz"),
    ("worker153thread153", "d29ya2VyMTUzdGhyZWFkMTUz"),
    ("worker153kitten153", "d29ya2VyMTUza2l0dGVuMTUz"),
    ("worker153sitting153", "d29ya2VyMTUzc2l0dGluZzE1Mw"),
    ("kernel153sitting153", "a2VybmVsMTUzc2l0dGluZzE1Mw"),
    ("kernel153agent153", "a2VybmVsMTUzYWdlbnQxNTM"),
    ("kernel153angle153", "a2VybmVsMTUzYW5nbGUxNTM"),
    ("kernel153universe153", "a2VybmVsMTUzdW5pdmVyc2UxNTM"),
    ("signal153universe153", "c2lnbmFsMTUzdW5pdmVyc2UxNTM"),
    ("signal153memory153", "c2lnbmFsMTUzbWVtb3J5MTUz"),
    ("signal153stream153", "c2lnbmFsMTUzc3RyZWFtMTUz"),
    ("signal153context153", "c2lnbmFsMTUzY29udGV4dDE1Mw"),
    ("packet153context153", "cGFja2V0MTUzY29udGV4dDE1Mw"),
    ("packet153knowledge153", "cGFja2V0MTUza25vd2xlZGdlMTUz"),
    ("packet153vector153", "cGFja2V0MTUzdmVjdG9yMTUz"),
    ("packet153processor153", "cGFja2V0MTUzcHJvY2Vzc29yMTUz"),
    ("router153processor153", "cm91dGVyMTUzcHJvY2Vzc29yMTUz"),
    ("router153reasoning153", "cm91dGVyMTUzcmVhc29uaW5nMTUz"),
    ("router153machine153", "cm91dGVyMTUzbWFjaGluZTE1Mw"),
    ("router153learning153", "cm91dGVyMTUzbGVhcm5pbmcxNTM"),
    ("cluster153learning153", "Y2x1c3RlcjE1M2xlYXJuaW5nMTUz"),
    ("cluster153model153", "Y2x1c3RlcjE1M21vZGVsMTUz"),
    ("cluster153token153", "Y2x1c3RlcjE1M3Rva2VuMTUz"),
    ("cluster153prompt153", "Y2x1c3RlcjE1M3Byb21wdDE1Mw"),
    ("mirror153prompt153", "bWlycm9yMTUzcHJvbXB0MTUz"),
    ("mirror153session153", "bWlycm9yMTUzc2Vzc2lvbjE1Mw"),
    ("mirror153library153", "bWlycm9yMTUzbGlicmFyeTE1Mw"),
    ("mirror153service153", "bWlycm9yMTUzc2VydmljZTE1Mw"),
    ("filter153service153", "ZmlsdGVyMTUzc2VydmljZTE1Mw"),
    ("filter153gateway153", "ZmlsdGVyMTUzZ2F0ZXdheTE1Mw"),
    ("filter153storage153", "ZmlsdGVyMTUzc3RvcmFnZTE1Mw"),
    ("filter153network153", "ZmlsdGVyMTUzbmV0d29yazE1Mw"),
    ("ranking153network153", "cmFua2luZzE1M25ldHdvcmsxNTM"),
    ("ranking153latency153", "cmFua2luZzE1M2xhdGVuY3kxNTM"),
    ("ranking153buffer153", "cmFua2luZzE1M2J1ZmZlcjE1Mw"),
    ("ranking153queue153", "cmFua2luZzE1M3F1ZXVlMTUz"),
    ("encoding153queue153", "ZW5jb2RpbmcxNTNxdWV1ZTE1Mw"),
    ("encoding153worker153", "ZW5jb2RpbmcxNTN3b3JrZXIxNTM"),
    ("encoding153kernel153", "ZW5jb2RpbmcxNTNrZXJuZWwxNTM"),
    ("encoding153signal153", "ZW5jb2RpbmcxNTNzaWduYWwxNTM"),
    ("mapping153signal153", "bWFwcGluZzE1M3NpZ25hbDE1Mw"),
    ("mapping153packet153", "bWFwcGluZzE1M3BhY2tldDE1Mw"),
    ("mapping153router153", "bWFwcGluZzE1M3JvdXRlcjE1Mw"),
    ("mapping153cluster153", "bWFwcGluZzE1M2NsdXN0ZXIxNTM"),
    ("record153cluster153", "cmVjb3JkMTUzY2x1c3RlcjE1Mw"),
    ("record153mirror153", "cmVjb3JkMTUzbWlycm9yMTUz"),
    ("record153filter153", "cmVjb3JkMTUzZmlsdGVyMTUz"),
    ("record153ranking153", "cmVjb3JkMTUzcmFua2luZzE1Mw"),
    ("candle153ranking153", "Y2FuZGxlMTUzcmFua2luZzE1Mw"),
    ("candle153encoding153", "Y2FuZGxlMTUzZW5jb2RpbmcxNTM"),
    ("candle153mapping153", "Y2FuZGxlMTUzbWFwcGluZzE1Mw"),
    ("candle153record153", "Y2FuZGxlMTUzcmVjb3JkMTUz"),
    ("thread153record153", "dGhyZWFkMTUzcmVjb3JkMTUz"),
    ("thread153candle153", "dGhyZWFkMTUzY2FuZGxlMTUz"),
    ("thread153thread153", "dGhyZWFkMTUzdGhyZWFkMTUz"),
    ("thread153kitten153", "dGhyZWFkMTUza2l0dGVuMTUz"),
    (
        "round 153: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTUzOiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 153: agentuniverse is a framework for multi agents",
        "cm91bmQgMTUzOiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 153: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTUzOiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 153: the processor reads the record then stops",
        "cm91bmQgMTUzOiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 153: a worker pulls the next task from the queue",
        "cm91bmQgMTUzOiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 153: signals travel through the network layer",
        "cm91bmQgMTUzOiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 153: the gateway routes each request by policy",
        "cm91bmQgMTUzOiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 153: memory grows until the buffer is full",
        "cm91bmQgMTUzOiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 153: the cluster mirrors every packet twice",
        "cm91bmQgMTUzOiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 153: ranking uses tokens learned from the corpus",
        "cm91bmQgMTUzOiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 153: a long session ends when the candle dies",
        "cm91bmQgMTUzOiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 153: encode the prompt then map the result",
        "cm91bmQgMTUzOiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 153: the kernel wakes the worker at dawn",
        "cm91bmQgMTUzOiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 153: service latency drops after the patch",
        "cm91bmQgMTUzOiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 153: the library caches every vector it sees",
        "cm91bmQgMTUzOiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 153: agents argue then the debate resolves",
        "cm91bmQgMTUzOiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 153: the filter keeps only strong matches",
        "cm91bmQgMTUzOiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 153: the model answers with a short reply",
        "cm91bmQgMTUzOiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 153: the recorder stores the reasoning trace",
        "cm91bmQgMTUzOiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 153: the angel watches the processor run",
        "cm91bmQgMTUzOiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 153: angle of the vector decides the match",
        "cm91bmQgMTUzOiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 153: the candle burns twice as long at night",
        "cm91bmQgMTUzOiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 153: a mirror of the universe in one line",
        "cm91bmQgMTUzOiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 153: the queue drains before the storm", "cm91bmQgMTUzOiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
