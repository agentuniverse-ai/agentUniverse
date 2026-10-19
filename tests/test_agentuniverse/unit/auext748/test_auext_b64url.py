"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten748kitten748", "a2l0dGVuNzQ4a2l0dGVuNzQ4"),
    ("kitten748sitting748", "a2l0dGVuNzQ4c2l0dGluZzc0OA"),
    ("kitten748agent748", "a2l0dGVuNzQ4YWdlbnQ3NDg"),
    ("kitten748angle748", "a2l0dGVuNzQ4YW5nbGU3NDg"),
    ("sitting748angle748", "c2l0dGluZzc0OGFuZ2xlNzQ4"),
    ("sitting748universe748", "c2l0dGluZzc0OHVuaXZlcnNlNzQ4"),
    ("sitting748memory748", "c2l0dGluZzc0OG1lbW9yeTc0OA"),
    ("sitting748stream748", "c2l0dGluZzc0OHN0cmVhbTc0OA"),
    ("agent748stream748", "YWdlbnQ3NDhzdHJlYW03NDg"),
    ("agent748context748", "YWdlbnQ3NDhjb250ZXh0NzQ4"),
    ("agent748knowledge748", "YWdlbnQ3NDhrbm93bGVkZ2U3NDg"),
    ("agent748vector748", "YWdlbnQ3NDh2ZWN0b3I3NDg"),
    ("angle748vector748", "YW5nbGU3NDh2ZWN0b3I3NDg"),
    ("angle748processor748", "YW5nbGU3NDhwcm9jZXNzb3I3NDg"),
    ("angle748reasoning748", "YW5nbGU3NDhyZWFzb25pbmc3NDg"),
    ("angle748machine748", "YW5nbGU3NDhtYWNoaW5lNzQ4"),
    ("universe748machine748", "dW5pdmVyc2U3NDhtYWNoaW5lNzQ4"),
    ("universe748learning748", "dW5pdmVyc2U3NDhsZWFybmluZzc0OA"),
    ("universe748model748", "dW5pdmVyc2U3NDhtb2RlbDc0OA"),
    ("universe748token748", "dW5pdmVyc2U3NDh0b2tlbjc0OA"),
    ("memory748token748", "bWVtb3J5NzQ4dG9rZW43NDg"),
    ("memory748prompt748", "bWVtb3J5NzQ4cHJvbXB0NzQ4"),
    ("memory748session748", "bWVtb3J5NzQ4c2Vzc2lvbjc0OA"),
    ("memory748library748", "bWVtb3J5NzQ4bGlicmFyeTc0OA"),
    ("stream748library748", "c3RyZWFtNzQ4bGlicmFyeTc0OA"),
    ("stream748service748", "c3RyZWFtNzQ4c2VydmljZTc0OA"),
    ("stream748gateway748", "c3RyZWFtNzQ4Z2F0ZXdheTc0OA"),
    ("stream748storage748", "c3RyZWFtNzQ4c3RvcmFnZTc0OA"),
    ("context748storage748", "Y29udGV4dDc0OHN0b3JhZ2U3NDg"),
    ("context748network748", "Y29udGV4dDc0OG5ldHdvcms3NDg"),
    ("context748latency748", "Y29udGV4dDc0OGxhdGVuY3k3NDg"),
    ("context748buffer748", "Y29udGV4dDc0OGJ1ZmZlcjc0OA"),
    ("knowledge748buffer748", "a25vd2xlZGdlNzQ4YnVmZmVyNzQ4"),
    ("knowledge748queue748", "a25vd2xlZGdlNzQ4cXVldWU3NDg"),
    ("knowledge748worker748", "a25vd2xlZGdlNzQ4d29ya2VyNzQ4"),
    ("knowledge748kernel748", "a25vd2xlZGdlNzQ4a2VybmVsNzQ4"),
    ("vector748kernel748", "dmVjdG9yNzQ4a2VybmVsNzQ4"),
    ("vector748signal748", "dmVjdG9yNzQ4c2lnbmFsNzQ4"),
    ("vector748packet748", "dmVjdG9yNzQ4cGFja2V0NzQ4"),
    ("vector748router748", "dmVjdG9yNzQ4cm91dGVyNzQ4"),
    ("processor748router748", "cHJvY2Vzc29yNzQ4cm91dGVyNzQ4"),
    ("processor748cluster748", "cHJvY2Vzc29yNzQ4Y2x1c3Rlcjc0OA"),
    ("processor748mirror748", "cHJvY2Vzc29yNzQ4bWlycm9yNzQ4"),
    ("processor748filter748", "cHJvY2Vzc29yNzQ4ZmlsdGVyNzQ4"),
    ("reasoning748filter748", "cmVhc29uaW5nNzQ4ZmlsdGVyNzQ4"),
    ("reasoning748ranking748", "cmVhc29uaW5nNzQ4cmFua2luZzc0OA"),
    ("reasoning748encoding748", "cmVhc29uaW5nNzQ4ZW5jb2Rpbmc3NDg"),
    ("reasoning748mapping748", "cmVhc29uaW5nNzQ4bWFwcGluZzc0OA"),
    ("machine748mapping748", "bWFjaGluZTc0OG1hcHBpbmc3NDg"),
    ("machine748record748", "bWFjaGluZTc0OHJlY29yZDc0OA"),
    ("machine748candle748", "bWFjaGluZTc0OGNhbmRsZTc0OA"),
    ("machine748thread748", "bWFjaGluZTc0OHRocmVhZDc0OA"),
    ("learning748thread748", "bGVhcm5pbmc3NDh0aHJlYWQ3NDg"),
    ("learning748kitten748", "bGVhcm5pbmc3NDhraXR0ZW43NDg"),
    ("learning748sitting748", "bGVhcm5pbmc3NDhzaXR0aW5nNzQ4"),
    ("learning748agent748", "bGVhcm5pbmc3NDhhZ2VudDc0OA"),
    ("model748agent748", "bW9kZWw3NDhhZ2VudDc0OA"),
    ("model748angle748", "bW9kZWw3NDhhbmdsZTc0OA"),
    ("model748universe748", "bW9kZWw3NDh1bml2ZXJzZTc0OA"),
    ("model748memory748", "bW9kZWw3NDhtZW1vcnk3NDg"),
    ("token748memory748", "dG9rZW43NDhtZW1vcnk3NDg"),
    ("token748stream748", "dG9rZW43NDhzdHJlYW03NDg"),
    ("token748context748", "dG9rZW43NDhjb250ZXh0NzQ4"),
    ("token748knowledge748", "dG9rZW43NDhrbm93bGVkZ2U3NDg"),
    ("prompt748knowledge748", "cHJvbXB0NzQ4a25vd2xlZGdlNzQ4"),
    ("prompt748vector748", "cHJvbXB0NzQ4dmVjdG9yNzQ4"),
    ("prompt748processor748", "cHJvbXB0NzQ4cHJvY2Vzc29yNzQ4"),
    ("prompt748reasoning748", "cHJvbXB0NzQ4cmVhc29uaW5nNzQ4"),
    ("session748reasoning748", "c2Vzc2lvbjc0OHJlYXNvbmluZzc0OA"),
    ("session748machine748", "c2Vzc2lvbjc0OG1hY2hpbmU3NDg"),
    ("session748learning748", "c2Vzc2lvbjc0OGxlYXJuaW5nNzQ4"),
    ("session748model748", "c2Vzc2lvbjc0OG1vZGVsNzQ4"),
    ("library748model748", "bGlicmFyeTc0OG1vZGVsNzQ4"),
    ("library748token748", "bGlicmFyeTc0OHRva2VuNzQ4"),
    ("library748prompt748", "bGlicmFyeTc0OHByb21wdDc0OA"),
    ("library748session748", "bGlicmFyeTc0OHNlc3Npb243NDg"),
    ("service748session748", "c2VydmljZTc0OHNlc3Npb243NDg"),
    ("service748library748", "c2VydmljZTc0OGxpYnJhcnk3NDg"),
    ("service748service748", "c2VydmljZTc0OHNlcnZpY2U3NDg"),
    ("service748gateway748", "c2VydmljZTc0OGdhdGV3YXk3NDg"),
    ("gateway748gateway748", "Z2F0ZXdheTc0OGdhdGV3YXk3NDg"),
    ("gateway748storage748", "Z2F0ZXdheTc0OHN0b3JhZ2U3NDg"),
    ("gateway748network748", "Z2F0ZXdheTc0OG5ldHdvcms3NDg"),
    ("gateway748latency748", "Z2F0ZXdheTc0OGxhdGVuY3k3NDg"),
    ("storage748latency748", "c3RvcmFnZTc0OGxhdGVuY3k3NDg"),
    ("storage748buffer748", "c3RvcmFnZTc0OGJ1ZmZlcjc0OA"),
    ("storage748queue748", "c3RvcmFnZTc0OHF1ZXVlNzQ4"),
    ("storage748worker748", "c3RvcmFnZTc0OHdvcmtlcjc0OA"),
    ("network748worker748", "bmV0d29yazc0OHdvcmtlcjc0OA"),
    ("network748kernel748", "bmV0d29yazc0OGtlcm5lbDc0OA"),
    ("network748signal748", "bmV0d29yazc0OHNpZ25hbDc0OA"),
    ("network748packet748", "bmV0d29yazc0OHBhY2tldDc0OA"),
    ("latency748packet748", "bGF0ZW5jeTc0OHBhY2tldDc0OA"),
    ("latency748router748", "bGF0ZW5jeTc0OHJvdXRlcjc0OA"),
    ("latency748cluster748", "bGF0ZW5jeTc0OGNsdXN0ZXI3NDg"),
    ("latency748mirror748", "bGF0ZW5jeTc0OG1pcnJvcjc0OA"),
    ("buffer748mirror748", "YnVmZmVyNzQ4bWlycm9yNzQ4"),
    ("buffer748filter748", "YnVmZmVyNzQ4ZmlsdGVyNzQ4"),
    ("buffer748ranking748", "YnVmZmVyNzQ4cmFua2luZzc0OA"),
    ("buffer748encoding748", "YnVmZmVyNzQ4ZW5jb2Rpbmc3NDg"),
    ("queue748encoding748", "cXVldWU3NDhlbmNvZGluZzc0OA"),
    ("queue748mapping748", "cXVldWU3NDhtYXBwaW5nNzQ4"),
    ("queue748record748", "cXVldWU3NDhyZWNvcmQ3NDg"),
    ("queue748candle748", "cXVldWU3NDhjYW5kbGU3NDg"),
    ("worker748candle748", "d29ya2VyNzQ4Y2FuZGxlNzQ4"),
    ("worker748thread748", "d29ya2VyNzQ4dGhyZWFkNzQ4"),
    ("worker748kitten748", "d29ya2VyNzQ4a2l0dGVuNzQ4"),
    ("worker748sitting748", "d29ya2VyNzQ4c2l0dGluZzc0OA"),
    ("kernel748sitting748", "a2VybmVsNzQ4c2l0dGluZzc0OA"),
    ("kernel748agent748", "a2VybmVsNzQ4YWdlbnQ3NDg"),
    ("kernel748angle748", "a2VybmVsNzQ4YW5nbGU3NDg"),
    ("kernel748universe748", "a2VybmVsNzQ4dW5pdmVyc2U3NDg"),
    ("signal748universe748", "c2lnbmFsNzQ4dW5pdmVyc2U3NDg"),
    ("signal748memory748", "c2lnbmFsNzQ4bWVtb3J5NzQ4"),
    ("signal748stream748", "c2lnbmFsNzQ4c3RyZWFtNzQ4"),
    ("signal748context748", "c2lnbmFsNzQ4Y29udGV4dDc0OA"),
    ("packet748context748", "cGFja2V0NzQ4Y29udGV4dDc0OA"),
    ("packet748knowledge748", "cGFja2V0NzQ4a25vd2xlZGdlNzQ4"),
    ("packet748vector748", "cGFja2V0NzQ4dmVjdG9yNzQ4"),
    ("packet748processor748", "cGFja2V0NzQ4cHJvY2Vzc29yNzQ4"),
    ("router748processor748", "cm91dGVyNzQ4cHJvY2Vzc29yNzQ4"),
    ("router748reasoning748", "cm91dGVyNzQ4cmVhc29uaW5nNzQ4"),
    ("router748machine748", "cm91dGVyNzQ4bWFjaGluZTc0OA"),
    ("router748learning748", "cm91dGVyNzQ4bGVhcm5pbmc3NDg"),
    ("cluster748learning748", "Y2x1c3Rlcjc0OGxlYXJuaW5nNzQ4"),
    ("cluster748model748", "Y2x1c3Rlcjc0OG1vZGVsNzQ4"),
    ("cluster748token748", "Y2x1c3Rlcjc0OHRva2VuNzQ4"),
    ("cluster748prompt748", "Y2x1c3Rlcjc0OHByb21wdDc0OA"),
    ("mirror748prompt748", "bWlycm9yNzQ4cHJvbXB0NzQ4"),
    ("mirror748session748", "bWlycm9yNzQ4c2Vzc2lvbjc0OA"),
    ("mirror748library748", "bWlycm9yNzQ4bGlicmFyeTc0OA"),
    ("mirror748service748", "bWlycm9yNzQ4c2VydmljZTc0OA"),
    ("filter748service748", "ZmlsdGVyNzQ4c2VydmljZTc0OA"),
    ("filter748gateway748", "ZmlsdGVyNzQ4Z2F0ZXdheTc0OA"),
    ("filter748storage748", "ZmlsdGVyNzQ4c3RvcmFnZTc0OA"),
    ("filter748network748", "ZmlsdGVyNzQ4bmV0d29yazc0OA"),
    ("ranking748network748", "cmFua2luZzc0OG5ldHdvcms3NDg"),
    ("ranking748latency748", "cmFua2luZzc0OGxhdGVuY3k3NDg"),
    ("ranking748buffer748", "cmFua2luZzc0OGJ1ZmZlcjc0OA"),
    ("ranking748queue748", "cmFua2luZzc0OHF1ZXVlNzQ4"),
    ("encoding748queue748", "ZW5jb2Rpbmc3NDhxdWV1ZTc0OA"),
    ("encoding748worker748", "ZW5jb2Rpbmc3NDh3b3JrZXI3NDg"),
    ("encoding748kernel748", "ZW5jb2Rpbmc3NDhrZXJuZWw3NDg"),
    ("encoding748signal748", "ZW5jb2Rpbmc3NDhzaWduYWw3NDg"),
    ("mapping748signal748", "bWFwcGluZzc0OHNpZ25hbDc0OA"),
    ("mapping748packet748", "bWFwcGluZzc0OHBhY2tldDc0OA"),
    ("mapping748router748", "bWFwcGluZzc0OHJvdXRlcjc0OA"),
    ("mapping748cluster748", "bWFwcGluZzc0OGNsdXN0ZXI3NDg"),
    ("record748cluster748", "cmVjb3JkNzQ4Y2x1c3Rlcjc0OA"),
    ("record748mirror748", "cmVjb3JkNzQ4bWlycm9yNzQ4"),
    ("record748filter748", "cmVjb3JkNzQ4ZmlsdGVyNzQ4"),
    ("record748ranking748", "cmVjb3JkNzQ4cmFua2luZzc0OA"),
    ("candle748ranking748", "Y2FuZGxlNzQ4cmFua2luZzc0OA"),
    ("candle748encoding748", "Y2FuZGxlNzQ4ZW5jb2Rpbmc3NDg"),
    ("candle748mapping748", "Y2FuZGxlNzQ4bWFwcGluZzc0OA"),
    ("candle748record748", "Y2FuZGxlNzQ4cmVjb3JkNzQ4"),
    ("thread748record748", "dGhyZWFkNzQ4cmVjb3JkNzQ4"),
    ("thread748candle748", "dGhyZWFkNzQ4Y2FuZGxlNzQ4"),
    ("thread748thread748", "dGhyZWFkNzQ4dGhyZWFkNzQ4"),
    ("thread748kitten748", "dGhyZWFkNzQ4a2l0dGVuNzQ4"),
    (
        "round 748: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNzQ4OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 748: agentuniverse is a framework for multi agents",
        "cm91bmQgNzQ4OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 748: knowledge stored as vectors enables retrieval",
        "cm91bmQgNzQ4OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 748: the processor reads the record then stops",
        "cm91bmQgNzQ4OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 748: a worker pulls the next task from the queue",
        "cm91bmQgNzQ4OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 748: signals travel through the network layer",
        "cm91bmQgNzQ4OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 748: the gateway routes each request by policy",
        "cm91bmQgNzQ4OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 748: memory grows until the buffer is full",
        "cm91bmQgNzQ4OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 748: the cluster mirrors every packet twice",
        "cm91bmQgNzQ4OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 748: ranking uses tokens learned from the corpus",
        "cm91bmQgNzQ4OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 748: a long session ends when the candle dies",
        "cm91bmQgNzQ4OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 748: encode the prompt then map the result",
        "cm91bmQgNzQ4OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 748: the kernel wakes the worker at dawn",
        "cm91bmQgNzQ4OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 748: service latency drops after the patch",
        "cm91bmQgNzQ4OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 748: the library caches every vector it sees",
        "cm91bmQgNzQ4OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 748: agents argue then the debate resolves",
        "cm91bmQgNzQ4OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 748: the filter keeps only strong matches",
        "cm91bmQgNzQ4OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 748: the model answers with a short reply",
        "cm91bmQgNzQ4OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 748: the recorder stores the reasoning trace",
        "cm91bmQgNzQ4OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 748: the angel watches the processor run",
        "cm91bmQgNzQ4OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 748: angle of the vector decides the match",
        "cm91bmQgNzQ4OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 748: the candle burns twice as long at night",
        "cm91bmQgNzQ4OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 748: a mirror of the universe in one line",
        "cm91bmQgNzQ4OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 748: the queue drains before the storm", "cm91bmQgNzQ4OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
