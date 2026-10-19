"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten67kitten67", "a2l0dGVuNjdraXR0ZW42Nw"),
    ("kitten67sitting67", "a2l0dGVuNjdzaXR0aW5nNjc"),
    ("kitten67agent67", "a2l0dGVuNjdhZ2VudDY3"),
    ("kitten67angle67", "a2l0dGVuNjdhbmdsZTY3"),
    ("sitting67angle67", "c2l0dGluZzY3YW5nbGU2Nw"),
    ("sitting67universe67", "c2l0dGluZzY3dW5pdmVyc2U2Nw"),
    ("sitting67memory67", "c2l0dGluZzY3bWVtb3J5Njc"),
    ("sitting67stream67", "c2l0dGluZzY3c3RyZWFtNjc"),
    ("agent67stream67", "YWdlbnQ2N3N0cmVhbTY3"),
    ("agent67context67", "YWdlbnQ2N2NvbnRleHQ2Nw"),
    ("agent67knowledge67", "YWdlbnQ2N2tub3dsZWRnZTY3"),
    ("agent67vector67", "YWdlbnQ2N3ZlY3RvcjY3"),
    ("angle67vector67", "YW5nbGU2N3ZlY3RvcjY3"),
    ("angle67processor67", "YW5nbGU2N3Byb2Nlc3NvcjY3"),
    ("angle67reasoning67", "YW5nbGU2N3JlYXNvbmluZzY3"),
    ("angle67machine67", "YW5nbGU2N21hY2hpbmU2Nw"),
    ("universe67machine67", "dW5pdmVyc2U2N21hY2hpbmU2Nw"),
    ("universe67learning67", "dW5pdmVyc2U2N2xlYXJuaW5nNjc"),
    ("universe67model67", "dW5pdmVyc2U2N21vZGVsNjc"),
    ("universe67token67", "dW5pdmVyc2U2N3Rva2VuNjc"),
    ("memory67token67", "bWVtb3J5Njd0b2tlbjY3"),
    ("memory67prompt67", "bWVtb3J5Njdwcm9tcHQ2Nw"),
    ("memory67session67", "bWVtb3J5NjdzZXNzaW9uNjc"),
    ("memory67library67", "bWVtb3J5NjdsaWJyYXJ5Njc"),
    ("stream67library67", "c3RyZWFtNjdsaWJyYXJ5Njc"),
    ("stream67service67", "c3RyZWFtNjdzZXJ2aWNlNjc"),
    ("stream67gateway67", "c3RyZWFtNjdnYXRld2F5Njc"),
    ("stream67storage67", "c3RyZWFtNjdzdG9yYWdlNjc"),
    ("context67storage67", "Y29udGV4dDY3c3RvcmFnZTY3"),
    ("context67network67", "Y29udGV4dDY3bmV0d29yazY3"),
    ("context67latency67", "Y29udGV4dDY3bGF0ZW5jeTY3"),
    ("context67buffer67", "Y29udGV4dDY3YnVmZmVyNjc"),
    ("knowledge67buffer67", "a25vd2xlZGdlNjdidWZmZXI2Nw"),
    ("knowledge67queue67", "a25vd2xlZGdlNjdxdWV1ZTY3"),
    ("knowledge67worker67", "a25vd2xlZGdlNjd3b3JrZXI2Nw"),
    ("knowledge67kernel67", "a25vd2xlZGdlNjdrZXJuZWw2Nw"),
    ("vector67kernel67", "dmVjdG9yNjdrZXJuZWw2Nw"),
    ("vector67signal67", "dmVjdG9yNjdzaWduYWw2Nw"),
    ("vector67packet67", "dmVjdG9yNjdwYWNrZXQ2Nw"),
    ("vector67router67", "dmVjdG9yNjdyb3V0ZXI2Nw"),
    ("processor67router67", "cHJvY2Vzc29yNjdyb3V0ZXI2Nw"),
    ("processor67cluster67", "cHJvY2Vzc29yNjdjbHVzdGVyNjc"),
    ("processor67mirror67", "cHJvY2Vzc29yNjdtaXJyb3I2Nw"),
    ("processor67filter67", "cHJvY2Vzc29yNjdmaWx0ZXI2Nw"),
    ("reasoning67filter67", "cmVhc29uaW5nNjdmaWx0ZXI2Nw"),
    ("reasoning67ranking67", "cmVhc29uaW5nNjdyYW5raW5nNjc"),
    ("reasoning67encoding67", "cmVhc29uaW5nNjdlbmNvZGluZzY3"),
    ("reasoning67mapping67", "cmVhc29uaW5nNjdtYXBwaW5nNjc"),
    ("machine67mapping67", "bWFjaGluZTY3bWFwcGluZzY3"),
    ("machine67record67", "bWFjaGluZTY3cmVjb3JkNjc"),
    ("machine67candle67", "bWFjaGluZTY3Y2FuZGxlNjc"),
    ("machine67thread67", "bWFjaGluZTY3dGhyZWFkNjc"),
    ("learning67thread67", "bGVhcm5pbmc2N3RocmVhZDY3"),
    ("learning67kitten67", "bGVhcm5pbmc2N2tpdHRlbjY3"),
    ("learning67sitting67", "bGVhcm5pbmc2N3NpdHRpbmc2Nw"),
    ("learning67agent67", "bGVhcm5pbmc2N2FnZW50Njc"),
    ("model67agent67", "bW9kZWw2N2FnZW50Njc"),
    ("model67angle67", "bW9kZWw2N2FuZ2xlNjc"),
    ("model67universe67", "bW9kZWw2N3VuaXZlcnNlNjc"),
    ("model67memory67", "bW9kZWw2N21lbW9yeTY3"),
    ("token67memory67", "dG9rZW42N21lbW9yeTY3"),
    ("token67stream67", "dG9rZW42N3N0cmVhbTY3"),
    ("token67context67", "dG9rZW42N2NvbnRleHQ2Nw"),
    ("token67knowledge67", "dG9rZW42N2tub3dsZWRnZTY3"),
    ("prompt67knowledge67", "cHJvbXB0Njdrbm93bGVkZ2U2Nw"),
    ("prompt67vector67", "cHJvbXB0Njd2ZWN0b3I2Nw"),
    ("prompt67processor67", "cHJvbXB0Njdwcm9jZXNzb3I2Nw"),
    ("prompt67reasoning67", "cHJvbXB0NjdyZWFzb25pbmc2Nw"),
    ("session67reasoning67", "c2Vzc2lvbjY3cmVhc29uaW5nNjc"),
    ("session67machine67", "c2Vzc2lvbjY3bWFjaGluZTY3"),
    ("session67learning67", "c2Vzc2lvbjY3bGVhcm5pbmc2Nw"),
    ("session67model67", "c2Vzc2lvbjY3bW9kZWw2Nw"),
    ("library67model67", "bGlicmFyeTY3bW9kZWw2Nw"),
    ("library67token67", "bGlicmFyeTY3dG9rZW42Nw"),
    ("library67prompt67", "bGlicmFyeTY3cHJvbXB0Njc"),
    ("library67session67", "bGlicmFyeTY3c2Vzc2lvbjY3"),
    ("service67session67", "c2VydmljZTY3c2Vzc2lvbjY3"),
    ("service67library67", "c2VydmljZTY3bGlicmFyeTY3"),
    ("service67service67", "c2VydmljZTY3c2VydmljZTY3"),
    ("service67gateway67", "c2VydmljZTY3Z2F0ZXdheTY3"),
    ("gateway67gateway67", "Z2F0ZXdheTY3Z2F0ZXdheTY3"),
    ("gateway67storage67", "Z2F0ZXdheTY3c3RvcmFnZTY3"),
    ("gateway67network67", "Z2F0ZXdheTY3bmV0d29yazY3"),
    ("gateway67latency67", "Z2F0ZXdheTY3bGF0ZW5jeTY3"),
    ("storage67latency67", "c3RvcmFnZTY3bGF0ZW5jeTY3"),
    ("storage67buffer67", "c3RvcmFnZTY3YnVmZmVyNjc"),
    ("storage67queue67", "c3RvcmFnZTY3cXVldWU2Nw"),
    ("storage67worker67", "c3RvcmFnZTY3d29ya2VyNjc"),
    ("network67worker67", "bmV0d29yazY3d29ya2VyNjc"),
    ("network67kernel67", "bmV0d29yazY3a2VybmVsNjc"),
    ("network67signal67", "bmV0d29yazY3c2lnbmFsNjc"),
    ("network67packet67", "bmV0d29yazY3cGFja2V0Njc"),
    ("latency67packet67", "bGF0ZW5jeTY3cGFja2V0Njc"),
    ("latency67router67", "bGF0ZW5jeTY3cm91dGVyNjc"),
    ("latency67cluster67", "bGF0ZW5jeTY3Y2x1c3RlcjY3"),
    ("latency67mirror67", "bGF0ZW5jeTY3bWlycm9yNjc"),
    ("buffer67mirror67", "YnVmZmVyNjdtaXJyb3I2Nw"),
    ("buffer67filter67", "YnVmZmVyNjdmaWx0ZXI2Nw"),
    ("buffer67ranking67", "YnVmZmVyNjdyYW5raW5nNjc"),
    ("buffer67encoding67", "YnVmZmVyNjdlbmNvZGluZzY3"),
    ("queue67encoding67", "cXVldWU2N2VuY29kaW5nNjc"),
    ("queue67mapping67", "cXVldWU2N21hcHBpbmc2Nw"),
    ("queue67record67", "cXVldWU2N3JlY29yZDY3"),
    ("queue67candle67", "cXVldWU2N2NhbmRsZTY3"),
    ("worker67candle67", "d29ya2VyNjdjYW5kbGU2Nw"),
    ("worker67thread67", "d29ya2VyNjd0aHJlYWQ2Nw"),
    ("worker67kitten67", "d29ya2VyNjdraXR0ZW42Nw"),
    ("worker67sitting67", "d29ya2VyNjdzaXR0aW5nNjc"),
    ("kernel67sitting67", "a2VybmVsNjdzaXR0aW5nNjc"),
    ("kernel67agent67", "a2VybmVsNjdhZ2VudDY3"),
    ("kernel67angle67", "a2VybmVsNjdhbmdsZTY3"),
    ("kernel67universe67", "a2VybmVsNjd1bml2ZXJzZTY3"),
    ("signal67universe67", "c2lnbmFsNjd1bml2ZXJzZTY3"),
    ("signal67memory67", "c2lnbmFsNjdtZW1vcnk2Nw"),
    ("signal67stream67", "c2lnbmFsNjdzdHJlYW02Nw"),
    ("signal67context67", "c2lnbmFsNjdjb250ZXh0Njc"),
    ("packet67context67", "cGFja2V0Njdjb250ZXh0Njc"),
    ("packet67knowledge67", "cGFja2V0Njdrbm93bGVkZ2U2Nw"),
    ("packet67vector67", "cGFja2V0Njd2ZWN0b3I2Nw"),
    ("packet67processor67", "cGFja2V0Njdwcm9jZXNzb3I2Nw"),
    ("router67processor67", "cm91dGVyNjdwcm9jZXNzb3I2Nw"),
    ("router67reasoning67", "cm91dGVyNjdyZWFzb25pbmc2Nw"),
    ("router67machine67", "cm91dGVyNjdtYWNoaW5lNjc"),
    ("router67learning67", "cm91dGVyNjdsZWFybmluZzY3"),
    ("cluster67learning67", "Y2x1c3RlcjY3bGVhcm5pbmc2Nw"),
    ("cluster67model67", "Y2x1c3RlcjY3bW9kZWw2Nw"),
    ("cluster67token67", "Y2x1c3RlcjY3dG9rZW42Nw"),
    ("cluster67prompt67", "Y2x1c3RlcjY3cHJvbXB0Njc"),
    ("mirror67prompt67", "bWlycm9yNjdwcm9tcHQ2Nw"),
    ("mirror67session67", "bWlycm9yNjdzZXNzaW9uNjc"),
    ("mirror67library67", "bWlycm9yNjdsaWJyYXJ5Njc"),
    ("mirror67service67", "bWlycm9yNjdzZXJ2aWNlNjc"),
    ("filter67service67", "ZmlsdGVyNjdzZXJ2aWNlNjc"),
    ("filter67gateway67", "ZmlsdGVyNjdnYXRld2F5Njc"),
    ("filter67storage67", "ZmlsdGVyNjdzdG9yYWdlNjc"),
    ("filter67network67", "ZmlsdGVyNjduZXR3b3JrNjc"),
    ("ranking67network67", "cmFua2luZzY3bmV0d29yazY3"),
    ("ranking67latency67", "cmFua2luZzY3bGF0ZW5jeTY3"),
    ("ranking67buffer67", "cmFua2luZzY3YnVmZmVyNjc"),
    ("ranking67queue67", "cmFua2luZzY3cXVldWU2Nw"),
    ("encoding67queue67", "ZW5jb2Rpbmc2N3F1ZXVlNjc"),
    ("encoding67worker67", "ZW5jb2Rpbmc2N3dvcmtlcjY3"),
    ("encoding67kernel67", "ZW5jb2Rpbmc2N2tlcm5lbDY3"),
    ("encoding67signal67", "ZW5jb2Rpbmc2N3NpZ25hbDY3"),
    ("mapping67signal67", "bWFwcGluZzY3c2lnbmFsNjc"),
    ("mapping67packet67", "bWFwcGluZzY3cGFja2V0Njc"),
    ("mapping67router67", "bWFwcGluZzY3cm91dGVyNjc"),
    ("mapping67cluster67", "bWFwcGluZzY3Y2x1c3RlcjY3"),
    ("record67cluster67", "cmVjb3JkNjdjbHVzdGVyNjc"),
    ("record67mirror67", "cmVjb3JkNjdtaXJyb3I2Nw"),
    ("record67filter67", "cmVjb3JkNjdmaWx0ZXI2Nw"),
    ("record67ranking67", "cmVjb3JkNjdyYW5raW5nNjc"),
    ("candle67ranking67", "Y2FuZGxlNjdyYW5raW5nNjc"),
    ("candle67encoding67", "Y2FuZGxlNjdlbmNvZGluZzY3"),
    ("candle67mapping67", "Y2FuZGxlNjdtYXBwaW5nNjc"),
    ("candle67record67", "Y2FuZGxlNjdyZWNvcmQ2Nw"),
    ("thread67record67", "dGhyZWFkNjdyZWNvcmQ2Nw"),
    ("thread67candle67", "dGhyZWFkNjdjYW5kbGU2Nw"),
    ("thread67thread67", "dGhyZWFkNjd0aHJlYWQ2Nw"),
    ("thread67kitten67", "dGhyZWFkNjdraXR0ZW42Nw"),
    (
        "round 67: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNjc6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 67: agentuniverse is a framework for multi agents",
        "cm91bmQgNjc6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 67: knowledge stored as vectors enables retrieval",
        "cm91bmQgNjc6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 67: the processor reads the record then stops",
        "cm91bmQgNjc6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 67: a worker pulls the next task from the queue",
        "cm91bmQgNjc6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 67: signals travel through the network layer",
        "cm91bmQgNjc6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 67: the gateway routes each request by policy",
        "cm91bmQgNjc6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 67: memory grows until the buffer is full",
        "cm91bmQgNjc6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 67: the cluster mirrors every packet twice",
        "cm91bmQgNjc6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 67: ranking uses tokens learned from the corpus",
        "cm91bmQgNjc6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 67: a long session ends when the candle dies",
        "cm91bmQgNjc6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 67: encode the prompt then map the result",
        "cm91bmQgNjc6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 67: the kernel wakes the worker at dawn", "cm91bmQgNjc6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 67: service latency drops after the patch",
        "cm91bmQgNjc6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 67: the library caches every vector it sees",
        "cm91bmQgNjc6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 67: agents argue then the debate resolves",
        "cm91bmQgNjc6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 67: the filter keeps only strong matches",
        "cm91bmQgNjc6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 67: the model answers with a short reply",
        "cm91bmQgNjc6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 67: the recorder stores the reasoning trace",
        "cm91bmQgNjc6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 67: the angel watches the processor run", "cm91bmQgNjc6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 67: angle of the vector decides the match",
        "cm91bmQgNjc6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 67: the candle burns twice as long at night",
        "cm91bmQgNjc6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 67: a mirror of the universe in one line",
        "cm91bmQgNjc6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 67: the queue drains before the storm", "cm91bmQgNjc6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
