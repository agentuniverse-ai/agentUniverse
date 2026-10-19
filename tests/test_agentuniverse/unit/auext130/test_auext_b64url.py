"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten130kitten130", "a2l0dGVuMTMwa2l0dGVuMTMw"),
    ("kitten130sitting130", "a2l0dGVuMTMwc2l0dGluZzEzMA"),
    ("kitten130agent130", "a2l0dGVuMTMwYWdlbnQxMzA"),
    ("kitten130angle130", "a2l0dGVuMTMwYW5nbGUxMzA"),
    ("sitting130angle130", "c2l0dGluZzEzMGFuZ2xlMTMw"),
    ("sitting130universe130", "c2l0dGluZzEzMHVuaXZlcnNlMTMw"),
    ("sitting130memory130", "c2l0dGluZzEzMG1lbW9yeTEzMA"),
    ("sitting130stream130", "c2l0dGluZzEzMHN0cmVhbTEzMA"),
    ("agent130stream130", "YWdlbnQxMzBzdHJlYW0xMzA"),
    ("agent130context130", "YWdlbnQxMzBjb250ZXh0MTMw"),
    ("agent130knowledge130", "YWdlbnQxMzBrbm93bGVkZ2UxMzA"),
    ("agent130vector130", "YWdlbnQxMzB2ZWN0b3IxMzA"),
    ("angle130vector130", "YW5nbGUxMzB2ZWN0b3IxMzA"),
    ("angle130processor130", "YW5nbGUxMzBwcm9jZXNzb3IxMzA"),
    ("angle130reasoning130", "YW5nbGUxMzByZWFzb25pbmcxMzA"),
    ("angle130machine130", "YW5nbGUxMzBtYWNoaW5lMTMw"),
    ("universe130machine130", "dW5pdmVyc2UxMzBtYWNoaW5lMTMw"),
    ("universe130learning130", "dW5pdmVyc2UxMzBsZWFybmluZzEzMA"),
    ("universe130model130", "dW5pdmVyc2UxMzBtb2RlbDEzMA"),
    ("universe130token130", "dW5pdmVyc2UxMzB0b2tlbjEzMA"),
    ("memory130token130", "bWVtb3J5MTMwdG9rZW4xMzA"),
    ("memory130prompt130", "bWVtb3J5MTMwcHJvbXB0MTMw"),
    ("memory130session130", "bWVtb3J5MTMwc2Vzc2lvbjEzMA"),
    ("memory130library130", "bWVtb3J5MTMwbGlicmFyeTEzMA"),
    ("stream130library130", "c3RyZWFtMTMwbGlicmFyeTEzMA"),
    ("stream130service130", "c3RyZWFtMTMwc2VydmljZTEzMA"),
    ("stream130gateway130", "c3RyZWFtMTMwZ2F0ZXdheTEzMA"),
    ("stream130storage130", "c3RyZWFtMTMwc3RvcmFnZTEzMA"),
    ("context130storage130", "Y29udGV4dDEzMHN0b3JhZ2UxMzA"),
    ("context130network130", "Y29udGV4dDEzMG5ldHdvcmsxMzA"),
    ("context130latency130", "Y29udGV4dDEzMGxhdGVuY3kxMzA"),
    ("context130buffer130", "Y29udGV4dDEzMGJ1ZmZlcjEzMA"),
    ("knowledge130buffer130", "a25vd2xlZGdlMTMwYnVmZmVyMTMw"),
    ("knowledge130queue130", "a25vd2xlZGdlMTMwcXVldWUxMzA"),
    ("knowledge130worker130", "a25vd2xlZGdlMTMwd29ya2VyMTMw"),
    ("knowledge130kernel130", "a25vd2xlZGdlMTMwa2VybmVsMTMw"),
    ("vector130kernel130", "dmVjdG9yMTMwa2VybmVsMTMw"),
    ("vector130signal130", "dmVjdG9yMTMwc2lnbmFsMTMw"),
    ("vector130packet130", "dmVjdG9yMTMwcGFja2V0MTMw"),
    ("vector130router130", "dmVjdG9yMTMwcm91dGVyMTMw"),
    ("processor130router130", "cHJvY2Vzc29yMTMwcm91dGVyMTMw"),
    ("processor130cluster130", "cHJvY2Vzc29yMTMwY2x1c3RlcjEzMA"),
    ("processor130mirror130", "cHJvY2Vzc29yMTMwbWlycm9yMTMw"),
    ("processor130filter130", "cHJvY2Vzc29yMTMwZmlsdGVyMTMw"),
    ("reasoning130filter130", "cmVhc29uaW5nMTMwZmlsdGVyMTMw"),
    ("reasoning130ranking130", "cmVhc29uaW5nMTMwcmFua2luZzEzMA"),
    ("reasoning130encoding130", "cmVhc29uaW5nMTMwZW5jb2RpbmcxMzA"),
    ("reasoning130mapping130", "cmVhc29uaW5nMTMwbWFwcGluZzEzMA"),
    ("machine130mapping130", "bWFjaGluZTEzMG1hcHBpbmcxMzA"),
    ("machine130record130", "bWFjaGluZTEzMHJlY29yZDEzMA"),
    ("machine130candle130", "bWFjaGluZTEzMGNhbmRsZTEzMA"),
    ("machine130thread130", "bWFjaGluZTEzMHRocmVhZDEzMA"),
    ("learning130thread130", "bGVhcm5pbmcxMzB0aHJlYWQxMzA"),
    ("learning130kitten130", "bGVhcm5pbmcxMzBraXR0ZW4xMzA"),
    ("learning130sitting130", "bGVhcm5pbmcxMzBzaXR0aW5nMTMw"),
    ("learning130agent130", "bGVhcm5pbmcxMzBhZ2VudDEzMA"),
    ("model130agent130", "bW9kZWwxMzBhZ2VudDEzMA"),
    ("model130angle130", "bW9kZWwxMzBhbmdsZTEzMA"),
    ("model130universe130", "bW9kZWwxMzB1bml2ZXJzZTEzMA"),
    ("model130memory130", "bW9kZWwxMzBtZW1vcnkxMzA"),
    ("token130memory130", "dG9rZW4xMzBtZW1vcnkxMzA"),
    ("token130stream130", "dG9rZW4xMzBzdHJlYW0xMzA"),
    ("token130context130", "dG9rZW4xMzBjb250ZXh0MTMw"),
    ("token130knowledge130", "dG9rZW4xMzBrbm93bGVkZ2UxMzA"),
    ("prompt130knowledge130", "cHJvbXB0MTMwa25vd2xlZGdlMTMw"),
    ("prompt130vector130", "cHJvbXB0MTMwdmVjdG9yMTMw"),
    ("prompt130processor130", "cHJvbXB0MTMwcHJvY2Vzc29yMTMw"),
    ("prompt130reasoning130", "cHJvbXB0MTMwcmVhc29uaW5nMTMw"),
    ("session130reasoning130", "c2Vzc2lvbjEzMHJlYXNvbmluZzEzMA"),
    ("session130machine130", "c2Vzc2lvbjEzMG1hY2hpbmUxMzA"),
    ("session130learning130", "c2Vzc2lvbjEzMGxlYXJuaW5nMTMw"),
    ("session130model130", "c2Vzc2lvbjEzMG1vZGVsMTMw"),
    ("library130model130", "bGlicmFyeTEzMG1vZGVsMTMw"),
    ("library130token130", "bGlicmFyeTEzMHRva2VuMTMw"),
    ("library130prompt130", "bGlicmFyeTEzMHByb21wdDEzMA"),
    ("library130session130", "bGlicmFyeTEzMHNlc3Npb24xMzA"),
    ("service130session130", "c2VydmljZTEzMHNlc3Npb24xMzA"),
    ("service130library130", "c2VydmljZTEzMGxpYnJhcnkxMzA"),
    ("service130service130", "c2VydmljZTEzMHNlcnZpY2UxMzA"),
    ("service130gateway130", "c2VydmljZTEzMGdhdGV3YXkxMzA"),
    ("gateway130gateway130", "Z2F0ZXdheTEzMGdhdGV3YXkxMzA"),
    ("gateway130storage130", "Z2F0ZXdheTEzMHN0b3JhZ2UxMzA"),
    ("gateway130network130", "Z2F0ZXdheTEzMG5ldHdvcmsxMzA"),
    ("gateway130latency130", "Z2F0ZXdheTEzMGxhdGVuY3kxMzA"),
    ("storage130latency130", "c3RvcmFnZTEzMGxhdGVuY3kxMzA"),
    ("storage130buffer130", "c3RvcmFnZTEzMGJ1ZmZlcjEzMA"),
    ("storage130queue130", "c3RvcmFnZTEzMHF1ZXVlMTMw"),
    ("storage130worker130", "c3RvcmFnZTEzMHdvcmtlcjEzMA"),
    ("network130worker130", "bmV0d29yazEzMHdvcmtlcjEzMA"),
    ("network130kernel130", "bmV0d29yazEzMGtlcm5lbDEzMA"),
    ("network130signal130", "bmV0d29yazEzMHNpZ25hbDEzMA"),
    ("network130packet130", "bmV0d29yazEzMHBhY2tldDEzMA"),
    ("latency130packet130", "bGF0ZW5jeTEzMHBhY2tldDEzMA"),
    ("latency130router130", "bGF0ZW5jeTEzMHJvdXRlcjEzMA"),
    ("latency130cluster130", "bGF0ZW5jeTEzMGNsdXN0ZXIxMzA"),
    ("latency130mirror130", "bGF0ZW5jeTEzMG1pcnJvcjEzMA"),
    ("buffer130mirror130", "YnVmZmVyMTMwbWlycm9yMTMw"),
    ("buffer130filter130", "YnVmZmVyMTMwZmlsdGVyMTMw"),
    ("buffer130ranking130", "YnVmZmVyMTMwcmFua2luZzEzMA"),
    ("buffer130encoding130", "YnVmZmVyMTMwZW5jb2RpbmcxMzA"),
    ("queue130encoding130", "cXVldWUxMzBlbmNvZGluZzEzMA"),
    ("queue130mapping130", "cXVldWUxMzBtYXBwaW5nMTMw"),
    ("queue130record130", "cXVldWUxMzByZWNvcmQxMzA"),
    ("queue130candle130", "cXVldWUxMzBjYW5kbGUxMzA"),
    ("worker130candle130", "d29ya2VyMTMwY2FuZGxlMTMw"),
    ("worker130thread130", "d29ya2VyMTMwdGhyZWFkMTMw"),
    ("worker130kitten130", "d29ya2VyMTMwa2l0dGVuMTMw"),
    ("worker130sitting130", "d29ya2VyMTMwc2l0dGluZzEzMA"),
    ("kernel130sitting130", "a2VybmVsMTMwc2l0dGluZzEzMA"),
    ("kernel130agent130", "a2VybmVsMTMwYWdlbnQxMzA"),
    ("kernel130angle130", "a2VybmVsMTMwYW5nbGUxMzA"),
    ("kernel130universe130", "a2VybmVsMTMwdW5pdmVyc2UxMzA"),
    ("signal130universe130", "c2lnbmFsMTMwdW5pdmVyc2UxMzA"),
    ("signal130memory130", "c2lnbmFsMTMwbWVtb3J5MTMw"),
    ("signal130stream130", "c2lnbmFsMTMwc3RyZWFtMTMw"),
    ("signal130context130", "c2lnbmFsMTMwY29udGV4dDEzMA"),
    ("packet130context130", "cGFja2V0MTMwY29udGV4dDEzMA"),
    ("packet130knowledge130", "cGFja2V0MTMwa25vd2xlZGdlMTMw"),
    ("packet130vector130", "cGFja2V0MTMwdmVjdG9yMTMw"),
    ("packet130processor130", "cGFja2V0MTMwcHJvY2Vzc29yMTMw"),
    ("router130processor130", "cm91dGVyMTMwcHJvY2Vzc29yMTMw"),
    ("router130reasoning130", "cm91dGVyMTMwcmVhc29uaW5nMTMw"),
    ("router130machine130", "cm91dGVyMTMwbWFjaGluZTEzMA"),
    ("router130learning130", "cm91dGVyMTMwbGVhcm5pbmcxMzA"),
    ("cluster130learning130", "Y2x1c3RlcjEzMGxlYXJuaW5nMTMw"),
    ("cluster130model130", "Y2x1c3RlcjEzMG1vZGVsMTMw"),
    ("cluster130token130", "Y2x1c3RlcjEzMHRva2VuMTMw"),
    ("cluster130prompt130", "Y2x1c3RlcjEzMHByb21wdDEzMA"),
    ("mirror130prompt130", "bWlycm9yMTMwcHJvbXB0MTMw"),
    ("mirror130session130", "bWlycm9yMTMwc2Vzc2lvbjEzMA"),
    ("mirror130library130", "bWlycm9yMTMwbGlicmFyeTEzMA"),
    ("mirror130service130", "bWlycm9yMTMwc2VydmljZTEzMA"),
    ("filter130service130", "ZmlsdGVyMTMwc2VydmljZTEzMA"),
    ("filter130gateway130", "ZmlsdGVyMTMwZ2F0ZXdheTEzMA"),
    ("filter130storage130", "ZmlsdGVyMTMwc3RvcmFnZTEzMA"),
    ("filter130network130", "ZmlsdGVyMTMwbmV0d29yazEzMA"),
    ("ranking130network130", "cmFua2luZzEzMG5ldHdvcmsxMzA"),
    ("ranking130latency130", "cmFua2luZzEzMGxhdGVuY3kxMzA"),
    ("ranking130buffer130", "cmFua2luZzEzMGJ1ZmZlcjEzMA"),
    ("ranking130queue130", "cmFua2luZzEzMHF1ZXVlMTMw"),
    ("encoding130queue130", "ZW5jb2RpbmcxMzBxdWV1ZTEzMA"),
    ("encoding130worker130", "ZW5jb2RpbmcxMzB3b3JrZXIxMzA"),
    ("encoding130kernel130", "ZW5jb2RpbmcxMzBrZXJuZWwxMzA"),
    ("encoding130signal130", "ZW5jb2RpbmcxMzBzaWduYWwxMzA"),
    ("mapping130signal130", "bWFwcGluZzEzMHNpZ25hbDEzMA"),
    ("mapping130packet130", "bWFwcGluZzEzMHBhY2tldDEzMA"),
    ("mapping130router130", "bWFwcGluZzEzMHJvdXRlcjEzMA"),
    ("mapping130cluster130", "bWFwcGluZzEzMGNsdXN0ZXIxMzA"),
    ("record130cluster130", "cmVjb3JkMTMwY2x1c3RlcjEzMA"),
    ("record130mirror130", "cmVjb3JkMTMwbWlycm9yMTMw"),
    ("record130filter130", "cmVjb3JkMTMwZmlsdGVyMTMw"),
    ("record130ranking130", "cmVjb3JkMTMwcmFua2luZzEzMA"),
    ("candle130ranking130", "Y2FuZGxlMTMwcmFua2luZzEzMA"),
    ("candle130encoding130", "Y2FuZGxlMTMwZW5jb2RpbmcxMzA"),
    ("candle130mapping130", "Y2FuZGxlMTMwbWFwcGluZzEzMA"),
    ("candle130record130", "Y2FuZGxlMTMwcmVjb3JkMTMw"),
    ("thread130record130", "dGhyZWFkMTMwcmVjb3JkMTMw"),
    ("thread130candle130", "dGhyZWFkMTMwY2FuZGxlMTMw"),
    ("thread130thread130", "dGhyZWFkMTMwdGhyZWFkMTMw"),
    ("thread130kitten130", "dGhyZWFkMTMwa2l0dGVuMTMw"),
    (
        "round 130: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTMwOiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 130: agentuniverse is a framework for multi agents",
        "cm91bmQgMTMwOiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 130: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTMwOiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 130: the processor reads the record then stops",
        "cm91bmQgMTMwOiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 130: a worker pulls the next task from the queue",
        "cm91bmQgMTMwOiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 130: signals travel through the network layer",
        "cm91bmQgMTMwOiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 130: the gateway routes each request by policy",
        "cm91bmQgMTMwOiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 130: memory grows until the buffer is full",
        "cm91bmQgMTMwOiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 130: the cluster mirrors every packet twice",
        "cm91bmQgMTMwOiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 130: ranking uses tokens learned from the corpus",
        "cm91bmQgMTMwOiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 130: a long session ends when the candle dies",
        "cm91bmQgMTMwOiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 130: encode the prompt then map the result",
        "cm91bmQgMTMwOiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 130: the kernel wakes the worker at dawn",
        "cm91bmQgMTMwOiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 130: service latency drops after the patch",
        "cm91bmQgMTMwOiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 130: the library caches every vector it sees",
        "cm91bmQgMTMwOiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 130: agents argue then the debate resolves",
        "cm91bmQgMTMwOiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 130: the filter keeps only strong matches",
        "cm91bmQgMTMwOiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 130: the model answers with a short reply",
        "cm91bmQgMTMwOiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 130: the recorder stores the reasoning trace",
        "cm91bmQgMTMwOiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 130: the angel watches the processor run",
        "cm91bmQgMTMwOiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 130: angle of the vector decides the match",
        "cm91bmQgMTMwOiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 130: the candle burns twice as long at night",
        "cm91bmQgMTMwOiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 130: a mirror of the universe in one line",
        "cm91bmQgMTMwOiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 130: the queue drains before the storm", "cm91bmQgMTMwOiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
