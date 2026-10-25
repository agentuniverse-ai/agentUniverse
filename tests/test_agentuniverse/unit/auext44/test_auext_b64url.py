"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten44kitten44", "a2l0dGVuNDRraXR0ZW40NA"),
    ("kitten44sitting44", "a2l0dGVuNDRzaXR0aW5nNDQ"),
    ("kitten44agent44", "a2l0dGVuNDRhZ2VudDQ0"),
    ("kitten44angle44", "a2l0dGVuNDRhbmdsZTQ0"),
    ("sitting44angle44", "c2l0dGluZzQ0YW5nbGU0NA"),
    ("sitting44universe44", "c2l0dGluZzQ0dW5pdmVyc2U0NA"),
    ("sitting44memory44", "c2l0dGluZzQ0bWVtb3J5NDQ"),
    ("sitting44stream44", "c2l0dGluZzQ0c3RyZWFtNDQ"),
    ("agent44stream44", "YWdlbnQ0NHN0cmVhbTQ0"),
    ("agent44context44", "YWdlbnQ0NGNvbnRleHQ0NA"),
    ("agent44knowledge44", "YWdlbnQ0NGtub3dsZWRnZTQ0"),
    ("agent44vector44", "YWdlbnQ0NHZlY3RvcjQ0"),
    ("angle44vector44", "YW5nbGU0NHZlY3RvcjQ0"),
    ("angle44processor44", "YW5nbGU0NHByb2Nlc3NvcjQ0"),
    ("angle44reasoning44", "YW5nbGU0NHJlYXNvbmluZzQ0"),
    ("angle44machine44", "YW5nbGU0NG1hY2hpbmU0NA"),
    ("universe44machine44", "dW5pdmVyc2U0NG1hY2hpbmU0NA"),
    ("universe44learning44", "dW5pdmVyc2U0NGxlYXJuaW5nNDQ"),
    ("universe44model44", "dW5pdmVyc2U0NG1vZGVsNDQ"),
    ("universe44token44", "dW5pdmVyc2U0NHRva2VuNDQ"),
    ("memory44token44", "bWVtb3J5NDR0b2tlbjQ0"),
    ("memory44prompt44", "bWVtb3J5NDRwcm9tcHQ0NA"),
    ("memory44session44", "bWVtb3J5NDRzZXNzaW9uNDQ"),
    ("memory44library44", "bWVtb3J5NDRsaWJyYXJ5NDQ"),
    ("stream44library44", "c3RyZWFtNDRsaWJyYXJ5NDQ"),
    ("stream44service44", "c3RyZWFtNDRzZXJ2aWNlNDQ"),
    ("stream44gateway44", "c3RyZWFtNDRnYXRld2F5NDQ"),
    ("stream44storage44", "c3RyZWFtNDRzdG9yYWdlNDQ"),
    ("context44storage44", "Y29udGV4dDQ0c3RvcmFnZTQ0"),
    ("context44network44", "Y29udGV4dDQ0bmV0d29yazQ0"),
    ("context44latency44", "Y29udGV4dDQ0bGF0ZW5jeTQ0"),
    ("context44buffer44", "Y29udGV4dDQ0YnVmZmVyNDQ"),
    ("knowledge44buffer44", "a25vd2xlZGdlNDRidWZmZXI0NA"),
    ("knowledge44queue44", "a25vd2xlZGdlNDRxdWV1ZTQ0"),
    ("knowledge44worker44", "a25vd2xlZGdlNDR3b3JrZXI0NA"),
    ("knowledge44kernel44", "a25vd2xlZGdlNDRrZXJuZWw0NA"),
    ("vector44kernel44", "dmVjdG9yNDRrZXJuZWw0NA"),
    ("vector44signal44", "dmVjdG9yNDRzaWduYWw0NA"),
    ("vector44packet44", "dmVjdG9yNDRwYWNrZXQ0NA"),
    ("vector44router44", "dmVjdG9yNDRyb3V0ZXI0NA"),
    ("processor44router44", "cHJvY2Vzc29yNDRyb3V0ZXI0NA"),
    ("processor44cluster44", "cHJvY2Vzc29yNDRjbHVzdGVyNDQ"),
    ("processor44mirror44", "cHJvY2Vzc29yNDRtaXJyb3I0NA"),
    ("processor44filter44", "cHJvY2Vzc29yNDRmaWx0ZXI0NA"),
    ("reasoning44filter44", "cmVhc29uaW5nNDRmaWx0ZXI0NA"),
    ("reasoning44ranking44", "cmVhc29uaW5nNDRyYW5raW5nNDQ"),
    ("reasoning44encoding44", "cmVhc29uaW5nNDRlbmNvZGluZzQ0"),
    ("reasoning44mapping44", "cmVhc29uaW5nNDRtYXBwaW5nNDQ"),
    ("machine44mapping44", "bWFjaGluZTQ0bWFwcGluZzQ0"),
    ("machine44record44", "bWFjaGluZTQ0cmVjb3JkNDQ"),
    ("machine44candle44", "bWFjaGluZTQ0Y2FuZGxlNDQ"),
    ("machine44thread44", "bWFjaGluZTQ0dGhyZWFkNDQ"),
    ("learning44thread44", "bGVhcm5pbmc0NHRocmVhZDQ0"),
    ("learning44kitten44", "bGVhcm5pbmc0NGtpdHRlbjQ0"),
    ("learning44sitting44", "bGVhcm5pbmc0NHNpdHRpbmc0NA"),
    ("learning44agent44", "bGVhcm5pbmc0NGFnZW50NDQ"),
    ("model44agent44", "bW9kZWw0NGFnZW50NDQ"),
    ("model44angle44", "bW9kZWw0NGFuZ2xlNDQ"),
    ("model44universe44", "bW9kZWw0NHVuaXZlcnNlNDQ"),
    ("model44memory44", "bW9kZWw0NG1lbW9yeTQ0"),
    ("token44memory44", "dG9rZW40NG1lbW9yeTQ0"),
    ("token44stream44", "dG9rZW40NHN0cmVhbTQ0"),
    ("token44context44", "dG9rZW40NGNvbnRleHQ0NA"),
    ("token44knowledge44", "dG9rZW40NGtub3dsZWRnZTQ0"),
    ("prompt44knowledge44", "cHJvbXB0NDRrbm93bGVkZ2U0NA"),
    ("prompt44vector44", "cHJvbXB0NDR2ZWN0b3I0NA"),
    ("prompt44processor44", "cHJvbXB0NDRwcm9jZXNzb3I0NA"),
    ("prompt44reasoning44", "cHJvbXB0NDRyZWFzb25pbmc0NA"),
    ("session44reasoning44", "c2Vzc2lvbjQ0cmVhc29uaW5nNDQ"),
    ("session44machine44", "c2Vzc2lvbjQ0bWFjaGluZTQ0"),
    ("session44learning44", "c2Vzc2lvbjQ0bGVhcm5pbmc0NA"),
    ("session44model44", "c2Vzc2lvbjQ0bW9kZWw0NA"),
    ("library44model44", "bGlicmFyeTQ0bW9kZWw0NA"),
    ("library44token44", "bGlicmFyeTQ0dG9rZW40NA"),
    ("library44prompt44", "bGlicmFyeTQ0cHJvbXB0NDQ"),
    ("library44session44", "bGlicmFyeTQ0c2Vzc2lvbjQ0"),
    ("service44session44", "c2VydmljZTQ0c2Vzc2lvbjQ0"),
    ("service44library44", "c2VydmljZTQ0bGlicmFyeTQ0"),
    ("service44service44", "c2VydmljZTQ0c2VydmljZTQ0"),
    ("service44gateway44", "c2VydmljZTQ0Z2F0ZXdheTQ0"),
    ("gateway44gateway44", "Z2F0ZXdheTQ0Z2F0ZXdheTQ0"),
    ("gateway44storage44", "Z2F0ZXdheTQ0c3RvcmFnZTQ0"),
    ("gateway44network44", "Z2F0ZXdheTQ0bmV0d29yazQ0"),
    ("gateway44latency44", "Z2F0ZXdheTQ0bGF0ZW5jeTQ0"),
    ("storage44latency44", "c3RvcmFnZTQ0bGF0ZW5jeTQ0"),
    ("storage44buffer44", "c3RvcmFnZTQ0YnVmZmVyNDQ"),
    ("storage44queue44", "c3RvcmFnZTQ0cXVldWU0NA"),
    ("storage44worker44", "c3RvcmFnZTQ0d29ya2VyNDQ"),
    ("network44worker44", "bmV0d29yazQ0d29ya2VyNDQ"),
    ("network44kernel44", "bmV0d29yazQ0a2VybmVsNDQ"),
    ("network44signal44", "bmV0d29yazQ0c2lnbmFsNDQ"),
    ("network44packet44", "bmV0d29yazQ0cGFja2V0NDQ"),
    ("latency44packet44", "bGF0ZW5jeTQ0cGFja2V0NDQ"),
    ("latency44router44", "bGF0ZW5jeTQ0cm91dGVyNDQ"),
    ("latency44cluster44", "bGF0ZW5jeTQ0Y2x1c3RlcjQ0"),
    ("latency44mirror44", "bGF0ZW5jeTQ0bWlycm9yNDQ"),
    ("buffer44mirror44", "YnVmZmVyNDRtaXJyb3I0NA"),
    ("buffer44filter44", "YnVmZmVyNDRmaWx0ZXI0NA"),
    ("buffer44ranking44", "YnVmZmVyNDRyYW5raW5nNDQ"),
    ("buffer44encoding44", "YnVmZmVyNDRlbmNvZGluZzQ0"),
    ("queue44encoding44", "cXVldWU0NGVuY29kaW5nNDQ"),
    ("queue44mapping44", "cXVldWU0NG1hcHBpbmc0NA"),
    ("queue44record44", "cXVldWU0NHJlY29yZDQ0"),
    ("queue44candle44", "cXVldWU0NGNhbmRsZTQ0"),
    ("worker44candle44", "d29ya2VyNDRjYW5kbGU0NA"),
    ("worker44thread44", "d29ya2VyNDR0aHJlYWQ0NA"),
    ("worker44kitten44", "d29ya2VyNDRraXR0ZW40NA"),
    ("worker44sitting44", "d29ya2VyNDRzaXR0aW5nNDQ"),
    ("kernel44sitting44", "a2VybmVsNDRzaXR0aW5nNDQ"),
    ("kernel44agent44", "a2VybmVsNDRhZ2VudDQ0"),
    ("kernel44angle44", "a2VybmVsNDRhbmdsZTQ0"),
    ("kernel44universe44", "a2VybmVsNDR1bml2ZXJzZTQ0"),
    ("signal44universe44", "c2lnbmFsNDR1bml2ZXJzZTQ0"),
    ("signal44memory44", "c2lnbmFsNDRtZW1vcnk0NA"),
    ("signal44stream44", "c2lnbmFsNDRzdHJlYW00NA"),
    ("signal44context44", "c2lnbmFsNDRjb250ZXh0NDQ"),
    ("packet44context44", "cGFja2V0NDRjb250ZXh0NDQ"),
    ("packet44knowledge44", "cGFja2V0NDRrbm93bGVkZ2U0NA"),
    ("packet44vector44", "cGFja2V0NDR2ZWN0b3I0NA"),
    ("packet44processor44", "cGFja2V0NDRwcm9jZXNzb3I0NA"),
    ("router44processor44", "cm91dGVyNDRwcm9jZXNzb3I0NA"),
    ("router44reasoning44", "cm91dGVyNDRyZWFzb25pbmc0NA"),
    ("router44machine44", "cm91dGVyNDRtYWNoaW5lNDQ"),
    ("router44learning44", "cm91dGVyNDRsZWFybmluZzQ0"),
    ("cluster44learning44", "Y2x1c3RlcjQ0bGVhcm5pbmc0NA"),
    ("cluster44model44", "Y2x1c3RlcjQ0bW9kZWw0NA"),
    ("cluster44token44", "Y2x1c3RlcjQ0dG9rZW40NA"),
    ("cluster44prompt44", "Y2x1c3RlcjQ0cHJvbXB0NDQ"),
    ("mirror44prompt44", "bWlycm9yNDRwcm9tcHQ0NA"),
    ("mirror44session44", "bWlycm9yNDRzZXNzaW9uNDQ"),
    ("mirror44library44", "bWlycm9yNDRsaWJyYXJ5NDQ"),
    ("mirror44service44", "bWlycm9yNDRzZXJ2aWNlNDQ"),
    ("filter44service44", "ZmlsdGVyNDRzZXJ2aWNlNDQ"),
    ("filter44gateway44", "ZmlsdGVyNDRnYXRld2F5NDQ"),
    ("filter44storage44", "ZmlsdGVyNDRzdG9yYWdlNDQ"),
    ("filter44network44", "ZmlsdGVyNDRuZXR3b3JrNDQ"),
    ("ranking44network44", "cmFua2luZzQ0bmV0d29yazQ0"),
    ("ranking44latency44", "cmFua2luZzQ0bGF0ZW5jeTQ0"),
    ("ranking44buffer44", "cmFua2luZzQ0YnVmZmVyNDQ"),
    ("ranking44queue44", "cmFua2luZzQ0cXVldWU0NA"),
    ("encoding44queue44", "ZW5jb2Rpbmc0NHF1ZXVlNDQ"),
    ("encoding44worker44", "ZW5jb2Rpbmc0NHdvcmtlcjQ0"),
    ("encoding44kernel44", "ZW5jb2Rpbmc0NGtlcm5lbDQ0"),
    ("encoding44signal44", "ZW5jb2Rpbmc0NHNpZ25hbDQ0"),
    ("mapping44signal44", "bWFwcGluZzQ0c2lnbmFsNDQ"),
    ("mapping44packet44", "bWFwcGluZzQ0cGFja2V0NDQ"),
    ("mapping44router44", "bWFwcGluZzQ0cm91dGVyNDQ"),
    ("mapping44cluster44", "bWFwcGluZzQ0Y2x1c3RlcjQ0"),
    ("record44cluster44", "cmVjb3JkNDRjbHVzdGVyNDQ"),
    ("record44mirror44", "cmVjb3JkNDRtaXJyb3I0NA"),
    ("record44filter44", "cmVjb3JkNDRmaWx0ZXI0NA"),
    ("record44ranking44", "cmVjb3JkNDRyYW5raW5nNDQ"),
    ("candle44ranking44", "Y2FuZGxlNDRyYW5raW5nNDQ"),
    ("candle44encoding44", "Y2FuZGxlNDRlbmNvZGluZzQ0"),
    ("candle44mapping44", "Y2FuZGxlNDRtYXBwaW5nNDQ"),
    ("candle44record44", "Y2FuZGxlNDRyZWNvcmQ0NA"),
    ("thread44record44", "dGhyZWFkNDRyZWNvcmQ0NA"),
    ("thread44candle44", "dGhyZWFkNDRjYW5kbGU0NA"),
    ("thread44thread44", "dGhyZWFkNDR0aHJlYWQ0NA"),
    ("thread44kitten44", "dGhyZWFkNDRraXR0ZW40NA"),
    (
        "round 44: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNDQ6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 44: agentuniverse is a framework for multi agents",
        "cm91bmQgNDQ6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 44: knowledge stored as vectors enables retrieval",
        "cm91bmQgNDQ6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 44: the processor reads the record then stops",
        "cm91bmQgNDQ6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 44: a worker pulls the next task from the queue",
        "cm91bmQgNDQ6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 44: signals travel through the network layer",
        "cm91bmQgNDQ6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 44: the gateway routes each request by policy",
        "cm91bmQgNDQ6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 44: memory grows until the buffer is full",
        "cm91bmQgNDQ6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 44: the cluster mirrors every packet twice",
        "cm91bmQgNDQ6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 44: ranking uses tokens learned from the corpus",
        "cm91bmQgNDQ6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 44: a long session ends when the candle dies",
        "cm91bmQgNDQ6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 44: encode the prompt then map the result",
        "cm91bmQgNDQ6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 44: the kernel wakes the worker at dawn", "cm91bmQgNDQ6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 44: service latency drops after the patch",
        "cm91bmQgNDQ6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 44: the library caches every vector it sees",
        "cm91bmQgNDQ6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 44: agents argue then the debate resolves",
        "cm91bmQgNDQ6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 44: the filter keeps only strong matches",
        "cm91bmQgNDQ6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 44: the model answers with a short reply",
        "cm91bmQgNDQ6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 44: the recorder stores the reasoning trace",
        "cm91bmQgNDQ6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 44: the angel watches the processor run", "cm91bmQgNDQ6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 44: angle of the vector decides the match",
        "cm91bmQgNDQ6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 44: the candle burns twice as long at night",
        "cm91bmQgNDQ6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 44: a mirror of the universe in one line",
        "cm91bmQgNDQ6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 44: the queue drains before the storm", "cm91bmQgNDQ6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
