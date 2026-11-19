"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten171kitten171", "a2l0dGVuMTcxa2l0dGVuMTcx"),
    ("kitten171sitting171", "a2l0dGVuMTcxc2l0dGluZzE3MQ"),
    ("kitten171agent171", "a2l0dGVuMTcxYWdlbnQxNzE"),
    ("kitten171angle171", "a2l0dGVuMTcxYW5nbGUxNzE"),
    ("sitting171angle171", "c2l0dGluZzE3MWFuZ2xlMTcx"),
    ("sitting171universe171", "c2l0dGluZzE3MXVuaXZlcnNlMTcx"),
    ("sitting171memory171", "c2l0dGluZzE3MW1lbW9yeTE3MQ"),
    ("sitting171stream171", "c2l0dGluZzE3MXN0cmVhbTE3MQ"),
    ("agent171stream171", "YWdlbnQxNzFzdHJlYW0xNzE"),
    ("agent171context171", "YWdlbnQxNzFjb250ZXh0MTcx"),
    ("agent171knowledge171", "YWdlbnQxNzFrbm93bGVkZ2UxNzE"),
    ("agent171vector171", "YWdlbnQxNzF2ZWN0b3IxNzE"),
    ("angle171vector171", "YW5nbGUxNzF2ZWN0b3IxNzE"),
    ("angle171processor171", "YW5nbGUxNzFwcm9jZXNzb3IxNzE"),
    ("angle171reasoning171", "YW5nbGUxNzFyZWFzb25pbmcxNzE"),
    ("angle171machine171", "YW5nbGUxNzFtYWNoaW5lMTcx"),
    ("universe171machine171", "dW5pdmVyc2UxNzFtYWNoaW5lMTcx"),
    ("universe171learning171", "dW5pdmVyc2UxNzFsZWFybmluZzE3MQ"),
    ("universe171model171", "dW5pdmVyc2UxNzFtb2RlbDE3MQ"),
    ("universe171token171", "dW5pdmVyc2UxNzF0b2tlbjE3MQ"),
    ("memory171token171", "bWVtb3J5MTcxdG9rZW4xNzE"),
    ("memory171prompt171", "bWVtb3J5MTcxcHJvbXB0MTcx"),
    ("memory171session171", "bWVtb3J5MTcxc2Vzc2lvbjE3MQ"),
    ("memory171library171", "bWVtb3J5MTcxbGlicmFyeTE3MQ"),
    ("stream171library171", "c3RyZWFtMTcxbGlicmFyeTE3MQ"),
    ("stream171service171", "c3RyZWFtMTcxc2VydmljZTE3MQ"),
    ("stream171gateway171", "c3RyZWFtMTcxZ2F0ZXdheTE3MQ"),
    ("stream171storage171", "c3RyZWFtMTcxc3RvcmFnZTE3MQ"),
    ("context171storage171", "Y29udGV4dDE3MXN0b3JhZ2UxNzE"),
    ("context171network171", "Y29udGV4dDE3MW5ldHdvcmsxNzE"),
    ("context171latency171", "Y29udGV4dDE3MWxhdGVuY3kxNzE"),
    ("context171buffer171", "Y29udGV4dDE3MWJ1ZmZlcjE3MQ"),
    ("knowledge171buffer171", "a25vd2xlZGdlMTcxYnVmZmVyMTcx"),
    ("knowledge171queue171", "a25vd2xlZGdlMTcxcXVldWUxNzE"),
    ("knowledge171worker171", "a25vd2xlZGdlMTcxd29ya2VyMTcx"),
    ("knowledge171kernel171", "a25vd2xlZGdlMTcxa2VybmVsMTcx"),
    ("vector171kernel171", "dmVjdG9yMTcxa2VybmVsMTcx"),
    ("vector171signal171", "dmVjdG9yMTcxc2lnbmFsMTcx"),
    ("vector171packet171", "dmVjdG9yMTcxcGFja2V0MTcx"),
    ("vector171router171", "dmVjdG9yMTcxcm91dGVyMTcx"),
    ("processor171router171", "cHJvY2Vzc29yMTcxcm91dGVyMTcx"),
    ("processor171cluster171", "cHJvY2Vzc29yMTcxY2x1c3RlcjE3MQ"),
    ("processor171mirror171", "cHJvY2Vzc29yMTcxbWlycm9yMTcx"),
    ("processor171filter171", "cHJvY2Vzc29yMTcxZmlsdGVyMTcx"),
    ("reasoning171filter171", "cmVhc29uaW5nMTcxZmlsdGVyMTcx"),
    ("reasoning171ranking171", "cmVhc29uaW5nMTcxcmFua2luZzE3MQ"),
    ("reasoning171encoding171", "cmVhc29uaW5nMTcxZW5jb2RpbmcxNzE"),
    ("reasoning171mapping171", "cmVhc29uaW5nMTcxbWFwcGluZzE3MQ"),
    ("machine171mapping171", "bWFjaGluZTE3MW1hcHBpbmcxNzE"),
    ("machine171record171", "bWFjaGluZTE3MXJlY29yZDE3MQ"),
    ("machine171candle171", "bWFjaGluZTE3MWNhbmRsZTE3MQ"),
    ("machine171thread171", "bWFjaGluZTE3MXRocmVhZDE3MQ"),
    ("learning171thread171", "bGVhcm5pbmcxNzF0aHJlYWQxNzE"),
    ("learning171kitten171", "bGVhcm5pbmcxNzFraXR0ZW4xNzE"),
    ("learning171sitting171", "bGVhcm5pbmcxNzFzaXR0aW5nMTcx"),
    ("learning171agent171", "bGVhcm5pbmcxNzFhZ2VudDE3MQ"),
    ("model171agent171", "bW9kZWwxNzFhZ2VudDE3MQ"),
    ("model171angle171", "bW9kZWwxNzFhbmdsZTE3MQ"),
    ("model171universe171", "bW9kZWwxNzF1bml2ZXJzZTE3MQ"),
    ("model171memory171", "bW9kZWwxNzFtZW1vcnkxNzE"),
    ("token171memory171", "dG9rZW4xNzFtZW1vcnkxNzE"),
    ("token171stream171", "dG9rZW4xNzFzdHJlYW0xNzE"),
    ("token171context171", "dG9rZW4xNzFjb250ZXh0MTcx"),
    ("token171knowledge171", "dG9rZW4xNzFrbm93bGVkZ2UxNzE"),
    ("prompt171knowledge171", "cHJvbXB0MTcxa25vd2xlZGdlMTcx"),
    ("prompt171vector171", "cHJvbXB0MTcxdmVjdG9yMTcx"),
    ("prompt171processor171", "cHJvbXB0MTcxcHJvY2Vzc29yMTcx"),
    ("prompt171reasoning171", "cHJvbXB0MTcxcmVhc29uaW5nMTcx"),
    ("session171reasoning171", "c2Vzc2lvbjE3MXJlYXNvbmluZzE3MQ"),
    ("session171machine171", "c2Vzc2lvbjE3MW1hY2hpbmUxNzE"),
    ("session171learning171", "c2Vzc2lvbjE3MWxlYXJuaW5nMTcx"),
    ("session171model171", "c2Vzc2lvbjE3MW1vZGVsMTcx"),
    ("library171model171", "bGlicmFyeTE3MW1vZGVsMTcx"),
    ("library171token171", "bGlicmFyeTE3MXRva2VuMTcx"),
    ("library171prompt171", "bGlicmFyeTE3MXByb21wdDE3MQ"),
    ("library171session171", "bGlicmFyeTE3MXNlc3Npb24xNzE"),
    ("service171session171", "c2VydmljZTE3MXNlc3Npb24xNzE"),
    ("service171library171", "c2VydmljZTE3MWxpYnJhcnkxNzE"),
    ("service171service171", "c2VydmljZTE3MXNlcnZpY2UxNzE"),
    ("service171gateway171", "c2VydmljZTE3MWdhdGV3YXkxNzE"),
    ("gateway171gateway171", "Z2F0ZXdheTE3MWdhdGV3YXkxNzE"),
    ("gateway171storage171", "Z2F0ZXdheTE3MXN0b3JhZ2UxNzE"),
    ("gateway171network171", "Z2F0ZXdheTE3MW5ldHdvcmsxNzE"),
    ("gateway171latency171", "Z2F0ZXdheTE3MWxhdGVuY3kxNzE"),
    ("storage171latency171", "c3RvcmFnZTE3MWxhdGVuY3kxNzE"),
    ("storage171buffer171", "c3RvcmFnZTE3MWJ1ZmZlcjE3MQ"),
    ("storage171queue171", "c3RvcmFnZTE3MXF1ZXVlMTcx"),
    ("storage171worker171", "c3RvcmFnZTE3MXdvcmtlcjE3MQ"),
    ("network171worker171", "bmV0d29yazE3MXdvcmtlcjE3MQ"),
    ("network171kernel171", "bmV0d29yazE3MWtlcm5lbDE3MQ"),
    ("network171signal171", "bmV0d29yazE3MXNpZ25hbDE3MQ"),
    ("network171packet171", "bmV0d29yazE3MXBhY2tldDE3MQ"),
    ("latency171packet171", "bGF0ZW5jeTE3MXBhY2tldDE3MQ"),
    ("latency171router171", "bGF0ZW5jeTE3MXJvdXRlcjE3MQ"),
    ("latency171cluster171", "bGF0ZW5jeTE3MWNsdXN0ZXIxNzE"),
    ("latency171mirror171", "bGF0ZW5jeTE3MW1pcnJvcjE3MQ"),
    ("buffer171mirror171", "YnVmZmVyMTcxbWlycm9yMTcx"),
    ("buffer171filter171", "YnVmZmVyMTcxZmlsdGVyMTcx"),
    ("buffer171ranking171", "YnVmZmVyMTcxcmFua2luZzE3MQ"),
    ("buffer171encoding171", "YnVmZmVyMTcxZW5jb2RpbmcxNzE"),
    ("queue171encoding171", "cXVldWUxNzFlbmNvZGluZzE3MQ"),
    ("queue171mapping171", "cXVldWUxNzFtYXBwaW5nMTcx"),
    ("queue171record171", "cXVldWUxNzFyZWNvcmQxNzE"),
    ("queue171candle171", "cXVldWUxNzFjYW5kbGUxNzE"),
    ("worker171candle171", "d29ya2VyMTcxY2FuZGxlMTcx"),
    ("worker171thread171", "d29ya2VyMTcxdGhyZWFkMTcx"),
    ("worker171kitten171", "d29ya2VyMTcxa2l0dGVuMTcx"),
    ("worker171sitting171", "d29ya2VyMTcxc2l0dGluZzE3MQ"),
    ("kernel171sitting171", "a2VybmVsMTcxc2l0dGluZzE3MQ"),
    ("kernel171agent171", "a2VybmVsMTcxYWdlbnQxNzE"),
    ("kernel171angle171", "a2VybmVsMTcxYW5nbGUxNzE"),
    ("kernel171universe171", "a2VybmVsMTcxdW5pdmVyc2UxNzE"),
    ("signal171universe171", "c2lnbmFsMTcxdW5pdmVyc2UxNzE"),
    ("signal171memory171", "c2lnbmFsMTcxbWVtb3J5MTcx"),
    ("signal171stream171", "c2lnbmFsMTcxc3RyZWFtMTcx"),
    ("signal171context171", "c2lnbmFsMTcxY29udGV4dDE3MQ"),
    ("packet171context171", "cGFja2V0MTcxY29udGV4dDE3MQ"),
    ("packet171knowledge171", "cGFja2V0MTcxa25vd2xlZGdlMTcx"),
    ("packet171vector171", "cGFja2V0MTcxdmVjdG9yMTcx"),
    ("packet171processor171", "cGFja2V0MTcxcHJvY2Vzc29yMTcx"),
    ("router171processor171", "cm91dGVyMTcxcHJvY2Vzc29yMTcx"),
    ("router171reasoning171", "cm91dGVyMTcxcmVhc29uaW5nMTcx"),
    ("router171machine171", "cm91dGVyMTcxbWFjaGluZTE3MQ"),
    ("router171learning171", "cm91dGVyMTcxbGVhcm5pbmcxNzE"),
    ("cluster171learning171", "Y2x1c3RlcjE3MWxlYXJuaW5nMTcx"),
    ("cluster171model171", "Y2x1c3RlcjE3MW1vZGVsMTcx"),
    ("cluster171token171", "Y2x1c3RlcjE3MXRva2VuMTcx"),
    ("cluster171prompt171", "Y2x1c3RlcjE3MXByb21wdDE3MQ"),
    ("mirror171prompt171", "bWlycm9yMTcxcHJvbXB0MTcx"),
    ("mirror171session171", "bWlycm9yMTcxc2Vzc2lvbjE3MQ"),
    ("mirror171library171", "bWlycm9yMTcxbGlicmFyeTE3MQ"),
    ("mirror171service171", "bWlycm9yMTcxc2VydmljZTE3MQ"),
    ("filter171service171", "ZmlsdGVyMTcxc2VydmljZTE3MQ"),
    ("filter171gateway171", "ZmlsdGVyMTcxZ2F0ZXdheTE3MQ"),
    ("filter171storage171", "ZmlsdGVyMTcxc3RvcmFnZTE3MQ"),
    ("filter171network171", "ZmlsdGVyMTcxbmV0d29yazE3MQ"),
    ("ranking171network171", "cmFua2luZzE3MW5ldHdvcmsxNzE"),
    ("ranking171latency171", "cmFua2luZzE3MWxhdGVuY3kxNzE"),
    ("ranking171buffer171", "cmFua2luZzE3MWJ1ZmZlcjE3MQ"),
    ("ranking171queue171", "cmFua2luZzE3MXF1ZXVlMTcx"),
    ("encoding171queue171", "ZW5jb2RpbmcxNzFxdWV1ZTE3MQ"),
    ("encoding171worker171", "ZW5jb2RpbmcxNzF3b3JrZXIxNzE"),
    ("encoding171kernel171", "ZW5jb2RpbmcxNzFrZXJuZWwxNzE"),
    ("encoding171signal171", "ZW5jb2RpbmcxNzFzaWduYWwxNzE"),
    ("mapping171signal171", "bWFwcGluZzE3MXNpZ25hbDE3MQ"),
    ("mapping171packet171", "bWFwcGluZzE3MXBhY2tldDE3MQ"),
    ("mapping171router171", "bWFwcGluZzE3MXJvdXRlcjE3MQ"),
    ("mapping171cluster171", "bWFwcGluZzE3MWNsdXN0ZXIxNzE"),
    ("record171cluster171", "cmVjb3JkMTcxY2x1c3RlcjE3MQ"),
    ("record171mirror171", "cmVjb3JkMTcxbWlycm9yMTcx"),
    ("record171filter171", "cmVjb3JkMTcxZmlsdGVyMTcx"),
    ("record171ranking171", "cmVjb3JkMTcxcmFua2luZzE3MQ"),
    ("candle171ranking171", "Y2FuZGxlMTcxcmFua2luZzE3MQ"),
    ("candle171encoding171", "Y2FuZGxlMTcxZW5jb2RpbmcxNzE"),
    ("candle171mapping171", "Y2FuZGxlMTcxbWFwcGluZzE3MQ"),
    ("candle171record171", "Y2FuZGxlMTcxcmVjb3JkMTcx"),
    ("thread171record171", "dGhyZWFkMTcxcmVjb3JkMTcx"),
    ("thread171candle171", "dGhyZWFkMTcxY2FuZGxlMTcx"),
    ("thread171thread171", "dGhyZWFkMTcxdGhyZWFkMTcx"),
    ("thread171kitten171", "dGhyZWFkMTcxa2l0dGVuMTcx"),
    (
        "round 171: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTcxOiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 171: agentuniverse is a framework for multi agents",
        "cm91bmQgMTcxOiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 171: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTcxOiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 171: the processor reads the record then stops",
        "cm91bmQgMTcxOiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 171: a worker pulls the next task from the queue",
        "cm91bmQgMTcxOiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 171: signals travel through the network layer",
        "cm91bmQgMTcxOiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 171: the gateway routes each request by policy",
        "cm91bmQgMTcxOiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 171: memory grows until the buffer is full",
        "cm91bmQgMTcxOiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 171: the cluster mirrors every packet twice",
        "cm91bmQgMTcxOiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 171: ranking uses tokens learned from the corpus",
        "cm91bmQgMTcxOiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 171: a long session ends when the candle dies",
        "cm91bmQgMTcxOiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 171: encode the prompt then map the result",
        "cm91bmQgMTcxOiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 171: the kernel wakes the worker at dawn",
        "cm91bmQgMTcxOiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 171: service latency drops after the patch",
        "cm91bmQgMTcxOiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 171: the library caches every vector it sees",
        "cm91bmQgMTcxOiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 171: agents argue then the debate resolves",
        "cm91bmQgMTcxOiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 171: the filter keeps only strong matches",
        "cm91bmQgMTcxOiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 171: the model answers with a short reply",
        "cm91bmQgMTcxOiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 171: the recorder stores the reasoning trace",
        "cm91bmQgMTcxOiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 171: the angel watches the processor run",
        "cm91bmQgMTcxOiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 171: angle of the vector decides the match",
        "cm91bmQgMTcxOiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 171: the candle burns twice as long at night",
        "cm91bmQgMTcxOiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 171: a mirror of the universe in one line",
        "cm91bmQgMTcxOiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 171: the queue drains before the storm", "cm91bmQgMTcxOiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
