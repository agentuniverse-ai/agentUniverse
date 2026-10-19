"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten65kitten65", "a2l0dGVuNjVraXR0ZW42NQ"),
    ("kitten65sitting65", "a2l0dGVuNjVzaXR0aW5nNjU"),
    ("kitten65agent65", "a2l0dGVuNjVhZ2VudDY1"),
    ("kitten65angle65", "a2l0dGVuNjVhbmdsZTY1"),
    ("sitting65angle65", "c2l0dGluZzY1YW5nbGU2NQ"),
    ("sitting65universe65", "c2l0dGluZzY1dW5pdmVyc2U2NQ"),
    ("sitting65memory65", "c2l0dGluZzY1bWVtb3J5NjU"),
    ("sitting65stream65", "c2l0dGluZzY1c3RyZWFtNjU"),
    ("agent65stream65", "YWdlbnQ2NXN0cmVhbTY1"),
    ("agent65context65", "YWdlbnQ2NWNvbnRleHQ2NQ"),
    ("agent65knowledge65", "YWdlbnQ2NWtub3dsZWRnZTY1"),
    ("agent65vector65", "YWdlbnQ2NXZlY3RvcjY1"),
    ("angle65vector65", "YW5nbGU2NXZlY3RvcjY1"),
    ("angle65processor65", "YW5nbGU2NXByb2Nlc3NvcjY1"),
    ("angle65reasoning65", "YW5nbGU2NXJlYXNvbmluZzY1"),
    ("angle65machine65", "YW5nbGU2NW1hY2hpbmU2NQ"),
    ("universe65machine65", "dW5pdmVyc2U2NW1hY2hpbmU2NQ"),
    ("universe65learning65", "dW5pdmVyc2U2NWxlYXJuaW5nNjU"),
    ("universe65model65", "dW5pdmVyc2U2NW1vZGVsNjU"),
    ("universe65token65", "dW5pdmVyc2U2NXRva2VuNjU"),
    ("memory65token65", "bWVtb3J5NjV0b2tlbjY1"),
    ("memory65prompt65", "bWVtb3J5NjVwcm9tcHQ2NQ"),
    ("memory65session65", "bWVtb3J5NjVzZXNzaW9uNjU"),
    ("memory65library65", "bWVtb3J5NjVsaWJyYXJ5NjU"),
    ("stream65library65", "c3RyZWFtNjVsaWJyYXJ5NjU"),
    ("stream65service65", "c3RyZWFtNjVzZXJ2aWNlNjU"),
    ("stream65gateway65", "c3RyZWFtNjVnYXRld2F5NjU"),
    ("stream65storage65", "c3RyZWFtNjVzdG9yYWdlNjU"),
    ("context65storage65", "Y29udGV4dDY1c3RvcmFnZTY1"),
    ("context65network65", "Y29udGV4dDY1bmV0d29yazY1"),
    ("context65latency65", "Y29udGV4dDY1bGF0ZW5jeTY1"),
    ("context65buffer65", "Y29udGV4dDY1YnVmZmVyNjU"),
    ("knowledge65buffer65", "a25vd2xlZGdlNjVidWZmZXI2NQ"),
    ("knowledge65queue65", "a25vd2xlZGdlNjVxdWV1ZTY1"),
    ("knowledge65worker65", "a25vd2xlZGdlNjV3b3JrZXI2NQ"),
    ("knowledge65kernel65", "a25vd2xlZGdlNjVrZXJuZWw2NQ"),
    ("vector65kernel65", "dmVjdG9yNjVrZXJuZWw2NQ"),
    ("vector65signal65", "dmVjdG9yNjVzaWduYWw2NQ"),
    ("vector65packet65", "dmVjdG9yNjVwYWNrZXQ2NQ"),
    ("vector65router65", "dmVjdG9yNjVyb3V0ZXI2NQ"),
    ("processor65router65", "cHJvY2Vzc29yNjVyb3V0ZXI2NQ"),
    ("processor65cluster65", "cHJvY2Vzc29yNjVjbHVzdGVyNjU"),
    ("processor65mirror65", "cHJvY2Vzc29yNjVtaXJyb3I2NQ"),
    ("processor65filter65", "cHJvY2Vzc29yNjVmaWx0ZXI2NQ"),
    ("reasoning65filter65", "cmVhc29uaW5nNjVmaWx0ZXI2NQ"),
    ("reasoning65ranking65", "cmVhc29uaW5nNjVyYW5raW5nNjU"),
    ("reasoning65encoding65", "cmVhc29uaW5nNjVlbmNvZGluZzY1"),
    ("reasoning65mapping65", "cmVhc29uaW5nNjVtYXBwaW5nNjU"),
    ("machine65mapping65", "bWFjaGluZTY1bWFwcGluZzY1"),
    ("machine65record65", "bWFjaGluZTY1cmVjb3JkNjU"),
    ("machine65candle65", "bWFjaGluZTY1Y2FuZGxlNjU"),
    ("machine65thread65", "bWFjaGluZTY1dGhyZWFkNjU"),
    ("learning65thread65", "bGVhcm5pbmc2NXRocmVhZDY1"),
    ("learning65kitten65", "bGVhcm5pbmc2NWtpdHRlbjY1"),
    ("learning65sitting65", "bGVhcm5pbmc2NXNpdHRpbmc2NQ"),
    ("learning65agent65", "bGVhcm5pbmc2NWFnZW50NjU"),
    ("model65agent65", "bW9kZWw2NWFnZW50NjU"),
    ("model65angle65", "bW9kZWw2NWFuZ2xlNjU"),
    ("model65universe65", "bW9kZWw2NXVuaXZlcnNlNjU"),
    ("model65memory65", "bW9kZWw2NW1lbW9yeTY1"),
    ("token65memory65", "dG9rZW42NW1lbW9yeTY1"),
    ("token65stream65", "dG9rZW42NXN0cmVhbTY1"),
    ("token65context65", "dG9rZW42NWNvbnRleHQ2NQ"),
    ("token65knowledge65", "dG9rZW42NWtub3dsZWRnZTY1"),
    ("prompt65knowledge65", "cHJvbXB0NjVrbm93bGVkZ2U2NQ"),
    ("prompt65vector65", "cHJvbXB0NjV2ZWN0b3I2NQ"),
    ("prompt65processor65", "cHJvbXB0NjVwcm9jZXNzb3I2NQ"),
    ("prompt65reasoning65", "cHJvbXB0NjVyZWFzb25pbmc2NQ"),
    ("session65reasoning65", "c2Vzc2lvbjY1cmVhc29uaW5nNjU"),
    ("session65machine65", "c2Vzc2lvbjY1bWFjaGluZTY1"),
    ("session65learning65", "c2Vzc2lvbjY1bGVhcm5pbmc2NQ"),
    ("session65model65", "c2Vzc2lvbjY1bW9kZWw2NQ"),
    ("library65model65", "bGlicmFyeTY1bW9kZWw2NQ"),
    ("library65token65", "bGlicmFyeTY1dG9rZW42NQ"),
    ("library65prompt65", "bGlicmFyeTY1cHJvbXB0NjU"),
    ("library65session65", "bGlicmFyeTY1c2Vzc2lvbjY1"),
    ("service65session65", "c2VydmljZTY1c2Vzc2lvbjY1"),
    ("service65library65", "c2VydmljZTY1bGlicmFyeTY1"),
    ("service65service65", "c2VydmljZTY1c2VydmljZTY1"),
    ("service65gateway65", "c2VydmljZTY1Z2F0ZXdheTY1"),
    ("gateway65gateway65", "Z2F0ZXdheTY1Z2F0ZXdheTY1"),
    ("gateway65storage65", "Z2F0ZXdheTY1c3RvcmFnZTY1"),
    ("gateway65network65", "Z2F0ZXdheTY1bmV0d29yazY1"),
    ("gateway65latency65", "Z2F0ZXdheTY1bGF0ZW5jeTY1"),
    ("storage65latency65", "c3RvcmFnZTY1bGF0ZW5jeTY1"),
    ("storage65buffer65", "c3RvcmFnZTY1YnVmZmVyNjU"),
    ("storage65queue65", "c3RvcmFnZTY1cXVldWU2NQ"),
    ("storage65worker65", "c3RvcmFnZTY1d29ya2VyNjU"),
    ("network65worker65", "bmV0d29yazY1d29ya2VyNjU"),
    ("network65kernel65", "bmV0d29yazY1a2VybmVsNjU"),
    ("network65signal65", "bmV0d29yazY1c2lnbmFsNjU"),
    ("network65packet65", "bmV0d29yazY1cGFja2V0NjU"),
    ("latency65packet65", "bGF0ZW5jeTY1cGFja2V0NjU"),
    ("latency65router65", "bGF0ZW5jeTY1cm91dGVyNjU"),
    ("latency65cluster65", "bGF0ZW5jeTY1Y2x1c3RlcjY1"),
    ("latency65mirror65", "bGF0ZW5jeTY1bWlycm9yNjU"),
    ("buffer65mirror65", "YnVmZmVyNjVtaXJyb3I2NQ"),
    ("buffer65filter65", "YnVmZmVyNjVmaWx0ZXI2NQ"),
    ("buffer65ranking65", "YnVmZmVyNjVyYW5raW5nNjU"),
    ("buffer65encoding65", "YnVmZmVyNjVlbmNvZGluZzY1"),
    ("queue65encoding65", "cXVldWU2NWVuY29kaW5nNjU"),
    ("queue65mapping65", "cXVldWU2NW1hcHBpbmc2NQ"),
    ("queue65record65", "cXVldWU2NXJlY29yZDY1"),
    ("queue65candle65", "cXVldWU2NWNhbmRsZTY1"),
    ("worker65candle65", "d29ya2VyNjVjYW5kbGU2NQ"),
    ("worker65thread65", "d29ya2VyNjV0aHJlYWQ2NQ"),
    ("worker65kitten65", "d29ya2VyNjVraXR0ZW42NQ"),
    ("worker65sitting65", "d29ya2VyNjVzaXR0aW5nNjU"),
    ("kernel65sitting65", "a2VybmVsNjVzaXR0aW5nNjU"),
    ("kernel65agent65", "a2VybmVsNjVhZ2VudDY1"),
    ("kernel65angle65", "a2VybmVsNjVhbmdsZTY1"),
    ("kernel65universe65", "a2VybmVsNjV1bml2ZXJzZTY1"),
    ("signal65universe65", "c2lnbmFsNjV1bml2ZXJzZTY1"),
    ("signal65memory65", "c2lnbmFsNjVtZW1vcnk2NQ"),
    ("signal65stream65", "c2lnbmFsNjVzdHJlYW02NQ"),
    ("signal65context65", "c2lnbmFsNjVjb250ZXh0NjU"),
    ("packet65context65", "cGFja2V0NjVjb250ZXh0NjU"),
    ("packet65knowledge65", "cGFja2V0NjVrbm93bGVkZ2U2NQ"),
    ("packet65vector65", "cGFja2V0NjV2ZWN0b3I2NQ"),
    ("packet65processor65", "cGFja2V0NjVwcm9jZXNzb3I2NQ"),
    ("router65processor65", "cm91dGVyNjVwcm9jZXNzb3I2NQ"),
    ("router65reasoning65", "cm91dGVyNjVyZWFzb25pbmc2NQ"),
    ("router65machine65", "cm91dGVyNjVtYWNoaW5lNjU"),
    ("router65learning65", "cm91dGVyNjVsZWFybmluZzY1"),
    ("cluster65learning65", "Y2x1c3RlcjY1bGVhcm5pbmc2NQ"),
    ("cluster65model65", "Y2x1c3RlcjY1bW9kZWw2NQ"),
    ("cluster65token65", "Y2x1c3RlcjY1dG9rZW42NQ"),
    ("cluster65prompt65", "Y2x1c3RlcjY1cHJvbXB0NjU"),
    ("mirror65prompt65", "bWlycm9yNjVwcm9tcHQ2NQ"),
    ("mirror65session65", "bWlycm9yNjVzZXNzaW9uNjU"),
    ("mirror65library65", "bWlycm9yNjVsaWJyYXJ5NjU"),
    ("mirror65service65", "bWlycm9yNjVzZXJ2aWNlNjU"),
    ("filter65service65", "ZmlsdGVyNjVzZXJ2aWNlNjU"),
    ("filter65gateway65", "ZmlsdGVyNjVnYXRld2F5NjU"),
    ("filter65storage65", "ZmlsdGVyNjVzdG9yYWdlNjU"),
    ("filter65network65", "ZmlsdGVyNjVuZXR3b3JrNjU"),
    ("ranking65network65", "cmFua2luZzY1bmV0d29yazY1"),
    ("ranking65latency65", "cmFua2luZzY1bGF0ZW5jeTY1"),
    ("ranking65buffer65", "cmFua2luZzY1YnVmZmVyNjU"),
    ("ranking65queue65", "cmFua2luZzY1cXVldWU2NQ"),
    ("encoding65queue65", "ZW5jb2Rpbmc2NXF1ZXVlNjU"),
    ("encoding65worker65", "ZW5jb2Rpbmc2NXdvcmtlcjY1"),
    ("encoding65kernel65", "ZW5jb2Rpbmc2NWtlcm5lbDY1"),
    ("encoding65signal65", "ZW5jb2Rpbmc2NXNpZ25hbDY1"),
    ("mapping65signal65", "bWFwcGluZzY1c2lnbmFsNjU"),
    ("mapping65packet65", "bWFwcGluZzY1cGFja2V0NjU"),
    ("mapping65router65", "bWFwcGluZzY1cm91dGVyNjU"),
    ("mapping65cluster65", "bWFwcGluZzY1Y2x1c3RlcjY1"),
    ("record65cluster65", "cmVjb3JkNjVjbHVzdGVyNjU"),
    ("record65mirror65", "cmVjb3JkNjVtaXJyb3I2NQ"),
    ("record65filter65", "cmVjb3JkNjVmaWx0ZXI2NQ"),
    ("record65ranking65", "cmVjb3JkNjVyYW5raW5nNjU"),
    ("candle65ranking65", "Y2FuZGxlNjVyYW5raW5nNjU"),
    ("candle65encoding65", "Y2FuZGxlNjVlbmNvZGluZzY1"),
    ("candle65mapping65", "Y2FuZGxlNjVtYXBwaW5nNjU"),
    ("candle65record65", "Y2FuZGxlNjVyZWNvcmQ2NQ"),
    ("thread65record65", "dGhyZWFkNjVyZWNvcmQ2NQ"),
    ("thread65candle65", "dGhyZWFkNjVjYW5kbGU2NQ"),
    ("thread65thread65", "dGhyZWFkNjV0aHJlYWQ2NQ"),
    ("thread65kitten65", "dGhyZWFkNjVraXR0ZW42NQ"),
    (
        "round 65: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNjU6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 65: agentuniverse is a framework for multi agents",
        "cm91bmQgNjU6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 65: knowledge stored as vectors enables retrieval",
        "cm91bmQgNjU6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 65: the processor reads the record then stops",
        "cm91bmQgNjU6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 65: a worker pulls the next task from the queue",
        "cm91bmQgNjU6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 65: signals travel through the network layer",
        "cm91bmQgNjU6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 65: the gateway routes each request by policy",
        "cm91bmQgNjU6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 65: memory grows until the buffer is full",
        "cm91bmQgNjU6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 65: the cluster mirrors every packet twice",
        "cm91bmQgNjU6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 65: ranking uses tokens learned from the corpus",
        "cm91bmQgNjU6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 65: a long session ends when the candle dies",
        "cm91bmQgNjU6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 65: encode the prompt then map the result",
        "cm91bmQgNjU6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 65: the kernel wakes the worker at dawn", "cm91bmQgNjU6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 65: service latency drops after the patch",
        "cm91bmQgNjU6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 65: the library caches every vector it sees",
        "cm91bmQgNjU6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 65: agents argue then the debate resolves",
        "cm91bmQgNjU6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 65: the filter keeps only strong matches",
        "cm91bmQgNjU6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 65: the model answers with a short reply",
        "cm91bmQgNjU6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 65: the recorder stores the reasoning trace",
        "cm91bmQgNjU6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 65: the angel watches the processor run", "cm91bmQgNjU6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 65: angle of the vector decides the match",
        "cm91bmQgNjU6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 65: the candle burns twice as long at night",
        "cm91bmQgNjU6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 65: a mirror of the universe in one line",
        "cm91bmQgNjU6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 65: the queue drains before the storm", "cm91bmQgNjU6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
