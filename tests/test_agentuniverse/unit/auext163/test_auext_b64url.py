"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten163kitten163", "a2l0dGVuMTYza2l0dGVuMTYz"),
    ("kitten163sitting163", "a2l0dGVuMTYzc2l0dGluZzE2Mw"),
    ("kitten163agent163", "a2l0dGVuMTYzYWdlbnQxNjM"),
    ("kitten163angle163", "a2l0dGVuMTYzYW5nbGUxNjM"),
    ("sitting163angle163", "c2l0dGluZzE2M2FuZ2xlMTYz"),
    ("sitting163universe163", "c2l0dGluZzE2M3VuaXZlcnNlMTYz"),
    ("sitting163memory163", "c2l0dGluZzE2M21lbW9yeTE2Mw"),
    ("sitting163stream163", "c2l0dGluZzE2M3N0cmVhbTE2Mw"),
    ("agent163stream163", "YWdlbnQxNjNzdHJlYW0xNjM"),
    ("agent163context163", "YWdlbnQxNjNjb250ZXh0MTYz"),
    ("agent163knowledge163", "YWdlbnQxNjNrbm93bGVkZ2UxNjM"),
    ("agent163vector163", "YWdlbnQxNjN2ZWN0b3IxNjM"),
    ("angle163vector163", "YW5nbGUxNjN2ZWN0b3IxNjM"),
    ("angle163processor163", "YW5nbGUxNjNwcm9jZXNzb3IxNjM"),
    ("angle163reasoning163", "YW5nbGUxNjNyZWFzb25pbmcxNjM"),
    ("angle163machine163", "YW5nbGUxNjNtYWNoaW5lMTYz"),
    ("universe163machine163", "dW5pdmVyc2UxNjNtYWNoaW5lMTYz"),
    ("universe163learning163", "dW5pdmVyc2UxNjNsZWFybmluZzE2Mw"),
    ("universe163model163", "dW5pdmVyc2UxNjNtb2RlbDE2Mw"),
    ("universe163token163", "dW5pdmVyc2UxNjN0b2tlbjE2Mw"),
    ("memory163token163", "bWVtb3J5MTYzdG9rZW4xNjM"),
    ("memory163prompt163", "bWVtb3J5MTYzcHJvbXB0MTYz"),
    ("memory163session163", "bWVtb3J5MTYzc2Vzc2lvbjE2Mw"),
    ("memory163library163", "bWVtb3J5MTYzbGlicmFyeTE2Mw"),
    ("stream163library163", "c3RyZWFtMTYzbGlicmFyeTE2Mw"),
    ("stream163service163", "c3RyZWFtMTYzc2VydmljZTE2Mw"),
    ("stream163gateway163", "c3RyZWFtMTYzZ2F0ZXdheTE2Mw"),
    ("stream163storage163", "c3RyZWFtMTYzc3RvcmFnZTE2Mw"),
    ("context163storage163", "Y29udGV4dDE2M3N0b3JhZ2UxNjM"),
    ("context163network163", "Y29udGV4dDE2M25ldHdvcmsxNjM"),
    ("context163latency163", "Y29udGV4dDE2M2xhdGVuY3kxNjM"),
    ("context163buffer163", "Y29udGV4dDE2M2J1ZmZlcjE2Mw"),
    ("knowledge163buffer163", "a25vd2xlZGdlMTYzYnVmZmVyMTYz"),
    ("knowledge163queue163", "a25vd2xlZGdlMTYzcXVldWUxNjM"),
    ("knowledge163worker163", "a25vd2xlZGdlMTYzd29ya2VyMTYz"),
    ("knowledge163kernel163", "a25vd2xlZGdlMTYza2VybmVsMTYz"),
    ("vector163kernel163", "dmVjdG9yMTYza2VybmVsMTYz"),
    ("vector163signal163", "dmVjdG9yMTYzc2lnbmFsMTYz"),
    ("vector163packet163", "dmVjdG9yMTYzcGFja2V0MTYz"),
    ("vector163router163", "dmVjdG9yMTYzcm91dGVyMTYz"),
    ("processor163router163", "cHJvY2Vzc29yMTYzcm91dGVyMTYz"),
    ("processor163cluster163", "cHJvY2Vzc29yMTYzY2x1c3RlcjE2Mw"),
    ("processor163mirror163", "cHJvY2Vzc29yMTYzbWlycm9yMTYz"),
    ("processor163filter163", "cHJvY2Vzc29yMTYzZmlsdGVyMTYz"),
    ("reasoning163filter163", "cmVhc29uaW5nMTYzZmlsdGVyMTYz"),
    ("reasoning163ranking163", "cmVhc29uaW5nMTYzcmFua2luZzE2Mw"),
    ("reasoning163encoding163", "cmVhc29uaW5nMTYzZW5jb2RpbmcxNjM"),
    ("reasoning163mapping163", "cmVhc29uaW5nMTYzbWFwcGluZzE2Mw"),
    ("machine163mapping163", "bWFjaGluZTE2M21hcHBpbmcxNjM"),
    ("machine163record163", "bWFjaGluZTE2M3JlY29yZDE2Mw"),
    ("machine163candle163", "bWFjaGluZTE2M2NhbmRsZTE2Mw"),
    ("machine163thread163", "bWFjaGluZTE2M3RocmVhZDE2Mw"),
    ("learning163thread163", "bGVhcm5pbmcxNjN0aHJlYWQxNjM"),
    ("learning163kitten163", "bGVhcm5pbmcxNjNraXR0ZW4xNjM"),
    ("learning163sitting163", "bGVhcm5pbmcxNjNzaXR0aW5nMTYz"),
    ("learning163agent163", "bGVhcm5pbmcxNjNhZ2VudDE2Mw"),
    ("model163agent163", "bW9kZWwxNjNhZ2VudDE2Mw"),
    ("model163angle163", "bW9kZWwxNjNhbmdsZTE2Mw"),
    ("model163universe163", "bW9kZWwxNjN1bml2ZXJzZTE2Mw"),
    ("model163memory163", "bW9kZWwxNjNtZW1vcnkxNjM"),
    ("token163memory163", "dG9rZW4xNjNtZW1vcnkxNjM"),
    ("token163stream163", "dG9rZW4xNjNzdHJlYW0xNjM"),
    ("token163context163", "dG9rZW4xNjNjb250ZXh0MTYz"),
    ("token163knowledge163", "dG9rZW4xNjNrbm93bGVkZ2UxNjM"),
    ("prompt163knowledge163", "cHJvbXB0MTYza25vd2xlZGdlMTYz"),
    ("prompt163vector163", "cHJvbXB0MTYzdmVjdG9yMTYz"),
    ("prompt163processor163", "cHJvbXB0MTYzcHJvY2Vzc29yMTYz"),
    ("prompt163reasoning163", "cHJvbXB0MTYzcmVhc29uaW5nMTYz"),
    ("session163reasoning163", "c2Vzc2lvbjE2M3JlYXNvbmluZzE2Mw"),
    ("session163machine163", "c2Vzc2lvbjE2M21hY2hpbmUxNjM"),
    ("session163learning163", "c2Vzc2lvbjE2M2xlYXJuaW5nMTYz"),
    ("session163model163", "c2Vzc2lvbjE2M21vZGVsMTYz"),
    ("library163model163", "bGlicmFyeTE2M21vZGVsMTYz"),
    ("library163token163", "bGlicmFyeTE2M3Rva2VuMTYz"),
    ("library163prompt163", "bGlicmFyeTE2M3Byb21wdDE2Mw"),
    ("library163session163", "bGlicmFyeTE2M3Nlc3Npb24xNjM"),
    ("service163session163", "c2VydmljZTE2M3Nlc3Npb24xNjM"),
    ("service163library163", "c2VydmljZTE2M2xpYnJhcnkxNjM"),
    ("service163service163", "c2VydmljZTE2M3NlcnZpY2UxNjM"),
    ("service163gateway163", "c2VydmljZTE2M2dhdGV3YXkxNjM"),
    ("gateway163gateway163", "Z2F0ZXdheTE2M2dhdGV3YXkxNjM"),
    ("gateway163storage163", "Z2F0ZXdheTE2M3N0b3JhZ2UxNjM"),
    ("gateway163network163", "Z2F0ZXdheTE2M25ldHdvcmsxNjM"),
    ("gateway163latency163", "Z2F0ZXdheTE2M2xhdGVuY3kxNjM"),
    ("storage163latency163", "c3RvcmFnZTE2M2xhdGVuY3kxNjM"),
    ("storage163buffer163", "c3RvcmFnZTE2M2J1ZmZlcjE2Mw"),
    ("storage163queue163", "c3RvcmFnZTE2M3F1ZXVlMTYz"),
    ("storage163worker163", "c3RvcmFnZTE2M3dvcmtlcjE2Mw"),
    ("network163worker163", "bmV0d29yazE2M3dvcmtlcjE2Mw"),
    ("network163kernel163", "bmV0d29yazE2M2tlcm5lbDE2Mw"),
    ("network163signal163", "bmV0d29yazE2M3NpZ25hbDE2Mw"),
    ("network163packet163", "bmV0d29yazE2M3BhY2tldDE2Mw"),
    ("latency163packet163", "bGF0ZW5jeTE2M3BhY2tldDE2Mw"),
    ("latency163router163", "bGF0ZW5jeTE2M3JvdXRlcjE2Mw"),
    ("latency163cluster163", "bGF0ZW5jeTE2M2NsdXN0ZXIxNjM"),
    ("latency163mirror163", "bGF0ZW5jeTE2M21pcnJvcjE2Mw"),
    ("buffer163mirror163", "YnVmZmVyMTYzbWlycm9yMTYz"),
    ("buffer163filter163", "YnVmZmVyMTYzZmlsdGVyMTYz"),
    ("buffer163ranking163", "YnVmZmVyMTYzcmFua2luZzE2Mw"),
    ("buffer163encoding163", "YnVmZmVyMTYzZW5jb2RpbmcxNjM"),
    ("queue163encoding163", "cXVldWUxNjNlbmNvZGluZzE2Mw"),
    ("queue163mapping163", "cXVldWUxNjNtYXBwaW5nMTYz"),
    ("queue163record163", "cXVldWUxNjNyZWNvcmQxNjM"),
    ("queue163candle163", "cXVldWUxNjNjYW5kbGUxNjM"),
    ("worker163candle163", "d29ya2VyMTYzY2FuZGxlMTYz"),
    ("worker163thread163", "d29ya2VyMTYzdGhyZWFkMTYz"),
    ("worker163kitten163", "d29ya2VyMTYza2l0dGVuMTYz"),
    ("worker163sitting163", "d29ya2VyMTYzc2l0dGluZzE2Mw"),
    ("kernel163sitting163", "a2VybmVsMTYzc2l0dGluZzE2Mw"),
    ("kernel163agent163", "a2VybmVsMTYzYWdlbnQxNjM"),
    ("kernel163angle163", "a2VybmVsMTYzYW5nbGUxNjM"),
    ("kernel163universe163", "a2VybmVsMTYzdW5pdmVyc2UxNjM"),
    ("signal163universe163", "c2lnbmFsMTYzdW5pdmVyc2UxNjM"),
    ("signal163memory163", "c2lnbmFsMTYzbWVtb3J5MTYz"),
    ("signal163stream163", "c2lnbmFsMTYzc3RyZWFtMTYz"),
    ("signal163context163", "c2lnbmFsMTYzY29udGV4dDE2Mw"),
    ("packet163context163", "cGFja2V0MTYzY29udGV4dDE2Mw"),
    ("packet163knowledge163", "cGFja2V0MTYza25vd2xlZGdlMTYz"),
    ("packet163vector163", "cGFja2V0MTYzdmVjdG9yMTYz"),
    ("packet163processor163", "cGFja2V0MTYzcHJvY2Vzc29yMTYz"),
    ("router163processor163", "cm91dGVyMTYzcHJvY2Vzc29yMTYz"),
    ("router163reasoning163", "cm91dGVyMTYzcmVhc29uaW5nMTYz"),
    ("router163machine163", "cm91dGVyMTYzbWFjaGluZTE2Mw"),
    ("router163learning163", "cm91dGVyMTYzbGVhcm5pbmcxNjM"),
    ("cluster163learning163", "Y2x1c3RlcjE2M2xlYXJuaW5nMTYz"),
    ("cluster163model163", "Y2x1c3RlcjE2M21vZGVsMTYz"),
    ("cluster163token163", "Y2x1c3RlcjE2M3Rva2VuMTYz"),
    ("cluster163prompt163", "Y2x1c3RlcjE2M3Byb21wdDE2Mw"),
    ("mirror163prompt163", "bWlycm9yMTYzcHJvbXB0MTYz"),
    ("mirror163session163", "bWlycm9yMTYzc2Vzc2lvbjE2Mw"),
    ("mirror163library163", "bWlycm9yMTYzbGlicmFyeTE2Mw"),
    ("mirror163service163", "bWlycm9yMTYzc2VydmljZTE2Mw"),
    ("filter163service163", "ZmlsdGVyMTYzc2VydmljZTE2Mw"),
    ("filter163gateway163", "ZmlsdGVyMTYzZ2F0ZXdheTE2Mw"),
    ("filter163storage163", "ZmlsdGVyMTYzc3RvcmFnZTE2Mw"),
    ("filter163network163", "ZmlsdGVyMTYzbmV0d29yazE2Mw"),
    ("ranking163network163", "cmFua2luZzE2M25ldHdvcmsxNjM"),
    ("ranking163latency163", "cmFua2luZzE2M2xhdGVuY3kxNjM"),
    ("ranking163buffer163", "cmFua2luZzE2M2J1ZmZlcjE2Mw"),
    ("ranking163queue163", "cmFua2luZzE2M3F1ZXVlMTYz"),
    ("encoding163queue163", "ZW5jb2RpbmcxNjNxdWV1ZTE2Mw"),
    ("encoding163worker163", "ZW5jb2RpbmcxNjN3b3JrZXIxNjM"),
    ("encoding163kernel163", "ZW5jb2RpbmcxNjNrZXJuZWwxNjM"),
    ("encoding163signal163", "ZW5jb2RpbmcxNjNzaWduYWwxNjM"),
    ("mapping163signal163", "bWFwcGluZzE2M3NpZ25hbDE2Mw"),
    ("mapping163packet163", "bWFwcGluZzE2M3BhY2tldDE2Mw"),
    ("mapping163router163", "bWFwcGluZzE2M3JvdXRlcjE2Mw"),
    ("mapping163cluster163", "bWFwcGluZzE2M2NsdXN0ZXIxNjM"),
    ("record163cluster163", "cmVjb3JkMTYzY2x1c3RlcjE2Mw"),
    ("record163mirror163", "cmVjb3JkMTYzbWlycm9yMTYz"),
    ("record163filter163", "cmVjb3JkMTYzZmlsdGVyMTYz"),
    ("record163ranking163", "cmVjb3JkMTYzcmFua2luZzE2Mw"),
    ("candle163ranking163", "Y2FuZGxlMTYzcmFua2luZzE2Mw"),
    ("candle163encoding163", "Y2FuZGxlMTYzZW5jb2RpbmcxNjM"),
    ("candle163mapping163", "Y2FuZGxlMTYzbWFwcGluZzE2Mw"),
    ("candle163record163", "Y2FuZGxlMTYzcmVjb3JkMTYz"),
    ("thread163record163", "dGhyZWFkMTYzcmVjb3JkMTYz"),
    ("thread163candle163", "dGhyZWFkMTYzY2FuZGxlMTYz"),
    ("thread163thread163", "dGhyZWFkMTYzdGhyZWFkMTYz"),
    ("thread163kitten163", "dGhyZWFkMTYza2l0dGVuMTYz"),
    (
        "round 163: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTYzOiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 163: agentuniverse is a framework for multi agents",
        "cm91bmQgMTYzOiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 163: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTYzOiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 163: the processor reads the record then stops",
        "cm91bmQgMTYzOiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 163: a worker pulls the next task from the queue",
        "cm91bmQgMTYzOiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 163: signals travel through the network layer",
        "cm91bmQgMTYzOiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 163: the gateway routes each request by policy",
        "cm91bmQgMTYzOiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 163: memory grows until the buffer is full",
        "cm91bmQgMTYzOiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 163: the cluster mirrors every packet twice",
        "cm91bmQgMTYzOiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 163: ranking uses tokens learned from the corpus",
        "cm91bmQgMTYzOiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 163: a long session ends when the candle dies",
        "cm91bmQgMTYzOiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 163: encode the prompt then map the result",
        "cm91bmQgMTYzOiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 163: the kernel wakes the worker at dawn",
        "cm91bmQgMTYzOiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 163: service latency drops after the patch",
        "cm91bmQgMTYzOiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 163: the library caches every vector it sees",
        "cm91bmQgMTYzOiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 163: agents argue then the debate resolves",
        "cm91bmQgMTYzOiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 163: the filter keeps only strong matches",
        "cm91bmQgMTYzOiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 163: the model answers with a short reply",
        "cm91bmQgMTYzOiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 163: the recorder stores the reasoning trace",
        "cm91bmQgMTYzOiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 163: the angel watches the processor run",
        "cm91bmQgMTYzOiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 163: angle of the vector decides the match",
        "cm91bmQgMTYzOiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 163: the candle burns twice as long at night",
        "cm91bmQgMTYzOiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 163: a mirror of the universe in one line",
        "cm91bmQgMTYzOiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 163: the queue drains before the storm", "cm91bmQgMTYzOiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
