"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten114kitten114", "a2l0dGVuMTE0a2l0dGVuMTE0"),
    ("kitten114sitting114", "a2l0dGVuMTE0c2l0dGluZzExNA"),
    ("kitten114agent114", "a2l0dGVuMTE0YWdlbnQxMTQ"),
    ("kitten114angle114", "a2l0dGVuMTE0YW5nbGUxMTQ"),
    ("sitting114angle114", "c2l0dGluZzExNGFuZ2xlMTE0"),
    ("sitting114universe114", "c2l0dGluZzExNHVuaXZlcnNlMTE0"),
    ("sitting114memory114", "c2l0dGluZzExNG1lbW9yeTExNA"),
    ("sitting114stream114", "c2l0dGluZzExNHN0cmVhbTExNA"),
    ("agent114stream114", "YWdlbnQxMTRzdHJlYW0xMTQ"),
    ("agent114context114", "YWdlbnQxMTRjb250ZXh0MTE0"),
    ("agent114knowledge114", "YWdlbnQxMTRrbm93bGVkZ2UxMTQ"),
    ("agent114vector114", "YWdlbnQxMTR2ZWN0b3IxMTQ"),
    ("angle114vector114", "YW5nbGUxMTR2ZWN0b3IxMTQ"),
    ("angle114processor114", "YW5nbGUxMTRwcm9jZXNzb3IxMTQ"),
    ("angle114reasoning114", "YW5nbGUxMTRyZWFzb25pbmcxMTQ"),
    ("angle114machine114", "YW5nbGUxMTRtYWNoaW5lMTE0"),
    ("universe114machine114", "dW5pdmVyc2UxMTRtYWNoaW5lMTE0"),
    ("universe114learning114", "dW5pdmVyc2UxMTRsZWFybmluZzExNA"),
    ("universe114model114", "dW5pdmVyc2UxMTRtb2RlbDExNA"),
    ("universe114token114", "dW5pdmVyc2UxMTR0b2tlbjExNA"),
    ("memory114token114", "bWVtb3J5MTE0dG9rZW4xMTQ"),
    ("memory114prompt114", "bWVtb3J5MTE0cHJvbXB0MTE0"),
    ("memory114session114", "bWVtb3J5MTE0c2Vzc2lvbjExNA"),
    ("memory114library114", "bWVtb3J5MTE0bGlicmFyeTExNA"),
    ("stream114library114", "c3RyZWFtMTE0bGlicmFyeTExNA"),
    ("stream114service114", "c3RyZWFtMTE0c2VydmljZTExNA"),
    ("stream114gateway114", "c3RyZWFtMTE0Z2F0ZXdheTExNA"),
    ("stream114storage114", "c3RyZWFtMTE0c3RvcmFnZTExNA"),
    ("context114storage114", "Y29udGV4dDExNHN0b3JhZ2UxMTQ"),
    ("context114network114", "Y29udGV4dDExNG5ldHdvcmsxMTQ"),
    ("context114latency114", "Y29udGV4dDExNGxhdGVuY3kxMTQ"),
    ("context114buffer114", "Y29udGV4dDExNGJ1ZmZlcjExNA"),
    ("knowledge114buffer114", "a25vd2xlZGdlMTE0YnVmZmVyMTE0"),
    ("knowledge114queue114", "a25vd2xlZGdlMTE0cXVldWUxMTQ"),
    ("knowledge114worker114", "a25vd2xlZGdlMTE0d29ya2VyMTE0"),
    ("knowledge114kernel114", "a25vd2xlZGdlMTE0a2VybmVsMTE0"),
    ("vector114kernel114", "dmVjdG9yMTE0a2VybmVsMTE0"),
    ("vector114signal114", "dmVjdG9yMTE0c2lnbmFsMTE0"),
    ("vector114packet114", "dmVjdG9yMTE0cGFja2V0MTE0"),
    ("vector114router114", "dmVjdG9yMTE0cm91dGVyMTE0"),
    ("processor114router114", "cHJvY2Vzc29yMTE0cm91dGVyMTE0"),
    ("processor114cluster114", "cHJvY2Vzc29yMTE0Y2x1c3RlcjExNA"),
    ("processor114mirror114", "cHJvY2Vzc29yMTE0bWlycm9yMTE0"),
    ("processor114filter114", "cHJvY2Vzc29yMTE0ZmlsdGVyMTE0"),
    ("reasoning114filter114", "cmVhc29uaW5nMTE0ZmlsdGVyMTE0"),
    ("reasoning114ranking114", "cmVhc29uaW5nMTE0cmFua2luZzExNA"),
    ("reasoning114encoding114", "cmVhc29uaW5nMTE0ZW5jb2RpbmcxMTQ"),
    ("reasoning114mapping114", "cmVhc29uaW5nMTE0bWFwcGluZzExNA"),
    ("machine114mapping114", "bWFjaGluZTExNG1hcHBpbmcxMTQ"),
    ("machine114record114", "bWFjaGluZTExNHJlY29yZDExNA"),
    ("machine114candle114", "bWFjaGluZTExNGNhbmRsZTExNA"),
    ("machine114thread114", "bWFjaGluZTExNHRocmVhZDExNA"),
    ("learning114thread114", "bGVhcm5pbmcxMTR0aHJlYWQxMTQ"),
    ("learning114kitten114", "bGVhcm5pbmcxMTRraXR0ZW4xMTQ"),
    ("learning114sitting114", "bGVhcm5pbmcxMTRzaXR0aW5nMTE0"),
    ("learning114agent114", "bGVhcm5pbmcxMTRhZ2VudDExNA"),
    ("model114agent114", "bW9kZWwxMTRhZ2VudDExNA"),
    ("model114angle114", "bW9kZWwxMTRhbmdsZTExNA"),
    ("model114universe114", "bW9kZWwxMTR1bml2ZXJzZTExNA"),
    ("model114memory114", "bW9kZWwxMTRtZW1vcnkxMTQ"),
    ("token114memory114", "dG9rZW4xMTRtZW1vcnkxMTQ"),
    ("token114stream114", "dG9rZW4xMTRzdHJlYW0xMTQ"),
    ("token114context114", "dG9rZW4xMTRjb250ZXh0MTE0"),
    ("token114knowledge114", "dG9rZW4xMTRrbm93bGVkZ2UxMTQ"),
    ("prompt114knowledge114", "cHJvbXB0MTE0a25vd2xlZGdlMTE0"),
    ("prompt114vector114", "cHJvbXB0MTE0dmVjdG9yMTE0"),
    ("prompt114processor114", "cHJvbXB0MTE0cHJvY2Vzc29yMTE0"),
    ("prompt114reasoning114", "cHJvbXB0MTE0cmVhc29uaW5nMTE0"),
    ("session114reasoning114", "c2Vzc2lvbjExNHJlYXNvbmluZzExNA"),
    ("session114machine114", "c2Vzc2lvbjExNG1hY2hpbmUxMTQ"),
    ("session114learning114", "c2Vzc2lvbjExNGxlYXJuaW5nMTE0"),
    ("session114model114", "c2Vzc2lvbjExNG1vZGVsMTE0"),
    ("library114model114", "bGlicmFyeTExNG1vZGVsMTE0"),
    ("library114token114", "bGlicmFyeTExNHRva2VuMTE0"),
    ("library114prompt114", "bGlicmFyeTExNHByb21wdDExNA"),
    ("library114session114", "bGlicmFyeTExNHNlc3Npb24xMTQ"),
    ("service114session114", "c2VydmljZTExNHNlc3Npb24xMTQ"),
    ("service114library114", "c2VydmljZTExNGxpYnJhcnkxMTQ"),
    ("service114service114", "c2VydmljZTExNHNlcnZpY2UxMTQ"),
    ("service114gateway114", "c2VydmljZTExNGdhdGV3YXkxMTQ"),
    ("gateway114gateway114", "Z2F0ZXdheTExNGdhdGV3YXkxMTQ"),
    ("gateway114storage114", "Z2F0ZXdheTExNHN0b3JhZ2UxMTQ"),
    ("gateway114network114", "Z2F0ZXdheTExNG5ldHdvcmsxMTQ"),
    ("gateway114latency114", "Z2F0ZXdheTExNGxhdGVuY3kxMTQ"),
    ("storage114latency114", "c3RvcmFnZTExNGxhdGVuY3kxMTQ"),
    ("storage114buffer114", "c3RvcmFnZTExNGJ1ZmZlcjExNA"),
    ("storage114queue114", "c3RvcmFnZTExNHF1ZXVlMTE0"),
    ("storage114worker114", "c3RvcmFnZTExNHdvcmtlcjExNA"),
    ("network114worker114", "bmV0d29yazExNHdvcmtlcjExNA"),
    ("network114kernel114", "bmV0d29yazExNGtlcm5lbDExNA"),
    ("network114signal114", "bmV0d29yazExNHNpZ25hbDExNA"),
    ("network114packet114", "bmV0d29yazExNHBhY2tldDExNA"),
    ("latency114packet114", "bGF0ZW5jeTExNHBhY2tldDExNA"),
    ("latency114router114", "bGF0ZW5jeTExNHJvdXRlcjExNA"),
    ("latency114cluster114", "bGF0ZW5jeTExNGNsdXN0ZXIxMTQ"),
    ("latency114mirror114", "bGF0ZW5jeTExNG1pcnJvcjExNA"),
    ("buffer114mirror114", "YnVmZmVyMTE0bWlycm9yMTE0"),
    ("buffer114filter114", "YnVmZmVyMTE0ZmlsdGVyMTE0"),
    ("buffer114ranking114", "YnVmZmVyMTE0cmFua2luZzExNA"),
    ("buffer114encoding114", "YnVmZmVyMTE0ZW5jb2RpbmcxMTQ"),
    ("queue114encoding114", "cXVldWUxMTRlbmNvZGluZzExNA"),
    ("queue114mapping114", "cXVldWUxMTRtYXBwaW5nMTE0"),
    ("queue114record114", "cXVldWUxMTRyZWNvcmQxMTQ"),
    ("queue114candle114", "cXVldWUxMTRjYW5kbGUxMTQ"),
    ("worker114candle114", "d29ya2VyMTE0Y2FuZGxlMTE0"),
    ("worker114thread114", "d29ya2VyMTE0dGhyZWFkMTE0"),
    ("worker114kitten114", "d29ya2VyMTE0a2l0dGVuMTE0"),
    ("worker114sitting114", "d29ya2VyMTE0c2l0dGluZzExNA"),
    ("kernel114sitting114", "a2VybmVsMTE0c2l0dGluZzExNA"),
    ("kernel114agent114", "a2VybmVsMTE0YWdlbnQxMTQ"),
    ("kernel114angle114", "a2VybmVsMTE0YW5nbGUxMTQ"),
    ("kernel114universe114", "a2VybmVsMTE0dW5pdmVyc2UxMTQ"),
    ("signal114universe114", "c2lnbmFsMTE0dW5pdmVyc2UxMTQ"),
    ("signal114memory114", "c2lnbmFsMTE0bWVtb3J5MTE0"),
    ("signal114stream114", "c2lnbmFsMTE0c3RyZWFtMTE0"),
    ("signal114context114", "c2lnbmFsMTE0Y29udGV4dDExNA"),
    ("packet114context114", "cGFja2V0MTE0Y29udGV4dDExNA"),
    ("packet114knowledge114", "cGFja2V0MTE0a25vd2xlZGdlMTE0"),
    ("packet114vector114", "cGFja2V0MTE0dmVjdG9yMTE0"),
    ("packet114processor114", "cGFja2V0MTE0cHJvY2Vzc29yMTE0"),
    ("router114processor114", "cm91dGVyMTE0cHJvY2Vzc29yMTE0"),
    ("router114reasoning114", "cm91dGVyMTE0cmVhc29uaW5nMTE0"),
    ("router114machine114", "cm91dGVyMTE0bWFjaGluZTExNA"),
    ("router114learning114", "cm91dGVyMTE0bGVhcm5pbmcxMTQ"),
    ("cluster114learning114", "Y2x1c3RlcjExNGxlYXJuaW5nMTE0"),
    ("cluster114model114", "Y2x1c3RlcjExNG1vZGVsMTE0"),
    ("cluster114token114", "Y2x1c3RlcjExNHRva2VuMTE0"),
    ("cluster114prompt114", "Y2x1c3RlcjExNHByb21wdDExNA"),
    ("mirror114prompt114", "bWlycm9yMTE0cHJvbXB0MTE0"),
    ("mirror114session114", "bWlycm9yMTE0c2Vzc2lvbjExNA"),
    ("mirror114library114", "bWlycm9yMTE0bGlicmFyeTExNA"),
    ("mirror114service114", "bWlycm9yMTE0c2VydmljZTExNA"),
    ("filter114service114", "ZmlsdGVyMTE0c2VydmljZTExNA"),
    ("filter114gateway114", "ZmlsdGVyMTE0Z2F0ZXdheTExNA"),
    ("filter114storage114", "ZmlsdGVyMTE0c3RvcmFnZTExNA"),
    ("filter114network114", "ZmlsdGVyMTE0bmV0d29yazExNA"),
    ("ranking114network114", "cmFua2luZzExNG5ldHdvcmsxMTQ"),
    ("ranking114latency114", "cmFua2luZzExNGxhdGVuY3kxMTQ"),
    ("ranking114buffer114", "cmFua2luZzExNGJ1ZmZlcjExNA"),
    ("ranking114queue114", "cmFua2luZzExNHF1ZXVlMTE0"),
    ("encoding114queue114", "ZW5jb2RpbmcxMTRxdWV1ZTExNA"),
    ("encoding114worker114", "ZW5jb2RpbmcxMTR3b3JrZXIxMTQ"),
    ("encoding114kernel114", "ZW5jb2RpbmcxMTRrZXJuZWwxMTQ"),
    ("encoding114signal114", "ZW5jb2RpbmcxMTRzaWduYWwxMTQ"),
    ("mapping114signal114", "bWFwcGluZzExNHNpZ25hbDExNA"),
    ("mapping114packet114", "bWFwcGluZzExNHBhY2tldDExNA"),
    ("mapping114router114", "bWFwcGluZzExNHJvdXRlcjExNA"),
    ("mapping114cluster114", "bWFwcGluZzExNGNsdXN0ZXIxMTQ"),
    ("record114cluster114", "cmVjb3JkMTE0Y2x1c3RlcjExNA"),
    ("record114mirror114", "cmVjb3JkMTE0bWlycm9yMTE0"),
    ("record114filter114", "cmVjb3JkMTE0ZmlsdGVyMTE0"),
    ("record114ranking114", "cmVjb3JkMTE0cmFua2luZzExNA"),
    ("candle114ranking114", "Y2FuZGxlMTE0cmFua2luZzExNA"),
    ("candle114encoding114", "Y2FuZGxlMTE0ZW5jb2RpbmcxMTQ"),
    ("candle114mapping114", "Y2FuZGxlMTE0bWFwcGluZzExNA"),
    ("candle114record114", "Y2FuZGxlMTE0cmVjb3JkMTE0"),
    ("thread114record114", "dGhyZWFkMTE0cmVjb3JkMTE0"),
    ("thread114candle114", "dGhyZWFkMTE0Y2FuZGxlMTE0"),
    ("thread114thread114", "dGhyZWFkMTE0dGhyZWFkMTE0"),
    ("thread114kitten114", "dGhyZWFkMTE0a2l0dGVuMTE0"),
    (
        "round 114: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTE0OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 114: agentuniverse is a framework for multi agents",
        "cm91bmQgMTE0OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 114: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTE0OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 114: the processor reads the record then stops",
        "cm91bmQgMTE0OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 114: a worker pulls the next task from the queue",
        "cm91bmQgMTE0OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 114: signals travel through the network layer",
        "cm91bmQgMTE0OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 114: the gateway routes each request by policy",
        "cm91bmQgMTE0OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 114: memory grows until the buffer is full",
        "cm91bmQgMTE0OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 114: the cluster mirrors every packet twice",
        "cm91bmQgMTE0OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 114: ranking uses tokens learned from the corpus",
        "cm91bmQgMTE0OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 114: a long session ends when the candle dies",
        "cm91bmQgMTE0OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 114: encode the prompt then map the result",
        "cm91bmQgMTE0OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 114: the kernel wakes the worker at dawn",
        "cm91bmQgMTE0OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 114: service latency drops after the patch",
        "cm91bmQgMTE0OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 114: the library caches every vector it sees",
        "cm91bmQgMTE0OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 114: agents argue then the debate resolves",
        "cm91bmQgMTE0OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 114: the filter keeps only strong matches",
        "cm91bmQgMTE0OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 114: the model answers with a short reply",
        "cm91bmQgMTE0OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 114: the recorder stores the reasoning trace",
        "cm91bmQgMTE0OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 114: the angel watches the processor run",
        "cm91bmQgMTE0OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 114: angle of the vector decides the match",
        "cm91bmQgMTE0OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 114: the candle burns twice as long at night",
        "cm91bmQgMTE0OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 114: a mirror of the universe in one line",
        "cm91bmQgMTE0OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 114: the queue drains before the storm", "cm91bmQgMTE0OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
