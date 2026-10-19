"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten740kitten740", "a2l0dGVuNzQwa2l0dGVuNzQw"),
    ("kitten740sitting740", "a2l0dGVuNzQwc2l0dGluZzc0MA"),
    ("kitten740agent740", "a2l0dGVuNzQwYWdlbnQ3NDA"),
    ("kitten740angle740", "a2l0dGVuNzQwYW5nbGU3NDA"),
    ("sitting740angle740", "c2l0dGluZzc0MGFuZ2xlNzQw"),
    ("sitting740universe740", "c2l0dGluZzc0MHVuaXZlcnNlNzQw"),
    ("sitting740memory740", "c2l0dGluZzc0MG1lbW9yeTc0MA"),
    ("sitting740stream740", "c2l0dGluZzc0MHN0cmVhbTc0MA"),
    ("agent740stream740", "YWdlbnQ3NDBzdHJlYW03NDA"),
    ("agent740context740", "YWdlbnQ3NDBjb250ZXh0NzQw"),
    ("agent740knowledge740", "YWdlbnQ3NDBrbm93bGVkZ2U3NDA"),
    ("agent740vector740", "YWdlbnQ3NDB2ZWN0b3I3NDA"),
    ("angle740vector740", "YW5nbGU3NDB2ZWN0b3I3NDA"),
    ("angle740processor740", "YW5nbGU3NDBwcm9jZXNzb3I3NDA"),
    ("angle740reasoning740", "YW5nbGU3NDByZWFzb25pbmc3NDA"),
    ("angle740machine740", "YW5nbGU3NDBtYWNoaW5lNzQw"),
    ("universe740machine740", "dW5pdmVyc2U3NDBtYWNoaW5lNzQw"),
    ("universe740learning740", "dW5pdmVyc2U3NDBsZWFybmluZzc0MA"),
    ("universe740model740", "dW5pdmVyc2U3NDBtb2RlbDc0MA"),
    ("universe740token740", "dW5pdmVyc2U3NDB0b2tlbjc0MA"),
    ("memory740token740", "bWVtb3J5NzQwdG9rZW43NDA"),
    ("memory740prompt740", "bWVtb3J5NzQwcHJvbXB0NzQw"),
    ("memory740session740", "bWVtb3J5NzQwc2Vzc2lvbjc0MA"),
    ("memory740library740", "bWVtb3J5NzQwbGlicmFyeTc0MA"),
    ("stream740library740", "c3RyZWFtNzQwbGlicmFyeTc0MA"),
    ("stream740service740", "c3RyZWFtNzQwc2VydmljZTc0MA"),
    ("stream740gateway740", "c3RyZWFtNzQwZ2F0ZXdheTc0MA"),
    ("stream740storage740", "c3RyZWFtNzQwc3RvcmFnZTc0MA"),
    ("context740storage740", "Y29udGV4dDc0MHN0b3JhZ2U3NDA"),
    ("context740network740", "Y29udGV4dDc0MG5ldHdvcms3NDA"),
    ("context740latency740", "Y29udGV4dDc0MGxhdGVuY3k3NDA"),
    ("context740buffer740", "Y29udGV4dDc0MGJ1ZmZlcjc0MA"),
    ("knowledge740buffer740", "a25vd2xlZGdlNzQwYnVmZmVyNzQw"),
    ("knowledge740queue740", "a25vd2xlZGdlNzQwcXVldWU3NDA"),
    ("knowledge740worker740", "a25vd2xlZGdlNzQwd29ya2VyNzQw"),
    ("knowledge740kernel740", "a25vd2xlZGdlNzQwa2VybmVsNzQw"),
    ("vector740kernel740", "dmVjdG9yNzQwa2VybmVsNzQw"),
    ("vector740signal740", "dmVjdG9yNzQwc2lnbmFsNzQw"),
    ("vector740packet740", "dmVjdG9yNzQwcGFja2V0NzQw"),
    ("vector740router740", "dmVjdG9yNzQwcm91dGVyNzQw"),
    ("processor740router740", "cHJvY2Vzc29yNzQwcm91dGVyNzQw"),
    ("processor740cluster740", "cHJvY2Vzc29yNzQwY2x1c3Rlcjc0MA"),
    ("processor740mirror740", "cHJvY2Vzc29yNzQwbWlycm9yNzQw"),
    ("processor740filter740", "cHJvY2Vzc29yNzQwZmlsdGVyNzQw"),
    ("reasoning740filter740", "cmVhc29uaW5nNzQwZmlsdGVyNzQw"),
    ("reasoning740ranking740", "cmVhc29uaW5nNzQwcmFua2luZzc0MA"),
    ("reasoning740encoding740", "cmVhc29uaW5nNzQwZW5jb2Rpbmc3NDA"),
    ("reasoning740mapping740", "cmVhc29uaW5nNzQwbWFwcGluZzc0MA"),
    ("machine740mapping740", "bWFjaGluZTc0MG1hcHBpbmc3NDA"),
    ("machine740record740", "bWFjaGluZTc0MHJlY29yZDc0MA"),
    ("machine740candle740", "bWFjaGluZTc0MGNhbmRsZTc0MA"),
    ("machine740thread740", "bWFjaGluZTc0MHRocmVhZDc0MA"),
    ("learning740thread740", "bGVhcm5pbmc3NDB0aHJlYWQ3NDA"),
    ("learning740kitten740", "bGVhcm5pbmc3NDBraXR0ZW43NDA"),
    ("learning740sitting740", "bGVhcm5pbmc3NDBzaXR0aW5nNzQw"),
    ("learning740agent740", "bGVhcm5pbmc3NDBhZ2VudDc0MA"),
    ("model740agent740", "bW9kZWw3NDBhZ2VudDc0MA"),
    ("model740angle740", "bW9kZWw3NDBhbmdsZTc0MA"),
    ("model740universe740", "bW9kZWw3NDB1bml2ZXJzZTc0MA"),
    ("model740memory740", "bW9kZWw3NDBtZW1vcnk3NDA"),
    ("token740memory740", "dG9rZW43NDBtZW1vcnk3NDA"),
    ("token740stream740", "dG9rZW43NDBzdHJlYW03NDA"),
    ("token740context740", "dG9rZW43NDBjb250ZXh0NzQw"),
    ("token740knowledge740", "dG9rZW43NDBrbm93bGVkZ2U3NDA"),
    ("prompt740knowledge740", "cHJvbXB0NzQwa25vd2xlZGdlNzQw"),
    ("prompt740vector740", "cHJvbXB0NzQwdmVjdG9yNzQw"),
    ("prompt740processor740", "cHJvbXB0NzQwcHJvY2Vzc29yNzQw"),
    ("prompt740reasoning740", "cHJvbXB0NzQwcmVhc29uaW5nNzQw"),
    ("session740reasoning740", "c2Vzc2lvbjc0MHJlYXNvbmluZzc0MA"),
    ("session740machine740", "c2Vzc2lvbjc0MG1hY2hpbmU3NDA"),
    ("session740learning740", "c2Vzc2lvbjc0MGxlYXJuaW5nNzQw"),
    ("session740model740", "c2Vzc2lvbjc0MG1vZGVsNzQw"),
    ("library740model740", "bGlicmFyeTc0MG1vZGVsNzQw"),
    ("library740token740", "bGlicmFyeTc0MHRva2VuNzQw"),
    ("library740prompt740", "bGlicmFyeTc0MHByb21wdDc0MA"),
    ("library740session740", "bGlicmFyeTc0MHNlc3Npb243NDA"),
    ("service740session740", "c2VydmljZTc0MHNlc3Npb243NDA"),
    ("service740library740", "c2VydmljZTc0MGxpYnJhcnk3NDA"),
    ("service740service740", "c2VydmljZTc0MHNlcnZpY2U3NDA"),
    ("service740gateway740", "c2VydmljZTc0MGdhdGV3YXk3NDA"),
    ("gateway740gateway740", "Z2F0ZXdheTc0MGdhdGV3YXk3NDA"),
    ("gateway740storage740", "Z2F0ZXdheTc0MHN0b3JhZ2U3NDA"),
    ("gateway740network740", "Z2F0ZXdheTc0MG5ldHdvcms3NDA"),
    ("gateway740latency740", "Z2F0ZXdheTc0MGxhdGVuY3k3NDA"),
    ("storage740latency740", "c3RvcmFnZTc0MGxhdGVuY3k3NDA"),
    ("storage740buffer740", "c3RvcmFnZTc0MGJ1ZmZlcjc0MA"),
    ("storage740queue740", "c3RvcmFnZTc0MHF1ZXVlNzQw"),
    ("storage740worker740", "c3RvcmFnZTc0MHdvcmtlcjc0MA"),
    ("network740worker740", "bmV0d29yazc0MHdvcmtlcjc0MA"),
    ("network740kernel740", "bmV0d29yazc0MGtlcm5lbDc0MA"),
    ("network740signal740", "bmV0d29yazc0MHNpZ25hbDc0MA"),
    ("network740packet740", "bmV0d29yazc0MHBhY2tldDc0MA"),
    ("latency740packet740", "bGF0ZW5jeTc0MHBhY2tldDc0MA"),
    ("latency740router740", "bGF0ZW5jeTc0MHJvdXRlcjc0MA"),
    ("latency740cluster740", "bGF0ZW5jeTc0MGNsdXN0ZXI3NDA"),
    ("latency740mirror740", "bGF0ZW5jeTc0MG1pcnJvcjc0MA"),
    ("buffer740mirror740", "YnVmZmVyNzQwbWlycm9yNzQw"),
    ("buffer740filter740", "YnVmZmVyNzQwZmlsdGVyNzQw"),
    ("buffer740ranking740", "YnVmZmVyNzQwcmFua2luZzc0MA"),
    ("buffer740encoding740", "YnVmZmVyNzQwZW5jb2Rpbmc3NDA"),
    ("queue740encoding740", "cXVldWU3NDBlbmNvZGluZzc0MA"),
    ("queue740mapping740", "cXVldWU3NDBtYXBwaW5nNzQw"),
    ("queue740record740", "cXVldWU3NDByZWNvcmQ3NDA"),
    ("queue740candle740", "cXVldWU3NDBjYW5kbGU3NDA"),
    ("worker740candle740", "d29ya2VyNzQwY2FuZGxlNzQw"),
    ("worker740thread740", "d29ya2VyNzQwdGhyZWFkNzQw"),
    ("worker740kitten740", "d29ya2VyNzQwa2l0dGVuNzQw"),
    ("worker740sitting740", "d29ya2VyNzQwc2l0dGluZzc0MA"),
    ("kernel740sitting740", "a2VybmVsNzQwc2l0dGluZzc0MA"),
    ("kernel740agent740", "a2VybmVsNzQwYWdlbnQ3NDA"),
    ("kernel740angle740", "a2VybmVsNzQwYW5nbGU3NDA"),
    ("kernel740universe740", "a2VybmVsNzQwdW5pdmVyc2U3NDA"),
    ("signal740universe740", "c2lnbmFsNzQwdW5pdmVyc2U3NDA"),
    ("signal740memory740", "c2lnbmFsNzQwbWVtb3J5NzQw"),
    ("signal740stream740", "c2lnbmFsNzQwc3RyZWFtNzQw"),
    ("signal740context740", "c2lnbmFsNzQwY29udGV4dDc0MA"),
    ("packet740context740", "cGFja2V0NzQwY29udGV4dDc0MA"),
    ("packet740knowledge740", "cGFja2V0NzQwa25vd2xlZGdlNzQw"),
    ("packet740vector740", "cGFja2V0NzQwdmVjdG9yNzQw"),
    ("packet740processor740", "cGFja2V0NzQwcHJvY2Vzc29yNzQw"),
    ("router740processor740", "cm91dGVyNzQwcHJvY2Vzc29yNzQw"),
    ("router740reasoning740", "cm91dGVyNzQwcmVhc29uaW5nNzQw"),
    ("router740machine740", "cm91dGVyNzQwbWFjaGluZTc0MA"),
    ("router740learning740", "cm91dGVyNzQwbGVhcm5pbmc3NDA"),
    ("cluster740learning740", "Y2x1c3Rlcjc0MGxlYXJuaW5nNzQw"),
    ("cluster740model740", "Y2x1c3Rlcjc0MG1vZGVsNzQw"),
    ("cluster740token740", "Y2x1c3Rlcjc0MHRva2VuNzQw"),
    ("cluster740prompt740", "Y2x1c3Rlcjc0MHByb21wdDc0MA"),
    ("mirror740prompt740", "bWlycm9yNzQwcHJvbXB0NzQw"),
    ("mirror740session740", "bWlycm9yNzQwc2Vzc2lvbjc0MA"),
    ("mirror740library740", "bWlycm9yNzQwbGlicmFyeTc0MA"),
    ("mirror740service740", "bWlycm9yNzQwc2VydmljZTc0MA"),
    ("filter740service740", "ZmlsdGVyNzQwc2VydmljZTc0MA"),
    ("filter740gateway740", "ZmlsdGVyNzQwZ2F0ZXdheTc0MA"),
    ("filter740storage740", "ZmlsdGVyNzQwc3RvcmFnZTc0MA"),
    ("filter740network740", "ZmlsdGVyNzQwbmV0d29yazc0MA"),
    ("ranking740network740", "cmFua2luZzc0MG5ldHdvcms3NDA"),
    ("ranking740latency740", "cmFua2luZzc0MGxhdGVuY3k3NDA"),
    ("ranking740buffer740", "cmFua2luZzc0MGJ1ZmZlcjc0MA"),
    ("ranking740queue740", "cmFua2luZzc0MHF1ZXVlNzQw"),
    ("encoding740queue740", "ZW5jb2Rpbmc3NDBxdWV1ZTc0MA"),
    ("encoding740worker740", "ZW5jb2Rpbmc3NDB3b3JrZXI3NDA"),
    ("encoding740kernel740", "ZW5jb2Rpbmc3NDBrZXJuZWw3NDA"),
    ("encoding740signal740", "ZW5jb2Rpbmc3NDBzaWduYWw3NDA"),
    ("mapping740signal740", "bWFwcGluZzc0MHNpZ25hbDc0MA"),
    ("mapping740packet740", "bWFwcGluZzc0MHBhY2tldDc0MA"),
    ("mapping740router740", "bWFwcGluZzc0MHJvdXRlcjc0MA"),
    ("mapping740cluster740", "bWFwcGluZzc0MGNsdXN0ZXI3NDA"),
    ("record740cluster740", "cmVjb3JkNzQwY2x1c3Rlcjc0MA"),
    ("record740mirror740", "cmVjb3JkNzQwbWlycm9yNzQw"),
    ("record740filter740", "cmVjb3JkNzQwZmlsdGVyNzQw"),
    ("record740ranking740", "cmVjb3JkNzQwcmFua2luZzc0MA"),
    ("candle740ranking740", "Y2FuZGxlNzQwcmFua2luZzc0MA"),
    ("candle740encoding740", "Y2FuZGxlNzQwZW5jb2Rpbmc3NDA"),
    ("candle740mapping740", "Y2FuZGxlNzQwbWFwcGluZzc0MA"),
    ("candle740record740", "Y2FuZGxlNzQwcmVjb3JkNzQw"),
    ("thread740record740", "dGhyZWFkNzQwcmVjb3JkNzQw"),
    ("thread740candle740", "dGhyZWFkNzQwY2FuZGxlNzQw"),
    ("thread740thread740", "dGhyZWFkNzQwdGhyZWFkNzQw"),
    ("thread740kitten740", "dGhyZWFkNzQwa2l0dGVuNzQw"),
    (
        "round 740: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNzQwOiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 740: agentuniverse is a framework for multi agents",
        "cm91bmQgNzQwOiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 740: knowledge stored as vectors enables retrieval",
        "cm91bmQgNzQwOiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 740: the processor reads the record then stops",
        "cm91bmQgNzQwOiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 740: a worker pulls the next task from the queue",
        "cm91bmQgNzQwOiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 740: signals travel through the network layer",
        "cm91bmQgNzQwOiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 740: the gateway routes each request by policy",
        "cm91bmQgNzQwOiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 740: memory grows until the buffer is full",
        "cm91bmQgNzQwOiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 740: the cluster mirrors every packet twice",
        "cm91bmQgNzQwOiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 740: ranking uses tokens learned from the corpus",
        "cm91bmQgNzQwOiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 740: a long session ends when the candle dies",
        "cm91bmQgNzQwOiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 740: encode the prompt then map the result",
        "cm91bmQgNzQwOiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 740: the kernel wakes the worker at dawn",
        "cm91bmQgNzQwOiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 740: service latency drops after the patch",
        "cm91bmQgNzQwOiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 740: the library caches every vector it sees",
        "cm91bmQgNzQwOiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 740: agents argue then the debate resolves",
        "cm91bmQgNzQwOiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 740: the filter keeps only strong matches",
        "cm91bmQgNzQwOiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 740: the model answers with a short reply",
        "cm91bmQgNzQwOiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 740: the recorder stores the reasoning trace",
        "cm91bmQgNzQwOiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 740: the angel watches the processor run",
        "cm91bmQgNzQwOiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 740: angle of the vector decides the match",
        "cm91bmQgNzQwOiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 740: the candle burns twice as long at night",
        "cm91bmQgNzQwOiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 740: a mirror of the universe in one line",
        "cm91bmQgNzQwOiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 740: the queue drains before the storm", "cm91bmQgNzQwOiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
