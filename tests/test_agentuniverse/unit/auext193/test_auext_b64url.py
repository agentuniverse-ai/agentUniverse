"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten193kitten193", "a2l0dGVuMTkza2l0dGVuMTkz"),
    ("kitten193sitting193", "a2l0dGVuMTkzc2l0dGluZzE5Mw"),
    ("kitten193agent193", "a2l0dGVuMTkzYWdlbnQxOTM"),
    ("kitten193angle193", "a2l0dGVuMTkzYW5nbGUxOTM"),
    ("sitting193angle193", "c2l0dGluZzE5M2FuZ2xlMTkz"),
    ("sitting193universe193", "c2l0dGluZzE5M3VuaXZlcnNlMTkz"),
    ("sitting193memory193", "c2l0dGluZzE5M21lbW9yeTE5Mw"),
    ("sitting193stream193", "c2l0dGluZzE5M3N0cmVhbTE5Mw"),
    ("agent193stream193", "YWdlbnQxOTNzdHJlYW0xOTM"),
    ("agent193context193", "YWdlbnQxOTNjb250ZXh0MTkz"),
    ("agent193knowledge193", "YWdlbnQxOTNrbm93bGVkZ2UxOTM"),
    ("agent193vector193", "YWdlbnQxOTN2ZWN0b3IxOTM"),
    ("angle193vector193", "YW5nbGUxOTN2ZWN0b3IxOTM"),
    ("angle193processor193", "YW5nbGUxOTNwcm9jZXNzb3IxOTM"),
    ("angle193reasoning193", "YW5nbGUxOTNyZWFzb25pbmcxOTM"),
    ("angle193machine193", "YW5nbGUxOTNtYWNoaW5lMTkz"),
    ("universe193machine193", "dW5pdmVyc2UxOTNtYWNoaW5lMTkz"),
    ("universe193learning193", "dW5pdmVyc2UxOTNsZWFybmluZzE5Mw"),
    ("universe193model193", "dW5pdmVyc2UxOTNtb2RlbDE5Mw"),
    ("universe193token193", "dW5pdmVyc2UxOTN0b2tlbjE5Mw"),
    ("memory193token193", "bWVtb3J5MTkzdG9rZW4xOTM"),
    ("memory193prompt193", "bWVtb3J5MTkzcHJvbXB0MTkz"),
    ("memory193session193", "bWVtb3J5MTkzc2Vzc2lvbjE5Mw"),
    ("memory193library193", "bWVtb3J5MTkzbGlicmFyeTE5Mw"),
    ("stream193library193", "c3RyZWFtMTkzbGlicmFyeTE5Mw"),
    ("stream193service193", "c3RyZWFtMTkzc2VydmljZTE5Mw"),
    ("stream193gateway193", "c3RyZWFtMTkzZ2F0ZXdheTE5Mw"),
    ("stream193storage193", "c3RyZWFtMTkzc3RvcmFnZTE5Mw"),
    ("context193storage193", "Y29udGV4dDE5M3N0b3JhZ2UxOTM"),
    ("context193network193", "Y29udGV4dDE5M25ldHdvcmsxOTM"),
    ("context193latency193", "Y29udGV4dDE5M2xhdGVuY3kxOTM"),
    ("context193buffer193", "Y29udGV4dDE5M2J1ZmZlcjE5Mw"),
    ("knowledge193buffer193", "a25vd2xlZGdlMTkzYnVmZmVyMTkz"),
    ("knowledge193queue193", "a25vd2xlZGdlMTkzcXVldWUxOTM"),
    ("knowledge193worker193", "a25vd2xlZGdlMTkzd29ya2VyMTkz"),
    ("knowledge193kernel193", "a25vd2xlZGdlMTkza2VybmVsMTkz"),
    ("vector193kernel193", "dmVjdG9yMTkza2VybmVsMTkz"),
    ("vector193signal193", "dmVjdG9yMTkzc2lnbmFsMTkz"),
    ("vector193packet193", "dmVjdG9yMTkzcGFja2V0MTkz"),
    ("vector193router193", "dmVjdG9yMTkzcm91dGVyMTkz"),
    ("processor193router193", "cHJvY2Vzc29yMTkzcm91dGVyMTkz"),
    ("processor193cluster193", "cHJvY2Vzc29yMTkzY2x1c3RlcjE5Mw"),
    ("processor193mirror193", "cHJvY2Vzc29yMTkzbWlycm9yMTkz"),
    ("processor193filter193", "cHJvY2Vzc29yMTkzZmlsdGVyMTkz"),
    ("reasoning193filter193", "cmVhc29uaW5nMTkzZmlsdGVyMTkz"),
    ("reasoning193ranking193", "cmVhc29uaW5nMTkzcmFua2luZzE5Mw"),
    ("reasoning193encoding193", "cmVhc29uaW5nMTkzZW5jb2RpbmcxOTM"),
    ("reasoning193mapping193", "cmVhc29uaW5nMTkzbWFwcGluZzE5Mw"),
    ("machine193mapping193", "bWFjaGluZTE5M21hcHBpbmcxOTM"),
    ("machine193record193", "bWFjaGluZTE5M3JlY29yZDE5Mw"),
    ("machine193candle193", "bWFjaGluZTE5M2NhbmRsZTE5Mw"),
    ("machine193thread193", "bWFjaGluZTE5M3RocmVhZDE5Mw"),
    ("learning193thread193", "bGVhcm5pbmcxOTN0aHJlYWQxOTM"),
    ("learning193kitten193", "bGVhcm5pbmcxOTNraXR0ZW4xOTM"),
    ("learning193sitting193", "bGVhcm5pbmcxOTNzaXR0aW5nMTkz"),
    ("learning193agent193", "bGVhcm5pbmcxOTNhZ2VudDE5Mw"),
    ("model193agent193", "bW9kZWwxOTNhZ2VudDE5Mw"),
    ("model193angle193", "bW9kZWwxOTNhbmdsZTE5Mw"),
    ("model193universe193", "bW9kZWwxOTN1bml2ZXJzZTE5Mw"),
    ("model193memory193", "bW9kZWwxOTNtZW1vcnkxOTM"),
    ("token193memory193", "dG9rZW4xOTNtZW1vcnkxOTM"),
    ("token193stream193", "dG9rZW4xOTNzdHJlYW0xOTM"),
    ("token193context193", "dG9rZW4xOTNjb250ZXh0MTkz"),
    ("token193knowledge193", "dG9rZW4xOTNrbm93bGVkZ2UxOTM"),
    ("prompt193knowledge193", "cHJvbXB0MTkza25vd2xlZGdlMTkz"),
    ("prompt193vector193", "cHJvbXB0MTkzdmVjdG9yMTkz"),
    ("prompt193processor193", "cHJvbXB0MTkzcHJvY2Vzc29yMTkz"),
    ("prompt193reasoning193", "cHJvbXB0MTkzcmVhc29uaW5nMTkz"),
    ("session193reasoning193", "c2Vzc2lvbjE5M3JlYXNvbmluZzE5Mw"),
    ("session193machine193", "c2Vzc2lvbjE5M21hY2hpbmUxOTM"),
    ("session193learning193", "c2Vzc2lvbjE5M2xlYXJuaW5nMTkz"),
    ("session193model193", "c2Vzc2lvbjE5M21vZGVsMTkz"),
    ("library193model193", "bGlicmFyeTE5M21vZGVsMTkz"),
    ("library193token193", "bGlicmFyeTE5M3Rva2VuMTkz"),
    ("library193prompt193", "bGlicmFyeTE5M3Byb21wdDE5Mw"),
    ("library193session193", "bGlicmFyeTE5M3Nlc3Npb24xOTM"),
    ("service193session193", "c2VydmljZTE5M3Nlc3Npb24xOTM"),
    ("service193library193", "c2VydmljZTE5M2xpYnJhcnkxOTM"),
    ("service193service193", "c2VydmljZTE5M3NlcnZpY2UxOTM"),
    ("service193gateway193", "c2VydmljZTE5M2dhdGV3YXkxOTM"),
    ("gateway193gateway193", "Z2F0ZXdheTE5M2dhdGV3YXkxOTM"),
    ("gateway193storage193", "Z2F0ZXdheTE5M3N0b3JhZ2UxOTM"),
    ("gateway193network193", "Z2F0ZXdheTE5M25ldHdvcmsxOTM"),
    ("gateway193latency193", "Z2F0ZXdheTE5M2xhdGVuY3kxOTM"),
    ("storage193latency193", "c3RvcmFnZTE5M2xhdGVuY3kxOTM"),
    ("storage193buffer193", "c3RvcmFnZTE5M2J1ZmZlcjE5Mw"),
    ("storage193queue193", "c3RvcmFnZTE5M3F1ZXVlMTkz"),
    ("storage193worker193", "c3RvcmFnZTE5M3dvcmtlcjE5Mw"),
    ("network193worker193", "bmV0d29yazE5M3dvcmtlcjE5Mw"),
    ("network193kernel193", "bmV0d29yazE5M2tlcm5lbDE5Mw"),
    ("network193signal193", "bmV0d29yazE5M3NpZ25hbDE5Mw"),
    ("network193packet193", "bmV0d29yazE5M3BhY2tldDE5Mw"),
    ("latency193packet193", "bGF0ZW5jeTE5M3BhY2tldDE5Mw"),
    ("latency193router193", "bGF0ZW5jeTE5M3JvdXRlcjE5Mw"),
    ("latency193cluster193", "bGF0ZW5jeTE5M2NsdXN0ZXIxOTM"),
    ("latency193mirror193", "bGF0ZW5jeTE5M21pcnJvcjE5Mw"),
    ("buffer193mirror193", "YnVmZmVyMTkzbWlycm9yMTkz"),
    ("buffer193filter193", "YnVmZmVyMTkzZmlsdGVyMTkz"),
    ("buffer193ranking193", "YnVmZmVyMTkzcmFua2luZzE5Mw"),
    ("buffer193encoding193", "YnVmZmVyMTkzZW5jb2RpbmcxOTM"),
    ("queue193encoding193", "cXVldWUxOTNlbmNvZGluZzE5Mw"),
    ("queue193mapping193", "cXVldWUxOTNtYXBwaW5nMTkz"),
    ("queue193record193", "cXVldWUxOTNyZWNvcmQxOTM"),
    ("queue193candle193", "cXVldWUxOTNjYW5kbGUxOTM"),
    ("worker193candle193", "d29ya2VyMTkzY2FuZGxlMTkz"),
    ("worker193thread193", "d29ya2VyMTkzdGhyZWFkMTkz"),
    ("worker193kitten193", "d29ya2VyMTkza2l0dGVuMTkz"),
    ("worker193sitting193", "d29ya2VyMTkzc2l0dGluZzE5Mw"),
    ("kernel193sitting193", "a2VybmVsMTkzc2l0dGluZzE5Mw"),
    ("kernel193agent193", "a2VybmVsMTkzYWdlbnQxOTM"),
    ("kernel193angle193", "a2VybmVsMTkzYW5nbGUxOTM"),
    ("kernel193universe193", "a2VybmVsMTkzdW5pdmVyc2UxOTM"),
    ("signal193universe193", "c2lnbmFsMTkzdW5pdmVyc2UxOTM"),
    ("signal193memory193", "c2lnbmFsMTkzbWVtb3J5MTkz"),
    ("signal193stream193", "c2lnbmFsMTkzc3RyZWFtMTkz"),
    ("signal193context193", "c2lnbmFsMTkzY29udGV4dDE5Mw"),
    ("packet193context193", "cGFja2V0MTkzY29udGV4dDE5Mw"),
    ("packet193knowledge193", "cGFja2V0MTkza25vd2xlZGdlMTkz"),
    ("packet193vector193", "cGFja2V0MTkzdmVjdG9yMTkz"),
    ("packet193processor193", "cGFja2V0MTkzcHJvY2Vzc29yMTkz"),
    ("router193processor193", "cm91dGVyMTkzcHJvY2Vzc29yMTkz"),
    ("router193reasoning193", "cm91dGVyMTkzcmVhc29uaW5nMTkz"),
    ("router193machine193", "cm91dGVyMTkzbWFjaGluZTE5Mw"),
    ("router193learning193", "cm91dGVyMTkzbGVhcm5pbmcxOTM"),
    ("cluster193learning193", "Y2x1c3RlcjE5M2xlYXJuaW5nMTkz"),
    ("cluster193model193", "Y2x1c3RlcjE5M21vZGVsMTkz"),
    ("cluster193token193", "Y2x1c3RlcjE5M3Rva2VuMTkz"),
    ("cluster193prompt193", "Y2x1c3RlcjE5M3Byb21wdDE5Mw"),
    ("mirror193prompt193", "bWlycm9yMTkzcHJvbXB0MTkz"),
    ("mirror193session193", "bWlycm9yMTkzc2Vzc2lvbjE5Mw"),
    ("mirror193library193", "bWlycm9yMTkzbGlicmFyeTE5Mw"),
    ("mirror193service193", "bWlycm9yMTkzc2VydmljZTE5Mw"),
    ("filter193service193", "ZmlsdGVyMTkzc2VydmljZTE5Mw"),
    ("filter193gateway193", "ZmlsdGVyMTkzZ2F0ZXdheTE5Mw"),
    ("filter193storage193", "ZmlsdGVyMTkzc3RvcmFnZTE5Mw"),
    ("filter193network193", "ZmlsdGVyMTkzbmV0d29yazE5Mw"),
    ("ranking193network193", "cmFua2luZzE5M25ldHdvcmsxOTM"),
    ("ranking193latency193", "cmFua2luZzE5M2xhdGVuY3kxOTM"),
    ("ranking193buffer193", "cmFua2luZzE5M2J1ZmZlcjE5Mw"),
    ("ranking193queue193", "cmFua2luZzE5M3F1ZXVlMTkz"),
    ("encoding193queue193", "ZW5jb2RpbmcxOTNxdWV1ZTE5Mw"),
    ("encoding193worker193", "ZW5jb2RpbmcxOTN3b3JrZXIxOTM"),
    ("encoding193kernel193", "ZW5jb2RpbmcxOTNrZXJuZWwxOTM"),
    ("encoding193signal193", "ZW5jb2RpbmcxOTNzaWduYWwxOTM"),
    ("mapping193signal193", "bWFwcGluZzE5M3NpZ25hbDE5Mw"),
    ("mapping193packet193", "bWFwcGluZzE5M3BhY2tldDE5Mw"),
    ("mapping193router193", "bWFwcGluZzE5M3JvdXRlcjE5Mw"),
    ("mapping193cluster193", "bWFwcGluZzE5M2NsdXN0ZXIxOTM"),
    ("record193cluster193", "cmVjb3JkMTkzY2x1c3RlcjE5Mw"),
    ("record193mirror193", "cmVjb3JkMTkzbWlycm9yMTkz"),
    ("record193filter193", "cmVjb3JkMTkzZmlsdGVyMTkz"),
    ("record193ranking193", "cmVjb3JkMTkzcmFua2luZzE5Mw"),
    ("candle193ranking193", "Y2FuZGxlMTkzcmFua2luZzE5Mw"),
    ("candle193encoding193", "Y2FuZGxlMTkzZW5jb2RpbmcxOTM"),
    ("candle193mapping193", "Y2FuZGxlMTkzbWFwcGluZzE5Mw"),
    ("candle193record193", "Y2FuZGxlMTkzcmVjb3JkMTkz"),
    ("thread193record193", "dGhyZWFkMTkzcmVjb3JkMTkz"),
    ("thread193candle193", "dGhyZWFkMTkzY2FuZGxlMTkz"),
    ("thread193thread193", "dGhyZWFkMTkzdGhyZWFkMTkz"),
    ("thread193kitten193", "dGhyZWFkMTkza2l0dGVuMTkz"),
    (
        "round 193: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTkzOiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 193: agentuniverse is a framework for multi agents",
        "cm91bmQgMTkzOiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 193: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTkzOiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 193: the processor reads the record then stops",
        "cm91bmQgMTkzOiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 193: a worker pulls the next task from the queue",
        "cm91bmQgMTkzOiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 193: signals travel through the network layer",
        "cm91bmQgMTkzOiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 193: the gateway routes each request by policy",
        "cm91bmQgMTkzOiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 193: memory grows until the buffer is full",
        "cm91bmQgMTkzOiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 193: the cluster mirrors every packet twice",
        "cm91bmQgMTkzOiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 193: ranking uses tokens learned from the corpus",
        "cm91bmQgMTkzOiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 193: a long session ends when the candle dies",
        "cm91bmQgMTkzOiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 193: encode the prompt then map the result",
        "cm91bmQgMTkzOiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 193: the kernel wakes the worker at dawn",
        "cm91bmQgMTkzOiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 193: service latency drops after the patch",
        "cm91bmQgMTkzOiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 193: the library caches every vector it sees",
        "cm91bmQgMTkzOiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 193: agents argue then the debate resolves",
        "cm91bmQgMTkzOiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 193: the filter keeps only strong matches",
        "cm91bmQgMTkzOiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 193: the model answers with a short reply",
        "cm91bmQgMTkzOiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 193: the recorder stores the reasoning trace",
        "cm91bmQgMTkzOiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 193: the angel watches the processor run",
        "cm91bmQgMTkzOiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 193: angle of the vector decides the match",
        "cm91bmQgMTkzOiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 193: the candle burns twice as long at night",
        "cm91bmQgMTkzOiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 193: a mirror of the universe in one line",
        "cm91bmQgMTkzOiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 193: the queue drains before the storm", "cm91bmQgMTkzOiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
