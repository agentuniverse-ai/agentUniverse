"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten143kitten143", "a2l0dGVuMTQza2l0dGVuMTQz"),
    ("kitten143sitting143", "a2l0dGVuMTQzc2l0dGluZzE0Mw"),
    ("kitten143agent143", "a2l0dGVuMTQzYWdlbnQxNDM"),
    ("kitten143angle143", "a2l0dGVuMTQzYW5nbGUxNDM"),
    ("sitting143angle143", "c2l0dGluZzE0M2FuZ2xlMTQz"),
    ("sitting143universe143", "c2l0dGluZzE0M3VuaXZlcnNlMTQz"),
    ("sitting143memory143", "c2l0dGluZzE0M21lbW9yeTE0Mw"),
    ("sitting143stream143", "c2l0dGluZzE0M3N0cmVhbTE0Mw"),
    ("agent143stream143", "YWdlbnQxNDNzdHJlYW0xNDM"),
    ("agent143context143", "YWdlbnQxNDNjb250ZXh0MTQz"),
    ("agent143knowledge143", "YWdlbnQxNDNrbm93bGVkZ2UxNDM"),
    ("agent143vector143", "YWdlbnQxNDN2ZWN0b3IxNDM"),
    ("angle143vector143", "YW5nbGUxNDN2ZWN0b3IxNDM"),
    ("angle143processor143", "YW5nbGUxNDNwcm9jZXNzb3IxNDM"),
    ("angle143reasoning143", "YW5nbGUxNDNyZWFzb25pbmcxNDM"),
    ("angle143machine143", "YW5nbGUxNDNtYWNoaW5lMTQz"),
    ("universe143machine143", "dW5pdmVyc2UxNDNtYWNoaW5lMTQz"),
    ("universe143learning143", "dW5pdmVyc2UxNDNsZWFybmluZzE0Mw"),
    ("universe143model143", "dW5pdmVyc2UxNDNtb2RlbDE0Mw"),
    ("universe143token143", "dW5pdmVyc2UxNDN0b2tlbjE0Mw"),
    ("memory143token143", "bWVtb3J5MTQzdG9rZW4xNDM"),
    ("memory143prompt143", "bWVtb3J5MTQzcHJvbXB0MTQz"),
    ("memory143session143", "bWVtb3J5MTQzc2Vzc2lvbjE0Mw"),
    ("memory143library143", "bWVtb3J5MTQzbGlicmFyeTE0Mw"),
    ("stream143library143", "c3RyZWFtMTQzbGlicmFyeTE0Mw"),
    ("stream143service143", "c3RyZWFtMTQzc2VydmljZTE0Mw"),
    ("stream143gateway143", "c3RyZWFtMTQzZ2F0ZXdheTE0Mw"),
    ("stream143storage143", "c3RyZWFtMTQzc3RvcmFnZTE0Mw"),
    ("context143storage143", "Y29udGV4dDE0M3N0b3JhZ2UxNDM"),
    ("context143network143", "Y29udGV4dDE0M25ldHdvcmsxNDM"),
    ("context143latency143", "Y29udGV4dDE0M2xhdGVuY3kxNDM"),
    ("context143buffer143", "Y29udGV4dDE0M2J1ZmZlcjE0Mw"),
    ("knowledge143buffer143", "a25vd2xlZGdlMTQzYnVmZmVyMTQz"),
    ("knowledge143queue143", "a25vd2xlZGdlMTQzcXVldWUxNDM"),
    ("knowledge143worker143", "a25vd2xlZGdlMTQzd29ya2VyMTQz"),
    ("knowledge143kernel143", "a25vd2xlZGdlMTQza2VybmVsMTQz"),
    ("vector143kernel143", "dmVjdG9yMTQza2VybmVsMTQz"),
    ("vector143signal143", "dmVjdG9yMTQzc2lnbmFsMTQz"),
    ("vector143packet143", "dmVjdG9yMTQzcGFja2V0MTQz"),
    ("vector143router143", "dmVjdG9yMTQzcm91dGVyMTQz"),
    ("processor143router143", "cHJvY2Vzc29yMTQzcm91dGVyMTQz"),
    ("processor143cluster143", "cHJvY2Vzc29yMTQzY2x1c3RlcjE0Mw"),
    ("processor143mirror143", "cHJvY2Vzc29yMTQzbWlycm9yMTQz"),
    ("processor143filter143", "cHJvY2Vzc29yMTQzZmlsdGVyMTQz"),
    ("reasoning143filter143", "cmVhc29uaW5nMTQzZmlsdGVyMTQz"),
    ("reasoning143ranking143", "cmVhc29uaW5nMTQzcmFua2luZzE0Mw"),
    ("reasoning143encoding143", "cmVhc29uaW5nMTQzZW5jb2RpbmcxNDM"),
    ("reasoning143mapping143", "cmVhc29uaW5nMTQzbWFwcGluZzE0Mw"),
    ("machine143mapping143", "bWFjaGluZTE0M21hcHBpbmcxNDM"),
    ("machine143record143", "bWFjaGluZTE0M3JlY29yZDE0Mw"),
    ("machine143candle143", "bWFjaGluZTE0M2NhbmRsZTE0Mw"),
    ("machine143thread143", "bWFjaGluZTE0M3RocmVhZDE0Mw"),
    ("learning143thread143", "bGVhcm5pbmcxNDN0aHJlYWQxNDM"),
    ("learning143kitten143", "bGVhcm5pbmcxNDNraXR0ZW4xNDM"),
    ("learning143sitting143", "bGVhcm5pbmcxNDNzaXR0aW5nMTQz"),
    ("learning143agent143", "bGVhcm5pbmcxNDNhZ2VudDE0Mw"),
    ("model143agent143", "bW9kZWwxNDNhZ2VudDE0Mw"),
    ("model143angle143", "bW9kZWwxNDNhbmdsZTE0Mw"),
    ("model143universe143", "bW9kZWwxNDN1bml2ZXJzZTE0Mw"),
    ("model143memory143", "bW9kZWwxNDNtZW1vcnkxNDM"),
    ("token143memory143", "dG9rZW4xNDNtZW1vcnkxNDM"),
    ("token143stream143", "dG9rZW4xNDNzdHJlYW0xNDM"),
    ("token143context143", "dG9rZW4xNDNjb250ZXh0MTQz"),
    ("token143knowledge143", "dG9rZW4xNDNrbm93bGVkZ2UxNDM"),
    ("prompt143knowledge143", "cHJvbXB0MTQza25vd2xlZGdlMTQz"),
    ("prompt143vector143", "cHJvbXB0MTQzdmVjdG9yMTQz"),
    ("prompt143processor143", "cHJvbXB0MTQzcHJvY2Vzc29yMTQz"),
    ("prompt143reasoning143", "cHJvbXB0MTQzcmVhc29uaW5nMTQz"),
    ("session143reasoning143", "c2Vzc2lvbjE0M3JlYXNvbmluZzE0Mw"),
    ("session143machine143", "c2Vzc2lvbjE0M21hY2hpbmUxNDM"),
    ("session143learning143", "c2Vzc2lvbjE0M2xlYXJuaW5nMTQz"),
    ("session143model143", "c2Vzc2lvbjE0M21vZGVsMTQz"),
    ("library143model143", "bGlicmFyeTE0M21vZGVsMTQz"),
    ("library143token143", "bGlicmFyeTE0M3Rva2VuMTQz"),
    ("library143prompt143", "bGlicmFyeTE0M3Byb21wdDE0Mw"),
    ("library143session143", "bGlicmFyeTE0M3Nlc3Npb24xNDM"),
    ("service143session143", "c2VydmljZTE0M3Nlc3Npb24xNDM"),
    ("service143library143", "c2VydmljZTE0M2xpYnJhcnkxNDM"),
    ("service143service143", "c2VydmljZTE0M3NlcnZpY2UxNDM"),
    ("service143gateway143", "c2VydmljZTE0M2dhdGV3YXkxNDM"),
    ("gateway143gateway143", "Z2F0ZXdheTE0M2dhdGV3YXkxNDM"),
    ("gateway143storage143", "Z2F0ZXdheTE0M3N0b3JhZ2UxNDM"),
    ("gateway143network143", "Z2F0ZXdheTE0M25ldHdvcmsxNDM"),
    ("gateway143latency143", "Z2F0ZXdheTE0M2xhdGVuY3kxNDM"),
    ("storage143latency143", "c3RvcmFnZTE0M2xhdGVuY3kxNDM"),
    ("storage143buffer143", "c3RvcmFnZTE0M2J1ZmZlcjE0Mw"),
    ("storage143queue143", "c3RvcmFnZTE0M3F1ZXVlMTQz"),
    ("storage143worker143", "c3RvcmFnZTE0M3dvcmtlcjE0Mw"),
    ("network143worker143", "bmV0d29yazE0M3dvcmtlcjE0Mw"),
    ("network143kernel143", "bmV0d29yazE0M2tlcm5lbDE0Mw"),
    ("network143signal143", "bmV0d29yazE0M3NpZ25hbDE0Mw"),
    ("network143packet143", "bmV0d29yazE0M3BhY2tldDE0Mw"),
    ("latency143packet143", "bGF0ZW5jeTE0M3BhY2tldDE0Mw"),
    ("latency143router143", "bGF0ZW5jeTE0M3JvdXRlcjE0Mw"),
    ("latency143cluster143", "bGF0ZW5jeTE0M2NsdXN0ZXIxNDM"),
    ("latency143mirror143", "bGF0ZW5jeTE0M21pcnJvcjE0Mw"),
    ("buffer143mirror143", "YnVmZmVyMTQzbWlycm9yMTQz"),
    ("buffer143filter143", "YnVmZmVyMTQzZmlsdGVyMTQz"),
    ("buffer143ranking143", "YnVmZmVyMTQzcmFua2luZzE0Mw"),
    ("buffer143encoding143", "YnVmZmVyMTQzZW5jb2RpbmcxNDM"),
    ("queue143encoding143", "cXVldWUxNDNlbmNvZGluZzE0Mw"),
    ("queue143mapping143", "cXVldWUxNDNtYXBwaW5nMTQz"),
    ("queue143record143", "cXVldWUxNDNyZWNvcmQxNDM"),
    ("queue143candle143", "cXVldWUxNDNjYW5kbGUxNDM"),
    ("worker143candle143", "d29ya2VyMTQzY2FuZGxlMTQz"),
    ("worker143thread143", "d29ya2VyMTQzdGhyZWFkMTQz"),
    ("worker143kitten143", "d29ya2VyMTQza2l0dGVuMTQz"),
    ("worker143sitting143", "d29ya2VyMTQzc2l0dGluZzE0Mw"),
    ("kernel143sitting143", "a2VybmVsMTQzc2l0dGluZzE0Mw"),
    ("kernel143agent143", "a2VybmVsMTQzYWdlbnQxNDM"),
    ("kernel143angle143", "a2VybmVsMTQzYW5nbGUxNDM"),
    ("kernel143universe143", "a2VybmVsMTQzdW5pdmVyc2UxNDM"),
    ("signal143universe143", "c2lnbmFsMTQzdW5pdmVyc2UxNDM"),
    ("signal143memory143", "c2lnbmFsMTQzbWVtb3J5MTQz"),
    ("signal143stream143", "c2lnbmFsMTQzc3RyZWFtMTQz"),
    ("signal143context143", "c2lnbmFsMTQzY29udGV4dDE0Mw"),
    ("packet143context143", "cGFja2V0MTQzY29udGV4dDE0Mw"),
    ("packet143knowledge143", "cGFja2V0MTQza25vd2xlZGdlMTQz"),
    ("packet143vector143", "cGFja2V0MTQzdmVjdG9yMTQz"),
    ("packet143processor143", "cGFja2V0MTQzcHJvY2Vzc29yMTQz"),
    ("router143processor143", "cm91dGVyMTQzcHJvY2Vzc29yMTQz"),
    ("router143reasoning143", "cm91dGVyMTQzcmVhc29uaW5nMTQz"),
    ("router143machine143", "cm91dGVyMTQzbWFjaGluZTE0Mw"),
    ("router143learning143", "cm91dGVyMTQzbGVhcm5pbmcxNDM"),
    ("cluster143learning143", "Y2x1c3RlcjE0M2xlYXJuaW5nMTQz"),
    ("cluster143model143", "Y2x1c3RlcjE0M21vZGVsMTQz"),
    ("cluster143token143", "Y2x1c3RlcjE0M3Rva2VuMTQz"),
    ("cluster143prompt143", "Y2x1c3RlcjE0M3Byb21wdDE0Mw"),
    ("mirror143prompt143", "bWlycm9yMTQzcHJvbXB0MTQz"),
    ("mirror143session143", "bWlycm9yMTQzc2Vzc2lvbjE0Mw"),
    ("mirror143library143", "bWlycm9yMTQzbGlicmFyeTE0Mw"),
    ("mirror143service143", "bWlycm9yMTQzc2VydmljZTE0Mw"),
    ("filter143service143", "ZmlsdGVyMTQzc2VydmljZTE0Mw"),
    ("filter143gateway143", "ZmlsdGVyMTQzZ2F0ZXdheTE0Mw"),
    ("filter143storage143", "ZmlsdGVyMTQzc3RvcmFnZTE0Mw"),
    ("filter143network143", "ZmlsdGVyMTQzbmV0d29yazE0Mw"),
    ("ranking143network143", "cmFua2luZzE0M25ldHdvcmsxNDM"),
    ("ranking143latency143", "cmFua2luZzE0M2xhdGVuY3kxNDM"),
    ("ranking143buffer143", "cmFua2luZzE0M2J1ZmZlcjE0Mw"),
    ("ranking143queue143", "cmFua2luZzE0M3F1ZXVlMTQz"),
    ("encoding143queue143", "ZW5jb2RpbmcxNDNxdWV1ZTE0Mw"),
    ("encoding143worker143", "ZW5jb2RpbmcxNDN3b3JrZXIxNDM"),
    ("encoding143kernel143", "ZW5jb2RpbmcxNDNrZXJuZWwxNDM"),
    ("encoding143signal143", "ZW5jb2RpbmcxNDNzaWduYWwxNDM"),
    ("mapping143signal143", "bWFwcGluZzE0M3NpZ25hbDE0Mw"),
    ("mapping143packet143", "bWFwcGluZzE0M3BhY2tldDE0Mw"),
    ("mapping143router143", "bWFwcGluZzE0M3JvdXRlcjE0Mw"),
    ("mapping143cluster143", "bWFwcGluZzE0M2NsdXN0ZXIxNDM"),
    ("record143cluster143", "cmVjb3JkMTQzY2x1c3RlcjE0Mw"),
    ("record143mirror143", "cmVjb3JkMTQzbWlycm9yMTQz"),
    ("record143filter143", "cmVjb3JkMTQzZmlsdGVyMTQz"),
    ("record143ranking143", "cmVjb3JkMTQzcmFua2luZzE0Mw"),
    ("candle143ranking143", "Y2FuZGxlMTQzcmFua2luZzE0Mw"),
    ("candle143encoding143", "Y2FuZGxlMTQzZW5jb2RpbmcxNDM"),
    ("candle143mapping143", "Y2FuZGxlMTQzbWFwcGluZzE0Mw"),
    ("candle143record143", "Y2FuZGxlMTQzcmVjb3JkMTQz"),
    ("thread143record143", "dGhyZWFkMTQzcmVjb3JkMTQz"),
    ("thread143candle143", "dGhyZWFkMTQzY2FuZGxlMTQz"),
    ("thread143thread143", "dGhyZWFkMTQzdGhyZWFkMTQz"),
    ("thread143kitten143", "dGhyZWFkMTQza2l0dGVuMTQz"),
    (
        "round 143: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTQzOiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 143: agentuniverse is a framework for multi agents",
        "cm91bmQgMTQzOiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 143: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTQzOiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 143: the processor reads the record then stops",
        "cm91bmQgMTQzOiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 143: a worker pulls the next task from the queue",
        "cm91bmQgMTQzOiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 143: signals travel through the network layer",
        "cm91bmQgMTQzOiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 143: the gateway routes each request by policy",
        "cm91bmQgMTQzOiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 143: memory grows until the buffer is full",
        "cm91bmQgMTQzOiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 143: the cluster mirrors every packet twice",
        "cm91bmQgMTQzOiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 143: ranking uses tokens learned from the corpus",
        "cm91bmQgMTQzOiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 143: a long session ends when the candle dies",
        "cm91bmQgMTQzOiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 143: encode the prompt then map the result",
        "cm91bmQgMTQzOiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 143: the kernel wakes the worker at dawn",
        "cm91bmQgMTQzOiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 143: service latency drops after the patch",
        "cm91bmQgMTQzOiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 143: the library caches every vector it sees",
        "cm91bmQgMTQzOiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 143: agents argue then the debate resolves",
        "cm91bmQgMTQzOiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 143: the filter keeps only strong matches",
        "cm91bmQgMTQzOiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 143: the model answers with a short reply",
        "cm91bmQgMTQzOiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 143: the recorder stores the reasoning trace",
        "cm91bmQgMTQzOiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 143: the angel watches the processor run",
        "cm91bmQgMTQzOiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 143: angle of the vector decides the match",
        "cm91bmQgMTQzOiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 143: the candle burns twice as long at night",
        "cm91bmQgMTQzOiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 143: a mirror of the universe in one line",
        "cm91bmQgMTQzOiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 143: the queue drains before the storm", "cm91bmQgMTQzOiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
