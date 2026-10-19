"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten99kitten99", "a2l0dGVuOTlraXR0ZW45OQ"),
    ("kitten99sitting99", "a2l0dGVuOTlzaXR0aW5nOTk"),
    ("kitten99agent99", "a2l0dGVuOTlhZ2VudDk5"),
    ("kitten99angle99", "a2l0dGVuOTlhbmdsZTk5"),
    ("sitting99angle99", "c2l0dGluZzk5YW5nbGU5OQ"),
    ("sitting99universe99", "c2l0dGluZzk5dW5pdmVyc2U5OQ"),
    ("sitting99memory99", "c2l0dGluZzk5bWVtb3J5OTk"),
    ("sitting99stream99", "c2l0dGluZzk5c3RyZWFtOTk"),
    ("agent99stream99", "YWdlbnQ5OXN0cmVhbTk5"),
    ("agent99context99", "YWdlbnQ5OWNvbnRleHQ5OQ"),
    ("agent99knowledge99", "YWdlbnQ5OWtub3dsZWRnZTk5"),
    ("agent99vector99", "YWdlbnQ5OXZlY3Rvcjk5"),
    ("angle99vector99", "YW5nbGU5OXZlY3Rvcjk5"),
    ("angle99processor99", "YW5nbGU5OXByb2Nlc3Nvcjk5"),
    ("angle99reasoning99", "YW5nbGU5OXJlYXNvbmluZzk5"),
    ("angle99machine99", "YW5nbGU5OW1hY2hpbmU5OQ"),
    ("universe99machine99", "dW5pdmVyc2U5OW1hY2hpbmU5OQ"),
    ("universe99learning99", "dW5pdmVyc2U5OWxlYXJuaW5nOTk"),
    ("universe99model99", "dW5pdmVyc2U5OW1vZGVsOTk"),
    ("universe99token99", "dW5pdmVyc2U5OXRva2VuOTk"),
    ("memory99token99", "bWVtb3J5OTl0b2tlbjk5"),
    ("memory99prompt99", "bWVtb3J5OTlwcm9tcHQ5OQ"),
    ("memory99session99", "bWVtb3J5OTlzZXNzaW9uOTk"),
    ("memory99library99", "bWVtb3J5OTlsaWJyYXJ5OTk"),
    ("stream99library99", "c3RyZWFtOTlsaWJyYXJ5OTk"),
    ("stream99service99", "c3RyZWFtOTlzZXJ2aWNlOTk"),
    ("stream99gateway99", "c3RyZWFtOTlnYXRld2F5OTk"),
    ("stream99storage99", "c3RyZWFtOTlzdG9yYWdlOTk"),
    ("context99storage99", "Y29udGV4dDk5c3RvcmFnZTk5"),
    ("context99network99", "Y29udGV4dDk5bmV0d29yazk5"),
    ("context99latency99", "Y29udGV4dDk5bGF0ZW5jeTk5"),
    ("context99buffer99", "Y29udGV4dDk5YnVmZmVyOTk"),
    ("knowledge99buffer99", "a25vd2xlZGdlOTlidWZmZXI5OQ"),
    ("knowledge99queue99", "a25vd2xlZGdlOTlxdWV1ZTk5"),
    ("knowledge99worker99", "a25vd2xlZGdlOTl3b3JrZXI5OQ"),
    ("knowledge99kernel99", "a25vd2xlZGdlOTlrZXJuZWw5OQ"),
    ("vector99kernel99", "dmVjdG9yOTlrZXJuZWw5OQ"),
    ("vector99signal99", "dmVjdG9yOTlzaWduYWw5OQ"),
    ("vector99packet99", "dmVjdG9yOTlwYWNrZXQ5OQ"),
    ("vector99router99", "dmVjdG9yOTlyb3V0ZXI5OQ"),
    ("processor99router99", "cHJvY2Vzc29yOTlyb3V0ZXI5OQ"),
    ("processor99cluster99", "cHJvY2Vzc29yOTljbHVzdGVyOTk"),
    ("processor99mirror99", "cHJvY2Vzc29yOTltaXJyb3I5OQ"),
    ("processor99filter99", "cHJvY2Vzc29yOTlmaWx0ZXI5OQ"),
    ("reasoning99filter99", "cmVhc29uaW5nOTlmaWx0ZXI5OQ"),
    ("reasoning99ranking99", "cmVhc29uaW5nOTlyYW5raW5nOTk"),
    ("reasoning99encoding99", "cmVhc29uaW5nOTllbmNvZGluZzk5"),
    ("reasoning99mapping99", "cmVhc29uaW5nOTltYXBwaW5nOTk"),
    ("machine99mapping99", "bWFjaGluZTk5bWFwcGluZzk5"),
    ("machine99record99", "bWFjaGluZTk5cmVjb3JkOTk"),
    ("machine99candle99", "bWFjaGluZTk5Y2FuZGxlOTk"),
    ("machine99thread99", "bWFjaGluZTk5dGhyZWFkOTk"),
    ("learning99thread99", "bGVhcm5pbmc5OXRocmVhZDk5"),
    ("learning99kitten99", "bGVhcm5pbmc5OWtpdHRlbjk5"),
    ("learning99sitting99", "bGVhcm5pbmc5OXNpdHRpbmc5OQ"),
    ("learning99agent99", "bGVhcm5pbmc5OWFnZW50OTk"),
    ("model99agent99", "bW9kZWw5OWFnZW50OTk"),
    ("model99angle99", "bW9kZWw5OWFuZ2xlOTk"),
    ("model99universe99", "bW9kZWw5OXVuaXZlcnNlOTk"),
    ("model99memory99", "bW9kZWw5OW1lbW9yeTk5"),
    ("token99memory99", "dG9rZW45OW1lbW9yeTk5"),
    ("token99stream99", "dG9rZW45OXN0cmVhbTk5"),
    ("token99context99", "dG9rZW45OWNvbnRleHQ5OQ"),
    ("token99knowledge99", "dG9rZW45OWtub3dsZWRnZTk5"),
    ("prompt99knowledge99", "cHJvbXB0OTlrbm93bGVkZ2U5OQ"),
    ("prompt99vector99", "cHJvbXB0OTl2ZWN0b3I5OQ"),
    ("prompt99processor99", "cHJvbXB0OTlwcm9jZXNzb3I5OQ"),
    ("prompt99reasoning99", "cHJvbXB0OTlyZWFzb25pbmc5OQ"),
    ("session99reasoning99", "c2Vzc2lvbjk5cmVhc29uaW5nOTk"),
    ("session99machine99", "c2Vzc2lvbjk5bWFjaGluZTk5"),
    ("session99learning99", "c2Vzc2lvbjk5bGVhcm5pbmc5OQ"),
    ("session99model99", "c2Vzc2lvbjk5bW9kZWw5OQ"),
    ("library99model99", "bGlicmFyeTk5bW9kZWw5OQ"),
    ("library99token99", "bGlicmFyeTk5dG9rZW45OQ"),
    ("library99prompt99", "bGlicmFyeTk5cHJvbXB0OTk"),
    ("library99session99", "bGlicmFyeTk5c2Vzc2lvbjk5"),
    ("service99session99", "c2VydmljZTk5c2Vzc2lvbjk5"),
    ("service99library99", "c2VydmljZTk5bGlicmFyeTk5"),
    ("service99service99", "c2VydmljZTk5c2VydmljZTk5"),
    ("service99gateway99", "c2VydmljZTk5Z2F0ZXdheTk5"),
    ("gateway99gateway99", "Z2F0ZXdheTk5Z2F0ZXdheTk5"),
    ("gateway99storage99", "Z2F0ZXdheTk5c3RvcmFnZTk5"),
    ("gateway99network99", "Z2F0ZXdheTk5bmV0d29yazk5"),
    ("gateway99latency99", "Z2F0ZXdheTk5bGF0ZW5jeTk5"),
    ("storage99latency99", "c3RvcmFnZTk5bGF0ZW5jeTk5"),
    ("storage99buffer99", "c3RvcmFnZTk5YnVmZmVyOTk"),
    ("storage99queue99", "c3RvcmFnZTk5cXVldWU5OQ"),
    ("storage99worker99", "c3RvcmFnZTk5d29ya2VyOTk"),
    ("network99worker99", "bmV0d29yazk5d29ya2VyOTk"),
    ("network99kernel99", "bmV0d29yazk5a2VybmVsOTk"),
    ("network99signal99", "bmV0d29yazk5c2lnbmFsOTk"),
    ("network99packet99", "bmV0d29yazk5cGFja2V0OTk"),
    ("latency99packet99", "bGF0ZW5jeTk5cGFja2V0OTk"),
    ("latency99router99", "bGF0ZW5jeTk5cm91dGVyOTk"),
    ("latency99cluster99", "bGF0ZW5jeTk5Y2x1c3Rlcjk5"),
    ("latency99mirror99", "bGF0ZW5jeTk5bWlycm9yOTk"),
    ("buffer99mirror99", "YnVmZmVyOTltaXJyb3I5OQ"),
    ("buffer99filter99", "YnVmZmVyOTlmaWx0ZXI5OQ"),
    ("buffer99ranking99", "YnVmZmVyOTlyYW5raW5nOTk"),
    ("buffer99encoding99", "YnVmZmVyOTllbmNvZGluZzk5"),
    ("queue99encoding99", "cXVldWU5OWVuY29kaW5nOTk"),
    ("queue99mapping99", "cXVldWU5OW1hcHBpbmc5OQ"),
    ("queue99record99", "cXVldWU5OXJlY29yZDk5"),
    ("queue99candle99", "cXVldWU5OWNhbmRsZTk5"),
    ("worker99candle99", "d29ya2VyOTljYW5kbGU5OQ"),
    ("worker99thread99", "d29ya2VyOTl0aHJlYWQ5OQ"),
    ("worker99kitten99", "d29ya2VyOTlraXR0ZW45OQ"),
    ("worker99sitting99", "d29ya2VyOTlzaXR0aW5nOTk"),
    ("kernel99sitting99", "a2VybmVsOTlzaXR0aW5nOTk"),
    ("kernel99agent99", "a2VybmVsOTlhZ2VudDk5"),
    ("kernel99angle99", "a2VybmVsOTlhbmdsZTk5"),
    ("kernel99universe99", "a2VybmVsOTl1bml2ZXJzZTk5"),
    ("signal99universe99", "c2lnbmFsOTl1bml2ZXJzZTk5"),
    ("signal99memory99", "c2lnbmFsOTltZW1vcnk5OQ"),
    ("signal99stream99", "c2lnbmFsOTlzdHJlYW05OQ"),
    ("signal99context99", "c2lnbmFsOTljb250ZXh0OTk"),
    ("packet99context99", "cGFja2V0OTljb250ZXh0OTk"),
    ("packet99knowledge99", "cGFja2V0OTlrbm93bGVkZ2U5OQ"),
    ("packet99vector99", "cGFja2V0OTl2ZWN0b3I5OQ"),
    ("packet99processor99", "cGFja2V0OTlwcm9jZXNzb3I5OQ"),
    ("router99processor99", "cm91dGVyOTlwcm9jZXNzb3I5OQ"),
    ("router99reasoning99", "cm91dGVyOTlyZWFzb25pbmc5OQ"),
    ("router99machine99", "cm91dGVyOTltYWNoaW5lOTk"),
    ("router99learning99", "cm91dGVyOTlsZWFybmluZzk5"),
    ("cluster99learning99", "Y2x1c3Rlcjk5bGVhcm5pbmc5OQ"),
    ("cluster99model99", "Y2x1c3Rlcjk5bW9kZWw5OQ"),
    ("cluster99token99", "Y2x1c3Rlcjk5dG9rZW45OQ"),
    ("cluster99prompt99", "Y2x1c3Rlcjk5cHJvbXB0OTk"),
    ("mirror99prompt99", "bWlycm9yOTlwcm9tcHQ5OQ"),
    ("mirror99session99", "bWlycm9yOTlzZXNzaW9uOTk"),
    ("mirror99library99", "bWlycm9yOTlsaWJyYXJ5OTk"),
    ("mirror99service99", "bWlycm9yOTlzZXJ2aWNlOTk"),
    ("filter99service99", "ZmlsdGVyOTlzZXJ2aWNlOTk"),
    ("filter99gateway99", "ZmlsdGVyOTlnYXRld2F5OTk"),
    ("filter99storage99", "ZmlsdGVyOTlzdG9yYWdlOTk"),
    ("filter99network99", "ZmlsdGVyOTluZXR3b3JrOTk"),
    ("ranking99network99", "cmFua2luZzk5bmV0d29yazk5"),
    ("ranking99latency99", "cmFua2luZzk5bGF0ZW5jeTk5"),
    ("ranking99buffer99", "cmFua2luZzk5YnVmZmVyOTk"),
    ("ranking99queue99", "cmFua2luZzk5cXVldWU5OQ"),
    ("encoding99queue99", "ZW5jb2Rpbmc5OXF1ZXVlOTk"),
    ("encoding99worker99", "ZW5jb2Rpbmc5OXdvcmtlcjk5"),
    ("encoding99kernel99", "ZW5jb2Rpbmc5OWtlcm5lbDk5"),
    ("encoding99signal99", "ZW5jb2Rpbmc5OXNpZ25hbDk5"),
    ("mapping99signal99", "bWFwcGluZzk5c2lnbmFsOTk"),
    ("mapping99packet99", "bWFwcGluZzk5cGFja2V0OTk"),
    ("mapping99router99", "bWFwcGluZzk5cm91dGVyOTk"),
    ("mapping99cluster99", "bWFwcGluZzk5Y2x1c3Rlcjk5"),
    ("record99cluster99", "cmVjb3JkOTljbHVzdGVyOTk"),
    ("record99mirror99", "cmVjb3JkOTltaXJyb3I5OQ"),
    ("record99filter99", "cmVjb3JkOTlmaWx0ZXI5OQ"),
    ("record99ranking99", "cmVjb3JkOTlyYW5raW5nOTk"),
    ("candle99ranking99", "Y2FuZGxlOTlyYW5raW5nOTk"),
    ("candle99encoding99", "Y2FuZGxlOTllbmNvZGluZzk5"),
    ("candle99mapping99", "Y2FuZGxlOTltYXBwaW5nOTk"),
    ("candle99record99", "Y2FuZGxlOTlyZWNvcmQ5OQ"),
    ("thread99record99", "dGhyZWFkOTlyZWNvcmQ5OQ"),
    ("thread99candle99", "dGhyZWFkOTljYW5kbGU5OQ"),
    ("thread99thread99", "dGhyZWFkOTl0aHJlYWQ5OQ"),
    ("thread99kitten99", "dGhyZWFkOTlraXR0ZW45OQ"),
    (
        "round 99: the quick brown fox jumps over the lazy dog",
        "cm91bmQgOTk6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 99: agentuniverse is a framework for multi agents",
        "cm91bmQgOTk6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 99: knowledge stored as vectors enables retrieval",
        "cm91bmQgOTk6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 99: the processor reads the record then stops",
        "cm91bmQgOTk6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 99: a worker pulls the next task from the queue",
        "cm91bmQgOTk6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 99: signals travel through the network layer",
        "cm91bmQgOTk6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 99: the gateway routes each request by policy",
        "cm91bmQgOTk6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 99: memory grows until the buffer is full",
        "cm91bmQgOTk6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 99: the cluster mirrors every packet twice",
        "cm91bmQgOTk6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 99: ranking uses tokens learned from the corpus",
        "cm91bmQgOTk6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 99: a long session ends when the candle dies",
        "cm91bmQgOTk6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 99: encode the prompt then map the result",
        "cm91bmQgOTk6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 99: the kernel wakes the worker at dawn", "cm91bmQgOTk6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 99: service latency drops after the patch",
        "cm91bmQgOTk6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 99: the library caches every vector it sees",
        "cm91bmQgOTk6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 99: agents argue then the debate resolves",
        "cm91bmQgOTk6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 99: the filter keeps only strong matches",
        "cm91bmQgOTk6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 99: the model answers with a short reply",
        "cm91bmQgOTk6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 99: the recorder stores the reasoning trace",
        "cm91bmQgOTk6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 99: the angel watches the processor run", "cm91bmQgOTk6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 99: angle of the vector decides the match",
        "cm91bmQgOTk6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 99: the candle burns twice as long at night",
        "cm91bmQgOTk6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 99: a mirror of the universe in one line",
        "cm91bmQgOTk6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 99: the queue drains before the storm", "cm91bmQgOTk6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
