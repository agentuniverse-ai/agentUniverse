"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten200kitten200", "a2l0dGVuMjAwa2l0dGVuMjAw"),
    ("kitten200sitting200", "a2l0dGVuMjAwc2l0dGluZzIwMA"),
    ("kitten200agent200", "a2l0dGVuMjAwYWdlbnQyMDA"),
    ("kitten200angle200", "a2l0dGVuMjAwYW5nbGUyMDA"),
    ("sitting200angle200", "c2l0dGluZzIwMGFuZ2xlMjAw"),
    ("sitting200universe200", "c2l0dGluZzIwMHVuaXZlcnNlMjAw"),
    ("sitting200memory200", "c2l0dGluZzIwMG1lbW9yeTIwMA"),
    ("sitting200stream200", "c2l0dGluZzIwMHN0cmVhbTIwMA"),
    ("agent200stream200", "YWdlbnQyMDBzdHJlYW0yMDA"),
    ("agent200context200", "YWdlbnQyMDBjb250ZXh0MjAw"),
    ("agent200knowledge200", "YWdlbnQyMDBrbm93bGVkZ2UyMDA"),
    ("agent200vector200", "YWdlbnQyMDB2ZWN0b3IyMDA"),
    ("angle200vector200", "YW5nbGUyMDB2ZWN0b3IyMDA"),
    ("angle200processor200", "YW5nbGUyMDBwcm9jZXNzb3IyMDA"),
    ("angle200reasoning200", "YW5nbGUyMDByZWFzb25pbmcyMDA"),
    ("angle200machine200", "YW5nbGUyMDBtYWNoaW5lMjAw"),
    ("universe200machine200", "dW5pdmVyc2UyMDBtYWNoaW5lMjAw"),
    ("universe200learning200", "dW5pdmVyc2UyMDBsZWFybmluZzIwMA"),
    ("universe200model200", "dW5pdmVyc2UyMDBtb2RlbDIwMA"),
    ("universe200token200", "dW5pdmVyc2UyMDB0b2tlbjIwMA"),
    ("memory200token200", "bWVtb3J5MjAwdG9rZW4yMDA"),
    ("memory200prompt200", "bWVtb3J5MjAwcHJvbXB0MjAw"),
    ("memory200session200", "bWVtb3J5MjAwc2Vzc2lvbjIwMA"),
    ("memory200library200", "bWVtb3J5MjAwbGlicmFyeTIwMA"),
    ("stream200library200", "c3RyZWFtMjAwbGlicmFyeTIwMA"),
    ("stream200service200", "c3RyZWFtMjAwc2VydmljZTIwMA"),
    ("stream200gateway200", "c3RyZWFtMjAwZ2F0ZXdheTIwMA"),
    ("stream200storage200", "c3RyZWFtMjAwc3RvcmFnZTIwMA"),
    ("context200storage200", "Y29udGV4dDIwMHN0b3JhZ2UyMDA"),
    ("context200network200", "Y29udGV4dDIwMG5ldHdvcmsyMDA"),
    ("context200latency200", "Y29udGV4dDIwMGxhdGVuY3kyMDA"),
    ("context200buffer200", "Y29udGV4dDIwMGJ1ZmZlcjIwMA"),
    ("knowledge200buffer200", "a25vd2xlZGdlMjAwYnVmZmVyMjAw"),
    ("knowledge200queue200", "a25vd2xlZGdlMjAwcXVldWUyMDA"),
    ("knowledge200worker200", "a25vd2xlZGdlMjAwd29ya2VyMjAw"),
    ("knowledge200kernel200", "a25vd2xlZGdlMjAwa2VybmVsMjAw"),
    ("vector200kernel200", "dmVjdG9yMjAwa2VybmVsMjAw"),
    ("vector200signal200", "dmVjdG9yMjAwc2lnbmFsMjAw"),
    ("vector200packet200", "dmVjdG9yMjAwcGFja2V0MjAw"),
    ("vector200router200", "dmVjdG9yMjAwcm91dGVyMjAw"),
    ("processor200router200", "cHJvY2Vzc29yMjAwcm91dGVyMjAw"),
    ("processor200cluster200", "cHJvY2Vzc29yMjAwY2x1c3RlcjIwMA"),
    ("processor200mirror200", "cHJvY2Vzc29yMjAwbWlycm9yMjAw"),
    ("processor200filter200", "cHJvY2Vzc29yMjAwZmlsdGVyMjAw"),
    ("reasoning200filter200", "cmVhc29uaW5nMjAwZmlsdGVyMjAw"),
    ("reasoning200ranking200", "cmVhc29uaW5nMjAwcmFua2luZzIwMA"),
    ("reasoning200encoding200", "cmVhc29uaW5nMjAwZW5jb2RpbmcyMDA"),
    ("reasoning200mapping200", "cmVhc29uaW5nMjAwbWFwcGluZzIwMA"),
    ("machine200mapping200", "bWFjaGluZTIwMG1hcHBpbmcyMDA"),
    ("machine200record200", "bWFjaGluZTIwMHJlY29yZDIwMA"),
    ("machine200candle200", "bWFjaGluZTIwMGNhbmRsZTIwMA"),
    ("machine200thread200", "bWFjaGluZTIwMHRocmVhZDIwMA"),
    ("learning200thread200", "bGVhcm5pbmcyMDB0aHJlYWQyMDA"),
    ("learning200kitten200", "bGVhcm5pbmcyMDBraXR0ZW4yMDA"),
    ("learning200sitting200", "bGVhcm5pbmcyMDBzaXR0aW5nMjAw"),
    ("learning200agent200", "bGVhcm5pbmcyMDBhZ2VudDIwMA"),
    ("model200agent200", "bW9kZWwyMDBhZ2VudDIwMA"),
    ("model200angle200", "bW9kZWwyMDBhbmdsZTIwMA"),
    ("model200universe200", "bW9kZWwyMDB1bml2ZXJzZTIwMA"),
    ("model200memory200", "bW9kZWwyMDBtZW1vcnkyMDA"),
    ("token200memory200", "dG9rZW4yMDBtZW1vcnkyMDA"),
    ("token200stream200", "dG9rZW4yMDBzdHJlYW0yMDA"),
    ("token200context200", "dG9rZW4yMDBjb250ZXh0MjAw"),
    ("token200knowledge200", "dG9rZW4yMDBrbm93bGVkZ2UyMDA"),
    ("prompt200knowledge200", "cHJvbXB0MjAwa25vd2xlZGdlMjAw"),
    ("prompt200vector200", "cHJvbXB0MjAwdmVjdG9yMjAw"),
    ("prompt200processor200", "cHJvbXB0MjAwcHJvY2Vzc29yMjAw"),
    ("prompt200reasoning200", "cHJvbXB0MjAwcmVhc29uaW5nMjAw"),
    ("session200reasoning200", "c2Vzc2lvbjIwMHJlYXNvbmluZzIwMA"),
    ("session200machine200", "c2Vzc2lvbjIwMG1hY2hpbmUyMDA"),
    ("session200learning200", "c2Vzc2lvbjIwMGxlYXJuaW5nMjAw"),
    ("session200model200", "c2Vzc2lvbjIwMG1vZGVsMjAw"),
    ("library200model200", "bGlicmFyeTIwMG1vZGVsMjAw"),
    ("library200token200", "bGlicmFyeTIwMHRva2VuMjAw"),
    ("library200prompt200", "bGlicmFyeTIwMHByb21wdDIwMA"),
    ("library200session200", "bGlicmFyeTIwMHNlc3Npb24yMDA"),
    ("service200session200", "c2VydmljZTIwMHNlc3Npb24yMDA"),
    ("service200library200", "c2VydmljZTIwMGxpYnJhcnkyMDA"),
    ("service200service200", "c2VydmljZTIwMHNlcnZpY2UyMDA"),
    ("service200gateway200", "c2VydmljZTIwMGdhdGV3YXkyMDA"),
    ("gateway200gateway200", "Z2F0ZXdheTIwMGdhdGV3YXkyMDA"),
    ("gateway200storage200", "Z2F0ZXdheTIwMHN0b3JhZ2UyMDA"),
    ("gateway200network200", "Z2F0ZXdheTIwMG5ldHdvcmsyMDA"),
    ("gateway200latency200", "Z2F0ZXdheTIwMGxhdGVuY3kyMDA"),
    ("storage200latency200", "c3RvcmFnZTIwMGxhdGVuY3kyMDA"),
    ("storage200buffer200", "c3RvcmFnZTIwMGJ1ZmZlcjIwMA"),
    ("storage200queue200", "c3RvcmFnZTIwMHF1ZXVlMjAw"),
    ("storage200worker200", "c3RvcmFnZTIwMHdvcmtlcjIwMA"),
    ("network200worker200", "bmV0d29yazIwMHdvcmtlcjIwMA"),
    ("network200kernel200", "bmV0d29yazIwMGtlcm5lbDIwMA"),
    ("network200signal200", "bmV0d29yazIwMHNpZ25hbDIwMA"),
    ("network200packet200", "bmV0d29yazIwMHBhY2tldDIwMA"),
    ("latency200packet200", "bGF0ZW5jeTIwMHBhY2tldDIwMA"),
    ("latency200router200", "bGF0ZW5jeTIwMHJvdXRlcjIwMA"),
    ("latency200cluster200", "bGF0ZW5jeTIwMGNsdXN0ZXIyMDA"),
    ("latency200mirror200", "bGF0ZW5jeTIwMG1pcnJvcjIwMA"),
    ("buffer200mirror200", "YnVmZmVyMjAwbWlycm9yMjAw"),
    ("buffer200filter200", "YnVmZmVyMjAwZmlsdGVyMjAw"),
    ("buffer200ranking200", "YnVmZmVyMjAwcmFua2luZzIwMA"),
    ("buffer200encoding200", "YnVmZmVyMjAwZW5jb2RpbmcyMDA"),
    ("queue200encoding200", "cXVldWUyMDBlbmNvZGluZzIwMA"),
    ("queue200mapping200", "cXVldWUyMDBtYXBwaW5nMjAw"),
    ("queue200record200", "cXVldWUyMDByZWNvcmQyMDA"),
    ("queue200candle200", "cXVldWUyMDBjYW5kbGUyMDA"),
    ("worker200candle200", "d29ya2VyMjAwY2FuZGxlMjAw"),
    ("worker200thread200", "d29ya2VyMjAwdGhyZWFkMjAw"),
    ("worker200kitten200", "d29ya2VyMjAwa2l0dGVuMjAw"),
    ("worker200sitting200", "d29ya2VyMjAwc2l0dGluZzIwMA"),
    ("kernel200sitting200", "a2VybmVsMjAwc2l0dGluZzIwMA"),
    ("kernel200agent200", "a2VybmVsMjAwYWdlbnQyMDA"),
    ("kernel200angle200", "a2VybmVsMjAwYW5nbGUyMDA"),
    ("kernel200universe200", "a2VybmVsMjAwdW5pdmVyc2UyMDA"),
    ("signal200universe200", "c2lnbmFsMjAwdW5pdmVyc2UyMDA"),
    ("signal200memory200", "c2lnbmFsMjAwbWVtb3J5MjAw"),
    ("signal200stream200", "c2lnbmFsMjAwc3RyZWFtMjAw"),
    ("signal200context200", "c2lnbmFsMjAwY29udGV4dDIwMA"),
    ("packet200context200", "cGFja2V0MjAwY29udGV4dDIwMA"),
    ("packet200knowledge200", "cGFja2V0MjAwa25vd2xlZGdlMjAw"),
    ("packet200vector200", "cGFja2V0MjAwdmVjdG9yMjAw"),
    ("packet200processor200", "cGFja2V0MjAwcHJvY2Vzc29yMjAw"),
    ("router200processor200", "cm91dGVyMjAwcHJvY2Vzc29yMjAw"),
    ("router200reasoning200", "cm91dGVyMjAwcmVhc29uaW5nMjAw"),
    ("router200machine200", "cm91dGVyMjAwbWFjaGluZTIwMA"),
    ("router200learning200", "cm91dGVyMjAwbGVhcm5pbmcyMDA"),
    ("cluster200learning200", "Y2x1c3RlcjIwMGxlYXJuaW5nMjAw"),
    ("cluster200model200", "Y2x1c3RlcjIwMG1vZGVsMjAw"),
    ("cluster200token200", "Y2x1c3RlcjIwMHRva2VuMjAw"),
    ("cluster200prompt200", "Y2x1c3RlcjIwMHByb21wdDIwMA"),
    ("mirror200prompt200", "bWlycm9yMjAwcHJvbXB0MjAw"),
    ("mirror200session200", "bWlycm9yMjAwc2Vzc2lvbjIwMA"),
    ("mirror200library200", "bWlycm9yMjAwbGlicmFyeTIwMA"),
    ("mirror200service200", "bWlycm9yMjAwc2VydmljZTIwMA"),
    ("filter200service200", "ZmlsdGVyMjAwc2VydmljZTIwMA"),
    ("filter200gateway200", "ZmlsdGVyMjAwZ2F0ZXdheTIwMA"),
    ("filter200storage200", "ZmlsdGVyMjAwc3RvcmFnZTIwMA"),
    ("filter200network200", "ZmlsdGVyMjAwbmV0d29yazIwMA"),
    ("ranking200network200", "cmFua2luZzIwMG5ldHdvcmsyMDA"),
    ("ranking200latency200", "cmFua2luZzIwMGxhdGVuY3kyMDA"),
    ("ranking200buffer200", "cmFua2luZzIwMGJ1ZmZlcjIwMA"),
    ("ranking200queue200", "cmFua2luZzIwMHF1ZXVlMjAw"),
    ("encoding200queue200", "ZW5jb2RpbmcyMDBxdWV1ZTIwMA"),
    ("encoding200worker200", "ZW5jb2RpbmcyMDB3b3JrZXIyMDA"),
    ("encoding200kernel200", "ZW5jb2RpbmcyMDBrZXJuZWwyMDA"),
    ("encoding200signal200", "ZW5jb2RpbmcyMDBzaWduYWwyMDA"),
    ("mapping200signal200", "bWFwcGluZzIwMHNpZ25hbDIwMA"),
    ("mapping200packet200", "bWFwcGluZzIwMHBhY2tldDIwMA"),
    ("mapping200router200", "bWFwcGluZzIwMHJvdXRlcjIwMA"),
    ("mapping200cluster200", "bWFwcGluZzIwMGNsdXN0ZXIyMDA"),
    ("record200cluster200", "cmVjb3JkMjAwY2x1c3RlcjIwMA"),
    ("record200mirror200", "cmVjb3JkMjAwbWlycm9yMjAw"),
    ("record200filter200", "cmVjb3JkMjAwZmlsdGVyMjAw"),
    ("record200ranking200", "cmVjb3JkMjAwcmFua2luZzIwMA"),
    ("candle200ranking200", "Y2FuZGxlMjAwcmFua2luZzIwMA"),
    ("candle200encoding200", "Y2FuZGxlMjAwZW5jb2RpbmcyMDA"),
    ("candle200mapping200", "Y2FuZGxlMjAwbWFwcGluZzIwMA"),
    ("candle200record200", "Y2FuZGxlMjAwcmVjb3JkMjAw"),
    ("thread200record200", "dGhyZWFkMjAwcmVjb3JkMjAw"),
    ("thread200candle200", "dGhyZWFkMjAwY2FuZGxlMjAw"),
    ("thread200thread200", "dGhyZWFkMjAwdGhyZWFkMjAw"),
    ("thread200kitten200", "dGhyZWFkMjAwa2l0dGVuMjAw"),
    (
        "round 200: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMjAwOiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 200: agentuniverse is a framework for multi agents",
        "cm91bmQgMjAwOiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 200: knowledge stored as vectors enables retrieval",
        "cm91bmQgMjAwOiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 200: the processor reads the record then stops",
        "cm91bmQgMjAwOiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 200: a worker pulls the next task from the queue",
        "cm91bmQgMjAwOiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 200: signals travel through the network layer",
        "cm91bmQgMjAwOiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 200: the gateway routes each request by policy",
        "cm91bmQgMjAwOiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 200: memory grows until the buffer is full",
        "cm91bmQgMjAwOiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 200: the cluster mirrors every packet twice",
        "cm91bmQgMjAwOiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 200: ranking uses tokens learned from the corpus",
        "cm91bmQgMjAwOiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 200: a long session ends when the candle dies",
        "cm91bmQgMjAwOiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 200: encode the prompt then map the result",
        "cm91bmQgMjAwOiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 200: the kernel wakes the worker at dawn",
        "cm91bmQgMjAwOiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 200: service latency drops after the patch",
        "cm91bmQgMjAwOiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 200: the library caches every vector it sees",
        "cm91bmQgMjAwOiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 200: agents argue then the debate resolves",
        "cm91bmQgMjAwOiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 200: the filter keeps only strong matches",
        "cm91bmQgMjAwOiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 200: the model answers with a short reply",
        "cm91bmQgMjAwOiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 200: the recorder stores the reasoning trace",
        "cm91bmQgMjAwOiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 200: the angel watches the processor run",
        "cm91bmQgMjAwOiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 200: angle of the vector decides the match",
        "cm91bmQgMjAwOiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 200: the candle burns twice as long at night",
        "cm91bmQgMjAwOiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 200: a mirror of the universe in one line",
        "cm91bmQgMjAwOiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 200: the queue drains before the storm", "cm91bmQgMjAwOiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
