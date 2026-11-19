"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten196kitten196", "a2l0dGVuMTk2a2l0dGVuMTk2"),
    ("kitten196sitting196", "a2l0dGVuMTk2c2l0dGluZzE5Ng"),
    ("kitten196agent196", "a2l0dGVuMTk2YWdlbnQxOTY"),
    ("kitten196angle196", "a2l0dGVuMTk2YW5nbGUxOTY"),
    ("sitting196angle196", "c2l0dGluZzE5NmFuZ2xlMTk2"),
    ("sitting196universe196", "c2l0dGluZzE5NnVuaXZlcnNlMTk2"),
    ("sitting196memory196", "c2l0dGluZzE5Nm1lbW9yeTE5Ng"),
    ("sitting196stream196", "c2l0dGluZzE5NnN0cmVhbTE5Ng"),
    ("agent196stream196", "YWdlbnQxOTZzdHJlYW0xOTY"),
    ("agent196context196", "YWdlbnQxOTZjb250ZXh0MTk2"),
    ("agent196knowledge196", "YWdlbnQxOTZrbm93bGVkZ2UxOTY"),
    ("agent196vector196", "YWdlbnQxOTZ2ZWN0b3IxOTY"),
    ("angle196vector196", "YW5nbGUxOTZ2ZWN0b3IxOTY"),
    ("angle196processor196", "YW5nbGUxOTZwcm9jZXNzb3IxOTY"),
    ("angle196reasoning196", "YW5nbGUxOTZyZWFzb25pbmcxOTY"),
    ("angle196machine196", "YW5nbGUxOTZtYWNoaW5lMTk2"),
    ("universe196machine196", "dW5pdmVyc2UxOTZtYWNoaW5lMTk2"),
    ("universe196learning196", "dW5pdmVyc2UxOTZsZWFybmluZzE5Ng"),
    ("universe196model196", "dW5pdmVyc2UxOTZtb2RlbDE5Ng"),
    ("universe196token196", "dW5pdmVyc2UxOTZ0b2tlbjE5Ng"),
    ("memory196token196", "bWVtb3J5MTk2dG9rZW4xOTY"),
    ("memory196prompt196", "bWVtb3J5MTk2cHJvbXB0MTk2"),
    ("memory196session196", "bWVtb3J5MTk2c2Vzc2lvbjE5Ng"),
    ("memory196library196", "bWVtb3J5MTk2bGlicmFyeTE5Ng"),
    ("stream196library196", "c3RyZWFtMTk2bGlicmFyeTE5Ng"),
    ("stream196service196", "c3RyZWFtMTk2c2VydmljZTE5Ng"),
    ("stream196gateway196", "c3RyZWFtMTk2Z2F0ZXdheTE5Ng"),
    ("stream196storage196", "c3RyZWFtMTk2c3RvcmFnZTE5Ng"),
    ("context196storage196", "Y29udGV4dDE5NnN0b3JhZ2UxOTY"),
    ("context196network196", "Y29udGV4dDE5Nm5ldHdvcmsxOTY"),
    ("context196latency196", "Y29udGV4dDE5NmxhdGVuY3kxOTY"),
    ("context196buffer196", "Y29udGV4dDE5NmJ1ZmZlcjE5Ng"),
    ("knowledge196buffer196", "a25vd2xlZGdlMTk2YnVmZmVyMTk2"),
    ("knowledge196queue196", "a25vd2xlZGdlMTk2cXVldWUxOTY"),
    ("knowledge196worker196", "a25vd2xlZGdlMTk2d29ya2VyMTk2"),
    ("knowledge196kernel196", "a25vd2xlZGdlMTk2a2VybmVsMTk2"),
    ("vector196kernel196", "dmVjdG9yMTk2a2VybmVsMTk2"),
    ("vector196signal196", "dmVjdG9yMTk2c2lnbmFsMTk2"),
    ("vector196packet196", "dmVjdG9yMTk2cGFja2V0MTk2"),
    ("vector196router196", "dmVjdG9yMTk2cm91dGVyMTk2"),
    ("processor196router196", "cHJvY2Vzc29yMTk2cm91dGVyMTk2"),
    ("processor196cluster196", "cHJvY2Vzc29yMTk2Y2x1c3RlcjE5Ng"),
    ("processor196mirror196", "cHJvY2Vzc29yMTk2bWlycm9yMTk2"),
    ("processor196filter196", "cHJvY2Vzc29yMTk2ZmlsdGVyMTk2"),
    ("reasoning196filter196", "cmVhc29uaW5nMTk2ZmlsdGVyMTk2"),
    ("reasoning196ranking196", "cmVhc29uaW5nMTk2cmFua2luZzE5Ng"),
    ("reasoning196encoding196", "cmVhc29uaW5nMTk2ZW5jb2RpbmcxOTY"),
    ("reasoning196mapping196", "cmVhc29uaW5nMTk2bWFwcGluZzE5Ng"),
    ("machine196mapping196", "bWFjaGluZTE5Nm1hcHBpbmcxOTY"),
    ("machine196record196", "bWFjaGluZTE5NnJlY29yZDE5Ng"),
    ("machine196candle196", "bWFjaGluZTE5NmNhbmRsZTE5Ng"),
    ("machine196thread196", "bWFjaGluZTE5NnRocmVhZDE5Ng"),
    ("learning196thread196", "bGVhcm5pbmcxOTZ0aHJlYWQxOTY"),
    ("learning196kitten196", "bGVhcm5pbmcxOTZraXR0ZW4xOTY"),
    ("learning196sitting196", "bGVhcm5pbmcxOTZzaXR0aW5nMTk2"),
    ("learning196agent196", "bGVhcm5pbmcxOTZhZ2VudDE5Ng"),
    ("model196agent196", "bW9kZWwxOTZhZ2VudDE5Ng"),
    ("model196angle196", "bW9kZWwxOTZhbmdsZTE5Ng"),
    ("model196universe196", "bW9kZWwxOTZ1bml2ZXJzZTE5Ng"),
    ("model196memory196", "bW9kZWwxOTZtZW1vcnkxOTY"),
    ("token196memory196", "dG9rZW4xOTZtZW1vcnkxOTY"),
    ("token196stream196", "dG9rZW4xOTZzdHJlYW0xOTY"),
    ("token196context196", "dG9rZW4xOTZjb250ZXh0MTk2"),
    ("token196knowledge196", "dG9rZW4xOTZrbm93bGVkZ2UxOTY"),
    ("prompt196knowledge196", "cHJvbXB0MTk2a25vd2xlZGdlMTk2"),
    ("prompt196vector196", "cHJvbXB0MTk2dmVjdG9yMTk2"),
    ("prompt196processor196", "cHJvbXB0MTk2cHJvY2Vzc29yMTk2"),
    ("prompt196reasoning196", "cHJvbXB0MTk2cmVhc29uaW5nMTk2"),
    ("session196reasoning196", "c2Vzc2lvbjE5NnJlYXNvbmluZzE5Ng"),
    ("session196machine196", "c2Vzc2lvbjE5Nm1hY2hpbmUxOTY"),
    ("session196learning196", "c2Vzc2lvbjE5NmxlYXJuaW5nMTk2"),
    ("session196model196", "c2Vzc2lvbjE5Nm1vZGVsMTk2"),
    ("library196model196", "bGlicmFyeTE5Nm1vZGVsMTk2"),
    ("library196token196", "bGlicmFyeTE5NnRva2VuMTk2"),
    ("library196prompt196", "bGlicmFyeTE5NnByb21wdDE5Ng"),
    ("library196session196", "bGlicmFyeTE5NnNlc3Npb24xOTY"),
    ("service196session196", "c2VydmljZTE5NnNlc3Npb24xOTY"),
    ("service196library196", "c2VydmljZTE5NmxpYnJhcnkxOTY"),
    ("service196service196", "c2VydmljZTE5NnNlcnZpY2UxOTY"),
    ("service196gateway196", "c2VydmljZTE5NmdhdGV3YXkxOTY"),
    ("gateway196gateway196", "Z2F0ZXdheTE5NmdhdGV3YXkxOTY"),
    ("gateway196storage196", "Z2F0ZXdheTE5NnN0b3JhZ2UxOTY"),
    ("gateway196network196", "Z2F0ZXdheTE5Nm5ldHdvcmsxOTY"),
    ("gateway196latency196", "Z2F0ZXdheTE5NmxhdGVuY3kxOTY"),
    ("storage196latency196", "c3RvcmFnZTE5NmxhdGVuY3kxOTY"),
    ("storage196buffer196", "c3RvcmFnZTE5NmJ1ZmZlcjE5Ng"),
    ("storage196queue196", "c3RvcmFnZTE5NnF1ZXVlMTk2"),
    ("storage196worker196", "c3RvcmFnZTE5NndvcmtlcjE5Ng"),
    ("network196worker196", "bmV0d29yazE5NndvcmtlcjE5Ng"),
    ("network196kernel196", "bmV0d29yazE5Nmtlcm5lbDE5Ng"),
    ("network196signal196", "bmV0d29yazE5NnNpZ25hbDE5Ng"),
    ("network196packet196", "bmV0d29yazE5NnBhY2tldDE5Ng"),
    ("latency196packet196", "bGF0ZW5jeTE5NnBhY2tldDE5Ng"),
    ("latency196router196", "bGF0ZW5jeTE5NnJvdXRlcjE5Ng"),
    ("latency196cluster196", "bGF0ZW5jeTE5NmNsdXN0ZXIxOTY"),
    ("latency196mirror196", "bGF0ZW5jeTE5Nm1pcnJvcjE5Ng"),
    ("buffer196mirror196", "YnVmZmVyMTk2bWlycm9yMTk2"),
    ("buffer196filter196", "YnVmZmVyMTk2ZmlsdGVyMTk2"),
    ("buffer196ranking196", "YnVmZmVyMTk2cmFua2luZzE5Ng"),
    ("buffer196encoding196", "YnVmZmVyMTk2ZW5jb2RpbmcxOTY"),
    ("queue196encoding196", "cXVldWUxOTZlbmNvZGluZzE5Ng"),
    ("queue196mapping196", "cXVldWUxOTZtYXBwaW5nMTk2"),
    ("queue196record196", "cXVldWUxOTZyZWNvcmQxOTY"),
    ("queue196candle196", "cXVldWUxOTZjYW5kbGUxOTY"),
    ("worker196candle196", "d29ya2VyMTk2Y2FuZGxlMTk2"),
    ("worker196thread196", "d29ya2VyMTk2dGhyZWFkMTk2"),
    ("worker196kitten196", "d29ya2VyMTk2a2l0dGVuMTk2"),
    ("worker196sitting196", "d29ya2VyMTk2c2l0dGluZzE5Ng"),
    ("kernel196sitting196", "a2VybmVsMTk2c2l0dGluZzE5Ng"),
    ("kernel196agent196", "a2VybmVsMTk2YWdlbnQxOTY"),
    ("kernel196angle196", "a2VybmVsMTk2YW5nbGUxOTY"),
    ("kernel196universe196", "a2VybmVsMTk2dW5pdmVyc2UxOTY"),
    ("signal196universe196", "c2lnbmFsMTk2dW5pdmVyc2UxOTY"),
    ("signal196memory196", "c2lnbmFsMTk2bWVtb3J5MTk2"),
    ("signal196stream196", "c2lnbmFsMTk2c3RyZWFtMTk2"),
    ("signal196context196", "c2lnbmFsMTk2Y29udGV4dDE5Ng"),
    ("packet196context196", "cGFja2V0MTk2Y29udGV4dDE5Ng"),
    ("packet196knowledge196", "cGFja2V0MTk2a25vd2xlZGdlMTk2"),
    ("packet196vector196", "cGFja2V0MTk2dmVjdG9yMTk2"),
    ("packet196processor196", "cGFja2V0MTk2cHJvY2Vzc29yMTk2"),
    ("router196processor196", "cm91dGVyMTk2cHJvY2Vzc29yMTk2"),
    ("router196reasoning196", "cm91dGVyMTk2cmVhc29uaW5nMTk2"),
    ("router196machine196", "cm91dGVyMTk2bWFjaGluZTE5Ng"),
    ("router196learning196", "cm91dGVyMTk2bGVhcm5pbmcxOTY"),
    ("cluster196learning196", "Y2x1c3RlcjE5NmxlYXJuaW5nMTk2"),
    ("cluster196model196", "Y2x1c3RlcjE5Nm1vZGVsMTk2"),
    ("cluster196token196", "Y2x1c3RlcjE5NnRva2VuMTk2"),
    ("cluster196prompt196", "Y2x1c3RlcjE5NnByb21wdDE5Ng"),
    ("mirror196prompt196", "bWlycm9yMTk2cHJvbXB0MTk2"),
    ("mirror196session196", "bWlycm9yMTk2c2Vzc2lvbjE5Ng"),
    ("mirror196library196", "bWlycm9yMTk2bGlicmFyeTE5Ng"),
    ("mirror196service196", "bWlycm9yMTk2c2VydmljZTE5Ng"),
    ("filter196service196", "ZmlsdGVyMTk2c2VydmljZTE5Ng"),
    ("filter196gateway196", "ZmlsdGVyMTk2Z2F0ZXdheTE5Ng"),
    ("filter196storage196", "ZmlsdGVyMTk2c3RvcmFnZTE5Ng"),
    ("filter196network196", "ZmlsdGVyMTk2bmV0d29yazE5Ng"),
    ("ranking196network196", "cmFua2luZzE5Nm5ldHdvcmsxOTY"),
    ("ranking196latency196", "cmFua2luZzE5NmxhdGVuY3kxOTY"),
    ("ranking196buffer196", "cmFua2luZzE5NmJ1ZmZlcjE5Ng"),
    ("ranking196queue196", "cmFua2luZzE5NnF1ZXVlMTk2"),
    ("encoding196queue196", "ZW5jb2RpbmcxOTZxdWV1ZTE5Ng"),
    ("encoding196worker196", "ZW5jb2RpbmcxOTZ3b3JrZXIxOTY"),
    ("encoding196kernel196", "ZW5jb2RpbmcxOTZrZXJuZWwxOTY"),
    ("encoding196signal196", "ZW5jb2RpbmcxOTZzaWduYWwxOTY"),
    ("mapping196signal196", "bWFwcGluZzE5NnNpZ25hbDE5Ng"),
    ("mapping196packet196", "bWFwcGluZzE5NnBhY2tldDE5Ng"),
    ("mapping196router196", "bWFwcGluZzE5NnJvdXRlcjE5Ng"),
    ("mapping196cluster196", "bWFwcGluZzE5NmNsdXN0ZXIxOTY"),
    ("record196cluster196", "cmVjb3JkMTk2Y2x1c3RlcjE5Ng"),
    ("record196mirror196", "cmVjb3JkMTk2bWlycm9yMTk2"),
    ("record196filter196", "cmVjb3JkMTk2ZmlsdGVyMTk2"),
    ("record196ranking196", "cmVjb3JkMTk2cmFua2luZzE5Ng"),
    ("candle196ranking196", "Y2FuZGxlMTk2cmFua2luZzE5Ng"),
    ("candle196encoding196", "Y2FuZGxlMTk2ZW5jb2RpbmcxOTY"),
    ("candle196mapping196", "Y2FuZGxlMTk2bWFwcGluZzE5Ng"),
    ("candle196record196", "Y2FuZGxlMTk2cmVjb3JkMTk2"),
    ("thread196record196", "dGhyZWFkMTk2cmVjb3JkMTk2"),
    ("thread196candle196", "dGhyZWFkMTk2Y2FuZGxlMTk2"),
    ("thread196thread196", "dGhyZWFkMTk2dGhyZWFkMTk2"),
    ("thread196kitten196", "dGhyZWFkMTk2a2l0dGVuMTk2"),
    (
        "round 196: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTk2OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 196: agentuniverse is a framework for multi agents",
        "cm91bmQgMTk2OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 196: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTk2OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 196: the processor reads the record then stops",
        "cm91bmQgMTk2OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 196: a worker pulls the next task from the queue",
        "cm91bmQgMTk2OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 196: signals travel through the network layer",
        "cm91bmQgMTk2OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 196: the gateway routes each request by policy",
        "cm91bmQgMTk2OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 196: memory grows until the buffer is full",
        "cm91bmQgMTk2OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 196: the cluster mirrors every packet twice",
        "cm91bmQgMTk2OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 196: ranking uses tokens learned from the corpus",
        "cm91bmQgMTk2OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 196: a long session ends when the candle dies",
        "cm91bmQgMTk2OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 196: encode the prompt then map the result",
        "cm91bmQgMTk2OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 196: the kernel wakes the worker at dawn",
        "cm91bmQgMTk2OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 196: service latency drops after the patch",
        "cm91bmQgMTk2OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 196: the library caches every vector it sees",
        "cm91bmQgMTk2OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 196: agents argue then the debate resolves",
        "cm91bmQgMTk2OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 196: the filter keeps only strong matches",
        "cm91bmQgMTk2OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 196: the model answers with a short reply",
        "cm91bmQgMTk2OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 196: the recorder stores the reasoning trace",
        "cm91bmQgMTk2OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 196: the angel watches the processor run",
        "cm91bmQgMTk2OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 196: angle of the vector decides the match",
        "cm91bmQgMTk2OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 196: the candle burns twice as long at night",
        "cm91bmQgMTk2OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 196: a mirror of the universe in one line",
        "cm91bmQgMTk2OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 196: the queue drains before the storm", "cm91bmQgMTk2OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
