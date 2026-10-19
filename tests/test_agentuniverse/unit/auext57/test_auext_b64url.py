"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten57kitten57", "a2l0dGVuNTdraXR0ZW41Nw"),
    ("kitten57sitting57", "a2l0dGVuNTdzaXR0aW5nNTc"),
    ("kitten57agent57", "a2l0dGVuNTdhZ2VudDU3"),
    ("kitten57angle57", "a2l0dGVuNTdhbmdsZTU3"),
    ("sitting57angle57", "c2l0dGluZzU3YW5nbGU1Nw"),
    ("sitting57universe57", "c2l0dGluZzU3dW5pdmVyc2U1Nw"),
    ("sitting57memory57", "c2l0dGluZzU3bWVtb3J5NTc"),
    ("sitting57stream57", "c2l0dGluZzU3c3RyZWFtNTc"),
    ("agent57stream57", "YWdlbnQ1N3N0cmVhbTU3"),
    ("agent57context57", "YWdlbnQ1N2NvbnRleHQ1Nw"),
    ("agent57knowledge57", "YWdlbnQ1N2tub3dsZWRnZTU3"),
    ("agent57vector57", "YWdlbnQ1N3ZlY3RvcjU3"),
    ("angle57vector57", "YW5nbGU1N3ZlY3RvcjU3"),
    ("angle57processor57", "YW5nbGU1N3Byb2Nlc3NvcjU3"),
    ("angle57reasoning57", "YW5nbGU1N3JlYXNvbmluZzU3"),
    ("angle57machine57", "YW5nbGU1N21hY2hpbmU1Nw"),
    ("universe57machine57", "dW5pdmVyc2U1N21hY2hpbmU1Nw"),
    ("universe57learning57", "dW5pdmVyc2U1N2xlYXJuaW5nNTc"),
    ("universe57model57", "dW5pdmVyc2U1N21vZGVsNTc"),
    ("universe57token57", "dW5pdmVyc2U1N3Rva2VuNTc"),
    ("memory57token57", "bWVtb3J5NTd0b2tlbjU3"),
    ("memory57prompt57", "bWVtb3J5NTdwcm9tcHQ1Nw"),
    ("memory57session57", "bWVtb3J5NTdzZXNzaW9uNTc"),
    ("memory57library57", "bWVtb3J5NTdsaWJyYXJ5NTc"),
    ("stream57library57", "c3RyZWFtNTdsaWJyYXJ5NTc"),
    ("stream57service57", "c3RyZWFtNTdzZXJ2aWNlNTc"),
    ("stream57gateway57", "c3RyZWFtNTdnYXRld2F5NTc"),
    ("stream57storage57", "c3RyZWFtNTdzdG9yYWdlNTc"),
    ("context57storage57", "Y29udGV4dDU3c3RvcmFnZTU3"),
    ("context57network57", "Y29udGV4dDU3bmV0d29yazU3"),
    ("context57latency57", "Y29udGV4dDU3bGF0ZW5jeTU3"),
    ("context57buffer57", "Y29udGV4dDU3YnVmZmVyNTc"),
    ("knowledge57buffer57", "a25vd2xlZGdlNTdidWZmZXI1Nw"),
    ("knowledge57queue57", "a25vd2xlZGdlNTdxdWV1ZTU3"),
    ("knowledge57worker57", "a25vd2xlZGdlNTd3b3JrZXI1Nw"),
    ("knowledge57kernel57", "a25vd2xlZGdlNTdrZXJuZWw1Nw"),
    ("vector57kernel57", "dmVjdG9yNTdrZXJuZWw1Nw"),
    ("vector57signal57", "dmVjdG9yNTdzaWduYWw1Nw"),
    ("vector57packet57", "dmVjdG9yNTdwYWNrZXQ1Nw"),
    ("vector57router57", "dmVjdG9yNTdyb3V0ZXI1Nw"),
    ("processor57router57", "cHJvY2Vzc29yNTdyb3V0ZXI1Nw"),
    ("processor57cluster57", "cHJvY2Vzc29yNTdjbHVzdGVyNTc"),
    ("processor57mirror57", "cHJvY2Vzc29yNTdtaXJyb3I1Nw"),
    ("processor57filter57", "cHJvY2Vzc29yNTdmaWx0ZXI1Nw"),
    ("reasoning57filter57", "cmVhc29uaW5nNTdmaWx0ZXI1Nw"),
    ("reasoning57ranking57", "cmVhc29uaW5nNTdyYW5raW5nNTc"),
    ("reasoning57encoding57", "cmVhc29uaW5nNTdlbmNvZGluZzU3"),
    ("reasoning57mapping57", "cmVhc29uaW5nNTdtYXBwaW5nNTc"),
    ("machine57mapping57", "bWFjaGluZTU3bWFwcGluZzU3"),
    ("machine57record57", "bWFjaGluZTU3cmVjb3JkNTc"),
    ("machine57candle57", "bWFjaGluZTU3Y2FuZGxlNTc"),
    ("machine57thread57", "bWFjaGluZTU3dGhyZWFkNTc"),
    ("learning57thread57", "bGVhcm5pbmc1N3RocmVhZDU3"),
    ("learning57kitten57", "bGVhcm5pbmc1N2tpdHRlbjU3"),
    ("learning57sitting57", "bGVhcm5pbmc1N3NpdHRpbmc1Nw"),
    ("learning57agent57", "bGVhcm5pbmc1N2FnZW50NTc"),
    ("model57agent57", "bW9kZWw1N2FnZW50NTc"),
    ("model57angle57", "bW9kZWw1N2FuZ2xlNTc"),
    ("model57universe57", "bW9kZWw1N3VuaXZlcnNlNTc"),
    ("model57memory57", "bW9kZWw1N21lbW9yeTU3"),
    ("token57memory57", "dG9rZW41N21lbW9yeTU3"),
    ("token57stream57", "dG9rZW41N3N0cmVhbTU3"),
    ("token57context57", "dG9rZW41N2NvbnRleHQ1Nw"),
    ("token57knowledge57", "dG9rZW41N2tub3dsZWRnZTU3"),
    ("prompt57knowledge57", "cHJvbXB0NTdrbm93bGVkZ2U1Nw"),
    ("prompt57vector57", "cHJvbXB0NTd2ZWN0b3I1Nw"),
    ("prompt57processor57", "cHJvbXB0NTdwcm9jZXNzb3I1Nw"),
    ("prompt57reasoning57", "cHJvbXB0NTdyZWFzb25pbmc1Nw"),
    ("session57reasoning57", "c2Vzc2lvbjU3cmVhc29uaW5nNTc"),
    ("session57machine57", "c2Vzc2lvbjU3bWFjaGluZTU3"),
    ("session57learning57", "c2Vzc2lvbjU3bGVhcm5pbmc1Nw"),
    ("session57model57", "c2Vzc2lvbjU3bW9kZWw1Nw"),
    ("library57model57", "bGlicmFyeTU3bW9kZWw1Nw"),
    ("library57token57", "bGlicmFyeTU3dG9rZW41Nw"),
    ("library57prompt57", "bGlicmFyeTU3cHJvbXB0NTc"),
    ("library57session57", "bGlicmFyeTU3c2Vzc2lvbjU3"),
    ("service57session57", "c2VydmljZTU3c2Vzc2lvbjU3"),
    ("service57library57", "c2VydmljZTU3bGlicmFyeTU3"),
    ("service57service57", "c2VydmljZTU3c2VydmljZTU3"),
    ("service57gateway57", "c2VydmljZTU3Z2F0ZXdheTU3"),
    ("gateway57gateway57", "Z2F0ZXdheTU3Z2F0ZXdheTU3"),
    ("gateway57storage57", "Z2F0ZXdheTU3c3RvcmFnZTU3"),
    ("gateway57network57", "Z2F0ZXdheTU3bmV0d29yazU3"),
    ("gateway57latency57", "Z2F0ZXdheTU3bGF0ZW5jeTU3"),
    ("storage57latency57", "c3RvcmFnZTU3bGF0ZW5jeTU3"),
    ("storage57buffer57", "c3RvcmFnZTU3YnVmZmVyNTc"),
    ("storage57queue57", "c3RvcmFnZTU3cXVldWU1Nw"),
    ("storage57worker57", "c3RvcmFnZTU3d29ya2VyNTc"),
    ("network57worker57", "bmV0d29yazU3d29ya2VyNTc"),
    ("network57kernel57", "bmV0d29yazU3a2VybmVsNTc"),
    ("network57signal57", "bmV0d29yazU3c2lnbmFsNTc"),
    ("network57packet57", "bmV0d29yazU3cGFja2V0NTc"),
    ("latency57packet57", "bGF0ZW5jeTU3cGFja2V0NTc"),
    ("latency57router57", "bGF0ZW5jeTU3cm91dGVyNTc"),
    ("latency57cluster57", "bGF0ZW5jeTU3Y2x1c3RlcjU3"),
    ("latency57mirror57", "bGF0ZW5jeTU3bWlycm9yNTc"),
    ("buffer57mirror57", "YnVmZmVyNTdtaXJyb3I1Nw"),
    ("buffer57filter57", "YnVmZmVyNTdmaWx0ZXI1Nw"),
    ("buffer57ranking57", "YnVmZmVyNTdyYW5raW5nNTc"),
    ("buffer57encoding57", "YnVmZmVyNTdlbmNvZGluZzU3"),
    ("queue57encoding57", "cXVldWU1N2VuY29kaW5nNTc"),
    ("queue57mapping57", "cXVldWU1N21hcHBpbmc1Nw"),
    ("queue57record57", "cXVldWU1N3JlY29yZDU3"),
    ("queue57candle57", "cXVldWU1N2NhbmRsZTU3"),
    ("worker57candle57", "d29ya2VyNTdjYW5kbGU1Nw"),
    ("worker57thread57", "d29ya2VyNTd0aHJlYWQ1Nw"),
    ("worker57kitten57", "d29ya2VyNTdraXR0ZW41Nw"),
    ("worker57sitting57", "d29ya2VyNTdzaXR0aW5nNTc"),
    ("kernel57sitting57", "a2VybmVsNTdzaXR0aW5nNTc"),
    ("kernel57agent57", "a2VybmVsNTdhZ2VudDU3"),
    ("kernel57angle57", "a2VybmVsNTdhbmdsZTU3"),
    ("kernel57universe57", "a2VybmVsNTd1bml2ZXJzZTU3"),
    ("signal57universe57", "c2lnbmFsNTd1bml2ZXJzZTU3"),
    ("signal57memory57", "c2lnbmFsNTdtZW1vcnk1Nw"),
    ("signal57stream57", "c2lnbmFsNTdzdHJlYW01Nw"),
    ("signal57context57", "c2lnbmFsNTdjb250ZXh0NTc"),
    ("packet57context57", "cGFja2V0NTdjb250ZXh0NTc"),
    ("packet57knowledge57", "cGFja2V0NTdrbm93bGVkZ2U1Nw"),
    ("packet57vector57", "cGFja2V0NTd2ZWN0b3I1Nw"),
    ("packet57processor57", "cGFja2V0NTdwcm9jZXNzb3I1Nw"),
    ("router57processor57", "cm91dGVyNTdwcm9jZXNzb3I1Nw"),
    ("router57reasoning57", "cm91dGVyNTdyZWFzb25pbmc1Nw"),
    ("router57machine57", "cm91dGVyNTdtYWNoaW5lNTc"),
    ("router57learning57", "cm91dGVyNTdsZWFybmluZzU3"),
    ("cluster57learning57", "Y2x1c3RlcjU3bGVhcm5pbmc1Nw"),
    ("cluster57model57", "Y2x1c3RlcjU3bW9kZWw1Nw"),
    ("cluster57token57", "Y2x1c3RlcjU3dG9rZW41Nw"),
    ("cluster57prompt57", "Y2x1c3RlcjU3cHJvbXB0NTc"),
    ("mirror57prompt57", "bWlycm9yNTdwcm9tcHQ1Nw"),
    ("mirror57session57", "bWlycm9yNTdzZXNzaW9uNTc"),
    ("mirror57library57", "bWlycm9yNTdsaWJyYXJ5NTc"),
    ("mirror57service57", "bWlycm9yNTdzZXJ2aWNlNTc"),
    ("filter57service57", "ZmlsdGVyNTdzZXJ2aWNlNTc"),
    ("filter57gateway57", "ZmlsdGVyNTdnYXRld2F5NTc"),
    ("filter57storage57", "ZmlsdGVyNTdzdG9yYWdlNTc"),
    ("filter57network57", "ZmlsdGVyNTduZXR3b3JrNTc"),
    ("ranking57network57", "cmFua2luZzU3bmV0d29yazU3"),
    ("ranking57latency57", "cmFua2luZzU3bGF0ZW5jeTU3"),
    ("ranking57buffer57", "cmFua2luZzU3YnVmZmVyNTc"),
    ("ranking57queue57", "cmFua2luZzU3cXVldWU1Nw"),
    ("encoding57queue57", "ZW5jb2Rpbmc1N3F1ZXVlNTc"),
    ("encoding57worker57", "ZW5jb2Rpbmc1N3dvcmtlcjU3"),
    ("encoding57kernel57", "ZW5jb2Rpbmc1N2tlcm5lbDU3"),
    ("encoding57signal57", "ZW5jb2Rpbmc1N3NpZ25hbDU3"),
    ("mapping57signal57", "bWFwcGluZzU3c2lnbmFsNTc"),
    ("mapping57packet57", "bWFwcGluZzU3cGFja2V0NTc"),
    ("mapping57router57", "bWFwcGluZzU3cm91dGVyNTc"),
    ("mapping57cluster57", "bWFwcGluZzU3Y2x1c3RlcjU3"),
    ("record57cluster57", "cmVjb3JkNTdjbHVzdGVyNTc"),
    ("record57mirror57", "cmVjb3JkNTdtaXJyb3I1Nw"),
    ("record57filter57", "cmVjb3JkNTdmaWx0ZXI1Nw"),
    ("record57ranking57", "cmVjb3JkNTdyYW5raW5nNTc"),
    ("candle57ranking57", "Y2FuZGxlNTdyYW5raW5nNTc"),
    ("candle57encoding57", "Y2FuZGxlNTdlbmNvZGluZzU3"),
    ("candle57mapping57", "Y2FuZGxlNTdtYXBwaW5nNTc"),
    ("candle57record57", "Y2FuZGxlNTdyZWNvcmQ1Nw"),
    ("thread57record57", "dGhyZWFkNTdyZWNvcmQ1Nw"),
    ("thread57candle57", "dGhyZWFkNTdjYW5kbGU1Nw"),
    ("thread57thread57", "dGhyZWFkNTd0aHJlYWQ1Nw"),
    ("thread57kitten57", "dGhyZWFkNTdraXR0ZW41Nw"),
    (
        "round 57: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNTc6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 57: agentuniverse is a framework for multi agents",
        "cm91bmQgNTc6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 57: knowledge stored as vectors enables retrieval",
        "cm91bmQgNTc6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 57: the processor reads the record then stops",
        "cm91bmQgNTc6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 57: a worker pulls the next task from the queue",
        "cm91bmQgNTc6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 57: signals travel through the network layer",
        "cm91bmQgNTc6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 57: the gateway routes each request by policy",
        "cm91bmQgNTc6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 57: memory grows until the buffer is full",
        "cm91bmQgNTc6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 57: the cluster mirrors every packet twice",
        "cm91bmQgNTc6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 57: ranking uses tokens learned from the corpus",
        "cm91bmQgNTc6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 57: a long session ends when the candle dies",
        "cm91bmQgNTc6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 57: encode the prompt then map the result",
        "cm91bmQgNTc6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 57: the kernel wakes the worker at dawn", "cm91bmQgNTc6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 57: service latency drops after the patch",
        "cm91bmQgNTc6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 57: the library caches every vector it sees",
        "cm91bmQgNTc6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 57: agents argue then the debate resolves",
        "cm91bmQgNTc6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 57: the filter keeps only strong matches",
        "cm91bmQgNTc6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 57: the model answers with a short reply",
        "cm91bmQgNTc6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 57: the recorder stores the reasoning trace",
        "cm91bmQgNTc6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 57: the angel watches the processor run", "cm91bmQgNTc6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 57: angle of the vector decides the match",
        "cm91bmQgNTc6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 57: the candle burns twice as long at night",
        "cm91bmQgNTc6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 57: a mirror of the universe in one line",
        "cm91bmQgNTc6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 57: the queue drains before the storm", "cm91bmQgNTc6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
