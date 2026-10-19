"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten746kitten746", "a2l0dGVuNzQ2a2l0dGVuNzQ2"),
    ("kitten746sitting746", "a2l0dGVuNzQ2c2l0dGluZzc0Ng"),
    ("kitten746agent746", "a2l0dGVuNzQ2YWdlbnQ3NDY"),
    ("kitten746angle746", "a2l0dGVuNzQ2YW5nbGU3NDY"),
    ("sitting746angle746", "c2l0dGluZzc0NmFuZ2xlNzQ2"),
    ("sitting746universe746", "c2l0dGluZzc0NnVuaXZlcnNlNzQ2"),
    ("sitting746memory746", "c2l0dGluZzc0Nm1lbW9yeTc0Ng"),
    ("sitting746stream746", "c2l0dGluZzc0NnN0cmVhbTc0Ng"),
    ("agent746stream746", "YWdlbnQ3NDZzdHJlYW03NDY"),
    ("agent746context746", "YWdlbnQ3NDZjb250ZXh0NzQ2"),
    ("agent746knowledge746", "YWdlbnQ3NDZrbm93bGVkZ2U3NDY"),
    ("agent746vector746", "YWdlbnQ3NDZ2ZWN0b3I3NDY"),
    ("angle746vector746", "YW5nbGU3NDZ2ZWN0b3I3NDY"),
    ("angle746processor746", "YW5nbGU3NDZwcm9jZXNzb3I3NDY"),
    ("angle746reasoning746", "YW5nbGU3NDZyZWFzb25pbmc3NDY"),
    ("angle746machine746", "YW5nbGU3NDZtYWNoaW5lNzQ2"),
    ("universe746machine746", "dW5pdmVyc2U3NDZtYWNoaW5lNzQ2"),
    ("universe746learning746", "dW5pdmVyc2U3NDZsZWFybmluZzc0Ng"),
    ("universe746model746", "dW5pdmVyc2U3NDZtb2RlbDc0Ng"),
    ("universe746token746", "dW5pdmVyc2U3NDZ0b2tlbjc0Ng"),
    ("memory746token746", "bWVtb3J5NzQ2dG9rZW43NDY"),
    ("memory746prompt746", "bWVtb3J5NzQ2cHJvbXB0NzQ2"),
    ("memory746session746", "bWVtb3J5NzQ2c2Vzc2lvbjc0Ng"),
    ("memory746library746", "bWVtb3J5NzQ2bGlicmFyeTc0Ng"),
    ("stream746library746", "c3RyZWFtNzQ2bGlicmFyeTc0Ng"),
    ("stream746service746", "c3RyZWFtNzQ2c2VydmljZTc0Ng"),
    ("stream746gateway746", "c3RyZWFtNzQ2Z2F0ZXdheTc0Ng"),
    ("stream746storage746", "c3RyZWFtNzQ2c3RvcmFnZTc0Ng"),
    ("context746storage746", "Y29udGV4dDc0NnN0b3JhZ2U3NDY"),
    ("context746network746", "Y29udGV4dDc0Nm5ldHdvcms3NDY"),
    ("context746latency746", "Y29udGV4dDc0NmxhdGVuY3k3NDY"),
    ("context746buffer746", "Y29udGV4dDc0NmJ1ZmZlcjc0Ng"),
    ("knowledge746buffer746", "a25vd2xlZGdlNzQ2YnVmZmVyNzQ2"),
    ("knowledge746queue746", "a25vd2xlZGdlNzQ2cXVldWU3NDY"),
    ("knowledge746worker746", "a25vd2xlZGdlNzQ2d29ya2VyNzQ2"),
    ("knowledge746kernel746", "a25vd2xlZGdlNzQ2a2VybmVsNzQ2"),
    ("vector746kernel746", "dmVjdG9yNzQ2a2VybmVsNzQ2"),
    ("vector746signal746", "dmVjdG9yNzQ2c2lnbmFsNzQ2"),
    ("vector746packet746", "dmVjdG9yNzQ2cGFja2V0NzQ2"),
    ("vector746router746", "dmVjdG9yNzQ2cm91dGVyNzQ2"),
    ("processor746router746", "cHJvY2Vzc29yNzQ2cm91dGVyNzQ2"),
    ("processor746cluster746", "cHJvY2Vzc29yNzQ2Y2x1c3Rlcjc0Ng"),
    ("processor746mirror746", "cHJvY2Vzc29yNzQ2bWlycm9yNzQ2"),
    ("processor746filter746", "cHJvY2Vzc29yNzQ2ZmlsdGVyNzQ2"),
    ("reasoning746filter746", "cmVhc29uaW5nNzQ2ZmlsdGVyNzQ2"),
    ("reasoning746ranking746", "cmVhc29uaW5nNzQ2cmFua2luZzc0Ng"),
    ("reasoning746encoding746", "cmVhc29uaW5nNzQ2ZW5jb2Rpbmc3NDY"),
    ("reasoning746mapping746", "cmVhc29uaW5nNzQ2bWFwcGluZzc0Ng"),
    ("machine746mapping746", "bWFjaGluZTc0Nm1hcHBpbmc3NDY"),
    ("machine746record746", "bWFjaGluZTc0NnJlY29yZDc0Ng"),
    ("machine746candle746", "bWFjaGluZTc0NmNhbmRsZTc0Ng"),
    ("machine746thread746", "bWFjaGluZTc0NnRocmVhZDc0Ng"),
    ("learning746thread746", "bGVhcm5pbmc3NDZ0aHJlYWQ3NDY"),
    ("learning746kitten746", "bGVhcm5pbmc3NDZraXR0ZW43NDY"),
    ("learning746sitting746", "bGVhcm5pbmc3NDZzaXR0aW5nNzQ2"),
    ("learning746agent746", "bGVhcm5pbmc3NDZhZ2VudDc0Ng"),
    ("model746agent746", "bW9kZWw3NDZhZ2VudDc0Ng"),
    ("model746angle746", "bW9kZWw3NDZhbmdsZTc0Ng"),
    ("model746universe746", "bW9kZWw3NDZ1bml2ZXJzZTc0Ng"),
    ("model746memory746", "bW9kZWw3NDZtZW1vcnk3NDY"),
    ("token746memory746", "dG9rZW43NDZtZW1vcnk3NDY"),
    ("token746stream746", "dG9rZW43NDZzdHJlYW03NDY"),
    ("token746context746", "dG9rZW43NDZjb250ZXh0NzQ2"),
    ("token746knowledge746", "dG9rZW43NDZrbm93bGVkZ2U3NDY"),
    ("prompt746knowledge746", "cHJvbXB0NzQ2a25vd2xlZGdlNzQ2"),
    ("prompt746vector746", "cHJvbXB0NzQ2dmVjdG9yNzQ2"),
    ("prompt746processor746", "cHJvbXB0NzQ2cHJvY2Vzc29yNzQ2"),
    ("prompt746reasoning746", "cHJvbXB0NzQ2cmVhc29uaW5nNzQ2"),
    ("session746reasoning746", "c2Vzc2lvbjc0NnJlYXNvbmluZzc0Ng"),
    ("session746machine746", "c2Vzc2lvbjc0Nm1hY2hpbmU3NDY"),
    ("session746learning746", "c2Vzc2lvbjc0NmxlYXJuaW5nNzQ2"),
    ("session746model746", "c2Vzc2lvbjc0Nm1vZGVsNzQ2"),
    ("library746model746", "bGlicmFyeTc0Nm1vZGVsNzQ2"),
    ("library746token746", "bGlicmFyeTc0NnRva2VuNzQ2"),
    ("library746prompt746", "bGlicmFyeTc0NnByb21wdDc0Ng"),
    ("library746session746", "bGlicmFyeTc0NnNlc3Npb243NDY"),
    ("service746session746", "c2VydmljZTc0NnNlc3Npb243NDY"),
    ("service746library746", "c2VydmljZTc0NmxpYnJhcnk3NDY"),
    ("service746service746", "c2VydmljZTc0NnNlcnZpY2U3NDY"),
    ("service746gateway746", "c2VydmljZTc0NmdhdGV3YXk3NDY"),
    ("gateway746gateway746", "Z2F0ZXdheTc0NmdhdGV3YXk3NDY"),
    ("gateway746storage746", "Z2F0ZXdheTc0NnN0b3JhZ2U3NDY"),
    ("gateway746network746", "Z2F0ZXdheTc0Nm5ldHdvcms3NDY"),
    ("gateway746latency746", "Z2F0ZXdheTc0NmxhdGVuY3k3NDY"),
    ("storage746latency746", "c3RvcmFnZTc0NmxhdGVuY3k3NDY"),
    ("storage746buffer746", "c3RvcmFnZTc0NmJ1ZmZlcjc0Ng"),
    ("storage746queue746", "c3RvcmFnZTc0NnF1ZXVlNzQ2"),
    ("storage746worker746", "c3RvcmFnZTc0Nndvcmtlcjc0Ng"),
    ("network746worker746", "bmV0d29yazc0Nndvcmtlcjc0Ng"),
    ("network746kernel746", "bmV0d29yazc0Nmtlcm5lbDc0Ng"),
    ("network746signal746", "bmV0d29yazc0NnNpZ25hbDc0Ng"),
    ("network746packet746", "bmV0d29yazc0NnBhY2tldDc0Ng"),
    ("latency746packet746", "bGF0ZW5jeTc0NnBhY2tldDc0Ng"),
    ("latency746router746", "bGF0ZW5jeTc0NnJvdXRlcjc0Ng"),
    ("latency746cluster746", "bGF0ZW5jeTc0NmNsdXN0ZXI3NDY"),
    ("latency746mirror746", "bGF0ZW5jeTc0Nm1pcnJvcjc0Ng"),
    ("buffer746mirror746", "YnVmZmVyNzQ2bWlycm9yNzQ2"),
    ("buffer746filter746", "YnVmZmVyNzQ2ZmlsdGVyNzQ2"),
    ("buffer746ranking746", "YnVmZmVyNzQ2cmFua2luZzc0Ng"),
    ("buffer746encoding746", "YnVmZmVyNzQ2ZW5jb2Rpbmc3NDY"),
    ("queue746encoding746", "cXVldWU3NDZlbmNvZGluZzc0Ng"),
    ("queue746mapping746", "cXVldWU3NDZtYXBwaW5nNzQ2"),
    ("queue746record746", "cXVldWU3NDZyZWNvcmQ3NDY"),
    ("queue746candle746", "cXVldWU3NDZjYW5kbGU3NDY"),
    ("worker746candle746", "d29ya2VyNzQ2Y2FuZGxlNzQ2"),
    ("worker746thread746", "d29ya2VyNzQ2dGhyZWFkNzQ2"),
    ("worker746kitten746", "d29ya2VyNzQ2a2l0dGVuNzQ2"),
    ("worker746sitting746", "d29ya2VyNzQ2c2l0dGluZzc0Ng"),
    ("kernel746sitting746", "a2VybmVsNzQ2c2l0dGluZzc0Ng"),
    ("kernel746agent746", "a2VybmVsNzQ2YWdlbnQ3NDY"),
    ("kernel746angle746", "a2VybmVsNzQ2YW5nbGU3NDY"),
    ("kernel746universe746", "a2VybmVsNzQ2dW5pdmVyc2U3NDY"),
    ("signal746universe746", "c2lnbmFsNzQ2dW5pdmVyc2U3NDY"),
    ("signal746memory746", "c2lnbmFsNzQ2bWVtb3J5NzQ2"),
    ("signal746stream746", "c2lnbmFsNzQ2c3RyZWFtNzQ2"),
    ("signal746context746", "c2lnbmFsNzQ2Y29udGV4dDc0Ng"),
    ("packet746context746", "cGFja2V0NzQ2Y29udGV4dDc0Ng"),
    ("packet746knowledge746", "cGFja2V0NzQ2a25vd2xlZGdlNzQ2"),
    ("packet746vector746", "cGFja2V0NzQ2dmVjdG9yNzQ2"),
    ("packet746processor746", "cGFja2V0NzQ2cHJvY2Vzc29yNzQ2"),
    ("router746processor746", "cm91dGVyNzQ2cHJvY2Vzc29yNzQ2"),
    ("router746reasoning746", "cm91dGVyNzQ2cmVhc29uaW5nNzQ2"),
    ("router746machine746", "cm91dGVyNzQ2bWFjaGluZTc0Ng"),
    ("router746learning746", "cm91dGVyNzQ2bGVhcm5pbmc3NDY"),
    ("cluster746learning746", "Y2x1c3Rlcjc0NmxlYXJuaW5nNzQ2"),
    ("cluster746model746", "Y2x1c3Rlcjc0Nm1vZGVsNzQ2"),
    ("cluster746token746", "Y2x1c3Rlcjc0NnRva2VuNzQ2"),
    ("cluster746prompt746", "Y2x1c3Rlcjc0NnByb21wdDc0Ng"),
    ("mirror746prompt746", "bWlycm9yNzQ2cHJvbXB0NzQ2"),
    ("mirror746session746", "bWlycm9yNzQ2c2Vzc2lvbjc0Ng"),
    ("mirror746library746", "bWlycm9yNzQ2bGlicmFyeTc0Ng"),
    ("mirror746service746", "bWlycm9yNzQ2c2VydmljZTc0Ng"),
    ("filter746service746", "ZmlsdGVyNzQ2c2VydmljZTc0Ng"),
    ("filter746gateway746", "ZmlsdGVyNzQ2Z2F0ZXdheTc0Ng"),
    ("filter746storage746", "ZmlsdGVyNzQ2c3RvcmFnZTc0Ng"),
    ("filter746network746", "ZmlsdGVyNzQ2bmV0d29yazc0Ng"),
    ("ranking746network746", "cmFua2luZzc0Nm5ldHdvcms3NDY"),
    ("ranking746latency746", "cmFua2luZzc0NmxhdGVuY3k3NDY"),
    ("ranking746buffer746", "cmFua2luZzc0NmJ1ZmZlcjc0Ng"),
    ("ranking746queue746", "cmFua2luZzc0NnF1ZXVlNzQ2"),
    ("encoding746queue746", "ZW5jb2Rpbmc3NDZxdWV1ZTc0Ng"),
    ("encoding746worker746", "ZW5jb2Rpbmc3NDZ3b3JrZXI3NDY"),
    ("encoding746kernel746", "ZW5jb2Rpbmc3NDZrZXJuZWw3NDY"),
    ("encoding746signal746", "ZW5jb2Rpbmc3NDZzaWduYWw3NDY"),
    ("mapping746signal746", "bWFwcGluZzc0NnNpZ25hbDc0Ng"),
    ("mapping746packet746", "bWFwcGluZzc0NnBhY2tldDc0Ng"),
    ("mapping746router746", "bWFwcGluZzc0NnJvdXRlcjc0Ng"),
    ("mapping746cluster746", "bWFwcGluZzc0NmNsdXN0ZXI3NDY"),
    ("record746cluster746", "cmVjb3JkNzQ2Y2x1c3Rlcjc0Ng"),
    ("record746mirror746", "cmVjb3JkNzQ2bWlycm9yNzQ2"),
    ("record746filter746", "cmVjb3JkNzQ2ZmlsdGVyNzQ2"),
    ("record746ranking746", "cmVjb3JkNzQ2cmFua2luZzc0Ng"),
    ("candle746ranking746", "Y2FuZGxlNzQ2cmFua2luZzc0Ng"),
    ("candle746encoding746", "Y2FuZGxlNzQ2ZW5jb2Rpbmc3NDY"),
    ("candle746mapping746", "Y2FuZGxlNzQ2bWFwcGluZzc0Ng"),
    ("candle746record746", "Y2FuZGxlNzQ2cmVjb3JkNzQ2"),
    ("thread746record746", "dGhyZWFkNzQ2cmVjb3JkNzQ2"),
    ("thread746candle746", "dGhyZWFkNzQ2Y2FuZGxlNzQ2"),
    ("thread746thread746", "dGhyZWFkNzQ2dGhyZWFkNzQ2"),
    ("thread746kitten746", "dGhyZWFkNzQ2a2l0dGVuNzQ2"),
    (
        "round 746: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNzQ2OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 746: agentuniverse is a framework for multi agents",
        "cm91bmQgNzQ2OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 746: knowledge stored as vectors enables retrieval",
        "cm91bmQgNzQ2OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 746: the processor reads the record then stops",
        "cm91bmQgNzQ2OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 746: a worker pulls the next task from the queue",
        "cm91bmQgNzQ2OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 746: signals travel through the network layer",
        "cm91bmQgNzQ2OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 746: the gateway routes each request by policy",
        "cm91bmQgNzQ2OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 746: memory grows until the buffer is full",
        "cm91bmQgNzQ2OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 746: the cluster mirrors every packet twice",
        "cm91bmQgNzQ2OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 746: ranking uses tokens learned from the corpus",
        "cm91bmQgNzQ2OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 746: a long session ends when the candle dies",
        "cm91bmQgNzQ2OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 746: encode the prompt then map the result",
        "cm91bmQgNzQ2OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 746: the kernel wakes the worker at dawn",
        "cm91bmQgNzQ2OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 746: service latency drops after the patch",
        "cm91bmQgNzQ2OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 746: the library caches every vector it sees",
        "cm91bmQgNzQ2OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 746: agents argue then the debate resolves",
        "cm91bmQgNzQ2OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 746: the filter keeps only strong matches",
        "cm91bmQgNzQ2OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 746: the model answers with a short reply",
        "cm91bmQgNzQ2OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 746: the recorder stores the reasoning trace",
        "cm91bmQgNzQ2OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 746: the angel watches the processor run",
        "cm91bmQgNzQ2OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 746: angle of the vector decides the match",
        "cm91bmQgNzQ2OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 746: the candle burns twice as long at night",
        "cm91bmQgNzQ2OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 746: a mirror of the universe in one line",
        "cm91bmQgNzQ2OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 746: the queue drains before the storm", "cm91bmQgNzQ2OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
