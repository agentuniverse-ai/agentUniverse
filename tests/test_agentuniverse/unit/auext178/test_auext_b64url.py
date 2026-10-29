"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten178kitten178", "a2l0dGVuMTc4a2l0dGVuMTc4"),
    ("kitten178sitting178", "a2l0dGVuMTc4c2l0dGluZzE3OA"),
    ("kitten178agent178", "a2l0dGVuMTc4YWdlbnQxNzg"),
    ("kitten178angle178", "a2l0dGVuMTc4YW5nbGUxNzg"),
    ("sitting178angle178", "c2l0dGluZzE3OGFuZ2xlMTc4"),
    ("sitting178universe178", "c2l0dGluZzE3OHVuaXZlcnNlMTc4"),
    ("sitting178memory178", "c2l0dGluZzE3OG1lbW9yeTE3OA"),
    ("sitting178stream178", "c2l0dGluZzE3OHN0cmVhbTE3OA"),
    ("agent178stream178", "YWdlbnQxNzhzdHJlYW0xNzg"),
    ("agent178context178", "YWdlbnQxNzhjb250ZXh0MTc4"),
    ("agent178knowledge178", "YWdlbnQxNzhrbm93bGVkZ2UxNzg"),
    ("agent178vector178", "YWdlbnQxNzh2ZWN0b3IxNzg"),
    ("angle178vector178", "YW5nbGUxNzh2ZWN0b3IxNzg"),
    ("angle178processor178", "YW5nbGUxNzhwcm9jZXNzb3IxNzg"),
    ("angle178reasoning178", "YW5nbGUxNzhyZWFzb25pbmcxNzg"),
    ("angle178machine178", "YW5nbGUxNzhtYWNoaW5lMTc4"),
    ("universe178machine178", "dW5pdmVyc2UxNzhtYWNoaW5lMTc4"),
    ("universe178learning178", "dW5pdmVyc2UxNzhsZWFybmluZzE3OA"),
    ("universe178model178", "dW5pdmVyc2UxNzhtb2RlbDE3OA"),
    ("universe178token178", "dW5pdmVyc2UxNzh0b2tlbjE3OA"),
    ("memory178token178", "bWVtb3J5MTc4dG9rZW4xNzg"),
    ("memory178prompt178", "bWVtb3J5MTc4cHJvbXB0MTc4"),
    ("memory178session178", "bWVtb3J5MTc4c2Vzc2lvbjE3OA"),
    ("memory178library178", "bWVtb3J5MTc4bGlicmFyeTE3OA"),
    ("stream178library178", "c3RyZWFtMTc4bGlicmFyeTE3OA"),
    ("stream178service178", "c3RyZWFtMTc4c2VydmljZTE3OA"),
    ("stream178gateway178", "c3RyZWFtMTc4Z2F0ZXdheTE3OA"),
    ("stream178storage178", "c3RyZWFtMTc4c3RvcmFnZTE3OA"),
    ("context178storage178", "Y29udGV4dDE3OHN0b3JhZ2UxNzg"),
    ("context178network178", "Y29udGV4dDE3OG5ldHdvcmsxNzg"),
    ("context178latency178", "Y29udGV4dDE3OGxhdGVuY3kxNzg"),
    ("context178buffer178", "Y29udGV4dDE3OGJ1ZmZlcjE3OA"),
    ("knowledge178buffer178", "a25vd2xlZGdlMTc4YnVmZmVyMTc4"),
    ("knowledge178queue178", "a25vd2xlZGdlMTc4cXVldWUxNzg"),
    ("knowledge178worker178", "a25vd2xlZGdlMTc4d29ya2VyMTc4"),
    ("knowledge178kernel178", "a25vd2xlZGdlMTc4a2VybmVsMTc4"),
    ("vector178kernel178", "dmVjdG9yMTc4a2VybmVsMTc4"),
    ("vector178signal178", "dmVjdG9yMTc4c2lnbmFsMTc4"),
    ("vector178packet178", "dmVjdG9yMTc4cGFja2V0MTc4"),
    ("vector178router178", "dmVjdG9yMTc4cm91dGVyMTc4"),
    ("processor178router178", "cHJvY2Vzc29yMTc4cm91dGVyMTc4"),
    ("processor178cluster178", "cHJvY2Vzc29yMTc4Y2x1c3RlcjE3OA"),
    ("processor178mirror178", "cHJvY2Vzc29yMTc4bWlycm9yMTc4"),
    ("processor178filter178", "cHJvY2Vzc29yMTc4ZmlsdGVyMTc4"),
    ("reasoning178filter178", "cmVhc29uaW5nMTc4ZmlsdGVyMTc4"),
    ("reasoning178ranking178", "cmVhc29uaW5nMTc4cmFua2luZzE3OA"),
    ("reasoning178encoding178", "cmVhc29uaW5nMTc4ZW5jb2RpbmcxNzg"),
    ("reasoning178mapping178", "cmVhc29uaW5nMTc4bWFwcGluZzE3OA"),
    ("machine178mapping178", "bWFjaGluZTE3OG1hcHBpbmcxNzg"),
    ("machine178record178", "bWFjaGluZTE3OHJlY29yZDE3OA"),
    ("machine178candle178", "bWFjaGluZTE3OGNhbmRsZTE3OA"),
    ("machine178thread178", "bWFjaGluZTE3OHRocmVhZDE3OA"),
    ("learning178thread178", "bGVhcm5pbmcxNzh0aHJlYWQxNzg"),
    ("learning178kitten178", "bGVhcm5pbmcxNzhraXR0ZW4xNzg"),
    ("learning178sitting178", "bGVhcm5pbmcxNzhzaXR0aW5nMTc4"),
    ("learning178agent178", "bGVhcm5pbmcxNzhhZ2VudDE3OA"),
    ("model178agent178", "bW9kZWwxNzhhZ2VudDE3OA"),
    ("model178angle178", "bW9kZWwxNzhhbmdsZTE3OA"),
    ("model178universe178", "bW9kZWwxNzh1bml2ZXJzZTE3OA"),
    ("model178memory178", "bW9kZWwxNzhtZW1vcnkxNzg"),
    ("token178memory178", "dG9rZW4xNzhtZW1vcnkxNzg"),
    ("token178stream178", "dG9rZW4xNzhzdHJlYW0xNzg"),
    ("token178context178", "dG9rZW4xNzhjb250ZXh0MTc4"),
    ("token178knowledge178", "dG9rZW4xNzhrbm93bGVkZ2UxNzg"),
    ("prompt178knowledge178", "cHJvbXB0MTc4a25vd2xlZGdlMTc4"),
    ("prompt178vector178", "cHJvbXB0MTc4dmVjdG9yMTc4"),
    ("prompt178processor178", "cHJvbXB0MTc4cHJvY2Vzc29yMTc4"),
    ("prompt178reasoning178", "cHJvbXB0MTc4cmVhc29uaW5nMTc4"),
    ("session178reasoning178", "c2Vzc2lvbjE3OHJlYXNvbmluZzE3OA"),
    ("session178machine178", "c2Vzc2lvbjE3OG1hY2hpbmUxNzg"),
    ("session178learning178", "c2Vzc2lvbjE3OGxlYXJuaW5nMTc4"),
    ("session178model178", "c2Vzc2lvbjE3OG1vZGVsMTc4"),
    ("library178model178", "bGlicmFyeTE3OG1vZGVsMTc4"),
    ("library178token178", "bGlicmFyeTE3OHRva2VuMTc4"),
    ("library178prompt178", "bGlicmFyeTE3OHByb21wdDE3OA"),
    ("library178session178", "bGlicmFyeTE3OHNlc3Npb24xNzg"),
    ("service178session178", "c2VydmljZTE3OHNlc3Npb24xNzg"),
    ("service178library178", "c2VydmljZTE3OGxpYnJhcnkxNzg"),
    ("service178service178", "c2VydmljZTE3OHNlcnZpY2UxNzg"),
    ("service178gateway178", "c2VydmljZTE3OGdhdGV3YXkxNzg"),
    ("gateway178gateway178", "Z2F0ZXdheTE3OGdhdGV3YXkxNzg"),
    ("gateway178storage178", "Z2F0ZXdheTE3OHN0b3JhZ2UxNzg"),
    ("gateway178network178", "Z2F0ZXdheTE3OG5ldHdvcmsxNzg"),
    ("gateway178latency178", "Z2F0ZXdheTE3OGxhdGVuY3kxNzg"),
    ("storage178latency178", "c3RvcmFnZTE3OGxhdGVuY3kxNzg"),
    ("storage178buffer178", "c3RvcmFnZTE3OGJ1ZmZlcjE3OA"),
    ("storage178queue178", "c3RvcmFnZTE3OHF1ZXVlMTc4"),
    ("storage178worker178", "c3RvcmFnZTE3OHdvcmtlcjE3OA"),
    ("network178worker178", "bmV0d29yazE3OHdvcmtlcjE3OA"),
    ("network178kernel178", "bmV0d29yazE3OGtlcm5lbDE3OA"),
    ("network178signal178", "bmV0d29yazE3OHNpZ25hbDE3OA"),
    ("network178packet178", "bmV0d29yazE3OHBhY2tldDE3OA"),
    ("latency178packet178", "bGF0ZW5jeTE3OHBhY2tldDE3OA"),
    ("latency178router178", "bGF0ZW5jeTE3OHJvdXRlcjE3OA"),
    ("latency178cluster178", "bGF0ZW5jeTE3OGNsdXN0ZXIxNzg"),
    ("latency178mirror178", "bGF0ZW5jeTE3OG1pcnJvcjE3OA"),
    ("buffer178mirror178", "YnVmZmVyMTc4bWlycm9yMTc4"),
    ("buffer178filter178", "YnVmZmVyMTc4ZmlsdGVyMTc4"),
    ("buffer178ranking178", "YnVmZmVyMTc4cmFua2luZzE3OA"),
    ("buffer178encoding178", "YnVmZmVyMTc4ZW5jb2RpbmcxNzg"),
    ("queue178encoding178", "cXVldWUxNzhlbmNvZGluZzE3OA"),
    ("queue178mapping178", "cXVldWUxNzhtYXBwaW5nMTc4"),
    ("queue178record178", "cXVldWUxNzhyZWNvcmQxNzg"),
    ("queue178candle178", "cXVldWUxNzhjYW5kbGUxNzg"),
    ("worker178candle178", "d29ya2VyMTc4Y2FuZGxlMTc4"),
    ("worker178thread178", "d29ya2VyMTc4dGhyZWFkMTc4"),
    ("worker178kitten178", "d29ya2VyMTc4a2l0dGVuMTc4"),
    ("worker178sitting178", "d29ya2VyMTc4c2l0dGluZzE3OA"),
    ("kernel178sitting178", "a2VybmVsMTc4c2l0dGluZzE3OA"),
    ("kernel178agent178", "a2VybmVsMTc4YWdlbnQxNzg"),
    ("kernel178angle178", "a2VybmVsMTc4YW5nbGUxNzg"),
    ("kernel178universe178", "a2VybmVsMTc4dW5pdmVyc2UxNzg"),
    ("signal178universe178", "c2lnbmFsMTc4dW5pdmVyc2UxNzg"),
    ("signal178memory178", "c2lnbmFsMTc4bWVtb3J5MTc4"),
    ("signal178stream178", "c2lnbmFsMTc4c3RyZWFtMTc4"),
    ("signal178context178", "c2lnbmFsMTc4Y29udGV4dDE3OA"),
    ("packet178context178", "cGFja2V0MTc4Y29udGV4dDE3OA"),
    ("packet178knowledge178", "cGFja2V0MTc4a25vd2xlZGdlMTc4"),
    ("packet178vector178", "cGFja2V0MTc4dmVjdG9yMTc4"),
    ("packet178processor178", "cGFja2V0MTc4cHJvY2Vzc29yMTc4"),
    ("router178processor178", "cm91dGVyMTc4cHJvY2Vzc29yMTc4"),
    ("router178reasoning178", "cm91dGVyMTc4cmVhc29uaW5nMTc4"),
    ("router178machine178", "cm91dGVyMTc4bWFjaGluZTE3OA"),
    ("router178learning178", "cm91dGVyMTc4bGVhcm5pbmcxNzg"),
    ("cluster178learning178", "Y2x1c3RlcjE3OGxlYXJuaW5nMTc4"),
    ("cluster178model178", "Y2x1c3RlcjE3OG1vZGVsMTc4"),
    ("cluster178token178", "Y2x1c3RlcjE3OHRva2VuMTc4"),
    ("cluster178prompt178", "Y2x1c3RlcjE3OHByb21wdDE3OA"),
    ("mirror178prompt178", "bWlycm9yMTc4cHJvbXB0MTc4"),
    ("mirror178session178", "bWlycm9yMTc4c2Vzc2lvbjE3OA"),
    ("mirror178library178", "bWlycm9yMTc4bGlicmFyeTE3OA"),
    ("mirror178service178", "bWlycm9yMTc4c2VydmljZTE3OA"),
    ("filter178service178", "ZmlsdGVyMTc4c2VydmljZTE3OA"),
    ("filter178gateway178", "ZmlsdGVyMTc4Z2F0ZXdheTE3OA"),
    ("filter178storage178", "ZmlsdGVyMTc4c3RvcmFnZTE3OA"),
    ("filter178network178", "ZmlsdGVyMTc4bmV0d29yazE3OA"),
    ("ranking178network178", "cmFua2luZzE3OG5ldHdvcmsxNzg"),
    ("ranking178latency178", "cmFua2luZzE3OGxhdGVuY3kxNzg"),
    ("ranking178buffer178", "cmFua2luZzE3OGJ1ZmZlcjE3OA"),
    ("ranking178queue178", "cmFua2luZzE3OHF1ZXVlMTc4"),
    ("encoding178queue178", "ZW5jb2RpbmcxNzhxdWV1ZTE3OA"),
    ("encoding178worker178", "ZW5jb2RpbmcxNzh3b3JrZXIxNzg"),
    ("encoding178kernel178", "ZW5jb2RpbmcxNzhrZXJuZWwxNzg"),
    ("encoding178signal178", "ZW5jb2RpbmcxNzhzaWduYWwxNzg"),
    ("mapping178signal178", "bWFwcGluZzE3OHNpZ25hbDE3OA"),
    ("mapping178packet178", "bWFwcGluZzE3OHBhY2tldDE3OA"),
    ("mapping178router178", "bWFwcGluZzE3OHJvdXRlcjE3OA"),
    ("mapping178cluster178", "bWFwcGluZzE3OGNsdXN0ZXIxNzg"),
    ("record178cluster178", "cmVjb3JkMTc4Y2x1c3RlcjE3OA"),
    ("record178mirror178", "cmVjb3JkMTc4bWlycm9yMTc4"),
    ("record178filter178", "cmVjb3JkMTc4ZmlsdGVyMTc4"),
    ("record178ranking178", "cmVjb3JkMTc4cmFua2luZzE3OA"),
    ("candle178ranking178", "Y2FuZGxlMTc4cmFua2luZzE3OA"),
    ("candle178encoding178", "Y2FuZGxlMTc4ZW5jb2RpbmcxNzg"),
    ("candle178mapping178", "Y2FuZGxlMTc4bWFwcGluZzE3OA"),
    ("candle178record178", "Y2FuZGxlMTc4cmVjb3JkMTc4"),
    ("thread178record178", "dGhyZWFkMTc4cmVjb3JkMTc4"),
    ("thread178candle178", "dGhyZWFkMTc4Y2FuZGxlMTc4"),
    ("thread178thread178", "dGhyZWFkMTc4dGhyZWFkMTc4"),
    ("thread178kitten178", "dGhyZWFkMTc4a2l0dGVuMTc4"),
    (
        "round 178: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTc4OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 178: agentuniverse is a framework for multi agents",
        "cm91bmQgMTc4OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 178: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTc4OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 178: the processor reads the record then stops",
        "cm91bmQgMTc4OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 178: a worker pulls the next task from the queue",
        "cm91bmQgMTc4OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 178: signals travel through the network layer",
        "cm91bmQgMTc4OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 178: the gateway routes each request by policy",
        "cm91bmQgMTc4OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 178: memory grows until the buffer is full",
        "cm91bmQgMTc4OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 178: the cluster mirrors every packet twice",
        "cm91bmQgMTc4OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 178: ranking uses tokens learned from the corpus",
        "cm91bmQgMTc4OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 178: a long session ends when the candle dies",
        "cm91bmQgMTc4OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 178: encode the prompt then map the result",
        "cm91bmQgMTc4OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 178: the kernel wakes the worker at dawn",
        "cm91bmQgMTc4OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 178: service latency drops after the patch",
        "cm91bmQgMTc4OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 178: the library caches every vector it sees",
        "cm91bmQgMTc4OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 178: agents argue then the debate resolves",
        "cm91bmQgMTc4OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 178: the filter keeps only strong matches",
        "cm91bmQgMTc4OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 178: the model answers with a short reply",
        "cm91bmQgMTc4OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 178: the recorder stores the reasoning trace",
        "cm91bmQgMTc4OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 178: the angel watches the processor run",
        "cm91bmQgMTc4OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 178: angle of the vector decides the match",
        "cm91bmQgMTc4OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 178: the candle burns twice as long at night",
        "cm91bmQgMTc4OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 178: a mirror of the universe in one line",
        "cm91bmQgMTc4OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 178: the queue drains before the storm", "cm91bmQgMTc4OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
