"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten142kitten142", "a2l0dGVuMTQya2l0dGVuMTQy"),
    ("kitten142sitting142", "a2l0dGVuMTQyc2l0dGluZzE0Mg"),
    ("kitten142agent142", "a2l0dGVuMTQyYWdlbnQxNDI"),
    ("kitten142angle142", "a2l0dGVuMTQyYW5nbGUxNDI"),
    ("sitting142angle142", "c2l0dGluZzE0MmFuZ2xlMTQy"),
    ("sitting142universe142", "c2l0dGluZzE0MnVuaXZlcnNlMTQy"),
    ("sitting142memory142", "c2l0dGluZzE0Mm1lbW9yeTE0Mg"),
    ("sitting142stream142", "c2l0dGluZzE0MnN0cmVhbTE0Mg"),
    ("agent142stream142", "YWdlbnQxNDJzdHJlYW0xNDI"),
    ("agent142context142", "YWdlbnQxNDJjb250ZXh0MTQy"),
    ("agent142knowledge142", "YWdlbnQxNDJrbm93bGVkZ2UxNDI"),
    ("agent142vector142", "YWdlbnQxNDJ2ZWN0b3IxNDI"),
    ("angle142vector142", "YW5nbGUxNDJ2ZWN0b3IxNDI"),
    ("angle142processor142", "YW5nbGUxNDJwcm9jZXNzb3IxNDI"),
    ("angle142reasoning142", "YW5nbGUxNDJyZWFzb25pbmcxNDI"),
    ("angle142machine142", "YW5nbGUxNDJtYWNoaW5lMTQy"),
    ("universe142machine142", "dW5pdmVyc2UxNDJtYWNoaW5lMTQy"),
    ("universe142learning142", "dW5pdmVyc2UxNDJsZWFybmluZzE0Mg"),
    ("universe142model142", "dW5pdmVyc2UxNDJtb2RlbDE0Mg"),
    ("universe142token142", "dW5pdmVyc2UxNDJ0b2tlbjE0Mg"),
    ("memory142token142", "bWVtb3J5MTQydG9rZW4xNDI"),
    ("memory142prompt142", "bWVtb3J5MTQycHJvbXB0MTQy"),
    ("memory142session142", "bWVtb3J5MTQyc2Vzc2lvbjE0Mg"),
    ("memory142library142", "bWVtb3J5MTQybGlicmFyeTE0Mg"),
    ("stream142library142", "c3RyZWFtMTQybGlicmFyeTE0Mg"),
    ("stream142service142", "c3RyZWFtMTQyc2VydmljZTE0Mg"),
    ("stream142gateway142", "c3RyZWFtMTQyZ2F0ZXdheTE0Mg"),
    ("stream142storage142", "c3RyZWFtMTQyc3RvcmFnZTE0Mg"),
    ("context142storage142", "Y29udGV4dDE0MnN0b3JhZ2UxNDI"),
    ("context142network142", "Y29udGV4dDE0Mm5ldHdvcmsxNDI"),
    ("context142latency142", "Y29udGV4dDE0MmxhdGVuY3kxNDI"),
    ("context142buffer142", "Y29udGV4dDE0MmJ1ZmZlcjE0Mg"),
    ("knowledge142buffer142", "a25vd2xlZGdlMTQyYnVmZmVyMTQy"),
    ("knowledge142queue142", "a25vd2xlZGdlMTQycXVldWUxNDI"),
    ("knowledge142worker142", "a25vd2xlZGdlMTQyd29ya2VyMTQy"),
    ("knowledge142kernel142", "a25vd2xlZGdlMTQya2VybmVsMTQy"),
    ("vector142kernel142", "dmVjdG9yMTQya2VybmVsMTQy"),
    ("vector142signal142", "dmVjdG9yMTQyc2lnbmFsMTQy"),
    ("vector142packet142", "dmVjdG9yMTQycGFja2V0MTQy"),
    ("vector142router142", "dmVjdG9yMTQycm91dGVyMTQy"),
    ("processor142router142", "cHJvY2Vzc29yMTQycm91dGVyMTQy"),
    ("processor142cluster142", "cHJvY2Vzc29yMTQyY2x1c3RlcjE0Mg"),
    ("processor142mirror142", "cHJvY2Vzc29yMTQybWlycm9yMTQy"),
    ("processor142filter142", "cHJvY2Vzc29yMTQyZmlsdGVyMTQy"),
    ("reasoning142filter142", "cmVhc29uaW5nMTQyZmlsdGVyMTQy"),
    ("reasoning142ranking142", "cmVhc29uaW5nMTQycmFua2luZzE0Mg"),
    ("reasoning142encoding142", "cmVhc29uaW5nMTQyZW5jb2RpbmcxNDI"),
    ("reasoning142mapping142", "cmVhc29uaW5nMTQybWFwcGluZzE0Mg"),
    ("machine142mapping142", "bWFjaGluZTE0Mm1hcHBpbmcxNDI"),
    ("machine142record142", "bWFjaGluZTE0MnJlY29yZDE0Mg"),
    ("machine142candle142", "bWFjaGluZTE0MmNhbmRsZTE0Mg"),
    ("machine142thread142", "bWFjaGluZTE0MnRocmVhZDE0Mg"),
    ("learning142thread142", "bGVhcm5pbmcxNDJ0aHJlYWQxNDI"),
    ("learning142kitten142", "bGVhcm5pbmcxNDJraXR0ZW4xNDI"),
    ("learning142sitting142", "bGVhcm5pbmcxNDJzaXR0aW5nMTQy"),
    ("learning142agent142", "bGVhcm5pbmcxNDJhZ2VudDE0Mg"),
    ("model142agent142", "bW9kZWwxNDJhZ2VudDE0Mg"),
    ("model142angle142", "bW9kZWwxNDJhbmdsZTE0Mg"),
    ("model142universe142", "bW9kZWwxNDJ1bml2ZXJzZTE0Mg"),
    ("model142memory142", "bW9kZWwxNDJtZW1vcnkxNDI"),
    ("token142memory142", "dG9rZW4xNDJtZW1vcnkxNDI"),
    ("token142stream142", "dG9rZW4xNDJzdHJlYW0xNDI"),
    ("token142context142", "dG9rZW4xNDJjb250ZXh0MTQy"),
    ("token142knowledge142", "dG9rZW4xNDJrbm93bGVkZ2UxNDI"),
    ("prompt142knowledge142", "cHJvbXB0MTQya25vd2xlZGdlMTQy"),
    ("prompt142vector142", "cHJvbXB0MTQydmVjdG9yMTQy"),
    ("prompt142processor142", "cHJvbXB0MTQycHJvY2Vzc29yMTQy"),
    ("prompt142reasoning142", "cHJvbXB0MTQycmVhc29uaW5nMTQy"),
    ("session142reasoning142", "c2Vzc2lvbjE0MnJlYXNvbmluZzE0Mg"),
    ("session142machine142", "c2Vzc2lvbjE0Mm1hY2hpbmUxNDI"),
    ("session142learning142", "c2Vzc2lvbjE0MmxlYXJuaW5nMTQy"),
    ("session142model142", "c2Vzc2lvbjE0Mm1vZGVsMTQy"),
    ("library142model142", "bGlicmFyeTE0Mm1vZGVsMTQy"),
    ("library142token142", "bGlicmFyeTE0MnRva2VuMTQy"),
    ("library142prompt142", "bGlicmFyeTE0MnByb21wdDE0Mg"),
    ("library142session142", "bGlicmFyeTE0MnNlc3Npb24xNDI"),
    ("service142session142", "c2VydmljZTE0MnNlc3Npb24xNDI"),
    ("service142library142", "c2VydmljZTE0MmxpYnJhcnkxNDI"),
    ("service142service142", "c2VydmljZTE0MnNlcnZpY2UxNDI"),
    ("service142gateway142", "c2VydmljZTE0MmdhdGV3YXkxNDI"),
    ("gateway142gateway142", "Z2F0ZXdheTE0MmdhdGV3YXkxNDI"),
    ("gateway142storage142", "Z2F0ZXdheTE0MnN0b3JhZ2UxNDI"),
    ("gateway142network142", "Z2F0ZXdheTE0Mm5ldHdvcmsxNDI"),
    ("gateway142latency142", "Z2F0ZXdheTE0MmxhdGVuY3kxNDI"),
    ("storage142latency142", "c3RvcmFnZTE0MmxhdGVuY3kxNDI"),
    ("storage142buffer142", "c3RvcmFnZTE0MmJ1ZmZlcjE0Mg"),
    ("storage142queue142", "c3RvcmFnZTE0MnF1ZXVlMTQy"),
    ("storage142worker142", "c3RvcmFnZTE0MndvcmtlcjE0Mg"),
    ("network142worker142", "bmV0d29yazE0MndvcmtlcjE0Mg"),
    ("network142kernel142", "bmV0d29yazE0Mmtlcm5lbDE0Mg"),
    ("network142signal142", "bmV0d29yazE0MnNpZ25hbDE0Mg"),
    ("network142packet142", "bmV0d29yazE0MnBhY2tldDE0Mg"),
    ("latency142packet142", "bGF0ZW5jeTE0MnBhY2tldDE0Mg"),
    ("latency142router142", "bGF0ZW5jeTE0MnJvdXRlcjE0Mg"),
    ("latency142cluster142", "bGF0ZW5jeTE0MmNsdXN0ZXIxNDI"),
    ("latency142mirror142", "bGF0ZW5jeTE0Mm1pcnJvcjE0Mg"),
    ("buffer142mirror142", "YnVmZmVyMTQybWlycm9yMTQy"),
    ("buffer142filter142", "YnVmZmVyMTQyZmlsdGVyMTQy"),
    ("buffer142ranking142", "YnVmZmVyMTQycmFua2luZzE0Mg"),
    ("buffer142encoding142", "YnVmZmVyMTQyZW5jb2RpbmcxNDI"),
    ("queue142encoding142", "cXVldWUxNDJlbmNvZGluZzE0Mg"),
    ("queue142mapping142", "cXVldWUxNDJtYXBwaW5nMTQy"),
    ("queue142record142", "cXVldWUxNDJyZWNvcmQxNDI"),
    ("queue142candle142", "cXVldWUxNDJjYW5kbGUxNDI"),
    ("worker142candle142", "d29ya2VyMTQyY2FuZGxlMTQy"),
    ("worker142thread142", "d29ya2VyMTQydGhyZWFkMTQy"),
    ("worker142kitten142", "d29ya2VyMTQya2l0dGVuMTQy"),
    ("worker142sitting142", "d29ya2VyMTQyc2l0dGluZzE0Mg"),
    ("kernel142sitting142", "a2VybmVsMTQyc2l0dGluZzE0Mg"),
    ("kernel142agent142", "a2VybmVsMTQyYWdlbnQxNDI"),
    ("kernel142angle142", "a2VybmVsMTQyYW5nbGUxNDI"),
    ("kernel142universe142", "a2VybmVsMTQydW5pdmVyc2UxNDI"),
    ("signal142universe142", "c2lnbmFsMTQydW5pdmVyc2UxNDI"),
    ("signal142memory142", "c2lnbmFsMTQybWVtb3J5MTQy"),
    ("signal142stream142", "c2lnbmFsMTQyc3RyZWFtMTQy"),
    ("signal142context142", "c2lnbmFsMTQyY29udGV4dDE0Mg"),
    ("packet142context142", "cGFja2V0MTQyY29udGV4dDE0Mg"),
    ("packet142knowledge142", "cGFja2V0MTQya25vd2xlZGdlMTQy"),
    ("packet142vector142", "cGFja2V0MTQydmVjdG9yMTQy"),
    ("packet142processor142", "cGFja2V0MTQycHJvY2Vzc29yMTQy"),
    ("router142processor142", "cm91dGVyMTQycHJvY2Vzc29yMTQy"),
    ("router142reasoning142", "cm91dGVyMTQycmVhc29uaW5nMTQy"),
    ("router142machine142", "cm91dGVyMTQybWFjaGluZTE0Mg"),
    ("router142learning142", "cm91dGVyMTQybGVhcm5pbmcxNDI"),
    ("cluster142learning142", "Y2x1c3RlcjE0MmxlYXJuaW5nMTQy"),
    ("cluster142model142", "Y2x1c3RlcjE0Mm1vZGVsMTQy"),
    ("cluster142token142", "Y2x1c3RlcjE0MnRva2VuMTQy"),
    ("cluster142prompt142", "Y2x1c3RlcjE0MnByb21wdDE0Mg"),
    ("mirror142prompt142", "bWlycm9yMTQycHJvbXB0MTQy"),
    ("mirror142session142", "bWlycm9yMTQyc2Vzc2lvbjE0Mg"),
    ("mirror142library142", "bWlycm9yMTQybGlicmFyeTE0Mg"),
    ("mirror142service142", "bWlycm9yMTQyc2VydmljZTE0Mg"),
    ("filter142service142", "ZmlsdGVyMTQyc2VydmljZTE0Mg"),
    ("filter142gateway142", "ZmlsdGVyMTQyZ2F0ZXdheTE0Mg"),
    ("filter142storage142", "ZmlsdGVyMTQyc3RvcmFnZTE0Mg"),
    ("filter142network142", "ZmlsdGVyMTQybmV0d29yazE0Mg"),
    ("ranking142network142", "cmFua2luZzE0Mm5ldHdvcmsxNDI"),
    ("ranking142latency142", "cmFua2luZzE0MmxhdGVuY3kxNDI"),
    ("ranking142buffer142", "cmFua2luZzE0MmJ1ZmZlcjE0Mg"),
    ("ranking142queue142", "cmFua2luZzE0MnF1ZXVlMTQy"),
    ("encoding142queue142", "ZW5jb2RpbmcxNDJxdWV1ZTE0Mg"),
    ("encoding142worker142", "ZW5jb2RpbmcxNDJ3b3JrZXIxNDI"),
    ("encoding142kernel142", "ZW5jb2RpbmcxNDJrZXJuZWwxNDI"),
    ("encoding142signal142", "ZW5jb2RpbmcxNDJzaWduYWwxNDI"),
    ("mapping142signal142", "bWFwcGluZzE0MnNpZ25hbDE0Mg"),
    ("mapping142packet142", "bWFwcGluZzE0MnBhY2tldDE0Mg"),
    ("mapping142router142", "bWFwcGluZzE0MnJvdXRlcjE0Mg"),
    ("mapping142cluster142", "bWFwcGluZzE0MmNsdXN0ZXIxNDI"),
    ("record142cluster142", "cmVjb3JkMTQyY2x1c3RlcjE0Mg"),
    ("record142mirror142", "cmVjb3JkMTQybWlycm9yMTQy"),
    ("record142filter142", "cmVjb3JkMTQyZmlsdGVyMTQy"),
    ("record142ranking142", "cmVjb3JkMTQycmFua2luZzE0Mg"),
    ("candle142ranking142", "Y2FuZGxlMTQycmFua2luZzE0Mg"),
    ("candle142encoding142", "Y2FuZGxlMTQyZW5jb2RpbmcxNDI"),
    ("candle142mapping142", "Y2FuZGxlMTQybWFwcGluZzE0Mg"),
    ("candle142record142", "Y2FuZGxlMTQycmVjb3JkMTQy"),
    ("thread142record142", "dGhyZWFkMTQycmVjb3JkMTQy"),
    ("thread142candle142", "dGhyZWFkMTQyY2FuZGxlMTQy"),
    ("thread142thread142", "dGhyZWFkMTQydGhyZWFkMTQy"),
    ("thread142kitten142", "dGhyZWFkMTQya2l0dGVuMTQy"),
    (
        "round 142: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTQyOiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 142: agentuniverse is a framework for multi agents",
        "cm91bmQgMTQyOiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 142: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTQyOiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 142: the processor reads the record then stops",
        "cm91bmQgMTQyOiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 142: a worker pulls the next task from the queue",
        "cm91bmQgMTQyOiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 142: signals travel through the network layer",
        "cm91bmQgMTQyOiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 142: the gateway routes each request by policy",
        "cm91bmQgMTQyOiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 142: memory grows until the buffer is full",
        "cm91bmQgMTQyOiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 142: the cluster mirrors every packet twice",
        "cm91bmQgMTQyOiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 142: ranking uses tokens learned from the corpus",
        "cm91bmQgMTQyOiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 142: a long session ends when the candle dies",
        "cm91bmQgMTQyOiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 142: encode the prompt then map the result",
        "cm91bmQgMTQyOiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 142: the kernel wakes the worker at dawn",
        "cm91bmQgMTQyOiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 142: service latency drops after the patch",
        "cm91bmQgMTQyOiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 142: the library caches every vector it sees",
        "cm91bmQgMTQyOiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 142: agents argue then the debate resolves",
        "cm91bmQgMTQyOiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 142: the filter keeps only strong matches",
        "cm91bmQgMTQyOiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 142: the model answers with a short reply",
        "cm91bmQgMTQyOiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 142: the recorder stores the reasoning trace",
        "cm91bmQgMTQyOiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 142: the angel watches the processor run",
        "cm91bmQgMTQyOiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 142: angle of the vector decides the match",
        "cm91bmQgMTQyOiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 142: the candle burns twice as long at night",
        "cm91bmQgMTQyOiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 142: a mirror of the universe in one line",
        "cm91bmQgMTQyOiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 142: the queue drains before the storm", "cm91bmQgMTQyOiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
