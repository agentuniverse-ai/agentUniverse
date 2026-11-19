"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten152kitten152", "a2l0dGVuMTUya2l0dGVuMTUy"),
    ("kitten152sitting152", "a2l0dGVuMTUyc2l0dGluZzE1Mg"),
    ("kitten152agent152", "a2l0dGVuMTUyYWdlbnQxNTI"),
    ("kitten152angle152", "a2l0dGVuMTUyYW5nbGUxNTI"),
    ("sitting152angle152", "c2l0dGluZzE1MmFuZ2xlMTUy"),
    ("sitting152universe152", "c2l0dGluZzE1MnVuaXZlcnNlMTUy"),
    ("sitting152memory152", "c2l0dGluZzE1Mm1lbW9yeTE1Mg"),
    ("sitting152stream152", "c2l0dGluZzE1MnN0cmVhbTE1Mg"),
    ("agent152stream152", "YWdlbnQxNTJzdHJlYW0xNTI"),
    ("agent152context152", "YWdlbnQxNTJjb250ZXh0MTUy"),
    ("agent152knowledge152", "YWdlbnQxNTJrbm93bGVkZ2UxNTI"),
    ("agent152vector152", "YWdlbnQxNTJ2ZWN0b3IxNTI"),
    ("angle152vector152", "YW5nbGUxNTJ2ZWN0b3IxNTI"),
    ("angle152processor152", "YW5nbGUxNTJwcm9jZXNzb3IxNTI"),
    ("angle152reasoning152", "YW5nbGUxNTJyZWFzb25pbmcxNTI"),
    ("angle152machine152", "YW5nbGUxNTJtYWNoaW5lMTUy"),
    ("universe152machine152", "dW5pdmVyc2UxNTJtYWNoaW5lMTUy"),
    ("universe152learning152", "dW5pdmVyc2UxNTJsZWFybmluZzE1Mg"),
    ("universe152model152", "dW5pdmVyc2UxNTJtb2RlbDE1Mg"),
    ("universe152token152", "dW5pdmVyc2UxNTJ0b2tlbjE1Mg"),
    ("memory152token152", "bWVtb3J5MTUydG9rZW4xNTI"),
    ("memory152prompt152", "bWVtb3J5MTUycHJvbXB0MTUy"),
    ("memory152session152", "bWVtb3J5MTUyc2Vzc2lvbjE1Mg"),
    ("memory152library152", "bWVtb3J5MTUybGlicmFyeTE1Mg"),
    ("stream152library152", "c3RyZWFtMTUybGlicmFyeTE1Mg"),
    ("stream152service152", "c3RyZWFtMTUyc2VydmljZTE1Mg"),
    ("stream152gateway152", "c3RyZWFtMTUyZ2F0ZXdheTE1Mg"),
    ("stream152storage152", "c3RyZWFtMTUyc3RvcmFnZTE1Mg"),
    ("context152storage152", "Y29udGV4dDE1MnN0b3JhZ2UxNTI"),
    ("context152network152", "Y29udGV4dDE1Mm5ldHdvcmsxNTI"),
    ("context152latency152", "Y29udGV4dDE1MmxhdGVuY3kxNTI"),
    ("context152buffer152", "Y29udGV4dDE1MmJ1ZmZlcjE1Mg"),
    ("knowledge152buffer152", "a25vd2xlZGdlMTUyYnVmZmVyMTUy"),
    ("knowledge152queue152", "a25vd2xlZGdlMTUycXVldWUxNTI"),
    ("knowledge152worker152", "a25vd2xlZGdlMTUyd29ya2VyMTUy"),
    ("knowledge152kernel152", "a25vd2xlZGdlMTUya2VybmVsMTUy"),
    ("vector152kernel152", "dmVjdG9yMTUya2VybmVsMTUy"),
    ("vector152signal152", "dmVjdG9yMTUyc2lnbmFsMTUy"),
    ("vector152packet152", "dmVjdG9yMTUycGFja2V0MTUy"),
    ("vector152router152", "dmVjdG9yMTUycm91dGVyMTUy"),
    ("processor152router152", "cHJvY2Vzc29yMTUycm91dGVyMTUy"),
    ("processor152cluster152", "cHJvY2Vzc29yMTUyY2x1c3RlcjE1Mg"),
    ("processor152mirror152", "cHJvY2Vzc29yMTUybWlycm9yMTUy"),
    ("processor152filter152", "cHJvY2Vzc29yMTUyZmlsdGVyMTUy"),
    ("reasoning152filter152", "cmVhc29uaW5nMTUyZmlsdGVyMTUy"),
    ("reasoning152ranking152", "cmVhc29uaW5nMTUycmFua2luZzE1Mg"),
    ("reasoning152encoding152", "cmVhc29uaW5nMTUyZW5jb2RpbmcxNTI"),
    ("reasoning152mapping152", "cmVhc29uaW5nMTUybWFwcGluZzE1Mg"),
    ("machine152mapping152", "bWFjaGluZTE1Mm1hcHBpbmcxNTI"),
    ("machine152record152", "bWFjaGluZTE1MnJlY29yZDE1Mg"),
    ("machine152candle152", "bWFjaGluZTE1MmNhbmRsZTE1Mg"),
    ("machine152thread152", "bWFjaGluZTE1MnRocmVhZDE1Mg"),
    ("learning152thread152", "bGVhcm5pbmcxNTJ0aHJlYWQxNTI"),
    ("learning152kitten152", "bGVhcm5pbmcxNTJraXR0ZW4xNTI"),
    ("learning152sitting152", "bGVhcm5pbmcxNTJzaXR0aW5nMTUy"),
    ("learning152agent152", "bGVhcm5pbmcxNTJhZ2VudDE1Mg"),
    ("model152agent152", "bW9kZWwxNTJhZ2VudDE1Mg"),
    ("model152angle152", "bW9kZWwxNTJhbmdsZTE1Mg"),
    ("model152universe152", "bW9kZWwxNTJ1bml2ZXJzZTE1Mg"),
    ("model152memory152", "bW9kZWwxNTJtZW1vcnkxNTI"),
    ("token152memory152", "dG9rZW4xNTJtZW1vcnkxNTI"),
    ("token152stream152", "dG9rZW4xNTJzdHJlYW0xNTI"),
    ("token152context152", "dG9rZW4xNTJjb250ZXh0MTUy"),
    ("token152knowledge152", "dG9rZW4xNTJrbm93bGVkZ2UxNTI"),
    ("prompt152knowledge152", "cHJvbXB0MTUya25vd2xlZGdlMTUy"),
    ("prompt152vector152", "cHJvbXB0MTUydmVjdG9yMTUy"),
    ("prompt152processor152", "cHJvbXB0MTUycHJvY2Vzc29yMTUy"),
    ("prompt152reasoning152", "cHJvbXB0MTUycmVhc29uaW5nMTUy"),
    ("session152reasoning152", "c2Vzc2lvbjE1MnJlYXNvbmluZzE1Mg"),
    ("session152machine152", "c2Vzc2lvbjE1Mm1hY2hpbmUxNTI"),
    ("session152learning152", "c2Vzc2lvbjE1MmxlYXJuaW5nMTUy"),
    ("session152model152", "c2Vzc2lvbjE1Mm1vZGVsMTUy"),
    ("library152model152", "bGlicmFyeTE1Mm1vZGVsMTUy"),
    ("library152token152", "bGlicmFyeTE1MnRva2VuMTUy"),
    ("library152prompt152", "bGlicmFyeTE1MnByb21wdDE1Mg"),
    ("library152session152", "bGlicmFyeTE1MnNlc3Npb24xNTI"),
    ("service152session152", "c2VydmljZTE1MnNlc3Npb24xNTI"),
    ("service152library152", "c2VydmljZTE1MmxpYnJhcnkxNTI"),
    ("service152service152", "c2VydmljZTE1MnNlcnZpY2UxNTI"),
    ("service152gateway152", "c2VydmljZTE1MmdhdGV3YXkxNTI"),
    ("gateway152gateway152", "Z2F0ZXdheTE1MmdhdGV3YXkxNTI"),
    ("gateway152storage152", "Z2F0ZXdheTE1MnN0b3JhZ2UxNTI"),
    ("gateway152network152", "Z2F0ZXdheTE1Mm5ldHdvcmsxNTI"),
    ("gateway152latency152", "Z2F0ZXdheTE1MmxhdGVuY3kxNTI"),
    ("storage152latency152", "c3RvcmFnZTE1MmxhdGVuY3kxNTI"),
    ("storage152buffer152", "c3RvcmFnZTE1MmJ1ZmZlcjE1Mg"),
    ("storage152queue152", "c3RvcmFnZTE1MnF1ZXVlMTUy"),
    ("storage152worker152", "c3RvcmFnZTE1MndvcmtlcjE1Mg"),
    ("network152worker152", "bmV0d29yazE1MndvcmtlcjE1Mg"),
    ("network152kernel152", "bmV0d29yazE1Mmtlcm5lbDE1Mg"),
    ("network152signal152", "bmV0d29yazE1MnNpZ25hbDE1Mg"),
    ("network152packet152", "bmV0d29yazE1MnBhY2tldDE1Mg"),
    ("latency152packet152", "bGF0ZW5jeTE1MnBhY2tldDE1Mg"),
    ("latency152router152", "bGF0ZW5jeTE1MnJvdXRlcjE1Mg"),
    ("latency152cluster152", "bGF0ZW5jeTE1MmNsdXN0ZXIxNTI"),
    ("latency152mirror152", "bGF0ZW5jeTE1Mm1pcnJvcjE1Mg"),
    ("buffer152mirror152", "YnVmZmVyMTUybWlycm9yMTUy"),
    ("buffer152filter152", "YnVmZmVyMTUyZmlsdGVyMTUy"),
    ("buffer152ranking152", "YnVmZmVyMTUycmFua2luZzE1Mg"),
    ("buffer152encoding152", "YnVmZmVyMTUyZW5jb2RpbmcxNTI"),
    ("queue152encoding152", "cXVldWUxNTJlbmNvZGluZzE1Mg"),
    ("queue152mapping152", "cXVldWUxNTJtYXBwaW5nMTUy"),
    ("queue152record152", "cXVldWUxNTJyZWNvcmQxNTI"),
    ("queue152candle152", "cXVldWUxNTJjYW5kbGUxNTI"),
    ("worker152candle152", "d29ya2VyMTUyY2FuZGxlMTUy"),
    ("worker152thread152", "d29ya2VyMTUydGhyZWFkMTUy"),
    ("worker152kitten152", "d29ya2VyMTUya2l0dGVuMTUy"),
    ("worker152sitting152", "d29ya2VyMTUyc2l0dGluZzE1Mg"),
    ("kernel152sitting152", "a2VybmVsMTUyc2l0dGluZzE1Mg"),
    ("kernel152agent152", "a2VybmVsMTUyYWdlbnQxNTI"),
    ("kernel152angle152", "a2VybmVsMTUyYW5nbGUxNTI"),
    ("kernel152universe152", "a2VybmVsMTUydW5pdmVyc2UxNTI"),
    ("signal152universe152", "c2lnbmFsMTUydW5pdmVyc2UxNTI"),
    ("signal152memory152", "c2lnbmFsMTUybWVtb3J5MTUy"),
    ("signal152stream152", "c2lnbmFsMTUyc3RyZWFtMTUy"),
    ("signal152context152", "c2lnbmFsMTUyY29udGV4dDE1Mg"),
    ("packet152context152", "cGFja2V0MTUyY29udGV4dDE1Mg"),
    ("packet152knowledge152", "cGFja2V0MTUya25vd2xlZGdlMTUy"),
    ("packet152vector152", "cGFja2V0MTUydmVjdG9yMTUy"),
    ("packet152processor152", "cGFja2V0MTUycHJvY2Vzc29yMTUy"),
    ("router152processor152", "cm91dGVyMTUycHJvY2Vzc29yMTUy"),
    ("router152reasoning152", "cm91dGVyMTUycmVhc29uaW5nMTUy"),
    ("router152machine152", "cm91dGVyMTUybWFjaGluZTE1Mg"),
    ("router152learning152", "cm91dGVyMTUybGVhcm5pbmcxNTI"),
    ("cluster152learning152", "Y2x1c3RlcjE1MmxlYXJuaW5nMTUy"),
    ("cluster152model152", "Y2x1c3RlcjE1Mm1vZGVsMTUy"),
    ("cluster152token152", "Y2x1c3RlcjE1MnRva2VuMTUy"),
    ("cluster152prompt152", "Y2x1c3RlcjE1MnByb21wdDE1Mg"),
    ("mirror152prompt152", "bWlycm9yMTUycHJvbXB0MTUy"),
    ("mirror152session152", "bWlycm9yMTUyc2Vzc2lvbjE1Mg"),
    ("mirror152library152", "bWlycm9yMTUybGlicmFyeTE1Mg"),
    ("mirror152service152", "bWlycm9yMTUyc2VydmljZTE1Mg"),
    ("filter152service152", "ZmlsdGVyMTUyc2VydmljZTE1Mg"),
    ("filter152gateway152", "ZmlsdGVyMTUyZ2F0ZXdheTE1Mg"),
    ("filter152storage152", "ZmlsdGVyMTUyc3RvcmFnZTE1Mg"),
    ("filter152network152", "ZmlsdGVyMTUybmV0d29yazE1Mg"),
    ("ranking152network152", "cmFua2luZzE1Mm5ldHdvcmsxNTI"),
    ("ranking152latency152", "cmFua2luZzE1MmxhdGVuY3kxNTI"),
    ("ranking152buffer152", "cmFua2luZzE1MmJ1ZmZlcjE1Mg"),
    ("ranking152queue152", "cmFua2luZzE1MnF1ZXVlMTUy"),
    ("encoding152queue152", "ZW5jb2RpbmcxNTJxdWV1ZTE1Mg"),
    ("encoding152worker152", "ZW5jb2RpbmcxNTJ3b3JrZXIxNTI"),
    ("encoding152kernel152", "ZW5jb2RpbmcxNTJrZXJuZWwxNTI"),
    ("encoding152signal152", "ZW5jb2RpbmcxNTJzaWduYWwxNTI"),
    ("mapping152signal152", "bWFwcGluZzE1MnNpZ25hbDE1Mg"),
    ("mapping152packet152", "bWFwcGluZzE1MnBhY2tldDE1Mg"),
    ("mapping152router152", "bWFwcGluZzE1MnJvdXRlcjE1Mg"),
    ("mapping152cluster152", "bWFwcGluZzE1MmNsdXN0ZXIxNTI"),
    ("record152cluster152", "cmVjb3JkMTUyY2x1c3RlcjE1Mg"),
    ("record152mirror152", "cmVjb3JkMTUybWlycm9yMTUy"),
    ("record152filter152", "cmVjb3JkMTUyZmlsdGVyMTUy"),
    ("record152ranking152", "cmVjb3JkMTUycmFua2luZzE1Mg"),
    ("candle152ranking152", "Y2FuZGxlMTUycmFua2luZzE1Mg"),
    ("candle152encoding152", "Y2FuZGxlMTUyZW5jb2RpbmcxNTI"),
    ("candle152mapping152", "Y2FuZGxlMTUybWFwcGluZzE1Mg"),
    ("candle152record152", "Y2FuZGxlMTUycmVjb3JkMTUy"),
    ("thread152record152", "dGhyZWFkMTUycmVjb3JkMTUy"),
    ("thread152candle152", "dGhyZWFkMTUyY2FuZGxlMTUy"),
    ("thread152thread152", "dGhyZWFkMTUydGhyZWFkMTUy"),
    ("thread152kitten152", "dGhyZWFkMTUya2l0dGVuMTUy"),
    (
        "round 152: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTUyOiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 152: agentuniverse is a framework for multi agents",
        "cm91bmQgMTUyOiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 152: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTUyOiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 152: the processor reads the record then stops",
        "cm91bmQgMTUyOiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 152: a worker pulls the next task from the queue",
        "cm91bmQgMTUyOiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 152: signals travel through the network layer",
        "cm91bmQgMTUyOiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 152: the gateway routes each request by policy",
        "cm91bmQgMTUyOiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 152: memory grows until the buffer is full",
        "cm91bmQgMTUyOiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 152: the cluster mirrors every packet twice",
        "cm91bmQgMTUyOiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 152: ranking uses tokens learned from the corpus",
        "cm91bmQgMTUyOiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 152: a long session ends when the candle dies",
        "cm91bmQgMTUyOiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 152: encode the prompt then map the result",
        "cm91bmQgMTUyOiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 152: the kernel wakes the worker at dawn",
        "cm91bmQgMTUyOiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 152: service latency drops after the patch",
        "cm91bmQgMTUyOiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 152: the library caches every vector it sees",
        "cm91bmQgMTUyOiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 152: agents argue then the debate resolves",
        "cm91bmQgMTUyOiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 152: the filter keeps only strong matches",
        "cm91bmQgMTUyOiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 152: the model answers with a short reply",
        "cm91bmQgMTUyOiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 152: the recorder stores the reasoning trace",
        "cm91bmQgMTUyOiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 152: the angel watches the processor run",
        "cm91bmQgMTUyOiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 152: angle of the vector decides the match",
        "cm91bmQgMTUyOiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 152: the candle burns twice as long at night",
        "cm91bmQgMTUyOiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 152: a mirror of the universe in one line",
        "cm91bmQgMTUyOiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 152: the queue drains before the storm", "cm91bmQgMTUyOiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
