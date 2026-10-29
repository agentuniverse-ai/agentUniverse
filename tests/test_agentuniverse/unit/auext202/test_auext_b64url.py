"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten202kitten202", "a2l0dGVuMjAya2l0dGVuMjAy"),
    ("kitten202sitting202", "a2l0dGVuMjAyc2l0dGluZzIwMg"),
    ("kitten202agent202", "a2l0dGVuMjAyYWdlbnQyMDI"),
    ("kitten202angle202", "a2l0dGVuMjAyYW5nbGUyMDI"),
    ("sitting202angle202", "c2l0dGluZzIwMmFuZ2xlMjAy"),
    ("sitting202universe202", "c2l0dGluZzIwMnVuaXZlcnNlMjAy"),
    ("sitting202memory202", "c2l0dGluZzIwMm1lbW9yeTIwMg"),
    ("sitting202stream202", "c2l0dGluZzIwMnN0cmVhbTIwMg"),
    ("agent202stream202", "YWdlbnQyMDJzdHJlYW0yMDI"),
    ("agent202context202", "YWdlbnQyMDJjb250ZXh0MjAy"),
    ("agent202knowledge202", "YWdlbnQyMDJrbm93bGVkZ2UyMDI"),
    ("agent202vector202", "YWdlbnQyMDJ2ZWN0b3IyMDI"),
    ("angle202vector202", "YW5nbGUyMDJ2ZWN0b3IyMDI"),
    ("angle202processor202", "YW5nbGUyMDJwcm9jZXNzb3IyMDI"),
    ("angle202reasoning202", "YW5nbGUyMDJyZWFzb25pbmcyMDI"),
    ("angle202machine202", "YW5nbGUyMDJtYWNoaW5lMjAy"),
    ("universe202machine202", "dW5pdmVyc2UyMDJtYWNoaW5lMjAy"),
    ("universe202learning202", "dW5pdmVyc2UyMDJsZWFybmluZzIwMg"),
    ("universe202model202", "dW5pdmVyc2UyMDJtb2RlbDIwMg"),
    ("universe202token202", "dW5pdmVyc2UyMDJ0b2tlbjIwMg"),
    ("memory202token202", "bWVtb3J5MjAydG9rZW4yMDI"),
    ("memory202prompt202", "bWVtb3J5MjAycHJvbXB0MjAy"),
    ("memory202session202", "bWVtb3J5MjAyc2Vzc2lvbjIwMg"),
    ("memory202library202", "bWVtb3J5MjAybGlicmFyeTIwMg"),
    ("stream202library202", "c3RyZWFtMjAybGlicmFyeTIwMg"),
    ("stream202service202", "c3RyZWFtMjAyc2VydmljZTIwMg"),
    ("stream202gateway202", "c3RyZWFtMjAyZ2F0ZXdheTIwMg"),
    ("stream202storage202", "c3RyZWFtMjAyc3RvcmFnZTIwMg"),
    ("context202storage202", "Y29udGV4dDIwMnN0b3JhZ2UyMDI"),
    ("context202network202", "Y29udGV4dDIwMm5ldHdvcmsyMDI"),
    ("context202latency202", "Y29udGV4dDIwMmxhdGVuY3kyMDI"),
    ("context202buffer202", "Y29udGV4dDIwMmJ1ZmZlcjIwMg"),
    ("knowledge202buffer202", "a25vd2xlZGdlMjAyYnVmZmVyMjAy"),
    ("knowledge202queue202", "a25vd2xlZGdlMjAycXVldWUyMDI"),
    ("knowledge202worker202", "a25vd2xlZGdlMjAyd29ya2VyMjAy"),
    ("knowledge202kernel202", "a25vd2xlZGdlMjAya2VybmVsMjAy"),
    ("vector202kernel202", "dmVjdG9yMjAya2VybmVsMjAy"),
    ("vector202signal202", "dmVjdG9yMjAyc2lnbmFsMjAy"),
    ("vector202packet202", "dmVjdG9yMjAycGFja2V0MjAy"),
    ("vector202router202", "dmVjdG9yMjAycm91dGVyMjAy"),
    ("processor202router202", "cHJvY2Vzc29yMjAycm91dGVyMjAy"),
    ("processor202cluster202", "cHJvY2Vzc29yMjAyY2x1c3RlcjIwMg"),
    ("processor202mirror202", "cHJvY2Vzc29yMjAybWlycm9yMjAy"),
    ("processor202filter202", "cHJvY2Vzc29yMjAyZmlsdGVyMjAy"),
    ("reasoning202filter202", "cmVhc29uaW5nMjAyZmlsdGVyMjAy"),
    ("reasoning202ranking202", "cmVhc29uaW5nMjAycmFua2luZzIwMg"),
    ("reasoning202encoding202", "cmVhc29uaW5nMjAyZW5jb2RpbmcyMDI"),
    ("reasoning202mapping202", "cmVhc29uaW5nMjAybWFwcGluZzIwMg"),
    ("machine202mapping202", "bWFjaGluZTIwMm1hcHBpbmcyMDI"),
    ("machine202record202", "bWFjaGluZTIwMnJlY29yZDIwMg"),
    ("machine202candle202", "bWFjaGluZTIwMmNhbmRsZTIwMg"),
    ("machine202thread202", "bWFjaGluZTIwMnRocmVhZDIwMg"),
    ("learning202thread202", "bGVhcm5pbmcyMDJ0aHJlYWQyMDI"),
    ("learning202kitten202", "bGVhcm5pbmcyMDJraXR0ZW4yMDI"),
    ("learning202sitting202", "bGVhcm5pbmcyMDJzaXR0aW5nMjAy"),
    ("learning202agent202", "bGVhcm5pbmcyMDJhZ2VudDIwMg"),
    ("model202agent202", "bW9kZWwyMDJhZ2VudDIwMg"),
    ("model202angle202", "bW9kZWwyMDJhbmdsZTIwMg"),
    ("model202universe202", "bW9kZWwyMDJ1bml2ZXJzZTIwMg"),
    ("model202memory202", "bW9kZWwyMDJtZW1vcnkyMDI"),
    ("token202memory202", "dG9rZW4yMDJtZW1vcnkyMDI"),
    ("token202stream202", "dG9rZW4yMDJzdHJlYW0yMDI"),
    ("token202context202", "dG9rZW4yMDJjb250ZXh0MjAy"),
    ("token202knowledge202", "dG9rZW4yMDJrbm93bGVkZ2UyMDI"),
    ("prompt202knowledge202", "cHJvbXB0MjAya25vd2xlZGdlMjAy"),
    ("prompt202vector202", "cHJvbXB0MjAydmVjdG9yMjAy"),
    ("prompt202processor202", "cHJvbXB0MjAycHJvY2Vzc29yMjAy"),
    ("prompt202reasoning202", "cHJvbXB0MjAycmVhc29uaW5nMjAy"),
    ("session202reasoning202", "c2Vzc2lvbjIwMnJlYXNvbmluZzIwMg"),
    ("session202machine202", "c2Vzc2lvbjIwMm1hY2hpbmUyMDI"),
    ("session202learning202", "c2Vzc2lvbjIwMmxlYXJuaW5nMjAy"),
    ("session202model202", "c2Vzc2lvbjIwMm1vZGVsMjAy"),
    ("library202model202", "bGlicmFyeTIwMm1vZGVsMjAy"),
    ("library202token202", "bGlicmFyeTIwMnRva2VuMjAy"),
    ("library202prompt202", "bGlicmFyeTIwMnByb21wdDIwMg"),
    ("library202session202", "bGlicmFyeTIwMnNlc3Npb24yMDI"),
    ("service202session202", "c2VydmljZTIwMnNlc3Npb24yMDI"),
    ("service202library202", "c2VydmljZTIwMmxpYnJhcnkyMDI"),
    ("service202service202", "c2VydmljZTIwMnNlcnZpY2UyMDI"),
    ("service202gateway202", "c2VydmljZTIwMmdhdGV3YXkyMDI"),
    ("gateway202gateway202", "Z2F0ZXdheTIwMmdhdGV3YXkyMDI"),
    ("gateway202storage202", "Z2F0ZXdheTIwMnN0b3JhZ2UyMDI"),
    ("gateway202network202", "Z2F0ZXdheTIwMm5ldHdvcmsyMDI"),
    ("gateway202latency202", "Z2F0ZXdheTIwMmxhdGVuY3kyMDI"),
    ("storage202latency202", "c3RvcmFnZTIwMmxhdGVuY3kyMDI"),
    ("storage202buffer202", "c3RvcmFnZTIwMmJ1ZmZlcjIwMg"),
    ("storage202queue202", "c3RvcmFnZTIwMnF1ZXVlMjAy"),
    ("storage202worker202", "c3RvcmFnZTIwMndvcmtlcjIwMg"),
    ("network202worker202", "bmV0d29yazIwMndvcmtlcjIwMg"),
    ("network202kernel202", "bmV0d29yazIwMmtlcm5lbDIwMg"),
    ("network202signal202", "bmV0d29yazIwMnNpZ25hbDIwMg"),
    ("network202packet202", "bmV0d29yazIwMnBhY2tldDIwMg"),
    ("latency202packet202", "bGF0ZW5jeTIwMnBhY2tldDIwMg"),
    ("latency202router202", "bGF0ZW5jeTIwMnJvdXRlcjIwMg"),
    ("latency202cluster202", "bGF0ZW5jeTIwMmNsdXN0ZXIyMDI"),
    ("latency202mirror202", "bGF0ZW5jeTIwMm1pcnJvcjIwMg"),
    ("buffer202mirror202", "YnVmZmVyMjAybWlycm9yMjAy"),
    ("buffer202filter202", "YnVmZmVyMjAyZmlsdGVyMjAy"),
    ("buffer202ranking202", "YnVmZmVyMjAycmFua2luZzIwMg"),
    ("buffer202encoding202", "YnVmZmVyMjAyZW5jb2RpbmcyMDI"),
    ("queue202encoding202", "cXVldWUyMDJlbmNvZGluZzIwMg"),
    ("queue202mapping202", "cXVldWUyMDJtYXBwaW5nMjAy"),
    ("queue202record202", "cXVldWUyMDJyZWNvcmQyMDI"),
    ("queue202candle202", "cXVldWUyMDJjYW5kbGUyMDI"),
    ("worker202candle202", "d29ya2VyMjAyY2FuZGxlMjAy"),
    ("worker202thread202", "d29ya2VyMjAydGhyZWFkMjAy"),
    ("worker202kitten202", "d29ya2VyMjAya2l0dGVuMjAy"),
    ("worker202sitting202", "d29ya2VyMjAyc2l0dGluZzIwMg"),
    ("kernel202sitting202", "a2VybmVsMjAyc2l0dGluZzIwMg"),
    ("kernel202agent202", "a2VybmVsMjAyYWdlbnQyMDI"),
    ("kernel202angle202", "a2VybmVsMjAyYW5nbGUyMDI"),
    ("kernel202universe202", "a2VybmVsMjAydW5pdmVyc2UyMDI"),
    ("signal202universe202", "c2lnbmFsMjAydW5pdmVyc2UyMDI"),
    ("signal202memory202", "c2lnbmFsMjAybWVtb3J5MjAy"),
    ("signal202stream202", "c2lnbmFsMjAyc3RyZWFtMjAy"),
    ("signal202context202", "c2lnbmFsMjAyY29udGV4dDIwMg"),
    ("packet202context202", "cGFja2V0MjAyY29udGV4dDIwMg"),
    ("packet202knowledge202", "cGFja2V0MjAya25vd2xlZGdlMjAy"),
    ("packet202vector202", "cGFja2V0MjAydmVjdG9yMjAy"),
    ("packet202processor202", "cGFja2V0MjAycHJvY2Vzc29yMjAy"),
    ("router202processor202", "cm91dGVyMjAycHJvY2Vzc29yMjAy"),
    ("router202reasoning202", "cm91dGVyMjAycmVhc29uaW5nMjAy"),
    ("router202machine202", "cm91dGVyMjAybWFjaGluZTIwMg"),
    ("router202learning202", "cm91dGVyMjAybGVhcm5pbmcyMDI"),
    ("cluster202learning202", "Y2x1c3RlcjIwMmxlYXJuaW5nMjAy"),
    ("cluster202model202", "Y2x1c3RlcjIwMm1vZGVsMjAy"),
    ("cluster202token202", "Y2x1c3RlcjIwMnRva2VuMjAy"),
    ("cluster202prompt202", "Y2x1c3RlcjIwMnByb21wdDIwMg"),
    ("mirror202prompt202", "bWlycm9yMjAycHJvbXB0MjAy"),
    ("mirror202session202", "bWlycm9yMjAyc2Vzc2lvbjIwMg"),
    ("mirror202library202", "bWlycm9yMjAybGlicmFyeTIwMg"),
    ("mirror202service202", "bWlycm9yMjAyc2VydmljZTIwMg"),
    ("filter202service202", "ZmlsdGVyMjAyc2VydmljZTIwMg"),
    ("filter202gateway202", "ZmlsdGVyMjAyZ2F0ZXdheTIwMg"),
    ("filter202storage202", "ZmlsdGVyMjAyc3RvcmFnZTIwMg"),
    ("filter202network202", "ZmlsdGVyMjAybmV0d29yazIwMg"),
    ("ranking202network202", "cmFua2luZzIwMm5ldHdvcmsyMDI"),
    ("ranking202latency202", "cmFua2luZzIwMmxhdGVuY3kyMDI"),
    ("ranking202buffer202", "cmFua2luZzIwMmJ1ZmZlcjIwMg"),
    ("ranking202queue202", "cmFua2luZzIwMnF1ZXVlMjAy"),
    ("encoding202queue202", "ZW5jb2RpbmcyMDJxdWV1ZTIwMg"),
    ("encoding202worker202", "ZW5jb2RpbmcyMDJ3b3JrZXIyMDI"),
    ("encoding202kernel202", "ZW5jb2RpbmcyMDJrZXJuZWwyMDI"),
    ("encoding202signal202", "ZW5jb2RpbmcyMDJzaWduYWwyMDI"),
    ("mapping202signal202", "bWFwcGluZzIwMnNpZ25hbDIwMg"),
    ("mapping202packet202", "bWFwcGluZzIwMnBhY2tldDIwMg"),
    ("mapping202router202", "bWFwcGluZzIwMnJvdXRlcjIwMg"),
    ("mapping202cluster202", "bWFwcGluZzIwMmNsdXN0ZXIyMDI"),
    ("record202cluster202", "cmVjb3JkMjAyY2x1c3RlcjIwMg"),
    ("record202mirror202", "cmVjb3JkMjAybWlycm9yMjAy"),
    ("record202filter202", "cmVjb3JkMjAyZmlsdGVyMjAy"),
    ("record202ranking202", "cmVjb3JkMjAycmFua2luZzIwMg"),
    ("candle202ranking202", "Y2FuZGxlMjAycmFua2luZzIwMg"),
    ("candle202encoding202", "Y2FuZGxlMjAyZW5jb2RpbmcyMDI"),
    ("candle202mapping202", "Y2FuZGxlMjAybWFwcGluZzIwMg"),
    ("candle202record202", "Y2FuZGxlMjAycmVjb3JkMjAy"),
    ("thread202record202", "dGhyZWFkMjAycmVjb3JkMjAy"),
    ("thread202candle202", "dGhyZWFkMjAyY2FuZGxlMjAy"),
    ("thread202thread202", "dGhyZWFkMjAydGhyZWFkMjAy"),
    ("thread202kitten202", "dGhyZWFkMjAya2l0dGVuMjAy"),
    (
        "round 202: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMjAyOiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 202: agentuniverse is a framework for multi agents",
        "cm91bmQgMjAyOiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 202: knowledge stored as vectors enables retrieval",
        "cm91bmQgMjAyOiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 202: the processor reads the record then stops",
        "cm91bmQgMjAyOiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 202: a worker pulls the next task from the queue",
        "cm91bmQgMjAyOiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 202: signals travel through the network layer",
        "cm91bmQgMjAyOiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 202: the gateway routes each request by policy",
        "cm91bmQgMjAyOiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 202: memory grows until the buffer is full",
        "cm91bmQgMjAyOiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 202: the cluster mirrors every packet twice",
        "cm91bmQgMjAyOiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 202: ranking uses tokens learned from the corpus",
        "cm91bmQgMjAyOiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 202: a long session ends when the candle dies",
        "cm91bmQgMjAyOiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 202: encode the prompt then map the result",
        "cm91bmQgMjAyOiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 202: the kernel wakes the worker at dawn",
        "cm91bmQgMjAyOiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 202: service latency drops after the patch",
        "cm91bmQgMjAyOiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 202: the library caches every vector it sees",
        "cm91bmQgMjAyOiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 202: agents argue then the debate resolves",
        "cm91bmQgMjAyOiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 202: the filter keeps only strong matches",
        "cm91bmQgMjAyOiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 202: the model answers with a short reply",
        "cm91bmQgMjAyOiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 202: the recorder stores the reasoning trace",
        "cm91bmQgMjAyOiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 202: the angel watches the processor run",
        "cm91bmQgMjAyOiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 202: angle of the vector decides the match",
        "cm91bmQgMjAyOiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 202: the candle burns twice as long at night",
        "cm91bmQgMjAyOiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 202: a mirror of the universe in one line",
        "cm91bmQgMjAyOiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 202: the queue drains before the storm", "cm91bmQgMjAyOiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
