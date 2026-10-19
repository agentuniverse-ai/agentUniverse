"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten741kitten741", "a2l0dGVuNzQxa2l0dGVuNzQx"),
    ("kitten741sitting741", "a2l0dGVuNzQxc2l0dGluZzc0MQ"),
    ("kitten741agent741", "a2l0dGVuNzQxYWdlbnQ3NDE"),
    ("kitten741angle741", "a2l0dGVuNzQxYW5nbGU3NDE"),
    ("sitting741angle741", "c2l0dGluZzc0MWFuZ2xlNzQx"),
    ("sitting741universe741", "c2l0dGluZzc0MXVuaXZlcnNlNzQx"),
    ("sitting741memory741", "c2l0dGluZzc0MW1lbW9yeTc0MQ"),
    ("sitting741stream741", "c2l0dGluZzc0MXN0cmVhbTc0MQ"),
    ("agent741stream741", "YWdlbnQ3NDFzdHJlYW03NDE"),
    ("agent741context741", "YWdlbnQ3NDFjb250ZXh0NzQx"),
    ("agent741knowledge741", "YWdlbnQ3NDFrbm93bGVkZ2U3NDE"),
    ("agent741vector741", "YWdlbnQ3NDF2ZWN0b3I3NDE"),
    ("angle741vector741", "YW5nbGU3NDF2ZWN0b3I3NDE"),
    ("angle741processor741", "YW5nbGU3NDFwcm9jZXNzb3I3NDE"),
    ("angle741reasoning741", "YW5nbGU3NDFyZWFzb25pbmc3NDE"),
    ("angle741machine741", "YW5nbGU3NDFtYWNoaW5lNzQx"),
    ("universe741machine741", "dW5pdmVyc2U3NDFtYWNoaW5lNzQx"),
    ("universe741learning741", "dW5pdmVyc2U3NDFsZWFybmluZzc0MQ"),
    ("universe741model741", "dW5pdmVyc2U3NDFtb2RlbDc0MQ"),
    ("universe741token741", "dW5pdmVyc2U3NDF0b2tlbjc0MQ"),
    ("memory741token741", "bWVtb3J5NzQxdG9rZW43NDE"),
    ("memory741prompt741", "bWVtb3J5NzQxcHJvbXB0NzQx"),
    ("memory741session741", "bWVtb3J5NzQxc2Vzc2lvbjc0MQ"),
    ("memory741library741", "bWVtb3J5NzQxbGlicmFyeTc0MQ"),
    ("stream741library741", "c3RyZWFtNzQxbGlicmFyeTc0MQ"),
    ("stream741service741", "c3RyZWFtNzQxc2VydmljZTc0MQ"),
    ("stream741gateway741", "c3RyZWFtNzQxZ2F0ZXdheTc0MQ"),
    ("stream741storage741", "c3RyZWFtNzQxc3RvcmFnZTc0MQ"),
    ("context741storage741", "Y29udGV4dDc0MXN0b3JhZ2U3NDE"),
    ("context741network741", "Y29udGV4dDc0MW5ldHdvcms3NDE"),
    ("context741latency741", "Y29udGV4dDc0MWxhdGVuY3k3NDE"),
    ("context741buffer741", "Y29udGV4dDc0MWJ1ZmZlcjc0MQ"),
    ("knowledge741buffer741", "a25vd2xlZGdlNzQxYnVmZmVyNzQx"),
    ("knowledge741queue741", "a25vd2xlZGdlNzQxcXVldWU3NDE"),
    ("knowledge741worker741", "a25vd2xlZGdlNzQxd29ya2VyNzQx"),
    ("knowledge741kernel741", "a25vd2xlZGdlNzQxa2VybmVsNzQx"),
    ("vector741kernel741", "dmVjdG9yNzQxa2VybmVsNzQx"),
    ("vector741signal741", "dmVjdG9yNzQxc2lnbmFsNzQx"),
    ("vector741packet741", "dmVjdG9yNzQxcGFja2V0NzQx"),
    ("vector741router741", "dmVjdG9yNzQxcm91dGVyNzQx"),
    ("processor741router741", "cHJvY2Vzc29yNzQxcm91dGVyNzQx"),
    ("processor741cluster741", "cHJvY2Vzc29yNzQxY2x1c3Rlcjc0MQ"),
    ("processor741mirror741", "cHJvY2Vzc29yNzQxbWlycm9yNzQx"),
    ("processor741filter741", "cHJvY2Vzc29yNzQxZmlsdGVyNzQx"),
    ("reasoning741filter741", "cmVhc29uaW5nNzQxZmlsdGVyNzQx"),
    ("reasoning741ranking741", "cmVhc29uaW5nNzQxcmFua2luZzc0MQ"),
    ("reasoning741encoding741", "cmVhc29uaW5nNzQxZW5jb2Rpbmc3NDE"),
    ("reasoning741mapping741", "cmVhc29uaW5nNzQxbWFwcGluZzc0MQ"),
    ("machine741mapping741", "bWFjaGluZTc0MW1hcHBpbmc3NDE"),
    ("machine741record741", "bWFjaGluZTc0MXJlY29yZDc0MQ"),
    ("machine741candle741", "bWFjaGluZTc0MWNhbmRsZTc0MQ"),
    ("machine741thread741", "bWFjaGluZTc0MXRocmVhZDc0MQ"),
    ("learning741thread741", "bGVhcm5pbmc3NDF0aHJlYWQ3NDE"),
    ("learning741kitten741", "bGVhcm5pbmc3NDFraXR0ZW43NDE"),
    ("learning741sitting741", "bGVhcm5pbmc3NDFzaXR0aW5nNzQx"),
    ("learning741agent741", "bGVhcm5pbmc3NDFhZ2VudDc0MQ"),
    ("model741agent741", "bW9kZWw3NDFhZ2VudDc0MQ"),
    ("model741angle741", "bW9kZWw3NDFhbmdsZTc0MQ"),
    ("model741universe741", "bW9kZWw3NDF1bml2ZXJzZTc0MQ"),
    ("model741memory741", "bW9kZWw3NDFtZW1vcnk3NDE"),
    ("token741memory741", "dG9rZW43NDFtZW1vcnk3NDE"),
    ("token741stream741", "dG9rZW43NDFzdHJlYW03NDE"),
    ("token741context741", "dG9rZW43NDFjb250ZXh0NzQx"),
    ("token741knowledge741", "dG9rZW43NDFrbm93bGVkZ2U3NDE"),
    ("prompt741knowledge741", "cHJvbXB0NzQxa25vd2xlZGdlNzQx"),
    ("prompt741vector741", "cHJvbXB0NzQxdmVjdG9yNzQx"),
    ("prompt741processor741", "cHJvbXB0NzQxcHJvY2Vzc29yNzQx"),
    ("prompt741reasoning741", "cHJvbXB0NzQxcmVhc29uaW5nNzQx"),
    ("session741reasoning741", "c2Vzc2lvbjc0MXJlYXNvbmluZzc0MQ"),
    ("session741machine741", "c2Vzc2lvbjc0MW1hY2hpbmU3NDE"),
    ("session741learning741", "c2Vzc2lvbjc0MWxlYXJuaW5nNzQx"),
    ("session741model741", "c2Vzc2lvbjc0MW1vZGVsNzQx"),
    ("library741model741", "bGlicmFyeTc0MW1vZGVsNzQx"),
    ("library741token741", "bGlicmFyeTc0MXRva2VuNzQx"),
    ("library741prompt741", "bGlicmFyeTc0MXByb21wdDc0MQ"),
    ("library741session741", "bGlicmFyeTc0MXNlc3Npb243NDE"),
    ("service741session741", "c2VydmljZTc0MXNlc3Npb243NDE"),
    ("service741library741", "c2VydmljZTc0MWxpYnJhcnk3NDE"),
    ("service741service741", "c2VydmljZTc0MXNlcnZpY2U3NDE"),
    ("service741gateway741", "c2VydmljZTc0MWdhdGV3YXk3NDE"),
    ("gateway741gateway741", "Z2F0ZXdheTc0MWdhdGV3YXk3NDE"),
    ("gateway741storage741", "Z2F0ZXdheTc0MXN0b3JhZ2U3NDE"),
    ("gateway741network741", "Z2F0ZXdheTc0MW5ldHdvcms3NDE"),
    ("gateway741latency741", "Z2F0ZXdheTc0MWxhdGVuY3k3NDE"),
    ("storage741latency741", "c3RvcmFnZTc0MWxhdGVuY3k3NDE"),
    ("storage741buffer741", "c3RvcmFnZTc0MWJ1ZmZlcjc0MQ"),
    ("storage741queue741", "c3RvcmFnZTc0MXF1ZXVlNzQx"),
    ("storage741worker741", "c3RvcmFnZTc0MXdvcmtlcjc0MQ"),
    ("network741worker741", "bmV0d29yazc0MXdvcmtlcjc0MQ"),
    ("network741kernel741", "bmV0d29yazc0MWtlcm5lbDc0MQ"),
    ("network741signal741", "bmV0d29yazc0MXNpZ25hbDc0MQ"),
    ("network741packet741", "bmV0d29yazc0MXBhY2tldDc0MQ"),
    ("latency741packet741", "bGF0ZW5jeTc0MXBhY2tldDc0MQ"),
    ("latency741router741", "bGF0ZW5jeTc0MXJvdXRlcjc0MQ"),
    ("latency741cluster741", "bGF0ZW5jeTc0MWNsdXN0ZXI3NDE"),
    ("latency741mirror741", "bGF0ZW5jeTc0MW1pcnJvcjc0MQ"),
    ("buffer741mirror741", "YnVmZmVyNzQxbWlycm9yNzQx"),
    ("buffer741filter741", "YnVmZmVyNzQxZmlsdGVyNzQx"),
    ("buffer741ranking741", "YnVmZmVyNzQxcmFua2luZzc0MQ"),
    ("buffer741encoding741", "YnVmZmVyNzQxZW5jb2Rpbmc3NDE"),
    ("queue741encoding741", "cXVldWU3NDFlbmNvZGluZzc0MQ"),
    ("queue741mapping741", "cXVldWU3NDFtYXBwaW5nNzQx"),
    ("queue741record741", "cXVldWU3NDFyZWNvcmQ3NDE"),
    ("queue741candle741", "cXVldWU3NDFjYW5kbGU3NDE"),
    ("worker741candle741", "d29ya2VyNzQxY2FuZGxlNzQx"),
    ("worker741thread741", "d29ya2VyNzQxdGhyZWFkNzQx"),
    ("worker741kitten741", "d29ya2VyNzQxa2l0dGVuNzQx"),
    ("worker741sitting741", "d29ya2VyNzQxc2l0dGluZzc0MQ"),
    ("kernel741sitting741", "a2VybmVsNzQxc2l0dGluZzc0MQ"),
    ("kernel741agent741", "a2VybmVsNzQxYWdlbnQ3NDE"),
    ("kernel741angle741", "a2VybmVsNzQxYW5nbGU3NDE"),
    ("kernel741universe741", "a2VybmVsNzQxdW5pdmVyc2U3NDE"),
    ("signal741universe741", "c2lnbmFsNzQxdW5pdmVyc2U3NDE"),
    ("signal741memory741", "c2lnbmFsNzQxbWVtb3J5NzQx"),
    ("signal741stream741", "c2lnbmFsNzQxc3RyZWFtNzQx"),
    ("signal741context741", "c2lnbmFsNzQxY29udGV4dDc0MQ"),
    ("packet741context741", "cGFja2V0NzQxY29udGV4dDc0MQ"),
    ("packet741knowledge741", "cGFja2V0NzQxa25vd2xlZGdlNzQx"),
    ("packet741vector741", "cGFja2V0NzQxdmVjdG9yNzQx"),
    ("packet741processor741", "cGFja2V0NzQxcHJvY2Vzc29yNzQx"),
    ("router741processor741", "cm91dGVyNzQxcHJvY2Vzc29yNzQx"),
    ("router741reasoning741", "cm91dGVyNzQxcmVhc29uaW5nNzQx"),
    ("router741machine741", "cm91dGVyNzQxbWFjaGluZTc0MQ"),
    ("router741learning741", "cm91dGVyNzQxbGVhcm5pbmc3NDE"),
    ("cluster741learning741", "Y2x1c3Rlcjc0MWxlYXJuaW5nNzQx"),
    ("cluster741model741", "Y2x1c3Rlcjc0MW1vZGVsNzQx"),
    ("cluster741token741", "Y2x1c3Rlcjc0MXRva2VuNzQx"),
    ("cluster741prompt741", "Y2x1c3Rlcjc0MXByb21wdDc0MQ"),
    ("mirror741prompt741", "bWlycm9yNzQxcHJvbXB0NzQx"),
    ("mirror741session741", "bWlycm9yNzQxc2Vzc2lvbjc0MQ"),
    ("mirror741library741", "bWlycm9yNzQxbGlicmFyeTc0MQ"),
    ("mirror741service741", "bWlycm9yNzQxc2VydmljZTc0MQ"),
    ("filter741service741", "ZmlsdGVyNzQxc2VydmljZTc0MQ"),
    ("filter741gateway741", "ZmlsdGVyNzQxZ2F0ZXdheTc0MQ"),
    ("filter741storage741", "ZmlsdGVyNzQxc3RvcmFnZTc0MQ"),
    ("filter741network741", "ZmlsdGVyNzQxbmV0d29yazc0MQ"),
    ("ranking741network741", "cmFua2luZzc0MW5ldHdvcms3NDE"),
    ("ranking741latency741", "cmFua2luZzc0MWxhdGVuY3k3NDE"),
    ("ranking741buffer741", "cmFua2luZzc0MWJ1ZmZlcjc0MQ"),
    ("ranking741queue741", "cmFua2luZzc0MXF1ZXVlNzQx"),
    ("encoding741queue741", "ZW5jb2Rpbmc3NDFxdWV1ZTc0MQ"),
    ("encoding741worker741", "ZW5jb2Rpbmc3NDF3b3JrZXI3NDE"),
    ("encoding741kernel741", "ZW5jb2Rpbmc3NDFrZXJuZWw3NDE"),
    ("encoding741signal741", "ZW5jb2Rpbmc3NDFzaWduYWw3NDE"),
    ("mapping741signal741", "bWFwcGluZzc0MXNpZ25hbDc0MQ"),
    ("mapping741packet741", "bWFwcGluZzc0MXBhY2tldDc0MQ"),
    ("mapping741router741", "bWFwcGluZzc0MXJvdXRlcjc0MQ"),
    ("mapping741cluster741", "bWFwcGluZzc0MWNsdXN0ZXI3NDE"),
    ("record741cluster741", "cmVjb3JkNzQxY2x1c3Rlcjc0MQ"),
    ("record741mirror741", "cmVjb3JkNzQxbWlycm9yNzQx"),
    ("record741filter741", "cmVjb3JkNzQxZmlsdGVyNzQx"),
    ("record741ranking741", "cmVjb3JkNzQxcmFua2luZzc0MQ"),
    ("candle741ranking741", "Y2FuZGxlNzQxcmFua2luZzc0MQ"),
    ("candle741encoding741", "Y2FuZGxlNzQxZW5jb2Rpbmc3NDE"),
    ("candle741mapping741", "Y2FuZGxlNzQxbWFwcGluZzc0MQ"),
    ("candle741record741", "Y2FuZGxlNzQxcmVjb3JkNzQx"),
    ("thread741record741", "dGhyZWFkNzQxcmVjb3JkNzQx"),
    ("thread741candle741", "dGhyZWFkNzQxY2FuZGxlNzQx"),
    ("thread741thread741", "dGhyZWFkNzQxdGhyZWFkNzQx"),
    ("thread741kitten741", "dGhyZWFkNzQxa2l0dGVuNzQx"),
    (
        "round 741: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNzQxOiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 741: agentuniverse is a framework for multi agents",
        "cm91bmQgNzQxOiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 741: knowledge stored as vectors enables retrieval",
        "cm91bmQgNzQxOiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 741: the processor reads the record then stops",
        "cm91bmQgNzQxOiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 741: a worker pulls the next task from the queue",
        "cm91bmQgNzQxOiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 741: signals travel through the network layer",
        "cm91bmQgNzQxOiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 741: the gateway routes each request by policy",
        "cm91bmQgNzQxOiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 741: memory grows until the buffer is full",
        "cm91bmQgNzQxOiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 741: the cluster mirrors every packet twice",
        "cm91bmQgNzQxOiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 741: ranking uses tokens learned from the corpus",
        "cm91bmQgNzQxOiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 741: a long session ends when the candle dies",
        "cm91bmQgNzQxOiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 741: encode the prompt then map the result",
        "cm91bmQgNzQxOiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 741: the kernel wakes the worker at dawn",
        "cm91bmQgNzQxOiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 741: service latency drops after the patch",
        "cm91bmQgNzQxOiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 741: the library caches every vector it sees",
        "cm91bmQgNzQxOiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 741: agents argue then the debate resolves",
        "cm91bmQgNzQxOiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 741: the filter keeps only strong matches",
        "cm91bmQgNzQxOiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 741: the model answers with a short reply",
        "cm91bmQgNzQxOiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 741: the recorder stores the reasoning trace",
        "cm91bmQgNzQxOiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 741: the angel watches the processor run",
        "cm91bmQgNzQxOiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 741: angle of the vector decides the match",
        "cm91bmQgNzQxOiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 741: the candle burns twice as long at night",
        "cm91bmQgNzQxOiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 741: a mirror of the universe in one line",
        "cm91bmQgNzQxOiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 741: the queue drains before the storm", "cm91bmQgNzQxOiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
