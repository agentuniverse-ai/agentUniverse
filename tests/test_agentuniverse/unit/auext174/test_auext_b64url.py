"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten174kitten174", "a2l0dGVuMTc0a2l0dGVuMTc0"),
    ("kitten174sitting174", "a2l0dGVuMTc0c2l0dGluZzE3NA"),
    ("kitten174agent174", "a2l0dGVuMTc0YWdlbnQxNzQ"),
    ("kitten174angle174", "a2l0dGVuMTc0YW5nbGUxNzQ"),
    ("sitting174angle174", "c2l0dGluZzE3NGFuZ2xlMTc0"),
    ("sitting174universe174", "c2l0dGluZzE3NHVuaXZlcnNlMTc0"),
    ("sitting174memory174", "c2l0dGluZzE3NG1lbW9yeTE3NA"),
    ("sitting174stream174", "c2l0dGluZzE3NHN0cmVhbTE3NA"),
    ("agent174stream174", "YWdlbnQxNzRzdHJlYW0xNzQ"),
    ("agent174context174", "YWdlbnQxNzRjb250ZXh0MTc0"),
    ("agent174knowledge174", "YWdlbnQxNzRrbm93bGVkZ2UxNzQ"),
    ("agent174vector174", "YWdlbnQxNzR2ZWN0b3IxNzQ"),
    ("angle174vector174", "YW5nbGUxNzR2ZWN0b3IxNzQ"),
    ("angle174processor174", "YW5nbGUxNzRwcm9jZXNzb3IxNzQ"),
    ("angle174reasoning174", "YW5nbGUxNzRyZWFzb25pbmcxNzQ"),
    ("angle174machine174", "YW5nbGUxNzRtYWNoaW5lMTc0"),
    ("universe174machine174", "dW5pdmVyc2UxNzRtYWNoaW5lMTc0"),
    ("universe174learning174", "dW5pdmVyc2UxNzRsZWFybmluZzE3NA"),
    ("universe174model174", "dW5pdmVyc2UxNzRtb2RlbDE3NA"),
    ("universe174token174", "dW5pdmVyc2UxNzR0b2tlbjE3NA"),
    ("memory174token174", "bWVtb3J5MTc0dG9rZW4xNzQ"),
    ("memory174prompt174", "bWVtb3J5MTc0cHJvbXB0MTc0"),
    ("memory174session174", "bWVtb3J5MTc0c2Vzc2lvbjE3NA"),
    ("memory174library174", "bWVtb3J5MTc0bGlicmFyeTE3NA"),
    ("stream174library174", "c3RyZWFtMTc0bGlicmFyeTE3NA"),
    ("stream174service174", "c3RyZWFtMTc0c2VydmljZTE3NA"),
    ("stream174gateway174", "c3RyZWFtMTc0Z2F0ZXdheTE3NA"),
    ("stream174storage174", "c3RyZWFtMTc0c3RvcmFnZTE3NA"),
    ("context174storage174", "Y29udGV4dDE3NHN0b3JhZ2UxNzQ"),
    ("context174network174", "Y29udGV4dDE3NG5ldHdvcmsxNzQ"),
    ("context174latency174", "Y29udGV4dDE3NGxhdGVuY3kxNzQ"),
    ("context174buffer174", "Y29udGV4dDE3NGJ1ZmZlcjE3NA"),
    ("knowledge174buffer174", "a25vd2xlZGdlMTc0YnVmZmVyMTc0"),
    ("knowledge174queue174", "a25vd2xlZGdlMTc0cXVldWUxNzQ"),
    ("knowledge174worker174", "a25vd2xlZGdlMTc0d29ya2VyMTc0"),
    ("knowledge174kernel174", "a25vd2xlZGdlMTc0a2VybmVsMTc0"),
    ("vector174kernel174", "dmVjdG9yMTc0a2VybmVsMTc0"),
    ("vector174signal174", "dmVjdG9yMTc0c2lnbmFsMTc0"),
    ("vector174packet174", "dmVjdG9yMTc0cGFja2V0MTc0"),
    ("vector174router174", "dmVjdG9yMTc0cm91dGVyMTc0"),
    ("processor174router174", "cHJvY2Vzc29yMTc0cm91dGVyMTc0"),
    ("processor174cluster174", "cHJvY2Vzc29yMTc0Y2x1c3RlcjE3NA"),
    ("processor174mirror174", "cHJvY2Vzc29yMTc0bWlycm9yMTc0"),
    ("processor174filter174", "cHJvY2Vzc29yMTc0ZmlsdGVyMTc0"),
    ("reasoning174filter174", "cmVhc29uaW5nMTc0ZmlsdGVyMTc0"),
    ("reasoning174ranking174", "cmVhc29uaW5nMTc0cmFua2luZzE3NA"),
    ("reasoning174encoding174", "cmVhc29uaW5nMTc0ZW5jb2RpbmcxNzQ"),
    ("reasoning174mapping174", "cmVhc29uaW5nMTc0bWFwcGluZzE3NA"),
    ("machine174mapping174", "bWFjaGluZTE3NG1hcHBpbmcxNzQ"),
    ("machine174record174", "bWFjaGluZTE3NHJlY29yZDE3NA"),
    ("machine174candle174", "bWFjaGluZTE3NGNhbmRsZTE3NA"),
    ("machine174thread174", "bWFjaGluZTE3NHRocmVhZDE3NA"),
    ("learning174thread174", "bGVhcm5pbmcxNzR0aHJlYWQxNzQ"),
    ("learning174kitten174", "bGVhcm5pbmcxNzRraXR0ZW4xNzQ"),
    ("learning174sitting174", "bGVhcm5pbmcxNzRzaXR0aW5nMTc0"),
    ("learning174agent174", "bGVhcm5pbmcxNzRhZ2VudDE3NA"),
    ("model174agent174", "bW9kZWwxNzRhZ2VudDE3NA"),
    ("model174angle174", "bW9kZWwxNzRhbmdsZTE3NA"),
    ("model174universe174", "bW9kZWwxNzR1bml2ZXJzZTE3NA"),
    ("model174memory174", "bW9kZWwxNzRtZW1vcnkxNzQ"),
    ("token174memory174", "dG9rZW4xNzRtZW1vcnkxNzQ"),
    ("token174stream174", "dG9rZW4xNzRzdHJlYW0xNzQ"),
    ("token174context174", "dG9rZW4xNzRjb250ZXh0MTc0"),
    ("token174knowledge174", "dG9rZW4xNzRrbm93bGVkZ2UxNzQ"),
    ("prompt174knowledge174", "cHJvbXB0MTc0a25vd2xlZGdlMTc0"),
    ("prompt174vector174", "cHJvbXB0MTc0dmVjdG9yMTc0"),
    ("prompt174processor174", "cHJvbXB0MTc0cHJvY2Vzc29yMTc0"),
    ("prompt174reasoning174", "cHJvbXB0MTc0cmVhc29uaW5nMTc0"),
    ("session174reasoning174", "c2Vzc2lvbjE3NHJlYXNvbmluZzE3NA"),
    ("session174machine174", "c2Vzc2lvbjE3NG1hY2hpbmUxNzQ"),
    ("session174learning174", "c2Vzc2lvbjE3NGxlYXJuaW5nMTc0"),
    ("session174model174", "c2Vzc2lvbjE3NG1vZGVsMTc0"),
    ("library174model174", "bGlicmFyeTE3NG1vZGVsMTc0"),
    ("library174token174", "bGlicmFyeTE3NHRva2VuMTc0"),
    ("library174prompt174", "bGlicmFyeTE3NHByb21wdDE3NA"),
    ("library174session174", "bGlicmFyeTE3NHNlc3Npb24xNzQ"),
    ("service174session174", "c2VydmljZTE3NHNlc3Npb24xNzQ"),
    ("service174library174", "c2VydmljZTE3NGxpYnJhcnkxNzQ"),
    ("service174service174", "c2VydmljZTE3NHNlcnZpY2UxNzQ"),
    ("service174gateway174", "c2VydmljZTE3NGdhdGV3YXkxNzQ"),
    ("gateway174gateway174", "Z2F0ZXdheTE3NGdhdGV3YXkxNzQ"),
    ("gateway174storage174", "Z2F0ZXdheTE3NHN0b3JhZ2UxNzQ"),
    ("gateway174network174", "Z2F0ZXdheTE3NG5ldHdvcmsxNzQ"),
    ("gateway174latency174", "Z2F0ZXdheTE3NGxhdGVuY3kxNzQ"),
    ("storage174latency174", "c3RvcmFnZTE3NGxhdGVuY3kxNzQ"),
    ("storage174buffer174", "c3RvcmFnZTE3NGJ1ZmZlcjE3NA"),
    ("storage174queue174", "c3RvcmFnZTE3NHF1ZXVlMTc0"),
    ("storage174worker174", "c3RvcmFnZTE3NHdvcmtlcjE3NA"),
    ("network174worker174", "bmV0d29yazE3NHdvcmtlcjE3NA"),
    ("network174kernel174", "bmV0d29yazE3NGtlcm5lbDE3NA"),
    ("network174signal174", "bmV0d29yazE3NHNpZ25hbDE3NA"),
    ("network174packet174", "bmV0d29yazE3NHBhY2tldDE3NA"),
    ("latency174packet174", "bGF0ZW5jeTE3NHBhY2tldDE3NA"),
    ("latency174router174", "bGF0ZW5jeTE3NHJvdXRlcjE3NA"),
    ("latency174cluster174", "bGF0ZW5jeTE3NGNsdXN0ZXIxNzQ"),
    ("latency174mirror174", "bGF0ZW5jeTE3NG1pcnJvcjE3NA"),
    ("buffer174mirror174", "YnVmZmVyMTc0bWlycm9yMTc0"),
    ("buffer174filter174", "YnVmZmVyMTc0ZmlsdGVyMTc0"),
    ("buffer174ranking174", "YnVmZmVyMTc0cmFua2luZzE3NA"),
    ("buffer174encoding174", "YnVmZmVyMTc0ZW5jb2RpbmcxNzQ"),
    ("queue174encoding174", "cXVldWUxNzRlbmNvZGluZzE3NA"),
    ("queue174mapping174", "cXVldWUxNzRtYXBwaW5nMTc0"),
    ("queue174record174", "cXVldWUxNzRyZWNvcmQxNzQ"),
    ("queue174candle174", "cXVldWUxNzRjYW5kbGUxNzQ"),
    ("worker174candle174", "d29ya2VyMTc0Y2FuZGxlMTc0"),
    ("worker174thread174", "d29ya2VyMTc0dGhyZWFkMTc0"),
    ("worker174kitten174", "d29ya2VyMTc0a2l0dGVuMTc0"),
    ("worker174sitting174", "d29ya2VyMTc0c2l0dGluZzE3NA"),
    ("kernel174sitting174", "a2VybmVsMTc0c2l0dGluZzE3NA"),
    ("kernel174agent174", "a2VybmVsMTc0YWdlbnQxNzQ"),
    ("kernel174angle174", "a2VybmVsMTc0YW5nbGUxNzQ"),
    ("kernel174universe174", "a2VybmVsMTc0dW5pdmVyc2UxNzQ"),
    ("signal174universe174", "c2lnbmFsMTc0dW5pdmVyc2UxNzQ"),
    ("signal174memory174", "c2lnbmFsMTc0bWVtb3J5MTc0"),
    ("signal174stream174", "c2lnbmFsMTc0c3RyZWFtMTc0"),
    ("signal174context174", "c2lnbmFsMTc0Y29udGV4dDE3NA"),
    ("packet174context174", "cGFja2V0MTc0Y29udGV4dDE3NA"),
    ("packet174knowledge174", "cGFja2V0MTc0a25vd2xlZGdlMTc0"),
    ("packet174vector174", "cGFja2V0MTc0dmVjdG9yMTc0"),
    ("packet174processor174", "cGFja2V0MTc0cHJvY2Vzc29yMTc0"),
    ("router174processor174", "cm91dGVyMTc0cHJvY2Vzc29yMTc0"),
    ("router174reasoning174", "cm91dGVyMTc0cmVhc29uaW5nMTc0"),
    ("router174machine174", "cm91dGVyMTc0bWFjaGluZTE3NA"),
    ("router174learning174", "cm91dGVyMTc0bGVhcm5pbmcxNzQ"),
    ("cluster174learning174", "Y2x1c3RlcjE3NGxlYXJuaW5nMTc0"),
    ("cluster174model174", "Y2x1c3RlcjE3NG1vZGVsMTc0"),
    ("cluster174token174", "Y2x1c3RlcjE3NHRva2VuMTc0"),
    ("cluster174prompt174", "Y2x1c3RlcjE3NHByb21wdDE3NA"),
    ("mirror174prompt174", "bWlycm9yMTc0cHJvbXB0MTc0"),
    ("mirror174session174", "bWlycm9yMTc0c2Vzc2lvbjE3NA"),
    ("mirror174library174", "bWlycm9yMTc0bGlicmFyeTE3NA"),
    ("mirror174service174", "bWlycm9yMTc0c2VydmljZTE3NA"),
    ("filter174service174", "ZmlsdGVyMTc0c2VydmljZTE3NA"),
    ("filter174gateway174", "ZmlsdGVyMTc0Z2F0ZXdheTE3NA"),
    ("filter174storage174", "ZmlsdGVyMTc0c3RvcmFnZTE3NA"),
    ("filter174network174", "ZmlsdGVyMTc0bmV0d29yazE3NA"),
    ("ranking174network174", "cmFua2luZzE3NG5ldHdvcmsxNzQ"),
    ("ranking174latency174", "cmFua2luZzE3NGxhdGVuY3kxNzQ"),
    ("ranking174buffer174", "cmFua2luZzE3NGJ1ZmZlcjE3NA"),
    ("ranking174queue174", "cmFua2luZzE3NHF1ZXVlMTc0"),
    ("encoding174queue174", "ZW5jb2RpbmcxNzRxdWV1ZTE3NA"),
    ("encoding174worker174", "ZW5jb2RpbmcxNzR3b3JrZXIxNzQ"),
    ("encoding174kernel174", "ZW5jb2RpbmcxNzRrZXJuZWwxNzQ"),
    ("encoding174signal174", "ZW5jb2RpbmcxNzRzaWduYWwxNzQ"),
    ("mapping174signal174", "bWFwcGluZzE3NHNpZ25hbDE3NA"),
    ("mapping174packet174", "bWFwcGluZzE3NHBhY2tldDE3NA"),
    ("mapping174router174", "bWFwcGluZzE3NHJvdXRlcjE3NA"),
    ("mapping174cluster174", "bWFwcGluZzE3NGNsdXN0ZXIxNzQ"),
    ("record174cluster174", "cmVjb3JkMTc0Y2x1c3RlcjE3NA"),
    ("record174mirror174", "cmVjb3JkMTc0bWlycm9yMTc0"),
    ("record174filter174", "cmVjb3JkMTc0ZmlsdGVyMTc0"),
    ("record174ranking174", "cmVjb3JkMTc0cmFua2luZzE3NA"),
    ("candle174ranking174", "Y2FuZGxlMTc0cmFua2luZzE3NA"),
    ("candle174encoding174", "Y2FuZGxlMTc0ZW5jb2RpbmcxNzQ"),
    ("candle174mapping174", "Y2FuZGxlMTc0bWFwcGluZzE3NA"),
    ("candle174record174", "Y2FuZGxlMTc0cmVjb3JkMTc0"),
    ("thread174record174", "dGhyZWFkMTc0cmVjb3JkMTc0"),
    ("thread174candle174", "dGhyZWFkMTc0Y2FuZGxlMTc0"),
    ("thread174thread174", "dGhyZWFkMTc0dGhyZWFkMTc0"),
    ("thread174kitten174", "dGhyZWFkMTc0a2l0dGVuMTc0"),
    (
        "round 174: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTc0OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 174: agentuniverse is a framework for multi agents",
        "cm91bmQgMTc0OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 174: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTc0OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 174: the processor reads the record then stops",
        "cm91bmQgMTc0OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 174: a worker pulls the next task from the queue",
        "cm91bmQgMTc0OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 174: signals travel through the network layer",
        "cm91bmQgMTc0OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 174: the gateway routes each request by policy",
        "cm91bmQgMTc0OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 174: memory grows until the buffer is full",
        "cm91bmQgMTc0OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 174: the cluster mirrors every packet twice",
        "cm91bmQgMTc0OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 174: ranking uses tokens learned from the corpus",
        "cm91bmQgMTc0OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 174: a long session ends when the candle dies",
        "cm91bmQgMTc0OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 174: encode the prompt then map the result",
        "cm91bmQgMTc0OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 174: the kernel wakes the worker at dawn",
        "cm91bmQgMTc0OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 174: service latency drops after the patch",
        "cm91bmQgMTc0OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 174: the library caches every vector it sees",
        "cm91bmQgMTc0OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 174: agents argue then the debate resolves",
        "cm91bmQgMTc0OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 174: the filter keeps only strong matches",
        "cm91bmQgMTc0OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 174: the model answers with a short reply",
        "cm91bmQgMTc0OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 174: the recorder stores the reasoning trace",
        "cm91bmQgMTc0OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 174: the angel watches the processor run",
        "cm91bmQgMTc0OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 174: angle of the vector decides the match",
        "cm91bmQgMTc0OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 174: the candle burns twice as long at night",
        "cm91bmQgMTc0OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 174: a mirror of the universe in one line",
        "cm91bmQgMTc0OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 174: the queue drains before the storm", "cm91bmQgMTc0OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
