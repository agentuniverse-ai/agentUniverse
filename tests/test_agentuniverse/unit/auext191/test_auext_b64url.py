"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten191kitten191", "a2l0dGVuMTkxa2l0dGVuMTkx"),
    ("kitten191sitting191", "a2l0dGVuMTkxc2l0dGluZzE5MQ"),
    ("kitten191agent191", "a2l0dGVuMTkxYWdlbnQxOTE"),
    ("kitten191angle191", "a2l0dGVuMTkxYW5nbGUxOTE"),
    ("sitting191angle191", "c2l0dGluZzE5MWFuZ2xlMTkx"),
    ("sitting191universe191", "c2l0dGluZzE5MXVuaXZlcnNlMTkx"),
    ("sitting191memory191", "c2l0dGluZzE5MW1lbW9yeTE5MQ"),
    ("sitting191stream191", "c2l0dGluZzE5MXN0cmVhbTE5MQ"),
    ("agent191stream191", "YWdlbnQxOTFzdHJlYW0xOTE"),
    ("agent191context191", "YWdlbnQxOTFjb250ZXh0MTkx"),
    ("agent191knowledge191", "YWdlbnQxOTFrbm93bGVkZ2UxOTE"),
    ("agent191vector191", "YWdlbnQxOTF2ZWN0b3IxOTE"),
    ("angle191vector191", "YW5nbGUxOTF2ZWN0b3IxOTE"),
    ("angle191processor191", "YW5nbGUxOTFwcm9jZXNzb3IxOTE"),
    ("angle191reasoning191", "YW5nbGUxOTFyZWFzb25pbmcxOTE"),
    ("angle191machine191", "YW5nbGUxOTFtYWNoaW5lMTkx"),
    ("universe191machine191", "dW5pdmVyc2UxOTFtYWNoaW5lMTkx"),
    ("universe191learning191", "dW5pdmVyc2UxOTFsZWFybmluZzE5MQ"),
    ("universe191model191", "dW5pdmVyc2UxOTFtb2RlbDE5MQ"),
    ("universe191token191", "dW5pdmVyc2UxOTF0b2tlbjE5MQ"),
    ("memory191token191", "bWVtb3J5MTkxdG9rZW4xOTE"),
    ("memory191prompt191", "bWVtb3J5MTkxcHJvbXB0MTkx"),
    ("memory191session191", "bWVtb3J5MTkxc2Vzc2lvbjE5MQ"),
    ("memory191library191", "bWVtb3J5MTkxbGlicmFyeTE5MQ"),
    ("stream191library191", "c3RyZWFtMTkxbGlicmFyeTE5MQ"),
    ("stream191service191", "c3RyZWFtMTkxc2VydmljZTE5MQ"),
    ("stream191gateway191", "c3RyZWFtMTkxZ2F0ZXdheTE5MQ"),
    ("stream191storage191", "c3RyZWFtMTkxc3RvcmFnZTE5MQ"),
    ("context191storage191", "Y29udGV4dDE5MXN0b3JhZ2UxOTE"),
    ("context191network191", "Y29udGV4dDE5MW5ldHdvcmsxOTE"),
    ("context191latency191", "Y29udGV4dDE5MWxhdGVuY3kxOTE"),
    ("context191buffer191", "Y29udGV4dDE5MWJ1ZmZlcjE5MQ"),
    ("knowledge191buffer191", "a25vd2xlZGdlMTkxYnVmZmVyMTkx"),
    ("knowledge191queue191", "a25vd2xlZGdlMTkxcXVldWUxOTE"),
    ("knowledge191worker191", "a25vd2xlZGdlMTkxd29ya2VyMTkx"),
    ("knowledge191kernel191", "a25vd2xlZGdlMTkxa2VybmVsMTkx"),
    ("vector191kernel191", "dmVjdG9yMTkxa2VybmVsMTkx"),
    ("vector191signal191", "dmVjdG9yMTkxc2lnbmFsMTkx"),
    ("vector191packet191", "dmVjdG9yMTkxcGFja2V0MTkx"),
    ("vector191router191", "dmVjdG9yMTkxcm91dGVyMTkx"),
    ("processor191router191", "cHJvY2Vzc29yMTkxcm91dGVyMTkx"),
    ("processor191cluster191", "cHJvY2Vzc29yMTkxY2x1c3RlcjE5MQ"),
    ("processor191mirror191", "cHJvY2Vzc29yMTkxbWlycm9yMTkx"),
    ("processor191filter191", "cHJvY2Vzc29yMTkxZmlsdGVyMTkx"),
    ("reasoning191filter191", "cmVhc29uaW5nMTkxZmlsdGVyMTkx"),
    ("reasoning191ranking191", "cmVhc29uaW5nMTkxcmFua2luZzE5MQ"),
    ("reasoning191encoding191", "cmVhc29uaW5nMTkxZW5jb2RpbmcxOTE"),
    ("reasoning191mapping191", "cmVhc29uaW5nMTkxbWFwcGluZzE5MQ"),
    ("machine191mapping191", "bWFjaGluZTE5MW1hcHBpbmcxOTE"),
    ("machine191record191", "bWFjaGluZTE5MXJlY29yZDE5MQ"),
    ("machine191candle191", "bWFjaGluZTE5MWNhbmRsZTE5MQ"),
    ("machine191thread191", "bWFjaGluZTE5MXRocmVhZDE5MQ"),
    ("learning191thread191", "bGVhcm5pbmcxOTF0aHJlYWQxOTE"),
    ("learning191kitten191", "bGVhcm5pbmcxOTFraXR0ZW4xOTE"),
    ("learning191sitting191", "bGVhcm5pbmcxOTFzaXR0aW5nMTkx"),
    ("learning191agent191", "bGVhcm5pbmcxOTFhZ2VudDE5MQ"),
    ("model191agent191", "bW9kZWwxOTFhZ2VudDE5MQ"),
    ("model191angle191", "bW9kZWwxOTFhbmdsZTE5MQ"),
    ("model191universe191", "bW9kZWwxOTF1bml2ZXJzZTE5MQ"),
    ("model191memory191", "bW9kZWwxOTFtZW1vcnkxOTE"),
    ("token191memory191", "dG9rZW4xOTFtZW1vcnkxOTE"),
    ("token191stream191", "dG9rZW4xOTFzdHJlYW0xOTE"),
    ("token191context191", "dG9rZW4xOTFjb250ZXh0MTkx"),
    ("token191knowledge191", "dG9rZW4xOTFrbm93bGVkZ2UxOTE"),
    ("prompt191knowledge191", "cHJvbXB0MTkxa25vd2xlZGdlMTkx"),
    ("prompt191vector191", "cHJvbXB0MTkxdmVjdG9yMTkx"),
    ("prompt191processor191", "cHJvbXB0MTkxcHJvY2Vzc29yMTkx"),
    ("prompt191reasoning191", "cHJvbXB0MTkxcmVhc29uaW5nMTkx"),
    ("session191reasoning191", "c2Vzc2lvbjE5MXJlYXNvbmluZzE5MQ"),
    ("session191machine191", "c2Vzc2lvbjE5MW1hY2hpbmUxOTE"),
    ("session191learning191", "c2Vzc2lvbjE5MWxlYXJuaW5nMTkx"),
    ("session191model191", "c2Vzc2lvbjE5MW1vZGVsMTkx"),
    ("library191model191", "bGlicmFyeTE5MW1vZGVsMTkx"),
    ("library191token191", "bGlicmFyeTE5MXRva2VuMTkx"),
    ("library191prompt191", "bGlicmFyeTE5MXByb21wdDE5MQ"),
    ("library191session191", "bGlicmFyeTE5MXNlc3Npb24xOTE"),
    ("service191session191", "c2VydmljZTE5MXNlc3Npb24xOTE"),
    ("service191library191", "c2VydmljZTE5MWxpYnJhcnkxOTE"),
    ("service191service191", "c2VydmljZTE5MXNlcnZpY2UxOTE"),
    ("service191gateway191", "c2VydmljZTE5MWdhdGV3YXkxOTE"),
    ("gateway191gateway191", "Z2F0ZXdheTE5MWdhdGV3YXkxOTE"),
    ("gateway191storage191", "Z2F0ZXdheTE5MXN0b3JhZ2UxOTE"),
    ("gateway191network191", "Z2F0ZXdheTE5MW5ldHdvcmsxOTE"),
    ("gateway191latency191", "Z2F0ZXdheTE5MWxhdGVuY3kxOTE"),
    ("storage191latency191", "c3RvcmFnZTE5MWxhdGVuY3kxOTE"),
    ("storage191buffer191", "c3RvcmFnZTE5MWJ1ZmZlcjE5MQ"),
    ("storage191queue191", "c3RvcmFnZTE5MXF1ZXVlMTkx"),
    ("storage191worker191", "c3RvcmFnZTE5MXdvcmtlcjE5MQ"),
    ("network191worker191", "bmV0d29yazE5MXdvcmtlcjE5MQ"),
    ("network191kernel191", "bmV0d29yazE5MWtlcm5lbDE5MQ"),
    ("network191signal191", "bmV0d29yazE5MXNpZ25hbDE5MQ"),
    ("network191packet191", "bmV0d29yazE5MXBhY2tldDE5MQ"),
    ("latency191packet191", "bGF0ZW5jeTE5MXBhY2tldDE5MQ"),
    ("latency191router191", "bGF0ZW5jeTE5MXJvdXRlcjE5MQ"),
    ("latency191cluster191", "bGF0ZW5jeTE5MWNsdXN0ZXIxOTE"),
    ("latency191mirror191", "bGF0ZW5jeTE5MW1pcnJvcjE5MQ"),
    ("buffer191mirror191", "YnVmZmVyMTkxbWlycm9yMTkx"),
    ("buffer191filter191", "YnVmZmVyMTkxZmlsdGVyMTkx"),
    ("buffer191ranking191", "YnVmZmVyMTkxcmFua2luZzE5MQ"),
    ("buffer191encoding191", "YnVmZmVyMTkxZW5jb2RpbmcxOTE"),
    ("queue191encoding191", "cXVldWUxOTFlbmNvZGluZzE5MQ"),
    ("queue191mapping191", "cXVldWUxOTFtYXBwaW5nMTkx"),
    ("queue191record191", "cXVldWUxOTFyZWNvcmQxOTE"),
    ("queue191candle191", "cXVldWUxOTFjYW5kbGUxOTE"),
    ("worker191candle191", "d29ya2VyMTkxY2FuZGxlMTkx"),
    ("worker191thread191", "d29ya2VyMTkxdGhyZWFkMTkx"),
    ("worker191kitten191", "d29ya2VyMTkxa2l0dGVuMTkx"),
    ("worker191sitting191", "d29ya2VyMTkxc2l0dGluZzE5MQ"),
    ("kernel191sitting191", "a2VybmVsMTkxc2l0dGluZzE5MQ"),
    ("kernel191agent191", "a2VybmVsMTkxYWdlbnQxOTE"),
    ("kernel191angle191", "a2VybmVsMTkxYW5nbGUxOTE"),
    ("kernel191universe191", "a2VybmVsMTkxdW5pdmVyc2UxOTE"),
    ("signal191universe191", "c2lnbmFsMTkxdW5pdmVyc2UxOTE"),
    ("signal191memory191", "c2lnbmFsMTkxbWVtb3J5MTkx"),
    ("signal191stream191", "c2lnbmFsMTkxc3RyZWFtMTkx"),
    ("signal191context191", "c2lnbmFsMTkxY29udGV4dDE5MQ"),
    ("packet191context191", "cGFja2V0MTkxY29udGV4dDE5MQ"),
    ("packet191knowledge191", "cGFja2V0MTkxa25vd2xlZGdlMTkx"),
    ("packet191vector191", "cGFja2V0MTkxdmVjdG9yMTkx"),
    ("packet191processor191", "cGFja2V0MTkxcHJvY2Vzc29yMTkx"),
    ("router191processor191", "cm91dGVyMTkxcHJvY2Vzc29yMTkx"),
    ("router191reasoning191", "cm91dGVyMTkxcmVhc29uaW5nMTkx"),
    ("router191machine191", "cm91dGVyMTkxbWFjaGluZTE5MQ"),
    ("router191learning191", "cm91dGVyMTkxbGVhcm5pbmcxOTE"),
    ("cluster191learning191", "Y2x1c3RlcjE5MWxlYXJuaW5nMTkx"),
    ("cluster191model191", "Y2x1c3RlcjE5MW1vZGVsMTkx"),
    ("cluster191token191", "Y2x1c3RlcjE5MXRva2VuMTkx"),
    ("cluster191prompt191", "Y2x1c3RlcjE5MXByb21wdDE5MQ"),
    ("mirror191prompt191", "bWlycm9yMTkxcHJvbXB0MTkx"),
    ("mirror191session191", "bWlycm9yMTkxc2Vzc2lvbjE5MQ"),
    ("mirror191library191", "bWlycm9yMTkxbGlicmFyeTE5MQ"),
    ("mirror191service191", "bWlycm9yMTkxc2VydmljZTE5MQ"),
    ("filter191service191", "ZmlsdGVyMTkxc2VydmljZTE5MQ"),
    ("filter191gateway191", "ZmlsdGVyMTkxZ2F0ZXdheTE5MQ"),
    ("filter191storage191", "ZmlsdGVyMTkxc3RvcmFnZTE5MQ"),
    ("filter191network191", "ZmlsdGVyMTkxbmV0d29yazE5MQ"),
    ("ranking191network191", "cmFua2luZzE5MW5ldHdvcmsxOTE"),
    ("ranking191latency191", "cmFua2luZzE5MWxhdGVuY3kxOTE"),
    ("ranking191buffer191", "cmFua2luZzE5MWJ1ZmZlcjE5MQ"),
    ("ranking191queue191", "cmFua2luZzE5MXF1ZXVlMTkx"),
    ("encoding191queue191", "ZW5jb2RpbmcxOTFxdWV1ZTE5MQ"),
    ("encoding191worker191", "ZW5jb2RpbmcxOTF3b3JrZXIxOTE"),
    ("encoding191kernel191", "ZW5jb2RpbmcxOTFrZXJuZWwxOTE"),
    ("encoding191signal191", "ZW5jb2RpbmcxOTFzaWduYWwxOTE"),
    ("mapping191signal191", "bWFwcGluZzE5MXNpZ25hbDE5MQ"),
    ("mapping191packet191", "bWFwcGluZzE5MXBhY2tldDE5MQ"),
    ("mapping191router191", "bWFwcGluZzE5MXJvdXRlcjE5MQ"),
    ("mapping191cluster191", "bWFwcGluZzE5MWNsdXN0ZXIxOTE"),
    ("record191cluster191", "cmVjb3JkMTkxY2x1c3RlcjE5MQ"),
    ("record191mirror191", "cmVjb3JkMTkxbWlycm9yMTkx"),
    ("record191filter191", "cmVjb3JkMTkxZmlsdGVyMTkx"),
    ("record191ranking191", "cmVjb3JkMTkxcmFua2luZzE5MQ"),
    ("candle191ranking191", "Y2FuZGxlMTkxcmFua2luZzE5MQ"),
    ("candle191encoding191", "Y2FuZGxlMTkxZW5jb2RpbmcxOTE"),
    ("candle191mapping191", "Y2FuZGxlMTkxbWFwcGluZzE5MQ"),
    ("candle191record191", "Y2FuZGxlMTkxcmVjb3JkMTkx"),
    ("thread191record191", "dGhyZWFkMTkxcmVjb3JkMTkx"),
    ("thread191candle191", "dGhyZWFkMTkxY2FuZGxlMTkx"),
    ("thread191thread191", "dGhyZWFkMTkxdGhyZWFkMTkx"),
    ("thread191kitten191", "dGhyZWFkMTkxa2l0dGVuMTkx"),
    (
        "round 191: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTkxOiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 191: agentuniverse is a framework for multi agents",
        "cm91bmQgMTkxOiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 191: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTkxOiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 191: the processor reads the record then stops",
        "cm91bmQgMTkxOiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 191: a worker pulls the next task from the queue",
        "cm91bmQgMTkxOiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 191: signals travel through the network layer",
        "cm91bmQgMTkxOiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 191: the gateway routes each request by policy",
        "cm91bmQgMTkxOiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 191: memory grows until the buffer is full",
        "cm91bmQgMTkxOiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 191: the cluster mirrors every packet twice",
        "cm91bmQgMTkxOiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 191: ranking uses tokens learned from the corpus",
        "cm91bmQgMTkxOiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 191: a long session ends when the candle dies",
        "cm91bmQgMTkxOiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 191: encode the prompt then map the result",
        "cm91bmQgMTkxOiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 191: the kernel wakes the worker at dawn",
        "cm91bmQgMTkxOiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 191: service latency drops after the patch",
        "cm91bmQgMTkxOiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 191: the library caches every vector it sees",
        "cm91bmQgMTkxOiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 191: agents argue then the debate resolves",
        "cm91bmQgMTkxOiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 191: the filter keeps only strong matches",
        "cm91bmQgMTkxOiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 191: the model answers with a short reply",
        "cm91bmQgMTkxOiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 191: the recorder stores the reasoning trace",
        "cm91bmQgMTkxOiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 191: the angel watches the processor run",
        "cm91bmQgMTkxOiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 191: angle of the vector decides the match",
        "cm91bmQgMTkxOiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 191: the candle burns twice as long at night",
        "cm91bmQgMTkxOiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 191: a mirror of the universe in one line",
        "cm91bmQgMTkxOiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 191: the queue drains before the storm", "cm91bmQgMTkxOiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
