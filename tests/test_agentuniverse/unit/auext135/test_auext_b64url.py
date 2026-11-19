"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten135kitten135", "a2l0dGVuMTM1a2l0dGVuMTM1"),
    ("kitten135sitting135", "a2l0dGVuMTM1c2l0dGluZzEzNQ"),
    ("kitten135agent135", "a2l0dGVuMTM1YWdlbnQxMzU"),
    ("kitten135angle135", "a2l0dGVuMTM1YW5nbGUxMzU"),
    ("sitting135angle135", "c2l0dGluZzEzNWFuZ2xlMTM1"),
    ("sitting135universe135", "c2l0dGluZzEzNXVuaXZlcnNlMTM1"),
    ("sitting135memory135", "c2l0dGluZzEzNW1lbW9yeTEzNQ"),
    ("sitting135stream135", "c2l0dGluZzEzNXN0cmVhbTEzNQ"),
    ("agent135stream135", "YWdlbnQxMzVzdHJlYW0xMzU"),
    ("agent135context135", "YWdlbnQxMzVjb250ZXh0MTM1"),
    ("agent135knowledge135", "YWdlbnQxMzVrbm93bGVkZ2UxMzU"),
    ("agent135vector135", "YWdlbnQxMzV2ZWN0b3IxMzU"),
    ("angle135vector135", "YW5nbGUxMzV2ZWN0b3IxMzU"),
    ("angle135processor135", "YW5nbGUxMzVwcm9jZXNzb3IxMzU"),
    ("angle135reasoning135", "YW5nbGUxMzVyZWFzb25pbmcxMzU"),
    ("angle135machine135", "YW5nbGUxMzVtYWNoaW5lMTM1"),
    ("universe135machine135", "dW5pdmVyc2UxMzVtYWNoaW5lMTM1"),
    ("universe135learning135", "dW5pdmVyc2UxMzVsZWFybmluZzEzNQ"),
    ("universe135model135", "dW5pdmVyc2UxMzVtb2RlbDEzNQ"),
    ("universe135token135", "dW5pdmVyc2UxMzV0b2tlbjEzNQ"),
    ("memory135token135", "bWVtb3J5MTM1dG9rZW4xMzU"),
    ("memory135prompt135", "bWVtb3J5MTM1cHJvbXB0MTM1"),
    ("memory135session135", "bWVtb3J5MTM1c2Vzc2lvbjEzNQ"),
    ("memory135library135", "bWVtb3J5MTM1bGlicmFyeTEzNQ"),
    ("stream135library135", "c3RyZWFtMTM1bGlicmFyeTEzNQ"),
    ("stream135service135", "c3RyZWFtMTM1c2VydmljZTEzNQ"),
    ("stream135gateway135", "c3RyZWFtMTM1Z2F0ZXdheTEzNQ"),
    ("stream135storage135", "c3RyZWFtMTM1c3RvcmFnZTEzNQ"),
    ("context135storage135", "Y29udGV4dDEzNXN0b3JhZ2UxMzU"),
    ("context135network135", "Y29udGV4dDEzNW5ldHdvcmsxMzU"),
    ("context135latency135", "Y29udGV4dDEzNWxhdGVuY3kxMzU"),
    ("context135buffer135", "Y29udGV4dDEzNWJ1ZmZlcjEzNQ"),
    ("knowledge135buffer135", "a25vd2xlZGdlMTM1YnVmZmVyMTM1"),
    ("knowledge135queue135", "a25vd2xlZGdlMTM1cXVldWUxMzU"),
    ("knowledge135worker135", "a25vd2xlZGdlMTM1d29ya2VyMTM1"),
    ("knowledge135kernel135", "a25vd2xlZGdlMTM1a2VybmVsMTM1"),
    ("vector135kernel135", "dmVjdG9yMTM1a2VybmVsMTM1"),
    ("vector135signal135", "dmVjdG9yMTM1c2lnbmFsMTM1"),
    ("vector135packet135", "dmVjdG9yMTM1cGFja2V0MTM1"),
    ("vector135router135", "dmVjdG9yMTM1cm91dGVyMTM1"),
    ("processor135router135", "cHJvY2Vzc29yMTM1cm91dGVyMTM1"),
    ("processor135cluster135", "cHJvY2Vzc29yMTM1Y2x1c3RlcjEzNQ"),
    ("processor135mirror135", "cHJvY2Vzc29yMTM1bWlycm9yMTM1"),
    ("processor135filter135", "cHJvY2Vzc29yMTM1ZmlsdGVyMTM1"),
    ("reasoning135filter135", "cmVhc29uaW5nMTM1ZmlsdGVyMTM1"),
    ("reasoning135ranking135", "cmVhc29uaW5nMTM1cmFua2luZzEzNQ"),
    ("reasoning135encoding135", "cmVhc29uaW5nMTM1ZW5jb2RpbmcxMzU"),
    ("reasoning135mapping135", "cmVhc29uaW5nMTM1bWFwcGluZzEzNQ"),
    ("machine135mapping135", "bWFjaGluZTEzNW1hcHBpbmcxMzU"),
    ("machine135record135", "bWFjaGluZTEzNXJlY29yZDEzNQ"),
    ("machine135candle135", "bWFjaGluZTEzNWNhbmRsZTEzNQ"),
    ("machine135thread135", "bWFjaGluZTEzNXRocmVhZDEzNQ"),
    ("learning135thread135", "bGVhcm5pbmcxMzV0aHJlYWQxMzU"),
    ("learning135kitten135", "bGVhcm5pbmcxMzVraXR0ZW4xMzU"),
    ("learning135sitting135", "bGVhcm5pbmcxMzVzaXR0aW5nMTM1"),
    ("learning135agent135", "bGVhcm5pbmcxMzVhZ2VudDEzNQ"),
    ("model135agent135", "bW9kZWwxMzVhZ2VudDEzNQ"),
    ("model135angle135", "bW9kZWwxMzVhbmdsZTEzNQ"),
    ("model135universe135", "bW9kZWwxMzV1bml2ZXJzZTEzNQ"),
    ("model135memory135", "bW9kZWwxMzVtZW1vcnkxMzU"),
    ("token135memory135", "dG9rZW4xMzVtZW1vcnkxMzU"),
    ("token135stream135", "dG9rZW4xMzVzdHJlYW0xMzU"),
    ("token135context135", "dG9rZW4xMzVjb250ZXh0MTM1"),
    ("token135knowledge135", "dG9rZW4xMzVrbm93bGVkZ2UxMzU"),
    ("prompt135knowledge135", "cHJvbXB0MTM1a25vd2xlZGdlMTM1"),
    ("prompt135vector135", "cHJvbXB0MTM1dmVjdG9yMTM1"),
    ("prompt135processor135", "cHJvbXB0MTM1cHJvY2Vzc29yMTM1"),
    ("prompt135reasoning135", "cHJvbXB0MTM1cmVhc29uaW5nMTM1"),
    ("session135reasoning135", "c2Vzc2lvbjEzNXJlYXNvbmluZzEzNQ"),
    ("session135machine135", "c2Vzc2lvbjEzNW1hY2hpbmUxMzU"),
    ("session135learning135", "c2Vzc2lvbjEzNWxlYXJuaW5nMTM1"),
    ("session135model135", "c2Vzc2lvbjEzNW1vZGVsMTM1"),
    ("library135model135", "bGlicmFyeTEzNW1vZGVsMTM1"),
    ("library135token135", "bGlicmFyeTEzNXRva2VuMTM1"),
    ("library135prompt135", "bGlicmFyeTEzNXByb21wdDEzNQ"),
    ("library135session135", "bGlicmFyeTEzNXNlc3Npb24xMzU"),
    ("service135session135", "c2VydmljZTEzNXNlc3Npb24xMzU"),
    ("service135library135", "c2VydmljZTEzNWxpYnJhcnkxMzU"),
    ("service135service135", "c2VydmljZTEzNXNlcnZpY2UxMzU"),
    ("service135gateway135", "c2VydmljZTEzNWdhdGV3YXkxMzU"),
    ("gateway135gateway135", "Z2F0ZXdheTEzNWdhdGV3YXkxMzU"),
    ("gateway135storage135", "Z2F0ZXdheTEzNXN0b3JhZ2UxMzU"),
    ("gateway135network135", "Z2F0ZXdheTEzNW5ldHdvcmsxMzU"),
    ("gateway135latency135", "Z2F0ZXdheTEzNWxhdGVuY3kxMzU"),
    ("storage135latency135", "c3RvcmFnZTEzNWxhdGVuY3kxMzU"),
    ("storage135buffer135", "c3RvcmFnZTEzNWJ1ZmZlcjEzNQ"),
    ("storage135queue135", "c3RvcmFnZTEzNXF1ZXVlMTM1"),
    ("storage135worker135", "c3RvcmFnZTEzNXdvcmtlcjEzNQ"),
    ("network135worker135", "bmV0d29yazEzNXdvcmtlcjEzNQ"),
    ("network135kernel135", "bmV0d29yazEzNWtlcm5lbDEzNQ"),
    ("network135signal135", "bmV0d29yazEzNXNpZ25hbDEzNQ"),
    ("network135packet135", "bmV0d29yazEzNXBhY2tldDEzNQ"),
    ("latency135packet135", "bGF0ZW5jeTEzNXBhY2tldDEzNQ"),
    ("latency135router135", "bGF0ZW5jeTEzNXJvdXRlcjEzNQ"),
    ("latency135cluster135", "bGF0ZW5jeTEzNWNsdXN0ZXIxMzU"),
    ("latency135mirror135", "bGF0ZW5jeTEzNW1pcnJvcjEzNQ"),
    ("buffer135mirror135", "YnVmZmVyMTM1bWlycm9yMTM1"),
    ("buffer135filter135", "YnVmZmVyMTM1ZmlsdGVyMTM1"),
    ("buffer135ranking135", "YnVmZmVyMTM1cmFua2luZzEzNQ"),
    ("buffer135encoding135", "YnVmZmVyMTM1ZW5jb2RpbmcxMzU"),
    ("queue135encoding135", "cXVldWUxMzVlbmNvZGluZzEzNQ"),
    ("queue135mapping135", "cXVldWUxMzVtYXBwaW5nMTM1"),
    ("queue135record135", "cXVldWUxMzVyZWNvcmQxMzU"),
    ("queue135candle135", "cXVldWUxMzVjYW5kbGUxMzU"),
    ("worker135candle135", "d29ya2VyMTM1Y2FuZGxlMTM1"),
    ("worker135thread135", "d29ya2VyMTM1dGhyZWFkMTM1"),
    ("worker135kitten135", "d29ya2VyMTM1a2l0dGVuMTM1"),
    ("worker135sitting135", "d29ya2VyMTM1c2l0dGluZzEzNQ"),
    ("kernel135sitting135", "a2VybmVsMTM1c2l0dGluZzEzNQ"),
    ("kernel135agent135", "a2VybmVsMTM1YWdlbnQxMzU"),
    ("kernel135angle135", "a2VybmVsMTM1YW5nbGUxMzU"),
    ("kernel135universe135", "a2VybmVsMTM1dW5pdmVyc2UxMzU"),
    ("signal135universe135", "c2lnbmFsMTM1dW5pdmVyc2UxMzU"),
    ("signal135memory135", "c2lnbmFsMTM1bWVtb3J5MTM1"),
    ("signal135stream135", "c2lnbmFsMTM1c3RyZWFtMTM1"),
    ("signal135context135", "c2lnbmFsMTM1Y29udGV4dDEzNQ"),
    ("packet135context135", "cGFja2V0MTM1Y29udGV4dDEzNQ"),
    ("packet135knowledge135", "cGFja2V0MTM1a25vd2xlZGdlMTM1"),
    ("packet135vector135", "cGFja2V0MTM1dmVjdG9yMTM1"),
    ("packet135processor135", "cGFja2V0MTM1cHJvY2Vzc29yMTM1"),
    ("router135processor135", "cm91dGVyMTM1cHJvY2Vzc29yMTM1"),
    ("router135reasoning135", "cm91dGVyMTM1cmVhc29uaW5nMTM1"),
    ("router135machine135", "cm91dGVyMTM1bWFjaGluZTEzNQ"),
    ("router135learning135", "cm91dGVyMTM1bGVhcm5pbmcxMzU"),
    ("cluster135learning135", "Y2x1c3RlcjEzNWxlYXJuaW5nMTM1"),
    ("cluster135model135", "Y2x1c3RlcjEzNW1vZGVsMTM1"),
    ("cluster135token135", "Y2x1c3RlcjEzNXRva2VuMTM1"),
    ("cluster135prompt135", "Y2x1c3RlcjEzNXByb21wdDEzNQ"),
    ("mirror135prompt135", "bWlycm9yMTM1cHJvbXB0MTM1"),
    ("mirror135session135", "bWlycm9yMTM1c2Vzc2lvbjEzNQ"),
    ("mirror135library135", "bWlycm9yMTM1bGlicmFyeTEzNQ"),
    ("mirror135service135", "bWlycm9yMTM1c2VydmljZTEzNQ"),
    ("filter135service135", "ZmlsdGVyMTM1c2VydmljZTEzNQ"),
    ("filter135gateway135", "ZmlsdGVyMTM1Z2F0ZXdheTEzNQ"),
    ("filter135storage135", "ZmlsdGVyMTM1c3RvcmFnZTEzNQ"),
    ("filter135network135", "ZmlsdGVyMTM1bmV0d29yazEzNQ"),
    ("ranking135network135", "cmFua2luZzEzNW5ldHdvcmsxMzU"),
    ("ranking135latency135", "cmFua2luZzEzNWxhdGVuY3kxMzU"),
    ("ranking135buffer135", "cmFua2luZzEzNWJ1ZmZlcjEzNQ"),
    ("ranking135queue135", "cmFua2luZzEzNXF1ZXVlMTM1"),
    ("encoding135queue135", "ZW5jb2RpbmcxMzVxdWV1ZTEzNQ"),
    ("encoding135worker135", "ZW5jb2RpbmcxMzV3b3JrZXIxMzU"),
    ("encoding135kernel135", "ZW5jb2RpbmcxMzVrZXJuZWwxMzU"),
    ("encoding135signal135", "ZW5jb2RpbmcxMzVzaWduYWwxMzU"),
    ("mapping135signal135", "bWFwcGluZzEzNXNpZ25hbDEzNQ"),
    ("mapping135packet135", "bWFwcGluZzEzNXBhY2tldDEzNQ"),
    ("mapping135router135", "bWFwcGluZzEzNXJvdXRlcjEzNQ"),
    ("mapping135cluster135", "bWFwcGluZzEzNWNsdXN0ZXIxMzU"),
    ("record135cluster135", "cmVjb3JkMTM1Y2x1c3RlcjEzNQ"),
    ("record135mirror135", "cmVjb3JkMTM1bWlycm9yMTM1"),
    ("record135filter135", "cmVjb3JkMTM1ZmlsdGVyMTM1"),
    ("record135ranking135", "cmVjb3JkMTM1cmFua2luZzEzNQ"),
    ("candle135ranking135", "Y2FuZGxlMTM1cmFua2luZzEzNQ"),
    ("candle135encoding135", "Y2FuZGxlMTM1ZW5jb2RpbmcxMzU"),
    ("candle135mapping135", "Y2FuZGxlMTM1bWFwcGluZzEzNQ"),
    ("candle135record135", "Y2FuZGxlMTM1cmVjb3JkMTM1"),
    ("thread135record135", "dGhyZWFkMTM1cmVjb3JkMTM1"),
    ("thread135candle135", "dGhyZWFkMTM1Y2FuZGxlMTM1"),
    ("thread135thread135", "dGhyZWFkMTM1dGhyZWFkMTM1"),
    ("thread135kitten135", "dGhyZWFkMTM1a2l0dGVuMTM1"),
    (
        "round 135: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTM1OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 135: agentuniverse is a framework for multi agents",
        "cm91bmQgMTM1OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 135: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTM1OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 135: the processor reads the record then stops",
        "cm91bmQgMTM1OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 135: a worker pulls the next task from the queue",
        "cm91bmQgMTM1OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 135: signals travel through the network layer",
        "cm91bmQgMTM1OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 135: the gateway routes each request by policy",
        "cm91bmQgMTM1OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 135: memory grows until the buffer is full",
        "cm91bmQgMTM1OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 135: the cluster mirrors every packet twice",
        "cm91bmQgMTM1OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 135: ranking uses tokens learned from the corpus",
        "cm91bmQgMTM1OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 135: a long session ends when the candle dies",
        "cm91bmQgMTM1OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 135: encode the prompt then map the result",
        "cm91bmQgMTM1OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 135: the kernel wakes the worker at dawn",
        "cm91bmQgMTM1OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 135: service latency drops after the patch",
        "cm91bmQgMTM1OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 135: the library caches every vector it sees",
        "cm91bmQgMTM1OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 135: agents argue then the debate resolves",
        "cm91bmQgMTM1OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 135: the filter keeps only strong matches",
        "cm91bmQgMTM1OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 135: the model answers with a short reply",
        "cm91bmQgMTM1OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 135: the recorder stores the reasoning trace",
        "cm91bmQgMTM1OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 135: the angel watches the processor run",
        "cm91bmQgMTM1OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 135: angle of the vector decides the match",
        "cm91bmQgMTM1OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 135: the candle burns twice as long at night",
        "cm91bmQgMTM1OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 135: a mirror of the universe in one line",
        "cm91bmQgMTM1OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 135: the queue drains before the storm", "cm91bmQgMTM1OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
