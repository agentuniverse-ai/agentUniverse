"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten145kitten145", "a2l0dGVuMTQ1a2l0dGVuMTQ1"),
    ("kitten145sitting145", "a2l0dGVuMTQ1c2l0dGluZzE0NQ"),
    ("kitten145agent145", "a2l0dGVuMTQ1YWdlbnQxNDU"),
    ("kitten145angle145", "a2l0dGVuMTQ1YW5nbGUxNDU"),
    ("sitting145angle145", "c2l0dGluZzE0NWFuZ2xlMTQ1"),
    ("sitting145universe145", "c2l0dGluZzE0NXVuaXZlcnNlMTQ1"),
    ("sitting145memory145", "c2l0dGluZzE0NW1lbW9yeTE0NQ"),
    ("sitting145stream145", "c2l0dGluZzE0NXN0cmVhbTE0NQ"),
    ("agent145stream145", "YWdlbnQxNDVzdHJlYW0xNDU"),
    ("agent145context145", "YWdlbnQxNDVjb250ZXh0MTQ1"),
    ("agent145knowledge145", "YWdlbnQxNDVrbm93bGVkZ2UxNDU"),
    ("agent145vector145", "YWdlbnQxNDV2ZWN0b3IxNDU"),
    ("angle145vector145", "YW5nbGUxNDV2ZWN0b3IxNDU"),
    ("angle145processor145", "YW5nbGUxNDVwcm9jZXNzb3IxNDU"),
    ("angle145reasoning145", "YW5nbGUxNDVyZWFzb25pbmcxNDU"),
    ("angle145machine145", "YW5nbGUxNDVtYWNoaW5lMTQ1"),
    ("universe145machine145", "dW5pdmVyc2UxNDVtYWNoaW5lMTQ1"),
    ("universe145learning145", "dW5pdmVyc2UxNDVsZWFybmluZzE0NQ"),
    ("universe145model145", "dW5pdmVyc2UxNDVtb2RlbDE0NQ"),
    ("universe145token145", "dW5pdmVyc2UxNDV0b2tlbjE0NQ"),
    ("memory145token145", "bWVtb3J5MTQ1dG9rZW4xNDU"),
    ("memory145prompt145", "bWVtb3J5MTQ1cHJvbXB0MTQ1"),
    ("memory145session145", "bWVtb3J5MTQ1c2Vzc2lvbjE0NQ"),
    ("memory145library145", "bWVtb3J5MTQ1bGlicmFyeTE0NQ"),
    ("stream145library145", "c3RyZWFtMTQ1bGlicmFyeTE0NQ"),
    ("stream145service145", "c3RyZWFtMTQ1c2VydmljZTE0NQ"),
    ("stream145gateway145", "c3RyZWFtMTQ1Z2F0ZXdheTE0NQ"),
    ("stream145storage145", "c3RyZWFtMTQ1c3RvcmFnZTE0NQ"),
    ("context145storage145", "Y29udGV4dDE0NXN0b3JhZ2UxNDU"),
    ("context145network145", "Y29udGV4dDE0NW5ldHdvcmsxNDU"),
    ("context145latency145", "Y29udGV4dDE0NWxhdGVuY3kxNDU"),
    ("context145buffer145", "Y29udGV4dDE0NWJ1ZmZlcjE0NQ"),
    ("knowledge145buffer145", "a25vd2xlZGdlMTQ1YnVmZmVyMTQ1"),
    ("knowledge145queue145", "a25vd2xlZGdlMTQ1cXVldWUxNDU"),
    ("knowledge145worker145", "a25vd2xlZGdlMTQ1d29ya2VyMTQ1"),
    ("knowledge145kernel145", "a25vd2xlZGdlMTQ1a2VybmVsMTQ1"),
    ("vector145kernel145", "dmVjdG9yMTQ1a2VybmVsMTQ1"),
    ("vector145signal145", "dmVjdG9yMTQ1c2lnbmFsMTQ1"),
    ("vector145packet145", "dmVjdG9yMTQ1cGFja2V0MTQ1"),
    ("vector145router145", "dmVjdG9yMTQ1cm91dGVyMTQ1"),
    ("processor145router145", "cHJvY2Vzc29yMTQ1cm91dGVyMTQ1"),
    ("processor145cluster145", "cHJvY2Vzc29yMTQ1Y2x1c3RlcjE0NQ"),
    ("processor145mirror145", "cHJvY2Vzc29yMTQ1bWlycm9yMTQ1"),
    ("processor145filter145", "cHJvY2Vzc29yMTQ1ZmlsdGVyMTQ1"),
    ("reasoning145filter145", "cmVhc29uaW5nMTQ1ZmlsdGVyMTQ1"),
    ("reasoning145ranking145", "cmVhc29uaW5nMTQ1cmFua2luZzE0NQ"),
    ("reasoning145encoding145", "cmVhc29uaW5nMTQ1ZW5jb2RpbmcxNDU"),
    ("reasoning145mapping145", "cmVhc29uaW5nMTQ1bWFwcGluZzE0NQ"),
    ("machine145mapping145", "bWFjaGluZTE0NW1hcHBpbmcxNDU"),
    ("machine145record145", "bWFjaGluZTE0NXJlY29yZDE0NQ"),
    ("machine145candle145", "bWFjaGluZTE0NWNhbmRsZTE0NQ"),
    ("machine145thread145", "bWFjaGluZTE0NXRocmVhZDE0NQ"),
    ("learning145thread145", "bGVhcm5pbmcxNDV0aHJlYWQxNDU"),
    ("learning145kitten145", "bGVhcm5pbmcxNDVraXR0ZW4xNDU"),
    ("learning145sitting145", "bGVhcm5pbmcxNDVzaXR0aW5nMTQ1"),
    ("learning145agent145", "bGVhcm5pbmcxNDVhZ2VudDE0NQ"),
    ("model145agent145", "bW9kZWwxNDVhZ2VudDE0NQ"),
    ("model145angle145", "bW9kZWwxNDVhbmdsZTE0NQ"),
    ("model145universe145", "bW9kZWwxNDV1bml2ZXJzZTE0NQ"),
    ("model145memory145", "bW9kZWwxNDVtZW1vcnkxNDU"),
    ("token145memory145", "dG9rZW4xNDVtZW1vcnkxNDU"),
    ("token145stream145", "dG9rZW4xNDVzdHJlYW0xNDU"),
    ("token145context145", "dG9rZW4xNDVjb250ZXh0MTQ1"),
    ("token145knowledge145", "dG9rZW4xNDVrbm93bGVkZ2UxNDU"),
    ("prompt145knowledge145", "cHJvbXB0MTQ1a25vd2xlZGdlMTQ1"),
    ("prompt145vector145", "cHJvbXB0MTQ1dmVjdG9yMTQ1"),
    ("prompt145processor145", "cHJvbXB0MTQ1cHJvY2Vzc29yMTQ1"),
    ("prompt145reasoning145", "cHJvbXB0MTQ1cmVhc29uaW5nMTQ1"),
    ("session145reasoning145", "c2Vzc2lvbjE0NXJlYXNvbmluZzE0NQ"),
    ("session145machine145", "c2Vzc2lvbjE0NW1hY2hpbmUxNDU"),
    ("session145learning145", "c2Vzc2lvbjE0NWxlYXJuaW5nMTQ1"),
    ("session145model145", "c2Vzc2lvbjE0NW1vZGVsMTQ1"),
    ("library145model145", "bGlicmFyeTE0NW1vZGVsMTQ1"),
    ("library145token145", "bGlicmFyeTE0NXRva2VuMTQ1"),
    ("library145prompt145", "bGlicmFyeTE0NXByb21wdDE0NQ"),
    ("library145session145", "bGlicmFyeTE0NXNlc3Npb24xNDU"),
    ("service145session145", "c2VydmljZTE0NXNlc3Npb24xNDU"),
    ("service145library145", "c2VydmljZTE0NWxpYnJhcnkxNDU"),
    ("service145service145", "c2VydmljZTE0NXNlcnZpY2UxNDU"),
    ("service145gateway145", "c2VydmljZTE0NWdhdGV3YXkxNDU"),
    ("gateway145gateway145", "Z2F0ZXdheTE0NWdhdGV3YXkxNDU"),
    ("gateway145storage145", "Z2F0ZXdheTE0NXN0b3JhZ2UxNDU"),
    ("gateway145network145", "Z2F0ZXdheTE0NW5ldHdvcmsxNDU"),
    ("gateway145latency145", "Z2F0ZXdheTE0NWxhdGVuY3kxNDU"),
    ("storage145latency145", "c3RvcmFnZTE0NWxhdGVuY3kxNDU"),
    ("storage145buffer145", "c3RvcmFnZTE0NWJ1ZmZlcjE0NQ"),
    ("storage145queue145", "c3RvcmFnZTE0NXF1ZXVlMTQ1"),
    ("storage145worker145", "c3RvcmFnZTE0NXdvcmtlcjE0NQ"),
    ("network145worker145", "bmV0d29yazE0NXdvcmtlcjE0NQ"),
    ("network145kernel145", "bmV0d29yazE0NWtlcm5lbDE0NQ"),
    ("network145signal145", "bmV0d29yazE0NXNpZ25hbDE0NQ"),
    ("network145packet145", "bmV0d29yazE0NXBhY2tldDE0NQ"),
    ("latency145packet145", "bGF0ZW5jeTE0NXBhY2tldDE0NQ"),
    ("latency145router145", "bGF0ZW5jeTE0NXJvdXRlcjE0NQ"),
    ("latency145cluster145", "bGF0ZW5jeTE0NWNsdXN0ZXIxNDU"),
    ("latency145mirror145", "bGF0ZW5jeTE0NW1pcnJvcjE0NQ"),
    ("buffer145mirror145", "YnVmZmVyMTQ1bWlycm9yMTQ1"),
    ("buffer145filter145", "YnVmZmVyMTQ1ZmlsdGVyMTQ1"),
    ("buffer145ranking145", "YnVmZmVyMTQ1cmFua2luZzE0NQ"),
    ("buffer145encoding145", "YnVmZmVyMTQ1ZW5jb2RpbmcxNDU"),
    ("queue145encoding145", "cXVldWUxNDVlbmNvZGluZzE0NQ"),
    ("queue145mapping145", "cXVldWUxNDVtYXBwaW5nMTQ1"),
    ("queue145record145", "cXVldWUxNDVyZWNvcmQxNDU"),
    ("queue145candle145", "cXVldWUxNDVjYW5kbGUxNDU"),
    ("worker145candle145", "d29ya2VyMTQ1Y2FuZGxlMTQ1"),
    ("worker145thread145", "d29ya2VyMTQ1dGhyZWFkMTQ1"),
    ("worker145kitten145", "d29ya2VyMTQ1a2l0dGVuMTQ1"),
    ("worker145sitting145", "d29ya2VyMTQ1c2l0dGluZzE0NQ"),
    ("kernel145sitting145", "a2VybmVsMTQ1c2l0dGluZzE0NQ"),
    ("kernel145agent145", "a2VybmVsMTQ1YWdlbnQxNDU"),
    ("kernel145angle145", "a2VybmVsMTQ1YW5nbGUxNDU"),
    ("kernel145universe145", "a2VybmVsMTQ1dW5pdmVyc2UxNDU"),
    ("signal145universe145", "c2lnbmFsMTQ1dW5pdmVyc2UxNDU"),
    ("signal145memory145", "c2lnbmFsMTQ1bWVtb3J5MTQ1"),
    ("signal145stream145", "c2lnbmFsMTQ1c3RyZWFtMTQ1"),
    ("signal145context145", "c2lnbmFsMTQ1Y29udGV4dDE0NQ"),
    ("packet145context145", "cGFja2V0MTQ1Y29udGV4dDE0NQ"),
    ("packet145knowledge145", "cGFja2V0MTQ1a25vd2xlZGdlMTQ1"),
    ("packet145vector145", "cGFja2V0MTQ1dmVjdG9yMTQ1"),
    ("packet145processor145", "cGFja2V0MTQ1cHJvY2Vzc29yMTQ1"),
    ("router145processor145", "cm91dGVyMTQ1cHJvY2Vzc29yMTQ1"),
    ("router145reasoning145", "cm91dGVyMTQ1cmVhc29uaW5nMTQ1"),
    ("router145machine145", "cm91dGVyMTQ1bWFjaGluZTE0NQ"),
    ("router145learning145", "cm91dGVyMTQ1bGVhcm5pbmcxNDU"),
    ("cluster145learning145", "Y2x1c3RlcjE0NWxlYXJuaW5nMTQ1"),
    ("cluster145model145", "Y2x1c3RlcjE0NW1vZGVsMTQ1"),
    ("cluster145token145", "Y2x1c3RlcjE0NXRva2VuMTQ1"),
    ("cluster145prompt145", "Y2x1c3RlcjE0NXByb21wdDE0NQ"),
    ("mirror145prompt145", "bWlycm9yMTQ1cHJvbXB0MTQ1"),
    ("mirror145session145", "bWlycm9yMTQ1c2Vzc2lvbjE0NQ"),
    ("mirror145library145", "bWlycm9yMTQ1bGlicmFyeTE0NQ"),
    ("mirror145service145", "bWlycm9yMTQ1c2VydmljZTE0NQ"),
    ("filter145service145", "ZmlsdGVyMTQ1c2VydmljZTE0NQ"),
    ("filter145gateway145", "ZmlsdGVyMTQ1Z2F0ZXdheTE0NQ"),
    ("filter145storage145", "ZmlsdGVyMTQ1c3RvcmFnZTE0NQ"),
    ("filter145network145", "ZmlsdGVyMTQ1bmV0d29yazE0NQ"),
    ("ranking145network145", "cmFua2luZzE0NW5ldHdvcmsxNDU"),
    ("ranking145latency145", "cmFua2luZzE0NWxhdGVuY3kxNDU"),
    ("ranking145buffer145", "cmFua2luZzE0NWJ1ZmZlcjE0NQ"),
    ("ranking145queue145", "cmFua2luZzE0NXF1ZXVlMTQ1"),
    ("encoding145queue145", "ZW5jb2RpbmcxNDVxdWV1ZTE0NQ"),
    ("encoding145worker145", "ZW5jb2RpbmcxNDV3b3JrZXIxNDU"),
    ("encoding145kernel145", "ZW5jb2RpbmcxNDVrZXJuZWwxNDU"),
    ("encoding145signal145", "ZW5jb2RpbmcxNDVzaWduYWwxNDU"),
    ("mapping145signal145", "bWFwcGluZzE0NXNpZ25hbDE0NQ"),
    ("mapping145packet145", "bWFwcGluZzE0NXBhY2tldDE0NQ"),
    ("mapping145router145", "bWFwcGluZzE0NXJvdXRlcjE0NQ"),
    ("mapping145cluster145", "bWFwcGluZzE0NWNsdXN0ZXIxNDU"),
    ("record145cluster145", "cmVjb3JkMTQ1Y2x1c3RlcjE0NQ"),
    ("record145mirror145", "cmVjb3JkMTQ1bWlycm9yMTQ1"),
    ("record145filter145", "cmVjb3JkMTQ1ZmlsdGVyMTQ1"),
    ("record145ranking145", "cmVjb3JkMTQ1cmFua2luZzE0NQ"),
    ("candle145ranking145", "Y2FuZGxlMTQ1cmFua2luZzE0NQ"),
    ("candle145encoding145", "Y2FuZGxlMTQ1ZW5jb2RpbmcxNDU"),
    ("candle145mapping145", "Y2FuZGxlMTQ1bWFwcGluZzE0NQ"),
    ("candle145record145", "Y2FuZGxlMTQ1cmVjb3JkMTQ1"),
    ("thread145record145", "dGhyZWFkMTQ1cmVjb3JkMTQ1"),
    ("thread145candle145", "dGhyZWFkMTQ1Y2FuZGxlMTQ1"),
    ("thread145thread145", "dGhyZWFkMTQ1dGhyZWFkMTQ1"),
    ("thread145kitten145", "dGhyZWFkMTQ1a2l0dGVuMTQ1"),
    (
        "round 145: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTQ1OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 145: agentuniverse is a framework for multi agents",
        "cm91bmQgMTQ1OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 145: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTQ1OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 145: the processor reads the record then stops",
        "cm91bmQgMTQ1OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 145: a worker pulls the next task from the queue",
        "cm91bmQgMTQ1OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 145: signals travel through the network layer",
        "cm91bmQgMTQ1OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 145: the gateway routes each request by policy",
        "cm91bmQgMTQ1OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 145: memory grows until the buffer is full",
        "cm91bmQgMTQ1OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 145: the cluster mirrors every packet twice",
        "cm91bmQgMTQ1OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 145: ranking uses tokens learned from the corpus",
        "cm91bmQgMTQ1OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 145: a long session ends when the candle dies",
        "cm91bmQgMTQ1OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 145: encode the prompt then map the result",
        "cm91bmQgMTQ1OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 145: the kernel wakes the worker at dawn",
        "cm91bmQgMTQ1OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 145: service latency drops after the patch",
        "cm91bmQgMTQ1OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 145: the library caches every vector it sees",
        "cm91bmQgMTQ1OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 145: agents argue then the debate resolves",
        "cm91bmQgMTQ1OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 145: the filter keeps only strong matches",
        "cm91bmQgMTQ1OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 145: the model answers with a short reply",
        "cm91bmQgMTQ1OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 145: the recorder stores the reasoning trace",
        "cm91bmQgMTQ1OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 145: the angel watches the processor run",
        "cm91bmQgMTQ1OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 145: angle of the vector decides the match",
        "cm91bmQgMTQ1OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 145: the candle burns twice as long at night",
        "cm91bmQgMTQ1OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 145: a mirror of the universe in one line",
        "cm91bmQgMTQ1OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 145: the queue drains before the storm", "cm91bmQgMTQ1OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
