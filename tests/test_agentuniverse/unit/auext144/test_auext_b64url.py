"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten144kitten144", "a2l0dGVuMTQ0a2l0dGVuMTQ0"),
    ("kitten144sitting144", "a2l0dGVuMTQ0c2l0dGluZzE0NA"),
    ("kitten144agent144", "a2l0dGVuMTQ0YWdlbnQxNDQ"),
    ("kitten144angle144", "a2l0dGVuMTQ0YW5nbGUxNDQ"),
    ("sitting144angle144", "c2l0dGluZzE0NGFuZ2xlMTQ0"),
    ("sitting144universe144", "c2l0dGluZzE0NHVuaXZlcnNlMTQ0"),
    ("sitting144memory144", "c2l0dGluZzE0NG1lbW9yeTE0NA"),
    ("sitting144stream144", "c2l0dGluZzE0NHN0cmVhbTE0NA"),
    ("agent144stream144", "YWdlbnQxNDRzdHJlYW0xNDQ"),
    ("agent144context144", "YWdlbnQxNDRjb250ZXh0MTQ0"),
    ("agent144knowledge144", "YWdlbnQxNDRrbm93bGVkZ2UxNDQ"),
    ("agent144vector144", "YWdlbnQxNDR2ZWN0b3IxNDQ"),
    ("angle144vector144", "YW5nbGUxNDR2ZWN0b3IxNDQ"),
    ("angle144processor144", "YW5nbGUxNDRwcm9jZXNzb3IxNDQ"),
    ("angle144reasoning144", "YW5nbGUxNDRyZWFzb25pbmcxNDQ"),
    ("angle144machine144", "YW5nbGUxNDRtYWNoaW5lMTQ0"),
    ("universe144machine144", "dW5pdmVyc2UxNDRtYWNoaW5lMTQ0"),
    ("universe144learning144", "dW5pdmVyc2UxNDRsZWFybmluZzE0NA"),
    ("universe144model144", "dW5pdmVyc2UxNDRtb2RlbDE0NA"),
    ("universe144token144", "dW5pdmVyc2UxNDR0b2tlbjE0NA"),
    ("memory144token144", "bWVtb3J5MTQ0dG9rZW4xNDQ"),
    ("memory144prompt144", "bWVtb3J5MTQ0cHJvbXB0MTQ0"),
    ("memory144session144", "bWVtb3J5MTQ0c2Vzc2lvbjE0NA"),
    ("memory144library144", "bWVtb3J5MTQ0bGlicmFyeTE0NA"),
    ("stream144library144", "c3RyZWFtMTQ0bGlicmFyeTE0NA"),
    ("stream144service144", "c3RyZWFtMTQ0c2VydmljZTE0NA"),
    ("stream144gateway144", "c3RyZWFtMTQ0Z2F0ZXdheTE0NA"),
    ("stream144storage144", "c3RyZWFtMTQ0c3RvcmFnZTE0NA"),
    ("context144storage144", "Y29udGV4dDE0NHN0b3JhZ2UxNDQ"),
    ("context144network144", "Y29udGV4dDE0NG5ldHdvcmsxNDQ"),
    ("context144latency144", "Y29udGV4dDE0NGxhdGVuY3kxNDQ"),
    ("context144buffer144", "Y29udGV4dDE0NGJ1ZmZlcjE0NA"),
    ("knowledge144buffer144", "a25vd2xlZGdlMTQ0YnVmZmVyMTQ0"),
    ("knowledge144queue144", "a25vd2xlZGdlMTQ0cXVldWUxNDQ"),
    ("knowledge144worker144", "a25vd2xlZGdlMTQ0d29ya2VyMTQ0"),
    ("knowledge144kernel144", "a25vd2xlZGdlMTQ0a2VybmVsMTQ0"),
    ("vector144kernel144", "dmVjdG9yMTQ0a2VybmVsMTQ0"),
    ("vector144signal144", "dmVjdG9yMTQ0c2lnbmFsMTQ0"),
    ("vector144packet144", "dmVjdG9yMTQ0cGFja2V0MTQ0"),
    ("vector144router144", "dmVjdG9yMTQ0cm91dGVyMTQ0"),
    ("processor144router144", "cHJvY2Vzc29yMTQ0cm91dGVyMTQ0"),
    ("processor144cluster144", "cHJvY2Vzc29yMTQ0Y2x1c3RlcjE0NA"),
    ("processor144mirror144", "cHJvY2Vzc29yMTQ0bWlycm9yMTQ0"),
    ("processor144filter144", "cHJvY2Vzc29yMTQ0ZmlsdGVyMTQ0"),
    ("reasoning144filter144", "cmVhc29uaW5nMTQ0ZmlsdGVyMTQ0"),
    ("reasoning144ranking144", "cmVhc29uaW5nMTQ0cmFua2luZzE0NA"),
    ("reasoning144encoding144", "cmVhc29uaW5nMTQ0ZW5jb2RpbmcxNDQ"),
    ("reasoning144mapping144", "cmVhc29uaW5nMTQ0bWFwcGluZzE0NA"),
    ("machine144mapping144", "bWFjaGluZTE0NG1hcHBpbmcxNDQ"),
    ("machine144record144", "bWFjaGluZTE0NHJlY29yZDE0NA"),
    ("machine144candle144", "bWFjaGluZTE0NGNhbmRsZTE0NA"),
    ("machine144thread144", "bWFjaGluZTE0NHRocmVhZDE0NA"),
    ("learning144thread144", "bGVhcm5pbmcxNDR0aHJlYWQxNDQ"),
    ("learning144kitten144", "bGVhcm5pbmcxNDRraXR0ZW4xNDQ"),
    ("learning144sitting144", "bGVhcm5pbmcxNDRzaXR0aW5nMTQ0"),
    ("learning144agent144", "bGVhcm5pbmcxNDRhZ2VudDE0NA"),
    ("model144agent144", "bW9kZWwxNDRhZ2VudDE0NA"),
    ("model144angle144", "bW9kZWwxNDRhbmdsZTE0NA"),
    ("model144universe144", "bW9kZWwxNDR1bml2ZXJzZTE0NA"),
    ("model144memory144", "bW9kZWwxNDRtZW1vcnkxNDQ"),
    ("token144memory144", "dG9rZW4xNDRtZW1vcnkxNDQ"),
    ("token144stream144", "dG9rZW4xNDRzdHJlYW0xNDQ"),
    ("token144context144", "dG9rZW4xNDRjb250ZXh0MTQ0"),
    ("token144knowledge144", "dG9rZW4xNDRrbm93bGVkZ2UxNDQ"),
    ("prompt144knowledge144", "cHJvbXB0MTQ0a25vd2xlZGdlMTQ0"),
    ("prompt144vector144", "cHJvbXB0MTQ0dmVjdG9yMTQ0"),
    ("prompt144processor144", "cHJvbXB0MTQ0cHJvY2Vzc29yMTQ0"),
    ("prompt144reasoning144", "cHJvbXB0MTQ0cmVhc29uaW5nMTQ0"),
    ("session144reasoning144", "c2Vzc2lvbjE0NHJlYXNvbmluZzE0NA"),
    ("session144machine144", "c2Vzc2lvbjE0NG1hY2hpbmUxNDQ"),
    ("session144learning144", "c2Vzc2lvbjE0NGxlYXJuaW5nMTQ0"),
    ("session144model144", "c2Vzc2lvbjE0NG1vZGVsMTQ0"),
    ("library144model144", "bGlicmFyeTE0NG1vZGVsMTQ0"),
    ("library144token144", "bGlicmFyeTE0NHRva2VuMTQ0"),
    ("library144prompt144", "bGlicmFyeTE0NHByb21wdDE0NA"),
    ("library144session144", "bGlicmFyeTE0NHNlc3Npb24xNDQ"),
    ("service144session144", "c2VydmljZTE0NHNlc3Npb24xNDQ"),
    ("service144library144", "c2VydmljZTE0NGxpYnJhcnkxNDQ"),
    ("service144service144", "c2VydmljZTE0NHNlcnZpY2UxNDQ"),
    ("service144gateway144", "c2VydmljZTE0NGdhdGV3YXkxNDQ"),
    ("gateway144gateway144", "Z2F0ZXdheTE0NGdhdGV3YXkxNDQ"),
    ("gateway144storage144", "Z2F0ZXdheTE0NHN0b3JhZ2UxNDQ"),
    ("gateway144network144", "Z2F0ZXdheTE0NG5ldHdvcmsxNDQ"),
    ("gateway144latency144", "Z2F0ZXdheTE0NGxhdGVuY3kxNDQ"),
    ("storage144latency144", "c3RvcmFnZTE0NGxhdGVuY3kxNDQ"),
    ("storage144buffer144", "c3RvcmFnZTE0NGJ1ZmZlcjE0NA"),
    ("storage144queue144", "c3RvcmFnZTE0NHF1ZXVlMTQ0"),
    ("storage144worker144", "c3RvcmFnZTE0NHdvcmtlcjE0NA"),
    ("network144worker144", "bmV0d29yazE0NHdvcmtlcjE0NA"),
    ("network144kernel144", "bmV0d29yazE0NGtlcm5lbDE0NA"),
    ("network144signal144", "bmV0d29yazE0NHNpZ25hbDE0NA"),
    ("network144packet144", "bmV0d29yazE0NHBhY2tldDE0NA"),
    ("latency144packet144", "bGF0ZW5jeTE0NHBhY2tldDE0NA"),
    ("latency144router144", "bGF0ZW5jeTE0NHJvdXRlcjE0NA"),
    ("latency144cluster144", "bGF0ZW5jeTE0NGNsdXN0ZXIxNDQ"),
    ("latency144mirror144", "bGF0ZW5jeTE0NG1pcnJvcjE0NA"),
    ("buffer144mirror144", "YnVmZmVyMTQ0bWlycm9yMTQ0"),
    ("buffer144filter144", "YnVmZmVyMTQ0ZmlsdGVyMTQ0"),
    ("buffer144ranking144", "YnVmZmVyMTQ0cmFua2luZzE0NA"),
    ("buffer144encoding144", "YnVmZmVyMTQ0ZW5jb2RpbmcxNDQ"),
    ("queue144encoding144", "cXVldWUxNDRlbmNvZGluZzE0NA"),
    ("queue144mapping144", "cXVldWUxNDRtYXBwaW5nMTQ0"),
    ("queue144record144", "cXVldWUxNDRyZWNvcmQxNDQ"),
    ("queue144candle144", "cXVldWUxNDRjYW5kbGUxNDQ"),
    ("worker144candle144", "d29ya2VyMTQ0Y2FuZGxlMTQ0"),
    ("worker144thread144", "d29ya2VyMTQ0dGhyZWFkMTQ0"),
    ("worker144kitten144", "d29ya2VyMTQ0a2l0dGVuMTQ0"),
    ("worker144sitting144", "d29ya2VyMTQ0c2l0dGluZzE0NA"),
    ("kernel144sitting144", "a2VybmVsMTQ0c2l0dGluZzE0NA"),
    ("kernel144agent144", "a2VybmVsMTQ0YWdlbnQxNDQ"),
    ("kernel144angle144", "a2VybmVsMTQ0YW5nbGUxNDQ"),
    ("kernel144universe144", "a2VybmVsMTQ0dW5pdmVyc2UxNDQ"),
    ("signal144universe144", "c2lnbmFsMTQ0dW5pdmVyc2UxNDQ"),
    ("signal144memory144", "c2lnbmFsMTQ0bWVtb3J5MTQ0"),
    ("signal144stream144", "c2lnbmFsMTQ0c3RyZWFtMTQ0"),
    ("signal144context144", "c2lnbmFsMTQ0Y29udGV4dDE0NA"),
    ("packet144context144", "cGFja2V0MTQ0Y29udGV4dDE0NA"),
    ("packet144knowledge144", "cGFja2V0MTQ0a25vd2xlZGdlMTQ0"),
    ("packet144vector144", "cGFja2V0MTQ0dmVjdG9yMTQ0"),
    ("packet144processor144", "cGFja2V0MTQ0cHJvY2Vzc29yMTQ0"),
    ("router144processor144", "cm91dGVyMTQ0cHJvY2Vzc29yMTQ0"),
    ("router144reasoning144", "cm91dGVyMTQ0cmVhc29uaW5nMTQ0"),
    ("router144machine144", "cm91dGVyMTQ0bWFjaGluZTE0NA"),
    ("router144learning144", "cm91dGVyMTQ0bGVhcm5pbmcxNDQ"),
    ("cluster144learning144", "Y2x1c3RlcjE0NGxlYXJuaW5nMTQ0"),
    ("cluster144model144", "Y2x1c3RlcjE0NG1vZGVsMTQ0"),
    ("cluster144token144", "Y2x1c3RlcjE0NHRva2VuMTQ0"),
    ("cluster144prompt144", "Y2x1c3RlcjE0NHByb21wdDE0NA"),
    ("mirror144prompt144", "bWlycm9yMTQ0cHJvbXB0MTQ0"),
    ("mirror144session144", "bWlycm9yMTQ0c2Vzc2lvbjE0NA"),
    ("mirror144library144", "bWlycm9yMTQ0bGlicmFyeTE0NA"),
    ("mirror144service144", "bWlycm9yMTQ0c2VydmljZTE0NA"),
    ("filter144service144", "ZmlsdGVyMTQ0c2VydmljZTE0NA"),
    ("filter144gateway144", "ZmlsdGVyMTQ0Z2F0ZXdheTE0NA"),
    ("filter144storage144", "ZmlsdGVyMTQ0c3RvcmFnZTE0NA"),
    ("filter144network144", "ZmlsdGVyMTQ0bmV0d29yazE0NA"),
    ("ranking144network144", "cmFua2luZzE0NG5ldHdvcmsxNDQ"),
    ("ranking144latency144", "cmFua2luZzE0NGxhdGVuY3kxNDQ"),
    ("ranking144buffer144", "cmFua2luZzE0NGJ1ZmZlcjE0NA"),
    ("ranking144queue144", "cmFua2luZzE0NHF1ZXVlMTQ0"),
    ("encoding144queue144", "ZW5jb2RpbmcxNDRxdWV1ZTE0NA"),
    ("encoding144worker144", "ZW5jb2RpbmcxNDR3b3JrZXIxNDQ"),
    ("encoding144kernel144", "ZW5jb2RpbmcxNDRrZXJuZWwxNDQ"),
    ("encoding144signal144", "ZW5jb2RpbmcxNDRzaWduYWwxNDQ"),
    ("mapping144signal144", "bWFwcGluZzE0NHNpZ25hbDE0NA"),
    ("mapping144packet144", "bWFwcGluZzE0NHBhY2tldDE0NA"),
    ("mapping144router144", "bWFwcGluZzE0NHJvdXRlcjE0NA"),
    ("mapping144cluster144", "bWFwcGluZzE0NGNsdXN0ZXIxNDQ"),
    ("record144cluster144", "cmVjb3JkMTQ0Y2x1c3RlcjE0NA"),
    ("record144mirror144", "cmVjb3JkMTQ0bWlycm9yMTQ0"),
    ("record144filter144", "cmVjb3JkMTQ0ZmlsdGVyMTQ0"),
    ("record144ranking144", "cmVjb3JkMTQ0cmFua2luZzE0NA"),
    ("candle144ranking144", "Y2FuZGxlMTQ0cmFua2luZzE0NA"),
    ("candle144encoding144", "Y2FuZGxlMTQ0ZW5jb2RpbmcxNDQ"),
    ("candle144mapping144", "Y2FuZGxlMTQ0bWFwcGluZzE0NA"),
    ("candle144record144", "Y2FuZGxlMTQ0cmVjb3JkMTQ0"),
    ("thread144record144", "dGhyZWFkMTQ0cmVjb3JkMTQ0"),
    ("thread144candle144", "dGhyZWFkMTQ0Y2FuZGxlMTQ0"),
    ("thread144thread144", "dGhyZWFkMTQ0dGhyZWFkMTQ0"),
    ("thread144kitten144", "dGhyZWFkMTQ0a2l0dGVuMTQ0"),
    (
        "round 144: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTQ0OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 144: agentuniverse is a framework for multi agents",
        "cm91bmQgMTQ0OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 144: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTQ0OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 144: the processor reads the record then stops",
        "cm91bmQgMTQ0OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 144: a worker pulls the next task from the queue",
        "cm91bmQgMTQ0OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 144: signals travel through the network layer",
        "cm91bmQgMTQ0OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 144: the gateway routes each request by policy",
        "cm91bmQgMTQ0OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 144: memory grows until the buffer is full",
        "cm91bmQgMTQ0OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 144: the cluster mirrors every packet twice",
        "cm91bmQgMTQ0OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 144: ranking uses tokens learned from the corpus",
        "cm91bmQgMTQ0OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 144: a long session ends when the candle dies",
        "cm91bmQgMTQ0OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 144: encode the prompt then map the result",
        "cm91bmQgMTQ0OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 144: the kernel wakes the worker at dawn",
        "cm91bmQgMTQ0OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 144: service latency drops after the patch",
        "cm91bmQgMTQ0OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 144: the library caches every vector it sees",
        "cm91bmQgMTQ0OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 144: agents argue then the debate resolves",
        "cm91bmQgMTQ0OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 144: the filter keeps only strong matches",
        "cm91bmQgMTQ0OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 144: the model answers with a short reply",
        "cm91bmQgMTQ0OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 144: the recorder stores the reasoning trace",
        "cm91bmQgMTQ0OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 144: the angel watches the processor run",
        "cm91bmQgMTQ0OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 144: angle of the vector decides the match",
        "cm91bmQgMTQ0OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 144: the candle burns twice as long at night",
        "cm91bmQgMTQ0OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 144: a mirror of the universe in one line",
        "cm91bmQgMTQ0OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 144: the queue drains before the storm", "cm91bmQgMTQ0OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
