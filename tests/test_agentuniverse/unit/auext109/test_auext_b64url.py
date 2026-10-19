"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten109kitten109", "a2l0dGVuMTA5a2l0dGVuMTA5"),
    ("kitten109sitting109", "a2l0dGVuMTA5c2l0dGluZzEwOQ"),
    ("kitten109agent109", "a2l0dGVuMTA5YWdlbnQxMDk"),
    ("kitten109angle109", "a2l0dGVuMTA5YW5nbGUxMDk"),
    ("sitting109angle109", "c2l0dGluZzEwOWFuZ2xlMTA5"),
    ("sitting109universe109", "c2l0dGluZzEwOXVuaXZlcnNlMTA5"),
    ("sitting109memory109", "c2l0dGluZzEwOW1lbW9yeTEwOQ"),
    ("sitting109stream109", "c2l0dGluZzEwOXN0cmVhbTEwOQ"),
    ("agent109stream109", "YWdlbnQxMDlzdHJlYW0xMDk"),
    ("agent109context109", "YWdlbnQxMDljb250ZXh0MTA5"),
    ("agent109knowledge109", "YWdlbnQxMDlrbm93bGVkZ2UxMDk"),
    ("agent109vector109", "YWdlbnQxMDl2ZWN0b3IxMDk"),
    ("angle109vector109", "YW5nbGUxMDl2ZWN0b3IxMDk"),
    ("angle109processor109", "YW5nbGUxMDlwcm9jZXNzb3IxMDk"),
    ("angle109reasoning109", "YW5nbGUxMDlyZWFzb25pbmcxMDk"),
    ("angle109machine109", "YW5nbGUxMDltYWNoaW5lMTA5"),
    ("universe109machine109", "dW5pdmVyc2UxMDltYWNoaW5lMTA5"),
    ("universe109learning109", "dW5pdmVyc2UxMDlsZWFybmluZzEwOQ"),
    ("universe109model109", "dW5pdmVyc2UxMDltb2RlbDEwOQ"),
    ("universe109token109", "dW5pdmVyc2UxMDl0b2tlbjEwOQ"),
    ("memory109token109", "bWVtb3J5MTA5dG9rZW4xMDk"),
    ("memory109prompt109", "bWVtb3J5MTA5cHJvbXB0MTA5"),
    ("memory109session109", "bWVtb3J5MTA5c2Vzc2lvbjEwOQ"),
    ("memory109library109", "bWVtb3J5MTA5bGlicmFyeTEwOQ"),
    ("stream109library109", "c3RyZWFtMTA5bGlicmFyeTEwOQ"),
    ("stream109service109", "c3RyZWFtMTA5c2VydmljZTEwOQ"),
    ("stream109gateway109", "c3RyZWFtMTA5Z2F0ZXdheTEwOQ"),
    ("stream109storage109", "c3RyZWFtMTA5c3RvcmFnZTEwOQ"),
    ("context109storage109", "Y29udGV4dDEwOXN0b3JhZ2UxMDk"),
    ("context109network109", "Y29udGV4dDEwOW5ldHdvcmsxMDk"),
    ("context109latency109", "Y29udGV4dDEwOWxhdGVuY3kxMDk"),
    ("context109buffer109", "Y29udGV4dDEwOWJ1ZmZlcjEwOQ"),
    ("knowledge109buffer109", "a25vd2xlZGdlMTA5YnVmZmVyMTA5"),
    ("knowledge109queue109", "a25vd2xlZGdlMTA5cXVldWUxMDk"),
    ("knowledge109worker109", "a25vd2xlZGdlMTA5d29ya2VyMTA5"),
    ("knowledge109kernel109", "a25vd2xlZGdlMTA5a2VybmVsMTA5"),
    ("vector109kernel109", "dmVjdG9yMTA5a2VybmVsMTA5"),
    ("vector109signal109", "dmVjdG9yMTA5c2lnbmFsMTA5"),
    ("vector109packet109", "dmVjdG9yMTA5cGFja2V0MTA5"),
    ("vector109router109", "dmVjdG9yMTA5cm91dGVyMTA5"),
    ("processor109router109", "cHJvY2Vzc29yMTA5cm91dGVyMTA5"),
    ("processor109cluster109", "cHJvY2Vzc29yMTA5Y2x1c3RlcjEwOQ"),
    ("processor109mirror109", "cHJvY2Vzc29yMTA5bWlycm9yMTA5"),
    ("processor109filter109", "cHJvY2Vzc29yMTA5ZmlsdGVyMTA5"),
    ("reasoning109filter109", "cmVhc29uaW5nMTA5ZmlsdGVyMTA5"),
    ("reasoning109ranking109", "cmVhc29uaW5nMTA5cmFua2luZzEwOQ"),
    ("reasoning109encoding109", "cmVhc29uaW5nMTA5ZW5jb2RpbmcxMDk"),
    ("reasoning109mapping109", "cmVhc29uaW5nMTA5bWFwcGluZzEwOQ"),
    ("machine109mapping109", "bWFjaGluZTEwOW1hcHBpbmcxMDk"),
    ("machine109record109", "bWFjaGluZTEwOXJlY29yZDEwOQ"),
    ("machine109candle109", "bWFjaGluZTEwOWNhbmRsZTEwOQ"),
    ("machine109thread109", "bWFjaGluZTEwOXRocmVhZDEwOQ"),
    ("learning109thread109", "bGVhcm5pbmcxMDl0aHJlYWQxMDk"),
    ("learning109kitten109", "bGVhcm5pbmcxMDlraXR0ZW4xMDk"),
    ("learning109sitting109", "bGVhcm5pbmcxMDlzaXR0aW5nMTA5"),
    ("learning109agent109", "bGVhcm5pbmcxMDlhZ2VudDEwOQ"),
    ("model109agent109", "bW9kZWwxMDlhZ2VudDEwOQ"),
    ("model109angle109", "bW9kZWwxMDlhbmdsZTEwOQ"),
    ("model109universe109", "bW9kZWwxMDl1bml2ZXJzZTEwOQ"),
    ("model109memory109", "bW9kZWwxMDltZW1vcnkxMDk"),
    ("token109memory109", "dG9rZW4xMDltZW1vcnkxMDk"),
    ("token109stream109", "dG9rZW4xMDlzdHJlYW0xMDk"),
    ("token109context109", "dG9rZW4xMDljb250ZXh0MTA5"),
    ("token109knowledge109", "dG9rZW4xMDlrbm93bGVkZ2UxMDk"),
    ("prompt109knowledge109", "cHJvbXB0MTA5a25vd2xlZGdlMTA5"),
    ("prompt109vector109", "cHJvbXB0MTA5dmVjdG9yMTA5"),
    ("prompt109processor109", "cHJvbXB0MTA5cHJvY2Vzc29yMTA5"),
    ("prompt109reasoning109", "cHJvbXB0MTA5cmVhc29uaW5nMTA5"),
    ("session109reasoning109", "c2Vzc2lvbjEwOXJlYXNvbmluZzEwOQ"),
    ("session109machine109", "c2Vzc2lvbjEwOW1hY2hpbmUxMDk"),
    ("session109learning109", "c2Vzc2lvbjEwOWxlYXJuaW5nMTA5"),
    ("session109model109", "c2Vzc2lvbjEwOW1vZGVsMTA5"),
    ("library109model109", "bGlicmFyeTEwOW1vZGVsMTA5"),
    ("library109token109", "bGlicmFyeTEwOXRva2VuMTA5"),
    ("library109prompt109", "bGlicmFyeTEwOXByb21wdDEwOQ"),
    ("library109session109", "bGlicmFyeTEwOXNlc3Npb24xMDk"),
    ("service109session109", "c2VydmljZTEwOXNlc3Npb24xMDk"),
    ("service109library109", "c2VydmljZTEwOWxpYnJhcnkxMDk"),
    ("service109service109", "c2VydmljZTEwOXNlcnZpY2UxMDk"),
    ("service109gateway109", "c2VydmljZTEwOWdhdGV3YXkxMDk"),
    ("gateway109gateway109", "Z2F0ZXdheTEwOWdhdGV3YXkxMDk"),
    ("gateway109storage109", "Z2F0ZXdheTEwOXN0b3JhZ2UxMDk"),
    ("gateway109network109", "Z2F0ZXdheTEwOW5ldHdvcmsxMDk"),
    ("gateway109latency109", "Z2F0ZXdheTEwOWxhdGVuY3kxMDk"),
    ("storage109latency109", "c3RvcmFnZTEwOWxhdGVuY3kxMDk"),
    ("storage109buffer109", "c3RvcmFnZTEwOWJ1ZmZlcjEwOQ"),
    ("storage109queue109", "c3RvcmFnZTEwOXF1ZXVlMTA5"),
    ("storage109worker109", "c3RvcmFnZTEwOXdvcmtlcjEwOQ"),
    ("network109worker109", "bmV0d29yazEwOXdvcmtlcjEwOQ"),
    ("network109kernel109", "bmV0d29yazEwOWtlcm5lbDEwOQ"),
    ("network109signal109", "bmV0d29yazEwOXNpZ25hbDEwOQ"),
    ("network109packet109", "bmV0d29yazEwOXBhY2tldDEwOQ"),
    ("latency109packet109", "bGF0ZW5jeTEwOXBhY2tldDEwOQ"),
    ("latency109router109", "bGF0ZW5jeTEwOXJvdXRlcjEwOQ"),
    ("latency109cluster109", "bGF0ZW5jeTEwOWNsdXN0ZXIxMDk"),
    ("latency109mirror109", "bGF0ZW5jeTEwOW1pcnJvcjEwOQ"),
    ("buffer109mirror109", "YnVmZmVyMTA5bWlycm9yMTA5"),
    ("buffer109filter109", "YnVmZmVyMTA5ZmlsdGVyMTA5"),
    ("buffer109ranking109", "YnVmZmVyMTA5cmFua2luZzEwOQ"),
    ("buffer109encoding109", "YnVmZmVyMTA5ZW5jb2RpbmcxMDk"),
    ("queue109encoding109", "cXVldWUxMDllbmNvZGluZzEwOQ"),
    ("queue109mapping109", "cXVldWUxMDltYXBwaW5nMTA5"),
    ("queue109record109", "cXVldWUxMDlyZWNvcmQxMDk"),
    ("queue109candle109", "cXVldWUxMDljYW5kbGUxMDk"),
    ("worker109candle109", "d29ya2VyMTA5Y2FuZGxlMTA5"),
    ("worker109thread109", "d29ya2VyMTA5dGhyZWFkMTA5"),
    ("worker109kitten109", "d29ya2VyMTA5a2l0dGVuMTA5"),
    ("worker109sitting109", "d29ya2VyMTA5c2l0dGluZzEwOQ"),
    ("kernel109sitting109", "a2VybmVsMTA5c2l0dGluZzEwOQ"),
    ("kernel109agent109", "a2VybmVsMTA5YWdlbnQxMDk"),
    ("kernel109angle109", "a2VybmVsMTA5YW5nbGUxMDk"),
    ("kernel109universe109", "a2VybmVsMTA5dW5pdmVyc2UxMDk"),
    ("signal109universe109", "c2lnbmFsMTA5dW5pdmVyc2UxMDk"),
    ("signal109memory109", "c2lnbmFsMTA5bWVtb3J5MTA5"),
    ("signal109stream109", "c2lnbmFsMTA5c3RyZWFtMTA5"),
    ("signal109context109", "c2lnbmFsMTA5Y29udGV4dDEwOQ"),
    ("packet109context109", "cGFja2V0MTA5Y29udGV4dDEwOQ"),
    ("packet109knowledge109", "cGFja2V0MTA5a25vd2xlZGdlMTA5"),
    ("packet109vector109", "cGFja2V0MTA5dmVjdG9yMTA5"),
    ("packet109processor109", "cGFja2V0MTA5cHJvY2Vzc29yMTA5"),
    ("router109processor109", "cm91dGVyMTA5cHJvY2Vzc29yMTA5"),
    ("router109reasoning109", "cm91dGVyMTA5cmVhc29uaW5nMTA5"),
    ("router109machine109", "cm91dGVyMTA5bWFjaGluZTEwOQ"),
    ("router109learning109", "cm91dGVyMTA5bGVhcm5pbmcxMDk"),
    ("cluster109learning109", "Y2x1c3RlcjEwOWxlYXJuaW5nMTA5"),
    ("cluster109model109", "Y2x1c3RlcjEwOW1vZGVsMTA5"),
    ("cluster109token109", "Y2x1c3RlcjEwOXRva2VuMTA5"),
    ("cluster109prompt109", "Y2x1c3RlcjEwOXByb21wdDEwOQ"),
    ("mirror109prompt109", "bWlycm9yMTA5cHJvbXB0MTA5"),
    ("mirror109session109", "bWlycm9yMTA5c2Vzc2lvbjEwOQ"),
    ("mirror109library109", "bWlycm9yMTA5bGlicmFyeTEwOQ"),
    ("mirror109service109", "bWlycm9yMTA5c2VydmljZTEwOQ"),
    ("filter109service109", "ZmlsdGVyMTA5c2VydmljZTEwOQ"),
    ("filter109gateway109", "ZmlsdGVyMTA5Z2F0ZXdheTEwOQ"),
    ("filter109storage109", "ZmlsdGVyMTA5c3RvcmFnZTEwOQ"),
    ("filter109network109", "ZmlsdGVyMTA5bmV0d29yazEwOQ"),
    ("ranking109network109", "cmFua2luZzEwOW5ldHdvcmsxMDk"),
    ("ranking109latency109", "cmFua2luZzEwOWxhdGVuY3kxMDk"),
    ("ranking109buffer109", "cmFua2luZzEwOWJ1ZmZlcjEwOQ"),
    ("ranking109queue109", "cmFua2luZzEwOXF1ZXVlMTA5"),
    ("encoding109queue109", "ZW5jb2RpbmcxMDlxdWV1ZTEwOQ"),
    ("encoding109worker109", "ZW5jb2RpbmcxMDl3b3JrZXIxMDk"),
    ("encoding109kernel109", "ZW5jb2RpbmcxMDlrZXJuZWwxMDk"),
    ("encoding109signal109", "ZW5jb2RpbmcxMDlzaWduYWwxMDk"),
    ("mapping109signal109", "bWFwcGluZzEwOXNpZ25hbDEwOQ"),
    ("mapping109packet109", "bWFwcGluZzEwOXBhY2tldDEwOQ"),
    ("mapping109router109", "bWFwcGluZzEwOXJvdXRlcjEwOQ"),
    ("mapping109cluster109", "bWFwcGluZzEwOWNsdXN0ZXIxMDk"),
    ("record109cluster109", "cmVjb3JkMTA5Y2x1c3RlcjEwOQ"),
    ("record109mirror109", "cmVjb3JkMTA5bWlycm9yMTA5"),
    ("record109filter109", "cmVjb3JkMTA5ZmlsdGVyMTA5"),
    ("record109ranking109", "cmVjb3JkMTA5cmFua2luZzEwOQ"),
    ("candle109ranking109", "Y2FuZGxlMTA5cmFua2luZzEwOQ"),
    ("candle109encoding109", "Y2FuZGxlMTA5ZW5jb2RpbmcxMDk"),
    ("candle109mapping109", "Y2FuZGxlMTA5bWFwcGluZzEwOQ"),
    ("candle109record109", "Y2FuZGxlMTA5cmVjb3JkMTA5"),
    ("thread109record109", "dGhyZWFkMTA5cmVjb3JkMTA5"),
    ("thread109candle109", "dGhyZWFkMTA5Y2FuZGxlMTA5"),
    ("thread109thread109", "dGhyZWFkMTA5dGhyZWFkMTA5"),
    ("thread109kitten109", "dGhyZWFkMTA5a2l0dGVuMTA5"),
    (
        "round 109: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTA5OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 109: agentuniverse is a framework for multi agents",
        "cm91bmQgMTA5OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 109: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTA5OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 109: the processor reads the record then stops",
        "cm91bmQgMTA5OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 109: a worker pulls the next task from the queue",
        "cm91bmQgMTA5OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 109: signals travel through the network layer",
        "cm91bmQgMTA5OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 109: the gateway routes each request by policy",
        "cm91bmQgMTA5OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 109: memory grows until the buffer is full",
        "cm91bmQgMTA5OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 109: the cluster mirrors every packet twice",
        "cm91bmQgMTA5OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 109: ranking uses tokens learned from the corpus",
        "cm91bmQgMTA5OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 109: a long session ends when the candle dies",
        "cm91bmQgMTA5OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 109: encode the prompt then map the result",
        "cm91bmQgMTA5OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 109: the kernel wakes the worker at dawn",
        "cm91bmQgMTA5OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 109: service latency drops after the patch",
        "cm91bmQgMTA5OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 109: the library caches every vector it sees",
        "cm91bmQgMTA5OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 109: agents argue then the debate resolves",
        "cm91bmQgMTA5OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 109: the filter keeps only strong matches",
        "cm91bmQgMTA5OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 109: the model answers with a short reply",
        "cm91bmQgMTA5OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 109: the recorder stores the reasoning trace",
        "cm91bmQgMTA5OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 109: the angel watches the processor run",
        "cm91bmQgMTA5OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 109: angle of the vector decides the match",
        "cm91bmQgMTA5OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 109: the candle burns twice as long at night",
        "cm91bmQgMTA5OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 109: a mirror of the universe in one line",
        "cm91bmQgMTA5OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 109: the queue drains before the storm", "cm91bmQgMTA5OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
