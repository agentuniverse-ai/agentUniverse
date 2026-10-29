"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten183kitten183", "a2l0dGVuMTgza2l0dGVuMTgz"),
    ("kitten183sitting183", "a2l0dGVuMTgzc2l0dGluZzE4Mw"),
    ("kitten183agent183", "a2l0dGVuMTgzYWdlbnQxODM"),
    ("kitten183angle183", "a2l0dGVuMTgzYW5nbGUxODM"),
    ("sitting183angle183", "c2l0dGluZzE4M2FuZ2xlMTgz"),
    ("sitting183universe183", "c2l0dGluZzE4M3VuaXZlcnNlMTgz"),
    ("sitting183memory183", "c2l0dGluZzE4M21lbW9yeTE4Mw"),
    ("sitting183stream183", "c2l0dGluZzE4M3N0cmVhbTE4Mw"),
    ("agent183stream183", "YWdlbnQxODNzdHJlYW0xODM"),
    ("agent183context183", "YWdlbnQxODNjb250ZXh0MTgz"),
    ("agent183knowledge183", "YWdlbnQxODNrbm93bGVkZ2UxODM"),
    ("agent183vector183", "YWdlbnQxODN2ZWN0b3IxODM"),
    ("angle183vector183", "YW5nbGUxODN2ZWN0b3IxODM"),
    ("angle183processor183", "YW5nbGUxODNwcm9jZXNzb3IxODM"),
    ("angle183reasoning183", "YW5nbGUxODNyZWFzb25pbmcxODM"),
    ("angle183machine183", "YW5nbGUxODNtYWNoaW5lMTgz"),
    ("universe183machine183", "dW5pdmVyc2UxODNtYWNoaW5lMTgz"),
    ("universe183learning183", "dW5pdmVyc2UxODNsZWFybmluZzE4Mw"),
    ("universe183model183", "dW5pdmVyc2UxODNtb2RlbDE4Mw"),
    ("universe183token183", "dW5pdmVyc2UxODN0b2tlbjE4Mw"),
    ("memory183token183", "bWVtb3J5MTgzdG9rZW4xODM"),
    ("memory183prompt183", "bWVtb3J5MTgzcHJvbXB0MTgz"),
    ("memory183session183", "bWVtb3J5MTgzc2Vzc2lvbjE4Mw"),
    ("memory183library183", "bWVtb3J5MTgzbGlicmFyeTE4Mw"),
    ("stream183library183", "c3RyZWFtMTgzbGlicmFyeTE4Mw"),
    ("stream183service183", "c3RyZWFtMTgzc2VydmljZTE4Mw"),
    ("stream183gateway183", "c3RyZWFtMTgzZ2F0ZXdheTE4Mw"),
    ("stream183storage183", "c3RyZWFtMTgzc3RvcmFnZTE4Mw"),
    ("context183storage183", "Y29udGV4dDE4M3N0b3JhZ2UxODM"),
    ("context183network183", "Y29udGV4dDE4M25ldHdvcmsxODM"),
    ("context183latency183", "Y29udGV4dDE4M2xhdGVuY3kxODM"),
    ("context183buffer183", "Y29udGV4dDE4M2J1ZmZlcjE4Mw"),
    ("knowledge183buffer183", "a25vd2xlZGdlMTgzYnVmZmVyMTgz"),
    ("knowledge183queue183", "a25vd2xlZGdlMTgzcXVldWUxODM"),
    ("knowledge183worker183", "a25vd2xlZGdlMTgzd29ya2VyMTgz"),
    ("knowledge183kernel183", "a25vd2xlZGdlMTgza2VybmVsMTgz"),
    ("vector183kernel183", "dmVjdG9yMTgza2VybmVsMTgz"),
    ("vector183signal183", "dmVjdG9yMTgzc2lnbmFsMTgz"),
    ("vector183packet183", "dmVjdG9yMTgzcGFja2V0MTgz"),
    ("vector183router183", "dmVjdG9yMTgzcm91dGVyMTgz"),
    ("processor183router183", "cHJvY2Vzc29yMTgzcm91dGVyMTgz"),
    ("processor183cluster183", "cHJvY2Vzc29yMTgzY2x1c3RlcjE4Mw"),
    ("processor183mirror183", "cHJvY2Vzc29yMTgzbWlycm9yMTgz"),
    ("processor183filter183", "cHJvY2Vzc29yMTgzZmlsdGVyMTgz"),
    ("reasoning183filter183", "cmVhc29uaW5nMTgzZmlsdGVyMTgz"),
    ("reasoning183ranking183", "cmVhc29uaW5nMTgzcmFua2luZzE4Mw"),
    ("reasoning183encoding183", "cmVhc29uaW5nMTgzZW5jb2RpbmcxODM"),
    ("reasoning183mapping183", "cmVhc29uaW5nMTgzbWFwcGluZzE4Mw"),
    ("machine183mapping183", "bWFjaGluZTE4M21hcHBpbmcxODM"),
    ("machine183record183", "bWFjaGluZTE4M3JlY29yZDE4Mw"),
    ("machine183candle183", "bWFjaGluZTE4M2NhbmRsZTE4Mw"),
    ("machine183thread183", "bWFjaGluZTE4M3RocmVhZDE4Mw"),
    ("learning183thread183", "bGVhcm5pbmcxODN0aHJlYWQxODM"),
    ("learning183kitten183", "bGVhcm5pbmcxODNraXR0ZW4xODM"),
    ("learning183sitting183", "bGVhcm5pbmcxODNzaXR0aW5nMTgz"),
    ("learning183agent183", "bGVhcm5pbmcxODNhZ2VudDE4Mw"),
    ("model183agent183", "bW9kZWwxODNhZ2VudDE4Mw"),
    ("model183angle183", "bW9kZWwxODNhbmdsZTE4Mw"),
    ("model183universe183", "bW9kZWwxODN1bml2ZXJzZTE4Mw"),
    ("model183memory183", "bW9kZWwxODNtZW1vcnkxODM"),
    ("token183memory183", "dG9rZW4xODNtZW1vcnkxODM"),
    ("token183stream183", "dG9rZW4xODNzdHJlYW0xODM"),
    ("token183context183", "dG9rZW4xODNjb250ZXh0MTgz"),
    ("token183knowledge183", "dG9rZW4xODNrbm93bGVkZ2UxODM"),
    ("prompt183knowledge183", "cHJvbXB0MTgza25vd2xlZGdlMTgz"),
    ("prompt183vector183", "cHJvbXB0MTgzdmVjdG9yMTgz"),
    ("prompt183processor183", "cHJvbXB0MTgzcHJvY2Vzc29yMTgz"),
    ("prompt183reasoning183", "cHJvbXB0MTgzcmVhc29uaW5nMTgz"),
    ("session183reasoning183", "c2Vzc2lvbjE4M3JlYXNvbmluZzE4Mw"),
    ("session183machine183", "c2Vzc2lvbjE4M21hY2hpbmUxODM"),
    ("session183learning183", "c2Vzc2lvbjE4M2xlYXJuaW5nMTgz"),
    ("session183model183", "c2Vzc2lvbjE4M21vZGVsMTgz"),
    ("library183model183", "bGlicmFyeTE4M21vZGVsMTgz"),
    ("library183token183", "bGlicmFyeTE4M3Rva2VuMTgz"),
    ("library183prompt183", "bGlicmFyeTE4M3Byb21wdDE4Mw"),
    ("library183session183", "bGlicmFyeTE4M3Nlc3Npb24xODM"),
    ("service183session183", "c2VydmljZTE4M3Nlc3Npb24xODM"),
    ("service183library183", "c2VydmljZTE4M2xpYnJhcnkxODM"),
    ("service183service183", "c2VydmljZTE4M3NlcnZpY2UxODM"),
    ("service183gateway183", "c2VydmljZTE4M2dhdGV3YXkxODM"),
    ("gateway183gateway183", "Z2F0ZXdheTE4M2dhdGV3YXkxODM"),
    ("gateway183storage183", "Z2F0ZXdheTE4M3N0b3JhZ2UxODM"),
    ("gateway183network183", "Z2F0ZXdheTE4M25ldHdvcmsxODM"),
    ("gateway183latency183", "Z2F0ZXdheTE4M2xhdGVuY3kxODM"),
    ("storage183latency183", "c3RvcmFnZTE4M2xhdGVuY3kxODM"),
    ("storage183buffer183", "c3RvcmFnZTE4M2J1ZmZlcjE4Mw"),
    ("storage183queue183", "c3RvcmFnZTE4M3F1ZXVlMTgz"),
    ("storage183worker183", "c3RvcmFnZTE4M3dvcmtlcjE4Mw"),
    ("network183worker183", "bmV0d29yazE4M3dvcmtlcjE4Mw"),
    ("network183kernel183", "bmV0d29yazE4M2tlcm5lbDE4Mw"),
    ("network183signal183", "bmV0d29yazE4M3NpZ25hbDE4Mw"),
    ("network183packet183", "bmV0d29yazE4M3BhY2tldDE4Mw"),
    ("latency183packet183", "bGF0ZW5jeTE4M3BhY2tldDE4Mw"),
    ("latency183router183", "bGF0ZW5jeTE4M3JvdXRlcjE4Mw"),
    ("latency183cluster183", "bGF0ZW5jeTE4M2NsdXN0ZXIxODM"),
    ("latency183mirror183", "bGF0ZW5jeTE4M21pcnJvcjE4Mw"),
    ("buffer183mirror183", "YnVmZmVyMTgzbWlycm9yMTgz"),
    ("buffer183filter183", "YnVmZmVyMTgzZmlsdGVyMTgz"),
    ("buffer183ranking183", "YnVmZmVyMTgzcmFua2luZzE4Mw"),
    ("buffer183encoding183", "YnVmZmVyMTgzZW5jb2RpbmcxODM"),
    ("queue183encoding183", "cXVldWUxODNlbmNvZGluZzE4Mw"),
    ("queue183mapping183", "cXVldWUxODNtYXBwaW5nMTgz"),
    ("queue183record183", "cXVldWUxODNyZWNvcmQxODM"),
    ("queue183candle183", "cXVldWUxODNjYW5kbGUxODM"),
    ("worker183candle183", "d29ya2VyMTgzY2FuZGxlMTgz"),
    ("worker183thread183", "d29ya2VyMTgzdGhyZWFkMTgz"),
    ("worker183kitten183", "d29ya2VyMTgza2l0dGVuMTgz"),
    ("worker183sitting183", "d29ya2VyMTgzc2l0dGluZzE4Mw"),
    ("kernel183sitting183", "a2VybmVsMTgzc2l0dGluZzE4Mw"),
    ("kernel183agent183", "a2VybmVsMTgzYWdlbnQxODM"),
    ("kernel183angle183", "a2VybmVsMTgzYW5nbGUxODM"),
    ("kernel183universe183", "a2VybmVsMTgzdW5pdmVyc2UxODM"),
    ("signal183universe183", "c2lnbmFsMTgzdW5pdmVyc2UxODM"),
    ("signal183memory183", "c2lnbmFsMTgzbWVtb3J5MTgz"),
    ("signal183stream183", "c2lnbmFsMTgzc3RyZWFtMTgz"),
    ("signal183context183", "c2lnbmFsMTgzY29udGV4dDE4Mw"),
    ("packet183context183", "cGFja2V0MTgzY29udGV4dDE4Mw"),
    ("packet183knowledge183", "cGFja2V0MTgza25vd2xlZGdlMTgz"),
    ("packet183vector183", "cGFja2V0MTgzdmVjdG9yMTgz"),
    ("packet183processor183", "cGFja2V0MTgzcHJvY2Vzc29yMTgz"),
    ("router183processor183", "cm91dGVyMTgzcHJvY2Vzc29yMTgz"),
    ("router183reasoning183", "cm91dGVyMTgzcmVhc29uaW5nMTgz"),
    ("router183machine183", "cm91dGVyMTgzbWFjaGluZTE4Mw"),
    ("router183learning183", "cm91dGVyMTgzbGVhcm5pbmcxODM"),
    ("cluster183learning183", "Y2x1c3RlcjE4M2xlYXJuaW5nMTgz"),
    ("cluster183model183", "Y2x1c3RlcjE4M21vZGVsMTgz"),
    ("cluster183token183", "Y2x1c3RlcjE4M3Rva2VuMTgz"),
    ("cluster183prompt183", "Y2x1c3RlcjE4M3Byb21wdDE4Mw"),
    ("mirror183prompt183", "bWlycm9yMTgzcHJvbXB0MTgz"),
    ("mirror183session183", "bWlycm9yMTgzc2Vzc2lvbjE4Mw"),
    ("mirror183library183", "bWlycm9yMTgzbGlicmFyeTE4Mw"),
    ("mirror183service183", "bWlycm9yMTgzc2VydmljZTE4Mw"),
    ("filter183service183", "ZmlsdGVyMTgzc2VydmljZTE4Mw"),
    ("filter183gateway183", "ZmlsdGVyMTgzZ2F0ZXdheTE4Mw"),
    ("filter183storage183", "ZmlsdGVyMTgzc3RvcmFnZTE4Mw"),
    ("filter183network183", "ZmlsdGVyMTgzbmV0d29yazE4Mw"),
    ("ranking183network183", "cmFua2luZzE4M25ldHdvcmsxODM"),
    ("ranking183latency183", "cmFua2luZzE4M2xhdGVuY3kxODM"),
    ("ranking183buffer183", "cmFua2luZzE4M2J1ZmZlcjE4Mw"),
    ("ranking183queue183", "cmFua2luZzE4M3F1ZXVlMTgz"),
    ("encoding183queue183", "ZW5jb2RpbmcxODNxdWV1ZTE4Mw"),
    ("encoding183worker183", "ZW5jb2RpbmcxODN3b3JrZXIxODM"),
    ("encoding183kernel183", "ZW5jb2RpbmcxODNrZXJuZWwxODM"),
    ("encoding183signal183", "ZW5jb2RpbmcxODNzaWduYWwxODM"),
    ("mapping183signal183", "bWFwcGluZzE4M3NpZ25hbDE4Mw"),
    ("mapping183packet183", "bWFwcGluZzE4M3BhY2tldDE4Mw"),
    ("mapping183router183", "bWFwcGluZzE4M3JvdXRlcjE4Mw"),
    ("mapping183cluster183", "bWFwcGluZzE4M2NsdXN0ZXIxODM"),
    ("record183cluster183", "cmVjb3JkMTgzY2x1c3RlcjE4Mw"),
    ("record183mirror183", "cmVjb3JkMTgzbWlycm9yMTgz"),
    ("record183filter183", "cmVjb3JkMTgzZmlsdGVyMTgz"),
    ("record183ranking183", "cmVjb3JkMTgzcmFua2luZzE4Mw"),
    ("candle183ranking183", "Y2FuZGxlMTgzcmFua2luZzE4Mw"),
    ("candle183encoding183", "Y2FuZGxlMTgzZW5jb2RpbmcxODM"),
    ("candle183mapping183", "Y2FuZGxlMTgzbWFwcGluZzE4Mw"),
    ("candle183record183", "Y2FuZGxlMTgzcmVjb3JkMTgz"),
    ("thread183record183", "dGhyZWFkMTgzcmVjb3JkMTgz"),
    ("thread183candle183", "dGhyZWFkMTgzY2FuZGxlMTgz"),
    ("thread183thread183", "dGhyZWFkMTgzdGhyZWFkMTgz"),
    ("thread183kitten183", "dGhyZWFkMTgza2l0dGVuMTgz"),
    (
        "round 183: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTgzOiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 183: agentuniverse is a framework for multi agents",
        "cm91bmQgMTgzOiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 183: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTgzOiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 183: the processor reads the record then stops",
        "cm91bmQgMTgzOiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 183: a worker pulls the next task from the queue",
        "cm91bmQgMTgzOiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 183: signals travel through the network layer",
        "cm91bmQgMTgzOiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 183: the gateway routes each request by policy",
        "cm91bmQgMTgzOiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 183: memory grows until the buffer is full",
        "cm91bmQgMTgzOiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 183: the cluster mirrors every packet twice",
        "cm91bmQgMTgzOiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 183: ranking uses tokens learned from the corpus",
        "cm91bmQgMTgzOiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 183: a long session ends when the candle dies",
        "cm91bmQgMTgzOiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 183: encode the prompt then map the result",
        "cm91bmQgMTgzOiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 183: the kernel wakes the worker at dawn",
        "cm91bmQgMTgzOiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 183: service latency drops after the patch",
        "cm91bmQgMTgzOiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 183: the library caches every vector it sees",
        "cm91bmQgMTgzOiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 183: agents argue then the debate resolves",
        "cm91bmQgMTgzOiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 183: the filter keeps only strong matches",
        "cm91bmQgMTgzOiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 183: the model answers with a short reply",
        "cm91bmQgMTgzOiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 183: the recorder stores the reasoning trace",
        "cm91bmQgMTgzOiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 183: the angel watches the processor run",
        "cm91bmQgMTgzOiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 183: angle of the vector decides the match",
        "cm91bmQgMTgzOiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 183: the candle burns twice as long at night",
        "cm91bmQgMTgzOiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 183: a mirror of the universe in one line",
        "cm91bmQgMTgzOiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 183: the queue drains before the storm", "cm91bmQgMTgzOiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
