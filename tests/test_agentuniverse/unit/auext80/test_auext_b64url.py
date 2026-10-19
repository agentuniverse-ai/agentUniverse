"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten80kitten80", "a2l0dGVuODBraXR0ZW44MA"),
    ("kitten80sitting80", "a2l0dGVuODBzaXR0aW5nODA"),
    ("kitten80agent80", "a2l0dGVuODBhZ2VudDgw"),
    ("kitten80angle80", "a2l0dGVuODBhbmdsZTgw"),
    ("sitting80angle80", "c2l0dGluZzgwYW5nbGU4MA"),
    ("sitting80universe80", "c2l0dGluZzgwdW5pdmVyc2U4MA"),
    ("sitting80memory80", "c2l0dGluZzgwbWVtb3J5ODA"),
    ("sitting80stream80", "c2l0dGluZzgwc3RyZWFtODA"),
    ("agent80stream80", "YWdlbnQ4MHN0cmVhbTgw"),
    ("agent80context80", "YWdlbnQ4MGNvbnRleHQ4MA"),
    ("agent80knowledge80", "YWdlbnQ4MGtub3dsZWRnZTgw"),
    ("agent80vector80", "YWdlbnQ4MHZlY3Rvcjgw"),
    ("angle80vector80", "YW5nbGU4MHZlY3Rvcjgw"),
    ("angle80processor80", "YW5nbGU4MHByb2Nlc3Nvcjgw"),
    ("angle80reasoning80", "YW5nbGU4MHJlYXNvbmluZzgw"),
    ("angle80machine80", "YW5nbGU4MG1hY2hpbmU4MA"),
    ("universe80machine80", "dW5pdmVyc2U4MG1hY2hpbmU4MA"),
    ("universe80learning80", "dW5pdmVyc2U4MGxlYXJuaW5nODA"),
    ("universe80model80", "dW5pdmVyc2U4MG1vZGVsODA"),
    ("universe80token80", "dW5pdmVyc2U4MHRva2VuODA"),
    ("memory80token80", "bWVtb3J5ODB0b2tlbjgw"),
    ("memory80prompt80", "bWVtb3J5ODBwcm9tcHQ4MA"),
    ("memory80session80", "bWVtb3J5ODBzZXNzaW9uODA"),
    ("memory80library80", "bWVtb3J5ODBsaWJyYXJ5ODA"),
    ("stream80library80", "c3RyZWFtODBsaWJyYXJ5ODA"),
    ("stream80service80", "c3RyZWFtODBzZXJ2aWNlODA"),
    ("stream80gateway80", "c3RyZWFtODBnYXRld2F5ODA"),
    ("stream80storage80", "c3RyZWFtODBzdG9yYWdlODA"),
    ("context80storage80", "Y29udGV4dDgwc3RvcmFnZTgw"),
    ("context80network80", "Y29udGV4dDgwbmV0d29yazgw"),
    ("context80latency80", "Y29udGV4dDgwbGF0ZW5jeTgw"),
    ("context80buffer80", "Y29udGV4dDgwYnVmZmVyODA"),
    ("knowledge80buffer80", "a25vd2xlZGdlODBidWZmZXI4MA"),
    ("knowledge80queue80", "a25vd2xlZGdlODBxdWV1ZTgw"),
    ("knowledge80worker80", "a25vd2xlZGdlODB3b3JrZXI4MA"),
    ("knowledge80kernel80", "a25vd2xlZGdlODBrZXJuZWw4MA"),
    ("vector80kernel80", "dmVjdG9yODBrZXJuZWw4MA"),
    ("vector80signal80", "dmVjdG9yODBzaWduYWw4MA"),
    ("vector80packet80", "dmVjdG9yODBwYWNrZXQ4MA"),
    ("vector80router80", "dmVjdG9yODByb3V0ZXI4MA"),
    ("processor80router80", "cHJvY2Vzc29yODByb3V0ZXI4MA"),
    ("processor80cluster80", "cHJvY2Vzc29yODBjbHVzdGVyODA"),
    ("processor80mirror80", "cHJvY2Vzc29yODBtaXJyb3I4MA"),
    ("processor80filter80", "cHJvY2Vzc29yODBmaWx0ZXI4MA"),
    ("reasoning80filter80", "cmVhc29uaW5nODBmaWx0ZXI4MA"),
    ("reasoning80ranking80", "cmVhc29uaW5nODByYW5raW5nODA"),
    ("reasoning80encoding80", "cmVhc29uaW5nODBlbmNvZGluZzgw"),
    ("reasoning80mapping80", "cmVhc29uaW5nODBtYXBwaW5nODA"),
    ("machine80mapping80", "bWFjaGluZTgwbWFwcGluZzgw"),
    ("machine80record80", "bWFjaGluZTgwcmVjb3JkODA"),
    ("machine80candle80", "bWFjaGluZTgwY2FuZGxlODA"),
    ("machine80thread80", "bWFjaGluZTgwdGhyZWFkODA"),
    ("learning80thread80", "bGVhcm5pbmc4MHRocmVhZDgw"),
    ("learning80kitten80", "bGVhcm5pbmc4MGtpdHRlbjgw"),
    ("learning80sitting80", "bGVhcm5pbmc4MHNpdHRpbmc4MA"),
    ("learning80agent80", "bGVhcm5pbmc4MGFnZW50ODA"),
    ("model80agent80", "bW9kZWw4MGFnZW50ODA"),
    ("model80angle80", "bW9kZWw4MGFuZ2xlODA"),
    ("model80universe80", "bW9kZWw4MHVuaXZlcnNlODA"),
    ("model80memory80", "bW9kZWw4MG1lbW9yeTgw"),
    ("token80memory80", "dG9rZW44MG1lbW9yeTgw"),
    ("token80stream80", "dG9rZW44MHN0cmVhbTgw"),
    ("token80context80", "dG9rZW44MGNvbnRleHQ4MA"),
    ("token80knowledge80", "dG9rZW44MGtub3dsZWRnZTgw"),
    ("prompt80knowledge80", "cHJvbXB0ODBrbm93bGVkZ2U4MA"),
    ("prompt80vector80", "cHJvbXB0ODB2ZWN0b3I4MA"),
    ("prompt80processor80", "cHJvbXB0ODBwcm9jZXNzb3I4MA"),
    ("prompt80reasoning80", "cHJvbXB0ODByZWFzb25pbmc4MA"),
    ("session80reasoning80", "c2Vzc2lvbjgwcmVhc29uaW5nODA"),
    ("session80machine80", "c2Vzc2lvbjgwbWFjaGluZTgw"),
    ("session80learning80", "c2Vzc2lvbjgwbGVhcm5pbmc4MA"),
    ("session80model80", "c2Vzc2lvbjgwbW9kZWw4MA"),
    ("library80model80", "bGlicmFyeTgwbW9kZWw4MA"),
    ("library80token80", "bGlicmFyeTgwdG9rZW44MA"),
    ("library80prompt80", "bGlicmFyeTgwcHJvbXB0ODA"),
    ("library80session80", "bGlicmFyeTgwc2Vzc2lvbjgw"),
    ("service80session80", "c2VydmljZTgwc2Vzc2lvbjgw"),
    ("service80library80", "c2VydmljZTgwbGlicmFyeTgw"),
    ("service80service80", "c2VydmljZTgwc2VydmljZTgw"),
    ("service80gateway80", "c2VydmljZTgwZ2F0ZXdheTgw"),
    ("gateway80gateway80", "Z2F0ZXdheTgwZ2F0ZXdheTgw"),
    ("gateway80storage80", "Z2F0ZXdheTgwc3RvcmFnZTgw"),
    ("gateway80network80", "Z2F0ZXdheTgwbmV0d29yazgw"),
    ("gateway80latency80", "Z2F0ZXdheTgwbGF0ZW5jeTgw"),
    ("storage80latency80", "c3RvcmFnZTgwbGF0ZW5jeTgw"),
    ("storage80buffer80", "c3RvcmFnZTgwYnVmZmVyODA"),
    ("storage80queue80", "c3RvcmFnZTgwcXVldWU4MA"),
    ("storage80worker80", "c3RvcmFnZTgwd29ya2VyODA"),
    ("network80worker80", "bmV0d29yazgwd29ya2VyODA"),
    ("network80kernel80", "bmV0d29yazgwa2VybmVsODA"),
    ("network80signal80", "bmV0d29yazgwc2lnbmFsODA"),
    ("network80packet80", "bmV0d29yazgwcGFja2V0ODA"),
    ("latency80packet80", "bGF0ZW5jeTgwcGFja2V0ODA"),
    ("latency80router80", "bGF0ZW5jeTgwcm91dGVyODA"),
    ("latency80cluster80", "bGF0ZW5jeTgwY2x1c3Rlcjgw"),
    ("latency80mirror80", "bGF0ZW5jeTgwbWlycm9yODA"),
    ("buffer80mirror80", "YnVmZmVyODBtaXJyb3I4MA"),
    ("buffer80filter80", "YnVmZmVyODBmaWx0ZXI4MA"),
    ("buffer80ranking80", "YnVmZmVyODByYW5raW5nODA"),
    ("buffer80encoding80", "YnVmZmVyODBlbmNvZGluZzgw"),
    ("queue80encoding80", "cXVldWU4MGVuY29kaW5nODA"),
    ("queue80mapping80", "cXVldWU4MG1hcHBpbmc4MA"),
    ("queue80record80", "cXVldWU4MHJlY29yZDgw"),
    ("queue80candle80", "cXVldWU4MGNhbmRsZTgw"),
    ("worker80candle80", "d29ya2VyODBjYW5kbGU4MA"),
    ("worker80thread80", "d29ya2VyODB0aHJlYWQ4MA"),
    ("worker80kitten80", "d29ya2VyODBraXR0ZW44MA"),
    ("worker80sitting80", "d29ya2VyODBzaXR0aW5nODA"),
    ("kernel80sitting80", "a2VybmVsODBzaXR0aW5nODA"),
    ("kernel80agent80", "a2VybmVsODBhZ2VudDgw"),
    ("kernel80angle80", "a2VybmVsODBhbmdsZTgw"),
    ("kernel80universe80", "a2VybmVsODB1bml2ZXJzZTgw"),
    ("signal80universe80", "c2lnbmFsODB1bml2ZXJzZTgw"),
    ("signal80memory80", "c2lnbmFsODBtZW1vcnk4MA"),
    ("signal80stream80", "c2lnbmFsODBzdHJlYW04MA"),
    ("signal80context80", "c2lnbmFsODBjb250ZXh0ODA"),
    ("packet80context80", "cGFja2V0ODBjb250ZXh0ODA"),
    ("packet80knowledge80", "cGFja2V0ODBrbm93bGVkZ2U4MA"),
    ("packet80vector80", "cGFja2V0ODB2ZWN0b3I4MA"),
    ("packet80processor80", "cGFja2V0ODBwcm9jZXNzb3I4MA"),
    ("router80processor80", "cm91dGVyODBwcm9jZXNzb3I4MA"),
    ("router80reasoning80", "cm91dGVyODByZWFzb25pbmc4MA"),
    ("router80machine80", "cm91dGVyODBtYWNoaW5lODA"),
    ("router80learning80", "cm91dGVyODBsZWFybmluZzgw"),
    ("cluster80learning80", "Y2x1c3RlcjgwbGVhcm5pbmc4MA"),
    ("cluster80model80", "Y2x1c3RlcjgwbW9kZWw4MA"),
    ("cluster80token80", "Y2x1c3RlcjgwdG9rZW44MA"),
    ("cluster80prompt80", "Y2x1c3RlcjgwcHJvbXB0ODA"),
    ("mirror80prompt80", "bWlycm9yODBwcm9tcHQ4MA"),
    ("mirror80session80", "bWlycm9yODBzZXNzaW9uODA"),
    ("mirror80library80", "bWlycm9yODBsaWJyYXJ5ODA"),
    ("mirror80service80", "bWlycm9yODBzZXJ2aWNlODA"),
    ("filter80service80", "ZmlsdGVyODBzZXJ2aWNlODA"),
    ("filter80gateway80", "ZmlsdGVyODBnYXRld2F5ODA"),
    ("filter80storage80", "ZmlsdGVyODBzdG9yYWdlODA"),
    ("filter80network80", "ZmlsdGVyODBuZXR3b3JrODA"),
    ("ranking80network80", "cmFua2luZzgwbmV0d29yazgw"),
    ("ranking80latency80", "cmFua2luZzgwbGF0ZW5jeTgw"),
    ("ranking80buffer80", "cmFua2luZzgwYnVmZmVyODA"),
    ("ranking80queue80", "cmFua2luZzgwcXVldWU4MA"),
    ("encoding80queue80", "ZW5jb2Rpbmc4MHF1ZXVlODA"),
    ("encoding80worker80", "ZW5jb2Rpbmc4MHdvcmtlcjgw"),
    ("encoding80kernel80", "ZW5jb2Rpbmc4MGtlcm5lbDgw"),
    ("encoding80signal80", "ZW5jb2Rpbmc4MHNpZ25hbDgw"),
    ("mapping80signal80", "bWFwcGluZzgwc2lnbmFsODA"),
    ("mapping80packet80", "bWFwcGluZzgwcGFja2V0ODA"),
    ("mapping80router80", "bWFwcGluZzgwcm91dGVyODA"),
    ("mapping80cluster80", "bWFwcGluZzgwY2x1c3Rlcjgw"),
    ("record80cluster80", "cmVjb3JkODBjbHVzdGVyODA"),
    ("record80mirror80", "cmVjb3JkODBtaXJyb3I4MA"),
    ("record80filter80", "cmVjb3JkODBmaWx0ZXI4MA"),
    ("record80ranking80", "cmVjb3JkODByYW5raW5nODA"),
    ("candle80ranking80", "Y2FuZGxlODByYW5raW5nODA"),
    ("candle80encoding80", "Y2FuZGxlODBlbmNvZGluZzgw"),
    ("candle80mapping80", "Y2FuZGxlODBtYXBwaW5nODA"),
    ("candle80record80", "Y2FuZGxlODByZWNvcmQ4MA"),
    ("thread80record80", "dGhyZWFkODByZWNvcmQ4MA"),
    ("thread80candle80", "dGhyZWFkODBjYW5kbGU4MA"),
    ("thread80thread80", "dGhyZWFkODB0aHJlYWQ4MA"),
    ("thread80kitten80", "dGhyZWFkODBraXR0ZW44MA"),
    (
        "round 80: the quick brown fox jumps over the lazy dog",
        "cm91bmQgODA6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 80: agentuniverse is a framework for multi agents",
        "cm91bmQgODA6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 80: knowledge stored as vectors enables retrieval",
        "cm91bmQgODA6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 80: the processor reads the record then stops",
        "cm91bmQgODA6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 80: a worker pulls the next task from the queue",
        "cm91bmQgODA6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 80: signals travel through the network layer",
        "cm91bmQgODA6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 80: the gateway routes each request by policy",
        "cm91bmQgODA6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 80: memory grows until the buffer is full",
        "cm91bmQgODA6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 80: the cluster mirrors every packet twice",
        "cm91bmQgODA6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 80: ranking uses tokens learned from the corpus",
        "cm91bmQgODA6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 80: a long session ends when the candle dies",
        "cm91bmQgODA6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 80: encode the prompt then map the result",
        "cm91bmQgODA6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 80: the kernel wakes the worker at dawn", "cm91bmQgODA6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 80: service latency drops after the patch",
        "cm91bmQgODA6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 80: the library caches every vector it sees",
        "cm91bmQgODA6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 80: agents argue then the debate resolves",
        "cm91bmQgODA6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 80: the filter keeps only strong matches",
        "cm91bmQgODA6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 80: the model answers with a short reply",
        "cm91bmQgODA6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 80: the recorder stores the reasoning trace",
        "cm91bmQgODA6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 80: the angel watches the processor run", "cm91bmQgODA6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 80: angle of the vector decides the match",
        "cm91bmQgODA6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 80: the candle burns twice as long at night",
        "cm91bmQgODA6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 80: a mirror of the universe in one line",
        "cm91bmQgODA6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 80: the queue drains before the storm", "cm91bmQgODA6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
