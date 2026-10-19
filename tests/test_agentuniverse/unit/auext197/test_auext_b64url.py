"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten197kitten197", "a2l0dGVuMTk3a2l0dGVuMTk3"),
    ("kitten197sitting197", "a2l0dGVuMTk3c2l0dGluZzE5Nw"),
    ("kitten197agent197", "a2l0dGVuMTk3YWdlbnQxOTc"),
    ("kitten197angle197", "a2l0dGVuMTk3YW5nbGUxOTc"),
    ("sitting197angle197", "c2l0dGluZzE5N2FuZ2xlMTk3"),
    ("sitting197universe197", "c2l0dGluZzE5N3VuaXZlcnNlMTk3"),
    ("sitting197memory197", "c2l0dGluZzE5N21lbW9yeTE5Nw"),
    ("sitting197stream197", "c2l0dGluZzE5N3N0cmVhbTE5Nw"),
    ("agent197stream197", "YWdlbnQxOTdzdHJlYW0xOTc"),
    ("agent197context197", "YWdlbnQxOTdjb250ZXh0MTk3"),
    ("agent197knowledge197", "YWdlbnQxOTdrbm93bGVkZ2UxOTc"),
    ("agent197vector197", "YWdlbnQxOTd2ZWN0b3IxOTc"),
    ("angle197vector197", "YW5nbGUxOTd2ZWN0b3IxOTc"),
    ("angle197processor197", "YW5nbGUxOTdwcm9jZXNzb3IxOTc"),
    ("angle197reasoning197", "YW5nbGUxOTdyZWFzb25pbmcxOTc"),
    ("angle197machine197", "YW5nbGUxOTdtYWNoaW5lMTk3"),
    ("universe197machine197", "dW5pdmVyc2UxOTdtYWNoaW5lMTk3"),
    ("universe197learning197", "dW5pdmVyc2UxOTdsZWFybmluZzE5Nw"),
    ("universe197model197", "dW5pdmVyc2UxOTdtb2RlbDE5Nw"),
    ("universe197token197", "dW5pdmVyc2UxOTd0b2tlbjE5Nw"),
    ("memory197token197", "bWVtb3J5MTk3dG9rZW4xOTc"),
    ("memory197prompt197", "bWVtb3J5MTk3cHJvbXB0MTk3"),
    ("memory197session197", "bWVtb3J5MTk3c2Vzc2lvbjE5Nw"),
    ("memory197library197", "bWVtb3J5MTk3bGlicmFyeTE5Nw"),
    ("stream197library197", "c3RyZWFtMTk3bGlicmFyeTE5Nw"),
    ("stream197service197", "c3RyZWFtMTk3c2VydmljZTE5Nw"),
    ("stream197gateway197", "c3RyZWFtMTk3Z2F0ZXdheTE5Nw"),
    ("stream197storage197", "c3RyZWFtMTk3c3RvcmFnZTE5Nw"),
    ("context197storage197", "Y29udGV4dDE5N3N0b3JhZ2UxOTc"),
    ("context197network197", "Y29udGV4dDE5N25ldHdvcmsxOTc"),
    ("context197latency197", "Y29udGV4dDE5N2xhdGVuY3kxOTc"),
    ("context197buffer197", "Y29udGV4dDE5N2J1ZmZlcjE5Nw"),
    ("knowledge197buffer197", "a25vd2xlZGdlMTk3YnVmZmVyMTk3"),
    ("knowledge197queue197", "a25vd2xlZGdlMTk3cXVldWUxOTc"),
    ("knowledge197worker197", "a25vd2xlZGdlMTk3d29ya2VyMTk3"),
    ("knowledge197kernel197", "a25vd2xlZGdlMTk3a2VybmVsMTk3"),
    ("vector197kernel197", "dmVjdG9yMTk3a2VybmVsMTk3"),
    ("vector197signal197", "dmVjdG9yMTk3c2lnbmFsMTk3"),
    ("vector197packet197", "dmVjdG9yMTk3cGFja2V0MTk3"),
    ("vector197router197", "dmVjdG9yMTk3cm91dGVyMTk3"),
    ("processor197router197", "cHJvY2Vzc29yMTk3cm91dGVyMTk3"),
    ("processor197cluster197", "cHJvY2Vzc29yMTk3Y2x1c3RlcjE5Nw"),
    ("processor197mirror197", "cHJvY2Vzc29yMTk3bWlycm9yMTk3"),
    ("processor197filter197", "cHJvY2Vzc29yMTk3ZmlsdGVyMTk3"),
    ("reasoning197filter197", "cmVhc29uaW5nMTk3ZmlsdGVyMTk3"),
    ("reasoning197ranking197", "cmVhc29uaW5nMTk3cmFua2luZzE5Nw"),
    ("reasoning197encoding197", "cmVhc29uaW5nMTk3ZW5jb2RpbmcxOTc"),
    ("reasoning197mapping197", "cmVhc29uaW5nMTk3bWFwcGluZzE5Nw"),
    ("machine197mapping197", "bWFjaGluZTE5N21hcHBpbmcxOTc"),
    ("machine197record197", "bWFjaGluZTE5N3JlY29yZDE5Nw"),
    ("machine197candle197", "bWFjaGluZTE5N2NhbmRsZTE5Nw"),
    ("machine197thread197", "bWFjaGluZTE5N3RocmVhZDE5Nw"),
    ("learning197thread197", "bGVhcm5pbmcxOTd0aHJlYWQxOTc"),
    ("learning197kitten197", "bGVhcm5pbmcxOTdraXR0ZW4xOTc"),
    ("learning197sitting197", "bGVhcm5pbmcxOTdzaXR0aW5nMTk3"),
    ("learning197agent197", "bGVhcm5pbmcxOTdhZ2VudDE5Nw"),
    ("model197agent197", "bW9kZWwxOTdhZ2VudDE5Nw"),
    ("model197angle197", "bW9kZWwxOTdhbmdsZTE5Nw"),
    ("model197universe197", "bW9kZWwxOTd1bml2ZXJzZTE5Nw"),
    ("model197memory197", "bW9kZWwxOTdtZW1vcnkxOTc"),
    ("token197memory197", "dG9rZW4xOTdtZW1vcnkxOTc"),
    ("token197stream197", "dG9rZW4xOTdzdHJlYW0xOTc"),
    ("token197context197", "dG9rZW4xOTdjb250ZXh0MTk3"),
    ("token197knowledge197", "dG9rZW4xOTdrbm93bGVkZ2UxOTc"),
    ("prompt197knowledge197", "cHJvbXB0MTk3a25vd2xlZGdlMTk3"),
    ("prompt197vector197", "cHJvbXB0MTk3dmVjdG9yMTk3"),
    ("prompt197processor197", "cHJvbXB0MTk3cHJvY2Vzc29yMTk3"),
    ("prompt197reasoning197", "cHJvbXB0MTk3cmVhc29uaW5nMTk3"),
    ("session197reasoning197", "c2Vzc2lvbjE5N3JlYXNvbmluZzE5Nw"),
    ("session197machine197", "c2Vzc2lvbjE5N21hY2hpbmUxOTc"),
    ("session197learning197", "c2Vzc2lvbjE5N2xlYXJuaW5nMTk3"),
    ("session197model197", "c2Vzc2lvbjE5N21vZGVsMTk3"),
    ("library197model197", "bGlicmFyeTE5N21vZGVsMTk3"),
    ("library197token197", "bGlicmFyeTE5N3Rva2VuMTk3"),
    ("library197prompt197", "bGlicmFyeTE5N3Byb21wdDE5Nw"),
    ("library197session197", "bGlicmFyeTE5N3Nlc3Npb24xOTc"),
    ("service197session197", "c2VydmljZTE5N3Nlc3Npb24xOTc"),
    ("service197library197", "c2VydmljZTE5N2xpYnJhcnkxOTc"),
    ("service197service197", "c2VydmljZTE5N3NlcnZpY2UxOTc"),
    ("service197gateway197", "c2VydmljZTE5N2dhdGV3YXkxOTc"),
    ("gateway197gateway197", "Z2F0ZXdheTE5N2dhdGV3YXkxOTc"),
    ("gateway197storage197", "Z2F0ZXdheTE5N3N0b3JhZ2UxOTc"),
    ("gateway197network197", "Z2F0ZXdheTE5N25ldHdvcmsxOTc"),
    ("gateway197latency197", "Z2F0ZXdheTE5N2xhdGVuY3kxOTc"),
    ("storage197latency197", "c3RvcmFnZTE5N2xhdGVuY3kxOTc"),
    ("storage197buffer197", "c3RvcmFnZTE5N2J1ZmZlcjE5Nw"),
    ("storage197queue197", "c3RvcmFnZTE5N3F1ZXVlMTk3"),
    ("storage197worker197", "c3RvcmFnZTE5N3dvcmtlcjE5Nw"),
    ("network197worker197", "bmV0d29yazE5N3dvcmtlcjE5Nw"),
    ("network197kernel197", "bmV0d29yazE5N2tlcm5lbDE5Nw"),
    ("network197signal197", "bmV0d29yazE5N3NpZ25hbDE5Nw"),
    ("network197packet197", "bmV0d29yazE5N3BhY2tldDE5Nw"),
    ("latency197packet197", "bGF0ZW5jeTE5N3BhY2tldDE5Nw"),
    ("latency197router197", "bGF0ZW5jeTE5N3JvdXRlcjE5Nw"),
    ("latency197cluster197", "bGF0ZW5jeTE5N2NsdXN0ZXIxOTc"),
    ("latency197mirror197", "bGF0ZW5jeTE5N21pcnJvcjE5Nw"),
    ("buffer197mirror197", "YnVmZmVyMTk3bWlycm9yMTk3"),
    ("buffer197filter197", "YnVmZmVyMTk3ZmlsdGVyMTk3"),
    ("buffer197ranking197", "YnVmZmVyMTk3cmFua2luZzE5Nw"),
    ("buffer197encoding197", "YnVmZmVyMTk3ZW5jb2RpbmcxOTc"),
    ("queue197encoding197", "cXVldWUxOTdlbmNvZGluZzE5Nw"),
    ("queue197mapping197", "cXVldWUxOTdtYXBwaW5nMTk3"),
    ("queue197record197", "cXVldWUxOTdyZWNvcmQxOTc"),
    ("queue197candle197", "cXVldWUxOTdjYW5kbGUxOTc"),
    ("worker197candle197", "d29ya2VyMTk3Y2FuZGxlMTk3"),
    ("worker197thread197", "d29ya2VyMTk3dGhyZWFkMTk3"),
    ("worker197kitten197", "d29ya2VyMTk3a2l0dGVuMTk3"),
    ("worker197sitting197", "d29ya2VyMTk3c2l0dGluZzE5Nw"),
    ("kernel197sitting197", "a2VybmVsMTk3c2l0dGluZzE5Nw"),
    ("kernel197agent197", "a2VybmVsMTk3YWdlbnQxOTc"),
    ("kernel197angle197", "a2VybmVsMTk3YW5nbGUxOTc"),
    ("kernel197universe197", "a2VybmVsMTk3dW5pdmVyc2UxOTc"),
    ("signal197universe197", "c2lnbmFsMTk3dW5pdmVyc2UxOTc"),
    ("signal197memory197", "c2lnbmFsMTk3bWVtb3J5MTk3"),
    ("signal197stream197", "c2lnbmFsMTk3c3RyZWFtMTk3"),
    ("signal197context197", "c2lnbmFsMTk3Y29udGV4dDE5Nw"),
    ("packet197context197", "cGFja2V0MTk3Y29udGV4dDE5Nw"),
    ("packet197knowledge197", "cGFja2V0MTk3a25vd2xlZGdlMTk3"),
    ("packet197vector197", "cGFja2V0MTk3dmVjdG9yMTk3"),
    ("packet197processor197", "cGFja2V0MTk3cHJvY2Vzc29yMTk3"),
    ("router197processor197", "cm91dGVyMTk3cHJvY2Vzc29yMTk3"),
    ("router197reasoning197", "cm91dGVyMTk3cmVhc29uaW5nMTk3"),
    ("router197machine197", "cm91dGVyMTk3bWFjaGluZTE5Nw"),
    ("router197learning197", "cm91dGVyMTk3bGVhcm5pbmcxOTc"),
    ("cluster197learning197", "Y2x1c3RlcjE5N2xlYXJuaW5nMTk3"),
    ("cluster197model197", "Y2x1c3RlcjE5N21vZGVsMTk3"),
    ("cluster197token197", "Y2x1c3RlcjE5N3Rva2VuMTk3"),
    ("cluster197prompt197", "Y2x1c3RlcjE5N3Byb21wdDE5Nw"),
    ("mirror197prompt197", "bWlycm9yMTk3cHJvbXB0MTk3"),
    ("mirror197session197", "bWlycm9yMTk3c2Vzc2lvbjE5Nw"),
    ("mirror197library197", "bWlycm9yMTk3bGlicmFyeTE5Nw"),
    ("mirror197service197", "bWlycm9yMTk3c2VydmljZTE5Nw"),
    ("filter197service197", "ZmlsdGVyMTk3c2VydmljZTE5Nw"),
    ("filter197gateway197", "ZmlsdGVyMTk3Z2F0ZXdheTE5Nw"),
    ("filter197storage197", "ZmlsdGVyMTk3c3RvcmFnZTE5Nw"),
    ("filter197network197", "ZmlsdGVyMTk3bmV0d29yazE5Nw"),
    ("ranking197network197", "cmFua2luZzE5N25ldHdvcmsxOTc"),
    ("ranking197latency197", "cmFua2luZzE5N2xhdGVuY3kxOTc"),
    ("ranking197buffer197", "cmFua2luZzE5N2J1ZmZlcjE5Nw"),
    ("ranking197queue197", "cmFua2luZzE5N3F1ZXVlMTk3"),
    ("encoding197queue197", "ZW5jb2RpbmcxOTdxdWV1ZTE5Nw"),
    ("encoding197worker197", "ZW5jb2RpbmcxOTd3b3JrZXIxOTc"),
    ("encoding197kernel197", "ZW5jb2RpbmcxOTdrZXJuZWwxOTc"),
    ("encoding197signal197", "ZW5jb2RpbmcxOTdzaWduYWwxOTc"),
    ("mapping197signal197", "bWFwcGluZzE5N3NpZ25hbDE5Nw"),
    ("mapping197packet197", "bWFwcGluZzE5N3BhY2tldDE5Nw"),
    ("mapping197router197", "bWFwcGluZzE5N3JvdXRlcjE5Nw"),
    ("mapping197cluster197", "bWFwcGluZzE5N2NsdXN0ZXIxOTc"),
    ("record197cluster197", "cmVjb3JkMTk3Y2x1c3RlcjE5Nw"),
    ("record197mirror197", "cmVjb3JkMTk3bWlycm9yMTk3"),
    ("record197filter197", "cmVjb3JkMTk3ZmlsdGVyMTk3"),
    ("record197ranking197", "cmVjb3JkMTk3cmFua2luZzE5Nw"),
    ("candle197ranking197", "Y2FuZGxlMTk3cmFua2luZzE5Nw"),
    ("candle197encoding197", "Y2FuZGxlMTk3ZW5jb2RpbmcxOTc"),
    ("candle197mapping197", "Y2FuZGxlMTk3bWFwcGluZzE5Nw"),
    ("candle197record197", "Y2FuZGxlMTk3cmVjb3JkMTk3"),
    ("thread197record197", "dGhyZWFkMTk3cmVjb3JkMTk3"),
    ("thread197candle197", "dGhyZWFkMTk3Y2FuZGxlMTk3"),
    ("thread197thread197", "dGhyZWFkMTk3dGhyZWFkMTk3"),
    ("thread197kitten197", "dGhyZWFkMTk3a2l0dGVuMTk3"),
    (
        "round 197: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTk3OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 197: agentuniverse is a framework for multi agents",
        "cm91bmQgMTk3OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 197: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTk3OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 197: the processor reads the record then stops",
        "cm91bmQgMTk3OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 197: a worker pulls the next task from the queue",
        "cm91bmQgMTk3OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 197: signals travel through the network layer",
        "cm91bmQgMTk3OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 197: the gateway routes each request by policy",
        "cm91bmQgMTk3OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 197: memory grows until the buffer is full",
        "cm91bmQgMTk3OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 197: the cluster mirrors every packet twice",
        "cm91bmQgMTk3OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 197: ranking uses tokens learned from the corpus",
        "cm91bmQgMTk3OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 197: a long session ends when the candle dies",
        "cm91bmQgMTk3OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 197: encode the prompt then map the result",
        "cm91bmQgMTk3OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 197: the kernel wakes the worker at dawn",
        "cm91bmQgMTk3OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 197: service latency drops after the patch",
        "cm91bmQgMTk3OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 197: the library caches every vector it sees",
        "cm91bmQgMTk3OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 197: agents argue then the debate resolves",
        "cm91bmQgMTk3OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 197: the filter keeps only strong matches",
        "cm91bmQgMTk3OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 197: the model answers with a short reply",
        "cm91bmQgMTk3OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 197: the recorder stores the reasoning trace",
        "cm91bmQgMTk3OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 197: the angel watches the processor run",
        "cm91bmQgMTk3OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 197: angle of the vector decides the match",
        "cm91bmQgMTk3OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 197: the candle burns twice as long at night",
        "cm91bmQgMTk3OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 197: a mirror of the universe in one line",
        "cm91bmQgMTk3OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 197: the queue drains before the storm", "cm91bmQgMTk3OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
