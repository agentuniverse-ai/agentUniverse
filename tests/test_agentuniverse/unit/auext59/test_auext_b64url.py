"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten59kitten59", "a2l0dGVuNTlraXR0ZW41OQ"),
    ("kitten59sitting59", "a2l0dGVuNTlzaXR0aW5nNTk"),
    ("kitten59agent59", "a2l0dGVuNTlhZ2VudDU5"),
    ("kitten59angle59", "a2l0dGVuNTlhbmdsZTU5"),
    ("sitting59angle59", "c2l0dGluZzU5YW5nbGU1OQ"),
    ("sitting59universe59", "c2l0dGluZzU5dW5pdmVyc2U1OQ"),
    ("sitting59memory59", "c2l0dGluZzU5bWVtb3J5NTk"),
    ("sitting59stream59", "c2l0dGluZzU5c3RyZWFtNTk"),
    ("agent59stream59", "YWdlbnQ1OXN0cmVhbTU5"),
    ("agent59context59", "YWdlbnQ1OWNvbnRleHQ1OQ"),
    ("agent59knowledge59", "YWdlbnQ1OWtub3dsZWRnZTU5"),
    ("agent59vector59", "YWdlbnQ1OXZlY3RvcjU5"),
    ("angle59vector59", "YW5nbGU1OXZlY3RvcjU5"),
    ("angle59processor59", "YW5nbGU1OXByb2Nlc3NvcjU5"),
    ("angle59reasoning59", "YW5nbGU1OXJlYXNvbmluZzU5"),
    ("angle59machine59", "YW5nbGU1OW1hY2hpbmU1OQ"),
    ("universe59machine59", "dW5pdmVyc2U1OW1hY2hpbmU1OQ"),
    ("universe59learning59", "dW5pdmVyc2U1OWxlYXJuaW5nNTk"),
    ("universe59model59", "dW5pdmVyc2U1OW1vZGVsNTk"),
    ("universe59token59", "dW5pdmVyc2U1OXRva2VuNTk"),
    ("memory59token59", "bWVtb3J5NTl0b2tlbjU5"),
    ("memory59prompt59", "bWVtb3J5NTlwcm9tcHQ1OQ"),
    ("memory59session59", "bWVtb3J5NTlzZXNzaW9uNTk"),
    ("memory59library59", "bWVtb3J5NTlsaWJyYXJ5NTk"),
    ("stream59library59", "c3RyZWFtNTlsaWJyYXJ5NTk"),
    ("stream59service59", "c3RyZWFtNTlzZXJ2aWNlNTk"),
    ("stream59gateway59", "c3RyZWFtNTlnYXRld2F5NTk"),
    ("stream59storage59", "c3RyZWFtNTlzdG9yYWdlNTk"),
    ("context59storage59", "Y29udGV4dDU5c3RvcmFnZTU5"),
    ("context59network59", "Y29udGV4dDU5bmV0d29yazU5"),
    ("context59latency59", "Y29udGV4dDU5bGF0ZW5jeTU5"),
    ("context59buffer59", "Y29udGV4dDU5YnVmZmVyNTk"),
    ("knowledge59buffer59", "a25vd2xlZGdlNTlidWZmZXI1OQ"),
    ("knowledge59queue59", "a25vd2xlZGdlNTlxdWV1ZTU5"),
    ("knowledge59worker59", "a25vd2xlZGdlNTl3b3JrZXI1OQ"),
    ("knowledge59kernel59", "a25vd2xlZGdlNTlrZXJuZWw1OQ"),
    ("vector59kernel59", "dmVjdG9yNTlrZXJuZWw1OQ"),
    ("vector59signal59", "dmVjdG9yNTlzaWduYWw1OQ"),
    ("vector59packet59", "dmVjdG9yNTlwYWNrZXQ1OQ"),
    ("vector59router59", "dmVjdG9yNTlyb3V0ZXI1OQ"),
    ("processor59router59", "cHJvY2Vzc29yNTlyb3V0ZXI1OQ"),
    ("processor59cluster59", "cHJvY2Vzc29yNTljbHVzdGVyNTk"),
    ("processor59mirror59", "cHJvY2Vzc29yNTltaXJyb3I1OQ"),
    ("processor59filter59", "cHJvY2Vzc29yNTlmaWx0ZXI1OQ"),
    ("reasoning59filter59", "cmVhc29uaW5nNTlmaWx0ZXI1OQ"),
    ("reasoning59ranking59", "cmVhc29uaW5nNTlyYW5raW5nNTk"),
    ("reasoning59encoding59", "cmVhc29uaW5nNTllbmNvZGluZzU5"),
    ("reasoning59mapping59", "cmVhc29uaW5nNTltYXBwaW5nNTk"),
    ("machine59mapping59", "bWFjaGluZTU5bWFwcGluZzU5"),
    ("machine59record59", "bWFjaGluZTU5cmVjb3JkNTk"),
    ("machine59candle59", "bWFjaGluZTU5Y2FuZGxlNTk"),
    ("machine59thread59", "bWFjaGluZTU5dGhyZWFkNTk"),
    ("learning59thread59", "bGVhcm5pbmc1OXRocmVhZDU5"),
    ("learning59kitten59", "bGVhcm5pbmc1OWtpdHRlbjU5"),
    ("learning59sitting59", "bGVhcm5pbmc1OXNpdHRpbmc1OQ"),
    ("learning59agent59", "bGVhcm5pbmc1OWFnZW50NTk"),
    ("model59agent59", "bW9kZWw1OWFnZW50NTk"),
    ("model59angle59", "bW9kZWw1OWFuZ2xlNTk"),
    ("model59universe59", "bW9kZWw1OXVuaXZlcnNlNTk"),
    ("model59memory59", "bW9kZWw1OW1lbW9yeTU5"),
    ("token59memory59", "dG9rZW41OW1lbW9yeTU5"),
    ("token59stream59", "dG9rZW41OXN0cmVhbTU5"),
    ("token59context59", "dG9rZW41OWNvbnRleHQ1OQ"),
    ("token59knowledge59", "dG9rZW41OWtub3dsZWRnZTU5"),
    ("prompt59knowledge59", "cHJvbXB0NTlrbm93bGVkZ2U1OQ"),
    ("prompt59vector59", "cHJvbXB0NTl2ZWN0b3I1OQ"),
    ("prompt59processor59", "cHJvbXB0NTlwcm9jZXNzb3I1OQ"),
    ("prompt59reasoning59", "cHJvbXB0NTlyZWFzb25pbmc1OQ"),
    ("session59reasoning59", "c2Vzc2lvbjU5cmVhc29uaW5nNTk"),
    ("session59machine59", "c2Vzc2lvbjU5bWFjaGluZTU5"),
    ("session59learning59", "c2Vzc2lvbjU5bGVhcm5pbmc1OQ"),
    ("session59model59", "c2Vzc2lvbjU5bW9kZWw1OQ"),
    ("library59model59", "bGlicmFyeTU5bW9kZWw1OQ"),
    ("library59token59", "bGlicmFyeTU5dG9rZW41OQ"),
    ("library59prompt59", "bGlicmFyeTU5cHJvbXB0NTk"),
    ("library59session59", "bGlicmFyeTU5c2Vzc2lvbjU5"),
    ("service59session59", "c2VydmljZTU5c2Vzc2lvbjU5"),
    ("service59library59", "c2VydmljZTU5bGlicmFyeTU5"),
    ("service59service59", "c2VydmljZTU5c2VydmljZTU5"),
    ("service59gateway59", "c2VydmljZTU5Z2F0ZXdheTU5"),
    ("gateway59gateway59", "Z2F0ZXdheTU5Z2F0ZXdheTU5"),
    ("gateway59storage59", "Z2F0ZXdheTU5c3RvcmFnZTU5"),
    ("gateway59network59", "Z2F0ZXdheTU5bmV0d29yazU5"),
    ("gateway59latency59", "Z2F0ZXdheTU5bGF0ZW5jeTU5"),
    ("storage59latency59", "c3RvcmFnZTU5bGF0ZW5jeTU5"),
    ("storage59buffer59", "c3RvcmFnZTU5YnVmZmVyNTk"),
    ("storage59queue59", "c3RvcmFnZTU5cXVldWU1OQ"),
    ("storage59worker59", "c3RvcmFnZTU5d29ya2VyNTk"),
    ("network59worker59", "bmV0d29yazU5d29ya2VyNTk"),
    ("network59kernel59", "bmV0d29yazU5a2VybmVsNTk"),
    ("network59signal59", "bmV0d29yazU5c2lnbmFsNTk"),
    ("network59packet59", "bmV0d29yazU5cGFja2V0NTk"),
    ("latency59packet59", "bGF0ZW5jeTU5cGFja2V0NTk"),
    ("latency59router59", "bGF0ZW5jeTU5cm91dGVyNTk"),
    ("latency59cluster59", "bGF0ZW5jeTU5Y2x1c3RlcjU5"),
    ("latency59mirror59", "bGF0ZW5jeTU5bWlycm9yNTk"),
    ("buffer59mirror59", "YnVmZmVyNTltaXJyb3I1OQ"),
    ("buffer59filter59", "YnVmZmVyNTlmaWx0ZXI1OQ"),
    ("buffer59ranking59", "YnVmZmVyNTlyYW5raW5nNTk"),
    ("buffer59encoding59", "YnVmZmVyNTllbmNvZGluZzU5"),
    ("queue59encoding59", "cXVldWU1OWVuY29kaW5nNTk"),
    ("queue59mapping59", "cXVldWU1OW1hcHBpbmc1OQ"),
    ("queue59record59", "cXVldWU1OXJlY29yZDU5"),
    ("queue59candle59", "cXVldWU1OWNhbmRsZTU5"),
    ("worker59candle59", "d29ya2VyNTljYW5kbGU1OQ"),
    ("worker59thread59", "d29ya2VyNTl0aHJlYWQ1OQ"),
    ("worker59kitten59", "d29ya2VyNTlraXR0ZW41OQ"),
    ("worker59sitting59", "d29ya2VyNTlzaXR0aW5nNTk"),
    ("kernel59sitting59", "a2VybmVsNTlzaXR0aW5nNTk"),
    ("kernel59agent59", "a2VybmVsNTlhZ2VudDU5"),
    ("kernel59angle59", "a2VybmVsNTlhbmdsZTU5"),
    ("kernel59universe59", "a2VybmVsNTl1bml2ZXJzZTU5"),
    ("signal59universe59", "c2lnbmFsNTl1bml2ZXJzZTU5"),
    ("signal59memory59", "c2lnbmFsNTltZW1vcnk1OQ"),
    ("signal59stream59", "c2lnbmFsNTlzdHJlYW01OQ"),
    ("signal59context59", "c2lnbmFsNTljb250ZXh0NTk"),
    ("packet59context59", "cGFja2V0NTljb250ZXh0NTk"),
    ("packet59knowledge59", "cGFja2V0NTlrbm93bGVkZ2U1OQ"),
    ("packet59vector59", "cGFja2V0NTl2ZWN0b3I1OQ"),
    ("packet59processor59", "cGFja2V0NTlwcm9jZXNzb3I1OQ"),
    ("router59processor59", "cm91dGVyNTlwcm9jZXNzb3I1OQ"),
    ("router59reasoning59", "cm91dGVyNTlyZWFzb25pbmc1OQ"),
    ("router59machine59", "cm91dGVyNTltYWNoaW5lNTk"),
    ("router59learning59", "cm91dGVyNTlsZWFybmluZzU5"),
    ("cluster59learning59", "Y2x1c3RlcjU5bGVhcm5pbmc1OQ"),
    ("cluster59model59", "Y2x1c3RlcjU5bW9kZWw1OQ"),
    ("cluster59token59", "Y2x1c3RlcjU5dG9rZW41OQ"),
    ("cluster59prompt59", "Y2x1c3RlcjU5cHJvbXB0NTk"),
    ("mirror59prompt59", "bWlycm9yNTlwcm9tcHQ1OQ"),
    ("mirror59session59", "bWlycm9yNTlzZXNzaW9uNTk"),
    ("mirror59library59", "bWlycm9yNTlsaWJyYXJ5NTk"),
    ("mirror59service59", "bWlycm9yNTlzZXJ2aWNlNTk"),
    ("filter59service59", "ZmlsdGVyNTlzZXJ2aWNlNTk"),
    ("filter59gateway59", "ZmlsdGVyNTlnYXRld2F5NTk"),
    ("filter59storage59", "ZmlsdGVyNTlzdG9yYWdlNTk"),
    ("filter59network59", "ZmlsdGVyNTluZXR3b3JrNTk"),
    ("ranking59network59", "cmFua2luZzU5bmV0d29yazU5"),
    ("ranking59latency59", "cmFua2luZzU5bGF0ZW5jeTU5"),
    ("ranking59buffer59", "cmFua2luZzU5YnVmZmVyNTk"),
    ("ranking59queue59", "cmFua2luZzU5cXVldWU1OQ"),
    ("encoding59queue59", "ZW5jb2Rpbmc1OXF1ZXVlNTk"),
    ("encoding59worker59", "ZW5jb2Rpbmc1OXdvcmtlcjU5"),
    ("encoding59kernel59", "ZW5jb2Rpbmc1OWtlcm5lbDU5"),
    ("encoding59signal59", "ZW5jb2Rpbmc1OXNpZ25hbDU5"),
    ("mapping59signal59", "bWFwcGluZzU5c2lnbmFsNTk"),
    ("mapping59packet59", "bWFwcGluZzU5cGFja2V0NTk"),
    ("mapping59router59", "bWFwcGluZzU5cm91dGVyNTk"),
    ("mapping59cluster59", "bWFwcGluZzU5Y2x1c3RlcjU5"),
    ("record59cluster59", "cmVjb3JkNTljbHVzdGVyNTk"),
    ("record59mirror59", "cmVjb3JkNTltaXJyb3I1OQ"),
    ("record59filter59", "cmVjb3JkNTlmaWx0ZXI1OQ"),
    ("record59ranking59", "cmVjb3JkNTlyYW5raW5nNTk"),
    ("candle59ranking59", "Y2FuZGxlNTlyYW5raW5nNTk"),
    ("candle59encoding59", "Y2FuZGxlNTllbmNvZGluZzU5"),
    ("candle59mapping59", "Y2FuZGxlNTltYXBwaW5nNTk"),
    ("candle59record59", "Y2FuZGxlNTlyZWNvcmQ1OQ"),
    ("thread59record59", "dGhyZWFkNTlyZWNvcmQ1OQ"),
    ("thread59candle59", "dGhyZWFkNTljYW5kbGU1OQ"),
    ("thread59thread59", "dGhyZWFkNTl0aHJlYWQ1OQ"),
    ("thread59kitten59", "dGhyZWFkNTlraXR0ZW41OQ"),
    (
        "round 59: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNTk6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 59: agentuniverse is a framework for multi agents",
        "cm91bmQgNTk6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 59: knowledge stored as vectors enables retrieval",
        "cm91bmQgNTk6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 59: the processor reads the record then stops",
        "cm91bmQgNTk6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 59: a worker pulls the next task from the queue",
        "cm91bmQgNTk6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 59: signals travel through the network layer",
        "cm91bmQgNTk6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 59: the gateway routes each request by policy",
        "cm91bmQgNTk6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 59: memory grows until the buffer is full",
        "cm91bmQgNTk6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 59: the cluster mirrors every packet twice",
        "cm91bmQgNTk6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 59: ranking uses tokens learned from the corpus",
        "cm91bmQgNTk6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 59: a long session ends when the candle dies",
        "cm91bmQgNTk6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 59: encode the prompt then map the result",
        "cm91bmQgNTk6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 59: the kernel wakes the worker at dawn", "cm91bmQgNTk6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 59: service latency drops after the patch",
        "cm91bmQgNTk6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 59: the library caches every vector it sees",
        "cm91bmQgNTk6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 59: agents argue then the debate resolves",
        "cm91bmQgNTk6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 59: the filter keeps only strong matches",
        "cm91bmQgNTk6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 59: the model answers with a short reply",
        "cm91bmQgNTk6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 59: the recorder stores the reasoning trace",
        "cm91bmQgNTk6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 59: the angel watches the processor run", "cm91bmQgNTk6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 59: angle of the vector decides the match",
        "cm91bmQgNTk6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 59: the candle burns twice as long at night",
        "cm91bmQgNTk6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 59: a mirror of the universe in one line",
        "cm91bmQgNTk6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 59: the queue drains before the storm", "cm91bmQgNTk6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
