"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten194kitten194", "a2l0dGVuMTk0a2l0dGVuMTk0"),
    ("kitten194sitting194", "a2l0dGVuMTk0c2l0dGluZzE5NA"),
    ("kitten194agent194", "a2l0dGVuMTk0YWdlbnQxOTQ"),
    ("kitten194angle194", "a2l0dGVuMTk0YW5nbGUxOTQ"),
    ("sitting194angle194", "c2l0dGluZzE5NGFuZ2xlMTk0"),
    ("sitting194universe194", "c2l0dGluZzE5NHVuaXZlcnNlMTk0"),
    ("sitting194memory194", "c2l0dGluZzE5NG1lbW9yeTE5NA"),
    ("sitting194stream194", "c2l0dGluZzE5NHN0cmVhbTE5NA"),
    ("agent194stream194", "YWdlbnQxOTRzdHJlYW0xOTQ"),
    ("agent194context194", "YWdlbnQxOTRjb250ZXh0MTk0"),
    ("agent194knowledge194", "YWdlbnQxOTRrbm93bGVkZ2UxOTQ"),
    ("agent194vector194", "YWdlbnQxOTR2ZWN0b3IxOTQ"),
    ("angle194vector194", "YW5nbGUxOTR2ZWN0b3IxOTQ"),
    ("angle194processor194", "YW5nbGUxOTRwcm9jZXNzb3IxOTQ"),
    ("angle194reasoning194", "YW5nbGUxOTRyZWFzb25pbmcxOTQ"),
    ("angle194machine194", "YW5nbGUxOTRtYWNoaW5lMTk0"),
    ("universe194machine194", "dW5pdmVyc2UxOTRtYWNoaW5lMTk0"),
    ("universe194learning194", "dW5pdmVyc2UxOTRsZWFybmluZzE5NA"),
    ("universe194model194", "dW5pdmVyc2UxOTRtb2RlbDE5NA"),
    ("universe194token194", "dW5pdmVyc2UxOTR0b2tlbjE5NA"),
    ("memory194token194", "bWVtb3J5MTk0dG9rZW4xOTQ"),
    ("memory194prompt194", "bWVtb3J5MTk0cHJvbXB0MTk0"),
    ("memory194session194", "bWVtb3J5MTk0c2Vzc2lvbjE5NA"),
    ("memory194library194", "bWVtb3J5MTk0bGlicmFyeTE5NA"),
    ("stream194library194", "c3RyZWFtMTk0bGlicmFyeTE5NA"),
    ("stream194service194", "c3RyZWFtMTk0c2VydmljZTE5NA"),
    ("stream194gateway194", "c3RyZWFtMTk0Z2F0ZXdheTE5NA"),
    ("stream194storage194", "c3RyZWFtMTk0c3RvcmFnZTE5NA"),
    ("context194storage194", "Y29udGV4dDE5NHN0b3JhZ2UxOTQ"),
    ("context194network194", "Y29udGV4dDE5NG5ldHdvcmsxOTQ"),
    ("context194latency194", "Y29udGV4dDE5NGxhdGVuY3kxOTQ"),
    ("context194buffer194", "Y29udGV4dDE5NGJ1ZmZlcjE5NA"),
    ("knowledge194buffer194", "a25vd2xlZGdlMTk0YnVmZmVyMTk0"),
    ("knowledge194queue194", "a25vd2xlZGdlMTk0cXVldWUxOTQ"),
    ("knowledge194worker194", "a25vd2xlZGdlMTk0d29ya2VyMTk0"),
    ("knowledge194kernel194", "a25vd2xlZGdlMTk0a2VybmVsMTk0"),
    ("vector194kernel194", "dmVjdG9yMTk0a2VybmVsMTk0"),
    ("vector194signal194", "dmVjdG9yMTk0c2lnbmFsMTk0"),
    ("vector194packet194", "dmVjdG9yMTk0cGFja2V0MTk0"),
    ("vector194router194", "dmVjdG9yMTk0cm91dGVyMTk0"),
    ("processor194router194", "cHJvY2Vzc29yMTk0cm91dGVyMTk0"),
    ("processor194cluster194", "cHJvY2Vzc29yMTk0Y2x1c3RlcjE5NA"),
    ("processor194mirror194", "cHJvY2Vzc29yMTk0bWlycm9yMTk0"),
    ("processor194filter194", "cHJvY2Vzc29yMTk0ZmlsdGVyMTk0"),
    ("reasoning194filter194", "cmVhc29uaW5nMTk0ZmlsdGVyMTk0"),
    ("reasoning194ranking194", "cmVhc29uaW5nMTk0cmFua2luZzE5NA"),
    ("reasoning194encoding194", "cmVhc29uaW5nMTk0ZW5jb2RpbmcxOTQ"),
    ("reasoning194mapping194", "cmVhc29uaW5nMTk0bWFwcGluZzE5NA"),
    ("machine194mapping194", "bWFjaGluZTE5NG1hcHBpbmcxOTQ"),
    ("machine194record194", "bWFjaGluZTE5NHJlY29yZDE5NA"),
    ("machine194candle194", "bWFjaGluZTE5NGNhbmRsZTE5NA"),
    ("machine194thread194", "bWFjaGluZTE5NHRocmVhZDE5NA"),
    ("learning194thread194", "bGVhcm5pbmcxOTR0aHJlYWQxOTQ"),
    ("learning194kitten194", "bGVhcm5pbmcxOTRraXR0ZW4xOTQ"),
    ("learning194sitting194", "bGVhcm5pbmcxOTRzaXR0aW5nMTk0"),
    ("learning194agent194", "bGVhcm5pbmcxOTRhZ2VudDE5NA"),
    ("model194agent194", "bW9kZWwxOTRhZ2VudDE5NA"),
    ("model194angle194", "bW9kZWwxOTRhbmdsZTE5NA"),
    ("model194universe194", "bW9kZWwxOTR1bml2ZXJzZTE5NA"),
    ("model194memory194", "bW9kZWwxOTRtZW1vcnkxOTQ"),
    ("token194memory194", "dG9rZW4xOTRtZW1vcnkxOTQ"),
    ("token194stream194", "dG9rZW4xOTRzdHJlYW0xOTQ"),
    ("token194context194", "dG9rZW4xOTRjb250ZXh0MTk0"),
    ("token194knowledge194", "dG9rZW4xOTRrbm93bGVkZ2UxOTQ"),
    ("prompt194knowledge194", "cHJvbXB0MTk0a25vd2xlZGdlMTk0"),
    ("prompt194vector194", "cHJvbXB0MTk0dmVjdG9yMTk0"),
    ("prompt194processor194", "cHJvbXB0MTk0cHJvY2Vzc29yMTk0"),
    ("prompt194reasoning194", "cHJvbXB0MTk0cmVhc29uaW5nMTk0"),
    ("session194reasoning194", "c2Vzc2lvbjE5NHJlYXNvbmluZzE5NA"),
    ("session194machine194", "c2Vzc2lvbjE5NG1hY2hpbmUxOTQ"),
    ("session194learning194", "c2Vzc2lvbjE5NGxlYXJuaW5nMTk0"),
    ("session194model194", "c2Vzc2lvbjE5NG1vZGVsMTk0"),
    ("library194model194", "bGlicmFyeTE5NG1vZGVsMTk0"),
    ("library194token194", "bGlicmFyeTE5NHRva2VuMTk0"),
    ("library194prompt194", "bGlicmFyeTE5NHByb21wdDE5NA"),
    ("library194session194", "bGlicmFyeTE5NHNlc3Npb24xOTQ"),
    ("service194session194", "c2VydmljZTE5NHNlc3Npb24xOTQ"),
    ("service194library194", "c2VydmljZTE5NGxpYnJhcnkxOTQ"),
    ("service194service194", "c2VydmljZTE5NHNlcnZpY2UxOTQ"),
    ("service194gateway194", "c2VydmljZTE5NGdhdGV3YXkxOTQ"),
    ("gateway194gateway194", "Z2F0ZXdheTE5NGdhdGV3YXkxOTQ"),
    ("gateway194storage194", "Z2F0ZXdheTE5NHN0b3JhZ2UxOTQ"),
    ("gateway194network194", "Z2F0ZXdheTE5NG5ldHdvcmsxOTQ"),
    ("gateway194latency194", "Z2F0ZXdheTE5NGxhdGVuY3kxOTQ"),
    ("storage194latency194", "c3RvcmFnZTE5NGxhdGVuY3kxOTQ"),
    ("storage194buffer194", "c3RvcmFnZTE5NGJ1ZmZlcjE5NA"),
    ("storage194queue194", "c3RvcmFnZTE5NHF1ZXVlMTk0"),
    ("storage194worker194", "c3RvcmFnZTE5NHdvcmtlcjE5NA"),
    ("network194worker194", "bmV0d29yazE5NHdvcmtlcjE5NA"),
    ("network194kernel194", "bmV0d29yazE5NGtlcm5lbDE5NA"),
    ("network194signal194", "bmV0d29yazE5NHNpZ25hbDE5NA"),
    ("network194packet194", "bmV0d29yazE5NHBhY2tldDE5NA"),
    ("latency194packet194", "bGF0ZW5jeTE5NHBhY2tldDE5NA"),
    ("latency194router194", "bGF0ZW5jeTE5NHJvdXRlcjE5NA"),
    ("latency194cluster194", "bGF0ZW5jeTE5NGNsdXN0ZXIxOTQ"),
    ("latency194mirror194", "bGF0ZW5jeTE5NG1pcnJvcjE5NA"),
    ("buffer194mirror194", "YnVmZmVyMTk0bWlycm9yMTk0"),
    ("buffer194filter194", "YnVmZmVyMTk0ZmlsdGVyMTk0"),
    ("buffer194ranking194", "YnVmZmVyMTk0cmFua2luZzE5NA"),
    ("buffer194encoding194", "YnVmZmVyMTk0ZW5jb2RpbmcxOTQ"),
    ("queue194encoding194", "cXVldWUxOTRlbmNvZGluZzE5NA"),
    ("queue194mapping194", "cXVldWUxOTRtYXBwaW5nMTk0"),
    ("queue194record194", "cXVldWUxOTRyZWNvcmQxOTQ"),
    ("queue194candle194", "cXVldWUxOTRjYW5kbGUxOTQ"),
    ("worker194candle194", "d29ya2VyMTk0Y2FuZGxlMTk0"),
    ("worker194thread194", "d29ya2VyMTk0dGhyZWFkMTk0"),
    ("worker194kitten194", "d29ya2VyMTk0a2l0dGVuMTk0"),
    ("worker194sitting194", "d29ya2VyMTk0c2l0dGluZzE5NA"),
    ("kernel194sitting194", "a2VybmVsMTk0c2l0dGluZzE5NA"),
    ("kernel194agent194", "a2VybmVsMTk0YWdlbnQxOTQ"),
    ("kernel194angle194", "a2VybmVsMTk0YW5nbGUxOTQ"),
    ("kernel194universe194", "a2VybmVsMTk0dW5pdmVyc2UxOTQ"),
    ("signal194universe194", "c2lnbmFsMTk0dW5pdmVyc2UxOTQ"),
    ("signal194memory194", "c2lnbmFsMTk0bWVtb3J5MTk0"),
    ("signal194stream194", "c2lnbmFsMTk0c3RyZWFtMTk0"),
    ("signal194context194", "c2lnbmFsMTk0Y29udGV4dDE5NA"),
    ("packet194context194", "cGFja2V0MTk0Y29udGV4dDE5NA"),
    ("packet194knowledge194", "cGFja2V0MTk0a25vd2xlZGdlMTk0"),
    ("packet194vector194", "cGFja2V0MTk0dmVjdG9yMTk0"),
    ("packet194processor194", "cGFja2V0MTk0cHJvY2Vzc29yMTk0"),
    ("router194processor194", "cm91dGVyMTk0cHJvY2Vzc29yMTk0"),
    ("router194reasoning194", "cm91dGVyMTk0cmVhc29uaW5nMTk0"),
    ("router194machine194", "cm91dGVyMTk0bWFjaGluZTE5NA"),
    ("router194learning194", "cm91dGVyMTk0bGVhcm5pbmcxOTQ"),
    ("cluster194learning194", "Y2x1c3RlcjE5NGxlYXJuaW5nMTk0"),
    ("cluster194model194", "Y2x1c3RlcjE5NG1vZGVsMTk0"),
    ("cluster194token194", "Y2x1c3RlcjE5NHRva2VuMTk0"),
    ("cluster194prompt194", "Y2x1c3RlcjE5NHByb21wdDE5NA"),
    ("mirror194prompt194", "bWlycm9yMTk0cHJvbXB0MTk0"),
    ("mirror194session194", "bWlycm9yMTk0c2Vzc2lvbjE5NA"),
    ("mirror194library194", "bWlycm9yMTk0bGlicmFyeTE5NA"),
    ("mirror194service194", "bWlycm9yMTk0c2VydmljZTE5NA"),
    ("filter194service194", "ZmlsdGVyMTk0c2VydmljZTE5NA"),
    ("filter194gateway194", "ZmlsdGVyMTk0Z2F0ZXdheTE5NA"),
    ("filter194storage194", "ZmlsdGVyMTk0c3RvcmFnZTE5NA"),
    ("filter194network194", "ZmlsdGVyMTk0bmV0d29yazE5NA"),
    ("ranking194network194", "cmFua2luZzE5NG5ldHdvcmsxOTQ"),
    ("ranking194latency194", "cmFua2luZzE5NGxhdGVuY3kxOTQ"),
    ("ranking194buffer194", "cmFua2luZzE5NGJ1ZmZlcjE5NA"),
    ("ranking194queue194", "cmFua2luZzE5NHF1ZXVlMTk0"),
    ("encoding194queue194", "ZW5jb2RpbmcxOTRxdWV1ZTE5NA"),
    ("encoding194worker194", "ZW5jb2RpbmcxOTR3b3JrZXIxOTQ"),
    ("encoding194kernel194", "ZW5jb2RpbmcxOTRrZXJuZWwxOTQ"),
    ("encoding194signal194", "ZW5jb2RpbmcxOTRzaWduYWwxOTQ"),
    ("mapping194signal194", "bWFwcGluZzE5NHNpZ25hbDE5NA"),
    ("mapping194packet194", "bWFwcGluZzE5NHBhY2tldDE5NA"),
    ("mapping194router194", "bWFwcGluZzE5NHJvdXRlcjE5NA"),
    ("mapping194cluster194", "bWFwcGluZzE5NGNsdXN0ZXIxOTQ"),
    ("record194cluster194", "cmVjb3JkMTk0Y2x1c3RlcjE5NA"),
    ("record194mirror194", "cmVjb3JkMTk0bWlycm9yMTk0"),
    ("record194filter194", "cmVjb3JkMTk0ZmlsdGVyMTk0"),
    ("record194ranking194", "cmVjb3JkMTk0cmFua2luZzE5NA"),
    ("candle194ranking194", "Y2FuZGxlMTk0cmFua2luZzE5NA"),
    ("candle194encoding194", "Y2FuZGxlMTk0ZW5jb2RpbmcxOTQ"),
    ("candle194mapping194", "Y2FuZGxlMTk0bWFwcGluZzE5NA"),
    ("candle194record194", "Y2FuZGxlMTk0cmVjb3JkMTk0"),
    ("thread194record194", "dGhyZWFkMTk0cmVjb3JkMTk0"),
    ("thread194candle194", "dGhyZWFkMTk0Y2FuZGxlMTk0"),
    ("thread194thread194", "dGhyZWFkMTk0dGhyZWFkMTk0"),
    ("thread194kitten194", "dGhyZWFkMTk0a2l0dGVuMTk0"),
    (
        "round 194: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTk0OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 194: agentuniverse is a framework for multi agents",
        "cm91bmQgMTk0OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 194: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTk0OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 194: the processor reads the record then stops",
        "cm91bmQgMTk0OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 194: a worker pulls the next task from the queue",
        "cm91bmQgMTk0OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 194: signals travel through the network layer",
        "cm91bmQgMTk0OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 194: the gateway routes each request by policy",
        "cm91bmQgMTk0OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 194: memory grows until the buffer is full",
        "cm91bmQgMTk0OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 194: the cluster mirrors every packet twice",
        "cm91bmQgMTk0OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 194: ranking uses tokens learned from the corpus",
        "cm91bmQgMTk0OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 194: a long session ends when the candle dies",
        "cm91bmQgMTk0OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 194: encode the prompt then map the result",
        "cm91bmQgMTk0OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 194: the kernel wakes the worker at dawn",
        "cm91bmQgMTk0OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 194: service latency drops after the patch",
        "cm91bmQgMTk0OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 194: the library caches every vector it sees",
        "cm91bmQgMTk0OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 194: agents argue then the debate resolves",
        "cm91bmQgMTk0OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 194: the filter keeps only strong matches",
        "cm91bmQgMTk0OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 194: the model answers with a short reply",
        "cm91bmQgMTk0OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 194: the recorder stores the reasoning trace",
        "cm91bmQgMTk0OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 194: the angel watches the processor run",
        "cm91bmQgMTk0OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 194: angle of the vector decides the match",
        "cm91bmQgMTk0OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 194: the candle burns twice as long at night",
        "cm91bmQgMTk0OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 194: a mirror of the universe in one line",
        "cm91bmQgMTk0OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 194: the queue drains before the storm", "cm91bmQgMTk0OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
