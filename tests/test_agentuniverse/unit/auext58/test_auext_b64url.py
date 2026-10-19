"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten58kitten58", "a2l0dGVuNThraXR0ZW41OA"),
    ("kitten58sitting58", "a2l0dGVuNThzaXR0aW5nNTg"),
    ("kitten58agent58", "a2l0dGVuNThhZ2VudDU4"),
    ("kitten58angle58", "a2l0dGVuNThhbmdsZTU4"),
    ("sitting58angle58", "c2l0dGluZzU4YW5nbGU1OA"),
    ("sitting58universe58", "c2l0dGluZzU4dW5pdmVyc2U1OA"),
    ("sitting58memory58", "c2l0dGluZzU4bWVtb3J5NTg"),
    ("sitting58stream58", "c2l0dGluZzU4c3RyZWFtNTg"),
    ("agent58stream58", "YWdlbnQ1OHN0cmVhbTU4"),
    ("agent58context58", "YWdlbnQ1OGNvbnRleHQ1OA"),
    ("agent58knowledge58", "YWdlbnQ1OGtub3dsZWRnZTU4"),
    ("agent58vector58", "YWdlbnQ1OHZlY3RvcjU4"),
    ("angle58vector58", "YW5nbGU1OHZlY3RvcjU4"),
    ("angle58processor58", "YW5nbGU1OHByb2Nlc3NvcjU4"),
    ("angle58reasoning58", "YW5nbGU1OHJlYXNvbmluZzU4"),
    ("angle58machine58", "YW5nbGU1OG1hY2hpbmU1OA"),
    ("universe58machine58", "dW5pdmVyc2U1OG1hY2hpbmU1OA"),
    ("universe58learning58", "dW5pdmVyc2U1OGxlYXJuaW5nNTg"),
    ("universe58model58", "dW5pdmVyc2U1OG1vZGVsNTg"),
    ("universe58token58", "dW5pdmVyc2U1OHRva2VuNTg"),
    ("memory58token58", "bWVtb3J5NTh0b2tlbjU4"),
    ("memory58prompt58", "bWVtb3J5NThwcm9tcHQ1OA"),
    ("memory58session58", "bWVtb3J5NThzZXNzaW9uNTg"),
    ("memory58library58", "bWVtb3J5NThsaWJyYXJ5NTg"),
    ("stream58library58", "c3RyZWFtNThsaWJyYXJ5NTg"),
    ("stream58service58", "c3RyZWFtNThzZXJ2aWNlNTg"),
    ("stream58gateway58", "c3RyZWFtNThnYXRld2F5NTg"),
    ("stream58storage58", "c3RyZWFtNThzdG9yYWdlNTg"),
    ("context58storage58", "Y29udGV4dDU4c3RvcmFnZTU4"),
    ("context58network58", "Y29udGV4dDU4bmV0d29yazU4"),
    ("context58latency58", "Y29udGV4dDU4bGF0ZW5jeTU4"),
    ("context58buffer58", "Y29udGV4dDU4YnVmZmVyNTg"),
    ("knowledge58buffer58", "a25vd2xlZGdlNThidWZmZXI1OA"),
    ("knowledge58queue58", "a25vd2xlZGdlNThxdWV1ZTU4"),
    ("knowledge58worker58", "a25vd2xlZGdlNTh3b3JrZXI1OA"),
    ("knowledge58kernel58", "a25vd2xlZGdlNThrZXJuZWw1OA"),
    ("vector58kernel58", "dmVjdG9yNThrZXJuZWw1OA"),
    ("vector58signal58", "dmVjdG9yNThzaWduYWw1OA"),
    ("vector58packet58", "dmVjdG9yNThwYWNrZXQ1OA"),
    ("vector58router58", "dmVjdG9yNThyb3V0ZXI1OA"),
    ("processor58router58", "cHJvY2Vzc29yNThyb3V0ZXI1OA"),
    ("processor58cluster58", "cHJvY2Vzc29yNThjbHVzdGVyNTg"),
    ("processor58mirror58", "cHJvY2Vzc29yNThtaXJyb3I1OA"),
    ("processor58filter58", "cHJvY2Vzc29yNThmaWx0ZXI1OA"),
    ("reasoning58filter58", "cmVhc29uaW5nNThmaWx0ZXI1OA"),
    ("reasoning58ranking58", "cmVhc29uaW5nNThyYW5raW5nNTg"),
    ("reasoning58encoding58", "cmVhc29uaW5nNThlbmNvZGluZzU4"),
    ("reasoning58mapping58", "cmVhc29uaW5nNThtYXBwaW5nNTg"),
    ("machine58mapping58", "bWFjaGluZTU4bWFwcGluZzU4"),
    ("machine58record58", "bWFjaGluZTU4cmVjb3JkNTg"),
    ("machine58candle58", "bWFjaGluZTU4Y2FuZGxlNTg"),
    ("machine58thread58", "bWFjaGluZTU4dGhyZWFkNTg"),
    ("learning58thread58", "bGVhcm5pbmc1OHRocmVhZDU4"),
    ("learning58kitten58", "bGVhcm5pbmc1OGtpdHRlbjU4"),
    ("learning58sitting58", "bGVhcm5pbmc1OHNpdHRpbmc1OA"),
    ("learning58agent58", "bGVhcm5pbmc1OGFnZW50NTg"),
    ("model58agent58", "bW9kZWw1OGFnZW50NTg"),
    ("model58angle58", "bW9kZWw1OGFuZ2xlNTg"),
    ("model58universe58", "bW9kZWw1OHVuaXZlcnNlNTg"),
    ("model58memory58", "bW9kZWw1OG1lbW9yeTU4"),
    ("token58memory58", "dG9rZW41OG1lbW9yeTU4"),
    ("token58stream58", "dG9rZW41OHN0cmVhbTU4"),
    ("token58context58", "dG9rZW41OGNvbnRleHQ1OA"),
    ("token58knowledge58", "dG9rZW41OGtub3dsZWRnZTU4"),
    ("prompt58knowledge58", "cHJvbXB0NThrbm93bGVkZ2U1OA"),
    ("prompt58vector58", "cHJvbXB0NTh2ZWN0b3I1OA"),
    ("prompt58processor58", "cHJvbXB0NThwcm9jZXNzb3I1OA"),
    ("prompt58reasoning58", "cHJvbXB0NThyZWFzb25pbmc1OA"),
    ("session58reasoning58", "c2Vzc2lvbjU4cmVhc29uaW5nNTg"),
    ("session58machine58", "c2Vzc2lvbjU4bWFjaGluZTU4"),
    ("session58learning58", "c2Vzc2lvbjU4bGVhcm5pbmc1OA"),
    ("session58model58", "c2Vzc2lvbjU4bW9kZWw1OA"),
    ("library58model58", "bGlicmFyeTU4bW9kZWw1OA"),
    ("library58token58", "bGlicmFyeTU4dG9rZW41OA"),
    ("library58prompt58", "bGlicmFyeTU4cHJvbXB0NTg"),
    ("library58session58", "bGlicmFyeTU4c2Vzc2lvbjU4"),
    ("service58session58", "c2VydmljZTU4c2Vzc2lvbjU4"),
    ("service58library58", "c2VydmljZTU4bGlicmFyeTU4"),
    ("service58service58", "c2VydmljZTU4c2VydmljZTU4"),
    ("service58gateway58", "c2VydmljZTU4Z2F0ZXdheTU4"),
    ("gateway58gateway58", "Z2F0ZXdheTU4Z2F0ZXdheTU4"),
    ("gateway58storage58", "Z2F0ZXdheTU4c3RvcmFnZTU4"),
    ("gateway58network58", "Z2F0ZXdheTU4bmV0d29yazU4"),
    ("gateway58latency58", "Z2F0ZXdheTU4bGF0ZW5jeTU4"),
    ("storage58latency58", "c3RvcmFnZTU4bGF0ZW5jeTU4"),
    ("storage58buffer58", "c3RvcmFnZTU4YnVmZmVyNTg"),
    ("storage58queue58", "c3RvcmFnZTU4cXVldWU1OA"),
    ("storage58worker58", "c3RvcmFnZTU4d29ya2VyNTg"),
    ("network58worker58", "bmV0d29yazU4d29ya2VyNTg"),
    ("network58kernel58", "bmV0d29yazU4a2VybmVsNTg"),
    ("network58signal58", "bmV0d29yazU4c2lnbmFsNTg"),
    ("network58packet58", "bmV0d29yazU4cGFja2V0NTg"),
    ("latency58packet58", "bGF0ZW5jeTU4cGFja2V0NTg"),
    ("latency58router58", "bGF0ZW5jeTU4cm91dGVyNTg"),
    ("latency58cluster58", "bGF0ZW5jeTU4Y2x1c3RlcjU4"),
    ("latency58mirror58", "bGF0ZW5jeTU4bWlycm9yNTg"),
    ("buffer58mirror58", "YnVmZmVyNThtaXJyb3I1OA"),
    ("buffer58filter58", "YnVmZmVyNThmaWx0ZXI1OA"),
    ("buffer58ranking58", "YnVmZmVyNThyYW5raW5nNTg"),
    ("buffer58encoding58", "YnVmZmVyNThlbmNvZGluZzU4"),
    ("queue58encoding58", "cXVldWU1OGVuY29kaW5nNTg"),
    ("queue58mapping58", "cXVldWU1OG1hcHBpbmc1OA"),
    ("queue58record58", "cXVldWU1OHJlY29yZDU4"),
    ("queue58candle58", "cXVldWU1OGNhbmRsZTU4"),
    ("worker58candle58", "d29ya2VyNThjYW5kbGU1OA"),
    ("worker58thread58", "d29ya2VyNTh0aHJlYWQ1OA"),
    ("worker58kitten58", "d29ya2VyNThraXR0ZW41OA"),
    ("worker58sitting58", "d29ya2VyNThzaXR0aW5nNTg"),
    ("kernel58sitting58", "a2VybmVsNThzaXR0aW5nNTg"),
    ("kernel58agent58", "a2VybmVsNThhZ2VudDU4"),
    ("kernel58angle58", "a2VybmVsNThhbmdsZTU4"),
    ("kernel58universe58", "a2VybmVsNTh1bml2ZXJzZTU4"),
    ("signal58universe58", "c2lnbmFsNTh1bml2ZXJzZTU4"),
    ("signal58memory58", "c2lnbmFsNThtZW1vcnk1OA"),
    ("signal58stream58", "c2lnbmFsNThzdHJlYW01OA"),
    ("signal58context58", "c2lnbmFsNThjb250ZXh0NTg"),
    ("packet58context58", "cGFja2V0NThjb250ZXh0NTg"),
    ("packet58knowledge58", "cGFja2V0NThrbm93bGVkZ2U1OA"),
    ("packet58vector58", "cGFja2V0NTh2ZWN0b3I1OA"),
    ("packet58processor58", "cGFja2V0NThwcm9jZXNzb3I1OA"),
    ("router58processor58", "cm91dGVyNThwcm9jZXNzb3I1OA"),
    ("router58reasoning58", "cm91dGVyNThyZWFzb25pbmc1OA"),
    ("router58machine58", "cm91dGVyNThtYWNoaW5lNTg"),
    ("router58learning58", "cm91dGVyNThsZWFybmluZzU4"),
    ("cluster58learning58", "Y2x1c3RlcjU4bGVhcm5pbmc1OA"),
    ("cluster58model58", "Y2x1c3RlcjU4bW9kZWw1OA"),
    ("cluster58token58", "Y2x1c3RlcjU4dG9rZW41OA"),
    ("cluster58prompt58", "Y2x1c3RlcjU4cHJvbXB0NTg"),
    ("mirror58prompt58", "bWlycm9yNThwcm9tcHQ1OA"),
    ("mirror58session58", "bWlycm9yNThzZXNzaW9uNTg"),
    ("mirror58library58", "bWlycm9yNThsaWJyYXJ5NTg"),
    ("mirror58service58", "bWlycm9yNThzZXJ2aWNlNTg"),
    ("filter58service58", "ZmlsdGVyNThzZXJ2aWNlNTg"),
    ("filter58gateway58", "ZmlsdGVyNThnYXRld2F5NTg"),
    ("filter58storage58", "ZmlsdGVyNThzdG9yYWdlNTg"),
    ("filter58network58", "ZmlsdGVyNThuZXR3b3JrNTg"),
    ("ranking58network58", "cmFua2luZzU4bmV0d29yazU4"),
    ("ranking58latency58", "cmFua2luZzU4bGF0ZW5jeTU4"),
    ("ranking58buffer58", "cmFua2luZzU4YnVmZmVyNTg"),
    ("ranking58queue58", "cmFua2luZzU4cXVldWU1OA"),
    ("encoding58queue58", "ZW5jb2Rpbmc1OHF1ZXVlNTg"),
    ("encoding58worker58", "ZW5jb2Rpbmc1OHdvcmtlcjU4"),
    ("encoding58kernel58", "ZW5jb2Rpbmc1OGtlcm5lbDU4"),
    ("encoding58signal58", "ZW5jb2Rpbmc1OHNpZ25hbDU4"),
    ("mapping58signal58", "bWFwcGluZzU4c2lnbmFsNTg"),
    ("mapping58packet58", "bWFwcGluZzU4cGFja2V0NTg"),
    ("mapping58router58", "bWFwcGluZzU4cm91dGVyNTg"),
    ("mapping58cluster58", "bWFwcGluZzU4Y2x1c3RlcjU4"),
    ("record58cluster58", "cmVjb3JkNThjbHVzdGVyNTg"),
    ("record58mirror58", "cmVjb3JkNThtaXJyb3I1OA"),
    ("record58filter58", "cmVjb3JkNThmaWx0ZXI1OA"),
    ("record58ranking58", "cmVjb3JkNThyYW5raW5nNTg"),
    ("candle58ranking58", "Y2FuZGxlNThyYW5raW5nNTg"),
    ("candle58encoding58", "Y2FuZGxlNThlbmNvZGluZzU4"),
    ("candle58mapping58", "Y2FuZGxlNThtYXBwaW5nNTg"),
    ("candle58record58", "Y2FuZGxlNThyZWNvcmQ1OA"),
    ("thread58record58", "dGhyZWFkNThyZWNvcmQ1OA"),
    ("thread58candle58", "dGhyZWFkNThjYW5kbGU1OA"),
    ("thread58thread58", "dGhyZWFkNTh0aHJlYWQ1OA"),
    ("thread58kitten58", "dGhyZWFkNThraXR0ZW41OA"),
    (
        "round 58: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNTg6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 58: agentuniverse is a framework for multi agents",
        "cm91bmQgNTg6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 58: knowledge stored as vectors enables retrieval",
        "cm91bmQgNTg6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 58: the processor reads the record then stops",
        "cm91bmQgNTg6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 58: a worker pulls the next task from the queue",
        "cm91bmQgNTg6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 58: signals travel through the network layer",
        "cm91bmQgNTg6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 58: the gateway routes each request by policy",
        "cm91bmQgNTg6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 58: memory grows until the buffer is full",
        "cm91bmQgNTg6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 58: the cluster mirrors every packet twice",
        "cm91bmQgNTg6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 58: ranking uses tokens learned from the corpus",
        "cm91bmQgNTg6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 58: a long session ends when the candle dies",
        "cm91bmQgNTg6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 58: encode the prompt then map the result",
        "cm91bmQgNTg6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 58: the kernel wakes the worker at dawn", "cm91bmQgNTg6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 58: service latency drops after the patch",
        "cm91bmQgNTg6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 58: the library caches every vector it sees",
        "cm91bmQgNTg6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 58: agents argue then the debate resolves",
        "cm91bmQgNTg6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 58: the filter keeps only strong matches",
        "cm91bmQgNTg6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 58: the model answers with a short reply",
        "cm91bmQgNTg6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 58: the recorder stores the reasoning trace",
        "cm91bmQgNTg6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 58: the angel watches the processor run", "cm91bmQgNTg6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 58: angle of the vector decides the match",
        "cm91bmQgNTg6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 58: the candle burns twice as long at night",
        "cm91bmQgNTg6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 58: a mirror of the universe in one line",
        "cm91bmQgNTg6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 58: the queue drains before the storm", "cm91bmQgNTg6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
