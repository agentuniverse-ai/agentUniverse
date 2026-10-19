"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten47kitten47", "a2l0dGVuNDdraXR0ZW40Nw"),
    ("kitten47sitting47", "a2l0dGVuNDdzaXR0aW5nNDc"),
    ("kitten47agent47", "a2l0dGVuNDdhZ2VudDQ3"),
    ("kitten47angle47", "a2l0dGVuNDdhbmdsZTQ3"),
    ("sitting47angle47", "c2l0dGluZzQ3YW5nbGU0Nw"),
    ("sitting47universe47", "c2l0dGluZzQ3dW5pdmVyc2U0Nw"),
    ("sitting47memory47", "c2l0dGluZzQ3bWVtb3J5NDc"),
    ("sitting47stream47", "c2l0dGluZzQ3c3RyZWFtNDc"),
    ("agent47stream47", "YWdlbnQ0N3N0cmVhbTQ3"),
    ("agent47context47", "YWdlbnQ0N2NvbnRleHQ0Nw"),
    ("agent47knowledge47", "YWdlbnQ0N2tub3dsZWRnZTQ3"),
    ("agent47vector47", "YWdlbnQ0N3ZlY3RvcjQ3"),
    ("angle47vector47", "YW5nbGU0N3ZlY3RvcjQ3"),
    ("angle47processor47", "YW5nbGU0N3Byb2Nlc3NvcjQ3"),
    ("angle47reasoning47", "YW5nbGU0N3JlYXNvbmluZzQ3"),
    ("angle47machine47", "YW5nbGU0N21hY2hpbmU0Nw"),
    ("universe47machine47", "dW5pdmVyc2U0N21hY2hpbmU0Nw"),
    ("universe47learning47", "dW5pdmVyc2U0N2xlYXJuaW5nNDc"),
    ("universe47model47", "dW5pdmVyc2U0N21vZGVsNDc"),
    ("universe47token47", "dW5pdmVyc2U0N3Rva2VuNDc"),
    ("memory47token47", "bWVtb3J5NDd0b2tlbjQ3"),
    ("memory47prompt47", "bWVtb3J5NDdwcm9tcHQ0Nw"),
    ("memory47session47", "bWVtb3J5NDdzZXNzaW9uNDc"),
    ("memory47library47", "bWVtb3J5NDdsaWJyYXJ5NDc"),
    ("stream47library47", "c3RyZWFtNDdsaWJyYXJ5NDc"),
    ("stream47service47", "c3RyZWFtNDdzZXJ2aWNlNDc"),
    ("stream47gateway47", "c3RyZWFtNDdnYXRld2F5NDc"),
    ("stream47storage47", "c3RyZWFtNDdzdG9yYWdlNDc"),
    ("context47storage47", "Y29udGV4dDQ3c3RvcmFnZTQ3"),
    ("context47network47", "Y29udGV4dDQ3bmV0d29yazQ3"),
    ("context47latency47", "Y29udGV4dDQ3bGF0ZW5jeTQ3"),
    ("context47buffer47", "Y29udGV4dDQ3YnVmZmVyNDc"),
    ("knowledge47buffer47", "a25vd2xlZGdlNDdidWZmZXI0Nw"),
    ("knowledge47queue47", "a25vd2xlZGdlNDdxdWV1ZTQ3"),
    ("knowledge47worker47", "a25vd2xlZGdlNDd3b3JrZXI0Nw"),
    ("knowledge47kernel47", "a25vd2xlZGdlNDdrZXJuZWw0Nw"),
    ("vector47kernel47", "dmVjdG9yNDdrZXJuZWw0Nw"),
    ("vector47signal47", "dmVjdG9yNDdzaWduYWw0Nw"),
    ("vector47packet47", "dmVjdG9yNDdwYWNrZXQ0Nw"),
    ("vector47router47", "dmVjdG9yNDdyb3V0ZXI0Nw"),
    ("processor47router47", "cHJvY2Vzc29yNDdyb3V0ZXI0Nw"),
    ("processor47cluster47", "cHJvY2Vzc29yNDdjbHVzdGVyNDc"),
    ("processor47mirror47", "cHJvY2Vzc29yNDdtaXJyb3I0Nw"),
    ("processor47filter47", "cHJvY2Vzc29yNDdmaWx0ZXI0Nw"),
    ("reasoning47filter47", "cmVhc29uaW5nNDdmaWx0ZXI0Nw"),
    ("reasoning47ranking47", "cmVhc29uaW5nNDdyYW5raW5nNDc"),
    ("reasoning47encoding47", "cmVhc29uaW5nNDdlbmNvZGluZzQ3"),
    ("reasoning47mapping47", "cmVhc29uaW5nNDdtYXBwaW5nNDc"),
    ("machine47mapping47", "bWFjaGluZTQ3bWFwcGluZzQ3"),
    ("machine47record47", "bWFjaGluZTQ3cmVjb3JkNDc"),
    ("machine47candle47", "bWFjaGluZTQ3Y2FuZGxlNDc"),
    ("machine47thread47", "bWFjaGluZTQ3dGhyZWFkNDc"),
    ("learning47thread47", "bGVhcm5pbmc0N3RocmVhZDQ3"),
    ("learning47kitten47", "bGVhcm5pbmc0N2tpdHRlbjQ3"),
    ("learning47sitting47", "bGVhcm5pbmc0N3NpdHRpbmc0Nw"),
    ("learning47agent47", "bGVhcm5pbmc0N2FnZW50NDc"),
    ("model47agent47", "bW9kZWw0N2FnZW50NDc"),
    ("model47angle47", "bW9kZWw0N2FuZ2xlNDc"),
    ("model47universe47", "bW9kZWw0N3VuaXZlcnNlNDc"),
    ("model47memory47", "bW9kZWw0N21lbW9yeTQ3"),
    ("token47memory47", "dG9rZW40N21lbW9yeTQ3"),
    ("token47stream47", "dG9rZW40N3N0cmVhbTQ3"),
    ("token47context47", "dG9rZW40N2NvbnRleHQ0Nw"),
    ("token47knowledge47", "dG9rZW40N2tub3dsZWRnZTQ3"),
    ("prompt47knowledge47", "cHJvbXB0NDdrbm93bGVkZ2U0Nw"),
    ("prompt47vector47", "cHJvbXB0NDd2ZWN0b3I0Nw"),
    ("prompt47processor47", "cHJvbXB0NDdwcm9jZXNzb3I0Nw"),
    ("prompt47reasoning47", "cHJvbXB0NDdyZWFzb25pbmc0Nw"),
    ("session47reasoning47", "c2Vzc2lvbjQ3cmVhc29uaW5nNDc"),
    ("session47machine47", "c2Vzc2lvbjQ3bWFjaGluZTQ3"),
    ("session47learning47", "c2Vzc2lvbjQ3bGVhcm5pbmc0Nw"),
    ("session47model47", "c2Vzc2lvbjQ3bW9kZWw0Nw"),
    ("library47model47", "bGlicmFyeTQ3bW9kZWw0Nw"),
    ("library47token47", "bGlicmFyeTQ3dG9rZW40Nw"),
    ("library47prompt47", "bGlicmFyeTQ3cHJvbXB0NDc"),
    ("library47session47", "bGlicmFyeTQ3c2Vzc2lvbjQ3"),
    ("service47session47", "c2VydmljZTQ3c2Vzc2lvbjQ3"),
    ("service47library47", "c2VydmljZTQ3bGlicmFyeTQ3"),
    ("service47service47", "c2VydmljZTQ3c2VydmljZTQ3"),
    ("service47gateway47", "c2VydmljZTQ3Z2F0ZXdheTQ3"),
    ("gateway47gateway47", "Z2F0ZXdheTQ3Z2F0ZXdheTQ3"),
    ("gateway47storage47", "Z2F0ZXdheTQ3c3RvcmFnZTQ3"),
    ("gateway47network47", "Z2F0ZXdheTQ3bmV0d29yazQ3"),
    ("gateway47latency47", "Z2F0ZXdheTQ3bGF0ZW5jeTQ3"),
    ("storage47latency47", "c3RvcmFnZTQ3bGF0ZW5jeTQ3"),
    ("storage47buffer47", "c3RvcmFnZTQ3YnVmZmVyNDc"),
    ("storage47queue47", "c3RvcmFnZTQ3cXVldWU0Nw"),
    ("storage47worker47", "c3RvcmFnZTQ3d29ya2VyNDc"),
    ("network47worker47", "bmV0d29yazQ3d29ya2VyNDc"),
    ("network47kernel47", "bmV0d29yazQ3a2VybmVsNDc"),
    ("network47signal47", "bmV0d29yazQ3c2lnbmFsNDc"),
    ("network47packet47", "bmV0d29yazQ3cGFja2V0NDc"),
    ("latency47packet47", "bGF0ZW5jeTQ3cGFja2V0NDc"),
    ("latency47router47", "bGF0ZW5jeTQ3cm91dGVyNDc"),
    ("latency47cluster47", "bGF0ZW5jeTQ3Y2x1c3RlcjQ3"),
    ("latency47mirror47", "bGF0ZW5jeTQ3bWlycm9yNDc"),
    ("buffer47mirror47", "YnVmZmVyNDdtaXJyb3I0Nw"),
    ("buffer47filter47", "YnVmZmVyNDdmaWx0ZXI0Nw"),
    ("buffer47ranking47", "YnVmZmVyNDdyYW5raW5nNDc"),
    ("buffer47encoding47", "YnVmZmVyNDdlbmNvZGluZzQ3"),
    ("queue47encoding47", "cXVldWU0N2VuY29kaW5nNDc"),
    ("queue47mapping47", "cXVldWU0N21hcHBpbmc0Nw"),
    ("queue47record47", "cXVldWU0N3JlY29yZDQ3"),
    ("queue47candle47", "cXVldWU0N2NhbmRsZTQ3"),
    ("worker47candle47", "d29ya2VyNDdjYW5kbGU0Nw"),
    ("worker47thread47", "d29ya2VyNDd0aHJlYWQ0Nw"),
    ("worker47kitten47", "d29ya2VyNDdraXR0ZW40Nw"),
    ("worker47sitting47", "d29ya2VyNDdzaXR0aW5nNDc"),
    ("kernel47sitting47", "a2VybmVsNDdzaXR0aW5nNDc"),
    ("kernel47agent47", "a2VybmVsNDdhZ2VudDQ3"),
    ("kernel47angle47", "a2VybmVsNDdhbmdsZTQ3"),
    ("kernel47universe47", "a2VybmVsNDd1bml2ZXJzZTQ3"),
    ("signal47universe47", "c2lnbmFsNDd1bml2ZXJzZTQ3"),
    ("signal47memory47", "c2lnbmFsNDdtZW1vcnk0Nw"),
    ("signal47stream47", "c2lnbmFsNDdzdHJlYW00Nw"),
    ("signal47context47", "c2lnbmFsNDdjb250ZXh0NDc"),
    ("packet47context47", "cGFja2V0NDdjb250ZXh0NDc"),
    ("packet47knowledge47", "cGFja2V0NDdrbm93bGVkZ2U0Nw"),
    ("packet47vector47", "cGFja2V0NDd2ZWN0b3I0Nw"),
    ("packet47processor47", "cGFja2V0NDdwcm9jZXNzb3I0Nw"),
    ("router47processor47", "cm91dGVyNDdwcm9jZXNzb3I0Nw"),
    ("router47reasoning47", "cm91dGVyNDdyZWFzb25pbmc0Nw"),
    ("router47machine47", "cm91dGVyNDdtYWNoaW5lNDc"),
    ("router47learning47", "cm91dGVyNDdsZWFybmluZzQ3"),
    ("cluster47learning47", "Y2x1c3RlcjQ3bGVhcm5pbmc0Nw"),
    ("cluster47model47", "Y2x1c3RlcjQ3bW9kZWw0Nw"),
    ("cluster47token47", "Y2x1c3RlcjQ3dG9rZW40Nw"),
    ("cluster47prompt47", "Y2x1c3RlcjQ3cHJvbXB0NDc"),
    ("mirror47prompt47", "bWlycm9yNDdwcm9tcHQ0Nw"),
    ("mirror47session47", "bWlycm9yNDdzZXNzaW9uNDc"),
    ("mirror47library47", "bWlycm9yNDdsaWJyYXJ5NDc"),
    ("mirror47service47", "bWlycm9yNDdzZXJ2aWNlNDc"),
    ("filter47service47", "ZmlsdGVyNDdzZXJ2aWNlNDc"),
    ("filter47gateway47", "ZmlsdGVyNDdnYXRld2F5NDc"),
    ("filter47storage47", "ZmlsdGVyNDdzdG9yYWdlNDc"),
    ("filter47network47", "ZmlsdGVyNDduZXR3b3JrNDc"),
    ("ranking47network47", "cmFua2luZzQ3bmV0d29yazQ3"),
    ("ranking47latency47", "cmFua2luZzQ3bGF0ZW5jeTQ3"),
    ("ranking47buffer47", "cmFua2luZzQ3YnVmZmVyNDc"),
    ("ranking47queue47", "cmFua2luZzQ3cXVldWU0Nw"),
    ("encoding47queue47", "ZW5jb2Rpbmc0N3F1ZXVlNDc"),
    ("encoding47worker47", "ZW5jb2Rpbmc0N3dvcmtlcjQ3"),
    ("encoding47kernel47", "ZW5jb2Rpbmc0N2tlcm5lbDQ3"),
    ("encoding47signal47", "ZW5jb2Rpbmc0N3NpZ25hbDQ3"),
    ("mapping47signal47", "bWFwcGluZzQ3c2lnbmFsNDc"),
    ("mapping47packet47", "bWFwcGluZzQ3cGFja2V0NDc"),
    ("mapping47router47", "bWFwcGluZzQ3cm91dGVyNDc"),
    ("mapping47cluster47", "bWFwcGluZzQ3Y2x1c3RlcjQ3"),
    ("record47cluster47", "cmVjb3JkNDdjbHVzdGVyNDc"),
    ("record47mirror47", "cmVjb3JkNDdtaXJyb3I0Nw"),
    ("record47filter47", "cmVjb3JkNDdmaWx0ZXI0Nw"),
    ("record47ranking47", "cmVjb3JkNDdyYW5raW5nNDc"),
    ("candle47ranking47", "Y2FuZGxlNDdyYW5raW5nNDc"),
    ("candle47encoding47", "Y2FuZGxlNDdlbmNvZGluZzQ3"),
    ("candle47mapping47", "Y2FuZGxlNDdtYXBwaW5nNDc"),
    ("candle47record47", "Y2FuZGxlNDdyZWNvcmQ0Nw"),
    ("thread47record47", "dGhyZWFkNDdyZWNvcmQ0Nw"),
    ("thread47candle47", "dGhyZWFkNDdjYW5kbGU0Nw"),
    ("thread47thread47", "dGhyZWFkNDd0aHJlYWQ0Nw"),
    ("thread47kitten47", "dGhyZWFkNDdraXR0ZW40Nw"),
    (
        "round 47: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNDc6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 47: agentuniverse is a framework for multi agents",
        "cm91bmQgNDc6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 47: knowledge stored as vectors enables retrieval",
        "cm91bmQgNDc6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 47: the processor reads the record then stops",
        "cm91bmQgNDc6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 47: a worker pulls the next task from the queue",
        "cm91bmQgNDc6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 47: signals travel through the network layer",
        "cm91bmQgNDc6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 47: the gateway routes each request by policy",
        "cm91bmQgNDc6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 47: memory grows until the buffer is full",
        "cm91bmQgNDc6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 47: the cluster mirrors every packet twice",
        "cm91bmQgNDc6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 47: ranking uses tokens learned from the corpus",
        "cm91bmQgNDc6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 47: a long session ends when the candle dies",
        "cm91bmQgNDc6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 47: encode the prompt then map the result",
        "cm91bmQgNDc6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 47: the kernel wakes the worker at dawn", "cm91bmQgNDc6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 47: service latency drops after the patch",
        "cm91bmQgNDc6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 47: the library caches every vector it sees",
        "cm91bmQgNDc6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 47: agents argue then the debate resolves",
        "cm91bmQgNDc6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 47: the filter keeps only strong matches",
        "cm91bmQgNDc6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 47: the model answers with a short reply",
        "cm91bmQgNDc6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 47: the recorder stores the reasoning trace",
        "cm91bmQgNDc6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 47: the angel watches the processor run", "cm91bmQgNDc6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 47: angle of the vector decides the match",
        "cm91bmQgNDc6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 47: the candle burns twice as long at night",
        "cm91bmQgNDc6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 47: a mirror of the universe in one line",
        "cm91bmQgNDc6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 47: the queue drains before the storm", "cm91bmQgNDc6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
