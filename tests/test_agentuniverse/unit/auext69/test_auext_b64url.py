"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten69kitten69", "a2l0dGVuNjlraXR0ZW42OQ"),
    ("kitten69sitting69", "a2l0dGVuNjlzaXR0aW5nNjk"),
    ("kitten69agent69", "a2l0dGVuNjlhZ2VudDY5"),
    ("kitten69angle69", "a2l0dGVuNjlhbmdsZTY5"),
    ("sitting69angle69", "c2l0dGluZzY5YW5nbGU2OQ"),
    ("sitting69universe69", "c2l0dGluZzY5dW5pdmVyc2U2OQ"),
    ("sitting69memory69", "c2l0dGluZzY5bWVtb3J5Njk"),
    ("sitting69stream69", "c2l0dGluZzY5c3RyZWFtNjk"),
    ("agent69stream69", "YWdlbnQ2OXN0cmVhbTY5"),
    ("agent69context69", "YWdlbnQ2OWNvbnRleHQ2OQ"),
    ("agent69knowledge69", "YWdlbnQ2OWtub3dsZWRnZTY5"),
    ("agent69vector69", "YWdlbnQ2OXZlY3RvcjY5"),
    ("angle69vector69", "YW5nbGU2OXZlY3RvcjY5"),
    ("angle69processor69", "YW5nbGU2OXByb2Nlc3NvcjY5"),
    ("angle69reasoning69", "YW5nbGU2OXJlYXNvbmluZzY5"),
    ("angle69machine69", "YW5nbGU2OW1hY2hpbmU2OQ"),
    ("universe69machine69", "dW5pdmVyc2U2OW1hY2hpbmU2OQ"),
    ("universe69learning69", "dW5pdmVyc2U2OWxlYXJuaW5nNjk"),
    ("universe69model69", "dW5pdmVyc2U2OW1vZGVsNjk"),
    ("universe69token69", "dW5pdmVyc2U2OXRva2VuNjk"),
    ("memory69token69", "bWVtb3J5Njl0b2tlbjY5"),
    ("memory69prompt69", "bWVtb3J5Njlwcm9tcHQ2OQ"),
    ("memory69session69", "bWVtb3J5NjlzZXNzaW9uNjk"),
    ("memory69library69", "bWVtb3J5NjlsaWJyYXJ5Njk"),
    ("stream69library69", "c3RyZWFtNjlsaWJyYXJ5Njk"),
    ("stream69service69", "c3RyZWFtNjlzZXJ2aWNlNjk"),
    ("stream69gateway69", "c3RyZWFtNjlnYXRld2F5Njk"),
    ("stream69storage69", "c3RyZWFtNjlzdG9yYWdlNjk"),
    ("context69storage69", "Y29udGV4dDY5c3RvcmFnZTY5"),
    ("context69network69", "Y29udGV4dDY5bmV0d29yazY5"),
    ("context69latency69", "Y29udGV4dDY5bGF0ZW5jeTY5"),
    ("context69buffer69", "Y29udGV4dDY5YnVmZmVyNjk"),
    ("knowledge69buffer69", "a25vd2xlZGdlNjlidWZmZXI2OQ"),
    ("knowledge69queue69", "a25vd2xlZGdlNjlxdWV1ZTY5"),
    ("knowledge69worker69", "a25vd2xlZGdlNjl3b3JrZXI2OQ"),
    ("knowledge69kernel69", "a25vd2xlZGdlNjlrZXJuZWw2OQ"),
    ("vector69kernel69", "dmVjdG9yNjlrZXJuZWw2OQ"),
    ("vector69signal69", "dmVjdG9yNjlzaWduYWw2OQ"),
    ("vector69packet69", "dmVjdG9yNjlwYWNrZXQ2OQ"),
    ("vector69router69", "dmVjdG9yNjlyb3V0ZXI2OQ"),
    ("processor69router69", "cHJvY2Vzc29yNjlyb3V0ZXI2OQ"),
    ("processor69cluster69", "cHJvY2Vzc29yNjljbHVzdGVyNjk"),
    ("processor69mirror69", "cHJvY2Vzc29yNjltaXJyb3I2OQ"),
    ("processor69filter69", "cHJvY2Vzc29yNjlmaWx0ZXI2OQ"),
    ("reasoning69filter69", "cmVhc29uaW5nNjlmaWx0ZXI2OQ"),
    ("reasoning69ranking69", "cmVhc29uaW5nNjlyYW5raW5nNjk"),
    ("reasoning69encoding69", "cmVhc29uaW5nNjllbmNvZGluZzY5"),
    ("reasoning69mapping69", "cmVhc29uaW5nNjltYXBwaW5nNjk"),
    ("machine69mapping69", "bWFjaGluZTY5bWFwcGluZzY5"),
    ("machine69record69", "bWFjaGluZTY5cmVjb3JkNjk"),
    ("machine69candle69", "bWFjaGluZTY5Y2FuZGxlNjk"),
    ("machine69thread69", "bWFjaGluZTY5dGhyZWFkNjk"),
    ("learning69thread69", "bGVhcm5pbmc2OXRocmVhZDY5"),
    ("learning69kitten69", "bGVhcm5pbmc2OWtpdHRlbjY5"),
    ("learning69sitting69", "bGVhcm5pbmc2OXNpdHRpbmc2OQ"),
    ("learning69agent69", "bGVhcm5pbmc2OWFnZW50Njk"),
    ("model69agent69", "bW9kZWw2OWFnZW50Njk"),
    ("model69angle69", "bW9kZWw2OWFuZ2xlNjk"),
    ("model69universe69", "bW9kZWw2OXVuaXZlcnNlNjk"),
    ("model69memory69", "bW9kZWw2OW1lbW9yeTY5"),
    ("token69memory69", "dG9rZW42OW1lbW9yeTY5"),
    ("token69stream69", "dG9rZW42OXN0cmVhbTY5"),
    ("token69context69", "dG9rZW42OWNvbnRleHQ2OQ"),
    ("token69knowledge69", "dG9rZW42OWtub3dsZWRnZTY5"),
    ("prompt69knowledge69", "cHJvbXB0Njlrbm93bGVkZ2U2OQ"),
    ("prompt69vector69", "cHJvbXB0Njl2ZWN0b3I2OQ"),
    ("prompt69processor69", "cHJvbXB0Njlwcm9jZXNzb3I2OQ"),
    ("prompt69reasoning69", "cHJvbXB0NjlyZWFzb25pbmc2OQ"),
    ("session69reasoning69", "c2Vzc2lvbjY5cmVhc29uaW5nNjk"),
    ("session69machine69", "c2Vzc2lvbjY5bWFjaGluZTY5"),
    ("session69learning69", "c2Vzc2lvbjY5bGVhcm5pbmc2OQ"),
    ("session69model69", "c2Vzc2lvbjY5bW9kZWw2OQ"),
    ("library69model69", "bGlicmFyeTY5bW9kZWw2OQ"),
    ("library69token69", "bGlicmFyeTY5dG9rZW42OQ"),
    ("library69prompt69", "bGlicmFyeTY5cHJvbXB0Njk"),
    ("library69session69", "bGlicmFyeTY5c2Vzc2lvbjY5"),
    ("service69session69", "c2VydmljZTY5c2Vzc2lvbjY5"),
    ("service69library69", "c2VydmljZTY5bGlicmFyeTY5"),
    ("service69service69", "c2VydmljZTY5c2VydmljZTY5"),
    ("service69gateway69", "c2VydmljZTY5Z2F0ZXdheTY5"),
    ("gateway69gateway69", "Z2F0ZXdheTY5Z2F0ZXdheTY5"),
    ("gateway69storage69", "Z2F0ZXdheTY5c3RvcmFnZTY5"),
    ("gateway69network69", "Z2F0ZXdheTY5bmV0d29yazY5"),
    ("gateway69latency69", "Z2F0ZXdheTY5bGF0ZW5jeTY5"),
    ("storage69latency69", "c3RvcmFnZTY5bGF0ZW5jeTY5"),
    ("storage69buffer69", "c3RvcmFnZTY5YnVmZmVyNjk"),
    ("storage69queue69", "c3RvcmFnZTY5cXVldWU2OQ"),
    ("storage69worker69", "c3RvcmFnZTY5d29ya2VyNjk"),
    ("network69worker69", "bmV0d29yazY5d29ya2VyNjk"),
    ("network69kernel69", "bmV0d29yazY5a2VybmVsNjk"),
    ("network69signal69", "bmV0d29yazY5c2lnbmFsNjk"),
    ("network69packet69", "bmV0d29yazY5cGFja2V0Njk"),
    ("latency69packet69", "bGF0ZW5jeTY5cGFja2V0Njk"),
    ("latency69router69", "bGF0ZW5jeTY5cm91dGVyNjk"),
    ("latency69cluster69", "bGF0ZW5jeTY5Y2x1c3RlcjY5"),
    ("latency69mirror69", "bGF0ZW5jeTY5bWlycm9yNjk"),
    ("buffer69mirror69", "YnVmZmVyNjltaXJyb3I2OQ"),
    ("buffer69filter69", "YnVmZmVyNjlmaWx0ZXI2OQ"),
    ("buffer69ranking69", "YnVmZmVyNjlyYW5raW5nNjk"),
    ("buffer69encoding69", "YnVmZmVyNjllbmNvZGluZzY5"),
    ("queue69encoding69", "cXVldWU2OWVuY29kaW5nNjk"),
    ("queue69mapping69", "cXVldWU2OW1hcHBpbmc2OQ"),
    ("queue69record69", "cXVldWU2OXJlY29yZDY5"),
    ("queue69candle69", "cXVldWU2OWNhbmRsZTY5"),
    ("worker69candle69", "d29ya2VyNjljYW5kbGU2OQ"),
    ("worker69thread69", "d29ya2VyNjl0aHJlYWQ2OQ"),
    ("worker69kitten69", "d29ya2VyNjlraXR0ZW42OQ"),
    ("worker69sitting69", "d29ya2VyNjlzaXR0aW5nNjk"),
    ("kernel69sitting69", "a2VybmVsNjlzaXR0aW5nNjk"),
    ("kernel69agent69", "a2VybmVsNjlhZ2VudDY5"),
    ("kernel69angle69", "a2VybmVsNjlhbmdsZTY5"),
    ("kernel69universe69", "a2VybmVsNjl1bml2ZXJzZTY5"),
    ("signal69universe69", "c2lnbmFsNjl1bml2ZXJzZTY5"),
    ("signal69memory69", "c2lnbmFsNjltZW1vcnk2OQ"),
    ("signal69stream69", "c2lnbmFsNjlzdHJlYW02OQ"),
    ("signal69context69", "c2lnbmFsNjljb250ZXh0Njk"),
    ("packet69context69", "cGFja2V0Njljb250ZXh0Njk"),
    ("packet69knowledge69", "cGFja2V0Njlrbm93bGVkZ2U2OQ"),
    ("packet69vector69", "cGFja2V0Njl2ZWN0b3I2OQ"),
    ("packet69processor69", "cGFja2V0Njlwcm9jZXNzb3I2OQ"),
    ("router69processor69", "cm91dGVyNjlwcm9jZXNzb3I2OQ"),
    ("router69reasoning69", "cm91dGVyNjlyZWFzb25pbmc2OQ"),
    ("router69machine69", "cm91dGVyNjltYWNoaW5lNjk"),
    ("router69learning69", "cm91dGVyNjlsZWFybmluZzY5"),
    ("cluster69learning69", "Y2x1c3RlcjY5bGVhcm5pbmc2OQ"),
    ("cluster69model69", "Y2x1c3RlcjY5bW9kZWw2OQ"),
    ("cluster69token69", "Y2x1c3RlcjY5dG9rZW42OQ"),
    ("cluster69prompt69", "Y2x1c3RlcjY5cHJvbXB0Njk"),
    ("mirror69prompt69", "bWlycm9yNjlwcm9tcHQ2OQ"),
    ("mirror69session69", "bWlycm9yNjlzZXNzaW9uNjk"),
    ("mirror69library69", "bWlycm9yNjlsaWJyYXJ5Njk"),
    ("mirror69service69", "bWlycm9yNjlzZXJ2aWNlNjk"),
    ("filter69service69", "ZmlsdGVyNjlzZXJ2aWNlNjk"),
    ("filter69gateway69", "ZmlsdGVyNjlnYXRld2F5Njk"),
    ("filter69storage69", "ZmlsdGVyNjlzdG9yYWdlNjk"),
    ("filter69network69", "ZmlsdGVyNjluZXR3b3JrNjk"),
    ("ranking69network69", "cmFua2luZzY5bmV0d29yazY5"),
    ("ranking69latency69", "cmFua2luZzY5bGF0ZW5jeTY5"),
    ("ranking69buffer69", "cmFua2luZzY5YnVmZmVyNjk"),
    ("ranking69queue69", "cmFua2luZzY5cXVldWU2OQ"),
    ("encoding69queue69", "ZW5jb2Rpbmc2OXF1ZXVlNjk"),
    ("encoding69worker69", "ZW5jb2Rpbmc2OXdvcmtlcjY5"),
    ("encoding69kernel69", "ZW5jb2Rpbmc2OWtlcm5lbDY5"),
    ("encoding69signal69", "ZW5jb2Rpbmc2OXNpZ25hbDY5"),
    ("mapping69signal69", "bWFwcGluZzY5c2lnbmFsNjk"),
    ("mapping69packet69", "bWFwcGluZzY5cGFja2V0Njk"),
    ("mapping69router69", "bWFwcGluZzY5cm91dGVyNjk"),
    ("mapping69cluster69", "bWFwcGluZzY5Y2x1c3RlcjY5"),
    ("record69cluster69", "cmVjb3JkNjljbHVzdGVyNjk"),
    ("record69mirror69", "cmVjb3JkNjltaXJyb3I2OQ"),
    ("record69filter69", "cmVjb3JkNjlmaWx0ZXI2OQ"),
    ("record69ranking69", "cmVjb3JkNjlyYW5raW5nNjk"),
    ("candle69ranking69", "Y2FuZGxlNjlyYW5raW5nNjk"),
    ("candle69encoding69", "Y2FuZGxlNjllbmNvZGluZzY5"),
    ("candle69mapping69", "Y2FuZGxlNjltYXBwaW5nNjk"),
    ("candle69record69", "Y2FuZGxlNjlyZWNvcmQ2OQ"),
    ("thread69record69", "dGhyZWFkNjlyZWNvcmQ2OQ"),
    ("thread69candle69", "dGhyZWFkNjljYW5kbGU2OQ"),
    ("thread69thread69", "dGhyZWFkNjl0aHJlYWQ2OQ"),
    ("thread69kitten69", "dGhyZWFkNjlraXR0ZW42OQ"),
    (
        "round 69: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNjk6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 69: agentuniverse is a framework for multi agents",
        "cm91bmQgNjk6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 69: knowledge stored as vectors enables retrieval",
        "cm91bmQgNjk6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 69: the processor reads the record then stops",
        "cm91bmQgNjk6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 69: a worker pulls the next task from the queue",
        "cm91bmQgNjk6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 69: signals travel through the network layer",
        "cm91bmQgNjk6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 69: the gateway routes each request by policy",
        "cm91bmQgNjk6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 69: memory grows until the buffer is full",
        "cm91bmQgNjk6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 69: the cluster mirrors every packet twice",
        "cm91bmQgNjk6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 69: ranking uses tokens learned from the corpus",
        "cm91bmQgNjk6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 69: a long session ends when the candle dies",
        "cm91bmQgNjk6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 69: encode the prompt then map the result",
        "cm91bmQgNjk6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 69: the kernel wakes the worker at dawn", "cm91bmQgNjk6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 69: service latency drops after the patch",
        "cm91bmQgNjk6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 69: the library caches every vector it sees",
        "cm91bmQgNjk6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 69: agents argue then the debate resolves",
        "cm91bmQgNjk6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 69: the filter keeps only strong matches",
        "cm91bmQgNjk6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 69: the model answers with a short reply",
        "cm91bmQgNjk6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 69: the recorder stores the reasoning trace",
        "cm91bmQgNjk6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 69: the angel watches the processor run", "cm91bmQgNjk6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 69: angle of the vector decides the match",
        "cm91bmQgNjk6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 69: the candle burns twice as long at night",
        "cm91bmQgNjk6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 69: a mirror of the universe in one line",
        "cm91bmQgNjk6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 69: the queue drains before the storm", "cm91bmQgNjk6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
