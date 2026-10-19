"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten190kitten190", "a2l0dGVuMTkwa2l0dGVuMTkw"),
    ("kitten190sitting190", "a2l0dGVuMTkwc2l0dGluZzE5MA"),
    ("kitten190agent190", "a2l0dGVuMTkwYWdlbnQxOTA"),
    ("kitten190angle190", "a2l0dGVuMTkwYW5nbGUxOTA"),
    ("sitting190angle190", "c2l0dGluZzE5MGFuZ2xlMTkw"),
    ("sitting190universe190", "c2l0dGluZzE5MHVuaXZlcnNlMTkw"),
    ("sitting190memory190", "c2l0dGluZzE5MG1lbW9yeTE5MA"),
    ("sitting190stream190", "c2l0dGluZzE5MHN0cmVhbTE5MA"),
    ("agent190stream190", "YWdlbnQxOTBzdHJlYW0xOTA"),
    ("agent190context190", "YWdlbnQxOTBjb250ZXh0MTkw"),
    ("agent190knowledge190", "YWdlbnQxOTBrbm93bGVkZ2UxOTA"),
    ("agent190vector190", "YWdlbnQxOTB2ZWN0b3IxOTA"),
    ("angle190vector190", "YW5nbGUxOTB2ZWN0b3IxOTA"),
    ("angle190processor190", "YW5nbGUxOTBwcm9jZXNzb3IxOTA"),
    ("angle190reasoning190", "YW5nbGUxOTByZWFzb25pbmcxOTA"),
    ("angle190machine190", "YW5nbGUxOTBtYWNoaW5lMTkw"),
    ("universe190machine190", "dW5pdmVyc2UxOTBtYWNoaW5lMTkw"),
    ("universe190learning190", "dW5pdmVyc2UxOTBsZWFybmluZzE5MA"),
    ("universe190model190", "dW5pdmVyc2UxOTBtb2RlbDE5MA"),
    ("universe190token190", "dW5pdmVyc2UxOTB0b2tlbjE5MA"),
    ("memory190token190", "bWVtb3J5MTkwdG9rZW4xOTA"),
    ("memory190prompt190", "bWVtb3J5MTkwcHJvbXB0MTkw"),
    ("memory190session190", "bWVtb3J5MTkwc2Vzc2lvbjE5MA"),
    ("memory190library190", "bWVtb3J5MTkwbGlicmFyeTE5MA"),
    ("stream190library190", "c3RyZWFtMTkwbGlicmFyeTE5MA"),
    ("stream190service190", "c3RyZWFtMTkwc2VydmljZTE5MA"),
    ("stream190gateway190", "c3RyZWFtMTkwZ2F0ZXdheTE5MA"),
    ("stream190storage190", "c3RyZWFtMTkwc3RvcmFnZTE5MA"),
    ("context190storage190", "Y29udGV4dDE5MHN0b3JhZ2UxOTA"),
    ("context190network190", "Y29udGV4dDE5MG5ldHdvcmsxOTA"),
    ("context190latency190", "Y29udGV4dDE5MGxhdGVuY3kxOTA"),
    ("context190buffer190", "Y29udGV4dDE5MGJ1ZmZlcjE5MA"),
    ("knowledge190buffer190", "a25vd2xlZGdlMTkwYnVmZmVyMTkw"),
    ("knowledge190queue190", "a25vd2xlZGdlMTkwcXVldWUxOTA"),
    ("knowledge190worker190", "a25vd2xlZGdlMTkwd29ya2VyMTkw"),
    ("knowledge190kernel190", "a25vd2xlZGdlMTkwa2VybmVsMTkw"),
    ("vector190kernel190", "dmVjdG9yMTkwa2VybmVsMTkw"),
    ("vector190signal190", "dmVjdG9yMTkwc2lnbmFsMTkw"),
    ("vector190packet190", "dmVjdG9yMTkwcGFja2V0MTkw"),
    ("vector190router190", "dmVjdG9yMTkwcm91dGVyMTkw"),
    ("processor190router190", "cHJvY2Vzc29yMTkwcm91dGVyMTkw"),
    ("processor190cluster190", "cHJvY2Vzc29yMTkwY2x1c3RlcjE5MA"),
    ("processor190mirror190", "cHJvY2Vzc29yMTkwbWlycm9yMTkw"),
    ("processor190filter190", "cHJvY2Vzc29yMTkwZmlsdGVyMTkw"),
    ("reasoning190filter190", "cmVhc29uaW5nMTkwZmlsdGVyMTkw"),
    ("reasoning190ranking190", "cmVhc29uaW5nMTkwcmFua2luZzE5MA"),
    ("reasoning190encoding190", "cmVhc29uaW5nMTkwZW5jb2RpbmcxOTA"),
    ("reasoning190mapping190", "cmVhc29uaW5nMTkwbWFwcGluZzE5MA"),
    ("machine190mapping190", "bWFjaGluZTE5MG1hcHBpbmcxOTA"),
    ("machine190record190", "bWFjaGluZTE5MHJlY29yZDE5MA"),
    ("machine190candle190", "bWFjaGluZTE5MGNhbmRsZTE5MA"),
    ("machine190thread190", "bWFjaGluZTE5MHRocmVhZDE5MA"),
    ("learning190thread190", "bGVhcm5pbmcxOTB0aHJlYWQxOTA"),
    ("learning190kitten190", "bGVhcm5pbmcxOTBraXR0ZW4xOTA"),
    ("learning190sitting190", "bGVhcm5pbmcxOTBzaXR0aW5nMTkw"),
    ("learning190agent190", "bGVhcm5pbmcxOTBhZ2VudDE5MA"),
    ("model190agent190", "bW9kZWwxOTBhZ2VudDE5MA"),
    ("model190angle190", "bW9kZWwxOTBhbmdsZTE5MA"),
    ("model190universe190", "bW9kZWwxOTB1bml2ZXJzZTE5MA"),
    ("model190memory190", "bW9kZWwxOTBtZW1vcnkxOTA"),
    ("token190memory190", "dG9rZW4xOTBtZW1vcnkxOTA"),
    ("token190stream190", "dG9rZW4xOTBzdHJlYW0xOTA"),
    ("token190context190", "dG9rZW4xOTBjb250ZXh0MTkw"),
    ("token190knowledge190", "dG9rZW4xOTBrbm93bGVkZ2UxOTA"),
    ("prompt190knowledge190", "cHJvbXB0MTkwa25vd2xlZGdlMTkw"),
    ("prompt190vector190", "cHJvbXB0MTkwdmVjdG9yMTkw"),
    ("prompt190processor190", "cHJvbXB0MTkwcHJvY2Vzc29yMTkw"),
    ("prompt190reasoning190", "cHJvbXB0MTkwcmVhc29uaW5nMTkw"),
    ("session190reasoning190", "c2Vzc2lvbjE5MHJlYXNvbmluZzE5MA"),
    ("session190machine190", "c2Vzc2lvbjE5MG1hY2hpbmUxOTA"),
    ("session190learning190", "c2Vzc2lvbjE5MGxlYXJuaW5nMTkw"),
    ("session190model190", "c2Vzc2lvbjE5MG1vZGVsMTkw"),
    ("library190model190", "bGlicmFyeTE5MG1vZGVsMTkw"),
    ("library190token190", "bGlicmFyeTE5MHRva2VuMTkw"),
    ("library190prompt190", "bGlicmFyeTE5MHByb21wdDE5MA"),
    ("library190session190", "bGlicmFyeTE5MHNlc3Npb24xOTA"),
    ("service190session190", "c2VydmljZTE5MHNlc3Npb24xOTA"),
    ("service190library190", "c2VydmljZTE5MGxpYnJhcnkxOTA"),
    ("service190service190", "c2VydmljZTE5MHNlcnZpY2UxOTA"),
    ("service190gateway190", "c2VydmljZTE5MGdhdGV3YXkxOTA"),
    ("gateway190gateway190", "Z2F0ZXdheTE5MGdhdGV3YXkxOTA"),
    ("gateway190storage190", "Z2F0ZXdheTE5MHN0b3JhZ2UxOTA"),
    ("gateway190network190", "Z2F0ZXdheTE5MG5ldHdvcmsxOTA"),
    ("gateway190latency190", "Z2F0ZXdheTE5MGxhdGVuY3kxOTA"),
    ("storage190latency190", "c3RvcmFnZTE5MGxhdGVuY3kxOTA"),
    ("storage190buffer190", "c3RvcmFnZTE5MGJ1ZmZlcjE5MA"),
    ("storage190queue190", "c3RvcmFnZTE5MHF1ZXVlMTkw"),
    ("storage190worker190", "c3RvcmFnZTE5MHdvcmtlcjE5MA"),
    ("network190worker190", "bmV0d29yazE5MHdvcmtlcjE5MA"),
    ("network190kernel190", "bmV0d29yazE5MGtlcm5lbDE5MA"),
    ("network190signal190", "bmV0d29yazE5MHNpZ25hbDE5MA"),
    ("network190packet190", "bmV0d29yazE5MHBhY2tldDE5MA"),
    ("latency190packet190", "bGF0ZW5jeTE5MHBhY2tldDE5MA"),
    ("latency190router190", "bGF0ZW5jeTE5MHJvdXRlcjE5MA"),
    ("latency190cluster190", "bGF0ZW5jeTE5MGNsdXN0ZXIxOTA"),
    ("latency190mirror190", "bGF0ZW5jeTE5MG1pcnJvcjE5MA"),
    ("buffer190mirror190", "YnVmZmVyMTkwbWlycm9yMTkw"),
    ("buffer190filter190", "YnVmZmVyMTkwZmlsdGVyMTkw"),
    ("buffer190ranking190", "YnVmZmVyMTkwcmFua2luZzE5MA"),
    ("buffer190encoding190", "YnVmZmVyMTkwZW5jb2RpbmcxOTA"),
    ("queue190encoding190", "cXVldWUxOTBlbmNvZGluZzE5MA"),
    ("queue190mapping190", "cXVldWUxOTBtYXBwaW5nMTkw"),
    ("queue190record190", "cXVldWUxOTByZWNvcmQxOTA"),
    ("queue190candle190", "cXVldWUxOTBjYW5kbGUxOTA"),
    ("worker190candle190", "d29ya2VyMTkwY2FuZGxlMTkw"),
    ("worker190thread190", "d29ya2VyMTkwdGhyZWFkMTkw"),
    ("worker190kitten190", "d29ya2VyMTkwa2l0dGVuMTkw"),
    ("worker190sitting190", "d29ya2VyMTkwc2l0dGluZzE5MA"),
    ("kernel190sitting190", "a2VybmVsMTkwc2l0dGluZzE5MA"),
    ("kernel190agent190", "a2VybmVsMTkwYWdlbnQxOTA"),
    ("kernel190angle190", "a2VybmVsMTkwYW5nbGUxOTA"),
    ("kernel190universe190", "a2VybmVsMTkwdW5pdmVyc2UxOTA"),
    ("signal190universe190", "c2lnbmFsMTkwdW5pdmVyc2UxOTA"),
    ("signal190memory190", "c2lnbmFsMTkwbWVtb3J5MTkw"),
    ("signal190stream190", "c2lnbmFsMTkwc3RyZWFtMTkw"),
    ("signal190context190", "c2lnbmFsMTkwY29udGV4dDE5MA"),
    ("packet190context190", "cGFja2V0MTkwY29udGV4dDE5MA"),
    ("packet190knowledge190", "cGFja2V0MTkwa25vd2xlZGdlMTkw"),
    ("packet190vector190", "cGFja2V0MTkwdmVjdG9yMTkw"),
    ("packet190processor190", "cGFja2V0MTkwcHJvY2Vzc29yMTkw"),
    ("router190processor190", "cm91dGVyMTkwcHJvY2Vzc29yMTkw"),
    ("router190reasoning190", "cm91dGVyMTkwcmVhc29uaW5nMTkw"),
    ("router190machine190", "cm91dGVyMTkwbWFjaGluZTE5MA"),
    ("router190learning190", "cm91dGVyMTkwbGVhcm5pbmcxOTA"),
    ("cluster190learning190", "Y2x1c3RlcjE5MGxlYXJuaW5nMTkw"),
    ("cluster190model190", "Y2x1c3RlcjE5MG1vZGVsMTkw"),
    ("cluster190token190", "Y2x1c3RlcjE5MHRva2VuMTkw"),
    ("cluster190prompt190", "Y2x1c3RlcjE5MHByb21wdDE5MA"),
    ("mirror190prompt190", "bWlycm9yMTkwcHJvbXB0MTkw"),
    ("mirror190session190", "bWlycm9yMTkwc2Vzc2lvbjE5MA"),
    ("mirror190library190", "bWlycm9yMTkwbGlicmFyeTE5MA"),
    ("mirror190service190", "bWlycm9yMTkwc2VydmljZTE5MA"),
    ("filter190service190", "ZmlsdGVyMTkwc2VydmljZTE5MA"),
    ("filter190gateway190", "ZmlsdGVyMTkwZ2F0ZXdheTE5MA"),
    ("filter190storage190", "ZmlsdGVyMTkwc3RvcmFnZTE5MA"),
    ("filter190network190", "ZmlsdGVyMTkwbmV0d29yazE5MA"),
    ("ranking190network190", "cmFua2luZzE5MG5ldHdvcmsxOTA"),
    ("ranking190latency190", "cmFua2luZzE5MGxhdGVuY3kxOTA"),
    ("ranking190buffer190", "cmFua2luZzE5MGJ1ZmZlcjE5MA"),
    ("ranking190queue190", "cmFua2luZzE5MHF1ZXVlMTkw"),
    ("encoding190queue190", "ZW5jb2RpbmcxOTBxdWV1ZTE5MA"),
    ("encoding190worker190", "ZW5jb2RpbmcxOTB3b3JrZXIxOTA"),
    ("encoding190kernel190", "ZW5jb2RpbmcxOTBrZXJuZWwxOTA"),
    ("encoding190signal190", "ZW5jb2RpbmcxOTBzaWduYWwxOTA"),
    ("mapping190signal190", "bWFwcGluZzE5MHNpZ25hbDE5MA"),
    ("mapping190packet190", "bWFwcGluZzE5MHBhY2tldDE5MA"),
    ("mapping190router190", "bWFwcGluZzE5MHJvdXRlcjE5MA"),
    ("mapping190cluster190", "bWFwcGluZzE5MGNsdXN0ZXIxOTA"),
    ("record190cluster190", "cmVjb3JkMTkwY2x1c3RlcjE5MA"),
    ("record190mirror190", "cmVjb3JkMTkwbWlycm9yMTkw"),
    ("record190filter190", "cmVjb3JkMTkwZmlsdGVyMTkw"),
    ("record190ranking190", "cmVjb3JkMTkwcmFua2luZzE5MA"),
    ("candle190ranking190", "Y2FuZGxlMTkwcmFua2luZzE5MA"),
    ("candle190encoding190", "Y2FuZGxlMTkwZW5jb2RpbmcxOTA"),
    ("candle190mapping190", "Y2FuZGxlMTkwbWFwcGluZzE5MA"),
    ("candle190record190", "Y2FuZGxlMTkwcmVjb3JkMTkw"),
    ("thread190record190", "dGhyZWFkMTkwcmVjb3JkMTkw"),
    ("thread190candle190", "dGhyZWFkMTkwY2FuZGxlMTkw"),
    ("thread190thread190", "dGhyZWFkMTkwdGhyZWFkMTkw"),
    ("thread190kitten190", "dGhyZWFkMTkwa2l0dGVuMTkw"),
    (
        "round 190: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTkwOiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 190: agentuniverse is a framework for multi agents",
        "cm91bmQgMTkwOiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 190: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTkwOiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 190: the processor reads the record then stops",
        "cm91bmQgMTkwOiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 190: a worker pulls the next task from the queue",
        "cm91bmQgMTkwOiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 190: signals travel through the network layer",
        "cm91bmQgMTkwOiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 190: the gateway routes each request by policy",
        "cm91bmQgMTkwOiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 190: memory grows until the buffer is full",
        "cm91bmQgMTkwOiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 190: the cluster mirrors every packet twice",
        "cm91bmQgMTkwOiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 190: ranking uses tokens learned from the corpus",
        "cm91bmQgMTkwOiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 190: a long session ends when the candle dies",
        "cm91bmQgMTkwOiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 190: encode the prompt then map the result",
        "cm91bmQgMTkwOiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 190: the kernel wakes the worker at dawn",
        "cm91bmQgMTkwOiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 190: service latency drops after the patch",
        "cm91bmQgMTkwOiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 190: the library caches every vector it sees",
        "cm91bmQgMTkwOiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 190: agents argue then the debate resolves",
        "cm91bmQgMTkwOiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 190: the filter keeps only strong matches",
        "cm91bmQgMTkwOiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 190: the model answers with a short reply",
        "cm91bmQgMTkwOiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 190: the recorder stores the reasoning trace",
        "cm91bmQgMTkwOiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 190: the angel watches the processor run",
        "cm91bmQgMTkwOiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 190: angle of the vector decides the match",
        "cm91bmQgMTkwOiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 190: the candle burns twice as long at night",
        "cm91bmQgMTkwOiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 190: a mirror of the universe in one line",
        "cm91bmQgMTkwOiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 190: the queue drains before the storm", "cm91bmQgMTkwOiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
