"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten110kitten110", "a2l0dGVuMTEwa2l0dGVuMTEw"),
    ("kitten110sitting110", "a2l0dGVuMTEwc2l0dGluZzExMA"),
    ("kitten110agent110", "a2l0dGVuMTEwYWdlbnQxMTA"),
    ("kitten110angle110", "a2l0dGVuMTEwYW5nbGUxMTA"),
    ("sitting110angle110", "c2l0dGluZzExMGFuZ2xlMTEw"),
    ("sitting110universe110", "c2l0dGluZzExMHVuaXZlcnNlMTEw"),
    ("sitting110memory110", "c2l0dGluZzExMG1lbW9yeTExMA"),
    ("sitting110stream110", "c2l0dGluZzExMHN0cmVhbTExMA"),
    ("agent110stream110", "YWdlbnQxMTBzdHJlYW0xMTA"),
    ("agent110context110", "YWdlbnQxMTBjb250ZXh0MTEw"),
    ("agent110knowledge110", "YWdlbnQxMTBrbm93bGVkZ2UxMTA"),
    ("agent110vector110", "YWdlbnQxMTB2ZWN0b3IxMTA"),
    ("angle110vector110", "YW5nbGUxMTB2ZWN0b3IxMTA"),
    ("angle110processor110", "YW5nbGUxMTBwcm9jZXNzb3IxMTA"),
    ("angle110reasoning110", "YW5nbGUxMTByZWFzb25pbmcxMTA"),
    ("angle110machine110", "YW5nbGUxMTBtYWNoaW5lMTEw"),
    ("universe110machine110", "dW5pdmVyc2UxMTBtYWNoaW5lMTEw"),
    ("universe110learning110", "dW5pdmVyc2UxMTBsZWFybmluZzExMA"),
    ("universe110model110", "dW5pdmVyc2UxMTBtb2RlbDExMA"),
    ("universe110token110", "dW5pdmVyc2UxMTB0b2tlbjExMA"),
    ("memory110token110", "bWVtb3J5MTEwdG9rZW4xMTA"),
    ("memory110prompt110", "bWVtb3J5MTEwcHJvbXB0MTEw"),
    ("memory110session110", "bWVtb3J5MTEwc2Vzc2lvbjExMA"),
    ("memory110library110", "bWVtb3J5MTEwbGlicmFyeTExMA"),
    ("stream110library110", "c3RyZWFtMTEwbGlicmFyeTExMA"),
    ("stream110service110", "c3RyZWFtMTEwc2VydmljZTExMA"),
    ("stream110gateway110", "c3RyZWFtMTEwZ2F0ZXdheTExMA"),
    ("stream110storage110", "c3RyZWFtMTEwc3RvcmFnZTExMA"),
    ("context110storage110", "Y29udGV4dDExMHN0b3JhZ2UxMTA"),
    ("context110network110", "Y29udGV4dDExMG5ldHdvcmsxMTA"),
    ("context110latency110", "Y29udGV4dDExMGxhdGVuY3kxMTA"),
    ("context110buffer110", "Y29udGV4dDExMGJ1ZmZlcjExMA"),
    ("knowledge110buffer110", "a25vd2xlZGdlMTEwYnVmZmVyMTEw"),
    ("knowledge110queue110", "a25vd2xlZGdlMTEwcXVldWUxMTA"),
    ("knowledge110worker110", "a25vd2xlZGdlMTEwd29ya2VyMTEw"),
    ("knowledge110kernel110", "a25vd2xlZGdlMTEwa2VybmVsMTEw"),
    ("vector110kernel110", "dmVjdG9yMTEwa2VybmVsMTEw"),
    ("vector110signal110", "dmVjdG9yMTEwc2lnbmFsMTEw"),
    ("vector110packet110", "dmVjdG9yMTEwcGFja2V0MTEw"),
    ("vector110router110", "dmVjdG9yMTEwcm91dGVyMTEw"),
    ("processor110router110", "cHJvY2Vzc29yMTEwcm91dGVyMTEw"),
    ("processor110cluster110", "cHJvY2Vzc29yMTEwY2x1c3RlcjExMA"),
    ("processor110mirror110", "cHJvY2Vzc29yMTEwbWlycm9yMTEw"),
    ("processor110filter110", "cHJvY2Vzc29yMTEwZmlsdGVyMTEw"),
    ("reasoning110filter110", "cmVhc29uaW5nMTEwZmlsdGVyMTEw"),
    ("reasoning110ranking110", "cmVhc29uaW5nMTEwcmFua2luZzExMA"),
    ("reasoning110encoding110", "cmVhc29uaW5nMTEwZW5jb2RpbmcxMTA"),
    ("reasoning110mapping110", "cmVhc29uaW5nMTEwbWFwcGluZzExMA"),
    ("machine110mapping110", "bWFjaGluZTExMG1hcHBpbmcxMTA"),
    ("machine110record110", "bWFjaGluZTExMHJlY29yZDExMA"),
    ("machine110candle110", "bWFjaGluZTExMGNhbmRsZTExMA"),
    ("machine110thread110", "bWFjaGluZTExMHRocmVhZDExMA"),
    ("learning110thread110", "bGVhcm5pbmcxMTB0aHJlYWQxMTA"),
    ("learning110kitten110", "bGVhcm5pbmcxMTBraXR0ZW4xMTA"),
    ("learning110sitting110", "bGVhcm5pbmcxMTBzaXR0aW5nMTEw"),
    ("learning110agent110", "bGVhcm5pbmcxMTBhZ2VudDExMA"),
    ("model110agent110", "bW9kZWwxMTBhZ2VudDExMA"),
    ("model110angle110", "bW9kZWwxMTBhbmdsZTExMA"),
    ("model110universe110", "bW9kZWwxMTB1bml2ZXJzZTExMA"),
    ("model110memory110", "bW9kZWwxMTBtZW1vcnkxMTA"),
    ("token110memory110", "dG9rZW4xMTBtZW1vcnkxMTA"),
    ("token110stream110", "dG9rZW4xMTBzdHJlYW0xMTA"),
    ("token110context110", "dG9rZW4xMTBjb250ZXh0MTEw"),
    ("token110knowledge110", "dG9rZW4xMTBrbm93bGVkZ2UxMTA"),
    ("prompt110knowledge110", "cHJvbXB0MTEwa25vd2xlZGdlMTEw"),
    ("prompt110vector110", "cHJvbXB0MTEwdmVjdG9yMTEw"),
    ("prompt110processor110", "cHJvbXB0MTEwcHJvY2Vzc29yMTEw"),
    ("prompt110reasoning110", "cHJvbXB0MTEwcmVhc29uaW5nMTEw"),
    ("session110reasoning110", "c2Vzc2lvbjExMHJlYXNvbmluZzExMA"),
    ("session110machine110", "c2Vzc2lvbjExMG1hY2hpbmUxMTA"),
    ("session110learning110", "c2Vzc2lvbjExMGxlYXJuaW5nMTEw"),
    ("session110model110", "c2Vzc2lvbjExMG1vZGVsMTEw"),
    ("library110model110", "bGlicmFyeTExMG1vZGVsMTEw"),
    ("library110token110", "bGlicmFyeTExMHRva2VuMTEw"),
    ("library110prompt110", "bGlicmFyeTExMHByb21wdDExMA"),
    ("library110session110", "bGlicmFyeTExMHNlc3Npb24xMTA"),
    ("service110session110", "c2VydmljZTExMHNlc3Npb24xMTA"),
    ("service110library110", "c2VydmljZTExMGxpYnJhcnkxMTA"),
    ("service110service110", "c2VydmljZTExMHNlcnZpY2UxMTA"),
    ("service110gateway110", "c2VydmljZTExMGdhdGV3YXkxMTA"),
    ("gateway110gateway110", "Z2F0ZXdheTExMGdhdGV3YXkxMTA"),
    ("gateway110storage110", "Z2F0ZXdheTExMHN0b3JhZ2UxMTA"),
    ("gateway110network110", "Z2F0ZXdheTExMG5ldHdvcmsxMTA"),
    ("gateway110latency110", "Z2F0ZXdheTExMGxhdGVuY3kxMTA"),
    ("storage110latency110", "c3RvcmFnZTExMGxhdGVuY3kxMTA"),
    ("storage110buffer110", "c3RvcmFnZTExMGJ1ZmZlcjExMA"),
    ("storage110queue110", "c3RvcmFnZTExMHF1ZXVlMTEw"),
    ("storage110worker110", "c3RvcmFnZTExMHdvcmtlcjExMA"),
    ("network110worker110", "bmV0d29yazExMHdvcmtlcjExMA"),
    ("network110kernel110", "bmV0d29yazExMGtlcm5lbDExMA"),
    ("network110signal110", "bmV0d29yazExMHNpZ25hbDExMA"),
    ("network110packet110", "bmV0d29yazExMHBhY2tldDExMA"),
    ("latency110packet110", "bGF0ZW5jeTExMHBhY2tldDExMA"),
    ("latency110router110", "bGF0ZW5jeTExMHJvdXRlcjExMA"),
    ("latency110cluster110", "bGF0ZW5jeTExMGNsdXN0ZXIxMTA"),
    ("latency110mirror110", "bGF0ZW5jeTExMG1pcnJvcjExMA"),
    ("buffer110mirror110", "YnVmZmVyMTEwbWlycm9yMTEw"),
    ("buffer110filter110", "YnVmZmVyMTEwZmlsdGVyMTEw"),
    ("buffer110ranking110", "YnVmZmVyMTEwcmFua2luZzExMA"),
    ("buffer110encoding110", "YnVmZmVyMTEwZW5jb2RpbmcxMTA"),
    ("queue110encoding110", "cXVldWUxMTBlbmNvZGluZzExMA"),
    ("queue110mapping110", "cXVldWUxMTBtYXBwaW5nMTEw"),
    ("queue110record110", "cXVldWUxMTByZWNvcmQxMTA"),
    ("queue110candle110", "cXVldWUxMTBjYW5kbGUxMTA"),
    ("worker110candle110", "d29ya2VyMTEwY2FuZGxlMTEw"),
    ("worker110thread110", "d29ya2VyMTEwdGhyZWFkMTEw"),
    ("worker110kitten110", "d29ya2VyMTEwa2l0dGVuMTEw"),
    ("worker110sitting110", "d29ya2VyMTEwc2l0dGluZzExMA"),
    ("kernel110sitting110", "a2VybmVsMTEwc2l0dGluZzExMA"),
    ("kernel110agent110", "a2VybmVsMTEwYWdlbnQxMTA"),
    ("kernel110angle110", "a2VybmVsMTEwYW5nbGUxMTA"),
    ("kernel110universe110", "a2VybmVsMTEwdW5pdmVyc2UxMTA"),
    ("signal110universe110", "c2lnbmFsMTEwdW5pdmVyc2UxMTA"),
    ("signal110memory110", "c2lnbmFsMTEwbWVtb3J5MTEw"),
    ("signal110stream110", "c2lnbmFsMTEwc3RyZWFtMTEw"),
    ("signal110context110", "c2lnbmFsMTEwY29udGV4dDExMA"),
    ("packet110context110", "cGFja2V0MTEwY29udGV4dDExMA"),
    ("packet110knowledge110", "cGFja2V0MTEwa25vd2xlZGdlMTEw"),
    ("packet110vector110", "cGFja2V0MTEwdmVjdG9yMTEw"),
    ("packet110processor110", "cGFja2V0MTEwcHJvY2Vzc29yMTEw"),
    ("router110processor110", "cm91dGVyMTEwcHJvY2Vzc29yMTEw"),
    ("router110reasoning110", "cm91dGVyMTEwcmVhc29uaW5nMTEw"),
    ("router110machine110", "cm91dGVyMTEwbWFjaGluZTExMA"),
    ("router110learning110", "cm91dGVyMTEwbGVhcm5pbmcxMTA"),
    ("cluster110learning110", "Y2x1c3RlcjExMGxlYXJuaW5nMTEw"),
    ("cluster110model110", "Y2x1c3RlcjExMG1vZGVsMTEw"),
    ("cluster110token110", "Y2x1c3RlcjExMHRva2VuMTEw"),
    ("cluster110prompt110", "Y2x1c3RlcjExMHByb21wdDExMA"),
    ("mirror110prompt110", "bWlycm9yMTEwcHJvbXB0MTEw"),
    ("mirror110session110", "bWlycm9yMTEwc2Vzc2lvbjExMA"),
    ("mirror110library110", "bWlycm9yMTEwbGlicmFyeTExMA"),
    ("mirror110service110", "bWlycm9yMTEwc2VydmljZTExMA"),
    ("filter110service110", "ZmlsdGVyMTEwc2VydmljZTExMA"),
    ("filter110gateway110", "ZmlsdGVyMTEwZ2F0ZXdheTExMA"),
    ("filter110storage110", "ZmlsdGVyMTEwc3RvcmFnZTExMA"),
    ("filter110network110", "ZmlsdGVyMTEwbmV0d29yazExMA"),
    ("ranking110network110", "cmFua2luZzExMG5ldHdvcmsxMTA"),
    ("ranking110latency110", "cmFua2luZzExMGxhdGVuY3kxMTA"),
    ("ranking110buffer110", "cmFua2luZzExMGJ1ZmZlcjExMA"),
    ("ranking110queue110", "cmFua2luZzExMHF1ZXVlMTEw"),
    ("encoding110queue110", "ZW5jb2RpbmcxMTBxdWV1ZTExMA"),
    ("encoding110worker110", "ZW5jb2RpbmcxMTB3b3JrZXIxMTA"),
    ("encoding110kernel110", "ZW5jb2RpbmcxMTBrZXJuZWwxMTA"),
    ("encoding110signal110", "ZW5jb2RpbmcxMTBzaWduYWwxMTA"),
    ("mapping110signal110", "bWFwcGluZzExMHNpZ25hbDExMA"),
    ("mapping110packet110", "bWFwcGluZzExMHBhY2tldDExMA"),
    ("mapping110router110", "bWFwcGluZzExMHJvdXRlcjExMA"),
    ("mapping110cluster110", "bWFwcGluZzExMGNsdXN0ZXIxMTA"),
    ("record110cluster110", "cmVjb3JkMTEwY2x1c3RlcjExMA"),
    ("record110mirror110", "cmVjb3JkMTEwbWlycm9yMTEw"),
    ("record110filter110", "cmVjb3JkMTEwZmlsdGVyMTEw"),
    ("record110ranking110", "cmVjb3JkMTEwcmFua2luZzExMA"),
    ("candle110ranking110", "Y2FuZGxlMTEwcmFua2luZzExMA"),
    ("candle110encoding110", "Y2FuZGxlMTEwZW5jb2RpbmcxMTA"),
    ("candle110mapping110", "Y2FuZGxlMTEwbWFwcGluZzExMA"),
    ("candle110record110", "Y2FuZGxlMTEwcmVjb3JkMTEw"),
    ("thread110record110", "dGhyZWFkMTEwcmVjb3JkMTEw"),
    ("thread110candle110", "dGhyZWFkMTEwY2FuZGxlMTEw"),
    ("thread110thread110", "dGhyZWFkMTEwdGhyZWFkMTEw"),
    ("thread110kitten110", "dGhyZWFkMTEwa2l0dGVuMTEw"),
    (
        "round 110: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTEwOiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 110: agentuniverse is a framework for multi agents",
        "cm91bmQgMTEwOiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 110: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTEwOiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 110: the processor reads the record then stops",
        "cm91bmQgMTEwOiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 110: a worker pulls the next task from the queue",
        "cm91bmQgMTEwOiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 110: signals travel through the network layer",
        "cm91bmQgMTEwOiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 110: the gateway routes each request by policy",
        "cm91bmQgMTEwOiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 110: memory grows until the buffer is full",
        "cm91bmQgMTEwOiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 110: the cluster mirrors every packet twice",
        "cm91bmQgMTEwOiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 110: ranking uses tokens learned from the corpus",
        "cm91bmQgMTEwOiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 110: a long session ends when the candle dies",
        "cm91bmQgMTEwOiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 110: encode the prompt then map the result",
        "cm91bmQgMTEwOiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 110: the kernel wakes the worker at dawn",
        "cm91bmQgMTEwOiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 110: service latency drops after the patch",
        "cm91bmQgMTEwOiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 110: the library caches every vector it sees",
        "cm91bmQgMTEwOiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 110: agents argue then the debate resolves",
        "cm91bmQgMTEwOiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 110: the filter keeps only strong matches",
        "cm91bmQgMTEwOiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 110: the model answers with a short reply",
        "cm91bmQgMTEwOiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 110: the recorder stores the reasoning trace",
        "cm91bmQgMTEwOiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 110: the angel watches the processor run",
        "cm91bmQgMTEwOiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 110: angle of the vector decides the match",
        "cm91bmQgMTEwOiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 110: the candle burns twice as long at night",
        "cm91bmQgMTEwOiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 110: a mirror of the universe in one line",
        "cm91bmQgMTEwOiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 110: the queue drains before the storm", "cm91bmQgMTEwOiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
