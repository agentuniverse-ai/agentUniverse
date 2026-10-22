"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten151kitten151", "a2l0dGVuMTUxa2l0dGVuMTUx"),
    ("kitten151sitting151", "a2l0dGVuMTUxc2l0dGluZzE1MQ"),
    ("kitten151agent151", "a2l0dGVuMTUxYWdlbnQxNTE"),
    ("kitten151angle151", "a2l0dGVuMTUxYW5nbGUxNTE"),
    ("sitting151angle151", "c2l0dGluZzE1MWFuZ2xlMTUx"),
    ("sitting151universe151", "c2l0dGluZzE1MXVuaXZlcnNlMTUx"),
    ("sitting151memory151", "c2l0dGluZzE1MW1lbW9yeTE1MQ"),
    ("sitting151stream151", "c2l0dGluZzE1MXN0cmVhbTE1MQ"),
    ("agent151stream151", "YWdlbnQxNTFzdHJlYW0xNTE"),
    ("agent151context151", "YWdlbnQxNTFjb250ZXh0MTUx"),
    ("agent151knowledge151", "YWdlbnQxNTFrbm93bGVkZ2UxNTE"),
    ("agent151vector151", "YWdlbnQxNTF2ZWN0b3IxNTE"),
    ("angle151vector151", "YW5nbGUxNTF2ZWN0b3IxNTE"),
    ("angle151processor151", "YW5nbGUxNTFwcm9jZXNzb3IxNTE"),
    ("angle151reasoning151", "YW5nbGUxNTFyZWFzb25pbmcxNTE"),
    ("angle151machine151", "YW5nbGUxNTFtYWNoaW5lMTUx"),
    ("universe151machine151", "dW5pdmVyc2UxNTFtYWNoaW5lMTUx"),
    ("universe151learning151", "dW5pdmVyc2UxNTFsZWFybmluZzE1MQ"),
    ("universe151model151", "dW5pdmVyc2UxNTFtb2RlbDE1MQ"),
    ("universe151token151", "dW5pdmVyc2UxNTF0b2tlbjE1MQ"),
    ("memory151token151", "bWVtb3J5MTUxdG9rZW4xNTE"),
    ("memory151prompt151", "bWVtb3J5MTUxcHJvbXB0MTUx"),
    ("memory151session151", "bWVtb3J5MTUxc2Vzc2lvbjE1MQ"),
    ("memory151library151", "bWVtb3J5MTUxbGlicmFyeTE1MQ"),
    ("stream151library151", "c3RyZWFtMTUxbGlicmFyeTE1MQ"),
    ("stream151service151", "c3RyZWFtMTUxc2VydmljZTE1MQ"),
    ("stream151gateway151", "c3RyZWFtMTUxZ2F0ZXdheTE1MQ"),
    ("stream151storage151", "c3RyZWFtMTUxc3RvcmFnZTE1MQ"),
    ("context151storage151", "Y29udGV4dDE1MXN0b3JhZ2UxNTE"),
    ("context151network151", "Y29udGV4dDE1MW5ldHdvcmsxNTE"),
    ("context151latency151", "Y29udGV4dDE1MWxhdGVuY3kxNTE"),
    ("context151buffer151", "Y29udGV4dDE1MWJ1ZmZlcjE1MQ"),
    ("knowledge151buffer151", "a25vd2xlZGdlMTUxYnVmZmVyMTUx"),
    ("knowledge151queue151", "a25vd2xlZGdlMTUxcXVldWUxNTE"),
    ("knowledge151worker151", "a25vd2xlZGdlMTUxd29ya2VyMTUx"),
    ("knowledge151kernel151", "a25vd2xlZGdlMTUxa2VybmVsMTUx"),
    ("vector151kernel151", "dmVjdG9yMTUxa2VybmVsMTUx"),
    ("vector151signal151", "dmVjdG9yMTUxc2lnbmFsMTUx"),
    ("vector151packet151", "dmVjdG9yMTUxcGFja2V0MTUx"),
    ("vector151router151", "dmVjdG9yMTUxcm91dGVyMTUx"),
    ("processor151router151", "cHJvY2Vzc29yMTUxcm91dGVyMTUx"),
    ("processor151cluster151", "cHJvY2Vzc29yMTUxY2x1c3RlcjE1MQ"),
    ("processor151mirror151", "cHJvY2Vzc29yMTUxbWlycm9yMTUx"),
    ("processor151filter151", "cHJvY2Vzc29yMTUxZmlsdGVyMTUx"),
    ("reasoning151filter151", "cmVhc29uaW5nMTUxZmlsdGVyMTUx"),
    ("reasoning151ranking151", "cmVhc29uaW5nMTUxcmFua2luZzE1MQ"),
    ("reasoning151encoding151", "cmVhc29uaW5nMTUxZW5jb2RpbmcxNTE"),
    ("reasoning151mapping151", "cmVhc29uaW5nMTUxbWFwcGluZzE1MQ"),
    ("machine151mapping151", "bWFjaGluZTE1MW1hcHBpbmcxNTE"),
    ("machine151record151", "bWFjaGluZTE1MXJlY29yZDE1MQ"),
    ("machine151candle151", "bWFjaGluZTE1MWNhbmRsZTE1MQ"),
    ("machine151thread151", "bWFjaGluZTE1MXRocmVhZDE1MQ"),
    ("learning151thread151", "bGVhcm5pbmcxNTF0aHJlYWQxNTE"),
    ("learning151kitten151", "bGVhcm5pbmcxNTFraXR0ZW4xNTE"),
    ("learning151sitting151", "bGVhcm5pbmcxNTFzaXR0aW5nMTUx"),
    ("learning151agent151", "bGVhcm5pbmcxNTFhZ2VudDE1MQ"),
    ("model151agent151", "bW9kZWwxNTFhZ2VudDE1MQ"),
    ("model151angle151", "bW9kZWwxNTFhbmdsZTE1MQ"),
    ("model151universe151", "bW9kZWwxNTF1bml2ZXJzZTE1MQ"),
    ("model151memory151", "bW9kZWwxNTFtZW1vcnkxNTE"),
    ("token151memory151", "dG9rZW4xNTFtZW1vcnkxNTE"),
    ("token151stream151", "dG9rZW4xNTFzdHJlYW0xNTE"),
    ("token151context151", "dG9rZW4xNTFjb250ZXh0MTUx"),
    ("token151knowledge151", "dG9rZW4xNTFrbm93bGVkZ2UxNTE"),
    ("prompt151knowledge151", "cHJvbXB0MTUxa25vd2xlZGdlMTUx"),
    ("prompt151vector151", "cHJvbXB0MTUxdmVjdG9yMTUx"),
    ("prompt151processor151", "cHJvbXB0MTUxcHJvY2Vzc29yMTUx"),
    ("prompt151reasoning151", "cHJvbXB0MTUxcmVhc29uaW5nMTUx"),
    ("session151reasoning151", "c2Vzc2lvbjE1MXJlYXNvbmluZzE1MQ"),
    ("session151machine151", "c2Vzc2lvbjE1MW1hY2hpbmUxNTE"),
    ("session151learning151", "c2Vzc2lvbjE1MWxlYXJuaW5nMTUx"),
    ("session151model151", "c2Vzc2lvbjE1MW1vZGVsMTUx"),
    ("library151model151", "bGlicmFyeTE1MW1vZGVsMTUx"),
    ("library151token151", "bGlicmFyeTE1MXRva2VuMTUx"),
    ("library151prompt151", "bGlicmFyeTE1MXByb21wdDE1MQ"),
    ("library151session151", "bGlicmFyeTE1MXNlc3Npb24xNTE"),
    ("service151session151", "c2VydmljZTE1MXNlc3Npb24xNTE"),
    ("service151library151", "c2VydmljZTE1MWxpYnJhcnkxNTE"),
    ("service151service151", "c2VydmljZTE1MXNlcnZpY2UxNTE"),
    ("service151gateway151", "c2VydmljZTE1MWdhdGV3YXkxNTE"),
    ("gateway151gateway151", "Z2F0ZXdheTE1MWdhdGV3YXkxNTE"),
    ("gateway151storage151", "Z2F0ZXdheTE1MXN0b3JhZ2UxNTE"),
    ("gateway151network151", "Z2F0ZXdheTE1MW5ldHdvcmsxNTE"),
    ("gateway151latency151", "Z2F0ZXdheTE1MWxhdGVuY3kxNTE"),
    ("storage151latency151", "c3RvcmFnZTE1MWxhdGVuY3kxNTE"),
    ("storage151buffer151", "c3RvcmFnZTE1MWJ1ZmZlcjE1MQ"),
    ("storage151queue151", "c3RvcmFnZTE1MXF1ZXVlMTUx"),
    ("storage151worker151", "c3RvcmFnZTE1MXdvcmtlcjE1MQ"),
    ("network151worker151", "bmV0d29yazE1MXdvcmtlcjE1MQ"),
    ("network151kernel151", "bmV0d29yazE1MWtlcm5lbDE1MQ"),
    ("network151signal151", "bmV0d29yazE1MXNpZ25hbDE1MQ"),
    ("network151packet151", "bmV0d29yazE1MXBhY2tldDE1MQ"),
    ("latency151packet151", "bGF0ZW5jeTE1MXBhY2tldDE1MQ"),
    ("latency151router151", "bGF0ZW5jeTE1MXJvdXRlcjE1MQ"),
    ("latency151cluster151", "bGF0ZW5jeTE1MWNsdXN0ZXIxNTE"),
    ("latency151mirror151", "bGF0ZW5jeTE1MW1pcnJvcjE1MQ"),
    ("buffer151mirror151", "YnVmZmVyMTUxbWlycm9yMTUx"),
    ("buffer151filter151", "YnVmZmVyMTUxZmlsdGVyMTUx"),
    ("buffer151ranking151", "YnVmZmVyMTUxcmFua2luZzE1MQ"),
    ("buffer151encoding151", "YnVmZmVyMTUxZW5jb2RpbmcxNTE"),
    ("queue151encoding151", "cXVldWUxNTFlbmNvZGluZzE1MQ"),
    ("queue151mapping151", "cXVldWUxNTFtYXBwaW5nMTUx"),
    ("queue151record151", "cXVldWUxNTFyZWNvcmQxNTE"),
    ("queue151candle151", "cXVldWUxNTFjYW5kbGUxNTE"),
    ("worker151candle151", "d29ya2VyMTUxY2FuZGxlMTUx"),
    ("worker151thread151", "d29ya2VyMTUxdGhyZWFkMTUx"),
    ("worker151kitten151", "d29ya2VyMTUxa2l0dGVuMTUx"),
    ("worker151sitting151", "d29ya2VyMTUxc2l0dGluZzE1MQ"),
    ("kernel151sitting151", "a2VybmVsMTUxc2l0dGluZzE1MQ"),
    ("kernel151agent151", "a2VybmVsMTUxYWdlbnQxNTE"),
    ("kernel151angle151", "a2VybmVsMTUxYW5nbGUxNTE"),
    ("kernel151universe151", "a2VybmVsMTUxdW5pdmVyc2UxNTE"),
    ("signal151universe151", "c2lnbmFsMTUxdW5pdmVyc2UxNTE"),
    ("signal151memory151", "c2lnbmFsMTUxbWVtb3J5MTUx"),
    ("signal151stream151", "c2lnbmFsMTUxc3RyZWFtMTUx"),
    ("signal151context151", "c2lnbmFsMTUxY29udGV4dDE1MQ"),
    ("packet151context151", "cGFja2V0MTUxY29udGV4dDE1MQ"),
    ("packet151knowledge151", "cGFja2V0MTUxa25vd2xlZGdlMTUx"),
    ("packet151vector151", "cGFja2V0MTUxdmVjdG9yMTUx"),
    ("packet151processor151", "cGFja2V0MTUxcHJvY2Vzc29yMTUx"),
    ("router151processor151", "cm91dGVyMTUxcHJvY2Vzc29yMTUx"),
    ("router151reasoning151", "cm91dGVyMTUxcmVhc29uaW5nMTUx"),
    ("router151machine151", "cm91dGVyMTUxbWFjaGluZTE1MQ"),
    ("router151learning151", "cm91dGVyMTUxbGVhcm5pbmcxNTE"),
    ("cluster151learning151", "Y2x1c3RlcjE1MWxlYXJuaW5nMTUx"),
    ("cluster151model151", "Y2x1c3RlcjE1MW1vZGVsMTUx"),
    ("cluster151token151", "Y2x1c3RlcjE1MXRva2VuMTUx"),
    ("cluster151prompt151", "Y2x1c3RlcjE1MXByb21wdDE1MQ"),
    ("mirror151prompt151", "bWlycm9yMTUxcHJvbXB0MTUx"),
    ("mirror151session151", "bWlycm9yMTUxc2Vzc2lvbjE1MQ"),
    ("mirror151library151", "bWlycm9yMTUxbGlicmFyeTE1MQ"),
    ("mirror151service151", "bWlycm9yMTUxc2VydmljZTE1MQ"),
    ("filter151service151", "ZmlsdGVyMTUxc2VydmljZTE1MQ"),
    ("filter151gateway151", "ZmlsdGVyMTUxZ2F0ZXdheTE1MQ"),
    ("filter151storage151", "ZmlsdGVyMTUxc3RvcmFnZTE1MQ"),
    ("filter151network151", "ZmlsdGVyMTUxbmV0d29yazE1MQ"),
    ("ranking151network151", "cmFua2luZzE1MW5ldHdvcmsxNTE"),
    ("ranking151latency151", "cmFua2luZzE1MWxhdGVuY3kxNTE"),
    ("ranking151buffer151", "cmFua2luZzE1MWJ1ZmZlcjE1MQ"),
    ("ranking151queue151", "cmFua2luZzE1MXF1ZXVlMTUx"),
    ("encoding151queue151", "ZW5jb2RpbmcxNTFxdWV1ZTE1MQ"),
    ("encoding151worker151", "ZW5jb2RpbmcxNTF3b3JrZXIxNTE"),
    ("encoding151kernel151", "ZW5jb2RpbmcxNTFrZXJuZWwxNTE"),
    ("encoding151signal151", "ZW5jb2RpbmcxNTFzaWduYWwxNTE"),
    ("mapping151signal151", "bWFwcGluZzE1MXNpZ25hbDE1MQ"),
    ("mapping151packet151", "bWFwcGluZzE1MXBhY2tldDE1MQ"),
    ("mapping151router151", "bWFwcGluZzE1MXJvdXRlcjE1MQ"),
    ("mapping151cluster151", "bWFwcGluZzE1MWNsdXN0ZXIxNTE"),
    ("record151cluster151", "cmVjb3JkMTUxY2x1c3RlcjE1MQ"),
    ("record151mirror151", "cmVjb3JkMTUxbWlycm9yMTUx"),
    ("record151filter151", "cmVjb3JkMTUxZmlsdGVyMTUx"),
    ("record151ranking151", "cmVjb3JkMTUxcmFua2luZzE1MQ"),
    ("candle151ranking151", "Y2FuZGxlMTUxcmFua2luZzE1MQ"),
    ("candle151encoding151", "Y2FuZGxlMTUxZW5jb2RpbmcxNTE"),
    ("candle151mapping151", "Y2FuZGxlMTUxbWFwcGluZzE1MQ"),
    ("candle151record151", "Y2FuZGxlMTUxcmVjb3JkMTUx"),
    ("thread151record151", "dGhyZWFkMTUxcmVjb3JkMTUx"),
    ("thread151candle151", "dGhyZWFkMTUxY2FuZGxlMTUx"),
    ("thread151thread151", "dGhyZWFkMTUxdGhyZWFkMTUx"),
    ("thread151kitten151", "dGhyZWFkMTUxa2l0dGVuMTUx"),
    (
        "round 151: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTUxOiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 151: agentuniverse is a framework for multi agents",
        "cm91bmQgMTUxOiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 151: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTUxOiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 151: the processor reads the record then stops",
        "cm91bmQgMTUxOiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 151: a worker pulls the next task from the queue",
        "cm91bmQgMTUxOiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 151: signals travel through the network layer",
        "cm91bmQgMTUxOiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 151: the gateway routes each request by policy",
        "cm91bmQgMTUxOiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 151: memory grows until the buffer is full",
        "cm91bmQgMTUxOiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 151: the cluster mirrors every packet twice",
        "cm91bmQgMTUxOiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 151: ranking uses tokens learned from the corpus",
        "cm91bmQgMTUxOiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 151: a long session ends when the candle dies",
        "cm91bmQgMTUxOiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 151: encode the prompt then map the result",
        "cm91bmQgMTUxOiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 151: the kernel wakes the worker at dawn",
        "cm91bmQgMTUxOiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 151: service latency drops after the patch",
        "cm91bmQgMTUxOiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 151: the library caches every vector it sees",
        "cm91bmQgMTUxOiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 151: agents argue then the debate resolves",
        "cm91bmQgMTUxOiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 151: the filter keeps only strong matches",
        "cm91bmQgMTUxOiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 151: the model answers with a short reply",
        "cm91bmQgMTUxOiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 151: the recorder stores the reasoning trace",
        "cm91bmQgMTUxOiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 151: the angel watches the processor run",
        "cm91bmQgMTUxOiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 151: angle of the vector decides the match",
        "cm91bmQgMTUxOiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 151: the candle burns twice as long at night",
        "cm91bmQgMTUxOiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 151: a mirror of the universe in one line",
        "cm91bmQgMTUxOiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 151: the queue drains before the storm", "cm91bmQgMTUxOiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
