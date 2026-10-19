"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten54kitten54", "a2l0dGVuNTRraXR0ZW41NA"),
    ("kitten54sitting54", "a2l0dGVuNTRzaXR0aW5nNTQ"),
    ("kitten54agent54", "a2l0dGVuNTRhZ2VudDU0"),
    ("kitten54angle54", "a2l0dGVuNTRhbmdsZTU0"),
    ("sitting54angle54", "c2l0dGluZzU0YW5nbGU1NA"),
    ("sitting54universe54", "c2l0dGluZzU0dW5pdmVyc2U1NA"),
    ("sitting54memory54", "c2l0dGluZzU0bWVtb3J5NTQ"),
    ("sitting54stream54", "c2l0dGluZzU0c3RyZWFtNTQ"),
    ("agent54stream54", "YWdlbnQ1NHN0cmVhbTU0"),
    ("agent54context54", "YWdlbnQ1NGNvbnRleHQ1NA"),
    ("agent54knowledge54", "YWdlbnQ1NGtub3dsZWRnZTU0"),
    ("agent54vector54", "YWdlbnQ1NHZlY3RvcjU0"),
    ("angle54vector54", "YW5nbGU1NHZlY3RvcjU0"),
    ("angle54processor54", "YW5nbGU1NHByb2Nlc3NvcjU0"),
    ("angle54reasoning54", "YW5nbGU1NHJlYXNvbmluZzU0"),
    ("angle54machine54", "YW5nbGU1NG1hY2hpbmU1NA"),
    ("universe54machine54", "dW5pdmVyc2U1NG1hY2hpbmU1NA"),
    ("universe54learning54", "dW5pdmVyc2U1NGxlYXJuaW5nNTQ"),
    ("universe54model54", "dW5pdmVyc2U1NG1vZGVsNTQ"),
    ("universe54token54", "dW5pdmVyc2U1NHRva2VuNTQ"),
    ("memory54token54", "bWVtb3J5NTR0b2tlbjU0"),
    ("memory54prompt54", "bWVtb3J5NTRwcm9tcHQ1NA"),
    ("memory54session54", "bWVtb3J5NTRzZXNzaW9uNTQ"),
    ("memory54library54", "bWVtb3J5NTRsaWJyYXJ5NTQ"),
    ("stream54library54", "c3RyZWFtNTRsaWJyYXJ5NTQ"),
    ("stream54service54", "c3RyZWFtNTRzZXJ2aWNlNTQ"),
    ("stream54gateway54", "c3RyZWFtNTRnYXRld2F5NTQ"),
    ("stream54storage54", "c3RyZWFtNTRzdG9yYWdlNTQ"),
    ("context54storage54", "Y29udGV4dDU0c3RvcmFnZTU0"),
    ("context54network54", "Y29udGV4dDU0bmV0d29yazU0"),
    ("context54latency54", "Y29udGV4dDU0bGF0ZW5jeTU0"),
    ("context54buffer54", "Y29udGV4dDU0YnVmZmVyNTQ"),
    ("knowledge54buffer54", "a25vd2xlZGdlNTRidWZmZXI1NA"),
    ("knowledge54queue54", "a25vd2xlZGdlNTRxdWV1ZTU0"),
    ("knowledge54worker54", "a25vd2xlZGdlNTR3b3JrZXI1NA"),
    ("knowledge54kernel54", "a25vd2xlZGdlNTRrZXJuZWw1NA"),
    ("vector54kernel54", "dmVjdG9yNTRrZXJuZWw1NA"),
    ("vector54signal54", "dmVjdG9yNTRzaWduYWw1NA"),
    ("vector54packet54", "dmVjdG9yNTRwYWNrZXQ1NA"),
    ("vector54router54", "dmVjdG9yNTRyb3V0ZXI1NA"),
    ("processor54router54", "cHJvY2Vzc29yNTRyb3V0ZXI1NA"),
    ("processor54cluster54", "cHJvY2Vzc29yNTRjbHVzdGVyNTQ"),
    ("processor54mirror54", "cHJvY2Vzc29yNTRtaXJyb3I1NA"),
    ("processor54filter54", "cHJvY2Vzc29yNTRmaWx0ZXI1NA"),
    ("reasoning54filter54", "cmVhc29uaW5nNTRmaWx0ZXI1NA"),
    ("reasoning54ranking54", "cmVhc29uaW5nNTRyYW5raW5nNTQ"),
    ("reasoning54encoding54", "cmVhc29uaW5nNTRlbmNvZGluZzU0"),
    ("reasoning54mapping54", "cmVhc29uaW5nNTRtYXBwaW5nNTQ"),
    ("machine54mapping54", "bWFjaGluZTU0bWFwcGluZzU0"),
    ("machine54record54", "bWFjaGluZTU0cmVjb3JkNTQ"),
    ("machine54candle54", "bWFjaGluZTU0Y2FuZGxlNTQ"),
    ("machine54thread54", "bWFjaGluZTU0dGhyZWFkNTQ"),
    ("learning54thread54", "bGVhcm5pbmc1NHRocmVhZDU0"),
    ("learning54kitten54", "bGVhcm5pbmc1NGtpdHRlbjU0"),
    ("learning54sitting54", "bGVhcm5pbmc1NHNpdHRpbmc1NA"),
    ("learning54agent54", "bGVhcm5pbmc1NGFnZW50NTQ"),
    ("model54agent54", "bW9kZWw1NGFnZW50NTQ"),
    ("model54angle54", "bW9kZWw1NGFuZ2xlNTQ"),
    ("model54universe54", "bW9kZWw1NHVuaXZlcnNlNTQ"),
    ("model54memory54", "bW9kZWw1NG1lbW9yeTU0"),
    ("token54memory54", "dG9rZW41NG1lbW9yeTU0"),
    ("token54stream54", "dG9rZW41NHN0cmVhbTU0"),
    ("token54context54", "dG9rZW41NGNvbnRleHQ1NA"),
    ("token54knowledge54", "dG9rZW41NGtub3dsZWRnZTU0"),
    ("prompt54knowledge54", "cHJvbXB0NTRrbm93bGVkZ2U1NA"),
    ("prompt54vector54", "cHJvbXB0NTR2ZWN0b3I1NA"),
    ("prompt54processor54", "cHJvbXB0NTRwcm9jZXNzb3I1NA"),
    ("prompt54reasoning54", "cHJvbXB0NTRyZWFzb25pbmc1NA"),
    ("session54reasoning54", "c2Vzc2lvbjU0cmVhc29uaW5nNTQ"),
    ("session54machine54", "c2Vzc2lvbjU0bWFjaGluZTU0"),
    ("session54learning54", "c2Vzc2lvbjU0bGVhcm5pbmc1NA"),
    ("session54model54", "c2Vzc2lvbjU0bW9kZWw1NA"),
    ("library54model54", "bGlicmFyeTU0bW9kZWw1NA"),
    ("library54token54", "bGlicmFyeTU0dG9rZW41NA"),
    ("library54prompt54", "bGlicmFyeTU0cHJvbXB0NTQ"),
    ("library54session54", "bGlicmFyeTU0c2Vzc2lvbjU0"),
    ("service54session54", "c2VydmljZTU0c2Vzc2lvbjU0"),
    ("service54library54", "c2VydmljZTU0bGlicmFyeTU0"),
    ("service54service54", "c2VydmljZTU0c2VydmljZTU0"),
    ("service54gateway54", "c2VydmljZTU0Z2F0ZXdheTU0"),
    ("gateway54gateway54", "Z2F0ZXdheTU0Z2F0ZXdheTU0"),
    ("gateway54storage54", "Z2F0ZXdheTU0c3RvcmFnZTU0"),
    ("gateway54network54", "Z2F0ZXdheTU0bmV0d29yazU0"),
    ("gateway54latency54", "Z2F0ZXdheTU0bGF0ZW5jeTU0"),
    ("storage54latency54", "c3RvcmFnZTU0bGF0ZW5jeTU0"),
    ("storage54buffer54", "c3RvcmFnZTU0YnVmZmVyNTQ"),
    ("storage54queue54", "c3RvcmFnZTU0cXVldWU1NA"),
    ("storage54worker54", "c3RvcmFnZTU0d29ya2VyNTQ"),
    ("network54worker54", "bmV0d29yazU0d29ya2VyNTQ"),
    ("network54kernel54", "bmV0d29yazU0a2VybmVsNTQ"),
    ("network54signal54", "bmV0d29yazU0c2lnbmFsNTQ"),
    ("network54packet54", "bmV0d29yazU0cGFja2V0NTQ"),
    ("latency54packet54", "bGF0ZW5jeTU0cGFja2V0NTQ"),
    ("latency54router54", "bGF0ZW5jeTU0cm91dGVyNTQ"),
    ("latency54cluster54", "bGF0ZW5jeTU0Y2x1c3RlcjU0"),
    ("latency54mirror54", "bGF0ZW5jeTU0bWlycm9yNTQ"),
    ("buffer54mirror54", "YnVmZmVyNTRtaXJyb3I1NA"),
    ("buffer54filter54", "YnVmZmVyNTRmaWx0ZXI1NA"),
    ("buffer54ranking54", "YnVmZmVyNTRyYW5raW5nNTQ"),
    ("buffer54encoding54", "YnVmZmVyNTRlbmNvZGluZzU0"),
    ("queue54encoding54", "cXVldWU1NGVuY29kaW5nNTQ"),
    ("queue54mapping54", "cXVldWU1NG1hcHBpbmc1NA"),
    ("queue54record54", "cXVldWU1NHJlY29yZDU0"),
    ("queue54candle54", "cXVldWU1NGNhbmRsZTU0"),
    ("worker54candle54", "d29ya2VyNTRjYW5kbGU1NA"),
    ("worker54thread54", "d29ya2VyNTR0aHJlYWQ1NA"),
    ("worker54kitten54", "d29ya2VyNTRraXR0ZW41NA"),
    ("worker54sitting54", "d29ya2VyNTRzaXR0aW5nNTQ"),
    ("kernel54sitting54", "a2VybmVsNTRzaXR0aW5nNTQ"),
    ("kernel54agent54", "a2VybmVsNTRhZ2VudDU0"),
    ("kernel54angle54", "a2VybmVsNTRhbmdsZTU0"),
    ("kernel54universe54", "a2VybmVsNTR1bml2ZXJzZTU0"),
    ("signal54universe54", "c2lnbmFsNTR1bml2ZXJzZTU0"),
    ("signal54memory54", "c2lnbmFsNTRtZW1vcnk1NA"),
    ("signal54stream54", "c2lnbmFsNTRzdHJlYW01NA"),
    ("signal54context54", "c2lnbmFsNTRjb250ZXh0NTQ"),
    ("packet54context54", "cGFja2V0NTRjb250ZXh0NTQ"),
    ("packet54knowledge54", "cGFja2V0NTRrbm93bGVkZ2U1NA"),
    ("packet54vector54", "cGFja2V0NTR2ZWN0b3I1NA"),
    ("packet54processor54", "cGFja2V0NTRwcm9jZXNzb3I1NA"),
    ("router54processor54", "cm91dGVyNTRwcm9jZXNzb3I1NA"),
    ("router54reasoning54", "cm91dGVyNTRyZWFzb25pbmc1NA"),
    ("router54machine54", "cm91dGVyNTRtYWNoaW5lNTQ"),
    ("router54learning54", "cm91dGVyNTRsZWFybmluZzU0"),
    ("cluster54learning54", "Y2x1c3RlcjU0bGVhcm5pbmc1NA"),
    ("cluster54model54", "Y2x1c3RlcjU0bW9kZWw1NA"),
    ("cluster54token54", "Y2x1c3RlcjU0dG9rZW41NA"),
    ("cluster54prompt54", "Y2x1c3RlcjU0cHJvbXB0NTQ"),
    ("mirror54prompt54", "bWlycm9yNTRwcm9tcHQ1NA"),
    ("mirror54session54", "bWlycm9yNTRzZXNzaW9uNTQ"),
    ("mirror54library54", "bWlycm9yNTRsaWJyYXJ5NTQ"),
    ("mirror54service54", "bWlycm9yNTRzZXJ2aWNlNTQ"),
    ("filter54service54", "ZmlsdGVyNTRzZXJ2aWNlNTQ"),
    ("filter54gateway54", "ZmlsdGVyNTRnYXRld2F5NTQ"),
    ("filter54storage54", "ZmlsdGVyNTRzdG9yYWdlNTQ"),
    ("filter54network54", "ZmlsdGVyNTRuZXR3b3JrNTQ"),
    ("ranking54network54", "cmFua2luZzU0bmV0d29yazU0"),
    ("ranking54latency54", "cmFua2luZzU0bGF0ZW5jeTU0"),
    ("ranking54buffer54", "cmFua2luZzU0YnVmZmVyNTQ"),
    ("ranking54queue54", "cmFua2luZzU0cXVldWU1NA"),
    ("encoding54queue54", "ZW5jb2Rpbmc1NHF1ZXVlNTQ"),
    ("encoding54worker54", "ZW5jb2Rpbmc1NHdvcmtlcjU0"),
    ("encoding54kernel54", "ZW5jb2Rpbmc1NGtlcm5lbDU0"),
    ("encoding54signal54", "ZW5jb2Rpbmc1NHNpZ25hbDU0"),
    ("mapping54signal54", "bWFwcGluZzU0c2lnbmFsNTQ"),
    ("mapping54packet54", "bWFwcGluZzU0cGFja2V0NTQ"),
    ("mapping54router54", "bWFwcGluZzU0cm91dGVyNTQ"),
    ("mapping54cluster54", "bWFwcGluZzU0Y2x1c3RlcjU0"),
    ("record54cluster54", "cmVjb3JkNTRjbHVzdGVyNTQ"),
    ("record54mirror54", "cmVjb3JkNTRtaXJyb3I1NA"),
    ("record54filter54", "cmVjb3JkNTRmaWx0ZXI1NA"),
    ("record54ranking54", "cmVjb3JkNTRyYW5raW5nNTQ"),
    ("candle54ranking54", "Y2FuZGxlNTRyYW5raW5nNTQ"),
    ("candle54encoding54", "Y2FuZGxlNTRlbmNvZGluZzU0"),
    ("candle54mapping54", "Y2FuZGxlNTRtYXBwaW5nNTQ"),
    ("candle54record54", "Y2FuZGxlNTRyZWNvcmQ1NA"),
    ("thread54record54", "dGhyZWFkNTRyZWNvcmQ1NA"),
    ("thread54candle54", "dGhyZWFkNTRjYW5kbGU1NA"),
    ("thread54thread54", "dGhyZWFkNTR0aHJlYWQ1NA"),
    ("thread54kitten54", "dGhyZWFkNTRraXR0ZW41NA"),
    (
        "round 54: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNTQ6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 54: agentuniverse is a framework for multi agents",
        "cm91bmQgNTQ6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 54: knowledge stored as vectors enables retrieval",
        "cm91bmQgNTQ6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 54: the processor reads the record then stops",
        "cm91bmQgNTQ6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 54: a worker pulls the next task from the queue",
        "cm91bmQgNTQ6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 54: signals travel through the network layer",
        "cm91bmQgNTQ6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 54: the gateway routes each request by policy",
        "cm91bmQgNTQ6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 54: memory grows until the buffer is full",
        "cm91bmQgNTQ6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 54: the cluster mirrors every packet twice",
        "cm91bmQgNTQ6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 54: ranking uses tokens learned from the corpus",
        "cm91bmQgNTQ6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 54: a long session ends when the candle dies",
        "cm91bmQgNTQ6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 54: encode the prompt then map the result",
        "cm91bmQgNTQ6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 54: the kernel wakes the worker at dawn", "cm91bmQgNTQ6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 54: service latency drops after the patch",
        "cm91bmQgNTQ6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 54: the library caches every vector it sees",
        "cm91bmQgNTQ6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 54: agents argue then the debate resolves",
        "cm91bmQgNTQ6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 54: the filter keeps only strong matches",
        "cm91bmQgNTQ6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 54: the model answers with a short reply",
        "cm91bmQgNTQ6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 54: the recorder stores the reasoning trace",
        "cm91bmQgNTQ6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 54: the angel watches the processor run", "cm91bmQgNTQ6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 54: angle of the vector decides the match",
        "cm91bmQgNTQ6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 54: the candle burns twice as long at night",
        "cm91bmQgNTQ6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 54: a mirror of the universe in one line",
        "cm91bmQgNTQ6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 54: the queue drains before the storm", "cm91bmQgNTQ6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
