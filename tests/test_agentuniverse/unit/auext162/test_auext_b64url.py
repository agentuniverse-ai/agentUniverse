"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten162kitten162", "a2l0dGVuMTYya2l0dGVuMTYy"),
    ("kitten162sitting162", "a2l0dGVuMTYyc2l0dGluZzE2Mg"),
    ("kitten162agent162", "a2l0dGVuMTYyYWdlbnQxNjI"),
    ("kitten162angle162", "a2l0dGVuMTYyYW5nbGUxNjI"),
    ("sitting162angle162", "c2l0dGluZzE2MmFuZ2xlMTYy"),
    ("sitting162universe162", "c2l0dGluZzE2MnVuaXZlcnNlMTYy"),
    ("sitting162memory162", "c2l0dGluZzE2Mm1lbW9yeTE2Mg"),
    ("sitting162stream162", "c2l0dGluZzE2MnN0cmVhbTE2Mg"),
    ("agent162stream162", "YWdlbnQxNjJzdHJlYW0xNjI"),
    ("agent162context162", "YWdlbnQxNjJjb250ZXh0MTYy"),
    ("agent162knowledge162", "YWdlbnQxNjJrbm93bGVkZ2UxNjI"),
    ("agent162vector162", "YWdlbnQxNjJ2ZWN0b3IxNjI"),
    ("angle162vector162", "YW5nbGUxNjJ2ZWN0b3IxNjI"),
    ("angle162processor162", "YW5nbGUxNjJwcm9jZXNzb3IxNjI"),
    ("angle162reasoning162", "YW5nbGUxNjJyZWFzb25pbmcxNjI"),
    ("angle162machine162", "YW5nbGUxNjJtYWNoaW5lMTYy"),
    ("universe162machine162", "dW5pdmVyc2UxNjJtYWNoaW5lMTYy"),
    ("universe162learning162", "dW5pdmVyc2UxNjJsZWFybmluZzE2Mg"),
    ("universe162model162", "dW5pdmVyc2UxNjJtb2RlbDE2Mg"),
    ("universe162token162", "dW5pdmVyc2UxNjJ0b2tlbjE2Mg"),
    ("memory162token162", "bWVtb3J5MTYydG9rZW4xNjI"),
    ("memory162prompt162", "bWVtb3J5MTYycHJvbXB0MTYy"),
    ("memory162session162", "bWVtb3J5MTYyc2Vzc2lvbjE2Mg"),
    ("memory162library162", "bWVtb3J5MTYybGlicmFyeTE2Mg"),
    ("stream162library162", "c3RyZWFtMTYybGlicmFyeTE2Mg"),
    ("stream162service162", "c3RyZWFtMTYyc2VydmljZTE2Mg"),
    ("stream162gateway162", "c3RyZWFtMTYyZ2F0ZXdheTE2Mg"),
    ("stream162storage162", "c3RyZWFtMTYyc3RvcmFnZTE2Mg"),
    ("context162storage162", "Y29udGV4dDE2MnN0b3JhZ2UxNjI"),
    ("context162network162", "Y29udGV4dDE2Mm5ldHdvcmsxNjI"),
    ("context162latency162", "Y29udGV4dDE2MmxhdGVuY3kxNjI"),
    ("context162buffer162", "Y29udGV4dDE2MmJ1ZmZlcjE2Mg"),
    ("knowledge162buffer162", "a25vd2xlZGdlMTYyYnVmZmVyMTYy"),
    ("knowledge162queue162", "a25vd2xlZGdlMTYycXVldWUxNjI"),
    ("knowledge162worker162", "a25vd2xlZGdlMTYyd29ya2VyMTYy"),
    ("knowledge162kernel162", "a25vd2xlZGdlMTYya2VybmVsMTYy"),
    ("vector162kernel162", "dmVjdG9yMTYya2VybmVsMTYy"),
    ("vector162signal162", "dmVjdG9yMTYyc2lnbmFsMTYy"),
    ("vector162packet162", "dmVjdG9yMTYycGFja2V0MTYy"),
    ("vector162router162", "dmVjdG9yMTYycm91dGVyMTYy"),
    ("processor162router162", "cHJvY2Vzc29yMTYycm91dGVyMTYy"),
    ("processor162cluster162", "cHJvY2Vzc29yMTYyY2x1c3RlcjE2Mg"),
    ("processor162mirror162", "cHJvY2Vzc29yMTYybWlycm9yMTYy"),
    ("processor162filter162", "cHJvY2Vzc29yMTYyZmlsdGVyMTYy"),
    ("reasoning162filter162", "cmVhc29uaW5nMTYyZmlsdGVyMTYy"),
    ("reasoning162ranking162", "cmVhc29uaW5nMTYycmFua2luZzE2Mg"),
    ("reasoning162encoding162", "cmVhc29uaW5nMTYyZW5jb2RpbmcxNjI"),
    ("reasoning162mapping162", "cmVhc29uaW5nMTYybWFwcGluZzE2Mg"),
    ("machine162mapping162", "bWFjaGluZTE2Mm1hcHBpbmcxNjI"),
    ("machine162record162", "bWFjaGluZTE2MnJlY29yZDE2Mg"),
    ("machine162candle162", "bWFjaGluZTE2MmNhbmRsZTE2Mg"),
    ("machine162thread162", "bWFjaGluZTE2MnRocmVhZDE2Mg"),
    ("learning162thread162", "bGVhcm5pbmcxNjJ0aHJlYWQxNjI"),
    ("learning162kitten162", "bGVhcm5pbmcxNjJraXR0ZW4xNjI"),
    ("learning162sitting162", "bGVhcm5pbmcxNjJzaXR0aW5nMTYy"),
    ("learning162agent162", "bGVhcm5pbmcxNjJhZ2VudDE2Mg"),
    ("model162agent162", "bW9kZWwxNjJhZ2VudDE2Mg"),
    ("model162angle162", "bW9kZWwxNjJhbmdsZTE2Mg"),
    ("model162universe162", "bW9kZWwxNjJ1bml2ZXJzZTE2Mg"),
    ("model162memory162", "bW9kZWwxNjJtZW1vcnkxNjI"),
    ("token162memory162", "dG9rZW4xNjJtZW1vcnkxNjI"),
    ("token162stream162", "dG9rZW4xNjJzdHJlYW0xNjI"),
    ("token162context162", "dG9rZW4xNjJjb250ZXh0MTYy"),
    ("token162knowledge162", "dG9rZW4xNjJrbm93bGVkZ2UxNjI"),
    ("prompt162knowledge162", "cHJvbXB0MTYya25vd2xlZGdlMTYy"),
    ("prompt162vector162", "cHJvbXB0MTYydmVjdG9yMTYy"),
    ("prompt162processor162", "cHJvbXB0MTYycHJvY2Vzc29yMTYy"),
    ("prompt162reasoning162", "cHJvbXB0MTYycmVhc29uaW5nMTYy"),
    ("session162reasoning162", "c2Vzc2lvbjE2MnJlYXNvbmluZzE2Mg"),
    ("session162machine162", "c2Vzc2lvbjE2Mm1hY2hpbmUxNjI"),
    ("session162learning162", "c2Vzc2lvbjE2MmxlYXJuaW5nMTYy"),
    ("session162model162", "c2Vzc2lvbjE2Mm1vZGVsMTYy"),
    ("library162model162", "bGlicmFyeTE2Mm1vZGVsMTYy"),
    ("library162token162", "bGlicmFyeTE2MnRva2VuMTYy"),
    ("library162prompt162", "bGlicmFyeTE2MnByb21wdDE2Mg"),
    ("library162session162", "bGlicmFyeTE2MnNlc3Npb24xNjI"),
    ("service162session162", "c2VydmljZTE2MnNlc3Npb24xNjI"),
    ("service162library162", "c2VydmljZTE2MmxpYnJhcnkxNjI"),
    ("service162service162", "c2VydmljZTE2MnNlcnZpY2UxNjI"),
    ("service162gateway162", "c2VydmljZTE2MmdhdGV3YXkxNjI"),
    ("gateway162gateway162", "Z2F0ZXdheTE2MmdhdGV3YXkxNjI"),
    ("gateway162storage162", "Z2F0ZXdheTE2MnN0b3JhZ2UxNjI"),
    ("gateway162network162", "Z2F0ZXdheTE2Mm5ldHdvcmsxNjI"),
    ("gateway162latency162", "Z2F0ZXdheTE2MmxhdGVuY3kxNjI"),
    ("storage162latency162", "c3RvcmFnZTE2MmxhdGVuY3kxNjI"),
    ("storage162buffer162", "c3RvcmFnZTE2MmJ1ZmZlcjE2Mg"),
    ("storage162queue162", "c3RvcmFnZTE2MnF1ZXVlMTYy"),
    ("storage162worker162", "c3RvcmFnZTE2MndvcmtlcjE2Mg"),
    ("network162worker162", "bmV0d29yazE2MndvcmtlcjE2Mg"),
    ("network162kernel162", "bmV0d29yazE2Mmtlcm5lbDE2Mg"),
    ("network162signal162", "bmV0d29yazE2MnNpZ25hbDE2Mg"),
    ("network162packet162", "bmV0d29yazE2MnBhY2tldDE2Mg"),
    ("latency162packet162", "bGF0ZW5jeTE2MnBhY2tldDE2Mg"),
    ("latency162router162", "bGF0ZW5jeTE2MnJvdXRlcjE2Mg"),
    ("latency162cluster162", "bGF0ZW5jeTE2MmNsdXN0ZXIxNjI"),
    ("latency162mirror162", "bGF0ZW5jeTE2Mm1pcnJvcjE2Mg"),
    ("buffer162mirror162", "YnVmZmVyMTYybWlycm9yMTYy"),
    ("buffer162filter162", "YnVmZmVyMTYyZmlsdGVyMTYy"),
    ("buffer162ranking162", "YnVmZmVyMTYycmFua2luZzE2Mg"),
    ("buffer162encoding162", "YnVmZmVyMTYyZW5jb2RpbmcxNjI"),
    ("queue162encoding162", "cXVldWUxNjJlbmNvZGluZzE2Mg"),
    ("queue162mapping162", "cXVldWUxNjJtYXBwaW5nMTYy"),
    ("queue162record162", "cXVldWUxNjJyZWNvcmQxNjI"),
    ("queue162candle162", "cXVldWUxNjJjYW5kbGUxNjI"),
    ("worker162candle162", "d29ya2VyMTYyY2FuZGxlMTYy"),
    ("worker162thread162", "d29ya2VyMTYydGhyZWFkMTYy"),
    ("worker162kitten162", "d29ya2VyMTYya2l0dGVuMTYy"),
    ("worker162sitting162", "d29ya2VyMTYyc2l0dGluZzE2Mg"),
    ("kernel162sitting162", "a2VybmVsMTYyc2l0dGluZzE2Mg"),
    ("kernel162agent162", "a2VybmVsMTYyYWdlbnQxNjI"),
    ("kernel162angle162", "a2VybmVsMTYyYW5nbGUxNjI"),
    ("kernel162universe162", "a2VybmVsMTYydW5pdmVyc2UxNjI"),
    ("signal162universe162", "c2lnbmFsMTYydW5pdmVyc2UxNjI"),
    ("signal162memory162", "c2lnbmFsMTYybWVtb3J5MTYy"),
    ("signal162stream162", "c2lnbmFsMTYyc3RyZWFtMTYy"),
    ("signal162context162", "c2lnbmFsMTYyY29udGV4dDE2Mg"),
    ("packet162context162", "cGFja2V0MTYyY29udGV4dDE2Mg"),
    ("packet162knowledge162", "cGFja2V0MTYya25vd2xlZGdlMTYy"),
    ("packet162vector162", "cGFja2V0MTYydmVjdG9yMTYy"),
    ("packet162processor162", "cGFja2V0MTYycHJvY2Vzc29yMTYy"),
    ("router162processor162", "cm91dGVyMTYycHJvY2Vzc29yMTYy"),
    ("router162reasoning162", "cm91dGVyMTYycmVhc29uaW5nMTYy"),
    ("router162machine162", "cm91dGVyMTYybWFjaGluZTE2Mg"),
    ("router162learning162", "cm91dGVyMTYybGVhcm5pbmcxNjI"),
    ("cluster162learning162", "Y2x1c3RlcjE2MmxlYXJuaW5nMTYy"),
    ("cluster162model162", "Y2x1c3RlcjE2Mm1vZGVsMTYy"),
    ("cluster162token162", "Y2x1c3RlcjE2MnRva2VuMTYy"),
    ("cluster162prompt162", "Y2x1c3RlcjE2MnByb21wdDE2Mg"),
    ("mirror162prompt162", "bWlycm9yMTYycHJvbXB0MTYy"),
    ("mirror162session162", "bWlycm9yMTYyc2Vzc2lvbjE2Mg"),
    ("mirror162library162", "bWlycm9yMTYybGlicmFyeTE2Mg"),
    ("mirror162service162", "bWlycm9yMTYyc2VydmljZTE2Mg"),
    ("filter162service162", "ZmlsdGVyMTYyc2VydmljZTE2Mg"),
    ("filter162gateway162", "ZmlsdGVyMTYyZ2F0ZXdheTE2Mg"),
    ("filter162storage162", "ZmlsdGVyMTYyc3RvcmFnZTE2Mg"),
    ("filter162network162", "ZmlsdGVyMTYybmV0d29yazE2Mg"),
    ("ranking162network162", "cmFua2luZzE2Mm5ldHdvcmsxNjI"),
    ("ranking162latency162", "cmFua2luZzE2MmxhdGVuY3kxNjI"),
    ("ranking162buffer162", "cmFua2luZzE2MmJ1ZmZlcjE2Mg"),
    ("ranking162queue162", "cmFua2luZzE2MnF1ZXVlMTYy"),
    ("encoding162queue162", "ZW5jb2RpbmcxNjJxdWV1ZTE2Mg"),
    ("encoding162worker162", "ZW5jb2RpbmcxNjJ3b3JrZXIxNjI"),
    ("encoding162kernel162", "ZW5jb2RpbmcxNjJrZXJuZWwxNjI"),
    ("encoding162signal162", "ZW5jb2RpbmcxNjJzaWduYWwxNjI"),
    ("mapping162signal162", "bWFwcGluZzE2MnNpZ25hbDE2Mg"),
    ("mapping162packet162", "bWFwcGluZzE2MnBhY2tldDE2Mg"),
    ("mapping162router162", "bWFwcGluZzE2MnJvdXRlcjE2Mg"),
    ("mapping162cluster162", "bWFwcGluZzE2MmNsdXN0ZXIxNjI"),
    ("record162cluster162", "cmVjb3JkMTYyY2x1c3RlcjE2Mg"),
    ("record162mirror162", "cmVjb3JkMTYybWlycm9yMTYy"),
    ("record162filter162", "cmVjb3JkMTYyZmlsdGVyMTYy"),
    ("record162ranking162", "cmVjb3JkMTYycmFua2luZzE2Mg"),
    ("candle162ranking162", "Y2FuZGxlMTYycmFua2luZzE2Mg"),
    ("candle162encoding162", "Y2FuZGxlMTYyZW5jb2RpbmcxNjI"),
    ("candle162mapping162", "Y2FuZGxlMTYybWFwcGluZzE2Mg"),
    ("candle162record162", "Y2FuZGxlMTYycmVjb3JkMTYy"),
    ("thread162record162", "dGhyZWFkMTYycmVjb3JkMTYy"),
    ("thread162candle162", "dGhyZWFkMTYyY2FuZGxlMTYy"),
    ("thread162thread162", "dGhyZWFkMTYydGhyZWFkMTYy"),
    ("thread162kitten162", "dGhyZWFkMTYya2l0dGVuMTYy"),
    (
        "round 162: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTYyOiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 162: agentuniverse is a framework for multi agents",
        "cm91bmQgMTYyOiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 162: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTYyOiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 162: the processor reads the record then stops",
        "cm91bmQgMTYyOiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 162: a worker pulls the next task from the queue",
        "cm91bmQgMTYyOiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 162: signals travel through the network layer",
        "cm91bmQgMTYyOiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 162: the gateway routes each request by policy",
        "cm91bmQgMTYyOiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 162: memory grows until the buffer is full",
        "cm91bmQgMTYyOiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 162: the cluster mirrors every packet twice",
        "cm91bmQgMTYyOiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 162: ranking uses tokens learned from the corpus",
        "cm91bmQgMTYyOiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 162: a long session ends when the candle dies",
        "cm91bmQgMTYyOiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 162: encode the prompt then map the result",
        "cm91bmQgMTYyOiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 162: the kernel wakes the worker at dawn",
        "cm91bmQgMTYyOiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 162: service latency drops after the patch",
        "cm91bmQgMTYyOiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 162: the library caches every vector it sees",
        "cm91bmQgMTYyOiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 162: agents argue then the debate resolves",
        "cm91bmQgMTYyOiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 162: the filter keeps only strong matches",
        "cm91bmQgMTYyOiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 162: the model answers with a short reply",
        "cm91bmQgMTYyOiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 162: the recorder stores the reasoning trace",
        "cm91bmQgMTYyOiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 162: the angel watches the processor run",
        "cm91bmQgMTYyOiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 162: angle of the vector decides the match",
        "cm91bmQgMTYyOiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 162: the candle burns twice as long at night",
        "cm91bmQgMTYyOiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 162: a mirror of the universe in one line",
        "cm91bmQgMTYyOiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 162: the queue drains before the storm", "cm91bmQgMTYyOiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
