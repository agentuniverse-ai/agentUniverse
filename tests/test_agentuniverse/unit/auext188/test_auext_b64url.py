"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten188kitten188", "a2l0dGVuMTg4a2l0dGVuMTg4"),
    ("kitten188sitting188", "a2l0dGVuMTg4c2l0dGluZzE4OA"),
    ("kitten188agent188", "a2l0dGVuMTg4YWdlbnQxODg"),
    ("kitten188angle188", "a2l0dGVuMTg4YW5nbGUxODg"),
    ("sitting188angle188", "c2l0dGluZzE4OGFuZ2xlMTg4"),
    ("sitting188universe188", "c2l0dGluZzE4OHVuaXZlcnNlMTg4"),
    ("sitting188memory188", "c2l0dGluZzE4OG1lbW9yeTE4OA"),
    ("sitting188stream188", "c2l0dGluZzE4OHN0cmVhbTE4OA"),
    ("agent188stream188", "YWdlbnQxODhzdHJlYW0xODg"),
    ("agent188context188", "YWdlbnQxODhjb250ZXh0MTg4"),
    ("agent188knowledge188", "YWdlbnQxODhrbm93bGVkZ2UxODg"),
    ("agent188vector188", "YWdlbnQxODh2ZWN0b3IxODg"),
    ("angle188vector188", "YW5nbGUxODh2ZWN0b3IxODg"),
    ("angle188processor188", "YW5nbGUxODhwcm9jZXNzb3IxODg"),
    ("angle188reasoning188", "YW5nbGUxODhyZWFzb25pbmcxODg"),
    ("angle188machine188", "YW5nbGUxODhtYWNoaW5lMTg4"),
    ("universe188machine188", "dW5pdmVyc2UxODhtYWNoaW5lMTg4"),
    ("universe188learning188", "dW5pdmVyc2UxODhsZWFybmluZzE4OA"),
    ("universe188model188", "dW5pdmVyc2UxODhtb2RlbDE4OA"),
    ("universe188token188", "dW5pdmVyc2UxODh0b2tlbjE4OA"),
    ("memory188token188", "bWVtb3J5MTg4dG9rZW4xODg"),
    ("memory188prompt188", "bWVtb3J5MTg4cHJvbXB0MTg4"),
    ("memory188session188", "bWVtb3J5MTg4c2Vzc2lvbjE4OA"),
    ("memory188library188", "bWVtb3J5MTg4bGlicmFyeTE4OA"),
    ("stream188library188", "c3RyZWFtMTg4bGlicmFyeTE4OA"),
    ("stream188service188", "c3RyZWFtMTg4c2VydmljZTE4OA"),
    ("stream188gateway188", "c3RyZWFtMTg4Z2F0ZXdheTE4OA"),
    ("stream188storage188", "c3RyZWFtMTg4c3RvcmFnZTE4OA"),
    ("context188storage188", "Y29udGV4dDE4OHN0b3JhZ2UxODg"),
    ("context188network188", "Y29udGV4dDE4OG5ldHdvcmsxODg"),
    ("context188latency188", "Y29udGV4dDE4OGxhdGVuY3kxODg"),
    ("context188buffer188", "Y29udGV4dDE4OGJ1ZmZlcjE4OA"),
    ("knowledge188buffer188", "a25vd2xlZGdlMTg4YnVmZmVyMTg4"),
    ("knowledge188queue188", "a25vd2xlZGdlMTg4cXVldWUxODg"),
    ("knowledge188worker188", "a25vd2xlZGdlMTg4d29ya2VyMTg4"),
    ("knowledge188kernel188", "a25vd2xlZGdlMTg4a2VybmVsMTg4"),
    ("vector188kernel188", "dmVjdG9yMTg4a2VybmVsMTg4"),
    ("vector188signal188", "dmVjdG9yMTg4c2lnbmFsMTg4"),
    ("vector188packet188", "dmVjdG9yMTg4cGFja2V0MTg4"),
    ("vector188router188", "dmVjdG9yMTg4cm91dGVyMTg4"),
    ("processor188router188", "cHJvY2Vzc29yMTg4cm91dGVyMTg4"),
    ("processor188cluster188", "cHJvY2Vzc29yMTg4Y2x1c3RlcjE4OA"),
    ("processor188mirror188", "cHJvY2Vzc29yMTg4bWlycm9yMTg4"),
    ("processor188filter188", "cHJvY2Vzc29yMTg4ZmlsdGVyMTg4"),
    ("reasoning188filter188", "cmVhc29uaW5nMTg4ZmlsdGVyMTg4"),
    ("reasoning188ranking188", "cmVhc29uaW5nMTg4cmFua2luZzE4OA"),
    ("reasoning188encoding188", "cmVhc29uaW5nMTg4ZW5jb2RpbmcxODg"),
    ("reasoning188mapping188", "cmVhc29uaW5nMTg4bWFwcGluZzE4OA"),
    ("machine188mapping188", "bWFjaGluZTE4OG1hcHBpbmcxODg"),
    ("machine188record188", "bWFjaGluZTE4OHJlY29yZDE4OA"),
    ("machine188candle188", "bWFjaGluZTE4OGNhbmRsZTE4OA"),
    ("machine188thread188", "bWFjaGluZTE4OHRocmVhZDE4OA"),
    ("learning188thread188", "bGVhcm5pbmcxODh0aHJlYWQxODg"),
    ("learning188kitten188", "bGVhcm5pbmcxODhraXR0ZW4xODg"),
    ("learning188sitting188", "bGVhcm5pbmcxODhzaXR0aW5nMTg4"),
    ("learning188agent188", "bGVhcm5pbmcxODhhZ2VudDE4OA"),
    ("model188agent188", "bW9kZWwxODhhZ2VudDE4OA"),
    ("model188angle188", "bW9kZWwxODhhbmdsZTE4OA"),
    ("model188universe188", "bW9kZWwxODh1bml2ZXJzZTE4OA"),
    ("model188memory188", "bW9kZWwxODhtZW1vcnkxODg"),
    ("token188memory188", "dG9rZW4xODhtZW1vcnkxODg"),
    ("token188stream188", "dG9rZW4xODhzdHJlYW0xODg"),
    ("token188context188", "dG9rZW4xODhjb250ZXh0MTg4"),
    ("token188knowledge188", "dG9rZW4xODhrbm93bGVkZ2UxODg"),
    ("prompt188knowledge188", "cHJvbXB0MTg4a25vd2xlZGdlMTg4"),
    ("prompt188vector188", "cHJvbXB0MTg4dmVjdG9yMTg4"),
    ("prompt188processor188", "cHJvbXB0MTg4cHJvY2Vzc29yMTg4"),
    ("prompt188reasoning188", "cHJvbXB0MTg4cmVhc29uaW5nMTg4"),
    ("session188reasoning188", "c2Vzc2lvbjE4OHJlYXNvbmluZzE4OA"),
    ("session188machine188", "c2Vzc2lvbjE4OG1hY2hpbmUxODg"),
    ("session188learning188", "c2Vzc2lvbjE4OGxlYXJuaW5nMTg4"),
    ("session188model188", "c2Vzc2lvbjE4OG1vZGVsMTg4"),
    ("library188model188", "bGlicmFyeTE4OG1vZGVsMTg4"),
    ("library188token188", "bGlicmFyeTE4OHRva2VuMTg4"),
    ("library188prompt188", "bGlicmFyeTE4OHByb21wdDE4OA"),
    ("library188session188", "bGlicmFyeTE4OHNlc3Npb24xODg"),
    ("service188session188", "c2VydmljZTE4OHNlc3Npb24xODg"),
    ("service188library188", "c2VydmljZTE4OGxpYnJhcnkxODg"),
    ("service188service188", "c2VydmljZTE4OHNlcnZpY2UxODg"),
    ("service188gateway188", "c2VydmljZTE4OGdhdGV3YXkxODg"),
    ("gateway188gateway188", "Z2F0ZXdheTE4OGdhdGV3YXkxODg"),
    ("gateway188storage188", "Z2F0ZXdheTE4OHN0b3JhZ2UxODg"),
    ("gateway188network188", "Z2F0ZXdheTE4OG5ldHdvcmsxODg"),
    ("gateway188latency188", "Z2F0ZXdheTE4OGxhdGVuY3kxODg"),
    ("storage188latency188", "c3RvcmFnZTE4OGxhdGVuY3kxODg"),
    ("storage188buffer188", "c3RvcmFnZTE4OGJ1ZmZlcjE4OA"),
    ("storage188queue188", "c3RvcmFnZTE4OHF1ZXVlMTg4"),
    ("storage188worker188", "c3RvcmFnZTE4OHdvcmtlcjE4OA"),
    ("network188worker188", "bmV0d29yazE4OHdvcmtlcjE4OA"),
    ("network188kernel188", "bmV0d29yazE4OGtlcm5lbDE4OA"),
    ("network188signal188", "bmV0d29yazE4OHNpZ25hbDE4OA"),
    ("network188packet188", "bmV0d29yazE4OHBhY2tldDE4OA"),
    ("latency188packet188", "bGF0ZW5jeTE4OHBhY2tldDE4OA"),
    ("latency188router188", "bGF0ZW5jeTE4OHJvdXRlcjE4OA"),
    ("latency188cluster188", "bGF0ZW5jeTE4OGNsdXN0ZXIxODg"),
    ("latency188mirror188", "bGF0ZW5jeTE4OG1pcnJvcjE4OA"),
    ("buffer188mirror188", "YnVmZmVyMTg4bWlycm9yMTg4"),
    ("buffer188filter188", "YnVmZmVyMTg4ZmlsdGVyMTg4"),
    ("buffer188ranking188", "YnVmZmVyMTg4cmFua2luZzE4OA"),
    ("buffer188encoding188", "YnVmZmVyMTg4ZW5jb2RpbmcxODg"),
    ("queue188encoding188", "cXVldWUxODhlbmNvZGluZzE4OA"),
    ("queue188mapping188", "cXVldWUxODhtYXBwaW5nMTg4"),
    ("queue188record188", "cXVldWUxODhyZWNvcmQxODg"),
    ("queue188candle188", "cXVldWUxODhjYW5kbGUxODg"),
    ("worker188candle188", "d29ya2VyMTg4Y2FuZGxlMTg4"),
    ("worker188thread188", "d29ya2VyMTg4dGhyZWFkMTg4"),
    ("worker188kitten188", "d29ya2VyMTg4a2l0dGVuMTg4"),
    ("worker188sitting188", "d29ya2VyMTg4c2l0dGluZzE4OA"),
    ("kernel188sitting188", "a2VybmVsMTg4c2l0dGluZzE4OA"),
    ("kernel188agent188", "a2VybmVsMTg4YWdlbnQxODg"),
    ("kernel188angle188", "a2VybmVsMTg4YW5nbGUxODg"),
    ("kernel188universe188", "a2VybmVsMTg4dW5pdmVyc2UxODg"),
    ("signal188universe188", "c2lnbmFsMTg4dW5pdmVyc2UxODg"),
    ("signal188memory188", "c2lnbmFsMTg4bWVtb3J5MTg4"),
    ("signal188stream188", "c2lnbmFsMTg4c3RyZWFtMTg4"),
    ("signal188context188", "c2lnbmFsMTg4Y29udGV4dDE4OA"),
    ("packet188context188", "cGFja2V0MTg4Y29udGV4dDE4OA"),
    ("packet188knowledge188", "cGFja2V0MTg4a25vd2xlZGdlMTg4"),
    ("packet188vector188", "cGFja2V0MTg4dmVjdG9yMTg4"),
    ("packet188processor188", "cGFja2V0MTg4cHJvY2Vzc29yMTg4"),
    ("router188processor188", "cm91dGVyMTg4cHJvY2Vzc29yMTg4"),
    ("router188reasoning188", "cm91dGVyMTg4cmVhc29uaW5nMTg4"),
    ("router188machine188", "cm91dGVyMTg4bWFjaGluZTE4OA"),
    ("router188learning188", "cm91dGVyMTg4bGVhcm5pbmcxODg"),
    ("cluster188learning188", "Y2x1c3RlcjE4OGxlYXJuaW5nMTg4"),
    ("cluster188model188", "Y2x1c3RlcjE4OG1vZGVsMTg4"),
    ("cluster188token188", "Y2x1c3RlcjE4OHRva2VuMTg4"),
    ("cluster188prompt188", "Y2x1c3RlcjE4OHByb21wdDE4OA"),
    ("mirror188prompt188", "bWlycm9yMTg4cHJvbXB0MTg4"),
    ("mirror188session188", "bWlycm9yMTg4c2Vzc2lvbjE4OA"),
    ("mirror188library188", "bWlycm9yMTg4bGlicmFyeTE4OA"),
    ("mirror188service188", "bWlycm9yMTg4c2VydmljZTE4OA"),
    ("filter188service188", "ZmlsdGVyMTg4c2VydmljZTE4OA"),
    ("filter188gateway188", "ZmlsdGVyMTg4Z2F0ZXdheTE4OA"),
    ("filter188storage188", "ZmlsdGVyMTg4c3RvcmFnZTE4OA"),
    ("filter188network188", "ZmlsdGVyMTg4bmV0d29yazE4OA"),
    ("ranking188network188", "cmFua2luZzE4OG5ldHdvcmsxODg"),
    ("ranking188latency188", "cmFua2luZzE4OGxhdGVuY3kxODg"),
    ("ranking188buffer188", "cmFua2luZzE4OGJ1ZmZlcjE4OA"),
    ("ranking188queue188", "cmFua2luZzE4OHF1ZXVlMTg4"),
    ("encoding188queue188", "ZW5jb2RpbmcxODhxdWV1ZTE4OA"),
    ("encoding188worker188", "ZW5jb2RpbmcxODh3b3JrZXIxODg"),
    ("encoding188kernel188", "ZW5jb2RpbmcxODhrZXJuZWwxODg"),
    ("encoding188signal188", "ZW5jb2RpbmcxODhzaWduYWwxODg"),
    ("mapping188signal188", "bWFwcGluZzE4OHNpZ25hbDE4OA"),
    ("mapping188packet188", "bWFwcGluZzE4OHBhY2tldDE4OA"),
    ("mapping188router188", "bWFwcGluZzE4OHJvdXRlcjE4OA"),
    ("mapping188cluster188", "bWFwcGluZzE4OGNsdXN0ZXIxODg"),
    ("record188cluster188", "cmVjb3JkMTg4Y2x1c3RlcjE4OA"),
    ("record188mirror188", "cmVjb3JkMTg4bWlycm9yMTg4"),
    ("record188filter188", "cmVjb3JkMTg4ZmlsdGVyMTg4"),
    ("record188ranking188", "cmVjb3JkMTg4cmFua2luZzE4OA"),
    ("candle188ranking188", "Y2FuZGxlMTg4cmFua2luZzE4OA"),
    ("candle188encoding188", "Y2FuZGxlMTg4ZW5jb2RpbmcxODg"),
    ("candle188mapping188", "Y2FuZGxlMTg4bWFwcGluZzE4OA"),
    ("candle188record188", "Y2FuZGxlMTg4cmVjb3JkMTg4"),
    ("thread188record188", "dGhyZWFkMTg4cmVjb3JkMTg4"),
    ("thread188candle188", "dGhyZWFkMTg4Y2FuZGxlMTg4"),
    ("thread188thread188", "dGhyZWFkMTg4dGhyZWFkMTg4"),
    ("thread188kitten188", "dGhyZWFkMTg4a2l0dGVuMTg4"),
    (
        "round 188: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTg4OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 188: agentuniverse is a framework for multi agents",
        "cm91bmQgMTg4OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 188: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTg4OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 188: the processor reads the record then stops",
        "cm91bmQgMTg4OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 188: a worker pulls the next task from the queue",
        "cm91bmQgMTg4OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 188: signals travel through the network layer",
        "cm91bmQgMTg4OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 188: the gateway routes each request by policy",
        "cm91bmQgMTg4OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 188: memory grows until the buffer is full",
        "cm91bmQgMTg4OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 188: the cluster mirrors every packet twice",
        "cm91bmQgMTg4OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 188: ranking uses tokens learned from the corpus",
        "cm91bmQgMTg4OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 188: a long session ends when the candle dies",
        "cm91bmQgMTg4OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 188: encode the prompt then map the result",
        "cm91bmQgMTg4OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 188: the kernel wakes the worker at dawn",
        "cm91bmQgMTg4OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 188: service latency drops after the patch",
        "cm91bmQgMTg4OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 188: the library caches every vector it sees",
        "cm91bmQgMTg4OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 188: agents argue then the debate resolves",
        "cm91bmQgMTg4OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 188: the filter keeps only strong matches",
        "cm91bmQgMTg4OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 188: the model answers with a short reply",
        "cm91bmQgMTg4OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 188: the recorder stores the reasoning trace",
        "cm91bmQgMTg4OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 188: the angel watches the processor run",
        "cm91bmQgMTg4OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 188: angle of the vector decides the match",
        "cm91bmQgMTg4OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 188: the candle burns twice as long at night",
        "cm91bmQgMTg4OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 188: a mirror of the universe in one line",
        "cm91bmQgMTg4OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 188: the queue drains before the storm", "cm91bmQgMTg4OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
