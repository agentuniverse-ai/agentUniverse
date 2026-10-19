"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten185kitten185", "a2l0dGVuMTg1a2l0dGVuMTg1"),
    ("kitten185sitting185", "a2l0dGVuMTg1c2l0dGluZzE4NQ"),
    ("kitten185agent185", "a2l0dGVuMTg1YWdlbnQxODU"),
    ("kitten185angle185", "a2l0dGVuMTg1YW5nbGUxODU"),
    ("sitting185angle185", "c2l0dGluZzE4NWFuZ2xlMTg1"),
    ("sitting185universe185", "c2l0dGluZzE4NXVuaXZlcnNlMTg1"),
    ("sitting185memory185", "c2l0dGluZzE4NW1lbW9yeTE4NQ"),
    ("sitting185stream185", "c2l0dGluZzE4NXN0cmVhbTE4NQ"),
    ("agent185stream185", "YWdlbnQxODVzdHJlYW0xODU"),
    ("agent185context185", "YWdlbnQxODVjb250ZXh0MTg1"),
    ("agent185knowledge185", "YWdlbnQxODVrbm93bGVkZ2UxODU"),
    ("agent185vector185", "YWdlbnQxODV2ZWN0b3IxODU"),
    ("angle185vector185", "YW5nbGUxODV2ZWN0b3IxODU"),
    ("angle185processor185", "YW5nbGUxODVwcm9jZXNzb3IxODU"),
    ("angle185reasoning185", "YW5nbGUxODVyZWFzb25pbmcxODU"),
    ("angle185machine185", "YW5nbGUxODVtYWNoaW5lMTg1"),
    ("universe185machine185", "dW5pdmVyc2UxODVtYWNoaW5lMTg1"),
    ("universe185learning185", "dW5pdmVyc2UxODVsZWFybmluZzE4NQ"),
    ("universe185model185", "dW5pdmVyc2UxODVtb2RlbDE4NQ"),
    ("universe185token185", "dW5pdmVyc2UxODV0b2tlbjE4NQ"),
    ("memory185token185", "bWVtb3J5MTg1dG9rZW4xODU"),
    ("memory185prompt185", "bWVtb3J5MTg1cHJvbXB0MTg1"),
    ("memory185session185", "bWVtb3J5MTg1c2Vzc2lvbjE4NQ"),
    ("memory185library185", "bWVtb3J5MTg1bGlicmFyeTE4NQ"),
    ("stream185library185", "c3RyZWFtMTg1bGlicmFyeTE4NQ"),
    ("stream185service185", "c3RyZWFtMTg1c2VydmljZTE4NQ"),
    ("stream185gateway185", "c3RyZWFtMTg1Z2F0ZXdheTE4NQ"),
    ("stream185storage185", "c3RyZWFtMTg1c3RvcmFnZTE4NQ"),
    ("context185storage185", "Y29udGV4dDE4NXN0b3JhZ2UxODU"),
    ("context185network185", "Y29udGV4dDE4NW5ldHdvcmsxODU"),
    ("context185latency185", "Y29udGV4dDE4NWxhdGVuY3kxODU"),
    ("context185buffer185", "Y29udGV4dDE4NWJ1ZmZlcjE4NQ"),
    ("knowledge185buffer185", "a25vd2xlZGdlMTg1YnVmZmVyMTg1"),
    ("knowledge185queue185", "a25vd2xlZGdlMTg1cXVldWUxODU"),
    ("knowledge185worker185", "a25vd2xlZGdlMTg1d29ya2VyMTg1"),
    ("knowledge185kernel185", "a25vd2xlZGdlMTg1a2VybmVsMTg1"),
    ("vector185kernel185", "dmVjdG9yMTg1a2VybmVsMTg1"),
    ("vector185signal185", "dmVjdG9yMTg1c2lnbmFsMTg1"),
    ("vector185packet185", "dmVjdG9yMTg1cGFja2V0MTg1"),
    ("vector185router185", "dmVjdG9yMTg1cm91dGVyMTg1"),
    ("processor185router185", "cHJvY2Vzc29yMTg1cm91dGVyMTg1"),
    ("processor185cluster185", "cHJvY2Vzc29yMTg1Y2x1c3RlcjE4NQ"),
    ("processor185mirror185", "cHJvY2Vzc29yMTg1bWlycm9yMTg1"),
    ("processor185filter185", "cHJvY2Vzc29yMTg1ZmlsdGVyMTg1"),
    ("reasoning185filter185", "cmVhc29uaW5nMTg1ZmlsdGVyMTg1"),
    ("reasoning185ranking185", "cmVhc29uaW5nMTg1cmFua2luZzE4NQ"),
    ("reasoning185encoding185", "cmVhc29uaW5nMTg1ZW5jb2RpbmcxODU"),
    ("reasoning185mapping185", "cmVhc29uaW5nMTg1bWFwcGluZzE4NQ"),
    ("machine185mapping185", "bWFjaGluZTE4NW1hcHBpbmcxODU"),
    ("machine185record185", "bWFjaGluZTE4NXJlY29yZDE4NQ"),
    ("machine185candle185", "bWFjaGluZTE4NWNhbmRsZTE4NQ"),
    ("machine185thread185", "bWFjaGluZTE4NXRocmVhZDE4NQ"),
    ("learning185thread185", "bGVhcm5pbmcxODV0aHJlYWQxODU"),
    ("learning185kitten185", "bGVhcm5pbmcxODVraXR0ZW4xODU"),
    ("learning185sitting185", "bGVhcm5pbmcxODVzaXR0aW5nMTg1"),
    ("learning185agent185", "bGVhcm5pbmcxODVhZ2VudDE4NQ"),
    ("model185agent185", "bW9kZWwxODVhZ2VudDE4NQ"),
    ("model185angle185", "bW9kZWwxODVhbmdsZTE4NQ"),
    ("model185universe185", "bW9kZWwxODV1bml2ZXJzZTE4NQ"),
    ("model185memory185", "bW9kZWwxODVtZW1vcnkxODU"),
    ("token185memory185", "dG9rZW4xODVtZW1vcnkxODU"),
    ("token185stream185", "dG9rZW4xODVzdHJlYW0xODU"),
    ("token185context185", "dG9rZW4xODVjb250ZXh0MTg1"),
    ("token185knowledge185", "dG9rZW4xODVrbm93bGVkZ2UxODU"),
    ("prompt185knowledge185", "cHJvbXB0MTg1a25vd2xlZGdlMTg1"),
    ("prompt185vector185", "cHJvbXB0MTg1dmVjdG9yMTg1"),
    ("prompt185processor185", "cHJvbXB0MTg1cHJvY2Vzc29yMTg1"),
    ("prompt185reasoning185", "cHJvbXB0MTg1cmVhc29uaW5nMTg1"),
    ("session185reasoning185", "c2Vzc2lvbjE4NXJlYXNvbmluZzE4NQ"),
    ("session185machine185", "c2Vzc2lvbjE4NW1hY2hpbmUxODU"),
    ("session185learning185", "c2Vzc2lvbjE4NWxlYXJuaW5nMTg1"),
    ("session185model185", "c2Vzc2lvbjE4NW1vZGVsMTg1"),
    ("library185model185", "bGlicmFyeTE4NW1vZGVsMTg1"),
    ("library185token185", "bGlicmFyeTE4NXRva2VuMTg1"),
    ("library185prompt185", "bGlicmFyeTE4NXByb21wdDE4NQ"),
    ("library185session185", "bGlicmFyeTE4NXNlc3Npb24xODU"),
    ("service185session185", "c2VydmljZTE4NXNlc3Npb24xODU"),
    ("service185library185", "c2VydmljZTE4NWxpYnJhcnkxODU"),
    ("service185service185", "c2VydmljZTE4NXNlcnZpY2UxODU"),
    ("service185gateway185", "c2VydmljZTE4NWdhdGV3YXkxODU"),
    ("gateway185gateway185", "Z2F0ZXdheTE4NWdhdGV3YXkxODU"),
    ("gateway185storage185", "Z2F0ZXdheTE4NXN0b3JhZ2UxODU"),
    ("gateway185network185", "Z2F0ZXdheTE4NW5ldHdvcmsxODU"),
    ("gateway185latency185", "Z2F0ZXdheTE4NWxhdGVuY3kxODU"),
    ("storage185latency185", "c3RvcmFnZTE4NWxhdGVuY3kxODU"),
    ("storage185buffer185", "c3RvcmFnZTE4NWJ1ZmZlcjE4NQ"),
    ("storage185queue185", "c3RvcmFnZTE4NXF1ZXVlMTg1"),
    ("storage185worker185", "c3RvcmFnZTE4NXdvcmtlcjE4NQ"),
    ("network185worker185", "bmV0d29yazE4NXdvcmtlcjE4NQ"),
    ("network185kernel185", "bmV0d29yazE4NWtlcm5lbDE4NQ"),
    ("network185signal185", "bmV0d29yazE4NXNpZ25hbDE4NQ"),
    ("network185packet185", "bmV0d29yazE4NXBhY2tldDE4NQ"),
    ("latency185packet185", "bGF0ZW5jeTE4NXBhY2tldDE4NQ"),
    ("latency185router185", "bGF0ZW5jeTE4NXJvdXRlcjE4NQ"),
    ("latency185cluster185", "bGF0ZW5jeTE4NWNsdXN0ZXIxODU"),
    ("latency185mirror185", "bGF0ZW5jeTE4NW1pcnJvcjE4NQ"),
    ("buffer185mirror185", "YnVmZmVyMTg1bWlycm9yMTg1"),
    ("buffer185filter185", "YnVmZmVyMTg1ZmlsdGVyMTg1"),
    ("buffer185ranking185", "YnVmZmVyMTg1cmFua2luZzE4NQ"),
    ("buffer185encoding185", "YnVmZmVyMTg1ZW5jb2RpbmcxODU"),
    ("queue185encoding185", "cXVldWUxODVlbmNvZGluZzE4NQ"),
    ("queue185mapping185", "cXVldWUxODVtYXBwaW5nMTg1"),
    ("queue185record185", "cXVldWUxODVyZWNvcmQxODU"),
    ("queue185candle185", "cXVldWUxODVjYW5kbGUxODU"),
    ("worker185candle185", "d29ya2VyMTg1Y2FuZGxlMTg1"),
    ("worker185thread185", "d29ya2VyMTg1dGhyZWFkMTg1"),
    ("worker185kitten185", "d29ya2VyMTg1a2l0dGVuMTg1"),
    ("worker185sitting185", "d29ya2VyMTg1c2l0dGluZzE4NQ"),
    ("kernel185sitting185", "a2VybmVsMTg1c2l0dGluZzE4NQ"),
    ("kernel185agent185", "a2VybmVsMTg1YWdlbnQxODU"),
    ("kernel185angle185", "a2VybmVsMTg1YW5nbGUxODU"),
    ("kernel185universe185", "a2VybmVsMTg1dW5pdmVyc2UxODU"),
    ("signal185universe185", "c2lnbmFsMTg1dW5pdmVyc2UxODU"),
    ("signal185memory185", "c2lnbmFsMTg1bWVtb3J5MTg1"),
    ("signal185stream185", "c2lnbmFsMTg1c3RyZWFtMTg1"),
    ("signal185context185", "c2lnbmFsMTg1Y29udGV4dDE4NQ"),
    ("packet185context185", "cGFja2V0MTg1Y29udGV4dDE4NQ"),
    ("packet185knowledge185", "cGFja2V0MTg1a25vd2xlZGdlMTg1"),
    ("packet185vector185", "cGFja2V0MTg1dmVjdG9yMTg1"),
    ("packet185processor185", "cGFja2V0MTg1cHJvY2Vzc29yMTg1"),
    ("router185processor185", "cm91dGVyMTg1cHJvY2Vzc29yMTg1"),
    ("router185reasoning185", "cm91dGVyMTg1cmVhc29uaW5nMTg1"),
    ("router185machine185", "cm91dGVyMTg1bWFjaGluZTE4NQ"),
    ("router185learning185", "cm91dGVyMTg1bGVhcm5pbmcxODU"),
    ("cluster185learning185", "Y2x1c3RlcjE4NWxlYXJuaW5nMTg1"),
    ("cluster185model185", "Y2x1c3RlcjE4NW1vZGVsMTg1"),
    ("cluster185token185", "Y2x1c3RlcjE4NXRva2VuMTg1"),
    ("cluster185prompt185", "Y2x1c3RlcjE4NXByb21wdDE4NQ"),
    ("mirror185prompt185", "bWlycm9yMTg1cHJvbXB0MTg1"),
    ("mirror185session185", "bWlycm9yMTg1c2Vzc2lvbjE4NQ"),
    ("mirror185library185", "bWlycm9yMTg1bGlicmFyeTE4NQ"),
    ("mirror185service185", "bWlycm9yMTg1c2VydmljZTE4NQ"),
    ("filter185service185", "ZmlsdGVyMTg1c2VydmljZTE4NQ"),
    ("filter185gateway185", "ZmlsdGVyMTg1Z2F0ZXdheTE4NQ"),
    ("filter185storage185", "ZmlsdGVyMTg1c3RvcmFnZTE4NQ"),
    ("filter185network185", "ZmlsdGVyMTg1bmV0d29yazE4NQ"),
    ("ranking185network185", "cmFua2luZzE4NW5ldHdvcmsxODU"),
    ("ranking185latency185", "cmFua2luZzE4NWxhdGVuY3kxODU"),
    ("ranking185buffer185", "cmFua2luZzE4NWJ1ZmZlcjE4NQ"),
    ("ranking185queue185", "cmFua2luZzE4NXF1ZXVlMTg1"),
    ("encoding185queue185", "ZW5jb2RpbmcxODVxdWV1ZTE4NQ"),
    ("encoding185worker185", "ZW5jb2RpbmcxODV3b3JrZXIxODU"),
    ("encoding185kernel185", "ZW5jb2RpbmcxODVrZXJuZWwxODU"),
    ("encoding185signal185", "ZW5jb2RpbmcxODVzaWduYWwxODU"),
    ("mapping185signal185", "bWFwcGluZzE4NXNpZ25hbDE4NQ"),
    ("mapping185packet185", "bWFwcGluZzE4NXBhY2tldDE4NQ"),
    ("mapping185router185", "bWFwcGluZzE4NXJvdXRlcjE4NQ"),
    ("mapping185cluster185", "bWFwcGluZzE4NWNsdXN0ZXIxODU"),
    ("record185cluster185", "cmVjb3JkMTg1Y2x1c3RlcjE4NQ"),
    ("record185mirror185", "cmVjb3JkMTg1bWlycm9yMTg1"),
    ("record185filter185", "cmVjb3JkMTg1ZmlsdGVyMTg1"),
    ("record185ranking185", "cmVjb3JkMTg1cmFua2luZzE4NQ"),
    ("candle185ranking185", "Y2FuZGxlMTg1cmFua2luZzE4NQ"),
    ("candle185encoding185", "Y2FuZGxlMTg1ZW5jb2RpbmcxODU"),
    ("candle185mapping185", "Y2FuZGxlMTg1bWFwcGluZzE4NQ"),
    ("candle185record185", "Y2FuZGxlMTg1cmVjb3JkMTg1"),
    ("thread185record185", "dGhyZWFkMTg1cmVjb3JkMTg1"),
    ("thread185candle185", "dGhyZWFkMTg1Y2FuZGxlMTg1"),
    ("thread185thread185", "dGhyZWFkMTg1dGhyZWFkMTg1"),
    ("thread185kitten185", "dGhyZWFkMTg1a2l0dGVuMTg1"),
    (
        "round 185: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTg1OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 185: agentuniverse is a framework for multi agents",
        "cm91bmQgMTg1OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 185: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTg1OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 185: the processor reads the record then stops",
        "cm91bmQgMTg1OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 185: a worker pulls the next task from the queue",
        "cm91bmQgMTg1OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 185: signals travel through the network layer",
        "cm91bmQgMTg1OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 185: the gateway routes each request by policy",
        "cm91bmQgMTg1OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 185: memory grows until the buffer is full",
        "cm91bmQgMTg1OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 185: the cluster mirrors every packet twice",
        "cm91bmQgMTg1OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 185: ranking uses tokens learned from the corpus",
        "cm91bmQgMTg1OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 185: a long session ends when the candle dies",
        "cm91bmQgMTg1OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 185: encode the prompt then map the result",
        "cm91bmQgMTg1OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 185: the kernel wakes the worker at dawn",
        "cm91bmQgMTg1OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 185: service latency drops after the patch",
        "cm91bmQgMTg1OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 185: the library caches every vector it sees",
        "cm91bmQgMTg1OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 185: agents argue then the debate resolves",
        "cm91bmQgMTg1OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 185: the filter keeps only strong matches",
        "cm91bmQgMTg1OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 185: the model answers with a short reply",
        "cm91bmQgMTg1OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 185: the recorder stores the reasoning trace",
        "cm91bmQgMTg1OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 185: the angel watches the processor run",
        "cm91bmQgMTg1OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 185: angle of the vector decides the match",
        "cm91bmQgMTg1OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 185: the candle burns twice as long at night",
        "cm91bmQgMTg1OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 185: a mirror of the universe in one line",
        "cm91bmQgMTg1OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 185: the queue drains before the storm", "cm91bmQgMTg1OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
