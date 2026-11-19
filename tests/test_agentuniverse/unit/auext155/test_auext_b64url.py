"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten155kitten155", "a2l0dGVuMTU1a2l0dGVuMTU1"),
    ("kitten155sitting155", "a2l0dGVuMTU1c2l0dGluZzE1NQ"),
    ("kitten155agent155", "a2l0dGVuMTU1YWdlbnQxNTU"),
    ("kitten155angle155", "a2l0dGVuMTU1YW5nbGUxNTU"),
    ("sitting155angle155", "c2l0dGluZzE1NWFuZ2xlMTU1"),
    ("sitting155universe155", "c2l0dGluZzE1NXVuaXZlcnNlMTU1"),
    ("sitting155memory155", "c2l0dGluZzE1NW1lbW9yeTE1NQ"),
    ("sitting155stream155", "c2l0dGluZzE1NXN0cmVhbTE1NQ"),
    ("agent155stream155", "YWdlbnQxNTVzdHJlYW0xNTU"),
    ("agent155context155", "YWdlbnQxNTVjb250ZXh0MTU1"),
    ("agent155knowledge155", "YWdlbnQxNTVrbm93bGVkZ2UxNTU"),
    ("agent155vector155", "YWdlbnQxNTV2ZWN0b3IxNTU"),
    ("angle155vector155", "YW5nbGUxNTV2ZWN0b3IxNTU"),
    ("angle155processor155", "YW5nbGUxNTVwcm9jZXNzb3IxNTU"),
    ("angle155reasoning155", "YW5nbGUxNTVyZWFzb25pbmcxNTU"),
    ("angle155machine155", "YW5nbGUxNTVtYWNoaW5lMTU1"),
    ("universe155machine155", "dW5pdmVyc2UxNTVtYWNoaW5lMTU1"),
    ("universe155learning155", "dW5pdmVyc2UxNTVsZWFybmluZzE1NQ"),
    ("universe155model155", "dW5pdmVyc2UxNTVtb2RlbDE1NQ"),
    ("universe155token155", "dW5pdmVyc2UxNTV0b2tlbjE1NQ"),
    ("memory155token155", "bWVtb3J5MTU1dG9rZW4xNTU"),
    ("memory155prompt155", "bWVtb3J5MTU1cHJvbXB0MTU1"),
    ("memory155session155", "bWVtb3J5MTU1c2Vzc2lvbjE1NQ"),
    ("memory155library155", "bWVtb3J5MTU1bGlicmFyeTE1NQ"),
    ("stream155library155", "c3RyZWFtMTU1bGlicmFyeTE1NQ"),
    ("stream155service155", "c3RyZWFtMTU1c2VydmljZTE1NQ"),
    ("stream155gateway155", "c3RyZWFtMTU1Z2F0ZXdheTE1NQ"),
    ("stream155storage155", "c3RyZWFtMTU1c3RvcmFnZTE1NQ"),
    ("context155storage155", "Y29udGV4dDE1NXN0b3JhZ2UxNTU"),
    ("context155network155", "Y29udGV4dDE1NW5ldHdvcmsxNTU"),
    ("context155latency155", "Y29udGV4dDE1NWxhdGVuY3kxNTU"),
    ("context155buffer155", "Y29udGV4dDE1NWJ1ZmZlcjE1NQ"),
    ("knowledge155buffer155", "a25vd2xlZGdlMTU1YnVmZmVyMTU1"),
    ("knowledge155queue155", "a25vd2xlZGdlMTU1cXVldWUxNTU"),
    ("knowledge155worker155", "a25vd2xlZGdlMTU1d29ya2VyMTU1"),
    ("knowledge155kernel155", "a25vd2xlZGdlMTU1a2VybmVsMTU1"),
    ("vector155kernel155", "dmVjdG9yMTU1a2VybmVsMTU1"),
    ("vector155signal155", "dmVjdG9yMTU1c2lnbmFsMTU1"),
    ("vector155packet155", "dmVjdG9yMTU1cGFja2V0MTU1"),
    ("vector155router155", "dmVjdG9yMTU1cm91dGVyMTU1"),
    ("processor155router155", "cHJvY2Vzc29yMTU1cm91dGVyMTU1"),
    ("processor155cluster155", "cHJvY2Vzc29yMTU1Y2x1c3RlcjE1NQ"),
    ("processor155mirror155", "cHJvY2Vzc29yMTU1bWlycm9yMTU1"),
    ("processor155filter155", "cHJvY2Vzc29yMTU1ZmlsdGVyMTU1"),
    ("reasoning155filter155", "cmVhc29uaW5nMTU1ZmlsdGVyMTU1"),
    ("reasoning155ranking155", "cmVhc29uaW5nMTU1cmFua2luZzE1NQ"),
    ("reasoning155encoding155", "cmVhc29uaW5nMTU1ZW5jb2RpbmcxNTU"),
    ("reasoning155mapping155", "cmVhc29uaW5nMTU1bWFwcGluZzE1NQ"),
    ("machine155mapping155", "bWFjaGluZTE1NW1hcHBpbmcxNTU"),
    ("machine155record155", "bWFjaGluZTE1NXJlY29yZDE1NQ"),
    ("machine155candle155", "bWFjaGluZTE1NWNhbmRsZTE1NQ"),
    ("machine155thread155", "bWFjaGluZTE1NXRocmVhZDE1NQ"),
    ("learning155thread155", "bGVhcm5pbmcxNTV0aHJlYWQxNTU"),
    ("learning155kitten155", "bGVhcm5pbmcxNTVraXR0ZW4xNTU"),
    ("learning155sitting155", "bGVhcm5pbmcxNTVzaXR0aW5nMTU1"),
    ("learning155agent155", "bGVhcm5pbmcxNTVhZ2VudDE1NQ"),
    ("model155agent155", "bW9kZWwxNTVhZ2VudDE1NQ"),
    ("model155angle155", "bW9kZWwxNTVhbmdsZTE1NQ"),
    ("model155universe155", "bW9kZWwxNTV1bml2ZXJzZTE1NQ"),
    ("model155memory155", "bW9kZWwxNTVtZW1vcnkxNTU"),
    ("token155memory155", "dG9rZW4xNTVtZW1vcnkxNTU"),
    ("token155stream155", "dG9rZW4xNTVzdHJlYW0xNTU"),
    ("token155context155", "dG9rZW4xNTVjb250ZXh0MTU1"),
    ("token155knowledge155", "dG9rZW4xNTVrbm93bGVkZ2UxNTU"),
    ("prompt155knowledge155", "cHJvbXB0MTU1a25vd2xlZGdlMTU1"),
    ("prompt155vector155", "cHJvbXB0MTU1dmVjdG9yMTU1"),
    ("prompt155processor155", "cHJvbXB0MTU1cHJvY2Vzc29yMTU1"),
    ("prompt155reasoning155", "cHJvbXB0MTU1cmVhc29uaW5nMTU1"),
    ("session155reasoning155", "c2Vzc2lvbjE1NXJlYXNvbmluZzE1NQ"),
    ("session155machine155", "c2Vzc2lvbjE1NW1hY2hpbmUxNTU"),
    ("session155learning155", "c2Vzc2lvbjE1NWxlYXJuaW5nMTU1"),
    ("session155model155", "c2Vzc2lvbjE1NW1vZGVsMTU1"),
    ("library155model155", "bGlicmFyeTE1NW1vZGVsMTU1"),
    ("library155token155", "bGlicmFyeTE1NXRva2VuMTU1"),
    ("library155prompt155", "bGlicmFyeTE1NXByb21wdDE1NQ"),
    ("library155session155", "bGlicmFyeTE1NXNlc3Npb24xNTU"),
    ("service155session155", "c2VydmljZTE1NXNlc3Npb24xNTU"),
    ("service155library155", "c2VydmljZTE1NWxpYnJhcnkxNTU"),
    ("service155service155", "c2VydmljZTE1NXNlcnZpY2UxNTU"),
    ("service155gateway155", "c2VydmljZTE1NWdhdGV3YXkxNTU"),
    ("gateway155gateway155", "Z2F0ZXdheTE1NWdhdGV3YXkxNTU"),
    ("gateway155storage155", "Z2F0ZXdheTE1NXN0b3JhZ2UxNTU"),
    ("gateway155network155", "Z2F0ZXdheTE1NW5ldHdvcmsxNTU"),
    ("gateway155latency155", "Z2F0ZXdheTE1NWxhdGVuY3kxNTU"),
    ("storage155latency155", "c3RvcmFnZTE1NWxhdGVuY3kxNTU"),
    ("storage155buffer155", "c3RvcmFnZTE1NWJ1ZmZlcjE1NQ"),
    ("storage155queue155", "c3RvcmFnZTE1NXF1ZXVlMTU1"),
    ("storage155worker155", "c3RvcmFnZTE1NXdvcmtlcjE1NQ"),
    ("network155worker155", "bmV0d29yazE1NXdvcmtlcjE1NQ"),
    ("network155kernel155", "bmV0d29yazE1NWtlcm5lbDE1NQ"),
    ("network155signal155", "bmV0d29yazE1NXNpZ25hbDE1NQ"),
    ("network155packet155", "bmV0d29yazE1NXBhY2tldDE1NQ"),
    ("latency155packet155", "bGF0ZW5jeTE1NXBhY2tldDE1NQ"),
    ("latency155router155", "bGF0ZW5jeTE1NXJvdXRlcjE1NQ"),
    ("latency155cluster155", "bGF0ZW5jeTE1NWNsdXN0ZXIxNTU"),
    ("latency155mirror155", "bGF0ZW5jeTE1NW1pcnJvcjE1NQ"),
    ("buffer155mirror155", "YnVmZmVyMTU1bWlycm9yMTU1"),
    ("buffer155filter155", "YnVmZmVyMTU1ZmlsdGVyMTU1"),
    ("buffer155ranking155", "YnVmZmVyMTU1cmFua2luZzE1NQ"),
    ("buffer155encoding155", "YnVmZmVyMTU1ZW5jb2RpbmcxNTU"),
    ("queue155encoding155", "cXVldWUxNTVlbmNvZGluZzE1NQ"),
    ("queue155mapping155", "cXVldWUxNTVtYXBwaW5nMTU1"),
    ("queue155record155", "cXVldWUxNTVyZWNvcmQxNTU"),
    ("queue155candle155", "cXVldWUxNTVjYW5kbGUxNTU"),
    ("worker155candle155", "d29ya2VyMTU1Y2FuZGxlMTU1"),
    ("worker155thread155", "d29ya2VyMTU1dGhyZWFkMTU1"),
    ("worker155kitten155", "d29ya2VyMTU1a2l0dGVuMTU1"),
    ("worker155sitting155", "d29ya2VyMTU1c2l0dGluZzE1NQ"),
    ("kernel155sitting155", "a2VybmVsMTU1c2l0dGluZzE1NQ"),
    ("kernel155agent155", "a2VybmVsMTU1YWdlbnQxNTU"),
    ("kernel155angle155", "a2VybmVsMTU1YW5nbGUxNTU"),
    ("kernel155universe155", "a2VybmVsMTU1dW5pdmVyc2UxNTU"),
    ("signal155universe155", "c2lnbmFsMTU1dW5pdmVyc2UxNTU"),
    ("signal155memory155", "c2lnbmFsMTU1bWVtb3J5MTU1"),
    ("signal155stream155", "c2lnbmFsMTU1c3RyZWFtMTU1"),
    ("signal155context155", "c2lnbmFsMTU1Y29udGV4dDE1NQ"),
    ("packet155context155", "cGFja2V0MTU1Y29udGV4dDE1NQ"),
    ("packet155knowledge155", "cGFja2V0MTU1a25vd2xlZGdlMTU1"),
    ("packet155vector155", "cGFja2V0MTU1dmVjdG9yMTU1"),
    ("packet155processor155", "cGFja2V0MTU1cHJvY2Vzc29yMTU1"),
    ("router155processor155", "cm91dGVyMTU1cHJvY2Vzc29yMTU1"),
    ("router155reasoning155", "cm91dGVyMTU1cmVhc29uaW5nMTU1"),
    ("router155machine155", "cm91dGVyMTU1bWFjaGluZTE1NQ"),
    ("router155learning155", "cm91dGVyMTU1bGVhcm5pbmcxNTU"),
    ("cluster155learning155", "Y2x1c3RlcjE1NWxlYXJuaW5nMTU1"),
    ("cluster155model155", "Y2x1c3RlcjE1NW1vZGVsMTU1"),
    ("cluster155token155", "Y2x1c3RlcjE1NXRva2VuMTU1"),
    ("cluster155prompt155", "Y2x1c3RlcjE1NXByb21wdDE1NQ"),
    ("mirror155prompt155", "bWlycm9yMTU1cHJvbXB0MTU1"),
    ("mirror155session155", "bWlycm9yMTU1c2Vzc2lvbjE1NQ"),
    ("mirror155library155", "bWlycm9yMTU1bGlicmFyeTE1NQ"),
    ("mirror155service155", "bWlycm9yMTU1c2VydmljZTE1NQ"),
    ("filter155service155", "ZmlsdGVyMTU1c2VydmljZTE1NQ"),
    ("filter155gateway155", "ZmlsdGVyMTU1Z2F0ZXdheTE1NQ"),
    ("filter155storage155", "ZmlsdGVyMTU1c3RvcmFnZTE1NQ"),
    ("filter155network155", "ZmlsdGVyMTU1bmV0d29yazE1NQ"),
    ("ranking155network155", "cmFua2luZzE1NW5ldHdvcmsxNTU"),
    ("ranking155latency155", "cmFua2luZzE1NWxhdGVuY3kxNTU"),
    ("ranking155buffer155", "cmFua2luZzE1NWJ1ZmZlcjE1NQ"),
    ("ranking155queue155", "cmFua2luZzE1NXF1ZXVlMTU1"),
    ("encoding155queue155", "ZW5jb2RpbmcxNTVxdWV1ZTE1NQ"),
    ("encoding155worker155", "ZW5jb2RpbmcxNTV3b3JrZXIxNTU"),
    ("encoding155kernel155", "ZW5jb2RpbmcxNTVrZXJuZWwxNTU"),
    ("encoding155signal155", "ZW5jb2RpbmcxNTVzaWduYWwxNTU"),
    ("mapping155signal155", "bWFwcGluZzE1NXNpZ25hbDE1NQ"),
    ("mapping155packet155", "bWFwcGluZzE1NXBhY2tldDE1NQ"),
    ("mapping155router155", "bWFwcGluZzE1NXJvdXRlcjE1NQ"),
    ("mapping155cluster155", "bWFwcGluZzE1NWNsdXN0ZXIxNTU"),
    ("record155cluster155", "cmVjb3JkMTU1Y2x1c3RlcjE1NQ"),
    ("record155mirror155", "cmVjb3JkMTU1bWlycm9yMTU1"),
    ("record155filter155", "cmVjb3JkMTU1ZmlsdGVyMTU1"),
    ("record155ranking155", "cmVjb3JkMTU1cmFua2luZzE1NQ"),
    ("candle155ranking155", "Y2FuZGxlMTU1cmFua2luZzE1NQ"),
    ("candle155encoding155", "Y2FuZGxlMTU1ZW5jb2RpbmcxNTU"),
    ("candle155mapping155", "Y2FuZGxlMTU1bWFwcGluZzE1NQ"),
    ("candle155record155", "Y2FuZGxlMTU1cmVjb3JkMTU1"),
    ("thread155record155", "dGhyZWFkMTU1cmVjb3JkMTU1"),
    ("thread155candle155", "dGhyZWFkMTU1Y2FuZGxlMTU1"),
    ("thread155thread155", "dGhyZWFkMTU1dGhyZWFkMTU1"),
    ("thread155kitten155", "dGhyZWFkMTU1a2l0dGVuMTU1"),
    (
        "round 155: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTU1OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 155: agentuniverse is a framework for multi agents",
        "cm91bmQgMTU1OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 155: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTU1OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 155: the processor reads the record then stops",
        "cm91bmQgMTU1OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 155: a worker pulls the next task from the queue",
        "cm91bmQgMTU1OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 155: signals travel through the network layer",
        "cm91bmQgMTU1OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 155: the gateway routes each request by policy",
        "cm91bmQgMTU1OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 155: memory grows until the buffer is full",
        "cm91bmQgMTU1OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 155: the cluster mirrors every packet twice",
        "cm91bmQgMTU1OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 155: ranking uses tokens learned from the corpus",
        "cm91bmQgMTU1OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 155: a long session ends when the candle dies",
        "cm91bmQgMTU1OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 155: encode the prompt then map the result",
        "cm91bmQgMTU1OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 155: the kernel wakes the worker at dawn",
        "cm91bmQgMTU1OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 155: service latency drops after the patch",
        "cm91bmQgMTU1OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 155: the library caches every vector it sees",
        "cm91bmQgMTU1OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 155: agents argue then the debate resolves",
        "cm91bmQgMTU1OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 155: the filter keeps only strong matches",
        "cm91bmQgMTU1OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 155: the model answers with a short reply",
        "cm91bmQgMTU1OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 155: the recorder stores the reasoning trace",
        "cm91bmQgMTU1OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 155: the angel watches the processor run",
        "cm91bmQgMTU1OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 155: angle of the vector decides the match",
        "cm91bmQgMTU1OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 155: the candle burns twice as long at night",
        "cm91bmQgMTU1OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 155: a mirror of the universe in one line",
        "cm91bmQgMTU1OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 155: the queue drains before the storm", "cm91bmQgMTU1OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
