"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten24kitten24", "a2l0dGVuMjRraXR0ZW4yNA"),
    ("kitten24sitting24", "a2l0dGVuMjRzaXR0aW5nMjQ"),
    ("kitten24agent24", "a2l0dGVuMjRhZ2VudDI0"),
    ("kitten24angle24", "a2l0dGVuMjRhbmdsZTI0"),
    ("sitting24angle24", "c2l0dGluZzI0YW5nbGUyNA"),
    ("sitting24universe24", "c2l0dGluZzI0dW5pdmVyc2UyNA"),
    ("sitting24memory24", "c2l0dGluZzI0bWVtb3J5MjQ"),
    ("sitting24stream24", "c2l0dGluZzI0c3RyZWFtMjQ"),
    ("agent24stream24", "YWdlbnQyNHN0cmVhbTI0"),
    ("agent24context24", "YWdlbnQyNGNvbnRleHQyNA"),
    ("agent24knowledge24", "YWdlbnQyNGtub3dsZWRnZTI0"),
    ("agent24vector24", "YWdlbnQyNHZlY3RvcjI0"),
    ("angle24vector24", "YW5nbGUyNHZlY3RvcjI0"),
    ("angle24processor24", "YW5nbGUyNHByb2Nlc3NvcjI0"),
    ("angle24reasoning24", "YW5nbGUyNHJlYXNvbmluZzI0"),
    ("angle24machine24", "YW5nbGUyNG1hY2hpbmUyNA"),
    ("universe24machine24", "dW5pdmVyc2UyNG1hY2hpbmUyNA"),
    ("universe24learning24", "dW5pdmVyc2UyNGxlYXJuaW5nMjQ"),
    ("universe24model24", "dW5pdmVyc2UyNG1vZGVsMjQ"),
    ("universe24token24", "dW5pdmVyc2UyNHRva2VuMjQ"),
    ("memory24token24", "bWVtb3J5MjR0b2tlbjI0"),
    ("memory24prompt24", "bWVtb3J5MjRwcm9tcHQyNA"),
    ("memory24session24", "bWVtb3J5MjRzZXNzaW9uMjQ"),
    ("memory24library24", "bWVtb3J5MjRsaWJyYXJ5MjQ"),
    ("stream24library24", "c3RyZWFtMjRsaWJyYXJ5MjQ"),
    ("stream24service24", "c3RyZWFtMjRzZXJ2aWNlMjQ"),
    ("stream24gateway24", "c3RyZWFtMjRnYXRld2F5MjQ"),
    ("stream24storage24", "c3RyZWFtMjRzdG9yYWdlMjQ"),
    ("context24storage24", "Y29udGV4dDI0c3RvcmFnZTI0"),
    ("context24network24", "Y29udGV4dDI0bmV0d29yazI0"),
    ("context24latency24", "Y29udGV4dDI0bGF0ZW5jeTI0"),
    ("context24buffer24", "Y29udGV4dDI0YnVmZmVyMjQ"),
    ("knowledge24buffer24", "a25vd2xlZGdlMjRidWZmZXIyNA"),
    ("knowledge24queue24", "a25vd2xlZGdlMjRxdWV1ZTI0"),
    ("knowledge24worker24", "a25vd2xlZGdlMjR3b3JrZXIyNA"),
    ("knowledge24kernel24", "a25vd2xlZGdlMjRrZXJuZWwyNA"),
    ("vector24kernel24", "dmVjdG9yMjRrZXJuZWwyNA"),
    ("vector24signal24", "dmVjdG9yMjRzaWduYWwyNA"),
    ("vector24packet24", "dmVjdG9yMjRwYWNrZXQyNA"),
    ("vector24router24", "dmVjdG9yMjRyb3V0ZXIyNA"),
    ("processor24router24", "cHJvY2Vzc29yMjRyb3V0ZXIyNA"),
    ("processor24cluster24", "cHJvY2Vzc29yMjRjbHVzdGVyMjQ"),
    ("processor24mirror24", "cHJvY2Vzc29yMjRtaXJyb3IyNA"),
    ("processor24filter24", "cHJvY2Vzc29yMjRmaWx0ZXIyNA"),
    ("reasoning24filter24", "cmVhc29uaW5nMjRmaWx0ZXIyNA"),
    ("reasoning24ranking24", "cmVhc29uaW5nMjRyYW5raW5nMjQ"),
    ("reasoning24encoding24", "cmVhc29uaW5nMjRlbmNvZGluZzI0"),
    ("reasoning24mapping24", "cmVhc29uaW5nMjRtYXBwaW5nMjQ"),
    ("machine24mapping24", "bWFjaGluZTI0bWFwcGluZzI0"),
    ("machine24record24", "bWFjaGluZTI0cmVjb3JkMjQ"),
    ("machine24candle24", "bWFjaGluZTI0Y2FuZGxlMjQ"),
    ("machine24thread24", "bWFjaGluZTI0dGhyZWFkMjQ"),
    ("learning24thread24", "bGVhcm5pbmcyNHRocmVhZDI0"),
    ("learning24kitten24", "bGVhcm5pbmcyNGtpdHRlbjI0"),
    ("learning24sitting24", "bGVhcm5pbmcyNHNpdHRpbmcyNA"),
    ("learning24agent24", "bGVhcm5pbmcyNGFnZW50MjQ"),
    ("model24agent24", "bW9kZWwyNGFnZW50MjQ"),
    ("model24angle24", "bW9kZWwyNGFuZ2xlMjQ"),
    ("model24universe24", "bW9kZWwyNHVuaXZlcnNlMjQ"),
    ("model24memory24", "bW9kZWwyNG1lbW9yeTI0"),
    ("token24memory24", "dG9rZW4yNG1lbW9yeTI0"),
    ("token24stream24", "dG9rZW4yNHN0cmVhbTI0"),
    ("token24context24", "dG9rZW4yNGNvbnRleHQyNA"),
    ("token24knowledge24", "dG9rZW4yNGtub3dsZWRnZTI0"),
    ("prompt24knowledge24", "cHJvbXB0MjRrbm93bGVkZ2UyNA"),
    ("prompt24vector24", "cHJvbXB0MjR2ZWN0b3IyNA"),
    ("prompt24processor24", "cHJvbXB0MjRwcm9jZXNzb3IyNA"),
    ("prompt24reasoning24", "cHJvbXB0MjRyZWFzb25pbmcyNA"),
    ("session24reasoning24", "c2Vzc2lvbjI0cmVhc29uaW5nMjQ"),
    ("session24machine24", "c2Vzc2lvbjI0bWFjaGluZTI0"),
    ("session24learning24", "c2Vzc2lvbjI0bGVhcm5pbmcyNA"),
    ("session24model24", "c2Vzc2lvbjI0bW9kZWwyNA"),
    ("library24model24", "bGlicmFyeTI0bW9kZWwyNA"),
    ("library24token24", "bGlicmFyeTI0dG9rZW4yNA"),
    ("library24prompt24", "bGlicmFyeTI0cHJvbXB0MjQ"),
    ("library24session24", "bGlicmFyeTI0c2Vzc2lvbjI0"),
    ("service24session24", "c2VydmljZTI0c2Vzc2lvbjI0"),
    ("service24library24", "c2VydmljZTI0bGlicmFyeTI0"),
    ("service24service24", "c2VydmljZTI0c2VydmljZTI0"),
    ("service24gateway24", "c2VydmljZTI0Z2F0ZXdheTI0"),
    ("gateway24gateway24", "Z2F0ZXdheTI0Z2F0ZXdheTI0"),
    ("gateway24storage24", "Z2F0ZXdheTI0c3RvcmFnZTI0"),
    ("gateway24network24", "Z2F0ZXdheTI0bmV0d29yazI0"),
    ("gateway24latency24", "Z2F0ZXdheTI0bGF0ZW5jeTI0"),
    ("storage24latency24", "c3RvcmFnZTI0bGF0ZW5jeTI0"),
    ("storage24buffer24", "c3RvcmFnZTI0YnVmZmVyMjQ"),
    ("storage24queue24", "c3RvcmFnZTI0cXVldWUyNA"),
    ("storage24worker24", "c3RvcmFnZTI0d29ya2VyMjQ"),
    ("network24worker24", "bmV0d29yazI0d29ya2VyMjQ"),
    ("network24kernel24", "bmV0d29yazI0a2VybmVsMjQ"),
    ("network24signal24", "bmV0d29yazI0c2lnbmFsMjQ"),
    ("network24packet24", "bmV0d29yazI0cGFja2V0MjQ"),
    ("latency24packet24", "bGF0ZW5jeTI0cGFja2V0MjQ"),
    ("latency24router24", "bGF0ZW5jeTI0cm91dGVyMjQ"),
    ("latency24cluster24", "bGF0ZW5jeTI0Y2x1c3RlcjI0"),
    ("latency24mirror24", "bGF0ZW5jeTI0bWlycm9yMjQ"),
    ("buffer24mirror24", "YnVmZmVyMjRtaXJyb3IyNA"),
    ("buffer24filter24", "YnVmZmVyMjRmaWx0ZXIyNA"),
    ("buffer24ranking24", "YnVmZmVyMjRyYW5raW5nMjQ"),
    ("buffer24encoding24", "YnVmZmVyMjRlbmNvZGluZzI0"),
    ("queue24encoding24", "cXVldWUyNGVuY29kaW5nMjQ"),
    ("queue24mapping24", "cXVldWUyNG1hcHBpbmcyNA"),
    ("queue24record24", "cXVldWUyNHJlY29yZDI0"),
    ("queue24candle24", "cXVldWUyNGNhbmRsZTI0"),
    ("worker24candle24", "d29ya2VyMjRjYW5kbGUyNA"),
    ("worker24thread24", "d29ya2VyMjR0aHJlYWQyNA"),
    ("worker24kitten24", "d29ya2VyMjRraXR0ZW4yNA"),
    ("worker24sitting24", "d29ya2VyMjRzaXR0aW5nMjQ"),
    ("kernel24sitting24", "a2VybmVsMjRzaXR0aW5nMjQ"),
    ("kernel24agent24", "a2VybmVsMjRhZ2VudDI0"),
    ("kernel24angle24", "a2VybmVsMjRhbmdsZTI0"),
    ("kernel24universe24", "a2VybmVsMjR1bml2ZXJzZTI0"),
    ("signal24universe24", "c2lnbmFsMjR1bml2ZXJzZTI0"),
    ("signal24memory24", "c2lnbmFsMjRtZW1vcnkyNA"),
    ("signal24stream24", "c2lnbmFsMjRzdHJlYW0yNA"),
    ("signal24context24", "c2lnbmFsMjRjb250ZXh0MjQ"),
    ("packet24context24", "cGFja2V0MjRjb250ZXh0MjQ"),
    ("packet24knowledge24", "cGFja2V0MjRrbm93bGVkZ2UyNA"),
    ("packet24vector24", "cGFja2V0MjR2ZWN0b3IyNA"),
    ("packet24processor24", "cGFja2V0MjRwcm9jZXNzb3IyNA"),
    ("router24processor24", "cm91dGVyMjRwcm9jZXNzb3IyNA"),
    ("router24reasoning24", "cm91dGVyMjRyZWFzb25pbmcyNA"),
    ("router24machine24", "cm91dGVyMjRtYWNoaW5lMjQ"),
    ("router24learning24", "cm91dGVyMjRsZWFybmluZzI0"),
    ("cluster24learning24", "Y2x1c3RlcjI0bGVhcm5pbmcyNA"),
    ("cluster24model24", "Y2x1c3RlcjI0bW9kZWwyNA"),
    ("cluster24token24", "Y2x1c3RlcjI0dG9rZW4yNA"),
    ("cluster24prompt24", "Y2x1c3RlcjI0cHJvbXB0MjQ"),
    ("mirror24prompt24", "bWlycm9yMjRwcm9tcHQyNA"),
    ("mirror24session24", "bWlycm9yMjRzZXNzaW9uMjQ"),
    ("mirror24library24", "bWlycm9yMjRsaWJyYXJ5MjQ"),
    ("mirror24service24", "bWlycm9yMjRzZXJ2aWNlMjQ"),
    ("filter24service24", "ZmlsdGVyMjRzZXJ2aWNlMjQ"),
    ("filter24gateway24", "ZmlsdGVyMjRnYXRld2F5MjQ"),
    ("filter24storage24", "ZmlsdGVyMjRzdG9yYWdlMjQ"),
    ("filter24network24", "ZmlsdGVyMjRuZXR3b3JrMjQ"),
    ("ranking24network24", "cmFua2luZzI0bmV0d29yazI0"),
    ("ranking24latency24", "cmFua2luZzI0bGF0ZW5jeTI0"),
    ("ranking24buffer24", "cmFua2luZzI0YnVmZmVyMjQ"),
    ("ranking24queue24", "cmFua2luZzI0cXVldWUyNA"),
    ("encoding24queue24", "ZW5jb2RpbmcyNHF1ZXVlMjQ"),
    ("encoding24worker24", "ZW5jb2RpbmcyNHdvcmtlcjI0"),
    ("encoding24kernel24", "ZW5jb2RpbmcyNGtlcm5lbDI0"),
    ("encoding24signal24", "ZW5jb2RpbmcyNHNpZ25hbDI0"),
    ("mapping24signal24", "bWFwcGluZzI0c2lnbmFsMjQ"),
    ("mapping24packet24", "bWFwcGluZzI0cGFja2V0MjQ"),
    ("mapping24router24", "bWFwcGluZzI0cm91dGVyMjQ"),
    ("mapping24cluster24", "bWFwcGluZzI0Y2x1c3RlcjI0"),
    ("record24cluster24", "cmVjb3JkMjRjbHVzdGVyMjQ"),
    ("record24mirror24", "cmVjb3JkMjRtaXJyb3IyNA"),
    ("record24filter24", "cmVjb3JkMjRmaWx0ZXIyNA"),
    ("record24ranking24", "cmVjb3JkMjRyYW5raW5nMjQ"),
    ("candle24ranking24", "Y2FuZGxlMjRyYW5raW5nMjQ"),
    ("candle24encoding24", "Y2FuZGxlMjRlbmNvZGluZzI0"),
    ("candle24mapping24", "Y2FuZGxlMjRtYXBwaW5nMjQ"),
    ("candle24record24", "Y2FuZGxlMjRyZWNvcmQyNA"),
    ("thread24record24", "dGhyZWFkMjRyZWNvcmQyNA"),
    ("thread24candle24", "dGhyZWFkMjRjYW5kbGUyNA"),
    ("thread24thread24", "dGhyZWFkMjR0aHJlYWQyNA"),
    ("thread24kitten24", "dGhyZWFkMjRraXR0ZW4yNA"),
    (
        "round 24: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMjQ6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 24: agentuniverse is a framework for multi agents",
        "cm91bmQgMjQ6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 24: knowledge stored as vectors enables retrieval",
        "cm91bmQgMjQ6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 24: the processor reads the record then stops",
        "cm91bmQgMjQ6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 24: a worker pulls the next task from the queue",
        "cm91bmQgMjQ6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 24: signals travel through the network layer",
        "cm91bmQgMjQ6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 24: the gateway routes each request by policy",
        "cm91bmQgMjQ6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 24: memory grows until the buffer is full",
        "cm91bmQgMjQ6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 24: the cluster mirrors every packet twice",
        "cm91bmQgMjQ6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 24: ranking uses tokens learned from the corpus",
        "cm91bmQgMjQ6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 24: a long session ends when the candle dies",
        "cm91bmQgMjQ6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 24: encode the prompt then map the result",
        "cm91bmQgMjQ6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 24: the kernel wakes the worker at dawn", "cm91bmQgMjQ6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 24: service latency drops after the patch",
        "cm91bmQgMjQ6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 24: the library caches every vector it sees",
        "cm91bmQgMjQ6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 24: agents argue then the debate resolves",
        "cm91bmQgMjQ6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 24: the filter keeps only strong matches",
        "cm91bmQgMjQ6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 24: the model answers with a short reply",
        "cm91bmQgMjQ6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 24: the recorder stores the reasoning trace",
        "cm91bmQgMjQ6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 24: the angel watches the processor run", "cm91bmQgMjQ6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 24: angle of the vector decides the match",
        "cm91bmQgMjQ6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 24: the candle burns twice as long at night",
        "cm91bmQgMjQ6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 24: a mirror of the universe in one line",
        "cm91bmQgMjQ6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 24: the queue drains before the storm", "cm91bmQgMjQ6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
