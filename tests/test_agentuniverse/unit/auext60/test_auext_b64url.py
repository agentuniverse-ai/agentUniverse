"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten60kitten60", "a2l0dGVuNjBraXR0ZW42MA"),
    ("kitten60sitting60", "a2l0dGVuNjBzaXR0aW5nNjA"),
    ("kitten60agent60", "a2l0dGVuNjBhZ2VudDYw"),
    ("kitten60angle60", "a2l0dGVuNjBhbmdsZTYw"),
    ("sitting60angle60", "c2l0dGluZzYwYW5nbGU2MA"),
    ("sitting60universe60", "c2l0dGluZzYwdW5pdmVyc2U2MA"),
    ("sitting60memory60", "c2l0dGluZzYwbWVtb3J5NjA"),
    ("sitting60stream60", "c2l0dGluZzYwc3RyZWFtNjA"),
    ("agent60stream60", "YWdlbnQ2MHN0cmVhbTYw"),
    ("agent60context60", "YWdlbnQ2MGNvbnRleHQ2MA"),
    ("agent60knowledge60", "YWdlbnQ2MGtub3dsZWRnZTYw"),
    ("agent60vector60", "YWdlbnQ2MHZlY3RvcjYw"),
    ("angle60vector60", "YW5nbGU2MHZlY3RvcjYw"),
    ("angle60processor60", "YW5nbGU2MHByb2Nlc3NvcjYw"),
    ("angle60reasoning60", "YW5nbGU2MHJlYXNvbmluZzYw"),
    ("angle60machine60", "YW5nbGU2MG1hY2hpbmU2MA"),
    ("universe60machine60", "dW5pdmVyc2U2MG1hY2hpbmU2MA"),
    ("universe60learning60", "dW5pdmVyc2U2MGxlYXJuaW5nNjA"),
    ("universe60model60", "dW5pdmVyc2U2MG1vZGVsNjA"),
    ("universe60token60", "dW5pdmVyc2U2MHRva2VuNjA"),
    ("memory60token60", "bWVtb3J5NjB0b2tlbjYw"),
    ("memory60prompt60", "bWVtb3J5NjBwcm9tcHQ2MA"),
    ("memory60session60", "bWVtb3J5NjBzZXNzaW9uNjA"),
    ("memory60library60", "bWVtb3J5NjBsaWJyYXJ5NjA"),
    ("stream60library60", "c3RyZWFtNjBsaWJyYXJ5NjA"),
    ("stream60service60", "c3RyZWFtNjBzZXJ2aWNlNjA"),
    ("stream60gateway60", "c3RyZWFtNjBnYXRld2F5NjA"),
    ("stream60storage60", "c3RyZWFtNjBzdG9yYWdlNjA"),
    ("context60storage60", "Y29udGV4dDYwc3RvcmFnZTYw"),
    ("context60network60", "Y29udGV4dDYwbmV0d29yazYw"),
    ("context60latency60", "Y29udGV4dDYwbGF0ZW5jeTYw"),
    ("context60buffer60", "Y29udGV4dDYwYnVmZmVyNjA"),
    ("knowledge60buffer60", "a25vd2xlZGdlNjBidWZmZXI2MA"),
    ("knowledge60queue60", "a25vd2xlZGdlNjBxdWV1ZTYw"),
    ("knowledge60worker60", "a25vd2xlZGdlNjB3b3JrZXI2MA"),
    ("knowledge60kernel60", "a25vd2xlZGdlNjBrZXJuZWw2MA"),
    ("vector60kernel60", "dmVjdG9yNjBrZXJuZWw2MA"),
    ("vector60signal60", "dmVjdG9yNjBzaWduYWw2MA"),
    ("vector60packet60", "dmVjdG9yNjBwYWNrZXQ2MA"),
    ("vector60router60", "dmVjdG9yNjByb3V0ZXI2MA"),
    ("processor60router60", "cHJvY2Vzc29yNjByb3V0ZXI2MA"),
    ("processor60cluster60", "cHJvY2Vzc29yNjBjbHVzdGVyNjA"),
    ("processor60mirror60", "cHJvY2Vzc29yNjBtaXJyb3I2MA"),
    ("processor60filter60", "cHJvY2Vzc29yNjBmaWx0ZXI2MA"),
    ("reasoning60filter60", "cmVhc29uaW5nNjBmaWx0ZXI2MA"),
    ("reasoning60ranking60", "cmVhc29uaW5nNjByYW5raW5nNjA"),
    ("reasoning60encoding60", "cmVhc29uaW5nNjBlbmNvZGluZzYw"),
    ("reasoning60mapping60", "cmVhc29uaW5nNjBtYXBwaW5nNjA"),
    ("machine60mapping60", "bWFjaGluZTYwbWFwcGluZzYw"),
    ("machine60record60", "bWFjaGluZTYwcmVjb3JkNjA"),
    ("machine60candle60", "bWFjaGluZTYwY2FuZGxlNjA"),
    ("machine60thread60", "bWFjaGluZTYwdGhyZWFkNjA"),
    ("learning60thread60", "bGVhcm5pbmc2MHRocmVhZDYw"),
    ("learning60kitten60", "bGVhcm5pbmc2MGtpdHRlbjYw"),
    ("learning60sitting60", "bGVhcm5pbmc2MHNpdHRpbmc2MA"),
    ("learning60agent60", "bGVhcm5pbmc2MGFnZW50NjA"),
    ("model60agent60", "bW9kZWw2MGFnZW50NjA"),
    ("model60angle60", "bW9kZWw2MGFuZ2xlNjA"),
    ("model60universe60", "bW9kZWw2MHVuaXZlcnNlNjA"),
    ("model60memory60", "bW9kZWw2MG1lbW9yeTYw"),
    ("token60memory60", "dG9rZW42MG1lbW9yeTYw"),
    ("token60stream60", "dG9rZW42MHN0cmVhbTYw"),
    ("token60context60", "dG9rZW42MGNvbnRleHQ2MA"),
    ("token60knowledge60", "dG9rZW42MGtub3dsZWRnZTYw"),
    ("prompt60knowledge60", "cHJvbXB0NjBrbm93bGVkZ2U2MA"),
    ("prompt60vector60", "cHJvbXB0NjB2ZWN0b3I2MA"),
    ("prompt60processor60", "cHJvbXB0NjBwcm9jZXNzb3I2MA"),
    ("prompt60reasoning60", "cHJvbXB0NjByZWFzb25pbmc2MA"),
    ("session60reasoning60", "c2Vzc2lvbjYwcmVhc29uaW5nNjA"),
    ("session60machine60", "c2Vzc2lvbjYwbWFjaGluZTYw"),
    ("session60learning60", "c2Vzc2lvbjYwbGVhcm5pbmc2MA"),
    ("session60model60", "c2Vzc2lvbjYwbW9kZWw2MA"),
    ("library60model60", "bGlicmFyeTYwbW9kZWw2MA"),
    ("library60token60", "bGlicmFyeTYwdG9rZW42MA"),
    ("library60prompt60", "bGlicmFyeTYwcHJvbXB0NjA"),
    ("library60session60", "bGlicmFyeTYwc2Vzc2lvbjYw"),
    ("service60session60", "c2VydmljZTYwc2Vzc2lvbjYw"),
    ("service60library60", "c2VydmljZTYwbGlicmFyeTYw"),
    ("service60service60", "c2VydmljZTYwc2VydmljZTYw"),
    ("service60gateway60", "c2VydmljZTYwZ2F0ZXdheTYw"),
    ("gateway60gateway60", "Z2F0ZXdheTYwZ2F0ZXdheTYw"),
    ("gateway60storage60", "Z2F0ZXdheTYwc3RvcmFnZTYw"),
    ("gateway60network60", "Z2F0ZXdheTYwbmV0d29yazYw"),
    ("gateway60latency60", "Z2F0ZXdheTYwbGF0ZW5jeTYw"),
    ("storage60latency60", "c3RvcmFnZTYwbGF0ZW5jeTYw"),
    ("storage60buffer60", "c3RvcmFnZTYwYnVmZmVyNjA"),
    ("storage60queue60", "c3RvcmFnZTYwcXVldWU2MA"),
    ("storage60worker60", "c3RvcmFnZTYwd29ya2VyNjA"),
    ("network60worker60", "bmV0d29yazYwd29ya2VyNjA"),
    ("network60kernel60", "bmV0d29yazYwa2VybmVsNjA"),
    ("network60signal60", "bmV0d29yazYwc2lnbmFsNjA"),
    ("network60packet60", "bmV0d29yazYwcGFja2V0NjA"),
    ("latency60packet60", "bGF0ZW5jeTYwcGFja2V0NjA"),
    ("latency60router60", "bGF0ZW5jeTYwcm91dGVyNjA"),
    ("latency60cluster60", "bGF0ZW5jeTYwY2x1c3RlcjYw"),
    ("latency60mirror60", "bGF0ZW5jeTYwbWlycm9yNjA"),
    ("buffer60mirror60", "YnVmZmVyNjBtaXJyb3I2MA"),
    ("buffer60filter60", "YnVmZmVyNjBmaWx0ZXI2MA"),
    ("buffer60ranking60", "YnVmZmVyNjByYW5raW5nNjA"),
    ("buffer60encoding60", "YnVmZmVyNjBlbmNvZGluZzYw"),
    ("queue60encoding60", "cXVldWU2MGVuY29kaW5nNjA"),
    ("queue60mapping60", "cXVldWU2MG1hcHBpbmc2MA"),
    ("queue60record60", "cXVldWU2MHJlY29yZDYw"),
    ("queue60candle60", "cXVldWU2MGNhbmRsZTYw"),
    ("worker60candle60", "d29ya2VyNjBjYW5kbGU2MA"),
    ("worker60thread60", "d29ya2VyNjB0aHJlYWQ2MA"),
    ("worker60kitten60", "d29ya2VyNjBraXR0ZW42MA"),
    ("worker60sitting60", "d29ya2VyNjBzaXR0aW5nNjA"),
    ("kernel60sitting60", "a2VybmVsNjBzaXR0aW5nNjA"),
    ("kernel60agent60", "a2VybmVsNjBhZ2VudDYw"),
    ("kernel60angle60", "a2VybmVsNjBhbmdsZTYw"),
    ("kernel60universe60", "a2VybmVsNjB1bml2ZXJzZTYw"),
    ("signal60universe60", "c2lnbmFsNjB1bml2ZXJzZTYw"),
    ("signal60memory60", "c2lnbmFsNjBtZW1vcnk2MA"),
    ("signal60stream60", "c2lnbmFsNjBzdHJlYW02MA"),
    ("signal60context60", "c2lnbmFsNjBjb250ZXh0NjA"),
    ("packet60context60", "cGFja2V0NjBjb250ZXh0NjA"),
    ("packet60knowledge60", "cGFja2V0NjBrbm93bGVkZ2U2MA"),
    ("packet60vector60", "cGFja2V0NjB2ZWN0b3I2MA"),
    ("packet60processor60", "cGFja2V0NjBwcm9jZXNzb3I2MA"),
    ("router60processor60", "cm91dGVyNjBwcm9jZXNzb3I2MA"),
    ("router60reasoning60", "cm91dGVyNjByZWFzb25pbmc2MA"),
    ("router60machine60", "cm91dGVyNjBtYWNoaW5lNjA"),
    ("router60learning60", "cm91dGVyNjBsZWFybmluZzYw"),
    ("cluster60learning60", "Y2x1c3RlcjYwbGVhcm5pbmc2MA"),
    ("cluster60model60", "Y2x1c3RlcjYwbW9kZWw2MA"),
    ("cluster60token60", "Y2x1c3RlcjYwdG9rZW42MA"),
    ("cluster60prompt60", "Y2x1c3RlcjYwcHJvbXB0NjA"),
    ("mirror60prompt60", "bWlycm9yNjBwcm9tcHQ2MA"),
    ("mirror60session60", "bWlycm9yNjBzZXNzaW9uNjA"),
    ("mirror60library60", "bWlycm9yNjBsaWJyYXJ5NjA"),
    ("mirror60service60", "bWlycm9yNjBzZXJ2aWNlNjA"),
    ("filter60service60", "ZmlsdGVyNjBzZXJ2aWNlNjA"),
    ("filter60gateway60", "ZmlsdGVyNjBnYXRld2F5NjA"),
    ("filter60storage60", "ZmlsdGVyNjBzdG9yYWdlNjA"),
    ("filter60network60", "ZmlsdGVyNjBuZXR3b3JrNjA"),
    ("ranking60network60", "cmFua2luZzYwbmV0d29yazYw"),
    ("ranking60latency60", "cmFua2luZzYwbGF0ZW5jeTYw"),
    ("ranking60buffer60", "cmFua2luZzYwYnVmZmVyNjA"),
    ("ranking60queue60", "cmFua2luZzYwcXVldWU2MA"),
    ("encoding60queue60", "ZW5jb2Rpbmc2MHF1ZXVlNjA"),
    ("encoding60worker60", "ZW5jb2Rpbmc2MHdvcmtlcjYw"),
    ("encoding60kernel60", "ZW5jb2Rpbmc2MGtlcm5lbDYw"),
    ("encoding60signal60", "ZW5jb2Rpbmc2MHNpZ25hbDYw"),
    ("mapping60signal60", "bWFwcGluZzYwc2lnbmFsNjA"),
    ("mapping60packet60", "bWFwcGluZzYwcGFja2V0NjA"),
    ("mapping60router60", "bWFwcGluZzYwcm91dGVyNjA"),
    ("mapping60cluster60", "bWFwcGluZzYwY2x1c3RlcjYw"),
    ("record60cluster60", "cmVjb3JkNjBjbHVzdGVyNjA"),
    ("record60mirror60", "cmVjb3JkNjBtaXJyb3I2MA"),
    ("record60filter60", "cmVjb3JkNjBmaWx0ZXI2MA"),
    ("record60ranking60", "cmVjb3JkNjByYW5raW5nNjA"),
    ("candle60ranking60", "Y2FuZGxlNjByYW5raW5nNjA"),
    ("candle60encoding60", "Y2FuZGxlNjBlbmNvZGluZzYw"),
    ("candle60mapping60", "Y2FuZGxlNjBtYXBwaW5nNjA"),
    ("candle60record60", "Y2FuZGxlNjByZWNvcmQ2MA"),
    ("thread60record60", "dGhyZWFkNjByZWNvcmQ2MA"),
    ("thread60candle60", "dGhyZWFkNjBjYW5kbGU2MA"),
    ("thread60thread60", "dGhyZWFkNjB0aHJlYWQ2MA"),
    ("thread60kitten60", "dGhyZWFkNjBraXR0ZW42MA"),
    (
        "round 60: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNjA6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 60: agentuniverse is a framework for multi agents",
        "cm91bmQgNjA6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 60: knowledge stored as vectors enables retrieval",
        "cm91bmQgNjA6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 60: the processor reads the record then stops",
        "cm91bmQgNjA6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 60: a worker pulls the next task from the queue",
        "cm91bmQgNjA6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 60: signals travel through the network layer",
        "cm91bmQgNjA6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 60: the gateway routes each request by policy",
        "cm91bmQgNjA6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 60: memory grows until the buffer is full",
        "cm91bmQgNjA6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 60: the cluster mirrors every packet twice",
        "cm91bmQgNjA6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 60: ranking uses tokens learned from the corpus",
        "cm91bmQgNjA6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 60: a long session ends when the candle dies",
        "cm91bmQgNjA6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 60: encode the prompt then map the result",
        "cm91bmQgNjA6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 60: the kernel wakes the worker at dawn", "cm91bmQgNjA6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 60: service latency drops after the patch",
        "cm91bmQgNjA6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 60: the library caches every vector it sees",
        "cm91bmQgNjA6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 60: agents argue then the debate resolves",
        "cm91bmQgNjA6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 60: the filter keeps only strong matches",
        "cm91bmQgNjA6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 60: the model answers with a short reply",
        "cm91bmQgNjA6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 60: the recorder stores the reasoning trace",
        "cm91bmQgNjA6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 60: the angel watches the processor run", "cm91bmQgNjA6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 60: angle of the vector decides the match",
        "cm91bmQgNjA6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 60: the candle burns twice as long at night",
        "cm91bmQgNjA6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 60: a mirror of the universe in one line",
        "cm91bmQgNjA6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 60: the queue drains before the storm", "cm91bmQgNjA6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
