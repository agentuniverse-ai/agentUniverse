"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten89kitten89", "a2l0dGVuODlraXR0ZW44OQ"),
    ("kitten89sitting89", "a2l0dGVuODlzaXR0aW5nODk"),
    ("kitten89agent89", "a2l0dGVuODlhZ2VudDg5"),
    ("kitten89angle89", "a2l0dGVuODlhbmdsZTg5"),
    ("sitting89angle89", "c2l0dGluZzg5YW5nbGU4OQ"),
    ("sitting89universe89", "c2l0dGluZzg5dW5pdmVyc2U4OQ"),
    ("sitting89memory89", "c2l0dGluZzg5bWVtb3J5ODk"),
    ("sitting89stream89", "c2l0dGluZzg5c3RyZWFtODk"),
    ("agent89stream89", "YWdlbnQ4OXN0cmVhbTg5"),
    ("agent89context89", "YWdlbnQ4OWNvbnRleHQ4OQ"),
    ("agent89knowledge89", "YWdlbnQ4OWtub3dsZWRnZTg5"),
    ("agent89vector89", "YWdlbnQ4OXZlY3Rvcjg5"),
    ("angle89vector89", "YW5nbGU4OXZlY3Rvcjg5"),
    ("angle89processor89", "YW5nbGU4OXByb2Nlc3Nvcjg5"),
    ("angle89reasoning89", "YW5nbGU4OXJlYXNvbmluZzg5"),
    ("angle89machine89", "YW5nbGU4OW1hY2hpbmU4OQ"),
    ("universe89machine89", "dW5pdmVyc2U4OW1hY2hpbmU4OQ"),
    ("universe89learning89", "dW5pdmVyc2U4OWxlYXJuaW5nODk"),
    ("universe89model89", "dW5pdmVyc2U4OW1vZGVsODk"),
    ("universe89token89", "dW5pdmVyc2U4OXRva2VuODk"),
    ("memory89token89", "bWVtb3J5ODl0b2tlbjg5"),
    ("memory89prompt89", "bWVtb3J5ODlwcm9tcHQ4OQ"),
    ("memory89session89", "bWVtb3J5ODlzZXNzaW9uODk"),
    ("memory89library89", "bWVtb3J5ODlsaWJyYXJ5ODk"),
    ("stream89library89", "c3RyZWFtODlsaWJyYXJ5ODk"),
    ("stream89service89", "c3RyZWFtODlzZXJ2aWNlODk"),
    ("stream89gateway89", "c3RyZWFtODlnYXRld2F5ODk"),
    ("stream89storage89", "c3RyZWFtODlzdG9yYWdlODk"),
    ("context89storage89", "Y29udGV4dDg5c3RvcmFnZTg5"),
    ("context89network89", "Y29udGV4dDg5bmV0d29yazg5"),
    ("context89latency89", "Y29udGV4dDg5bGF0ZW5jeTg5"),
    ("context89buffer89", "Y29udGV4dDg5YnVmZmVyODk"),
    ("knowledge89buffer89", "a25vd2xlZGdlODlidWZmZXI4OQ"),
    ("knowledge89queue89", "a25vd2xlZGdlODlxdWV1ZTg5"),
    ("knowledge89worker89", "a25vd2xlZGdlODl3b3JrZXI4OQ"),
    ("knowledge89kernel89", "a25vd2xlZGdlODlrZXJuZWw4OQ"),
    ("vector89kernel89", "dmVjdG9yODlrZXJuZWw4OQ"),
    ("vector89signal89", "dmVjdG9yODlzaWduYWw4OQ"),
    ("vector89packet89", "dmVjdG9yODlwYWNrZXQ4OQ"),
    ("vector89router89", "dmVjdG9yODlyb3V0ZXI4OQ"),
    ("processor89router89", "cHJvY2Vzc29yODlyb3V0ZXI4OQ"),
    ("processor89cluster89", "cHJvY2Vzc29yODljbHVzdGVyODk"),
    ("processor89mirror89", "cHJvY2Vzc29yODltaXJyb3I4OQ"),
    ("processor89filter89", "cHJvY2Vzc29yODlmaWx0ZXI4OQ"),
    ("reasoning89filter89", "cmVhc29uaW5nODlmaWx0ZXI4OQ"),
    ("reasoning89ranking89", "cmVhc29uaW5nODlyYW5raW5nODk"),
    ("reasoning89encoding89", "cmVhc29uaW5nODllbmNvZGluZzg5"),
    ("reasoning89mapping89", "cmVhc29uaW5nODltYXBwaW5nODk"),
    ("machine89mapping89", "bWFjaGluZTg5bWFwcGluZzg5"),
    ("machine89record89", "bWFjaGluZTg5cmVjb3JkODk"),
    ("machine89candle89", "bWFjaGluZTg5Y2FuZGxlODk"),
    ("machine89thread89", "bWFjaGluZTg5dGhyZWFkODk"),
    ("learning89thread89", "bGVhcm5pbmc4OXRocmVhZDg5"),
    ("learning89kitten89", "bGVhcm5pbmc4OWtpdHRlbjg5"),
    ("learning89sitting89", "bGVhcm5pbmc4OXNpdHRpbmc4OQ"),
    ("learning89agent89", "bGVhcm5pbmc4OWFnZW50ODk"),
    ("model89agent89", "bW9kZWw4OWFnZW50ODk"),
    ("model89angle89", "bW9kZWw4OWFuZ2xlODk"),
    ("model89universe89", "bW9kZWw4OXVuaXZlcnNlODk"),
    ("model89memory89", "bW9kZWw4OW1lbW9yeTg5"),
    ("token89memory89", "dG9rZW44OW1lbW9yeTg5"),
    ("token89stream89", "dG9rZW44OXN0cmVhbTg5"),
    ("token89context89", "dG9rZW44OWNvbnRleHQ4OQ"),
    ("token89knowledge89", "dG9rZW44OWtub3dsZWRnZTg5"),
    ("prompt89knowledge89", "cHJvbXB0ODlrbm93bGVkZ2U4OQ"),
    ("prompt89vector89", "cHJvbXB0ODl2ZWN0b3I4OQ"),
    ("prompt89processor89", "cHJvbXB0ODlwcm9jZXNzb3I4OQ"),
    ("prompt89reasoning89", "cHJvbXB0ODlyZWFzb25pbmc4OQ"),
    ("session89reasoning89", "c2Vzc2lvbjg5cmVhc29uaW5nODk"),
    ("session89machine89", "c2Vzc2lvbjg5bWFjaGluZTg5"),
    ("session89learning89", "c2Vzc2lvbjg5bGVhcm5pbmc4OQ"),
    ("session89model89", "c2Vzc2lvbjg5bW9kZWw4OQ"),
    ("library89model89", "bGlicmFyeTg5bW9kZWw4OQ"),
    ("library89token89", "bGlicmFyeTg5dG9rZW44OQ"),
    ("library89prompt89", "bGlicmFyeTg5cHJvbXB0ODk"),
    ("library89session89", "bGlicmFyeTg5c2Vzc2lvbjg5"),
    ("service89session89", "c2VydmljZTg5c2Vzc2lvbjg5"),
    ("service89library89", "c2VydmljZTg5bGlicmFyeTg5"),
    ("service89service89", "c2VydmljZTg5c2VydmljZTg5"),
    ("service89gateway89", "c2VydmljZTg5Z2F0ZXdheTg5"),
    ("gateway89gateway89", "Z2F0ZXdheTg5Z2F0ZXdheTg5"),
    ("gateway89storage89", "Z2F0ZXdheTg5c3RvcmFnZTg5"),
    ("gateway89network89", "Z2F0ZXdheTg5bmV0d29yazg5"),
    ("gateway89latency89", "Z2F0ZXdheTg5bGF0ZW5jeTg5"),
    ("storage89latency89", "c3RvcmFnZTg5bGF0ZW5jeTg5"),
    ("storage89buffer89", "c3RvcmFnZTg5YnVmZmVyODk"),
    ("storage89queue89", "c3RvcmFnZTg5cXVldWU4OQ"),
    ("storage89worker89", "c3RvcmFnZTg5d29ya2VyODk"),
    ("network89worker89", "bmV0d29yazg5d29ya2VyODk"),
    ("network89kernel89", "bmV0d29yazg5a2VybmVsODk"),
    ("network89signal89", "bmV0d29yazg5c2lnbmFsODk"),
    ("network89packet89", "bmV0d29yazg5cGFja2V0ODk"),
    ("latency89packet89", "bGF0ZW5jeTg5cGFja2V0ODk"),
    ("latency89router89", "bGF0ZW5jeTg5cm91dGVyODk"),
    ("latency89cluster89", "bGF0ZW5jeTg5Y2x1c3Rlcjg5"),
    ("latency89mirror89", "bGF0ZW5jeTg5bWlycm9yODk"),
    ("buffer89mirror89", "YnVmZmVyODltaXJyb3I4OQ"),
    ("buffer89filter89", "YnVmZmVyODlmaWx0ZXI4OQ"),
    ("buffer89ranking89", "YnVmZmVyODlyYW5raW5nODk"),
    ("buffer89encoding89", "YnVmZmVyODllbmNvZGluZzg5"),
    ("queue89encoding89", "cXVldWU4OWVuY29kaW5nODk"),
    ("queue89mapping89", "cXVldWU4OW1hcHBpbmc4OQ"),
    ("queue89record89", "cXVldWU4OXJlY29yZDg5"),
    ("queue89candle89", "cXVldWU4OWNhbmRsZTg5"),
    ("worker89candle89", "d29ya2VyODljYW5kbGU4OQ"),
    ("worker89thread89", "d29ya2VyODl0aHJlYWQ4OQ"),
    ("worker89kitten89", "d29ya2VyODlraXR0ZW44OQ"),
    ("worker89sitting89", "d29ya2VyODlzaXR0aW5nODk"),
    ("kernel89sitting89", "a2VybmVsODlzaXR0aW5nODk"),
    ("kernel89agent89", "a2VybmVsODlhZ2VudDg5"),
    ("kernel89angle89", "a2VybmVsODlhbmdsZTg5"),
    ("kernel89universe89", "a2VybmVsODl1bml2ZXJzZTg5"),
    ("signal89universe89", "c2lnbmFsODl1bml2ZXJzZTg5"),
    ("signal89memory89", "c2lnbmFsODltZW1vcnk4OQ"),
    ("signal89stream89", "c2lnbmFsODlzdHJlYW04OQ"),
    ("signal89context89", "c2lnbmFsODljb250ZXh0ODk"),
    ("packet89context89", "cGFja2V0ODljb250ZXh0ODk"),
    ("packet89knowledge89", "cGFja2V0ODlrbm93bGVkZ2U4OQ"),
    ("packet89vector89", "cGFja2V0ODl2ZWN0b3I4OQ"),
    ("packet89processor89", "cGFja2V0ODlwcm9jZXNzb3I4OQ"),
    ("router89processor89", "cm91dGVyODlwcm9jZXNzb3I4OQ"),
    ("router89reasoning89", "cm91dGVyODlyZWFzb25pbmc4OQ"),
    ("router89machine89", "cm91dGVyODltYWNoaW5lODk"),
    ("router89learning89", "cm91dGVyODlsZWFybmluZzg5"),
    ("cluster89learning89", "Y2x1c3Rlcjg5bGVhcm5pbmc4OQ"),
    ("cluster89model89", "Y2x1c3Rlcjg5bW9kZWw4OQ"),
    ("cluster89token89", "Y2x1c3Rlcjg5dG9rZW44OQ"),
    ("cluster89prompt89", "Y2x1c3Rlcjg5cHJvbXB0ODk"),
    ("mirror89prompt89", "bWlycm9yODlwcm9tcHQ4OQ"),
    ("mirror89session89", "bWlycm9yODlzZXNzaW9uODk"),
    ("mirror89library89", "bWlycm9yODlsaWJyYXJ5ODk"),
    ("mirror89service89", "bWlycm9yODlzZXJ2aWNlODk"),
    ("filter89service89", "ZmlsdGVyODlzZXJ2aWNlODk"),
    ("filter89gateway89", "ZmlsdGVyODlnYXRld2F5ODk"),
    ("filter89storage89", "ZmlsdGVyODlzdG9yYWdlODk"),
    ("filter89network89", "ZmlsdGVyODluZXR3b3JrODk"),
    ("ranking89network89", "cmFua2luZzg5bmV0d29yazg5"),
    ("ranking89latency89", "cmFua2luZzg5bGF0ZW5jeTg5"),
    ("ranking89buffer89", "cmFua2luZzg5YnVmZmVyODk"),
    ("ranking89queue89", "cmFua2luZzg5cXVldWU4OQ"),
    ("encoding89queue89", "ZW5jb2Rpbmc4OXF1ZXVlODk"),
    ("encoding89worker89", "ZW5jb2Rpbmc4OXdvcmtlcjg5"),
    ("encoding89kernel89", "ZW5jb2Rpbmc4OWtlcm5lbDg5"),
    ("encoding89signal89", "ZW5jb2Rpbmc4OXNpZ25hbDg5"),
    ("mapping89signal89", "bWFwcGluZzg5c2lnbmFsODk"),
    ("mapping89packet89", "bWFwcGluZzg5cGFja2V0ODk"),
    ("mapping89router89", "bWFwcGluZzg5cm91dGVyODk"),
    ("mapping89cluster89", "bWFwcGluZzg5Y2x1c3Rlcjg5"),
    ("record89cluster89", "cmVjb3JkODljbHVzdGVyODk"),
    ("record89mirror89", "cmVjb3JkODltaXJyb3I4OQ"),
    ("record89filter89", "cmVjb3JkODlmaWx0ZXI4OQ"),
    ("record89ranking89", "cmVjb3JkODlyYW5raW5nODk"),
    ("candle89ranking89", "Y2FuZGxlODlyYW5raW5nODk"),
    ("candle89encoding89", "Y2FuZGxlODllbmNvZGluZzg5"),
    ("candle89mapping89", "Y2FuZGxlODltYXBwaW5nODk"),
    ("candle89record89", "Y2FuZGxlODlyZWNvcmQ4OQ"),
    ("thread89record89", "dGhyZWFkODlyZWNvcmQ4OQ"),
    ("thread89candle89", "dGhyZWFkODljYW5kbGU4OQ"),
    ("thread89thread89", "dGhyZWFkODl0aHJlYWQ4OQ"),
    ("thread89kitten89", "dGhyZWFkODlraXR0ZW44OQ"),
    (
        "round 89: the quick brown fox jumps over the lazy dog",
        "cm91bmQgODk6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 89: agentuniverse is a framework for multi agents",
        "cm91bmQgODk6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 89: knowledge stored as vectors enables retrieval",
        "cm91bmQgODk6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 89: the processor reads the record then stops",
        "cm91bmQgODk6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 89: a worker pulls the next task from the queue",
        "cm91bmQgODk6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 89: signals travel through the network layer",
        "cm91bmQgODk6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 89: the gateway routes each request by policy",
        "cm91bmQgODk6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 89: memory grows until the buffer is full",
        "cm91bmQgODk6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 89: the cluster mirrors every packet twice",
        "cm91bmQgODk6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 89: ranking uses tokens learned from the corpus",
        "cm91bmQgODk6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 89: a long session ends when the candle dies",
        "cm91bmQgODk6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 89: encode the prompt then map the result",
        "cm91bmQgODk6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 89: the kernel wakes the worker at dawn", "cm91bmQgODk6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 89: service latency drops after the patch",
        "cm91bmQgODk6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 89: the library caches every vector it sees",
        "cm91bmQgODk6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 89: agents argue then the debate resolves",
        "cm91bmQgODk6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 89: the filter keeps only strong matches",
        "cm91bmQgODk6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 89: the model answers with a short reply",
        "cm91bmQgODk6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 89: the recorder stores the reasoning trace",
        "cm91bmQgODk6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 89: the angel watches the processor run", "cm91bmQgODk6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 89: angle of the vector decides the match",
        "cm91bmQgODk6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 89: the candle burns twice as long at night",
        "cm91bmQgODk6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 89: a mirror of the universe in one line",
        "cm91bmQgODk6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 89: the queue drains before the storm", "cm91bmQgODk6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
