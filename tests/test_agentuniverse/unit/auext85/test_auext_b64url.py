"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten85kitten85", "a2l0dGVuODVraXR0ZW44NQ"),
    ("kitten85sitting85", "a2l0dGVuODVzaXR0aW5nODU"),
    ("kitten85agent85", "a2l0dGVuODVhZ2VudDg1"),
    ("kitten85angle85", "a2l0dGVuODVhbmdsZTg1"),
    ("sitting85angle85", "c2l0dGluZzg1YW5nbGU4NQ"),
    ("sitting85universe85", "c2l0dGluZzg1dW5pdmVyc2U4NQ"),
    ("sitting85memory85", "c2l0dGluZzg1bWVtb3J5ODU"),
    ("sitting85stream85", "c2l0dGluZzg1c3RyZWFtODU"),
    ("agent85stream85", "YWdlbnQ4NXN0cmVhbTg1"),
    ("agent85context85", "YWdlbnQ4NWNvbnRleHQ4NQ"),
    ("agent85knowledge85", "YWdlbnQ4NWtub3dsZWRnZTg1"),
    ("agent85vector85", "YWdlbnQ4NXZlY3Rvcjg1"),
    ("angle85vector85", "YW5nbGU4NXZlY3Rvcjg1"),
    ("angle85processor85", "YW5nbGU4NXByb2Nlc3Nvcjg1"),
    ("angle85reasoning85", "YW5nbGU4NXJlYXNvbmluZzg1"),
    ("angle85machine85", "YW5nbGU4NW1hY2hpbmU4NQ"),
    ("universe85machine85", "dW5pdmVyc2U4NW1hY2hpbmU4NQ"),
    ("universe85learning85", "dW5pdmVyc2U4NWxlYXJuaW5nODU"),
    ("universe85model85", "dW5pdmVyc2U4NW1vZGVsODU"),
    ("universe85token85", "dW5pdmVyc2U4NXRva2VuODU"),
    ("memory85token85", "bWVtb3J5ODV0b2tlbjg1"),
    ("memory85prompt85", "bWVtb3J5ODVwcm9tcHQ4NQ"),
    ("memory85session85", "bWVtb3J5ODVzZXNzaW9uODU"),
    ("memory85library85", "bWVtb3J5ODVsaWJyYXJ5ODU"),
    ("stream85library85", "c3RyZWFtODVsaWJyYXJ5ODU"),
    ("stream85service85", "c3RyZWFtODVzZXJ2aWNlODU"),
    ("stream85gateway85", "c3RyZWFtODVnYXRld2F5ODU"),
    ("stream85storage85", "c3RyZWFtODVzdG9yYWdlODU"),
    ("context85storage85", "Y29udGV4dDg1c3RvcmFnZTg1"),
    ("context85network85", "Y29udGV4dDg1bmV0d29yazg1"),
    ("context85latency85", "Y29udGV4dDg1bGF0ZW5jeTg1"),
    ("context85buffer85", "Y29udGV4dDg1YnVmZmVyODU"),
    ("knowledge85buffer85", "a25vd2xlZGdlODVidWZmZXI4NQ"),
    ("knowledge85queue85", "a25vd2xlZGdlODVxdWV1ZTg1"),
    ("knowledge85worker85", "a25vd2xlZGdlODV3b3JrZXI4NQ"),
    ("knowledge85kernel85", "a25vd2xlZGdlODVrZXJuZWw4NQ"),
    ("vector85kernel85", "dmVjdG9yODVrZXJuZWw4NQ"),
    ("vector85signal85", "dmVjdG9yODVzaWduYWw4NQ"),
    ("vector85packet85", "dmVjdG9yODVwYWNrZXQ4NQ"),
    ("vector85router85", "dmVjdG9yODVyb3V0ZXI4NQ"),
    ("processor85router85", "cHJvY2Vzc29yODVyb3V0ZXI4NQ"),
    ("processor85cluster85", "cHJvY2Vzc29yODVjbHVzdGVyODU"),
    ("processor85mirror85", "cHJvY2Vzc29yODVtaXJyb3I4NQ"),
    ("processor85filter85", "cHJvY2Vzc29yODVmaWx0ZXI4NQ"),
    ("reasoning85filter85", "cmVhc29uaW5nODVmaWx0ZXI4NQ"),
    ("reasoning85ranking85", "cmVhc29uaW5nODVyYW5raW5nODU"),
    ("reasoning85encoding85", "cmVhc29uaW5nODVlbmNvZGluZzg1"),
    ("reasoning85mapping85", "cmVhc29uaW5nODVtYXBwaW5nODU"),
    ("machine85mapping85", "bWFjaGluZTg1bWFwcGluZzg1"),
    ("machine85record85", "bWFjaGluZTg1cmVjb3JkODU"),
    ("machine85candle85", "bWFjaGluZTg1Y2FuZGxlODU"),
    ("machine85thread85", "bWFjaGluZTg1dGhyZWFkODU"),
    ("learning85thread85", "bGVhcm5pbmc4NXRocmVhZDg1"),
    ("learning85kitten85", "bGVhcm5pbmc4NWtpdHRlbjg1"),
    ("learning85sitting85", "bGVhcm5pbmc4NXNpdHRpbmc4NQ"),
    ("learning85agent85", "bGVhcm5pbmc4NWFnZW50ODU"),
    ("model85agent85", "bW9kZWw4NWFnZW50ODU"),
    ("model85angle85", "bW9kZWw4NWFuZ2xlODU"),
    ("model85universe85", "bW9kZWw4NXVuaXZlcnNlODU"),
    ("model85memory85", "bW9kZWw4NW1lbW9yeTg1"),
    ("token85memory85", "dG9rZW44NW1lbW9yeTg1"),
    ("token85stream85", "dG9rZW44NXN0cmVhbTg1"),
    ("token85context85", "dG9rZW44NWNvbnRleHQ4NQ"),
    ("token85knowledge85", "dG9rZW44NWtub3dsZWRnZTg1"),
    ("prompt85knowledge85", "cHJvbXB0ODVrbm93bGVkZ2U4NQ"),
    ("prompt85vector85", "cHJvbXB0ODV2ZWN0b3I4NQ"),
    ("prompt85processor85", "cHJvbXB0ODVwcm9jZXNzb3I4NQ"),
    ("prompt85reasoning85", "cHJvbXB0ODVyZWFzb25pbmc4NQ"),
    ("session85reasoning85", "c2Vzc2lvbjg1cmVhc29uaW5nODU"),
    ("session85machine85", "c2Vzc2lvbjg1bWFjaGluZTg1"),
    ("session85learning85", "c2Vzc2lvbjg1bGVhcm5pbmc4NQ"),
    ("session85model85", "c2Vzc2lvbjg1bW9kZWw4NQ"),
    ("library85model85", "bGlicmFyeTg1bW9kZWw4NQ"),
    ("library85token85", "bGlicmFyeTg1dG9rZW44NQ"),
    ("library85prompt85", "bGlicmFyeTg1cHJvbXB0ODU"),
    ("library85session85", "bGlicmFyeTg1c2Vzc2lvbjg1"),
    ("service85session85", "c2VydmljZTg1c2Vzc2lvbjg1"),
    ("service85library85", "c2VydmljZTg1bGlicmFyeTg1"),
    ("service85service85", "c2VydmljZTg1c2VydmljZTg1"),
    ("service85gateway85", "c2VydmljZTg1Z2F0ZXdheTg1"),
    ("gateway85gateway85", "Z2F0ZXdheTg1Z2F0ZXdheTg1"),
    ("gateway85storage85", "Z2F0ZXdheTg1c3RvcmFnZTg1"),
    ("gateway85network85", "Z2F0ZXdheTg1bmV0d29yazg1"),
    ("gateway85latency85", "Z2F0ZXdheTg1bGF0ZW5jeTg1"),
    ("storage85latency85", "c3RvcmFnZTg1bGF0ZW5jeTg1"),
    ("storage85buffer85", "c3RvcmFnZTg1YnVmZmVyODU"),
    ("storage85queue85", "c3RvcmFnZTg1cXVldWU4NQ"),
    ("storage85worker85", "c3RvcmFnZTg1d29ya2VyODU"),
    ("network85worker85", "bmV0d29yazg1d29ya2VyODU"),
    ("network85kernel85", "bmV0d29yazg1a2VybmVsODU"),
    ("network85signal85", "bmV0d29yazg1c2lnbmFsODU"),
    ("network85packet85", "bmV0d29yazg1cGFja2V0ODU"),
    ("latency85packet85", "bGF0ZW5jeTg1cGFja2V0ODU"),
    ("latency85router85", "bGF0ZW5jeTg1cm91dGVyODU"),
    ("latency85cluster85", "bGF0ZW5jeTg1Y2x1c3Rlcjg1"),
    ("latency85mirror85", "bGF0ZW5jeTg1bWlycm9yODU"),
    ("buffer85mirror85", "YnVmZmVyODVtaXJyb3I4NQ"),
    ("buffer85filter85", "YnVmZmVyODVmaWx0ZXI4NQ"),
    ("buffer85ranking85", "YnVmZmVyODVyYW5raW5nODU"),
    ("buffer85encoding85", "YnVmZmVyODVlbmNvZGluZzg1"),
    ("queue85encoding85", "cXVldWU4NWVuY29kaW5nODU"),
    ("queue85mapping85", "cXVldWU4NW1hcHBpbmc4NQ"),
    ("queue85record85", "cXVldWU4NXJlY29yZDg1"),
    ("queue85candle85", "cXVldWU4NWNhbmRsZTg1"),
    ("worker85candle85", "d29ya2VyODVjYW5kbGU4NQ"),
    ("worker85thread85", "d29ya2VyODV0aHJlYWQ4NQ"),
    ("worker85kitten85", "d29ya2VyODVraXR0ZW44NQ"),
    ("worker85sitting85", "d29ya2VyODVzaXR0aW5nODU"),
    ("kernel85sitting85", "a2VybmVsODVzaXR0aW5nODU"),
    ("kernel85agent85", "a2VybmVsODVhZ2VudDg1"),
    ("kernel85angle85", "a2VybmVsODVhbmdsZTg1"),
    ("kernel85universe85", "a2VybmVsODV1bml2ZXJzZTg1"),
    ("signal85universe85", "c2lnbmFsODV1bml2ZXJzZTg1"),
    ("signal85memory85", "c2lnbmFsODVtZW1vcnk4NQ"),
    ("signal85stream85", "c2lnbmFsODVzdHJlYW04NQ"),
    ("signal85context85", "c2lnbmFsODVjb250ZXh0ODU"),
    ("packet85context85", "cGFja2V0ODVjb250ZXh0ODU"),
    ("packet85knowledge85", "cGFja2V0ODVrbm93bGVkZ2U4NQ"),
    ("packet85vector85", "cGFja2V0ODV2ZWN0b3I4NQ"),
    ("packet85processor85", "cGFja2V0ODVwcm9jZXNzb3I4NQ"),
    ("router85processor85", "cm91dGVyODVwcm9jZXNzb3I4NQ"),
    ("router85reasoning85", "cm91dGVyODVyZWFzb25pbmc4NQ"),
    ("router85machine85", "cm91dGVyODVtYWNoaW5lODU"),
    ("router85learning85", "cm91dGVyODVsZWFybmluZzg1"),
    ("cluster85learning85", "Y2x1c3Rlcjg1bGVhcm5pbmc4NQ"),
    ("cluster85model85", "Y2x1c3Rlcjg1bW9kZWw4NQ"),
    ("cluster85token85", "Y2x1c3Rlcjg1dG9rZW44NQ"),
    ("cluster85prompt85", "Y2x1c3Rlcjg1cHJvbXB0ODU"),
    ("mirror85prompt85", "bWlycm9yODVwcm9tcHQ4NQ"),
    ("mirror85session85", "bWlycm9yODVzZXNzaW9uODU"),
    ("mirror85library85", "bWlycm9yODVsaWJyYXJ5ODU"),
    ("mirror85service85", "bWlycm9yODVzZXJ2aWNlODU"),
    ("filter85service85", "ZmlsdGVyODVzZXJ2aWNlODU"),
    ("filter85gateway85", "ZmlsdGVyODVnYXRld2F5ODU"),
    ("filter85storage85", "ZmlsdGVyODVzdG9yYWdlODU"),
    ("filter85network85", "ZmlsdGVyODVuZXR3b3JrODU"),
    ("ranking85network85", "cmFua2luZzg1bmV0d29yazg1"),
    ("ranking85latency85", "cmFua2luZzg1bGF0ZW5jeTg1"),
    ("ranking85buffer85", "cmFua2luZzg1YnVmZmVyODU"),
    ("ranking85queue85", "cmFua2luZzg1cXVldWU4NQ"),
    ("encoding85queue85", "ZW5jb2Rpbmc4NXF1ZXVlODU"),
    ("encoding85worker85", "ZW5jb2Rpbmc4NXdvcmtlcjg1"),
    ("encoding85kernel85", "ZW5jb2Rpbmc4NWtlcm5lbDg1"),
    ("encoding85signal85", "ZW5jb2Rpbmc4NXNpZ25hbDg1"),
    ("mapping85signal85", "bWFwcGluZzg1c2lnbmFsODU"),
    ("mapping85packet85", "bWFwcGluZzg1cGFja2V0ODU"),
    ("mapping85router85", "bWFwcGluZzg1cm91dGVyODU"),
    ("mapping85cluster85", "bWFwcGluZzg1Y2x1c3Rlcjg1"),
    ("record85cluster85", "cmVjb3JkODVjbHVzdGVyODU"),
    ("record85mirror85", "cmVjb3JkODVtaXJyb3I4NQ"),
    ("record85filter85", "cmVjb3JkODVmaWx0ZXI4NQ"),
    ("record85ranking85", "cmVjb3JkODVyYW5raW5nODU"),
    ("candle85ranking85", "Y2FuZGxlODVyYW5raW5nODU"),
    ("candle85encoding85", "Y2FuZGxlODVlbmNvZGluZzg1"),
    ("candle85mapping85", "Y2FuZGxlODVtYXBwaW5nODU"),
    ("candle85record85", "Y2FuZGxlODVyZWNvcmQ4NQ"),
    ("thread85record85", "dGhyZWFkODVyZWNvcmQ4NQ"),
    ("thread85candle85", "dGhyZWFkODVjYW5kbGU4NQ"),
    ("thread85thread85", "dGhyZWFkODV0aHJlYWQ4NQ"),
    ("thread85kitten85", "dGhyZWFkODVraXR0ZW44NQ"),
    (
        "round 85: the quick brown fox jumps over the lazy dog",
        "cm91bmQgODU6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 85: agentuniverse is a framework for multi agents",
        "cm91bmQgODU6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 85: knowledge stored as vectors enables retrieval",
        "cm91bmQgODU6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 85: the processor reads the record then stops",
        "cm91bmQgODU6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 85: a worker pulls the next task from the queue",
        "cm91bmQgODU6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 85: signals travel through the network layer",
        "cm91bmQgODU6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 85: the gateway routes each request by policy",
        "cm91bmQgODU6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 85: memory grows until the buffer is full",
        "cm91bmQgODU6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 85: the cluster mirrors every packet twice",
        "cm91bmQgODU6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 85: ranking uses tokens learned from the corpus",
        "cm91bmQgODU6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 85: a long session ends when the candle dies",
        "cm91bmQgODU6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 85: encode the prompt then map the result",
        "cm91bmQgODU6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 85: the kernel wakes the worker at dawn", "cm91bmQgODU6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 85: service latency drops after the patch",
        "cm91bmQgODU6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 85: the library caches every vector it sees",
        "cm91bmQgODU6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 85: agents argue then the debate resolves",
        "cm91bmQgODU6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 85: the filter keeps only strong matches",
        "cm91bmQgODU6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 85: the model answers with a short reply",
        "cm91bmQgODU6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 85: the recorder stores the reasoning trace",
        "cm91bmQgODU6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 85: the angel watches the processor run", "cm91bmQgODU6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 85: angle of the vector decides the match",
        "cm91bmQgODU6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 85: the candle burns twice as long at night",
        "cm91bmQgODU6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 85: a mirror of the universe in one line",
        "cm91bmQgODU6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 85: the queue drains before the storm", "cm91bmQgODU6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
