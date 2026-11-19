"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten148kitten148", "a2l0dGVuMTQ4a2l0dGVuMTQ4"),
    ("kitten148sitting148", "a2l0dGVuMTQ4c2l0dGluZzE0OA"),
    ("kitten148agent148", "a2l0dGVuMTQ4YWdlbnQxNDg"),
    ("kitten148angle148", "a2l0dGVuMTQ4YW5nbGUxNDg"),
    ("sitting148angle148", "c2l0dGluZzE0OGFuZ2xlMTQ4"),
    ("sitting148universe148", "c2l0dGluZzE0OHVuaXZlcnNlMTQ4"),
    ("sitting148memory148", "c2l0dGluZzE0OG1lbW9yeTE0OA"),
    ("sitting148stream148", "c2l0dGluZzE0OHN0cmVhbTE0OA"),
    ("agent148stream148", "YWdlbnQxNDhzdHJlYW0xNDg"),
    ("agent148context148", "YWdlbnQxNDhjb250ZXh0MTQ4"),
    ("agent148knowledge148", "YWdlbnQxNDhrbm93bGVkZ2UxNDg"),
    ("agent148vector148", "YWdlbnQxNDh2ZWN0b3IxNDg"),
    ("angle148vector148", "YW5nbGUxNDh2ZWN0b3IxNDg"),
    ("angle148processor148", "YW5nbGUxNDhwcm9jZXNzb3IxNDg"),
    ("angle148reasoning148", "YW5nbGUxNDhyZWFzb25pbmcxNDg"),
    ("angle148machine148", "YW5nbGUxNDhtYWNoaW5lMTQ4"),
    ("universe148machine148", "dW5pdmVyc2UxNDhtYWNoaW5lMTQ4"),
    ("universe148learning148", "dW5pdmVyc2UxNDhsZWFybmluZzE0OA"),
    ("universe148model148", "dW5pdmVyc2UxNDhtb2RlbDE0OA"),
    ("universe148token148", "dW5pdmVyc2UxNDh0b2tlbjE0OA"),
    ("memory148token148", "bWVtb3J5MTQ4dG9rZW4xNDg"),
    ("memory148prompt148", "bWVtb3J5MTQ4cHJvbXB0MTQ4"),
    ("memory148session148", "bWVtb3J5MTQ4c2Vzc2lvbjE0OA"),
    ("memory148library148", "bWVtb3J5MTQ4bGlicmFyeTE0OA"),
    ("stream148library148", "c3RyZWFtMTQ4bGlicmFyeTE0OA"),
    ("stream148service148", "c3RyZWFtMTQ4c2VydmljZTE0OA"),
    ("stream148gateway148", "c3RyZWFtMTQ4Z2F0ZXdheTE0OA"),
    ("stream148storage148", "c3RyZWFtMTQ4c3RvcmFnZTE0OA"),
    ("context148storage148", "Y29udGV4dDE0OHN0b3JhZ2UxNDg"),
    ("context148network148", "Y29udGV4dDE0OG5ldHdvcmsxNDg"),
    ("context148latency148", "Y29udGV4dDE0OGxhdGVuY3kxNDg"),
    ("context148buffer148", "Y29udGV4dDE0OGJ1ZmZlcjE0OA"),
    ("knowledge148buffer148", "a25vd2xlZGdlMTQ4YnVmZmVyMTQ4"),
    ("knowledge148queue148", "a25vd2xlZGdlMTQ4cXVldWUxNDg"),
    ("knowledge148worker148", "a25vd2xlZGdlMTQ4d29ya2VyMTQ4"),
    ("knowledge148kernel148", "a25vd2xlZGdlMTQ4a2VybmVsMTQ4"),
    ("vector148kernel148", "dmVjdG9yMTQ4a2VybmVsMTQ4"),
    ("vector148signal148", "dmVjdG9yMTQ4c2lnbmFsMTQ4"),
    ("vector148packet148", "dmVjdG9yMTQ4cGFja2V0MTQ4"),
    ("vector148router148", "dmVjdG9yMTQ4cm91dGVyMTQ4"),
    ("processor148router148", "cHJvY2Vzc29yMTQ4cm91dGVyMTQ4"),
    ("processor148cluster148", "cHJvY2Vzc29yMTQ4Y2x1c3RlcjE0OA"),
    ("processor148mirror148", "cHJvY2Vzc29yMTQ4bWlycm9yMTQ4"),
    ("processor148filter148", "cHJvY2Vzc29yMTQ4ZmlsdGVyMTQ4"),
    ("reasoning148filter148", "cmVhc29uaW5nMTQ4ZmlsdGVyMTQ4"),
    ("reasoning148ranking148", "cmVhc29uaW5nMTQ4cmFua2luZzE0OA"),
    ("reasoning148encoding148", "cmVhc29uaW5nMTQ4ZW5jb2RpbmcxNDg"),
    ("reasoning148mapping148", "cmVhc29uaW5nMTQ4bWFwcGluZzE0OA"),
    ("machine148mapping148", "bWFjaGluZTE0OG1hcHBpbmcxNDg"),
    ("machine148record148", "bWFjaGluZTE0OHJlY29yZDE0OA"),
    ("machine148candle148", "bWFjaGluZTE0OGNhbmRsZTE0OA"),
    ("machine148thread148", "bWFjaGluZTE0OHRocmVhZDE0OA"),
    ("learning148thread148", "bGVhcm5pbmcxNDh0aHJlYWQxNDg"),
    ("learning148kitten148", "bGVhcm5pbmcxNDhraXR0ZW4xNDg"),
    ("learning148sitting148", "bGVhcm5pbmcxNDhzaXR0aW5nMTQ4"),
    ("learning148agent148", "bGVhcm5pbmcxNDhhZ2VudDE0OA"),
    ("model148agent148", "bW9kZWwxNDhhZ2VudDE0OA"),
    ("model148angle148", "bW9kZWwxNDhhbmdsZTE0OA"),
    ("model148universe148", "bW9kZWwxNDh1bml2ZXJzZTE0OA"),
    ("model148memory148", "bW9kZWwxNDhtZW1vcnkxNDg"),
    ("token148memory148", "dG9rZW4xNDhtZW1vcnkxNDg"),
    ("token148stream148", "dG9rZW4xNDhzdHJlYW0xNDg"),
    ("token148context148", "dG9rZW4xNDhjb250ZXh0MTQ4"),
    ("token148knowledge148", "dG9rZW4xNDhrbm93bGVkZ2UxNDg"),
    ("prompt148knowledge148", "cHJvbXB0MTQ4a25vd2xlZGdlMTQ4"),
    ("prompt148vector148", "cHJvbXB0MTQ4dmVjdG9yMTQ4"),
    ("prompt148processor148", "cHJvbXB0MTQ4cHJvY2Vzc29yMTQ4"),
    ("prompt148reasoning148", "cHJvbXB0MTQ4cmVhc29uaW5nMTQ4"),
    ("session148reasoning148", "c2Vzc2lvbjE0OHJlYXNvbmluZzE0OA"),
    ("session148machine148", "c2Vzc2lvbjE0OG1hY2hpbmUxNDg"),
    ("session148learning148", "c2Vzc2lvbjE0OGxlYXJuaW5nMTQ4"),
    ("session148model148", "c2Vzc2lvbjE0OG1vZGVsMTQ4"),
    ("library148model148", "bGlicmFyeTE0OG1vZGVsMTQ4"),
    ("library148token148", "bGlicmFyeTE0OHRva2VuMTQ4"),
    ("library148prompt148", "bGlicmFyeTE0OHByb21wdDE0OA"),
    ("library148session148", "bGlicmFyeTE0OHNlc3Npb24xNDg"),
    ("service148session148", "c2VydmljZTE0OHNlc3Npb24xNDg"),
    ("service148library148", "c2VydmljZTE0OGxpYnJhcnkxNDg"),
    ("service148service148", "c2VydmljZTE0OHNlcnZpY2UxNDg"),
    ("service148gateway148", "c2VydmljZTE0OGdhdGV3YXkxNDg"),
    ("gateway148gateway148", "Z2F0ZXdheTE0OGdhdGV3YXkxNDg"),
    ("gateway148storage148", "Z2F0ZXdheTE0OHN0b3JhZ2UxNDg"),
    ("gateway148network148", "Z2F0ZXdheTE0OG5ldHdvcmsxNDg"),
    ("gateway148latency148", "Z2F0ZXdheTE0OGxhdGVuY3kxNDg"),
    ("storage148latency148", "c3RvcmFnZTE0OGxhdGVuY3kxNDg"),
    ("storage148buffer148", "c3RvcmFnZTE0OGJ1ZmZlcjE0OA"),
    ("storage148queue148", "c3RvcmFnZTE0OHF1ZXVlMTQ4"),
    ("storage148worker148", "c3RvcmFnZTE0OHdvcmtlcjE0OA"),
    ("network148worker148", "bmV0d29yazE0OHdvcmtlcjE0OA"),
    ("network148kernel148", "bmV0d29yazE0OGtlcm5lbDE0OA"),
    ("network148signal148", "bmV0d29yazE0OHNpZ25hbDE0OA"),
    ("network148packet148", "bmV0d29yazE0OHBhY2tldDE0OA"),
    ("latency148packet148", "bGF0ZW5jeTE0OHBhY2tldDE0OA"),
    ("latency148router148", "bGF0ZW5jeTE0OHJvdXRlcjE0OA"),
    ("latency148cluster148", "bGF0ZW5jeTE0OGNsdXN0ZXIxNDg"),
    ("latency148mirror148", "bGF0ZW5jeTE0OG1pcnJvcjE0OA"),
    ("buffer148mirror148", "YnVmZmVyMTQ4bWlycm9yMTQ4"),
    ("buffer148filter148", "YnVmZmVyMTQ4ZmlsdGVyMTQ4"),
    ("buffer148ranking148", "YnVmZmVyMTQ4cmFua2luZzE0OA"),
    ("buffer148encoding148", "YnVmZmVyMTQ4ZW5jb2RpbmcxNDg"),
    ("queue148encoding148", "cXVldWUxNDhlbmNvZGluZzE0OA"),
    ("queue148mapping148", "cXVldWUxNDhtYXBwaW5nMTQ4"),
    ("queue148record148", "cXVldWUxNDhyZWNvcmQxNDg"),
    ("queue148candle148", "cXVldWUxNDhjYW5kbGUxNDg"),
    ("worker148candle148", "d29ya2VyMTQ4Y2FuZGxlMTQ4"),
    ("worker148thread148", "d29ya2VyMTQ4dGhyZWFkMTQ4"),
    ("worker148kitten148", "d29ya2VyMTQ4a2l0dGVuMTQ4"),
    ("worker148sitting148", "d29ya2VyMTQ4c2l0dGluZzE0OA"),
    ("kernel148sitting148", "a2VybmVsMTQ4c2l0dGluZzE0OA"),
    ("kernel148agent148", "a2VybmVsMTQ4YWdlbnQxNDg"),
    ("kernel148angle148", "a2VybmVsMTQ4YW5nbGUxNDg"),
    ("kernel148universe148", "a2VybmVsMTQ4dW5pdmVyc2UxNDg"),
    ("signal148universe148", "c2lnbmFsMTQ4dW5pdmVyc2UxNDg"),
    ("signal148memory148", "c2lnbmFsMTQ4bWVtb3J5MTQ4"),
    ("signal148stream148", "c2lnbmFsMTQ4c3RyZWFtMTQ4"),
    ("signal148context148", "c2lnbmFsMTQ4Y29udGV4dDE0OA"),
    ("packet148context148", "cGFja2V0MTQ4Y29udGV4dDE0OA"),
    ("packet148knowledge148", "cGFja2V0MTQ4a25vd2xlZGdlMTQ4"),
    ("packet148vector148", "cGFja2V0MTQ4dmVjdG9yMTQ4"),
    ("packet148processor148", "cGFja2V0MTQ4cHJvY2Vzc29yMTQ4"),
    ("router148processor148", "cm91dGVyMTQ4cHJvY2Vzc29yMTQ4"),
    ("router148reasoning148", "cm91dGVyMTQ4cmVhc29uaW5nMTQ4"),
    ("router148machine148", "cm91dGVyMTQ4bWFjaGluZTE0OA"),
    ("router148learning148", "cm91dGVyMTQ4bGVhcm5pbmcxNDg"),
    ("cluster148learning148", "Y2x1c3RlcjE0OGxlYXJuaW5nMTQ4"),
    ("cluster148model148", "Y2x1c3RlcjE0OG1vZGVsMTQ4"),
    ("cluster148token148", "Y2x1c3RlcjE0OHRva2VuMTQ4"),
    ("cluster148prompt148", "Y2x1c3RlcjE0OHByb21wdDE0OA"),
    ("mirror148prompt148", "bWlycm9yMTQ4cHJvbXB0MTQ4"),
    ("mirror148session148", "bWlycm9yMTQ4c2Vzc2lvbjE0OA"),
    ("mirror148library148", "bWlycm9yMTQ4bGlicmFyeTE0OA"),
    ("mirror148service148", "bWlycm9yMTQ4c2VydmljZTE0OA"),
    ("filter148service148", "ZmlsdGVyMTQ4c2VydmljZTE0OA"),
    ("filter148gateway148", "ZmlsdGVyMTQ4Z2F0ZXdheTE0OA"),
    ("filter148storage148", "ZmlsdGVyMTQ4c3RvcmFnZTE0OA"),
    ("filter148network148", "ZmlsdGVyMTQ4bmV0d29yazE0OA"),
    ("ranking148network148", "cmFua2luZzE0OG5ldHdvcmsxNDg"),
    ("ranking148latency148", "cmFua2luZzE0OGxhdGVuY3kxNDg"),
    ("ranking148buffer148", "cmFua2luZzE0OGJ1ZmZlcjE0OA"),
    ("ranking148queue148", "cmFua2luZzE0OHF1ZXVlMTQ4"),
    ("encoding148queue148", "ZW5jb2RpbmcxNDhxdWV1ZTE0OA"),
    ("encoding148worker148", "ZW5jb2RpbmcxNDh3b3JrZXIxNDg"),
    ("encoding148kernel148", "ZW5jb2RpbmcxNDhrZXJuZWwxNDg"),
    ("encoding148signal148", "ZW5jb2RpbmcxNDhzaWduYWwxNDg"),
    ("mapping148signal148", "bWFwcGluZzE0OHNpZ25hbDE0OA"),
    ("mapping148packet148", "bWFwcGluZzE0OHBhY2tldDE0OA"),
    ("mapping148router148", "bWFwcGluZzE0OHJvdXRlcjE0OA"),
    ("mapping148cluster148", "bWFwcGluZzE0OGNsdXN0ZXIxNDg"),
    ("record148cluster148", "cmVjb3JkMTQ4Y2x1c3RlcjE0OA"),
    ("record148mirror148", "cmVjb3JkMTQ4bWlycm9yMTQ4"),
    ("record148filter148", "cmVjb3JkMTQ4ZmlsdGVyMTQ4"),
    ("record148ranking148", "cmVjb3JkMTQ4cmFua2luZzE0OA"),
    ("candle148ranking148", "Y2FuZGxlMTQ4cmFua2luZzE0OA"),
    ("candle148encoding148", "Y2FuZGxlMTQ4ZW5jb2RpbmcxNDg"),
    ("candle148mapping148", "Y2FuZGxlMTQ4bWFwcGluZzE0OA"),
    ("candle148record148", "Y2FuZGxlMTQ4cmVjb3JkMTQ4"),
    ("thread148record148", "dGhyZWFkMTQ4cmVjb3JkMTQ4"),
    ("thread148candle148", "dGhyZWFkMTQ4Y2FuZGxlMTQ4"),
    ("thread148thread148", "dGhyZWFkMTQ4dGhyZWFkMTQ4"),
    ("thread148kitten148", "dGhyZWFkMTQ4a2l0dGVuMTQ4"),
    (
        "round 148: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTQ4OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 148: agentuniverse is a framework for multi agents",
        "cm91bmQgMTQ4OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 148: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTQ4OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 148: the processor reads the record then stops",
        "cm91bmQgMTQ4OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 148: a worker pulls the next task from the queue",
        "cm91bmQgMTQ4OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 148: signals travel through the network layer",
        "cm91bmQgMTQ4OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 148: the gateway routes each request by policy",
        "cm91bmQgMTQ4OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 148: memory grows until the buffer is full",
        "cm91bmQgMTQ4OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 148: the cluster mirrors every packet twice",
        "cm91bmQgMTQ4OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 148: ranking uses tokens learned from the corpus",
        "cm91bmQgMTQ4OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 148: a long session ends when the candle dies",
        "cm91bmQgMTQ4OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 148: encode the prompt then map the result",
        "cm91bmQgMTQ4OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 148: the kernel wakes the worker at dawn",
        "cm91bmQgMTQ4OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 148: service latency drops after the patch",
        "cm91bmQgMTQ4OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 148: the library caches every vector it sees",
        "cm91bmQgMTQ4OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 148: agents argue then the debate resolves",
        "cm91bmQgMTQ4OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 148: the filter keeps only strong matches",
        "cm91bmQgMTQ4OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 148: the model answers with a short reply",
        "cm91bmQgMTQ4OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 148: the recorder stores the reasoning trace",
        "cm91bmQgMTQ4OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 148: the angel watches the processor run",
        "cm91bmQgMTQ4OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 148: angle of the vector decides the match",
        "cm91bmQgMTQ4OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 148: the candle burns twice as long at night",
        "cm91bmQgMTQ4OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 148: a mirror of the universe in one line",
        "cm91bmQgMTQ4OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 148: the queue drains before the storm", "cm91bmQgMTQ4OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
