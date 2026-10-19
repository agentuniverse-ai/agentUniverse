"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten86kitten86", "a2l0dGVuODZraXR0ZW44Ng"),
    ("kitten86sitting86", "a2l0dGVuODZzaXR0aW5nODY"),
    ("kitten86agent86", "a2l0dGVuODZhZ2VudDg2"),
    ("kitten86angle86", "a2l0dGVuODZhbmdsZTg2"),
    ("sitting86angle86", "c2l0dGluZzg2YW5nbGU4Ng"),
    ("sitting86universe86", "c2l0dGluZzg2dW5pdmVyc2U4Ng"),
    ("sitting86memory86", "c2l0dGluZzg2bWVtb3J5ODY"),
    ("sitting86stream86", "c2l0dGluZzg2c3RyZWFtODY"),
    ("agent86stream86", "YWdlbnQ4NnN0cmVhbTg2"),
    ("agent86context86", "YWdlbnQ4NmNvbnRleHQ4Ng"),
    ("agent86knowledge86", "YWdlbnQ4Nmtub3dsZWRnZTg2"),
    ("agent86vector86", "YWdlbnQ4NnZlY3Rvcjg2"),
    ("angle86vector86", "YW5nbGU4NnZlY3Rvcjg2"),
    ("angle86processor86", "YW5nbGU4NnByb2Nlc3Nvcjg2"),
    ("angle86reasoning86", "YW5nbGU4NnJlYXNvbmluZzg2"),
    ("angle86machine86", "YW5nbGU4Nm1hY2hpbmU4Ng"),
    ("universe86machine86", "dW5pdmVyc2U4Nm1hY2hpbmU4Ng"),
    ("universe86learning86", "dW5pdmVyc2U4NmxlYXJuaW5nODY"),
    ("universe86model86", "dW5pdmVyc2U4Nm1vZGVsODY"),
    ("universe86token86", "dW5pdmVyc2U4NnRva2VuODY"),
    ("memory86token86", "bWVtb3J5ODZ0b2tlbjg2"),
    ("memory86prompt86", "bWVtb3J5ODZwcm9tcHQ4Ng"),
    ("memory86session86", "bWVtb3J5ODZzZXNzaW9uODY"),
    ("memory86library86", "bWVtb3J5ODZsaWJyYXJ5ODY"),
    ("stream86library86", "c3RyZWFtODZsaWJyYXJ5ODY"),
    ("stream86service86", "c3RyZWFtODZzZXJ2aWNlODY"),
    ("stream86gateway86", "c3RyZWFtODZnYXRld2F5ODY"),
    ("stream86storage86", "c3RyZWFtODZzdG9yYWdlODY"),
    ("context86storage86", "Y29udGV4dDg2c3RvcmFnZTg2"),
    ("context86network86", "Y29udGV4dDg2bmV0d29yazg2"),
    ("context86latency86", "Y29udGV4dDg2bGF0ZW5jeTg2"),
    ("context86buffer86", "Y29udGV4dDg2YnVmZmVyODY"),
    ("knowledge86buffer86", "a25vd2xlZGdlODZidWZmZXI4Ng"),
    ("knowledge86queue86", "a25vd2xlZGdlODZxdWV1ZTg2"),
    ("knowledge86worker86", "a25vd2xlZGdlODZ3b3JrZXI4Ng"),
    ("knowledge86kernel86", "a25vd2xlZGdlODZrZXJuZWw4Ng"),
    ("vector86kernel86", "dmVjdG9yODZrZXJuZWw4Ng"),
    ("vector86signal86", "dmVjdG9yODZzaWduYWw4Ng"),
    ("vector86packet86", "dmVjdG9yODZwYWNrZXQ4Ng"),
    ("vector86router86", "dmVjdG9yODZyb3V0ZXI4Ng"),
    ("processor86router86", "cHJvY2Vzc29yODZyb3V0ZXI4Ng"),
    ("processor86cluster86", "cHJvY2Vzc29yODZjbHVzdGVyODY"),
    ("processor86mirror86", "cHJvY2Vzc29yODZtaXJyb3I4Ng"),
    ("processor86filter86", "cHJvY2Vzc29yODZmaWx0ZXI4Ng"),
    ("reasoning86filter86", "cmVhc29uaW5nODZmaWx0ZXI4Ng"),
    ("reasoning86ranking86", "cmVhc29uaW5nODZyYW5raW5nODY"),
    ("reasoning86encoding86", "cmVhc29uaW5nODZlbmNvZGluZzg2"),
    ("reasoning86mapping86", "cmVhc29uaW5nODZtYXBwaW5nODY"),
    ("machine86mapping86", "bWFjaGluZTg2bWFwcGluZzg2"),
    ("machine86record86", "bWFjaGluZTg2cmVjb3JkODY"),
    ("machine86candle86", "bWFjaGluZTg2Y2FuZGxlODY"),
    ("machine86thread86", "bWFjaGluZTg2dGhyZWFkODY"),
    ("learning86thread86", "bGVhcm5pbmc4NnRocmVhZDg2"),
    ("learning86kitten86", "bGVhcm5pbmc4NmtpdHRlbjg2"),
    ("learning86sitting86", "bGVhcm5pbmc4NnNpdHRpbmc4Ng"),
    ("learning86agent86", "bGVhcm5pbmc4NmFnZW50ODY"),
    ("model86agent86", "bW9kZWw4NmFnZW50ODY"),
    ("model86angle86", "bW9kZWw4NmFuZ2xlODY"),
    ("model86universe86", "bW9kZWw4NnVuaXZlcnNlODY"),
    ("model86memory86", "bW9kZWw4Nm1lbW9yeTg2"),
    ("token86memory86", "dG9rZW44Nm1lbW9yeTg2"),
    ("token86stream86", "dG9rZW44NnN0cmVhbTg2"),
    ("token86context86", "dG9rZW44NmNvbnRleHQ4Ng"),
    ("token86knowledge86", "dG9rZW44Nmtub3dsZWRnZTg2"),
    ("prompt86knowledge86", "cHJvbXB0ODZrbm93bGVkZ2U4Ng"),
    ("prompt86vector86", "cHJvbXB0ODZ2ZWN0b3I4Ng"),
    ("prompt86processor86", "cHJvbXB0ODZwcm9jZXNzb3I4Ng"),
    ("prompt86reasoning86", "cHJvbXB0ODZyZWFzb25pbmc4Ng"),
    ("session86reasoning86", "c2Vzc2lvbjg2cmVhc29uaW5nODY"),
    ("session86machine86", "c2Vzc2lvbjg2bWFjaGluZTg2"),
    ("session86learning86", "c2Vzc2lvbjg2bGVhcm5pbmc4Ng"),
    ("session86model86", "c2Vzc2lvbjg2bW9kZWw4Ng"),
    ("library86model86", "bGlicmFyeTg2bW9kZWw4Ng"),
    ("library86token86", "bGlicmFyeTg2dG9rZW44Ng"),
    ("library86prompt86", "bGlicmFyeTg2cHJvbXB0ODY"),
    ("library86session86", "bGlicmFyeTg2c2Vzc2lvbjg2"),
    ("service86session86", "c2VydmljZTg2c2Vzc2lvbjg2"),
    ("service86library86", "c2VydmljZTg2bGlicmFyeTg2"),
    ("service86service86", "c2VydmljZTg2c2VydmljZTg2"),
    ("service86gateway86", "c2VydmljZTg2Z2F0ZXdheTg2"),
    ("gateway86gateway86", "Z2F0ZXdheTg2Z2F0ZXdheTg2"),
    ("gateway86storage86", "Z2F0ZXdheTg2c3RvcmFnZTg2"),
    ("gateway86network86", "Z2F0ZXdheTg2bmV0d29yazg2"),
    ("gateway86latency86", "Z2F0ZXdheTg2bGF0ZW5jeTg2"),
    ("storage86latency86", "c3RvcmFnZTg2bGF0ZW5jeTg2"),
    ("storage86buffer86", "c3RvcmFnZTg2YnVmZmVyODY"),
    ("storage86queue86", "c3RvcmFnZTg2cXVldWU4Ng"),
    ("storage86worker86", "c3RvcmFnZTg2d29ya2VyODY"),
    ("network86worker86", "bmV0d29yazg2d29ya2VyODY"),
    ("network86kernel86", "bmV0d29yazg2a2VybmVsODY"),
    ("network86signal86", "bmV0d29yazg2c2lnbmFsODY"),
    ("network86packet86", "bmV0d29yazg2cGFja2V0ODY"),
    ("latency86packet86", "bGF0ZW5jeTg2cGFja2V0ODY"),
    ("latency86router86", "bGF0ZW5jeTg2cm91dGVyODY"),
    ("latency86cluster86", "bGF0ZW5jeTg2Y2x1c3Rlcjg2"),
    ("latency86mirror86", "bGF0ZW5jeTg2bWlycm9yODY"),
    ("buffer86mirror86", "YnVmZmVyODZtaXJyb3I4Ng"),
    ("buffer86filter86", "YnVmZmVyODZmaWx0ZXI4Ng"),
    ("buffer86ranking86", "YnVmZmVyODZyYW5raW5nODY"),
    ("buffer86encoding86", "YnVmZmVyODZlbmNvZGluZzg2"),
    ("queue86encoding86", "cXVldWU4NmVuY29kaW5nODY"),
    ("queue86mapping86", "cXVldWU4Nm1hcHBpbmc4Ng"),
    ("queue86record86", "cXVldWU4NnJlY29yZDg2"),
    ("queue86candle86", "cXVldWU4NmNhbmRsZTg2"),
    ("worker86candle86", "d29ya2VyODZjYW5kbGU4Ng"),
    ("worker86thread86", "d29ya2VyODZ0aHJlYWQ4Ng"),
    ("worker86kitten86", "d29ya2VyODZraXR0ZW44Ng"),
    ("worker86sitting86", "d29ya2VyODZzaXR0aW5nODY"),
    ("kernel86sitting86", "a2VybmVsODZzaXR0aW5nODY"),
    ("kernel86agent86", "a2VybmVsODZhZ2VudDg2"),
    ("kernel86angle86", "a2VybmVsODZhbmdsZTg2"),
    ("kernel86universe86", "a2VybmVsODZ1bml2ZXJzZTg2"),
    ("signal86universe86", "c2lnbmFsODZ1bml2ZXJzZTg2"),
    ("signal86memory86", "c2lnbmFsODZtZW1vcnk4Ng"),
    ("signal86stream86", "c2lnbmFsODZzdHJlYW04Ng"),
    ("signal86context86", "c2lnbmFsODZjb250ZXh0ODY"),
    ("packet86context86", "cGFja2V0ODZjb250ZXh0ODY"),
    ("packet86knowledge86", "cGFja2V0ODZrbm93bGVkZ2U4Ng"),
    ("packet86vector86", "cGFja2V0ODZ2ZWN0b3I4Ng"),
    ("packet86processor86", "cGFja2V0ODZwcm9jZXNzb3I4Ng"),
    ("router86processor86", "cm91dGVyODZwcm9jZXNzb3I4Ng"),
    ("router86reasoning86", "cm91dGVyODZyZWFzb25pbmc4Ng"),
    ("router86machine86", "cm91dGVyODZtYWNoaW5lODY"),
    ("router86learning86", "cm91dGVyODZsZWFybmluZzg2"),
    ("cluster86learning86", "Y2x1c3Rlcjg2bGVhcm5pbmc4Ng"),
    ("cluster86model86", "Y2x1c3Rlcjg2bW9kZWw4Ng"),
    ("cluster86token86", "Y2x1c3Rlcjg2dG9rZW44Ng"),
    ("cluster86prompt86", "Y2x1c3Rlcjg2cHJvbXB0ODY"),
    ("mirror86prompt86", "bWlycm9yODZwcm9tcHQ4Ng"),
    ("mirror86session86", "bWlycm9yODZzZXNzaW9uODY"),
    ("mirror86library86", "bWlycm9yODZsaWJyYXJ5ODY"),
    ("mirror86service86", "bWlycm9yODZzZXJ2aWNlODY"),
    ("filter86service86", "ZmlsdGVyODZzZXJ2aWNlODY"),
    ("filter86gateway86", "ZmlsdGVyODZnYXRld2F5ODY"),
    ("filter86storage86", "ZmlsdGVyODZzdG9yYWdlODY"),
    ("filter86network86", "ZmlsdGVyODZuZXR3b3JrODY"),
    ("ranking86network86", "cmFua2luZzg2bmV0d29yazg2"),
    ("ranking86latency86", "cmFua2luZzg2bGF0ZW5jeTg2"),
    ("ranking86buffer86", "cmFua2luZzg2YnVmZmVyODY"),
    ("ranking86queue86", "cmFua2luZzg2cXVldWU4Ng"),
    ("encoding86queue86", "ZW5jb2Rpbmc4NnF1ZXVlODY"),
    ("encoding86worker86", "ZW5jb2Rpbmc4Nndvcmtlcjg2"),
    ("encoding86kernel86", "ZW5jb2Rpbmc4Nmtlcm5lbDg2"),
    ("encoding86signal86", "ZW5jb2Rpbmc4NnNpZ25hbDg2"),
    ("mapping86signal86", "bWFwcGluZzg2c2lnbmFsODY"),
    ("mapping86packet86", "bWFwcGluZzg2cGFja2V0ODY"),
    ("mapping86router86", "bWFwcGluZzg2cm91dGVyODY"),
    ("mapping86cluster86", "bWFwcGluZzg2Y2x1c3Rlcjg2"),
    ("record86cluster86", "cmVjb3JkODZjbHVzdGVyODY"),
    ("record86mirror86", "cmVjb3JkODZtaXJyb3I4Ng"),
    ("record86filter86", "cmVjb3JkODZmaWx0ZXI4Ng"),
    ("record86ranking86", "cmVjb3JkODZyYW5raW5nODY"),
    ("candle86ranking86", "Y2FuZGxlODZyYW5raW5nODY"),
    ("candle86encoding86", "Y2FuZGxlODZlbmNvZGluZzg2"),
    ("candle86mapping86", "Y2FuZGxlODZtYXBwaW5nODY"),
    ("candle86record86", "Y2FuZGxlODZyZWNvcmQ4Ng"),
    ("thread86record86", "dGhyZWFkODZyZWNvcmQ4Ng"),
    ("thread86candle86", "dGhyZWFkODZjYW5kbGU4Ng"),
    ("thread86thread86", "dGhyZWFkODZ0aHJlYWQ4Ng"),
    ("thread86kitten86", "dGhyZWFkODZraXR0ZW44Ng"),
    (
        "round 86: the quick brown fox jumps over the lazy dog",
        "cm91bmQgODY6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 86: agentuniverse is a framework for multi agents",
        "cm91bmQgODY6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 86: knowledge stored as vectors enables retrieval",
        "cm91bmQgODY6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 86: the processor reads the record then stops",
        "cm91bmQgODY6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 86: a worker pulls the next task from the queue",
        "cm91bmQgODY6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 86: signals travel through the network layer",
        "cm91bmQgODY6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 86: the gateway routes each request by policy",
        "cm91bmQgODY6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 86: memory grows until the buffer is full",
        "cm91bmQgODY6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 86: the cluster mirrors every packet twice",
        "cm91bmQgODY6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 86: ranking uses tokens learned from the corpus",
        "cm91bmQgODY6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 86: a long session ends when the candle dies",
        "cm91bmQgODY6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 86: encode the prompt then map the result",
        "cm91bmQgODY6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 86: the kernel wakes the worker at dawn", "cm91bmQgODY6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 86: service latency drops after the patch",
        "cm91bmQgODY6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 86: the library caches every vector it sees",
        "cm91bmQgODY6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 86: agents argue then the debate resolves",
        "cm91bmQgODY6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 86: the filter keeps only strong matches",
        "cm91bmQgODY6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 86: the model answers with a short reply",
        "cm91bmQgODY6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 86: the recorder stores the reasoning trace",
        "cm91bmQgODY6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 86: the angel watches the processor run", "cm91bmQgODY6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 86: angle of the vector decides the match",
        "cm91bmQgODY6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 86: the candle burns twice as long at night",
        "cm91bmQgODY6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 86: a mirror of the universe in one line",
        "cm91bmQgODY6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 86: the queue drains before the storm", "cm91bmQgODY6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
