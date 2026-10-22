"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten169kitten169", "a2l0dGVuMTY5a2l0dGVuMTY5"),
    ("kitten169sitting169", "a2l0dGVuMTY5c2l0dGluZzE2OQ"),
    ("kitten169agent169", "a2l0dGVuMTY5YWdlbnQxNjk"),
    ("kitten169angle169", "a2l0dGVuMTY5YW5nbGUxNjk"),
    ("sitting169angle169", "c2l0dGluZzE2OWFuZ2xlMTY5"),
    ("sitting169universe169", "c2l0dGluZzE2OXVuaXZlcnNlMTY5"),
    ("sitting169memory169", "c2l0dGluZzE2OW1lbW9yeTE2OQ"),
    ("sitting169stream169", "c2l0dGluZzE2OXN0cmVhbTE2OQ"),
    ("agent169stream169", "YWdlbnQxNjlzdHJlYW0xNjk"),
    ("agent169context169", "YWdlbnQxNjljb250ZXh0MTY5"),
    ("agent169knowledge169", "YWdlbnQxNjlrbm93bGVkZ2UxNjk"),
    ("agent169vector169", "YWdlbnQxNjl2ZWN0b3IxNjk"),
    ("angle169vector169", "YW5nbGUxNjl2ZWN0b3IxNjk"),
    ("angle169processor169", "YW5nbGUxNjlwcm9jZXNzb3IxNjk"),
    ("angle169reasoning169", "YW5nbGUxNjlyZWFzb25pbmcxNjk"),
    ("angle169machine169", "YW5nbGUxNjltYWNoaW5lMTY5"),
    ("universe169machine169", "dW5pdmVyc2UxNjltYWNoaW5lMTY5"),
    ("universe169learning169", "dW5pdmVyc2UxNjlsZWFybmluZzE2OQ"),
    ("universe169model169", "dW5pdmVyc2UxNjltb2RlbDE2OQ"),
    ("universe169token169", "dW5pdmVyc2UxNjl0b2tlbjE2OQ"),
    ("memory169token169", "bWVtb3J5MTY5dG9rZW4xNjk"),
    ("memory169prompt169", "bWVtb3J5MTY5cHJvbXB0MTY5"),
    ("memory169session169", "bWVtb3J5MTY5c2Vzc2lvbjE2OQ"),
    ("memory169library169", "bWVtb3J5MTY5bGlicmFyeTE2OQ"),
    ("stream169library169", "c3RyZWFtMTY5bGlicmFyeTE2OQ"),
    ("stream169service169", "c3RyZWFtMTY5c2VydmljZTE2OQ"),
    ("stream169gateway169", "c3RyZWFtMTY5Z2F0ZXdheTE2OQ"),
    ("stream169storage169", "c3RyZWFtMTY5c3RvcmFnZTE2OQ"),
    ("context169storage169", "Y29udGV4dDE2OXN0b3JhZ2UxNjk"),
    ("context169network169", "Y29udGV4dDE2OW5ldHdvcmsxNjk"),
    ("context169latency169", "Y29udGV4dDE2OWxhdGVuY3kxNjk"),
    ("context169buffer169", "Y29udGV4dDE2OWJ1ZmZlcjE2OQ"),
    ("knowledge169buffer169", "a25vd2xlZGdlMTY5YnVmZmVyMTY5"),
    ("knowledge169queue169", "a25vd2xlZGdlMTY5cXVldWUxNjk"),
    ("knowledge169worker169", "a25vd2xlZGdlMTY5d29ya2VyMTY5"),
    ("knowledge169kernel169", "a25vd2xlZGdlMTY5a2VybmVsMTY5"),
    ("vector169kernel169", "dmVjdG9yMTY5a2VybmVsMTY5"),
    ("vector169signal169", "dmVjdG9yMTY5c2lnbmFsMTY5"),
    ("vector169packet169", "dmVjdG9yMTY5cGFja2V0MTY5"),
    ("vector169router169", "dmVjdG9yMTY5cm91dGVyMTY5"),
    ("processor169router169", "cHJvY2Vzc29yMTY5cm91dGVyMTY5"),
    ("processor169cluster169", "cHJvY2Vzc29yMTY5Y2x1c3RlcjE2OQ"),
    ("processor169mirror169", "cHJvY2Vzc29yMTY5bWlycm9yMTY5"),
    ("processor169filter169", "cHJvY2Vzc29yMTY5ZmlsdGVyMTY5"),
    ("reasoning169filter169", "cmVhc29uaW5nMTY5ZmlsdGVyMTY5"),
    ("reasoning169ranking169", "cmVhc29uaW5nMTY5cmFua2luZzE2OQ"),
    ("reasoning169encoding169", "cmVhc29uaW5nMTY5ZW5jb2RpbmcxNjk"),
    ("reasoning169mapping169", "cmVhc29uaW5nMTY5bWFwcGluZzE2OQ"),
    ("machine169mapping169", "bWFjaGluZTE2OW1hcHBpbmcxNjk"),
    ("machine169record169", "bWFjaGluZTE2OXJlY29yZDE2OQ"),
    ("machine169candle169", "bWFjaGluZTE2OWNhbmRsZTE2OQ"),
    ("machine169thread169", "bWFjaGluZTE2OXRocmVhZDE2OQ"),
    ("learning169thread169", "bGVhcm5pbmcxNjl0aHJlYWQxNjk"),
    ("learning169kitten169", "bGVhcm5pbmcxNjlraXR0ZW4xNjk"),
    ("learning169sitting169", "bGVhcm5pbmcxNjlzaXR0aW5nMTY5"),
    ("learning169agent169", "bGVhcm5pbmcxNjlhZ2VudDE2OQ"),
    ("model169agent169", "bW9kZWwxNjlhZ2VudDE2OQ"),
    ("model169angle169", "bW9kZWwxNjlhbmdsZTE2OQ"),
    ("model169universe169", "bW9kZWwxNjl1bml2ZXJzZTE2OQ"),
    ("model169memory169", "bW9kZWwxNjltZW1vcnkxNjk"),
    ("token169memory169", "dG9rZW4xNjltZW1vcnkxNjk"),
    ("token169stream169", "dG9rZW4xNjlzdHJlYW0xNjk"),
    ("token169context169", "dG9rZW4xNjljb250ZXh0MTY5"),
    ("token169knowledge169", "dG9rZW4xNjlrbm93bGVkZ2UxNjk"),
    ("prompt169knowledge169", "cHJvbXB0MTY5a25vd2xlZGdlMTY5"),
    ("prompt169vector169", "cHJvbXB0MTY5dmVjdG9yMTY5"),
    ("prompt169processor169", "cHJvbXB0MTY5cHJvY2Vzc29yMTY5"),
    ("prompt169reasoning169", "cHJvbXB0MTY5cmVhc29uaW5nMTY5"),
    ("session169reasoning169", "c2Vzc2lvbjE2OXJlYXNvbmluZzE2OQ"),
    ("session169machine169", "c2Vzc2lvbjE2OW1hY2hpbmUxNjk"),
    ("session169learning169", "c2Vzc2lvbjE2OWxlYXJuaW5nMTY5"),
    ("session169model169", "c2Vzc2lvbjE2OW1vZGVsMTY5"),
    ("library169model169", "bGlicmFyeTE2OW1vZGVsMTY5"),
    ("library169token169", "bGlicmFyeTE2OXRva2VuMTY5"),
    ("library169prompt169", "bGlicmFyeTE2OXByb21wdDE2OQ"),
    ("library169session169", "bGlicmFyeTE2OXNlc3Npb24xNjk"),
    ("service169session169", "c2VydmljZTE2OXNlc3Npb24xNjk"),
    ("service169library169", "c2VydmljZTE2OWxpYnJhcnkxNjk"),
    ("service169service169", "c2VydmljZTE2OXNlcnZpY2UxNjk"),
    ("service169gateway169", "c2VydmljZTE2OWdhdGV3YXkxNjk"),
    ("gateway169gateway169", "Z2F0ZXdheTE2OWdhdGV3YXkxNjk"),
    ("gateway169storage169", "Z2F0ZXdheTE2OXN0b3JhZ2UxNjk"),
    ("gateway169network169", "Z2F0ZXdheTE2OW5ldHdvcmsxNjk"),
    ("gateway169latency169", "Z2F0ZXdheTE2OWxhdGVuY3kxNjk"),
    ("storage169latency169", "c3RvcmFnZTE2OWxhdGVuY3kxNjk"),
    ("storage169buffer169", "c3RvcmFnZTE2OWJ1ZmZlcjE2OQ"),
    ("storage169queue169", "c3RvcmFnZTE2OXF1ZXVlMTY5"),
    ("storage169worker169", "c3RvcmFnZTE2OXdvcmtlcjE2OQ"),
    ("network169worker169", "bmV0d29yazE2OXdvcmtlcjE2OQ"),
    ("network169kernel169", "bmV0d29yazE2OWtlcm5lbDE2OQ"),
    ("network169signal169", "bmV0d29yazE2OXNpZ25hbDE2OQ"),
    ("network169packet169", "bmV0d29yazE2OXBhY2tldDE2OQ"),
    ("latency169packet169", "bGF0ZW5jeTE2OXBhY2tldDE2OQ"),
    ("latency169router169", "bGF0ZW5jeTE2OXJvdXRlcjE2OQ"),
    ("latency169cluster169", "bGF0ZW5jeTE2OWNsdXN0ZXIxNjk"),
    ("latency169mirror169", "bGF0ZW5jeTE2OW1pcnJvcjE2OQ"),
    ("buffer169mirror169", "YnVmZmVyMTY5bWlycm9yMTY5"),
    ("buffer169filter169", "YnVmZmVyMTY5ZmlsdGVyMTY5"),
    ("buffer169ranking169", "YnVmZmVyMTY5cmFua2luZzE2OQ"),
    ("buffer169encoding169", "YnVmZmVyMTY5ZW5jb2RpbmcxNjk"),
    ("queue169encoding169", "cXVldWUxNjllbmNvZGluZzE2OQ"),
    ("queue169mapping169", "cXVldWUxNjltYXBwaW5nMTY5"),
    ("queue169record169", "cXVldWUxNjlyZWNvcmQxNjk"),
    ("queue169candle169", "cXVldWUxNjljYW5kbGUxNjk"),
    ("worker169candle169", "d29ya2VyMTY5Y2FuZGxlMTY5"),
    ("worker169thread169", "d29ya2VyMTY5dGhyZWFkMTY5"),
    ("worker169kitten169", "d29ya2VyMTY5a2l0dGVuMTY5"),
    ("worker169sitting169", "d29ya2VyMTY5c2l0dGluZzE2OQ"),
    ("kernel169sitting169", "a2VybmVsMTY5c2l0dGluZzE2OQ"),
    ("kernel169agent169", "a2VybmVsMTY5YWdlbnQxNjk"),
    ("kernel169angle169", "a2VybmVsMTY5YW5nbGUxNjk"),
    ("kernel169universe169", "a2VybmVsMTY5dW5pdmVyc2UxNjk"),
    ("signal169universe169", "c2lnbmFsMTY5dW5pdmVyc2UxNjk"),
    ("signal169memory169", "c2lnbmFsMTY5bWVtb3J5MTY5"),
    ("signal169stream169", "c2lnbmFsMTY5c3RyZWFtMTY5"),
    ("signal169context169", "c2lnbmFsMTY5Y29udGV4dDE2OQ"),
    ("packet169context169", "cGFja2V0MTY5Y29udGV4dDE2OQ"),
    ("packet169knowledge169", "cGFja2V0MTY5a25vd2xlZGdlMTY5"),
    ("packet169vector169", "cGFja2V0MTY5dmVjdG9yMTY5"),
    ("packet169processor169", "cGFja2V0MTY5cHJvY2Vzc29yMTY5"),
    ("router169processor169", "cm91dGVyMTY5cHJvY2Vzc29yMTY5"),
    ("router169reasoning169", "cm91dGVyMTY5cmVhc29uaW5nMTY5"),
    ("router169machine169", "cm91dGVyMTY5bWFjaGluZTE2OQ"),
    ("router169learning169", "cm91dGVyMTY5bGVhcm5pbmcxNjk"),
    ("cluster169learning169", "Y2x1c3RlcjE2OWxlYXJuaW5nMTY5"),
    ("cluster169model169", "Y2x1c3RlcjE2OW1vZGVsMTY5"),
    ("cluster169token169", "Y2x1c3RlcjE2OXRva2VuMTY5"),
    ("cluster169prompt169", "Y2x1c3RlcjE2OXByb21wdDE2OQ"),
    ("mirror169prompt169", "bWlycm9yMTY5cHJvbXB0MTY5"),
    ("mirror169session169", "bWlycm9yMTY5c2Vzc2lvbjE2OQ"),
    ("mirror169library169", "bWlycm9yMTY5bGlicmFyeTE2OQ"),
    ("mirror169service169", "bWlycm9yMTY5c2VydmljZTE2OQ"),
    ("filter169service169", "ZmlsdGVyMTY5c2VydmljZTE2OQ"),
    ("filter169gateway169", "ZmlsdGVyMTY5Z2F0ZXdheTE2OQ"),
    ("filter169storage169", "ZmlsdGVyMTY5c3RvcmFnZTE2OQ"),
    ("filter169network169", "ZmlsdGVyMTY5bmV0d29yazE2OQ"),
    ("ranking169network169", "cmFua2luZzE2OW5ldHdvcmsxNjk"),
    ("ranking169latency169", "cmFua2luZzE2OWxhdGVuY3kxNjk"),
    ("ranking169buffer169", "cmFua2luZzE2OWJ1ZmZlcjE2OQ"),
    ("ranking169queue169", "cmFua2luZzE2OXF1ZXVlMTY5"),
    ("encoding169queue169", "ZW5jb2RpbmcxNjlxdWV1ZTE2OQ"),
    ("encoding169worker169", "ZW5jb2RpbmcxNjl3b3JrZXIxNjk"),
    ("encoding169kernel169", "ZW5jb2RpbmcxNjlrZXJuZWwxNjk"),
    ("encoding169signal169", "ZW5jb2RpbmcxNjlzaWduYWwxNjk"),
    ("mapping169signal169", "bWFwcGluZzE2OXNpZ25hbDE2OQ"),
    ("mapping169packet169", "bWFwcGluZzE2OXBhY2tldDE2OQ"),
    ("mapping169router169", "bWFwcGluZzE2OXJvdXRlcjE2OQ"),
    ("mapping169cluster169", "bWFwcGluZzE2OWNsdXN0ZXIxNjk"),
    ("record169cluster169", "cmVjb3JkMTY5Y2x1c3RlcjE2OQ"),
    ("record169mirror169", "cmVjb3JkMTY5bWlycm9yMTY5"),
    ("record169filter169", "cmVjb3JkMTY5ZmlsdGVyMTY5"),
    ("record169ranking169", "cmVjb3JkMTY5cmFua2luZzE2OQ"),
    ("candle169ranking169", "Y2FuZGxlMTY5cmFua2luZzE2OQ"),
    ("candle169encoding169", "Y2FuZGxlMTY5ZW5jb2RpbmcxNjk"),
    ("candle169mapping169", "Y2FuZGxlMTY5bWFwcGluZzE2OQ"),
    ("candle169record169", "Y2FuZGxlMTY5cmVjb3JkMTY5"),
    ("thread169record169", "dGhyZWFkMTY5cmVjb3JkMTY5"),
    ("thread169candle169", "dGhyZWFkMTY5Y2FuZGxlMTY5"),
    ("thread169thread169", "dGhyZWFkMTY5dGhyZWFkMTY5"),
    ("thread169kitten169", "dGhyZWFkMTY5a2l0dGVuMTY5"),
    (
        "round 169: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTY5OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 169: agentuniverse is a framework for multi agents",
        "cm91bmQgMTY5OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 169: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTY5OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 169: the processor reads the record then stops",
        "cm91bmQgMTY5OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 169: a worker pulls the next task from the queue",
        "cm91bmQgMTY5OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 169: signals travel through the network layer",
        "cm91bmQgMTY5OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 169: the gateway routes each request by policy",
        "cm91bmQgMTY5OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 169: memory grows until the buffer is full",
        "cm91bmQgMTY5OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 169: the cluster mirrors every packet twice",
        "cm91bmQgMTY5OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 169: ranking uses tokens learned from the corpus",
        "cm91bmQgMTY5OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 169: a long session ends when the candle dies",
        "cm91bmQgMTY5OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 169: encode the prompt then map the result",
        "cm91bmQgMTY5OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 169: the kernel wakes the worker at dawn",
        "cm91bmQgMTY5OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 169: service latency drops after the patch",
        "cm91bmQgMTY5OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 169: the library caches every vector it sees",
        "cm91bmQgMTY5OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 169: agents argue then the debate resolves",
        "cm91bmQgMTY5OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 169: the filter keeps only strong matches",
        "cm91bmQgMTY5OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 169: the model answers with a short reply",
        "cm91bmQgMTY5OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 169: the recorder stores the reasoning trace",
        "cm91bmQgMTY5OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 169: the angel watches the processor run",
        "cm91bmQgMTY5OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 169: angle of the vector decides the match",
        "cm91bmQgMTY5OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 169: the candle burns twice as long at night",
        "cm91bmQgMTY5OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 169: a mirror of the universe in one line",
        "cm91bmQgMTY5OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 169: the queue drains before the storm", "cm91bmQgMTY5OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
