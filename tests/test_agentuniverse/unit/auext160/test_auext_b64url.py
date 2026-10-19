"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten160kitten160", "a2l0dGVuMTYwa2l0dGVuMTYw"),
    ("kitten160sitting160", "a2l0dGVuMTYwc2l0dGluZzE2MA"),
    ("kitten160agent160", "a2l0dGVuMTYwYWdlbnQxNjA"),
    ("kitten160angle160", "a2l0dGVuMTYwYW5nbGUxNjA"),
    ("sitting160angle160", "c2l0dGluZzE2MGFuZ2xlMTYw"),
    ("sitting160universe160", "c2l0dGluZzE2MHVuaXZlcnNlMTYw"),
    ("sitting160memory160", "c2l0dGluZzE2MG1lbW9yeTE2MA"),
    ("sitting160stream160", "c2l0dGluZzE2MHN0cmVhbTE2MA"),
    ("agent160stream160", "YWdlbnQxNjBzdHJlYW0xNjA"),
    ("agent160context160", "YWdlbnQxNjBjb250ZXh0MTYw"),
    ("agent160knowledge160", "YWdlbnQxNjBrbm93bGVkZ2UxNjA"),
    ("agent160vector160", "YWdlbnQxNjB2ZWN0b3IxNjA"),
    ("angle160vector160", "YW5nbGUxNjB2ZWN0b3IxNjA"),
    ("angle160processor160", "YW5nbGUxNjBwcm9jZXNzb3IxNjA"),
    ("angle160reasoning160", "YW5nbGUxNjByZWFzb25pbmcxNjA"),
    ("angle160machine160", "YW5nbGUxNjBtYWNoaW5lMTYw"),
    ("universe160machine160", "dW5pdmVyc2UxNjBtYWNoaW5lMTYw"),
    ("universe160learning160", "dW5pdmVyc2UxNjBsZWFybmluZzE2MA"),
    ("universe160model160", "dW5pdmVyc2UxNjBtb2RlbDE2MA"),
    ("universe160token160", "dW5pdmVyc2UxNjB0b2tlbjE2MA"),
    ("memory160token160", "bWVtb3J5MTYwdG9rZW4xNjA"),
    ("memory160prompt160", "bWVtb3J5MTYwcHJvbXB0MTYw"),
    ("memory160session160", "bWVtb3J5MTYwc2Vzc2lvbjE2MA"),
    ("memory160library160", "bWVtb3J5MTYwbGlicmFyeTE2MA"),
    ("stream160library160", "c3RyZWFtMTYwbGlicmFyeTE2MA"),
    ("stream160service160", "c3RyZWFtMTYwc2VydmljZTE2MA"),
    ("stream160gateway160", "c3RyZWFtMTYwZ2F0ZXdheTE2MA"),
    ("stream160storage160", "c3RyZWFtMTYwc3RvcmFnZTE2MA"),
    ("context160storage160", "Y29udGV4dDE2MHN0b3JhZ2UxNjA"),
    ("context160network160", "Y29udGV4dDE2MG5ldHdvcmsxNjA"),
    ("context160latency160", "Y29udGV4dDE2MGxhdGVuY3kxNjA"),
    ("context160buffer160", "Y29udGV4dDE2MGJ1ZmZlcjE2MA"),
    ("knowledge160buffer160", "a25vd2xlZGdlMTYwYnVmZmVyMTYw"),
    ("knowledge160queue160", "a25vd2xlZGdlMTYwcXVldWUxNjA"),
    ("knowledge160worker160", "a25vd2xlZGdlMTYwd29ya2VyMTYw"),
    ("knowledge160kernel160", "a25vd2xlZGdlMTYwa2VybmVsMTYw"),
    ("vector160kernel160", "dmVjdG9yMTYwa2VybmVsMTYw"),
    ("vector160signal160", "dmVjdG9yMTYwc2lnbmFsMTYw"),
    ("vector160packet160", "dmVjdG9yMTYwcGFja2V0MTYw"),
    ("vector160router160", "dmVjdG9yMTYwcm91dGVyMTYw"),
    ("processor160router160", "cHJvY2Vzc29yMTYwcm91dGVyMTYw"),
    ("processor160cluster160", "cHJvY2Vzc29yMTYwY2x1c3RlcjE2MA"),
    ("processor160mirror160", "cHJvY2Vzc29yMTYwbWlycm9yMTYw"),
    ("processor160filter160", "cHJvY2Vzc29yMTYwZmlsdGVyMTYw"),
    ("reasoning160filter160", "cmVhc29uaW5nMTYwZmlsdGVyMTYw"),
    ("reasoning160ranking160", "cmVhc29uaW5nMTYwcmFua2luZzE2MA"),
    ("reasoning160encoding160", "cmVhc29uaW5nMTYwZW5jb2RpbmcxNjA"),
    ("reasoning160mapping160", "cmVhc29uaW5nMTYwbWFwcGluZzE2MA"),
    ("machine160mapping160", "bWFjaGluZTE2MG1hcHBpbmcxNjA"),
    ("machine160record160", "bWFjaGluZTE2MHJlY29yZDE2MA"),
    ("machine160candle160", "bWFjaGluZTE2MGNhbmRsZTE2MA"),
    ("machine160thread160", "bWFjaGluZTE2MHRocmVhZDE2MA"),
    ("learning160thread160", "bGVhcm5pbmcxNjB0aHJlYWQxNjA"),
    ("learning160kitten160", "bGVhcm5pbmcxNjBraXR0ZW4xNjA"),
    ("learning160sitting160", "bGVhcm5pbmcxNjBzaXR0aW5nMTYw"),
    ("learning160agent160", "bGVhcm5pbmcxNjBhZ2VudDE2MA"),
    ("model160agent160", "bW9kZWwxNjBhZ2VudDE2MA"),
    ("model160angle160", "bW9kZWwxNjBhbmdsZTE2MA"),
    ("model160universe160", "bW9kZWwxNjB1bml2ZXJzZTE2MA"),
    ("model160memory160", "bW9kZWwxNjBtZW1vcnkxNjA"),
    ("token160memory160", "dG9rZW4xNjBtZW1vcnkxNjA"),
    ("token160stream160", "dG9rZW4xNjBzdHJlYW0xNjA"),
    ("token160context160", "dG9rZW4xNjBjb250ZXh0MTYw"),
    ("token160knowledge160", "dG9rZW4xNjBrbm93bGVkZ2UxNjA"),
    ("prompt160knowledge160", "cHJvbXB0MTYwa25vd2xlZGdlMTYw"),
    ("prompt160vector160", "cHJvbXB0MTYwdmVjdG9yMTYw"),
    ("prompt160processor160", "cHJvbXB0MTYwcHJvY2Vzc29yMTYw"),
    ("prompt160reasoning160", "cHJvbXB0MTYwcmVhc29uaW5nMTYw"),
    ("session160reasoning160", "c2Vzc2lvbjE2MHJlYXNvbmluZzE2MA"),
    ("session160machine160", "c2Vzc2lvbjE2MG1hY2hpbmUxNjA"),
    ("session160learning160", "c2Vzc2lvbjE2MGxlYXJuaW5nMTYw"),
    ("session160model160", "c2Vzc2lvbjE2MG1vZGVsMTYw"),
    ("library160model160", "bGlicmFyeTE2MG1vZGVsMTYw"),
    ("library160token160", "bGlicmFyeTE2MHRva2VuMTYw"),
    ("library160prompt160", "bGlicmFyeTE2MHByb21wdDE2MA"),
    ("library160session160", "bGlicmFyeTE2MHNlc3Npb24xNjA"),
    ("service160session160", "c2VydmljZTE2MHNlc3Npb24xNjA"),
    ("service160library160", "c2VydmljZTE2MGxpYnJhcnkxNjA"),
    ("service160service160", "c2VydmljZTE2MHNlcnZpY2UxNjA"),
    ("service160gateway160", "c2VydmljZTE2MGdhdGV3YXkxNjA"),
    ("gateway160gateway160", "Z2F0ZXdheTE2MGdhdGV3YXkxNjA"),
    ("gateway160storage160", "Z2F0ZXdheTE2MHN0b3JhZ2UxNjA"),
    ("gateway160network160", "Z2F0ZXdheTE2MG5ldHdvcmsxNjA"),
    ("gateway160latency160", "Z2F0ZXdheTE2MGxhdGVuY3kxNjA"),
    ("storage160latency160", "c3RvcmFnZTE2MGxhdGVuY3kxNjA"),
    ("storage160buffer160", "c3RvcmFnZTE2MGJ1ZmZlcjE2MA"),
    ("storage160queue160", "c3RvcmFnZTE2MHF1ZXVlMTYw"),
    ("storage160worker160", "c3RvcmFnZTE2MHdvcmtlcjE2MA"),
    ("network160worker160", "bmV0d29yazE2MHdvcmtlcjE2MA"),
    ("network160kernel160", "bmV0d29yazE2MGtlcm5lbDE2MA"),
    ("network160signal160", "bmV0d29yazE2MHNpZ25hbDE2MA"),
    ("network160packet160", "bmV0d29yazE2MHBhY2tldDE2MA"),
    ("latency160packet160", "bGF0ZW5jeTE2MHBhY2tldDE2MA"),
    ("latency160router160", "bGF0ZW5jeTE2MHJvdXRlcjE2MA"),
    ("latency160cluster160", "bGF0ZW5jeTE2MGNsdXN0ZXIxNjA"),
    ("latency160mirror160", "bGF0ZW5jeTE2MG1pcnJvcjE2MA"),
    ("buffer160mirror160", "YnVmZmVyMTYwbWlycm9yMTYw"),
    ("buffer160filter160", "YnVmZmVyMTYwZmlsdGVyMTYw"),
    ("buffer160ranking160", "YnVmZmVyMTYwcmFua2luZzE2MA"),
    ("buffer160encoding160", "YnVmZmVyMTYwZW5jb2RpbmcxNjA"),
    ("queue160encoding160", "cXVldWUxNjBlbmNvZGluZzE2MA"),
    ("queue160mapping160", "cXVldWUxNjBtYXBwaW5nMTYw"),
    ("queue160record160", "cXVldWUxNjByZWNvcmQxNjA"),
    ("queue160candle160", "cXVldWUxNjBjYW5kbGUxNjA"),
    ("worker160candle160", "d29ya2VyMTYwY2FuZGxlMTYw"),
    ("worker160thread160", "d29ya2VyMTYwdGhyZWFkMTYw"),
    ("worker160kitten160", "d29ya2VyMTYwa2l0dGVuMTYw"),
    ("worker160sitting160", "d29ya2VyMTYwc2l0dGluZzE2MA"),
    ("kernel160sitting160", "a2VybmVsMTYwc2l0dGluZzE2MA"),
    ("kernel160agent160", "a2VybmVsMTYwYWdlbnQxNjA"),
    ("kernel160angle160", "a2VybmVsMTYwYW5nbGUxNjA"),
    ("kernel160universe160", "a2VybmVsMTYwdW5pdmVyc2UxNjA"),
    ("signal160universe160", "c2lnbmFsMTYwdW5pdmVyc2UxNjA"),
    ("signal160memory160", "c2lnbmFsMTYwbWVtb3J5MTYw"),
    ("signal160stream160", "c2lnbmFsMTYwc3RyZWFtMTYw"),
    ("signal160context160", "c2lnbmFsMTYwY29udGV4dDE2MA"),
    ("packet160context160", "cGFja2V0MTYwY29udGV4dDE2MA"),
    ("packet160knowledge160", "cGFja2V0MTYwa25vd2xlZGdlMTYw"),
    ("packet160vector160", "cGFja2V0MTYwdmVjdG9yMTYw"),
    ("packet160processor160", "cGFja2V0MTYwcHJvY2Vzc29yMTYw"),
    ("router160processor160", "cm91dGVyMTYwcHJvY2Vzc29yMTYw"),
    ("router160reasoning160", "cm91dGVyMTYwcmVhc29uaW5nMTYw"),
    ("router160machine160", "cm91dGVyMTYwbWFjaGluZTE2MA"),
    ("router160learning160", "cm91dGVyMTYwbGVhcm5pbmcxNjA"),
    ("cluster160learning160", "Y2x1c3RlcjE2MGxlYXJuaW5nMTYw"),
    ("cluster160model160", "Y2x1c3RlcjE2MG1vZGVsMTYw"),
    ("cluster160token160", "Y2x1c3RlcjE2MHRva2VuMTYw"),
    ("cluster160prompt160", "Y2x1c3RlcjE2MHByb21wdDE2MA"),
    ("mirror160prompt160", "bWlycm9yMTYwcHJvbXB0MTYw"),
    ("mirror160session160", "bWlycm9yMTYwc2Vzc2lvbjE2MA"),
    ("mirror160library160", "bWlycm9yMTYwbGlicmFyeTE2MA"),
    ("mirror160service160", "bWlycm9yMTYwc2VydmljZTE2MA"),
    ("filter160service160", "ZmlsdGVyMTYwc2VydmljZTE2MA"),
    ("filter160gateway160", "ZmlsdGVyMTYwZ2F0ZXdheTE2MA"),
    ("filter160storage160", "ZmlsdGVyMTYwc3RvcmFnZTE2MA"),
    ("filter160network160", "ZmlsdGVyMTYwbmV0d29yazE2MA"),
    ("ranking160network160", "cmFua2luZzE2MG5ldHdvcmsxNjA"),
    ("ranking160latency160", "cmFua2luZzE2MGxhdGVuY3kxNjA"),
    ("ranking160buffer160", "cmFua2luZzE2MGJ1ZmZlcjE2MA"),
    ("ranking160queue160", "cmFua2luZzE2MHF1ZXVlMTYw"),
    ("encoding160queue160", "ZW5jb2RpbmcxNjBxdWV1ZTE2MA"),
    ("encoding160worker160", "ZW5jb2RpbmcxNjB3b3JrZXIxNjA"),
    ("encoding160kernel160", "ZW5jb2RpbmcxNjBrZXJuZWwxNjA"),
    ("encoding160signal160", "ZW5jb2RpbmcxNjBzaWduYWwxNjA"),
    ("mapping160signal160", "bWFwcGluZzE2MHNpZ25hbDE2MA"),
    ("mapping160packet160", "bWFwcGluZzE2MHBhY2tldDE2MA"),
    ("mapping160router160", "bWFwcGluZzE2MHJvdXRlcjE2MA"),
    ("mapping160cluster160", "bWFwcGluZzE2MGNsdXN0ZXIxNjA"),
    ("record160cluster160", "cmVjb3JkMTYwY2x1c3RlcjE2MA"),
    ("record160mirror160", "cmVjb3JkMTYwbWlycm9yMTYw"),
    ("record160filter160", "cmVjb3JkMTYwZmlsdGVyMTYw"),
    ("record160ranking160", "cmVjb3JkMTYwcmFua2luZzE2MA"),
    ("candle160ranking160", "Y2FuZGxlMTYwcmFua2luZzE2MA"),
    ("candle160encoding160", "Y2FuZGxlMTYwZW5jb2RpbmcxNjA"),
    ("candle160mapping160", "Y2FuZGxlMTYwbWFwcGluZzE2MA"),
    ("candle160record160", "Y2FuZGxlMTYwcmVjb3JkMTYw"),
    ("thread160record160", "dGhyZWFkMTYwcmVjb3JkMTYw"),
    ("thread160candle160", "dGhyZWFkMTYwY2FuZGxlMTYw"),
    ("thread160thread160", "dGhyZWFkMTYwdGhyZWFkMTYw"),
    ("thread160kitten160", "dGhyZWFkMTYwa2l0dGVuMTYw"),
    (
        "round 160: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTYwOiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 160: agentuniverse is a framework for multi agents",
        "cm91bmQgMTYwOiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 160: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTYwOiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 160: the processor reads the record then stops",
        "cm91bmQgMTYwOiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 160: a worker pulls the next task from the queue",
        "cm91bmQgMTYwOiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 160: signals travel through the network layer",
        "cm91bmQgMTYwOiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 160: the gateway routes each request by policy",
        "cm91bmQgMTYwOiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 160: memory grows until the buffer is full",
        "cm91bmQgMTYwOiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 160: the cluster mirrors every packet twice",
        "cm91bmQgMTYwOiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 160: ranking uses tokens learned from the corpus",
        "cm91bmQgMTYwOiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 160: a long session ends when the candle dies",
        "cm91bmQgMTYwOiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 160: encode the prompt then map the result",
        "cm91bmQgMTYwOiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 160: the kernel wakes the worker at dawn",
        "cm91bmQgMTYwOiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 160: service latency drops after the patch",
        "cm91bmQgMTYwOiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 160: the library caches every vector it sees",
        "cm91bmQgMTYwOiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 160: agents argue then the debate resolves",
        "cm91bmQgMTYwOiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 160: the filter keeps only strong matches",
        "cm91bmQgMTYwOiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 160: the model answers with a short reply",
        "cm91bmQgMTYwOiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 160: the recorder stores the reasoning trace",
        "cm91bmQgMTYwOiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 160: the angel watches the processor run",
        "cm91bmQgMTYwOiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 160: angle of the vector decides the match",
        "cm91bmQgMTYwOiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 160: the candle burns twice as long at night",
        "cm91bmQgMTYwOiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 160: a mirror of the universe in one line",
        "cm91bmQgMTYwOiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 160: the queue drains before the storm", "cm91bmQgMTYwOiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
