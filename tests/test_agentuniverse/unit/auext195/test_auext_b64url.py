"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten195kitten195", "a2l0dGVuMTk1a2l0dGVuMTk1"),
    ("kitten195sitting195", "a2l0dGVuMTk1c2l0dGluZzE5NQ"),
    ("kitten195agent195", "a2l0dGVuMTk1YWdlbnQxOTU"),
    ("kitten195angle195", "a2l0dGVuMTk1YW5nbGUxOTU"),
    ("sitting195angle195", "c2l0dGluZzE5NWFuZ2xlMTk1"),
    ("sitting195universe195", "c2l0dGluZzE5NXVuaXZlcnNlMTk1"),
    ("sitting195memory195", "c2l0dGluZzE5NW1lbW9yeTE5NQ"),
    ("sitting195stream195", "c2l0dGluZzE5NXN0cmVhbTE5NQ"),
    ("agent195stream195", "YWdlbnQxOTVzdHJlYW0xOTU"),
    ("agent195context195", "YWdlbnQxOTVjb250ZXh0MTk1"),
    ("agent195knowledge195", "YWdlbnQxOTVrbm93bGVkZ2UxOTU"),
    ("agent195vector195", "YWdlbnQxOTV2ZWN0b3IxOTU"),
    ("angle195vector195", "YW5nbGUxOTV2ZWN0b3IxOTU"),
    ("angle195processor195", "YW5nbGUxOTVwcm9jZXNzb3IxOTU"),
    ("angle195reasoning195", "YW5nbGUxOTVyZWFzb25pbmcxOTU"),
    ("angle195machine195", "YW5nbGUxOTVtYWNoaW5lMTk1"),
    ("universe195machine195", "dW5pdmVyc2UxOTVtYWNoaW5lMTk1"),
    ("universe195learning195", "dW5pdmVyc2UxOTVsZWFybmluZzE5NQ"),
    ("universe195model195", "dW5pdmVyc2UxOTVtb2RlbDE5NQ"),
    ("universe195token195", "dW5pdmVyc2UxOTV0b2tlbjE5NQ"),
    ("memory195token195", "bWVtb3J5MTk1dG9rZW4xOTU"),
    ("memory195prompt195", "bWVtb3J5MTk1cHJvbXB0MTk1"),
    ("memory195session195", "bWVtb3J5MTk1c2Vzc2lvbjE5NQ"),
    ("memory195library195", "bWVtb3J5MTk1bGlicmFyeTE5NQ"),
    ("stream195library195", "c3RyZWFtMTk1bGlicmFyeTE5NQ"),
    ("stream195service195", "c3RyZWFtMTk1c2VydmljZTE5NQ"),
    ("stream195gateway195", "c3RyZWFtMTk1Z2F0ZXdheTE5NQ"),
    ("stream195storage195", "c3RyZWFtMTk1c3RvcmFnZTE5NQ"),
    ("context195storage195", "Y29udGV4dDE5NXN0b3JhZ2UxOTU"),
    ("context195network195", "Y29udGV4dDE5NW5ldHdvcmsxOTU"),
    ("context195latency195", "Y29udGV4dDE5NWxhdGVuY3kxOTU"),
    ("context195buffer195", "Y29udGV4dDE5NWJ1ZmZlcjE5NQ"),
    ("knowledge195buffer195", "a25vd2xlZGdlMTk1YnVmZmVyMTk1"),
    ("knowledge195queue195", "a25vd2xlZGdlMTk1cXVldWUxOTU"),
    ("knowledge195worker195", "a25vd2xlZGdlMTk1d29ya2VyMTk1"),
    ("knowledge195kernel195", "a25vd2xlZGdlMTk1a2VybmVsMTk1"),
    ("vector195kernel195", "dmVjdG9yMTk1a2VybmVsMTk1"),
    ("vector195signal195", "dmVjdG9yMTk1c2lnbmFsMTk1"),
    ("vector195packet195", "dmVjdG9yMTk1cGFja2V0MTk1"),
    ("vector195router195", "dmVjdG9yMTk1cm91dGVyMTk1"),
    ("processor195router195", "cHJvY2Vzc29yMTk1cm91dGVyMTk1"),
    ("processor195cluster195", "cHJvY2Vzc29yMTk1Y2x1c3RlcjE5NQ"),
    ("processor195mirror195", "cHJvY2Vzc29yMTk1bWlycm9yMTk1"),
    ("processor195filter195", "cHJvY2Vzc29yMTk1ZmlsdGVyMTk1"),
    ("reasoning195filter195", "cmVhc29uaW5nMTk1ZmlsdGVyMTk1"),
    ("reasoning195ranking195", "cmVhc29uaW5nMTk1cmFua2luZzE5NQ"),
    ("reasoning195encoding195", "cmVhc29uaW5nMTk1ZW5jb2RpbmcxOTU"),
    ("reasoning195mapping195", "cmVhc29uaW5nMTk1bWFwcGluZzE5NQ"),
    ("machine195mapping195", "bWFjaGluZTE5NW1hcHBpbmcxOTU"),
    ("machine195record195", "bWFjaGluZTE5NXJlY29yZDE5NQ"),
    ("machine195candle195", "bWFjaGluZTE5NWNhbmRsZTE5NQ"),
    ("machine195thread195", "bWFjaGluZTE5NXRocmVhZDE5NQ"),
    ("learning195thread195", "bGVhcm5pbmcxOTV0aHJlYWQxOTU"),
    ("learning195kitten195", "bGVhcm5pbmcxOTVraXR0ZW4xOTU"),
    ("learning195sitting195", "bGVhcm5pbmcxOTVzaXR0aW5nMTk1"),
    ("learning195agent195", "bGVhcm5pbmcxOTVhZ2VudDE5NQ"),
    ("model195agent195", "bW9kZWwxOTVhZ2VudDE5NQ"),
    ("model195angle195", "bW9kZWwxOTVhbmdsZTE5NQ"),
    ("model195universe195", "bW9kZWwxOTV1bml2ZXJzZTE5NQ"),
    ("model195memory195", "bW9kZWwxOTVtZW1vcnkxOTU"),
    ("token195memory195", "dG9rZW4xOTVtZW1vcnkxOTU"),
    ("token195stream195", "dG9rZW4xOTVzdHJlYW0xOTU"),
    ("token195context195", "dG9rZW4xOTVjb250ZXh0MTk1"),
    ("token195knowledge195", "dG9rZW4xOTVrbm93bGVkZ2UxOTU"),
    ("prompt195knowledge195", "cHJvbXB0MTk1a25vd2xlZGdlMTk1"),
    ("prompt195vector195", "cHJvbXB0MTk1dmVjdG9yMTk1"),
    ("prompt195processor195", "cHJvbXB0MTk1cHJvY2Vzc29yMTk1"),
    ("prompt195reasoning195", "cHJvbXB0MTk1cmVhc29uaW5nMTk1"),
    ("session195reasoning195", "c2Vzc2lvbjE5NXJlYXNvbmluZzE5NQ"),
    ("session195machine195", "c2Vzc2lvbjE5NW1hY2hpbmUxOTU"),
    ("session195learning195", "c2Vzc2lvbjE5NWxlYXJuaW5nMTk1"),
    ("session195model195", "c2Vzc2lvbjE5NW1vZGVsMTk1"),
    ("library195model195", "bGlicmFyeTE5NW1vZGVsMTk1"),
    ("library195token195", "bGlicmFyeTE5NXRva2VuMTk1"),
    ("library195prompt195", "bGlicmFyeTE5NXByb21wdDE5NQ"),
    ("library195session195", "bGlicmFyeTE5NXNlc3Npb24xOTU"),
    ("service195session195", "c2VydmljZTE5NXNlc3Npb24xOTU"),
    ("service195library195", "c2VydmljZTE5NWxpYnJhcnkxOTU"),
    ("service195service195", "c2VydmljZTE5NXNlcnZpY2UxOTU"),
    ("service195gateway195", "c2VydmljZTE5NWdhdGV3YXkxOTU"),
    ("gateway195gateway195", "Z2F0ZXdheTE5NWdhdGV3YXkxOTU"),
    ("gateway195storage195", "Z2F0ZXdheTE5NXN0b3JhZ2UxOTU"),
    ("gateway195network195", "Z2F0ZXdheTE5NW5ldHdvcmsxOTU"),
    ("gateway195latency195", "Z2F0ZXdheTE5NWxhdGVuY3kxOTU"),
    ("storage195latency195", "c3RvcmFnZTE5NWxhdGVuY3kxOTU"),
    ("storage195buffer195", "c3RvcmFnZTE5NWJ1ZmZlcjE5NQ"),
    ("storage195queue195", "c3RvcmFnZTE5NXF1ZXVlMTk1"),
    ("storage195worker195", "c3RvcmFnZTE5NXdvcmtlcjE5NQ"),
    ("network195worker195", "bmV0d29yazE5NXdvcmtlcjE5NQ"),
    ("network195kernel195", "bmV0d29yazE5NWtlcm5lbDE5NQ"),
    ("network195signal195", "bmV0d29yazE5NXNpZ25hbDE5NQ"),
    ("network195packet195", "bmV0d29yazE5NXBhY2tldDE5NQ"),
    ("latency195packet195", "bGF0ZW5jeTE5NXBhY2tldDE5NQ"),
    ("latency195router195", "bGF0ZW5jeTE5NXJvdXRlcjE5NQ"),
    ("latency195cluster195", "bGF0ZW5jeTE5NWNsdXN0ZXIxOTU"),
    ("latency195mirror195", "bGF0ZW5jeTE5NW1pcnJvcjE5NQ"),
    ("buffer195mirror195", "YnVmZmVyMTk1bWlycm9yMTk1"),
    ("buffer195filter195", "YnVmZmVyMTk1ZmlsdGVyMTk1"),
    ("buffer195ranking195", "YnVmZmVyMTk1cmFua2luZzE5NQ"),
    ("buffer195encoding195", "YnVmZmVyMTk1ZW5jb2RpbmcxOTU"),
    ("queue195encoding195", "cXVldWUxOTVlbmNvZGluZzE5NQ"),
    ("queue195mapping195", "cXVldWUxOTVtYXBwaW5nMTk1"),
    ("queue195record195", "cXVldWUxOTVyZWNvcmQxOTU"),
    ("queue195candle195", "cXVldWUxOTVjYW5kbGUxOTU"),
    ("worker195candle195", "d29ya2VyMTk1Y2FuZGxlMTk1"),
    ("worker195thread195", "d29ya2VyMTk1dGhyZWFkMTk1"),
    ("worker195kitten195", "d29ya2VyMTk1a2l0dGVuMTk1"),
    ("worker195sitting195", "d29ya2VyMTk1c2l0dGluZzE5NQ"),
    ("kernel195sitting195", "a2VybmVsMTk1c2l0dGluZzE5NQ"),
    ("kernel195agent195", "a2VybmVsMTk1YWdlbnQxOTU"),
    ("kernel195angle195", "a2VybmVsMTk1YW5nbGUxOTU"),
    ("kernel195universe195", "a2VybmVsMTk1dW5pdmVyc2UxOTU"),
    ("signal195universe195", "c2lnbmFsMTk1dW5pdmVyc2UxOTU"),
    ("signal195memory195", "c2lnbmFsMTk1bWVtb3J5MTk1"),
    ("signal195stream195", "c2lnbmFsMTk1c3RyZWFtMTk1"),
    ("signal195context195", "c2lnbmFsMTk1Y29udGV4dDE5NQ"),
    ("packet195context195", "cGFja2V0MTk1Y29udGV4dDE5NQ"),
    ("packet195knowledge195", "cGFja2V0MTk1a25vd2xlZGdlMTk1"),
    ("packet195vector195", "cGFja2V0MTk1dmVjdG9yMTk1"),
    ("packet195processor195", "cGFja2V0MTk1cHJvY2Vzc29yMTk1"),
    ("router195processor195", "cm91dGVyMTk1cHJvY2Vzc29yMTk1"),
    ("router195reasoning195", "cm91dGVyMTk1cmVhc29uaW5nMTk1"),
    ("router195machine195", "cm91dGVyMTk1bWFjaGluZTE5NQ"),
    ("router195learning195", "cm91dGVyMTk1bGVhcm5pbmcxOTU"),
    ("cluster195learning195", "Y2x1c3RlcjE5NWxlYXJuaW5nMTk1"),
    ("cluster195model195", "Y2x1c3RlcjE5NW1vZGVsMTk1"),
    ("cluster195token195", "Y2x1c3RlcjE5NXRva2VuMTk1"),
    ("cluster195prompt195", "Y2x1c3RlcjE5NXByb21wdDE5NQ"),
    ("mirror195prompt195", "bWlycm9yMTk1cHJvbXB0MTk1"),
    ("mirror195session195", "bWlycm9yMTk1c2Vzc2lvbjE5NQ"),
    ("mirror195library195", "bWlycm9yMTk1bGlicmFyeTE5NQ"),
    ("mirror195service195", "bWlycm9yMTk1c2VydmljZTE5NQ"),
    ("filter195service195", "ZmlsdGVyMTk1c2VydmljZTE5NQ"),
    ("filter195gateway195", "ZmlsdGVyMTk1Z2F0ZXdheTE5NQ"),
    ("filter195storage195", "ZmlsdGVyMTk1c3RvcmFnZTE5NQ"),
    ("filter195network195", "ZmlsdGVyMTk1bmV0d29yazE5NQ"),
    ("ranking195network195", "cmFua2luZzE5NW5ldHdvcmsxOTU"),
    ("ranking195latency195", "cmFua2luZzE5NWxhdGVuY3kxOTU"),
    ("ranking195buffer195", "cmFua2luZzE5NWJ1ZmZlcjE5NQ"),
    ("ranking195queue195", "cmFua2luZzE5NXF1ZXVlMTk1"),
    ("encoding195queue195", "ZW5jb2RpbmcxOTVxdWV1ZTE5NQ"),
    ("encoding195worker195", "ZW5jb2RpbmcxOTV3b3JrZXIxOTU"),
    ("encoding195kernel195", "ZW5jb2RpbmcxOTVrZXJuZWwxOTU"),
    ("encoding195signal195", "ZW5jb2RpbmcxOTVzaWduYWwxOTU"),
    ("mapping195signal195", "bWFwcGluZzE5NXNpZ25hbDE5NQ"),
    ("mapping195packet195", "bWFwcGluZzE5NXBhY2tldDE5NQ"),
    ("mapping195router195", "bWFwcGluZzE5NXJvdXRlcjE5NQ"),
    ("mapping195cluster195", "bWFwcGluZzE5NWNsdXN0ZXIxOTU"),
    ("record195cluster195", "cmVjb3JkMTk1Y2x1c3RlcjE5NQ"),
    ("record195mirror195", "cmVjb3JkMTk1bWlycm9yMTk1"),
    ("record195filter195", "cmVjb3JkMTk1ZmlsdGVyMTk1"),
    ("record195ranking195", "cmVjb3JkMTk1cmFua2luZzE5NQ"),
    ("candle195ranking195", "Y2FuZGxlMTk1cmFua2luZzE5NQ"),
    ("candle195encoding195", "Y2FuZGxlMTk1ZW5jb2RpbmcxOTU"),
    ("candle195mapping195", "Y2FuZGxlMTk1bWFwcGluZzE5NQ"),
    ("candle195record195", "Y2FuZGxlMTk1cmVjb3JkMTk1"),
    ("thread195record195", "dGhyZWFkMTk1cmVjb3JkMTk1"),
    ("thread195candle195", "dGhyZWFkMTk1Y2FuZGxlMTk1"),
    ("thread195thread195", "dGhyZWFkMTk1dGhyZWFkMTk1"),
    ("thread195kitten195", "dGhyZWFkMTk1a2l0dGVuMTk1"),
    (
        "round 195: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTk1OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 195: agentuniverse is a framework for multi agents",
        "cm91bmQgMTk1OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 195: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTk1OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 195: the processor reads the record then stops",
        "cm91bmQgMTk1OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 195: a worker pulls the next task from the queue",
        "cm91bmQgMTk1OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 195: signals travel through the network layer",
        "cm91bmQgMTk1OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 195: the gateway routes each request by policy",
        "cm91bmQgMTk1OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 195: memory grows until the buffer is full",
        "cm91bmQgMTk1OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 195: the cluster mirrors every packet twice",
        "cm91bmQgMTk1OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 195: ranking uses tokens learned from the corpus",
        "cm91bmQgMTk1OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 195: a long session ends when the candle dies",
        "cm91bmQgMTk1OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 195: encode the prompt then map the result",
        "cm91bmQgMTk1OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 195: the kernel wakes the worker at dawn",
        "cm91bmQgMTk1OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 195: service latency drops after the patch",
        "cm91bmQgMTk1OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 195: the library caches every vector it sees",
        "cm91bmQgMTk1OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 195: agents argue then the debate resolves",
        "cm91bmQgMTk1OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 195: the filter keeps only strong matches",
        "cm91bmQgMTk1OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 195: the model answers with a short reply",
        "cm91bmQgMTk1OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 195: the recorder stores the reasoning trace",
        "cm91bmQgMTk1OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 195: the angel watches the processor run",
        "cm91bmQgMTk1OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 195: angle of the vector decides the match",
        "cm91bmQgMTk1OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 195: the candle burns twice as long at night",
        "cm91bmQgMTk1OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 195: a mirror of the universe in one line",
        "cm91bmQgMTk1OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 195: the queue drains before the storm", "cm91bmQgMTk1OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
