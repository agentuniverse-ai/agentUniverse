"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten28kitten28", "a2l0dGVuMjhraXR0ZW4yOA"),
    ("kitten28sitting28", "a2l0dGVuMjhzaXR0aW5nMjg"),
    ("kitten28agent28", "a2l0dGVuMjhhZ2VudDI4"),
    ("kitten28angle28", "a2l0dGVuMjhhbmdsZTI4"),
    ("sitting28angle28", "c2l0dGluZzI4YW5nbGUyOA"),
    ("sitting28universe28", "c2l0dGluZzI4dW5pdmVyc2UyOA"),
    ("sitting28memory28", "c2l0dGluZzI4bWVtb3J5Mjg"),
    ("sitting28stream28", "c2l0dGluZzI4c3RyZWFtMjg"),
    ("agent28stream28", "YWdlbnQyOHN0cmVhbTI4"),
    ("agent28context28", "YWdlbnQyOGNvbnRleHQyOA"),
    ("agent28knowledge28", "YWdlbnQyOGtub3dsZWRnZTI4"),
    ("agent28vector28", "YWdlbnQyOHZlY3RvcjI4"),
    ("angle28vector28", "YW5nbGUyOHZlY3RvcjI4"),
    ("angle28processor28", "YW5nbGUyOHByb2Nlc3NvcjI4"),
    ("angle28reasoning28", "YW5nbGUyOHJlYXNvbmluZzI4"),
    ("angle28machine28", "YW5nbGUyOG1hY2hpbmUyOA"),
    ("universe28machine28", "dW5pdmVyc2UyOG1hY2hpbmUyOA"),
    ("universe28learning28", "dW5pdmVyc2UyOGxlYXJuaW5nMjg"),
    ("universe28model28", "dW5pdmVyc2UyOG1vZGVsMjg"),
    ("universe28token28", "dW5pdmVyc2UyOHRva2VuMjg"),
    ("memory28token28", "bWVtb3J5Mjh0b2tlbjI4"),
    ("memory28prompt28", "bWVtb3J5Mjhwcm9tcHQyOA"),
    ("memory28session28", "bWVtb3J5MjhzZXNzaW9uMjg"),
    ("memory28library28", "bWVtb3J5MjhsaWJyYXJ5Mjg"),
    ("stream28library28", "c3RyZWFtMjhsaWJyYXJ5Mjg"),
    ("stream28service28", "c3RyZWFtMjhzZXJ2aWNlMjg"),
    ("stream28gateway28", "c3RyZWFtMjhnYXRld2F5Mjg"),
    ("stream28storage28", "c3RyZWFtMjhzdG9yYWdlMjg"),
    ("context28storage28", "Y29udGV4dDI4c3RvcmFnZTI4"),
    ("context28network28", "Y29udGV4dDI4bmV0d29yazI4"),
    ("context28latency28", "Y29udGV4dDI4bGF0ZW5jeTI4"),
    ("context28buffer28", "Y29udGV4dDI4YnVmZmVyMjg"),
    ("knowledge28buffer28", "a25vd2xlZGdlMjhidWZmZXIyOA"),
    ("knowledge28queue28", "a25vd2xlZGdlMjhxdWV1ZTI4"),
    ("knowledge28worker28", "a25vd2xlZGdlMjh3b3JrZXIyOA"),
    ("knowledge28kernel28", "a25vd2xlZGdlMjhrZXJuZWwyOA"),
    ("vector28kernel28", "dmVjdG9yMjhrZXJuZWwyOA"),
    ("vector28signal28", "dmVjdG9yMjhzaWduYWwyOA"),
    ("vector28packet28", "dmVjdG9yMjhwYWNrZXQyOA"),
    ("vector28router28", "dmVjdG9yMjhyb3V0ZXIyOA"),
    ("processor28router28", "cHJvY2Vzc29yMjhyb3V0ZXIyOA"),
    ("processor28cluster28", "cHJvY2Vzc29yMjhjbHVzdGVyMjg"),
    ("processor28mirror28", "cHJvY2Vzc29yMjhtaXJyb3IyOA"),
    ("processor28filter28", "cHJvY2Vzc29yMjhmaWx0ZXIyOA"),
    ("reasoning28filter28", "cmVhc29uaW5nMjhmaWx0ZXIyOA"),
    ("reasoning28ranking28", "cmVhc29uaW5nMjhyYW5raW5nMjg"),
    ("reasoning28encoding28", "cmVhc29uaW5nMjhlbmNvZGluZzI4"),
    ("reasoning28mapping28", "cmVhc29uaW5nMjhtYXBwaW5nMjg"),
    ("machine28mapping28", "bWFjaGluZTI4bWFwcGluZzI4"),
    ("machine28record28", "bWFjaGluZTI4cmVjb3JkMjg"),
    ("machine28candle28", "bWFjaGluZTI4Y2FuZGxlMjg"),
    ("machine28thread28", "bWFjaGluZTI4dGhyZWFkMjg"),
    ("learning28thread28", "bGVhcm5pbmcyOHRocmVhZDI4"),
    ("learning28kitten28", "bGVhcm5pbmcyOGtpdHRlbjI4"),
    ("learning28sitting28", "bGVhcm5pbmcyOHNpdHRpbmcyOA"),
    ("learning28agent28", "bGVhcm5pbmcyOGFnZW50Mjg"),
    ("model28agent28", "bW9kZWwyOGFnZW50Mjg"),
    ("model28angle28", "bW9kZWwyOGFuZ2xlMjg"),
    ("model28universe28", "bW9kZWwyOHVuaXZlcnNlMjg"),
    ("model28memory28", "bW9kZWwyOG1lbW9yeTI4"),
    ("token28memory28", "dG9rZW4yOG1lbW9yeTI4"),
    ("token28stream28", "dG9rZW4yOHN0cmVhbTI4"),
    ("token28context28", "dG9rZW4yOGNvbnRleHQyOA"),
    ("token28knowledge28", "dG9rZW4yOGtub3dsZWRnZTI4"),
    ("prompt28knowledge28", "cHJvbXB0Mjhrbm93bGVkZ2UyOA"),
    ("prompt28vector28", "cHJvbXB0Mjh2ZWN0b3IyOA"),
    ("prompt28processor28", "cHJvbXB0Mjhwcm9jZXNzb3IyOA"),
    ("prompt28reasoning28", "cHJvbXB0MjhyZWFzb25pbmcyOA"),
    ("session28reasoning28", "c2Vzc2lvbjI4cmVhc29uaW5nMjg"),
    ("session28machine28", "c2Vzc2lvbjI4bWFjaGluZTI4"),
    ("session28learning28", "c2Vzc2lvbjI4bGVhcm5pbmcyOA"),
    ("session28model28", "c2Vzc2lvbjI4bW9kZWwyOA"),
    ("library28model28", "bGlicmFyeTI4bW9kZWwyOA"),
    ("library28token28", "bGlicmFyeTI4dG9rZW4yOA"),
    ("library28prompt28", "bGlicmFyeTI4cHJvbXB0Mjg"),
    ("library28session28", "bGlicmFyeTI4c2Vzc2lvbjI4"),
    ("service28session28", "c2VydmljZTI4c2Vzc2lvbjI4"),
    ("service28library28", "c2VydmljZTI4bGlicmFyeTI4"),
    ("service28service28", "c2VydmljZTI4c2VydmljZTI4"),
    ("service28gateway28", "c2VydmljZTI4Z2F0ZXdheTI4"),
    ("gateway28gateway28", "Z2F0ZXdheTI4Z2F0ZXdheTI4"),
    ("gateway28storage28", "Z2F0ZXdheTI4c3RvcmFnZTI4"),
    ("gateway28network28", "Z2F0ZXdheTI4bmV0d29yazI4"),
    ("gateway28latency28", "Z2F0ZXdheTI4bGF0ZW5jeTI4"),
    ("storage28latency28", "c3RvcmFnZTI4bGF0ZW5jeTI4"),
    ("storage28buffer28", "c3RvcmFnZTI4YnVmZmVyMjg"),
    ("storage28queue28", "c3RvcmFnZTI4cXVldWUyOA"),
    ("storage28worker28", "c3RvcmFnZTI4d29ya2VyMjg"),
    ("network28worker28", "bmV0d29yazI4d29ya2VyMjg"),
    ("network28kernel28", "bmV0d29yazI4a2VybmVsMjg"),
    ("network28signal28", "bmV0d29yazI4c2lnbmFsMjg"),
    ("network28packet28", "bmV0d29yazI4cGFja2V0Mjg"),
    ("latency28packet28", "bGF0ZW5jeTI4cGFja2V0Mjg"),
    ("latency28router28", "bGF0ZW5jeTI4cm91dGVyMjg"),
    ("latency28cluster28", "bGF0ZW5jeTI4Y2x1c3RlcjI4"),
    ("latency28mirror28", "bGF0ZW5jeTI4bWlycm9yMjg"),
    ("buffer28mirror28", "YnVmZmVyMjhtaXJyb3IyOA"),
    ("buffer28filter28", "YnVmZmVyMjhmaWx0ZXIyOA"),
    ("buffer28ranking28", "YnVmZmVyMjhyYW5raW5nMjg"),
    ("buffer28encoding28", "YnVmZmVyMjhlbmNvZGluZzI4"),
    ("queue28encoding28", "cXVldWUyOGVuY29kaW5nMjg"),
    ("queue28mapping28", "cXVldWUyOG1hcHBpbmcyOA"),
    ("queue28record28", "cXVldWUyOHJlY29yZDI4"),
    ("queue28candle28", "cXVldWUyOGNhbmRsZTI4"),
    ("worker28candle28", "d29ya2VyMjhjYW5kbGUyOA"),
    ("worker28thread28", "d29ya2VyMjh0aHJlYWQyOA"),
    ("worker28kitten28", "d29ya2VyMjhraXR0ZW4yOA"),
    ("worker28sitting28", "d29ya2VyMjhzaXR0aW5nMjg"),
    ("kernel28sitting28", "a2VybmVsMjhzaXR0aW5nMjg"),
    ("kernel28agent28", "a2VybmVsMjhhZ2VudDI4"),
    ("kernel28angle28", "a2VybmVsMjhhbmdsZTI4"),
    ("kernel28universe28", "a2VybmVsMjh1bml2ZXJzZTI4"),
    ("signal28universe28", "c2lnbmFsMjh1bml2ZXJzZTI4"),
    ("signal28memory28", "c2lnbmFsMjhtZW1vcnkyOA"),
    ("signal28stream28", "c2lnbmFsMjhzdHJlYW0yOA"),
    ("signal28context28", "c2lnbmFsMjhjb250ZXh0Mjg"),
    ("packet28context28", "cGFja2V0Mjhjb250ZXh0Mjg"),
    ("packet28knowledge28", "cGFja2V0Mjhrbm93bGVkZ2UyOA"),
    ("packet28vector28", "cGFja2V0Mjh2ZWN0b3IyOA"),
    ("packet28processor28", "cGFja2V0Mjhwcm9jZXNzb3IyOA"),
    ("router28processor28", "cm91dGVyMjhwcm9jZXNzb3IyOA"),
    ("router28reasoning28", "cm91dGVyMjhyZWFzb25pbmcyOA"),
    ("router28machine28", "cm91dGVyMjhtYWNoaW5lMjg"),
    ("router28learning28", "cm91dGVyMjhsZWFybmluZzI4"),
    ("cluster28learning28", "Y2x1c3RlcjI4bGVhcm5pbmcyOA"),
    ("cluster28model28", "Y2x1c3RlcjI4bW9kZWwyOA"),
    ("cluster28token28", "Y2x1c3RlcjI4dG9rZW4yOA"),
    ("cluster28prompt28", "Y2x1c3RlcjI4cHJvbXB0Mjg"),
    ("mirror28prompt28", "bWlycm9yMjhwcm9tcHQyOA"),
    ("mirror28session28", "bWlycm9yMjhzZXNzaW9uMjg"),
    ("mirror28library28", "bWlycm9yMjhsaWJyYXJ5Mjg"),
    ("mirror28service28", "bWlycm9yMjhzZXJ2aWNlMjg"),
    ("filter28service28", "ZmlsdGVyMjhzZXJ2aWNlMjg"),
    ("filter28gateway28", "ZmlsdGVyMjhnYXRld2F5Mjg"),
    ("filter28storage28", "ZmlsdGVyMjhzdG9yYWdlMjg"),
    ("filter28network28", "ZmlsdGVyMjhuZXR3b3JrMjg"),
    ("ranking28network28", "cmFua2luZzI4bmV0d29yazI4"),
    ("ranking28latency28", "cmFua2luZzI4bGF0ZW5jeTI4"),
    ("ranking28buffer28", "cmFua2luZzI4YnVmZmVyMjg"),
    ("ranking28queue28", "cmFua2luZzI4cXVldWUyOA"),
    ("encoding28queue28", "ZW5jb2RpbmcyOHF1ZXVlMjg"),
    ("encoding28worker28", "ZW5jb2RpbmcyOHdvcmtlcjI4"),
    ("encoding28kernel28", "ZW5jb2RpbmcyOGtlcm5lbDI4"),
    ("encoding28signal28", "ZW5jb2RpbmcyOHNpZ25hbDI4"),
    ("mapping28signal28", "bWFwcGluZzI4c2lnbmFsMjg"),
    ("mapping28packet28", "bWFwcGluZzI4cGFja2V0Mjg"),
    ("mapping28router28", "bWFwcGluZzI4cm91dGVyMjg"),
    ("mapping28cluster28", "bWFwcGluZzI4Y2x1c3RlcjI4"),
    ("record28cluster28", "cmVjb3JkMjhjbHVzdGVyMjg"),
    ("record28mirror28", "cmVjb3JkMjhtaXJyb3IyOA"),
    ("record28filter28", "cmVjb3JkMjhmaWx0ZXIyOA"),
    ("record28ranking28", "cmVjb3JkMjhyYW5raW5nMjg"),
    ("candle28ranking28", "Y2FuZGxlMjhyYW5raW5nMjg"),
    ("candle28encoding28", "Y2FuZGxlMjhlbmNvZGluZzI4"),
    ("candle28mapping28", "Y2FuZGxlMjhtYXBwaW5nMjg"),
    ("candle28record28", "Y2FuZGxlMjhyZWNvcmQyOA"),
    ("thread28record28", "dGhyZWFkMjhyZWNvcmQyOA"),
    ("thread28candle28", "dGhyZWFkMjhjYW5kbGUyOA"),
    ("thread28thread28", "dGhyZWFkMjh0aHJlYWQyOA"),
    ("thread28kitten28", "dGhyZWFkMjhraXR0ZW4yOA"),
    (
        "round 28: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMjg6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 28: agentuniverse is a framework for multi agents",
        "cm91bmQgMjg6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 28: knowledge stored as vectors enables retrieval",
        "cm91bmQgMjg6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 28: the processor reads the record then stops",
        "cm91bmQgMjg6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 28: a worker pulls the next task from the queue",
        "cm91bmQgMjg6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 28: signals travel through the network layer",
        "cm91bmQgMjg6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 28: the gateway routes each request by policy",
        "cm91bmQgMjg6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 28: memory grows until the buffer is full",
        "cm91bmQgMjg6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 28: the cluster mirrors every packet twice",
        "cm91bmQgMjg6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 28: ranking uses tokens learned from the corpus",
        "cm91bmQgMjg6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 28: a long session ends when the candle dies",
        "cm91bmQgMjg6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 28: encode the prompt then map the result",
        "cm91bmQgMjg6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 28: the kernel wakes the worker at dawn", "cm91bmQgMjg6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 28: service latency drops after the patch",
        "cm91bmQgMjg6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 28: the library caches every vector it sees",
        "cm91bmQgMjg6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 28: agents argue then the debate resolves",
        "cm91bmQgMjg6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 28: the filter keeps only strong matches",
        "cm91bmQgMjg6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 28: the model answers with a short reply",
        "cm91bmQgMjg6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 28: the recorder stores the reasoning trace",
        "cm91bmQgMjg6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 28: the angel watches the processor run", "cm91bmQgMjg6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 28: angle of the vector decides the match",
        "cm91bmQgMjg6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 28: the candle burns twice as long at night",
        "cm91bmQgMjg6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 28: a mirror of the universe in one line",
        "cm91bmQgMjg6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 28: the queue drains before the storm", "cm91bmQgMjg6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
