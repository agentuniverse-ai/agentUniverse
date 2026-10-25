"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten13kitten13", "a2l0dGVuMTNraXR0ZW4xMw"),
    ("kitten13sitting13", "a2l0dGVuMTNzaXR0aW5nMTM"),
    ("kitten13agent13", "a2l0dGVuMTNhZ2VudDEz"),
    ("kitten13angle13", "a2l0dGVuMTNhbmdsZTEz"),
    ("sitting13angle13", "c2l0dGluZzEzYW5nbGUxMw"),
    ("sitting13universe13", "c2l0dGluZzEzdW5pdmVyc2UxMw"),
    ("sitting13memory13", "c2l0dGluZzEzbWVtb3J5MTM"),
    ("sitting13stream13", "c2l0dGluZzEzc3RyZWFtMTM"),
    ("agent13stream13", "YWdlbnQxM3N0cmVhbTEz"),
    ("agent13context13", "YWdlbnQxM2NvbnRleHQxMw"),
    ("agent13knowledge13", "YWdlbnQxM2tub3dsZWRnZTEz"),
    ("agent13vector13", "YWdlbnQxM3ZlY3RvcjEz"),
    ("angle13vector13", "YW5nbGUxM3ZlY3RvcjEz"),
    ("angle13processor13", "YW5nbGUxM3Byb2Nlc3NvcjEz"),
    ("angle13reasoning13", "YW5nbGUxM3JlYXNvbmluZzEz"),
    ("angle13machine13", "YW5nbGUxM21hY2hpbmUxMw"),
    ("universe13machine13", "dW5pdmVyc2UxM21hY2hpbmUxMw"),
    ("universe13learning13", "dW5pdmVyc2UxM2xlYXJuaW5nMTM"),
    ("universe13model13", "dW5pdmVyc2UxM21vZGVsMTM"),
    ("universe13token13", "dW5pdmVyc2UxM3Rva2VuMTM"),
    ("memory13token13", "bWVtb3J5MTN0b2tlbjEz"),
    ("memory13prompt13", "bWVtb3J5MTNwcm9tcHQxMw"),
    ("memory13session13", "bWVtb3J5MTNzZXNzaW9uMTM"),
    ("memory13library13", "bWVtb3J5MTNsaWJyYXJ5MTM"),
    ("stream13library13", "c3RyZWFtMTNsaWJyYXJ5MTM"),
    ("stream13service13", "c3RyZWFtMTNzZXJ2aWNlMTM"),
    ("stream13gateway13", "c3RyZWFtMTNnYXRld2F5MTM"),
    ("stream13storage13", "c3RyZWFtMTNzdG9yYWdlMTM"),
    ("context13storage13", "Y29udGV4dDEzc3RvcmFnZTEz"),
    ("context13network13", "Y29udGV4dDEzbmV0d29yazEz"),
    ("context13latency13", "Y29udGV4dDEzbGF0ZW5jeTEz"),
    ("context13buffer13", "Y29udGV4dDEzYnVmZmVyMTM"),
    ("knowledge13buffer13", "a25vd2xlZGdlMTNidWZmZXIxMw"),
    ("knowledge13queue13", "a25vd2xlZGdlMTNxdWV1ZTEz"),
    ("knowledge13worker13", "a25vd2xlZGdlMTN3b3JrZXIxMw"),
    ("knowledge13kernel13", "a25vd2xlZGdlMTNrZXJuZWwxMw"),
    ("vector13kernel13", "dmVjdG9yMTNrZXJuZWwxMw"),
    ("vector13signal13", "dmVjdG9yMTNzaWduYWwxMw"),
    ("vector13packet13", "dmVjdG9yMTNwYWNrZXQxMw"),
    ("vector13router13", "dmVjdG9yMTNyb3V0ZXIxMw"),
    ("processor13router13", "cHJvY2Vzc29yMTNyb3V0ZXIxMw"),
    ("processor13cluster13", "cHJvY2Vzc29yMTNjbHVzdGVyMTM"),
    ("processor13mirror13", "cHJvY2Vzc29yMTNtaXJyb3IxMw"),
    ("processor13filter13", "cHJvY2Vzc29yMTNmaWx0ZXIxMw"),
    ("reasoning13filter13", "cmVhc29uaW5nMTNmaWx0ZXIxMw"),
    ("reasoning13ranking13", "cmVhc29uaW5nMTNyYW5raW5nMTM"),
    ("reasoning13encoding13", "cmVhc29uaW5nMTNlbmNvZGluZzEz"),
    ("reasoning13mapping13", "cmVhc29uaW5nMTNtYXBwaW5nMTM"),
    ("machine13mapping13", "bWFjaGluZTEzbWFwcGluZzEz"),
    ("machine13record13", "bWFjaGluZTEzcmVjb3JkMTM"),
    ("machine13candle13", "bWFjaGluZTEzY2FuZGxlMTM"),
    ("machine13thread13", "bWFjaGluZTEzdGhyZWFkMTM"),
    ("learning13thread13", "bGVhcm5pbmcxM3RocmVhZDEz"),
    ("learning13kitten13", "bGVhcm5pbmcxM2tpdHRlbjEz"),
    ("learning13sitting13", "bGVhcm5pbmcxM3NpdHRpbmcxMw"),
    ("learning13agent13", "bGVhcm5pbmcxM2FnZW50MTM"),
    ("model13agent13", "bW9kZWwxM2FnZW50MTM"),
    ("model13angle13", "bW9kZWwxM2FuZ2xlMTM"),
    ("model13universe13", "bW9kZWwxM3VuaXZlcnNlMTM"),
    ("model13memory13", "bW9kZWwxM21lbW9yeTEz"),
    ("token13memory13", "dG9rZW4xM21lbW9yeTEz"),
    ("token13stream13", "dG9rZW4xM3N0cmVhbTEz"),
    ("token13context13", "dG9rZW4xM2NvbnRleHQxMw"),
    ("token13knowledge13", "dG9rZW4xM2tub3dsZWRnZTEz"),
    ("prompt13knowledge13", "cHJvbXB0MTNrbm93bGVkZ2UxMw"),
    ("prompt13vector13", "cHJvbXB0MTN2ZWN0b3IxMw"),
    ("prompt13processor13", "cHJvbXB0MTNwcm9jZXNzb3IxMw"),
    ("prompt13reasoning13", "cHJvbXB0MTNyZWFzb25pbmcxMw"),
    ("session13reasoning13", "c2Vzc2lvbjEzcmVhc29uaW5nMTM"),
    ("session13machine13", "c2Vzc2lvbjEzbWFjaGluZTEz"),
    ("session13learning13", "c2Vzc2lvbjEzbGVhcm5pbmcxMw"),
    ("session13model13", "c2Vzc2lvbjEzbW9kZWwxMw"),
    ("library13model13", "bGlicmFyeTEzbW9kZWwxMw"),
    ("library13token13", "bGlicmFyeTEzdG9rZW4xMw"),
    ("library13prompt13", "bGlicmFyeTEzcHJvbXB0MTM"),
    ("library13session13", "bGlicmFyeTEzc2Vzc2lvbjEz"),
    ("service13session13", "c2VydmljZTEzc2Vzc2lvbjEz"),
    ("service13library13", "c2VydmljZTEzbGlicmFyeTEz"),
    ("service13service13", "c2VydmljZTEzc2VydmljZTEz"),
    ("service13gateway13", "c2VydmljZTEzZ2F0ZXdheTEz"),
    ("gateway13gateway13", "Z2F0ZXdheTEzZ2F0ZXdheTEz"),
    ("gateway13storage13", "Z2F0ZXdheTEzc3RvcmFnZTEz"),
    ("gateway13network13", "Z2F0ZXdheTEzbmV0d29yazEz"),
    ("gateway13latency13", "Z2F0ZXdheTEzbGF0ZW5jeTEz"),
    ("storage13latency13", "c3RvcmFnZTEzbGF0ZW5jeTEz"),
    ("storage13buffer13", "c3RvcmFnZTEzYnVmZmVyMTM"),
    ("storage13queue13", "c3RvcmFnZTEzcXVldWUxMw"),
    ("storage13worker13", "c3RvcmFnZTEzd29ya2VyMTM"),
    ("network13worker13", "bmV0d29yazEzd29ya2VyMTM"),
    ("network13kernel13", "bmV0d29yazEza2VybmVsMTM"),
    ("network13signal13", "bmV0d29yazEzc2lnbmFsMTM"),
    ("network13packet13", "bmV0d29yazEzcGFja2V0MTM"),
    ("latency13packet13", "bGF0ZW5jeTEzcGFja2V0MTM"),
    ("latency13router13", "bGF0ZW5jeTEzcm91dGVyMTM"),
    ("latency13cluster13", "bGF0ZW5jeTEzY2x1c3RlcjEz"),
    ("latency13mirror13", "bGF0ZW5jeTEzbWlycm9yMTM"),
    ("buffer13mirror13", "YnVmZmVyMTNtaXJyb3IxMw"),
    ("buffer13filter13", "YnVmZmVyMTNmaWx0ZXIxMw"),
    ("buffer13ranking13", "YnVmZmVyMTNyYW5raW5nMTM"),
    ("buffer13encoding13", "YnVmZmVyMTNlbmNvZGluZzEz"),
    ("queue13encoding13", "cXVldWUxM2VuY29kaW5nMTM"),
    ("queue13mapping13", "cXVldWUxM21hcHBpbmcxMw"),
    ("queue13record13", "cXVldWUxM3JlY29yZDEz"),
    ("queue13candle13", "cXVldWUxM2NhbmRsZTEz"),
    ("worker13candle13", "d29ya2VyMTNjYW5kbGUxMw"),
    ("worker13thread13", "d29ya2VyMTN0aHJlYWQxMw"),
    ("worker13kitten13", "d29ya2VyMTNraXR0ZW4xMw"),
    ("worker13sitting13", "d29ya2VyMTNzaXR0aW5nMTM"),
    ("kernel13sitting13", "a2VybmVsMTNzaXR0aW5nMTM"),
    ("kernel13agent13", "a2VybmVsMTNhZ2VudDEz"),
    ("kernel13angle13", "a2VybmVsMTNhbmdsZTEz"),
    ("kernel13universe13", "a2VybmVsMTN1bml2ZXJzZTEz"),
    ("signal13universe13", "c2lnbmFsMTN1bml2ZXJzZTEz"),
    ("signal13memory13", "c2lnbmFsMTNtZW1vcnkxMw"),
    ("signal13stream13", "c2lnbmFsMTNzdHJlYW0xMw"),
    ("signal13context13", "c2lnbmFsMTNjb250ZXh0MTM"),
    ("packet13context13", "cGFja2V0MTNjb250ZXh0MTM"),
    ("packet13knowledge13", "cGFja2V0MTNrbm93bGVkZ2UxMw"),
    ("packet13vector13", "cGFja2V0MTN2ZWN0b3IxMw"),
    ("packet13processor13", "cGFja2V0MTNwcm9jZXNzb3IxMw"),
    ("router13processor13", "cm91dGVyMTNwcm9jZXNzb3IxMw"),
    ("router13reasoning13", "cm91dGVyMTNyZWFzb25pbmcxMw"),
    ("router13machine13", "cm91dGVyMTNtYWNoaW5lMTM"),
    ("router13learning13", "cm91dGVyMTNsZWFybmluZzEz"),
    ("cluster13learning13", "Y2x1c3RlcjEzbGVhcm5pbmcxMw"),
    ("cluster13model13", "Y2x1c3RlcjEzbW9kZWwxMw"),
    ("cluster13token13", "Y2x1c3RlcjEzdG9rZW4xMw"),
    ("cluster13prompt13", "Y2x1c3RlcjEzcHJvbXB0MTM"),
    ("mirror13prompt13", "bWlycm9yMTNwcm9tcHQxMw"),
    ("mirror13session13", "bWlycm9yMTNzZXNzaW9uMTM"),
    ("mirror13library13", "bWlycm9yMTNsaWJyYXJ5MTM"),
    ("mirror13service13", "bWlycm9yMTNzZXJ2aWNlMTM"),
    ("filter13service13", "ZmlsdGVyMTNzZXJ2aWNlMTM"),
    ("filter13gateway13", "ZmlsdGVyMTNnYXRld2F5MTM"),
    ("filter13storage13", "ZmlsdGVyMTNzdG9yYWdlMTM"),
    ("filter13network13", "ZmlsdGVyMTNuZXR3b3JrMTM"),
    ("ranking13network13", "cmFua2luZzEzbmV0d29yazEz"),
    ("ranking13latency13", "cmFua2luZzEzbGF0ZW5jeTEz"),
    ("ranking13buffer13", "cmFua2luZzEzYnVmZmVyMTM"),
    ("ranking13queue13", "cmFua2luZzEzcXVldWUxMw"),
    ("encoding13queue13", "ZW5jb2RpbmcxM3F1ZXVlMTM"),
    ("encoding13worker13", "ZW5jb2RpbmcxM3dvcmtlcjEz"),
    ("encoding13kernel13", "ZW5jb2RpbmcxM2tlcm5lbDEz"),
    ("encoding13signal13", "ZW5jb2RpbmcxM3NpZ25hbDEz"),
    ("mapping13signal13", "bWFwcGluZzEzc2lnbmFsMTM"),
    ("mapping13packet13", "bWFwcGluZzEzcGFja2V0MTM"),
    ("mapping13router13", "bWFwcGluZzEzcm91dGVyMTM"),
    ("mapping13cluster13", "bWFwcGluZzEzY2x1c3RlcjEz"),
    ("record13cluster13", "cmVjb3JkMTNjbHVzdGVyMTM"),
    ("record13mirror13", "cmVjb3JkMTNtaXJyb3IxMw"),
    ("record13filter13", "cmVjb3JkMTNmaWx0ZXIxMw"),
    ("record13ranking13", "cmVjb3JkMTNyYW5raW5nMTM"),
    ("candle13ranking13", "Y2FuZGxlMTNyYW5raW5nMTM"),
    ("candle13encoding13", "Y2FuZGxlMTNlbmNvZGluZzEz"),
    ("candle13mapping13", "Y2FuZGxlMTNtYXBwaW5nMTM"),
    ("candle13record13", "Y2FuZGxlMTNyZWNvcmQxMw"),
    ("thread13record13", "dGhyZWFkMTNyZWNvcmQxMw"),
    ("thread13candle13", "dGhyZWFkMTNjYW5kbGUxMw"),
    ("thread13thread13", "dGhyZWFkMTN0aHJlYWQxMw"),
    ("thread13kitten13", "dGhyZWFkMTNraXR0ZW4xMw"),
    (
        "round 13: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTM6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 13: agentuniverse is a framework for multi agents",
        "cm91bmQgMTM6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 13: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTM6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 13: the processor reads the record then stops",
        "cm91bmQgMTM6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 13: a worker pulls the next task from the queue",
        "cm91bmQgMTM6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 13: signals travel through the network layer",
        "cm91bmQgMTM6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 13: the gateway routes each request by policy",
        "cm91bmQgMTM6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 13: memory grows until the buffer is full",
        "cm91bmQgMTM6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 13: the cluster mirrors every packet twice",
        "cm91bmQgMTM6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 13: ranking uses tokens learned from the corpus",
        "cm91bmQgMTM6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 13: a long session ends when the candle dies",
        "cm91bmQgMTM6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 13: encode the prompt then map the result",
        "cm91bmQgMTM6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 13: the kernel wakes the worker at dawn", "cm91bmQgMTM6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 13: service latency drops after the patch",
        "cm91bmQgMTM6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 13: the library caches every vector it sees",
        "cm91bmQgMTM6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 13: agents argue then the debate resolves",
        "cm91bmQgMTM6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 13: the filter keeps only strong matches",
        "cm91bmQgMTM6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 13: the model answers with a short reply",
        "cm91bmQgMTM6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 13: the recorder stores the reasoning trace",
        "cm91bmQgMTM6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 13: the angel watches the processor run", "cm91bmQgMTM6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 13: angle of the vector decides the match",
        "cm91bmQgMTM6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 13: the candle burns twice as long at night",
        "cm91bmQgMTM6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 13: a mirror of the universe in one line",
        "cm91bmQgMTM6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 13: the queue drains before the storm", "cm91bmQgMTM6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
