"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten175kitten175", "a2l0dGVuMTc1a2l0dGVuMTc1"),
    ("kitten175sitting175", "a2l0dGVuMTc1c2l0dGluZzE3NQ"),
    ("kitten175agent175", "a2l0dGVuMTc1YWdlbnQxNzU"),
    ("kitten175angle175", "a2l0dGVuMTc1YW5nbGUxNzU"),
    ("sitting175angle175", "c2l0dGluZzE3NWFuZ2xlMTc1"),
    ("sitting175universe175", "c2l0dGluZzE3NXVuaXZlcnNlMTc1"),
    ("sitting175memory175", "c2l0dGluZzE3NW1lbW9yeTE3NQ"),
    ("sitting175stream175", "c2l0dGluZzE3NXN0cmVhbTE3NQ"),
    ("agent175stream175", "YWdlbnQxNzVzdHJlYW0xNzU"),
    ("agent175context175", "YWdlbnQxNzVjb250ZXh0MTc1"),
    ("agent175knowledge175", "YWdlbnQxNzVrbm93bGVkZ2UxNzU"),
    ("agent175vector175", "YWdlbnQxNzV2ZWN0b3IxNzU"),
    ("angle175vector175", "YW5nbGUxNzV2ZWN0b3IxNzU"),
    ("angle175processor175", "YW5nbGUxNzVwcm9jZXNzb3IxNzU"),
    ("angle175reasoning175", "YW5nbGUxNzVyZWFzb25pbmcxNzU"),
    ("angle175machine175", "YW5nbGUxNzVtYWNoaW5lMTc1"),
    ("universe175machine175", "dW5pdmVyc2UxNzVtYWNoaW5lMTc1"),
    ("universe175learning175", "dW5pdmVyc2UxNzVsZWFybmluZzE3NQ"),
    ("universe175model175", "dW5pdmVyc2UxNzVtb2RlbDE3NQ"),
    ("universe175token175", "dW5pdmVyc2UxNzV0b2tlbjE3NQ"),
    ("memory175token175", "bWVtb3J5MTc1dG9rZW4xNzU"),
    ("memory175prompt175", "bWVtb3J5MTc1cHJvbXB0MTc1"),
    ("memory175session175", "bWVtb3J5MTc1c2Vzc2lvbjE3NQ"),
    ("memory175library175", "bWVtb3J5MTc1bGlicmFyeTE3NQ"),
    ("stream175library175", "c3RyZWFtMTc1bGlicmFyeTE3NQ"),
    ("stream175service175", "c3RyZWFtMTc1c2VydmljZTE3NQ"),
    ("stream175gateway175", "c3RyZWFtMTc1Z2F0ZXdheTE3NQ"),
    ("stream175storage175", "c3RyZWFtMTc1c3RvcmFnZTE3NQ"),
    ("context175storage175", "Y29udGV4dDE3NXN0b3JhZ2UxNzU"),
    ("context175network175", "Y29udGV4dDE3NW5ldHdvcmsxNzU"),
    ("context175latency175", "Y29udGV4dDE3NWxhdGVuY3kxNzU"),
    ("context175buffer175", "Y29udGV4dDE3NWJ1ZmZlcjE3NQ"),
    ("knowledge175buffer175", "a25vd2xlZGdlMTc1YnVmZmVyMTc1"),
    ("knowledge175queue175", "a25vd2xlZGdlMTc1cXVldWUxNzU"),
    ("knowledge175worker175", "a25vd2xlZGdlMTc1d29ya2VyMTc1"),
    ("knowledge175kernel175", "a25vd2xlZGdlMTc1a2VybmVsMTc1"),
    ("vector175kernel175", "dmVjdG9yMTc1a2VybmVsMTc1"),
    ("vector175signal175", "dmVjdG9yMTc1c2lnbmFsMTc1"),
    ("vector175packet175", "dmVjdG9yMTc1cGFja2V0MTc1"),
    ("vector175router175", "dmVjdG9yMTc1cm91dGVyMTc1"),
    ("processor175router175", "cHJvY2Vzc29yMTc1cm91dGVyMTc1"),
    ("processor175cluster175", "cHJvY2Vzc29yMTc1Y2x1c3RlcjE3NQ"),
    ("processor175mirror175", "cHJvY2Vzc29yMTc1bWlycm9yMTc1"),
    ("processor175filter175", "cHJvY2Vzc29yMTc1ZmlsdGVyMTc1"),
    ("reasoning175filter175", "cmVhc29uaW5nMTc1ZmlsdGVyMTc1"),
    ("reasoning175ranking175", "cmVhc29uaW5nMTc1cmFua2luZzE3NQ"),
    ("reasoning175encoding175", "cmVhc29uaW5nMTc1ZW5jb2RpbmcxNzU"),
    ("reasoning175mapping175", "cmVhc29uaW5nMTc1bWFwcGluZzE3NQ"),
    ("machine175mapping175", "bWFjaGluZTE3NW1hcHBpbmcxNzU"),
    ("machine175record175", "bWFjaGluZTE3NXJlY29yZDE3NQ"),
    ("machine175candle175", "bWFjaGluZTE3NWNhbmRsZTE3NQ"),
    ("machine175thread175", "bWFjaGluZTE3NXRocmVhZDE3NQ"),
    ("learning175thread175", "bGVhcm5pbmcxNzV0aHJlYWQxNzU"),
    ("learning175kitten175", "bGVhcm5pbmcxNzVraXR0ZW4xNzU"),
    ("learning175sitting175", "bGVhcm5pbmcxNzVzaXR0aW5nMTc1"),
    ("learning175agent175", "bGVhcm5pbmcxNzVhZ2VudDE3NQ"),
    ("model175agent175", "bW9kZWwxNzVhZ2VudDE3NQ"),
    ("model175angle175", "bW9kZWwxNzVhbmdsZTE3NQ"),
    ("model175universe175", "bW9kZWwxNzV1bml2ZXJzZTE3NQ"),
    ("model175memory175", "bW9kZWwxNzVtZW1vcnkxNzU"),
    ("token175memory175", "dG9rZW4xNzVtZW1vcnkxNzU"),
    ("token175stream175", "dG9rZW4xNzVzdHJlYW0xNzU"),
    ("token175context175", "dG9rZW4xNzVjb250ZXh0MTc1"),
    ("token175knowledge175", "dG9rZW4xNzVrbm93bGVkZ2UxNzU"),
    ("prompt175knowledge175", "cHJvbXB0MTc1a25vd2xlZGdlMTc1"),
    ("prompt175vector175", "cHJvbXB0MTc1dmVjdG9yMTc1"),
    ("prompt175processor175", "cHJvbXB0MTc1cHJvY2Vzc29yMTc1"),
    ("prompt175reasoning175", "cHJvbXB0MTc1cmVhc29uaW5nMTc1"),
    ("session175reasoning175", "c2Vzc2lvbjE3NXJlYXNvbmluZzE3NQ"),
    ("session175machine175", "c2Vzc2lvbjE3NW1hY2hpbmUxNzU"),
    ("session175learning175", "c2Vzc2lvbjE3NWxlYXJuaW5nMTc1"),
    ("session175model175", "c2Vzc2lvbjE3NW1vZGVsMTc1"),
    ("library175model175", "bGlicmFyeTE3NW1vZGVsMTc1"),
    ("library175token175", "bGlicmFyeTE3NXRva2VuMTc1"),
    ("library175prompt175", "bGlicmFyeTE3NXByb21wdDE3NQ"),
    ("library175session175", "bGlicmFyeTE3NXNlc3Npb24xNzU"),
    ("service175session175", "c2VydmljZTE3NXNlc3Npb24xNzU"),
    ("service175library175", "c2VydmljZTE3NWxpYnJhcnkxNzU"),
    ("service175service175", "c2VydmljZTE3NXNlcnZpY2UxNzU"),
    ("service175gateway175", "c2VydmljZTE3NWdhdGV3YXkxNzU"),
    ("gateway175gateway175", "Z2F0ZXdheTE3NWdhdGV3YXkxNzU"),
    ("gateway175storage175", "Z2F0ZXdheTE3NXN0b3JhZ2UxNzU"),
    ("gateway175network175", "Z2F0ZXdheTE3NW5ldHdvcmsxNzU"),
    ("gateway175latency175", "Z2F0ZXdheTE3NWxhdGVuY3kxNzU"),
    ("storage175latency175", "c3RvcmFnZTE3NWxhdGVuY3kxNzU"),
    ("storage175buffer175", "c3RvcmFnZTE3NWJ1ZmZlcjE3NQ"),
    ("storage175queue175", "c3RvcmFnZTE3NXF1ZXVlMTc1"),
    ("storage175worker175", "c3RvcmFnZTE3NXdvcmtlcjE3NQ"),
    ("network175worker175", "bmV0d29yazE3NXdvcmtlcjE3NQ"),
    ("network175kernel175", "bmV0d29yazE3NWtlcm5lbDE3NQ"),
    ("network175signal175", "bmV0d29yazE3NXNpZ25hbDE3NQ"),
    ("network175packet175", "bmV0d29yazE3NXBhY2tldDE3NQ"),
    ("latency175packet175", "bGF0ZW5jeTE3NXBhY2tldDE3NQ"),
    ("latency175router175", "bGF0ZW5jeTE3NXJvdXRlcjE3NQ"),
    ("latency175cluster175", "bGF0ZW5jeTE3NWNsdXN0ZXIxNzU"),
    ("latency175mirror175", "bGF0ZW5jeTE3NW1pcnJvcjE3NQ"),
    ("buffer175mirror175", "YnVmZmVyMTc1bWlycm9yMTc1"),
    ("buffer175filter175", "YnVmZmVyMTc1ZmlsdGVyMTc1"),
    ("buffer175ranking175", "YnVmZmVyMTc1cmFua2luZzE3NQ"),
    ("buffer175encoding175", "YnVmZmVyMTc1ZW5jb2RpbmcxNzU"),
    ("queue175encoding175", "cXVldWUxNzVlbmNvZGluZzE3NQ"),
    ("queue175mapping175", "cXVldWUxNzVtYXBwaW5nMTc1"),
    ("queue175record175", "cXVldWUxNzVyZWNvcmQxNzU"),
    ("queue175candle175", "cXVldWUxNzVjYW5kbGUxNzU"),
    ("worker175candle175", "d29ya2VyMTc1Y2FuZGxlMTc1"),
    ("worker175thread175", "d29ya2VyMTc1dGhyZWFkMTc1"),
    ("worker175kitten175", "d29ya2VyMTc1a2l0dGVuMTc1"),
    ("worker175sitting175", "d29ya2VyMTc1c2l0dGluZzE3NQ"),
    ("kernel175sitting175", "a2VybmVsMTc1c2l0dGluZzE3NQ"),
    ("kernel175agent175", "a2VybmVsMTc1YWdlbnQxNzU"),
    ("kernel175angle175", "a2VybmVsMTc1YW5nbGUxNzU"),
    ("kernel175universe175", "a2VybmVsMTc1dW5pdmVyc2UxNzU"),
    ("signal175universe175", "c2lnbmFsMTc1dW5pdmVyc2UxNzU"),
    ("signal175memory175", "c2lnbmFsMTc1bWVtb3J5MTc1"),
    ("signal175stream175", "c2lnbmFsMTc1c3RyZWFtMTc1"),
    ("signal175context175", "c2lnbmFsMTc1Y29udGV4dDE3NQ"),
    ("packet175context175", "cGFja2V0MTc1Y29udGV4dDE3NQ"),
    ("packet175knowledge175", "cGFja2V0MTc1a25vd2xlZGdlMTc1"),
    ("packet175vector175", "cGFja2V0MTc1dmVjdG9yMTc1"),
    ("packet175processor175", "cGFja2V0MTc1cHJvY2Vzc29yMTc1"),
    ("router175processor175", "cm91dGVyMTc1cHJvY2Vzc29yMTc1"),
    ("router175reasoning175", "cm91dGVyMTc1cmVhc29uaW5nMTc1"),
    ("router175machine175", "cm91dGVyMTc1bWFjaGluZTE3NQ"),
    ("router175learning175", "cm91dGVyMTc1bGVhcm5pbmcxNzU"),
    ("cluster175learning175", "Y2x1c3RlcjE3NWxlYXJuaW5nMTc1"),
    ("cluster175model175", "Y2x1c3RlcjE3NW1vZGVsMTc1"),
    ("cluster175token175", "Y2x1c3RlcjE3NXRva2VuMTc1"),
    ("cluster175prompt175", "Y2x1c3RlcjE3NXByb21wdDE3NQ"),
    ("mirror175prompt175", "bWlycm9yMTc1cHJvbXB0MTc1"),
    ("mirror175session175", "bWlycm9yMTc1c2Vzc2lvbjE3NQ"),
    ("mirror175library175", "bWlycm9yMTc1bGlicmFyeTE3NQ"),
    ("mirror175service175", "bWlycm9yMTc1c2VydmljZTE3NQ"),
    ("filter175service175", "ZmlsdGVyMTc1c2VydmljZTE3NQ"),
    ("filter175gateway175", "ZmlsdGVyMTc1Z2F0ZXdheTE3NQ"),
    ("filter175storage175", "ZmlsdGVyMTc1c3RvcmFnZTE3NQ"),
    ("filter175network175", "ZmlsdGVyMTc1bmV0d29yazE3NQ"),
    ("ranking175network175", "cmFua2luZzE3NW5ldHdvcmsxNzU"),
    ("ranking175latency175", "cmFua2luZzE3NWxhdGVuY3kxNzU"),
    ("ranking175buffer175", "cmFua2luZzE3NWJ1ZmZlcjE3NQ"),
    ("ranking175queue175", "cmFua2luZzE3NXF1ZXVlMTc1"),
    ("encoding175queue175", "ZW5jb2RpbmcxNzVxdWV1ZTE3NQ"),
    ("encoding175worker175", "ZW5jb2RpbmcxNzV3b3JrZXIxNzU"),
    ("encoding175kernel175", "ZW5jb2RpbmcxNzVrZXJuZWwxNzU"),
    ("encoding175signal175", "ZW5jb2RpbmcxNzVzaWduYWwxNzU"),
    ("mapping175signal175", "bWFwcGluZzE3NXNpZ25hbDE3NQ"),
    ("mapping175packet175", "bWFwcGluZzE3NXBhY2tldDE3NQ"),
    ("mapping175router175", "bWFwcGluZzE3NXJvdXRlcjE3NQ"),
    ("mapping175cluster175", "bWFwcGluZzE3NWNsdXN0ZXIxNzU"),
    ("record175cluster175", "cmVjb3JkMTc1Y2x1c3RlcjE3NQ"),
    ("record175mirror175", "cmVjb3JkMTc1bWlycm9yMTc1"),
    ("record175filter175", "cmVjb3JkMTc1ZmlsdGVyMTc1"),
    ("record175ranking175", "cmVjb3JkMTc1cmFua2luZzE3NQ"),
    ("candle175ranking175", "Y2FuZGxlMTc1cmFua2luZzE3NQ"),
    ("candle175encoding175", "Y2FuZGxlMTc1ZW5jb2RpbmcxNzU"),
    ("candle175mapping175", "Y2FuZGxlMTc1bWFwcGluZzE3NQ"),
    ("candle175record175", "Y2FuZGxlMTc1cmVjb3JkMTc1"),
    ("thread175record175", "dGhyZWFkMTc1cmVjb3JkMTc1"),
    ("thread175candle175", "dGhyZWFkMTc1Y2FuZGxlMTc1"),
    ("thread175thread175", "dGhyZWFkMTc1dGhyZWFkMTc1"),
    ("thread175kitten175", "dGhyZWFkMTc1a2l0dGVuMTc1"),
    (
        "round 175: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTc1OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 175: agentuniverse is a framework for multi agents",
        "cm91bmQgMTc1OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 175: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTc1OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 175: the processor reads the record then stops",
        "cm91bmQgMTc1OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 175: a worker pulls the next task from the queue",
        "cm91bmQgMTc1OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 175: signals travel through the network layer",
        "cm91bmQgMTc1OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 175: the gateway routes each request by policy",
        "cm91bmQgMTc1OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 175: memory grows until the buffer is full",
        "cm91bmQgMTc1OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 175: the cluster mirrors every packet twice",
        "cm91bmQgMTc1OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 175: ranking uses tokens learned from the corpus",
        "cm91bmQgMTc1OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 175: a long session ends when the candle dies",
        "cm91bmQgMTc1OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 175: encode the prompt then map the result",
        "cm91bmQgMTc1OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 175: the kernel wakes the worker at dawn",
        "cm91bmQgMTc1OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 175: service latency drops after the patch",
        "cm91bmQgMTc1OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 175: the library caches every vector it sees",
        "cm91bmQgMTc1OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 175: agents argue then the debate resolves",
        "cm91bmQgMTc1OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 175: the filter keeps only strong matches",
        "cm91bmQgMTc1OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 175: the model answers with a short reply",
        "cm91bmQgMTc1OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 175: the recorder stores the reasoning trace",
        "cm91bmQgMTc1OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 175: the angel watches the processor run",
        "cm91bmQgMTc1OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 175: angle of the vector decides the match",
        "cm91bmQgMTc1OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 175: the candle burns twice as long at night",
        "cm91bmQgMTc1OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 175: a mirror of the universe in one line",
        "cm91bmQgMTc1OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 175: the queue drains before the storm", "cm91bmQgMTc1OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
