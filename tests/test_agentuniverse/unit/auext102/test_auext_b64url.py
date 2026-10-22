"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten102kitten102", "a2l0dGVuMTAya2l0dGVuMTAy"),
    ("kitten102sitting102", "a2l0dGVuMTAyc2l0dGluZzEwMg"),
    ("kitten102agent102", "a2l0dGVuMTAyYWdlbnQxMDI"),
    ("kitten102angle102", "a2l0dGVuMTAyYW5nbGUxMDI"),
    ("sitting102angle102", "c2l0dGluZzEwMmFuZ2xlMTAy"),
    ("sitting102universe102", "c2l0dGluZzEwMnVuaXZlcnNlMTAy"),
    ("sitting102memory102", "c2l0dGluZzEwMm1lbW9yeTEwMg"),
    ("sitting102stream102", "c2l0dGluZzEwMnN0cmVhbTEwMg"),
    ("agent102stream102", "YWdlbnQxMDJzdHJlYW0xMDI"),
    ("agent102context102", "YWdlbnQxMDJjb250ZXh0MTAy"),
    ("agent102knowledge102", "YWdlbnQxMDJrbm93bGVkZ2UxMDI"),
    ("agent102vector102", "YWdlbnQxMDJ2ZWN0b3IxMDI"),
    ("angle102vector102", "YW5nbGUxMDJ2ZWN0b3IxMDI"),
    ("angle102processor102", "YW5nbGUxMDJwcm9jZXNzb3IxMDI"),
    ("angle102reasoning102", "YW5nbGUxMDJyZWFzb25pbmcxMDI"),
    ("angle102machine102", "YW5nbGUxMDJtYWNoaW5lMTAy"),
    ("universe102machine102", "dW5pdmVyc2UxMDJtYWNoaW5lMTAy"),
    ("universe102learning102", "dW5pdmVyc2UxMDJsZWFybmluZzEwMg"),
    ("universe102model102", "dW5pdmVyc2UxMDJtb2RlbDEwMg"),
    ("universe102token102", "dW5pdmVyc2UxMDJ0b2tlbjEwMg"),
    ("memory102token102", "bWVtb3J5MTAydG9rZW4xMDI"),
    ("memory102prompt102", "bWVtb3J5MTAycHJvbXB0MTAy"),
    ("memory102session102", "bWVtb3J5MTAyc2Vzc2lvbjEwMg"),
    ("memory102library102", "bWVtb3J5MTAybGlicmFyeTEwMg"),
    ("stream102library102", "c3RyZWFtMTAybGlicmFyeTEwMg"),
    ("stream102service102", "c3RyZWFtMTAyc2VydmljZTEwMg"),
    ("stream102gateway102", "c3RyZWFtMTAyZ2F0ZXdheTEwMg"),
    ("stream102storage102", "c3RyZWFtMTAyc3RvcmFnZTEwMg"),
    ("context102storage102", "Y29udGV4dDEwMnN0b3JhZ2UxMDI"),
    ("context102network102", "Y29udGV4dDEwMm5ldHdvcmsxMDI"),
    ("context102latency102", "Y29udGV4dDEwMmxhdGVuY3kxMDI"),
    ("context102buffer102", "Y29udGV4dDEwMmJ1ZmZlcjEwMg"),
    ("knowledge102buffer102", "a25vd2xlZGdlMTAyYnVmZmVyMTAy"),
    ("knowledge102queue102", "a25vd2xlZGdlMTAycXVldWUxMDI"),
    ("knowledge102worker102", "a25vd2xlZGdlMTAyd29ya2VyMTAy"),
    ("knowledge102kernel102", "a25vd2xlZGdlMTAya2VybmVsMTAy"),
    ("vector102kernel102", "dmVjdG9yMTAya2VybmVsMTAy"),
    ("vector102signal102", "dmVjdG9yMTAyc2lnbmFsMTAy"),
    ("vector102packet102", "dmVjdG9yMTAycGFja2V0MTAy"),
    ("vector102router102", "dmVjdG9yMTAycm91dGVyMTAy"),
    ("processor102router102", "cHJvY2Vzc29yMTAycm91dGVyMTAy"),
    ("processor102cluster102", "cHJvY2Vzc29yMTAyY2x1c3RlcjEwMg"),
    ("processor102mirror102", "cHJvY2Vzc29yMTAybWlycm9yMTAy"),
    ("processor102filter102", "cHJvY2Vzc29yMTAyZmlsdGVyMTAy"),
    ("reasoning102filter102", "cmVhc29uaW5nMTAyZmlsdGVyMTAy"),
    ("reasoning102ranking102", "cmVhc29uaW5nMTAycmFua2luZzEwMg"),
    ("reasoning102encoding102", "cmVhc29uaW5nMTAyZW5jb2RpbmcxMDI"),
    ("reasoning102mapping102", "cmVhc29uaW5nMTAybWFwcGluZzEwMg"),
    ("machine102mapping102", "bWFjaGluZTEwMm1hcHBpbmcxMDI"),
    ("machine102record102", "bWFjaGluZTEwMnJlY29yZDEwMg"),
    ("machine102candle102", "bWFjaGluZTEwMmNhbmRsZTEwMg"),
    ("machine102thread102", "bWFjaGluZTEwMnRocmVhZDEwMg"),
    ("learning102thread102", "bGVhcm5pbmcxMDJ0aHJlYWQxMDI"),
    ("learning102kitten102", "bGVhcm5pbmcxMDJraXR0ZW4xMDI"),
    ("learning102sitting102", "bGVhcm5pbmcxMDJzaXR0aW5nMTAy"),
    ("learning102agent102", "bGVhcm5pbmcxMDJhZ2VudDEwMg"),
    ("model102agent102", "bW9kZWwxMDJhZ2VudDEwMg"),
    ("model102angle102", "bW9kZWwxMDJhbmdsZTEwMg"),
    ("model102universe102", "bW9kZWwxMDJ1bml2ZXJzZTEwMg"),
    ("model102memory102", "bW9kZWwxMDJtZW1vcnkxMDI"),
    ("token102memory102", "dG9rZW4xMDJtZW1vcnkxMDI"),
    ("token102stream102", "dG9rZW4xMDJzdHJlYW0xMDI"),
    ("token102context102", "dG9rZW4xMDJjb250ZXh0MTAy"),
    ("token102knowledge102", "dG9rZW4xMDJrbm93bGVkZ2UxMDI"),
    ("prompt102knowledge102", "cHJvbXB0MTAya25vd2xlZGdlMTAy"),
    ("prompt102vector102", "cHJvbXB0MTAydmVjdG9yMTAy"),
    ("prompt102processor102", "cHJvbXB0MTAycHJvY2Vzc29yMTAy"),
    ("prompt102reasoning102", "cHJvbXB0MTAycmVhc29uaW5nMTAy"),
    ("session102reasoning102", "c2Vzc2lvbjEwMnJlYXNvbmluZzEwMg"),
    ("session102machine102", "c2Vzc2lvbjEwMm1hY2hpbmUxMDI"),
    ("session102learning102", "c2Vzc2lvbjEwMmxlYXJuaW5nMTAy"),
    ("session102model102", "c2Vzc2lvbjEwMm1vZGVsMTAy"),
    ("library102model102", "bGlicmFyeTEwMm1vZGVsMTAy"),
    ("library102token102", "bGlicmFyeTEwMnRva2VuMTAy"),
    ("library102prompt102", "bGlicmFyeTEwMnByb21wdDEwMg"),
    ("library102session102", "bGlicmFyeTEwMnNlc3Npb24xMDI"),
    ("service102session102", "c2VydmljZTEwMnNlc3Npb24xMDI"),
    ("service102library102", "c2VydmljZTEwMmxpYnJhcnkxMDI"),
    ("service102service102", "c2VydmljZTEwMnNlcnZpY2UxMDI"),
    ("service102gateway102", "c2VydmljZTEwMmdhdGV3YXkxMDI"),
    ("gateway102gateway102", "Z2F0ZXdheTEwMmdhdGV3YXkxMDI"),
    ("gateway102storage102", "Z2F0ZXdheTEwMnN0b3JhZ2UxMDI"),
    ("gateway102network102", "Z2F0ZXdheTEwMm5ldHdvcmsxMDI"),
    ("gateway102latency102", "Z2F0ZXdheTEwMmxhdGVuY3kxMDI"),
    ("storage102latency102", "c3RvcmFnZTEwMmxhdGVuY3kxMDI"),
    ("storage102buffer102", "c3RvcmFnZTEwMmJ1ZmZlcjEwMg"),
    ("storage102queue102", "c3RvcmFnZTEwMnF1ZXVlMTAy"),
    ("storage102worker102", "c3RvcmFnZTEwMndvcmtlcjEwMg"),
    ("network102worker102", "bmV0d29yazEwMndvcmtlcjEwMg"),
    ("network102kernel102", "bmV0d29yazEwMmtlcm5lbDEwMg"),
    ("network102signal102", "bmV0d29yazEwMnNpZ25hbDEwMg"),
    ("network102packet102", "bmV0d29yazEwMnBhY2tldDEwMg"),
    ("latency102packet102", "bGF0ZW5jeTEwMnBhY2tldDEwMg"),
    ("latency102router102", "bGF0ZW5jeTEwMnJvdXRlcjEwMg"),
    ("latency102cluster102", "bGF0ZW5jeTEwMmNsdXN0ZXIxMDI"),
    ("latency102mirror102", "bGF0ZW5jeTEwMm1pcnJvcjEwMg"),
    ("buffer102mirror102", "YnVmZmVyMTAybWlycm9yMTAy"),
    ("buffer102filter102", "YnVmZmVyMTAyZmlsdGVyMTAy"),
    ("buffer102ranking102", "YnVmZmVyMTAycmFua2luZzEwMg"),
    ("buffer102encoding102", "YnVmZmVyMTAyZW5jb2RpbmcxMDI"),
    ("queue102encoding102", "cXVldWUxMDJlbmNvZGluZzEwMg"),
    ("queue102mapping102", "cXVldWUxMDJtYXBwaW5nMTAy"),
    ("queue102record102", "cXVldWUxMDJyZWNvcmQxMDI"),
    ("queue102candle102", "cXVldWUxMDJjYW5kbGUxMDI"),
    ("worker102candle102", "d29ya2VyMTAyY2FuZGxlMTAy"),
    ("worker102thread102", "d29ya2VyMTAydGhyZWFkMTAy"),
    ("worker102kitten102", "d29ya2VyMTAya2l0dGVuMTAy"),
    ("worker102sitting102", "d29ya2VyMTAyc2l0dGluZzEwMg"),
    ("kernel102sitting102", "a2VybmVsMTAyc2l0dGluZzEwMg"),
    ("kernel102agent102", "a2VybmVsMTAyYWdlbnQxMDI"),
    ("kernel102angle102", "a2VybmVsMTAyYW5nbGUxMDI"),
    ("kernel102universe102", "a2VybmVsMTAydW5pdmVyc2UxMDI"),
    ("signal102universe102", "c2lnbmFsMTAydW5pdmVyc2UxMDI"),
    ("signal102memory102", "c2lnbmFsMTAybWVtb3J5MTAy"),
    ("signal102stream102", "c2lnbmFsMTAyc3RyZWFtMTAy"),
    ("signal102context102", "c2lnbmFsMTAyY29udGV4dDEwMg"),
    ("packet102context102", "cGFja2V0MTAyY29udGV4dDEwMg"),
    ("packet102knowledge102", "cGFja2V0MTAya25vd2xlZGdlMTAy"),
    ("packet102vector102", "cGFja2V0MTAydmVjdG9yMTAy"),
    ("packet102processor102", "cGFja2V0MTAycHJvY2Vzc29yMTAy"),
    ("router102processor102", "cm91dGVyMTAycHJvY2Vzc29yMTAy"),
    ("router102reasoning102", "cm91dGVyMTAycmVhc29uaW5nMTAy"),
    ("router102machine102", "cm91dGVyMTAybWFjaGluZTEwMg"),
    ("router102learning102", "cm91dGVyMTAybGVhcm5pbmcxMDI"),
    ("cluster102learning102", "Y2x1c3RlcjEwMmxlYXJuaW5nMTAy"),
    ("cluster102model102", "Y2x1c3RlcjEwMm1vZGVsMTAy"),
    ("cluster102token102", "Y2x1c3RlcjEwMnRva2VuMTAy"),
    ("cluster102prompt102", "Y2x1c3RlcjEwMnByb21wdDEwMg"),
    ("mirror102prompt102", "bWlycm9yMTAycHJvbXB0MTAy"),
    ("mirror102session102", "bWlycm9yMTAyc2Vzc2lvbjEwMg"),
    ("mirror102library102", "bWlycm9yMTAybGlicmFyeTEwMg"),
    ("mirror102service102", "bWlycm9yMTAyc2VydmljZTEwMg"),
    ("filter102service102", "ZmlsdGVyMTAyc2VydmljZTEwMg"),
    ("filter102gateway102", "ZmlsdGVyMTAyZ2F0ZXdheTEwMg"),
    ("filter102storage102", "ZmlsdGVyMTAyc3RvcmFnZTEwMg"),
    ("filter102network102", "ZmlsdGVyMTAybmV0d29yazEwMg"),
    ("ranking102network102", "cmFua2luZzEwMm5ldHdvcmsxMDI"),
    ("ranking102latency102", "cmFua2luZzEwMmxhdGVuY3kxMDI"),
    ("ranking102buffer102", "cmFua2luZzEwMmJ1ZmZlcjEwMg"),
    ("ranking102queue102", "cmFua2luZzEwMnF1ZXVlMTAy"),
    ("encoding102queue102", "ZW5jb2RpbmcxMDJxdWV1ZTEwMg"),
    ("encoding102worker102", "ZW5jb2RpbmcxMDJ3b3JrZXIxMDI"),
    ("encoding102kernel102", "ZW5jb2RpbmcxMDJrZXJuZWwxMDI"),
    ("encoding102signal102", "ZW5jb2RpbmcxMDJzaWduYWwxMDI"),
    ("mapping102signal102", "bWFwcGluZzEwMnNpZ25hbDEwMg"),
    ("mapping102packet102", "bWFwcGluZzEwMnBhY2tldDEwMg"),
    ("mapping102router102", "bWFwcGluZzEwMnJvdXRlcjEwMg"),
    ("mapping102cluster102", "bWFwcGluZzEwMmNsdXN0ZXIxMDI"),
    ("record102cluster102", "cmVjb3JkMTAyY2x1c3RlcjEwMg"),
    ("record102mirror102", "cmVjb3JkMTAybWlycm9yMTAy"),
    ("record102filter102", "cmVjb3JkMTAyZmlsdGVyMTAy"),
    ("record102ranking102", "cmVjb3JkMTAycmFua2luZzEwMg"),
    ("candle102ranking102", "Y2FuZGxlMTAycmFua2luZzEwMg"),
    ("candle102encoding102", "Y2FuZGxlMTAyZW5jb2RpbmcxMDI"),
    ("candle102mapping102", "Y2FuZGxlMTAybWFwcGluZzEwMg"),
    ("candle102record102", "Y2FuZGxlMTAycmVjb3JkMTAy"),
    ("thread102record102", "dGhyZWFkMTAycmVjb3JkMTAy"),
    ("thread102candle102", "dGhyZWFkMTAyY2FuZGxlMTAy"),
    ("thread102thread102", "dGhyZWFkMTAydGhyZWFkMTAy"),
    ("thread102kitten102", "dGhyZWFkMTAya2l0dGVuMTAy"),
    (
        "round 102: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTAyOiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 102: agentuniverse is a framework for multi agents",
        "cm91bmQgMTAyOiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 102: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTAyOiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 102: the processor reads the record then stops",
        "cm91bmQgMTAyOiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 102: a worker pulls the next task from the queue",
        "cm91bmQgMTAyOiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 102: signals travel through the network layer",
        "cm91bmQgMTAyOiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 102: the gateway routes each request by policy",
        "cm91bmQgMTAyOiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 102: memory grows until the buffer is full",
        "cm91bmQgMTAyOiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 102: the cluster mirrors every packet twice",
        "cm91bmQgMTAyOiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 102: ranking uses tokens learned from the corpus",
        "cm91bmQgMTAyOiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 102: a long session ends when the candle dies",
        "cm91bmQgMTAyOiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 102: encode the prompt then map the result",
        "cm91bmQgMTAyOiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 102: the kernel wakes the worker at dawn",
        "cm91bmQgMTAyOiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 102: service latency drops after the patch",
        "cm91bmQgMTAyOiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 102: the library caches every vector it sees",
        "cm91bmQgMTAyOiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 102: agents argue then the debate resolves",
        "cm91bmQgMTAyOiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 102: the filter keeps only strong matches",
        "cm91bmQgMTAyOiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 102: the model answers with a short reply",
        "cm91bmQgMTAyOiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 102: the recorder stores the reasoning trace",
        "cm91bmQgMTAyOiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 102: the angel watches the processor run",
        "cm91bmQgMTAyOiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 102: angle of the vector decides the match",
        "cm91bmQgMTAyOiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 102: the candle burns twice as long at night",
        "cm91bmQgMTAyOiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 102: a mirror of the universe in one line",
        "cm91bmQgMTAyOiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 102: the queue drains before the storm", "cm91bmQgMTAyOiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
