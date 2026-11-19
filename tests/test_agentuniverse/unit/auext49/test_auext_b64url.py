"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten49kitten49", "a2l0dGVuNDlraXR0ZW40OQ"),
    ("kitten49sitting49", "a2l0dGVuNDlzaXR0aW5nNDk"),
    ("kitten49agent49", "a2l0dGVuNDlhZ2VudDQ5"),
    ("kitten49angle49", "a2l0dGVuNDlhbmdsZTQ5"),
    ("sitting49angle49", "c2l0dGluZzQ5YW5nbGU0OQ"),
    ("sitting49universe49", "c2l0dGluZzQ5dW5pdmVyc2U0OQ"),
    ("sitting49memory49", "c2l0dGluZzQ5bWVtb3J5NDk"),
    ("sitting49stream49", "c2l0dGluZzQ5c3RyZWFtNDk"),
    ("agent49stream49", "YWdlbnQ0OXN0cmVhbTQ5"),
    ("agent49context49", "YWdlbnQ0OWNvbnRleHQ0OQ"),
    ("agent49knowledge49", "YWdlbnQ0OWtub3dsZWRnZTQ5"),
    ("agent49vector49", "YWdlbnQ0OXZlY3RvcjQ5"),
    ("angle49vector49", "YW5nbGU0OXZlY3RvcjQ5"),
    ("angle49processor49", "YW5nbGU0OXByb2Nlc3NvcjQ5"),
    ("angle49reasoning49", "YW5nbGU0OXJlYXNvbmluZzQ5"),
    ("angle49machine49", "YW5nbGU0OW1hY2hpbmU0OQ"),
    ("universe49machine49", "dW5pdmVyc2U0OW1hY2hpbmU0OQ"),
    ("universe49learning49", "dW5pdmVyc2U0OWxlYXJuaW5nNDk"),
    ("universe49model49", "dW5pdmVyc2U0OW1vZGVsNDk"),
    ("universe49token49", "dW5pdmVyc2U0OXRva2VuNDk"),
    ("memory49token49", "bWVtb3J5NDl0b2tlbjQ5"),
    ("memory49prompt49", "bWVtb3J5NDlwcm9tcHQ0OQ"),
    ("memory49session49", "bWVtb3J5NDlzZXNzaW9uNDk"),
    ("memory49library49", "bWVtb3J5NDlsaWJyYXJ5NDk"),
    ("stream49library49", "c3RyZWFtNDlsaWJyYXJ5NDk"),
    ("stream49service49", "c3RyZWFtNDlzZXJ2aWNlNDk"),
    ("stream49gateway49", "c3RyZWFtNDlnYXRld2F5NDk"),
    ("stream49storage49", "c3RyZWFtNDlzdG9yYWdlNDk"),
    ("context49storage49", "Y29udGV4dDQ5c3RvcmFnZTQ5"),
    ("context49network49", "Y29udGV4dDQ5bmV0d29yazQ5"),
    ("context49latency49", "Y29udGV4dDQ5bGF0ZW5jeTQ5"),
    ("context49buffer49", "Y29udGV4dDQ5YnVmZmVyNDk"),
    ("knowledge49buffer49", "a25vd2xlZGdlNDlidWZmZXI0OQ"),
    ("knowledge49queue49", "a25vd2xlZGdlNDlxdWV1ZTQ5"),
    ("knowledge49worker49", "a25vd2xlZGdlNDl3b3JrZXI0OQ"),
    ("knowledge49kernel49", "a25vd2xlZGdlNDlrZXJuZWw0OQ"),
    ("vector49kernel49", "dmVjdG9yNDlrZXJuZWw0OQ"),
    ("vector49signal49", "dmVjdG9yNDlzaWduYWw0OQ"),
    ("vector49packet49", "dmVjdG9yNDlwYWNrZXQ0OQ"),
    ("vector49router49", "dmVjdG9yNDlyb3V0ZXI0OQ"),
    ("processor49router49", "cHJvY2Vzc29yNDlyb3V0ZXI0OQ"),
    ("processor49cluster49", "cHJvY2Vzc29yNDljbHVzdGVyNDk"),
    ("processor49mirror49", "cHJvY2Vzc29yNDltaXJyb3I0OQ"),
    ("processor49filter49", "cHJvY2Vzc29yNDlmaWx0ZXI0OQ"),
    ("reasoning49filter49", "cmVhc29uaW5nNDlmaWx0ZXI0OQ"),
    ("reasoning49ranking49", "cmVhc29uaW5nNDlyYW5raW5nNDk"),
    ("reasoning49encoding49", "cmVhc29uaW5nNDllbmNvZGluZzQ5"),
    ("reasoning49mapping49", "cmVhc29uaW5nNDltYXBwaW5nNDk"),
    ("machine49mapping49", "bWFjaGluZTQ5bWFwcGluZzQ5"),
    ("machine49record49", "bWFjaGluZTQ5cmVjb3JkNDk"),
    ("machine49candle49", "bWFjaGluZTQ5Y2FuZGxlNDk"),
    ("machine49thread49", "bWFjaGluZTQ5dGhyZWFkNDk"),
    ("learning49thread49", "bGVhcm5pbmc0OXRocmVhZDQ5"),
    ("learning49kitten49", "bGVhcm5pbmc0OWtpdHRlbjQ5"),
    ("learning49sitting49", "bGVhcm5pbmc0OXNpdHRpbmc0OQ"),
    ("learning49agent49", "bGVhcm5pbmc0OWFnZW50NDk"),
    ("model49agent49", "bW9kZWw0OWFnZW50NDk"),
    ("model49angle49", "bW9kZWw0OWFuZ2xlNDk"),
    ("model49universe49", "bW9kZWw0OXVuaXZlcnNlNDk"),
    ("model49memory49", "bW9kZWw0OW1lbW9yeTQ5"),
    ("token49memory49", "dG9rZW40OW1lbW9yeTQ5"),
    ("token49stream49", "dG9rZW40OXN0cmVhbTQ5"),
    ("token49context49", "dG9rZW40OWNvbnRleHQ0OQ"),
    ("token49knowledge49", "dG9rZW40OWtub3dsZWRnZTQ5"),
    ("prompt49knowledge49", "cHJvbXB0NDlrbm93bGVkZ2U0OQ"),
    ("prompt49vector49", "cHJvbXB0NDl2ZWN0b3I0OQ"),
    ("prompt49processor49", "cHJvbXB0NDlwcm9jZXNzb3I0OQ"),
    ("prompt49reasoning49", "cHJvbXB0NDlyZWFzb25pbmc0OQ"),
    ("session49reasoning49", "c2Vzc2lvbjQ5cmVhc29uaW5nNDk"),
    ("session49machine49", "c2Vzc2lvbjQ5bWFjaGluZTQ5"),
    ("session49learning49", "c2Vzc2lvbjQ5bGVhcm5pbmc0OQ"),
    ("session49model49", "c2Vzc2lvbjQ5bW9kZWw0OQ"),
    ("library49model49", "bGlicmFyeTQ5bW9kZWw0OQ"),
    ("library49token49", "bGlicmFyeTQ5dG9rZW40OQ"),
    ("library49prompt49", "bGlicmFyeTQ5cHJvbXB0NDk"),
    ("library49session49", "bGlicmFyeTQ5c2Vzc2lvbjQ5"),
    ("service49session49", "c2VydmljZTQ5c2Vzc2lvbjQ5"),
    ("service49library49", "c2VydmljZTQ5bGlicmFyeTQ5"),
    ("service49service49", "c2VydmljZTQ5c2VydmljZTQ5"),
    ("service49gateway49", "c2VydmljZTQ5Z2F0ZXdheTQ5"),
    ("gateway49gateway49", "Z2F0ZXdheTQ5Z2F0ZXdheTQ5"),
    ("gateway49storage49", "Z2F0ZXdheTQ5c3RvcmFnZTQ5"),
    ("gateway49network49", "Z2F0ZXdheTQ5bmV0d29yazQ5"),
    ("gateway49latency49", "Z2F0ZXdheTQ5bGF0ZW5jeTQ5"),
    ("storage49latency49", "c3RvcmFnZTQ5bGF0ZW5jeTQ5"),
    ("storage49buffer49", "c3RvcmFnZTQ5YnVmZmVyNDk"),
    ("storage49queue49", "c3RvcmFnZTQ5cXVldWU0OQ"),
    ("storage49worker49", "c3RvcmFnZTQ5d29ya2VyNDk"),
    ("network49worker49", "bmV0d29yazQ5d29ya2VyNDk"),
    ("network49kernel49", "bmV0d29yazQ5a2VybmVsNDk"),
    ("network49signal49", "bmV0d29yazQ5c2lnbmFsNDk"),
    ("network49packet49", "bmV0d29yazQ5cGFja2V0NDk"),
    ("latency49packet49", "bGF0ZW5jeTQ5cGFja2V0NDk"),
    ("latency49router49", "bGF0ZW5jeTQ5cm91dGVyNDk"),
    ("latency49cluster49", "bGF0ZW5jeTQ5Y2x1c3RlcjQ5"),
    ("latency49mirror49", "bGF0ZW5jeTQ5bWlycm9yNDk"),
    ("buffer49mirror49", "YnVmZmVyNDltaXJyb3I0OQ"),
    ("buffer49filter49", "YnVmZmVyNDlmaWx0ZXI0OQ"),
    ("buffer49ranking49", "YnVmZmVyNDlyYW5raW5nNDk"),
    ("buffer49encoding49", "YnVmZmVyNDllbmNvZGluZzQ5"),
    ("queue49encoding49", "cXVldWU0OWVuY29kaW5nNDk"),
    ("queue49mapping49", "cXVldWU0OW1hcHBpbmc0OQ"),
    ("queue49record49", "cXVldWU0OXJlY29yZDQ5"),
    ("queue49candle49", "cXVldWU0OWNhbmRsZTQ5"),
    ("worker49candle49", "d29ya2VyNDljYW5kbGU0OQ"),
    ("worker49thread49", "d29ya2VyNDl0aHJlYWQ0OQ"),
    ("worker49kitten49", "d29ya2VyNDlraXR0ZW40OQ"),
    ("worker49sitting49", "d29ya2VyNDlzaXR0aW5nNDk"),
    ("kernel49sitting49", "a2VybmVsNDlzaXR0aW5nNDk"),
    ("kernel49agent49", "a2VybmVsNDlhZ2VudDQ5"),
    ("kernel49angle49", "a2VybmVsNDlhbmdsZTQ5"),
    ("kernel49universe49", "a2VybmVsNDl1bml2ZXJzZTQ5"),
    ("signal49universe49", "c2lnbmFsNDl1bml2ZXJzZTQ5"),
    ("signal49memory49", "c2lnbmFsNDltZW1vcnk0OQ"),
    ("signal49stream49", "c2lnbmFsNDlzdHJlYW00OQ"),
    ("signal49context49", "c2lnbmFsNDljb250ZXh0NDk"),
    ("packet49context49", "cGFja2V0NDljb250ZXh0NDk"),
    ("packet49knowledge49", "cGFja2V0NDlrbm93bGVkZ2U0OQ"),
    ("packet49vector49", "cGFja2V0NDl2ZWN0b3I0OQ"),
    ("packet49processor49", "cGFja2V0NDlwcm9jZXNzb3I0OQ"),
    ("router49processor49", "cm91dGVyNDlwcm9jZXNzb3I0OQ"),
    ("router49reasoning49", "cm91dGVyNDlyZWFzb25pbmc0OQ"),
    ("router49machine49", "cm91dGVyNDltYWNoaW5lNDk"),
    ("router49learning49", "cm91dGVyNDlsZWFybmluZzQ5"),
    ("cluster49learning49", "Y2x1c3RlcjQ5bGVhcm5pbmc0OQ"),
    ("cluster49model49", "Y2x1c3RlcjQ5bW9kZWw0OQ"),
    ("cluster49token49", "Y2x1c3RlcjQ5dG9rZW40OQ"),
    ("cluster49prompt49", "Y2x1c3RlcjQ5cHJvbXB0NDk"),
    ("mirror49prompt49", "bWlycm9yNDlwcm9tcHQ0OQ"),
    ("mirror49session49", "bWlycm9yNDlzZXNzaW9uNDk"),
    ("mirror49library49", "bWlycm9yNDlsaWJyYXJ5NDk"),
    ("mirror49service49", "bWlycm9yNDlzZXJ2aWNlNDk"),
    ("filter49service49", "ZmlsdGVyNDlzZXJ2aWNlNDk"),
    ("filter49gateway49", "ZmlsdGVyNDlnYXRld2F5NDk"),
    ("filter49storage49", "ZmlsdGVyNDlzdG9yYWdlNDk"),
    ("filter49network49", "ZmlsdGVyNDluZXR3b3JrNDk"),
    ("ranking49network49", "cmFua2luZzQ5bmV0d29yazQ5"),
    ("ranking49latency49", "cmFua2luZzQ5bGF0ZW5jeTQ5"),
    ("ranking49buffer49", "cmFua2luZzQ5YnVmZmVyNDk"),
    ("ranking49queue49", "cmFua2luZzQ5cXVldWU0OQ"),
    ("encoding49queue49", "ZW5jb2Rpbmc0OXF1ZXVlNDk"),
    ("encoding49worker49", "ZW5jb2Rpbmc0OXdvcmtlcjQ5"),
    ("encoding49kernel49", "ZW5jb2Rpbmc0OWtlcm5lbDQ5"),
    ("encoding49signal49", "ZW5jb2Rpbmc0OXNpZ25hbDQ5"),
    ("mapping49signal49", "bWFwcGluZzQ5c2lnbmFsNDk"),
    ("mapping49packet49", "bWFwcGluZzQ5cGFja2V0NDk"),
    ("mapping49router49", "bWFwcGluZzQ5cm91dGVyNDk"),
    ("mapping49cluster49", "bWFwcGluZzQ5Y2x1c3RlcjQ5"),
    ("record49cluster49", "cmVjb3JkNDljbHVzdGVyNDk"),
    ("record49mirror49", "cmVjb3JkNDltaXJyb3I0OQ"),
    ("record49filter49", "cmVjb3JkNDlmaWx0ZXI0OQ"),
    ("record49ranking49", "cmVjb3JkNDlyYW5raW5nNDk"),
    ("candle49ranking49", "Y2FuZGxlNDlyYW5raW5nNDk"),
    ("candle49encoding49", "Y2FuZGxlNDllbmNvZGluZzQ5"),
    ("candle49mapping49", "Y2FuZGxlNDltYXBwaW5nNDk"),
    ("candle49record49", "Y2FuZGxlNDlyZWNvcmQ0OQ"),
    ("thread49record49", "dGhyZWFkNDlyZWNvcmQ0OQ"),
    ("thread49candle49", "dGhyZWFkNDljYW5kbGU0OQ"),
    ("thread49thread49", "dGhyZWFkNDl0aHJlYWQ0OQ"),
    ("thread49kitten49", "dGhyZWFkNDlraXR0ZW40OQ"),
    (
        "round 49: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNDk6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 49: agentuniverse is a framework for multi agents",
        "cm91bmQgNDk6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 49: knowledge stored as vectors enables retrieval",
        "cm91bmQgNDk6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 49: the processor reads the record then stops",
        "cm91bmQgNDk6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 49: a worker pulls the next task from the queue",
        "cm91bmQgNDk6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 49: signals travel through the network layer",
        "cm91bmQgNDk6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 49: the gateway routes each request by policy",
        "cm91bmQgNDk6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 49: memory grows until the buffer is full",
        "cm91bmQgNDk6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 49: the cluster mirrors every packet twice",
        "cm91bmQgNDk6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 49: ranking uses tokens learned from the corpus",
        "cm91bmQgNDk6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 49: a long session ends when the candle dies",
        "cm91bmQgNDk6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 49: encode the prompt then map the result",
        "cm91bmQgNDk6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 49: the kernel wakes the worker at dawn", "cm91bmQgNDk6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 49: service latency drops after the patch",
        "cm91bmQgNDk6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 49: the library caches every vector it sees",
        "cm91bmQgNDk6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 49: agents argue then the debate resolves",
        "cm91bmQgNDk6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 49: the filter keeps only strong matches",
        "cm91bmQgNDk6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 49: the model answers with a short reply",
        "cm91bmQgNDk6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 49: the recorder stores the reasoning trace",
        "cm91bmQgNDk6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 49: the angel watches the processor run", "cm91bmQgNDk6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 49: angle of the vector decides the match",
        "cm91bmQgNDk6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 49: the candle burns twice as long at night",
        "cm91bmQgNDk6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 49: a mirror of the universe in one line",
        "cm91bmQgNDk6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 49: the queue drains before the storm", "cm91bmQgNDk6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
