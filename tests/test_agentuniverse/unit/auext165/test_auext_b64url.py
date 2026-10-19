"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten165kitten165", "a2l0dGVuMTY1a2l0dGVuMTY1"),
    ("kitten165sitting165", "a2l0dGVuMTY1c2l0dGluZzE2NQ"),
    ("kitten165agent165", "a2l0dGVuMTY1YWdlbnQxNjU"),
    ("kitten165angle165", "a2l0dGVuMTY1YW5nbGUxNjU"),
    ("sitting165angle165", "c2l0dGluZzE2NWFuZ2xlMTY1"),
    ("sitting165universe165", "c2l0dGluZzE2NXVuaXZlcnNlMTY1"),
    ("sitting165memory165", "c2l0dGluZzE2NW1lbW9yeTE2NQ"),
    ("sitting165stream165", "c2l0dGluZzE2NXN0cmVhbTE2NQ"),
    ("agent165stream165", "YWdlbnQxNjVzdHJlYW0xNjU"),
    ("agent165context165", "YWdlbnQxNjVjb250ZXh0MTY1"),
    ("agent165knowledge165", "YWdlbnQxNjVrbm93bGVkZ2UxNjU"),
    ("agent165vector165", "YWdlbnQxNjV2ZWN0b3IxNjU"),
    ("angle165vector165", "YW5nbGUxNjV2ZWN0b3IxNjU"),
    ("angle165processor165", "YW5nbGUxNjVwcm9jZXNzb3IxNjU"),
    ("angle165reasoning165", "YW5nbGUxNjVyZWFzb25pbmcxNjU"),
    ("angle165machine165", "YW5nbGUxNjVtYWNoaW5lMTY1"),
    ("universe165machine165", "dW5pdmVyc2UxNjVtYWNoaW5lMTY1"),
    ("universe165learning165", "dW5pdmVyc2UxNjVsZWFybmluZzE2NQ"),
    ("universe165model165", "dW5pdmVyc2UxNjVtb2RlbDE2NQ"),
    ("universe165token165", "dW5pdmVyc2UxNjV0b2tlbjE2NQ"),
    ("memory165token165", "bWVtb3J5MTY1dG9rZW4xNjU"),
    ("memory165prompt165", "bWVtb3J5MTY1cHJvbXB0MTY1"),
    ("memory165session165", "bWVtb3J5MTY1c2Vzc2lvbjE2NQ"),
    ("memory165library165", "bWVtb3J5MTY1bGlicmFyeTE2NQ"),
    ("stream165library165", "c3RyZWFtMTY1bGlicmFyeTE2NQ"),
    ("stream165service165", "c3RyZWFtMTY1c2VydmljZTE2NQ"),
    ("stream165gateway165", "c3RyZWFtMTY1Z2F0ZXdheTE2NQ"),
    ("stream165storage165", "c3RyZWFtMTY1c3RvcmFnZTE2NQ"),
    ("context165storage165", "Y29udGV4dDE2NXN0b3JhZ2UxNjU"),
    ("context165network165", "Y29udGV4dDE2NW5ldHdvcmsxNjU"),
    ("context165latency165", "Y29udGV4dDE2NWxhdGVuY3kxNjU"),
    ("context165buffer165", "Y29udGV4dDE2NWJ1ZmZlcjE2NQ"),
    ("knowledge165buffer165", "a25vd2xlZGdlMTY1YnVmZmVyMTY1"),
    ("knowledge165queue165", "a25vd2xlZGdlMTY1cXVldWUxNjU"),
    ("knowledge165worker165", "a25vd2xlZGdlMTY1d29ya2VyMTY1"),
    ("knowledge165kernel165", "a25vd2xlZGdlMTY1a2VybmVsMTY1"),
    ("vector165kernel165", "dmVjdG9yMTY1a2VybmVsMTY1"),
    ("vector165signal165", "dmVjdG9yMTY1c2lnbmFsMTY1"),
    ("vector165packet165", "dmVjdG9yMTY1cGFja2V0MTY1"),
    ("vector165router165", "dmVjdG9yMTY1cm91dGVyMTY1"),
    ("processor165router165", "cHJvY2Vzc29yMTY1cm91dGVyMTY1"),
    ("processor165cluster165", "cHJvY2Vzc29yMTY1Y2x1c3RlcjE2NQ"),
    ("processor165mirror165", "cHJvY2Vzc29yMTY1bWlycm9yMTY1"),
    ("processor165filter165", "cHJvY2Vzc29yMTY1ZmlsdGVyMTY1"),
    ("reasoning165filter165", "cmVhc29uaW5nMTY1ZmlsdGVyMTY1"),
    ("reasoning165ranking165", "cmVhc29uaW5nMTY1cmFua2luZzE2NQ"),
    ("reasoning165encoding165", "cmVhc29uaW5nMTY1ZW5jb2RpbmcxNjU"),
    ("reasoning165mapping165", "cmVhc29uaW5nMTY1bWFwcGluZzE2NQ"),
    ("machine165mapping165", "bWFjaGluZTE2NW1hcHBpbmcxNjU"),
    ("machine165record165", "bWFjaGluZTE2NXJlY29yZDE2NQ"),
    ("machine165candle165", "bWFjaGluZTE2NWNhbmRsZTE2NQ"),
    ("machine165thread165", "bWFjaGluZTE2NXRocmVhZDE2NQ"),
    ("learning165thread165", "bGVhcm5pbmcxNjV0aHJlYWQxNjU"),
    ("learning165kitten165", "bGVhcm5pbmcxNjVraXR0ZW4xNjU"),
    ("learning165sitting165", "bGVhcm5pbmcxNjVzaXR0aW5nMTY1"),
    ("learning165agent165", "bGVhcm5pbmcxNjVhZ2VudDE2NQ"),
    ("model165agent165", "bW9kZWwxNjVhZ2VudDE2NQ"),
    ("model165angle165", "bW9kZWwxNjVhbmdsZTE2NQ"),
    ("model165universe165", "bW9kZWwxNjV1bml2ZXJzZTE2NQ"),
    ("model165memory165", "bW9kZWwxNjVtZW1vcnkxNjU"),
    ("token165memory165", "dG9rZW4xNjVtZW1vcnkxNjU"),
    ("token165stream165", "dG9rZW4xNjVzdHJlYW0xNjU"),
    ("token165context165", "dG9rZW4xNjVjb250ZXh0MTY1"),
    ("token165knowledge165", "dG9rZW4xNjVrbm93bGVkZ2UxNjU"),
    ("prompt165knowledge165", "cHJvbXB0MTY1a25vd2xlZGdlMTY1"),
    ("prompt165vector165", "cHJvbXB0MTY1dmVjdG9yMTY1"),
    ("prompt165processor165", "cHJvbXB0MTY1cHJvY2Vzc29yMTY1"),
    ("prompt165reasoning165", "cHJvbXB0MTY1cmVhc29uaW5nMTY1"),
    ("session165reasoning165", "c2Vzc2lvbjE2NXJlYXNvbmluZzE2NQ"),
    ("session165machine165", "c2Vzc2lvbjE2NW1hY2hpbmUxNjU"),
    ("session165learning165", "c2Vzc2lvbjE2NWxlYXJuaW5nMTY1"),
    ("session165model165", "c2Vzc2lvbjE2NW1vZGVsMTY1"),
    ("library165model165", "bGlicmFyeTE2NW1vZGVsMTY1"),
    ("library165token165", "bGlicmFyeTE2NXRva2VuMTY1"),
    ("library165prompt165", "bGlicmFyeTE2NXByb21wdDE2NQ"),
    ("library165session165", "bGlicmFyeTE2NXNlc3Npb24xNjU"),
    ("service165session165", "c2VydmljZTE2NXNlc3Npb24xNjU"),
    ("service165library165", "c2VydmljZTE2NWxpYnJhcnkxNjU"),
    ("service165service165", "c2VydmljZTE2NXNlcnZpY2UxNjU"),
    ("service165gateway165", "c2VydmljZTE2NWdhdGV3YXkxNjU"),
    ("gateway165gateway165", "Z2F0ZXdheTE2NWdhdGV3YXkxNjU"),
    ("gateway165storage165", "Z2F0ZXdheTE2NXN0b3JhZ2UxNjU"),
    ("gateway165network165", "Z2F0ZXdheTE2NW5ldHdvcmsxNjU"),
    ("gateway165latency165", "Z2F0ZXdheTE2NWxhdGVuY3kxNjU"),
    ("storage165latency165", "c3RvcmFnZTE2NWxhdGVuY3kxNjU"),
    ("storage165buffer165", "c3RvcmFnZTE2NWJ1ZmZlcjE2NQ"),
    ("storage165queue165", "c3RvcmFnZTE2NXF1ZXVlMTY1"),
    ("storage165worker165", "c3RvcmFnZTE2NXdvcmtlcjE2NQ"),
    ("network165worker165", "bmV0d29yazE2NXdvcmtlcjE2NQ"),
    ("network165kernel165", "bmV0d29yazE2NWtlcm5lbDE2NQ"),
    ("network165signal165", "bmV0d29yazE2NXNpZ25hbDE2NQ"),
    ("network165packet165", "bmV0d29yazE2NXBhY2tldDE2NQ"),
    ("latency165packet165", "bGF0ZW5jeTE2NXBhY2tldDE2NQ"),
    ("latency165router165", "bGF0ZW5jeTE2NXJvdXRlcjE2NQ"),
    ("latency165cluster165", "bGF0ZW5jeTE2NWNsdXN0ZXIxNjU"),
    ("latency165mirror165", "bGF0ZW5jeTE2NW1pcnJvcjE2NQ"),
    ("buffer165mirror165", "YnVmZmVyMTY1bWlycm9yMTY1"),
    ("buffer165filter165", "YnVmZmVyMTY1ZmlsdGVyMTY1"),
    ("buffer165ranking165", "YnVmZmVyMTY1cmFua2luZzE2NQ"),
    ("buffer165encoding165", "YnVmZmVyMTY1ZW5jb2RpbmcxNjU"),
    ("queue165encoding165", "cXVldWUxNjVlbmNvZGluZzE2NQ"),
    ("queue165mapping165", "cXVldWUxNjVtYXBwaW5nMTY1"),
    ("queue165record165", "cXVldWUxNjVyZWNvcmQxNjU"),
    ("queue165candle165", "cXVldWUxNjVjYW5kbGUxNjU"),
    ("worker165candle165", "d29ya2VyMTY1Y2FuZGxlMTY1"),
    ("worker165thread165", "d29ya2VyMTY1dGhyZWFkMTY1"),
    ("worker165kitten165", "d29ya2VyMTY1a2l0dGVuMTY1"),
    ("worker165sitting165", "d29ya2VyMTY1c2l0dGluZzE2NQ"),
    ("kernel165sitting165", "a2VybmVsMTY1c2l0dGluZzE2NQ"),
    ("kernel165agent165", "a2VybmVsMTY1YWdlbnQxNjU"),
    ("kernel165angle165", "a2VybmVsMTY1YW5nbGUxNjU"),
    ("kernel165universe165", "a2VybmVsMTY1dW5pdmVyc2UxNjU"),
    ("signal165universe165", "c2lnbmFsMTY1dW5pdmVyc2UxNjU"),
    ("signal165memory165", "c2lnbmFsMTY1bWVtb3J5MTY1"),
    ("signal165stream165", "c2lnbmFsMTY1c3RyZWFtMTY1"),
    ("signal165context165", "c2lnbmFsMTY1Y29udGV4dDE2NQ"),
    ("packet165context165", "cGFja2V0MTY1Y29udGV4dDE2NQ"),
    ("packet165knowledge165", "cGFja2V0MTY1a25vd2xlZGdlMTY1"),
    ("packet165vector165", "cGFja2V0MTY1dmVjdG9yMTY1"),
    ("packet165processor165", "cGFja2V0MTY1cHJvY2Vzc29yMTY1"),
    ("router165processor165", "cm91dGVyMTY1cHJvY2Vzc29yMTY1"),
    ("router165reasoning165", "cm91dGVyMTY1cmVhc29uaW5nMTY1"),
    ("router165machine165", "cm91dGVyMTY1bWFjaGluZTE2NQ"),
    ("router165learning165", "cm91dGVyMTY1bGVhcm5pbmcxNjU"),
    ("cluster165learning165", "Y2x1c3RlcjE2NWxlYXJuaW5nMTY1"),
    ("cluster165model165", "Y2x1c3RlcjE2NW1vZGVsMTY1"),
    ("cluster165token165", "Y2x1c3RlcjE2NXRva2VuMTY1"),
    ("cluster165prompt165", "Y2x1c3RlcjE2NXByb21wdDE2NQ"),
    ("mirror165prompt165", "bWlycm9yMTY1cHJvbXB0MTY1"),
    ("mirror165session165", "bWlycm9yMTY1c2Vzc2lvbjE2NQ"),
    ("mirror165library165", "bWlycm9yMTY1bGlicmFyeTE2NQ"),
    ("mirror165service165", "bWlycm9yMTY1c2VydmljZTE2NQ"),
    ("filter165service165", "ZmlsdGVyMTY1c2VydmljZTE2NQ"),
    ("filter165gateway165", "ZmlsdGVyMTY1Z2F0ZXdheTE2NQ"),
    ("filter165storage165", "ZmlsdGVyMTY1c3RvcmFnZTE2NQ"),
    ("filter165network165", "ZmlsdGVyMTY1bmV0d29yazE2NQ"),
    ("ranking165network165", "cmFua2luZzE2NW5ldHdvcmsxNjU"),
    ("ranking165latency165", "cmFua2luZzE2NWxhdGVuY3kxNjU"),
    ("ranking165buffer165", "cmFua2luZzE2NWJ1ZmZlcjE2NQ"),
    ("ranking165queue165", "cmFua2luZzE2NXF1ZXVlMTY1"),
    ("encoding165queue165", "ZW5jb2RpbmcxNjVxdWV1ZTE2NQ"),
    ("encoding165worker165", "ZW5jb2RpbmcxNjV3b3JrZXIxNjU"),
    ("encoding165kernel165", "ZW5jb2RpbmcxNjVrZXJuZWwxNjU"),
    ("encoding165signal165", "ZW5jb2RpbmcxNjVzaWduYWwxNjU"),
    ("mapping165signal165", "bWFwcGluZzE2NXNpZ25hbDE2NQ"),
    ("mapping165packet165", "bWFwcGluZzE2NXBhY2tldDE2NQ"),
    ("mapping165router165", "bWFwcGluZzE2NXJvdXRlcjE2NQ"),
    ("mapping165cluster165", "bWFwcGluZzE2NWNsdXN0ZXIxNjU"),
    ("record165cluster165", "cmVjb3JkMTY1Y2x1c3RlcjE2NQ"),
    ("record165mirror165", "cmVjb3JkMTY1bWlycm9yMTY1"),
    ("record165filter165", "cmVjb3JkMTY1ZmlsdGVyMTY1"),
    ("record165ranking165", "cmVjb3JkMTY1cmFua2luZzE2NQ"),
    ("candle165ranking165", "Y2FuZGxlMTY1cmFua2luZzE2NQ"),
    ("candle165encoding165", "Y2FuZGxlMTY1ZW5jb2RpbmcxNjU"),
    ("candle165mapping165", "Y2FuZGxlMTY1bWFwcGluZzE2NQ"),
    ("candle165record165", "Y2FuZGxlMTY1cmVjb3JkMTY1"),
    ("thread165record165", "dGhyZWFkMTY1cmVjb3JkMTY1"),
    ("thread165candle165", "dGhyZWFkMTY1Y2FuZGxlMTY1"),
    ("thread165thread165", "dGhyZWFkMTY1dGhyZWFkMTY1"),
    ("thread165kitten165", "dGhyZWFkMTY1a2l0dGVuMTY1"),
    (
        "round 165: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTY1OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 165: agentuniverse is a framework for multi agents",
        "cm91bmQgMTY1OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 165: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTY1OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 165: the processor reads the record then stops",
        "cm91bmQgMTY1OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 165: a worker pulls the next task from the queue",
        "cm91bmQgMTY1OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 165: signals travel through the network layer",
        "cm91bmQgMTY1OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 165: the gateway routes each request by policy",
        "cm91bmQgMTY1OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 165: memory grows until the buffer is full",
        "cm91bmQgMTY1OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 165: the cluster mirrors every packet twice",
        "cm91bmQgMTY1OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 165: ranking uses tokens learned from the corpus",
        "cm91bmQgMTY1OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 165: a long session ends when the candle dies",
        "cm91bmQgMTY1OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 165: encode the prompt then map the result",
        "cm91bmQgMTY1OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 165: the kernel wakes the worker at dawn",
        "cm91bmQgMTY1OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 165: service latency drops after the patch",
        "cm91bmQgMTY1OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 165: the library caches every vector it sees",
        "cm91bmQgMTY1OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 165: agents argue then the debate resolves",
        "cm91bmQgMTY1OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 165: the filter keeps only strong matches",
        "cm91bmQgMTY1OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 165: the model answers with a short reply",
        "cm91bmQgMTY1OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 165: the recorder stores the reasoning trace",
        "cm91bmQgMTY1OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 165: the angel watches the processor run",
        "cm91bmQgMTY1OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 165: angle of the vector decides the match",
        "cm91bmQgMTY1OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 165: the candle burns twice as long at night",
        "cm91bmQgMTY1OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 165: a mirror of the universe in one line",
        "cm91bmQgMTY1OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 165: the queue drains before the storm", "cm91bmQgMTY1OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
