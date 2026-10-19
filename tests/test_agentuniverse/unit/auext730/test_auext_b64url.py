"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten730kitten730", "a2l0dGVuNzMwa2l0dGVuNzMw"),
    ("kitten730sitting730", "a2l0dGVuNzMwc2l0dGluZzczMA"),
    ("kitten730agent730", "a2l0dGVuNzMwYWdlbnQ3MzA"),
    ("kitten730angle730", "a2l0dGVuNzMwYW5nbGU3MzA"),
    ("sitting730angle730", "c2l0dGluZzczMGFuZ2xlNzMw"),
    ("sitting730universe730", "c2l0dGluZzczMHVuaXZlcnNlNzMw"),
    ("sitting730memory730", "c2l0dGluZzczMG1lbW9yeTczMA"),
    ("sitting730stream730", "c2l0dGluZzczMHN0cmVhbTczMA"),
    ("agent730stream730", "YWdlbnQ3MzBzdHJlYW03MzA"),
    ("agent730context730", "YWdlbnQ3MzBjb250ZXh0NzMw"),
    ("agent730knowledge730", "YWdlbnQ3MzBrbm93bGVkZ2U3MzA"),
    ("agent730vector730", "YWdlbnQ3MzB2ZWN0b3I3MzA"),
    ("angle730vector730", "YW5nbGU3MzB2ZWN0b3I3MzA"),
    ("angle730processor730", "YW5nbGU3MzBwcm9jZXNzb3I3MzA"),
    ("angle730reasoning730", "YW5nbGU3MzByZWFzb25pbmc3MzA"),
    ("angle730machine730", "YW5nbGU3MzBtYWNoaW5lNzMw"),
    ("universe730machine730", "dW5pdmVyc2U3MzBtYWNoaW5lNzMw"),
    ("universe730learning730", "dW5pdmVyc2U3MzBsZWFybmluZzczMA"),
    ("universe730model730", "dW5pdmVyc2U3MzBtb2RlbDczMA"),
    ("universe730token730", "dW5pdmVyc2U3MzB0b2tlbjczMA"),
    ("memory730token730", "bWVtb3J5NzMwdG9rZW43MzA"),
    ("memory730prompt730", "bWVtb3J5NzMwcHJvbXB0NzMw"),
    ("memory730session730", "bWVtb3J5NzMwc2Vzc2lvbjczMA"),
    ("memory730library730", "bWVtb3J5NzMwbGlicmFyeTczMA"),
    ("stream730library730", "c3RyZWFtNzMwbGlicmFyeTczMA"),
    ("stream730service730", "c3RyZWFtNzMwc2VydmljZTczMA"),
    ("stream730gateway730", "c3RyZWFtNzMwZ2F0ZXdheTczMA"),
    ("stream730storage730", "c3RyZWFtNzMwc3RvcmFnZTczMA"),
    ("context730storage730", "Y29udGV4dDczMHN0b3JhZ2U3MzA"),
    ("context730network730", "Y29udGV4dDczMG5ldHdvcms3MzA"),
    ("context730latency730", "Y29udGV4dDczMGxhdGVuY3k3MzA"),
    ("context730buffer730", "Y29udGV4dDczMGJ1ZmZlcjczMA"),
    ("knowledge730buffer730", "a25vd2xlZGdlNzMwYnVmZmVyNzMw"),
    ("knowledge730queue730", "a25vd2xlZGdlNzMwcXVldWU3MzA"),
    ("knowledge730worker730", "a25vd2xlZGdlNzMwd29ya2VyNzMw"),
    ("knowledge730kernel730", "a25vd2xlZGdlNzMwa2VybmVsNzMw"),
    ("vector730kernel730", "dmVjdG9yNzMwa2VybmVsNzMw"),
    ("vector730signal730", "dmVjdG9yNzMwc2lnbmFsNzMw"),
    ("vector730packet730", "dmVjdG9yNzMwcGFja2V0NzMw"),
    ("vector730router730", "dmVjdG9yNzMwcm91dGVyNzMw"),
    ("processor730router730", "cHJvY2Vzc29yNzMwcm91dGVyNzMw"),
    ("processor730cluster730", "cHJvY2Vzc29yNzMwY2x1c3RlcjczMA"),
    ("processor730mirror730", "cHJvY2Vzc29yNzMwbWlycm9yNzMw"),
    ("processor730filter730", "cHJvY2Vzc29yNzMwZmlsdGVyNzMw"),
    ("reasoning730filter730", "cmVhc29uaW5nNzMwZmlsdGVyNzMw"),
    ("reasoning730ranking730", "cmVhc29uaW5nNzMwcmFua2luZzczMA"),
    ("reasoning730encoding730", "cmVhc29uaW5nNzMwZW5jb2Rpbmc3MzA"),
    ("reasoning730mapping730", "cmVhc29uaW5nNzMwbWFwcGluZzczMA"),
    ("machine730mapping730", "bWFjaGluZTczMG1hcHBpbmc3MzA"),
    ("machine730record730", "bWFjaGluZTczMHJlY29yZDczMA"),
    ("machine730candle730", "bWFjaGluZTczMGNhbmRsZTczMA"),
    ("machine730thread730", "bWFjaGluZTczMHRocmVhZDczMA"),
    ("learning730thread730", "bGVhcm5pbmc3MzB0aHJlYWQ3MzA"),
    ("learning730kitten730", "bGVhcm5pbmc3MzBraXR0ZW43MzA"),
    ("learning730sitting730", "bGVhcm5pbmc3MzBzaXR0aW5nNzMw"),
    ("learning730agent730", "bGVhcm5pbmc3MzBhZ2VudDczMA"),
    ("model730agent730", "bW9kZWw3MzBhZ2VudDczMA"),
    ("model730angle730", "bW9kZWw3MzBhbmdsZTczMA"),
    ("model730universe730", "bW9kZWw3MzB1bml2ZXJzZTczMA"),
    ("model730memory730", "bW9kZWw3MzBtZW1vcnk3MzA"),
    ("token730memory730", "dG9rZW43MzBtZW1vcnk3MzA"),
    ("token730stream730", "dG9rZW43MzBzdHJlYW03MzA"),
    ("token730context730", "dG9rZW43MzBjb250ZXh0NzMw"),
    ("token730knowledge730", "dG9rZW43MzBrbm93bGVkZ2U3MzA"),
    ("prompt730knowledge730", "cHJvbXB0NzMwa25vd2xlZGdlNzMw"),
    ("prompt730vector730", "cHJvbXB0NzMwdmVjdG9yNzMw"),
    ("prompt730processor730", "cHJvbXB0NzMwcHJvY2Vzc29yNzMw"),
    ("prompt730reasoning730", "cHJvbXB0NzMwcmVhc29uaW5nNzMw"),
    ("session730reasoning730", "c2Vzc2lvbjczMHJlYXNvbmluZzczMA"),
    ("session730machine730", "c2Vzc2lvbjczMG1hY2hpbmU3MzA"),
    ("session730learning730", "c2Vzc2lvbjczMGxlYXJuaW5nNzMw"),
    ("session730model730", "c2Vzc2lvbjczMG1vZGVsNzMw"),
    ("library730model730", "bGlicmFyeTczMG1vZGVsNzMw"),
    ("library730token730", "bGlicmFyeTczMHRva2VuNzMw"),
    ("library730prompt730", "bGlicmFyeTczMHByb21wdDczMA"),
    ("library730session730", "bGlicmFyeTczMHNlc3Npb243MzA"),
    ("service730session730", "c2VydmljZTczMHNlc3Npb243MzA"),
    ("service730library730", "c2VydmljZTczMGxpYnJhcnk3MzA"),
    ("service730service730", "c2VydmljZTczMHNlcnZpY2U3MzA"),
    ("service730gateway730", "c2VydmljZTczMGdhdGV3YXk3MzA"),
    ("gateway730gateway730", "Z2F0ZXdheTczMGdhdGV3YXk3MzA"),
    ("gateway730storage730", "Z2F0ZXdheTczMHN0b3JhZ2U3MzA"),
    ("gateway730network730", "Z2F0ZXdheTczMG5ldHdvcms3MzA"),
    ("gateway730latency730", "Z2F0ZXdheTczMGxhdGVuY3k3MzA"),
    ("storage730latency730", "c3RvcmFnZTczMGxhdGVuY3k3MzA"),
    ("storage730buffer730", "c3RvcmFnZTczMGJ1ZmZlcjczMA"),
    ("storage730queue730", "c3RvcmFnZTczMHF1ZXVlNzMw"),
    ("storage730worker730", "c3RvcmFnZTczMHdvcmtlcjczMA"),
    ("network730worker730", "bmV0d29yazczMHdvcmtlcjczMA"),
    ("network730kernel730", "bmV0d29yazczMGtlcm5lbDczMA"),
    ("network730signal730", "bmV0d29yazczMHNpZ25hbDczMA"),
    ("network730packet730", "bmV0d29yazczMHBhY2tldDczMA"),
    ("latency730packet730", "bGF0ZW5jeTczMHBhY2tldDczMA"),
    ("latency730router730", "bGF0ZW5jeTczMHJvdXRlcjczMA"),
    ("latency730cluster730", "bGF0ZW5jeTczMGNsdXN0ZXI3MzA"),
    ("latency730mirror730", "bGF0ZW5jeTczMG1pcnJvcjczMA"),
    ("buffer730mirror730", "YnVmZmVyNzMwbWlycm9yNzMw"),
    ("buffer730filter730", "YnVmZmVyNzMwZmlsdGVyNzMw"),
    ("buffer730ranking730", "YnVmZmVyNzMwcmFua2luZzczMA"),
    ("buffer730encoding730", "YnVmZmVyNzMwZW5jb2Rpbmc3MzA"),
    ("queue730encoding730", "cXVldWU3MzBlbmNvZGluZzczMA"),
    ("queue730mapping730", "cXVldWU3MzBtYXBwaW5nNzMw"),
    ("queue730record730", "cXVldWU3MzByZWNvcmQ3MzA"),
    ("queue730candle730", "cXVldWU3MzBjYW5kbGU3MzA"),
    ("worker730candle730", "d29ya2VyNzMwY2FuZGxlNzMw"),
    ("worker730thread730", "d29ya2VyNzMwdGhyZWFkNzMw"),
    ("worker730kitten730", "d29ya2VyNzMwa2l0dGVuNzMw"),
    ("worker730sitting730", "d29ya2VyNzMwc2l0dGluZzczMA"),
    ("kernel730sitting730", "a2VybmVsNzMwc2l0dGluZzczMA"),
    ("kernel730agent730", "a2VybmVsNzMwYWdlbnQ3MzA"),
    ("kernel730angle730", "a2VybmVsNzMwYW5nbGU3MzA"),
    ("kernel730universe730", "a2VybmVsNzMwdW5pdmVyc2U3MzA"),
    ("signal730universe730", "c2lnbmFsNzMwdW5pdmVyc2U3MzA"),
    ("signal730memory730", "c2lnbmFsNzMwbWVtb3J5NzMw"),
    ("signal730stream730", "c2lnbmFsNzMwc3RyZWFtNzMw"),
    ("signal730context730", "c2lnbmFsNzMwY29udGV4dDczMA"),
    ("packet730context730", "cGFja2V0NzMwY29udGV4dDczMA"),
    ("packet730knowledge730", "cGFja2V0NzMwa25vd2xlZGdlNzMw"),
    ("packet730vector730", "cGFja2V0NzMwdmVjdG9yNzMw"),
    ("packet730processor730", "cGFja2V0NzMwcHJvY2Vzc29yNzMw"),
    ("router730processor730", "cm91dGVyNzMwcHJvY2Vzc29yNzMw"),
    ("router730reasoning730", "cm91dGVyNzMwcmVhc29uaW5nNzMw"),
    ("router730machine730", "cm91dGVyNzMwbWFjaGluZTczMA"),
    ("router730learning730", "cm91dGVyNzMwbGVhcm5pbmc3MzA"),
    ("cluster730learning730", "Y2x1c3RlcjczMGxlYXJuaW5nNzMw"),
    ("cluster730model730", "Y2x1c3RlcjczMG1vZGVsNzMw"),
    ("cluster730token730", "Y2x1c3RlcjczMHRva2VuNzMw"),
    ("cluster730prompt730", "Y2x1c3RlcjczMHByb21wdDczMA"),
    ("mirror730prompt730", "bWlycm9yNzMwcHJvbXB0NzMw"),
    ("mirror730session730", "bWlycm9yNzMwc2Vzc2lvbjczMA"),
    ("mirror730library730", "bWlycm9yNzMwbGlicmFyeTczMA"),
    ("mirror730service730", "bWlycm9yNzMwc2VydmljZTczMA"),
    ("filter730service730", "ZmlsdGVyNzMwc2VydmljZTczMA"),
    ("filter730gateway730", "ZmlsdGVyNzMwZ2F0ZXdheTczMA"),
    ("filter730storage730", "ZmlsdGVyNzMwc3RvcmFnZTczMA"),
    ("filter730network730", "ZmlsdGVyNzMwbmV0d29yazczMA"),
    ("ranking730network730", "cmFua2luZzczMG5ldHdvcms3MzA"),
    ("ranking730latency730", "cmFua2luZzczMGxhdGVuY3k3MzA"),
    ("ranking730buffer730", "cmFua2luZzczMGJ1ZmZlcjczMA"),
    ("ranking730queue730", "cmFua2luZzczMHF1ZXVlNzMw"),
    ("encoding730queue730", "ZW5jb2Rpbmc3MzBxdWV1ZTczMA"),
    ("encoding730worker730", "ZW5jb2Rpbmc3MzB3b3JrZXI3MzA"),
    ("encoding730kernel730", "ZW5jb2Rpbmc3MzBrZXJuZWw3MzA"),
    ("encoding730signal730", "ZW5jb2Rpbmc3MzBzaWduYWw3MzA"),
    ("mapping730signal730", "bWFwcGluZzczMHNpZ25hbDczMA"),
    ("mapping730packet730", "bWFwcGluZzczMHBhY2tldDczMA"),
    ("mapping730router730", "bWFwcGluZzczMHJvdXRlcjczMA"),
    ("mapping730cluster730", "bWFwcGluZzczMGNsdXN0ZXI3MzA"),
    ("record730cluster730", "cmVjb3JkNzMwY2x1c3RlcjczMA"),
    ("record730mirror730", "cmVjb3JkNzMwbWlycm9yNzMw"),
    ("record730filter730", "cmVjb3JkNzMwZmlsdGVyNzMw"),
    ("record730ranking730", "cmVjb3JkNzMwcmFua2luZzczMA"),
    ("candle730ranking730", "Y2FuZGxlNzMwcmFua2luZzczMA"),
    ("candle730encoding730", "Y2FuZGxlNzMwZW5jb2Rpbmc3MzA"),
    ("candle730mapping730", "Y2FuZGxlNzMwbWFwcGluZzczMA"),
    ("candle730record730", "Y2FuZGxlNzMwcmVjb3JkNzMw"),
    ("thread730record730", "dGhyZWFkNzMwcmVjb3JkNzMw"),
    ("thread730candle730", "dGhyZWFkNzMwY2FuZGxlNzMw"),
    ("thread730thread730", "dGhyZWFkNzMwdGhyZWFkNzMw"),
    ("thread730kitten730", "dGhyZWFkNzMwa2l0dGVuNzMw"),
    (
        "round 730: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNzMwOiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 730: agentuniverse is a framework for multi agents",
        "cm91bmQgNzMwOiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 730: knowledge stored as vectors enables retrieval",
        "cm91bmQgNzMwOiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 730: the processor reads the record then stops",
        "cm91bmQgNzMwOiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 730: a worker pulls the next task from the queue",
        "cm91bmQgNzMwOiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 730: signals travel through the network layer",
        "cm91bmQgNzMwOiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 730: the gateway routes each request by policy",
        "cm91bmQgNzMwOiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 730: memory grows until the buffer is full",
        "cm91bmQgNzMwOiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 730: the cluster mirrors every packet twice",
        "cm91bmQgNzMwOiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 730: ranking uses tokens learned from the corpus",
        "cm91bmQgNzMwOiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 730: a long session ends when the candle dies",
        "cm91bmQgNzMwOiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 730: encode the prompt then map the result",
        "cm91bmQgNzMwOiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 730: the kernel wakes the worker at dawn",
        "cm91bmQgNzMwOiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 730: service latency drops after the patch",
        "cm91bmQgNzMwOiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 730: the library caches every vector it sees",
        "cm91bmQgNzMwOiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 730: agents argue then the debate resolves",
        "cm91bmQgNzMwOiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 730: the filter keeps only strong matches",
        "cm91bmQgNzMwOiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 730: the model answers with a short reply",
        "cm91bmQgNzMwOiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 730: the recorder stores the reasoning trace",
        "cm91bmQgNzMwOiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 730: the angel watches the processor run",
        "cm91bmQgNzMwOiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 730: angle of the vector decides the match",
        "cm91bmQgNzMwOiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 730: the candle burns twice as long at night",
        "cm91bmQgNzMwOiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 730: a mirror of the universe in one line",
        "cm91bmQgNzMwOiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 730: the queue drains before the storm", "cm91bmQgNzMwOiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
