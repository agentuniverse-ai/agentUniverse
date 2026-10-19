"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten744kitten744", "a2l0dGVuNzQ0a2l0dGVuNzQ0"),
    ("kitten744sitting744", "a2l0dGVuNzQ0c2l0dGluZzc0NA"),
    ("kitten744agent744", "a2l0dGVuNzQ0YWdlbnQ3NDQ"),
    ("kitten744angle744", "a2l0dGVuNzQ0YW5nbGU3NDQ"),
    ("sitting744angle744", "c2l0dGluZzc0NGFuZ2xlNzQ0"),
    ("sitting744universe744", "c2l0dGluZzc0NHVuaXZlcnNlNzQ0"),
    ("sitting744memory744", "c2l0dGluZzc0NG1lbW9yeTc0NA"),
    ("sitting744stream744", "c2l0dGluZzc0NHN0cmVhbTc0NA"),
    ("agent744stream744", "YWdlbnQ3NDRzdHJlYW03NDQ"),
    ("agent744context744", "YWdlbnQ3NDRjb250ZXh0NzQ0"),
    ("agent744knowledge744", "YWdlbnQ3NDRrbm93bGVkZ2U3NDQ"),
    ("agent744vector744", "YWdlbnQ3NDR2ZWN0b3I3NDQ"),
    ("angle744vector744", "YW5nbGU3NDR2ZWN0b3I3NDQ"),
    ("angle744processor744", "YW5nbGU3NDRwcm9jZXNzb3I3NDQ"),
    ("angle744reasoning744", "YW5nbGU3NDRyZWFzb25pbmc3NDQ"),
    ("angle744machine744", "YW5nbGU3NDRtYWNoaW5lNzQ0"),
    ("universe744machine744", "dW5pdmVyc2U3NDRtYWNoaW5lNzQ0"),
    ("universe744learning744", "dW5pdmVyc2U3NDRsZWFybmluZzc0NA"),
    ("universe744model744", "dW5pdmVyc2U3NDRtb2RlbDc0NA"),
    ("universe744token744", "dW5pdmVyc2U3NDR0b2tlbjc0NA"),
    ("memory744token744", "bWVtb3J5NzQ0dG9rZW43NDQ"),
    ("memory744prompt744", "bWVtb3J5NzQ0cHJvbXB0NzQ0"),
    ("memory744session744", "bWVtb3J5NzQ0c2Vzc2lvbjc0NA"),
    ("memory744library744", "bWVtb3J5NzQ0bGlicmFyeTc0NA"),
    ("stream744library744", "c3RyZWFtNzQ0bGlicmFyeTc0NA"),
    ("stream744service744", "c3RyZWFtNzQ0c2VydmljZTc0NA"),
    ("stream744gateway744", "c3RyZWFtNzQ0Z2F0ZXdheTc0NA"),
    ("stream744storage744", "c3RyZWFtNzQ0c3RvcmFnZTc0NA"),
    ("context744storage744", "Y29udGV4dDc0NHN0b3JhZ2U3NDQ"),
    ("context744network744", "Y29udGV4dDc0NG5ldHdvcms3NDQ"),
    ("context744latency744", "Y29udGV4dDc0NGxhdGVuY3k3NDQ"),
    ("context744buffer744", "Y29udGV4dDc0NGJ1ZmZlcjc0NA"),
    ("knowledge744buffer744", "a25vd2xlZGdlNzQ0YnVmZmVyNzQ0"),
    ("knowledge744queue744", "a25vd2xlZGdlNzQ0cXVldWU3NDQ"),
    ("knowledge744worker744", "a25vd2xlZGdlNzQ0d29ya2VyNzQ0"),
    ("knowledge744kernel744", "a25vd2xlZGdlNzQ0a2VybmVsNzQ0"),
    ("vector744kernel744", "dmVjdG9yNzQ0a2VybmVsNzQ0"),
    ("vector744signal744", "dmVjdG9yNzQ0c2lnbmFsNzQ0"),
    ("vector744packet744", "dmVjdG9yNzQ0cGFja2V0NzQ0"),
    ("vector744router744", "dmVjdG9yNzQ0cm91dGVyNzQ0"),
    ("processor744router744", "cHJvY2Vzc29yNzQ0cm91dGVyNzQ0"),
    ("processor744cluster744", "cHJvY2Vzc29yNzQ0Y2x1c3Rlcjc0NA"),
    ("processor744mirror744", "cHJvY2Vzc29yNzQ0bWlycm9yNzQ0"),
    ("processor744filter744", "cHJvY2Vzc29yNzQ0ZmlsdGVyNzQ0"),
    ("reasoning744filter744", "cmVhc29uaW5nNzQ0ZmlsdGVyNzQ0"),
    ("reasoning744ranking744", "cmVhc29uaW5nNzQ0cmFua2luZzc0NA"),
    ("reasoning744encoding744", "cmVhc29uaW5nNzQ0ZW5jb2Rpbmc3NDQ"),
    ("reasoning744mapping744", "cmVhc29uaW5nNzQ0bWFwcGluZzc0NA"),
    ("machine744mapping744", "bWFjaGluZTc0NG1hcHBpbmc3NDQ"),
    ("machine744record744", "bWFjaGluZTc0NHJlY29yZDc0NA"),
    ("machine744candle744", "bWFjaGluZTc0NGNhbmRsZTc0NA"),
    ("machine744thread744", "bWFjaGluZTc0NHRocmVhZDc0NA"),
    ("learning744thread744", "bGVhcm5pbmc3NDR0aHJlYWQ3NDQ"),
    ("learning744kitten744", "bGVhcm5pbmc3NDRraXR0ZW43NDQ"),
    ("learning744sitting744", "bGVhcm5pbmc3NDRzaXR0aW5nNzQ0"),
    ("learning744agent744", "bGVhcm5pbmc3NDRhZ2VudDc0NA"),
    ("model744agent744", "bW9kZWw3NDRhZ2VudDc0NA"),
    ("model744angle744", "bW9kZWw3NDRhbmdsZTc0NA"),
    ("model744universe744", "bW9kZWw3NDR1bml2ZXJzZTc0NA"),
    ("model744memory744", "bW9kZWw3NDRtZW1vcnk3NDQ"),
    ("token744memory744", "dG9rZW43NDRtZW1vcnk3NDQ"),
    ("token744stream744", "dG9rZW43NDRzdHJlYW03NDQ"),
    ("token744context744", "dG9rZW43NDRjb250ZXh0NzQ0"),
    ("token744knowledge744", "dG9rZW43NDRrbm93bGVkZ2U3NDQ"),
    ("prompt744knowledge744", "cHJvbXB0NzQ0a25vd2xlZGdlNzQ0"),
    ("prompt744vector744", "cHJvbXB0NzQ0dmVjdG9yNzQ0"),
    ("prompt744processor744", "cHJvbXB0NzQ0cHJvY2Vzc29yNzQ0"),
    ("prompt744reasoning744", "cHJvbXB0NzQ0cmVhc29uaW5nNzQ0"),
    ("session744reasoning744", "c2Vzc2lvbjc0NHJlYXNvbmluZzc0NA"),
    ("session744machine744", "c2Vzc2lvbjc0NG1hY2hpbmU3NDQ"),
    ("session744learning744", "c2Vzc2lvbjc0NGxlYXJuaW5nNzQ0"),
    ("session744model744", "c2Vzc2lvbjc0NG1vZGVsNzQ0"),
    ("library744model744", "bGlicmFyeTc0NG1vZGVsNzQ0"),
    ("library744token744", "bGlicmFyeTc0NHRva2VuNzQ0"),
    ("library744prompt744", "bGlicmFyeTc0NHByb21wdDc0NA"),
    ("library744session744", "bGlicmFyeTc0NHNlc3Npb243NDQ"),
    ("service744session744", "c2VydmljZTc0NHNlc3Npb243NDQ"),
    ("service744library744", "c2VydmljZTc0NGxpYnJhcnk3NDQ"),
    ("service744service744", "c2VydmljZTc0NHNlcnZpY2U3NDQ"),
    ("service744gateway744", "c2VydmljZTc0NGdhdGV3YXk3NDQ"),
    ("gateway744gateway744", "Z2F0ZXdheTc0NGdhdGV3YXk3NDQ"),
    ("gateway744storage744", "Z2F0ZXdheTc0NHN0b3JhZ2U3NDQ"),
    ("gateway744network744", "Z2F0ZXdheTc0NG5ldHdvcms3NDQ"),
    ("gateway744latency744", "Z2F0ZXdheTc0NGxhdGVuY3k3NDQ"),
    ("storage744latency744", "c3RvcmFnZTc0NGxhdGVuY3k3NDQ"),
    ("storage744buffer744", "c3RvcmFnZTc0NGJ1ZmZlcjc0NA"),
    ("storage744queue744", "c3RvcmFnZTc0NHF1ZXVlNzQ0"),
    ("storage744worker744", "c3RvcmFnZTc0NHdvcmtlcjc0NA"),
    ("network744worker744", "bmV0d29yazc0NHdvcmtlcjc0NA"),
    ("network744kernel744", "bmV0d29yazc0NGtlcm5lbDc0NA"),
    ("network744signal744", "bmV0d29yazc0NHNpZ25hbDc0NA"),
    ("network744packet744", "bmV0d29yazc0NHBhY2tldDc0NA"),
    ("latency744packet744", "bGF0ZW5jeTc0NHBhY2tldDc0NA"),
    ("latency744router744", "bGF0ZW5jeTc0NHJvdXRlcjc0NA"),
    ("latency744cluster744", "bGF0ZW5jeTc0NGNsdXN0ZXI3NDQ"),
    ("latency744mirror744", "bGF0ZW5jeTc0NG1pcnJvcjc0NA"),
    ("buffer744mirror744", "YnVmZmVyNzQ0bWlycm9yNzQ0"),
    ("buffer744filter744", "YnVmZmVyNzQ0ZmlsdGVyNzQ0"),
    ("buffer744ranking744", "YnVmZmVyNzQ0cmFua2luZzc0NA"),
    ("buffer744encoding744", "YnVmZmVyNzQ0ZW5jb2Rpbmc3NDQ"),
    ("queue744encoding744", "cXVldWU3NDRlbmNvZGluZzc0NA"),
    ("queue744mapping744", "cXVldWU3NDRtYXBwaW5nNzQ0"),
    ("queue744record744", "cXVldWU3NDRyZWNvcmQ3NDQ"),
    ("queue744candle744", "cXVldWU3NDRjYW5kbGU3NDQ"),
    ("worker744candle744", "d29ya2VyNzQ0Y2FuZGxlNzQ0"),
    ("worker744thread744", "d29ya2VyNzQ0dGhyZWFkNzQ0"),
    ("worker744kitten744", "d29ya2VyNzQ0a2l0dGVuNzQ0"),
    ("worker744sitting744", "d29ya2VyNzQ0c2l0dGluZzc0NA"),
    ("kernel744sitting744", "a2VybmVsNzQ0c2l0dGluZzc0NA"),
    ("kernel744agent744", "a2VybmVsNzQ0YWdlbnQ3NDQ"),
    ("kernel744angle744", "a2VybmVsNzQ0YW5nbGU3NDQ"),
    ("kernel744universe744", "a2VybmVsNzQ0dW5pdmVyc2U3NDQ"),
    ("signal744universe744", "c2lnbmFsNzQ0dW5pdmVyc2U3NDQ"),
    ("signal744memory744", "c2lnbmFsNzQ0bWVtb3J5NzQ0"),
    ("signal744stream744", "c2lnbmFsNzQ0c3RyZWFtNzQ0"),
    ("signal744context744", "c2lnbmFsNzQ0Y29udGV4dDc0NA"),
    ("packet744context744", "cGFja2V0NzQ0Y29udGV4dDc0NA"),
    ("packet744knowledge744", "cGFja2V0NzQ0a25vd2xlZGdlNzQ0"),
    ("packet744vector744", "cGFja2V0NzQ0dmVjdG9yNzQ0"),
    ("packet744processor744", "cGFja2V0NzQ0cHJvY2Vzc29yNzQ0"),
    ("router744processor744", "cm91dGVyNzQ0cHJvY2Vzc29yNzQ0"),
    ("router744reasoning744", "cm91dGVyNzQ0cmVhc29uaW5nNzQ0"),
    ("router744machine744", "cm91dGVyNzQ0bWFjaGluZTc0NA"),
    ("router744learning744", "cm91dGVyNzQ0bGVhcm5pbmc3NDQ"),
    ("cluster744learning744", "Y2x1c3Rlcjc0NGxlYXJuaW5nNzQ0"),
    ("cluster744model744", "Y2x1c3Rlcjc0NG1vZGVsNzQ0"),
    ("cluster744token744", "Y2x1c3Rlcjc0NHRva2VuNzQ0"),
    ("cluster744prompt744", "Y2x1c3Rlcjc0NHByb21wdDc0NA"),
    ("mirror744prompt744", "bWlycm9yNzQ0cHJvbXB0NzQ0"),
    ("mirror744session744", "bWlycm9yNzQ0c2Vzc2lvbjc0NA"),
    ("mirror744library744", "bWlycm9yNzQ0bGlicmFyeTc0NA"),
    ("mirror744service744", "bWlycm9yNzQ0c2VydmljZTc0NA"),
    ("filter744service744", "ZmlsdGVyNzQ0c2VydmljZTc0NA"),
    ("filter744gateway744", "ZmlsdGVyNzQ0Z2F0ZXdheTc0NA"),
    ("filter744storage744", "ZmlsdGVyNzQ0c3RvcmFnZTc0NA"),
    ("filter744network744", "ZmlsdGVyNzQ0bmV0d29yazc0NA"),
    ("ranking744network744", "cmFua2luZzc0NG5ldHdvcms3NDQ"),
    ("ranking744latency744", "cmFua2luZzc0NGxhdGVuY3k3NDQ"),
    ("ranking744buffer744", "cmFua2luZzc0NGJ1ZmZlcjc0NA"),
    ("ranking744queue744", "cmFua2luZzc0NHF1ZXVlNzQ0"),
    ("encoding744queue744", "ZW5jb2Rpbmc3NDRxdWV1ZTc0NA"),
    ("encoding744worker744", "ZW5jb2Rpbmc3NDR3b3JrZXI3NDQ"),
    ("encoding744kernel744", "ZW5jb2Rpbmc3NDRrZXJuZWw3NDQ"),
    ("encoding744signal744", "ZW5jb2Rpbmc3NDRzaWduYWw3NDQ"),
    ("mapping744signal744", "bWFwcGluZzc0NHNpZ25hbDc0NA"),
    ("mapping744packet744", "bWFwcGluZzc0NHBhY2tldDc0NA"),
    ("mapping744router744", "bWFwcGluZzc0NHJvdXRlcjc0NA"),
    ("mapping744cluster744", "bWFwcGluZzc0NGNsdXN0ZXI3NDQ"),
    ("record744cluster744", "cmVjb3JkNzQ0Y2x1c3Rlcjc0NA"),
    ("record744mirror744", "cmVjb3JkNzQ0bWlycm9yNzQ0"),
    ("record744filter744", "cmVjb3JkNzQ0ZmlsdGVyNzQ0"),
    ("record744ranking744", "cmVjb3JkNzQ0cmFua2luZzc0NA"),
    ("candle744ranking744", "Y2FuZGxlNzQ0cmFua2luZzc0NA"),
    ("candle744encoding744", "Y2FuZGxlNzQ0ZW5jb2Rpbmc3NDQ"),
    ("candle744mapping744", "Y2FuZGxlNzQ0bWFwcGluZzc0NA"),
    ("candle744record744", "Y2FuZGxlNzQ0cmVjb3JkNzQ0"),
    ("thread744record744", "dGhyZWFkNzQ0cmVjb3JkNzQ0"),
    ("thread744candle744", "dGhyZWFkNzQ0Y2FuZGxlNzQ0"),
    ("thread744thread744", "dGhyZWFkNzQ0dGhyZWFkNzQ0"),
    ("thread744kitten744", "dGhyZWFkNzQ0a2l0dGVuNzQ0"),
    (
        "round 744: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNzQ0OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 744: agentuniverse is a framework for multi agents",
        "cm91bmQgNzQ0OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 744: knowledge stored as vectors enables retrieval",
        "cm91bmQgNzQ0OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 744: the processor reads the record then stops",
        "cm91bmQgNzQ0OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 744: a worker pulls the next task from the queue",
        "cm91bmQgNzQ0OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 744: signals travel through the network layer",
        "cm91bmQgNzQ0OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 744: the gateway routes each request by policy",
        "cm91bmQgNzQ0OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 744: memory grows until the buffer is full",
        "cm91bmQgNzQ0OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 744: the cluster mirrors every packet twice",
        "cm91bmQgNzQ0OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 744: ranking uses tokens learned from the corpus",
        "cm91bmQgNzQ0OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 744: a long session ends when the candle dies",
        "cm91bmQgNzQ0OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 744: encode the prompt then map the result",
        "cm91bmQgNzQ0OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 744: the kernel wakes the worker at dawn",
        "cm91bmQgNzQ0OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 744: service latency drops after the patch",
        "cm91bmQgNzQ0OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 744: the library caches every vector it sees",
        "cm91bmQgNzQ0OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 744: agents argue then the debate resolves",
        "cm91bmQgNzQ0OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 744: the filter keeps only strong matches",
        "cm91bmQgNzQ0OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 744: the model answers with a short reply",
        "cm91bmQgNzQ0OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 744: the recorder stores the reasoning trace",
        "cm91bmQgNzQ0OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 744: the angel watches the processor run",
        "cm91bmQgNzQ0OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 744: angle of the vector decides the match",
        "cm91bmQgNzQ0OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 744: the candle burns twice as long at night",
        "cm91bmQgNzQ0OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 744: a mirror of the universe in one line",
        "cm91bmQgNzQ0OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 744: the queue drains before the storm", "cm91bmQgNzQ0OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
