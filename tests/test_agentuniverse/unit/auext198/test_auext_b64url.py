"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten198kitten198", "a2l0dGVuMTk4a2l0dGVuMTk4"),
    ("kitten198sitting198", "a2l0dGVuMTk4c2l0dGluZzE5OA"),
    ("kitten198agent198", "a2l0dGVuMTk4YWdlbnQxOTg"),
    ("kitten198angle198", "a2l0dGVuMTk4YW5nbGUxOTg"),
    ("sitting198angle198", "c2l0dGluZzE5OGFuZ2xlMTk4"),
    ("sitting198universe198", "c2l0dGluZzE5OHVuaXZlcnNlMTk4"),
    ("sitting198memory198", "c2l0dGluZzE5OG1lbW9yeTE5OA"),
    ("sitting198stream198", "c2l0dGluZzE5OHN0cmVhbTE5OA"),
    ("agent198stream198", "YWdlbnQxOThzdHJlYW0xOTg"),
    ("agent198context198", "YWdlbnQxOThjb250ZXh0MTk4"),
    ("agent198knowledge198", "YWdlbnQxOThrbm93bGVkZ2UxOTg"),
    ("agent198vector198", "YWdlbnQxOTh2ZWN0b3IxOTg"),
    ("angle198vector198", "YW5nbGUxOTh2ZWN0b3IxOTg"),
    ("angle198processor198", "YW5nbGUxOThwcm9jZXNzb3IxOTg"),
    ("angle198reasoning198", "YW5nbGUxOThyZWFzb25pbmcxOTg"),
    ("angle198machine198", "YW5nbGUxOThtYWNoaW5lMTk4"),
    ("universe198machine198", "dW5pdmVyc2UxOThtYWNoaW5lMTk4"),
    ("universe198learning198", "dW5pdmVyc2UxOThsZWFybmluZzE5OA"),
    ("universe198model198", "dW5pdmVyc2UxOThtb2RlbDE5OA"),
    ("universe198token198", "dW5pdmVyc2UxOTh0b2tlbjE5OA"),
    ("memory198token198", "bWVtb3J5MTk4dG9rZW4xOTg"),
    ("memory198prompt198", "bWVtb3J5MTk4cHJvbXB0MTk4"),
    ("memory198session198", "bWVtb3J5MTk4c2Vzc2lvbjE5OA"),
    ("memory198library198", "bWVtb3J5MTk4bGlicmFyeTE5OA"),
    ("stream198library198", "c3RyZWFtMTk4bGlicmFyeTE5OA"),
    ("stream198service198", "c3RyZWFtMTk4c2VydmljZTE5OA"),
    ("stream198gateway198", "c3RyZWFtMTk4Z2F0ZXdheTE5OA"),
    ("stream198storage198", "c3RyZWFtMTk4c3RvcmFnZTE5OA"),
    ("context198storage198", "Y29udGV4dDE5OHN0b3JhZ2UxOTg"),
    ("context198network198", "Y29udGV4dDE5OG5ldHdvcmsxOTg"),
    ("context198latency198", "Y29udGV4dDE5OGxhdGVuY3kxOTg"),
    ("context198buffer198", "Y29udGV4dDE5OGJ1ZmZlcjE5OA"),
    ("knowledge198buffer198", "a25vd2xlZGdlMTk4YnVmZmVyMTk4"),
    ("knowledge198queue198", "a25vd2xlZGdlMTk4cXVldWUxOTg"),
    ("knowledge198worker198", "a25vd2xlZGdlMTk4d29ya2VyMTk4"),
    ("knowledge198kernel198", "a25vd2xlZGdlMTk4a2VybmVsMTk4"),
    ("vector198kernel198", "dmVjdG9yMTk4a2VybmVsMTk4"),
    ("vector198signal198", "dmVjdG9yMTk4c2lnbmFsMTk4"),
    ("vector198packet198", "dmVjdG9yMTk4cGFja2V0MTk4"),
    ("vector198router198", "dmVjdG9yMTk4cm91dGVyMTk4"),
    ("processor198router198", "cHJvY2Vzc29yMTk4cm91dGVyMTk4"),
    ("processor198cluster198", "cHJvY2Vzc29yMTk4Y2x1c3RlcjE5OA"),
    ("processor198mirror198", "cHJvY2Vzc29yMTk4bWlycm9yMTk4"),
    ("processor198filter198", "cHJvY2Vzc29yMTk4ZmlsdGVyMTk4"),
    ("reasoning198filter198", "cmVhc29uaW5nMTk4ZmlsdGVyMTk4"),
    ("reasoning198ranking198", "cmVhc29uaW5nMTk4cmFua2luZzE5OA"),
    ("reasoning198encoding198", "cmVhc29uaW5nMTk4ZW5jb2RpbmcxOTg"),
    ("reasoning198mapping198", "cmVhc29uaW5nMTk4bWFwcGluZzE5OA"),
    ("machine198mapping198", "bWFjaGluZTE5OG1hcHBpbmcxOTg"),
    ("machine198record198", "bWFjaGluZTE5OHJlY29yZDE5OA"),
    ("machine198candle198", "bWFjaGluZTE5OGNhbmRsZTE5OA"),
    ("machine198thread198", "bWFjaGluZTE5OHRocmVhZDE5OA"),
    ("learning198thread198", "bGVhcm5pbmcxOTh0aHJlYWQxOTg"),
    ("learning198kitten198", "bGVhcm5pbmcxOThraXR0ZW4xOTg"),
    ("learning198sitting198", "bGVhcm5pbmcxOThzaXR0aW5nMTk4"),
    ("learning198agent198", "bGVhcm5pbmcxOThhZ2VudDE5OA"),
    ("model198agent198", "bW9kZWwxOThhZ2VudDE5OA"),
    ("model198angle198", "bW9kZWwxOThhbmdsZTE5OA"),
    ("model198universe198", "bW9kZWwxOTh1bml2ZXJzZTE5OA"),
    ("model198memory198", "bW9kZWwxOThtZW1vcnkxOTg"),
    ("token198memory198", "dG9rZW4xOThtZW1vcnkxOTg"),
    ("token198stream198", "dG9rZW4xOThzdHJlYW0xOTg"),
    ("token198context198", "dG9rZW4xOThjb250ZXh0MTk4"),
    ("token198knowledge198", "dG9rZW4xOThrbm93bGVkZ2UxOTg"),
    ("prompt198knowledge198", "cHJvbXB0MTk4a25vd2xlZGdlMTk4"),
    ("prompt198vector198", "cHJvbXB0MTk4dmVjdG9yMTk4"),
    ("prompt198processor198", "cHJvbXB0MTk4cHJvY2Vzc29yMTk4"),
    ("prompt198reasoning198", "cHJvbXB0MTk4cmVhc29uaW5nMTk4"),
    ("session198reasoning198", "c2Vzc2lvbjE5OHJlYXNvbmluZzE5OA"),
    ("session198machine198", "c2Vzc2lvbjE5OG1hY2hpbmUxOTg"),
    ("session198learning198", "c2Vzc2lvbjE5OGxlYXJuaW5nMTk4"),
    ("session198model198", "c2Vzc2lvbjE5OG1vZGVsMTk4"),
    ("library198model198", "bGlicmFyeTE5OG1vZGVsMTk4"),
    ("library198token198", "bGlicmFyeTE5OHRva2VuMTk4"),
    ("library198prompt198", "bGlicmFyeTE5OHByb21wdDE5OA"),
    ("library198session198", "bGlicmFyeTE5OHNlc3Npb24xOTg"),
    ("service198session198", "c2VydmljZTE5OHNlc3Npb24xOTg"),
    ("service198library198", "c2VydmljZTE5OGxpYnJhcnkxOTg"),
    ("service198service198", "c2VydmljZTE5OHNlcnZpY2UxOTg"),
    ("service198gateway198", "c2VydmljZTE5OGdhdGV3YXkxOTg"),
    ("gateway198gateway198", "Z2F0ZXdheTE5OGdhdGV3YXkxOTg"),
    ("gateway198storage198", "Z2F0ZXdheTE5OHN0b3JhZ2UxOTg"),
    ("gateway198network198", "Z2F0ZXdheTE5OG5ldHdvcmsxOTg"),
    ("gateway198latency198", "Z2F0ZXdheTE5OGxhdGVuY3kxOTg"),
    ("storage198latency198", "c3RvcmFnZTE5OGxhdGVuY3kxOTg"),
    ("storage198buffer198", "c3RvcmFnZTE5OGJ1ZmZlcjE5OA"),
    ("storage198queue198", "c3RvcmFnZTE5OHF1ZXVlMTk4"),
    ("storage198worker198", "c3RvcmFnZTE5OHdvcmtlcjE5OA"),
    ("network198worker198", "bmV0d29yazE5OHdvcmtlcjE5OA"),
    ("network198kernel198", "bmV0d29yazE5OGtlcm5lbDE5OA"),
    ("network198signal198", "bmV0d29yazE5OHNpZ25hbDE5OA"),
    ("network198packet198", "bmV0d29yazE5OHBhY2tldDE5OA"),
    ("latency198packet198", "bGF0ZW5jeTE5OHBhY2tldDE5OA"),
    ("latency198router198", "bGF0ZW5jeTE5OHJvdXRlcjE5OA"),
    ("latency198cluster198", "bGF0ZW5jeTE5OGNsdXN0ZXIxOTg"),
    ("latency198mirror198", "bGF0ZW5jeTE5OG1pcnJvcjE5OA"),
    ("buffer198mirror198", "YnVmZmVyMTk4bWlycm9yMTk4"),
    ("buffer198filter198", "YnVmZmVyMTk4ZmlsdGVyMTk4"),
    ("buffer198ranking198", "YnVmZmVyMTk4cmFua2luZzE5OA"),
    ("buffer198encoding198", "YnVmZmVyMTk4ZW5jb2RpbmcxOTg"),
    ("queue198encoding198", "cXVldWUxOThlbmNvZGluZzE5OA"),
    ("queue198mapping198", "cXVldWUxOThtYXBwaW5nMTk4"),
    ("queue198record198", "cXVldWUxOThyZWNvcmQxOTg"),
    ("queue198candle198", "cXVldWUxOThjYW5kbGUxOTg"),
    ("worker198candle198", "d29ya2VyMTk4Y2FuZGxlMTk4"),
    ("worker198thread198", "d29ya2VyMTk4dGhyZWFkMTk4"),
    ("worker198kitten198", "d29ya2VyMTk4a2l0dGVuMTk4"),
    ("worker198sitting198", "d29ya2VyMTk4c2l0dGluZzE5OA"),
    ("kernel198sitting198", "a2VybmVsMTk4c2l0dGluZzE5OA"),
    ("kernel198agent198", "a2VybmVsMTk4YWdlbnQxOTg"),
    ("kernel198angle198", "a2VybmVsMTk4YW5nbGUxOTg"),
    ("kernel198universe198", "a2VybmVsMTk4dW5pdmVyc2UxOTg"),
    ("signal198universe198", "c2lnbmFsMTk4dW5pdmVyc2UxOTg"),
    ("signal198memory198", "c2lnbmFsMTk4bWVtb3J5MTk4"),
    ("signal198stream198", "c2lnbmFsMTk4c3RyZWFtMTk4"),
    ("signal198context198", "c2lnbmFsMTk4Y29udGV4dDE5OA"),
    ("packet198context198", "cGFja2V0MTk4Y29udGV4dDE5OA"),
    ("packet198knowledge198", "cGFja2V0MTk4a25vd2xlZGdlMTk4"),
    ("packet198vector198", "cGFja2V0MTk4dmVjdG9yMTk4"),
    ("packet198processor198", "cGFja2V0MTk4cHJvY2Vzc29yMTk4"),
    ("router198processor198", "cm91dGVyMTk4cHJvY2Vzc29yMTk4"),
    ("router198reasoning198", "cm91dGVyMTk4cmVhc29uaW5nMTk4"),
    ("router198machine198", "cm91dGVyMTk4bWFjaGluZTE5OA"),
    ("router198learning198", "cm91dGVyMTk4bGVhcm5pbmcxOTg"),
    ("cluster198learning198", "Y2x1c3RlcjE5OGxlYXJuaW5nMTk4"),
    ("cluster198model198", "Y2x1c3RlcjE5OG1vZGVsMTk4"),
    ("cluster198token198", "Y2x1c3RlcjE5OHRva2VuMTk4"),
    ("cluster198prompt198", "Y2x1c3RlcjE5OHByb21wdDE5OA"),
    ("mirror198prompt198", "bWlycm9yMTk4cHJvbXB0MTk4"),
    ("mirror198session198", "bWlycm9yMTk4c2Vzc2lvbjE5OA"),
    ("mirror198library198", "bWlycm9yMTk4bGlicmFyeTE5OA"),
    ("mirror198service198", "bWlycm9yMTk4c2VydmljZTE5OA"),
    ("filter198service198", "ZmlsdGVyMTk4c2VydmljZTE5OA"),
    ("filter198gateway198", "ZmlsdGVyMTk4Z2F0ZXdheTE5OA"),
    ("filter198storage198", "ZmlsdGVyMTk4c3RvcmFnZTE5OA"),
    ("filter198network198", "ZmlsdGVyMTk4bmV0d29yazE5OA"),
    ("ranking198network198", "cmFua2luZzE5OG5ldHdvcmsxOTg"),
    ("ranking198latency198", "cmFua2luZzE5OGxhdGVuY3kxOTg"),
    ("ranking198buffer198", "cmFua2luZzE5OGJ1ZmZlcjE5OA"),
    ("ranking198queue198", "cmFua2luZzE5OHF1ZXVlMTk4"),
    ("encoding198queue198", "ZW5jb2RpbmcxOThxdWV1ZTE5OA"),
    ("encoding198worker198", "ZW5jb2RpbmcxOTh3b3JrZXIxOTg"),
    ("encoding198kernel198", "ZW5jb2RpbmcxOThrZXJuZWwxOTg"),
    ("encoding198signal198", "ZW5jb2RpbmcxOThzaWduYWwxOTg"),
    ("mapping198signal198", "bWFwcGluZzE5OHNpZ25hbDE5OA"),
    ("mapping198packet198", "bWFwcGluZzE5OHBhY2tldDE5OA"),
    ("mapping198router198", "bWFwcGluZzE5OHJvdXRlcjE5OA"),
    ("mapping198cluster198", "bWFwcGluZzE5OGNsdXN0ZXIxOTg"),
    ("record198cluster198", "cmVjb3JkMTk4Y2x1c3RlcjE5OA"),
    ("record198mirror198", "cmVjb3JkMTk4bWlycm9yMTk4"),
    ("record198filter198", "cmVjb3JkMTk4ZmlsdGVyMTk4"),
    ("record198ranking198", "cmVjb3JkMTk4cmFua2luZzE5OA"),
    ("candle198ranking198", "Y2FuZGxlMTk4cmFua2luZzE5OA"),
    ("candle198encoding198", "Y2FuZGxlMTk4ZW5jb2RpbmcxOTg"),
    ("candle198mapping198", "Y2FuZGxlMTk4bWFwcGluZzE5OA"),
    ("candle198record198", "Y2FuZGxlMTk4cmVjb3JkMTk4"),
    ("thread198record198", "dGhyZWFkMTk4cmVjb3JkMTk4"),
    ("thread198candle198", "dGhyZWFkMTk4Y2FuZGxlMTk4"),
    ("thread198thread198", "dGhyZWFkMTk4dGhyZWFkMTk4"),
    ("thread198kitten198", "dGhyZWFkMTk4a2l0dGVuMTk4"),
    (
        "round 198: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTk4OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 198: agentuniverse is a framework for multi agents",
        "cm91bmQgMTk4OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 198: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTk4OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 198: the processor reads the record then stops",
        "cm91bmQgMTk4OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 198: a worker pulls the next task from the queue",
        "cm91bmQgMTk4OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 198: signals travel through the network layer",
        "cm91bmQgMTk4OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 198: the gateway routes each request by policy",
        "cm91bmQgMTk4OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 198: memory grows until the buffer is full",
        "cm91bmQgMTk4OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 198: the cluster mirrors every packet twice",
        "cm91bmQgMTk4OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 198: ranking uses tokens learned from the corpus",
        "cm91bmQgMTk4OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 198: a long session ends when the candle dies",
        "cm91bmQgMTk4OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 198: encode the prompt then map the result",
        "cm91bmQgMTk4OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 198: the kernel wakes the worker at dawn",
        "cm91bmQgMTk4OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 198: service latency drops after the patch",
        "cm91bmQgMTk4OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 198: the library caches every vector it sees",
        "cm91bmQgMTk4OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 198: agents argue then the debate resolves",
        "cm91bmQgMTk4OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 198: the filter keeps only strong matches",
        "cm91bmQgMTk4OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 198: the model answers with a short reply",
        "cm91bmQgMTk4OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 198: the recorder stores the reasoning trace",
        "cm91bmQgMTk4OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 198: the angel watches the processor run",
        "cm91bmQgMTk4OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 198: angle of the vector decides the match",
        "cm91bmQgMTk4OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 198: the candle burns twice as long at night",
        "cm91bmQgMTk4OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 198: a mirror of the universe in one line",
        "cm91bmQgMTk4OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 198: the queue drains before the storm", "cm91bmQgMTk4OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
